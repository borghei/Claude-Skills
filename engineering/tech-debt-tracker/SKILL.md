---
name: tech-debt-tracker
description: >
  Scans codebases for technical debt with AST parsing, prioritizes debt items by
  impact, and generates trend dashboards. Use when tracking tech debt across a
  codebase, prioritizing refactoring work, calculating cost-of-delay for debt
  items, planning sprint debt allocation, or generating executive debt reports.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: code-quality
  tier: POWERFUL
  updated: 2026-03-31
---
# Tech Debt Tracker

The agent identifies, scores, prioritizes, and tracks technical debt across codebases using AST parsing, cost-of-delay analysis, and trend dashboards.

## Workflow

1. **Scan codebase** -- Run the Debt Scanner against the target repository. It uses AST parsing and pattern matching to detect debt signals across all six categories (code, architecture, test, documentation, dependency, infrastructure).
2. **Score each item** -- Apply the Severity Scoring Framework. Rate each item on velocity impact, quality impact, productivity impact, and business impact (1-10 each). Estimate effort (XS-XL) and risk level.
3. **Calculate interest rate** -- For each item, compute `Interest Rate = Impact Score x Frequency of Encounter` per sprint. Calculate `Cost of Delay = Interest Rate x Sprints Until Fix x Team Size Multiplier`.
4. **Prioritize** -- Plot items on the Cost-of-Delay vs Effort matrix. Assign priority: Immediate (high cost, low effort), Planned (high cost, high effort), Opportunistic (low cost, low effort), Backlog (low cost, high effort).
5. **Allocate sprint capacity** -- Apply the Debt-to-Feature Ratio based on current team velocity. Reserve the recommended percentage for debt work.
6. **Generate reports** -- Produce the Executive Dashboard (health score, trend, top risks, investment recommendation) and the Engineering Dashboard (daily new/resolved, interest rate by component, hotspots).
7. **Track trends** -- Compare current scan against previous baselines. Alert if debt accumulation rate exceeds paydown rate for two consecutive sprints.

## Debt Classification

| Category | Key Indicators | Detection Method |
|----------|---------------|-----------------|
| Code | Functions > 50 lines, nesting > 4 levels, cyclomatic complexity > 10, duplicate blocks > 3 | AST parsing, complexity metrics |
| Architecture | Circular dependencies, tight coupling, missing abstraction layers, monolithic components | Dependency analysis, coupling metrics |
| Test | Coverage < 80% on critical paths, flaky tests, test suite > 10 min | Coverage reports, failure pattern analysis |
| Documentation | Missing API docs, outdated READMEs, no ADRs, stale comments | Coverage analysis, freshness checking |
| Dependency | Known CVEs, deprecated APIs, unused packages, version conflicts | Vulnerability scanning, usage analysis |
| Infrastructure | Manual deploys, missing monitoring, env inconsistencies, no DR plan | Audit checklists, config drift detection |

## Severity Scoring Framework

Rate each dimension 1-10:

| Dimension | 1-2 | 5-6 | 9-10 |
|-----------|-----|-----|------|
| Velocity Impact | Negligible | Affects some features | Blocks new development |
| Quality Impact | No defect increase | Moderate defect increase | Critical reliability problems |
| Productivity Impact | No team impact | Regular complaints | Causing developer turnover |
| Business Impact | No customer impact | Moderate performance hit | Revenue-impacting issues |

**Effort sizing**: XS (1-4 hrs), S (1-2 days), M (3-5 days), L (1-2 weeks), XL (3+ weeks)

## Interest Rate and Cost of Delay

```
Interest Rate = Impact Score x Frequency of Encounter (per sprint)
Cost of Delay = Interest Rate x Sprints Until Fix x Team Size Multiplier

Example:
  Legacy auth module with poor error handling
  Impact: 7  |  Frequency: 15 encounters/sprint  |  Team: 8 devs
  Planned fix: sprint 4 (3 sprints away)

  Interest Rate = 7 x 15 = 105 points/sprint
  Cost of Delay = 105 x 3 x 1.2 = 378 total cost points
```

## Prioritization Matrix

| Quadrant | Cost of Delay | Effort | Action |
|----------|--------------|--------|--------|
| Immediate (quick wins) | High | Low | Do first |
| Planned (major initiatives) | High | High | Schedule dedicated sprints |
| Opportunistic | Low | Low | Fix when touching related code |
| Backlog | Low | High | Reconsider quarterly |

