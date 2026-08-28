# Next Dev Plan — 402Arena v0.2 → Live

**Why:** current live (`549` receipts, `scarce 20%` switch, `wash 0.0/1.0`, `daemon 3079388`) proves incentive works but mechanism is patched stubs; Sepolia lab (`271K`, `k=4 0.832` wins, `7 passed`, `ResearchEscrow.sol`) is the complete lab. Plan merges live evidence into lab and progresses `SIM→SEPOLIA→SHADOW→LIMITED` per `PRODUCTION_GATES.md` — no jump to mainnet.

## Phase 0: Consolidate (1 day) — WHY: single source of truth
- **Adopt sepolia as base:** `rsync /root/402arena-cogym-sepolia → /root/402arena` keep `logs/*.jsonl` (549) → `experiments/results/full_lab.json` structure; `daemon nohup` stays on new `arena402/simulation.py` (12-provider hidden winner) not synthetic 2-provider.
- **Why:** sepolia already fixes `pseudo-MMR→greedy`, `winner>all→BWS`, `GRADE A-D` `mechanism.py:28`, `DiscountedBeta` `bandits.py` — stops re-patching.

## Phase 1: Simulation harden (2 days) — WHY: trust ranking before spending
- **Hidden controls:** 10% `control` provider with known answer (`arena40254:751`), `scout_reliability (success+2)/(total+4)` already `anticheat.py:22` but needs table `HiddenControl`; **why:** without ground truth `peer-prediction` has uninformative equilibria (`arena40254:751`).
- **D-optimal opponents:** `slate.py` today diversity-only → `1 incumbent+1 closest+1 price+1 uncertain+NewSearch` (`arena40254:975`) maximizing `ResearchValue` `information_value` (`MECHANISM_SPEC.md:20`); **why:** `NewSearch vs A B C D` arbitrary wastes funded trials.
- **Privacy tiers:** `RAW` opt-in / `REDACTED` / `DERIVED embedding` (`arena40254:369`) into `ledger.py`; **why:** raw request onchain leaks, derived still gives provider `request cluster`.
- **Adaptive K evolve:** `k∈{3,4,5,6,8}` sweep already `mechanism_sweep.json:4` shows `4>5>6` (0.832>0.829>0.816) but live still `k=5` fixed; wire `adaptive_k(uncertainty)` `exploration.py:97` to Hydra `REL_RAN_ON`; **why:** fixed K is suboptimal (`402arena:344`).
- **Gate:** `PYTHONPATH=. pytest -q` `7 passed` + `mechanism_sweep --rounds 1200` `separated_ids` must beat `organic_only`/`paid_rank_bad` on `net_utility/discovery_round`.

## Phase 2: Frozen replay (2 days) — WHY: real data before chain
- **402Pilot 823×5×5=20575** `scripts/fetch_402pilot.py` + `run_402pilot_experiments.py --rounds 10000` (`README.md:103`); cold-start `new Provider = clone quality + cheaper price` (`test_frontier.py`) already in sepolia; **why:** synthetic market may not transfer, 402Pilot has price drift + failures.
- **Metrics:** `mean_buyer_utility / discovery time / research $ per discovery / worst-tail regret` (`MECHANISM_SPEC.md:20`).

## Phase 3: Base Sepolia witness (3 days) — WHY: prove x402 binding with minimal gas
- **Check RPC** `scripts/check_base_sepolia.py` `84532 sepolia.base.org` `USDC 0x036CbD` already `alch_GX8 0x2bc7a51` `base-sepolia` `1 use`; **why:** Sepolia USDC has no value (`README.md:133`).
- **Signed witness** `chain-ts` `npm run seller/buyer` → `arena-evidence.json` `arena-provider-evidence-v1` `requestHash/responseHash` (`README.md:143`) because standard x402 receipt doesn't bind body; **why:** `GRADE A` needs provider-signed hashes (`mechanism.py:28`).
- **Escrow** `contracts/ResearchEscrow.sol` USDC budgets + replay-protected bounties (`README.md:160`) `forge test` + `Deploy.s.sol` on `base_sepolia`; fund `$5` test budget, issue `bounty.py:13` `arena_task_id` challenges, verify `wallet separation` (buyer ≠ provider owner) via `ledger.py`.

## Phase 4: Shadow mainnet (1 week) — WHY: conservative exploration
- **Recommend but never auto-pay** (`README.md:178`); log `slate_provenance p_include/p_position` `store.py:49` for IPS; `regret budget {0,0.02,0.05,0.10,0.20}` (`MECHANISM_SPEC.md:20`) must keep `≥0.95 organic` (`exploration.py:108`); **why:** prevents `paid_rank_bad` corruption live.

## Phase 5: Limited live (capped) — WHY: provider proposition
- Tiny `research budget $1` + opt-in campaigns `UNSEEN→SEEDED→CHALLENGER→ORGANIC` (`mechanism.py:13`) diminishing `log1p(balance)` (`arena40254:466`); `provider_report 22 rows` `provider_report.py` + niche map; batch `Merkle` `merkle.py` anchoring to `EvidenceRootRegistry.sol` (`README.md:160`).

**Logging throughout:** every `hermes -z ox-alpha→mimo` choice → `logs/live_hermes_z.jsonl` (now `9`) → `Hydra REL_RAN_ON` → `cogym evolve` `k/thr/VoI`; daemon `nohup run_daemon_nohup.sh` `3079388` continues.

**Next commit:** Phase 0 rsync + `pytest` green, then Phase 1 hidden controls PR.
