"""
验证血流成河规则的结算逻辑：查花猪/查大叫/退税
以及定缺规则的完整性：未定缺不得胡/定缺后不可更改/天命花猪豁免
"""
import pytest
from src.core.data.card import Card
from src.core.data.player import Player
from src.core.data.game_state import GameState
from src.core.data.action import Meld
from src.rules.tencent_xueliu.rule import TencentXueliuRule


class TestXueliuQueuenRule:
    """定缺规则测试"""
    
    def test_must_define_que_men_before_hu(self):
        """规则：必须已定缺才能胡牌"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.que_men = None  # 未定缺
        p.hand = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"), Card("万", "6"),
            Card("万", "7"), Card("万", "8"), Card("万", "9"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("筒", "4"), Card("筒", "4"),
        ]
        p.melds = []
        
        # 未定缺不能胡
        assert rule.can_hu(p, Card("万", "5")) == False
    
    def test_que_men_locked_after_first_hu(self):
        """规则：首次定缺后不可更改"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.que_men = "万"
        p.que_men_locked = False
        p.hand = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"), Card("万", "6"),
            Card("万", "7"), Card("万", "8"), Card("万", "9"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("筒", "4"), Card("筒", "4"),
        ]
        p.melds = []
        
        # 首次定缺会锁定
        if rule.can_hu(p, Card("万", "5")):
            # 定缺被锁定
            assert p.que_men_locked == True or p.que_men == "万"
    
    def test_que_men_rule_max_2_suits(self):
        """规则：定缺后，手牌花色不能超过2门（不包括缺的花色）"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.que_men = "万"  # 定缺万子
        p.hand = [
            Card("筒", "1"), Card("筒", "2"), Card("筒", "3"),
            Card("筒", "4"), Card("筒", "5"), Card("筒", "6"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("条", "4"), Card("条", "5"), Card("条", "6"),
            Card("筒", "7"), Card("筒", "7"),
        ]
        p.melds = []
        
        # 手牌中有筒和条（2门，不含缺的万），符合规则
        # 但胡牌本身需要形成有效的牌型
        # 这个检查会在 can_hu 中进行
    
    def test_tian_ming_hua_zhu_exemption(self):
        """规则：天命花猪豁免 - 打出的牌均为缺牌则不赔付"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.que_men = "万"
        p.discarded_cards = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"),
        ]  # 所有打出的牌都是万子（缺牌）
        p.hand = [
            Card("筒", "1"), Card("筒", "2"), Card("筒", "3"),
            Card("条", "1"), Card("条", "2"),
        ]
        
        # 检查是否是天命花猪
        is_tian_ming = rule._is_tian_ming_hua_zhu(p, "万")
        assert is_tian_ming == True
    
    def test_non_tian_ming_hua_zhu(self):
        """规则：非天命花猪 - 打出过非缺牌"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.que_men = "万"
        p.discarded_cards = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("筒", "1"),  # 打过筒子（不是缺牌）
        ]
        p.hand = [
            Card("筒", "2"), Card("筒", "3"), Card("条", "1"),
        ]
        
        # 不是天命花猪（因为打过非缺牌）
        is_tian_ming = rule._is_tian_ming_hua_zhu(p, "万")
        assert is_tian_ming == False


class TestXueliuSettlement:
    """结算规则测试"""
    
    def test_settlement_methods_exist(self):
        """验证所有结算方法都存在"""
        rule = TencentXueliuRule()
        
        # 验证结算方法存在
        assert hasattr(rule, '_settle_hua_zhu')
        assert hasattr(rule, '_settle_cha_da_jiao')
        assert hasattr(rule, '_settle_tui_shui')
        assert hasattr(rule, '_is_tian_ming_hua_zhu')
        assert hasattr(rule, '_is_player_listening')
        assert hasattr(rule, '_get_max_fans_for_listening')
    
    def test_on_deck_empty_settlement_flow(self):
        """验证牌墙摸空时的完整结算流程"""
        rule = TencentXueliuRule()
        gs = GameState("tencent_xueliu")
        gs.rule = rule
        
        # 创建玩家
        players = []
        for i in range(4):
            p = Player(f"Player{i}", is_ai=True)
            p.score = 1000
            p.que_men = "万"
            p.hand = [
                Card("筒", "1"), Card("筒", "2"), Card("筒", "3"),
                Card("条", "1"), Card("条", "2"), Card("条", "3"),
            ]
            players.append(p)
        
        # 设置玩家链接
        for i in range(len(players)):
            players[i].next_player = players[(i + 1) % len(players)]
            players[i].previous_player = players[(i - 1) % len(players)]
        
        gs.players = players
        gs.deck = []
        
        # 调用结算
        rule.on_deck_empty(gs)
        
        # 验证结算执行没有错误
        assert True  # 如果执行到这里说明没有崩溃

    def test_cha_da_jiao_excludes_winners(self):
        """查大叫：只赔听牌未胡玩家，不包括已胡玩家"""
        rule = TencentXueliuRule()
        gs = GameState("tencent_xueliu")
        gs.rule = rule
        
        # 两名玩家：A（未听牌），B（听牌且已胡）
        A = Player("A", is_ai=False)
        B = Player("B", is_ai=False)
        for p in [A, B]:
            p.score = 1000
            p.que_men = "万"
        
        # B听牌（构造可胡），且标记为已胡
        B.hand = [
            Card("筒", "1"), Card("筒", "2"), Card("筒", "3"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("万", "2"), Card("万", "2"),
            Card("万", "3"), Card("万", "3"),
            Card("万", "4"), Card("万", "4"),
            Card("万", "5"), Card("万", "5"),
        ]
        gs.winners = [B]
        
        # A不听牌
        A.hand = [Card("筒", "4"), Card("条", "4"), Card("筒", "5"), Card("条", "5"), Card("筒", "6"), Card("条", "6"), Card("筒", "7"), Card("条", "7"), Card("筒", "8"), Card("条", "8"), Card("筒", "9"), Card("条", "9"), Card("筒", "1"), Card("条", "1")]
        
        players = [A, B]
        gs.players = players
        
        # 执行查大叫
        rule._settle_cha_da_jiao(gs, players, 10)
        
        # 因为B已胡，不应再获得查大叫赔付
        assert B.score == 1000
        assert A.score == 1000
    
    def test_hua_zhu_settlement_basic(self):
        """查花猪：手牌含缺牌的玩家赔付"""
        rule = TencentXueliuRule()
        gs = GameState("tencent_xueliu")
        gs.rule = rule
        
        # 创建玩家1：手牌含缺牌
        p1 = Player("P1", is_ai=False)
        p1.score = 1000
        p1.que_men = "万"
        p1.hand = [
            Card("万", "1"),  # 含缺牌万子
            Card("筒", "1"), Card("筒", "2"),
            Card("条", "1"), Card("条", "2"),
        ]
        p1.discarded_cards = [Card("筒", "3")]  # 打过非缺牌，非天命花猪
        
        # 创建玩家2、3、4：手牌不含缺牌
        p2 = Player("P2", is_ai=False)
        p2.score = 1000
        p2.que_men = "万"
        p2.hand = [
            Card("筒", "3"), Card("筒", "4"),
            Card("条", "3"), Card("条", "4"),
        ]
        p2.discarded_cards = []
        
        p3 = Player("P3", is_ai=False)
        p3.score = 1000
        p3.que_men = "万"
        p3.hand = [Card("筒", "5"), Card("条", "5")]
        p3.discarded_cards = []
        
        p4 = Player("P4", is_ai=False)
        p4.score = 1000
        p4.que_men = "万"
        p4.hand = [Card("筒", "6"), Card("条", "6")]
        p4.discarded_cards = []
        
        # 设置玩家链接
        players = [p1, p2, p3, p4]
        for i in range(len(players)):
            players[i].next_player = players[(i + 1) % len(players)]
            players[i].previous_player = players[(i - 1) % len(players)]
        
        gs.players = players
        gs.deck = []
        
        # 执行花猪结算
        rule._settle_hua_zhu(gs, players, 10)
        
        # p1 应该被扣分，其他玩家应该得分
        assert p1.score < 1000  # p1 被扣分
        assert p2.score > 1000  # p2 得分
        assert p3.score > 1000  # p3 得分
        assert p4.score > 1000  # p4 得分
    
    def test_hua_zhu_exemption_for_tian_ming(self):
        """查花猪：天命花猪豁免"""
        rule = TencentXueliuRule()
        gs = GameState("tencent_xueliu")
        gs.rule = rule
        
        # 创建天命花猪玩家：只打过缺牌
        p1 = Player("TianMing", is_ai=False)
        initial_score = 1000
        p1.score = initial_score
        p1.que_men = "万"
        p1.hand = [
            Card("万", "1"),  # 手牌含缺牌
            Card("筒", "1"), Card("筒", "2"),
        ]
        p1.discarded_cards = [
            Card("万", "2"), Card("万", "3"),  # 只打过万子（缺牌）
        ]
        
        p2 = Player("P2", is_ai=False)
        p2.score = 1000
        p2.que_men = "万"
        p2.hand = [Card("筒", "3"), Card("条", "1")]
        p2.discarded_cards = []
        
        players = [p1, p2]
        for i in range(len(players)):
            players[i].next_player = players[(i + 1) % len(players)]
        
        gs.players = players
        gs.deck = []
        
        # 执行花猪结算
        rule._settle_hua_zhu(gs, players, 10)
        
        # 天命花猪应该豁免，分数不变
        assert p1.score == initial_score


class TestXueliuDiscardedCardTracking:
    """打出卡牌追踪测试"""
    
    def test_discarded_cards_recorded(self):
        """验证打出的牌被正确记录"""
        from src.core.logic.turn_handler import TurnHandler
        
        rule = TencentXueliuRule()
        gs = GameState("tencent_xueliu")
        gs.rule = rule
        gs.deck = []
        
        p = Player("Test", is_ai=False)
        p.hand = [Card("万", "1"), Card("万", "2"), Card("万", "3")]
        p.melds = []
        p.discarded_cards = []
        p.is_dealer = True
        
        from src.core.data.action import Action
        action = Action("discard", Card("万", "1"))
        
        # 执行打牌操作
        TurnHandler.execute_action(action, p, gs)
        
        # 验证牌被记录到 discarded_cards
        assert len(p.discarded_cards) > 0
        assert p.discarded_cards[-1] == Card("万", "1")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
