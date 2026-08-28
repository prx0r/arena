# 402Arena Canonical Reference Guide

**Purpose:** single source of truth for *what* we hypothesize, *how* we validate, *what* logs show, *why* it matters. Updated from live logs.

## 1. What is actually going on?

402Arena is an **empirical routing evidence graph** for machine-payable services (`arena402/mechanism.py:13`). It does not rank providers by payment. It runs two separate policies:

- **RECOMMEND** (exploit): `buyer utility` only (`organic_score` `MECHANISM_SPEC.md:10` `0.62/0.23/0.10/0.05` evolvable, sponsor absent) — helps agent choose.
- **ARENA RESEARCH** (explore): `information_value = uncertainty×demand×novelty×transferability/√cost` (`MECHANISM_SPEC.md:20`) + capped `log sponsor` — decides which blind experiment to fund.

Buyer default is **5→2→1 blind tournament** (`README.md:34`): 5 blind outputs, keep 2, reveal first, buy or reveal second → partial order `E>B>{A,C,D}` (`store.py:191` `record_tournament`). Provider lifecycle `UNSEEN→SEEDED→CHALLENGER→ORGANIC/ELIMINATED` (`mechanism.py:13`). Hermés workers **are** agents with queries (`HERMES_AGENT_SPEC.md:7`) `claim→search→BEST/WORST→PURCHASE→receipt→Hydra`.

## 2. Hypotheses + Validation + Findings (from logs)

| # | Hypothesis | Validation method | What drives it | Log evidence (current) | Interpretation | Status |
|---|---|---|---|---|---|---|
| H1 | **Sponsor/organic separation works** — sponsor never improves organic rank, only exposure in eligible experimental slot | Negative control `paid_rank_bad` baseline vs `separated_ids` + `test_sponsor_money_does_not_change_organic_score` `tests/test_mechanism.py:69` | `evidence_market.py` `GRADE A-D` `mechanism.py:28` + `retrieval.py:25` eligibility gate | `mechanism_sweep.json:4` `separated_ids` `net_utility 0.832` beats `paid_rank_bad`; `23 passed` | Separation holds; paid rank would corrupt | **CONFIRMED** |
| H2 | **Scarce 2-reveals creates truthful price/quality split** — `BEST quality ≠ PURCHASE` after price reveals willingness-to-pay | Synthetic 5 archetypes ×50 scarce vs full `rank_sim_{scarce,full}.jsonl:250` + `scarce best==purchase` rate | `store.record_best_worst:215` BWS + `arena40254:60` `2 reveals $0.0001` | `scarce 79.6%` vs `full 100%` `logs:250` `greedy 74%→100% +26pp` `cautious 84%→100% +16pp` `analysis 29.1s` | 20.4% switch proves scarcity enforces `quality` vs `economic` labels (`402arena:299`) | **CONFIRMED** |
| H3 | **Adaptive K matters** — fixed `k=5` not optimal, `K* = argmax E[utility]+λI - cost` | Sweep `k∈{3,4,5,6,8}` `experiments:run_k_sweep` `MECHANISM_SPEC.md:33` `bandits.py:27` `DiscountedBeta` | `adaptive_k` `exploration.py:97` + `slate.py` D-optimal | `k=4 0.833 > k=3 0.828 > k=5 0.829 > k=6 0.816` `mechanism_sweep.json:4` but `live: k=5` fixed `30` receipts | `K=4` optimal in synthetic hidden-winner market; live not yet evolved | **PROVISIONAL** |
| H4 | **BWS scarce disincentivizes cheap talk** — paying for `say B is good` gets garbage, paying for `best/worst` with reveals costs | Cheat incentive `anticheat_tests.jsonl:2` `full 0.001 vs BWS -0.0007 delta 0.0017` `anticheat.py:38` | `402molt:863` never pay for opinion | `bws delta 0.0017` `hermes_z_batch:3` `mimo fallback` | Random ranking loses `$0.0007` reveal value under BWS — anti-cheat by design | **CONFIRMED** |
| H5 | **Wash/self-dealing detectable** — `wallet correlation + duplicates + timing + clusters` flags farming | `wash_score 6 checks` `anticheat.py:10` + `test_sponsor_money...` `ledger.py` | `retro` `self-deal 0.4` `duplicate 0.3` `burst 0.2` | `live_z wash 0.00` clean `43` vs `self-deal wash 1.0` `is_wash true` `anticheat_tests:2` | Clean live vs 1.0 self-deal validates threshold `0.5` | **CONFIRMED** |
| H6 | **Provider lifecycle funds test, not ranking** — `$5` buys `2 incumbents+1 pareto+1 challenger+1 diversity+1 experimental` trials, cost rises as `log1p(bid)` + `loss>0.7→0.5 subsidy` | `sponsor.py` diminishing `Trial $0.005→$0.50 paused` (`arena40254:514`) `exploration.py:73` | `GRADE_WEIGHT` `ORIGIN_WEIGHT` `mechanism.py:28` | `evolve_proposals 5` `k 3-4 wash 0.4-0.6` from `live 9`; `live_z` still `wash 0.0` no elimination yet | Lifecycle implemented, not yet stressed with losing provider | **PROVISIONAL** |
| H7 | **Hermes = real agent evidence** — each `kanban claim→hermes -z ox-alpha→mimo→deterministic` choice is genuine revealed preference, not synthetic | `hermes kanban stats ready 0 running 0 done 20` `continuous_hermes_daemon.py:3075613` `PPID 1` `daemon.log:24` `hermes_z_batch:3` `ox-alpha 2 mimo 1` `29s` | `HERMES_AGENT_SPEC.md:7` + `scripts/hermes_live_loop.py:29` fallback chain | `live_hermes_z 43` `models deterministic 32 / ox-alpha 3 / mimo 2` `live_arena 30` `k=5` `Hydra ready True` `base-sepolia 0x2bc8242` | Hermes is being called (35s timeout → mimo) but often falls back to deterministic `max sim` — proves plumbing, not yet LLM preference quality | **PARTIAL** |
| H8 | **Evidence market saturates** — bid `futureDemand×uncertainty×regret×freshness` falls to `$0` when `n>80` | `test_evidence_market_saturates` `experiments/evidence_market.py` | `DataValue` `402molt:460` | `23 passed` market saturates | Saturation works | **CONFIRMED** |

