from typing import List, Tuple

from src.core.data.action import Action
from src.ai.evaluation.risk_evaluator import RiskEvaluator, BayesEvalResult
from src.ai.strategy.base_strategy import BaseStrategy


class AdvancedStrategy(BaseStrategy):
    """高级策略：基于贝叶斯定理平衡风险与番型收益，提供理由说明。
    
    核心原则（来自 risk.md）：
    - 进攻优先、防守为辅，结合对手舍牌判断风险
    - 序盘打孤张，中盘防同色，尾盘只打熟
    """
    
    # 风险和番型潜力的权重
    RISK_WEIGHT = 0.6
    FAN_WEIGHT = 0.4
    
    # 阶段风险调整系数
    PHASE_RISK_MULT = {"early": 0.7, "mid": 1.0, "late": 1.4}

    def __init__(self, rule):
        super().__init__(rule)
        # 规则提供的计分模块，用于估算番型潜力
        self.score_rules = getattr(rule, "score_rules", None)

    def recommend(self, player, game_state, valid_actions: List[str]) -> Tuple[Action, str]:
        # 血流定缺强制执行：如果有缺门牌，必须先打出缺门牌
        if "must_discard_que" in valid_actions:
            que_men = getattr(player, "que_men", None)
            if que_men:
                que_card = next((c for c in player.hand if c.suit == que_men), None)
                if que_card:
                    return Action("discard", que_card), f"定缺{que_men}，必须先打出缺门牌"
        
        # 沿用基础的动作优先级
        if "hu" in valid_actions:
            return Action("hu", player.drawn_card or getattr(game_state.last_discarded_card, "card", None)), "可胡牌，直接胡"
        if "kong" in valid_actions:
            target = player.drawn_card or getattr(game_state.last_discarded_card, "card", None)
            return Action("kong", target), "杠提升收益并可能连杠加成"
        if "pong" in valid_actions:
            target = getattr(game_state.last_discarded_card, "card", None)
            return Action("pong", target), "碰成刻提高番型机会"
        if "chow" in valid_actions:
            target = getattr(game_state.last_discarded_card, "card", None)
            return Action("chow", target), "吃补顺子保持听口"
        if "flower" in valid_actions:
            return Action("flower"), "补花补牌"

        # 高级：基于贝叶斯定理为每张候选打牌计算综合评分
        discard, detail = self._select_best_discard(player, game_state)
        return Action("discard", discard), detail

    def _select_best_discard(self, player, game_state) -> Tuple:
        """选择最优弃牌
        
        基于 risk.md 原则：
        - 牌型好：进攻优先，打孤张废牌
        - 牌型中等：攻守平衡
        - 牌型差：防守优先，只打熟张
        """
        candidates = []
        
        for card in player.hand:
            # 使用贝叶斯风险评估
            bayes_result = self._bayes_risk(card, player, game_state)
            risk = bayes_result.aggregate.total_expected_loss
            phase = bayes_result.aggregate.phase
            
            # 计算番型潜力
            potential = self._fan_potential(player, card)
            
            # 阶段调整风险权重
            phase_mult = self.PHASE_RISK_MULT.get(phase, 1.0)
            adjusted_risk = risk * phase_mult
            
            # 综合评分：风险越低越好，潜在番型越高越好
            score = adjusted_risk * self.RISK_WEIGHT + (1 - potential) * self.FAN_WEIGHT
            
            # 收集特征说明
            notes = self._collect_notes(bayes_result, card)
            
            candidates.append({
                "score": score,
                "risk": risk,
                "potential": potential,
                "card": card,
                "phase": phase,
                "notes": notes,
                "bayes": bayes_result
            })
        
        # 按综合得分排序，选最优
        candidates.sort(key=lambda x: x["score"])
        
        if not candidates:
            # 兜底：如果没有候选（不应发生），返回第一张手牌
            return player.hand[0] if player.hand else None, "无可选牌"
        
        best = candidates[0]
        reason = self._build_reason(best)
        return best["card"], reason
    
    def _bayes_risk(self, card, player, game_state) -> BayesEvalResult:
        """调用贝叶斯风险评估
        
        Returns:
            BayesEvalResult 包含每个对手的概率和聚合结果
        """
        return self.risk_evaluator.evaluate_discard_reaction_prob(card, player, game_state)
    
    def _collect_notes(self, bayes_result: BayesEvalResult, card) -> List[str]:
        """收集特征说明用于推理展示"""
        notes = []
        
        # 聚合特征
        for opp in bayes_result.per_opponent:
            if opp.features_used.is_safe_seen_opponent:
                notes.append("熟张")
                break
        
        for opp in bayes_result.per_opponent:
            if opp.features_used.is_last_tile:
                notes.append("绝张")
                break
        
        for opp in bayes_result.per_opponent:
            if opp.features_used.flush_tilt:
                notes.append("对手清一色倾向")
                break
        
        for opp in bayes_result.per_opponent:
            if opp.features_used.pair_break:
                notes.append("对手拆对子")
                break
        
        # 牌类型
        if card.suit in ("风", "箭"):
            notes.append("字牌")
        elif str(card.rank) in ("1", "9"):
            notes.append("幺九")
        elif str(card.rank) in [str(i) for i in range(2, 9)]:
            notes.append("中张")
        
        return notes
    
    def _build_reason(self, best: dict) -> str:
        """构建推理说明"""
        parts = []
        
        # 阶段
        phase_names = {"early": "序盘", "mid": "中盘", "late": "尾盘"}
        phase_name = phase_names.get(best["phase"], best["phase"])
        parts.append(f"阶段={phase_name}")
        
        # 风险和番型潜力
        parts.append(f"风险={best['risk']:.2f}")
        parts.append(f"番型潜力={best['potential']:.2f}")
        
        # 特征说明
        if best["notes"]:
            parts.append(f"特征=[{', '.join(best['notes'][:3])}]")
        
        return "，".join(parts) + " → 综合最优"

    def _fan_potential(self, player, discard_candidate) -> float:
        """尝试用计分规则估计打出后番型潜力：
        - 将该牌视为弃掉，估算剩余手牌的番型基础得分上限。
        """
        # 模拟移除该牌再用计分规则检查基础番
        temp_player = type(player)(player.name, player.is_ai)
        temp_player.hand = list(player.hand)
        # 去掉一个候选实例
        for i, c in enumerate(temp_player.hand):
            if c == discard_candidate:
                temp_player.hand.pop(i)
                break
        temp_player.melds = list(player.melds)
        temp_player.drawn_card = None
        try:
            fans = self.score_rules._calculate_fans(temp_player, discard_candidate) if self.score_rules else 0
        except Exception:
            fans = 0
        # 映射为0-1区间
        if fans >= 8:
            return 1.0
        if fans >= 4:
            return 0.7
        if fans >= 2:
            return 0.5
        return 0.2
