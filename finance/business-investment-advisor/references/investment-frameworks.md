# Investment Analysis Frameworks

## Investment Scoring Methodology

### Composite Score Components

The investment screener uses a weighted composite score (0-100):

| Component | Weight | Measures |
|-----------|--------|----------|
| Return Score | 30% | Expected ROI relative to risk-adjusted benchmarks |
| Risk Score | 25% | Risk level, runway, diversification benefit |
| Growth Score | 20% | Revenue growth rate, market position |
| Efficiency Score | 15% | Gross margin, burn efficiency, unit economics |
| Payback Score | 10% | Time to recover invested capital |

### Return Score Calculation

- ROI > 30%: Score 90-100
- ROI 20-30%: Score 70-89
- ROI 10-20%: Score 50-69
- ROI 5-10%: Score 30-49
- ROI < 5%: Score 0-29

Adjust down by 10-20 points for "high" or "very_high" risk investments to create risk-adjusted return score.

### Growth Score Calculation

- Revenue growth > 100%: Score 90-100 (hypergrowth)
- Revenue growth 50-100%: Score 70-89 (strong growth)
- Revenue growth 20-50%: Score 50-69 (healthy growth)
- Revenue growth 0-20%: Score 30-49 (moderate)
- Revenue declining: Score 0-29

## Risk Assessment Matrix

### Financial Risk Factors

1. **Runway risk** - Months of cash remaining
   - > 18 months: Low risk
   - 12-18 months: Medium risk
   - 6-12 months: High risk
   - < 6 months: Critical risk

2. **Concentration risk** - Revenue dependency
   - Top customer < 10% revenue: Low
   - Top customer 10-25%: Medium
   - Top customer > 25%: High

3. **Burn rate risk** - Cash consumption relative to growth
   - Burn multiple < 1: Efficient
   - Burn multiple 1-2: Acceptable
   - Burn multiple > 2: Concerning

### Market Risk Factors

1. **Market size** - Total addressable market relative to investment thesis
2. **Competition** - Number and strength of competitors
3. **Regulatory** - Regulatory barriers or pending regulation
4. **Technology** - Platform risk, technical debt, defensibility

### Execution Risk Factors

1. **Team completeness** - Key roles filled
2. **Product maturity** - MVP, growth, or scale stage
3. **Customer validation** - Paying customers, retention data
4. **Operational scalability** - Can operations scale with growth

## Portfolio Diversification Guidelines

### Sector Allocation Targets

| Investor Type | Max Single Sector | Min Sectors | Max Single Investment |
|--------------|-------------------|-------------|----------------------|
| Conservative | 40% | 4+ | 15% |
| Moderate | 50% | 3+ | 20% |
| Aggressive | 60% | 2+ | 30% |

### Stage Diversification

Balanced portfolio across investment stages:
- **Seed/Angel:** 20-30% (highest risk, highest return potential)
- **Series A:** 30-40% (validated product, scaling risk)
- **Series B+:** 20-30% (lower risk, moderate returns)
- **Mature/Stable:** 10-20% (cash flow, portfolio anchor)

### Liquidity Management

- Maintain 10-20% in liquid or semi-liquid positions
- Plan for 5-7 year hold periods on illiquid investments
- Stagger investment timing to avoid liquidity crunches
- Reserve 20% of allocated capital for follow-on rounds

## Due Diligence Framework

### Phase 1: Initial Screening (1-2 days)

Quick assessment to determine if full DD is warranted:
- Business model viability
- Market size validation
- Team background check
- Financial summary review
- Red flag identification

### Phase 2: Deep Dive (1-3 weeks)

Comprehensive investigation across all dimensions:

**Financial DD:**
- Historical financial statements (3 years if available)
- Revenue recognition practices
- Unit economics validation
- Cash flow projections
- Cap table review
- Debt and liability analysis

**Commercial DD:**
- Customer interviews (5-10 customers)
- Market sizing methodology review
- Competitive landscape mapping
- Pricing strategy analysis
- Sales pipeline review

**Technical DD:**
- Architecture review
- Code quality assessment
- Infrastructure scalability
- Security posture
- Technical debt estimation
- IP ownership verification

**Legal DD:**
- Corporate structure
- Material contracts review
- IP assignments and patents
- Regulatory compliance
- Pending or threatened litigation
- Employment agreements

### Phase 3: Negotiation Preparation (3-5 days)

- Valuation modeling (DCF, comparables, precedent transactions)
- Term sheet drafting
- Key terms identification
- Deal structure optimization
- Governance requirements

## Industry-Specific Criteria

### SaaS Companies
- NRR > 110%
- Gross margin > 70%
- CAC payback < 18 months
- LTV:CAC > 3x
- Monthly churn < 3%
- Rule of 40 compliance

### E-Commerce
- Gross margin > 40%
- Customer repeat rate > 30%
- Inventory turnover > 6x
- CAC:First order value < 0.5
- Organic traffic > 40%

### Marketplace
- GMV growth > 50%
- Take rate stability
- Supply/demand balance
- Network effects evidence
- Disintermediation risk

### Hardware/Manufacturing
- Gross margin > 35%
- Design-to-production timeline
- Supply chain resilience
- IP moat strength
- Certification status
