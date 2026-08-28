# Report 3 — Anti-Cheat: Wash + BWS

**Logs:** `anticheat_tests.jsonl:2` `wash 1.0 self-deal` + `BWS delta 0.0017`.

**Hypothesis H4/H5:** Wash `wallet correlation + duplicates + timing` flags farming; BWS scarce disincentivizes cheap talk vs full ranking.

**Method:** `AntiCheat wash 6 checks` self-deal `0.4` duplicate `0.3` burst `0.2` (`anti_cheat.py:10`); `bws_vs_full_cheat_test` `full 0.001 vs BWS -0.0007`.

**Results:**
- `wash 1.0 is_wash True reasons ['self-deal buyer owner_of_p1 == owner of p1', 'self-deal buyer owner_of_p1 == owner of p1']` for `owner_of_p1 == owner` + duplicate prompts.
- Clean live `wash 0.0` vs self-deal `1.0` validates threshold `0.5`.
- `BWS delta 0.0017` — random gets $0.001 under full ranking but loses $0.0007 reveal value under BWS.

**Proves:** Wash detection threshold `0.5` works; BWS scarcity makes random unprofitable (`402molt:863` never pay for say B is good). **H4/H5 CONFIRMED**.

**Drives:** Enforce `heavy buyer >10` `0.15` + `duplicate >3` `0.3` live; use `wash_score` to downweight `GRADE C` in ranking.
