import pytest

from src.core.data.card import Card
from src.core.data.game_state import GameState
from src.core.data.player import Player
from src.core.logic.turn_handler import TurnHandler
from src.interface.game_api import get_player_input
from src.rules.tencent_xueliu.rule import TencentXueliuRule


def test_xueliu_deck_size_and_suits():
    rule = TencentXueliuRule()
    deck = rule.create_initial_deck()
    assert len(deck) == 108
    suits = {c.suit for c in deck}
    assert suits == {"万", "筒", "条"}


def test_cli_must_discard_que_enforced(monkeypatch):
    rule = TencentXueliuRule()
    game_state = GameState("tencent_xueliu")
    game_state.rule = rule
    player = Player("P1", is_ai=False)
    player.hand = [Card("万", "1"), Card("筒", "2")]
    player.que_men = "万"

    # 直接回车使用推荐，应被强制改为缺门弃牌
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    action = get_player_input(player, game_state, ["discard", "must_discard_que"])
    assert action.type == "discard"
    assert action.card.suit == "万"


def test_multi_hu_continuation_from_last_hu_next():
    rule = TencentXueliuRule()
    game_state = GameState("tencent_xueliu")
    game_state.rule = rule
    game_state.game_stage = "playing"

    # Players
    p0 = Player("南", is_ai=True)
    p1 = Player("西", is_ai=True)
    p2 = Player("北", is_ai=True)
    p3 = Player("东", is_ai=True)
    players = [p0, p1, p2, p3]
    for idx, p in enumerate(players):
        p.next_player = players[(idx + 1) % len(players)]
        p.previous_player = players[(idx - 1) % len(players)]
        p.game_state = game_state
    game_state.players = players
    game_state.current_player = p0

    # Current player hand and forced discard strategy
    target = Card("万", "1")
    p0.hand = [target, Card("筒", "3"), Card("筒", "4")]

    class ForceDiscardStrategy:
        def __init__(self, rule):
            self.rule = rule

        def recommend(self, player, game_state, valid_actions):
            from src.core.data.action import Action
            return Action("discard", target), "force discard"

    p0.ai_strategy = ForceDiscardStrategy(rule)

    # Hu-ready hands for p1 and p2
    base_waiting_hand = [
        Card("万", "1"), Card("万", "1"),  # 2x target
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "5"), Card("万", "6"), Card("万", "7"),
        Card("万", "7"), Card("万", "8"), Card("万", "9"),
        Card("筒", "2"), Card("筒", "2"),
    ]
    p1.hand = list(base_waiting_hand)
    p2.hand = list(base_waiting_hand)
    p1.que_men = "条"
    p2.que_men = "条"

    # Empty deck/discard
    game_state.deck = []
    game_state.discard_pile = []
    game_state.last_discarded_card = None

    action = TurnHandler.process_turn(game_state)

    assert action.type == "hu"
    assert game_state.winners == [p1, p2]
    assert game_state.current_player == p3  # continue from last hu's next player
    assert game_state.game_stage == "playing"
    assert not game_state.discard_pile  # discard consumed by multi-hu
