Plan: Detailed Features & Output Schema
Use discard/meld signals from the table to estimate per-opponent claim probabilities, respecting rule variants for chow.

Steps
Define feature detection in RiskEvaluator across table state (熟张/绝张/幺九/中张/字牌/连张支撑) with per-opponent and global counts.
Encode seat relation and chow handling: next player only in Tencent Common; chow disabled in Tencent Xueliu.
Specify neighbor sets and table-frequency multipliers for chow and pong/kong likelihoods.
Add discard-pattern signals (清一色倾向、拆对子、无字弃牌) and gang/flower prior boosts.
Return a structured object from evaluate_discard_reaction_prob() and consume it in AdvancedStrategy.
Feature Signals
熟张: per opponent, is_safe_seen_opponent=True if they have discarded the exact Card.id at least once; global seen_count_table from game_state.py discard_pile + visible player.py melds.
绝张: remaining_visible = 4 - (table_discard_count + table_meld_count) on the exact Card.id; is_last_tile=True when 1; is_exhausted=True when 0.
幺九/中张/字牌: from card.py suit/rank:
is_terminal when suit ∈ {万,筒,条} and rank ∈ {1,9}
is_middle when rank ∈ {2..8}
is_honor when suit ∈ {风,箭}
连张支撑 (chow support, suited only): neighbors N(r) = {r-2,r-1,r+1,r+2}. Triplets: (r-2,r-1,r), (r-1,r,r+1), (r,r+1,r+2). Define sequence_support_score ∈ [0,1] from neighbor remaining ratios: remaining_ratio(n)=(4 - visible_count(n))/4, aggregate by geometric mean per triplet, take max across triplets.
Seat relation:
Tencent Common rule.py: chow risk computed only for next seat relative to current_player in game_state.py.
Tencent Xueliu rule.py: chow disabled → chow_prob=0.
Discard patterns (per opponent from discarded_cards):
清一色倾向: last k (3–5) discards same suit and ranks in 2–8 → flush_tilt=True.
拆对子: same Card.id appears twice in a short window (2–3 latest) → pair_break=True.
无字弃牌: no honors among last k discards → honor_tilt=True.
Gang/flower priors: if opponent last_action is kong or flower in player.py, boost tenpai_prior for 1–2 turns; also consider consecutive_gang_count.
Output Schema
Function: evaluate_discard_reaction_prob(card, player, game_state) in risk_evaluator.py.
Return:
per_opponent: list of
opponent_id: string (e.g., player name)
seat: string (东/南/西/北)
claim_probs:
hu: float [0,1]
pong: float [0,1]
kong: float [0,1]
chow: float [0,1] (0 under Xueliu; non-zero only for next seat under Common)
features_used:
is_honor, is_terminal, is_middle: booleans
is_safe_seen_opponent: boolean
seen_count_table: int 0–4
is_last_tile, is_exhausted: booleans
sequence_support_score: float [0,1]
flush_tilt, pair_break, honor_tilt: booleans
recent_meld_count: int
last_action_type: string (discard/pong/kong/chow/flower/draw/None)
consecutive_gang_count, changed_flower_count: ints
priors:
tenpai_prior: float [0,1]
holding_prior: float [0,1] (≥k copies needed per claim)
expected_loss:
hu, pong, kong, chow: floats (severity-weighted)
total: float
notes: short rationale string
aggregate:
P_any: float [0,1] = 1 − Π_i(1 − max claim prob_i)
total_expected_loss: float = Σ_i expected_loss.total
component_weights:
seat_relation_weight, table_freq_weight, safe_seen_weight, last_tile_weight, pattern_weight, gang_flower_weight: floats
phase: early/mid/late from deck_manager.py len(game_state.deck)
rule_variant: tencent_common/tencent_xueliu
metadata: deck_remaining, discard_pile_size, current_player_id, last_discarded_card_id
Next steps

I can also provide a compact defaults table (priors, severity, likelihood multipliers) embedded as constants, and a brief dataflow sketch for AdvancedStrategy._bayes_risk() in advanced_strategy.py. Would you like that?