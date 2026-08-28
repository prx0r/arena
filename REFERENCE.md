# 402Arena — Categorised Reference (Root)

**Repo:** `/root/402arena` — 402Arena v0.2 Cogym + Base Sepolia lab  
**Live:** `daemon 3079388` `nohup` `logs 611` `Hydra ready True` `base-sepolia 84532`

## 1. Verbatim Research (immutable source)
| File | Lines | What |
|---|---|---|
| `docs/402arena-peer-review-verbatim.md` | 810 | 17-point peer review: Recommend vs Arena, 10 flaws, S*=αU+βI+γD-δC, VoI, conservative 95%, lifecycle |
| `docs/402molt-evidence-market-verbatim.md` | 930 | Evidence market: sell_evidence, bounties, receipt grades A/B/C, DataValue, microjobs, Moltbook |
| `docs/arena40254-scarcity-mechanic-verbatim.md` | 1082 | Scarcity: 2 reveals $0.0001, 5→2→1 tournament, provider dashboard 22 rows, ExposureWeight log |
| `402arena-full-verbatim.md` etc root copies | 810+930+1082 | Same verbatims at root for visibility |

## 2. Canonical Specs (evolving truth)
| File | Role |
|---|---|
| `docs/CANONICAL_REFERENCE.md` | **Single source of truth** H1-H8 hypotheses + validation + log findings (79.6% vs 100% etc) |
| `docs/HERMES_AGENT_SPEC.md` | Hermes = agent with query `claim→search→BEST/WORST→PURCHASE→receipt` + scarcity + provenance |
| `docs/MECHANISM_SPEC.md` | Mechanism v0.2: eligibility, organic 0.62/0.23, ResearchValue, adaptive K, tournament |
| `docs/NEXT_DEV_PLAN.md` | 5 phases SIM→SEPOLIA→SHADOW→LIMITED why each |
| `docs/NEXT_PHASE.md` | Hidden controls, D-optimal, privacy tiers next |
| `docs/CHAIN.md` | Base Sepolia 84532 vs ETH, alch_GX8 key, EAS dry-run |
| `docs/PRODUCTION_GATES.md` | Gates 0 deterministic → 1 Sepolia testnet |
| `README.md` | v0.2 map: 4 stages, 9 invariants, repo map |

## 3. Mechanism Code (`arena402/`)
| File | Implements |
|---|---|
| `mechanism.py` | CampaignState UNSEEN..PAUSED, GRADE A-D weights, EvidenceOrigin |
| `bandits.py` | DiscountedContextualBeta half_life 800 |
| `slate.py` | Adaptive K* + safe experimental slot + D-optimal proxy |
| `choice.py` | Consequential 5→2→1 partial-order, BWS |
| `retrieval.py` | Eligibility gate sim≥0.15 + greedy MMR + provenance |
| `store.py` | Slates/slate_provenance/choices/pairwise/outcomes, record_best_worst/tournament |
| `preferences.py` | Contextual BT skill[(task,provider)] |
| `anti_cheat.py` | Wash 6 checks + scout reliability Beta |
| `evidence_market.py` | Bids saturate, commissioned bounties |
| `sponsor.py` | Diminishing log1p(bid), Trial $0.005→$0.50 paused |
| `ledger.py` | Deterministic escrow mirror |
| `merkle.py` | Batch commitments EvidenceRootRegistry |
| `exploration.py` | VoI score, adaptive_k, conservative 95% |
| `simulation.py` | 12-provider hidden winner deterministic market |

## 4. Experiments & Results
| Path | Content |
|---|---|
| `experiments/results/mechanism_sweep.json` | k=4 0.833 > k=3 0.828, separated_ids beats paid_rank_bad |
| `experiments/results/full_lab.json 26K` | Full lab snapshot |
| `tests/` `23 passed` | Frontier, mechanism, OPE, replay |
| `cogymkernel/tests 32 passed` | Kernel determinism, Hydra |

## 5. Logs (canonical receipts, JSONL)
| File | N | Meaning |
|---|---|---|
| `logs/rank_sim_scarce.jsonl` | 250 | 5 archetypes scarce 79.6% best==purchase |
| `logs/rank_sim_full.jsonl` | 250 | Full 100% (no price split) |
| `logs/live_arena_hermes_oxalpha.jsonl` | 30 | Real Store k=5 |
| `logs/live_hermes_z.jsonl` | 71 | Daemon hermes -z ox-alpha→mimo wash 0.0 |
| `logs/hermes_z_batch.jsonl` | 3 | Explicit -z 29s avg |
| `logs/anticheat_tests.jsonl` | 2 | Wash 1.0 / BWS delta 0.0017 |
| `logs/evolve_proposals.jsonl` | 5 | K wash thr candidates |
| `logs/daemon.log` | 1.9K | nohup wrapper 3079388 |
| `logs/README.md` | — | Canonical, Hydra derived |

## 6. Chain & Cogym
| Path | Role |
|---|---|
| `chain-ts/` | x402 v2 @x402/fetch seller/buyer arena-evidence-v1 |
| `contracts/` | ResearchEscrow.sol + EvidenceRootRegistry.sol forge test |
| `worldpacks/arena402/` | Cogym world arena402.routing_replay + mechanism_lab |
| `cogymkernel/` at `/root/cogymkernel` | Kernel async, Hydra pooled batch, recipes 10, styles 33 |
| `.secrets/alchemy.key` `alch_GX8` | Base Sepolia 0x2bc7a51 eth-sepolia 0xb05ae0 0 tx |

## 7. Imported / Archive
| Path | Note |
|---|---|
| `imported/`, `402arena-cg.zip 271K`, `402arena-cogym-sepolia.zip` | Prior imports, preserved |
| `experiments/results/*.jsonl` mirror | Logs mirrored for Cogym |

**How to navigate:** start `CANONICAL_REFERENCE.md` → `MECHANISM_SPEC.md` → `arena402/mechanism.py` → `logs/README.md` → `HERMES_AGENT_SPEC.md`.


## 8. Moltbook + Moltwork + Wallet Integration
| File | What |
|---|---|
| `docs/MOLTBOOK_MOLTWORK_WALLET_SPEC.md` | **Spec** — honest Moltbook assessment, wallet creation, x402 payment flow, Moltwork grades → 402Arena GRADE mapping |
| `docs/MOLTWORK_VISION.md` | Visionary — Bounties=BatchJobs, WorkReceipts=evidence grades, rankRoutes=ResearchValue |
| `docs/ETHEREUM_STANDARDS.md` | ERC-8004 + x402 + 4337 + A2A/MCP reference |
| `imports/moltwork/` | Moltwork repo (MIT) — economics.ts, receipts, M0-M5 schemas |

## 9. Handover & Status
| File | What |
|---|---|
| `HANDOVER.md` | **READ FIRST** — timestamped 2026-08-24 16:40, status snapshot, 25 missing mechanics, queue, all docs |
| `logs/daemon.log` | daemon 3079388 k-sweep log (currently killed for fix) |
| `logs/live_hermes_z.jsonl:185` | 185 receipts, daemon iter 0-90, k stuck 4,5 (fix needed) |
