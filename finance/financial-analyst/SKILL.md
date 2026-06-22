---
name: financial-analyst
description: >
  Performs financial ratio analysis, DCF valuation, budget variance analysis,
  and rolling forecast construction for strategic decision-making
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: finance
  domain: financial-analysis
  updated: 2026-03-31
  tags: [financial-analysis, dcf, budgeting, forecasting, ratios]
---
# Financial Analyst Skill

## Overview

Production-ready financial analysis toolkit providing ratio analysis, DCF valuation, budget variance analysis, and rolling forecast construction. Designed for financial analysts with 3-6 years experience performing financial modeling, forecasting & budgeting, management reporting, business performance analysis, and investment analysis.

## Use when

- The user asks to "run financial ratios", "build a DCF", "analyze budget variance", or "build a forecast"
- A valuation range is needed for an acquisition, fundraise, or board presentation
- Actuals vs budget needs investigation (which variances are material, favorable/unfavorable, department breakdown)
- A rolling 13-week cash flow or driver-based revenue forecast needs construction
- Sensitivity analysis is required to stress-test valuation or forecast assumptions
- The user asks about profitability, liquidity, leverage, efficiency, or valuation metrics with industry context

## Clarify First

Before the analysis, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which analysis** — ratios, DCF valuation, budget variance, or forecast (selects the tool and the required input schema; each needs different data)
- [ ] **The decision it supports** — acquisition, fundraise, board review, or budget reforecast (sets the executive-summary conclusion and which metrics lead)
- [ ] **Materiality threshold** — absolute $ or % of budget (drives which variances surface vs. go to the appendix; default 10% / $50K)
- [ ] **Key assumptions + as-of date** — WACC inputs, terminal growth, or forecast drivers and when each was last sourced (drives DCF/forecast outputs and the assumptions appendix)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## 5-Phase Workflow

### Phase 1: Scoping
- Define analysis objectives and stakeholder requirements
- Identify data sources and time periods
- Establish materiality thresholds and accuracy targets
- Select appropriate analytical frameworks
- *Validate:* materiality threshold is explicit (absolute $ or %), accuracy target is a number, and the decision the analysis supports is named

### Phase 2: Data Analysis & Modeling
- Collect and validate financial data (income statement, balance sheet, cash flow)
- Calculate financial ratios across 5 categories (profitability, liquidity, leverage, efficiency, valuation)
- Build DCF models with WACC and terminal value calculations
- Construct budget variance analyses with favorable/unfavorable classification
- Develop driver-based forecasts with scenario modeling
- *Validate:* input JSON conforms to the expected schema (no missing statements, no mixed periods); WACC inputs sourced within the last quarter; terminal growth rate ≤ long-run GDP growth

### Phase 3: Insight Generation
- Interpret ratio trends and benchmark against industry standards
- Identify material variances and root causes
- Assess valuation ranges through sensitivity analysis
- Evaluate forecast scenarios (base/bull/bear) for decision support
- *Validate:* every material variance has a root-cause hypothesis; DCF sensitivity range is wider than ±15% on WACC and terminal growth

### Phase 4: Reporting
- Generate executive summaries with key findings
- Produce detailed variance reports by department and category
- Deliver DCF valuation reports with sensitivity tables
- Present rolling forecasts with trend analysis
- *Validate:* executive summary leads with the decision-relevant conclusion, not the method; assumptions appendix lists source + last-reviewed date for each

### Phase 5: Follow-up
- Track forecast accuracy (target: +/-5% revenue, +/-3% expenses)
- Monitor report delivery timeliness (target: 100% on time)
- Update models with actuals as they become available
- Refine assumptions based on variance analysis

## Tools

### 1. Ratio Calculator (`scripts/ratio_calculator.py`)

Calculate and interpret financial ratios from financial statement data.

**Ratio Categories:**
- **Profitability:** ROE, ROA, Gross Margin, Operating Margin, Net Margin
- **Liquidity:** Current Ratio, Quick Ratio, Cash Ratio
- **Leverage:** Debt-to-Equity, Interest Coverage, DSCR
- **Efficiency:** Asset Turnover, Inventory Turnover, Receivables Turnover, DSO
- **Valuation:** P/E, P/B, P/S, EV/EBITDA, PEG Ratio

```bash
python scripts/ratio_calculator.py sample_financial_data.json
python scripts/ratio_calculator.py sample_financial_data.json --format json
python scripts/ratio_calculator.py sample_financial_data.json --category profitability
```

### 2. DCF Valuation (`scripts/dcf_valuation.py`)

Discounted Cash Flow enterprise and equity valuation with sensitivity analysis.

