---
name: marketing-analyst
description: Expert marketing analytics covering campaign analysis, attribution modeling, marketing mix modeling, ROI measurement, and performance reporting.
version: 1.0.0
author: Claude Skills
category: marketing-growth
tags: [analytics, attribution, roi, campaigns, reporting]
---

# Marketing Analyst

Expert-level marketing analytics for data-driven decisions.

## Core Competencies

- Campaign performance analysis
- Attribution modeling
- Marketing mix modeling
- ROI measurement
- Customer analytics
- Channel optimization
- Forecasting
- Reporting and visualization

## Marketing Metrics Framework

### Acquisition Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| CPL (Cost per Lead) | Spend / Leads | Varies by industry |
| CAC (Customer Acquisition Cost) | S&M Spend / New Customers | LTV/CAC > 3:1 |
| CPA (Cost per Acquisition) | Spend / Acquisitions | Target specific |
| ROAS (Return on Ad Spend) | Revenue / Ad Spend | > 4:1 |

### Engagement Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Engagement Rate | Engagements / Impressions | 1-5% |
| Click-Through Rate | Clicks / Impressions | 0.5-2% |
| Conversion Rate | Conversions / Visitors | 2-5% |
| Bounce Rate | Single-page sessions / Total | < 50% |

### Retention Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Churn Rate | Lost Customers / Total | < 5% monthly |
| Retention Rate | 1 - Churn Rate | > 95% monthly |
| NRR (Net Revenue Retention) | (MRR - Churn + Expansion) / MRR | > 100% |
| LTV (Lifetime Value) | ARPU × Gross Margin × Lifetime | 3x+ CAC |

## Attribution Modeling

### Model Comparison

```python
import pandas as pd

def calculate_attribution(touchpoints, model='linear'):
    """
    Calculate attribution credit for each touchpoint

    touchpoints: List of touchpoint events
    model: 'first', 'last', 'linear', 'time_decay', 'position'
    """

    n = len(touchpoints)
    credits = {}

    if model == 'first':
        credits[touchpoints[0]] = 1.0

    elif model == 'last':
        credits[touchpoints[-1]] = 1.0

    elif model == 'linear':
        credit = 1.0 / n
        for tp in touchpoints:
            credits[tp] = credits.get(tp, 0) + credit

    elif model == 'time_decay':
        # More recent = more credit
        decay_rate = 0.7
        total_weight = sum([decay_rate ** i for i in range(n)])
        for i, tp in enumerate(reversed(touchpoints)):
            weight = (decay_rate ** i) / total_weight
            credits[tp] = credits.get(tp, 0) + weight

    elif model == 'position':
        # 40% first, 40% last, 20% middle
        if n == 1:
            credits[touchpoints[0]] = 1.0
        elif n == 2:
            credits[touchpoints[0]] = 0.5
            credits[touchpoints[-1]] = 0.5
        else:
            credits[touchpoints[0]] = 0.4
            credits[touchpoints[-1]] = 0.4
            middle_credit = 0.2 / (n - 2)
            for tp in touchpoints[1:-1]:
                credits[tp] = credits.get(tp, 0) + middle_credit

    return credits
```

### Attribution Report

```
┌─────────────────────────────────────────────────────────────┐
│               Attribution Analysis - [Period]                │
├─────────────────────────────────────────────────────────────┤
│  Model Comparison (Revenue Attribution)                      │
│                                                              │
│  Channel      First    Last    Linear   Position  Data-Driven│
│  Paid Search  $250K    $180K   $210K    $220K     $215K      │
│  Email        $120K    $200K   $160K    $165K     $170K      │
│  Social       $80K     $50K    $65K     $60K      $58K       │
│  Organic      $150K    $170K   $165K    $155K     $157K      │
├─────────────────────────────────────────────────────────────┤
│  Avg Touches to Conversion: 4.2                              │
│  Avg Days to Conversion: 18                                  │
│  Most Common Path: Paid → Email → Organic → Direct           │
└─────────────────────────────────────────────────────────────┘
```

## Campaign Analysis

### Campaign Performance Template

```markdown
# Campaign Analysis: [Campaign Name]

## Overview
- Type: [Type]
- Duration: [Dates]
- Budget: $[Amount]
- Spend: $[Amount]

## Performance Summary

| Metric | Target | Actual | vs Target |
|--------|--------|--------|-----------|
| Impressions | X | Y | +/-% |
| Clicks | X | Y | +/-% |
| Leads | X | Y | +/-% |
| MQLs | X | Y | +/-% |
| Pipeline | $X | $Y | +/-% |
| Revenue | $X | $Y | +/-% |

## Channel Breakdown

| Channel | Spend | Leads | CPL | Pipeline |
|---------|-------|-------|-----|----------|
| [Channel] | $X | Y | $Z | $W |

## Creative Performance

| Variant | Impressions | CTR | Conv Rate |
|---------|-------------|-----|-----------|
| A | X | Y% | Z% |
| B | X | Y% | Z% |

## Audience Insights

### Top Performing Segments
1. [Segment]: [Performance]
2. [Segment]: [Performance]

### Underperforming Segments
1. [Segment]: [Performance]

## Key Learnings
- [Learning 1]
- [Learning 2]

## Recommendations
1. [Recommendation]
2. [Recommendation]
```

