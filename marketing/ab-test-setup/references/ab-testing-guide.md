# A/B Testing Comprehensive Guide

## Statistical Foundations

### Hypothesis Testing Framework

Every A/B test is a hypothesis test:
- **Null hypothesis (H0):** There is no difference between variants
- **Alternative hypothesis (H1):** There is a meaningful difference

Key parameters:
- **Significance level (alpha):** Probability of false positive (typically 0.05)
- **Power (1-beta):** Probability of detecting a real effect (typically 0.80)
- **Minimum Detectable Effect (MDE):** Smallest effect size worth detecting

### Type I and Type II Errors

| | H0 True (No Effect) | H0 False (Real Effect) |
|---|---|---|
| Reject H0 | Type I Error (False Positive) | Correct Decision |
| Fail to Reject H0 | Correct Decision | Type II Error (False Negative) |

- **Type I error rate** = alpha (typically 5%)
- **Type II error rate** = beta (typically 20%)
- **Power** = 1 - beta (typically 80%)

### Z-Test for Proportions

For conversion rate tests (binary outcomes), use a two-proportion z-test:

**Test statistic:** z = (p1 - p2) / sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

Where:
- p1, p2 = conversion rates of control and treatment
- p_pooled = (x1 + x2) / (n1 + n2)
- n1, n2 = sample sizes

**Decision:** Reject H0 if |z| > z_alpha/2 (1.96 for alpha=0.05)

### Confidence Intervals

A 95% confidence interval for the difference in proportions:

(p1 - p2) +/- z_alpha/2 * sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)

If the confidence interval excludes zero, the result is statistically significant.

## Sample Size Theory

### Sample Size Formula

For a two-proportion z-test:

n = (z_alpha/2 + z_beta)^2 * (p1*(1-p1) + p2*(1-p2)) / (p1 - p2)^2

Where:
- z_alpha/2 = 1.96 for 95% confidence
- z_beta = 0.84 for 80% power
- p1 = baseline conversion rate
- p2 = expected conversion rate with treatment

### Trade-offs

**Larger sample = More precision, but:**
- Longer test duration
- Higher opportunity cost
- More exposure to potentially worse variant

**Smaller sample = Faster, but:**
- Higher chance of missing real effects (Type II error)
- Wider confidence intervals
- Less reliable estimates

### Duration Estimation

Test duration = Required sample size per variant / Daily traffic per variant

**Important adjustments:**
- Minimum 2 full business cycles (typically 2 weeks)
- Account for day-of-week effects
- Avoid launching during holidays or special events
- Don't peek at results before planned analysis date

## Common Pitfalls

### 1. Peeking Problem

Checking results repeatedly before reaching full sample size inflates false positive rate. At 5% alpha with daily checks, the actual false positive rate can exceed 30%.

**Solutions:**
- Pre-commit to analysis date
- Use sequential testing methods if early stopping is needed
- Adjust alpha using Pocock or O'Brien-Fleming boundaries

### 2. Multiple Comparisons

Testing multiple metrics increases false positive rate. With 20 metrics at alpha=0.05, you expect 1 false positive on average.

**Solutions:**
- Designate one primary metric before test starts
- Apply Bonferroni correction for secondary metrics
- Use False Discovery Rate (FDR) control

### 3. Simpson's Paradox

Overall results can be misleading when segment proportions differ between variants. A treatment can appear worse overall while being better in every segment.

**Solution:** Always check for consistent effects across key segments.

### 4. Novelty and Primacy Effects

- **Novelty effect:** Users engage more with something new (temporary lift)
- **Primacy effect:** Users prefer the familiar (temporary decline)

Both wear off over time. Run tests long enough (minimum 2 weeks) to account for these.

### 5. Selection Bias

Non-random assignment invalidates results. Common causes:
- Cookie-based assignment with high cookie deletion rates
- Device-specific assignment without cross-device tracking
- Time-of-day assignment differences

### 6. Insufficient Power

Running underpowered tests wastes resources. With 50% power, you have a coin-flip chance of detecting a real effect.

**Rule of thumb:** Always aim for 80%+ power. For critical decisions, use 90%.

## Advanced Topics

### Multi-Variant Testing (A/B/n)

Testing more than 2 variants simultaneously:
- Increases sample size requirement
- Requires multiple comparison correction
- Useful for testing multiple creative options
- Apply Dunnett's test (compare all variants to control)

### Sequential Testing

Allows checking results at pre-defined intervals with controlled error rates:
- **Group Sequential:** Check at fixed intervals (weekly), use adjusted boundaries
- **Always Valid:** Continuous monitoring with confidence sequences
- Trade-off: ~20-30% larger sample size for flexibility of early stopping

### Bayesian A/B Testing

Alternative to frequentist approach:
- Provides probability of treatment being better (e.g., "92% chance of improvement")
- Naturally handles early stopping
- Requires prior specification
- Results are more intuitive for stakeholders

### Interaction Effects

When running multiple concurrent tests:
- Full factorial design captures all interactions
- Requires much larger sample sizes
- Most interactions are negligible in practice
- Monitor for unexpected interactions on shared metrics

## Test Planning Checklist

1. Define clear, measurable hypothesis
2. Select primary metric (one only)
3. Define secondary metrics (up to 3-5)
4. Calculate required sample size
5. Estimate test duration
6. Define segments for subgroup analysis
7. Set analysis date (commit to it)
8. Document test plan and share with stakeholders
9. Verify instrumentation and data collection
10. Launch and monitor for technical issues (not results)