## 3. What is driving all this?

- **Evidence graph is moat:** `REL_RAN_ON` `Hydra` (`docs/HYDRA.md:44`) hard `gates` (`AGENTS.md:3` quality never traded for cost), Wilson CI + `Q-archive` `SPEC.md:80`.
- **Logs are canonical:** `logs/*.jsonl` `591` total (`rank_sim 500 + live 43+30 + anticheat 2 + evolve 5 + batch 3`) canonical, `Hydra` + `git` derived (`HYDRA.md:69` rebuild).
- **Evolution loop:** `logs → Hydra batch (≤64 write-behind SPEC.md:47) → propose_children (elitist_mutation etc) → next K/thr/VoI` `cogym_kernel/evo` (now `571` preserved to `experiments/results`).

## 4. Current live truth (2026-08-24 15:29 UTC)

- **Tests:** `402arena 23 passed` `cogymkernel 32 passed` `k=4 beats 5`
- **Hermes:** `daemon 3075613` `nohup run_daemon_nohup.sh 3079385` `ready 0` workers consumed queue, but `hermes -z` flaky → mostly deterministic fallback → next: fix prompt + use `hermes -z --json` or direct API.
- **Chain:** `base-sepolia 84532 0x036CbD` `alch_GX8 0x2bc7a51` `0 tx` — `chain-ts seller/buyer` dry-run only, `ResearchEscrow.sol` not yet deployed.
- **Gaps:** `adaptive K` not live, `22-row dashboard` `6→22`, `hidden controls` `10%` not yet injected, `D-optimal` opponents diversity-only, `402Pilot 10k` not fetched (needs `MCCodeAI/402Pilot` external).

## 5. Next to prove

