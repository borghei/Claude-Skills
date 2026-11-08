---
name: brainstorm-okrs
description: >
  Draft and score quarterly OKRs: a qualitative objective, measurable key
  results and a counter-metric. Use when setting or reviewing a team's OKRs
  before they are committed, or when KRs read like a task list.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: okr_validator.py
  tech-stack: okr, radical-focus, goal-setting, strategic-planning
  tags:
    - okrs
    - radical-focus
    - key-results
    - goal-setting
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

Before generating the OKR sets, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Quarterly theme:** the single team theme for the quarter (every objective and KR must connect back to it; without it the sets are unfocused).
- **Parent / company objective:** the higher-level priority this team supports (sets the objective framing and the top-down alignment).
- **Current baselines:** today's values for the candidate metrics (turns KRs from aspirational guesses into measurable, gradeable targets).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. Settle the theme and baselines (Clarify First), then draft [RECOMMENDED] three distinct OKR sets, each with one qualitative objective and three KRs: primary, a second dimension, and a counter-metric that would expose gaming.
2. Score the drafts:

```bash
python3 project-management/execution/brainstorm-okrs/scripts/okr_validator.py \
  --input project-management/execution/brainstorm-okrs/assets/sample_okrs_clean.json
```

3. Revise any set below the threshold (default 80, the tool's "Strong" line) and re-run. The score checks structure: numbers in the objective, KR count, a metric and target on each KR, task verbs ("launch", "build") in KR position. It cannot judge whether the goal is the right one, so read each passing set against the theme yourself.
4. **Done when** the validator exits 0 and the team states a 60-70% confidence for each KR.

`--threshold N` changes the bar; `--format json` for pipelines; `--demo` runs the built-in mix.

**Exit codes:** 0 every set scores at or above the threshold, 1 at least one below (`assets/sample_okrs.json` exits 1 by design: "Increase revenue by 25%" with two task KRs scores 75), 2 missing file, invalid JSON or wrong shape.

## Anti-Patterns

### Targets set at 100% confidence
**Mistake:** Every KR is one the team is 95-100% sure to hit, such as a 4% MRR lift that would happen anyway.
**Why it happens:** A green scorecard at quarter end feels safer than a visible miss.
**Instead:** Set targets at 60-70% confidence and ask the team for its confidence number on each KR. A hit rate above 90% sustained over three quarters means the bar is too low.

### Lowering the target mid-quarter
**Mistake:** In week 8 a KR is behind, so the team cuts the target from 35% to 20% and reports it green.
**Why it happens:** A red KR feels like failure in front of leadership.
**Instead:** Keep the week-1 targets. Mark the KR red, look for what would close the gap, and if nothing realistic will, record the miss and its cause in the retrospective.

### The roadmap listed as KRs
**Mistake:** The OKR has five KRs, each "Ship X" for a planned roadmap item.
**Why it happens:** The roadmap already exists, and copying it skips the hard choice of what to focus on.
**Instead:** Keep three KRs per Objective (primary, secondary dimension, counter-metric) that measure change for customers or the business. List supporting initiatives separately. More than 4 KRs on one Objective is a flag.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## Files

| File | Purpose |
|---|---|
| `scripts/okr_validator.py` | Structural OKR scorer and gate |
| `assets/sample_okrs.json` | Three sets incl. a flawed one (exit 1) |
| `assets/sample_okrs_clean.json` | Two strong sets (exit 0) |
| `assets/okr_template.md` | OKR document and quarterly review template |
| `examples/q3-okrs-shared-dashboards-launch.md` | Worked quarter |

## References

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
- OKRs work best with weekly check-ins; reviewed only at quarter end, a KR that drifts in week 3 is discovered when nothing can be done about it.
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
