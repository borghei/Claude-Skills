---
name: financial-analyst
description: "Performs financial ratio analysis, DCF valuation, budget variance analysis, and rolling forecast construction for strategic decision-making. Use when the user asks about financial analysis, company valuation, budget review, forecasting, financial ratios, cash flow projections, variance analysis, DCF modeling, or financial planning."
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: finance
  domain: financial-analysis
  updated: 2026-03-31
  tags: [financial-analysis, dcf, budgeting, forecasting, ratios]
---

# Financial Analyst

Production-ready financial analysis toolkit providing ratio analysis, DCF valuation, budget variance analysis, and rolling forecast construction. All scripts use Python standard library only — no numpy, pandas, or scipy required.

## Core Workflow

### 1. Define Scope and Validate Data

The agent establishes analysis objectives, identifies data sources, and validates input:

```bash
# Validate JSON input before running any script
python -m json.tool assets/sample_financial_data.json > /dev/null
```

Required input sections: `income_statement`, `balance_sheet`, `cash_flow`. Optional: `market_data` (for valuation ratios).

**Validate:** JSON parses without error; all required sections present with non-zero values.

### 2. Calculate Financial Ratios

The agent runs ratio analysis across 5 categories:

```bash
python scripts/ratio_calculator.py assets/sample_financial_data.json
python scripts/ratio_calculator.py assets/sample_financial_data.json --format json
python scripts/ratio_calculator.py assets/sample_financial_data.json --category profitability
```

**Ratio categories:** Profitability (ROE, ROA, Gross/Operating/Net Margin), Liquidity (Current, Quick, Cash Ratio), Leverage (Debt-to-Equity, Interest Coverage, DSCR), Efficiency (Asset/Inventory/Receivables Turnover, DSO), Valuation (P/E, P/B, P/S, EV/EBITDA, PEG).

**Validate:** No ratios return 0.00 (indicates missing data). Cross-check key ratios against industry benchmarks in `references/financial-ratios-guide.md`.

### 3. Build DCF Valuation

The agent constructs a discounted cash flow model:

```bash
python scripts/dcf_valuation.py valuation_data.json
python scripts/dcf_valuation.py valuation_data.json --format json
python scripts/dcf_valuation.py valuation_data.json --projection-years 7
```

The tool calculates WACC (via CAPM), projects revenue and FCF over 5 years (default), derives terminal value via perpetuity growth and exit multiple methods, and produces a two-way sensitivity table (WACC vs terminal growth rate).

**Validate:** Terminal growth rate < WACC (typically 2-3% vs 8-12%); equity value is positive; sensitivity table has no N/A rows.

### 4. Analyze Budget Variances

The agent identifies material deviations from budget:

```bash
python scripts/budget_variance_analyzer.py budget_data.json
python scripts/budget_variance_analyzer.py budget_data.json --threshold-pct 5 --threshold-amt 25000
```

The tool calculates dollar and percentage variances, classifies favorable/unfavorable, filters by materiality threshold, and generates department and category summaries.

**Validate:** All material variances (exceeding threshold) have documented root-cause explanations. Cross-check revenue/expense classification (revenue favorable = actual > budget; expense favorable = actual < budget).

### 5. Construct Rolling Forecast

The agent builds driver-based forecasts with scenario modeling:

```bash
python scripts/forecast_builder.py forecast_data.json
python scripts/forecast_builder.py forecast_data.json --scenarios base,bull,bear
```

The tool produces trend analysis (linear regression, growth rates), scenario comparison, per-period forecast detail, and 13-week rolling cash flow projection with runway calculation.

**Validate:** At least 3 historical periods provided; revenue growth rate is non-zero; cash runway calculation is realistic (compare against known burn rate).

### 6. Synthesize and Report

The agent generates the final deliverable:
- Executive summary with key findings and recommendations
- Detailed ratio report with trend interpretation
- DCF valuation report with sensitivity ranges
- Variance analysis with corrective action plans
- Rolling forecast with scenario comparisons

