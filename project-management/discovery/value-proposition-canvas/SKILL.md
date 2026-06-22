---
name: value-proposition-canvas
description: >
  Strategyzer Value Proposition Canvas (Customer Profile + Value Map) with fit
  validation across problem-solution, product-market, and business-model
  dimensions. Use for jobs-to-be-done, pains/gains, and product-market-fit framing.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-discovery
  updated: 2026-06-15
  tech-stack: value-proposition, jobs-to-be-done, strategyzer, product-market-fit
---
# Value Proposition Canvas Expert

## Overview

The Value Proposition Canvas (VPC) is the canonical Strategyzer tool for designing and testing the fit between what customers care about and what your product offers. It is the "zoom-in" companion to the Business Model Canvas, focused on the two most failure-prone blocks: Customer Segments and Value Propositions. Where the Business Model Canvas asks "is this a viable business?", the VPC asks "are we building something customers actually want?"

The canvas has two sides. The **Customer Profile** describes the customer's world in their language -- jobs they are trying to do, pains they experience, and gains they aspire to. The **Value Map** describes the product's response -- the products and services offered, the pain relievers they include, and the gain creators they enable. Fit is achieved when the Value Map mirrors the Customer Profile element-by-element. The method follows Alexander Osterwalder and Yves Pigneur's *Value Proposition Design* (2014).

## Core Capabilities

- **Customer Profile construction** -- jobs (functional/social/emotional), pains, and gains, each ranked (importance, severity x frequency, desirability).
- **Value Map construction** -- products & services, pain relievers, and gain creators, each mapped to a specific profile element.
- **Three-level fit validation** -- problem-solution fit (interviews), product-market fit (behavior), business-model fit (unit economics).
- **Artifacts** -- markdown canvas template, worked example, and a fit-validation checklist that flags strong/partial/absent fit.

## When to Use

- **Pre-PRD framing** -- validate the value proposition and customer profile before writing requirements.
- **Solution refinement** -- diagnose whether weak traction is a wrong-segment (Customer Profile) or wrong-response (Value Map) problem.
- **New segment expansion** -- build a separate VPC per segment to test fit.
- **Pricing and packaging** -- pains/gains rank-ordering informs which features go in which tier.
- **Sales enablement** -- pain relievers and gain creators become talking points and proof points.

## Clarify First

Before building the canvas, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The one segment** — the VPC is segment-level; one canvas per segment (defines whose Customer Profile you fill)
- [ ] **Customer evidence source** — interviews/synthesis vs team assumptions (jobs/pains/gains in the team's own words is the #1 way the canvas becomes fiction)
- [ ] **Which fit level** — problem-solution / product-market / business-model (sets the validation method: interviews vs behavior vs unit economics)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. Pick one segment; run 5-7 interviews via `discovery/customer-interview-script/`.
2. Fill the Customer Profile (jobs/pains/gains, ranked) from `discovery/interview-synthesis/` themes; then draft the Value Map so each top item has a pain reliever or gain creator.
3. Run `assets/fit_validation_checklist.md`, list the top unaddressed pains/gains, and feed the canvas into `execution/create-prd/` Sections 5-6.

See `references/canvas-construction-playbook.md` for the full two-side method, three fit levels, template, worked example, and troubleshooting.

## References

- `references/canvas-construction-playbook.md` -- read this when building a canvas end-to-end: both sides in detail, the three levels of fit, the markdown canvas template, a full worked example (Finance Reconciliation SaaS), common mistakes, workflow, troubleshooting, and success criteria.
- `references/value-proposition-design-guide.md` -- read this for the deep Strategyzer methodology with additional worked examples.
- `references/red-flags.md` -- read this when reviewing a completed canvas for anti-patterns (team-language, forced fit, fit-level confusion) before relying on it.
- `assets/vpc_template.md` -- markdown canvas template.
- `assets/customer_profile_worksheet.md` -- jobs/pains/gains capture worksheet.
- `assets/value_map_worksheet.md` -- products/pain-relievers/gain-creators capture worksheet.
- `assets/fit_validation_checklist.md` -- three-level fit validation checklist.

## Scope & Limitations

**In scope:** Customer Profile (jobs, pains, gains) construction and ranking; Value Map construction; problem-solution fit validation; mapping the canvas into PRD inputs (`execution/create-prd/` Sections 5 and 6); sales-enablement translation.

**Out of scope:** Business Model Canvas (sister tool, 9 blocks); unit economics and business-model fit (`finance/` skills); detailed financial modeling, LTV/CAC; persona generation (the VPC is segment-level); competitive positioning (`marketing/` or `c-level-advisor/competitive-strategy/`).

**Caveats:** the VPC is a thinking aid, not a roadmap -- solutions still need experimentation (`discovery/brainstorm-experiments/`). Problem-solution fit is the minimum bar, necessary but not sufficient for product-market fit. Strategyzer methodology is CC-BY-SA; attribute to Strategyzer / Osterwalder when sharing externally. A beautifully filled canvas with no customer interviews is fiction.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `discovery/customer-interview-script/` | Receives from | Verbatim customer quotes populate the Customer Profile |
| `discovery/interview-synthesis/` | Receives from | Themed insights become jobs, pains, and gains |
| `discovery/jtbd-workshop/` | Complementary | JTBD workshop produces the job hierarchy; VPC adds pains and gains |
| `discovery/identify-assumptions/` | Bidirectional | Unaddressed pains become risk assumptions; assumptions inform validation focus |
| `execution/create-prd/` | Feeds into | Canvas populates PRD Section 5 (Market Segments) and Section 6 (Value Propositions) |
| `execution/product-vision/` | Bidirectional | Vision defines the long-term promise; VPC validates current-day delivery |
| `execution/prioritization-frameworks/` | Feeds into | Unaddressed top pains and gains become candidate features |
| `marketing/` | Feeds into | Pain relievers and gain creators become marketing talking points and proof points |