### A/B Test Analysis

```python
from scipy import stats
import numpy as np

def analyze_ab_test(control_conversions, control_total,
                    treatment_conversions, treatment_total,
                    alpha=0.05):
    """
    Analyze A/B test results for statistical significance
    """
    # Conversion rates
    p_control = control_conversions / control_total
    p_treatment = treatment_conversions / treatment_total

    # Pooled probability
    p_pool = (control_conversions + treatment_conversions) / \
             (control_total + treatment_total)

    # Standard error
    se = np.sqrt(p_pool * (1 - p_pool) *
                 (1/control_total + 1/treatment_total))

    # Z-score
    z = (p_treatment - p_control) / se

    # P-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Lift
    lift = (p_treatment - p_control) / p_control

    return {
        'control_rate': p_control,
        'treatment_rate': p_treatment,
        'lift': lift,
        'lift_pct': lift * 100,
        'z_score': z,
        'p_value': p_value,
        'significant': p_value < alpha,
        'confidence': 1 - alpha
    }
```

## Marketing Mix Modeling

### MMM Framework

```
SALES = β₀ + β₁(TV) + β₂(Digital) + β₃(Print) + β₄(Seasonality) + ε

Components:
- Base: Organic demand without marketing
- TV: Television advertising impact
- Digital: Digital channels (paid, social)
- Print: Print advertising impact
- Seasonality: Time-based patterns
- Carryover: Delayed effects (adstock)

Outputs:
- Channel contribution to sales
- ROI by channel
- Optimal budget allocation
```

### Budget Optimization

```
┌─────────────────────────────────────────────────────────────┐
│            Budget Allocation Recommendation                  │
├─────────────────────────────────────────────────────────────┤
│  Channel        Current    Optimal    Change    Expected ROI │
│  Paid Search    30%        35%        +5%       4.2x         │
│  Social Paid    25%        20%        -5%       2.8x         │
│  Display        15%        10%        -5%       1.5x         │
│  Email          10%        15%        +5%       8.5x         │
│  Content        10%        12%        +2%       5.2x         │
│  Events         10%        8%         -2%       2.2x         │
├─────────────────────────────────────────────────────────────┤
│  Projected Impact: +15% pipeline with same budget            │
└─────────────────────────────────────────────────────────────┘
```

## Reporting

### Marketing Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│              Marketing Performance - [Month]                 │
├─────────────────────────────────────────────────────────────┤
│  ACQUISITION                                                 │
│  Visitors: 125K (+12%)   Leads: 5.2K (+8%)   CAC: $145 (-5%)│
├─────────────────────────────────────────────────────────────┤
│  PIPELINE                                                    │
│  MQLs: 823    SALs: 495    SQLs: 198    Pipeline: $2.4M     │
│  Conv: 15.8%  Conv: 60.1%  Conv: 40.0%  vs Goal: +108%      │
├─────────────────────────────────────────────────────────────┤
│  REVENUE                                                     │
│  Marketing Revenue: $580K    ROI: 5.2x    vs Goal: +115%    │
├─────────────────────────────────────────────────────────────┤
│  CHANNEL PERFORMANCE                                         │
│  [Bar chart by channel showing leads and pipeline]          │
├─────────────────────────────────────────────────────────────┤
│  TRENDS                                                      │
│  [Line chart showing key metrics over time]                 │
└─────────────────────────────────────────────────────────────┘
```

### Executive Summary Template

```markdown
# Marketing Performance: [Period]

## Headline
[One sentence summary of performance]

## Key Metrics
| Metric | Actual | Goal | Status |
|--------|--------|------|--------|
| Leads | X | Y | 🟢/🟡/🔴 |
| MQLs | X | Y | 🟢/🟡/🔴 |
| Pipeline | $X | $Y | 🟢/🟡/🔴 |
| Revenue | $X | $Y | 🟢/🟡/🔴 |

## Wins
- [Win 1]
- [Win 2]

## Challenges
- [Challenge 1]
- [Challenge 2]

## Next Period Focus
- [Focus area 1]
- [Focus area 2]
```

## Reference Materials

- `references/metrics.md` - Marketing metrics guide
- `references/attribution.md` - Attribution modeling
- `references/reporting.md` - Reporting best practices
- `references/forecasting.md` - Forecasting methods

## Scripts

```bash
# Campaign analyzer
python scripts/campaign_analyzer.py --data campaigns.csv --output report.html

# Attribution calculator
python scripts/attribution.py --touchpoints journeys.csv --model position

# ROI calculator
python scripts/roi_calculator.py --spend spend.csv --revenue revenue.csv

# Forecast generator
python scripts/forecast.py --historical data.csv --periods 6
```
