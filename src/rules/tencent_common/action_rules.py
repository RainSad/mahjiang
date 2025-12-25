class TencentActionRules:
    """腾讯大众麻将动作规则"""
    
    def __init__(self, rule):
        self.rule = rule
    
    def can_chow(self, player, card, from_player) -> bool:
        """判断是否可以吃牌
        
        条件：
        1. 必须是上家打出的牌
        2. 只能吃同种花色的牌
        3. 必须是连续的三张牌
        """
        # 检查是否是上家
        if player.next_player != from_player:
            return False
        
        # 检查花色是否相同（只能吃序数牌）
        if card.suit not in ['万', '筒', '条'] or any(c.suit != card.suit for c in player.hand):
            return False
        
        # 检查是否能组成顺子
        current_rank = int(card.rank)
        needed_combinations = [
            {str(current_rank - 2), str(current_rank - 1)},  # 吃前两张
            {str(current_rank - 1), str(current_rank + 1)},  # 吃中间
            {str(current_rank + 1), str(current_rank + 2)}   # 吃后两张
        ]
        
        # 检查手牌中是否有对应的组合
        hand_ranks = {c.rank for c in player.hand if c.suit == card.suit}
        
        for combo in needed_combinations:
            if combo.issubset(hand_ranks):
                return True
        
        return False
    
    def can_pong(self, player, card, from_player) -> bool:
        """判断是否可以碰牌
        
        条件：
        1. 手牌中有至少两张相同的牌
        """
        # 检查手牌中是否有至少两张相同的牌
        count = sum(1 for c in player.hand if c == card)
        return count >= 2
    
    def can_kong(self, player, card, from_player) -> bool:
        """判断是否可以杠牌
        
        条件：
        1. 手牌中有三张相同的牌（明杠）
        2. 或者手牌中有四张相同的牌（暗杠）
        """
        count = sum(1 for c in player.hand if c == card)
        
        # 明杠：手牌中有三张，别人打出一张
        if from_player is not None and count == 3:
            return True
        
        # 暗杠：手牌中有四张
        if from_player is None and count == 4:
            return True
        
        return False
    
    def get_valid_actions(self, player, game_state) -> list:
        """获取当前玩家的有效操作"""
        valid_actions = []
        
        # 摸牌后的基本操作：胡（如果可以）或打牌
        valid_actions.append("discard")
        
        # 如果有上一张打出的牌，检查是否可以吃碰杠胡
        if game_state.last_discarded_card:
            last_card = game_state.last_discarded_card.card
            last_player = game_state.last_discarded_card.from_player
            
            # 检查是否可以吃牌
            if self.rule.allow_chow and self.can_chow(player, last_card, last_player):
                valid_actions.append("chow")
            
            # 检查是否可以碰牌
            if self.rule.allow_pong and self.can_pong(player, last_card, last_player):
                valid_actions.append("pong")
            
            # 检查是否可以杠牌
            if self.rule.allow_kong and self.can_kong(player, last_card, last_player):
                valid_actions.append("kong")
            
            # 检查是否可以胡牌（点炮）
            if self.rule.allow_other_hu:
                from src.rules.tencent_common.hu_rules import TencentHuRules
                hu_rules = TencentHuRules(self.rule)
                if hu_rules.can_hu(player, last_card):
                    valid_actions.append("hu")
        
        # 检查是否可以自摸胡牌（如果当前是摸牌阶段）
        if player.drawn_card and self.rule.allow_self_hu:
            from src.rules.tencent_common.hu_rules import TencentHuRules
            hu_rules = TencentHuRules(self.rule)
            if hu_rules.can_hu(player, player.drawn_card):
                valid_actions.append("hu")
        
        return valid_actions