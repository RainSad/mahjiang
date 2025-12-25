class TencentScoreRules:
    """腾讯大众麻将计分规则"""
    
    def __init__(self, rule):
        self.rule = rule
    
    def calculate_score(self, player, winning_card) -> int:
        """计算胡牌分数
        
        Args:
            player: 胡牌玩家
            winning_card: 胡牌的牌
        
        Returns:
            胡牌分数
        """
        # 基础分数
        base_score = 1
        
        # 计算番数
        fans = self._calculate_fans(player, winning_card)
        
        # 计算最终分数（基础分 × 2^番数）
        final_score = base_score * (2 ** fans)
        
        return final_score
    
    def _calculate_fans(self, player, winning_card) -> int:
        """计算番数
        
        Args:
            player: 胡牌玩家
            winning_card: 胡牌的牌
        
        Returns:
            番数（最大不超过规则设定的max_fans）
        """
        total_fans = 0
        
        # 基本番型
        total_fans += self._check_basic_fans(player, winning_card)
        
        # 特殊番型
        total_fans += self._check_special_fans(player)
        
        # 限制最大番数
        return min(total_fans, self.rule.max_fans)
    
    def _check_basic_fans(self, player, winning_card) -> int:
        """检查基本番型"""
        fans = 0
        
        # 自摸
        if winning_card == player.drawn_card:
            fans += 1
        
        # 门清
        if not player.melds:
            fans += 1
        
        # 大对子（碰碰胡）
        if self._is_all_pairs(player):
            fans += 2
        
        # 七对子
        if self._is_seven_pairs(player):
            fans += 4
        
        return fans
    
    def _check_special_fans(self, player) -> int:
        """检查特殊番型"""
        fans = 0
        
        # 清一色
        if self._is_pure_suit(player):
            fans += 6
        
        # 混一色
        if self._is_mixed_suit(player):
            fans += 3
        
        # 一条龙
        if self._is_dragon(player):
            fans += 3
        
        return fans
    
    def _is_all_pairs(self, player) -> bool:
        """判断是否是大对子（碰碰胡）"""
        # 大对子是四组刻子+一对将牌
        # 这里简化检查：是否所有的牌都是刻子或对子
        # 注意：需要考虑吃碰杠的牌
        return True  # 简化实现，实际需要更复杂的检查
    
    def _is_seven_pairs(self, player) -> bool:
        """判断是否是七对子"""
        # 七对子是七对不同的对子
        hand = player.hand.copy()
        if len(hand) != 14:
            return False
        
        # 检查是否有七个不同的对子
        pairs = set()
        for card in hand:
            if card in pairs:
                pairs.remove(card)
            else:
                pairs.add(card)
        
        return len(pairs) == 0
    
    def _is_pure_suit(self, player) -> bool:
        """判断是否是清一色"""
        if not player.hand:
            return False
        
        suit = player.hand[0].suit
        return all(card.suit == suit for card in player.hand)
    
    def _is_mixed_suit(self, player) -> bool:
        """判断是否是混一色"""
        # 混一色是一种花色 + 风牌/箭牌
        hand = player.hand
        if not hand:
            return False
        
        suits = {card.suit for card in hand}
        
        # 检查是否只有一种花色 + 风/箭牌
        ordinal_suits = suits.intersection(['万', '筒', '条'])
        special_suits = suits.intersection(['风', '箭'])
        
        return len(ordinal_suits) == 1 and special_suits.issubset(['风', '箭'])
    
    def _is_dragon(self, player) -> bool:
        """判断是否是一条龙"""
        # 一条龙是某一花色的1-9牌都有
        hand = player.hand
        
        # 检查每种花色是否有1-9
        for suit in ['万', '筒', '条']:
            ranks = {card.rank for card in hand if card.suit == suit}
            if set(map(str, range(1, 10))).issubset(ranks):
                return True
        
        return False