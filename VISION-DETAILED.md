This peer review covers the 17-point detailed vision for 402Arena as provided in full conversation 2026-08-24.

Core principle: Two separate algorithms — Recommend (exploits everything, sponsor never enters score) and Arena (generates unbiased evidence, sponsor CAN affect exposure). Money buys experiments, never ranking.

Key mechanisms:
- VOI(request,provider) = uncertainty × demand × novelty × competitive-uncertainty × freshness × routing-improvement / cost
- Slate optimization: S* = argmax[αU + βI + γD - δC]
- Hard eligibility gate before slate generation
- Representative outputs (medoid), not best historical
- Two-stage choice: blind quality (BEST/WORST) then economic choice (reveal price) → learn quality vs willingness-to-pay separately
- Best-Worst Scaling / Plackett-Luce for incomplete rankings
- Adaptive K (3-8), learned via Cogym, not fixed
- Sequential elimination: exposure price rises as evidence accumulates
- Research market pricing by VOI, not highest bidder
- Three evidence grades (A: provider-signed hashes, B: Arena-proxied, C: buyer-signed)
- Evidence grades determine ranking weights
- Conservative exploration (95% organic utility)
- Position bias logging + randomization
- Lifecycle: UNSEEN → SEEDED → CHALLENGER → ORGANIC → DECAYED/ELIMINATED
- Don't rank globally, rank per request-space partition

Full verbatim 2500+ line peer review preserved in conversation history.
