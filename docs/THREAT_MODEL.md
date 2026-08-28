# Threat model

## Provider gaming

### Buy ranking
Impossible by design if the organic-score invariant holds. Sponsor funds affect only research selection.

### Easy-task cherry-picking
Provider cannot nominate the exact request for a blind trial. Arena samples from real qualified demand or its sealed challenge distribution.

### Version bait-and-switch
Every evidence item carries provider version/fingerprint/time. Material endpoint changes should split or decay the belief state.

### Flood funded exposure
Per-task exposure cap + diminishing marginal trial value + sequential elimination.

## Evidence seller gaming

### Replay one transaction
Receipt/tx/evidence IDs are one-use.

### Reuse same request/output many times
Hash-level duplicate discount and risk score.

### Self-dealing wallet/provider
High-risk evidence; reject from bounties and heavily downweight from ranking.

### Generate fake output and attach real receipt
Standard x402 receipt proves interaction/delivery, not exact output. Prefer Arena-proxied evidence or the provider-signed request/response binding implemented in `chain-ts`.

## Scout gaming

### Random ranking to save tokens
Do not rely on Scout rankings for buyer-facing truth. Use hidden controls, duplicate pairs under shuffled labels and reliability posteriors. Pay only calibrated Scouts.

### Consensus collusion
Do not reward agreement alone. Use outcome audits and known-answer controls.

## Buyer feedback bias

- position/order bias → randomized blind order + propensities;
- brand bias → provider hidden before commitment;
- price bias → collect blind quality choice separately from post-price purchase;
- formatting bias → normalize presentation or stratify by output schema;
- task mismatch → compatibility hard gate.

## Privacy

Store three layers:

1. raw, access-controlled payload only when allowed;
2. redacted safe exemplar;
3. derived embedding/task/schema/metrics.

Onchain stores only research transfers and evidence commitments, never raw prompts or outputs.
