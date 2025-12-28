from src.ai.strategy.decision import AI_Decision
from src.ai.strategy.advanced_strategy import AdvancedStrategy
from src.ai.evaluation.hand_evaluator import HandEvaluator
from src.core.data.action import Action

class AIDecisionManager:
    """AI决策管理器，负责AI策略的初始化和管理"""
    
    def __init__(self, rule):
        # 使用外部注入的规则，便于切换血流/大众
        self.rule = rule
        # 初始化高级AI策略并包装在AI_Decision中
        self.strategy = AdvancedStrategy(self.rule)
        self.ai_decision = AI_Decision(self.strategy)
    
    def get_best_action(self, player, game_state):
        """获取最佳行动
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            tuple: (Action对象, 理由)
        """
        valid_actions = self.rule.get_valid_actions(player, game_state)
        action, reason = self.ai_decision.recommend_with_reason(player, game_state, valid_actions)
        return action, reason
    
    def get_best_discard(self, player, game_state):
        """获取最佳出牌
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            tuple: (推荐牌, 推荐理由)
        """
        valid_actions = self.rule.get_valid_actions(player, game_state)
        discard_actions = [a for a in valid_actions if a.type == "discard"]
        if discard_actions:
            action, reason = self.ai_decision.recommend_with_reason(player, game_state, discard_actions)
            return action.card, reason
        return None, "无可出牌"
    
    def analyze_danger_cards(self, player, game_state):
        """分析危险牌
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            dict: 危险牌分析结果，键为牌，值为危险等级
        """
        
        evaluator = HandEvaluator()
        
        danger_cards = {}
        for card in player.hand:
            # Use hand evaluator to assess card value (lower shanten when removed = less valuable = safer)
            temp_hand = player.hand.copy()
            temp_hand.remove(card)
            shanten_without_card = evaluator.calculate_shanten(temp_hand)
            original_shanten = evaluator.calculate_shanten(player.hand)
            # Higher difference means card is more important (more dangerous to discard)
            risk = shanten_without_card - original_shanten
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
        # AdvancedStrategy uses hand_evaluator internally
        # Return shanten distance as a proxy for hand value (lower is better)
        evaluator = HandEvaluator()
        return evaluator.calculate_shanten(player.hand)