### WSJF Alternative

```
WSJF = (Business Value + Time Criticality + Risk Reduction) / Effort
```

Each component scored 1-10. Highest WSJF items are prioritized first.

## Sprint Allocation (Debt-to-Feature Ratio)

| Team Velocity | Debt % | Feature % | Strategy |
|--------------|--------|-----------|----------|
| < 70% of capacity | 60% | 40% | Remove major blockers |
| 70-85% of capacity | 30% | 70% | Balanced maintenance |
| > 85% of capacity | 15% | 85% | Opportunistic only |

**Sprint planning rule**: Reserve 20% of sprint capacity for debt. Prioritize items with the highest interest rates. Add "debt tax" to feature estimates when working in high-debt areas.

## Debt Item Data Structure

```json
{
  "id": "DEBT-2024-001",
  "title": "Legacy user authentication module",
  "category": "code",
  "subcategory": "error_handling",
  "location": "src/auth/legacy_auth.py:45-120",
  "description": "Authentication error handling uses generic exceptions",
  "impact": { "velocity": 7, "quality": 8, "productivity": 6, "business": 5 },
  "effort": { "size": "M", "risk": "medium", "skill_required": "mid" },
  "interest_rate": 105,
  "cost_of_delay": 378,
  "priority": "high",
  "status": "identified",
  "tags": ["security", "user-experience", "maintainability"]
}
```

**Status lifecycle**: Identified > Analyzed > Prioritized > Planned > In Progress > Review > Done | Won't Fix

## Refactoring Strategies

| Strategy | When to Use | How It Works |
|----------|-------------|-------------|
| Strangler Fig | Large monoliths, high-risk migrations | Build new around old; gradually redirect traffic; remove old |
| Branch by Abstraction | Need old + new running in parallel | Create interface; implement both behind it; switch via config |
| Feature Toggles | Gradual rollout of refactored components | Add toggle at decision points; test both paths; remove old |
| Parallel Run | Critical business logic changes | Run both implementations; compare outputs; build confidence |

## Executive Dashboard

```
TECH DEBT HEALTH
  Overall Score: [0-100]  |  Trend: [improving/declining]
  Cost of Delayed Fixes: [X development days]
  High-Risk Items: [count]

MONTHLY REPORT:
  1. Executive Summary (3 bullet points)
  2. Health Score Trend (6-month view)
  3. Top 3 Risk Items (business impact focus)
  4. Investment Recommendation (resource allocation)
  5. Success Stories (debt resolved last month)
```

## Engineering Dashboard

```
DAILY:
  New items identified  |  Items resolved  |  Interest rate by component

SPRINT REVIEW:
  Debt points completed vs planned  |  Velocity impact
  Newly discovered debt  |  Team code quality sentiment
```

## Example: Scanning a Python Microservice

```bash
# Run debt scanner
python scripts/debt_scanner.py --repo ./payment-service --output debt_inventory.json

# Output summary:
#   Total items found: 47
#   Critical: 3  |  High: 8  |  Medium: 21  |  Low: 15
#
#   Top 3 by cost-of-delay:
#     1. DEBT-001: payment_processor.py - nested exception handling (CoD: 420)
#     2. DEBT-002: db/migrations/ - 12 unapplied migrations (CoD: 315)
#     3. DEBT-003: tests/ - 62% coverage on payment flow (CoD: 280)

# Prioritize items
python scripts/debt_prioritizer.py --inventory debt_inventory.json --sprint-capacity 40

# Generate executive report
python scripts/debt_dashboard.py --inventory debt_inventory.json --baseline previous_scan.json
```

## Quarterly Planning

1. Identify 1-2 major debt themes per quarter
2. Allocate dedicated sprints for large-scale refactoring
3. Plan debt work around major feature releases
4. Track: debt interest rate reduction, velocity improvements, defect rate reduction, code review cycle time

## Scripts

### Debt Scanner (`debt_scanner.py`)
Scans codebase using AST parsing and pattern matching. Detects all six debt categories. Outputs structured JSON inventory.

### Debt Prioritizer (`debt_prioritizer.py`)
Analyses debt inventory using cost-of-delay and WSJF frameworks. Outputs prioritized backlog with sprint allocation recommendations.

