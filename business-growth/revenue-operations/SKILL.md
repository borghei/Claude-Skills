---
name: revenue-operations
description: >
  Analyzes pipeline coverage, tracks forecast accuracy with MAPE, and calculates
  GTM efficiency metrics for SaaS revenue optimization
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  domain: revenue-ops
  updated: 2026-03-31
  tags: [revops, pipeline, forecast, gtm-efficiency, saas-metrics]
---
# Revenue Operations

Pipeline analysis, forecast accuracy tracking, and GTM efficiency measurement for SaaS revenue teams.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
  - [Pipeline Analyzer](#1-pipeline-analyzer)
  - [Forecast Accuracy Tracker](#2-forecast-accuracy-tracker)
  - [GTM Efficiency Calculator](#3-gtm-efficiency-calculator)
- [Revenue Operations Workflows](#revenue-operations-workflows)
  - [Weekly Pipeline Review](#weekly-pipeline-review)
  - [Forecast Accuracy Review](#forecast-accuracy-review)
  - [GTM Efficiency Audit](#gtm-efficiency-audit)
  - [Quarterly Business Review](#quarterly-business-review)
- [Reference Documentation](#reference-documentation)
- [Templates](#templates)

---

## Quick Start

```bash
# Analyze pipeline health and coverage
python scripts/pipeline_analyzer.py --input assets/sample_pipeline_data.json --format text

# Track forecast accuracy over multiple periods
python scripts/forecast_accuracy_tracker.py assets/sample_forecast_data.json --format text

# Calculate GTM efficiency metrics
python scripts/gtm_efficiency_calculator.py assets/sample_gtm_data.json --format text
```

---

## Tools Overview

### 1. Pipeline Analyzer

Analyzes sales pipeline health including coverage ratios, stage conversion rates, deal velocity, aging risks, and concentration risks.

**Input:** JSON file with deals, quota, and stage configuration
**Output:** Coverage ratios, conversion rates, velocity metrics, aging flags, risk assessment

**Usage:**

```bash
# Text report (human-readable)
python scripts/pipeline_analyzer.py --input pipeline.json --format text

# JSON output (for dashboards/integrations)
python scripts/pipeline_analyzer.py --input pipeline.json --format json
```

**Key Metrics Calculated:**
- **Pipeline Coverage Ratio** -- Total pipeline value / quota target (healthy: 3-4x)
- **Stage Conversion Rates** -- Stage-to-stage progression rates
- **Sales Velocity** -- (Opportunities x Avg Deal Size x Win Rate) / Avg Sales Cycle
- **Deal Aging** -- Flags deals exceeding 2x average cycle time per stage
- **Concentration Risk** -- Warns when >40% of pipeline is in a single deal
- **Coverage Gap Analysis** -- Identifies quarters with insufficient pipeline

**Input Schema:**

```json
{
  "quota": 500000,
  "stages": ["Discovery", "Qualification", "Proposal", "Negotiation", "Closed Won"],
  "average_cycle_days": 45,
  "deals": [
    {
      "id": "D001",
      "name": "Acme Corp",
      "stage": "Proposal",
      "value": 85000,
      "age_days": 32,
      "close_date": "2025-03-15",
      "owner": "rep_1"
    }
  ]
}
```

### 2. Forecast Accuracy Tracker

Tracks forecast accuracy over time using MAPE, detects systematic bias, analyzes trends, and provides category-level breakdowns.

**Input:** JSON file with forecast periods and optional category breakdowns
**Output:** MAPE score, bias analysis, trends, category breakdown, accuracy rating

**Usage:**

```bash
# Track forecast accuracy
python scripts/forecast_accuracy_tracker.py forecast_data.json --format text

# JSON output for trend analysis
python scripts/forecast_accuracy_tracker.py forecast_data.json --format json
```

**Key Metrics Calculated:**
- **MAPE** -- Mean Absolute Percentage Error: mean(|actual - forecast| / |actual|) x 100
- **Forecast Bias** -- Over-forecasting (positive) vs under-forecasting (negative) tendency
- **Weighted Accuracy** -- MAPE weighted by deal value for materiality
- **Period Trends** -- Improving, stable, or declining accuracy over time
- **Category Breakdown** -- Accuracy by rep, product, segment, or any custom dimension

**Accuracy Ratings:**
| Rating | MAPE Range | Interpretation |
|--------|-----------|----------------|
| Excellent | <10% | Highly predictable, data-driven process |
| Good | 10-15% | Reliable forecasting with minor variance |
| Fair | 15-25% | Needs process improvement |
| Poor | >25% | Significant forecasting methodology gaps |

**Input Schema:**

```json
{
  "forecast_periods": [
    {"period": "2025-Q1", "forecast": 480000, "actual": 520000},
    {"period": "2025-Q2", "forecast": 550000, "actual": 510000}
  ],
  "category_breakdowns": {
    "by_rep": [
      {"category": "Rep A", "forecast": 200000, "actual": 210000},
      {"category": "Rep B", "forecast": 280000, "actual": 310000}
    ]
  }
}
```

### 3. GTM Efficiency Calculator

Calculates core SaaS GTM efficiency metrics with industry benchmarking, ratings, and improvement recommendations.

**Input:** JSON file with revenue, cost, and customer metrics
**Output:** Magic Number, LTV:CAC, CAC Payback, Burn Multiple, Rule of 40, NDR with ratings

**Usage:**

```bash
# Calculate all GTM efficiency metrics
python scripts/gtm_efficiency_calculator.py gtm_data.json --format text

# JSON output for dashboards
python scripts/gtm_efficiency_calculator.py gtm_data.json --format json
```

**Key Metrics Calculated:**

| Metric | Formula | Target |
|--------|---------|--------|
| Magic Number | Net New ARR / Prior Period S&M Spend | >0.75 |
| LTV:CAC | (ARPA x Gross Margin / Churn Rate) / CAC | >3:1 |
| CAC Payback | CAC / (ARPA x Gross Margin) months | <18 months |
| Burn Multiple | Net Burn / Net New ARR | <2x |
| Rule of 40 | Revenue Growth % + FCF Margin % | >40% |
| Net Dollar Retention | (Begin ARR + Expansion - Contraction - Churn) / Begin ARR | >110% |

**Input Schema:**

```json
{
  "revenue": {
    "current_arr": 5000000,
    "prior_arr": 3800000,
    "net_new_arr": 1200000,
    "arpa_monthly": 2500,
    "revenue_growth_pct": 31.6
  },
  "costs": {
    "sales_marketing_spend": 1800000,
    "cac": 18000,
    "gross_margin_pct": 78,
    "total_operating_expense": 6500000,
    "net_burn": 1500000,
    "fcf_margin_pct": 8.4
  },
  "customers": {
    "beginning_arr": 3800000,
    "expansion_arr": 600000,
    "contraction_arr": 100000,
    "churned_arr": 300000,
    "annual_churn_rate_pct": 8
  }
}
```

---

## Revenue Operations Workflows

### Weekly Pipeline Review

Use this workflow for your weekly pipeline inspection cadence.

1. **Generate pipeline report:**
   ```bash
   python scripts/pipeline_analyzer.py --input current_pipeline.json --format text
   ```

2. **Review key indicators:**
   - Pipeline coverage ratio (is it above 3x quota?)
   - Deals aging beyond threshold (which deals need intervention?)
   - Concentration risk (are we over-reliant on a few large deals?)
   - Stage distribution (is there a healthy funnel shape?)

3. **Document using template:** Use `assets/pipeline_review_template.md`

4. **Action items:** Address aging deals, redistribute pipeline concentration, fill coverage gaps

### Forecast Accuracy Review

Use monthly or quarterly to evaluate and improve forecasting discipline.

1. **Generate accuracy report:**
   ```bash
   python scripts/forecast_accuracy_tracker.py forecast_history.json --format text
   ```

2. **Analyze patterns:**
   - Is MAPE trending down (improving)?
   - Which reps or segments have the highest error rates?
   - Is there systematic over- or under-forecasting?

3. **Document using template:** Use `assets/forecast_report_template.md`

4. **Improvement actions:** Coach high-bias reps, adjust methodology, improve data hygiene

### GTM Efficiency Audit

Use quarterly or during board prep to evaluate go-to-market efficiency.

1. **Calculate efficiency metrics:**
   ```bash
   python scripts/gtm_efficiency_calculator.py quarterly_data.json --format text
   ```

2. **Benchmark against targets:**
   - Magic Number signals GTM spend efficiency
   - LTV:CAC validates unit economics
   - CAC Payback shows capital efficiency
   - Rule of 40 balances growth and profitability

3. **Document using template:** Use `assets/gtm_dashboard_template.md`

4. **Strategic decisions:** Adjust spend allocation, optimize channels, improve retention

### Quarterly Business Review

Combine all three tools for a comprehensive QBR analysis.

1. Run pipeline analyzer for forward-looking coverage
2. Run forecast tracker for backward-looking accuracy
3. Run GTM calculator for efficiency benchmarks
4. Cross-reference pipeline health with forecast accuracy
5. Align GTM efficiency metrics with growth targets

---

## Reference Documentation

| Reference | Description |
|-----------|-------------|
| [RevOps Metrics Guide](references/revops-metrics-guide.md) | Complete metrics hierarchy, definitions, formulas, and interpretation |
| [Pipeline Management Framework](references/pipeline-management-framework.md) | Pipeline best practices, stage definitions, conversion benchmarks |
| [GTM Efficiency Benchmarks](references/gtm-efficiency-benchmarks.md) | SaaS benchmarks by stage, industry standards, improvement strategies |

---

## Templates

| Template | Use Case |
|----------|----------|
| [Pipeline Review Template](assets/pipeline_review_template.md) | Weekly/monthly pipeline inspection documentation |
| [Forecast Report Template](assets/forecast_report_template.md) | Forecast accuracy reporting and trend analysis |
| [GTM Dashboard Template](assets/gtm_dashboard_template.md) | GTM efficiency dashboard for leadership review |
| [Sample Pipeline Data](assets/sample_pipeline_data.json) | Example input for pipeline_analyzer.py |
| [Expected Output](assets/expected_output.json) | Reference output from pipeline_analyzer.py |

---

## Tool Reference

### 1. pipeline_analyzer.py

Analyzes sales pipeline health including coverage ratios, stage conversion rates, sales velocity, deal aging risks, and concentration risks.

```bash
python scripts/pipeline_analyzer.py --input pipeline.json --format text
python scripts/pipeline_analyzer.py --input pipeline.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `--input` | required | Path to JSON file with deals, quota, and stage configuration |
| `--format` | optional | Output format: `text` (default) or `json` |

### 2. forecast_accuracy_tracker.py

Tracks forecast accuracy over time using MAPE, detects systematic bias, analyzes trends, and provides category-level breakdowns.

```bash
python scripts/forecast_accuracy_tracker.py forecast_data.json --format text
python scripts/forecast_accuracy_tracker.py forecast_data.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `forecast_data.json` | positional | Path to JSON file with forecast periods and optional category breakdowns |
| `--format` | optional | Output format: `text` (default) or `json` |

### 3. gtm_efficiency_calculator.py

Calculates core SaaS GTM efficiency metrics with industry benchmarking, ratings, and improvement recommendations.

```bash
python scripts/gtm_efficiency_calculator.py gtm_data.json --format text
python scripts/gtm_efficiency_calculator.py gtm_data.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `gtm_data.json` | positional | Path to JSON file with revenue, cost, and customer metrics |
| `--format` | optional | Output format: `text` (default) or `json` |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Pipeline coverage below 3x quota | Insufficient top-of-funnel activity or poor lead-to-opportunity conversion | Audit lead sources and conversion rates by stage; increase outbound activity or marketing spend in underperforming channels |
| Forecast MAPE above 25% | Inconsistent deal stage criteria, sandbagging, or lack of inspection rigor | Standardize stage exit criteria; implement weekly pipeline reviews tied to velocity not just activity; coach high-bias reps individually |
| Magic Number below 0.5 | GTM spend is inefficient relative to new ARR generated | Review channel ROI; reduce spend in low-performing channels; improve rep productivity before adding headcount |
| LTV:CAC below 3:1 | CAC too high or churn eroding lifetime value | Address churn first (use churn-prevention skill); then optimize CAC by shifting to lower-cost acquisition channels |
| Deals slipping past forecast close date | Lack of deal qualification, missing champion, or no compelling event | Implement MEDDIC/BANT qualification; require compelling event documentation for commit-stage deals |
| Pipeline heavily concentrated in early stages | Poor stage progression indicating stalled deals or loose qualification | Set maximum stage age limits; implement automated alerts for deals exceeding 2x average cycle per stage |
| Net Dollar Retention below 100% | Contraction and churn outpacing expansion revenue | Prioritize expansion playbooks for healthy accounts; conduct exit interviews for churning accounts; review pricing tier structure |

---

## Success Criteria

- Pipeline coverage ratio stabilizes at 3-4x quota with healthy stage distribution
- Forecast MAPE improves to below 15% (Good) or below 10% (Excellent) within two quarters
- Magic Number exceeds 0.75 indicating efficient GTM spend
- LTV:CAC ratio exceeds 3:1 with CAC payback under 18 months
- Rule of 40 score exceeds 40% (revenue growth % + FCF margin %)
- Net Dollar Retention exceeds 110% driven by expansion revenue
- Deal slippage rate drops below 30% (improved from 2024 industry average of 44%)

---

## Scope & Limitations

**In scope:** Pipeline health analysis (coverage, velocity, aging, concentration), forecast accuracy measurement (MAPE, bias, trends, category breakdowns), GTM efficiency metrics (Magic Number, LTV:CAC, CAC Payback, Burn Multiple, Rule of 40, NDR), weekly/monthly/quarterly review workflows, and QBR preparation combining all three analysis dimensions.

**Out of scope:** CRM system administration or data extraction (tools consume JSON exports), deal-level sales coaching (tools flag deals but do not prescribe sales tactics), marketing attribution modeling, customer success health scoring (use customer-success-manager skill), and real-time pipeline monitoring. Tools analyze point-in-time snapshots; continuous monitoring requires integration with CRM/BI platforms.

**Limitations:** Benchmarks are based on aggregate SaaS industry data and vary by company stage (seed, Series A-C, growth, public), vertical, and sales motion (PLG vs enterprise). Pipeline analysis assumes deal data includes accurate stage, value, age, and close date fields. Forecast accuracy requires minimum 3 periods for trend analysis. GTM metrics require accurate financial data that may not be available in early-stage companies.

---

## Integration Points

- **sales-engineer** -- Pipeline deals requiring technical validation route through sales-engineer POC and RFP workflows
- **customer-success-manager** -- Post-close handoff; NDR metrics depend on customer success health scoring and expansion plays
- **pricing-strategy** -- Pricing model impacts pipeline velocity, deal sizes, and conversion rates; pricing changes require pipeline reforecasting
- **churn-prevention** -- Churn rate directly impacts LTV:CAC and NDR metrics; reducing churn improves all GTM efficiency measures
- **c-level-advisor** -- GTM efficiency metrics feed directly into board-level reporting and strategic resource allocation decisions
