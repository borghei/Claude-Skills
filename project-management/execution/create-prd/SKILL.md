---
name: create-prd
description: >
  PRD scaffolding expert that generates structured product requirements
  documents using an 8-section framework.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  python-tools: prd_scaffolder.py
  tech-stack: prd, product-requirements, documentation
---
# PRD Scaffolding Expert

## Overview

Structured product requirements document creation using a proven 8-section framework. This skill produces clear, jargon-free PRDs that communicate what to build, why it matters, and how success is measured. Every PRD generated follows a consistent structure that keeps engineering, design, and business stakeholders aligned.

### When to Use

- **New Product Initiative** -- Starting a product from scratch and need a comprehensive spec before development begins.
- **Feature Expansion** -- Adding significant functionality to an existing product that requires cross-team alignment.
- **Stakeholder Alignment** -- Need a single document that answers "what are we building and why?" for everyone involved.

## PRD Framework (8 Sections)

### Section 1: Summary

Write 2-3 sentences that a busy executive can read in 10 seconds and understand the full scope. Answer three questions: What is this? Who is it for? Why are we doing it now?

Do not use marketing language. State the product, the user, and the expected outcome plainly.

### Section 2: Contacts

A table of people involved in the decision:

| Name | Role | Responsibility |
|------|------|----------------|
| ... | Product Manager | Final decision on scope |
| ... | Engineering Lead | Technical feasibility |
| ... | Design Lead | UX direction |
| ... | Stakeholder | Business approval |

Keep this short. Only list people who will actively contribute or approve.

### Section 3: Background

Answer three questions:

1. **Context** -- What is the current state? What exists today?
2. **Why now?** -- What changed in the market, technology, or business that makes this urgent?
3. **What recently became possible?** -- New capabilities, partnerships, data, or insights that enable this initiative.

This section sets the stage. A reader who skips every other section should still understand the motivation after reading Background.

### Section 4: Objective

State the business benefit and the customer benefit separately:

- **Business benefit**: How does this move a business metric? (revenue, retention, cost reduction, market share)
- **Customer benefit**: How does this improve the user's life? (time saved, friction removed, new capability)

Then define 2-4 SMART Key Results in OKR format:

- **Objective**: [qualitative, inspirational statement]
- **KR1**: [metric] from [current] to [target] by [date]
- **KR2**: [metric] from [current] to [target] by [date]
- **KR3**: [metric] from [current] to [target] by [date]

### Section 5: Market Segment(s)

Define segments by the problems they face or jobs they need done -- not by demographics. A segment is a group of people who share a common struggle or desired outcome.

Format: "[Segment name]: People who need to [job/problem] because [context]."

Bad: "Millennials aged 25-35 in urban areas"
Good: "Time-constrained professionals who need to coordinate schedules across 3+ tools because their organization lacks a unified calendar system"

### Section 6: Value Proposition(s)

For each market segment, define:

1. **Jobs addressed** -- What tasks or goals does this product help accomplish?
2. **Gains created** -- What positive outcomes does the user experience?
3. **Pains relieved** -- What frustrations, risks, or obstacles are removed?
4. **Competitive advantage** -- Why is our approach better than existing alternatives?

Use the **Value Curve** framework to visualize where you compete, where you exceed, and where you deliberately underinvest relative to alternatives.

### Section 7: Solution

Break into subsections:

- **UX / Prototypes** -- Key screens, flows, or interaction patterns. Link to design files.
- **Key Features** -- Numbered list of features with one-sentence descriptions. Mark each as P0 (must-have), P1 (important), or P2 (nice-to-have).
- **Technology** (optional) -- Architecture decisions, integrations, or infrastructure requirements that constrain the solution.
- **Assumptions** -- Explicit list of things you believe to be true but have not validated. Each assumption should have a plan to validate it.

### Section 8: Release

- **Relative timeline** -- Use T-shirt sizes (S/M/L/XL) or Now/Next/Later rather than specific dates, unless dates are firm.
- **v1 scope** -- What ships in the first version? Draw a clear line.
- **Future versions** -- What is explicitly deferred? List it so stakeholders know it was considered but intentionally excluded.
- **Success criteria** -- When do we know v1 succeeded? Reference the Key Results from Section 4.

## Writing Principles

- **Plain language** -- No jargon, no acronyms without definition, no buzzwords.
- **One idea per sentence** -- If a sentence has "and" connecting two distinct ideas, split it.
- **Specificity over abstraction** -- "Reduce onboarding from 12 steps to 4" beats "Simplify onboarding."
- **Saved as**: `PRD-[product-name].md`

## Workflow

