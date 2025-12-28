from typing import List, Tuple

from src.core.data.action import Action
from src.ai.evaluation.risk_evaluator import RiskEvaluator
from src.rules.tencent_common.score_rules import TencentScoreRules
from src.ai.strategy.base_strategy import BaseStrategy


class AdvancedStrategy(BaseStrategy):
    """高级策略：平衡风险与番型收益，提供理由说明。"""

    def __init__(self, rule):
        super().__init__(rule)
        self.score_rules = TencentScoreRules(rule)

    def recommend(self, player, game_state, valid_actions: List[str]) -> Tuple[Action, str]:
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

        # 高级：为每张候选打牌计算综合评分 = 风险权重 + 潜在番型收益权重
        discard, detail = self._select_best_discard(player, game_state)
        return Action("discard", discard), detail

    def _select_best_discard(self, player, game_state):
        candidates = []
        for card in player.hand:
            risk = self.risk_evaluator.evaluate_card_risk(card, player, game_state)
            potential = self._fan_potential(player, card)
            # 评分：风险越低越好，潜在番型越高越好
            score = risk * 0.6 + (1 - potential) * 0.4
            candidates.append((score, risk, potential, card))
        candidates.sort(key=lambda x: x[0])
        _, risk, potential, card = candidates[0]
        reason = f"风险={risk:.2f}, 番型潜力={potential:.2f}，综合得分最优"
        return card, reason

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
            fans = self.score_rules._calculate_fans(temp_player, discard_candidate)
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