**Features:**
- WACC calculation via CAPM
- Revenue and free cash flow projections (5-year default)
- Terminal value via perpetuity growth and exit multiple methods
- Enterprise value and equity value derivation
- Two-way sensitivity analysis (discount rate vs growth rate)

```bash
python scripts/dcf_valuation.py valuation_data.json
python scripts/dcf_valuation.py valuation_data.json --format json
python scripts/dcf_valuation.py valuation_data.json --projection-years 7
```

### 3. Budget Variance Analyzer (`scripts/budget_variance_analyzer.py`)

Analyze actual vs budget vs prior year performance with materiality filtering.

**Features:**
- Dollar and percentage variance calculation
- Materiality threshold filtering (default: 10% or $50K)
- Favorable/unfavorable classification with revenue/expense logic
- Department and category breakdown
- Executive summary generation

```bash
python scripts/budget_variance_analyzer.py budget_data.json
python scripts/budget_variance_analyzer.py budget_data.json --format json
python scripts/budget_variance_analyzer.py budget_data.json --threshold-pct 5 --threshold-amt 25000
```

### 4. Forecast Builder (`scripts/forecast_builder.py`)

Driver-based revenue forecasting with rolling cash flow projection and scenario modeling.

**Features:**
- Driver-based revenue forecast model
- 13-week rolling cash flow projection
- Scenario modeling (base/bull/bear cases)
- Trend analysis using simple linear regression (standard library)

```bash
python scripts/forecast_builder.py forecast_data.json
python scripts/forecast_builder.py forecast_data.json --format json
python scripts/forecast_builder.py forecast_data.json --scenarios base,bull,bear
```

## Knowledge Bases

| Reference | Purpose |
|-----------|---------|
| `references/financial-ratios-guide.md` | Ratio formulas, interpretation, industry benchmarks |
| `references/valuation-methodology.md` | DCF methodology, WACC, terminal value, comps |
| `references/forecasting-best-practices.md` | Driver-based forecasting, rolling forecasts, accuracy |

## Templates

| Template | Purpose |
|----------|---------|
| `assets/variance_report_template.md` | Budget variance report template |
| `assets/dcf_analysis_template.md` | DCF valuation analysis template |
| `assets/forecast_report_template.md` | Revenue forecast report template |

## Industry Adaptations

### SaaS
- Key metrics: MRR, ARR, CAC, LTV, Churn Rate, Net Revenue Retention
- Revenue recognition: subscription-based, deferred revenue tracking
- Unit economics: CAC payback period, LTV/CAC ratio
- Cohort analysis for retention and expansion revenue

### Retail
- Key metrics: Same-store sales, Revenue per square foot, Inventory turnover
- Seasonal adjustment factors in forecasting
- Gross margin analysis by product category
- Working capital cycle optimization

### Manufacturing
- Key metrics: Gross margin by product line, Capacity utilization, COGS breakdown
- Bill of materials cost analysis
- Absorption vs variable costing impact
- Capital expenditure planning and ROI

### Financial Services
- Key metrics: Net Interest Margin, Efficiency Ratio, ROA, Tier 1 Capital
- Regulatory capital requirements
- Credit loss provisioning and reserves
- Fee income analysis and diversification

### Healthcare
- Key metrics: Revenue per patient, Payer mix, Days in A/R, Operating margin
- Reimbursement rate analysis by payer
- Case mix index impact on revenue
- Compliance cost allocation

## Key Metrics & Targets

| Metric | Target |
|--------|--------|
| Forecast accuracy (revenue) | +/-5% |
| Forecast accuracy (expenses) | +/-3% |
| Report delivery | 100% on time |
| Model documentation | Complete for all assumptions |
| Variance explanation | 100% of material variances |

## Input Data Format

All scripts accept JSON input files. See `assets/sample_financial_data.json` for the complete input schema covering all four tools.

## Dependencies

**None** - All scripts use Python standard library only (`math`, `statistics`, `json`, `argparse`, `datetime`). No numpy, pandas, or scipy required.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| All ratios return 0.00 | Missing or zeroed financial statement fields in input JSON | Verify `income_statement`, `balance_sheet`, and `cash_flow` keys are populated with non-zero values; check field names match expected schema |
| DCF yields negative equity value | Net debt exceeds enterprise value, or WACC is set lower than terminal growth rate | Confirm `net_debt` is accurate; ensure `terminal_growth_rate` < WACC (typically 2-3% vs 8-12%); review capital structure assumptions |
| Sensitivity table shows "N/A" across entire row | WACC value in that row is less than or equal to every terminal growth rate in the range | Widen the gap between WACC and terminal growth; raise WACC inputs or lower the growth range in `assumptions.terminal_growth_rate` |
| Budget variance analyzer flags every line as material | Materiality thresholds set too low relative to the data scale | Increase `--threshold-pct` (e.g., from 5 to 10) and `--threshold-amt` (e.g., from 25000 to 100000) to match organizational materiality policy |
| Forecast builder produces flat projections | Historical data has fewer than 2 periods, or `revenue_growth_rate` is set to 0 | Provide at least 3-4 historical periods in `historical_periods`; set a non-zero `revenue_growth_rate` in `assumptions` |
| JSON parsing error on script execution | Malformed JSON input file (trailing commas, unquoted keys, encoding issues) | Validate input with `python -m json.tool input_file.json`; ensure UTF-8 encoding; remove trailing commas and comments |
| Valuation ratios all show "Insufficient data" | Missing `market_data` section in input JSON (share price, shares outstanding) | Add the `market_data` object with `share_price`, `shares_outstanding`, and `earnings_growth_rate` fields to the input file |