1. **402Pilot 10k replay** `scripts/fetch_402pilot.py` → `discovery time` for hidden cheap winner must beat `organic_only` under bounded budget.
2. **Hidden controls inject 10%** → `scout_reliability 0.5→>0.7` with `control` provider.
3. **Hermes LLM preference quality** → switch from deterministic `max sim` to `ox-alpha` JSON `reason_codes` and measure `best==purchase` vs `human` calibration.

*This file is the canonical reference — update after each `mechanism_sweep` or `live_*` batch.*

## 6. Major Findings Update (2026-08-24 15:45 UTC) — Hermes Live + Reports

**Hermes still running:** `daemon 3079388` `nohup` `PPID 1` `15s` `ready 0 running 1 done 20` `live_hermes_z 71` (up from 9) `total 611` receipts canonical; `hermes -z ox-alpha 25s` → `mimo 35s` fallback deterministic `32/43` proves plumbing but LLM JSON flaky — next prompt fix.

**Reports written `experiments/reports/*.md` 5 files `COMBINED_REPORT.md:87`:**
- **Scarce 20% switch** `79.6% vs 100%` `greedy +26pp` validates `402arena:299` two-stage; full reveal not incentive-compatible.
- **K=4 optimal** `0.833 > 0.828` synthetic but live fixed `5` — adaptive `K*` next.
- **Wash 0.0 vs 1.0** threshold `0.5` works; **BWS delta 0.0017** disincentivizes random.

**Next level per user:** replicate `x402` actual schemas (`resource, 402 Payment Required, facilitator, signed offer/receipt, USDC 84532`), use `Hermes as customer agents (Buyer: scarce reveals) and worker agents (Bounty: run provider, Scout: rank)`, set up exemplar provider paying `$5` research budget, data back via `22-row dashboard` + niche map + `request cluster/ opponents/ propensity` (`arena40254:1001`), whole algorithm `eligibility → organic/research → tournament → reveals → purchase → outcome → Hydra → Cogym evolve` integrated into `simulation.py` (12-provider hidden winner) + `chain-ts` witness.



## 7. Integrated Simulation Run 2026-08-24
Exemplar newsearch $5 → slate 3 → BEST cheap → evidence 87a362fb → balance 5.0 → 5→2→1 partial order [['YHxiAoQJ'], ['G4m1tjB_'], ['Z-x7oemv']]

## 8. New Findings Update (2026-08-24 19:55 UTC) — Gap Analysis + Fixes

**25 gaps identified from verbatim analysis** (`HANDOVER.md`). 6 fixed today:

1. **D-optimal opponents** implemented in `retrieval.py:31` — `1 incumbent+1 closest+1 price+1 uncertain+NewSearch` with dedup. Previously was per-provider greedy MMR only.
2. **Dashboard 22 rows** expanded `provider_report.py:58` — added `price_rejections`, `price_rejection_rate`, `inclusion_propensity`, `organic_lift`, `confidence.ci_width`, `niche_map`, `cost_per_finding`. Now 19+ fields.
3. **Provenance tags** — `store.record_choice:191` now accepts `provenance` parameter (`ORGANIC/ARENA_COMMISSIONED/PROVIDER_SPONSORED/SELF_REPORTED`).
4. **ArenaEvidenceV1 end-to-end** — 3 tests pass (`test_evidence_v1.py`): create, verify hashes, GRADE weights.
5. **Evidence market quote** — 2 tests pass (`test_evidence_market_v2.py`): saturated bid near 0, sparse bid higher. `quote_organic` returns `EvidenceQuote` with `bid_usd` and `reasons`.
6. **Daemon k-sweep fixed** — killed stale process, restarted, confirmed `k=3,4,5,6` cycling in `live_hermes_z.jsonl:189`.

**Total tests: 28/28 pass** (was 23).

**Remaining 19 gaps:** tournament in daemon, reveal limits, sell_evidence live, bounty x402, GRADE in ranking, hidden controls, 402Pilot replay, WorkReceipt adapter, adaptive_k from beliefs, escrow deploy.

*This file is the canonical reference — update after each batch.*
