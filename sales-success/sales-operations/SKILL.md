---
name: sales-operations
description: Expert sales operations covering CRM management, sales analytics, territory planning, compensation design, and process optimization.
version: 1.0.0
author: Claude Skills
category: sales-success
tags: [sales-ops, crm, analytics, territory, compensation]
---

# Sales Operations

Expert-level sales operations for revenue optimization.

## Core Competencies

- CRM administration
- Sales analytics
- Territory planning
- Quota setting
- Compensation design
- Process optimization
- Forecasting
- Sales enablement

## Sales Analytics

### Key Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│               Sales Performance - [Period]                   │
├─────────────────────────────────────────────────────────────┤
│  Revenue          Pipeline         Win Rate      Cycle Time  │
│  $2.4M            $8.2M            28%           45 days     │
│  vs Quota: 102%   Coverage: 3.4x   vs LQ: +3%   vs LQ: -5d  │
├─────────────────────────────────────────────────────────────┤
│  PIPELINE BY STAGE                                           │
│  Prospect:    $1.2M (15%)  ████                             │
│  Discovery:   $2.1M (26%)  ███████                          │
│  Demo:        $2.8M (34%)  █████████                        │
│  Proposal:    $1.5M (18%)  █████                            │
│  Negotiation: $0.6M (7%)   ██                               │
├─────────────────────────────────────────────────────────────┤
│  REP PERFORMANCE                                             │
│  Rep A: $520K (115%)  Rep B: $480K (107%)  Rep C: $420K (93%)│
└─────────────────────────────────────────────────────────────┘
```

### Sales Metrics Framework

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
| Pipeline Velocity | Won Deals / Avg Cycle Time | - |
| Stage Conversion | Stage N+1 / Stage N | Varies |

**Outcome Metrics:**
| Metric | Formula | Target |
|--------|---------|--------|
| Win Rate | Won / (Won + Lost) | 25%+ |
| Average Deal Size | Revenue / Deals | $[X] |
| Sales Cycle | Avg days to close | <60 |
| Quota Attainment | Actual / Quota | 100%+ |

## Territory Planning

### Territory Design Principles

**Balance:**
- Similar opportunity potential
- Comparable workload
- Fair distribution

**Coverage:**
- Geographic proximity
- Industry alignment
- Account relationships

**Growth:**
- Room for expansion
- Career progression
- Market potential

### Territory Model

```markdown
# Territory Plan: [Region/Segment]

## Overview
- Total accounts: [Number]
- Total ARR potential: $[Amount]
- Rep count: [Number]

## Territory Assignment

### Territory 1: [Name]
- Rep: [Name]
- Accounts: [Number]
- ARR Potential: $[Amount]
- Named accounts: [List]
- Geographic coverage: [Area]

### Territory 2: [Name]
...

## Metrics by Territory

| Territory | Accounts | Potential | Quota | Coverage |
|-----------|----------|-----------|-------|----------|
| [T1] | X | $Y | $Z | W% |

## Rules of Engagement
- Account ownership: [Rules]
- Lead routing: [Rules]
- Splits: [Rules]
```

### Account Scoring

```python
def score_account(account):
    """
    Score accounts for territory assignment and prioritization
    """
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

    return score
```

## Quota Setting

### Quota Methodology

**Top-Down:**
```
Company Revenue Target: $50M
├── Growth Rate: 30%
├── Team Capacity: 20 reps
├── Average Quota: $2.5M
└── Adjustments: ±20% based on territory
```

**Bottom-Up:**
```
Account Potential Analysis:
├── Existing accounts: $30M
├── Pipeline value: $15M
├── New logo potential: $10M
├── Total: $55M
└── Risk adjustment: -10%
Final: $49.5M
```

### Quota Allocation

| Rep | Territory Potential | Historical | Ramp | Final Quota |
|-----|---------------------|------------|------|-------------|
| Rep A | $3M | 110% | Full | $2.7M |
| Rep B | $2.8M | 95% | Full | $2.4M |
| Rep C | $2.5M | N/A | 50% | $1.2M |

## Compensation Design

### Compensation Structure

```
TOTAL ON-TARGET EARNINGS (OTE)
├── Base Salary: 50-60%
└── Variable: 40-50%
    ├── Commission: 80%
    │   ├── New Business: 60%
    │   └── Expansion: 40%
    └── Bonus: 20%
        ├── Quarterly accelerators
        └── SPIFs

COMMISSION RATE
├── 0-50% quota: 0.5x rate
├── 50-100% quota: 1x rate
├── 100-150% quota: 1.5x rate
└── 150%+ quota: 2x rate
```

### Comp Plan Template

```markdown
# Sales Compensation Plan: [Role]

## Plan Overview
- Role: [Role Name]
- OTE: $[Amount]
- Base/Variable Split: [X/Y]%
- Pay Period: [Frequency]

## Commission Structure

### New Business
- Rate: [X]% of ACV
- Accelerators:
  - 100-120%: 1.2x multiplier
  - 120%+: 1.5x multiplier

### Renewal/Expansion
- Rate: [Y]% of ACV
- Expansion: Same as new business
- Renewal: Reduced rate

## Quota
- Annual: $[Amount]
- Quarterly: $[Amount]
- Ramped: [If applicable]

## Payment Terms
- Commission paid: [Timing]
- Clawback period: [Duration]
- Draw: [If applicable]

## Special Incentives
- [SPIF 1]: [Details]
- [SPIF 2]: [Details]
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

### Forecast Report

```
┌─────────────────────────────────────────────────────────────┐
│                  Q4 Forecast - Week 8                        │
├─────────────────────────────────────────────────────────────┤
│  Quota: $10M                                                 │
│                                                              │
│  Category       Deals    Amount     Weighted                 │
│  Closed         12       $2.4M      $2.4M                   │
│  Commit         8        $1.8M      $1.6M                   │
│  Best Case      15       $3.2M      $1.6M                   │
│  Pipeline       22       $4.5M      $0.9M                   │
│  ─────────────────────────────────────────────              │
│  Weighted Total          $11.9M     $6.5M                   │
├─────────────────────────────────────────────────────────────┤
│  Forecast: $4.0M (Closed + Commit)                          │
│  Upside: $5.6M (with Best Case)                             │
│  Gap to Quota: $6.0M                                        │
│  Required Win Rate on Pipeline: 35%                         │
└─────────────────────────────────────────────────────────────┘
```

## Process Optimization

### Sales Process Audit

```
STAGE ANALYSIS
├── Average time in stage
├── Conversion rate
├── Drop-off reasons
└── Bottleneck identification

ACTIVITY ANALYSIS
├── Activities per stage
├── Activity to outcome ratio
├── Time allocation
└── Best rep practices

TOOL UTILIZATION
├── CRM adoption
├── Feature usage
├── Data quality
└── Automation opportunities
```

### CRM Hygiene

**Data Quality Checks:**
- [ ] Required fields populated
- [ ] Stage dates updated
- [ ] Close dates realistic
- [ ] Deal amounts accurate
- [ ] Contact roles assigned
- [ ] Next steps documented

## Reference Materials

- `references/analytics.md` - Sales analytics guide
- `references/territory.md` - Territory planning
- `references/compensation.md` - Comp design principles
- `references/forecasting.md` - Forecasting methodology

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
