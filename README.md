# 402Arena — Arena for non-fungible machine outputs

**402Arena learns which machine service produces the best output for each kind of job.**

> **Don't Arena commodities. Arena outputs where taste/quality matters.**

## The thesis

Arena gets valuable when these three things are simultaneously true:

1. Different providers produce **materially different outputs**
2. Quality is **difficult to know before buying**
3. The output costs enough that **choosing well matters**

This immediately disqualifies:

| Category | Fungible? | Arena fit |
|----------|-----------|-----------|
| Web search | mostly (after LLM synthesis) | weak |
| RPC / node access | commodity | none |
| Price feeds | identical | none |
| Raw LLM access | increasingly fungible | weak |
| **Images** | **massively different** | **excellent** |
| **Deep research reports** | **yes** | **excellent** |
| **Video** | **yes** | **excellent, but expensive** |
| Specialized analysis | yes | excellent |
| Code | varies | medium |

## Why images are the cleanest first demo

```text
same request

Flux provider
Imagen provider
GPT Image provider
Seedream provider
specialized x402 design agent

        ↓

blind outputs

 A    B    C    D    E

        ↓

which would you actually buy?
```

There is almost no ambiguity about what Arena contributes. Metadata cannot tell you which image you'll prefer. **You have to see the outputs.**

## Why deep research is different from search

Search: "find sources about Nvidia's Chinese competitors"
→ Exa returns links, Tavily returns links. Pretty substitutable.

Research job: "Produce an investment memo on Nvidia's Chinese competitors: market shares, funding, products, sanctions exposure, primary-source citations, and unresolved uncertainties."
→ Provider A does 3 searches and slaps together prose. Provider B searches 40 sources, finds filings, reconciles contradictory numbers. Provider C has specialist financial datasets. **Those are different products.**

Search results converge after `search engine → 10 pages → same LLM → synthesis`. Deep research reports don't.

## Why not creative writing

An agent holding an LLM can ask it to "write this better" directly. Generic prose has no moat for a middleman. Images, video, and research reports are different because the product includes retrieval infrastructure, proprietary sources, model choice, pipeline design, and specialization.

## How it works

### 5→2→1 blind tournament

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

### Capability lineage

Arena tracks upstream engines, not just URLs. Three Flux wrappers are the same capability; a custom img2img pipeline is different.

```text
Provider
 └── Endpoint
      ├── capability_family: image.gen, research.finance, video.gen
      ├── upstream_family: flux, imagen, custom
      ├── pipeline_fingerprint
      ├── model_family
      ├── data_sources
      └── version
```

## Measurable quality dimensions

```text
OBJECTIVE                          SUBJECTIVE / CONTEXTUAL
resolution                          aesthetic quality
latency                             relevance to request
price                               depth
failed calls                        clarity
duplication                         what the buyer actually needed
citation validity (research)        which output they preferred
source quality (research)

CONSEQUENTIAL
did buyer reveal it?
did buyer purchase it?
did agent use the output?
did downstream task succeed?
```

## Reproducible simulation

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. python scripts/run_mechanism_sweep.py --rounds 1200 --seeds 12
```

## Base Sepolia witness

- Chain ID: **84532** / CAIP-2 `eip155:84532`
- RPC: `https://sepolia.base.org`
- Testnet USDC: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`

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
