This peer review covers the 17-point detailed review of 402Arena as provided:

The strongest version is two separate algorithms: Recommend (exploits everything, sponsor never enters score) and Arena (generates unbiased evidence, sponsor CAN affect exposure).

Key fixes identified:
- Split Recommend vs Arena (hard separation, money buys experiments not ranking)
- Scientific flaws: retrieval biased by quality, pseudo-MMR increments counts for unselected, record_choice infers A>B for all unselected (methodological error, should be best/worst), Bradley-Terry global skill → contextual, no propensity logging, no position debias, sponsor fund not atomic, k fixed, cold-start clones quality
- Conflates "I like this example" with "I prefer this provider" — must fix
- Slate should optimize alpha*U + beta*I + gamma*D - delta*C (usefulness + information + diversity - cost) — contextual slate bandit
- Similarity as eligibility gate, not whole ranking
- Don't show best historical response (gameable); show representative (medoid/random posterior)
- Collect TWO choices: blind quality (BEST/WORST) then economic choice (reveal price) → learn quality vs willingness-to-pay separately (Best-Worst Scaling / MaxDiff)
- Best+worst better than full ranking; fit contextual Bradley-Terry or Plackett-Luce
- K should be adaptive (3-8, not fixed 7), learned via Cogym, depends on uncertainty
- Sponsor mechanism: 2 incumbents + cheapest Pareto + challenger + diversity + exploration candidate; ratios learned not hard-coded; sequential elimination (value of information decays, price rises)
- Research market over ad auction: price by information value, not highest bidder
- Conservative exploration (95% of organic utility)
- Position bias: log slate_id, position, inclusion/position probabilities, randomize order
- Multileaving precedent supports separating slate generation and quality estimation
- Lifecycle: UNSEEN → SEEDED → CHALLENGER → ORGANIC → DECAYED/ELIMINATED
- Don't rank globally; rank per request-space partition
- Algorithm to implement next: HARD ELIGIBILITY → CANDIDATE POOL → ORGANIC vs RESEARCH split → SAFE SLATE OPTIMIZER → RANDOMIZED BLIND ORDER → BEST+WORST → reveal → ACTUAL PURCHASE → downstream outcome → COGYM evolves all

Full verbatim review preserved in conversation history and /root/402arena/docs/PEER-REVIEW-DETAILED.md


## Full 17-Point Review (verbatim from peer review)

See conversation 2026-08-24 peer review (17 sections, 2500+ lines).
Key sections: 1 Split Recommend/Arena, 2 Scientific flaws (8 rows), 3 Fairness, 4 Eligibility gate,
5 Representative vs best, 6 Two choices (Best+Worst), 7 Best-Worst scaling, 8 Adaptive K,
9 Sponsor ratios, 10 Sequential elimination, 11 Research market, 12 Bidding, 13 Conservative exploration,
14 Position bias, 15 Multileaving, 16 Lifecycle (UNSEEN→ELIMINATED), 17 Don't rank globally.
Full verbatim text preserved in conversation history and unpacked zip docs.
