---
name: saas-metrics-coach
description: >
  This skill should be used when the user asks to "calculate MRR", "analyze churn",
  "compute SaaS metrics", "do cohort retention analysis", "calculate LTV or CAC",
  "evaluate unit economics", or "track subscription revenue growth".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: finance
  domain: saas-metrics
  updated: 2026-04-02
  tags: [saas, mrr, arr, churn, cohort-analysis, ltv, cac, unit-economics]
---
# SaaS Metrics Coach Skill

## Overview

Production-ready SaaS metrics toolkit for calculating MRR/ARR, analyzing cohort retention, and evaluating unit economics. Designed for SaaS founders, finance teams, and growth operators who need precise subscription revenue analysis without spreadsheet gymnastics.

## Quick Start

```bash
# Calculate MRR, ARR, growth rate, and churn from subscription data
python scripts/mrr_calculator.py subscriptions.csv

# Run cohort retention analysis
python scripts/cohort_analyzer.py users.csv --cohort-period monthly

# Calculate LTV, CAC, LTV:CAC ratio, and payback period
python scripts/unit_economics.py metrics.json
```

## Tools Overview

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `mrr_calculator.py` | MRR, ARR, growth rate, churn | CSV with subscription data | Revenue metrics + trends |
| `cohort_analyzer.py` | Cohort retention analysis | CSV with user signup/activity data | Retention matrix + curves |
| `unit_economics.py` | LTV, CAC, LTV:CAC, payback | JSON with acquisition/revenue data | Unit economics dashboard |

## Workflows

### Workflow 1: Monthly SaaS Health Check

1. Export subscription data as CSV (columns: customer_id, plan, mrr, start_date, end_date)
2. Run `mrr_calculator.py` to get current MRR, ARR, net new MRR, churn rate
3. Run `cohort_analyzer.py` on user activity data to identify retention trends
4. Run `unit_economics.py` to validate LTV:CAC ratio stays above 3:1
5. Review output for warning flags (churn > 5%, LTV:CAC < 3, payback > 18 months)

### Workflow 2: Investor Deck Preparation

1. Run `mrr_calculator.py --format json` to get growth metrics for charts
2. Run `cohort_analyzer.py --format json` for retention curves
3. Run `unit_economics.py --format json` for unit economics summary
4. Use JSON output to populate investor deck data points

### Workflow 3: Churn Investigation

1. Run `mrr_calculator.py` with `--breakdown` to see churn by plan tier
2. Run `cohort_analyzer.py` to identify which cohorts churn fastest
3. Cross-reference cohort drop-off periods with product changes
4. Identify if churn is concentrated in specific segments or time windows

## Reference Documentation

### Key SaaS Metrics Definitions

- **MRR (Monthly Recurring Revenue):** Sum of all active subscription revenue normalized to monthly
- **ARR (Annual Recurring Revenue):** MRR x 12
- **Net New MRR:** New MRR + Expansion MRR - Churned MRR - Contraction MRR
- **Gross Churn Rate:** Lost MRR / Beginning MRR for the period
- **Net Revenue Retention (NRR):** (Beginning MRR + Expansion - Churn - Contraction) / Beginning MRR
- **LTV (Lifetime Value):** ARPU / Monthly Churn Rate (simplified) or ARPU x Gross Margin / Churn
- **CAC (Customer Acquisition Cost):** Total Sales & Marketing Spend / New Customers Acquired
- **LTV:CAC Ratio:** Target 3:1 or higher for healthy SaaS
- **CAC Payback Period:** CAC / (ARPU x Gross Margin) in months

See `references/saas-metrics-guide.md` for comprehensive framework details.

## Common Patterns

### Pattern: Subscription CSV Format
```csv
customer_id,plan,mrr,start_date,end_date,status
C001,pro,99.00,2025-01-15,,active
C002,basic,29.00,2025-02-01,2025-08-15,churned
C003,enterprise,499.00,2025-03-10,,active
```

### Pattern: User Activity CSV Format
```csv
user_id,signup_date,last_active_date,activity_month
U001,2025-01-05,2025-06-15,2025-06
U002,2025-01-12,2025-03-20,2025-03
```

### Pattern: Unit Economics JSON Format
```json
{
  "period": "2025-Q4",
  "total_customers": 1200,
  "new_customers": 150,
  "churned_customers": 45,
  "total_mrr": 89500.00,
  "arpu": 74.58,
  "gross_margin": 0.82,
  "sales_marketing_spend": 45000.00,
  "monthly_churn_rate": 0.0375
}
```

### Healthy SaaS Benchmarks

| Metric | Concerning | Acceptable | Strong |
|--------|-----------|------------|--------|
| Monthly Churn | > 5% | 2-5% | < 2% |
| Net Revenue Retention | < 90% | 90-110% | > 120% |
| LTV:CAC | < 1:1 | 1:1-3:1 | > 3:1 |
| CAC Payback | > 24 mo | 12-18 mo | < 12 mo |
| Gross Margin | < 60% | 60-75% | > 75% |
