---
name: cycle-time-analyzer
description: >
  Flow metrics analyzer (lead time, cycle time, throughput, WIP, aging WIP)
  for sprint and team health, with cumulative flow diagrams.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: flow_metrics.py
  tech-stack: kanban, flow-metrics, cfd, littles-law, aging-wip
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

Before running the analysis, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Issue history with status transitions** — per-item timestamps for when work started and finished (every metric is derived from these; missing transitions invalidate the numbers)
- [ ] **Workflow states that count as "in progress" vs "done"** — your board's actual status names (defines where cycle time starts/stops, which changes every result)
- [ ] **Analysis window** — the rolling period (e.g. last 6-8 weeks) and any type filter (scopes throughput trend and which in-flight items are flagged as aging WIP)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/flow_metrics.py --input issues.json --format markdown   # full dashboard
python scripts/flow_metrics.py --input issues.json --format mermaid     # cumulative flow diagram
python scripts/flow_metrics.py --demo --format markdown                 # sample output, no input
```

Review the 85th-percentile cycle time (not the average), flag aging WIP that exceeds it, and re-run weekly to track the trend. See `references/metrics-and-tool-reference.md` for the full workflow, CLI flags, and JSON schemas.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `flow_metrics.py` | Compute lead time, cycle time, throughput, WIP, aging WIP, CFD | `python scripts/flow_metrics.py --input issues.json --format markdown` |

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
