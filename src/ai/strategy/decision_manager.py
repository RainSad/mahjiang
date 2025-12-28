from typing import Dict, List

from src.ai.evaluation.risk_evaluator import RiskEvaluator
from src.ai.strategy.decision import AI_Decision


class AIDecisionManager:
    """统一管理AI决策、推荐理由和风险分析，供GUI/CLI调用。"""

    def __init__(self, rule, strategy: str = "advanced"):
        self.rule = rule
        self.risk = RiskEvaluator(rule)
        self.ai = AI_Decision(strategy=strategy, rule=rule)

    def recommend(self, player, game_state) -> Dict:
        valid_actions = self.rule.get_valid_actions(player, game_state)
        action, reason = self.ai.recommend_with_reason(player, game_state, valid_actions)
        risks = self.risk_by_card(player, game_state)
        return {
            "action": action,
            "reason": reason,
            "risk": risks,
        }

    def risk_by_card(self, player, game_state) -> List[Dict]:
        result = []
        for card in player.hand:
            risk_value = self.risk.evaluate_card_risk(card, player, game_state)
            result.append({"card": card, "risk": round(risk_value, 3)})
        # 风险从高到低排序便于展示
        result.sort(key=lambda x: x["risk"], reverse=True)
        return result
