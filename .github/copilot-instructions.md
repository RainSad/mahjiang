# Mahjong AI Agent - Copilot Guide

## Architecture & Flow
- Rules plug-ins: [src/rules/tencent_common/rule.py](src/rules/tencent_common/rule.py) and [src/rules/tencent_xueliu/rule.py](src/rules/tencent_xueliu/rule.py) wrap hu/action/score modules; extend behaviors there instead of duplicating logic.
- Core loop in [src/core/logic/game_flow.py](src/core/logic/game_flow.py) hands control to [src/core/logic/turn_handler.py](src/core/logic/turn_handler.py): draw → `rule.can_hu` → `rule.get_valid_actions` → AI/CLI choice → `execute_action`. Kong/flower recurses to continue the turn; `allow_multiple_hu` keeps blood-flow games running after a hu.
- Decks: common builds 144 tiles including 风/箭/花; blood-flow builds 108 suited tiles only via each rule’s `create_initial_deck`.

## State & Data Contracts
- Card comparisons rely on `Card.__eq__` (`Card.id = f"{suit}{rank}"`); avoid manual suit/rank checks.
- `Player` carries `hand`, `melds`, `drawn_card`, `last_action`, `consecutive_gang_count`, `changed_flower_count`, dealer flags, seat links, 天/地胡 candidates; hu confirmation clears the flags in `process_turn`.
- `GameState` owns `deck`, `discard_pile`, `last_discarded_card`, `current_player`, `winners`, `wind`, `round_number`, `game_stage`, `rule`, `first_turn`, plus per-rule fields like `settlement_logs` and `gang_events` in blood-flow.

## Action Rules & Turn Handling
- Discard-pile sync: chow/pong/kong/hu must remove the consumed discard and reset `last_discarded_card`; kong draws replacements via `DeckManager.draw_replacement`.
- 血流定缺: `TencentXueliuActionRules.get_valid_actions` injects `must_discard_que` when holding the缺门 suit, short-circuiting other actions; AI path in `process_turn` discards that suit first.
- Multi-hu: when `allow_multiple_hu` is True, discards can trigger multiple `hu`, removing the discard, invoking `handle_call_transfer` for 杠上炮收益移转, and resuming from the last hu player’s next seat.
- Kong bookkeeping: `execute_action` tracks 连杠次数, records gang events, and settles payments via `score_rules.settle_gang_payment`.

## Scoring & Settlement
- Common rule: cap total fans at 10; hu requires pair+four melds and at least one fan (鸡胡自摸) with multipliers for 杠上开花/炮/抢杠/妙手/海底 + dealer + 连杠 in [src/rules/tencent_common/score_rules.py](src/rules/tencent_common/score_rules.py).
- 血流 scoring formula in [src/rules/tencent_xueliu/score_rules.py](src/rules/tencent_xueliu/score_rules.py): base 10 × fan multiplier (1–256 with互斥) × gang multiplier (each gang ×2) × special multipliers (自摸/杠上开花/杠上炮/抢杠胡/海底 each ×4); gang payments settle immediately and log `gang_events` for later transfer/refund.
- End-of-wall settlement in 血流: `on_deck_empty` runs 查花猪 (天命花猪豁免 via discard history), 查大叫 (max fans for listeners), then 退税 using recorded `gang_events`.

## AI & Interface
- `AI_Decision` selects `AdvancedStrategy` by default and delegates to `strategy.recommend`; string "base"/"advanced" toggles strategies in [src/ai/strategy/decision.py](src/ai/strategy/decision.py).
- Non-AI input comes from [src/interface/game_api.py](src/interface/game_api.py); ensure new actions are exposed there when extending rules.
- PyQt UI: [src/ui/mahjong_ui.py](src/ui/mahjong_ui.py) main window with rule selector dropdown; rule-specific pages inherit [src/ui/rule_page.py](src/ui/rule_page.py) `RulePage` interface (`setup_ui`, `render_state`, `render_actions`, `render_hand`, `reset`, `get_widget`). Add new rule pages by implementing `RulePage` and registering in `MainWindow.rule_pages` dict. Pages own their action/hand button layout; callback `handle_player_action(action_type, card)` drives main loop.

## Conventions & Pitfalls
- Use absolute imports `from src...`.
- Keep `discard_pile` and `last_discarded_card` in sync; do not bypass `DeckManager` helpers for draws/discards.
- Preserve future-state hooks: `last_action`, `consecutive_gang_count`, `changed_flower_count`, `discarded_cards`, `gang_events`, `last_gang_gain/event`.
- Stick to Card object equality; suits may be 汉字, but comments/code stay ASCII.

## Run & Test
- Full suite: `pytest tests/ -v`.
- Common rule focus: `pytest tests/rules/tencent_common/ -v`.
- 血流 focus (multi-hu/settlement/定缺 coverage): `pytest tests/rules/tencent_xueliu/ -v`.
- Quick manual run: `python main.py --rule tencent_common --players ai,ai,ai,ai` (blood-flow available via `--rule tencent_xueliu`).
