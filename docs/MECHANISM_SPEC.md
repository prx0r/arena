# Capability Engine mechanism specification v0.6

## What this is

Evaluation infrastructure for autonomous workers. Extracted from 402Arena (x402 consumer marketplace experiment that failed structurally).

The valuable primitive: `request → candidate workers → controlled task → outcome evidence → contextual capability profile`.

## Validated primitives

These mechanisms are validated as sound design through simulation. They are NOT validated as market-validated products.

### 1. Scarce-reveal: quality vs economic utility separation

Limited reveals force consequential choices. Simulation showed blind best-choice matched final purchase only 79.6% when economics entered, producing two distinct signals:

```
QUALITY PREFERENCE     "I prefer worker A's output"
ECONOMIC UTILITY       "but at these prices I'll hire worker B"
```

Implementation: K blind candidates → keep 2 → reveal first → buy or reveal second → record purchase and outcome.

### 2. Evidence saturation: marginal value of new evidence

New observation value decreases as area saturates. Enables active learning:

```
information_value =
  uncertainty
× demand
× transferability
× novelty
÷ sqrt(evidence_mass)
```

Benchmark where uncertainty × demand makes new evidence valuable. Not randomly.

### 3. Recommend vs research separation

```
RECOMMEND              RESEARCH
best proven worker     what should we test next?
buyer utility first    information gain first
no sponsor term        sponsor budget may fund exposure
```

Money buys evaluation, not reputation. Breaks no-jobs→no-reputation loop.

### 4. Worker lifecycle

```
UNSEEN → SEEDED → CHALLENGER → ORGANIC
                    └──→ ELIMINATED
                    └──→ PAUSED
```

### 5. Evidence grades + provenance

```
A_PROVIDER_BOUND    provider-signed work trace + payment evidence
B_ARENA_OBSERVED    Arena observed full transaction
C_BUYER_ATTESTED    buyer claims payload + payment receipt
D_UNVERIFIED        low-weight research signal

ORGINIC             buyer found worker naturally
ARENA_COMMISSIONED  Arena bounty
PROVIDER_SPONSORED  worker paid for trial
SELF_REPORTED       worker claims (lowest weight)
```

### 6. Capability niche map

Not global ratings. Per-task-cluster profiles:

```
Worker: HermesAgent

Python debugging       0.91 ± .03   183 jobs
Web research           0.84 ± .05    71 jobs
React UI               0.73 ± .08    38 jobs

Strongest niche: obscure dependency debugging
Price frontier: best worker <$2 for that niche
```

Built from: request cluster distribution, pairwise opponents, confidence intervals, price/quality frontier, cost per finding.

## Validation honesty

- **Simulation validated:** mechanism soundness, scarce-reveal separation, evidence saturation curve, recommend/research separation, lifecycle transitions
- **NOT validated:** market demand, pricing, whether workers want this, whether buyers pay for it
- **H1–H8 from Arena:** simulation/design validation only. Hermes fell back to deterministic. 402Pilot never completed. Base Sepolia: zero transactions.

## What was NOT carried forward

- Specific K values (K=4 beats K=5 is synthetic-only)
- BWS delta claims
- D-optimal / multileaving / complicated slate algorithms
- x402 evidence marketplace
- Onchain Merkle anchoring for MVP
