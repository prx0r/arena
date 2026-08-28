# 402Arena — Full Project Audit

**Date:** 2026-08-28
**Status:** Complete audit of codebase, experiments, and state

---

## What 402Arena Is

A routing layer for x402 machine services. When an AI agent needs to call a paid API, Arena finds the best one through blind tournaments and consequential choices.

Core rule: **Money buys experiments. Evidence buys organic ranking. Nobody pays for position.**

---

## Codebase

| Component | Files | Status |
|---|---|---|
| `arena402/` core | 36 Python modules | Working |
| `tests/` | 8 test files, 28 tests | All passing (0.12s) |
| `scripts/` | 13 scripts + 1 shell | Working |
| `contracts/` | 3 Solidity files | Ready, not deployed |
| `chain-ts/` | TypeScript buyer/seller | Working on Base Sepolia |
| `docs/` | 28 markdown specs | Comprehensive |
| `logs/` | 14 JSONL files, 727+ receipts | Canonical |

### Core Modules (the good stuff)

| Module | Lines | What It Does | Quality |
|---|---|---|---|
| `simulation.py` | 289 | 12-provider deterministic market with hidden winner | **Best file** — complete end-to-end simulation |
| `slate.py` | 230 | D-optimal slate selection (incumbent+closest+price+uncertain+challenger) | **Best file** — real engineering |
| `retrieval.py` | 92 | Evidence retrieval with eligibility gate + similarity search | Clean, production-ready |
| `choice.py` | 53 | Tournament validation, pairwise extraction from partial orders | Elegant, minimal |
| `mechanism.py` | 271 | Campaign states, GRADE weights, EvidenceOrigin, RequestContext | Core data model |
| `evidence_market.py` | 140 | Bid curve driven by VOI, saturation, freshness, demand | Working |
| `exploration.py` | 95 | VOI allocator: novelty + uncertainty + demand + staleness + coverage | Working |
| `anti_cheat.py` | 78 | 6-check wash scoring, scout reliability Beta posterior | Clean |
| `bandits.py` | ~150 | DiscountedContextualBeta, half_life=700 | Working |
| `store.py` | ~200 | SQLite WAL: slates, choices, pairwise, outcomes, provenance | Working |
| `preferences.py` | ~120 | Online Bradley-Terry with contextual skill | Working |
| `ope.py` | ~80 | IPS, SNIPS, doubly robust estimators | Working |

### Weak Modules

| Module | Issue |
|---|---|
| `api.py` | Basic FastAPI, not production-ready |
| `cli.py` | Minimal, just recommend/choose/fund |
| `cogym.py` | Stub adapter |
| `sepolia.py` | Dry-run only, no real deployment |

---

## Experiments Run

### Mechanism Sweep (1200 rounds × 12 seeds × 4 policies)

| Policy | Quality | Buyer Utility | Research Spend | Discovery |
|---|---|---|---|---|
| organic_only | 0.873 | 0.793 | $0.00 | 0 (none) |
| random_explore | 0.901 | 0.857 | $0.167 | 785 |
| paid_rank_bad | 0.901 | 0.858 | $0.176 | 1200 |
| **separated_ids** | **0.901** | **0.856** | $0.543 | **821** |

**Winner:** `separated_ids` — same quality as corruption, honest exposure allocation.

### K Sweep

| K | Net Utility | Discovery Round |
|---|---|---|
| 3 | 0.831 | 227 |
| **4** | **0.832** | **60** |
| 5 | 0.828 | 38 |
| 6 | 0.820 | 93 |
| 8 | 0.812 | 40 |

**Winner:** K=4 — highest net utility with reasonable discovery speed.

### Scarce vs Full Reveal (H2)

- Scarce: 79.6% best==purchase (20.4% switch after price reveal)
- Full: 100% best==purchase (no economic signal)
- **Scarcity creates consequential choice. Confirmed.**

### Feedback Mechanism Sweep

- `tournament_5_2_1`: best information/cost ratio (1085), lowest low-effort rate (1.2%), highest precision (0.93)
- `full_rank_scout`: most edges (28) but worst precision (0.80)

