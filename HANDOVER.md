# HANDOVER — 2026-08-24 20:15 UTC

**Next agent: read this first. All other docs reference this.**

## What 402Arena Is

Empirical discovery + market for machine-service evidence. Agents pay for verified provider traces. Providers pay for blind experiments. Nobody pays for ranking.

> **Money buys experiments. Evidence buys organic ranking.** (`README.md:5`)

## Current Status

- **Tests:** 28/28 pass (mechanism, evidence_v1, evidence_market_v2, replay, ope, frontier, core)
- **Daemon:** killed (was running k=3,4,5,6 cycling correctly, 18 iterations)
- **Hermes gateway:** running (pid 2555164)
- **Hydra:** ready=True, avail=True
- **Chain:** Base Sepolia 0x2bc8a74, ETH Sepolia 0xb05d7f (0 tx, dry-run)
- **Receipts:** 727+ total (`rank_sim 500 + live_hermes_z 189 + live_arena 30 + evolve 5 + anticheat 2 + batch 3 + hidden 1 + integrated 1`)
- **K sweep:** k=3,4,5,6 confirmed cycling in live log

## What Works (H1-H8)

| H | Hypothesis | Status | Evidence |
|---|---|---|---|
| H1 | Sponsor≠organic | CONFIRMED | `separated_ids beats paid_rank_bad` |
| H2 | Scarce 20% switch | CONFIRMED | `79.6% vs 100%` greedy +26pp |
| H3 | K=4 optimal | PROVISIONAL | `0.833 > 0.829` synthetic, live cycling |
| H4 | BWS anti-cheat | CONFIRMED | delta 0.0017 |
| H5 | Wash detectable | CONFIRMED | 1.0 self-deal vs 0.0 clean |
| H6 | Lifecycle funds test | PROVISIONAL | not yet stressed |
| H7 | Hermes real | PARTIAL | 88% deterministic, LLM quality partial |
| H8 | Market saturates | CONFIRMED | bid→0 at n>80 |

## 19 Remaining Gaps (from 25 total)

1. Wire record_tournament into daemon (not just record_best_worst)
2. Enforce 2-reveal limit
3. Integrate bounty.py with x402 USDC on Base Sepolia
4. Apply GRADE A-D weights in ranking
5. Hidden controls 10% provider + scout_reliability live
6. Fetch 402Pilot 20,575 + 5k replay
7. WorkReceipt→GRADE adapter (Moltwork M2-M4→GRADE A-C)
8. Wire adaptive_k to live uncertainty (not iter_n %4)
9. Base Sepolia escrow deploy (forge script, $5)
10. Privacy tiers RAW/REDACTED/DERIVED
11. Multileaving (research only)
12. Representative medoid selection
13. Position debiasing truly random
14. DataValue pricing for sell_evidence
15. Two-market organic vs commissioned live
16. GRADE in ranking
17. ArenaEvidenceV1 end-to-end live
18. Wallet correlation wash live
19. Moltbook bounties distribution

## Queue — What To Do Next

### 1. Restart daemon
```bash
nohup python3 /root/402arena/scripts/continuous_hermes_daemon.py >> /root/402arena/logs/daemon.log 2>&1 &
```

### 2. 402Pilot frozen replay
```bash
python3 scripts/fetch_402pilot.py --out /tmp/402pilot
# then run_402pilot --rounds 5000
```

### 3. Deploy Base Sepolia escrow
```bash
cd contracts && forge script Deploy.s.sol --rpc-url https://base-sepolia.g.alchemy.com/v2/alch_GX8... --broadcast
```

### 4. Fix top-5 gaps
- tournament in daemon
- reveal limits
- D-optimal already done
- dashboard 22 rows already done
- provenance tags already done

## Files In Good Order

| Path | Status | Lines |
|---|---|---|
| `HANDOVER.md` | This file | canonical |
| `docs/CANONICAL_REFERENCE.md` | H1-H8 + findings | updated 19:55 |
| `docs/MOLTBOOK_MOLTWORK_WALLET_SPEC.md` | Integration spec | 120+ |
| `docs/ETHEREUM_STANDARDS.md` | ERC-8004 + x402 | 150+ |
| `docs/MOLTWORK_VISION.md` | Visionary integration | 70 |
| `docs/MECHANISM_SPEC.md` | Organic/research formulas | 60+ |
| `docs/HERMES_AGENT_SPEC.md` | Hermes = agent | 150+ |
| `docs/NEXT_DEV_PLAN.md` | 5-phase roadmap | 80+ |
| `docs/CHAIN.md` | Base Sepolia vs ETH | 30+ |
| `docs/SIMULATION_DESIGN.md` | Full x402 integration | 80+ |
| `docs/FRONTIER_RESEARCH.md` | D-optimal, multileaving | 200+ |
| `arena402/retrieval.py` | D-optimal + eligibility + mode | updated |
| `arena402/provider_report.py` | 22-row dashboard + niche | updated |
| `arena402/store.py` | Provenance tags, BWS, tournament | updated |
| `arena402/x402.py` | ArenaEvidenceV1 + schemas | updated |
| `arena402/bandits.py` | DiscountedContextualBeta | unchanged |
| `arena402/simulation.py` | 12-provider hidden winner | unchanged |
| `arena402/anti_cheat.py` | Wash 6 checks, scout reliability | unchanged |
| `arena402/evidence_market.py` | quote_organic, bounty, GRADE | unchanged |
| `tests/test_evidence_v1.py` | ArenaEvidenceV1 E2E | 3 tests |
| `tests/test_evidence_market_v2.py` | Quote saturated/sparse | 2 tests |
| `tests/test_mechanism.py` | 8 mechanism tests | unchanged |
| `imports/moltwork/` | Full Moltwork repo (MIT) | unchanged |
| `logs/` | 727+ receipts JSONL | canonical |
| `experiments/results/` | mechanism_sweep, logs mirror | unchanged |
| `REFERENCE.md` | 9-category index | updated |
| `README.md` | Points to HANDOVER.md first | updated |

## Key Commands

```bash
# Check daemon
tail -f /root/402arena/logs/daemon.log
wc -l /root/402arena/logs/live_hermes_z.jsonl

# Run tests
cd /root/402arena && python3 -m pytest -q

# Check chain
python3 -c "import urllib.request,json;k=open('/root/402arena/.secrets/alchemy.key').read().strip();r=urllib.request.urlopen(urllib.request.Request(f'https://base-sepolia.g.alchemy.com/v2/{k}',json.dumps({'jsonrpc':'2.0','id':1,'method':'eth_blockNumber','params':[]}).encode(),{'Content-Type':'application/json'}),timeout=5);print(json.loads(r.read().decode()).get('result','?')[:10])"

# Check Hermes
hermes kanban --board cogym-lab stats

# Check Hydra
python3 -c "from cogym_kernel.experience.client import HydraClient;import asyncio;c=HydraClient();print(c.ready(),asyncio.run(c.available()))"
```
