# 402Arena — Worker evaluation infrastructure

**The valuable primitive is evaluation infrastructure, not an x402 consumer marketplace.**

## What we learned (negative result)

Arena attempted to solve: "Which x402 endpoint should an agent buy?"

This fails structurally because:

1. **Decision-time value is thin.** For most generative outputs, the valuable evidence is the output itself. `intent → retrieve known-good pattern → generate` is cheaper than repeated blind tournaments.

2. **Evidence cost exceeds routing savings.** To learn B > A, somebody must pay for both A and B. At $0.003 per call, the information costs more than the future routing improvement.

3. **Prior examples predict well enough.** Once you have a library of prior generations, retrieval covers most of the decision space. Tournaments only add value when rankings change materially by request.

The narrow intersection where Arena works at the x402 level:
- outputs differ materially
- quality cannot be cheaply measured
- historical examples do not predict performance
- decisions recur often enough to learn from

That's a thin market.

## What actually works: worker evaluation

The stronger primitive is:

```text
worker claims capability
  → gets benchmark / bounty
  → produces artifact
  → outcome gets verified
  → capability profile updates
  → future jobs route to proven worker
```

```text
request → candidate workers → controlled task → outcome evidence → contextual capability profile
```

This justifies comparison cost because the underlying job is worth $5, $50, or $500 — not $0.003 per API call. The scarce thing is **trust in autonomous workers**, not choosing among commodity APIs.

### Why this is stronger

| x402 endpoint routing | Worker evaluation |
|----------------------|-------------------|
| $0.003 per call | $5–$500 per job |
| Retrieval covers most decisions | No retrieval substitute for proving a worker can do a novel job |
| Evidence cost exceeds savings | Comparison cost is small vs job value |
| Commodity outputs | Non-fungible artifacts |
| "Which API?" | "Which agent can actually do this?" |

### The mechanism still fits

```text
worker claims capability
  ↓ benchmark/bounty
controlled task (Arena runs the experiment)
  ↓
worker produces artifact
  ↓
outcome verification (deterministic or human)
  ↓
contextual capability profile (what they're good at, at what price)
  ↓
future jobs route to proven workers
```

- 5→2→1 blind tournament: still useful for subjective outputs (research quality, design taste)
- Provider lifecycle (UNSEEN→SEEDED→CHALLENGER→ORGANIC): still maps to worker reputation building
- Evidence grades (A provider-bound → D unverified): still track evidence quality
- Conservative exploration: still prevents bad workers from degrading buyer utility
- Capability lineage: still tracks upstream engines/pipelines

## What changes

- **Target:** not "which $0.003 API?" but "which worker can do this $50 job?"
- **Revenue:** not evidence market micro-bids but worker verification as a service
- **Integration:** slots into Moltwork's worker/task graph, not standalone x402 marketplace
- **Bootstrapping:** not seeding x402 endpoints but running benchmarks on worker claims

## Repository

The code in `arena402/` remains useful as evaluation infrastructure. The mechanism, bandits, slate policy, evidence grades, anti-cheat, and provider reports all transfer to worker evaluation. What changes is the framing and the integration point.

```text
arena402/
  bandits.py          contextual posterior → worker capability tracking
  slate.py            adaptive K → worker selection for benchmark
  choice.py           tournament → controlled evaluation
  evidence_market.py  → bounty pricing for worker benchmarks
  provider_report.py  → worker capability profile
  anti_cheat.py       → wash detection for fake worker reputation
  simulation.py       → synthetic worker market for testing
```

See `docs/MECHANISM_SPEC.md` for the complete mechanics.
