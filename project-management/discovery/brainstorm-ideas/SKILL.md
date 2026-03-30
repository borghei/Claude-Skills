---
name: brainstorm-ideas
description: >
  Product ideation expert using Product Trio approach and Opportunity Solution
  Trees for both new and existing products.
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

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Ideation session produces only incremental ideas, no breakthrough thinking | Anchoring bias -- team defaults to what they know; PM perspective dominates | Explicitly rotate perspectives (Designer first, then Engineer); use "Worst Possible Idea" technique to break anchoring; invite an outsider to challenge assumptions |
| Prioritization scores cluster tightly, making ranking impossible | Scoring criteria are too similar, or the team is avoiding differentiation | Add a forced-rank step after weighted scoring; increase weight spread between criteria; use pairwise comparison for the top 5 |
| Opportunity Solution Tree has too many branches to be actionable | Team brainstormed opportunities without filtering by evidence | Require each opportunity to link to at least 2 user interview quotes or data points; prune branches without evidence |
| Stakeholders reject prioritized ideas because "the real problem is different" | Problem framing was done without stakeholder input; target outcome not validated | Run a problem framing workshop with stakeholders before ideation; validate the target outcome with data before generating solutions |
| Same ideas keep resurfacing across sessions | Previous ideation results not documented or accessible; no "already considered" registry | Maintain an idea backlog with status (explored, parked, rejected with rationale); review it at the start of each session |
| Engineer perspective ideas are too implementation-focused | Engineers default to "how to build" rather than "what to build" | Reframe the prompt: "What new capability would our tech stack enable for users?" rather than "What should we build next?" |
| Validation suggestions are too expensive or slow | Team defaults to full A/B tests when lighter methods exist | Introduce pretotyping and Wizard-of-Oz as first validation options; use the `brainstorm-experiments/` skill for experiment design |

## Success Criteria

- Each ideation session produces at least 15 ideas across all three Product Trio perspectives (minimum 3 per perspective)
- Top 5 prioritized ideas each have a documented riskiest assumption and a validation plan
- At least 60% of prioritized ideas can begin validation within 2 weeks using lightweight methods
- Stakeholders rate the ideation output as "relevant to strategic objectives" at 4+/5
- Ideas that proceed to validation have a clear connection to the target outcome (traceable through the Opportunity Solution Tree)
- Ideation cadence is maintained (at minimum quarterly for existing products, monthly during new product exploration)
- At least 1 idea per quarter advances from ideation through validation to backlog commitment

## Scope & Limitations

**In Scope:** Structured ideation facilitation using Product Trio approach, Opportunity Solution Tree mapping, idea prioritization with weighted scoring, SCAMPER and HMW supplementary techniques, idea documentation with validation plans, integration with downstream discovery skills.

**Out of Scope:** Assumption testing and experiment design (hand off to `brainstorm-experiments/` and `identify-assumptions/`), detailed product requirements (hand off to `execution/create-prd/`), market research and competitive analysis, financial modeling for ideas.

**Limitations:** Ideation quality is bounded by the diversity of perspectives in the room -- remote-only sessions may reduce creative energy. Scoring models provide structured comparison but are not objective truth; they encode the biases of the scorers. Opportunity Solution Trees require ongoing user research to populate -- they are not a substitute for customer interviews.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `identify-assumptions/` | Ideas -> Assumptions | Top 5 ideas feed into assumption mapping for risk assessment |
| `brainstorm-experiments/` | Ideas -> Experiments | Riskiest assumptions from ideas become experiment candidates |
| `pre-mortem/` | Ideas -> Risk | Selected ideas run through pre-mortem before build commitment |
| `execution/create-prd/` | Ideas -> PRD | Validated ideas become PRD inputs with problem statement and success metrics |
| `execution/brainstorm-okrs/` | OKRs -> Ideas | Team OKRs define the target outcomes that frame ideation sessions |
| `execution/prioritization-frameworks/` | Ideas -> Prioritization | Scored ideas feed into RICE or other frameworks for backlog ordering |
