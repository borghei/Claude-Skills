---
name: outcome-roadmap
description: >
  Transform output-based feature lists into outcome-driven Now/Next/Later
  roadmaps using the "so what?" technique. Use when converting a feature-list
  roadmap to outcomes, communicating product strategy, or running quarterly
  planning.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: roadmap_transformer.py
  tech-stack: outcome-roadmap, product-strategy, now-next-later
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

Before transforming the roadmap, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Customer segment + business impact per item** — fills the "Enable [segment] to [outcome] so that [impact]" statement; without it the tool only emits placeholder templates
- [ ] **Target quarter per initiative** — drives Now/Next/Later horizon placement and the detail/commitment level
- [ ] **Initiative type** — feature / improvement / infrastructure drives the strategic-question and metric suggestions
- [ ] **Success metric per Now/Next item** — the primary/secondary/counter-metrics; Later items intentionally stay metric-light to avoid false precision

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/roadmap_transformer.py --input roadmap.json            # transform a roadmap
python scripts/roadmap_transformer.py --input roadmap.json --format markdown
python scripts/roadmap_transformer.py --demo                          # run on built-in demo data
```

Each input initiative needs `title`, `description`, `quarter` (format "Q[1-4] YYYY"), and `type` (`feature`/`improvement`/`infrastructure`). The tool emits outcome-statement *templates* — fill the placeholders with real customer and business data.

## References

- **[references/outcome-roadmap-workflow.md](references/outcome-roadmap-workflow.md)** — read this when transforming a roadmap: the 6-step workflow with validation checkpoints, the "so what?" technique, Now/Next/Later detail levels, a full worked example, why output roadmaps fail, output structure, tool flags, troubleshooting, and success criteria.
- **[references/outcome-roadmap-guide.md](references/outcome-roadmap-guide.md)** — read this for the deeper guide: output-vs-outcome comparison, outcome formulas, and stakeholder communication strategies.
- **[references/red-flags.md](references/red-flags.md)** — read this to spot the common ways outcome roadmaps go wrong (false precision, mechanical templates, too many Now items) before sharing.
- `assets/outcome_roadmap_template.md` — roadmap document template with Now/Next/Later sections.

## Scope & Limitations

**In Scope:** transforming output-based feature lists into outcome-driven items, Now/Next/Later classification by quarter-to-current-date distance, "so what?" chain generation, strategic-question and metric suggestions by initiative type, markdown/text/JSON report output grouped by horizon.

**Out of Scope:** feature prioritization or scoring (`execution/prioritization-frameworks/`), sprint-level planning or capacity allocation (`scrum-master/`), product strategy or vision definition (roadmaps communicate strategy, they don't create it), cross-team dependency management (`program-manager/`).

**Important Caveats:** outcome roadmaps require a cultural shift — teams used to date-driven lists need coaching on commitment levels; the tool generates outcome-statement templates, not finished outcomes; Later items intentionally lack detailed metrics, and adding false precision undermines credibility.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `execution/brainstorm-okrs/` | Receives from | OKR key results become success metrics for Now/Next roadmap items |
| `execution/prioritization-frameworks/` | Receives from | RICE/ICE scores inform which initiatives move to Now vs. Next vs. Later |
| `execution/create-prd/` | Feeds into | Now items with validated outcomes become PRD candidates |
| `discovery/brainstorm-experiments/` | Receives from | Experiment results validate demand for Next/Later items, promoting them to Now |
| `senior-pm/` | Receives from | Portfolio strategic priorities influence roadmap horizon placement |
| `scrum-master/` | Receives from | Sprint capacity data determines how many Now items the team can support |
