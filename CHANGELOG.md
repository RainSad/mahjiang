# Changelog

## 2025-12-29

- Added: Bayes-driven risk evaluator in src/ai/evaluation/risk_evaluator.py
  - New API: evaluate_discard_reaction_prob() returns per-opponent probabilities and aggregate expected loss
  - Backward compat: evaluate_card_risk() remains available and now uses Bayes aggregate
- Updated: AdvancedStrategy integrates Bayes risk in src/ai/strategy/advanced_strategy.py
  - Phase-aware risk weighting (序/中/尾)
  - Explainable notes (熟张/绝张/清一色倾向/拆对子)
- Docs: Updated .github/copilot-instructions.md and src/ai/evaluation/risk.md with Bayes formulas and usage
- Rules compatibility:
  - Tencent Common: chow risk only for next seat
  - Tencent Xueliu: chow disabled; 缺门 gating reduces hu risk
- Tests: Full suite 70/70 passed locally
- Behavior: Safer late-game discards (prefer 熟张/绝张), risk-aware selection balances fan potential
