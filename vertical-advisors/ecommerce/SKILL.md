---
name: ecommerce-advisor
description: >
  Strategic advisory for e-commerce founders on unit economics, fulfillment models,
  payments, and channel strategy. Use when evaluating an ecommerce idea or modeling
  unit economics, or mentioning DTC, Shopify, Amazon, 3PL, or CAC.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: vertical-advisors
  domain: ecommerce
  updated: 2026-05-04
  python-tools: ecom_unit_economics_calculator.py
  tech-stack: ecommerce, retail
---

# E-commerce Advisor

Strategic frameworks for e-commerce founders, operators, and brand builders. Most ecommerce decisions are unit-economics decisions — knowing the math is the difference between a brand that compounds and one that subsidizes itself out of existence.

---

## Keywords

ecommerce, e-commerce, DTC, direct-to-consumer, Shopify, Amazon, retail, wholesale, 3PL, fulfillment, dropship, unit economics, contribution margin, CAC, AOV, LTV, returns, refunds, payment processing, interchange

---

## Clarify First

Before building the model, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Single channel or blended** — model each channel (DTC, Amazon, wholesale) separately; a blended model hides an unprofitable channel and makes contribution margin meaningless
- [ ] **AOV and COGS** — average order value and landed cost of goods (drives gross margin, the top line of the model)
- [ ] **Returns/refund rate** — returns eat margin twice (the sale plus reverse logistics), so this swings contribution margin
- [ ] **CAC basis** — true paid/blended CAC and what ad spend is counted (drives CAC payback period and break-even repeat rate)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the model.

## Quick Start

```bash
python scripts/ecom_unit_economics_calculator.py model.json
```

Calculates gross margin, contribution margin, CAC payback, and per-order profit from a structured input file.

---

## Core Workflows

### Workflow 1: Unit Economics Model
1. Build a JSON config: COGS, fulfillment cost, payment processing %, returns %, ad spend %, AOV
2. Run calculator: `python scripts/ecom_unit_economics_calculator.py model.json`
3. Identify the marginal cost line items eating most of the margin
4. Decide: cut costs, raise price, change channel mix, or kill the SKU

**Time Estimate:** 2-4 weeks for first robust model.

### Workflow 2: Fulfillment Strategy
1. Read `references/fulfillment_models.md`
2. Score each model (DTC self-fulfilled, 3PL, Amazon FBA, dropship, retail) for your stage and SKU profile
3. Migrate fulfillment as you scale — most brands change models 2-3 times in their first 3 years

**Time Estimate:** 4-8 weeks per major fulfillment transition.

### Workflow 3: Channel Strategy
1. Read `references/channel_strategy.md`
2. Decide channel mix: DTC site, Amazon, wholesale, retail, marketplace
3. Each channel has distinct unit economics — model them separately, never blend
4. Sequence: most brands start DTC, add Amazon, add wholesale / retail

**Time Estimate:** Continuous, with major decisions every 6-12 months.

---

## Tools

### ecom_unit_economics_calculator.py

Models per-order, per-month, and CAC-payback economics from a structured input.

```bash
python scripts/ecom_unit_economics_calculator.py model.json
python scripts/ecom_unit_economics_calculator.py model.json --json
```

**Input model schema** in the script's docstring; example in `assets/unit_economics_template.json`.

**Outputs:**
- Gross margin (% and absolute)
- Contribution margin (after marginal CAC)
- CAC payback period (months)
- Break-even repeat rate

---

## Reference Guides

- **`references/fulfillment_models.md`** — DTC self, 3PL, FBA, dropship, retail — when each fits
- **`references/channel_strategy.md`** — DTC site, Amazon, wholesale, retail — economics per channel

---

## Templates

- **`assets/unit_economics_template.json`** — Input file for the calculator with example values

---

## Best Practices

- **Model channels separately.** A blended LTV across DTC and Amazon hides the fact that Amazon may be unprofitable.
- **Returns and refunds compound.** A 15% return rate eats into margin twice — once on the initial sale, once on the reverse logistics.
- **Plan for inventory.** Working capital tied up in inventory is the #1 cash-flow killer for product brands.
- **Don't fall in love with revenue.** $10M revenue at 5% contribution margin is worse than $3M revenue at 30% contribution margin.
- **Be honest about CAC.** Most DTC brands subsidize CAC and call it growth. CAC payback under 6 months is the bar.