Templates: `assets/variance_report_template.md`, `assets/dcf_analysis_template.md`, `assets/forecast_report_template.md`

**Validate:** Report delivery meets agreed SLA; all assumptions documented with source and rationale.

## Anti-Patterns

1. **Running scripts on incomplete data** — Missing financial statement fields produce misleading zero ratios. The agent validates JSON input completeness before running any analysis.
2. **Setting terminal growth rate above WACC** — This produces infinite valuations. The agent ensures terminal growth is 2-3% and always below WACC.
3. **Ignoring materiality thresholds** — Flagging every $100 variance wastes stakeholder attention. The agent sets thresholds matching organizational materiality policy (default: 10% or $50K).
4. **Presenting forecasts without scenario ranges** — Single-point forecasts create false precision. The agent always generates base/bull/bear scenarios.
5. **Treating ratio benchmarks as universal** — Industry benchmarks vary significantly by vertical and company stage. The agent adjusts benchmarks using `references/financial-ratios-guide.md`.

## Tools

### ratio_calculator.py

```
usage: ratio_calculator.py [-h] [--format {text,json}]
                           [--category {profitability,liquidity,leverage,efficiency,valuation}]
                           input_file
```

Calculates 20 financial ratios across 5 categories with interpretation and benchmarking.

### dcf_valuation.py

```
usage: dcf_valuation.py [-h] [--format {text,json}]
                        [--projection-years PROJECTION_YEARS]
                        input_file
```

DCF enterprise and equity valuation with WACC, terminal value, and sensitivity analysis.

### budget_variance_analyzer.py

```
usage: budget_variance_analyzer.py [-h] [--format {text,json}]
                                   [--threshold-pct PCT] [--threshold-amt AMT]
                                   input_file
```

Actual vs budget vs prior year analysis with materiality filtering and executive summaries.

### forecast_builder.py

```
usage: forecast_builder.py [-h] [--format {text,json}]
                           [--scenarios SCENARIOS]
                           input_file
```

Driver-based revenue forecasting with 13-week cash flow projection and multi-scenario modeling.

## Troubleshooting

| Problem | Resolution |
|---------|------------|
| All ratios return 0.00 | Verify `income_statement`, `balance_sheet`, and `cash_flow` keys are populated with non-zero values |
| DCF yields negative equity value | Confirm `net_debt` is accurate; ensure `terminal_growth_rate` < WACC |
| Sensitivity table shows N/A | Widen gap between WACC and terminal growth rate |
| Every budget line flagged as material | Increase `--threshold-pct` and `--threshold-amt` to match organizational policy |
| Forecast produces flat projections | Provide at least 3 historical periods; set non-zero `revenue_growth_rate` |
| JSON parsing error | Validate with `python -m json.tool input_file.json`; ensure UTF-8 encoding |

## References

- [Financial Ratios Guide](references/financial-ratios-guide.md) — Ratio formulas, interpretation, and industry benchmarks
- [Valuation Methodology](references/valuation-methodology.md) — DCF methodology, WACC derivation, terminal value approaches
- [Forecasting Best Practices](references/forecasting-best-practices.md) — Driver-based forecasting, rolling forecasts, accuracy measurement
- [Industry Adaptations](references/industry-adaptations.md) — SaaS, Retail, Manufacturing, Financial Services, and Healthcare-specific metrics and considerations

## Integration Points

| Related Skill | Use Case |
|---------------|----------|
| `c-level-advisor/ceo-advisor` | Feed DCF outputs into strategic investment decisions |
| `c-level-advisor/cto-advisor` | Provide technology investment ROI and CapEx forecasts |
| `business-growth/revenue-operations` | Connect forecasts to pipeline and GTM planning |
| `data-analytics/data-analyst` | Export structured JSON for BI dashboard integration |