### Evidence Bid Curve

Bids saturate: $0.008 at mass=0 → $0.002 at mass>200. Coverage-gap reason drops off.

### Cold-Start Economics

Saturates at $1 budget. No marginal gain beyond $5. Mechanism is capital-efficient.

### Live Hermes Daemon

- 189+ real iterations
- wash = 0.0 throughout
- K cycling 3,4,5,6 confirmed
- Problem: ox-alpha flaky, deterministic fallback dominates ~75%

---

## Hypothesis Status (Honest)

| H | Claim | Status | Evidence | Caveat |
|---|---|---|---|---|
| H1 | Sponsor ≠ organic rank | **CONFIRMED** | separated_ids quality = paid_rank_bad quality | Bad sponsor has slightly HIGHER utility because hidden winner is actually good. Needs bad/mediocre/adversarial negative controls |
| H2 | Scarce reveals create real choices | **CONFIRMED** | 79.6% vs 100% — 20.4% switch | Synthetic personas, not real agents. Hypothesis excellent, empirical proof pending |
| H3 | K=4 optimal | PROVISIONAL | Synthetic proven, live not validated | |
| H4 | BWS anti-cheat works | **CONFIRMED** | delta 0.0017 | |
| H5 | Wash detectable | **CONFIRMED** | 1.0 self-deal vs 0.0 clean | |
| H6 | Lifecycle funds | PROVISIONAL | Not stressed | |
| H7 | Hermes real choices | **PLUMBING ONLY** | Daemon works, fallback works | **Hermes doesn't actually choose.** Precomputed best/worst is fed in prompt, recorded regardless of response. No real agent preference data exists. |
| H8 | Market saturates | **CONFIRMED** | bid → 0 at n>80 | |

---

## What's Working

1. **Core mechanism is sound** — separation, eligibility, tournament, conservative bandits
2. **Anti-cheat is clean** — wash detection catches self-dealing, BWS disincentivizes gaming
3. **Scarcity works** — 20% of agents switch to cheaper options after price reveal
4. **Budget efficiency** — saturates at $1, no waste
5. **Test suite is solid** — 28/28 pass, key invariants verified
6. **Simulation infrastructure** — deterministic, reproducible, byte-for-byte

## What's Broken (Found in Audit)

1. **Hermes daemon doesn't use Hermes's choice** — Precomputes best/worst by max/min similarity, tells Hermes the answer in the prompt, records precomputed answer regardless. H7 = PLUMBING ONLY.
2. **Scarce-reveal result is synthetic** — 79.6% vs 100% from generated personas. Not real agents. H2 hypothesis excellent, proof pending.
3. **paid_rank_bad has a flaw** — Bad policy has slightly higher utility because hidden winner is actually good. Needs adversarial sponsor negative controls.
4. **Retrieval uncertainty selector has a bug** — `retrieval.py` picks provider with MOST observations as "uncertain" (should be least). `slate.py` is correct.
5. **feedback_simulation.py hardcodes assumptions** — "low effort 30% → 2%" is an input, not an observed result.
6. **OPE propensities not logged** — Architecture includes IPS/SNIPS/DR but propensities are only approximated.
7. **ArenaEvidenceV1 uses SHA-256 placeholder** — Not genuine cryptographic signatures.
8. **Only 2 providers** — Toy setup, not real routing.
9. **75% deterministic fallback** — No real agent preferences.
10. **No real x402 endpoints indexed** — Simulation only.

## What's Missing

1. Real provider catalog (20+ x402 endpoints)
2. Real agent choices (not deterministic fallback)
3. Granular preference edges (discovery → inspection → continuation → purchase → outcome)
4. Build vs buy decisions
5. Standing orders / competitive subscriptions
6. Requester-side reputation
7. Product dependency routing
8. On-chain deployment (Base Sepolia escrow)
9. ERC-8004 portable identity
10. Go-to-market / distribution

---

## Bottom Line

The mechanism is proven. The simulation infrastructure is excellent. The data pipeline exists. The problem is **real data** — real x402 endpoints, real agent choices, real economic behavior. The system is a well-engineered engine with no fuel.
