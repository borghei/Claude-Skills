---
name: sales-operations
description: >
  Expert sales operations covering CRM management, sales analytics, territory
  planning, compensation design, and process optimization. Use when building
  pipeline reports, designing territories, setting quotas, creating comp plans,
  or auditing CRM data quality.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: sales-success
  updated: 2026-03-31
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

## Troubleshooting

| Problem | Root Cause | Resolution |
|---------|-----------|------------|
| Forecast accuracy below 70% | Inconsistent stage definitions; reps over-committing; lack of weighted methodology | Enforce strict stage entry/exit criteria. Apply probability weights by category (Commit 90%, Best Case 50%, Pipeline 20%). Review commit deals individually in weekly forecast calls. Compare rolling 4-quarter actuals to calibrate weights. |
| Territory imbalance causing rep attrition | Uneven account distribution; potential-to-quota mismatch exceeding 20% | Re-score accounts quarterly using the scoring model. Target less than 15% variance in potential-to-quota ratio across territories. Review territory balance monthly in high-growth periods. |
| CRM data quality below 80% completeness | Insufficient enforcement; no automated validation; rep adoption gaps | Implement required field validation at stage transitions. Run weekly data quality reports. Tie CRM hygiene to variable compensation (5-10% of bonus). Target 95%+ daily login rate. |
| Quota attainment below 60% team-wide | Quotas set too aggressively; insufficient pipeline; ramp time underestimated | Reconcile top-down and bottom-up models. Flag divergence exceeding 10%. Risk-adjust for ramp (ramping reps at 50-75% quota). Ensure 3-4x pipeline coverage at quarter start. |
| Comp plan driving wrong behaviors | Misaligned incentives; rewarding volume over quality; no accelerators | Audit comp plans against strategic objectives. Ensure accelerators kick in at 100% attainment. Weight new business vs. expansion per GTM strategy. Add SPIFs for strategic priorities. |
| Pipeline coverage drops mid-quarter | Insufficient lead flow; deals pushed or lost faster than replaced | Alert AEs when individual coverage drops below 2.5x. Coordinate with Marketing on lead generation campaigns. Implement minimum weekly prospecting activity requirements. |
| Stage conversion rates declining | Process bottleneck; missing enablement; competitive pressure | Identify the specific stage with the highest drop-off. Compare top performer conversion rates to team average. Deploy targeted training on the bottleneck stage. Review competitive win/loss data for that stage. |

## Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Forecast accuracy | Within 10% of actual quarterly | Abs(Weighted Forecast - Actual) / Actual |
| Pipeline coverage ratio | 3-4x quota at quarter start | Total pipeline value / Team quota |
| CRM data completeness | 95%+ required fields populated | Weekly automated data quality audit |
| Territory balance | Less than 15% variance in potential-to-quota | Standard deviation of potential-to-quota ratio across territories |
| Quota attainment distribution | 60%+ of reps at or above quota | Reps at 100%+ / Total ramped reps |
| Stage conversion rates | Improving or stable QoQ | Stage N+1 entries / Stage N entries per period |
| Sales cycle length | Trending downward or stable | Average days from opportunity creation to close |
| Ramp time to productivity | Under 6 months for new hires | Months until new rep reaches 75% of quota run rate |
| Process adoption | 90%+ compliance with defined process | Audit score from monthly process compliance review |

## Scope & Limitations

**In Scope:**
- CRM administration, data quality management, and process enforcement
- Pipeline analytics: coverage ratios, stage conversion, velocity metrics, deal aging
- Territory design, account scoring, and balanced assignment optimization
- Quota modeling: top-down, bottom-up, and reconciliation approaches
- Compensation architecture: OTE splits, commission tiers, accelerators, SPIFs
- Forecast methodology: weighted pipeline, category-based, rolling forecasts
- Sales process audit: stage analysis, activity benchmarking, tool utilization
- Reporting infrastructure and dashboard design

**Out of Scope:**
- Individual deal strategy, qualification, and closing (see account-executive)
- Technical demos, RFP responses, and POC management (see sales-engineer)
- Post-sale customer management and retention (see customer-success-manager)
- Enterprise solution architecture and integration design (see solutions-architect)
- Marketing attribution modeling and campaign ROI (see marketing/campaign-analytics)
- Financial modeling beyond sales compensation (see finance)

**Limitations:**
- Territory optimization uses heuristic scoring, not mathematical optimization solvers; results are directional, not globally optimal
- Quota models require accurate historical data; garbage in, garbage out
- Forecast accuracy benchmarks assume consistent CRM hygiene; accuracy degrades with poor data quality
- Scripts process CSV/JSON exports only; no direct CRM API connectivity
- Compensation modeling does not account for tax implications or local labor law constraints

## Integration Points

| Integration | Direction | Purpose | Handoff Artifact |
|-------------|-----------|---------|-----------------|
| **Account Executive** | Ops -> AE | Territory assignments, quota targets, pipeline reports, forecast templates | Territory map, quota letter, pipeline dashboard, forecast submission form |
| **Sales Engineer** | Ops -> SE | Activity tracking, demo conversion metrics, technical win/loss data | SE activity reports, technical evaluation pipeline |
| **Customer Success Manager** | Ops -> CSM | Renewal pipeline tracking, expansion revenue attribution, churn reporting | Renewal forecast rollup, NRR reports, churn analysis |
| **Marketing** | Bidirectional | Lead attribution, MQL-to-SQL conversion, campaign ROI, pipeline sourcing | Attribution reports, lead routing rules, campaign pipeline reports |
| **Finance** | Ops -> Finance | Revenue forecasting, commission calculations, quota-to-capacity planning | Forecast submissions, commission statements, headcount models |
| **Revenue Operations** | Bidirectional | Cross-functional GTM metrics, funnel analytics, ARR reporting | Unified revenue dashboard, GTM efficiency metrics |
| **HR** | Ops -> HR | Headcount planning, ramp modeling, performance data for reviews | Ramp timelines, quota attainment reports, territory capacity models |

**Workflow Handoff Protocol:**
1. Sales Ops publishes territory assignments and quota letters at least 2 weeks before quarter start
2. Sales Ops delivers weekly pipeline report to sales leadership every Monday by 10 AM
3. Sales Ops collects forecast submissions from AEs every Friday and publishes rolled-up forecast by Monday
4. Sales Ops runs monthly territory health review and flags imbalances exceeding 15% variance

## Reference Materials

- `references/analytics.md` -- Sales analytics guide
- `references/territory.md` -- Territory planning
- `references/compensation.md` -- Comp design principles
- `references/forecasting.md` -- Forecasting methodology
