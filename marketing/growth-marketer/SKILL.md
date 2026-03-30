---
name: growth-marketer
description: >
  Expert growth marketing covering experimentation, funnel optimization,
  acquisition channels, retention strategies, and viral growth. Use when
  designing A/B experiments, optimizing AARRR funnel stages, calculating viral
  coefficients, building growth models, or prioritizing acquisition channels by
  CAC and LTV.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing-growth
  updated: 2026-03-31
  tags: [growth, experimentation, acquisition, retention, viral]
---
# Growth Marketer

The agent operates as a senior growth marketer, delivering experiment-driven strategies for scalable user acquisition, activation, retention, referral, and revenue optimization.

## Workflow

1. **Define North Star Metric** - Identify the single metric that reflects customer value and leads to revenue. Checkpoint: the metric must be measurable, actionable, and correlated with retention.
2. **Map the AARRR funnel** - Quantify current performance at each stage (Acquisition, Activation, Retention, Referral, Revenue). Checkpoint: every stage has a baseline number and a target.
3. **Identify biggest lever** - Find the funnel stage with the largest drop-off or lowest performance vs. benchmark. This becomes the focus area.
4. **Design experiments** - Write hypotheses using the format: "If we [change], then [metric] will [direction] by [amount] because [reasoning]." Prioritize using ICE scoring.
5. **Calculate sample size and run** - Determine required sample per variant for statistical significance (95% confidence, 80% power). Launch the experiment.
6. **Analyze results** - Evaluate lift, p-value, and guardrail metrics. Decision: Ship, Iterate, or Kill.
7. **Model growth trajectory** - Forecast user growth incorporating acquisition rate, churn, and viral coefficient. Validate that LTV:CAC > 3:1 for sustainability.

## AARRR Funnel (Pirate Metrics)

| Stage | Key Question | Metrics | Benchmark |
|-------|-------------|---------|-----------|
| Acquisition | How do users find us? | Traffic, CAC, channel mix | CAC < 1/3 LTV |
| Activation | Great first experience? | Activation rate, time to value | 40%+ activation |
| Retention | Do users come back? | D1/D7/D30 retention, churn | SaaS: D30 30% |
| Referral | Do users tell others? | Viral coefficient (K), NPS | K-factor > 0.5 |
| Revenue | How do we monetize? | ARPU, LTV, conversion rate | LTV:CAC > 3:1 |

## Experimentation Framework

### Experiment Document Template

```markdown
# Experiment: Onboarding Checklist v2

## Hypothesis
If we add a progress bar to the onboarding checklist, then activation rate
will increase by 15% because users respond to completion motivation.

## Metrics
- Primary: 7-day activation rate
- Secondary: Time to first value action
- Guardrails: Support ticket volume, bounce rate

## Design
- Type: A/B test
- Sample: 8,200 per variant (5% baseline, 15% MDE, 95% confidence)
- Duration: 14 days
- Segments: New signups only

## Results
| Variant   | Users  | Activation | Lift  | p-value |
|-----------|--------|------------|-------|---------|
| Control   | 8,350  | 5.1%       | -     | -       |
| Treatment | 8,280  | 6.2%       | +21%  | 0.003   |

## Decision: Ship
```

### ICE Prioritization

| Experiment | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Score |
|------------|---------------|-------------------|-------------|-----------|
| Onboarding checklist v2 | 8 | 7 | 9 | 24 |
| Referral incentive test | 6 | 8 | 7 | 21 |
| Pricing page redesign | 9 | 5 | 6 | 20 |

### Sample Size Calculator

```python
from scipy import stats

def sample_size(baseline_rate, mde, alpha=0.05, power=0.8):
    """Calculate required sample size per variant for an A/B test.

    Args:
        baseline_rate: Current conversion rate (e.g. 0.05 for 5%)
        mde: Minimum detectable effect as proportion (e.g. 0.15 for 15% lift)
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.8)

    Returns:
        Required users per variant (int)

    Example:
        >>> sample_size(0.05, 0.15)
        8218
    """
    effect_size = mde * baseline_rate
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) ** 2) * baseline_rate * (1 - baseline_rate) / (effect_size ** 2)
    return int(n)
```

## Acquisition Channel Analysis

| Channel | CAC | Volume | Quality | Scalability |
|---------|-----|--------|---------|-------------|
| Organic Search | $20 | High | High | Medium |
| Paid Search | $50 | Medium | High | High |
| Social Organic | $10 | Medium | Medium | Low |
| Social Paid | $40 | High | Medium | High |
| Content | $15 | Medium | High | Medium |
| Referral | $5 | Low | Very High | Medium |
| Partnerships | $30 | Medium | High | Medium |

## Retention Benchmarks

