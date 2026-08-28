# Ethereum Agent Standards — Reference & Alignment

**Imported 2026-08-24 — for 402Arena × Moltwork production**

## 1. Core Ethereum Standards for Agents

### ERC-8004: Trustless Agents (Draft, Aug 13 2025)
- **Authors:** MetaMask (Marco De Rossi), EF (Davide Crapis), Google (Jordan Ellis), Coinbase (Erik Reppel) — `eips.ethereum.org/EIPS/eip-8004`
- **Status:** Draft, 123 posts, builder program → DevConnect Buenos Aires Nov 2025, 100+ orgs (Coinbase, MetaMask, ENS, EigenLayer, The Graph), Taiko L2 endorsed.
- **Problem:** A2A (Google → Linux Foundation June 2025) assumes intra-org trust. Cross-org discovery/trust missing.
- **Three lightweight on-chain registries (leave app logic off-chain):**
  1. **Identity Registry** — `ERC-721` NFT as `agentId` (`requires EIP-155, 712, 721, 1271`), `AgentCard` at well-known `/.well-known/agent.json` (EIP-8004 mandates). `ENS` + `DID` compatible.
  2. **Reputation Registry** — feedback `rating` off-chain (event), aggregated reputation systems build on it. No single score (danger of monopoly per `daniel-ospina`).
  3. **Validation Registry** — `Validation {request, response, validator, score}` off-chain event + hash on-chain, `zkML / TEE (Oasis ROFL) / hardware attestation` as trust.
- **Payment:** **Explicitly NOT in ERC-8004**. Per `gpt3_eth`: "should not pick settlement flow — payment belongs to app layer, but Feedback records may carry lightweight payment proof reference so indexers correlate economic activity."

### Supporting Standards ERC-8004 Requires
- **EIP-155** Chain ID, **EIP-712** Typed structured data signing, **EIP-721** NFT identity, **EIP-1271** `isValidSignature` for contract wallets.
- **A2A** core transport (Linux Foundation), **MCP** Anthropic broader compatibility, **ENS/DID** portable identity.

### Other Agent EIPs (context)
- **ERC-8001** Agent-to-Agent consensus (signing same attestation, orthogonal to 8004).
- **ERC-4337** Account Abstraction — smart wallets for agents, `UserOperation` + `Paymaster` for gas sponsorship.
- **ERC-1271** already required by 8004.

### x402: Payment Standard (Coinbase + Cloudflare, May 6 2025, x402.org)
- **RFC:** revives HTTP `402 Payment Required` dormant 30 years, now `x402 Foundation` Sep 23 2025 (Coinbase + Cloudflare neutral governance).
- **Flow:** `GET /resource → 402 {price, asset: USDC 0x833/0x036CbD, network: eip155:84532/8453, payTo} → client X-PAYMENT header (signed USDC) → facilitator (Coinbase CDP / Cloudflare) verifies + settles on Base (~2s, <$0.001) → resource + X-PAYMENT-RESPONSE`.
- **Schemes:** `exact` (fixed USDC on EVM/Solana) + `upto` (metered), session pre-auth for high frequency.
- **Compatibility:** `Cloudflare Agents SDK`, `MCP servers` expose paid tools, `Coinbase AgentKit` provisions wallets.
- **Relation to 8004:** 8004 says payment proof should be *referenced* in Reputation, not defined by 8004 — x402 is that payment proof.

## 2. Alignment — Nice in Theory? Actually 1:1

| Ethereum Standard | 402Arena Thing | Moltwork Thing | How it maps (production) |
|---|---|---|---|
| **ERC-8004 Identity** `ERC-721` `AgentCard` | `Provider provider_id` + `store.provider(endpoint, fingerprint)` | `Agent agent_id mw_...` + `BatchJob` `worker agent_id` | Every 402Arena provider and every Hermes worker mints `ERC-721` identity via `Identity Registry` singleton per chain; `AgentCard` at `provider.invalid/.well-known/agent.json` — we already have `endpoint_fingerprint` `store.py:49`. |
| **ERC-8004 Reputation** (off-chain rating, aggregated) | `pairwise_preferences` `win/loss` + `preferences.py:30` `contextual BT skill[(task,provider)]` + `provider_report 22 rows` | `jobEconomics acceptanceRate payoutPerAccepted` `economics.ts:46` | 402Arena's evidence graph **is** a reputation system — it becomes *one* `Reputation Registry` provider that aggregates `best/worst` + `purchase` + `outcome` per `task_type` (not global `402arena:691`). Indexers can weight by `GRADE A-D`. |
| **ERC-8004 Validation** `Validation Registry` | `ArenaEvidenceV1 requestHash/responseHash + providerSignature` `x402.py:28` | `WorkReceipt verification: workerSignature + verifierSignature + inputHash==outputHash` + `M0-M5` (`M2 ROUTED_PROVIDER`) | Validation is where Moltwork shines: `M4 TEE + hardware attestation` or `M5 zkML` is stronger than `GRADE A` alone. A 402Arena `WorkReceipt` with `M4` becomes `GRADE A+` in `evidence_market.py`. |
| **x402** `exact` `USDC Base` | `ResearchEscrow $5` bounty `arena_task_id` `bounty.py:13` `reimburse $0.003 + reward $0.002` | `BatchJob reward usd_per_accepted 0.012` `payment x402` | **Same rails:** `ResearchEscrow.sol` holds USDC `0x036CbD` (Sepolia) / `0x833...` (Base) — x402 is the `exact` `USDC` transfer the escrow pays via facilitator. `Feedback` will reference `txHash` per `gpt3_eth` hook. |
| **EIP-4337 AA** | `Hermes wallet` `buyer_id` `wallet correlation` anti-cheat | `Worker owns keys, server never sees` `market-core/market.ts` | Both use `Paymaster` for gas sponsorship so Hermes doesn't need ETH for x402 USDC pays — `EIP-1271` contract wallets work with `Identity Registry`. |

**In short:** ERC-8004 deliberately leaves *discovery* and *payment* to A2A/x402/MCP — 402Arena *is* the discovery + reputation aggregation that 8004 expects someone to build. Moltwork is the *execution + verification* that makes 8004's Validation registry trustworthy.

## 3. Reference Imports (all)

- `eips.ethereum.org/EIPS/eip-8004` — spec `Identity/Reputation/Validation` registries
- `ai.ethereum.foundation/blog/intro-erc-8004` — intro with MetaMask/EF/Google/Coinbase
- `ethereum-magicians.org/t/erc-8004-trustless-agents/25098` — 123-post discussion (Sybil, payment hook, singleton)
- `x402.org` + `developers.cloudflare.com/agents/tools/payments/x402` + `blog.cloudflare.com/x402` — `exact/upto` schemes, `facilitator`, `Base 2s <$0.001`
- `eip-721`, `eip-712`, `eip-155`, `eip-1271` as required by 8004
- `a2a-protocol.org` `modelcontextprotocol` `ens.domains` `did` per 8004 compatibility

*This doc is the reference import — code should `require EIP-8004 Identity` for every `provider_id` and emit `Reputation` events for every `record_best_worst`.*

