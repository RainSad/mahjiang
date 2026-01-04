# Mahjong AI Agent - Copilot Guide

## Quickstart for AI Agents
- Big picture: rule plug-ins ([src/rules/tencent_common/rule.py](src/rules/tencent_common/rule.py), [src/rules/tencent_xueliu/rule.py](src/rules/tencent_xueliu/rule.py)) wire `hu_rules`/`action_rules`/`score_rules` into the core loop ([src/core/logic/game_flow.py](src/core/logic/game_flow.py) → [src/core/logic/turn_handler.py](src/core/logic/turn_handler.py)). Always route actions via `TurnHandler.execute_action()`; draw/discard through `DeckManager`.
- Start a game: call [init_game](src/core/logic/turn_handler.py#L307) to build `GameState`, then step with `TurnHandler.process_turn()`. For manual play, launch PyQt via [src/ui/mahjong_ui.py](src/ui/mahjong_ui.py) `run_pyqt_ui_game()`; CLI flows in [src/interface/game_api.py](src/interface/game_api.py) and [src/cli/cli_main.py](src/cli/cli_main.py); quick Blood Flow smoke run via `python cli/cli_xueliu.py`.
- State contracts: object-based card identity (`Card.id`, see [src/core/data/card.py](src/core/data/card.py)); keep `GameState.discard_pile` and `last_discarded_card` in sync; update `current_player`, `winners`, `settlement_logs` through core APIs; use `DeckManager.draw_replacement()` for flower/kong draws.
- Action semantics: when resolving discard/pong/kong/chow, remove the consumed discard, clear `last_discarded_card`, and use [DeckManager.discard_card](src/core/logic/deck_manager.py) to sync `from_player`.
- Blood Flow (血流): lock `que_men` before hu; enforce缺门弃牌 (`must_discard_que`) when holding缺门 ([src/rules/tencent_xueliu/action_rules.py](src/rules/tencent_xueliu/action_rules.py)); auto `exchange_three` after deal unless disabled; supports multi-hu (`allow_multiple_hu`) with 呼叫转移 and resuming from the last hu player’s next seat.
- Kong bookkeeping: on `kong`, set `last_action`, increment `consecutive_gang_count`, record via `score_rules.settle_gang_payment`, then draw a replacement.
- Scoring: Common caps fans × base10 ([src/rules/tencent_common/score_rules.py](src/rules/tencent_common/score_rules.py)); Blood Flow multiplies fans (1–256) × gang multiplier (2^根) + special ×4 flags, using `gang_events` for later settlement ([src/rules/tencent_xueliu/score_rules.py](src/rules/tencent_xueliu/score_rules.py)).
- Hooks: first-turn 天/地胡 candidates are tagged and cleared on hu; empty wall triggers Blood Flow `on_deck_empty` (查花猪/查大叫/退税) ([src/rules/tencent_xueliu/rule.py](src/rules/tencent_xueliu/rule.py)).
- AI choices: `AI_Decision` defaults to `AdvancedStrategy` (risk + fan potential via `score_rules`); UI enforces缺门弃牌 ([src/interface/game_api.py](src/interface/game_api.py), [src/ui/xueliu_page.py](src/ui/xueliu_page.py)).
- Conventions: absolute imports `from src...`; ASCII comments; preserve state hooks (`last_action`, `consecutive_gang_count`, `changed_flower_count`, `discarded_cards`, `gang_events`, `last_gang_gain/event`, 天/地胡 candidates). See [structure.md](structure.md) for broader design notes.
- Dev workflows: install deps `pip install -r requirements.txt`; run tests `pytest tests/ -v`; focused suites: Common [tests/rules/tencent_common](tests/rules/tencent_common), Blood Flow [tests/rules/tencent_xueliu](tests/rules/tencent_xueliu); PyQt demo `python -m src.ui.mahjong_ui`.


## Architecture & Flow
- Two rule plug-ins: [src/rules/tencent_common/rule.py](src/rules/tencent_common/rule.py) and [src/rules/tencent_xueliu/rule.py](src/rules/tencent_xueliu/rule.py) wire `hu_rules`/`action_rules`/`score_rules`; extend behaviors inside those modules instead of forking the loop. Base interface defined in [src/rules/base_rule.py](src/rules/base_rule.py).
- Core loop in [src/core/logic/game_flow.py](src/core/logic/game_flow.py) → [src/core/logic/turn_handler.py](src/core/logic/turn_handler.py): draw via `DeckManager.draw_card`, tag 天/地胡 candidates on the first turn, `rule.can_hu` → `rule.get_valid_actions` → AI/CLI/UI choice → `execute_action`; flower/kong recurses; empty wall can trigger rule hook (血流 `on_deck_empty`).
- Setup helper `init_game` in [src/core/logic/turn_handler.py](src/core/logic/turn_handler.py) (line 307+) builds `GameState`, assigns seats/庄, shuffles/deals via `shuffle_and_deal`, auto `exchange_three` for 血流 unless disabled (UI can pass options).
- Project structure documented in [structure.md](structure.md); data models in [src/core/data/](src/core/data/) (Card, Player, GameState, Action, Meld).

## State & Data Contracts
- Card equality is `Card.id = f"{suit}{rank}"`; use object equality instead of suit/rank checks. `Card.__lt__` defines UI sort.
- Key containers: `GameState.deck/discard_pile/last_discarded_card/current_player/winners/wind/settlement_logs`; `Player.hand/melds/score/position/is_dealer/drawn_card/last_action/consecutive_gang_count/changed_flower_count/que_men/discarded_cards/gang_events/last_gang_gain`.
- `Action` stores `type/card/from_player/timestamp`; `Meld` keeps `type/cards/from_player/concealed`.
- `DeckManager.draw_replacement` pulls up to 3, keeps one at random, shuffles the rest back.

## Action Rules & Turn Handling
- Discard/pong/kong/chow must remove the consumed discard and clear `last_discarded_card`; discard uses `DeckManager.discard_card` to sync pile and `from_player`.
- Multi-hu: `allow_multiple_hu` (血流) iterates others after a discard, removes the discard, triggers `handle_call_transfer`, and resumes from the last hu player’s next seat.
- Kong bookkeeping: `execute_action` sets `last_action`, updates `consecutive_gang_count`, records gang events via `score_rules.settle_gang_payment`, and draws a replacement.
- 血流定缺: `TencentXueliuActionRules.get_valid_actions` adds `must_discard_que` when holding缺门牌; `que_men` must be locked before hu; UI auto-assigns AI缺门为手牌最少的花色.
- 血流换三张: auto after deal when `auto_exchange_three=True`; UI can disable and use `exchange_three_for_player`/`exchange_three_auto_for_ai` flows.

## Scoring & Settlement
- 大众: base 10 × capped fans (`TencentScoreRules._calculate_fans`, max 10) with multipliers for 杠上开花/炮/抢杠/妙手/海底、自摸、庄家、连杠 in [src/rules/tencent_common/score_rules.py](src/rules/tencent_common/score_rules.py).
- 血流: base 10 × fan multiplier (1–256) × gang multiplier (2^根) × special multipliers (自摸/杠上开花/杠上炮/抢杠胡/海底 each ×4) in [src/rules/tencent_xueliu/score_rules.py](src/rules/tencent_xueliu/score_rules.py); `settle_gang_payment` records `gang_events` and `last_gang_gain` for 呼叫转移/退税.
- 血流收尾: `on_deck_empty` runs 查花猪 (天命花猪豁免 via `discarded_cards`), 查大叫 (听牌最大倍数), then 退税 using recorded `gang_events`.

## AI & Interfaces
- AI entry: `AI_Decision` defaults to `AdvancedStrategy` (risk + fan potential using `score_rules`); valid actions drive choice; CLI path in [src/interface/game_api.py](src/interface/game_api.py) shows recommendation and enforces缺门弃牌。
- PyQt UI: [src/ui/mahjong_ui.py](src/ui/mahjong_ui.py) main window with rule switcher; rule pages implement [src/ui/rule_page.py](src/ui/rule_page.py) interface. 血流页面 [src/ui/xueliu_page.py](src/ui/xueliu_page.py) handles 定缺/换三张/缺门提示 and forwards actions to `TurnHandler`.
- Tk stub in [main.py](main.py) is prototypical; prefer PyQt launcher `run_pyqt_ui_game()` in [src/ui/mahjong_ui.py](src/ui/mahjong_ui.py) for manual runs.

## Conventions & Pitfalls
- Use absolute imports `from src...`; keep comments ASCII.
- Never bypass `DeckManager` for draw/discard/replacement; keep `discard_pile` and `last_discarded_card` in sync.
- Preserve state hooks: `last_action`, `consecutive_gang_count`, `changed_flower_count`, `discarded_cards`, `gang_events`, `last_gang_gain/event`, 天/地胡 candidates; hu confirmation clears candidate flags.
- 血流需先定缺后胡，缺门牌优先打出；新增结算需写清 `gang_events.contributors` 便于退税。
- Card identity is object-based: use `Card.__eq__` via `card1 == card2` or `card in list`, not `card.suit == other.suit and card.rank == other.rank`; `Card.id` is string `f"{suit}{rank}"`.
- Test fixtures in [conftest.py](conftest.py) configure `sys.path` for absolute imports from project root.

## Run & Test
- Dependencies: `pip install -r requirements.txt` (pytest, numpy, mypy, PyQt5; tkinter is stdlib).
- Full suite: `pytest tests/ -v`.
- 大众聚焦: `pytest tests/rules/tencent_common/ -v`.
- 血流聚焦（定缺/多胡/结算）: `pytest tests/rules/tencent_xueliu/ -v`.
- PyQt demo: `python -m src.ui.mahjong_ui`（选择规则，human 通过 UI 出牌）；CLI 可用 `init_game` + `TurnHandler.process_turn` 驱动实验。
- Legacy Tk stub in [main.py](main.py) is prototypical; prefer PyQt for full functionality.

