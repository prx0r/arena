# HANDOVER — 2026-08-24 23:00 UTC

**Next agent: read this first.**

## What this repo is

Moltwork Capability Engine — evaluation infrastructure for autonomous workers. Extracted from 402Arena, an x402 consumer marketplace experiment that failed structurally.

## What was learned

### Negative result: x402 consumer marketplace doesn't work

- Decision-time value is thin (retrieval covers most decisions)
- Evidence cost exceeds routing savings at $0.003/call
- Prior examples predict well enough for most generative outputs

### What's valuable (salvaged)

1. **Scarce-reveal mechanism** — quality vs economic utility separation. 79.6% switch rate proves blind preference ≠ purchase preference. Directly useful for worker routing.

2. **Evidence saturation** — marginal value of new evidence decreases. Enables active learning: benchmark where uncertainty × demand makes new evidence valuable.

3. **Recommend vs research separation** — money buys evaluation, not reputation. Breaks no-jobs→no-reputation loop.

4. **Contextual capability niche map** — not global ratings but per-task-cluster capability profiles with confidence intervals and price frontiers.

5. **Evidence grades + provenance** — A_PROVIDER_BOUND through D_UNVERIFIED, organic vs commissioned vs self-reported. Work trace quality tiers.

### Validation honesty

H1–H8 are **simulation/design validation**, not market evidence:
- Hermes runs fell back to deterministic selection
- 402Pilot replay never completed
- Adaptive K not live
- Base Sepolia: zero transactions
- K=4 beats K=5: meaningless outside synthetic
- BWS delta 0.0017: unit test
- Wash detection: constructed obvious case

## Code that transfers

```
arena402/bandits.py       → worker capability tracking
arena402/slate.py         → worker selection for benchmark
arena402/choice.py        → controlled evaluation
arena402/evidence_market.py → bounty pricing
arena402/provider_report.py → capability profile (niche map, confidence, price frontier)
arena402/anti_cheat.py    → wash detection for fake reputation
arena402/simulation.py    → synthetic worker market
arena402/mechanism.py     → evidence grades, provenance, lifecycle
```

## Status

- **Tests:** 28/28 pass
- **Repo:** `prx0r/arena` at `19a55c2`
- **Integration:** slots into Moltwork worker/task graph
