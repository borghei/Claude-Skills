---
name: growth-marketer
description: Expert growth marketing covering experimentation, funnel optimization, acquisition channels, retention strategies, and viral growth.
version: 1.0.0
author: Claude Skills
category: marketing-growth
tags: [growth, experimentation, acquisition, retention, viral]
---

# Growth Marketer

Expert-level growth marketing for scalable user acquisition.

## Core Competencies

- Growth experimentation
- Funnel optimization
- Acquisition channels
- Retention strategies
- Viral mechanics
- Data analytics
- A/B testing
- Growth modeling

## Growth Framework

### AARRR Funnel (Pirate Metrics)

```
ACQUISITION → ACTIVATION → RETENTION → REFERRAL → REVENUE

Acquisition: How do users find us?
├── Channels: SEO, Paid, Social, Content
├── Metrics: Traffic, CAC, Channel mix
└── Goal: Efficient user acquisition

Activation: Do users have a great first experience?
├── Triggers: Aha moment, value realization
├── Metrics: Activation rate, Time to value
└── Goal: 40%+ activation rate

Retention: Do users come back?
├── Drivers: Habit formation, value delivery
├── Metrics: D1/D7/D30 retention, Churn
└── Goal: Strong retention curves

Referral: Do users tell others?
├── Mechanisms: Invite systems, sharing
├── Metrics: Viral coefficient, NPS
└── Goal: K-factor > 0.5

Revenue: How do we make money?
├── Models: Subscription, Usage, Freemium
├── Metrics: ARPU, LTV, Conversion rate
└── Goal: LTV:CAC > 3:1
```

### North Star Metric

```markdown
NORTH STAR METRIC: [Metric Name]

Definition: [How it's calculated]

Why it matters:
1. Reflects customer value
2. Leads to revenue
3. Measurable
4. Actionable

Supporting Metrics:
├── Input 1: [Metric]
├── Input 2: [Metric]
└── Input 3: [Metric]

Current: [Value]
Target: [Value] by [Date]
```

## Experimentation

### Experiment Framework

```markdown
# Experiment: [Name]

## Hypothesis
If we [change], then [metric] will [increase/decrease] by [amount]
because [reasoning].

## Metrics
- Primary: [Metric]
- Secondary: [Metrics]
- Guardrails: [Metrics we don't want to hurt]

## Design
- Type: A/B / Multivariate / Holdout
- Sample: [Size calculation]
- Duration: [Days/Weeks]
- Segments: [User segments]

## Variants
- Control: [Description]
- Treatment A: [Description]
- Treatment B: [Description] (if applicable)

## Results
| Variant | Users | Conversion | Lift | Significance |
|---------|-------|------------|------|--------------|
| Control | X | Y% | - | - |
| Treatment | X | Y% | +Z% | 95% |

## Decision
[Ship / Iterate / Kill]

## Learnings
[What we learned]
```

### Statistical Significance

```python
# Sample size calculator
def sample_size(baseline_rate, mde, alpha=0.05, power=0.8):
    """
    baseline_rate: Current conversion rate
    mde: Minimum detectable effect (e.g., 0.1 for 10%)
    alpha: Significance level (0.05 = 95% confidence)
    power: Statistical power (0.8 = 80%)
    """
    from scipy import stats

    effect_size = mde * baseline_rate
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)

    n = 2 * ((z_alpha + z_beta) ** 2) * baseline_rate * (1 - baseline_rate) / (effect_size ** 2)
    return int(n)

# Example: 5% baseline, 10% MDE
# sample_size(0.05, 0.1) = ~31,000 per variant
```

### Experiment Prioritization (ICE)

| Experiment | Impact | Confidence | Ease | ICE Score |
|------------|--------|------------|------|-----------|
| [Exp 1] | 8 | 7 | 9 | 24 |
| [Exp 2] | 6 | 8 | 7 | 21 |
| [Exp 3] | 9 | 5 | 6 | 20 |

