# Pricing Experimentation Guide

Pricing experiments differ from feature experiments in three important ways:

1. **Revenue sensitivity**: a 5% drop in conversion at a 20% higher price might still be a revenue win. A feature experiment usually optimizes a single conversion-rate proxy; a pricing experiment requires multi-metric reasoning.
2. **Cohort effects matter more**: the customers a pricing change attracts (or repels) will retain at different rates than the baseline. The signal you care about is often 90 days out, not 3 days out.
3. **Legal and ethical exposure**: showing different prices to different customers raises consumer-protection concerns in some jurisdictions. Test design must account for this.

This guide covers the practical mechanics: hypothesis design, sample sizing, readout windows, mix-shift detection, and common pitfalls.

## Hypothesis design

A well-formed pricing hypothesis has four parts:

1. **The change**: "raise the Pro tier from $29 to $39"
2. **The predicted effect on the primary metric**: "ARPU will increase by ≥ 15%"
3. **The threshold for the secondary guardrail**: "without dropping conversion-to-paid more than 8 percentage points relative"
4. **The duration**: "measured over a 6-week test period with 90-day retention follow-up"

Worked example:

> Raising the Pro tier from $29 to $39 will increase ARPU among new sign-ups by at least 15% relative to the control arm, without dropping conversion-to-paid more than 8 percentage points relative, measured over a 6-week test period. We will read out at 6 weeks for the primary metric and at 12 weeks plus 90-day cohort retention for the durability metric.

Anti-patterns in hypothesis design:

- **Vague metric**: "we expect engagement to improve". Pricing experiments need revenue-grade metrics.
- **No threshold**: "we expect conversion to drop a bit". Quantify "a bit".
- **No duration**: failing to state the readout window invites peeking and motivated stopping.

## Sample sizing

For a binary metric (conversion rate), the standard sample size formula at 80% power and 5% significance:

```
n per arm = ((z_alpha + z_beta)² * (p1*(1-p1) + p2*(1-p2))) / (p1 - p2)²
```

Where `p1` and `p2` are the baseline and post-change conversion rates.

For a continuous metric (ARPU), the formula uses variance:

```
n per arm = 2 * (z_alpha + z_beta)² * sigma² / delta²
```

Where `sigma` is the standard deviation of ARPU in the baseline and `delta` is the absolute change you want to detect.

Practical rule of thumb for SaaS pricing tests:

| Baseline conversion | MDE (relative) | Sample per arm |
|---|---|---|
| 1% | 5% | ~63,000 |
| 1% | 10% | ~16,000 |
| 3% | 5% | ~20,000 |
| 3% | 10% | ~5,000 |
| 5% | 10% | ~3,000 |

If your traffic does not support these volumes, you have three options:

1. **Reduce MDE expectations**: accept that you can only detect large effects.
2. **Test on multiple acquisition channels** to broaden the funnel.
3. **Don't A/B test**: gather willingness-to-pay through surveys (Van Westendorp, conjoint) and roll out a decision without a test. This is reasonable for small-traffic products.

## Readout windows

Pricing effects unfold across multiple windows:

| Window | What you measure | What it tells you |
|---|---|---|
| **Day 1-3** | Visitor-to-trial conversion | Initial price-point reaction; high noise |
| **Day 7-14** | Trial-to-paid conversion | Whether the price changed the buy decision |
| **Day 30** | First-month retention | Whether buyers regret the purchase |
| **Day 90** | Cohort retention, downgrades | The durable effect on revenue per cohort |
| **Day 180+** | LTV by cohort | The full picture; rarely available before rollout decisions |

A 2-week test that shows a conversion drop and a 14-day ARPU lift is suggestive, not conclusive. Decisions on permanent pricing changes typically need at least 90 days of cohort data, even if the rollout starts earlier.

A common pattern: run the A/B test for 6-8 weeks, make a rollout decision on the primary metric at that point, but reserve the right to roll back at 90 days if cohort retention reveals a problem.

## Holdout group

Even after rollout, maintain a small holdout (5-10%) on the old pricing for 90-180 days. The holdout serves two purposes:

