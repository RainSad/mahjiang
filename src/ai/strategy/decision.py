from typing import List, Tuple

from src.core.data.action import Action
from src.ai.strategy.base_strategy import BaseStrategy
from src.ai.strategy.advanced_strategy import AdvancedStrategy


class AI_Decision:
    """AI决策类：封装策略选择，返回操作和可解释理由。"""

    def __init__(self, strategy=None, rule=None):
        """初始化AI决策

        Args:
            strategy: AI策略实例或字符串（"base"/"advanced"），未提供时默认高级策略
            rule: 游戏规则实例
        """
        self.rule = rule
        self.strategy = self._ensure_strategy(strategy)

    def _ensure_strategy(self, strategy):
        if strategy is None:
            return AdvancedStrategy(self.rule)
        if isinstance(strategy, str):
            if strategy == "base":
                return BaseStrategy(self.rule)
            if strategy == "advanced":
                return AdvancedStrategy(self.rule)
            # Fallback for unknown string values
            return AdvancedStrategy(self.rule)
        return strategy

    def make_decision(self, player, game_state, valid_actions: List[str]) -> Action:
        """AI做出决策

        Returns:
            Action: 选择的操作
        """
        action, _ = self.recommend_with_reason(player, game_state, valid_actions)
        return action

    def recommend_with_reason(self, player, game_state, valid_actions: List[str]) -> Tuple[Action, str]:
        """返回操作及理由，便于UI展示。"""
        if not self.strategy:
            self.strategy = AdvancedStrategy(self.rule)
        return self.strategy.recommend(player, game_state, valid_actions)