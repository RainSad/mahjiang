class TencentHuRules:
    """腾讯大众麻将胡牌规则"""
    
    def __init__(self, rule):
        self.rule = rule
    
    def can_hu(self, player, card) -> bool:
        """判断是否可以胡牌
        
        Args:
            player: 玩家对象
            card: 胡牌的牌
        
        Returns:
            是否可以胡牌
        """
        # 检查基本条件：是否有将牌（对子）和四组面子
        if not self._check_basic_hu_condition(player, card):
            return False
        
        # 检查是否满足至少一种番型
        if not self._check_has_at_least_one_fan(player, card):
            return False
        
        return True
    
    def _check_has_at_least_one_fan(self, player, card) -> bool:
        """检查是否至少有一种番型
        
        Args:
            player: 玩家对象
            card: 胡牌的牌
        
        Returns:
            是否至少有一种番型
        """
        # 抢杠胡、杠上炮、杠上开花属于番型
        if self._is_qiang_gang_hu(player, card):
            return True
        if self._is_gang_shang_pao(player, card):
            return True
        if self._is_gang_shang_kai_hua(player, card):
            return True
        
        # 其他番型检查
        return self._has_any_fan_type(player, card)
    
    def _is_qiang_gang_hu(self, player, card) -> bool:
        """判断是否是抢杠胡"""
        # 抢杠胡：胡别人补杠的那张牌
        # 需要游戏状态支持，暂时返回False
        return False
    
    def _is_gang_shang_pao(self, player, card) -> bool:
        """判断是否是杠上炮"""
        # 杠上炮：胡别人杠牌后打出的那张牌
        # 需要游戏状态支持，暂时返回False
        return False
    
    def _is_gang_shang_kai_hua(self, player, card) -> bool:
        """判断是否是杠上开花"""
        # 杠上开花：杠牌/补花后摸牌胡牌
        # 需要游戏状态支持，暂时返回False
        return False
    
    def _has_any_fan_type(self, player, card) -> bool:
        """检查是否有其他番型"""
        # 这里需要调用计分规则中的番数计算逻辑
        # 暂时实现一些基本番型检查
        from src.rules.tencent_common.score_rules import TencentScoreRules
        score_rules = TencentScoreRules(self.rule)
        return score_rules._calculate_fans(player, card) > 0
    
    def _check_basic_hu_condition(self, player, card) -> bool:
        """检查基本胡牌条件：将牌+四组面子"""
        # 临时组合手牌用于检查
        temp_hand = player.hand.copy()
        temp_hand.append(card)
        
        # 按照花色和点数排序，便于检查
        sorted_hand = self._sort_hand(temp_hand)
        
        # 尝试找出将牌（对子）
        for i in range(len(sorted_hand) - 1):
            if sorted_hand[i] == sorted_hand[i + 1]:
                # 假设这对是将牌，移除后检查剩余的牌是否能组成面子
                temp = sorted_hand.copy()
                del temp[i + 1]
                del temp[i]
                
                if self._check_melds(temp):
                    return True
        
        return False
    
    def _sort_hand(self, hand) -> list:
        """将手牌按照花色和点数排序"""
        # 定义排序规则：万>筒>条>风>箭，点数从小到大
        suit_order = {'万': 1, '筒': 2, '条': 3, '风': 4, '箭': 5}
        rank_order = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                     '东': 1, '南': 2, '西': 3, '北': 4, '中': 1, '发': 2, '白': 3}
        
        return sorted(hand, key=lambda card: (suit_order[card.suit], rank_order[card.rank]))
    
    def _check_melds(self, hand) -> bool:
        """检查剩余的牌是否能组成面子（刻子或顺子）"""
        if not hand:
            return True
        
        # 尝试组成刻子
        if len(hand) >= 3 and hand[0] == hand[1] == hand[2]:
            temp = hand.copy()
            del temp[2]
            del temp[1]
            del temp[0]
            if self._check_melds(temp):
                return True
        
        # 尝试组成顺子（仅适用于序数牌：万、筒、条）
        if hand[0].suit in ['万', '筒', '条']:
            # 查找是否有连续的三张牌
            current_rank = int(hand[0].rank)
            needed_rank1 = current_rank + 1
            needed_rank2 = current_rank + 2
            
            has_next1 = any(card.suit == hand[0].suit and int(card.rank) == needed_rank1 for card in hand[1:])
            has_next2 = any(card.suit == hand[0].suit and int(card.rank) == needed_rank2 for card in hand[1:])
            
            if has_next1 and has_next2:
                temp = hand.copy()
                # 移除组成顺子的三张牌
                del temp[0]
                for i in range(len(temp)):
                    if temp[i].suit == hand[0].suit and int(temp[i].rank) == needed_rank1:
                        del temp[i]
                        break
                for i in range(len(temp)):
                    if temp[i].suit == hand[0].suit and int(temp[i].rank) == needed_rank2:
                        del temp[i]
                        break
                if self._check_melds(temp):
                    return True
        
        return False