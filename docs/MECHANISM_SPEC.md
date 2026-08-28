# 402Arena mechanism specification v0.4

## Thesis: non-fungible machine outputs

Arena is valuable when: different providers produce materially different outputs + quality is hard to pre-judge + output costs enough that choosing well matters.

| Category | Fungible? | Arena fit | Priority |
|----------|-----------|-----------|----------|
| Images | massively different | excellent | **#1** |
| Deep research reports | yes | excellent | **#2** |
| Video | yes | excellent (expensive) | later |
| Specialized analysis | yes | excellent | #3 |
| Code | varies | medium | #4 |
| Web search | mostly fungible | weak | routing only |
| RPC / price feeds | commodity | none | — |
| Creative writing | commodity | none | — |

## Capability lineage

Arena tracks upstream engines, not just URLs. Three Tavily wrappers are the same capability; a custom crawler + Claude is different.

```text
Provider
 └── Endpoint
      ├── capability_family: research.web, research.finance, image.gen
      ├── upstream_family: tavily, exa, custom
      ├── pipeline_fingerprint: hash(model + sources + steps)
      ├── model_family
      ├── data_sources
      └── version
```

Evidence transfers across same-family providers. The `capability_family` field determines substitutability for blind tournament selection.

## Objective

For every machine request `q`, estimate which payable service will maximize buyer utility **and** decide whether spending research budget on an uncertain provider would improve future routing enough to justify the cost.

These are separate objectives and separate policies.

## A. Eligibility

A provider cannot buy its way around eligibility. It must satisfy:

```text
healthy
AND claimed/observed task compatibility
AND schema compatibility
AND current price <= buyer budget
AND relevance >= threshold
```

The production implementation should replace task-tag similarity with a request/evidence embedding and capability/schema classifier, while retaining these as hard gates.

## B. Organic score

`organic_score` contains only buyer-relevant evidence:

```text
0.62 predicted_utility
+0.23 request/provider similarity
+0.10 predicted success
+0.05 price efficiency
```

The constants are **initial candidates, not truths**. Cogym must evolve them. Sponsor balance is deliberately absent.

## C. Research score

For eligible providers:

```text
information_value =
  uncertainty
× demand
× transferability
× novelty
÷ sqrt(call_cost)
```

The current implementation combines this with uncertainty, relevance, a capped logarithmic sponsor component, and exposure fairness. Funding therefore increases the chance that an already-qualified uncertain provider is used for an experiment, with diminishing returns.

## D. Conservative exploration

Start with the best organic slate. An experimental provider may displace at most `experimental_slots_max` items and must satisfy a predicted-utility floor relative to the organic baseline.

Cogym experiment: regret budgets `{0, 0.02, 0.05, 0.10, 0.20}`.

Primary metrics:

- buyer utility;
- discovery time for a hidden niche winner;
- research dollars per useful discovery;
- downstream success;
- worst-tail buyer regret.

## E. Adaptive K

K is chosen from uncertainty, information value, utility spread, and explicit comparison cost:

```text
K* = argmax_K [
    expected buyer utility
  + λ * information gain
  - comparison/token/latency cost
]
```

The dependency-free MVP uses a monotone heuristic. Cogym must compare fixed K `{3,4,5,6,8}` and learned K.

## F. Consequential feedback

Ordinary buyers are not paid to fill out a survey.

Default mechanic:

1. show K blind evidence cards;
2. buyer keeps up to two finalists;
3. reveal provider + current price for the first finalist;
4. buyer can purchase or use its second reveal;
5. record purchase and downstream outcome.

This creates a partial order. A 5→2→1 interaction can establish:

```text
first > second > eliminated-set
```

but not an ordering inside the eliminated set.

## G. Provider campaign lifecycle

```text
UNSEEN → SEEDED → CHALLENGER → ORGANIC
                         └──→ ELIMINATED
                         └──→ PAUSED
```

- **UNSEEN**: no historical output; cannot enter blind slates.
- **SEEDED**: commissioned bounties produced authenticated examples.
- **CHALLENGER**: enough examples for blind trials.
- **ORGANIC**: evidence supports useful placement without sponsor boost.
- **ELIMINATED**: sequential confidence says more subsidized exposure has low information value.
- **PAUSED**: campaign budget exhausted or provider stopped it.

The current code uses Wilson intervals as a simple sequential gate. Production should test confidence sequences / Bayesian stopping rules.

## H. Trial pricing

Provider research spend should have diminishing returns:

```text
trial_price = base_price × marginal_trial_multiplier
```

where the multiplier grows with trial count and rises faster when evidence strongly rejects the provider. A new version can reopen uncertainty, but version identity must change.

## I. Evidence market

Two channels:

### Organic evidence

Agent was already going to buy a service. Arena quotes a small price for the trace. This should be cheap because Arena does not reimburse the original call.

### Commissioned bounty

Arena or a provider campaign selects a specific request/provider experiment. Reward covers:

```text
provider call reimbursement + research reward
```

The task is issued before the purchase and carries a nonce/deadline/commitment so a worker cannot submit an unrelated preexisting transaction.

## J. Evidence grades

- **A_PROVIDER_BOUND** — provider signature binds request and response hashes plus x402 evidence;
- **B_ARENA_OBSERVED** — Arena proxy observed request and response plus payment evidence;
- **C_BUYER_ATTESTED** — buyer supplies payload plus valid payment evidence;
- **D_UNVERIFIED** — low-weight research-only signal.

## K. Onchain/offchain split

Do not store outputs onchain.

Onchain:

- provider research deposits;
- bounty payouts;
- optional evidence-batch Merkle roots.

Offchain:

- requests and outputs;
- embeddings;
- preference graph;
- propensities;
- statistical models;
- private/redacted examples.

## L. Provider report

Every campaign should expose:

- qualified opportunities;
- inclusion propensity and blind appearances;
- request/task cluster distribution;
- opponents and pairwise outcomes;
- finalist / first-choice / worst-choice rates;
- reveals and price rejection;
- purchases;
- downstream outcome rate;
- price/quality frontier;
- confidence intervals;
- research spend and marginal information value;
- organic traffic earned after experimentation;
- endpoint version drift.

This report is a major provider-side product: it reveals *where the service actually wins* rather than giving a meaningless global star rating.
