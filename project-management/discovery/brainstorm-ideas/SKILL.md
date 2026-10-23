---
name: brainstorm-ideas
description: >
  Product ideation expert using Product Trio approach and Opportunity Solution
  Trees for both new and existing products.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-06-15
  tech-stack: product-trio, opportunity-solution-tree, scamper, hmw
  tags:
    - ideation
    - product-trio
    - opportunity-solution-tree
    - discovery
---
# Product Ideation Expert

## Overview

Structured product ideation for both new product creation and existing product enhancement. This skill combines the Product Trio approach (PM + Designer + Engineer perspectives) with Teresa Torres' Opportunity Solution Tree framework to generate, evaluate, and prioritize product ideas systematically.

## Core Capabilities

- **Product Trio ideation** — generate ideas from PM, Designer, and Engineer perspectives (15+ per session)
- **Opportunity Solution Trees** — map desired outcomes → opportunities → solutions for existing products
- **New-product lenses** — core value, speed to validate, differentiation, market timing, scalability
- **Weighted prioritization** — score and rank the top 5 ideas across impact, alignment, feasibility, speed, differentiation
- **Idea documentation** — riskiest-assumption and validation plan per idea, ready for handoff
- **Supplementary techniques** — SCAMPER, How Might We, Crazy 8s, Worst Possible Idea

## When to Use

- **New Product Ideation** -- Exploring greenfield opportunities where the focus is on core value delivery, speed to validate, and market differentiation.
- **Existing Product Enhancement** -- Identifying opportunities within a live product using the Opportunity Solution Tree to connect desired outcomes to concrete solutions.

## Clarify First

Before ideating, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **New vs existing product:** selects the approach (new-product lenses vs Opportunity Solution Tree mapping).
- **Target outcome or problem:** the desired outcome the session is anchored to (ungrounded ideation produces random ideas, not prioritizable ones).
- **Hard constraints:** tech stack, timeline, budget limits (bound the feasibility and speed scores in prioritization).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### Ideas with no opportunity behind them
**Mistake:** The session produces a feature list ("dark mode, AI assistant, calendar integration") with no link to a customer opportunity or outcome.
**Why it happens:** Features are concrete and easy to picture, so they come out first.
**Instead:** Anchor every idea to a named opportunity on the Opportunity Solution Tree, and that opportunity to the target outcome. If you can't name the opportunity an idea serves, park it.

### No confidence score
**Mistake:** Ideas get impact estimates, but nothing shows how sure the team is about those estimates.
**Why it happens:** The weighted scoring covers impact and feasibility, so confidence seems already covered.
**Instead:** Add a confidence score or evidence column for each idea before ranking the top 5. Note whether each estimate rests on customer interviews or one person's hunch, and test the low-confidence bets first.

### Ideas with no next-step owner
**Mistake:** The workshop ends, the ideas stay on the board, and a month later nothing has happened.
**Why it happens:** Generating ideas feels like the output, so nobody plans what comes after.
**Instead:** Give each surviving idea an owner and a next step before the session ends. Hand each one's riskiest assumption to `discovery/identify-assumptions`.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/ideation-process.md](references/ideation-process.md)** — the full five-phase methodology (frame → trio → product-type approach → prioritize → document), output formats, supplementary techniques, troubleshooting table, success criteria, and further reading. Read when running a session end to end.
- **[references/ideation-frameworks.md](references/ideation-frameworks.md)** — deep descriptions of the Product Trio methodology and each supplementary technique (SCAMPER, HMW, Crazy 8s, Worst Possible Idea). Read when you need technique detail or facilitation mechanics.
- **[references/red-flags.md](references/red-flags.md)** — common ways ideation output goes wrong with bad/good examples. Read before publishing the idea list or moving to prioritization.

## Integration with Other Discovery Skills

- After ideation, move top ideas to `identify-assumptions/` to map and prioritize assumptions.
- Use `brainstorm-experiments/` to design validation experiments for key assumptions.
- Run `pre-mortem/` before committing to build, to surface hidden risks.

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
