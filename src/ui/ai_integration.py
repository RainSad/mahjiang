from src.ai.strategy.advanced_strategy import AdvancedStrategy
from src.rules.tencent_common.rule import TencentCommonRule

class AIDecisionManager:
    """AI决策管理器，负责AI策略的初始化和管理"""
    
    def __init__(self):
        # 初始化腾讯大众麻将规则
        self.rule = TencentCommonRule()
        # 初始化高级AI策略
        self.strategy = AdvancedStrategy(self.rule)
    
    def get_best_action(self, player, game_state):
        """获取最佳行动
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            tuple: (行动类型, 牌, 理由)
        """
        return self.strategy.recommend_action(player, game_state)
    
    def get_best_discard(self, player, game_state):
        """获取最佳出牌
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            tuple: (推荐牌, 推荐理由)
        """
        return self.strategy.recommend_discard(player, game_state)
    
    def analyze_danger_cards(self, player, game_state):
        """分析危险牌
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            dict: 危险牌分析结果，键为牌，值为危险等级
        """
        danger_cards = {}
        for card in player.hand:
            risk = self.strategy.risk_evaluator.evaluate_card_risk(card, player, game_state)
            danger_cards[card] = risk
        
        # 按危险等级排序
        sorted_danger_cards = dict(sorted(danger_cards.items(), key=lambda item: item[1], reverse=True))
        return sorted_danger_cards
    
    def get_hand_evaluation(self, player, game_state):
        """获取手牌评估
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            float: 手牌价值评分
        """
        return self.strategy.evaluate_hand(player, game_state)
