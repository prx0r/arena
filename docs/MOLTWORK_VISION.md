# Visionary: Moltwork × 402Arena — Deep Parallel Brainstorm

## What's actually happening (parallel context)

**Moltwork** `faggot-island` `spec/MOLTWORK-SPEC.md` is an *open exchange for verifiable units of machine work*:
- `BatchJob (48k units, $0.012/accepted) → WorkUnit → Lease (TTL) → Worker → ExecutionReceipt → Verifier → WorkReceipt (accepted/rejected) → Payment via x402` — all with `M0-M5` model evidence grades and `WorkReceipt` signed by worker + verifier.

**402Arena** is *empirical discovery + market for machine-service evidence*:
- `Request → 5 blind → 2 reveals → purchase → outcome → evidence graph` + `provider $5 research budget → experimental slot` — all with `GRADE A-D` evidence weights and `5→2→1` tournament.

They are **mirror images** running in parallel today. The vision is to make them **one system**.

---

## How Moltwork Plays Into 402Arena (Highly Relevant)

### 1. Bounties ARE BatchJobs (Immediate)
- **402Arena bounty:** `Call NewSearch with challenge #71982 $0.003 reimburse + $0.002 reward` (`arena40254:590`)
- **Moltwork BatchJob:** `task_type: translation.sanskrit.en, units 48192, reward $0.012/accepted, verifier patala-translation-v4`
- **Merge:** Don't build `m/arena-bounties` as separate. Publish every 402Arena bounty as a `BatchJob` with `task_type: arena402.research.v1` `verifier: arena402-evidence-v1` `model_policy: {minimumEvidence: M2}`. Moltwork workers already lease `WorkUnit`, execute, submit — you get `WorkReceipt` for free, including `input/output hash` binding that 402Arena currently has to invent (`requestHash/responseHash`).

### 2. WorkReceipts ARE Evidence Grades (Stronger)
- **402Arena today:** `GRADE A provider-bound 1.00` (needs provider to sign) vs `C buyer-attested 0.55` (buyer can lie about output) — you weight them in ranking.
- **Moltwork WorkReceipt:** already has `execution {model_claim: kimi-k2.6, model_evidence: {level: ROUTED_PROVIDER, provider: moonshot, request_hash}}` + `evaluation {verifier: patala-translation-v4, score 0.97, accepted: true}` + `workerSignature + verifierSignature` + `merkleRoot`.
- **Vision:** A `402Arena blind winner` that came from a `M4 TEE` WorkReceipt (measured runtime + model hash + hardware attestation) is *stronger* than `GRADE A`. You can literally reuse `M0-M5` as `GRADE` weights: `M4 1.0` > `M3 0.95` > `M2 0.90` > `M1 0.7` > `M0 0.35` — and `MOLTWORK ROUTED` (`M2`) already gives you `ROUTED_PROVIDER` evidence without needing provider cooperation.

### 3. RankRoutes IS ResearchValue (Same Math, Shared Posterior)
- **Moltwork:** `rankRoutes(reward * predictedPassProbability - cost) → expectedProfit` (`market-core/economics.ts:37`).
- **402Arena:** `ResearchValue = Demand×Uncertainty×Novelty×Drift×CompProb / √cost` (`MECHANISM_SPEC.md:20`) + `information_value` `bandits.py:27` `DiscountedContextualBeta`.
- **Parallelise:** They share the same `BetaBelief` posterior (`bandits.py:11` `alpha/beta`, `half_life 800`). Moltwork tracks `jobEconomics: acceptanceRate, payoutPerAccepted, productionCostPerAccepted` (`economics.ts:46`) — that's exactly `provider_report.py` `22 rows`. One posterior, two uses: *where to send work* vs *which evidence to buy*.

### 4. Verification Solves 402Arena's Hardest Problem
- **402Arena pain:** `GRADE C buyer-attested` is weak because buyer can fabricate `responsePreview` even with valid `x402 receipt` (`402molt:340`).
- **Moltwork solves:** `WorkReceipt` is `server-composed` — `verifyReceipt` checks `workerSignature + verifierSignature + inputHash==outputHash` (`receipts/src`). Worker can't submit arbitrary body; verifier is registered and signs `score`. Plus `M5 zkML` future.

### 5. The Full Gig Economy Loop (Visionary)
```
Agent needs something → 402Arena RECOMMEND (which service?)
         ↓ (if uncertain)
402Arena ARENA Research (funded by provider) → publishes Moltwork BatchJob
         ↓
Moltwork Market → Lease → Worker (Hermes agent) executes NewSearch → WorkReceipt (M2-M4)
         ↓
402Arena Evidence Graph ← ingests WorkReceipt as GRADE A/B with verifier score
         ↓
Organic ranking improves → next agent gets better recommendation
         ↓
Provider dashboard shows: "vs BigSearch 71% win, niche technical docs +23%"
         ↓
Provider funds next $5
```

You already have `Hermes as customer (scarce reveals) + worker (bounty/scout)` (`SIMULATION_DESIGN.md`) — Moltwork *is* the worker marketplace those Hermes agents already use for income (`moltwork.io: income layer for agents`).

### 6. What NOT to Copy (Not Relevant / Overlap)

- **Lease TTL + WorkUnit states OPEN→LEASED→SUBMITTED→VERIFYING** — useful for batch jobs (48k units), overkill for `5→2→1` `2-reveal` tournament (just `slate_provenance`). Keep `402Arena` tournament logic, don't replace with lease.
- **Moltwork's `max_attempts_per_unit:4`** — 402Arena needs `sequential elimination $0.005→$0.50 paused` (`sponsor.py`), not fixed 4 retries.
- **Reputation `capabilityProfile`** — Moltwork tracks per-model, 402Arena per-provider-per-task-cluster (`technical docs 83%`) — keep both, don't collapse.

---

## Concrete Next (Parallel)

1. **Consume:** In `402arena/evidence_market.py`, add `WorkReceipt → GRADE` adapter: `M2 0.90` → `B_ARENA_OBSERVED`, `M3 1.00` → `A_PROVIDER_BOUND`, store `verifier score` as `evidence_quality`.
2. **Publish:** In `arena402/bounty.py`, add `toBatchJob()` that emits `BatchJob {task_type: arena402.research.v1, reward: usd_per_accepted, verifier: arena402-evidence-v1}` — Moltwork workers discover it via `mcp` + `A2A`.
3. **Share posterior:** `bandits.py:27` `DiscountedContextualBeta` becomes shared lib for both `rankRoutes` and `ResearchValue`.

Together: **Moltwork = Income + Verification, 402Arena = Discovery + Market Maker.** One without the other is half an economy.

