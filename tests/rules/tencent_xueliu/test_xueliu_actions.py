from src.core.data.card import Card
from src.core.data.player import Player
from src.core.data.game_state import GameState
from src.rules.tencent_xueliu.rule import TencentXueliuRule


def test_must_discard_que_blocks_other_actions():
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    p0 = Player("A", is_ai=False)
    p1 = Player("B", is_ai=False)
    p0.hand = [Card("万", "1"), Card("筒", "2"), Card("筒", "3")]
    p0.que_men = "万"
    gs.players = [p0, p1]
    gs.last_discarded_card = None

    actions = rule.get_valid_actions(p0, gs)
    assert actions == ["discard", "must_discard_que"]


def test_self_kong_returns_kong_action():
    rule = TencentXueliuRule()
    gs = GameState("tencent_xueliu")
    gs.rule = rule
    p0 = Player("A", is_ai=False)
    p0.hand = [Card("万", "1") for _ in range(4)]
    gs.players = [p0]
    actions = rule.get_valid_actions(p0, gs)
    assert "kong" in actions
