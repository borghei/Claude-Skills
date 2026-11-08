---
name: senior-pm
description: >
  Scores portfolio health, risk exposure and resource capacity from a project JSON
  and frames board-ready status reports. Use when running a portfolio review,
  writing an executive RAG report, or rebalancing people across projects.
license: MIT + Commons Clause
metadata:
  version: 2.0.1
  author: borghei
  category: project-management
  domain: enterprise-pm
  updated: 2026-11-08
  tags: [project-management, stakeholder-management, risk, planning]
  python-tools: project_health_dashboard.py, risk_matrix_analyzer.py, resource_capacity_planner.py, stakeholder_mapper.py
  tech-stack: portfolio-management, risk-analysis, stakeholder-mapping, executive-reporting
---
# Senior Project Management Expert

## Overview

Portfolio-level project management for enterprise software and SaaS: which projects need attention, where the risk sits, whether the people exist to deliver, and how to tell executives. The tools do the arithmetic deterministically; your job is to check their inputs, read the results against the context, and turn them into a decision someone can make.

**Done looks like:** every red or amber project is named with its weakest dimension and a recommended action; every top risk has an owner and a mitigation; capacity gaps are stated in hours per week with the people or dates that close them; the executive ask sits in the first 100 words.

## When to Use

- "Run a portfolio health review", "build an executive status report", "map our stakeholders"
- Several projects compete for the same people and someone has to say which slips
- A board or exec RAG report is due and the current one hides red projects in an average
- A risk register exists but nobody knows which risks matter most or which mitigations are late

Single-team sprint health belongs to `scrum-master/`; cross-team dependency and milestone tracking to `program-manager/`.

## Clarify First

Before generating the report or analysis, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which artifact:** portfolio health review, executive status report, stakeholder map, or risk/capacity analysis (each maps to a different tool and structure).
- **Audience:** board, exec staff, or delivery team (sets the altitude, RAG framing, and level of detail).
- **Portfolio scope and data:** which projects and what timeline/budget/risk data exists (scores and dashboards are only as good as the inputs).
- **Prioritization model:** WSJF, RICE, ICE, or MoSCoW, when ranking projects (each produces a different order).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

Run from the skill folder (`project-management/senior-pm/`). All four tools print text by default and JSON with `--format json`.

```bash
# Portfolio health: per-project timeline/budget/scope/quality/risk scores and RAG
python3 scripts/project_health_dashboard.py assets/sample_project_data.json

# Risk register: probability x impact matrix, categories, overdue mitigations
python3 scripts/risk_matrix_analyzer.py assets/sample_project_data.json --format json

# Capacity: utilisation per person, weekly demand vs capacity, gaps per project
python3 scripts/resource_capacity_planner.py assets/sample_project_data.json

# Stakeholders: Mendelow quadrant, communication plan, blocker strategies
python3 scripts/stakeholder_mapper.py assets/sample_stakeholders.json
```

`assets/expected_output.json` holds the key numbers these commands produce on the sample, so you can confirm a change did not break the maths.

### Inputs and how the numbers are derived

`sample_project_data.json` is one portfolio file with `portfolio_metadata`, `projects`, `resources` and `risks`. The first three tools read it directly:

| Tool | Reads | Derived values |
|------|-------|----------------|
| `project_health_dashboard.py` | `projects[]`, `risks[]` | Timeline: planned end plus `days_behind_schedule`. Budget: estimate at completion = spent / progress once 20% done, else spent + remaining. Scope: share of milestones due by the as-of date that are complete, less 0.03 per scope change. Quality: 0.7 x test pass rate + 0.3 x coverage, left out (weights renormalised) when both are 0. Risk: sum of probability x impact over the project's open risks. |
| `risk_matrix_analyzer.py` | `risks[]` | Score, level, category concentration, mitigations past `target_resolution` |
| `resource_capacity_planner.py` | `resources[]`, `projects[]` | Weekly demand = remaining budget / blended hourly rate of assigned people, spread over the weeks left; allocation = each person's utilisation split across `current_projects` |
| `stakeholder_mapper.py` | `stakeholders[]` (see `assets/sample_stakeholders.json`) | Quadrant from power and interest (1-10, threshold 5) |

A flat per-project schema (`project_id`, `planned_budget`, `forecasted_total_cost`, ...) is also accepted; see the docstrings. These derivations are heuristics: say so when a number drives a decision, and override with real forecasts when the team has them.

**Dates.** Schedule, milestone and overdue checks use `--as-of YYYY-MM-DD`, defaulting to `portfolio_metadata.generated_on` and otherwise the latest date in the file, so a report is reproducible and the sample does not drift with today's date. Pass `--as-of` with today's date for a live review.

**Exit codes.** `0` report produced · `2` missing or unreadable file, invalid JSON, or the wrong shape (for example no `projects`, a project without `id`, no `stakeholders`). The tools report; they do not gate, so a red project still exits 0.

## Anti-Patterns

