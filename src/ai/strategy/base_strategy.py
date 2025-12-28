from typing import List, Tuple

from src.core.data.action import Action
from src.ai.evaluation.risk_evaluator import RiskEvaluator


class BaseStrategy:
    """基础出牌策略：提供可解释的决策逻辑，优先安全与番型机会。"""

    def __init__(self, rule):
        self.rule = rule
        self.risk_evaluator = RiskEvaluator(rule)

    def recommend(self, player, game_state, valid_actions: List[str]) -> Tuple[Action, str]:
        """给出推荐操作及理由。"""
        # 最高优先：胡
        if "hu" in valid_actions:
            return Action("hu", player.drawn_card or game_state.last_discarded_card), "可胡牌，直接胡"

        # 次优先：杠（保留连杠机会）
        if "kong" in valid_actions:
            target = player.drawn_card or getattr(game_state.last_discarded_card, "card", None)
            return Action("kong", target), "可杠提升收益"

        # 碰/吃用于阻断或成型
        if "pong" in valid_actions:
            target = getattr(game_state.last_discarded_card, "card", None)
            return Action("pong", target), "碰牌成刻或阻断他家"
        if "chow" in valid_actions:
            target = getattr(game_state.last_discarded_card, "card", None)
            return Action("chow", target), "吃牌补顺子"

        # 补花
        if "flower" in valid_actions:
            return Action("flower"), "补花补牌"

        # 默认：打出风险最低、成型价值低的牌
        discard_card, reason = self._select_discard(player, game_state)
        return Action("discard", discard_card), reason

    def _select_discard(self, player, game_state):
        risks = []
        for c in player.hand:
            risk = self.risk_evaluator.evaluate_card_risk(c, player, game_state)
            potential = self._meld_potential(c, player)
            score = risk + (1 - potential)  # 低风险且潜力低优先打出
            risks.append((score, risk, potential, c))
        risks.sort(key=lambda x: x[0])
        _, risk, potential, card = risks[0]
        reason = f"风险={risk:.2f}, 成型潜力={potential:.2f}"
        return card, reason

    @staticmethod
    def _meld_potential(card, player) -> float:
        """粗略评估牌的成型潜力（顺子/刻子）。"""
        same = sum(1 for c in player.hand if c == card)
        if same >= 2:
            return 0.9  # 已有对子/刻子潜力高
        if card.suit in {"万", "筒", "条"}:
            ranks = {int(c.rank) for c in player.hand if c.suit == card.suit}
            r = int(card.rank)
            neighbors = sum(1 for dr in (-2, -1, 1, 2) if r + dr in ranks)
            return min(0.2 + 0.2 * neighbors, 0.8)
        return 0.1  # 字牌默认潜力低
