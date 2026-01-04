from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ClaimProbs:
    """各类吃碰杠胡概率"""
    hu: float = 0.0
    pong: float = 0.0
    kong: float = 0.0
    chow: float = 0.0


@dataclass
class OpponentFeatures:
    """对手特征集合"""
    is_honor: bool = False
    is_terminal: bool = False
    is_middle: bool = False
    is_safe_seen_opponent: bool = False
    seen_count_table: int = 0
    is_last_tile: bool = False
    is_exhausted: bool = False
    sequence_support_score: float = 0.0
    flush_tilt: bool = False
    pair_break: bool = False
    honor_tilt: bool = False
    recent_meld_count: int = 0
    last_action_type: str = ""
    consecutive_gang_count: int = 0
    changed_flower_count: int = 0


@dataclass
class OpponentPriors:
    """对手先验概率"""
    tenpai_prior: float = 0.0
    holding_prior: float = 0.0


@dataclass
class ExpectedLoss:
    """期望损失"""
    hu: float = 0.0
    pong: float = 0.0
    kong: float = 0.0
    chow: float = 0.0
    total: float = 0.0


@dataclass
class OpponentResult:
    """单个对手的评估结果"""
    opponent_id: str = ""
    seat: str = ""
    claim_probs: ClaimProbs = field(default_factory=ClaimProbs)
    features_used: OpponentFeatures = field(default_factory=OpponentFeatures)
    priors: OpponentPriors = field(default_factory=OpponentPriors)
    expected_loss: ExpectedLoss = field(default_factory=ExpectedLoss)
    notes: str = ""


@dataclass
class AggregateResult:
    """聚合评估结果"""
    P_any: float = 0.0
    total_expected_loss: float = 0.0
    phase: str = "early"
    rule_variant: str = "tencent_common"
    deck_remaining: int = 0
    discard_pile_size: int = 0


@dataclass
class BayesEvalResult:
    """贝叶斯评估完整结果"""
    per_opponent: List[OpponentResult] = field(default_factory=list)
    aggregate: AggregateResult = field(default_factory=AggregateResult)


