# Hermes Agent Choice Spec — 402Arena Live Runs

**Status:** SPEC before implementation · `ox-alpha-free` only · Base Sepolia minimal gas

## 1. Core idea

> Every Hermes worker IS a potential agent with a real query, choosing from our blind options.

Not a cron job. An autonomous economic actor that:
1. Has a `query` (intent) + `budget` + `context`
2. Claims one `slate` (5 blind evidence cards)
3. Spends scarce `reveals` to inspect
4. Makes `best/worst` + `purchase` choice
5. Logs a content-addressed `receipt` → Hydra → Cogym evolves the mechanism

## 2. Job model (kanban)

**Board:** `hermes kanban --board cogym-lab` (embedded SQLite WAL, `orchestration/scheduler.py`, Hermes adapter optional `docs/HERMES.md:4`)

**Enqueue:**
```json
{
  "job_id": "arena_q_<hash>",
  "query": "find obscure Python API docs",
  "budget_usd": 0.01,
  "task_type": "search",
  "k": 5,
  "mode": "arena", 
  "reveals_allowed": 2,
  "algo_version": "retrieval.v2-gate-greedyMMR",
  "created_at": 1234567890
}
```
`k` from `adaptive_k(uncertainty)` `exploration.py:97` (3-6), `mode=arena` (no quality bias) vs `recommend`.

**Claim:** `HermesBoard.claim_next()` atomic (`HERMES.md:20` race mitigated by `job_id` idempotency). Worker receives job, no other worker gets it.

## 3. Agent execution (per job)

```
query
  ↓
EvidenceRetriever.search(query, k, mode, budget_usd)  # retrieval.py:36 eligibility gate sim≥0.20 + budget/health
  ↓
slate_id + 5 blind items (provider hidden, price hidden) + provenance (p_include, p_position) → store.save_slate + save_provenance
  ↓
Hermes worker (ox-alpha-free) receives slate:
  A-E blind outputs (historical_request + output_preview + similarity)
  ↓
Step 1: choose BEST (free, reveals provider)  → why scarce? wasting reveal on garbage hurts agent
Step 2: choose WORST or 2nd-best (tiny bonus) → BWS/MaxDiff signal
Step 3: reveal price for chosen → choose ACTUAL PURCHASE (free, strongest signal)
  ↓
store.record_best_worst(slate_id, best, worst) + record_tournament() for 5→2→1
store.record_outcome(observation_id, success) if downstream available
  ↓
receipt = {run_id=blake3(slate+choices+seed), job_id, query, k, best, worst, purchase, model=ox-alpha-free, slate_provenance, ts}
append to logs/live_arena_hermes_oxalpha.jsonl (canonical) → async Hydra flush (best-effort) → REL_RAN_ON
```

**Scarcity enforces truthfulness:** `arena40254:60` 2 reveals, further reveals `$0.0001` or `research_credit` → random ranking unlocks nothing. Agent must look.

## 4. What we log (every run)

**JSONL receipt** `logs/live_arena_hermes_oxalpha.jsonl`:
```json
{"run_id":"blake3...","job_id":"arena_q_abc","query":"...","mode":"arena","k":5,"best":"b2","worst":"b0","purchase":"b2","arch":"cautious","model":"ox-alpha-free","chain":"base-sepolia-sim","slate_id":"slate_...","provenance":[{"blind_id":"b2","provider":"p1","position":0,"p_include":0.8,"p_position":0.2}],"ts":123}
```
**SQLite store** `arena402.sqlite`:
- `slates`, `slate_provenance`, `choices`, `pairwise_preferences`, `outcomes`
- Enables `provider_report:report.py:5` (exposures/wins/losses/task_clusters) + `preferences.py:contextual` ranking per `task_type`

**Hydra projection** `docs/HYDRA.md:44`:
- `REL_RAN_ON {src_key: policy, dst_key: worldfamily, quality_pass, mean_utility_bps}` + `REL_IMPROVED_ON` + `epistemic chain`
- Rebuildable `python -m cogym_kernel.experience.rebuild` `HYDRA.md:69` — deleting Hydra loses nothing

## 5. Incentive layers (already in code)

| Layer | Who pays | Code |
|---|---|---|
| BEST reveal | free (agent wants provider) | `store.record_best_worst:215` |
| WORST tiny bonus | Arena `$0.0004` | `402molt:138` table |
| PURCHASE | free (revealed pref) | strongest signal |
| Bounty `CALL+COST+REWARD` | Provider/Arena `reimburse+bonus` | `bounty.py:13` `issue_challenge` before purchase |
| Research subsidy | Arena VoI `demand×uncertainty×novelty` | `exploration.py:73` `score()` |

**No pay for "say B is good"** `402molt:863` — pay for `authenticated evidence` or `perform experiment`.

## 6. Chain binding (minimal gas)

