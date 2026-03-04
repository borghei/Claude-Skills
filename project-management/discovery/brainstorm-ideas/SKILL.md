---
name: brainstorm-ideas
description: Product ideation expert using Product Trio approach and Opportunity Solution Trees for both new and existing products.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-03-04
  tech-stack: product-trio, opportunity-solution-tree, scamper, hmw
---

# Product Ideation Expert

## Overview

Structured product ideation for both new product creation and existing product enhancement. This skill combines the Product Trio approach (PM + Designer + Engineer perspectives) with Teresa Torres' Opportunity Solution Tree framework to generate, evaluate, and prioritize product ideas systematically.

### When to Use

- **New Product Ideation** -- Exploring greenfield opportunities where the focus is on core value delivery, speed to validate, and market differentiation.
- **Existing Product Enhancement** -- Identifying opportunities within a live product using the Opportunity Solution Tree to connect desired outcomes to concrete solutions.

## Methodology

### Phase 1: Frame the Problem Space

Before generating ideas, establish clarity on the context:

1. **Define the Target Outcome** -- What measurable result are we trying to achieve? (e.g., increase activation rate by 15%, reduce churn by 10%)
2. **Identify the Target Segment** -- Who specifically are we solving for? Include behavioral and situational context, not just demographics.
3. **Map Known Constraints** -- Budget, timeline, technical platform, regulatory requirements, team capacity.

### Phase 2: Product Trio Ideation

Generate 5 ideas from each of the three perspectives (15 total):

**Product Manager Perspective (5 ideas)**
Focus: Business value, market positioning, customer pain points, strategic alignment
- What problems do customers report most frequently?
- Where are competitors weak that we could be strong?
- Which segments are underserved by current solutions?
- What would make customers willing to pay more or switch?
- How does this connect to our strategic objectives?

**Designer Perspective (5 ideas)**
Focus: User experience, workflows, accessibility, delight, friction reduction
- Where do users drop off or struggle in current flows?
- What tasks take too many steps or too much cognitive load?
- How could we surprise users with unexpected value?
- What accessibility gaps exist that exclude potential users?
- Where can we reduce time-to-value for new users?

**Engineer Perspective (5 ideas)**
Focus: Technical feasibility, scalability, platform capabilities, integration opportunities
- What new capabilities does our tech stack enable?
- Which features could we build quickly with high impact?
- Where could automation replace manual processes?
- What data do we have that we are not leveraging?
- Which technical debt, if resolved, would unlock new possibilities?

### Phase 3: Approach by Product Type

#### For New Products

Apply these lenses to each idea:

| Lens | Question |
|------|----------|
| **Core Value** | Does this idea deliver a single, clear value proposition? |
| **Speed to Validate** | Can we test the core assumption in under 2 weeks? |
| **Differentiation** | Why would someone choose this over existing alternatives? |
| **Market Timing** | Is the market ready for this? What tailwinds exist? |
| **Scalability** | Can this grow beyond the initial use case? |

#### For Existing Products (Opportunity Solution Tree)

Follow Teresa Torres' Continuous Discovery Habits framework:

```
Desired Outcome
├── Opportunity 1 (unmet need / pain point / desire)
│   ├── Solution A
│   ├── Solution B
│   └── Solution C
├── Opportunity 2
│   ├── Solution D
│   └── Solution E
└── Opportunity 3
    ├── Solution F
    └── Solution G
```

1. **Start with the outcome** -- The metric or business result you want to move.
2. **Map opportunities** -- Interview-driven insights about what customers need, want, or struggle with.
3. **Generate solutions per opportunity** -- Each opportunity gets multiple potential solutions.
4. **Compare and select** -- Evaluate solutions within the same opportunity branch, not across branches.

### Phase 4: Prioritize Top 5

From the 15 generated ideas, select the top 5 using this scoring model:

| Criterion | Weight | Scale |
|-----------|--------|-------|
| Customer Impact | 30% | 1-10 |
| Strategic Alignment | 25% | 1-10 |
| Feasibility | 20% | 1-10 |
| Speed to Validate | 15% | 1-10 |
| Differentiation | 10% | 1-10 |

**Weighted Score** = (Impact x 0.30) + (Strategy x 0.25) + (Feasibility x 0.20) + (Speed x 0.15) + (Differentiation x 0.10)

### Phase 5: Document Each Idea

For each of the top 5 prioritized ideas, produce:

| Field | Description |
|-------|-------------|
| **Name** | Short, memorable name for the idea |
| **Description** | 2-3 sentence summary of what it is |
| **Reasoning** | Why this idea ranks highly -- connect to outcome and evidence |
| **Source Perspective** | PM, Designer, or Engineer |
| **Key Assumptions** | 2-3 assumptions that must be true for this to succeed |
| **Suggested Validation** | How to test the riskiest assumption first |
| **Effort Estimate** | T-shirt size (XS / S / M / L / XL) |

## Output Format

### Prioritized Ideas Table

| Rank | Name | Source | Score | Effort | Top Assumption |
|------|------|--------|-------|--------|----------------|
| 1 | ... | PM | 8.4 | M | ... |
| 2 | ... | Design | 7.9 | S | ... |
| 3 | ... | Eng | 7.6 | L | ... |
| 4 | ... | PM | 7.2 | S | ... |
| 5 | ... | Design | 6.8 | M | ... |

### Detailed Idea Cards

For each idea, fill in the template from `assets/ideation_workshop_template.md`.

## Supplementary Techniques

When the trio needs additional stimulus:

- **SCAMPER** -- Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse. Apply to existing products or competitor features.
- **How Might We (HMW)** -- Reframe problems as opportunity questions. "Users churn after trial" becomes "How might we demonstrate value before the trial ends?"
- **Crazy 8s** -- 8 sketches in 8 minutes per person. Forces breadth over depth.
- **Worst Possible Idea** -- Generate deliberately bad ideas, then invert them to find hidden good ones.

See `references/ideation-frameworks.md` for detailed descriptions of each technique.

## Integration with Other Discovery Skills

- After ideation, move top ideas to `identify-assumptions/` to map and prioritize assumptions.
- Use `brainstorm-experiments/` to design validation experiments for key assumptions.
- Run `pre-mortem/` before committing to build, to surface hidden risks.

## References

- Teresa Torres, *Continuous Discovery Habits* (2021)
- Marty Cagan, *Inspired* (2018)
- Jake Knapp, *Sprint* (2016)
- Michael Michalko, *Thinkertoys* (2006) -- SCAMPER origin
