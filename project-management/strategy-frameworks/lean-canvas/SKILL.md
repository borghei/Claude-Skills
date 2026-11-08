---
name: lean-canvas
description: >
  Sketches a one-page startup model as testable hypotheses: problem, early
  adopters, value proposition, unfair advantage, riskiest assumptions. Use at
  the idea, pre-product-market-fit or pivot stage, or for a fast model.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-11-08
  python-tools: lean_canvas_validator.py
  tech-stack: lean-canvas, ash-maurya, lean-startup, problem-solution-fit
  tags:
    - lean-canvas
    - startups
    - assumptions
    - business-model
---

# Lean Canvas

The agent sketches a startup's model as hypotheses: problem and early adopter first, a one-sentence value proposition, three features, and an honest unfair advantage, then names the riskiest assumptions to test. Lean Canvas swaps four BMC blocks (resources, activities, partnerships, relationships) for problem, solution, key metrics and unfair advantage; block detail is in `references/lean-canvas-framework.md`.

**Done looks like:** three problems for one specific segment, each with today's alternative; at least five early adopters named with their workaround; a UVP naming segment, outcome and differentiator; at most three features; channels testable within four weeks; price, LTV and CAC estimates; a North Star with inputs; the unfair advantage classified honestly (most startups: none yet, with a plan); the top assumptions with tests; `lean_canvas_validator.py` exits 0.

## When to Use

- Early-stage (pre-product-market-fit or under about $1M ARR) product or company
- A 20-minute model sketch, or comparing the current and a proposed model in a pivot conversation
- Stress-testing the unfair advantage before building

Mature, multi-segment businesses usually need `business-model-canvas` instead.

## Clarify First

