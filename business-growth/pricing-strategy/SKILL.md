---
name: pricing-strategy
description: >
  SaaS pricing design and optimization covering value metric selection, tier
  architecture, price point research, pricing page design, price increase
  execution, and competitive pricing analysis.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: business-growth
  updated: 2026-06-15
  tags: [pricing, monetization, packaging, saas, value-based-pricing, revenue]
---
# Pricing Strategy

Production-grade SaaS pricing framework covering the three pricing axes (value metric, packaging, price point), value-based pricing methodology, tier architecture, pricing research methods, pricing page design, price increase execution, and competitive pricing positioning. Pricing is positioning -- the right price communicates as much about your product as your marketing does.

## Core Capabilities

- **Three pricing axes (in order)** — lock the value metric (how it scales), then packaging (what's in each tier), then test the price point (the number). Most teams skip to price point; that is backwards.
- **Value metric & tier design** — select a metric that scales with customer value and is hard to game; architect Good-Better-Best tiers with deliberate feature allocation and naming.
- **Value-based pricing** — price inside the corridor (above the next-best alternative, below perceived value), at 10-20% of documented value delivered.
- **Pricing research** — Van Westendorp, MaxDiff, competitor benchmarking, willingness-to-pay interviews.
- **Pricing page, price increases & competition** — page design (above/below fold, annual toggle), price-increase playbook (strategy, timeline, comms, impact), competitive positioning and health diagnostics.

## Use when

- The user asks to "design pricing", "set prices", or "choose a value metric"
- Pricing tiers need to be restructured (Good-Better-Best, add/remove tiers, repackage features)
- A price increase is planned and needs execution design (strategy, timing, communication, grandfathering)
- Conversion on the pricing page is flat or declining
- Freemium vs free trial decision needs to be made, or the freemium tier is cannibalizing paid
- Competitor pricing shifts require a positioning response
- The user says "our pricing feels off" or asks for a pricing audit

## Clarify First

Before designing the pricing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Operating mode** — design from scratch, optimize existing, or price increase (each has a different validation gate and workflow)
- [ ] **Value metric** — how price scales (seats, usage, etc.) (must be locked before tiers and price points)
- [ ] **Current pricing + the symptom** — existing tiers and the specific failure, e.g. "middle tier too narrow" (optimize mode needs a named failure mode before any change)
- [ ] **Target segment + willingness-to-pay** — SMB vs enterprise price sensitivity (sets the value corridor and price points)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the deliverable.

## Operating Modes

- **Mode 1 — Design From Scratch:** No pricing exists or full rebuild needed. Work value metric → tier structure → price points → page design. *Validate:* value metric chosen before tier design; tiers locked before price points; price points tested against the corridor before page design.
- **Mode 2 — Optimize Existing Pricing:** Pricing exists but conversion is low, expansion flat, or customers feel mispriced. Audit, benchmark, find specific improvements. *Validate:* the diagnosis names a specific failure mode (e.g., "middle tier too narrow") before any change is proposed.
- **Mode 3 — Price Increase:** Prices need to go up without burning relationships. *Validate:* grandfather policy defined, communication window set (90+ days for annual customers), and expected churn modeled before the first notice.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/pricing-models.md](references/pricing-models.md)** — the three pricing axes, value metric selection (table, criteria, red flags), tier architecture (Good-Better-Best, feature allocation, naming), and value-based pricing corridor. Read when designing or restructuring pricing.
- **[references/research-and-page-design.md](references/research-and-page-design.md)** — Van Westendorp, MaxDiff, competitor benchmarking, WTP interviews, pricing page design, and the freemium vs free trial decision. Read when researching willingness-to-pay or designing the page.
- **[references/price-increase-and-competitive.md](references/price-increase-and-competitive.md)** — price increase strategy/timeline/comms/impact, competitive position map and positioning strategy, and pricing health signals. Read when raising prices or positioning against competitors.
- **[references/tools-and-diagnostics.md](references/tools-and-diagnostics.md)** — output artifacts, the three Python scripts (analyzer, sensitivity calculator, increase modeler), troubleshooting table, success criteria, and anti-patterns. Read when producing deliverables, running tools, or debugging a pricing problem.

## Scope & Limitations

**In scope:** Value metric selection, tier architecture design, price point research (Van Westendorp, competitor benchmarking, willingness-to-pay interviews), pricing page design specifications, price increase strategy and execution, freemium vs free trial decision frameworks, competitive pricing analysis and positioning, and pricing health diagnostics.

**Out of scope:** Pricing page visual design and CRO (use page-cro), in-app upgrade prompts and paywalls (use paywall-upgrade-cro), signup flow optimization after pricing page (use signup-flow-cro), churn intervention when churn is the root cause (use churn-prevention), and full competitive analysis beyond pricing (use competitive-teardown). Scripts do not integrate with billing systems (Stripe, Chargebee, etc.) or analytics platforms.

**Limitations:** Van Westendorp analysis requires minimum 30 survey respondents for statistical validity. Pricing benchmarks are based on aggregate SaaS industry data and vary significantly by vertical, company stage, and geography. Credit-based and usage-based pricing models (growing to 38% of SaaS in 2026) have different optimization dynamics than flat-rate or per-seat models. Price elasticity varies by customer segment -- enterprise buyers are less price-sensitive than SMB.

## Integration Points

- **page-cro** -- Pricing page layout, CTA placement, and social proof design should follow page-cro best practices
- **paywall-upgrade-cro** -- In-app upgrade screens must reflect the same tier structure and messaging as the public pricing page
- **competitive-teardown** -- Competitive pricing data from teardowns feeds directly into pricing position map and tier design
- **churn-prevention** -- Churn analysis by price point and tier informs whether pricing is causing retention issues
- **signup-flow-cro** -- Signup flow design depends on pricing model (CC-required vs free trial vs freemium)
- **revenue-operations** -- GTM efficiency metrics (LTV:CAC, Magic Number) validate whether pricing supports unit economics

## Related Skills

- **page-cro** -- Use for optimizing the pricing page conversion rate (layout, CTA, social proof). Not for pricing structure or tier design.
- **churn-prevention** -- Use when churn is the underlying issue. Fix retention before raising prices.
- **competitive-teardown** -- Use for comprehensive competitive analysis. Feed teardown pricing data into this skill.
- **paywall-upgrade-cro** -- Use for in-app upgrade prompts and paywalls. Different from public pricing page design.
- **signup-flow-cro** -- Use for optimizing the signup flow that follows pricing page conversion.