1. **Causal attribution**: post-rollout, the world changes (marketing campaigns, seasonality, competitor moves). The holdout is the only way to attribute observed differences to the pricing change specifically.
2. **Insurance**: if a delayed-effect problem emerges (churn at 90 days), the holdout cohort gives you a clean baseline.

The holdout should be balanced demographically with the treatment to avoid attribution problems. Random assignment, no exclusions, no resampling.

## Mix-shift detection

Pricing changes attract different customer mixes. A "successful" test that shifts your customer mix toward lower-LTV segments is a long-term loss disguised as a short-term win.

Detect mix shifts by tracking pre-and-post composition on:

- **Acquisition channel**: organic, paid, referral, partner
- **Segment**: SMB, mid-market, enterprise
- **Geography**: by country or region
- **Plan tier**: distribution across tiers in the treatment vs control
- **Use case / industry**: if you capture firmographic data

If the treatment arm shifts toward (for example) 60% SMB / 40% mid-market while the control stays 50/50, the test is not just measuring price elasticity — it is measuring elasticity within a shifted customer mix. Decompose the effect:

```
total effect = price elasticity effect + mix shift effect
```

The cleanest way is to compute the metric separately within each segment, then average back to the population using the control's mix as the weighting. This isolates the pure price-elasticity effect from the mix-shift effect.

## Common pitfalls

### Optimizing the wrong metric

Conversion rate is the most-watched pricing metric. It is also the most-misleading: raising prices reduces conversion almost by definition, and so a conversion-rate-optimized test produces a "lower the price" recommendation. Optimize ARPU or LTV, not conversion.

### Short readout window

A test that runs for 2 weeks and shows a flat ARPU might be measuring noise. Pricing changes often show their effect at the 30-90 day mark when cohort dynamics surface.

### Peeking

Looking at results daily and stopping when significance is reached inflates the false-positive rate. Pre-register the readout date; do not look until then. If business pressure demands an interim check, use sequential testing methods (mSPRT, group sequential) rather than naive frequentist tests.

### Cross-contamination

If existing customers see the new pricing through any path (referral link, support agent, marketing email), the experiment is contaminated. Audit every customer-facing surface before launch.

### Single-arm test

Showing the new price to all new customers and comparing to historical baseline is not an A/B test. Time confounds the result. Random assignment to treatment and control simultaneously is required for causal inference.

### Power discipline collapse

When the team realizes the test is underpowered, the temptation is to extend the duration indefinitely. This works for stationary effects but exposes the test to time-varying confounders (seasonality, mix shift, market changes). Either accept underpowered status and rely on qualitative signal, or design a test with adequate sample at the outset.

### Confounded UX and pricing change

Redesigning the pricing page while also changing prices makes attribution impossible. Run pricing-change and UX-change experiments separately. If you must combine, plan a follow-up test on one variable holding the other constant.

### Customer support volume as a leading indicator

Pricing experiments that pass A/B significance can still fail if they generate a 5x spike in support tickets. Track support contact rate as a guardrail metric; a spike means the pricing page is confusing customers, regardless of the conversion delta.

## Decision framework: test, survey, or just decide

| You should test when | You should survey when | You should just decide when |
|---|---|---|
| Traffic supports adequate sample | Traffic too low for testing | You have strong prior data |
| Pricing change is reversible | Change is hard to A/B (regulated) | Change is forced (competitor move) |
| The hypothesis is bounded ($29 vs $39) | Many price points to evaluate | Decision is strategic, not tactical |
| Customers in the test won't be harmed by losing | Stated preference is acceptable | Cost of waiting is high |

Most pricing changes warrant a combination: survey to narrow the band, test the top 1-2 candidates, decide with the data.

## References

- Ronny Kohavi, Diane Tang, Ya Xu, *Trustworthy Online Controlled Experiments* (2020) — Chapter 18 specifically addresses pricing experiments
- Madhavan Ramanujam, *Monetizing Innovation* (2016)
- Stripe's published pricing experiment guidance — https://stripe.com/atlas/guides/pricing
