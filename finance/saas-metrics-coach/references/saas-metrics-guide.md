# SaaS Metrics Comprehensive Guide

## Revenue Metrics

### MRR Components

MRR is the foundation of SaaS financial analysis. It decomposes into:

1. **New MRR** - Revenue from brand new customers acquired this period
2. **Expansion MRR** - Additional revenue from existing customers (upgrades, add-ons, seat expansion)
3. **Contraction MRR** - Revenue reduction from existing customers (downgrades, seat reduction)
4. **Churned MRR** - Revenue lost from customers who cancelled entirely
5. **Reactivation MRR** - Revenue from previously churned customers who return

**Net New MRR** = New + Expansion + Reactivation - Contraction - Churned

### ARR Calculation

ARR = MRR x 12. Use ARR for annual planning and investor reporting. Use MRR for operational tracking.

For contracts with annual billing: ARR = Annual Contract Value. Do not multiply monthly equivalent by 12 if the contract is already annual.

### Revenue Recognition

- Recognize subscription revenue ratably over the service period
- One-time fees (setup, onboarding) recognized when service delivered
- Usage-based revenue recognized as consumed
- Annual prepayments create deferred revenue liability

## Churn Metrics

### Logo Churn vs Revenue Churn

- **Logo Churn Rate** = Customers Lost / Beginning Customers
- **Revenue Churn Rate** = MRR Lost / Beginning MRR

Revenue churn is more important than logo churn. Losing 10 small customers matters less than losing 1 enterprise customer.

### Gross vs Net Churn

- **Gross Revenue Churn** = (Churned MRR + Contraction MRR) / Beginning MRR
- **Net Revenue Churn** = (Churned MRR + Contraction MRR - Expansion MRR) / Beginning MRR

Net negative churn (NRR > 100%) means expansion from existing customers exceeds losses. This is the holy grail of SaaS.

### Churn Analysis Framework

1. **Segment by plan tier** - Enterprise vs SMB churn patterns differ
2. **Segment by cohort** - Are newer cohorts churning faster or slower?
3. **Segment by acquisition channel** - Which channels produce stickier customers?
4. **Time-based patterns** - Is there a "danger zone" month where most churn happens?
5. **Voluntary vs involuntary** - Failed payments vs active cancellations need different interventions

## Cohort Analysis

### Building Cohort Tables

Group customers by their signup month (or week/quarter). Track what percentage of each cohort remains active in subsequent periods.

**Reading cohort tables:**
- Each row = one cohort (e.g., Jan 2025 signups)
- Each column = months since signup (Month 0, Month 1, Month 2...)
- Values = retention rate (percentage of cohort still active)

### Retention Curve Shapes

- **Steep early drop, then flat** = Healthy. Users who survive month 2-3 stick around.
- **Continuous decline** = Product-market fit issue. No stable user base forming.
- **Flat then sudden drop** = Contract cliff. Likely annual contracts not renewing.
- **Improving over cohorts** = Good sign. Product improvements driving better retention.

### Key Cohort Metrics

- **Month 1 Retention** - Activation quality (target: > 80%)
- **Month 3 Retention** - Product-market fit signal (target: > 60%)
- **Month 12 Retention** - Long-term value indicator (target: > 40%)

## Unit Economics

### LTV Calculation Methods

**Simple method:** LTV = ARPU / Monthly Churn Rate

**Gross margin adjusted:** LTV = (ARPU x Gross Margin) / Monthly Churn Rate

**DCF method:** LTV = Sum of (Monthly Revenue x Gross Margin x Discount Factor) for expected lifetime

Use gross-margin-adjusted LTV for most purposes. The simple method overstates value by ignoring COGS.

### CAC Calculation

**Fully-loaded CAC** = (All Sales + Marketing Costs) / New Customers

Include: salaries, commissions, ad spend, tools, events, content production costs.

**Blended vs Paid CAC:**
- Blended CAC includes organic acquisitions (lower)
- Paid CAC isolates paid channel efficiency (higher but more actionable)

### LTV:CAC Ratio Interpretation

| Ratio | Interpretation | Action |
|-------|---------------|--------|
| < 1:1 | Losing money on every customer | Stop spending, fix retention or pricing |
| 1:1 - 3:1 | Marginal or break-even | Optimize funnel, reduce CAC, improve retention |
| 3:1 - 5:1 | Healthy and sustainable | Maintain, consider scaling spend |
| > 5:1 | Under-investing in growth | Increase marketing spend aggressively |

### CAC Payback Period

**Payback** = CAC / (ARPU x Gross Margin)

Measures months to recover customer acquisition cost. Under 12 months is strong. Over 18 months strains cash flow. Over 24 months is dangerous without significant funding runway.

## Growth Metrics

### Growth Rate Calculations

- **MoM Growth** = (Current MRR - Prior MRR) / Prior MRR
- **QoQ Growth** = (Current Quarter MRR - Prior Quarter MRR) / Prior Quarter MRR
- **YoY Growth** = (Current MRR - Same Month Last Year MRR) / Same Month Last Year MRR
- **CMGR (Compound Monthly Growth Rate)** = (End MRR / Start MRR)^(1/months) - 1

### The Rule of 40

Growth Rate + Profit Margin >= 40% indicates a healthy SaaS business.

- High growth, low margin: Acceptable if investing for scale
- Low growth, high margin: Acceptable if market is mature
- Both low: Fundamental business model issues

### Quick Ratio (SaaS)

SaaS Quick Ratio = (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)

- < 1: Shrinking (losing more than gaining)
- 1-2: Slow growth, high relative churn
- 2-4: Healthy growth with manageable churn
- > 4: Exceptional efficiency

## Benchmarks by Stage

### Seed Stage ($0-$1M ARR)
- Focus: Product-market fit, not metrics optimization
- Acceptable churn: Higher (learning phase)
- Key metric: Month 1 retention, qualitative feedback

### Series A ($1M-$5M ARR)
- Monthly growth: 15-20%
- Gross churn: < 5% monthly
- LTV:CAC: > 3:1
- Key metric: Net revenue retention

### Series B ($5M-$20M ARR)
- Monthly growth: 10-15%
- Net revenue retention: > 110%
- CAC payback: < 18 months
- Key metric: Sales efficiency

### Growth Stage ($20M+ ARR)
- YoY growth: > 50%
- Net revenue retention: > 120%
- Rule of 40: > 40%
- Key metric: Free cash flow margin
