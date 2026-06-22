---
name: brainstorm-okrs
description: >
  OKR brainstorming and validation using the Radical Focus framework — outcome
  objectives, measurable key results, counter-metrics. Use for setting or
  validating quarterly OKRs, aligning team goals, or teaching outcomes vs outputs.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: okr_validator.py
  tech-stack: okr, radical-focus, goal-setting, strategic-planning
---
# OKR Brainstorming Expert

The agent generates and validates outcome-focused OKR sets using Christina Wodtke's Radical Focus methodology. It produces inspirational objectives with measurable key results, applies counter-metric tests, and scores quality against proven criteria.

## Core Capabilities

- **Theme-anchored generation** — one theme per team per quarter; every OKR connects back to it
- **3 distinct OKR sets** — each with a qualitative objective, 3 key results (primary, secondary dimension, counter-metric), and rationale
- **Counter-metric testing** — guards against gaming KRs by doing something harmful
- **Automated validation** — `okr_validator.py` scores sets and flags disguised tasks, missing metrics, output-framed KRs, and missing counter-metrics

## When to Use

- Setting quarterly OKRs from a single team theme
- Validating existing OKRs against quality criteria before committing
- Aligning team goals to company objectives
- Teaching teams the difference between outputs and outcomes

## Clarify First

Before generating the OKR sets, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Quarterly theme** — the single team theme for the quarter (every objective and KR must connect back to it; without it the sets are unfocused)
- [ ] **Parent / company objective** — the higher-level priority this team supports (sets the objective framing and the top-down alignment)
- [ ] **Current baselines** — today's values for the candidate metrics (turns KRs from aspirational guesses into measurable, gradeable targets)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/okr_validator.py --input okrs.json   # validate & score
python scripts/okr_validator.py --demo              # built-in good/bad demo
```

Any OKR set scoring below 70% must be revised before committing. See the references for the full workflow and input schema.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/okr-workflow-and-examples.md](references/okr-workflow-and-examples.md)** — full step-by-step workflow, a worked quarterly OKR example, mistakes/KPI tables, troubleshooting, success criteria, and the `okr_validator.py` flag + JSON-schema reference. Read when generating OKRs or wiring up the validator.
- **[references/okr-best-practices.md](references/okr-best-practices.md)** — comprehensive OKR anatomy, scoring, and management guide using Radical Focus. Read for the deeper "why" behind the rules.
- **[references/red-flags.md](references/red-flags.md)** — concrete bad-vs-good examples of common OKR failure modes and how to fix them. Read before sharing a draft OKR set.
- **[assets/okr_template.md](assets/okr_template.md)** — OKR document template and quarterly review format. Use when writing up the committed set.

## Scope & Limitations

**In Scope:**
- OKR brainstorming using Christina Wodtke's Radical Focus methodology
- Generating 3 distinct OKR sets per theme with counter-metric testing
- Automated validation and scoring of OKR quality (output detection, metric presence, structural checks)
- Guidance on OKR vs. KPI vs. North Star Metric distinctions
- Common OKR mistake identification and remediation

**Out of Scope:**
- OKR tracking and progress monitoring over the quarter (use dedicated OKR platforms)
- Company-level OKR cascade and alignment across teams (see `senior-pm/` for portfolio alignment)
- Individual performance-linked OKRs (OKRs should be team goals, not performance reviews)
- Metric instrumentation or analytics setup for measuring key results

**Important Caveats:**
- OKRs work best when combined with weekly check-ins. Teams that review OKRs only at quarter end see 30-45% lower completion rates.
- The validator catches structural issues but cannot assess strategic quality. A perfectly scored OKR can still be the wrong goal.
- OKRs should be aligned top-down (strategic direction) and bottom-up (team insight). Pure top-down OKRs reduce team ownership.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `scrum-master/` | Receives from | Sprint velocity and capacity data inform realistic KR target-setting |
| `senior-pm/` | Receives from | Portfolio strategic priorities shape quarterly OKR themes |
| `execution/outcome-roadmap/` | Feeds into | OKR key results become success metrics for roadmap Now/Next items |
| `execution/prioritization-frameworks/` | Complements | Prioritized initiatives inform which OKR theme to focus on |
| `discovery/identify-assumptions/` | Receives from | Validated assumptions increase confidence in OKR target feasibility |
| `discovery/brainstorm-experiments/` | Feeds into | Experiment metrics may become OKR key results when validated |
