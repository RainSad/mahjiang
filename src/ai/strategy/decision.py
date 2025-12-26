# src/ai/decision.py
from src.core.data.action import Action

class AI_Decision:
    """AI决策类"""
    
    def __init__(self, strategy=None, rule=None):
        """初始化AI决策
        
        Args:
            strategy: AI策略（可选，用于未来扩展不同策略）
            rule: 游戏规则实例
        """
        self.strategy = strategy
        self.rule = rule
    
    def make_decision(self, player, game_state, valid_actions):
        """AI做出决策
        
        Args:
            player: 当前玩家
            game_state: 游戏状态
            valid_actions: 有效操作列表
        
        Returns:
            Action: 选择的操作
        """
        # 简单策略：优先级 胡 > 杠 > 碰 > 吃 > 打牌
        
        # 1. 检查是否可以胡牌
        for action in valid_actions:
            if action.type == "hu":
                return action
        
        # 2. 检查是否可以杠
        for action in valid_actions:
            if action.type == "kong":
                return action
        
        # 3. 检查是否可以碰
        for action in valid_actions:
            if action.type == "pong":
                return action
        
        # 4. 检查是否可以吃（较低优先级）
        for action in valid_actions:
            if action.type == "chow":
                return action
        
        # 5. 检查是否需要补花
        for action in valid_actions:
            if action.type == "flower":
                return action
        
        # 6. 默认打牌：选择打出drawn_card或手牌中第一张
        if player.drawn_card and player.drawn_card in player.hand:
            return Action("discard", player.drawn_card)
        elif player.hand:
            return Action("discard", player.hand[0])
        
        # 7. 如果没有有效操作，返回None
        return None