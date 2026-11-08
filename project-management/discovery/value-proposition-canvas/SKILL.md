---
name: value-proposition-canvas
description: >
  Maps one segment's jobs, pains and gains against your product's relievers and creators
  and checks fit. Use when testing whether an offer matches what customers care about,
  or positioning a product for one segment.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-discovery
  updated: 2026-11-08
  tech-stack: value-proposition, jobs-to-be-done, strategyzer, product-market-fit
  tags:
    - value-proposition-canvas
    - strategyzer
    - product-market-fit
    - jobs-to-be-done
---
# Value Proposition Canvas Expert

## Overview

The Value Proposition Canvas (VPC) is the canonical Strategyzer tool for designing and testing the fit between what customers care about and what your product offers. It is the "zoom-in" companion to the Business Model Canvas, focused on the two most failure-prone blocks: Customer Segments and Value Propositions. Where the Business Model Canvas asks "is this a viable business?", the VPC asks "are we building something customers actually want?"

Fit is reached when every top-ranked job, pain and gain in the Customer Profile has a matching reliever or creator in the Value Map. This skill owns the offer-design step; discovering why customers switch belongs to `jtbd-workshop`, and running the interviews to `customer-interview-script`.

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

Before building the canvas, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The one segment:** the VPC is segment-level; one canvas per segment (defines whose Customer Profile you fill).
- **Customer evidence source:** interviews/synthesis vs team assumptions (jobs/pains/gains in the team's own words is the #1 way the canvas becomes fiction).
- **Which fit level:** problem-solution / product-market / business-model (sets the validation method: interviews vs behavior vs unit economics).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

The workflow, start to finish:

1. Pick one segment; run 5-7 interviews via `discovery/customer-interview-script/`.
2. Fill the Customer Profile (jobs/pains/gains, ranked) from `discovery/interview-synthesis/` themes; then draft the Value Map so each top item has a pain reliever or gain creator.
3. Run `assets/fit_validation_checklist.md`, list the top unaddressed pains/gains, and feed the canvas into `execution/create-prd/` Sections 5-6.
4. Verify that every profile item comes from interview evidence in the customer's words, each top-3 pain and gain has a reliever or creator, and the unaddressed items are listed rather than dropped before calling it done.

See `references/canvas-construction-playbook.md` for the full two-side method, three fit levels, template, worked example, and troubleshooting.

## Anti-Patterns

### Every pain marked Extreme
**Mistake:** Twelve pains, all tagged Extreme, and ten gains, all Essential.
**Why it happens:** Each item felt important when the customer said it, and ranking means demoting someone's point.
**Instead:** Force-rank jobs, pains and gains. Keep the top severity tier under 30% of items, and aim the Value Map at the top one or two first.

### Customer Profile written after the solution
**Mistake:** The team has already decided to build an AI assistant, then writes pains and gains that the assistant happens to solve.
**Why it happens:** The canvas is often started to justify a plan that already has momentum.
**Instead:** Build the Customer Profile from interviews before the Value Map is decided, using `discovery/interview-synthesis/` themes in customer language. Then check the Value Map against it element by element.

### Pain relievers with no matching pain
**Mistake:** The Value Map lists "real-time collaboration" as a pain reliever, but no pain in the Customer Profile relates to collaboration.
**Why it happens:** Teams list what the product can do and file each capability under a heading.
**Instead:** Name the specific pain each reliever addresses. If you cannot, drop the reliever or re-interview to learn whether a pain was missed. Apply the same test to gain creators.

Nine more, each with a bad and a good example: `references/red-flags.md`.

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

## Files

| File | Purpose |
|------|---------|
| `assets/vpc_template.md`, `assets/customer_profile_worksheet.md`, `assets/value_map_worksheet.md`, `assets/fit_validation_checklist.md` | Canvas, worksheets, fit checklist |
| `references/canvas-construction-playbook.md`, `references/value-proposition-design-guide.md`, `references/red-flags.md` | Method, background, failure modes |
| `examples/dev-tools-platform-engineer-vpc.md` | Worked canvas |
