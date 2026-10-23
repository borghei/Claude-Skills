---
name: climate-tech-advisor
description: >
  Strategic advisory for climate-tech founders on carbon markets, GHG accounting,
  climate regulation, and funding. Use when scoping a climate-tech idea or picking a
  category, or mentioning climate, carbon, GHG, ESG, IRA, DOE, or net-zero.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: vertical-advisors
  domain: climate-tech
  updated: 2026-05-04
  python-tools: carbon_impact_estimator.py
  tech-stack: climate, sustainability
  tags:
    - climate-tech
    - carbon-markets
    - ghg-accounting
    - climate-regulation
    - startups
---

# Climate-Tech Advisor

Strategic frameworks for climate-tech founders, operators, and product leaders.

> **Disclaimer:** Frameworks only. Climate compliance, carbon accounting, and verification require qualified specialists. Engage GHG / climate counsel and verifiers for binding decisions.

---

## Keywords

climate, climate-tech, climate tech, carbon, GHG, greenhouse gas, scope 1, scope 2, scope 3, ESG, IRA, DOE, CSRD, SEC climate rule, net zero, decarbonization, carbon removal, CDR, EU Green Deal, taxonomy, MRV

---

## Clarify First

Climate-tech advice turns on the category the business sits in and on where its impact claims and funding will be judged. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Category and physical mechanism:** Energy generation, storage, transport, industry, buildings, food and agriculture, carbon removal, or software and data. Capital intensity, time to impact, the applicable methodology and the relevant funding all follow from it. `carbon_impact_estimator.py` needs a description of what the product physically changes, not a mission statement.
- **Jurisdiction:** US, EU or elsewhere decides the funding map (DOE, USDA, IRA tax credits against the EU Innovation Fund, Horizon Europe, member-state programs) and which reporting regime customers face (CSRD, the SEC climate rule, or voluntary frameworks).
- **Stage:** The funding stack differs at pre-seed and seed, Series A, Series B and C, and the first commercial plant. Project finance only fits later, and grants need writing capacity the team may not have yet.
- **What the impact claim is for:** Internal sizing, an investor pitch, a customer's Scope 3 reporting, or carbon-credit issuance. Credit issuance needs a voluntary-market methodology (Verra, Gold Standard, Puro.earth, Isometric) and third-party verification. A CSRD-reporting customer needs audit-grade data.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

---

## Quick Start

```bash
python scripts/carbon_impact_estimator.py business_description.txt
```

Estimates rough order-of-magnitude carbon impact category and surfaces verification considerations. **Not** a verified carbon accounting result.

---

## Core Workflows

### Workflow 1: Category and Impact Sizing
1. Run estimator on business description
2. Cross-reference with `references/climate_categories.md`
3. Identify market category (energy, industry, transport, food/ag, buildings, CDR, software/data)
4. Plan a path to verifiable impact measurement

**Time Estimate:** 4-8 weeks for first sizing.

### Workflow 2: Funding Strategy
1. Read `references/climate_funding_sources.md`
2. Map to your stage and category: DOE, IRA tax credits, USDA, EU Green Deal, climate-focused VC
3. Sequence: most climate-tech blends grants + dilutive equity + (later) project finance
4. Plan grant capacity (grants take time and writing skill)

**Time Estimate:** Continuous.

### Workflow 3: GHG Accounting for Customers
1. Many climate-tech products require demonstrating GHG impact for their customers
2. Read `references/ghg_accounting_basics.md`
3. Understand Scope 1/2/3 boundaries; pick the boundaries your product affects
4. Plan MRV (Measurement, Reporting, Verification) approach
5. For customers facing CSRD, SEC climate rule, or voluntary frameworks: align reporting

**Time Estimate:** 6-12 weeks for first robust MRV plan.

---

## Tools

### carbon_impact_estimator.py

Classifies a business description into climate categories and provides order-of-magnitude impact ranges and verification considerations.

```bash
python scripts/carbon_impact_estimator.py description.txt
python scripts/carbon_impact_estimator.py description.txt --json
```

**This is a categorization tool, not a verified carbon-accounting calculator.** Real GHG accounting requires methodology selection, data collection, and (for credit issuance) third-party verification.

---

## Reference Guides

- **`references/climate_categories.md`** — Categories overview, market sizing intuition, common business model patterns
- **`references/climate_funding_sources.md`** — Grants (DOE, USDA, NSF), tax credits (IRA), prizes, climate VC
- **`references/ghg_accounting_basics.md`** — Scope 1/2/3, GHG Protocol, methodologies, MRV, verification

---

## Templates

- **`assets/climate_impact_assessment.md`** — Document template for capturing category, impact estimate, and MRV plan

---

## Best Practices

- **Quantify in tons, not adjectives.** "Significant climate impact" means nothing. "1 Mt CO2e abated annually at $50/ton" is a real claim.
- **Pick a verifiable methodology.** Voluntary carbon markets (Verra, Gold Standard, Puro.earth, Isometric) have specific methodologies. Pick before building.
- **Avoid greenwashing.** Lifecycle assessment (LCA) often shows products are 20-50% less green than initial claims. Be honest in modeling.
- **Plan for IRA / IRA expiration.** US IRA tax credits drove much of the 2023-2025 climate-tech boom. Policy can shift; build for value beyond subsidy where possible.
- **Customer-side ESG reporting matters.** Selling to a CSRD-reporting customer requires you to provide audit-grade data on Scope 3 — this is a competitive advantage if you're ready and a deal-killer if you're not.

---

## Scope & Limitations

**In Scope:**
- Category selection across energy, storage, transport, industry, buildings, food and agriculture, carbon removal, and software and data
- Keyword-based classification of a business description, with order-of-magnitude impact ranges and verification considerations, from `carbon_impact_estimator.py`
- Funding strategy that blends grants, tax credits, dilutive equity and later project finance, mapped to US and EU sources
- GHG accounting orientation (Scope 1/2/3, GHG Protocol, MRV) and how customer reporting under CSRD, the SEC climate rule or voluntary frameworks shapes the product

**Out of Scope:**
- Verified carbon accounting, lifecycle assessment or carbon-credit issuance
- IRA tax-credit qualification and carbon-credit contracts (pairs with `legal/` counsel, as noted in Integration Points)
- Detailed financial models and fundraising mechanics (see `c-level-advisor/cfo-advisor/`)
- Grant writing or applications for a specific program

**Important Caveats:**
- `carbon_impact_estimator.py` is a categorization tool. It matches keywords in your text, and its impact ranges are rough orders of magnitude, not a tonnage you can claim.
- Impact claims for credits or audit-grade customer data need a recognized methodology and third-party verification, as the disclaimer above states.
- Funding programs, tax credits and reporting rules change with policy. Check current program terms and rule status before planning around them.

---

## Integration Points

- Pairs with `c-level-advisor/cfo-advisor` — climate-tech often combines grant + equity + project finance
- Pairs with `legal/` — IRA tax-credit qualification, carbon-credit contracts
- Pairs with `ra-qm-team/` — some categories overlap with regulated industries (chemicals, energy, food)
