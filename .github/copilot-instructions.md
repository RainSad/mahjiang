# Mahjong AI Agent - Copilot Guide

## Architecture & Flow
- Modular rules plugin: [src/rules/tencent_common/rule.py](src/rules/tencent_common/rule.py#L1-L80) and [src/rules/tencent_xueliu/rule.py](src/rules/tencent_xueliu/rule.py#L1-L110) wrap hu/action/score submodules; never reimplement logic outside these entrypoints.
- Core loop: [src/core/logic/game_flow.py](src/core/logic/game_flow.py#L1-L40) → `TurnHandler.process_turn()` → draw → `rule.can_hu()` → `rule.get_valid_actions()` → AI/CLI pick → `execute_action()`; ends on hu unless `allow_multiple_hu` is set (血流成河 keeps playing).
- Decks: `TencentCommonRule.create_initial_deck()` builds 144 tiles (万/筒/条 + 风/箭 + 花) while `TencentXueliuRule.create_initial_deck()` is 108 suited tiles only.

## Data Contracts
- Use `Card.__eq__()` for comparisons (no manual suit/rank checks). `Card.id` is `f"{suit}{rank}"`.
- `Player` tracks `hand`, `melds`, `drawn_card`, `last_action`, `consecutive_gang_count`, `changed_flower_count`, dealer flags, position links, and 天/地胡候选标志 (`is_tian_hu_candidate` / `is_di_hu_candidate`) set in [src/core/logic/turn_handler.py](src/core/logic/turn_handler.py#L15-L55).
- `GameState` holds `deck`, `discard_pile`, `last_discarded_card`, `current_player`, `winners`, `wind`, `round_number`, `game_stage`, `rule`, `first_turn` (首轮天/地胡判断) and per-rule extras (e.g., settlement logs in 血流成河).

## Turn Handling
- `process_turn` draws, marks 天/地胡 candidates on the first draw, confirms flags on self-hu, then executes AI/CLI decisions; kong/flower recurse into another turn, so keep state pure between calls ([src/core/logic/turn_handler.py](src/core/logic/turn_handler.py#L15-L170)).
- Multi-hu path: when `allow_multiple_hu` is True, discards can trigger multiple `hu` actions, discard pile entry is removed, `handle_call_transfer` is invoked for杠上炮收益移转, and play resumes from the last hu player’s next seat.
- 定缺 (血流成河): `TencentXueliuActionRules.get_valid_actions()` inserts `must_discard_que` when the hand still holds the缺门 suit; AI path discards that suit before other actions ([src/rules/tencent_xueliu/action_rules.py](src/rules/tencent_xueliu/action_rules.py#L35-L110), [src/core/logic/turn_handler.py](src/core/logic/turn_handler.py#L64-L95)).
- Kong execution records连杠次数, triggers `score_rules.settle_gang_payment`, draws replacement via `DeckManager.draw_replacement`, and consumes discard pile entries when appropriate ([src/core/logic/turn_handler.py](src/core/logic/turn_handler.py#L97-L170)).

## Rule Highlights
- 腾讯大众 (common): allows chow/pong/kong, `max_fans=10`, `mandatory_discard=True`; hu requires pair+four melds and at least one fan (鸡胡需自摸) ([src/rules/tencent_common/hu_rules.py](src/rules/tencent_common/hu_rules.py#L1-L120)). Fans are summed across 88→1 brackets then capped, with multipliers for 杠上开花/炮/抢杠/妙手/海底 + dealer + 连杠 ([src/rules/tencent_common/score_rules.py](src/rules/tencent_common/score_rules.py#L1-L120)).
- 血流成河: no chow, allows multiple hu, 支持换三张, 定缺强制出缺牌, room levels gate 256/128番 (连七对/九莲) ([src/rules/tencent_xueliu/rule.py](src/rules/tencent_xueliu/rule.py#L1-L120)). Scoring uses base 10 × fan multiplier (1–256 with互斥处理) × gang multiplier (each gang ×2) × special multipliers (自摸/杠上开花/杠上炮/抢杠胡/海底 each ×4) with gang payments settled immediately ([src/rules/tencent_xueliu/score_rules.py](src/rules/tencent_xueliu/score_rules.py#L1-L140)).
- End-of-wall settlement (血流): 查花猪→查大叫→退税; 天命花猪豁免 if all discards are 缺门 ([src/rules/tencent_xueliu/rule.py](src/rules/tencent_xueliu/rule.py#L120-L220)).

## AI & Interface
- `AI_Decision` defaults to `AdvancedStrategy` and drives choices for AI players ([src/ai/strategy/decision.py](src/ai/strategy/decision.py)). CLI fallback lives in [src/interface/game_api.py](src/interface/game_api.py).
- `init_game` wires rule selection, player seats, dealer flag, and shuffles/deals; 血流规则 calls `exchange_three` after dealing ([src/core/logic/turn_handler.py](src/core/logic/turn_handler.py#L178-L230)).

## Conventions & Pitfalls
- Always use absolute imports (`from src...`).
- Keep `discard_pile` and `last_discarded_card` in sync when actions consume a discard (chow/pong/kong/hu).
- Respect state hooks for future features: `last_action`, `consecutive_gang_count`, `changed_flower_count`, `discarded_cards`, `gang_events`.
- Card comparisons must use object equality; suits include 汉字, but stick to ASCII in code/comments.

## Testing & Commands
- Global tests: `pytest tests/ -v`.
- Common rule focus: `pytest tests/rules/tencent_common/ -v`.
- 血流成河 suite (38 tests): `pytest tests/rules/tencent_xueliu/ -v` (covers 番型互斥、天/地胡、结算、定缺、多胡 flow).