### Debt Dashboard (`debt_dashboard.py`)
Generates trend reports comparing current scan against baselines. Produces executive and engineering dashboard views.

## References

See `REFERENCE.md` for the complete Technical Debt Quadrant (Fowler), detailed detection heuristics per category, and implementation roadmap phases.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Scanner finds zero debt items | Target directory contains no recognized file extensions, or all files match ignore patterns | Verify the directory path is correct and contains source files. Check `--config` to ensure `file_extensions` and `ignore_patterns` are appropriate for your stack. |
| AST parsing errors on valid Python files | Files use syntax from a newer Python version than the runtime executing the scanner | Run the scanner with the same Python version the target codebase requires (e.g., `python3.12 scripts/debt_scanner.py`). |
| Duplicate code detection is slow on large repos | The scanner hashes every N-line sliding window across all files, which scales quadratically with file count | Reduce scope by scanning one service directory at a time, or increase `min_duplicate_lines` in the config to reduce candidate blocks. |
| Prioritizer produces all-zero cost-of-delay scores | Input inventory lacks `severity` or `type` fields that the enrichment step depends on | Ensure the inventory JSON was produced by `debt_scanner.py` or follows the Debt Item Data Structure documented above. Manual inventories must include `type` and `severity` per item. |
| Dashboard shows "No valid data files loaded" | Files passed as arguments are not valid JSON, or the JSON structure is unrecognized | The dashboard accepts scanner output (`debt_items` key), prioritizer output (`prioritized_backlog` key), or a raw JSON array of debt items. Validate file contents with `python -m json.tool <file>`. |
| Health score is unexpectedly low despite few critical items | High debt density (items per file) dominates the health formula even when individual severities are low | Review the density contribution: health penalizes 10 points per item-per-file. Break large files into smaller modules or resolve low-severity bulk items like `todo_comment` and `missing_docstring`. |
| Sprint allocation plan shows hundreds of sprints | Default debt capacity is 20% of `--sprint-capacity`, which may be too low for a large backlog | Increase `--sprint-capacity` to reflect actual team hours, or filter the inventory to high-priority items before running the prioritizer. |

## Success Criteria

- Scan completes in under 60 seconds for repositories up to 100,000 lines of code.
- Every detected debt item includes a unique ID, file path, line number (where applicable), severity, and debt type -- no fields left as null or unknown.
- Health score correlates with manual code review assessments within 15 points on the 0-100 scale when validated against a senior engineer's judgment.
- Prioritized backlog produces a clear top-10 list where the first item has at least 2x the priority score of the tenth item, confirming meaningful differentiation.
- Sprint allocation recommendations fit within the configured capacity (no single sprint exceeds 100% of debt budget) and cover all high-priority items within the first 3 sprints.
- Dashboard trend analysis correctly identifies improving, declining, or stable directions when compared against at least 3 historical snapshots with known trajectories.
- Cost-of-delay calculations produce actionable dollar-equivalent values that engineering managers can use directly in sprint planning and quarterly roadmap discussions.

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

## Tool Reference

### Debt Scanner (`scripts/debt_scanner.py`)

**Purpose:** Scans a codebase directory for technical debt signals using AST parsing (Python files) and regex pattern matching (all languages). Detects code smells, large functions, high complexity, duplicate code, TODO comments, and common anti-patterns. Produces a structured JSON inventory and a human-readable text report.

