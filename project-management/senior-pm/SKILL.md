---
name: senior-pm
description: >
  Senior PM for enterprise software and SaaS — portfolio management,
  quantitative risk analysis, prioritization, and executive reporting.
  Use for portfolio health reviews, board-ready status reports, and
  multi-project risk/capacity analysis.
license: MIT + Commons Clause
metadata:
  version: 2.0.1
  author: borghei
  category: project-management
  domain: enterprise-pm
  updated: 2026-06-15
  tags: [project-management, stakeholder-management, risk, planning]
  python-tools: project_health_dashboard.py, risk_matrix_analyzer.py, resource_capacity_planner.py, stakeholder_mapper.py
  tech-stack: portfolio-management, risk-analysis, stakeholder-mapping, executive-reporting
---
# Senior Project Management Expert

## Overview

Strategic project management for enterprise software, SaaS, and digital transformation initiatives. This skill provides sophisticated portfolio management capabilities, quantitative analysis tools, and executive-level reporting frameworks for managing complex, multi-million dollar project portfolios. It pairs deterministic Python analysis (health scoring, risk matrices, capacity planning, stakeholder mapping) with board-ready communication frameworks.

## Use when

- The user asks to "run a portfolio health review", "build an executive status report", or "do a stakeholder map"
- Multiple projects need prioritization across WSJF / RICE / ICE / MoSCoW with strategic alignment
- A board-ready or executive-ready RAG report needs to be produced
- Risk analysis needs EMV, Monte Carlo, or portfolio risk correlation — beyond a basic probability/impact matrix
- Resource capacity planning is needed across multiple concurrent projects
- A quarterly portfolio rebalancing or three-horizons review is being planned
- The user says "our portfolio is misaligned", "executives don't trust the reports", or "we can't tell which projects are actually healthy"

## Core Capabilities

- **Portfolio health & strategic alignment** — multi-dimensional weighted scoring (timeline, budget, scope, quality, risk), RAG status, three-horizons rebalancing
- **Quantitative risk management** — EMV analysis, three-point/Monte Carlo estimation, category weighting, portfolio risk correlation, risk-appetite framework
- **Advanced prioritization** — WSJF, RICE, ICE, MoSCoW, MCDA with a model-selection decision tree
- **Resource capacity planning** — utilization optimization (70-85% band), skill matching, bottleneck identification, scenario planning
- **Executive communication & governance** — board-ready RAG reports, RACI matrices, escalation paths, risk-adjusted ROI/NPV

## Clarify First

Before generating the report or analysis, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which artifact** — portfolio health review, executive status report, stakeholder map, or risk/capacity analysis (each maps to a different tool and structure)
- [ ] **Audience** — board, exec staff, or delivery team (sets the altitude, RAG framing, and level of detail)
- [ ] **Portfolio scope and data** — which projects and what timeline/budget/risk data exists (scores and dashboards are only as good as the inputs)
- [ ] **Prioritization model** — WSJF, RICE, ICE, or MoSCoW, when ranking projects (each produces a different order)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Tier 1 — portfolio health (multi-dimensional RAG scoring)
python3 scripts/project_health_dashboard.py assets/sample_project_data.json

# Tier 2 — quantitative risk matrix + mitigation strategy
python3 scripts/risk_matrix_analyzer.py assets/sample_project_data.json

# Tier 3 — resource capacity / utilization
python3 scripts/resource_capacity_planner.py assets/sample_project_data.json

# Stakeholder mapping (Mendelow's Matrix + comms plan)
python3 scripts/stakeholder_mapper.py --demo --format json
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology-and-operations.md](references/methodology-and-operations.md)** — the full three-tier analysis approach, prioritization models, risk framework, stakeholder-mapping detail, asset/template descriptions, weekly/monthly/quarterly workflows, handoff protocols, KPIs, anti-patterns, troubleshooting, success criteria, and Python tool flag reference. Read this for any hands-on portfolio, risk, capacity, or reporting work.
- **[references/portfolio-prioritization-models.md](references/portfolio-prioritization-models.md)** — deep dive on WSJF/RICE/ICE/MoSCoW/MCDA and the model-selection decision tree. Read when choosing or defending a prioritization model.
- **[references/risk-management-framework.md](references/risk-management-framework.md)** — full quantitative risk process: identification, three-point estimation, EMV, portfolio correlation, risk appetite. Read for any non-trivial risk analysis.
- **[references/stakeholder-engagement-guide.md](references/stakeholder-engagement-guide.md)** — Mendelow quadrant playbooks, blocker engagement, communication cadences. Read when building a stakeholder/communication plan.
- **[references/red-flags.md](references/red-flags.md)** — common ways this skill's output goes wrong, with fixes. Read before finalizing a portfolio assessment or executive report.

## Scope & Limitations

**In Scope:** Multi-project portfolio health assessment with weighted composite scoring; quantitative risk analysis using EMV, probability/impact matrices, and category weighting; resource capacity planning with utilization optimization and skill-matching; stakeholder mapping with Mendelow's Matrix and targeted communication plans; executive-level reporting with RAG status dashboards and strategic recommendations.

**Out of Scope:** Sprint-level team management (see `scrum-master/`); product backlog management and feature prioritization (see `execution/prioritization-frameworks/`); agile coaching and team maturity (see `agile-coach/`); financial modeling beyond project-level ROI (see `finance/`); contract negotiation and procurement.

**Important Caveats:** Health scores use deterministic formulas, not ML predictions — calibrate thresholds to your portfolio. Risk EMV assumes independent risks; portfolio correlation analysis (Step 4) gives a more accurate combined view but needs cross-project dependency data. Capacity models are weekly snapshots; they do not account for intra-week variability or unplanned spikes.

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
