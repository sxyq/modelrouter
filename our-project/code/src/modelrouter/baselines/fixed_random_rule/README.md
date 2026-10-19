# Static, Random, and Heuristic Baselines

This package provides standard non-learned comparative routing baselines.

## Policies
1. **`FixedStrongPolicy` (`fixed_strong`)**: Always routes to the Flagship model (`gpt-6-luna` or `gpt-4o`). Provides the upper-bound accuracy ceiling.
2. **`FixedCheapPolicy` (`fixed_cheap`)**: Always routes to the lowest-cost model (`gpt-5.6-luna` or `deepseek-chat`). Provides the lower-bound cost baseline.
3. **`RandomPolicy` (`random`)**: Uniform random selection across all legal actions.
4. **`RuleStickyPolicy` (`rule_sticky`)**: Phase-conditioned heuristic routing with an emergency budget preservation override when remaining budget falls below \$0.30.

## CLI Usage
```bash
python -m modelrouter.baselines.fixed_random_rule.runner --policy rule_sticky --phase modify
```
