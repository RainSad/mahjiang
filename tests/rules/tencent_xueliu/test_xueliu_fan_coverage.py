"""
综合验证 tencent_xueliu 中 fan.md 记录的所有番型是否都被正确实现
"""
import pytest
from src.core.data.card import Card
from src.core.data.player import Player
from src.core.data.game_state import GameState
from src.core.data.action import Meld
from src.rules.tencent_xueliu.rule import TencentXueliuRule


class TestXueliuFanCoverage:
    """验证 fan.md 中列出的所有番型"""
    
    def test_256_fans_lian_qi_dui_in_fu_shang_room(self):
        """256倍：连七对（仅富商场）"""
        rule = TencentXueliuRule(room_level='富商场')
        gs = GameState("tencent_xueliu")
        gs.rule = rule
        
        p = Player("Test", is_ai=False)
        # 连七对：万子2-8序数的七对
        p.hand = [
            Card("万", "2"), Card("万", "2"),
            Card("万", "3"), Card("万", "3"),
            Card("万", "4"), Card("万", "4"),
            Card("万", "5"), Card("万", "5"),
            Card("万", "6"), Card("万", "6"),
            Card("万", "7"), Card("万", "7"),
            Card("万", "8"), Card("万", "8"),
        ]
        p.melds = []
        
        fans = rule.score_rules._calculate_fans(p, Card("万", "2"))
        assert fans == 256
    
    def test_256_fans_unavailable_in_normal_room(self):
        """256倍：连七对在普通场不可用"""
        rule = TencentXueliuRule(room_level='普通场')
        gs = GameState("tencent_xueliu")
        gs.rule = rule
        
        p = Player("Test", is_ai=False)
        p.hand = [
            Card("万", "2"), Card("万", "2"),
            Card("万", "3"), Card("万", "3"),
            Card("万", "4"), Card("万", "4"),
            Card("万", "5"), Card("万", "5"),
            Card("万", "6"), Card("万", "6"),
            Card("万", "7"), Card("万", "7"),
            Card("万", "8"), Card("万", "8"),
        ]
        p.melds = []
        
        fans = rule.score_rules._calculate_fans(p, Card("万", "2"))
        # 在普通场，应该降级处理
        assert fans < 256
    
    def test_128_fans_jiu_lian_bao_deng(self):
        """128倍：九莲宝灯"""
        rule = TencentXueliuRule(room_level='尊爵场')
        
        p = Player("Test", is_ai=False)
        # 九莲宝灯：1112345678999 + 任意牌
        p.hand = [
            Card("万", "1"), Card("万", "1"), Card("万", "1"),
            Card("万", "2"), Card("万", "3"), Card("万", "4"),
            Card("万", "5"), Card("万", "6"), Card("万", "7"),
            Card("万", "8"), Card("万", "9"), Card("万", "9"),
            Card("万", "9"), Card("万", "5"),  # 胡五万
        ]
        p.melds = []
        
        fans = rule.score_rules._calculate_fans(p, Card("万", "5"))
        assert fans == 128
    
    def test_32_fans_tian_hu(self):
        """32倍：天胡"""
        rule = TencentXueliuRule()
        
        p = Player("庄", is_ai=False)
        p.is_dealer = True
        p.is_tian_hu = True
        p.hand = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"), Card("万", "6"),
            Card("万", "7"), Card("万", "8"), Card("万", "9"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("筒", "4"), Card("筒", "4"),
        ]
        p.melds = []
        
        fans = rule.score_rules._calculate_fans(p, Card("万", "5"))
        assert fans == 32
    
    def test_32_fans_di_hu(self):
        """32倍：地胡"""
        rule = TencentXueliuRule()
        
        p = Player("闲", is_ai=False)
        p.is_dealer = False
        p.is_di_hu = True
        p.hand = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"), Card("万", "6"),
            Card("万", "7"), Card("万", "8"), Card("万", "9"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("筒", "4"), Card("筒", "4"),
        ]
        p.melds = []
        
        fans = rule.score_rules._calculate_fans(p, Card("万", "5"))
        assert fans == 32
    
    def test_32_fans_qing_shi_ba_luo_han(self):
        """32倍：清十八罗汉"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [Card("万", "1"), Card("万", "2")]
        p.melds = [
            Meld("明杠", [Card("万", "1"), Card("万", "1"), Card("万", "1"), Card("万", "1")]),
            Meld("暗杠", [Card("万", "2"), Card("万", "2"), Card("万", "2"), Card("万", "2")]),
            Meld("明杠", [Card("万", "3"), Card("万", "3"), Card("万", "3"), Card("万", "3")]),
            Meld("暗杠", [Card("万", "4"), Card("万", "4"), Card("万", "4"), Card("万", "4")]),
        ]
        
        # 清十八罗汉 = 清一色 + 十八罗汉
        assert rule.score_rules._is_qing_yi_se(p) == True
        assert rule.score_rules._is_shi_ba_luo_han(p) == True
        assert rule.score_rules._is_qing_shi_ba_luo_han(p) == True
    
    def test_16_fans_qing_qi_dui(self):
        """16倍：清七对"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [
            Card("万", "1"), Card("万", "1"),
            Card("万", "2"), Card("万", "2"),
            Card("万", "3"), Card("万", "3"),
            Card("万", "4"), Card("万", "4"),
            Card("万", "5"), Card("万", "5"),
            Card("万", "6"), Card("万", "6"),
            Card("万", "7"), Card("万", "7"),
        ]
        p.melds = []
        
        fans = rule.score_rules._calculate_fans(p, Card("万", "1"))
        assert fans == 16
    
    def test_16_fans_qing_jin_gou_diao(self):
        """16倍：清金钩钓"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [Card("万", "1"), Card("万", "2")]
        p.melds = [
            Meld("碰", [Card("万", "1"), Card("万", "1"), Card("万", "1")]),
            Meld("碰", [Card("万", "2"), Card("万", "2"), Card("万", "2")]),
            Meld("碰", [Card("万", "3"), Card("万", "3"), Card("万", "3")]),
            Meld("碰", [Card("万", "4"), Card("万", "4"), Card("万", "4")]),
        ]
        
        assert rule.score_rules._is_qing_yi_se(p) == True
        assert rule.score_rules._is_jin_gou_diao(p) == True
        assert rule.score_rules._is_qing_jin_gou_diao(p) == True
    
    def test_8_fans_qing_peng(self):
        """8倍：清碰"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [
            Card("万", "1"), Card("万", "1"),  # 将
        ]
        p.melds = [
            Meld("碰", [Card("万", "2"), Card("万", "2"), Card("万", "2")]),
            Meld("碰", [Card("万", "3"), Card("万", "3"), Card("万", "3")]),
            Meld("碰", [Card("万", "4"), Card("万", "4"), Card("万", "4")]),
            Meld("碰", [Card("万", "5"), Card("万", "5"), Card("万", "5")]),
        ]
        
        assert rule.score_rules._is_qing_yi_se(p) == True
        assert rule.score_rules._is_peng_peng_hu(p) == True
        assert rule.score_rules._is_qing_peng(p) == True
    
    def test_8_fans_shi_ba_luo_han(self):
        """8倍：十八罗汉"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [Card("万", "1"), Card("万", "2")]
        p.melds = [
            Meld("明杠", [Card("万", "1"), Card("万", "1"), Card("万", "1"), Card("万", "1")]),
            Meld("暗杠", [Card("万", "2"), Card("万", "2"), Card("万", "2"), Card("万", "2")]),
            Meld("明杠", [Card("筒", "1"), Card("筒", "1"), Card("筒", "1"), Card("筒", "1")]),
            Meld("暗杠", [Card("条", "1"), Card("条", "1"), Card("条", "1"), Card("条", "1")]),
        ]
        
        assert rule.score_rules._is_shi_ba_luo_han(p) == True
        fans = rule.score_rules._check_8_fans(p, Card("万", "1"))
        assert fans >= 8
    
    def test_4_fans_qing_yi_se(self):
        """4倍：清一色"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"), Card("万", "6"),
            Card("万", "7"), Card("万", "8"), Card("万", "9"),
            Card("万", "2"), Card("万", "2"),
        ]
        p.melds = [
            Meld("碰", [Card("万", "1"), Card("万", "1"), Card("万", "1")]),
        ]
        
        assert rule.score_rules._is_qing_yi_se(p) == True
        fans = rule.score_rules._check_4_fans(p, Card("万", "1"))
        assert fans >= 4
    
    def test_4_fans_qi_dui(self):
        """4倍：七对"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [
            Card("万", "1"), Card("万", "1"),
            Card("万", "2"), Card("万", "2"),
            Card("万", "3"), Card("万", "3"),
            Card("万", "4"), Card("万", "4"),
            Card("万", "5"), Card("万", "5"),
            Card("万", "6"), Card("万", "6"),
            Card("万", "7"), Card("万", "7"),
        ]
        p.melds = []
        
        assert rule.score_rules._is_qi_dui(p) == True
        fans = rule.score_rules._check_4_fans(p, Card("万", "1"))
        assert fans >= 4
    
    def test_4_fans_peng_peng_hu(self):
        """4倍：碰碰胡"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [Card("万", "1"), Card("万", "1")]
        p.melds = [
            Meld("碰", [Card("万", "2"), Card("万", "2"), Card("万", "2")]),
            Meld("碰", [Card("万", "3"), Card("万", "3"), Card("万", "3")]),
            Meld("碰", [Card("万", "4"), Card("万", "4"), Card("万", "4")]),
            Meld("碰", [Card("万", "5"), Card("万", "5"), Card("万", "5")]),
        ]
        
        assert rule.score_rules._is_peng_peng_hu(p) == True
        fans = rule.score_rules._check_4_fans(p, Card("万", "1"))
        assert fans >= 4
    
    def test_4_fans_yao_jiu(self):
        """4倍：幺九（每个刻子/顺子/将都含1/9）"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [
            Card("万", "1"), Card("万", "1"),  # 将
            Card("万", "1"), Card("万", "1"), Card("万", "1"),  # 幺九刻
            Card("万", "9"), Card("万", "9"), Card("万", "9"),  # 幺九刻
        ]
        p.melds = [
            Meld("碰", [Card("条", "1"), Card("条", "1"), Card("条", "1")]),
            Meld("吃", [Card("条", "7"), Card("条", "8"), Card("条", "9")]),
        ]
        
        assert rule.score_rules._is_yao_jiu(p) == True
        fans = rule.score_rules._check_4_fans(p, Card("万", "1"))
        assert fans >= 4
    
    def test_4_fans_duan_yao_jiu(self):
        """4倍：断幺九（手牌中没有1、9）"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.hand = [
            Card("万", "2"), Card("万", "2"), Card("万", "2"),
            Card("万", "3"), Card("万", "4"), Card("万", "5"),
            Card("条", "2"), Card("条", "3"), Card("条", "4"),
            Card("筒", "5"), Card("筒", "6"), Card("筒", "7"),
            Card("万", "5"), Card("万", "5"),
        ]
        p.melds = []
        
        assert rule.score_rules._is_duan_yao_jiu(p) == True
        fans = rule.score_rules._check_4_fans(p, Card("万", "2"))
        assert fans >= 4
    
    def test_2_fans_zi_mo(self):
        """2倍：自摸"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.drawn_card = Card("万", "5")
        p.hand = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"), Card("万", "6"),
            Card("万", "7"), Card("万", "8"), Card("万", "9"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("筒", "4"), Card("筒", "4"),
        ]
        p.melds = []
        
        assert rule.score_rules._is_zi_mo(p, Card("万", "5")) == True
    
    def test_2_fans_gang_shang_kai_hua(self):
        """2倍：杠上开花"""
        rule = TencentXueliuRule()
        
        p = Player("Test", is_ai=False)
        p.drawn_card = Card("万", "5")
        p.last_action = "明杠"
        p.hand = [
            Card("万", "1"), Card("万", "2"), Card("万", "3"),
            Card("万", "4"), Card("万", "5"), Card("万", "6"),
            Card("万", "7"), Card("万", "8"), Card("万", "9"),
            Card("条", "1"), Card("条", "2"), Card("条", "3"),
            Card("筒", "4"), Card("筒", "4"),
        ]
        p.melds = []
        
        assert rule.score_rules._is_gang_shang_kai_hua(p, Card("万", "5")) == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
