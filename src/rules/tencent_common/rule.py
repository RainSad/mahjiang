from src.rules.base_rule import BaseRule
from src.rules.tencent_common.hu_rules import TencentHuRules
from src.rules.tencent_common.action_rules import TencentActionRules
from src.rules.tencent_common.score_rules import TencentScoreRules

class TencentCommonRule(BaseRule):
    """腾讯大众麻将规则实现"""
    
    def __init__(self):
        super().__init__()
        # 腾讯大众麻将特定规则配置
        self.allow_chow = True  # 允许吃牌
        self.allow_pong = True  # 允许碰牌
        self.allow_kong = True  # 允许杠牌
        self.max_fans = 10      # 最大番数
        self.mandatory_discard = True  # 必须有一张牌可以打出
        
        # 加载子规则
        self.hu_rules = TencentHuRules(self)
        self.action_rules = TencentActionRules(self)
        self.score_rules = TencentScoreRules(self)
    
    def can_chow(self, player, card, from_player) -> bool:
        """腾讯大众麻将吃牌规则"""
        return self.action_rules.can_chow(player, card, from_player)
    
    def can_pong(self, player, card, from_player) -> bool:
        """腾讯大众麻将碰牌规则"""
        return self.action_rules.can_pong(player, card, from_player)
    
    def can_kong(self, player, card, from_player) -> bool:
        """腾讯大众麻将杠牌规则"""
        return self.action_rules.can_kong(player, card, from_player)
    
    def can_hu(self, player, card) -> bool:
        """腾讯大众麻将胡牌规则"""
        return self.hu_rules.can_hu(player, card)
    
    def calculate_score(self, player, winning_card) -> int:
        """腾讯大众麻将计分规则"""
        return self.score_rules.calculate_score(player, winning_card)
    
    def get_valid_actions(self, player, game_state) -> list:
        """获取当前玩家的有效操作"""
        return self.action_rules.get_valid_actions(player, game_state)
    
    def create_initial_deck(self) -> list:
        """创建腾讯大众麻将初始牌组"""
        # 实现创建136张牌的逻辑
        from src.core.data.card import Card
        deck = []
        
        # 序数牌（万、筒、条）
        for suit in ['万', '筒', '条']:
            for rank in range(1, 10):
                for _ in range(4):
                    deck.append(Card(suit, str(rank)))
        
        # 风牌
        for suit in ['风']:
            for rank in ['东', '南', '西', '北']:
                for _ in range(4):
                    deck.append(Card(suit, rank))
        
        # 箭牌
        for suit in ['箭']:
            for rank in ['中', '发', '白']:
                for _ in range(4):
                    deck.append(Card(suit, rank))
        
        return deck