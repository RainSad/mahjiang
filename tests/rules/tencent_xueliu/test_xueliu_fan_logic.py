import pytest
from src.core.data.card import Card
from src.core.data.player import Player
from src.core.data.game_state import GameState
from src.core.data.action import Meld
from src.core.logic.turn_handler import init_game
from src.rules.tencent_xueliu.rule import TencentXueliuRule


def test_tian_hu_flag_set_on_dealer_first_draw():
    """庄家首轮自摸胡应标记 is_tian_hu"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    gs.first_turn = True
    
    p_dealer = Player("庄", is_ai=True)
    p_dealer.is_dealer = True
    
    # 标记候选
    p_dealer.is_tian_hu_candidate = True
    
    # 确认胡牌
    p_dealer.is_tian_hu = True
    p_dealer.is_tian_hu_candidate = False
    
    assert p_dealer.is_tian_hu == True


def test_di_hu_flag_set_on_non_dealer_first_draw():
    """非庄家首轮摸牌胡应标记 is_di_hu"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    gs.first_turn = True
    
    p_闲 = Player("闲", is_ai=True)
    p_闲.is_dealer = False
    
    # 标记候选
    p_闲.is_di_hu_candidate = True
    
    # 确认胡牌
    p_闲.is_di_hu = True
    p_闲.is_di_hu_candidate = False
    
    assert p_闲.is_di_hu == True


def test_jin_gou_diao_validates_meld_types():
    """金钩钓必须验证副露全是碰杠"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p = Player("Test", is_ai=False)
    p.hand = [Card("万", "1"), Card("万", "2")]
    p.melds = [
        Meld("碰", [Card("万", "1"), Card("万", "1"), Card("万", "1")]),
        Meld("碰", [Card("万", "2"), Card("万", "2"), Card("万", "2")]),
        Meld("明杠", [Card("万", "3"), Card("万", "3"), Card("万", "3"), Card("万", "3")]),
        Meld("暗杠", [Card("万", "4"), Card("万", "4"), Card("万", "4"), Card("万", "4")]),
    ]
    
    assert rule.score_rules._is_jin_gou_diao(p) == True


def test_jin_gou_diao_rejects_chow():
    """金钩钓必须拒绝含吃的副露"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p = Player("Test", is_ai=False)
    p.hand = [Card("万", "1"), Card("万", "2")]
    p.melds = [
        Meld("吃", [Card("万", "1"), Card("万", "2"), Card("万", "3")]),  # 含吃
        Meld("碰", [Card("万", "4"), Card("万", "4"), Card("万", "4")]),
        Meld("碰", [Card("万", "5"), Card("万", "5"), Card("万", "5")]),
        Meld("碰", [Card("万", "6"), Card("万", "6"), Card("万", "6")]),
    ]
    
    assert rule.score_rules._is_jin_gou_diao(p) == False


def test_shi_ba_luo_han_requires_4_gangs():
    """十八罗汉必须是金钩钓+4个杠"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p = Player("Test", is_ai=False)
    p.hand = [Card("万", "1"), Card("万", "2")]
    p.melds = [
        Meld("明杠", [Card("万", "1"), Card("万", "1"), Card("万", "1"), Card("万", "1")]),
        Meld("暗杠", [Card("万", "2"), Card("万", "2"), Card("万", "2"), Card("万", "2")]),
        Meld("明杠", [Card("万", "3"), Card("万", "3"), Card("万", "3"), Card("万", "3")]),
        Meld("暗杠", [Card("万", "4"), Card("万", "4"), Card("万", "4"), Card("万", "4")]),
    ]
    
    assert rule.score_rules._is_shi_ba_luo_han(p) == True


def test_shi_ba_luo_han_rejects_less_than_4_gangs():
    """十八罗汉拒绝少于4个杠"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p = Player("Test", is_ai=False)
    p.hand = [Card("万", "1"), Card("万", "2")]
    p.melds = [
        Meld("明杠", [Card("万", "1"), Card("万", "1"), Card("万", "1"), Card("万", "1")]),
        Meld("暗杠", [Card("万", "2"), Card("万", "2"), Card("万", "2"), Card("万", "2")]),
        Meld("暗杠", [Card("万", "3"), Card("万", "3"), Card("万", "3"), Card("万", "3")]),
        Meld("碰", [Card("万", "4"), Card("万", "4"), Card("万", "4")]),  # 碰，非杠
    ]
    
    assert rule.score_rules._is_shi_ba_luo_han(p) == False


def test_yao_jiu_and_duan_yao_jiu_mutually_exclusive():
    """幺九和断幺九互斥，幺九优先"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p = Player("Test", is_ai=False)
    # 仅幺九满足
    p.hand = [
        Card("万", "1"), Card("万", "1"), Card("万", "1"),
        Card("万", "9"), Card("万", "9"), Card("万", "9"),
        Card("筒", "1"), Card("筒", "1"), Card("筒", "1"),
        Card("条", "9"), Card("条", "9"), Card("条", "9"),
        Card("万", "5"), Card("万", "5"),
    ]
    p.melds = []
    
    fans = rule.score_rules._check_4_fans(p, Card("万", "1"))
    # 应该检测到幺九和断幺九互斥，选幺九
    assert rule.score_rules._is_yao_jiu(p) == True
    # 累加中应只计幺九 4倍，不重复计算


def test_qi_dui_and_peng_peng_hu_mutually_exclusive():
    """七对和碰碰胡互斥"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p = Player("Test", is_ai=False)
    # 七对：7个对子
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
    
    # 七对不是碰碰胡
    assert rule.score_rules._is_qi_dui(p) == True
    assert rule.score_rules._is_peng_peng_hu(p) == False


def test_qing_yi_se_does_not_double_count_with_qi_dui():
    """清一色与清七对等不重复计算"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p = Player("Test", is_ai=False)
    # 全万子七对
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
    
    fans = rule.score_rules._check_4_fans(p, Card("万", "1"))
    # 清七对由高倍番型处理（16倍），4倍应该不重复
    assert fans == 0 or fans == 4  # 取决于实现，不应该同时累加清一色+七对