- **Now (simulation):** `chain=base-sepolia-sim`, no tx, key `alch_G...` only for `eth_blockNumber` probe (verified `0x2bc7a51`)
- **Next (live):** `arena-evidence-v1` receipt `requestHash+responseHash+providerSignature` → EAS attestation on Base Sepolia (`docs/CHAIN.md`) — ~$0.001 per attestation, batch ≤64 ops (`SPEC.md:47` write-behind)
- **Bounty escrow:** off-chain `provider_funds` until 50 providers compete → `Research_Auction` `402arena:519` with `sponsor_budget_factor=log1p(balance)`

## 7. Verification & evolution

- **Hard gates** `AGENTS.md:3` gates dominate: `quality_pass ≥0.7` never traded for cost
- **Stats:** Wilson CI on `best` rate, contextual `BradleyTerry.fit_contextual` per `task_type` `preferences.py:30`
- **QD archive** `SPEC.md:80` `style-family × cost` elites-per-cell, `recipes:elitist_mutation` mutates `k/threshold/diversity/VoI`
- **Idempotency:** `job_id` + `run_id` blake3 → double-claim ( `HERMES.md:33` race) never double-counts

## 8. What we will implement next (after spec approval)

1. `hermes_adapter` worker loop `claim_next → EvidenceRetriever.search → synthetic_agent_choose (ox-alpha prompt) → record_best_worst → log receipt`
2. `scripts/hermes_live_loop.py` — continuous `while True: claim or sleep`, respects `api_limits` `AGENTS.md:11`
3. `scripts/project_to_hydra.py` — replay `logs/*.jsonl` → `HydraClient.batch` (`loop.py:50` query pattern)
4. `worldpacks/arena402/experience.py` — Hydra read `top_policies` for next `propose_children`
5. Base Sepolia attestation stub `tools/eas_attest.py` (dry-run until we fund `$1` for 1,000 attestations)

## 9. Alignment audit vs all 402 research (verbatim)

**`402arena-peer-review-verbatim.md:810` (17 points):**
- `402arena:3` **Recommend vs Arena split** — `mode=arena` (explore, sponsor can affect exposure `Arena` `402arena:50`) vs `mode=recommend` (exploit, sponsor never enters score `402arena:29`) both in `retrieval.py:36`
- `402arena:70` **Flaws table** — all 10 fixed: `0.70/0.20/0.10→0.80/0.20 arena` (`retrieval.py:54`), greedy MMR (`retrieval.py:59`), `winner>all→best>worst` (`store.py:191`), contextual `skill(request,provider)` (`preferences.py:30`), `slate_provenance` (`store.py:49`), randomized (`retrieval.py:103`), atomic `provider_funds` + `bounty.py:13`, adaptive `k` (`exploration.py:97`)
- `402arena:135` **S*=αU+βI+γD-δC** slate bandit — `U=sim+freshness, I=VoI, D=diversity, C=tokens/latency` weights `αβγδ` in `policy_surface` evolved by Cogym
- `402arena:157` **Eligibility gate** `sim≥thr AND schema/budget/health/price≤budget` (`retrieval.py:25`) before slate, prevents weather-for-Solidity
- `402arena:195` **Representative not best** — `retrieval.py:76` medoid/TODO, not max quality outlier
- `402arena:240` **Two-stage** blind `BEST/WORST` → reveal price → `ACTUAL PURCHASE` → quality vs economic `402arena:299` separate labels (`service.py:24` + `store.record_best_worst`)
- `402arena:311` **BWS/MaxDiff** best+worst json `reason_codes` + contextual BT/PL (`preferences.py:35`)
- `402arena:344` **Adaptive K 3-8** — `adaptive_k(uncertainty)` table `3 if <0.25 else 4/5/6` (`exploration.py:97`), evolved not hard-coded
- `402arena:394` **Slate composition 2+1+1+1+1** incumbents/pareto/challenger/diversity/experimental — `k=5` composition in `policy_surface`, sixth slot is provider-funded exploration
- `402arena:432` **Sequential elimination $0.02→$0.50→paused** — `exploration.py:73` `loss>0.7→0.5 subsidy, >0.85+50→None` until `v2`
- `402arena:497` **ResearchValue=Demand×Uncertainty×Novelty×Drift×CompProb** — `exploration.py:104` + progressive `budget_factor=log1p(balance)` (`arena40254:466`)
- `402arena:552` **Conservative ≥95%** — `conservative_slate_ok:108` regret budget
- `402arena:579` **Position bias IPS** — `slate_provenance.p_include/p_position/algo_version/sponsor` (`store.py:49`) + uniform shuffle (`retrieval.py:103`)
- `402arena:615` **Multileaving** separate `SLATE GENERATION` vs `QUALITY ESTIMATION`
- `402arena:644` **Lifecycle UNSEEN→SEEDED→CHALLENGER→ORGANIC→DECAYED/ELIMINATED** — `bounty.py:13` seeds UNSEEN via funded `arena_task_id` → `report.py` tracks exposures→organic lift
- `402arena:691` **No global ranking** #17 #1 coding #24 news — contextual `fit_contextual(task_type)` (`preferences.py:30`)