| Category | D1 | D7 | D30 |
|----------|-----|-----|------|
| SaaS | 60% | 40% | 30% |
| Social | 50% | 30% | 20% |
| E-commerce | 25% | 15% | 10% |
| Games | 35% | 15% | 8% |

### Cohort Analysis Example

```
         Week 0  Week 1  Week 2  Week 3  Week 4
Jan W1   100%    45%     35%     28%     25%
Jan W2   100%    48%     38%     32%     28%
Jan W3   100%    52%     42%     35%     31%
Jan W4   100%    55%     45%     38%     34%

Insight: Week-over-week improvement correlates with onboarding
changes shipped in Jan W3.
```

## Viral Growth

**K-Factor** = invites per user (i) x conversion rate of invites (c)

- K > 1: True viral growth (each user brings >1 new user)
- K = 0.5-1: Viral boost (amplifies paid acquisition)
- K < 0.5: Minimal viral effect

## Growth Forecast Model

```python
def growth_forecast(current_users, monthly_growth_rate, months):
    """Forecast user base over time with compound growth.

    Example:
        >>> growth_forecast(10000, 0.10, 12)[-1]
        31384
    """
    users = [current_users]
    for _ in range(months):
        users.append(int(users[-1] * (1 + monthly_growth_rate)))
    return users
```

## Scripts

```bash
# Experiment analyzer
python scripts/experiment_analyzer.py --experiment exp_001 --data results.csv

# Funnel analyzer
python scripts/funnel_analyzer.py --events events.csv --output funnel.html

# Cohort generator
python scripts/cohort_generator.py --users users.csv --metric retention

# Growth model
python scripts/growth_model.py --current 10000 --growth 0.1 --months 12
```

## Reference Materials

- `references/experimentation.md` - A/B testing guide
- `references/acquisition.md` - Channel playbooks
- `references/retention.md` - Retention strategies
- `references/viral.md` - Viral mechanics

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| K-factor below 0.1 despite referral program | Invite UX has too much friction or incentive misaligned with user value | Reduce invite flow to one click; align incentive with product value (usage credits > cash) |
| Activation rate below 20% for new signups | Time-to-value too long or onboarding not guiding users to aha moment | Map activation events, identify first value action, build guided onboarding to reach it in under 5 minutes |
| Growth stalls after initial PLG ramp | Free tier captures low-intent users who never convert; paid conversion rate below 3% | Tighten free tier limits around high-value features, add contextual upgrade prompts at usage gates |
| A/B test results not reaching significance | Sample size too small for the minimum detectable effect being tested | Use sample size calculator; increase traffic to test or accept larger MDE |
| Cohort retention curves flatten at under 15% | Product does not build enough habit; no ongoing value loop | Implement engagement hooks (notifications, reports, streaks); investigate which features drive retention |
| Experiments consistently show no lift | Testing cosmetic changes rather than meaningful value propositions | Focus experiments on activation flow, pricing, and value communication — not button colors |

---

## Success Criteria

- North Star Metric identified, measurable, and reviewed weekly with cross-functional team
- Activation rate above 40% for new signups within first 7 days
- LTV:CAC ratio sustained above 3:1 across all acquisition channels
- K-factor above 0.5, providing meaningful viral amplification of paid acquisition
- Experiment velocity of 2+ tests per sprint with documented hypotheses and outcomes
- D30 retention at or above SaaS benchmark (30%) for primary user segment
- Growth model accurately forecasts within 15% of actual for 3-month projections

---

## Scope & Limitations

**In Scope:** AARRR funnel optimization, experiment design and prioritization (ICE/RICE), viral growth modeling, PLG strategy, retention analysis, cohort analysis, growth forecasting, acquisition channel analysis, sample size calculation.

**Out of Scope:** Brand strategy (see brand-strategist skill), content creation (see content-creator skill), paid ad campaign management (see paid-ads skill), product design and engineering implementation, pricing strategy.

**Limitations:** Growth loop models use simplified compound growth assumptions — real growth has diminishing returns and market saturation effects. Viral coefficient calculations assume uniform user behavior; actual viral spread varies by segment. Sample size calculator uses normal approximation; for very low conversion rates, exact tests may be needed.

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/growth_loop_modeler.py` | Model viral, PLG, and content growth loops with forecasts | `python scripts/growth_loop_modeler.py --type viral --users 1000 --k-factor 0.6 --months 12` |
| `scripts/viral_coefficient_calculator.py` | Calculate K-factor, branching factor, and improvement scenarios | `python scripts/viral_coefficient_calculator.py --invites 5000 --conversions 800 --users 2000` |
| `scripts/experiment_prioritizer.py` | Prioritize growth experiments using ICE or RICE scoring | `python scripts/experiment_prioritizer.py experiments.json --framework ice --demo` |