**Usage:**
```bash
python scripts/debt_scanner.py <directory> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `directory` | positional, required | -- | Path to the directory to scan. |
| `--config` | string | None | Path to a JSON configuration file that overrides default thresholds (e.g., `max_function_length`, `max_complexity`, `ignore_patterns`). |
| `--output` | string | None | Output file path. When set, writes report to file instead of stdout. JSON output appends `.json`, text output appends `.txt`. |
| `--format` | choice | `both` | Output format: `json`, `text`, or `both`. |

**Example:**
```bash
python scripts/debt_scanner.py ./src --config custom_thresholds.json --output scan_results --format both
```

**Output Formats:**
- **JSON:** Contains `scan_metadata`, `summary` (files scanned, lines scanned, health score, debt density, priority/type breakdowns), `debt_items` (array of debt objects with id, type, description, file_path, severity, metadata, priority_score, priority), `file_statistics`, and `recommendations`.
- **Text:** Human-readable report with header, summary statistics, priority breakdown, top 10 debt items, and numbered recommendations.

---

### Debt Prioritizer (`scripts/debt_prioritizer.py`)

**Purpose:** Takes a debt inventory (from the scanner or a manual JSON file) and enriches each item with effort estimates, business impact scores, interest rate calculations, and cost-of-delay values. Produces a prioritized backlog with sprint allocation recommendations using one of three frameworks: cost-of-delay, WSJF, or RICE.

**Usage:**
```bash
python scripts/debt_prioritizer.py <inventory_file> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `inventory_file` | positional, required | -- | Path to debt inventory JSON file (scanner output, prioritizer output, or raw array of debt items). |
| `--output` | string | None | Output file path. JSON output appends `.json`, text output appends `.txt`. |
| `--format` | choice | `both` | Output format: `json`, `text`, or `both`. |
| `--framework` | choice | `cost_of_delay` | Prioritization framework: `cost_of_delay`, `wsjf`, or `rice`. |
| `--team-size` | integer | `5` | Number of developers on the team. Affects interest rate team impact multiplier and RICE reach calculation. |
| `--sprint-capacity` | integer | `80` | Total sprint capacity in hours. 20% is allocated to debt work by default. Used for sprint allocation planning. |

**Example:**
```bash
python scripts/debt_prioritizer.py scan_results.json --framework wsjf --team-size 8 --sprint-capacity 120 --output prioritized --format json
```

**Output Formats:**
- **JSON:** Contains `metadata` (analysis date, framework, team size, sprint capacity), `prioritized_backlog` (enriched items sorted by priority score, each with `effort_estimate`, `business_impact`, `interest_rate`, `cost_of_delay`, `category`, `impact_tags`), `sprint_allocation` (total debt hours, capacity per sprint, sprint plan with item assignments), `insights` (category distribution, effort breakdown, quick wins count, cost totals), `charts_data` (scatter, pie, timeline, interest trend arrays), and `recommendations`.
- **Text:** Executive summary with total effort and cost-of-delay, sprint allocation plan (first 3 sprints with top items), top 10 priority items with scores and tags, and numbered recommendations.

---

### Debt Dashboard (`scripts/debt_dashboard.py`)

**Purpose:** Takes one or more historical debt inventory files (from the scanner or prioritizer) and generates trend analysis, debt velocity tracking (accruing vs. paying down), health score timelines, forecasts, and an executive summary. Supports loading files individually or from a directory.

**Usage:**
```bash
python scripts/debt_dashboard.py [files...] [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `files` | positional, optional | -- | One or more debt inventory JSON file paths. Accepts scanner output, prioritizer output, or raw arrays. |
| `--input-dir` | string | None | Directory containing debt inventory JSON files. All `*.json` files in the directory are loaded. Mutually exclusive usage with positional `files`. |
| `--output` | string | None | Output file path. JSON output appends `.json`, text output appends `.txt`. |
| `--format` | choice | `both` | Output format: `json`, `text`, or `both`. |
| `--period` | choice | `monthly` | Analysis period for trend grouping: `weekly`, `monthly`, or `quarterly`. |
| `--team-size` | integer | `5` | Number of developers on the team. Used for velocity impact estimation. |

**Example:**
```bash
python scripts/debt_dashboard.py --input-dir ./debt_scans/ --period quarterly --team-size 10 --output dashboard --format both
```

**Output Formats:**
- **JSON:** Contains `metadata` (generated date, period, snapshot count, date range, team size), `executive_summary` (overall status, health score, status message, key insights, total debt items, effort hours, high priority count, velocity impact percent), `current_health` (overall score, debt density, velocity impact, quality score, maintainability score, technical risk score), `trend_analysis` (per-metric trend direction, change rate, correlation strength, forecast, confidence interval), `debt_velocity` (per-period new/resolved items, net change, velocity ratio, effort hours added/resolved), `forecasts` (3-month and 6-month projections for health, debt count, risk), `recommendations` (prioritized strategic actions with category, impact, effort), `visualizations` (health timeline, debt accumulation, category distribution, velocity chart, effort trend arrays), and `detailed_metrics`.
- **Text:** Executive summary with status and key metrics, current health metrics, trend analysis with directional indicators, and top 5 strategic recommendations with priority, impact, and effort ratings.