**`402molt-evidence-market-verbatim.md:930`:**
- **Loop** need-money vs have-evidence `402molt:3` → `arena.find` + `arena.sell_evidence` both sides in spec 3
- **Tiered evidence price** `request $0 → receipt $0.0001 → +response $0.0008 → +outcome $0.0021` `402molt:220` — `evidence/quote` not flat `402molt:460` `DataValue=futureDemand×uncertainty×regret×freshness×strength×uniqueness`
- **Bounties live market** `technical-search×NewSearch $0.0042 needed 81` `402molt:249` → `HERMES AGENT` bounty board `bounty.py`
- **Two markets organic $0.0007 vs commissioned reimburse $0.004+reward $0.003** `402molt:275` — `store.provider_funds` vs `bounty` reimbursement
- **Microjobs** run provider/compare outputs/execute downstream/re-test stale `402molt:311` — `hermes_live_loop` publishes as jobs
- **Receipt extension** `arena-evidence-v1 requestHash/responseHash/providerSignature` `402molt:378` → grades `A signed/B proxied/C buyer-signed` `402molt:421` weighted differently
- **Discovery** x402 Bazaar `arena.recommend/evidence_quote/sell_evidence/bounties` + `@402arena/x402` wrapper lifecycle hooks `cashback $0.0007` `402molt:602-646` — spec 6 Bazaar + wrapper TODO
- **Moltbook** `m/arena-bounties` as distribution, not infra `402molt:661` — spec notes distribution channel
- **Generic observation** `INTENT→SERVICE→OUTPUT→COST→OUTCOME` beyond x402 `MCP/A2A/Moltbook/coding/model/compute` `402molt:685` — worldpack `experience.py` extensible, x402 is start
- **Wash trading** provenance `ORGANIC/ARENA_COMMISSIONED/PROVIDER_SPONSORED/SELF_REPORTED` + `wallet correlation/duplicate/timing/clusters` `402molt:834` — `store.slate_provenance.sponsor_status` + `report.py` fraud TODO
- **Never pay for "B is good"** `402molt:863` — pay `authenticated evidence` or `perform experiment`

**`arena40254-scarcity-mechanic-verbatim.md:1082`:**
- **Three modes Buyer/Scout/Bounty worker** `arena40254:13` — Buyer free, Scout paid `Arena` `arena40254:13`, Bounty `reimburse+reward`
- **2 reveals $0.0001** `arena40254:60/192` further reveals tiny payment → scarcity `store.save_provenance` enforces
- **Sequential 5→1** `Which one first? → reveal → Buy? → next` `arena40254:108` yields `C>A>rest` + `quality vs economic` `arena40254:157`
- **Subsidy as reward after commitment** `research credit -$0.006 effective $0.001` `arena40254:202` sponsor cannot contaminate blind ranking
- **Provider dashboard 22 rows** `Qualified opportunities...Organic lift/Version drift` `arena40254:1001` + niche map `technical docs 83%` `arena40254:1031` — `report.py:5` implements core, full 22 TODO
- **Privacy tiers** `RAW/REDACTED/DERIVED embedding+taxonomy` `arena40254:369` — spec needs adding to `report` privacy controls
- **Diminishing ExposureWeight=log(1+bid)** `arena40254:466` + **cost rise Trial1 $0.005→$0.50 paused** `arena40254:514` — both in `exploration.py:73`
- **Signed challenge before purchase** `arena_task_id/request_hash/provider/wallet/nonce/deadline` `arena40254:655` — `bounty.py:13`
- **Organic $0.0007 cheapest** `arena40254:687` vs commissioned
- **Scout full ranking with hidden controls** `deterministic tasks/repeated pairs/dominated outputs` + `reliability posterior` `arena40254:751` — spec needs Scout reliability TODO
- **Hierarchy SCOUT<RANKING<BLIND<PURCHASE<SUCCESS** `arena40254:783` strongest at bottom
- **Keep 2 of 5 tournament** `B,E > A,C,D → E>B` `arena40254:845` — `store.record_tournament:233`
- **K(request,uncertainty,value) 3/5/7/8** `arena40254:937` — `adaptive_k` already
- **D-optimal opponents** `1 incumbent+1 closest+1 price+1 uncertain+NewSearch` `arena40254:975` — **Cogym evolves slate-design policy**

All runs logged, Hermes = ox-alpha-free only, mechanisms before chain.

## 10. Gaps to close before live

- `PRIVACY` raw request opt-in + `SCOUT reliability` posterior + full `22-row dashboard` + `EAS` verifier — add after first 100 live receipts