class RiskEvaluator:
    """危险牌预测模块 - 基于贝叶斯定理"""
    
    # 阶段分界：基于巡数（一巡=4人各出一张牌）
    PHASE_EARLY_ROUNDS = 5    # 前5巡（≤20张弃牌）
    PHASE_MID_ROUNDS = 12     # 6-12巡（21-48张弃牌）
    # 13巡后（≥49张弃牌）为尾盘
    
    # 严重度权重：胡牌最高，杠次之，碰、吃最低
    SEVERITY_WEIGHTS = {"hu": 1.0, "kong": 0.20, "pong": 0.08, "chow": 0.05}
    
    # 庄家和尾期乘数
    DEALER_MULTIPLIER = 1.2
    LATE_PHASE_MULTIPLIER = 1.3

    # 定缺花色安全乘数（对手缺该花色时进一步降低反应概率）
    QUE_MISSING_MULT = {"hu": 0.15, "pong": 0.12, "kong": 0.10, "chow": 0.08}
    
    # 先验概率边界
    PRIORS = {
        "tenpai": {"floor": 0.05, "ceiling": 0.70},
        "pong": {"floor": 0.02, "ceiling": 0.60},
        "kong": {"floor": 0.01, "ceiling": 0.25},
        "chow": {"floor": 0.03, "ceiling": 0.65},
        "hu": {"floor": 0.005, "ceiling": 0.30},
    }
    
    # 特征似然乘数 P(feature | claim_type)
    # 熟张/绝张降低风险；幺九/中张/连张各有不同影响
    LIKELIHOODS = {
        # 熟张降低风险（适度恢复以防尾盘冒进）
        "safe_seen": {"hu": 0.40, "kong": 0.60, "pong": 0.50, "chow": 0.30},
        # 绝张牌进一步减权（适度恢复）
        "last_tile": {"hu": 0.15, "kong": 0.25, "pong": 0.20, "chow": 0.12},
        "terminal": {"hu": 1.2, "kong": 1.3, "pong": 1.4, "chow": 0.7},
        "middle": {"hu": 0.9, "kong": 0.8, "pong": 1.0, "chow": 1.2},
        "sequence_support": {"hu": 1.0, "kong": 0.7, "pong": 0.9, "chow": 1.4},
        "honor": {"hu": 1.3, "kong": 1.4, "pong": 1.5, "chow": 0.0},
    }
    
    # 形状奖励惩罚
    SHAPE_TRIPLET_BONUS = 0.35      # 保护刻子
    SHAPE_PAIR_BONUS = 0.18         # 保护对子
    SHAPE_TWO_SIDED_BONUS = 0.08    # 保护两面
    SHAPE_ONE_SIDE_BONUS = 0.05     # 保护单侧
    SHAPE_ISOLATED_PENALTY = -0.08  # 惩罚孤张
    
    def __init__(self, rule):
        self.rule = rule
        self._remaining_cache: Dict[str, int] = {}
    
    # ==================== 公开接口 ====================
    
    def evaluate_card_risk(self, card, player, game_state) -> float:
        """评估打出某张牌的风险（兼容旧接口）
        
        Args:
            card: 要评估的牌
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            风险值（0-1，越高越危险）
        """
        result = self.evaluate_discard_reaction_prob(card, player, game_state)
        return min(result.aggregate.total_expected_loss, 1.0)
    
    def evaluate_discard_reaction_prob(self, card, player, game_state) -> BayesEvalResult:
        """基于贝叶斯定理评估打出某张牌后对手反应的概率
        
        Args:
            card: 要评估的牌
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            BayesEvalResult 包含每个对手的概率和聚合结果
        """
        # 1. 推断阶段
        phase = self._infer_phase(game_state)
        
        # 2. 计算牌的全局剩余数量
        seen_count, remaining_count = self._compute_remaining_counts(card, game_state)
        
        # 3. 判断牌的基本属性
        is_honor = card.suit in ("风", "箭")
        is_terminal = card.suit in ("万", "筒", "条") and card.rank in ("1", "9", 1, 9)
        is_middle = card.suit in ("万", "筒", "条") and str(card.rank) in [str(i) for i in range(2, 9)]
        
        # 4. 计算连张支撑分数（仅序数牌）
        sequence_support = self._compute_sequence_support(card, game_state) if not is_honor else 0.0
        
        # 5. 判断规则变体
        rule_variant = getattr(game_state, "rule_name", "tencent_common")
        allow_chow = rule_variant == "tencent_common"
        
        # 6. 遍历每个对手计算概率
        per_opponent: List[OpponentResult] = []
        for opponent in game_state.players:
            if opponent == player:
                continue
            
            opp_result = self._evaluate_single_opponent(
                card, player, opponent, game_state,
                phase, seen_count, remaining_count,
                is_honor, is_terminal, is_middle, sequence_support,
                allow_chow
            )
            per_opponent.append(opp_result)
        
        # 7. 聚合结果
        aggregate = self._aggregate_opponents(per_opponent, phase, rule_variant, game_state)
        
        return BayesEvalResult(per_opponent=per_opponent, aggregate=aggregate)
    
    # ==================== 阶段推断 ====================
    
    def _infer_phase(self, game_state) -> str:
        """推断当前牌局阶段：early/mid/late
        
        基于 risk.md：
        - 序盘（前5巡）：early
        - 中盘（6-12巡）：mid
        - 尾盘（13巡后）：late
        
        一巡 = 4人各出一张牌（4张弃牌）
        """
        # 计算弃牌堆中的牌数（不含副露牌）
        discard_count = len(game_state.discard_pile)
        
        # 计算巡数：每4张弃牌算一巡
        rounds = discard_count / 4.0
        
        if rounds <= self.PHASE_EARLY_ROUNDS:
            return "early"
        elif rounds <= self.PHASE_MID_ROUNDS:
            return "mid"
        else:
            return "late"
    
    # ==================== 剩余牌计算 ====================
    
    def _compute_remaining_counts(self, card, game_state) -> tuple:
        """计算某张牌的可见数量和剩余数量
        
        Returns:
            (seen_count, remaining_count)
        """
        seen_count = 0
        
        # 统计弃牌堆
        for c in game_state.discard_pile:
            if c == card:
                seen_count += 1
        
        # 统计所有玩家的副露
        for p in game_state.players:
            for meld in getattr(p, "melds", []):
                for c in getattr(meld, "cards", []):
                    if c == card:
                        seen_count += 1
        
        # 花牌只有1张，其他牌4张
        max_count = 1 if card.suit == "花" else 4
        remaining_count = max(0, max_count - seen_count)
        
        return seen_count, remaining_count
    
    # ==================== 连张支撑计算 ====================
    
    def _compute_sequence_support(self, card, game_state) -> float:
        """计算连张支撑分数
        
        基于 risk.md：连张牌（桌上多3、5万，4万就是危险牌）
        检查相邻牌的剩余比例
        """
        if card.suit not in ("万", "筒", "条"):
            return 0.0
        
        try:
            rank = int(card.rank)
        except (ValueError, TypeError):
            return 0.0
        
        # 计算相邻牌的剩余比例
        neighbors = []
        for delta in [-2, -1, 1, 2]:
            neighbor_rank = rank + delta
            if 1 <= neighbor_rank <= 9:
                neighbors.append(neighbor_rank)
        
        if not neighbors:
            return 0.0
        
        # 计算每个邻居的剩余比例
        ratios = []
        for n_rank in neighbors:
            # 构造邻居牌ID
            neighbor_id = f"{card.suit}{n_rank}"
            seen = 0
            for c in game_state.discard_pile:
                if c.id == neighbor_id:
                    seen += 1
            for p in game_state.players:
                for meld in getattr(p, "melds", []):
                    for c in getattr(meld, "cards", []):
                        if c.id == neighbor_id:
                            seen += 1
            ratios.append((4 - seen) / 4)
        
        # 几何平均
        if not ratios:
            return 0.0
        product = 1.0
        for r in ratios:
            product *= max(r, 0.01)
        return product ** (1 / len(ratios))
    
    # ==================== 单对手评估 ====================
    
    def _evaluate_single_opponent(
        self, card, player, opponent, game_state,
        phase, seen_count, remaining_count,
        is_honor, is_terminal, is_middle, sequence_support,
        allow_chow
    ) -> OpponentResult:
        """评估单个对手对该牌的反应概率"""
        
        result = OpponentResult()
        result.opponent_id = getattr(opponent, "name", str(id(opponent)))
        result.seat = getattr(opponent, "position", "")
        
        # 1. 提取对手特征
        features = self._extract_opponent_features(
            card, opponent, game_state,
            is_honor, is_terminal, is_middle, sequence_support, seen_count
        )
        result.features_used = features
        
        # 2. 估计对手听牌先验
        tenpai_prior = self._estimate_opponent_tenpai(opponent, game_state, phase)
        holding_prior = self._holding_posterior(remaining_count, opponent, 1)
        result.priors = OpponentPriors(tenpai_prior=tenpai_prior, holding_prior=holding_prior)
        
        # 3. 计算各类claim概率
        claim_probs = ClaimProbs()
        
        # 判断座位关系（吃牌只能下家）
        is_next_player = getattr(player, "next_player", None) == opponent
        
        # 血流规则下不能吃
        rule_variant = getattr(game_state, "rule_name", "tencent_common")
        can_chow_this_opponent = allow_chow and is_next_player and not is_honor
        
        # 血流定缺：如果对手缺门等于该牌花色，所有反应概率降低
        que_mult = {"hu": 1.0, "pong": 1.0, "kong": 1.0, "chow": 1.0}
        opponent_que = getattr(opponent, "que_men", None)
        if rule_variant == "tencent_xueliu" and opponent_que == card.suit:
            que_mult = self.QUE_MISSING_MULT
        
        # 胡牌概率
        claim_probs.hu = self._naive_bayes_p_claim(
            features, tenpai_prior, holding_prior, "hu", remaining_count
        ) * que_mult["hu"]
        
        # 碰牌概率（需要手中>=2张）
        holding_2 = self._holding_posterior(remaining_count, opponent, 2)
        claim_probs.pong = self._naive_bayes_p_claim(
            features, 0.5, holding_2, "pong", remaining_count
        ) * que_mult["pong"]
        
        # 杠牌概率（需要手中>=3张）
        holding_3 = self._holding_posterior(remaining_count, opponent, 3)
        claim_probs.kong = self._naive_bayes_p_claim(
            features, 0.3, holding_3, "kong", remaining_count
        ) * que_mult["kong"]
        
        # 吃牌概率（仅下家，仅序数牌）
        if can_chow_this_opponent:
            claim_probs.chow = self._naive_bayes_p_claim(
                features, 0.4, sequence_support, "chow", remaining_count
            ) * que_mult["chow"]
        else:
            claim_probs.chow = 0.0
        
        result.claim_probs = claim_probs
        
        # 4. 计算期望损失
        is_dealer = getattr(opponent, "is_dealer", False)
        result.expected_loss = self._compute_expected_loss(claim_probs, phase, is_dealer)
        
        # 5. 生成说明
        notes_parts = []
        if features.is_safe_seen_opponent:
            notes_parts.append("熟张")
        if features.is_last_tile:
            notes_parts.append("绝张")
        if features.flush_tilt:
            notes_parts.append("清一色倾向")
        if features.pair_break:
            notes_parts.append("拆对子")
        if is_next_player and allow_chow:
            notes_parts.append("下家可吃")
        result.notes = "; ".join(notes_parts) if notes_parts else ""
        
        return result
    
    # ==================== 特征提取 ====================
    
    def _extract_opponent_features(
        self, card, opponent, game_state,
        is_honor, is_terminal, is_middle, sequence_support, seen_count
    ) -> OpponentFeatures:
        """提取对手特征用于贝叶斯计算
        
        基于 risk.md 的信号识别：
        - 熟张：对手打过的牌
        - 绝张：已出3张
        - 连续打同花色中张 → 清一色倾向
        - 拆对子 → 听牌优化
        """
        features = OpponentFeatures()
        features.is_honor = is_honor
        features.is_terminal = is_terminal
        features.is_middle = is_middle
        features.seen_count_table = seen_count
        features.sequence_support_score = sequence_support
        
        # 检查是否为熟张（对手打过）
        discarded = getattr(opponent, "discarded_cards", [])
        features.is_safe_seen_opponent = any(c == card for c in discarded)
        
        # 检查是否为绝张/已绝
        features.is_last_tile = (seen_count == 3)
        features.is_exhausted = (seen_count >= 4)
        
        # 副露数量
        melds = getattr(opponent, "melds", [])
        features.recent_meld_count = len(melds)
        
        # 最近动作
        last_action = getattr(opponent, "last_action", None)
        if last_action:
            features.last_action_type = getattr(last_action, "type", str(last_action))
        
        # 杠/花次数
        features.consecutive_gang_count = getattr(opponent, "consecutive_gang_count", 0)
        features.changed_flower_count = getattr(opponent, "changed_flower_count", 0)
        
        # 弃牌模式分析
        if len(discarded) >= 3:
            recent = discarded[-3:]
            
            # 清一色倾向：连续弃同花色中张
            suits = [c.suit for c in recent]
            if len(set(suits)) == 1 and suits[0] in ("万", "筒", "条"):
                ranks = []
                for c in recent:
                    try:
                        ranks.append(int(c.rank))
                    except (ValueError, TypeError):
                        pass
                if ranks and all(2 <= r <= 8 for r in ranks):
                    features.flush_tilt = True
            
            # 拆对子：最近两张牌相同
            if len(recent) >= 2 and recent[-1] == recent[-2]:
                features.pair_break = True
            
            # 无字弃牌 → 字/混一色倾向
            if all(c.suit not in ("风", "箭") for c in recent):
                features.honor_tilt = True
        
        return features
    
    # ==================== 听牌先验估计 ====================
    
    def _estimate_opponent_tenpai(self, opponent, game_state, phase) -> float:
        """估计对手听牌的先验概率
        
        基于 risk.md：
        - 序盘：低概率
        - 中盘：中等概率
        - 尾盘：高概率
        - 副露>=3：提高
        - 最近杠/花：提高
        """
        # 阶段基础概率
        phase_priors = {"early": 0.10, "mid": 0.35, "late": 0.60}
        base = phase_priors.get(phase, 0.35)
        
        # 副露调整
        melds = getattr(opponent, "melds", [])
        if len(melds) >= 3:
            base += 0.15
        elif len(melds) >= 2:
            base += 0.08
        
        # 最近杠/花调整
        last_action = getattr(opponent, "last_action", None)
        if last_action:
            action_type = getattr(last_action, "type", str(last_action))
            if action_type in ("kong", "flower"):
                base += 0.10
        
        # 连续杠调整
        gang_count = getattr(opponent, "consecutive_gang_count", 0)
        if gang_count > 0:
            base += 0.05 * min(gang_count, 3)
        
        # 约束在边界内
        floor = self.PRIORS["tenpai"]["floor"]
        ceiling = self.PRIORS["tenpai"]["ceiling"]
        return max(floor, min(ceiling, base))
    
    # ==================== 持牌后验概率 ====================
    
    def _holding_posterior(self, remaining_count, opponent, k_needed) -> float:
        """估计对手持有>=k张该牌的后验概率
        
        基于超几何分布的简化近似
        """
        if remaining_count < k_needed:
            return 0.0
        
        # 对手未知手牌数量估计
        melds = getattr(opponent, "melds", [])
        # 标准13张手牌，每副露减3张
        concealed_count = max(1, 13 - len(melds) * 3)
        
        # 简化：假设剩余牌均匀分布在未知区域
        # P(持有>=k) ≈ C(remaining, k) * C(pool-remaining, concealed-k) / C(pool, concealed)
        # 这里用简化近似
        
        if k_needed == 1:
            # 至少1张的概率
            p = remaining_count / max(remaining_count + 20, 1)
        elif k_needed == 2:
            # 至少2张的概率（较低）
            p = (remaining_count * (remaining_count - 1)) / max((remaining_count + 30) * (remaining_count + 29), 1)
            p = min(p * 10, 0.4)  # 调整比例
        else:
            # 至少3张的概率（很低）
            p = 0.05 * remaining_count / 4
        
        return max(0.01, min(0.8, p))
    
    # ==================== 贝叶斯概率计算 ====================
    
    def _naive_bayes_p_claim(
        self, features: OpponentFeatures, tenpai_prior: float,
        holding_prior: float, claim_type: str, remaining_count: int
    ) -> float:
        """朴素贝叶斯计算P(claim_type | features)
        
        P(claim | E) ∝ P(claim) × Π P(F_j | claim)
        """
        # 基础先验
        prior = tenpai_prior * holding_prior
        
        # 约束先验边界
        prior_bounds = self.PRIORS.get(claim_type, {"floor": 0.01, "ceiling": 0.5})
        prior = max(prior_bounds["floor"], min(prior_bounds["ceiling"], prior))
        
        # 应用特征似然乘数
        likelihood = 1.0
        
        # 熟张降低风险
        if features.is_safe_seen_opponent:
            likelihood *= self.LIKELIHOODS["safe_seen"].get(claim_type, 0.5)
        
        # 绝张降低风险
        if features.is_last_tile:
            likelihood *= self.LIKELIHOODS["last_tile"].get(claim_type, 0.3)
        
        # 已绝牌风险极低
        if features.is_exhausted:
            likelihood *= 0.02
        
        # 字牌
        if features.is_honor:
            likelihood *= self.LIKELIHOODS["honor"].get(claim_type, 1.0)
        
        # 幺九牌
        if features.is_terminal:
            likelihood *= self.LIKELIHOODS["terminal"].get(claim_type, 1.0)
        
        # 中张牌
        if features.is_middle:
            likelihood *= self.LIKELIHOODS["middle"].get(claim_type, 1.0)
        
        # 连张支撑（主要影响吃牌）
        if claim_type == "chow" and features.sequence_support_score > 0:
            likelihood *= (1 + features.sequence_support_score * 0.5)
        
        # 清一色倾向：同花色牌风险提高
        if features.flush_tilt:
            likelihood *= 1.3
        
        # 拆对子：听牌可能性高
        if features.pair_break:
            likelihood *= 1.4
        
        # 计算后验
        posterior = prior * likelihood
        
        # 约束在[0, 1]
        return max(0.0, min(1.0, posterior))
    
    # ==================== 期望损失计算 ====================
    
    def _compute_expected_loss(self, claim_probs: ClaimProbs, phase: str, is_dealer: bool) -> ExpectedLoss:
        """计算期望损失
        
        基于 risk.md：尾盘风险更高，庄家输赢×2
        """
        loss = ExpectedLoss()
        
        # 阶段乘数
        phase_mult = self.LATE_PHASE_MULTIPLIER if phase == "late" else 1.0
        
        # 庄家乘数
        dealer_mult = self.DEALER_MULTIPLIER if is_dealer else 1.0
        
        # 各类型期望损失
        loss.hu = claim_probs.hu * self.SEVERITY_WEIGHTS["hu"] * phase_mult * dealer_mult
        loss.pong = claim_probs.pong * self.SEVERITY_WEIGHTS["pong"] * phase_mult
        loss.kong = claim_probs.kong * self.SEVERITY_WEIGHTS["kong"] * phase_mult
        loss.chow = claim_probs.chow * self.SEVERITY_WEIGHTS["chow"] * phase_mult
        
        loss.total = loss.hu + loss.pong + loss.kong + loss.chow
        
        return loss
    
    # ==================== 聚合对手结果 ====================
    
    def _aggregate_opponents(
        self, per_opponent: List[OpponentResult],
        phase: str, rule_variant: str, game_state
    ) -> AggregateResult:
        """聚合所有对手的评估结果
        
        P_any = 1 - Π(1 - max_claim_prob_i)
        """
        agg = AggregateResult()
        agg.phase = phase
        agg.rule_variant = rule_variant
        agg.deck_remaining = len(game_state.deck)
        agg.discard_pile_size = len(game_state.discard_pile)
        
        if not per_opponent:
            return agg
        
        # 计算P_any：任一对手claim的概率
        p_none = 1.0
        total_loss = 0.0
        
        for opp in per_opponent:
            # 取该对手最大claim概率
            max_p = max(
                opp.claim_probs.hu,
                opp.claim_probs.pong,
                opp.claim_probs.kong,
                opp.claim_probs.chow
            )
            p_none *= (1 - max_p)
            total_loss += opp.expected_loss.total
        
        agg.P_any = 1 - p_none
        agg.total_expected_loss = total_loss
        
        return agg
    
    # ==================== 兼容旧接口 ====================
    
    def _calculate_card_probability(self, card, game_state) -> float:
        """计算某张牌被对手需要的概率（综合危险度）- 兼容旧接口"""
        seen_count, remaining_count = self._compute_remaining_counts(card, game_state)
        total_remaining = len(game_state.deck)
        if total_remaining == 0:
            return 0.5
        
        # 检查对手是否已经打过此牌
        safe_factor = 1.0
        for p in game_state.players:
            discarded = getattr(p, "discarded_cards", [])
            if any(c == card for c in discarded):
                safe_factor *= 0.7
        
        base_prob = remaining_count / max(total_remaining, 1)
        return base_prob * safe_factor
    
    def _estimate_opponent_hu_probability(self, player, game_state) -> float:
        """评估对手听牌的可能性 - 兼容旧接口"""
        phase = self._infer_phase(game_state)
        
        probability = 0.0
        for opponent in game_state.players:
            if opponent == player:
                continue
            tenpai = self._estimate_opponent_tenpai(opponent, game_state, phase)
            probability = max(probability, tenpai)
        
        # 分析弃牌模式
        for opponent in game_state.players:
            if opponent == player:
                continue
            discarded = getattr(opponent, "discarded_cards", [])
            if len(discarded) >= 3:
                recent = discarded[-3:]
                suits = [c.suit for c in recent]
                if len(set(suits)) == 1:
                    probability += 0.05  # 连续弃同花色，可能在定缺或整理
        
        return min(probability, 1.0)
    
    def _get_card_value_risk(self, card) -> float:
        """获取牌的价值风险系数"""
        # 实现牌价值风险计算逻辑
        # 字牌的价值风险通常高于序数牌
        if card.suit in ['风', '箭']:
            return 1.5
        return 1.0