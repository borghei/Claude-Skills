---
name: cfo-advisor
description: >
  Financial leadership advisor for CFOs on financial planning, fundraising,
  investor reporting, unit economics, cash management, and financial operations.
  Use when building a financial model, preparing for fundraising due diligence,
  designing investor reporting packages, calculating unit economics, managing
  cash runway, or planning month-end close processes.
version: 1.0.0
author: borghei
category: executive-leadership
tags: [finance, fundraising, accounting, reporting, treasury]
---

# CFO Advisor

The agent acts as a fractional CFO, providing financial strategy and operational finance guidance grounded in SaaS benchmarks, GAAP standards, and investor expectations.

## Workflow

1. **Establish financial baseline** -- Collect current ARR, burn rate, cash balance, and headcount. Calculate runway in months. Validate that the data is recent (within 30 days).
2. **Build unit economics** -- Calculate CAC, LTV, CAC Payback, LTV:CAC ratio, NRR, and Burn Multiple using the formulas below. Flag any metric outside benchmark ranges.
3. **Construct financial model** -- Build a 3-year model following the Revenue Build and Expense Build structures. Document all key assumptions explicitly.
4. **Design investor reporting** -- Configure the Monthly Metrics Package template. Set up the Board Financial Presentation slide structure for quarterly use.
5. **Set up cash management** -- Build the 13-week cash flow forecast. Establish the monthly rolling forecast. Verify minimum 6-month runway is maintained.
6. **Establish close cadence** -- Implement the Month-End Timeline (Day 1-12). Assign owners to each quality checklist item.
7. **Assess risk posture** -- Review market, credit, and operational risk categories. Confirm insurance coverage is adequate for company stage.

## SaaS Unit Economics

```
CAC = (Sales + Marketing Spend) / New Customers
CAC Payback = CAC / (ARPU x Gross Margin)

LTV = ARPU x Gross Margin x Customer Lifetime
LTV:CAC Ratio = LTV / CAC                        Target: > 3:1

Logo Retention = (Customers End - New) / Customers Start
Net Revenue Retention = (MRR End - Churn + Expansion) / MRR Start
```

## Burn Multiple

```
Burn Multiple = Net Burn / Net New ARR

< 1.0x   Excellent efficiency
1.0-1.5x Good efficiency
1.5-2.0x Average
> 2.0x   Needs improvement
```

## Rule of 40

```
Rule of 40 = Revenue Growth % + Profit Margin %

> 40%   Strong performance
20-40%  Acceptable
< 20%   Needs attention
```

## Monthly Metrics Package

```
FINANCIAL HIGHLIGHTS
- Revenue: $X.XM (vs Plan: +/-Y%)
- Gross Margin: XX% (vs Plan: +/-Y%)
- Operating Loss: $X.XM (vs Plan: +/-Y%)
- Cash Balance: $X.XM
- Runway: XX months

REVENUE METRICS
- ARR: $X.XM (+Y% QoQ)
- Net New ARR: $XXK
- NRR: XXX%
- Logo Churn: X.X%

EFFICIENCY METRICS
- CAC: $X,XXX
- CAC Payback: XX months
- Burn Multiple: X.Xx
```

## Board Financial Presentation

1. Financial summary (1 slide)
2. Revenue performance (1-2 slides)
3. Expense breakdown (1 slide)
4. Cash flow and runway (1 slide)
5. Key metrics trends (1 slide)
6. Forecast outlook (1 slide)

## Revenue Build (Financial Model)

1. Starting ARR / customers
2. New logo assumptions (by segment)
3. Expansion rate
4. Churn rate
5. Pricing changes
6. Segment mix

## Expense Build (Financial Model)

1. Headcount plan (by department)
2. Comp and benefits
3. Contractors
4. Software / tools
5. Facilities
6. Marketing programs
7. Travel and events

## Budget Categories

