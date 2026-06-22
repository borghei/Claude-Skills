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
  updated: 2026-06-17
---
# Tech Debt Tracker

The agent identifies, scores, prioritizes, and tracks technical debt across codebases using AST parsing, cost-of-delay analysis, and trend dashboards.

## Core Capabilities

- **Detection** — AST parsing (Python) and regex pattern matching (all languages) across six debt categories: code, architecture, test, documentation, dependency, infrastructure.
- **Severity scoring** — rate each item on velocity, quality, productivity, and business impact (1-10) plus effort sizing (XS-XL) and risk.
- **Cost-of-delay** — compute interest rate (`Impact x Frequency`) and cost of delay (`Interest x Sprints x Team Multiplier`); also WSJF and RICE frameworks.
- **Prioritization** — plot on the Cost-of-Delay vs Effort matrix (Immediate / Planned / Opportunistic / Backlog).
- **Sprint allocation** — apply the Debt-to-Feature ratio by team velocity; reserve capacity for debt work.
- **Refactoring strategies** — Strangler Fig, Branch by Abstraction, Feature Toggles, Parallel Run.
- **Reporting** — executive and engineering dashboards, trend analysis, velocity tracking, and forecasts from scan snapshots.

## When to Use

- Tracking and quantifying technical debt across a repository.
- Prioritizing refactoring work and calculating cost-of-delay.
- Planning sprint capacity allocation between debt and features.
- Reporting debt health, trends, and investment recommendations to execs.

## Clarify First

Before scanning or reporting, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target codebase** — the directory to scan (the subject of the debt inventory)
- [ ] **Prioritization framework & team size** — cost-of-delay / WSJF / RICE and headcount (`--framework`, `--team-size`; changes the ranking and sprint allocation)
- [ ] **Report audience** — exec dashboard vs engineering inventory (sets the report format and altitude)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `debt_scanner.py` | Scan a directory for debt signals; output JSON inventory + text report | `python scripts/debt_scanner.py <dir> --output scan_results --format both` |
| `debt_prioritizer.py` | Enrich inventory with cost-of-delay/WSJF/RICE and sprint allocation | `python scripts/debt_prioritizer.py scan_results.json --framework wsjf --team-size 8` |
| `debt_dashboard.py` | Trend analysis, velocity, forecasts, and exec summary across snapshots | `python scripts/debt_dashboard.py --input-dir ./debt_scans/ --period quarterly` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology.md](references/methodology.md)** — the 7-step workflow, debt-classification table, severity scoring framework, interest-rate/cost-of-delay formulas, prioritization matrix, WSJF, sprint allocation ratios, the debt-item JSON schema, refactoring strategies, and quarterly planning. Read when scoring, prioritizing, or planning.
- **[references/tool-reference.md](references/tool-reference.md)** — full parameter tables, examples, and output-format details for all three scripts plus the troubleshooting table. Read when running the scripts or debugging output.
- **[references/dashboards-and-examples.md](references/dashboards-and-examples.md)** — executive and engineering dashboard layouts, a worked Python-microservice scan example, and the success-criteria bar. Read when generating reports or validating quality.
- **[references/debt-classification-taxonomy.md](references/debt-classification-taxonomy.md)** — comprehensive taxonomy for classifying debt across dimensions with detection heuristics per category. Read when calibrating detection or labeling items.
- **[references/prioritization-framework.md](references/prioritization-framework.md)** — deep prioritization approaches based on business value, risk, effort, and strategic alignment. Read when designing a prioritization rubric.
- **[references/stakeholder-communication-templates.md](references/stakeholder-communication-templates.md)** — templates and guidelines for communicating debt status, impact, and recommendations to different stakeholder groups. Read when reporting to execs or product.

Also see the skill-root `REFERENCE.md` for the Technical Debt Quadrant (Fowler) and the implementation roadmap phases.

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

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/dependency-auditor` | Feed dependency audit findings into the scanner as `dependency_debt` items to unify all debt in one inventory. | Dependency audit JSON -> scanner config or manual merge into `debt_inventory.json` |
| `engineering/performance-profiler` | Correlate performance hotspots with high-complexity debt items to prioritize refactoring that yields both quality and speed gains. | Profiler hotspot report -> cross-reference with scanner output by file path |
| `engineering/ci-cd-pipeline-builder` | Add `debt_scanner.py` as a CI pipeline step to fail builds when health score drops below a threshold or critical debt count increases. | Scanner JSON output -> CI gate condition on `summary.health_score` |
| `engineering/pr-review-expert` | Surface relevant debt items during code review by querying the debt inventory for files touched in a pull request. | PR changed-files list -> filter `debt_inventory.json` by `file_path` |
| `engineering/observability-designer` | Map infrastructure debt items (missing monitoring, env inconsistencies) to observability gaps identified by the observability skill. | Dashboard `category_distribution` -> observability gap analysis |
| `engineering/migration-architect` | Use the prioritized backlog to scope and sequence large-scale migration efforts, especially for architecture-category debt rated as planned initiatives. | Prioritizer `sprint_allocation` -> migration planning timeline |
