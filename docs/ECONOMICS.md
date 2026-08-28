# Economics before live spend

The economic unit is **a useful new observation**, not an API call.

A sponsor funds experiments. 402Arena never sells ranking. It uses the fund only when the estimated value of information (VOI) exceeds a threshold.

## First simulation grid

For each policy and each market regime, measure:

- future quality on chronological holdout
- future spend on chronological holdout
- quality/$
- regret to a replay oracle
- provider/task coverage
- how quickly a new cheap winner is discovered
- subsidy spend
- incremental future utility per $1 subsidy

Run at research budgets: `$0, $1, $5, $10, $25, $50` per 10,000 requests.

## Stop-subsidizing rule

A provider/task neighborhood should receive near-zero subsidy when:

- effective sample mass is already high;
- posterior uncertainty is low;
- evidence is fresh;
- its closest competitor is clearly worse;
- buying another observation is unlikely to change a future routing decision.

## Seed-provider contract

A provider may deposit an exploration budget. The contract should promise only:

1. eligibility for blind real-demand experiments;
2. immutable/raw result retention where consent permits;
3. a report of where it wins/loses;
4. no paid boost to production ranking.

This makes the product closer to "pay for measurement" than advertising.
