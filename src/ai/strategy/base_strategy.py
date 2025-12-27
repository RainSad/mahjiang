class BaseStrategy:
    """AI策略基类"""
    
    def __init__(self, rule):
        self.rule = rule
    
    def recommend_action(self, player, game_state):
        """推荐动作
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            tuple: (推荐动作类型, 推荐牌, 推荐理由)
        """
        raise NotImplementedError("子类必须实现recommend_action方法")
    
    def evaluate_hand(self, player, game_state):
        """评估手牌价值
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            float: 手牌价值评分
        """
        raise NotImplementedError("子类必须实现evaluate_hand方法")
    
    def calculate_discard_value(self, card, player, game_state):
        """计算打出某张牌的价值

        Args:
            card: 要评估的牌
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            float: 打出该牌的价值评分（越高越好）
        """
        raise NotImplementedError("子类必须实现calculate_discard_value方法")
