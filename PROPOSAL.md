# 402Arena Evolution Proposal — Formal Dev Plan

**Status:** Draft for autonomous execution via Cogym + Hermes Kanban + Hydra
**Date:** 2026-08-24
**Objective:** Evolve 402Arena's router and acquisition policy to maximize future routing utility per subsidy dollar under hard quality constraints.

## 1. What We Evolve (Cogym Worlds)

Two evolvable components, each a Cogym world with hard gates:

1. **Router world** (`arena402.routing_replay`): `k` (adaptive slate size), MMR λ (diversity), VOI weights (α,β,γ,δ), conservative slack (95% organic utility). Gene: `k = clamp(3, ceil(sqrt(M)), 7)` + MMR rerank.
2. **Acquisition world** (VOI allocator): `ValueOfInformationAllocator` thresholds (`min_voi`, `max_subsidy_fraction`), staleness half-life, demand window. Gene: VOIConfig tuple.

Both use `Arena402ReplayWorld` (`cg_overlay/cogym_kernel/worlds/arena402/world.py:37`) over frozen 402Pilot 20,575 responses (deterministic replay, seed picks response variant). Hard gate: 10/10 correct on retrieval, non-inferior on secret holdout (last 20% chronologically).

## 2. What We Optimize For

Primary: **quality per dollar** = mean quality / total spend (provider fees + subsidies).
Secondary: **oracle regret** (gap to best affordable provider), **new-provider discovery rate**, **provider/task coverage**, **chronological holdout win rate**, **subsidy dollars per useful new edge**.

All reported in `experiments/economics.json:1` splits (train 60% / validation 20% / secret 20% chronologically).

## 3. How We Review and Compare

- **Offline replay:** `scripts/run_402pilot_experiments.py` (V1 policies: random, cheapest, empirical_mean, PA-DCT, VOI-Thompson) vs **Cogym-evolved** policies (evolved k, VOI weights). Same seeds, same frozen answers → differences are causal.
- **Metrics:** mean quality, spend, quality/$, regret, provider share, forced explorations, subsidy spend. V1 baseline: `empirical_mean` 0.824 @ $1.99 (best quality/$); V2 seeded_explorer at $1 budget: 58% new-provider share, 115 forced explorations.
- **Statistical:** Paired bootstrap on deltas, Wilson CI on win rates; promote only if `lower bound ≥ -margin`.

## 4. Seeding with Arxiv Research

Initial gene pool seeded from frontier:

- **Cascading bandits** (Kveton 2015) — slate (not single arm) optimization for relevance + diversity.
- **Best-Worst Scaling / MaxDiff** (ScienceDirect) — collect best+worst, not full ranking; fits Bradley-Terry/Plackett-Luce.
- **Contextual Information-Directed Sampling** (Hao 2022) — exploration should help future unseen contexts, not just current.
- **Conservative contextual bandits** (ICLR 2025) — guarantee ≥95% of organic utility while exploring.
- **Position bias & IPS** (Microsoft Unbiased LTR) — log slate_id, position, inclusion probability; debias.

Each paper maps to a gene: e.g., MaxDiff → `collect_best_worst=True`, conservative → `slack=0.95`.

## 5. Autonomous Execution via Hermes Kanban + Hydra + Cogym

```
HERMES KANBAN (orchestrator)
  │
  ├── Board: 402arena-evolution
  │     ├── Task: evolve router (k, MMR λ) — hermes kanban claim
  │     └── Task: evolve acquisition (VOI thresholds)
  │
  ├── Workers: hermes profiles (builder) claim tasks, run in isolated worktrees
  │     └── Candidate branch: `cogym_kernel/worlds/arena402` mutated
  │
  ├── Verify: independent verifier profile runs frozen suite, Receipt v3
  │     └── promotes exact SHA via git worktree
  │
  └── Hydra: every run appends to `arena402` SQLite → Hydra graph
        (REL_RAN_ON, REL_IMPROVED_ON, blind-choice edges)
        Next evolution queries: `top_policies` → leaders

COGYM STACK:
  - `cogym_kernel/evo/loop.py` — EvolutionCampaign with hard gates
  - `cogym_kernel/kernel/runner.py` — AsyncRunner, deterministic replay
  - `cogym_kernel/experience/client.py` — Hydra async, capability-probed
  - `scripts/run_cold_start_economics.py` — cold-start isolation ($0,1,5,10,25,50)
```

**Loop:** Hermes supervisor (`supervisor.mjs` cron) automates verify → promote → observe drift → repair WorkOrders → loop. No human in the hot path.

## 6. Next 30 Days

- Week 1: Evolve `k` + MMR λ on 402Pilot replay (chronological holdout).
- Week 2: Evolve VOI weights (α,β,γ,δ) under $5 budget cap.
- Week 3: Live Bazaar shadow (enrichment worldpack, 20 ground-truth contacts).
- Week 4: Publish `worldpack/arena402-v2` + claim, EAS attestation on Base Sepolia.

Success = evolved router beats `empirical_mean` on secret holdout quality/$ with p < 0.05, and cold-start discovers cheap-strong provider within $1.
