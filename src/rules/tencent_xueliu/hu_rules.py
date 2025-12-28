# /workspaces/mahjiang/src/rules/tencent_xueliu/hu_rules.py
class TencentXueliuHuRules:
    """血流成河麻将胡牌规则"""
    
    def __init__(self, rule):
        self.rule = rule
    
    def can_hu(self, player, card) -> bool:
        """判断是否可以胡牌
        
        Args:
            player: 玩家对象
            card: 胡牌的牌
        
        Returns:
            是否可以胡牌
        
        血流麻将胡牌条件：
        1. 必须符合基本胡牌牌型（将牌+四组面子）
        2. 必须符合定缺规则（手牌中花色不超过2门）
        3. 必须至少有1倍番型
        """
        # 检查基本胡牌条件
        if not self._check_basic_hu_condition(player, card):
            return False
        
        # 检查定缺规则
        if not self._check_que_men_rule(player, card):
            return False
        
        # 检查是否至少有1倍番型
        if not self._check_has_at_least_one_fan(player, card):
            return False
        
        return True
    
    def _check_que_men_rule(self, player, card) -> bool:
        """检查定缺规则
        
        定缺规则：手牌中花色不能超过2门（不包括缺的花色）
        """
        que_men = getattr(player, 'que_men', None)
        if not que_men:
            return False  # 必须已经定缺
        
        # 组合临时手牌
        temp_hand = player.hand.copy()
        if card is not None and len(temp_hand) % 3 == 1:
            temp_hand.append(card)
        
        # 获取手牌中的花色（排除缺的花色）
        hand_suits = {c.suit for c in temp_hand if c.suit in ['万', '筒', '条'] and c.suit != que_men}
        
        # 手牌中的花色不能超过2门
        return len(hand_suits) <= 2
    
    def _check_has_at_least_one_fan(self, player, card) -> bool:
        """检查是否至少有1倍番型"""
        from src.rules.tencent_xueliu.score_rules import TencentXueliuScoreRules
        score_rules = TencentXueliuScoreRules(self.rule)
        fans = score_rules._calculate_fans(player, card)
        return fans >= 1
    
    def _check_basic_hu_condition(self, player, card) -> bool:
        """检查基本胡牌条件：将牌+四组面子"""
        # 临时组合手牌用于检查
        temp_hand = player.hand.copy()
        # 仅在手牌张数为 13 时补上待胡的牌
        if card is not None and len(temp_hand) % 3 == 1:
            temp_hand.append(card)
        
        # 按照花色和点数排序
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
        suit_order = {'万': 1, '筒': 2, '条': 3}
        
        def sort_key(card):
            suit_val = suit_order.get(card.suit, 99)
            rank_val = int(card.rank) if card.rank.isdigit() else 99
            return (suit_val, rank_val)
        
        return sorted(hand, key=sort_key)
    
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
        
        # 尝试组成顺子（仅适用于序数牌）
        if hand[0].suit in ['万', '筒', '条']:
            current_rank = int(hand[0].rank)
            needed_rank1 = current_rank + 1
            needed_rank2 = current_rank + 2
            
            # 检查是否在有效范围内
            if needed_rank2 <= 9:
                has_next1 = any(card.suit == hand[0].suit and int(card.rank) == needed_rank1 for card in hand[1:])
                has_next2 = any(card.suit == hand[0].suit and int(card.rank) == needed_rank2 for card in hand[1:])
                
                if has_next1 and has_next2:
                    temp = hand.copy()
                    # 移除组成顺子的三张牌
                    to_remove = []
                    for i, card in enumerate(temp):
                        if len(to_remove) < 3:
                            if (card.suit == hand[0].suit and 
                                int(card.rank) in [current_rank, needed_rank1, needed_rank2]):
                                to_remove.append(i)
                    
                    # 按逆序删除
                    for i in sorted(to_remove, reverse=True):
                        del temp[i]
                    
                    if self._check_melds(temp):
                        return True
        
        return False