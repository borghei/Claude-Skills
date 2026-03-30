---
name: marketing-analyst
description: >
  Expert marketing analytics covering campaign analysis, attribution modeling,
  marketing mix modeling, ROI measurement, and performance reporting. Use when
  analyzing campaign ROI, comparing attribution models, optimizing marketing
  budget allocation, building executive dashboards, or running A/B test
  statistical analysis.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing-growth
  updated: 2026-03-31
  tags: [analytics, attribution, roi, campaigns, reporting]
---
# Marketing Analyst

The agent operates as a senior marketing analyst, delivering campaign performance analysis, multi-touch attribution, marketing mix modeling, ROI measurement, and data-driven budget optimization.

## Workflow

1. **Define measurement objectives** - Identify which campaigns, channels, or initiatives require analysis. Confirm KPIs (CPL, CAC, ROAS, pipeline, revenue). Checkpoint: every KPI has a target and a data source.
2. **Collect and validate data** - Pull campaign data from ad platforms, CRM, and analytics tools. Validate completeness and consistency. Checkpoint: no channel has >5% missing data.
3. **Run attribution analysis** - Apply multiple attribution models (first-touch, last-touch, linear, time-decay, position-based) and compare channel credit allocation. Checkpoint: results are compared across at least 3 models.
4. **Analyze campaign performance** - Calculate ROI, ROAS, CPL, CAC, and conversion rates per campaign. Identify top and bottom performers. Checkpoint: performance table includes target vs. actual for every metric.
5. **Optimize budget allocation** - Use marketing mix modeling or ROI data to recommend budget shifts. Checkpoint: reallocation recommendations are backed by expected ROI per channel.
6. **Build executive report** - Summarize headline metrics, wins, challenges, and next-period focus. Checkpoint: report passes the "so what" test (every data point has an actionable insight).

## Marketing Metrics Reference

### Acquisition Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| CPL | Spend / Leads | Varies by industry |
| CAC | S&M Spend / New Customers | LTV/CAC > 3:1 |
| CPA | Spend / Acquisitions | Target specific |
| ROAS | Revenue / Ad Spend | > 4:1 |

### Engagement Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Engagement Rate | Engagements / Impressions | 1-5% |
| CTR | Clicks / Impressions | 0.5-2% |
| Conversion Rate | Conversions / Visitors | 2-5% |
| Bounce Rate | Single-page sessions / Total | < 50% |

### Retention Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Churn Rate | Lost Customers / Total | < 5% monthly |
| NRR | (MRR - Churn + Expansion) / MRR | > 100% |
| LTV | ARPU x Gross Margin x Lifetime | 3x+ CAC |

## Attribution Modeling

### Model Comparison

The agent should apply multiple models and compare results to identify channel over/under-valuation:

| Model | Logic | Best For |
|-------|-------|----------|
| First-touch | 100% credit to first interaction | Measuring awareness channels |
| Last-touch | 100% credit to final interaction | Measuring conversion channels |
| Linear | Equal credit across all touches | Balanced view of full journey |
| Time-decay | More credit to recent touches | Short sales cycles |
| Position-based | 40% first, 40% last, 20% middle | Most B2B scenarios |

### Attribution Calculator

```python
def calculate_attribution(touchpoints, model='position'):
    """Calculate attribution credit for a conversion journey.

    Args:
        touchpoints: List of channel names in order of interaction
        model: One of 'first', 'last', 'linear', 'time_decay', 'position'

    Returns:
        Dict mapping channel -> credit (sums to 1.0)

    Example:
        >>> calculate_attribution(['paid_search', 'email', 'organic', 'direct'], 'position')
        {'paid_search': 0.4, 'email': 0.1, 'organic': 0.1, 'direct': 0.4}
    """
    n = len(touchpoints)
    credits = {}

    if model == 'first':
        credits[touchpoints[0]] = 1.0
    elif model == 'last':
        credits[touchpoints[-1]] = 1.0
    elif model == 'linear':
        for tp in touchpoints:
            credits[tp] = credits.get(tp, 0) + 1.0 / n
    elif model == 'time_decay':
        decay = 0.7
        total = sum(decay ** i for i in range(n))
        for i, tp in enumerate(reversed(touchpoints)):
            credits[tp] = credits.get(tp, 0) + (decay ** i) / total
    elif model == 'position':
        if n == 1:
            credits[touchpoints[0]] = 1.0
        elif n == 2:
            credits[touchpoints[0]] = 0.5
            credits[touchpoints[-1]] = credits.get(touchpoints[-1], 0) + 0.5
        else:
            credits[touchpoints[0]] = 0.4
            credits[touchpoints[-1]] = credits.get(touchpoints[-1], 0) + 0.4
            for tp in touchpoints[1:-1]:
                credits[tp] = credits.get(tp, 0) + 0.2 / (n - 2)

    return credits
```

## Example: Campaign Analysis Report

