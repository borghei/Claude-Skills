---
name: sales-operations
description: >
  Expert sales operations covering CRM management, sales analytics, territory planning,
  compensation design, and process optimization. Use when building pipeline reports,
  designing territories, setting quotas, creating comp plans, or auditing CRM data quality.
version: 1.0.0
author: borghei
category: sales-success
tags: [sales-ops, crm, analytics, territory, compensation]
---

# Sales Operations

The agent operates as an expert sales operations professional, delivering revenue infrastructure through analytics, territory design, quota modeling, compensation architecture, and process optimization.

## Workflow

1. **Assess current state** -- Audit CRM data quality, pipeline coverage, and rep performance baselines. Validate that required fields are populated and stage dates are current.
2. **Analyze pipeline health** -- Calculate coverage ratios, stage conversion rates, velocity metrics, and deal aging. Flag bottlenecks where conversion drops below historical norms.
3. **Design or refine territories** -- Balance territories by opportunity potential, workload, and geographic/industry alignment. Score accounts to inform assignment.
4. **Model quotas** -- Run top-down (revenue target / capacity) and bottom-up (account potential analysis) models. Reconcile and risk-adjust.
5. **Architect compensation** -- Structure OTE splits, commission tiers, accelerators, and SPIFs aligned to company stage and selling motion.
6. **Build forecast** -- Categorize deals by confidence tier, apply probability weights, and surface the gap-to-quota with required win rates.
7. **Validate and iterate** -- Cross-check outputs against historical actuals. Confirm territory balance, quota fairness, and forecast accuracy before publishing.

## Sales Metrics Framework

**Activity Metrics:**

| Metric | Formula | Target |
|--------|---------|--------|
| Calls/Day | Total calls / Days | 50+ |
| Meetings/Week | Total meetings / Weeks | 15+ |
| Proposals/Month | Total proposals / Months | 8+ |

**Pipeline Metrics:**

| Metric | Formula | Target |
|--------|---------|--------|
| Pipeline Coverage | Pipeline / Quota | 3x+ |
| Pipeline Velocity | Won Deals / Avg Cycle Time | -- |
| Stage Conversion | Stage N+1 / Stage N | Varies |

**Outcome Metrics:**

| Metric | Formula | Target |
|--------|---------|--------|
| Win Rate | Won / (Won + Lost) | 25%+ |
| Average Deal Size | Revenue / Deals | Context-dependent |
| Sales Cycle | Avg days to close | <60 |
| Quota Attainment | Actual / Quota | 100%+ |

## Account Scoring

```python
def score_account(account):
    """Score accounts for territory assignment and prioritization."""
    score = 0

    # Company size (0-30 points)
    if account['employees'] > 5000:
        score += 30
    elif account['employees'] > 1000:
        score += 20
    elif account['employees'] > 200:
        score += 10

    # Industry fit (0-25 points)
    if account['industry'] in ['Technology', 'Finance']:
        score += 25
    elif account['industry'] in ['Healthcare', 'Manufacturing']:
        score += 15

    # Engagement (0-25 points)
    if account['website_visits'] > 10:
        score += 15
    if account['content_downloads'] > 0:
        score += 10

    # Intent signals (0-20 points)
    if account['intent_score'] > 80:
        score += 20
    elif account['intent_score'] > 50:
        score += 10

    return score  # Max 100; 70+ = Tier 1, 40-69 = Tier 2, <40 = Tier 3
```

## Territory Design

The agent balances territories across three dimensions:

- **Balance** -- Similar opportunity potential, comparable workload, fair distribution across reps.
- **Coverage** -- Geographic proximity, industry alignment, existing account relationships.
- **Growth** -- Room for expansion, career progression paths, untapped market potential.

### Example: Territory Allocation Table

| Territory | Rep | Accounts | ARR Potential | Quota | Coverage |
|-----------|-----|----------|---------------|-------|----------|
| West Enterprise | Rep A | 45 | $3.0M | $2.7M | 111% |
| East Mid-Market | Rep B | 62 | $2.8M | $2.4M | 117% |
| Central (Ramping) | Rep C | 38 | $2.5M | $1.2M | 208% |

## Quota Setting

### Top-Down Model

```
Company Revenue Target: $50M
  Growth Rate: 30%
  Team Capacity: 20 reps
  Average Quota: $2.5M
  Adjustments: +/-20% based on territory potential
```

### Bottom-Up Model

```
Account Potential Analysis:
  Existing accounts: $30M
  Pipeline value: $15M
  New logo potential: $10M
  Total: $55M
  Risk adjustment: -10%
  Final: $49.5M
```

The agent reconciles both models and flags divergence exceeding 10%.

## Compensation Architecture

```
TOTAL ON-TARGET EARNINGS (OTE)
  Base Salary: 50-60%
  Variable: 40-50%
    Commission: 80% of variable
      New Business: 60%
      Expansion: 40%
    Bonus: 20% of variable
      Quarterly accelerators
      SPIFs

COMMISSION RATE TIERS
  0-50% quota:   0.5x rate
  50-100% quota:  1.0x rate
  100-150% quota: 1.5x rate
  150%+ quota:    2.0x rate
```

## Forecasting

### Forecast Categories

| Category | Definition | Weighting |
|----------|------------|-----------|
| Closed | Signed contract | 100% |
| Commit | Verbal commit, high confidence | 90% |
| Best Case | Strong opportunity, likely to close | 50% |
| Pipeline | Active opportunity | 20% |
| Upside | Early stage | 5% |

### Example: Weighted Forecast Output

```
Q4 Forecast - Week 8
  Quota: $10M

  Category       Deals    Amount     Weighted
  Closed         12       $2.4M      $2.4M
  Commit         8        $1.8M      $1.6M
  Best Case      15       $3.2M      $1.6M
  Pipeline       22       $4.5M      $0.9M

  Forecast (Closed + Commit): $4.0M
  Upside (with Best Case): $5.6M
  Gap to Quota: $6.0M
  Required Win Rate on Pipeline: 35%
```

## CRM Data Quality Checklist

The agent validates these fields during every pipeline review:

- [ ] Required fields populated on all open opportunities
- [ ] Stage dates updated within the last 7 days
- [ ] Close dates set to realistic future dates (no past-due)
- [ ] Deal amounts reflect current pricing discussions
- [ ] Contact roles assigned with at least one economic buyer
- [ ] Next steps documented with specific actions and dates

## Process Optimization

### Sales Process Audit Framework

```
STAGE ANALYSIS
  Average time in stage -> identify stalls
  Conversion rate per stage -> find drop-off points
  Drop-off reasons -> categorize and address

ACTIVITY ANALYSIS
  Activities per stage -> benchmark against top performers
  Activity-to-outcome ratio -> measure efficiency
  Time allocation -> optimize selling vs. admin time

TOOL UTILIZATION
  CRM adoption rate -> target 95%+ daily login
  Feature usage -> identify underused capabilities
  Data quality score -> track completeness over time
  Automation opportunities -> reduce manual entry
```

## Scripts

```bash
# Pipeline analyzer
python scripts/pipeline_analyzer.py --data opportunities.csv

# Territory optimizer
python scripts/territory_optimizer.py --accounts accounts.csv --reps 10

# Quota calculator
python scripts/quota_calculator.py --target 50000000 --reps team.csv

# Forecast reporter
python scripts/forecast_report.py --quarter Q4 --output report.html
```

## Reference Materials

- `references/analytics.md` -- Sales analytics guide
- `references/territory.md` -- Territory planning
- `references/compensation.md` -- Comp design principles
- `references/forecasting.md` -- Forecasting methodology
