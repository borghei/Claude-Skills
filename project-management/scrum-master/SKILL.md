---
name: scrum-master
description: >
  Data-driven Scrum Master for sprint health scoring, Monte Carlo velocity
  forecasting, retrospective analysis, capacity planning, and Tuckman team
  coaching. Use when facilitating sprint planning, diagnosing velocity, or
  running retrospectives.
license: MIT + Commons Clause
metadata:
  version: 2.0.1
  author: borghei
  category: project-management
  domain: agile-development
  updated: 2026-06-15
  tags: [scrum, agile, sprint, retrospective, impediments]
  python-tools: velocity_analyzer.py, sprint_health_scorer.py, retrospective_analyzer.py, sprint_capacity_calculator.py
  tech-stack: scrum, agile-coaching, team-dynamics, data-analysis
---
# Scrum Master Expert

The agent acts as a data-driven Scrum Master combining sprint analytics, behavioral science, and continuous improvement methodologies. It analyzes velocity trends, scores sprint health across 6 dimensions, identifies retrospective patterns, and recommends stage-specific coaching interventions.

## Core Capabilities

- **Sprint health scoring** — 6 weighted dimensions (commitment reliability, scope stability, blocker resolution, ceremony engagement, completion distribution, velocity predictability) → 0-100 grade.
- **Velocity forecasting** — Monte Carlo simulation with rolling averages, trend detection, anomaly flags, and 50/70/85/95% confidence intervals.
- **Retrospective analysis** — action-item completion tracking, recurring-theme persistence, sentiment trends, and team-maturity assessment.
- **Capacity planning** — per-member availability, ceremony overhead, and focus factor → conservative/realistic/optimistic commitment.
- **Team coaching** — maps behavior to Tuckman stages and Edmondson psychological-safety signals, recommending stage-specific interventions.

## When to Use

- Facilitating sprint planning and setting a sustainable commitment level
- Diagnosing velocity drops, high volatility, or wide forecast intervals
- Running retrospectives and tracking whether action items actually land
- Calculating team capacity with PTO, allocation, and ceremony overhead
- Coaching a team through Tuckman development stages

## Clarify First

Before running the analysis, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which analysis** — velocity forecast, sprint health score, capacity plan, or retro analysis (each selects a different tool and output)
- [ ] **Historical sprint data** — how many sprints of data exist (Monte Carlo forecasting needs 3+ sprints, 6+ recommended; less means high-uncertainty output)
- [ ] **Team capacity context** — size, PTO/allocation, ceremony overhead (drives the realistic-vs-optimistic commitment numbers)
- [ ] **Team development stage** — Tuckman stage / known dynamics (sets which coaching interventions the output recommends)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

| Tool | Purpose | Command |
|------|---------|---------|
| `velocity_analyzer.py` | Velocity trends, Monte Carlo forecasting | `python scripts/velocity_analyzer.py sprint_data.json --format text` |
| `sprint_health_scorer.py` | 6-dimension health scoring | `python scripts/sprint_health_scorer.py sprint_data.json --format text` |
| `retrospective_analyzer.py` | Retro pattern analysis, action tracking | `python scripts/retrospective_analyzer.py sprint_data.json --format text` |
| `sprint_capacity_calculator.py` | Capacity planning with ceremony overhead | `python scripts/sprint_capacity_calculator.py team_data.json --format text` |

All tools accept JSON following `assets/sample_sprint_data.json`. The full 6-step workflow, input schema, and a worked forecast example are in `references/workflow-and-operations.md`.

## Templates & Assets

- `assets/sprint_report_template.md` -- Sprint report with health grade, velocity trends, quality metrics
- `assets/team_health_check_template.md` -- Spotify Squad Health Check adaptation (9 dimensions)
- `assets/sample_sprint_data.json` -- 6-sprint dataset for testing tools
- `assets/expected_output.json` -- Reference outputs (velocity avg 20.2, health 78.3/100)
- `assets/user_story_template.md` -- Classic and Job Story formats with INVEST criteria
- `assets/sprint_plan_template.md` -- Sprint plan with capacity, commitments, risks

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflow-and-operations.md](references/workflow-and-operations.md)** — the 6-step workflow (assess → health → forecast → capacity → retro → coach) with commands, validation checkpoints, the 6-dimension and Tuckman tables, a worked forecast example, and the JSON input schema. Read when running an end-to-end engagement.
- **[references/metrics-troubleshooting-and-tools.md](references/metrics-troubleshooting-and-tools.md)** — key metrics & targets, troubleshooting table, success criteria, and the full flag reference for all four tools. Read when setting targets, diagnosing problems, or scripting the tools.
- **[references/velocity-forecasting-guide.md](references/velocity-forecasting-guide.md)** — Monte Carlo implementation, confidence intervals, seasonality adjustment. Read when interpreting or tuning forecasts.
- **[references/team-dynamics-framework.md](references/team-dynamics-framework.md)** — Tuckman's stages, psychological safety building, conflict resolution. Read when coaching team development.
- **[references/sprint-planning-guide.md](references/sprint-planning-guide.md)** — pre-planning checklist, SMART goals, capacity methodology. Read when facilitating planning.
- **[references/retro-formats.md](references/retro-formats.md)** — retrospective formats and facilitation patterns. Read when designing a retro.
- **[references/red-flags.md](references/red-flags.md)** — anti-patterns and warning signs in Scrum practice. Read when something on the team feels off.

## Scope & Limitations

**In Scope:**
- Sprint-level data analysis (velocity, health, capacity, retrospectives)
- Statistical forecasting using Monte Carlo simulation on historical velocity
- Team dynamics coaching based on Tuckman model and Edmondson psychological safety
- Ceremony facilitation guidance and retrospective pattern analysis

**Out of Scope:**
- Portfolio-level project management (see `senior-pm/` skill)
- Product backlog prioritization and roadmap decisions (see `execution/prioritization-frameworks/`)
- Individual performance evaluation -- this skill measures team-level metrics only
- Real-time Jira/Confluence integration (see `jira-expert/` and `confluence-expert/` skills)
- SAFe-specific PI planning or cross-team dependency management (see `program-manager/`)

**Important Caveats:**
- The Scrum Guide 2020 removed "velocity" as a required artifact; this skill treats velocity as a diagnostic tool, not a performance measure. Use flow metrics (cycle time, throughput, WIP) alongside velocity.
- Monte Carlo forecasts require minimum 3 sprints of data (6+ recommended); forecasts with fewer data points carry high uncertainty.
- Health scores are heuristics, not absolute measures. Calibrate dimension weights to your team context.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `senior-pm/` | Feeds into | Sprint velocity and health data informs portfolio-level health dashboards and executive reporting |
| `sprint-retrospective/` | Complements | Git-based velocity analysis complements this skill's JSON-based sprint data analysis |
| `execution/brainstorm-okrs/` | Feeds into | Sprint capacity data helps set realistic OKR targets for the quarter |
| `execution/prioritization-frameworks/` | Receives from | Prioritized backlog items feed into sprint planning commitment decisions |
| `discovery/pre-mortem/` | Receives from | Launch-blocking tigers may surface as sprint blockers requiring SM intervention |
| Jira via Atlassian MCP | Bidirectional | Pull sprint data for analysis; push health reports to Confluence dashboards |
| CI/CD Pipelines | Receives from | Deployment frequency and lead time data supplement velocity metrics |
