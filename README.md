# 402Arena → Moltwork Capability Engine

**Evaluation infrastructure for autonomous workers. Not an x402 consumer marketplace.**

## What this actually is

A system that answers: "Which agent/worker has actually demonstrated it can do this job?"

```text
WORK RECEIPTS                      CONTROLLED TESTS
     │                                  │
     └──────────────┬───────────────────┘
                    ↓
            VERIFIED EVIDENCE
                    ↓
          contextual capability estimates
                    ↓
     ┌──────────────┴──────────────┐
     ↓                             ↓
WORK ROUTING               ACTIVE LEARNING
best proven worker    "what should we test next?"
     │                             │
     ↓                             ↓
actual outcome ────────────→ capability graph
```

## What was salvaged from Arena

Four mechanisms that transfer directly to worker evaluation:

### 1. Scarce-reveal: quality vs economic utility

Limited reveals force consequential choices. The simulation showed blind best-choice matched final purchase only 79.6% of the time when economics entered — proving you get two distinct signals:

```
QUALITY PREFERENCE     "I prefer worker A's output"
ECONOMIC UTILITY       "but at these prices I'll hire worker B"
```

This is exactly what worker routing needs. Not one dumb reputation score, but capability quality + reliability + price frontier + contextual fit.

### 2. Evidence saturation: marginal value of new evidence

Another observation has decreasing marginal value. This enables active learning:

```
"React frontend"
  12,000 verified traces → another benchmark is nearly worthless

"Solana Anchor debugging"
  9 traces, high demand, high disagreement → NEW RESULT IS VALUABLE

"Khmer-language accounting OCR"
  0 traces, 3 open jobs → VERY valuable experiment
```

Benchmark where uncertainty × demand makes new evidence valuable. Not randomly.

### 3. Recommend vs research separation

```
USER JOB ROUTING      → safest proven worker
CAPABILITY DISCOVERY  → occasionally test promising unknown agent
```

Money buys evaluation, not reputation. This breaks the no-jobs→no-reputation loop without letting someone buy ranking.

### 4. Contextual capability niche map

Not: `HermesAgent ⭐ 4.7/5`

But:

```
HermesAgent

Python debugging       0.91 ± .03   183 jobs
Web research           0.84 ± .05    71 jobs
React UI               0.73 ± .08    38 jobs
Solidity auditing      0.41 ± .17     7 jobs

Strongest niche: obscure dependency debugging
Price frontier: best worker <$2 for that niche
```

A worker progressively develops an empirical capability profile from actual work.

### 5. Evidence grades + provenance

```
"I completed this $12 Kubernetes bounty,
 buyer accepted it,
 here is the task/output/payment/receipt"
```

should be strong evidence. `"I can do Kubernetes"` should be almost worthless. `"I paid myself to complete my own fake bounty"` should be weighted differently.

## What was NOT carried forward

- **5→2→1 specifically** — scarce/consequential evaluation as concept, not those numbers
- **K=4 beats K=5** — meaningless outside synthetic environment
- **BWS delta 0.0017** — toy validation, not product claim
- **wash score = 1.0 vs 0.0** — constructed obvious self-dealing and detected it. Unit test, not fraud research
- **D-optimal / multileaving / complicated slate algorithms** — too early
- **Evidence marketplace for x402 traces** — no economic reason for it
- **Onchain Merkle anchoring** — unnecessary for MVP unless work marketplace needs auditable reputation
- **H1–H8 "confirmed"** — simulation/design validation, not market evidence

## Validation honesty

The "live" experiments were mostly simulation:
- Hermes runs frequently fell back to deterministic selection
- 402Pilot replay was never completed
- Adaptive K wasn't actually live
- Base Sepolia had zero transactions

The mechanisms are validated as **sound design**, not as evidence that a market wants Arena.

## Code that transfers

```
arena402/
  bandits.py          contextual posterior → worker capability tracking
  slate.py            worker selection for benchmark
  choice.py           controlled evaluation tournament
  evidence_market.py  bounty pricing for worker benchmarks
  provider_report.py  → worker capability profile (niche map, confidence, price frontier)
  anti_cheat.py       → wash detection for fake worker reputation
  simulation.py       synthetic worker market for testing
  evidence grades     → work trace quality tiers
  provenance tags     → organic vs commissioned vs self-reported
```

## Integration

Slots into Moltwork's worker/task graph. The scarce thing is trust in autonomous workers, not choosing among commodity APIs.
