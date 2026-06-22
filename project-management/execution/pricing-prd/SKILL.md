---
name: pricing-prd
description: >
  Tactical PM PRD for pricing experiments and pricing-page launches. Pairs with
  business-growth/pricing-strategy. Covers packaging, willingness-to-pay,
  grandfathering, A/B design, rollback, regional pricing, and UX.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: [pricing-prd, ab-testing, packaging, van-westendorp, monetizing-innovation]
  tags: [pricing, prd, packaging, ab-test, grandfathering, monetization]
---
# Pricing PRD (Tactical)

## Overview

A pricing PRD is the tactical artifact that converts a pricing strategy into a shipped change. Where `business-growth/pricing-strategy/` decides "we are moving from per-seat to per-usage and adding an enterprise tier", a pricing PRD decides "here is the page, the experiment, the rollout, and the rollback". Most PMs underinvest in this artifact — they treat pricing as a marketing problem until the rollout breaks revenue.

This skill is opinionated about the structure of a pricing PRD (distinct from a feature PRD), the discipline of pricing experiments (small samples + revenue sensitivity == high risk of false-positive readouts), grandfathering and communication (the most-often-skipped sections that cause the most damage), A/B testing pricing without confusing customers or violating consumer-law principles, and rollback criteria written in advance rather than improvised under pressure. The frameworks behind it: Patrick Campbell's "Pricing as a feature", Ramanujam's *Monetizing Innovation*, Van Westendorp's Price Sensitivity Meter, Reforge pricing experimentation, and Stripe's pricing-page patterns.

## Core Capabilities

- **PRD structure** — the 13-section pricing PRD: pricing model, packaging, grandfathering, communication plan, A/B design, rollback, regional pricing, on top of the standard PRD spine.
- **Pricing model & packaging decisions** — tier / usage / hybrid / per-seat / outcome-based selection with rationale; value carriers, tier boundaries, trial mechanisms.
- **Willingness-to-pay research** — Van Westendorp, conjoint, and revealed-preference experiments.
- **Experiment discipline** — hypothesis, primary metric, MDE, sample size, holdout, stop conditions, mix-shift detection.
- **Risk management** — grandfathering policy, multi-channel communication plan, pre-written rollback thresholds, regional/compliance decisions.

## When to Use

- Launching a new pricing model or tier
- Updating prices on existing packages
- Adding usage-based components to a previously flat-fee product
- Reshaping packaging (moving features between tiers, sunsetting a tier, adding entitlements)
- Running a pricing A/B test
- Localizing prices to a new region or currency
- Splitting self-serve and enterprise pricing surfaces

**When NOT to use:** for the strategic question "should we change pricing at all?" (use `business-growth/pricing-strategy/`); for the financial-modeling side (use `finance/` skills); for SKU/billing implementation (engineering tickets generated from this PRD).

## Clarify First

Before generating the pricing PRD, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Pricing model change** — tier / usage / hybrid / per-seat / outcome-based shift (drives the pricing-model + packaging sections)
- [ ] **Existing customers' fate** — the grandfathering policy (drives the most-skipped grandfathering + communication sections that cause the most damage)
- [ ] **Experiment vs hard launch** — A/B test or direct rollout (drives the experiment-design section: hypothesis, MDE, holdout)
- [ ] **Rollback trigger** — the revenue/conversion threshold that aborts the change (drives the pre-written rollback criteria)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

Pull the reference that matches the task; keep this file lean and load detail on demand.

- **[references/pricing-prd-playbook.md](references/pricing-prd-playbook.md)** — the full end-to-end playbook: pricing-PRD-vs-feature-PRD table, model decision, willingness-to-pay methods, packaging, grandfathering, communication plan, A/B test design, rollback criteria, regional pricing, UX checklist, anti-patterns, 12-step workflow, tools/assets table, troubleshooting, success criteria, and source frameworks. Read when authoring any pricing PRD.
- **[references/pricing-experimentation-guide.md](references/pricing-experimentation-guide.md)** — deep guide on pricing A/B tests, mix-shift detection, and readout windows. Read when designing or reading out a pricing experiment.
- **[references/packaging-frameworks.md](references/packaging-frameworks.md)** — tier vs usage vs hybrid frameworks and Ramanujam-style packaging. Read when deciding what goes in which tier.
- **[references/red-flags.md](references/red-flags.md)** — concrete examples of how pricing PRDs go wrong and how to fix them. Read when reviewing a draft for quality.
- **assets/pricing_prd_template.md** — 13-section pricing PRD template. Use to author the artifact.
- **assets/pricing_experiment_design.md** — A/B test design worksheet (hypothesis, MDE, holdout). Use when planning a test.
- **assets/pricing_page_checklist.md** — UX review checklist for the pricing page. Use before shipping the page.
- **assets/grandfathering_communication_template.md** — customer email for grandfathering communication. Use when drafting the comm plan.

## Scope & Limitations

**In Scope:** Tactical pricing PRD authoring, willingness-to-pay research summary (Van Westendorp, conjoint), packaging decisions, grandfathering policy, customer/sales/support communication plan, A/B test design, rollback criteria, regional pricing decisions, pricing-page UX checklist, anti-pattern avoidance.

**Out of Scope:** Strategic pricing question "should we change pricing at all?" (see `business-growth/pricing-strategy/`). Financial modeling and revenue projection (see `finance/`). Billing and subscription-management implementation (engineering tickets). Detailed conjoint analysis methodology (specialist tooling). Legal review of pricing terms in regulated jurisdictions (must involve actual legal counsel; this skill is not legal advice).

**Important Caveats:**
- Pricing changes have asymmetric risk. A bad pricing change can erase a year of growth. The PRD discipline (rollback criteria, holdout, communication plan) is risk management, not bureaucracy.
- A/B testing pricing on identified customers carries consumer-law risk in some jurisdictions. When in doubt, test on anonymous visitors only and consult legal.
- The Van Westendorp method has known limitations — stated preference rather than revealed, feature-blind, segment-aggregated. Use as one input among three, not as the answer.
- Pricing-page UX changes can be confounded with pricing-model changes in A/B tests. Run UX-only experiments separately from model-change experiments to attribute the lift correctly.

## Integration Points

| Integration | Direction | What flows |
|---|---|---|
| `business-growth/pricing-strategy/` | Receives from | Strategic direction (new model, new tier, new segment) becomes the input to the tactical PRD |
| `create-prd/` | Extends | Pricing PRD uses sections 1-2 of standard PRD plus 11 pricing-specific sections |
| `feature-flag-strategy/` | Feeds into | Pricing rollout uses feature flags for tier entitlements and rollback |
| `activation-funnel/` | Bidirectional | Pricing changes affect activation rates; activation funnel measures the impact |
| `customer-feedback-triage/` | Receives from | Pricing-related feedback clusters surface willingness-to-pay signals and bill-shock issues |
| `finance/` | Bidirectional | Finance models the revenue projection; pricing PRD constrains the model assumptions |
| `senior-pm/` | Feeds into | Pricing change becomes a portfolio risk and an executive update item |
| `prfaq/` | Feeds into | A new pricing model often warrants a PR/FAQ for internal alignment |
| `eol-communication/` | Pattern overlap | EOL of a pricing tier uses similar grandfathering and communication patterns |
| `launch-playbook/` | Feeds into | Pricing-page launch follows standard launch playbook for internal/external comm coordination |
