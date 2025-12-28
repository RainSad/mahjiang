# Mahjong AI Agent - Copilot Guide

## Architecture & Purpose
- **Project goal**: Modular Tencent Mahjong simulator with pluggable rule systems. Main implementation is `TencentCommonRule` composed from hu/action/score submodules.
- **Core loop**: [src/core/logic/game_flow.py](src/core/logic/game_flow.py) → `TurnHandler.process_turn()` → draws card → checks `rule.can_hu()` → gathers `rule.get_valid_actions()` → `AI_Decision.make_decision()` → `execute_action()` → switches player unless kong/flower recurses.
- **Deck**: 144 tiles (108 suited: 万/筒/条 1-9 ×4; 28 winds/arrows: 东南西北中发白 ×4; 8 flowers: 梅兰竹菊春夏秋冬) created in `TencentCommonRule.create_initial_deck()`.

## Data Contracts & Key Classes
- **Card**: `id = f"{suit}{rank}"` (e.g., 万1, 风东). Always use `Card.__eq__()` for comparison, never manual string checks.
- **Player**: Tracks `hand`, `melds`, `drawn_card`, `last_action`, `consecutive_gang_count`, `changed_flower_count`, `is_dealer`, `men_feng`/`chang_feng`, `next_player`/`previous_player` links.
- **GameState**: `deck`, `discard_pile`, `last_discarded_card`, `current_player`, `wind`, `round_number`, `game_stage` (init→playing→ended), `rule` instance.
- **Action**: type (draw/discard/chow/pong/kong/hu/flower), `card`, `from_player`, `timestamp`.
- **Meld**: type (吃/碰/明杠/暗杠/补杠/补花), `cards`, `from_player`, `concealed`.

## Rule Plugin Pattern
- **Base class**: `BaseRule` defines interface; rule implementations compose submodules.
- **TencentCommonRule**: Sets `allow_chow=True`, `allow_pong=True`, `allow_kong=True`, `max_fans=10`, `mandatory_discard=True`. Routes all validations to submodules—never hardcode action logic outside rule classes.
- **Submodules**:
  - `TencentActionRules`: `can_chow` (only from previous player, only suited tiles, checks rank adjacency), `can_pong` (≥2 in hand), `can_kong` (明杠: 3 in hand + discard; 暗杠: 4 in hand; 补杠: upgrade existing pong), `can_flower` (any 花 in hand), `get_valid_actions`.
  - `TencentHuRules`: Validates pair+four-meld structure, at least one fan required. **Chicken hu (fans==1) only self-draw**. Special fans: `_is_gang_shang_kai_hua` (杠上开花), `_is_qiang_gang_hu` (抢杠胡), `_is_gang_shang_pao` (杠上炮) check `last_action` of `last_discarded_card.from_player`.
  - `TencentScoreRules`: `base_score=10`. `_calculate_fans()` aggregates fan checks (88/64/48/36/32/24/16/12/8/4/2/1 fan types), capped at `rule.max_fans`. Multipliers: gang_shang_kai_hua/pao/qiang_gang_hu/miao_shou_hui_chun/hai_di_lao_yue ×2, dealer ×2, consecutive_gang_count ×(count+1).

## Turn Execution Flow
- **TurnHandler.execute_action()** side effects:
  - `discard`: Removes card from hand, updates `discard_pile`/`last_discarded_card`, resets `consecutive_gang_count=0`.
  - `chow/pong`: Removes cards from hand, appends `Meld`, removes consumed card from `discard_pile`, sets `last_discarded_card=None`, resets `consecutive_gang_count=0`.
  - `kong` (明杠/暗杠/补杠): Updates `melds`, increments `consecutive_gang_count`, draws replacement via `DeckManager.draw_replacement()`, **recurses** `process_turn()`.
  - `flower`: Appends `Meld`, removes flower from hand, increments `consecutive_gang_count`, draws replacement, **recurses**.
- **Discard consumption**: Always remove from `discard_pile` and set `last_discarded_card=None` when chow/pong/kong consumes it.

## AI Decision System
- **AI_Decision** ([src/ai/strategy/decision.py](src/ai/strategy/decision.py)): Defaults to `AdvancedStrategy` if no strategy provided. Returns `Action` via `make_decision()` or `(Action, reason)` via `recommend_with_reason()`.
- **Strategies**: Extend `BaseStrategy`, implement `recommend(player, game_state, valid_actions)`.

## Testing & Development
- **Test framework**: pytest with conftest injecting project root to `sys.path`.
- **Run tests**: `pytest tests/` or `pytest tests/rules/tencent_common/` (add `-v` for verbose). Test fixtures for `player`, `score_rules` in [tests/rules/tencent_common/test_score_rules.py](tests/rules/tencent_common/test_score_rules.py).
- **Imports**: Always use **absolute imports** (`from src.core.data.card import Card`).

## Project Conventions
- **Player positions**: 东/南/西/北.
- **Game stage**: init → playing → ended.
- **Language**: Chinese for in-game strings (番型, 操作类型, etc.); English for code/comments acceptable.
- **Consistency**: Keep `discard_pile` and `last_discarded_card` synchronized when consuming discards.

## Known Gaps & Future Work
See [structure.md](structure.md) §4 for detailed gap analysis. Key unimplemented features:
- Opening rules: 换牌 (exchange tiles), 跟庄 (follow-dealer instant payouts).
- 补花/补牌: Full flower supplement + 3-choose-1 replacement flow.
- 连杠/接杠: Multi-kong inheritance and consecutive gang logic (hooks exist: `consecutive_gang_count`, `last_action`).
- 三滩承包: Three-exposure liability (土豪场 only).
- Dealer multiplier: Defined but not fully integrated (hook: `is_dealer`).

**Preserve state hooks** (`last_action`, `consecutive_gang_count`, `changed_flower_count`) for future rule extensions.
