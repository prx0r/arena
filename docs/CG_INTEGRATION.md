# Cogym integration

Base reviewed: `prx0r/cg`, latest observed commit `f8281d7e137b939bd679d279561924444926ca77` (2026-08-24).

402Arena should be one **world/problem** inside Cogym, not a rewrite of Cogym.

## World

State:
- incoming request text/features
- candidate providers and current prices
- historical evidence graph snapshot
- remaining research/subsidy budget
- timestamp / market regime

Action:
- choose provider
- optionally offer a research subsidy for a high-VOI provider
- abstain / direct route

Observation:
- response/outcome
- cost
- latency
- failure
- blind selection or downstream success

Metrics:
- quality
- cost
- regret
- coverage
- new-provider discovery speed
- calibration
- subsidy efficiency

Hard gates:
- never exceed caller budget
- sponsor balance cannot enter ranking score
- do not leak provider identity before blind choice
- private historical payloads never appear in public previews

## Cogym candidate search space

Evolve/tune:
- embedding/retrieval policy
- similarity/freshness/quality weights
- MMR provider-diversity penalty
- time-decay half-life
- Thompson prior and discount factor
- quality-vs-cost tradeoff
- VOI component weights
- subsidy threshold/cap
- cold-start prior
- drift detector threshold
- OPE deployment gate

The strongest candidate must pass chronological validation and secret holdout before becoming production router policy.

## Ready-to-copy overlay

`cg_overlay/cogym_kernel/worlds/arena402/` now implements the current `prx0r/cg` world protocol (`WorldSpec`, `ActionSpec`, `MetricVector`, registry decorator). `apply_to_cg.sh /path/to/cg` installs it.

The replay world is a one-step contextual routing problem and uses a deterministic seed to choose among frozen recorded response variants. This makes provider-routing experiments content-addressable with normal Cogym `RunReceipt`s.
