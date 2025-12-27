from src.ai.strategy.base_strategy import BaseStrategy
from src.ai.evaluation.risk_evaluator import RiskEvaluator
from src.core.data.card import Card

class AdvancedStrategy(BaseStrategy):
    """高级AI策略"""
    
    def __init__(self, rule):
        super().__init__(rule)
        self.risk_evaluator = RiskEvaluator(rule)
    
    def recommend_action(self, player, game_state):
        """推荐动作
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            tuple: (推荐动作类型, 推荐牌, 推荐理由)
        """
        # 如果可以胡牌，直接推荐胡牌
        # TODO: 实现胡牌检测逻辑
        
        # 否则，推荐最佳出牌
        return "discard", *self.recommend_discard(player, game_state)
    
    def recommend_discard(self, player, game_state):
        """推荐最佳出牌
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            tuple: (推荐牌, 推荐理由)
        """
        if not player.hand:
            return None, "手牌为空"
        
        # 计算每张牌的综合评分
        card_scores = []
        for card in player.hand:
            # 计算打出该牌的价值（越高越好）
            discard_value = self.calculate_discard_value(card, player, game_state)
            # 计算打出该牌的风险（越低越好）
            risk = self.risk_evaluator.evaluate_card_risk(card, player, game_state)
            # 综合评分：价值高且风险低的牌更适合打出
            score = discard_value - risk * 10  # 风险权重更高
            card_scores.append((score, card))
        
        # 找出评分最低的牌（最应该打出的牌）
        card_scores.sort()
        best_card = card_scores[0][1]
        
        # 生成推荐理由
        reason = self._generate_reason(best_card, player, game_state)
        
        return best_card, reason
    
    def evaluate_hand(self, player, game_state):
        """评估手牌价值
        
        Args:
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            float: 手牌价值评分
        """
        # 基础评分
        score = 0.0
        
        # 1. 评估手牌的进张数量
        # TODO: 实现进张数量计算
        
        # 2. 评估手牌的番型潜力
        # TODO: 实现番型潜力评估
        
        # 3. 评估手牌的结构完整性
        # TODO: 实现结构完整性评估
        
        return score
    
    def calculate_discard_value(self, card, player, game_state):
        """计算打出某张牌的价值
        
        Args:
            card: 要评估的牌
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            float: 打出该牌的价值评分（越高越好，0表示最适合打出）
        """
        # 创建临时手牌（移除要评估的牌）
        temp_hand = [c for c in player.hand if c != card]
        
        # 1. 计算剩余手牌的价值
        remaining_value = self.evaluate_hand(player, game_state)
        
        # 2. 评估该牌在当前手牌中的作用
        card_value = self._evaluate_card_in_hand(card, player, game_state)
        
        # 3. 综合考虑牌的类型（字牌、序数牌等）
        type_bonus = self._get_card_type_bonus(card)
        
        # 总分：剩余价值 + 牌型奖励 - 该牌的作用
        total_score = remaining_value + type_bonus - card_value
        
        return total_score
    
    def _evaluate_card_in_hand(self, card, player, game_state):
        """评估牌在当前手牌中的作用
        
        Args:
            card: 要评估的牌
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            float: 牌的作用评分（越高表示该牌越重要）
        """
        # 基础作用评分
        score = 0.0
        
        # 统计手牌中该牌的数量
        card_count = sum(1 for c in player.hand if c == card)
        
        # 1. 对子、刻子、杠子的价值
        if card_count == 2:  # 对子
            score += 2.0
        elif card_count == 3:  # 刻子
            score += 3.0
        elif card_count == 4:  # 杠子
            score += 4.0
        
        # 2. 连牌的价值
        # TODO: 实现连牌价值评估
        
        # 3. 搭子的价值
        # TODO: 实现搭子价值评估
        
        return score
    
    def _get_card_type_bonus(self, card):
        """获取牌类型的奖励
        
        Args:
            card: 要评估的牌
        
        Returns:
            float: 类型奖励
        """
        # 字牌的处理优先级较低
        if card.suit in ['风', '箭']:
            return -1.0
        return 0.0
    
    def _generate_reason(self, card, player, game_state):
        """生成推荐理由
        
        Args:
            card: 推荐打出的牌
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            str: 推荐理由
        """
        # 计算该牌的风险
        risk = self.risk_evaluator.evaluate_card_risk(card, player, game_state)
        
        # 统计该牌在手中的数量
        card_count = sum(1 for c in player.hand if c == card)
        
        # 基础理由
        reason_parts = []
        
        # 风险相关理由
        if risk > 0.7:
            reason_parts.append("该牌风险较高")
        elif risk < 0.3:
            reason_parts.append("该牌风险较低")
        
        # 手牌作用相关理由
        if card_count == 1:
            reason_parts.append("单张牌，难以形成搭子")
        elif card_count == 2:
            reason_parts.append("对子，但价值不高")
        
        # 牌类型相关理由
        if card.suit in ['风', '箭']:
            reason_parts.append("字牌，难以形成顺子")
        
        # 组合理由
        if reason_parts:
            return f"推荐打出{card.get_display_name()}，理由：{'; '.join(reason_parts)}"
        else:
            return f"推荐打出{card.get_display_name()}，综合评估最佳选择"