| Category | Line Items |
|----------|-----------|
| Revenue | New business (by segment), expansion, renewals, professional services |
| Cost of Revenue | Hosting/infrastructure, support, PS delivery, payment processing |
| OpEx | Sales & Marketing, R&D, G&A |

## Month-End Close Timeline

| Days | Activity |
|------|----------|
| 1-3 | Transaction cutoff |
| 3-5 | Reconciliations |
| 5-7 | Accruals and adjustments |
| 7-10 | Management review |
| 10-12 | Final close |

**Quality Checklist**: Bank reconciliation, revenue recognition, expense accruals, prepaid amortization, deferred revenue, intercompany elimination, flux analysis.

## Revenue Recognition (ASC 606)

1. Identify the contract
2. Identify performance obligations
3. Determine transaction price
4. Allocate price to obligations
5. Recognize revenue when satisfied

**SaaS considerations**: Subscription vs usage revenue, implementation services, professional services, multi-year contracts, discounts and credits.

## Cash Management

**13-Week Cash Flow**: Week-by-week projections of all known inflows/outflows. Review weekly. Maintain minimum cash buffer.

**Monthly Rolling Forecast**: 12-month forward view covering revenue collection timing, payroll, vendor payments, debt service, and CapEx.

**Treasury Principles**: Maintain 6+ months runway, preserve capital, optimize yield on idle cash, follow investment policy.

**Cash Preservation Levers** (when extending runway):
1. Hiring freeze
2. Vendor renegotiation
3. Discretionary spend cuts
4. Payment term extension
5. Revenue acceleration
6. Bridge financing

## Due Diligence Data Room Checklist

**Financial data**:
- [ ] 3 years historical financials
- [ ] Monthly P&L by segment
- [ ] Balance sheet and cash flow
- [ ] ARR/MRR cohort analysis
- [ ] Customer unit economics
- [ ] Revenue recognition policy
- [ ] AR aging
- [ ] AP summary

**Projections**:
- [ ] 3-5 year financial model
- [ ] Key assumptions documented
- [ ] Sensitivity analysis
- [ ] Use of funds breakdown
- [ ] Path to profitability

## Financial Risk Categories

| Risk Type | Key Concerns |
|-----------|-------------|
| Market | Interest rate exposure, FX exposure, customer concentration |
| Credit | Customer creditworthiness, AR aging, bad debt reserves |
| Operational | Internal controls, fraud prevention, systems reliability |

## Example: Series-A SaaS Financial Snapshot

A Series-A company ($3M ARR, 35 employees, $12M raised) preparing for Series B:

```
Unit Economics:
  CAC: $22K  |  LTV: $88K  |  LTV:CAC: 4.0x  |  CAC Payback: 16 months
  NRR: 115%  |  Logo Retention: 90%  |  Gross Margin: 78%

Burn:
  Monthly burn: $350K  |  Net new ARR/month: $180K
  Burn Multiple: 1.9x (average -- needs improvement for Series B)
  Cash: $5.2M  |  Runway: 15 months

Rule of 40:
  Revenue growth: 95% YoY  |  Profit margin: -40%
  Score: 55% (strong)

Board recommendation: Raise in 6 months at current trajectory.
  Target metrics for raise: Burn Multiple < 1.5x, NRR > 120%.
```

## Essential Insurance Policies

D&O, E&O, Cyber liability, General liability, Workers compensation, Key person insurance.

## Scripts

```bash
# Unit economics calculator
python scripts/unit_economics.py --metrics data.csv

# Cash flow projector
python scripts/cash_forecast.py --actuals Q1.csv --assumptions model.yaml

# Financial model builder
python scripts/fin_model.py --template saas --output model.xlsx

# Investor metrics dashboard
python scripts/investor_metrics.py --period monthly
```

## References

- `references/financial_modeling.md` -- Model building guide
- `references/saas_metrics.md` -- SaaS metrics deep dive
- `references/accounting_policies.md` -- Policy documentation
- `references/audit_prep.md` -- Audit readiness guide
