---
name: pricing-strategy
description: "Designs and optimizes SaaS pricing covering value metric selection, tier architecture, price point research, pricing page design, price increase execution, and competitive pricing analysis. Use when the user asks about setting prices, choosing a value metric, designing pricing tiers, running a price increase, analyzing competitor pricing, optimizing a pricing page, or evaluating freemium versus free trial models."
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  updated: 2026-03-31
  tags: [pricing, monetization, packaging, saas, value-based-pricing, revenue]
---

# Pricing Strategy

Production-grade SaaS pricing framework covering the three pricing axes (value metric, packaging, price point), value-based pricing methodology, tier architecture, pricing research, pricing page design, price increase execution, and competitive positioning.

## The Three Pricing Axes

Every pricing decision lives across three axes. The agent works through them in order — most teams skip to price point, which is backwards.

```
VALUE METRIC → PACKAGING → PRICE POINT
(what you charge for)  (what's in each tier)  (the number)
```

## Core Workflow

### 1. Select the Value Metric

The agent evaluates value metrics against four criteria:

| Question | Answer Points To |
|----------|-----------------|
| What makes a customer willing to pay MORE? | That is the value metric |
| Does the metric scale with their success? | If they grow, the vendor should grow |
| Is it easy to understand? | Complexity kills conversion |
| Is it hard to game? | Customers should not be able to work around it |

**Common value metrics:**

| Metric | Best For | Scales With Value? |
|--------|---------|-------------------|
| Per seat / user | Collaboration tools, CRMs | Yes if all users active |
| Per usage | APIs, infrastructure, AI | Yes |
| Per feature | Platform plays, modular products | Somewhat |
| Flat fee | Simple products, SMB market | No |
| Hybrid | Most mature SaaS | Yes |

**Validate:** Selected metric passes all 4 criteria; red flags checked (e.g., per-seat in a tool where 1 power user does all the work).

### 2. Design Tier Architecture

The agent structures a Good-Better-Best 3-tier model:

| Tier | Role | Pricing Rule | Feature Rule |
|------|------|-------------|-------------|
| Entry (Good) | Price-sensitive segment | Covers costs minimum | Core product, limited usage |
| Middle (Better) | Most customers land here | 2-3x entry | Everything a growing company needs |
| Top (Best) | Enterprise | 3-5x entry or custom | SSO, audit logs, SLA, dedicated support |

**Feature allocation principles:**
- Core product in all tiers (limited in Entry)
- Admin features (SSO, SCIM, audit logs) only in Top
- Support escalates: Email (48h) → Priority (24h) → Dedicated CSM
- API access: None → Rate-limited → Full

**Validate:** Exactly 3 tiers; middle tier highlighted as recommended; each tier has ≥ 3 differentiators from adjacent tier.

### 3. Set Price Points

The agent uses the pricing corridor:

```
[Cost floor] ... [Next-best alternative] ... YOUR PRICE ... [Perceived value]
```

**Steps:**
1. Define the next-best alternative (competitor, manual process, hiring)
2. Estimate value delivered (time saved × hourly rate, revenue generated, risk avoided)
3. Price at 10-20% of documented value delivered

**Validate:** Price is above cost floor, above next-best alternative, and at 10-20% of estimated value.

### 4. Run Pricing Research

The agent selects the appropriate research method:

- **Van Westendorp** (30+ respondents): Four questions to find optimal price point and acceptable range
- **MaxDiff**: Feature value ranking for tier allocation
- **Competitor Benchmarking**: Position relative to market (premium +20-40%, parity, value -10-20%)
- **Customer Interviews**: "What would you do if the price doubled?" and "How would you describe the ROI to your CFO?"

Reference: `references/pricing-research-methods.md`

**Validate:** Research method selected; if Van Westendorp, minimum 30 respondents planned.

### 5. Design Pricing Page

The agent specifies the pricing page with required elements:

**Above the fold:**
- Plan names with clear positioning
- Prices with monthly/annual toggle (annual shows "Save 20%")
- 3-5 bullet differentiators per plan
- "Most Popular" badge on middle tier

**Below the fold:**
- Full feature comparison table
- FAQ addressing: cancellation, limits, refunds, security, plan switching
- Social proof (logos, testimonials)

**Validate:** Annual pricing is default display; middle tier visually highlighted; FAQ covers top 5 purchase objections.

### 6. Execute Price Increase (When Needed)

The agent selects strategy by risk tolerance:

| Strategy | Risk | Use When |
|---------|------|---------|
| New customers only | Low | Testing market response |
| Grandfather + scheduled increase | Medium | Loyal customer base |
| Tied to new value | Low | Clear product improvements |
| Uniform increase | Medium-High | Price clearly below market |

**Timeline:** Announce at Week -4 (60+ day notice for annual); offer lock-in; new pricing live at Week 0; review at Week +12.

**Expected impact for 20-30% increase:** 5-15% churn; net positive if churn < (increase% / (100% + increase%)).

**Validate:** Revenue impact modeled at 80%, 90%, and 100% retention; communication template prepared; CS talking points ready.

## Pricing Signals and Diagnostics

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| Trial-to-paid > 40% | Underpriced | Test 20-30% increase |
| All customers on middle tier | No upsell path | Add enterprise features |
| Price unchanged for 2+ years | Inflation justifies 10-15% | Plan an increase |
| Frequent discount requests | Overpriced or poor value communication | Audit value proposition |
| Only one pricing option | No anchoring, no upsell | Add tiers |

## Anti-Patterns

1. **Copying competitor prices** — Competitor pricing reflects their cost structure and positioning, not yours. The agent always derives pricing from value delivered.
2. **Skipping value metric selection** — Jumping to price points without defining how the product charges leads to misaligned packaging. The agent works through the three axes in order.
3. **Removing value from free tier** — Taking away established free features erodes trust. The agent recommends grandfathering or adding new paid features alongside existing free ones.
4. **Hiding monthly pricing** — Only showing annual pricing creates distrust. The agent always includes a visible monthly/annual toggle.
5. **Discounting instead of packaging** — Frequent discounts signal the price is wrong. The agent recommends adding a lighter entry tier instead.

## Tools

### pricing_model_analyzer.py

Evaluates value metric alignment, tier architecture, and feature allocation. Outputs a health scorecard.

```bash
python scripts/pricing_model_analyzer.py pricing.json --format text
python scripts/pricing_model_analyzer.py pricing.json --format json
```

### price_sensitivity_calculator.py

Implements Van Westendorp Price Sensitivity Meter. Calculates optimal price point, acceptable range, and indifference price.

```bash
python scripts/price_sensitivity_calculator.py survey.json --format text
```

### price_increase_modeler.py

Models revenue impact of price increases at 80%, 90%, and 100% retention with break-even analysis.

```bash
python scripts/price_increase_modeler.py increase.json --format text
```

## Troubleshooting

| Problem | Resolution |
|---------|------------|
| Trial-to-paid above 40% | Test 20-30% price increase on new customers first |
| All customers on middle tier | Add SSO, audit logs, SLA to top tier; ensure 3-5x price jump |
| Frequent discount requests | Audit ROI messaging; consider adding lighter entry tier |
| High involuntary churn on usage pricing | Add usage bands, committed minimums, or spending caps with 80% alerts |

## References

- [Pricing Research Methods](references/pricing-research-methods.md) — Van Westendorp methodology, MaxDiff analysis, competitor benchmarking details, interview question bank
- **page-cro** — Pricing page CTA and layout optimization
- **churn-prevention** — Fix retention before raising prices
- **competitive-teardown** — Feed competitive pricing data into position map
