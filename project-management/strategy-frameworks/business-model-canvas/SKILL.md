---
name: business-model-canvas
description: >
  Builds and audits a nine-block Business Model Canvas, tracing each segment
  through value, channel and revenue and naming the riskiest assumptions. Use
  when designing, refreshing or stress-testing a business model.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-11-08
  python-tools: canvas_validator.py
  tech-stack: business-model-canvas, osterwalder, strategy
  tags:
    - business-model-canvas
    - osterwalder
    - business-model
    - strategy
---

# Business Model Canvas

The agent builds a canvas whose blocks connect: every customer segment traces to a value proposition, a channel, a relationship and a revenue stream, and the cost structure fits the chosen posture. The nine blocks and the model patterns are in `references/canvas-framework.md`.

**Done looks like:** all nine blocks specific to this business (no "everyone", no "better, faster, cheaper"); each segment's chain complete; value-driven or cost-driven chosen; the three riskiest assumptions rated on evidence, risk and testability with an experiment for each; `canvas_validator.py` exits 0.

## When to Use

- Designing the business model for a new product or company, or refreshing it after a pivot
- Stress-testing the assumptions in an existing model, or comparing candidate models
- Aligning leadership, a new executive or an investor on how value flows

Pre-product-market-fit startups usually get more from `lean-canvas`.

## Clarify First

Before building the canvas, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Customer segment(s):** who you serve, specifically (drives Value Prop, Channels, Relationships, Revenue — "everyone" collapses the whole canvas).
- **Revenue model:** how the customer pays: subscription / usage / licensing / advertising (must reconcile against Cost Structure or unit economics break).
- **Stage:** new model / pivot / mature operating business (determines whether Lean Canvas is the better tool).
- **Cost-driven vs value-driven posture:** shapes Cost Structure and Key Activities (trying both produces mediocre everything).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Two-segment HR analytics canvas: exit 0
python3 project-management/strategy-frameworks/business-model-canvas/scripts/canvas_validator.py \
  --input project-management/strategy-frameworks/business-model-canvas/assets/sample_canvas.json --format markdown
```

```bash
# "Everyone" segment, empty blocks, untargeted value proposition: exit 1
python3 project-management/strategy-frameworks/business-model-canvas/scripts/canvas_validator.py \
  --input project-management/strategy-frameworks/business-model-canvas/assets/sample_canvas_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/strategy-frameworks/business-model-canvas/scripts/canvas_validator.py --help
```

## Tools Overview

`canvas_validator.py` is the quality gate for this skill. **What the validator checks:** each block populated (fail when empty); generic wording ("everyone", "innovative", "best-in-class", "great service"); every segment matched by a value proposition (fail otherwise) and a channel; value propositions targeting undefined segments or lacking measurable outcomes; channel phase coverage; revenue streams without a pricing mechanism or unit; fewer than three cost lines; undeclared posture; missing or untested assumptions. Matching is by segment name text, and it checks wording, not truth.

**Exit codes:** `0` no fail findings · `1` at least one fail (an empty block, a segment with no value proposition) · `2` unreadable file, invalid JSON or a top level that is not an object. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **Draft per block.** Customer Segments and Value Propositions first; then Channels, Relationships, Revenue; then Resources, Activities, Partnerships; Cost Structure last.
2. **Validate the chain.** For each segment trace segment → value proposition → channel → relationship → revenue. A segment you cannot trace is a gap, not a detail.
3. **Pick the posture.** Cost-driven (lean, automated, low price) or value-driven (premium, high touch). Trying both usually produces a mediocre version of each.
4. **Stress-test assumptions.** List the riskiest 2-3 and rate evidence, risk and testability; the high-risk, low-evidence ones get an experiment.
5. **Audit.** Write the canvas as JSON (schema in `--help`; `assets/sample_canvas.json` is a complete example) and run the validator. It must pass with no fail findings; then verify that each warning is fixed or deliberately accepted.
6. **Iterate.** First drafts are wrong in useful ways; expect 3-5 revisions.

## Anti-Patterns

### A value proposition that fits anyone
**Mistake:** "Better, faster, cheaper" or "innovative platform".
**Why it happens:** Specific claims feel risky to commit to.
**Instead:** State the measurable change for one named segment, such as "monthly reporting from 3 days to 4 hours".

### Revenue with no route to it
**Mistake:** A revenue stream exists for a segment that has no channel or relationship.
**Why it happens:** Blocks are filled one at a time rather than traced per segment.
**Instead:** Walk the chain in step 2 for every segment before polishing any block.

### Partners without a role
**Mistake:** Key Partnerships lists logos.
**Why it happens:** Partnerships signal credibility in a deck.
**Instead:** Give each partner the activity or resource it provides; drop the ones that provide neither.

More, with worked examples: `references/examples-anti-patterns.md`.

## Scope & Limitations

**In Scope:**
- A nine-block Business Model Canvas (Osterwalder), drafted from Customer Segments and Value Propositions outward to Cost Structure
- Chain validation from segment to value proposition, channel, relationship and revenue
- Assumption stress tests per block on evidence, riskiness and testability
- Business model patterns (unbundled, long tail, multi-sided, freemium, open) and the cost-driven versus value-driven choice
- A canvas audit for empty or generic blocks, cross-block coherence and revenue versus cost orientation (`canvas_validator.py`)

**Out of Scope:**
- Early-stage startup canvases built around problem and unfair advantage (see `project-management/strategy-frameworks/lean-canvas/`)
- Deep work on the value proposition block (see `project-management/discovery/value-proposition-canvas/`)
- Setting prices for the revenue block (see `business-growth/pricing-strategy/`)
- Financial models and unit economics in numbers (see `finance/financial-analyst/`)
- Running the experiments that test the assumptions (see `project-management/discovery/brainstorm-experiments/`)

**Important Caveats:**
- `canvas_validator.py` reads a hand-written JSON canvas. It checks completeness, generic wording and coherence by heuristics, not whether the content is true.
- Evidence, risk and testability ratings are the team's own judgments.
- First drafts are expected to be wrong. The skill plans for 3-5 revisions, and a canvas goes stale after a pivot.

## Files

| File | Purpose |
|------|---------|
| `scripts/canvas_validator.py` | Canvas completeness and coherence audit |
| `assets/sample_canvas.json` | Two-segment HR analytics canvas; exits 0 |
| `assets/sample_canvas_flawed.json` | Generic, incomplete canvas; exits 1 |
| `assets/canvas_template.md` | Fill-in template |

## Reference Documentation

- [references/canvas-framework.md](references/canvas-framework.md): The nine blocks, patterns, examples
- [references/examples-anti-patterns.md](references/examples-anti-patterns.md): Worked examples and common failures

## Related skills

- `project-management/strategy-frameworks/lean-canvas` — startup-stage variant
- `project-management/strategy-frameworks/swot-analysis` — internal/external strengths-weaknesses
- `project-management/strategy-frameworks/porters-five-forces` — competitive dynamics
- `project-management/discovery/value-proposition-canvas` — deeper on the value-prop block
- `project-management/execution/north-star-metric` — what to measure once model is set
- `business-growth/pricing-strategy` — pricing depth for the revenue block
- `c-level-advisor/ceo-advisor` — strategic context for the model
