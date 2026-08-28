# 402Arena v0.2 — Cogym + Base Sepolia mechanism lab

**402Arena is an empirical recommendation layer and market for machine-service evidence.**

> **⚠️ READ FIRST: [`HANDOVER.md`](HANDOVER.md) — timestamped status, queue, 25 missing mechanics, all docs.** Start here.

The core rule is deliberately strict:

> **Money buys experiments. Evidence buys organic ranking.**

A provider can fund controlled blind trials or bounties that generate missing evidence. Funding cannot directly increase the buyer-facing organic score. Buyers get useful recommendations from prior real calls; their consequential reveal/purchase behavior creates preference data; agents can sell verified x402 traces when Arena currently values that evidence.

This repository is designed to progress in four reproducible stages:

1. **Pure deterministic simulation** — no chain, no API keys, no money.
2. **Frozen-data replay** — 402Pilot and other datasets; off-policy and cold-start experiments.
3. **Base Sepolia witness** — testnet USDC, x402 v2, signed offer/receipt evidence, research escrow.
4. **Mainnet production only after gates pass** — bounded budgets, shadow routing, batch Merkle anchoring, then limited real traffic.

## Why the split matters

402Arena runs two separate policies:

```text
RECOMMEND POLICY                  ARENA RESEARCH POLICY
buyer utility first               information gain first
no sponsor term                   sponsor budget may fund exposure
historical outcomes               uncertainty / novelty / drift
price / latency / reliability     conservative buyer-regret constraint
          |                                |
          +---------- evidence ------------+
```

A sponsored provider may occupy a qualified **experimental slot** because it funded the experiment. Its sponsor balance is never read by the organic scorer.

## Buyer mechanism: consequential partial ranking

The default interaction is a **5 → 2 → 1 blind tournament** (K is actually adaptive and should be learned):

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

This yields defensible partial-order evidence without pretending a single click means “winner beats every unseen item.” For example:

```text
E > B > {A,C,D}
```

but Arena records no ordering among A/C/D.

## Provider mechanism

A new x402 provider has no historical output, so it enters through a funded research campaign:

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

Additional subsidized trials become more expensive as evidence becomes decisive. Large funding therefore buys more opportunities to test the hypothesis “you are better than our current belief,” but not unlimited exposure.

## Agent evidence market

An agent that independently made an x402 call can ask Arena for a bid:

```text
POST /evidence/quote
```

The bid falls toward zero when the provider/task region is saturated and rises for uncertainty, high future demand, stale evidence, or a new provider. Commissioned bounties reimburse the provider call and add a research reward.

## Reproducible simulation

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. python scripts/run_mechanism_sweep.py --rounds 1200 --seeds 12
```

The current deterministic synthetic market has 12 providers, including a hidden cheap niche winner. It compares:

- `organic_only` — incumbency / no exploration baseline;
- `random_explore` — one random challenger;
- `paid_rank_bad` — deliberately corrupt baseline where sponsor money enters rank;
- `separated_ids` — organic/research separation + contextual information value + conservative exploration.

`experiments/results/mechanism_sweep.json` contains the generated run snapshot.

## 402Pilot replay

402Pilot commits 823 tasks × 5 providers × 5 response variants = 20,575 frozen responses. Its repository permits research/educational use and asks commercial users to contact the author, so this package does **not** redistribute the dataset.

```bash
python scripts/fetch_402pilot.py /path/to/402Pilot
PYTHONPATH=. python scripts/run_402pilot_experiments.py --repo /path/to/402Pilot --rounds 10000
```

The importer understands the committed `data/tasks/` and `data/pregen/` layout.

## Cogym integration

The overlay implements `arena402.mechanism_lab` against the current Cogym `WorldSpec / ActionSpec / MetricVector` interface.

```bash
./apply_to_cg.sh /path/to/prx0r/cg
cd /path/to/prx0r/cg
cg worlds
```

The world deterministically evaluates the mechanism choices under identical seeds. `arena402.cogym.deterministic_experiment_receipt()` also produces a content-addressed experiment receipt when running outside a Cogym checkout.

## Base Sepolia witness

Official current network values used by the code:

- Base Sepolia chain ID: **84532** / CAIP-2 `eip155:84532`
- Base Sepolia RPC: `https://sepolia.base.org`
- testnet USDC: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- x402 test facilitator: `https://x402.org/facilitator`

Testnet USDC has no monetary value.

### 1. Check the RPC

```bash
PYTHONPATH=. python scripts/check_base_sepolia.py
```

### 2. Run the signed x402 witness

The TypeScript witness uses x402 v2 `@x402/fetch`, `@x402/evm`, and Signed Offers & Receipts. It additionally signs an `arena-provider-evidence-v1` envelope binding the exact request and response hashes because the standard x402 receipt proves delivery but intentionally does not include those hashes.

```bash
cd chain-ts
npm install
cp .env.example .env
npm run seller
# second terminal
npm run buyer
```

The buyer writes `arena-evidence.json` containing the x402 settlement response plus provider-signed request/response commitments.

### 3. Deploy research escrow on Base Sepolia

The Solidity contracts are intentionally small:

- `ResearchEscrow.sol` — provider-funded USDC research budgets and replay-protected bounty payouts;
- `EvidenceRootRegistry.sol` — Merkle-root anchoring for evidence batches;
- `MockUSDC.sol` — local contract tests only.

With Foundry installed:

```bash
cd contracts
export BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
export USDC_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
export ARENA_OPERATOR=0x...
forge test
forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast
```

No deployment is required for the Python simulation.

## Production progression

Do not jump from simulation to unrestricted mainnet. The intended gates are:

```text
SIMULATION
  ↓ mechanism beats baselines over frozen + synthetic replay
SEPOLIA
  ↓ receipts, escrow invariants, replay protection, wallet separation verified
SHADOW MAINNET
  ↓ recommend but never auto-pay; log propensities and outcomes
LIMITED LIVE
  ↓ tiny capped research budget + opt-in provider campaigns
OPEN LIVE
```

See `docs/PRODUCTION_GATES.md` for exact gates.

## Repository map

```text
arena402/
  bandits.py          discounted contextual posterior + information value
  slate.py            adaptive K, safe experimental slot, D-optimal proxy
  choice.py           consequential partial-order tournament
  sponsor.py          campaign lifecycle + diminishing trial value
  evidence_market.py  live evidence bids + commissioned bounties
  anti_cheat.py       replay/self-dealing/duplicate + scout reliability
  simulation.py       deterministic market simulator
  experiments.py      policy/K/regret-budget sweeps
  ledger.py           deterministic escrow mirror
  merkle.py           evidence batch commitments
  sepolia.py          Base network constants + optional RPC smoke check
contracts/            Sepolia/mainnet-compatible escrow + root registry
chain-ts/             x402 v2 signed witness on Base Sepolia
integration/          Cogym world overlay
docs/                 mechanism, experiments, threat model, research, rollout
```

## Core scientific invariants

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
