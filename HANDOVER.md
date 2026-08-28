# HANDOVER — 2026-08-24 22:30 UTC

**Next agent: read this first. All other docs reference this.**

## What 402Arena Is

Worker evaluation infrastructure. The valuable primitive is `request → candidate workers → controlled task → outcome evidence → contextual capability profile`.

> **The scarce thing is trust in autonomous workers, not choosing among commodity APIs.**

## Negative result: x402 consumer marketplace doesn't work

Arena attempted to solve "which x402 endpoint should an agent buy?" This fails structurally:

1. **Decision-time value is thin.** For most generative outputs, `intent → retrieve known-good → generate` is cheaper than blind tournaments.
2. **Evidence cost exceeds routing savings.** Learning B > A at $0.003/call costs more than the routing improvement.
3. **Prior examples predict well enough.** Retrieval covers most of the decision space.

The narrow intersection where Arena works at x402 level is too thin a market.

## What works: worker evaluation

The same mechanism transfers to evaluating agents/workers at $5–$500 per job:

```text
worker claims capability
  → benchmark/bounty
  → produces artifact
  → outcome verified
  → capability profile updates
  → future jobs route to proven worker
```

Comparison cost is justified because the job value dwarfs the evaluation cost.

## What's useful from this repo

The `arena402/` code is evaluation infrastructure:
- **bandits.py** → worker capability tracking
- **slate.py** → worker selection for benchmark
- **choice.py** → controlled evaluation tournament
- **evidence_market.py** → bounty pricing for worker benchmarks
- **provider_report.py** → worker capability profile
- **anti_cheat.py** → wash detection for fake worker reputation
- **simulation.py** → synthetic worker market for testing

All mechanism, evidence grades, conservative exploration, and capability lineage transfer to worker evaluation.

## Status

- **Tests:** 28/28 pass
- **Repo:** `prx0r/arena` at `5926495`
- **Integration point:** Moltwork worker/task graph
