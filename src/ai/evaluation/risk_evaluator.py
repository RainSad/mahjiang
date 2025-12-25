class RiskEvaluator:
    """危险牌预测模块"""
    
    def __init__(self, rule):
        self.rule = rule
        
    def evaluate_card_risk(self, card, player, game_state) -> float:
        """评估打出某张牌的风险
        
        Args:
            card: 要评估的牌
            player: 当前玩家
            game_state: 当前游戏状态
        
        Returns:
            风险值（0-1，越高越危险）
        """
        # 1. 计算牌的出现概率
        card_probability = self._calculate_card_probability(card, game_state)
        
        # 2. 评估对手听牌可能性
        opponent_hu_probability = self._estimate_opponent_hu_probability(player, game_state)
        
        # 3. 综合计算风险值
        risk_value = card_probability * opponent_hu_probability * self._get_card_value_risk(card)
        
        return risk_value
    
    def _calculate_card_probability(self, card, game_state) -> float:
        """计算某张牌在剩余牌中的概率"""
        # 实现概率计算逻辑
        total_remaining = len(game_state.deck)
        if total_remaining == 0:
            return 0.0
            
        # 统计已经出现的该牌数量
        appeared_count = 0
        for p in game_state.players:
            appeared_count += sum(1 for c in p.hand if c == card)
            appeared_count += sum(1 for meld in p.melds for c in meld if c == card)
        
        for c in game_state.discard_pile:
            if c == card:
                appeared_count += 1
        
        remaining_count = 4 - appeared_count
        return remaining_count / total_remaining
    
    def _estimate_opponent_hu_probability(self, player, game_state) -> float:
        """评估对手听牌的可能性"""
        # 实现对手听牌概率估计逻辑
        # 基于对手已经打出的牌、吃碰杠情况等进行估计
        probability = 0.0
        # 简化实现：根据牌局阶段估计概率
        total_tiles = self.rule.tiles_count
        remaining_tiles = len(game_state.deck)
        progress = (total_tiles - remaining_tiles) / total_tiles
        
        # 牌局越靠后，对手听牌概率越高
        probability = min(progress * 2, 1.0)
        
        return probability
    
    def _get_card_value_risk(self, card) -> float:
        """获取牌的价值风险系数"""
        # 实现牌价值风险计算逻辑
        # 字牌的价值风险通常高于序数牌
        if card.suit in ['风', '箭']:
            return 1.5
        return 1.0