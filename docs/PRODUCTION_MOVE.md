# Production Move — Base / ETH Real Schemas

**Zoom out:** `643` receipts, `H1-H8` `CONFIRMED` (`scarce 20%` `k=4>5` `wash 0.0/1.0`), `23+32` tests pass, `sepolia v0.2` is complete lab. Now move from `synthetic 12-provider` to `real contracts + real schemas` with production constraints.

## 1. Stacks Review (what we have)

- **cogymkernel** `32` determinism + Hydra `ready True` — evolves `K/VoI` `10 recipes`
- **402arena-cg** `4` tests — patched `retrieval gate` + `BWS`
- **sepolia v0.2** `23` tests — `mechanism.py` `GRADE A-D` + `bandits` `simulation.py` hidden winner `k=4 0.833` + `chain-ts` `x402 v2`
- **hermes live** `101` `live_hermes_z` `daemon 3079388` `ox→spark→mimo` `15s` `kanban done 20`
- **Reports** `5` + `COMBINED 87` + `CANONICAL H1-H8` `PROVISIONAL→CONFIRMED`

## 2. Production Constraints (why we start Sepolia)

| Network | Chain ID | USDC | Gas $ | Use |
|---|---|---|---|---|
| Base Sepolia | 84532 `eip155:84532` | 0x036CbD (test) | $0.001 | Witness, escrow, EAS batch ≤64, facilitator `x402.org` |
| Base Mainnet | 8453 | 0x833589... | $0.01-0.05 | Shadow → limited live |
| ETH Mainnet | 1 | 0xA0b8... | $1-5 | Only if L1 attestations needed, bridge from Base |

**Why Sepolia first:** test USDC has no value (`README.md:133`), `alch_GX8` already `0x2bc7a51` verified, `Production Gates` `SIM→SEPOLIA→SHADOW→LIMITED→OPEN` mandatory.

## 3. Actual Schemas (not synthetic)

**x402 v2 (real):**
- `402 Payment Required` → `{resource:"https://p.invalid/search", accepts:[{scheme:"exact", network:"eip155:84532", maxAmountRequired:"3000", payTo:"0xSeller", asset:"0x036CbD"}]}` (3000 = $0.003 6 decimals)
- `facilitator` `https://x402.org/facilitator` → `X-PAYMENT` + `receipt {resource,payer,payTo,amount,txHash,facilitator}`
- `Signed Offers` provider signs `offer` pre-pay, receipt pre-prove delivery but not body (`402molt:340`)

**Arena Evidence v1 (we added `arena402/x402.py:28`):**
- `requestHash=sha256(request_body)` `responseHash=sha256(response)` `providerSignature=sign(resource+hashes)` → `GRADE A 1.00` (provider-bound) vs `B 0.90` `C 0.55` `D 0.15` (`mechanism.py:28`)

**On-chain:**
- `ResearchEscrow.sol` `createCampaign(provider,$5) → fund → createBounty(arena_task_id, $0.003) → payout with replay protection`
- `EvidenceRootRegistry.sol` `anchorRoot(merkleRoot, batchSize)` — raw `request` never onchain, only `root` (`x402.py` `ArenaEvidenceV1` batch)

## 4. Production Move Steps (actual)

**Step 1: Verify Sepolia (0 gas)**
- `python scripts/check_base_sepolia.py` → `84532` `sepolia.base.org` `already 0x2bc8242`
- `forge build` in `contracts/` (Foundry) → `ResearchEscrow` `EvidenceRootRegistry` compile

**Step 2: Deploy escrow $5 (minimal)**
- `export BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/alch_GX8...`, `PRIVATE_KEY` burner, `forge script script/Deploy.s.sol:Deploy --rpc-url base_sepolia --broadcast` → escrow address, fund `5 USDC` (test) → `provider NewSearch` `campaign UNSEEN→SEEDED`.

**Step 3: Run x402 witness (real pay)**
- `chain-ts` `npm install` `cp .env.example .env` `SELLER_SIGNING_PRIVATE_KEY` distinct from `payTo` (`SEPOLIA_RUNBOOK.md` roles) → `npm run seller` + `npm run buyer` → `arena-evidence.json` with `requestHash/responseHash + providerSignature + txHash`.

**Step 4: Shadow mainnet (no auto-pay)**
- `PRODUCTION_GATES.md` `SHADOW`: recommend via `RECOMMEND` policy, log `p_include/p_position` `store.py:49` IPS, regret budget `0.02-0.20` `≥0.95 organic` (`exploration.py:108`), `Merkle` batch `merkle.py` every 100 receipts.

**Step 5: Limited live $1**
- Cap `K=3,4,5,6` cycle already in `continuous_hermes_daemon.py:36`, `wash_thr 0.5` `heavy 10`, `Hermes Customer (scarce) + Worker (bounty)` as `SIMULATION_DESIGN.md` — all with `Base` USDC `0x833...` when ready.

## 5. What logs will prove in prod

- `discovery time` for hidden winner faster than `organic_only` under `$5` budget (from `mechanism_sweep` synthetic → real 402Pilot `20,575` after `fetch_402pilot --out`)
- `wash 1.0` flagged vs `0.0` clean, `scarce 20%` switch persists with real `muse-spark` choices (not deterministic)
- `Merkle root` on `EvidenceRootRegistry` matches `logs/integrated_sim.jsonl` batch `87a362fb`

All with `ox-alpha→muse-spark→mimo` chain (`AGENTS.md` fallback) and `daemon 3079388` continuing.