1. Gather context: product name, target segment, core problem.
2. Run `scripts/prd_scaffolder.py` to generate the skeleton.
3. Fill in each section using the guidance above and `references/prd-writing-guide.md`.
4. Review against the checklist in `references/prd-writing-guide.md`.
5. Share with stakeholders for feedback.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `prd_scaffolder.py` | Generate PRD skeleton | `python scripts/prd_scaffolder.py --product-name "MyProduct" --objective "Short description" --segments "Segment A, Segment B"` |

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| PRD scaffolder output is too generic | Only product name provided; objective and segments need specificity | Write a 1-2 sentence objective that states the outcome, not just the product category; define segments by jobs-to-be-done, not demographics |
| Stakeholders skip reading the PRD | Document too long, too jargon-heavy, or lacks a clear Summary section | Ensure Section 1 (Summary) answers What/Who/Why in 3 sentences; cut any section beyond 1 page that is not Section 7 |
| Engineering team builds the wrong thing | PRD focuses on solution before establishing problem context | Strengthen Section 3 (Background) and Section 5 (Market Segments); ensure problem definition precedes solution |
| PRD assumptions never validated | Assumptions listed in Section 7 but no validation plan assigned | Add a validation plan column to the Assumptions table; link each assumption to `identify-assumptions/` or `brainstorm-experiments/` |
| Scope creep after PRD approval | Section 8 (Release) does not clearly separate v1 from future versions | Be explicit about "Explicitly Deferred" items; ensure every stakeholder has seen and acknowledged the deferred list |
| PRD becomes stale during development | Treated as a static document rather than a living reference | Update after implementation decisions change; archive final state and link to retrospective notes |
| `--segments` flag parsing fails | Segments not properly comma-separated or contain special characters | Wrap the segments argument in quotes: `--segments "Segment A, Segment B"` |

## Success Criteria

- PRD passes the "10-second executive test" -- a busy executive understands scope from Section 1 alone
- All 8 sections are complete before development begins (no placeholder sections remain)
- Market segments defined by jobs-to-be-done, not demographics
- Key Results in Section 4 are measurable with baselines, targets, and deadlines
- Every assumption in Section 7 has a validation plan and owner
- PRD reviewed by PM, Engineering Lead, Design Lead, and at least one stakeholder before commitment
- v1 scope in Section 8 draws a clear line between what ships and what is explicitly deferred

## Scope & Limitations

**In Scope:**
- 8-section PRD skeleton generation with guided placeholders
- Section-by-section writing guidance following plain-language, specificity-over-abstraction principles
- Market segment definition using jobs-to-be-done framework
- Value proposition mapping with Value Curve competitive analysis
- Release planning with Now/Next/Later and explicit deferral documentation

**Out of Scope:**
- Technical architecture or system design documents (see `engineering/` skills)
- User story writing and backlog creation (see `execution/job-stories/` and `execution/wwas/`)
- Detailed UX research or usability testing plans (see `product-team/` skills)
- Financial business case modeling (see `finance/` domain skills)

**Important Caveats:**
- A PRD is a communication tool, not a contract. Treat it as a living document that evolves with implementation learning.
- The 8-section framework is a proven structure, but lightweight agile teams may need only sections 1, 3, 4, 7, and 8. Heavyweight compliance contexts (medical devices, regulated industries) may need additional sections.
- A 2025 Carnegie Mellon SEI study found that effective requirements management eliminates 50-80% of project defects. The investment in a clear PRD pays for itself in reduced rework.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `discovery/identify-assumptions/` | Receives from | Validated and "Test Now" assumptions populate PRD Section 7 with evidence |
| `discovery/brainstorm-experiments/` | Receives from | Experiment results validate or invalidate PRD assumptions |
| `discovery/pre-mortem/` | Receives from | Tiger mitigations become PRD risk sections |
| `execution/brainstorm-okrs/` | Feeds into | PRD Key Results (Section 4) align with quarterly OKR targets |
| `execution/outcome-roadmap/` | Feeds into | PRD release plan (Section 8) maps to roadmap Now/Next/Later horizons |
| `execution/prioritization-frameworks/` | Receives from | Feature priority (P0/P1/P2) in Section 7 informed by RICE/ICE scoring |
| `senior-pm/` | Feeds into | PRD stakeholder context feeds stakeholder mapper engagement plans |

## Tool Reference

### prd_scaffolder.py

Generates a complete 8-section PRD markdown skeleton with guided placeholders, market segment sections, and value proposition templates.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--product-name` | string | (required) | Name of the product (used in title and headers) |
| `--objective` | string | (required) | Short description of the product objective (1-2 sentences) |
| `--segments` | string | (required) | Comma-separated list of market segments |
| `--output` | string | stdout | Output file path; if omitted, prints to stdout |

## References

- `references/prd-writing-guide.md` -- Section-by-section writing guide and review checklist
- `assets/prd_template.md` -- Complete PRD template ready to fill in
