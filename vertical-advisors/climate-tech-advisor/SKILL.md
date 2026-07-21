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
---

# Climate-Tech Advisor

Strategic frameworks for climate-tech founders, operators, and product leaders.

> **Disclaimer:** Frameworks only. Climate compliance, carbon accounting, and verification require qualified specialists. Engage GHG / climate counsel and verifiers for binding decisions.

---

## Keywords

climate, climate-tech, climate tech, carbon, GHG, greenhouse gas, scope 1, scope 2, scope 3, ESG, IRA, DOE, CSRD, SEC climate rule, net zero, decarbonization, carbon removal, CDR, EU Green Deal, taxonomy, MRV

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

## Integration Points

- Pairs with `c-level-advisor/cfo-advisor` — climate-tech often combines grant + equity + project finance
- Pairs with `legal/` — IRA tax-credit qualification, carbon-credit contracts
- Pairs with `ra-qm-team/` — some categories overlap with regulated industries (chemicals, energy, food)
