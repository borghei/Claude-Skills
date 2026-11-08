---
name: outcome-roadmap
description: >
  Turn a feature-list roadmap into outcome statements placed in Now/Next/Later,
  and check each has a measure. Use when converting a feature-list
  roadmap, reviewing a roadmap before it goes to leadership, or quarterly
  planning.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: roadmap_transformer.py
  tech-stack: outcome-roadmap, product-strategy, now-next-later
  tags:
    - roadmap
    - outcomes
    - now-next-later
    - product-strategy
---
# Outcome Roadmap Expert

The agent transforms output-based roadmaps ("build feature X") into outcome-driven roadmaps ("enable customers to achieve Y") using the "so what?" technique and Now/Next/Later framing. It produces roadmaps that communicate strategy and measurable impact, not just feature lists and dates.

## Core Capabilities

- **Output → outcome transformation** — applies the formula "Enable [segment] to [outcome] so that [impact]" via a "so what?" chain that drills from feature to business metric.
- **Now/Next/Later classification** — sorts initiatives into horizons whose detail and commitment level match certainty.
- **Metric definition** — primary, secondary, and counter-metrics for Now/Next items.
- **Dependency capture** — technical, organizational, and market prerequisites per item.
- **Stakeholder-ready output** — text, JSON, and markdown reports grouped by horizon for alignment review.

## When to Use

- Converting a feature-list / date-driven roadmap into outcome-driven format.
- Communicating product strategy to executives or customers.
- Running quarterly planning and aligning teams around impact rather than deliverables.
- Anchoring roadmap items to customer value and OKRs.

## Clarify First

Before transforming the roadmap, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Customer segment + business impact per item:** the raw material for "Enable [segment] to [outcome] so that [impact]"; without it the outcome is a guess.
- **Target quarter per initiative and the current quarter:** drive Now/Next/Later placement and the commitment level.
- **Success metric with a baseline per Now/Next item:** an outcome nobody can measure is still an output.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Write the outcomes yourself.** For each initiative, run the "so what?" chain (feature → what changes for the user → which number moves → what the business gets) until you reach a named segment, a job and a number. State it as "Enable [segment] to [outcome] so that [impact]". The tool cannot write these; it checks them.
2. **Add the measures**: a metric with baseline and target for Now and Next items, a counter-metric for Now items. Later items stay metric-light on purpose; false precision there hurts credibility.
3. **Check the roadmap:**

```bash
python3 project-management/execution/outcome-roadmap/scripts/roadmap_transformer.py \
  --input project-management/execution/outcome-roadmap/assets/sample_roadmap_clean.json --as-of "Q3 2026"
```

4. **Fix every error and re-run.** Done when the tool exits 0 and three outcome statements read aloud could not be swapped between items.

**What the tool checks:** horizon from quarter vs `--as-of` (default: earliest quarter in the file, so samples read the same on any day; pass the current quarter for a live roadmap); more than 3 Now items; Now/Next items with no outcome, an outcome that starts with an output verb (build, launch, migrate...), no "so that", no metric, or a metric without baseline or target; Now items with no counter-metric; quarters already past. Items without an outcome get the "so what?" prompts for their type.

Input per initiative: `title`, `description`, `quarter` ("Q3 2026"), `type` (feature, improvement, infrastructure), and the fields you write: `outcome`, `metric {name, baseline, target}`, `counter_metric`. Flags: `--input F` or `--demo`, `--as-of`, `--format text|json|markdown`, `--output`.

**Exit codes:** 0 no errors, 1 at least one error (`assets/sample_roadmap.json` and `--demo` exit 1 by design: a feature list with 4 Now items), 2 missing file, invalid JSON, wrong shape or bad `--as-of`.

## Anti-Patterns

### Outcome statements on top of a dated feature list
**Mistake:** Each item opens with "Enable [X] to [Y] so that [Z]", but underneath sits a feature list with ship dates, and standups only discuss the dates.
**Why it happens:** Teams used to date-driven roadmaps add the outcome wording without changing how they work.
**Instead:** Under each Now item, list the success metric with baseline and target, and frame the features as a working hypothesis the team will change if the metric doesn't move. Check standup notes: if they name only features, the roadmap is still output-driven.

### Too many Now items
**Mistake:** The Now column lists 8 initiatives.
**Why it happens:** Everything feels urgent, and moving an item to Next feels like saying no to a stakeholder.
**Instead:** [RECOMMENDED] Cap Now at 2-3 items, sized to what the team can ship in 6-8 weeks. Move the rest to Next. More than 3 Now items means the commitment level on the roadmap is false.

### Interchangeable outcome statements
**Mistake:** "Enable users to be more productive, so we grow revenue." "Enable customers to succeed, so they retain better." The template is filled in mechanically.
**Why it happens:** The "Enable ... so that ..." formula is easy to fill with generic words, and a structural check passes them.
**Instead:** Each outcome names a specific segment, a specific job and a number. Read three statements aloud. If they could be swapped between items without anyone noticing, push the "so what?" chain 2-3 levels deeper.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

- **[references/outcome-roadmap-workflow.md](references/outcome-roadmap-workflow.md)** — read this when transforming a roadmap: the 6-step workflow with validation checkpoints, the "so what?" technique, Now/Next/Later detail levels, a full worked example, why output roadmaps fail, output structure, tool flags, troubleshooting, and success criteria.
- **[references/outcome-roadmap-guide.md](references/outcome-roadmap-guide.md)** — read this for the deeper guide: output-vs-outcome comparison, outcome formulas, and stakeholder communication strategies.
- **[references/red-flags.md](references/red-flags.md)** — read this to spot the common ways outcome roadmaps go wrong (false precision, mechanical templates, too many Now items) before sharing.

## Files

| File | Purpose |
|---|---|
| `scripts/roadmap_transformer.py` | Horizon placement and outcome-readiness check |
| `assets/sample_roadmap_clean.json` | Outcome roadmap that passes (exit 0) |
| `assets/sample_roadmap.json` | Output-style feature list (exit 1) |
| `assets/outcome_roadmap_template.md` | Roadmap document template |
| `examples/output-to-outcome-transformation.md` | Worked transformation |

## Scope & Limitations

**In Scope:** turning output-based feature lists into outcome-driven items, Now/Next/Later placement by quarter, "so what?" prompts by initiative type, and a structural check of outcomes and measures.

**Out of Scope:** feature prioritization or scoring (`execution/prioritization-frameworks/`), sprint-level planning or capacity allocation (`scrum-master/`), product strategy or vision definition (roadmaps communicate strategy, they don't create it), cross-team dependency management (`program-manager/`).

**Important Caveats:** outcome roadmaps require a cultural shift — teams used to date-driven lists need coaching on commitment levels; the tool checks outcome statements, it does not write them; Later items intentionally lack detailed metrics, and adding false precision undermines credibility.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `execution/brainstorm-okrs/` | Receives from | OKR key results become success metrics for Now/Next roadmap items |
| `execution/prioritization-frameworks/` | Receives from | RICE/ICE scores inform which initiatives move to Now vs. Next vs. Later |
| `execution/create-prd/` | Feeds into | Now items with validated outcomes become PRD candidates |
| `discovery/brainstorm-experiments/` | Receives from | Experiment results validate demand for Next/Later items, promoting them to Now |
| `senior-pm/` | Receives from | Portfolio strategic priorities influence roadmap horizon placement |
| `scrum-master/` | Receives from | Sprint capacity data determines how many Now items the team can support |
