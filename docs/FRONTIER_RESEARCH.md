# Frontier research mapped onto 402Arena

This is the research basis used for the v0.2 mechanism. The point is not to implement papers literally; it is to map each solved adjacent problem onto a testable Cogym candidate.

## 1. Contextual dueling bandits → blind provider comparisons

Dudík et al., **Contextual Dueling Bandits** (COLT 2015) formalizes learning a context-dependent policy from relative pairwise feedback and notes that preference feedback can be more reliable than absolute labels in search/recommendation.

Reference: https://proceedings.mlr.press/v40/Dudik15.pdf

402Arena implication:

- request/task = context;
- providers = actions;
- blind output choice = preference feedback;
- do not require a global Condorcet winner; provider quality can be cyclic/context-dependent;
- fit contextual pairwise models rather than one global provider score.

Candidate experiments: contextual Bradley–Terry, contextual Plackett–Luce, regression-oracle dueling policy, simple task-bucket Beta posteriors.

## 2. Cascading/slate bandits → adaptive candidate lists

Kveton et al., **Cascading Bandits: Learning to Rank in the Cascade Model** (ICML 2015), models ordered recommendation lists with partial feedback. Hiranandani et al. (UAI 2020) extends this direction to account for position bias and diversity.

References:
- https://proceedings.mlr.press/v37/kveton15
- https://proceedings.mlr.press/v115/hiranandani20a.html

402Arena implication:

- K is a decision variable, not a UI constant;
- slate composition should optimize utility + information + diversity − comparison cost;
- position propensities must be logged;
- blind order should be randomized where compatible with buyer utility.

## 3. Contextual Information-Directed Sampling → where research dollars go

Hao, Lattimore & Qin, **Contextual Information-Directed Sampling** (ICML 2022), emphasizes that exploration should value information useful for future unseen contexts, not only uncertainty on the current request.

Reference: https://proceedings.mlr.press/v162/hao22b.html

402Arena implication:

```text
ResearchValue(q,p) ≈
  uncertainty(q,p)
× future demand around q
× transferability to nearby requests
× freshness / novelty
÷ experiment cost
```

This is why another common OCR call can be worth ~0 while one rare legal-extraction call can have a positive evidence bid.

## 4. Conservative contextual bandits → protect buyers during exploration

Deb, Ghavamzadeh & Banerjee, **Conservative Contextual Bandits: Beyond Linear Representations** (2024/ICLR 2025) studies exploration while constraining performance relative to a baseline policy.

Reference: https://arxiv.org/abs/2412.06165

402Arena implication:

- experimental candidate must be plausible enough not to wreck buyer utility;
- enforce a configurable regret budget relative to the organic baseline;
- Cogym sweeps this budget because 0% is too conservative and unrestricted exploration is unsafe for the product.

## 5. Off-policy slate evaluation → learn before going live

Swaminathan et al., **Off-policy evaluation for slate recommendation** (2016) specifically addresses evaluating ordered lists from logged interaction data and shows that slate structure can be exploited for sample-efficiency.

Reference: https://arxiv.org/abs/1605.04812

Dudík, Langford & Li, **Doubly Robust Policy Evaluation and Learning** (2011) combines reward and propensity models to reduce the failure modes of either alone.

Reference: https://arxiv.org/abs/1103.4601

402Arena implication:

Every production slate must log:

- candidate set;
- algorithm/version;
- inclusion propensity;
- position propensity;
- reveal policy;
- sponsor/research role;
- outcome.

Then use IPS/SNIPS/DR before changing production policy.

## 6. Bayesian D-optimal discrete-choice design → which opponents to show

Bayesian optimal-design literature chooses comparison sets that maximize information about choice-model parameters. Mao, Kessels & van der Zanden (2024) explores simulated annealing for Bayesian D-optimal discrete choice designs.

Reference: https://arxiv.org/abs/2402.18533

402Arena implication:

Do not compare a challenger against four redundant endpoints. Construct slates with informative opponent geometry: category leader, nearest predicted rival, similar-price rival, uncertain rival, challenger. `arena402.slate.d_efficiency` is a dependency-free proxy to test this idea; it is not claimed to be a complete DCE optimizer.

## 7. Best–Worst / MaxDiff → richer commissioned feedback

Best–Worst Scaling asks for the most and least preferred items in a set and relates to Bradley–Terry / multinomial-logit choice models.

References:
- https://www.sciencedirect.com/science/article/pii/S1755534514000128
- https://www.sciencedirect.com/science/article/abs/pii/S1755534515300701

402Arena implication:

- organic buyers: use consequential 5→2→1 partial orders;
- paid Scouts: best+worst or fuller ranking can be worthwhile because Arena pays explicitly for extra information;
- do not treat Scout prose as ground truth; calibrate Scout reliability with hidden controls and eventual downstream outcomes.

## 8. Sponsored-search bandits → funding should buy experimentation, not conclusions

Bandit work on multi-slot sponsored search studies the joint learning/incentive problem when click probabilities are initially unknown.

Reference: https://arxiv.org/abs/1001.1414

402Arena implication:

A real auction is a later feature, not v1. Start with posted research budgets and an Arena-defined qualified experimental pool. If demand for one experimental slot becomes scarce, then test capped/diminishing-return bidding mechanisms while preserving the no-paid-organic-rank invariant.

## 9. x402 signed offers/receipts → portable proof of interaction

The x402 Signed Offers & Receipts extension provides server-signed offers on 402 responses and signed receipts on successful delivery. Receipts include resource URL, payer, network, timestamp and optionally transaction hash.

Reference: https://docs.x402.org/extensions/offer-receipt

Important limitation for Arena: the standard receipt intentionally does **not** bind the exact request body and response body. The Sepolia witness therefore pairs the official x402 receipt with a provider-signed `arena-provider-evidence-v1` containing SHA-256 request/response hashes.

## 10. Base Sepolia → safe reproducible payment witness

Official Base docs list chain ID 84532 and public Sepolia RPC `https://sepolia.base.org`.

Reference: https://docs.base.org/base-chain/quickstart/connecting-to-base

Circle lists Base Sepolia USDC as `0x036CbD53842c5426634e7929541eC2318f3dCF7e`; testnet tokens have no monetary value.

Reference: https://developers.circle.com/stablecoins/usdc-contract-addresses

x402 seller docs use CAIP-2 `eip155:84532` and the x402.org facilitator for testnet flows.

Reference: https://docs.x402.org/getting-started/quickstart-for-buyers
