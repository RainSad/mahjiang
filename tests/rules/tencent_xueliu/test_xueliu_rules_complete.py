import pytest
from src.core.data.card import Card
from src.core.data.player import Player
from src.core.data.game_state import GameState
from src.core.data.action import Meld
from src.rules.tencent_xueliu.rule import TencentXueliuRule


def test_que_men_blocks_all_non_discard():
    """缺门时应禁止碰/杠/胡，只允许打牌"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p0 = Player("A", is_ai=False)
    p1 = Player("B", is_ai=False)
    
    p0.hand = [Card("万", "1"), Card("筒", "2"), Card("筒", "3")]
    p0.que_men = "万"
    
    gs.players = [p0, p1]
    
    # 有缺门牌时的有效动作
    actions = rule.get_valid_actions(p0, gs)
    assert actions == ["discard", "must_discard_que"]
    assert "pong" not in actions
    assert "kong" not in actions
    assert "hu" not in actions


def test_no_que_men_allows_all_actions():
    """未定缺或无缺门牌时应允许所有合法动作"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p0 = Player("A", is_ai=False)
    p1 = Player("B", is_ai=False)
    
    # 手牌无缺门牌
    p0.hand = [Card("万", "1"), Card("筒", "2"), Card("筒", "3")]
    p0.que_men = "条"
    
    gs.players = [p0, p1]
    
    actions = rule.get_valid_actions(p0, gs)
    assert "discard" in actions
    assert "must_discard_que" not in actions


def test_exchange_three_executed_on_init():
    """血流规则应在初始化后自动执行换三张"""
    from src.core.logic.turn_handler import init_game
    
    players_config = [
        {"name": "P1", "is_ai": True},
        {"name": "P2", "is_ai": True},
        {"name": "P3", "is_ai": True},
        {"name": "P4", "is_ai": True},
    ]
    
    gs = init_game("tencent_xueliu", players_config)
    
    # 验证发牌后手牌数：庄家14张，其他13张
    for i, p in enumerate(gs.players):
        expected = 14 if i == 0 else 13  # 第一个为庄家
        assert len(p.hand) == expected, f"玩家 {p.name} 应有{expected}张牌，实际有 {len(p.hand)} 张"


def test_gang_settlement_明杠():
    """明杠：放杠者支付2倍底分"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p_gang = Player("杠家", is_ai=False)
    p_from = Player("放杠家", is_ai=False)
    gs.players = [p_gang, p_from]
    
    p_gang.score = 0
    p_from.score = 0
    
    rule.score_rules.settle_gang_payment(p_gang, "明杠", p_from, gs)
    
    assert p_gang.score == 20, "杠家应得20分"
    assert p_from.score == -20, "放杠家应付20分"
    assert p_gang.last_gang_gain == 20, "最近杠收益应为20"


def test_gang_settlement_暗杠():
    """暗杠：其他各家支付2倍底分"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p_gang = Player("杠家", is_ai=False)
    p_other1 = Player("其他1", is_ai=False)
    p_other2 = Player("其他2", is_ai=False)
    p_other3 = Player("其他3", is_ai=False)
    
    gs.players = [p_gang, p_other1, p_other2, p_other3]
    
    for p in gs.players:
        p.score = 0
    
    rule.score_rules.settle_gang_payment(p_gang, "暗杠", None, gs)
    
    assert p_gang.score == 60, "杠家应得60分（3×20）"
    assert p_other1.score == -20, "其他家应各付20分"
    assert p_other2.score == -20
    assert p_other3.score == -20
    assert p_gang.last_gang_gain == 60, "最近杠收益应为60"


def test_gang_settlement_补杠():
    """补杠：其他各家支付1倍底分"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p_gang = Player("补杠家", is_ai=False)
    p_other1 = Player("其他1", is_ai=False)
    p_other2 = Player("其他2", is_ai=False)
    
    gs.players = [p_gang, p_other1, p_other2]
    
    for p in gs.players:
        p.score = 0
    
    rule.score_rules.settle_gang_payment(p_gang, "补杠", None, gs)
    
    assert p_gang.score == 20, "补杠家应得20分（2×10）"
    assert p_other1.score == -10, "其他家应各付10分"
    assert p_other2.score == -10
    assert p_gang.last_gang_gain == 20, "最近杠收益应为20"


def test_call_transfer_on_hu():
    """胡牌时应将放杠者的杠收益转给胡家"""
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    
    p_gang = Player("杠家", is_ai=False)
    p_hu = Player("胡家", is_ai=False)
    
    gs.players = [p_gang, p_hu]
    
    p_gang.score = 0
    p_hu.score = 0
    p_gang.last_gang_gain = 20
    
    rule.handle_call_transfer(p_hu, p_gang)
    
    assert p_gang.score == -20, "杠家应失去20分"
    assert p_hu.score == 20, "胡家应获得20分"
    assert p_gang.last_gang_gain == 0, "转移后杠收益应清零"
