---
name: tech-debt-tracker
description: >
  Scan codebases for technical debt with AST parsing, prioritize by impact, and generate trend
  dashboards. Use when tracking tech debt, prioritizing refactoring, calculating cost-of-
  delay, planning sprint debt, or reporting debt to execs.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: code-quality
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - technical-debt
    - code-quality
    - refactoring
    - ast
    - prioritization
---
# Tech Debt Tracker

The agent identifies, scores, prioritizes, and tracks technical debt across codebases using AST parsing, cost-of-delay analysis, and trend dashboards.

## Core Capabilities

- **Detection** — AST parsing (Python) and regex pattern matching (all languages) across six debt categories: code, architecture, test, documentation, dependency, infrastructure.
- **Interest rate** — the number this skill adds: `interest = impact x frequency` (how much the debt slows work each time the code is touched), and `cost of delay = interest x sprints x team multiplier`. Rank by cost of delay over effort; WSJF and RICE are available as alternatives.
- **Data flow** — `debt_scanner.py` produces the inventory, `debt_prioritizer.py` scores and schedules it, `debt_dashboard.py` compares snapshots over time.

## When to Use

- Tracking and quantifying technical debt across a repository.
- Prioritizing refactoring work and calculating cost-of-delay.
- Planning sprint capacity allocation between debt and features.
- Reporting debt health, trends, and investment recommendations to execs.

## Clarify First

Before scanning or reporting, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target codebase:** the directory to scan (the subject of the debt inventory).
- **Prioritization framework & team size:** cost-of-delay / WSJF / RICE and headcount (`--framework`, `--team-size`; changes the ranking and sprint allocation).
- **Report audience:** exec dashboard vs engineering inventory (sets the report format and altitude).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `debt_scanner.py` | Scan a directory for debt signals; output JSON inventory + text report | `python scripts/debt_scanner.py <dir> --output scan_results --format both` |
| `debt_prioritizer.py` | Enrich inventory with cost-of-delay/WSJF/RICE and sprint allocation | `python scripts/debt_prioritizer.py scan_results.json --framework wsjf --team-size 8` |
| `debt_dashboard.py` | Trend analysis, velocity, forecasts, and exec summary across snapshots | `python scripts/debt_dashboard.py --input-dir ./debt_scans/ --period quarterly` |

Runnable on the bundled samples:

```bash
python scripts/debt_scanner.py assets/sample_codebase --format text
python scripts/debt_prioritizer.py assets/sample_debt_inventory.json --framework cost_of_delay
python scripts/debt_dashboard.py assets/historical_debt_2024-01-15.json assets/historical_debt_2024-02-01.json
```

The scanner reports each duplicated region once (overlapping windows are merged and
repetitive runs inside one file are ignored), so the 986-line sample yields about 60 items.
Health score is `100 - severity-weighted items per 1,000 lines` (critical 5, high 3, medium 1,
low 0.5), so it compares codebases of different sizes. Exit codes: `0` ok; `2` bad input
(missing directory or file, unreadable inventory).

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology.md](references/methodology.md)** — the 7-step workflow, debt-classification table, severity scoring framework, interest-rate/cost-of-delay formulas, prioritization matrix, WSJF, sprint allocation ratios, the debt-item JSON schema, refactoring strategies, and quarterly planning. Read when scoring, prioritizing, or planning.
- **[references/tool-reference.md](references/tool-reference.md)** — full parameter tables, examples, and output-format details for all three scripts plus the troubleshooting table. Read when running the scripts or debugging output.
- **[references/dashboards-and-examples.md](references/dashboards-and-examples.md)** — executive and engineering dashboard layouts, a worked Python-microservice scan example, and the success-criteria bar. Read when generating reports or validating quality.
- **[references/debt-classification-taxonomy.md](references/debt-classification-taxonomy.md)** — comprehensive taxonomy for classifying debt across dimensions with detection heuristics per category. Read when calibrating detection or labeling items.
- **[references/prioritization-framework.md](references/prioritization-framework.md)** — deep prioritization approaches based on business value, risk, effort, and strategic alignment. Read when designing a prioritization rubric.
- **[references/stakeholder-communication-templates.md](references/stakeholder-communication-templates.md)** — templates and guidelines for communicating debt status, impact, and recommendations to different stakeholder groups. Read when reporting to execs or product.

- **[references/quadrant-and-roadmap.md](references/quadrant-and-roadmap.md)** — the technical debt quadrant and the implementation roadmap phases. Read when framing debt for a team new to tracking it.

## Scope & Limitations

**This skill covers:**
- Static detection of code-level, architecture, test, documentation, dependency, and infrastructure debt via AST parsing (Python) and regex pattern matching (all languages).
- Quantitative prioritization of debt items using cost-of-delay, WSJF, and RICE frameworks with configurable team size and sprint capacity.
- Historical trend analysis, health scoring, debt velocity tracking, and executive/engineering dashboard generation from multiple scan snapshots.
- Sprint allocation planning with capacity-aware backlog scheduling and effort estimation by debt type.

**This skill does NOT cover:**
- Runtime performance profiling or production monitoring -- see `engineering/performance-profiler` and `engineering/observability-designer` for those concerns.
- Dependency vulnerability scanning (CVE detection) or software composition analysis -- see `engineering/dependency-auditor` for security-focused dependency review.
- Automated refactoring or code transformation -- the skill identifies and prioritizes debt but does not modify source code.
- Database schema debt, API contract drift, or infrastructure-as-code drift detection -- see `engineering/database-schema-designer`, `engineering/api-design-reviewer`, and `engineering/migration-architect` for those domains.

## Integration Points

| Skill | Use for |
|-------|---------|
| `engineering/dependency-auditor` | CVE and outdated-dependency findings to merge into the inventory |
| `engineering/ci-cd-pipeline-builder` | Gate builds on `summary.health_score` or new critical items |

## Anti-Patterns

### Counting Items Instead of Interest
**Mistake:** Reporting "we have 412 debt items" and prioritising by count per module.
**Why it happens:** Counts are what scanners produce.
**Instead:** Rank by interest: debt in code touched every sprint costs far more than debt in a file nobody opens. Weight by change frequency (for example `git log --since=6.months --name-only`).

### A Debt Sprint Every Quarter
**Mistake:** Saving all debt work for a dedicated cleanup sprint.
**Why it happens:** It is easy to negotiate once.
**Instead:** Reserve a fixed share of every sprint (the prioritizer's allocation) and fix debt where feature work already touches the code.

### Dashboards Without a Decision
**Mistake:** Sending executives a health trend with no ask.
**Why it happens:** The dashboard looks like the deliverable.
**Instead:** Lead with the decision: what to fund, what it unblocks, and what happens to delivery speed if nothing changes.

## Files

| File | Purpose |
|------|---------|
| `scripts/debt_scanner.py` | Codebase scan to a debt inventory with health score |
| `scripts/debt_prioritizer.py` | Cost-of-delay, WSJF or RICE ranking and sprint allocation |
| `scripts/debt_dashboard.py` | Trends, velocity and forecasts across snapshots |
| `assets/sample_codebase/` | Three-file codebase with planted debt |
| `assets/sample_debt_inventory.json`, `historical_debt_*.json` | Inventory and snapshots for the prioritizer and dashboard |
| `expected_outputs/*.json` | Reference outputs for the samples |
| `references/*.md` | Methodology, tool reference, dashboards, taxonomy, prioritization, communication templates, quadrant and roadmap |
