# Cogym experiment matrix

All experiments must be replayable with fixed seeds and emit content-addressed receipts.

## E0 — invariants

Before performance tests:

- sponsor balance has zero influence on organic score;
- escrow conservation;
- bounty replay protection;
- same simulation seed → byte-identical event hash;
- no pairwise edge inferred from a simple reveal choice;
- evidence saturation decreases bid price.

Implemented in `tests/`.

## E1 — cold-start discovery

Question: can a new, cheaper niche winner earn organic distribution?

Treatments:

1. organic-only;
2. random exploration;
3. sponsor-corrupted rank (negative control);
4. separated contextual research.

Metrics:

- discovery round;
- buyer utility/quality;
- research spend;
- qualified→appearance→finalist→purchase funnel;
- organic purchases after discovery;
- tail regret.

## E2 — K / choice-set size

Treatments: K = `3,4,5,6,8`, plus adaptive K.

Measure:

- net buyer utility after explicit comparison cost;
- discovery time;
- information per comparison item;
- reveal rate;
- ranking stability;
- token/latency cost once an LLM agent is used.

Do not choose K from intuition; optimize it.

## E3 — slate composition

Compare:

- top-K organic;
- top-K + random challenger;
- top-K + highest uncertainty;
- contextual IDS;
- D-efficiency proxy;
- diversity-aware cascade objective;
- learned combination.

## E4 — conservative regret budget

Sweep `{0, .02, .05, .10, .20}`.

A good mechanism should discover useful challengers without noticeably reducing buyer utility. Inspect p95/p99 regret, not only mean.

## E5 — funding curve

New provider funds `{0,1,5,10,25,50,100,1000}` simulated dollars.

Measure:

- experimental appearances purchased;
- cost per useful observation;
- time until sequential elimination or organic graduation;
- whether large budgets can dominate exposure despite poor evidence;
- diminishing-return behavior.

Hard gate: funding may never alter organic score.

## E6 — evidence-market price curve

Vary:

- coverage mass;
- future task demand;
- provider uncertainty;
- evidence age;
- evidence grade;
- duplicate rate.

The price should approach zero under saturation and rise for high-value gaps.

## E7 — feedback mechanism

Compare:

- favorite only;
- best + worst;
- full ranking;
- 5→2→1 consequential tournament;
- two-stage blind quality then post-price purchase.

Simulate honest, noisy, token-minimizing and adversarial agents.

Primary metric: predictive value of the feedback for future actual purchases per token/reward dollar.

## E8 — anti-cheat

Attacks:

- transaction replay;
- repeated request/response farming;
- provider self-dealing;
- provider↔buyer repeated pair;
- random Scout ranking;
- colluding Scouts;
- old provider version masquerading as new.

Controls:

- nonce-bound commissioned tasks;
- hidden deterministic comparisons;
- duplicated items under shuffled labels;
- eventual downstream-outcome calibration;
- wallet-graph risk score;
- lower evidence weights for sponsored/self-reported data.

## E9 — drift

Introduce:

- provider outage;
- price cut;
- model upgrade;
- quiet quality degradation;
- new version.

Compare fixed history, windows, exponential decay, change-point reset and discounted contextual Thompson sampling.

## E10 — 402Pilot frozen replay

Use 402Pilot's 20,575 frozen provider responses to compare routing algorithms without live spend. Preserve its task/provider/version structure and respect its research/educational license.

## E11 — Base Sepolia witness

Run three wallets:

- provider;
- buyer/worker;
- Arena operator.

Verify:

1. x402 402→pay→200 on `eip155:84532`;
2. signed x402 receipt verifies;
3. provider-signed request/response commitment verifies;
4. campaign funds escrow in test USDC;
5. exact bounty cannot be paid twice;
6. evidence hash in payout matches stored evidence envelope;
7. batch root can be independently recomputed.

## E12 — shadow mainnet

Before Arena spends anything:

- ingest live x402 discovery metadata;
- produce recommendations without auto-paying;
- log eligible pools and propensities;
- compare recommendations to actual externally observed choices where available.

Only proceed to capped live tests after shadow calibration is acceptable.