### Burying the ask in the executive report
**Mistake:** The 20-slide deck puts the decision the exec must make on slide 14.
**Why it happens:** Decks follow the order the work happened, so the ask lands at the end.
**Instead:** Put the decision or ask on slide 1 or in the first 100 words. Any ask past slide 5 means the report needs restructuring. Executives skim, and a missed ask leads to a decision made on incomplete data.

### Averaging the portfolio into one color
**Mistake:** The dashboard shows portfolio health as a single R/Y/G. Two projects are red, but the aggregate reads yellow.
**Why it happens:** One summary color is what executives asked for, and averaging is the easy way to produce it.
**Instead:** Name each red project next to any aggregate from `project_health_dashboard.py`. Eight greens and two reds is not a yellow portfolio. It has two projects that need attention now.

### A risk matrix with no mitigations
**Mistake:** The risk matrix plots 22 risks by probability and impact, with no mitigation column.
**Why it happens:** Plotting and scoring feel like the analysis, so the plan for each risk gets left for later.
**Instead:** Give every risk a mitigation before the matrix goes to anyone. `risk_matrix_analyzer.py` outputs a mitigation strategy, so carry it into the report instead of showing the plot alone.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology-and-operations.md](references/methodology-and-operations.md)** — the full three-tier analysis approach, prioritization models, risk framework, stakeholder-mapping detail, asset/template descriptions, weekly/monthly/quarterly workflows, handoff protocols, KPIs, anti-patterns, troubleshooting, success criteria, and Python tool flag reference. Read this for any hands-on portfolio, risk, capacity, or reporting work.
- **[references/portfolio-prioritization-models.md](references/portfolio-prioritization-models.md)** — deep dive on WSJF/RICE/ICE/MoSCoW/MCDA and the model-selection decision tree. Read when choosing or defending a prioritization model.
- **[references/risk-management-framework.md](references/risk-management-framework.md)** — full quantitative risk process: identification, three-point estimation, EMV, portfolio correlation, risk appetite. Read for any non-trivial risk analysis.
- **[references/stakeholder-engagement-guide.md](references/stakeholder-engagement-guide.md)** — Mendelow quadrant playbooks, blocker engagement, communication cadences. Read when building a stakeholder/communication plan.
- **[references/red-flags.md](references/red-flags.md)** — common ways this skill's output goes wrong, with fixes. Read before finalizing a portfolio assessment or executive report.

## Scope & Limitations

**In Scope:** Multi-project portfolio health assessment with weighted composite scoring; probability/impact risk analysis with category weighting (EMV and Monte Carlo by hand, guided by the references); resource capacity planning with utilization optimization and skill-matching; stakeholder mapping with Mendelow's Matrix and targeted communication plans; executive-level reporting with RAG status dashboards and strategic recommendations.

**Out of Scope:** Sprint-level team management (see `scrum-master/`); product backlog management and feature prioritization (see `execution/prioritization-frameworks/`); agile coaching and team maturity (see `agile-coach/`); financial modeling beyond project-level ROI (see `finance/`); contract negotiation and procurement.

**Important Caveats:** Health scores use fixed thresholds (see the script headers); calibrate them to your portfolio. The tools do not compute EMV or Monte Carlo forecasts; `references/risk-management-framework.md` explains how to do that by hand when the decision warrants it. Capacity is a weekly snapshot and assumes the named resources are the whole team, so a project staffed partly by people outside the file shows a large gap; check that before escalating. Inputs are self-reported and the tools check arithmetic, not truth.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `scrum-master/` | Receives from | Sprint velocity and health metrics feed portfolio-level health dashboards |
| `sprint-retrospective/` | Receives from | Retro insights inform stakeholder reports and process improvement tracking |
| `execution/brainstorm-okrs/` | Feeds into | Portfolio priorities and strategic context shape quarterly OKR themes |
| `execution/outcome-roadmap/` | Feeds into | Portfolio health data influences roadmap commitment levels (Now/Next/Later) |
| `discovery/pre-mortem/` | Receives from | Launch-blocking tigers escalate into portfolio risk register |
| `execution/release-notes/` | Complements | Release notes incorporate stakeholder communication plans from mapper |
| Jira via Atlassian MCP | Bidirectional | Pull project data for health analysis; push status reports to Confluence |
| Financial Systems | Receives from | Real-time budget and spend data for variance analysis |

## Files

| File | Purpose |
|------|---------|
| `scripts/project_health_dashboard.py` | Per-project health scores, RAG, interventions |
| `scripts/risk_matrix_analyzer.py` | Risk matrix, categories, overdue mitigations |
| `scripts/resource_capacity_planner.py` | Utilisation, demand vs capacity, gaps |
| `scripts/stakeholder_mapper.py` | Mendelow quadrants and communication plan |
| `assets/sample_project_data.json` | Four-project portfolio with resources and risks |
| `assets/sample_stakeholders.json` | Ten stakeholders for the mapper |
| `assets/expected_output.json` | Key results of the first three tools on the sample |
| `assets/*_template.md` | Charter, RACI, stakeholder map and executive report templates |
