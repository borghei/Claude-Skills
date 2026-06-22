---
name: referral-program
description: >
  Referral and affiliate program design covering referral loop architecture,
  incentive design, trigger moment optimization, viral coefficient modeling,
  affiliate program structure, and optimization playbook.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: business-growth
  updated: 2026-06-15
  tags: [referral, affiliate, growth, viral, word-of-mouth, acquisition]
---
# Referral Program

Production-grade referral and affiliate program framework covering the 4-stage referral loop, incentive design methodology, trigger moment optimization, share mechanics, viral coefficient modeling, affiliate program architecture, and systematic optimization playbook. Designed to build programs that compound, not collect dust.

## Core Capabilities

- **Program type & loop design** — referral vs affiliate decision, plus the 4-stage loop (trigger → share → convert → reward)
- **Incentive design** — single- vs double-sided, reward types, tiered gamification, reward economics against LTV/CAC
- **Trigger & share mechanics** — in-product and email trigger points, share channel priority, first-person share copy
- **Referred-user experience** — referral landing page, attribution rules, program copy set (prompts, emails, dashboards)
- **Growth math** — K-factor modeling, revenue impact models, and lever-by-lever K improvement
- **Affiliate framework** — commission models, tier systems, partner toolkit, recruitment
- **Optimization** — diagnose-before-optimize playbook, metric benchmarks, troubleshooting, and three Python tools

## When to Use

- The user asks to "design a referral program", "launch an affiliate program", or "improve viral growth"
- The decision between customer referral vs affiliate program needs to be made
- An existing referral program has stalled (K-factor <1, low share rate, low referred-user conversion)
- Reward structure needs sizing against CAC, margin, or LTV
- Trigger moments need to be identified (when to ask, which in-product events, which lifecycle emails)
- The user says "word-of-mouth isn't working" or "we want to add a refer-a-friend flow"

## Clarify First

Before designing the referral program, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Program type** — customer referral vs affiliate (enthusiastic/social customers vs team buyers) (selects the entire framework)
- [ ] **Trigger moment** — the in-product or lifecycle point where you ask (a broken Stage 1 can't be fixed by a bigger reward at Stage 4)
- [ ] **Reward economics** — first-payment value, margin, and CAC (caps the reward at <30% of first payment)
- [ ] **Current referral rate (if any)** — decides single- vs double-sided incentive and which stage to fix first

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the deliverable.

## Quick Start

1. **Pick the program type** — use the Referral vs Affiliate Decision table (enthusiastic/social customers → referral; team buyers → affiliate).
2. **Build the loop in order** — trigger → share → convert → reward; a broken Stage 1 can't be fixed by a bigger reward at Stage 4.
3. **Size the incentive** — cap reward at <30% of first payment; go double-sided if referral rate <1%.
4. **Model and validate** — run the scripts (`referral_economics_calculator.py`, `referral_funnel_analyzer.py`, `affiliate_commission_modeler.py`) to size rewards, find the weakest stage, and model affiliate tiers.
5. **Optimize by priority** — fix awareness first, then share flow, then referred experience, then the incentive.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/loop-and-incentives.md](references/loop-and-incentives.md)** — Referral vs Affiliate decision table, the full 4-stage loop with per-stage tables, incentive design (single/double-sided, reward types, tiers, economics), and trigger moment architecture. Read when designing the core program.
- **[references/share-and-experience.md](references/share-and-experience.md)** — share channel priority, share message templates, referral landing page layout, attribution rules, and the program copy set (in-app prompt, dashboard, post-activation email). Read when building the sharing flow and referred-user experience.
- **[references/modeling-and-affiliate.md](references/modeling-and-affiliate.md)** — K-factor calculation and improvement levers, plus the full affiliate framework (commission structure, tier system, toolkit, recruitment). Read when modeling growth math or designing an affiliate program.
- **[references/optimization-and-operations.md](references/optimization-and-operations.md)** — optimization playbook, key metrics and benchmarks, revenue impact model, output artifacts, full tool reference, troubleshooting table, success criteria, and anti-patterns. Read when diagnosing a stalled program or operating the scripts.

## Scope & Limitations

**In scope:** Customer referral program design (4-stage loop), incentive structure (single-sided, double-sided, tiered), trigger moment architecture, share mechanics, referral landing page specifications, viral coefficient modeling, affiliate program framework (commission models, tier systems, recruitment), and systematic optimization playbook.

**Out of scope:** Referral landing page visual design and CRO (use page-cro), signup flow optimization for referred users (use signup-flow-cro), post-signup onboarding for referred users (use onboarding-cro), churn prevention for referred customers (use churn-prevention), and reward pricing alignment (use pricing-strategy). Scripts operate on local data only -- no integrations with referral platforms (ReferralHero, Viral Loops, PartnerStack, etc.).

**Limitations:** K-factor benchmarks assume consumer or prosumer SaaS; B2B enterprise referral programs have different dynamics (lower K but higher per-referral value). Affiliate commission benchmarks (20-30% recurring) are SaaS-specific; marketplace and e-commerce commissions follow different models. Attribution windows (30-90 day cookies) face increasing limitations from browser privacy features (Safari ITP, Chrome third-party cookie deprecation). Revenue projections are estimates based on provided conversion rates.

## Integration Points

- **pricing-strategy** -- Referral reward sizing must align with pricing margins and LTV; reward should be <30% of first payment
- **signup-flow-cro** -- Referred user signup flow should pre-fill email, show referrer context, and minimize friction
- **onboarding-cro** -- Referred users may need different onboarding path (they arrive with context from the referrer)
- **churn-prevention** -- Monitor referred customer retention separately; high referral churn wastes acquisition spend
- **page-cro** -- Referral landing page conversion optimization follows page-cro methodology
- **popup-cro** -- Post-purchase or post-milestone popups are natural referral trigger points
