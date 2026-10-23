---
name: marketing-psychology
description: >
  Apply behavioral psychology, cognitive biases, and 70+ mental models to
  marketing for conversion optimization, pricing, copy, and campaigns. Use for
  persuasion, behavioral science, why people buy, consumer behavior, or
  neuromarketing.
license: MIT
metadata:
  version: 1.1.0
  author: borghei
  category: marketing
  domain: psychology
  updated: 2026-06-15
  tags:
    - behavioral-psychology
    - cognitive-biases
    - persuasion
    - conversion
    - pricing-psychology
---
# Marketing Psychology

Applied behavioral science for marketing — identifying which psychological principles apply to specific challenges and showing exactly how to implement them. The skill diagnoses behavioral barriers, prescribes 2-3 relevant principles from a catalog of 70+ mental models, and turns them into concrete, testable changes to landing pages, pricing, email, copy, and ads.

## Core Capabilities

- **Behavioral diagnosis** — map the decision journey, identify barriers (cognitive load, choice paralysis, trust deficit, friction), and prescribe matching principles
- **Mental model catalog** — 70+ principles across buyer psychology, persuasion/influence, pricing, design/UX, and growth
- **Application by challenge** — principle-by-principle playbooks for landing pages, pricing pages, email, churn reduction, and ad creative
- **Pricing & conversion frameworks** — three-tier/decoy pricing design, the trust cascade, the micro-commitment ladder
- **Copy techniques** — loss vs. gain framing, specificity bias, future pacing
- **Ethical application** — the persuasion/manipulation line, anti-dark-pattern boundaries, A/B testing discipline

## When to Use

- A page, pricing tier, email, or ad is underperforming and you need a behavioral root-cause diagnosis
- You are designing or optimizing a pricing page (anchoring, decoy, charm pricing, tier structure)
- You want to apply psychology to copy or campaign creative with specific, testable changes
- You need to audit existing assets for missing persuasion principles or dark patterns

## Clarify First

What most shapes this skill's output is the asset and the behavior you want from it, since the skill prescribes only 2-3 principles out of 70+. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Asset and desired behavior:** landing pages, pricing pages, email and ads each have their own principle tables in `references/application-playbooks.md`. Whether the goal is a click, a purchase, a share or a return visit narrows the catalog to the principles that address that barrier.
- **Audience:** what works for consumer SaaS may not work for enterprise buyers, and cultural context changes how framing and urgency land. A skeptical buyer needs trust signals more than scarcity.

If a marketing context document exists (the one the marketing-context skill builds), start from it and ask only about the gaps. Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

### Diagnose Why Something Is Not Converting
1. Identify the desired behavior (click, buy, share, return)
2. Identify the current friction (too many choices, unclear value, no urgency)
3. Map the visitor's emotional state (excited, skeptical, confused, impatient)
4. Match to applicable principles from `references/mental-models.md`
5. Implement 2-3 principle-based changes with specific execution

### Apply Psychology to a Marketing Asset
1. Select the asset (landing page, pricing page, email, ad)
2. Review the applicable psychology in `references/application-playbooks.md`
3. Choose 3-5 principles to apply
4. Implement each with the specific technique described
5. Measure the impact through A/B testing

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/mental-models.md](references/mental-models.md)** — full catalog of 70+ principles (buyer psychology, persuasion, pricing, design/UX, growth) with definitions and marketing applications. Read when matching a barrier to the principle that addresses it.
- **[references/application-playbooks.md](references/application-playbooks.md)** — behavioral diagnosis workflows, principle-by-challenge tables (landing pages, pricing, email, churn, ads), pricing framework, trust cascade, micro-commitment ladder, and copy techniques. Read when diagnosing a problem or applying psychology to an asset.
- **[references/ethics-and-quality.md](references/ethics-and-quality.md)** — ethical guidelines (persuasion vs. manipulation), best practices, troubleshooting table, and success criteria. Read when judging whether a technique is ethical or hardening an implementation.

## Python Automation Tools

- **`scripts/persuasion_auditor.py`** — audits copy for Cialdini's 7 principles plus behavioral economics techniques; flags what's applied and what's missing.
- **`scripts/cognitive_bias_checker.py`** — identifies cognitive biases leveraged (or missed) in copy, pricing pages, and landing pages.
- **`scripts/pricing_psychology_analyzer.py`** — analyzes pricing page structure for anchoring, decoy effect, charm pricing, framing, and tier design.

```bash
python scripts/persuasion_auditor.py page.html
python scripts/cognitive_bias_checker.py pricing_page.html --json
python scripts/pricing_psychology_analyzer.py pricing.json
```

## Scope & Limitations

**In Scope:** Behavioral psychology principles applied to marketing, conversion optimization, pricing strategy, copy improvement, campaign design. 70+ mental models with implementation guides.

**Out of Scope:** Academic psychology research, clinical applications, UX research methodology (use product-team), A/B test statistical analysis tools, consumer psychology outside marketing context.

**Limitations:** Psychology provides hypotheses, not certainties. All changes must be A/B tested. What works for consumer SaaS may not work for enterprise. Cultural context matters significantly. Principles should be applied ethically — persuasion that helps customers make good decisions, not manipulation.

## Integration Points

- **Copywriting** — Apply psychological principles when writing page copy (headlines, CTAs, objection handling).
- **Landing Page Generator** — Use psychology to guide page structure and section ordering.
- **Paid Ads** — Apply ad-specific psychology (mere exposure, contrast effect, curiosity gap) to creative.
- **Pricing** — Apply pricing psychology (anchoring, decoy, charm pricing) to pricing page design.
- **Copy Editing** — Use the Heightened Emotion sweep to apply psychology during editorial review.
- **Marketing Context** — Understanding customer psychology informs positioning and messaging strategy.
