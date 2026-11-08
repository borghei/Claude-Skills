---
name: cycle-time-analyzer
description: >
  Compute lead time, cycle time, throughput, WIP, aging WIP and a cumulative
  flow diagram from issue status history. Use when diagnosing slow delivery,
  setting WIP limits or preparing a flow review.
license: MIT + Commons Clause
metadata:
  version: 1.0.2
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: flow_metrics.py
  tech-stack: kanban, flow-metrics, cfd, littles-law, aging-wip
  tags:
    - flow-metrics
    - cycle-time
    - throughput
    - wip
    - cumulative-flow
---
# Cycle Time Analyzer (Flow Metrics)

## Overview

Compute and visualize the four core Kanban flow metrics -- lead time, cycle time, throughput, and work-in-progress -- from issue history data exported from Jira, Linear, GitHub Projects, or any tracker that records status transitions. The output is a dashboard suitable for sprint retrospectives, executive reporting, and bottleneck analysis, plus a Mermaid cumulative flow diagram that visualizes work accumulation over time.

Flow metrics are the most useful diagnostic for team and process health, far more so than velocity or story points. Daniel Vacanti's work (*Actionable Agile Metrics for Predictability*, 2015) shows that predictability and throughput are governed by Little's Law (`Throughput = WIP / Cycle Time`), and that the most reliable way to improve delivery is to lower WIP and stabilize cycle time -- not to estimate harder. This skill also reports aging WIP (in-flight work older than the team's 85th-percentile cycle time -- the items most at risk) and supports the shared `--format` schema (json, markdown, mermaid, confluence, notion, linear).

## Core Capabilities

- **Four flow metrics** — lead time, cycle time (as a distribution, never an average), throughput, and WIP, tied together by Little's Law.
- **Aging WIP** — flags in-flight items older than the 85th-percentile cycle time as at-risk; the most actionable daily metric.
- **Cumulative flow diagram** — Mermaid CFD for retrospectives and exec reports.
- **Per-type filtering & trends** — bug/feature/spike breakdowns over rolling 6-8 week windows across all six output formats.

## When to Use

- **Sprint retrospective** -- A team wants data-driven discussion of why some sprints feel slow.
- **Bottleneck investigation** -- Throughput has fallen and the team needs to identify the constraining step.
- **Quarterly delivery review** -- Leadership wants a real picture of delivery performance beyond story-point velocity.
- **Predictability analysis** -- Stakeholders want delivery forecasts grounded in actual cycle time distributions (use with Monte Carlo via `scrum-master/`).
- **WIP-limit calibration** -- A Kanban team is setting WIP limits and needs a baseline of current behavior.

## When NOT to Use

- For story-point velocity tracking, use `scrum-master/velocity_analyzer.py`.
- For sprint capacity calculation, use `scrum-master/sprint_capacity_calculator.py`.
- For per-person performance evaluation -- flow metrics are team-level signals; using them to rank individuals destroys the team behavior they measure.

## Clarify First

Before running the analysis, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Issue history with status transitions:** per-item timestamps for when work started and finished (every metric is derived from these; missing transitions invalidate the numbers).
- **Workflow states that count as "in progress" vs "done":** your board's actual status names (defines where cycle time starts/stops, which changes every result).
- **Analysis window:** the rolling period (e.g. last 6-8 weeks) and any type filter (scopes throughput trend and which in-flight items are flagged as aging WIP).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Export** issue history with status transitions into the input shape (`assets/sample_issues.json`).
2. **Map your states** if your board's names differ from the defaults (`--ready-state`, `--in-progress-state`, `--done-state`, each repeatable).
3. **Run the analysis:**

```bash
python3 project-management/execution/cycle-time-analyzer/scripts/flow_metrics.py \
  --input project-management/execution/cycle-time-analyzer/assets/sample_issues.json --format markdown
# Live board: add --as-of YYYY-MM-DD (today) so aging WIP is measured to now
```

4. **Read the distribution, not the average:** quote p85 cycle time and p85 lead time, flag aging WIP above p85, read throughput as a 6-8 week trend.
5. **Verify** before sharing: completed-in-window is not zero, WIP matches the board, and the as-of date in the header is the date you meant. Re-run weekly.

**As-of date:** defaults to the latest timestamp in the data, so the sample (April-May 2026) reads the same on any day: 7 completed, 0.82 items/week, 1 aging item. For a live board pass `--as-of` with today's date; otherwise items still in progress look younger than they are.

## Tools

| Tool | Purpose | Key flags |
|------|---------|---------|
| `flow_metrics.py` | Lead time, cycle time, throughput, WIP, aging WIP, CFD | `--input F` or `--demo`, `--format json\|markdown\|mermaid\|confluence\|notion\|linear`, `--type`, `--window-days 60`, `--as-of`, `--ignore-missing`, `--output` |

**Exit codes:** 0 report written; 2 missing file, invalid JSON, empty or wrong-shape `issues`, bad `--as-of`, or malformed issue data. Full flags and schemas: `references/metrics-and-tool-reference.md`.

## Anti-Patterns

### Quoting cycle time when asked for lead time
**Mistake:** An exec asks how long a feature takes, the team says 6 days, and the customer waits 11 weeks because the item sat in the backlog first.
**Why it happens:** Cycle time is the team's own number and the one the board shows.
**Instead:** Report both, labelled. Use lead time (from when the request entered the backlog) for customer commitments and cycle time for engineering planning, each at p85.

### WIP limits set by feel
**Mistake:** The team adopts a WIP limit of 5 per engineer because "that feels manageable".
**Why it happens:** Teams pick a limit before anyone has measured current WIP.
**Instead:** Measure the team's current WIP distribution first. A starting heuristic [EXPERIMENTAL] is a limit just below its median: low enough to bind on a normal day (that is what forces finishing over starting), high enough not to idle people. A limit above the 85th percentile almost never binds, so it has no effect. Re-measure cycle time with `flow_metrics.py` after 4 weeks and adjust.

### Single-sprint throughput read as a trend
**Mistake:** "Throughput dropped to 4 items this sprint, down from 6. Investigating slowdown."
**Why it happens:** Status updates cover one sprint, so one sprint's number is what gets reported.
**Instead:** Report throughput as a rolling 6-8 week trend with its range, and annotate known causes such as PTO. Investigate only when a sprint falls outside that range.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## Files

| File | Purpose |
|---|---|
| `scripts/flow_metrics.py` | The analyzer |
| `assets/sample_issues.json` | 10-issue history (same as `--demo`) |
| `assets/flow-metrics-dashboard.md` | Dashboard template |
| `examples/wayfinder-flow-analysis.md` | Worked analysis |

## References

- `references/metrics-and-tool-reference.md` -- Precise definitions of the four metrics, Little's Law, aging WIP, the 7-step workflow, troubleshooting matrix, success criteria, and the full `flow_metrics.py` CLI flags + input/output JSON schemas. Read when running an analysis or wiring up the tool.
- `references/flow-metrics-guide.md` -- Vacanti-style deep dive: lead vs cycle, distributions vs averages, Little's Law, aging WIP, common anti-patterns. Read for narrative depth and tracker-specific export instructions.
- `references/red-flags.md` -- Bad-vs-good examples of flow-metric reporting. Read this to sanity-check a dashboard before sharing it.
- Vacanti, Daniel S. *Actionable Agile Metrics for Predictability*. ActionableAgile Press, 2015.
- Vacanti, Daniel S. *When Will It Be Done?* ActionableAgile Press, 2020.
- Little, John D. C. "A Proof for the Queuing Formula: L = λW." Operations Research, 1961.
- Anderson, David J. *Kanban: Successful Evolutionary Change for Your Technology Business*. Blue Hole Press, 2010.

## Scope & Limitations

**In Scope:**
- Lead time, cycle time, throughput, WIP, aging WIP calculation
- Cumulative flow diagram generation (Mermaid)
- Per-type filtering (bug, feature, spike)
- All six output formats per `SHARED_OUTPUT_SCHEMA.md`

**Out of Scope:**
- Monte Carlo delivery forecasting (use `scrum-master/velocity_analyzer.py`)
- Story-point velocity (use `scrum-master/`)
- Resource capacity planning (use `senior-pm/resource_capacity_planner.py`)
- Code-level metrics (PR review time, deploy frequency -- use DevOps-focused tools)

**Important Caveats:**
- Flow metrics depend on accurate status transitions. If your team batch-updates the board once a day, the cycle time data will be discretized by that batch interval.
- A team that gamifies flow metrics will produce better-looking numbers without changing real delivery. Use these metrics as a diagnostic, not a target. (Goodhart's Law.)
- Cycle time is a team property, not an individual property. Resist the urge to compute per-assignee cycle time -- it will incentivize hand-offs that hurt the team.
- AI-assisted teams: faster coding often shifts the wait into review and test states. Watch time-in-review and aging WIP there, not just total cycle time, and pair flow metrics with DORA rework rate. See the "AI-Assisted Delivery" sections in `delivery-manager/` and `scrum-master/`.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `scrum-master/` | Complementary | Flow metrics + velocity together provide the full delivery picture |
| `scrum-master/retrospective_analyzer.py` | Feeds into | Flow trends inform retro topics |
| `dependency-map/` | Complementary | Long cycle times often correlate with cross-team dependencies |
| `sprint-retrospective/` | Feeds into | CFD and aging WIP are standard retro inputs |
| `senior-pm/project_health_dashboard.py` | Feeds into | Throughput trends feed portfolio health |
| `status-update-generator/` | Feeds into | Weekly status includes throughput and aging WIP highlights |
| `agile-coach/` | Used by | Coaches use flow metrics to assess team maturity |