Before building the canvas, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The specific early-adopter segment:** named, not "everyone" (the Problem, UVP, and Channels blocks all hinge on a concrete early adopter).
- **The top 3 problems:** for that segment (the Problem block; if you can't name them you have an idea, not a startup).
- **Existing alternatives:** how customers solve this today (signals whether the problem is real; "they live with it" is important signal).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Restaurant shift-swap canvas: exit 0
python3 project-management/strategy-frameworks/lean-canvas/scripts/lean_canvas_validator.py \
  --input project-management/strategy-frameworks/lean-canvas/assets/sample_lean_canvas.json --format markdown
```

```bash
# Idea-stage canvas with no alternatives, channels, pricing or North Star: exit 1
python3 project-management/strategy-frameworks/lean-canvas/scripts/lean_canvas_validator.py \
  --input project-management/strategy-frameworks/lean-canvas/assets/sample_lean_canvas_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/strategy-frameworks/lean-canvas/scripts/lean_canvas_validator.py --help
```

## Tools Overview

`lean_canvas_validator.py` is the quality gate for this skill. **What the validator checks:** problems present (at most three) with existing alternatives; a target segment and at least five early adopters; UVP present, with the segment / outcome / differentiator flags set; at most three features; channels with a test plan and CAC; pricing model, price, LTV and a first-$10K MRR plan; burn, CAC and cost lines; a North Star and inputs; generic moats ("passion", "great team", "first mover"); an assumption register with tests. The UVP flags are self-reported, so read the sentence too.

**Exit codes:** `0` no fail findings · `1` at least one fail (no problems or alternatives, no segment, no UVP, no features, no channels, no pricing model, no North Star) · `2` unreadable file, invalid JSON or a top level that is not an object. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **Problem and segment first.** Top three problems for one segment, and how they solve it today. "They live with it" is a signal too; no alternatives at all usually means the problem is not painful.
2. **Name early adopters.** People who know they have the problem, have a workaround and can buy. If you cannot name five, you are not at problem-solution fit yet.
3. **UVP.** One sentence: "[outcome] for [segment] that [differentiator]".
4. **Solution.** Three features at most; the rest is backlog.
5. **Unfair advantage.** Counts: insider data, recognised authority, an existing audience, network effects already in motion. Does not count: hard work, a great team, first mover, better UX, "AI", cheaper. Mark "none-yet" with a plan rather than inventing one.
6. **Channels, revenue, costs, metrics.** Channels you can test in four weeks, a price and LTV, burn and CAC, a North Star with input metrics.
7. **Audit.** Write the canvas as JSON (schema in `--help`; `assets/sample_lean_canvas.json` is a complete example) and run the validator. It must pass with no fail findings; then verify that each warning is fixed or accepted, and design a test for each high-risk, low-evidence assumption.

## Anti-Patterns

### Solution before problem
**Mistake:** The canvas starts from the feature list and back-fills a problem.
**Why it happens:** Founders usually start with the product they want to build.
**Instead:** Fill Problem and Segment first; if the features do not map to the three problems, cut them.

### "Execution" as the unfair advantage
**Mistake:** The moat is speed, passion or a great team.
**Why it happens:** Leaving the block empty feels like admitting weakness.
**Instead:** Mark it "none-yet" and write the plan to build a real one; the validator warns on generic moats.

### No assumption register
**Mistake:** The canvas is presented as a plan.
**Why it happens:** A filled canvas looks finished.
**Instead:** List the riskiest assumptions with evidence ratings and a planned test each; the canvas is a set of hypotheses.

More with fixes: `references/lean-startup-anti-patterns.md`.

## Scope & Limitations

**In Scope:**
- A nine-block Lean Canvas: Problem, Customer Segments, Unique Value Proposition, Solution, Channels, Revenue Streams, Cost Structure, Key Metrics and Unfair Advantage
- Problem and early-adopter work first, including existing alternatives and named early adopters
- Tests for what counts as an unfair advantage and when to use Lean Canvas instead of the Business Model Canvas
- A canvas audit for missing blocks, generic content, no named early adopter, no existing alternatives, missing Key Metrics and a vague Unfair Advantage (`lean_canvas_validator.py`)
- Current-state versus proposed-state canvases for pivot conversations

**Out of Scope:**
- Operating-scale business models with partners, resources and activities (see `project-management/strategy-frameworks/business-model-canvas/`)
- Deep work on the value proposition (see `project-management/discovery/value-proposition-canvas/`)
- Building a full assumption register (see `project-management/discovery/identify-assumptions/`)
- Defining the Key Metric as a North Star (see `project-management/execution/north-star-metric/`)
- Financial forecasts behind the revenue and cost blocks (see `finance/financial-analyst/`)

**Important Caveats:**
- `lean_canvas_validator.py` reads a hand-written JSON canvas. Flags such as `names_segment` and `names_differentiator` are self-reported.
- The tool checks structure and specificity, not whether the problems are real. That needs customer evidence.
- A Lean Canvas is a set of hypotheses, not a plan. It goes stale as soon as tests come back.

## Files

| File | Purpose |
|------|---------|
| `scripts/lean_canvas_validator.py` | Lean Canvas completeness and quality audit |
| `assets/sample_lean_canvas.json` | Restaurant shift-swap startup; exits 0 |
| `assets/sample_lean_canvas_flawed.json` | Idea-stage canvas with gaps; exits 1 |
| `assets/lean_canvas_template.md` | Fill-in template |

## Reference Documentation

- [references/lean-canvas-framework.md](references/lean-canvas-framework.md): Blocks, early adopters, unfair advantage
- [references/lean-startup-anti-patterns.md](references/lean-startup-anti-patterns.md): Common failures and fixes

## Related skills

- `project-management/strategy-frameworks/business-model-canvas` — operating-scale variant
- `project-management/discovery/value-proposition-canvas` — deeper on UVP
- `project-management/discovery/identify-assumptions` — assumption register
- `project-management/discovery/pre-mortem` — risk discovery
- `project-management/execution/north-star-metric` — Key Metric definition
- `c-level-advisor/ceo-advisor` — strategic context
