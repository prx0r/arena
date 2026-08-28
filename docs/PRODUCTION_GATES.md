# Sepolia → production gates

## Gate 0 — deterministic science

Required:

- all unit/invariant tests pass;
- every experiment records seed/config/code version/data hash;
- 402Pilot replay reproducible;
- synthetic cold-start winner is discovered faster than organic baseline under a bounded research budget;
- paid-rank negative control demonstrates why sponsor/organic separation is necessary.

## Gate 1 — Base Sepolia

Use only testnet assets.

Required:

- chain ID 84532 verified before signing;
- buyer, seller, signer and Arena operator keys are separated;
- x402 Signed Offers & Receipts enabled;
- exact request/response hashes separately provider-signed;
- ResearchEscrow conservation/replay tests pass;
- no private payloads written onchain;
- evidence roots independently recomputable.

## Gate 2 — shadow mainnet

No autonomous Arena-funded purchase.

Required:

- live provider metadata ingestion;
- endpoint/version fingerprints;
- propensities logged for every slate;
- provider privacy/data-retention policy;
- abuse detection and rate limits;
- dashboard clearly distinguishes organic, commissioned and provider-sponsored evidence.

## Gate 3 — capped live research

Start with explicit fixed daily research-loss budget and per-provider/per-wallet caps. Human operator can disable all spending.

Required:

- only qualified experimental candidates can receive sponsored exposure;
- conservative-regret budget enforced;
- no campaign can exceed configured task exposure share;
- evidence quote/bounty duplicate checks active;
- provider campaign can be refunded/closed;
- organic score audited to contain no sponsor term.

## Gate 4 — automated market

Only after enough logged data supports off-policy evaluation.

Add:

- contextual model instead of coarse task buckets;
- slate OPE / doubly robust evaluation;
- sequential confidence / change-point handling;
- calibrated downstream outcome model;
- potentially a capped research-slot auction, but only after posted-price campaigns are understood.