```markdown
# Campaign Analysis: Q1 2026 Product Launch

## Performance Summary
| Metric       | Target  | Actual  | vs Target |
|--------------|---------|---------|-----------|
| Impressions  | 500K    | 612K    | +22%      |
| Clicks       | 25K     | 28.4K   | +14%      |
| Leads        | 1,200   | 1,350   | +13%      |
| MQLs         | 360     | 410     | +14%      |
| Pipeline     | $1.2M   | $1.45M  | +21%      |
| Revenue      | $380K   | $425K   | +12%      |

## Channel Breakdown
| Channel      | Spend   | Leads | CPL   | Pipeline |
|--------------|---------|-------|-------|----------|
| Paid Search  | $45K    | 520   | $87   | $580K    |
| LinkedIn Ads | $30K    | 310   | $97   | $420K    |
| Email        | $5K     | 380   | $13   | $350K    |
| Content/SEO  | $8K     | 140   | $57   | $100K    |

## Key Insight
Email delivers lowest CPL ($13) and strong pipeline. Recommend shifting
10% of LinkedIn budget to email nurture sequences for Q2.
```

## Budget Optimization Framework

```
Budget Allocation Recommendation
  Channel        Current    Optimal    Change    Expected ROI
  Paid Search    30%        35%        +5%       4.2x
  Social Paid    25%        20%        -5%       2.8x
  Display        15%        10%        -5%       1.5x
  Email          10%        15%        +5%       8.5x
  Content        10%        12%        +2%       5.2x
  Events         10%        8%         -2%       2.2x

  Projected Impact: +15% pipeline with same budget
```

## A/B Test Statistical Analysis

```python
from scipy import stats
import numpy as np

def analyze_ab_test(control_conv, control_total, treatment_conv, treatment_total, alpha=0.05):
    """Analyze A/B test for statistical significance.

    Example:
        >>> result = analyze_ab_test(150, 5000, 195, 5000)
        >>> result['significant']
        True
        >>> f"{result['lift_pct']:.1f}%"
        '30.0%'
    """
    p_c = control_conv / control_total
    p_t = treatment_conv / treatment_total
    p_pool = (control_conv + treatment_conv) / (control_total + treatment_total)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/control_total + 1/treatment_total))
    z = (p_t - p_c) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    return {
        'control_rate': p_c,
        'treatment_rate': p_t,
        'lift_pct': ((p_t - p_c) / p_c) * 100,
        'p_value': p_value,
        'significant': p_value < alpha,
    }
```

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

## Reference Materials

- `references/metrics.md` - Marketing metrics guide
- `references/attribution.md` - Attribution modeling
- `references/reporting.md` - Reporting best practices
- `references/forecasting.md` - Forecasting methods

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Attribution models give wildly different channel credit allocations | No single model captures full truth; each has structural bias | Run 3+ models (first-touch, last-touch, position-based) and compare; use position-based as default for B2B |
| ROAS calculations look great but pipeline is flat | Revenue attribution counting existing customers, not new pipeline | Separate new business attribution from expansion; report pipeline separately from revenue |
| Marketing reports and sales reports show different lead counts | Marketing counts MQLs at form fill, sales counts at CRM entry with different criteria | Align on shared definitions: document exact MQL, SQL, and opportunity criteria in a shared SLA |
| Forecast consistently over-predicts by 20%+ | Model uses linear extrapolation without accounting for seasonality or saturation | Apply dampening factors for longer forecasts; use ensemble method (linear + growth rate + moving average) |
| Executive dashboard takes too long to build each month | Manual data pulls from 5+ platforms with different schemas | Automate data collection; standardize UTM and naming conventions so cross-platform analysis is consistent |
| Channel ROI is negative but still generating pipeline | Long B2B sales cycle means revenue attribution has not caught up to spend | Use pipeline-based attribution for channels with 3+ month sales cycles rather than closed-won revenue |

---

## Success Criteria

- Multi-touch attribution model deployed comparing 3+ models with documented channel credit differences
- Monthly marketing report delivered within 3 business days of month close
- Budget reallocation recommendations backed by per-channel ROI data and implemented quarterly
- Forecast accuracy within 15% of actual for 3-month projections
- Campaign performance reports include target vs actual for every KPI
- Every data point in executive reports has an actionable insight (passes "so what" test)
- Channel data completeness above 95% (no channel has >5% missing data)

---

## Scope & Limitations

**In Scope:** Campaign performance analysis, multi-touch attribution modeling, marketing mix optimization, ROI/ROAS calculation, budget allocation recommendations, executive reporting, cohort retention analysis, marketing forecasting.

**Out of Scope:** Analytics implementation and tracking setup (see analytics-tracking skill), product analytics (see product-team skills), financial modeling beyond marketing metrics (see finance skill), data engineering and warehouse management.

**Limitations:** Attribution models are approximations — no model perfectly captures the buyer journey, especially for high-touch B2B sales. Forecasting uses historical extrapolation with dampening; it does not account for market disruptions or competitive moves. Budget optimization assumes linear channel scaling; most channels have diminishing returns at scale.

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/channel_mix_optimizer.py` | Analyze channel performance and recommend optimal budget allocation | `python scripts/channel_mix_optimizer.py channels.json --budget 100000 --demo` |
| `scripts/cohort_analyzer.py` | Analyze user retention by cohort, identify trends and best/worst performers | `python scripts/cohort_analyzer.py cohort_data.json --demo` |
| `scripts/marketing_forecast_generator.py` | Generate marketing forecasts using linear, growth rate, and ensemble methods | `python scripts/marketing_forecast_generator.py historical.json --periods 6` |
