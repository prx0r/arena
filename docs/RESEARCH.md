# 402Arena research basis

## Closest live systems

- **402Pilot** — learns provider quality/cost using payment-aware discounted contextual Thompson sampling. Its frozen replay contains 823 tasks × 5 providers × 5 response variants = 20,575 scored responses. This validates the central premise that paid outputs can be generated once and reused to compare routing policies cheaply.
  - https://github.com/MCCodeAI/402Pilot
- **Agent402 Smart Order Router** — live x402 discovery + proxy execution; external selection uses proven settlement history, live health checks and price. 402Arena deliberately targets the layer above this: task-conditioned empirical outcome evidence.
  - https://agent402.tools/guides/smart-order-router
- **RouteLLM** — preference-trained model routing; weighted Elo conditioned on prompt similarity is particularly relevant to our blind example selection.
  - https://github.com/lm-sys/RouteLLM
- **WS-DREAM** — real QoS matrices for 339 users × 5,825 services, plus a time-aware 142 × 4,500 × 64 dataset. Useful for stress-testing sparse service recommendation and drift without paying APIs.
  - https://github.com/hariingit/wsdream-dataset

## Frontier mechanisms to test

1. **Discounted Thompson Sampling** for non-stationary providers. Evidence must decay because service/model/price changes make old data stale.
   - Qi, Wang, Zhu, 2023: https://arxiv.org/abs/2305.10718
2. **Change-detection + Thompson Sampling** to reset beliefs when provider behavior jumps.
   - Ghatak, 2020: https://arxiv.org/abs/2009.02791
3. **Contextual Information-Directed Sampling (IDS)** for subsidy allocation. Important insight: exploration should value information useful for *future unseen contexts*, not merely uncertainty on the current query.
   - Hao, Lattimore, Qin, 2022: https://arxiv.org/abs/2205.10895
4. **Contextual dueling / pairwise preference learning** for blind A/B choices.
   - Dudík et al.: https://arxiv.org/abs/1502.06362
5. **Off-policy evaluation** so we can estimate a new routing policy from logged traffic before deploying it. Implement IPS/SNIPS/DR first; later add SWITCH/shrinkage estimators.
   - Wang, Agarwal, Dudík: https://arxiv.org/abs/1612.01205
   - Su et al.: https://arxiv.org/abs/1907.09623
6. **Prompt-conditioned preference routing / weighted Elo** from RouteLLM. Similar historical requests should weight pairwise preference evidence more strongly.
   - https://arxiv.org/abs/2406.18665
7. **QoS collaborative filtering / graph recommendation** for sparse provider histories and cold start. WS-DREAM is the canonical offline testbed.

## Experiments Cogym should run

### E1 — Does empirical routing beat metadata routing?
Baseline: task-description similarity + health + price. Candidate: nearest historical outcomes + learned preference prior.

### E2 — How much should 402Arena subsidize?
Sweep research pool = $0, $1, $5, $10, $50 per 10k simulated calls. Plot future held-out utility improvement per subsidy dollar.

### E3 — Which observation is worth buying?
Compare random exploration, epsilon-greedy, uncertainty sampling, Thompson, VOI heuristic, contextual IDS proxy.

### E4 — Cold-start provider
Insert a high-quality cheap provider with zero history at round 2,000. Measure time/cost until the router discovers its winning prompt clusters.

### E5 — Provider drift
At round 5,000, degrade incumbent quality or change price. Compare static history, exponential decay, Page-Hinkley/CUSUM reset, discounted TS.

### E6 — Blind preference value
Compare routers trained on deterministic quality only vs pairwise blind choices vs downstream success labels.

### E7 — Sponsor gaming
Give one mediocre provider a large exploration fund. Hard invariant: funding may increase *measurement count* but must not directly increase ranking score.

### E8 — Historical-example UX
Compare top-5 nearest examples, top-5 provider-diverse examples, and predicted-utility list. Record selection entropy and downstream success.

### E9 — Off-policy safety
Use logged propensities and IPS/SNIPS/DR to reject a candidate router if offline evidence is too uncertain; only then A/B test live.

### E10 — Graph value
Compare flat task-type bandit vs nearest-neighbor vs request-provider-outcome graph features. Cogym evolves the feature/policy combination under chronological secret holdout.
