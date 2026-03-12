---
name: growth-marketer
description: >
  Expert growth marketing covering experimentation, funnel optimization, acquisition channels, retention strategies, and viral growth.
  Use when designing A/B experiments, optimizing AARRR funnel stages, calculating viral coefficients, building growth models, or prioritizing acquisition channels by CAC and LTV.
version: 1.0.0
author: borghei
category: marketing-growth
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
