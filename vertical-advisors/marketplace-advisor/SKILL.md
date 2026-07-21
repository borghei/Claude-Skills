---
name: marketplace-advisor
description: >
  Strategic advisory for two-sided marketplace founders on chicken-and-egg, take
  rates, liquidity, and network effects. Use when scoping a marketplace idea or
  scoring health, or mentioning marketplace, take rate, liquidity, or network effects.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: vertical-advisors
  domain: marketplace
  updated: 2026-05-04
  python-tools: marketplace_health_scorer.py
  tech-stack: marketplace, network-effects
---

# Marketplace Advisor

Strategic frameworks for two-sided and multi-sided marketplace founders, operators, and product leaders. Marketplaces have distinctive economics — most ecommerce / SaaS playbooks don't translate.

---

## Keywords

marketplace, two-sided market, three-sided market, multi-sided market, supply, demand, liquidity, take rate, network effects, chicken and egg, GMV, repeat rate, fill rate, supply density

---

## Clarify First

Before scoring, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Measurement unit** — whole marketplace or one liquid segment (city/category)? Liquidity beats GMV; a blended global number can hide a broken core (sets what the score actually describes)
- [ ] **Category + take rate** — benchmarks vary widely (Etsy ~6.5% vs Uber ~25-30%), so the take-rate-sustainability dimension is meaningless without the category
- [ ] **Supply, demand, and fill rate** — drive the liquidity and balance dimensions, usually the binding constraint
- [ ] **Repeat rate** — drives repeat-strength; a low repeat often signals off-platform leakage rather than a healthy marketplace

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the score.

## Quick Start

```bash
python scripts/marketplace_health_scorer.py metrics.json
```

Scores marketplace health across liquidity, supply/demand balance, take rate sustainability, repeat rate, and network-effect strength.

---

## Core Workflows

### Workflow 1: Marketplace Health Diagnostic
1. Capture key metrics: GMV, take rate, supply, demand, fill rate, repeat rate
2. Run: `python scripts/marketplace_health_scorer.py metrics.json`
3. Identify which dimension is the constraint (usually one of: not enough supply, not enough demand, low repeat, weak liquidity, take rate too high or too low)
4. Plan one focused intervention; don't try to fix all five at once

**Time Estimate:** 2-4 weeks per diagnostic.

### Workflow 2: Chicken-and-Egg Strategy
1. Read `references/marketplace_dynamics.md`
2. Identify your "constrained side" (usually supply for new marketplaces)
3. Pick a strategy: subsidize the constrained side, single-player mode, vertical wedge, geographic concentration
4. Measure liquidity in the smallest viable unit (one city, one category, one buyer segment)

**Time Estimate:** 6-12 months for first liquid segment.

### Workflow 3: Take-Rate Decision
1. Read `references/take_rate_design.md`
2. Benchmark category norms (eBay 10-13%, Airbnb 14%, Uber 25-30%, Etsy 6.5%, vertical B2B varies)
3. Decide: high take rate (full-stack with lots of value-add) vs. low take rate (commodity matching)
4. Plan trajectory: most marketplaces *raise* take rate over time as value-adds compound

**Time Estimate:** 4-8 weeks for first take-rate decision.

---

## Tools

### marketplace_health_scorer.py

Scores marketplace health on five dimensions: liquidity, balance, take-rate sustainability, repeat-rate strength, and supply density.

```bash
python scripts/marketplace_health_scorer.py metrics.json
python scripts/marketplace_health_scorer.py metrics.json --json
```

---

## Reference Guides

- **`references/marketplace_dynamics.md`** — Chicken-and-egg, liquidity, network effects, vertical / horizontal trade-offs
- **`references/take_rate_design.md`** — Take rate benchmarks, when to raise / lower, full-stack vs lean

---

## Templates

- **`assets/marketplace_metrics_template.json`** — Input file for the health scorer with example values

---

## Best Practices

- **Liquidity over GMV.** A marketplace with $10M GMV across 1,000 cities is mostly broken; the same GMV in 5 cities can be liquid and growing.
- **Pick a wedge.** New marketplaces almost always start narrow (single city, single category, single segment) and expand.
- **Measure repeat early.** Marketplaces without repeat are often serving as infrastructure for off-platform transactions (a leakage problem to fix or accept).
- **Take rate ratchets up, rarely down.** Start low to attract supply; add value-adds (payments, fulfillment, insurance, financing) that justify higher take rate.
- **Single-side first when possible.** Some categories let you build a tool for one side that becomes a marketplace once liquid (e.g., OpenTable started as restaurant software).
- **Beware of weak network effects.** Many "marketplaces" lack real network effects — supply on one platform doesn't make demand stickier on that platform. Examine carefully.

---

## Integration Points

- Pairs with `business-growth/pricing-strategy` — take rate is essentially marketplace pricing
- Pairs with `c-level-advisor/cs-fundraising-advisor` — marketplace investor expectations differ from SaaS
- Pairs with `marketing/landing-page-generator` for supply / demand recruitment funnels
