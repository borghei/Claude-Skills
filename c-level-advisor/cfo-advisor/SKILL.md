---
name: cfo-advisor
description: Financial leadership advisor for CFOs on financial planning, fundraising, investor reporting, unit economics, cash management, and financial operations.
version: 1.0.0
author: borghei
category: executive-leadership
tags: [finance, fundraising, accounting, reporting, treasury]
---

# CFO Advisor

Financial leadership advisory for Chief Financial Officers.

## Core Competencies

- Financial planning and analysis (FP&A)
- Fundraising and capital markets
- Investor and board reporting
- Unit economics and metrics
- Cash flow management
- Accounting and compliance
- Tax strategy
- Risk management

## Financial Planning Framework

### Annual Planning Process

**Timeline:**
- Month 1: Strategic priorities from CEO/Board
- Month 2: Departmental bottoms-up planning
- Month 3: Consolidation and iteration
- Month 4: Board approval and communication

**Plan Components:**
1. Revenue model and assumptions
2. Headcount plan by department
3. Operating expense budget
4. Capital expenditure plan
5. Cash flow projections
6. Key metrics and targets

### Budget Categories

**Revenue:**
- New business (by segment)
- Expansion revenue
- Renewals
- Professional services
- Other revenue

**Cost of Revenue:**
- Hosting/infrastructure
- Customer support
- Professional services delivery
- Payment processing

**Operating Expenses:**
- Sales and Marketing
- Research and Development
- General and Administrative

## Unit Economics

### SaaS Metrics Framework

**Customer Acquisition:**
```
CAC = (Sales + Marketing Spend) / New Customers
CAC Payback = CAC / (ARPU × Gross Margin)
```

**Customer Value:**
```
LTV = ARPU × Gross Margin × Customer Lifetime
LTV:CAC Ratio = LTV / CAC (Target: > 3:1)
```

**Retention:**
```
Logo Retention = (Customers End - New) / Customers Start
Net Revenue Retention = (MRR End - Churn + Expansion) / MRR Start
```

### Burn Multiple

```
Burn Multiple = Net Burn / Net New ARR

Benchmarks:
- < 1.0x: Excellent efficiency
- 1.0-1.5x: Good efficiency
- 1.5-2.0x: Average
- > 2.0x: Needs improvement
```

### Rule of 40

```
Rule of 40 = Revenue Growth % + Profit Margin %

Benchmarks:
- > 40%: Strong performance
- 20-40%: Acceptable
- < 20%: Needs attention
```

## Fundraising Finance

### Due Diligence Preparation

**Financial Data Room:**
- [ ] 3 years historical financials
- [ ] Monthly P&L by segment
- [ ] Balance sheet and cash flow
- [ ] ARR/MRR cohort analysis
- [ ] Customer unit economics
- [ ] Revenue recognition policy
- [ ] Accounts receivable aging
- [ ] Accounts payable summary

**Projections:**
- [ ] 3-5 year financial model
- [ ] Key assumptions documented
- [ ] Sensitivity analysis
- [ ] Use of funds breakdown
- [ ] Path to profitability

### Financial Model Structure

**Revenue Build:**
1. Starting ARR/customers
2. New logo assumptions
3. Expansion rate
4. Churn rate
5. Pricing changes
6. Segment mix

**Expense Build:**
1. Headcount plan
2. Comp and benefits
3. Contractors
4. Software/tools
5. Facilities
6. Marketing programs
7. Travel and events

## Investor Reporting

### Monthly Metrics Package

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

### Board Financial Presentation

**Slide Structure:**
1. Financial summary (1 slide)
2. Revenue performance (1-2 slides)
3. Expense breakdown (1 slide)
4. Cash flow and runway (1 slide)
5. Key metrics trends (1 slide)
6. Forecast outlook (1 slide)

## Cash Management

### Cash Flow Forecasting

**13-Week Cash Flow:**
- Week-by-week projections
- All known inflows/outflows
- Timing of large payments
- Minimum cash buffer
- Review weekly

**Monthly Rolling Forecast:**
- 12-month forward view
- Revenue collection timing
- Payroll and benefits
- Vendor payments
- Debt service
- Capital expenditures

### Treasury Principles

1. **Liquidity**: Maintain minimum 6 months runway
2. **Safety**: Preserve capital, minimize risk
3. **Yield**: Optimize returns on idle cash
4. **Compliance**: Follow investment policy

### Cash Preservation Levers

When extending runway:
1. Hiring freeze
2. Vendor renegotiation
3. Discretionary spend cuts
4. Payment term extension
5. Revenue acceleration
6. Bridge financing

## Accounting Operations

### Close Process

**Month-End Timeline:**
- Day 1-3: Transaction cutoff
- Day 3-5: Reconciliations
- Day 5-7: Accruals and adjustments
- Day 7-10: Management review
- Day 10-12: Final close

**Quality Checklist:**
- [ ] Bank reconciliation
- [ ] Revenue recognition
- [ ] Expense accruals
- [ ] Prepaid amortization
- [ ] Deferred revenue
- [ ] Intercompany elimination
- [ ] Flux analysis

### Revenue Recognition (ASC 606)

**Five-Step Model:**
1. Identify the contract
2. Identify performance obligations
3. Determine transaction price
4. Allocate price to obligations
5. Recognize revenue when satisfied

**Common SaaS Considerations:**
- Subscription vs usage
- Implementation services
- Professional services
- Multi-year contracts
- Discounts and credits

## Risk Management

### Financial Risk Categories

**Market Risk:**
- Interest rate exposure
- Foreign exchange exposure
- Customer concentration

**Credit Risk:**
- Customer creditworthiness
- AR aging management
- Bad debt reserves

**Operational Risk:**
- Internal controls
- Fraud prevention
- Systems reliability

### Insurance Coverage

Essential policies:
- Directors & Officers (D&O)
- Errors & Omissions (E&O)
- Cyber liability
- General liability
- Workers compensation
- Key person insurance

## Common Scenarios

### Scenario: Runway Concerns

When cash runway drops below 12 months:
1. Model scenarios (growth vs conservation)
2. Identify quick wins on spend
3. Accelerate collections efforts
4. Explore bridge financing
5. Communicate to board proactively

### Scenario: Audit Preparation

First audit checklist:
1. Select auditor (Big 4 or regional)
2. Prepare accounting policies
3. Document internal controls
4. Gather supporting documentation
5. Schedule interim fieldwork
6. Management representation letter

### Scenario: M&A Financial Diligence

Acquirer requests:
- Quality of earnings analysis
- Working capital normalization
- Customer cohort data
- Expense categorization
- Liability identification
- Tax exposure assessment

## Reference Materials

- `references/financial_modeling.md` - Model building guide
- `references/saas_metrics.md` - SaaS metrics deep dive
- `references/accounting_policies.md` - Policy documentation
- `references/audit_prep.md` - Audit readiness guide

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
