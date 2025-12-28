# /workspaces/mahjiang/src/rules/tencent_xueliu/rule.py
from src.rules.base_rule import BaseRule
from src.rules.tencent_xueliu.hu_rules import TencentXueliuHuRules
from src.rules.tencent_xueliu.action_rules import TencentXueliuActionRules
from src.rules.tencent_xueliu.score_rules import TencentXueliuScoreRules

class TencentXueliuRule(BaseRule):
    """腾讯血流成河麻将规则实现
    
    特点：
    1. 只使用万、筒、条三种花色，共108张牌
    2. 不允许吃牌，只能碰、杠
    3. 必须定缺一门，摸到缺的花色必须打出
    4. 支持一炮多响
    5. 杠牌计分：明杠2倍、暗杠2倍、补杠1倍
    """
    
    def __init__(self, room_level='普通场'):
        super().__init__()
        # 血流麻将特定规则配置
        self.allow_chow = False      # 不允许吃牌
        self.allow_pong = True       # 允许碰牌
        self.allow_kong = True       # 允许杠牌
        self.allow_multiple_hu = True  # 允许一炮多响
        self.max_fans = 256          # 最大番数256倍
        self.mandatory_discard = True  # 必须有一张牌可以打出
        self.room_level = room_level  # 房间等级：普通场/富商场/尊爵场
        
        # 加载子规则
        self.hu_rules = TencentXueliuHuRules(self)
        self.action_rules = TencentXueliuActionRules(self)
        self.score_rules = TencentXueliuScoreRules(self)
    
    def can_chow(self, player, card, from_player) -> bool:
        """血流麻将不允许吃牌"""
        return False
    
    def can_pong(self, player, card, from_player) -> bool:
        """血流麻将碰牌规则"""
        return self.action_rules.can_pong(player, card, from_player)
    
    def can_kong(self, player, card, from_player) -> bool:
        """血流麻将杠牌规则"""
        return self.action_rules.can_kong(player, card, from_player)
    
    def can_hu(self, player, card) -> bool:
        """血流麻将胡牌规则"""
        return self.hu_rules.can_hu(player, card)
    
    def calculate_score(self, player, winning_card) -> int:
        """血流麻将计分规则"""
        return self.score_rules.calculate_score(player, winning_card)
    
    def get_valid_actions(self, player, game_state) -> list:
        """获取当前玩家的有效操作"""
        return self.action_rules.get_valid_actions(player, game_state)
    
    def create_initial_deck(self) -> list:
        """创建血流麻将初始牌组（只有万、筒、条，共108张）"""
        from src.core.data.card import Card
        deck = []
        
        # 序数牌（万、筒、条），每种花色1-9各4张
        for suit in ['万', '筒', '条']:
            for rank in range(1, 10):
                for _ in range(4):
                    deck.append(Card(suit, str(rank)))
        
        return deck
    
    def check_que_men(self, player) -> bool:
        """检查玩家手牌是否符合定缺规则
        
        定缺规则：手牌中的花色不能超过2门
        """
        # 获取手牌中的花色（不包括缺的花色）
        que_men = getattr(player, 'que_men', None)
        if not que_men:
            return True  # 未定缺时默认通过
        
        hand_suits = {card.suit for card in player.hand if card.suit in ['万', '筒', '条']}
        
        # 手牌中不应该有缺的花色
        if que_men in hand_suits:
            # 允许手牌中有缺牌，但必须在下一次出牌时打出
            return True
        
        return True
    
    def must_discard_que_men(self, player) -> bool:
        """检查玩家是否必须打出缺门的牌"""
        que_men = getattr(player, 'que_men', None)
        if not que_men:
            return False
        
        # 检查手牌中是否有缺门的牌
        has_que_card = any(card.suit == que_men for card in player.hand)
        return has_que_card