## Success Criteria

- **Forecast Accuracy**: Revenue forecasts land within +/-5% of actuals; expense forecasts within +/-3% over rolling 12-month periods
- **Variance Coverage**: 100% of material variances (exceeding threshold) include documented root-cause explanations and corrective action plans
- **Valuation Confidence**: DCF-derived equity value falls within 15% of comparable-company and precedent-transaction benchmarks, validated through sensitivity analysis
- **Report Timeliness**: All financial analysis deliverables (ratio reports, variance analyses, forecast updates) published within agreed SLA -- target 100% on-time delivery
- **Model Integrity**: Every assumption in DCF and forecast models is documented with source, rationale, and last-reviewed date; WACC inputs refresh quarterly against market data
- **Stakeholder Adoption**: Financial models and dashboards referenced in at least 80% of executive budget reviews, board presentations, and investment committee decisions
- **Analytical Efficiency**: End-to-end analysis cycle time (data collection through report delivery) reduced by 40%+ compared to manual spreadsheet workflows, measured per reporting period

## Scope & Limitations

**This skill covers:**
- Quantitative financial ratio analysis across profitability, liquidity, leverage, efficiency, and valuation categories with built-in industry benchmarking
- Discounted Cash Flow (DCF) enterprise and equity valuation using CAPM-based WACC, perpetuity growth and exit multiple terminal value methods, and two-way sensitivity analysis
- Budget variance analysis with materiality filtering, favorable/unfavorable classification, department and category breakdowns, and executive summary generation
- Driver-based revenue forecasting with 13-week rolling cash flow projection, base/bull/bear scenario modeling, and linear regression trend analysis

**This skill does NOT cover:**
- Real-time market data feeds, live stock price retrieval, or automated data ingestion from ERP/accounting systems (all input is via static JSON files)
- Qualitative analysis such as management quality assessment, competitive moat evaluation, ESG scoring, or regulatory risk judgment
- Tax optimization, transfer pricing, multi-entity consolidation, or jurisdiction-specific accounting treatments (IFRS vs GAAP reconciliation)
- Monte Carlo simulation, options pricing (Black-Scholes), credit risk modeling, or any analysis requiring external libraries beyond the Python standard library

## Anti-patterns

| Anti-pattern | Failure mode | Fix |
|--------------|--------------|-----|
| Building a DCF on a single-scenario forecast | False precision; one number presented as a target price | Always run base/bull/bear; present valuation as a range with sensitivity tables |
| Terminal growth rate ≥ long-run GDP growth | Valuation dominated by terminal value assuming perpetual above-economy growth | Cap terminal growth at 2-3% (long-run GDP proxy); if comps justify higher, flag explicitly |
| WACC inputs more than a quarter old | Rate environment moved; discount rate is wrong; valuation wrong | Refresh risk-free rate, ERP, and beta quarterly; document "last reviewed" date per input |
| Benchmarking ratios against a generic "industry average" | Peer set is wrong; conclusions are wrong | Use a specific comparable-company set (size, geography, business model) — see industry benchmarks in `references/financial-ratios-guide.md` |
| Reporting every variance instead of filtering by materiality | Stakeholders tune out; real issues buried | Apply a materiality threshold (absolute $ or % of budget); below threshold goes into an appendix, not the report |
| Favorable variance = "good"; unfavorable = "bad" | Misses revenue shortfalls masked by expense underspend; misses over-delivery hiding scope cuts | Always pair the classification with a root-cause note — direction alone is not insight |
| Mixing forecast periods (quarterly actuals against annual budget) | Variances that don't reconcile; trust collapses | Run the tools on matched periods only; if a period is partial, annotate and use period-adjusted comparisons |
| Treating model output as the answer | Model is a reasoning aid, not a decision | Lead the executive summary with the decision; put the model outputs in support |

## Integration Points

