# 402Arena — Empirical routing for machine-service intelligence

**402Arena learns which machine service produces the best outcome for each kind of job.**

> **Money buys experiments. Evidence buys organic ranking.**

A provider can fund controlled blind trials or bounties that generate missing evidence. Funding cannot directly increase the buyer-facing organic score. Buyers get useful recommendations from prior real calls; their consequential reveal/purchase behavior creates preference data; agents can sell verified x402 traces when Arena currently values that evidence.

## Vertical: Research Arena (first)

Research/search is the first vertical because real x402 demand exists:

| Provider | 30d calls | Unique payers | What it does |
|----------|-----------|---------------|--------------|
| Tavily search | ~60,307 | 422 | Agent web search |
| Exa search | ~11,002 | 265 | Neural search + contents |
| You.com deep research | — | — | $0.11 deep / $0.50 exhaustive |
| Agent402 reports | — | — | $0.60–$1.10 finished research |

Arena learns: **for what query does which research/search engine win?**

```text
"latest news about X"
    → Tavily may dominate

"obscure technical papers about X"
    → Exa may dominate

"finance question with synthesis"
    → You.com research

"investigate this person's public footprint"
    → specialized researcher

"research this token"
    → crypto-specific service
```

## Why research, not creative writing

An agent holding an LLM can ask it to "write this better" directly. Generic prose has no moat for a middleman.

Research is different because the product includes:
- retrieval infrastructure
- proprietary sources
- multi-step search
- citation handling
- synthesis and specialization

These are capabilities the buyer cannot trivially invoke themselves.

## Why not images first?

Images have cleaner blind comparison but lower current x402 demand (~34 calls/30 payers vs Tavily's 60K). Images are **#2** — structurally beautiful market, just less demand today.

## Rank capabilities, not URLs

The x402 ecosystem has tons of wrappers. Arena must understand capability lineage:

```text
Provider
 └── Endpoint
      ├── capability_family: research.web
      ├── upstream_family: tavily
      ├── pipeline_fingerprint
      ├── model_family
      ├── data_sources
      └── version
```

Evidence transfers across same-family providers. Three Tavily wrappers are the same capability; a custom crawler + Claude is different.

## How it works

### Buyer mechanism: 5→2→1 blind tournament

```text
5 blind historical outputs
        ↓
buyer keeps up to 2
        ↓
reveal provider + current price for first finalist
        ↓
buy, or reveal second finalist
        ↓
actual purchase + downstream outcome
```

Partial order: `E > B > {A,C,D}`. No ordering among eliminated set.

### Research routing

```text
query
  ↓
task classifier (research.web, research.finance, research.person, ...)
  ↓
find substitutable services by capability_family
  ↓
Arena posterior for this request cluster
  ↓
price / quality / latency frontier
  ↓
route
  ↓
capture outcome evidence
  ↓
update provider niches
```

### Two separate policies

```text
RECOMMEND POLICY                  ARENA RESEARCH POLICY
buyer utility first               information gain first
no sponsor term                   sponsor budget may fund exposure
historical outcomes               uncertainty / novelty / drift
price / latency / reliability     conservative buyer-regret constraint
          |                                |
          +---------- evidence ------------+
```

### Provider lifecycle

```text
UNSEEN
  ↓ commissioned real-demand bounties
SEEDED
  ↓ enough blind trials
CHALLENGER
  ├─ evidence proves niche strength → ORGANIC
  ├─ evidence strongly rejects it  → ELIMINATED
  └─ budget exhausted              → PAUSED
```

## Measurable quality dimensions

```text
OBJECTIVE                          SUBJECTIVE / CONTEXTUAL
citation validity                  usefulness
source quality                     depth
freshness                          relevance
claim support                      clarity
coverage                           what the buyer actually needed
latency                            which report they preferred
price
failed calls
duplication

CONSEQUENTIAL
did buyer reveal it?
did buyer purchase it?
did agent use the information?
did downstream task succeed?
```

## Reproducible simulation

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. python scripts/run_mechanism_sweep.py --rounds 1200 --seeds 12
```

The deterministic synthetic market has 12 providers including a hidden cheap niche winner. It compares:

- `organic_only` — incumbency / no exploration baseline
- `random_explore` — one random challenger
- `paid_rank_bad` — sponsor money corrupts rank
- `separated_ids` — organic/research separation + contextual information value

## Base Sepolia witness

- Chain ID: **84532** / CAIP-2 `eip155:84532`
- RPC: `https://sepolia.base.org`
- Testnet USDC: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- x402 test facilitator: `https://x402.org/facilitator`

```bash
cd chain-ts && npm install && cp .env.example .env && npm run seller
cd contracts && forge test
```

## Production progression

```text
SIMULATION
  ↓ mechanism beats baselines over frozen + synthetic replay
SEPOLIA
  ↓ receipts, escrow invariants, replay protection verified
SHADOW MAINNET
  ↓ recommend but never auto-pay; log propensities and outcomes
LIMITED LIVE
  ↓ tiny capped research budget + opt-in provider campaigns
OPEN LIVE
```

## Repository map

```text
arena402/
  models.py           Provider, Observation, capability lineage fields
  mechanism.py        CampaignState, EvidenceGrade, ProviderArm, RequestContext
  bandits.py          discounted contextual posterior + information value
  slate.py            adaptive K, safe experimental slot, D-optimal proxy
  choice.py           consequential partial-order tournament
  sponsor.py          campaign lifecycle + diminishing trial value
  evidence_market.py  live evidence bids + commissioned bounties
  anti_cheat.py       replay/self-dealing/duplicate + scout reliability
  retrieval.py        D-optimal opponent selection + eligibility
  provider_report.py  22-row dashboard with niche map
  simulation.py       12-provider hidden-winner market simulator
  x402.py             ArenaEvidenceV1, x402 schemas
contracts/            Sepolia escrow + root registry
chain-ts/             x402 v2 signed witness on Base Sepolia
integration/          Cogym world overlay
docs/                 mechanism, experiments, threat model, research, rollout
```

## Core invariants

1. Sponsor balance is absent from organic recommendation score.
2. Experimental exposure must pass compatibility and conservative-regret gates.
3. Every displayed item logs selection/position propensity before production learning.
4. A single favorite does not imply a full ranking.
5. Blind preference and post-price purchase preference are separate labels.
6. Evidence value decays with saturation and rises with uncertainty/freshness/demand.
7. Provider campaign reports include request cluster, opponents, propensity, blind result, reveal, purchase, outcome, and spend.
8. Raw request/output data is never put onchain; batch commitments are.
9. Testnet → shadow → capped live rollout is mandatory.

See `docs/MECHANISM_SPEC.md` for the complete mechanics.
