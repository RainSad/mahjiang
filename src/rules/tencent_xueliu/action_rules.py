# /workspaces/mahjiang/src/rules/tencent_xueliu/action_rules.py
class TencentXueliuActionRules:
    """血流成河麻将动作规则"""
    
    def __init__(self, rule):
        self.rule = rule
    
    def can_chow(self, player, card, from_player) -> bool:
        """血流麻将不允许吃牌"""
        return False
    
    def can_pong(self, player, card, from_player) -> bool:
        """判断是否可以碰牌
        
        条件：
        1. 手牌中有至少两张相同的牌
        2. 不检查定缺限制（碰牌不受定缺影响）
        """
        # 检查手牌中是否有至少两张相同的牌
        count = sum(1 for c in player.hand if c == card)
        return count >= 2
    
    def can_kong(self, player, card, from_player) -> bool:
        """判断是否可以杠牌
        
        杠牌类型：
        1. 明杠（刮风）：手牌中有三张，别人打出一张
        2. 暗杠（下雨）：手牌中有四张
        3. 补杠：已经碰过，再摸到第四张
        """
        count = sum(1 for c in player.hand if c == card)
        
        # 明杠：手牌中有三张，别人打出一张
        if from_player is not None and from_player != player and count == 3:
            return True
        
        # 暗杠：手牌中有四张
        if from_player is None and count == 4:
            return True
        
        # 补杠：检查是否已经碰过这张牌
        if from_player is None or from_player == player:
            for meld in getattr(player, 'melds', []):
                meld_type = getattr(meld, 'type', '')
                meld_cards = getattr(meld, 'cards', [])
                if meld_type == '碰' and meld_cards and meld_cards[0] == card:
                    # 已经碰过，检查手牌中是否有第四张
                    if count >= 1:
                        return True
        
        return False
    
    def get_valid_actions(self, player, game_state) -> list:
        """获取当前玩家的有效操作"""
        valid_actions = []
        
        # 基本操作：打牌
        valid_actions.append("discard")
        
        # 检查是否必须打出缺门的牌
        if self.rule.must_discard_que_men(player):
            valid_actions.append("must_discard_que")
        
        # 如果有上一张打出的牌，检查是否可以碰杠胡
        if game_state.last_discarded_card:
            last_action = game_state.last_discarded_card
            last_card = getattr(last_action, 'card', None) or game_state.last_discarded_card
            last_player = getattr(last_action, 'from_player', None)
            
            # 检查是否可以碰牌
            if self.rule.allow_pong and self.can_pong(player, last_card, last_player):
                valid_actions.append("pong")
            
            # 检查是否可以杠牌
            if self.rule.allow_kong and self.can_kong(player, last_card, last_player):
                valid_actions.append("kong")
            
            # 检查是否可以胡牌（点炮）
            if self.rule.allow_other_hu:
                if self.rule.hu_rules.can_hu(player, last_card):
                    valid_actions.append("hu")
        
        # 检查是否可以自摸胡牌
        if player.drawn_card and self.rule.allow_self_hu:
            if self.rule.hu_rules.can_hu(player, player.drawn_card):
                valid_actions.append("hu")
        
        # 检查是否可以暗杠或补杠
        if self.rule.allow_kong:
            from collections import Counter
            hand_counts = Counter(player.hand)
            
            # 检查暗杠（手牌中有四张）
            for card, count in hand_counts.items():
                if count == 4:
                    valid_actions.append("an_gang")
                    break
            
            # 检查补杠（已碰过，手牌中有第四张）
            for meld in getattr(player, 'melds', []):
                meld_type = getattr(meld, 'type', '')
                meld_cards = getattr(meld, 'cards', [])
                if meld_type == '碰' and meld_cards:
                    pong_card = meld_cards[0]
                    if hand_counts[pong_card] >= 1:
                        valid_actions.append("bu_gang")
                        break
        
        return valid_actions