## Acquisition Channels

### Channel Analysis

| Channel | CAC | Volume | Quality | Scalability |
|---------|-----|--------|---------|-------------|
| Organic Search | $20 | High | High | Medium |
| Paid Search | $50 | Medium | High | High |
| Social Organic | $10 | Medium | Medium | Low |
| Social Paid | $40 | High | Medium | High |
| Content | $15 | Medium | High | Medium |
| Referral | $5 | Low | Very High | Medium |
| Partnerships | $30 | Medium | High | Medium |

### Channel Optimization

```markdown
## Channel: [Channel Name]

### Current Performance
- Spend: $[X]/month
- Users: [X]
- CAC: $[X]
- Quality Score: [X]/10

### Optimization Levers
1. [Lever 1]: [Current → Target]
2. [Lever 2]: [Current → Target]
3. [Lever 3]: [Current → Target]

### Experiments
- [Experiment 1]: [Hypothesis]
- [Experiment 2]: [Hypothesis]

### 90-Day Target
- CAC: $[X] → $[Y]
- Volume: [X] → [Y]
```

## Retention Strategies

### Retention Curves

```
DAY 1 RETENTION: 40%
DAY 7 RETENTION: 25%
DAY 30 RETENTION: 15%
DAY 90 RETENTION: 10%

Benchmarks (by category):
├── Social: D1 50%, D7 30%, D30 20%
├── E-commerce: D1 25%, D7 15%, D30 10%
├── SaaS: D1 60%, D7 40%, D30 30%
└── Games: D1 35%, D7 15%, D30 8%
```

### Retention Tactics

**Onboarding:**
- Progressive disclosure
- Personalized setup
- Quick wins
- Social proof

**Engagement:**
- Push notifications
- Email sequences
- In-app messages
- Feature education

**Re-engagement:**
- Win-back campaigns
- New feature announcements
- Special offers
- Community events

### Cohort Analysis

```
         Week 0  Week 1  Week 2  Week 3  Week 4
Jan W1   100%    45%     35%     28%     25%
Jan W2   100%    48%     38%     32%     28%
Jan W3   100%    52%     42%     35%     31%
Jan W4   100%    55%     45%     38%     34%

Insight: Improving week-over-week, likely due to
onboarding changes in Jan W3.
```

## Viral Growth

### Viral Coefficient (K-Factor)

```
K = i × c

i = number of invites per user
c = conversion rate of invites

Example:
i = 5 invites per user
c = 20% convert
K = 5 × 0.20 = 1.0

K > 1: Viral growth
K = 0.5-1: Viral boost
K < 0.5: Minimal viral
```

### Viral Loop Optimization

```
USER → MOTIVATE → INVITE → CONVERT → NEW USER

1. MOTIVATE: Why should users invite?
   - Intrinsic: Product is better with friends
   - Extrinsic: Rewards, credits, features

2. INVITE: Make it easy
   - Pre-written messages
   - Multiple channels
   - Low friction

3. CONVERT: Optimize landing
   - Social proof
   - Clear value prop
   - Easy sign-up
```

## Growth Modeling

### Growth Equation

```
New Users = Acquisition + Referrals - Churn

Monthly Growth Rate = (New Users - Churned Users) / Total Users

Sustainable Growth requires:
- Positive unit economics (LTV > CAC)
- Manageable churn (<5% monthly for SaaS)
- Scalable acquisition channels
```

### Forecast Model

```python
def growth_forecast(current_users, monthly_growth_rate, months):
    users = [current_users]
    for m in range(months):
        new_users = users[-1] * (1 + monthly_growth_rate)
        users.append(new_users)
    return users

# Example: 10,000 users, 10% monthly growth, 12 months
# Result: 31,384 users at month 12
```

## Reference Materials

- `references/experimentation.md` - A/B testing guide
- `references/acquisition.md` - Channel playbooks
- `references/retention.md` - Retention strategies
- `references/viral.md` - Viral mechanics

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