| Related Skill | Domain | Integration Use Case |
|---------------|--------|---------------------|
| `c-level-advisor/ceo-advisor` | C-Level Advisory | Feed DCF valuation outputs and scenario comparisons into CEO strategic investment decisions and board-ready presentations |
| `c-level-advisor/cto-advisor` | C-Level Advisory | Provide technology investment ROI analysis and CapEx forecasts to support build-vs-buy and infrastructure scaling decisions |
| `business-growth/revenue-operations` | Business & Growth | Connect revenue forecasts and unit-economics metrics (CAC, LTV, payback period) to pipeline and go-to-market planning |
| `product-team/product-manager` | Product Team | Supply budget variance data and RICE-weighted financial projections for feature prioritization and resource allocation |
| `data-analytics/data-analyst` | Data Analytics | Export ratio analysis and forecast outputs as structured JSON for BI dashboard integration and trend visualization |
| `project-management/project-financial-management` | Project Management | Align budget variance analysis with project-level cost tracking, earned value management, and milestone-based funding releases |

## Tool Reference

### `scripts/ratio_calculator.py`

Calculate and interpret financial ratios across 5 categories with industry benchmarking.

```
usage: ratio_calculator.py [-h] [--format {text,json}]
                           [--category {profitability,liquidity,leverage,efficiency,valuation}]
                           input_file

positional arguments:
  input_file            Path to JSON file with financial statement data
                        (must contain income_statement, balance_sheet,
                        cash_flow, and optionally market_data objects)

options:
  -h, --help            Show help message and exit
  --format {text,json}  Output format (default: text)
  --category {profitability,liquidity,leverage,efficiency,valuation}
                        Calculate only a specific ratio category;
                        omit to calculate all 5 categories (20 ratios)
```

**Ratios computed:** ROE, ROA, Gross Margin, Operating Margin, Net Margin, Current Ratio, Quick Ratio, Cash Ratio, Debt-to-Equity, Interest Coverage, DSCR, Asset Turnover, Inventory Turnover, Receivables Turnover, DSO, P/E, P/B, P/S, EV/EBITDA, PEG Ratio.

### `scripts/dcf_valuation.py`

Discounted Cash Flow enterprise and equity valuation with WACC calculation and sensitivity analysis.

```
usage: dcf_valuation.py [-h] [--format {text,json}]
                        [--projection-years PROJECTION_YEARS]
                        input_file

positional arguments:
  input_file            Path to JSON file with valuation data
                        (must contain historical and assumptions objects)

options:
  -h, --help            Show help message and exit
  --format {text,json}  Output format (default: text)
  --projection-years PROJECTION_YEARS
                        Number of projection years; overrides the value
                        in the input file (default: 5)
```

**Outputs:** WACC (CAPM), projected revenue and FCF, terminal value (perpetuity growth + exit multiple), enterprise value, equity value, value per share, and a two-way sensitivity table (WACC vs terminal growth rate).

### `scripts/budget_variance_analyzer.py`

Analyze actual vs budget vs prior year performance with materiality filtering and executive summaries.

```
usage: budget_variance_analyzer.py [-h] [--format {text,json}]
                                   [--threshold-pct THRESHOLD_PCT]
                                   [--threshold-amt THRESHOLD_AMT]
                                   input_file

positional arguments:
  input_file            Path to JSON file with budget data
                        (must contain line_items array with actual,
                        budget, and optionally prior_year values)

options:
  -h, --help            Show help message and exit
  --format {text,json}  Output format (default: text)
  --threshold-pct THRESHOLD_PCT
                        Materiality threshold as percentage (default: 10.0)
  --threshold-amt THRESHOLD_AMT
                        Materiality threshold as dollar amount (default: 50000.0)
```

**Outputs:** Executive summary (revenue/expense/net impact), all variances with favorability classification, material variances filtered by threshold, department summary, and category summary.

### `scripts/forecast_builder.py`

Driver-based revenue forecasting with rolling cash flow projection and multi-scenario modeling.

```
usage: forecast_builder.py [-h] [--format {text,json}]
                           [--scenarios SCENARIOS]
                           input_file

positional arguments:
  input_file            Path to JSON file with forecast data
                        (must contain historical_periods, drivers,
                        assumptions, cash_flow_inputs, and scenarios objects)

options:
  -h, --help            Show help message and exit
  --format {text,json}  Output format (default: text)
  --scenarios SCENARIOS
                        Comma-separated list of scenarios to model
                        (default: base,bull,bear)
```

**Outputs:** Trend analysis (linear regression, growth rates, seasonality index), scenario comparison table, per-period forecast detail (revenue, COGS, gross profit, OpEx, operating income), and 13-week rolling cash flow projection with runway calculation.
