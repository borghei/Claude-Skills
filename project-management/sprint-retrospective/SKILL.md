---
name: sprint-retrospective
description: >
  Data-driven sprint retrospectives with velocity analytics, contributor insights,
  code quality trends, and actionable improvement recommendations. Analyzes git history
  to produce comprehensive retrospective reports with session detection, churn hotspots,
  work pattern analysis, and sprint-over-sprint comparison dashboards.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: project-management
  domain: agile-ceremonies
  updated: 2026-03-18
  python-tools: velocity_analyzer.py, contributor_insights.py, code_churn_analyzer.py, retro_report_generator.py
  tech-stack: python, git, agile, scrum, analytics
---

# Sprint Retrospective Expert

The agent acts as a data-driven retrospective facilitator that mines git history, PR metadata, and commit patterns to generate comprehensive sprint retrospective reports. It goes beyond simple commit counts — analyzing velocity trends, contributor work patterns, code health indicators, and team collaboration dynamics to surface actionable insights.

## Keywords

sprint retrospective, velocity analytics, contributor insights, code churn, work sessions, cycle time, lead time, throughput, burndown, team health, collaboration metrics, bus factor, refactor ratio, hotspot analysis, conventional commits, session detection, deep work, improvement tracking

## Quick Start

```bash
# 1. Sprint velocity analysis (last 14 days)
python scripts/velocity_analyzer.py --days 14 --format json > velocity.json

# 2. Contributor deep dive
python scripts/contributor_insights.py --days 14 --format json > contributors.json

# 3. Code churn analysis
python scripts/code_churn_analyzer.py --days 14 --format json > churn.json

# 4. Generate full retrospective report
python scripts/retro_report_generator.py \
  --velocity velocity.json \
  --contributors contributors.json \
  --churn churn.json \
  --sprint-name "Sprint 23" \
  --output retro_sprint_23.md

# One-liner: full pipeline
python scripts/velocity_analyzer.py --days 14 -f json > /tmp/v.json && \
python scripts/contributor_insights.py --days 14 -f json > /tmp/c.json && \
python scripts/code_churn_analyzer.py --days 14 -f json > /tmp/ch.json && \
python scripts/retro_report_generator.py -v /tmp/v.json -c /tmp/c.json -u /tmp/ch.json -s "Sprint 23"
```

## Core Workflows

### 1. Sprint Velocity Analysis

Analyze throughput, cycle time, and delivery patterns across the sprint window.

```bash
# Default: last 7 days
python scripts/velocity_analyzer.py

# Custom range
python scripts/velocity_analyzer.py --since 2026-03-04 --until 2026-03-18

# Compare against previous period
python scripts/velocity_analyzer.py --days 14 --compare-previous

# JSON output for pipeline
python scripts/velocity_analyzer.py --days 14 --format json
```

**Metrics computed:**

| Metric | Description |
|--------|-------------|
| Total Commits | Raw commit count in window |
| LOC Added / Removed / Net | Lines of code delta |
| PRs Merged | Pull requests merged (via merge commit detection) |
| Avg PR Size | Average lines changed per PR |
| Throughput | Commits per day |
| Cycle Time | Avg time from first commit on branch to merge |
| Lead Time | Avg time from commit to production (main branch) |
| Deploy Frequency | Merges to main per day |
| Commit Type Breakdown | feat/fix/docs/refactor/test/chore distribution |
| Hourly Distribution | Commit activity by hour of day |

**Session Detection:**

The analyzer detects work sessions using configurable gap thresholds:

| Session Type | Duration | Interpretation |
|-------------|----------|----------------|
| Deep Work | >50 min | Sustained focused coding |
| Focused | 20-50 min | Standard development sessions |
| Micro | <20 min | Quick fixes, reviews, hotfixes |

Gap threshold default: 45 minutes. Commits within the gap belong to the same session.

**Trend Comparison:**

When `--compare-previous` is enabled, the tool compares the current window against the immediately preceding window of equal length and computes deltas with directional indicators.

### 2. Contributor Deep Dive

Per-person analysis of contributions, work patterns, and specialization areas.

```bash
# All contributors, last 14 days
python scripts/contributor_insights.py --days 14

# Single contributor focus
python scripts/contributor_insights.py --days 14 --author "jane@example.com"

# Include collaboration metrics
python scripts/contributor_insights.py --days 14 --collaboration
```

**Per-contributor metrics:**

- Commits, LOC added/removed, files touched
- Peak working hours (hourly heatmap)
- Session analysis (deep work ratio, session count)
- Focus areas by directory and file type
- Specialization detection: frontend / backend / infrastructure / docs / tests / data
- Consistency score (how evenly distributed are commits across the sprint)
- Collaboration: co-authored commits, cross-directory work

**Specialization Detection Rules:**

| Category | File Patterns |
|----------|--------------|
| Frontend | `*.tsx, *.jsx, *.vue, *.svelte, *.css, *.scss, *.html` |
| Backend | `*.py, *.go, *.rs, *.java, *.rb, *.php, *.cs` |
| Infrastructure | `Dockerfile, *.yml, *.yaml, terraform/*, k8s/*, .github/*` |
| Documentation | `*.md, *.rst, *.txt, docs/*` |
| Tests | `*test*, *spec*, __tests__/*` |
| Data | `*.sql, *.json, *.csv, migrations/*` |

### 3. Code Quality Trends

Identify churn hotspots, refactoring candidates, and code health indicators.

```bash
# Churn analysis
python scripts/code_churn_analyzer.py --days 14

# Top 20 hotspots
python scripts/code_churn_analyzer.py --days 14 --top 20

# Filter by directory
python scripts/code_churn_analyzer.py --days 14 --path src/

# Detect oscillation (files changed back and forth)
python scripts/code_churn_analyzer.py --days 14 --detect-oscillation
```

**Code Health Indicators:**

| Indicator | Calculation | Healthy Range |
|-----------|-------------|---------------|
| Churn Rate | Changes per file per day | <0.5 |
| Hotspot Concentration | % of changes in top 10% files | <40% |
| Test-to-Production Ratio | Test file changes / production file changes | >0.3 |
| Refactor Frequency | refactor commits / total commits | 10-25% |
| Oscillation Score | Files with >3 change-revert cycles | <5% of files |
| Directory Spread | Unique directories changed / total directories | Context-dependent |

**Hotspot Analysis:**

Files are ranked by a composite score: `changes * unique_authors * recency_weight`. High scores indicate files that are:
- Changed frequently (unstable or central)
- Touched by multiple people (potential conflict zone)
- Recently active (not historical noise)

### 4. Team Health Assessment

Evaluate collaboration patterns, review dynamics, and knowledge distribution.

```bash
# Team health from contributor data
python scripts/contributor_insights.py --days 14 --collaboration --format json
```

**Collaboration Metrics:**

| Metric | Description | Target |
|--------|-------------|--------|
| Review Coverage | % of PRs with at least one review | >90% |
| Cross-team PRs | PRs touching multiple team areas | Healthy: 10-30% |
| Knowledge Distribution | Files touched by only 1 person | <30% (bus factor) |
| Review Turnaround | Avg time from PR open to first review | <4 hours |
| Co-authored Commits | Commits with Co-authored-by trailers | Context-dependent |

**Bus Factor Analysis:**

For each directory, the tool computes how many contributors have touched files. Directories with only 1 contributor are flagged as knowledge silos.

### 5. Improvement Tracking

Track action items from previous retrospectives and measure follow-through.

```bash
# Generate report with action item tracking
python scripts/retro_report_generator.py \
  --velocity velocity.json \
  --contributors contributors.json \
  --churn churn.json \
  --previous-retro retro_sprint_22.md \
  --sprint-name "Sprint 23"

# Compare two sprints
python scripts/retro_report_generator.py \
  --velocity velocity_current.json \
  --contributors contributors_current.json \
  --churn churn_current.json \
  --previous-velocity velocity_previous.json \
  --sprint-name "Sprint 23"
```

The report generator extracts action items from previous retro reports (marked with `- [ ]` or `- [x]`) and includes a follow-through section showing completion status.

## Tools

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `velocity_analyzer.py` | Sprint throughput, cycle time, sessions | `--days`, `--since/--until`, `--compare-previous`, `--gap-minutes` |
| `contributor_insights.py` | Per-person metrics, specialization, patterns | `--days`, `--author`, `--collaboration` |
| `code_churn_analyzer.py` | File hotspots, churn rate, oscillation | `--days`, `--top`, `--path`, `--detect-oscillation` |
| `retro_report_generator.py` | Markdown report generation | `--velocity`, `--contributors`, `--churn`, `--previous-retro` |

All tools support:
- `--format text|json` (default: text)
- `--days N` for time window (default: 7)
- `--since YYYY-MM-DD --until YYYY-MM-DD` for custom ranges
- `--repo /path/to/repo` to analyze a specific repository (default: cwd)

## Time Windows

| Window | Use Case |
|--------|----------|
| 7 days | Weekly retrospectives, iteration reviews |
| 14 days | Standard 2-week sprint retrospectives |
| 30 days | Monthly health checks, PI reviews |
| Custom range | Release retrospectives, incident post-mortems |
| Sprint comparison | Progress tracking between sprints |

## Velocity Benchmarks

See `references/velocity_benchmarks.md` for industry benchmarks by team size, healthy velocity patterns, and when velocity metrics mislead.

## Session Analysis Deep Dive

Session detection uses timestamp gaps between consecutive commits by the same author:

1. Sort commits by author and timestamp
2. If gap between consecutive commits > threshold (default 45min), start new session
3. Classify session by total duration
4. Compute per-author session profile

**Why this matters:** A team doing 90% micro-sessions may be context-switching too much. A healthy ratio is roughly 40% deep work, 40% focused, 20% micro.

## Code Health Deep Dive

Churn analysis identifies:

- **Hotspots**: Files changed most frequently — candidates for refactoring or splitting
- **Oscillation**: Files where lines are added then removed repeatedly — signals unclear requirements or design churn
- **Test Coverage Proxy**: Ratio of test file changes to production file changes — declining ratio signals growing tech debt
- **Refactor Signal**: High proportion of `refactor:` commits in a file indicates active improvement

## Team Collaboration Deep Dive

Knowledge distribution analysis flags:

- **Single-owner files**: Only one person has ever modified them — bus factor risk
- **High-contention files**: Many authors, frequent changes — coordination overhead
- **Cross-boundary work**: Commits spanning multiple directories — integration work

## State Persistence & Trend Tracking

### Snapshot Storage
Save retro data after each sprint for historical comparison:

```bash
# Save sprint snapshot (auto-names by sprint)
python scripts/retro_report_generator.py -v velocity.json -c contributors.json -u churn.json \
  -s "Sprint 23" --save .retro-history/

# Compare two sprints
python scripts/retro_report_generator.py -v velocity.json -c contributors.json -u churn.json \
  -s "Sprint 24" --previous-velocity .retro-history/sprint-23-velocity.json
```

**Storage:** `.retro-history/{sprint-name}-{type}.json` — velocity, contributors, churn snapshots per sprint.

### Trend Analysis
After 3+ sprints, the report generator includes:
- **Velocity trajectory** — throughput and cycle time trending up, down, or stable
- **Sprint-over-sprint deltas** — percentage changes with directional indicators
- **Streak tracking** — consecutive sprints with improving velocity, shrinking cycle time, or growing test ratio
- **Attention alerts** — categories that degraded 3+ sprints in a row

### Action Item Carry-Over
The report generator parses previous retro reports for unchecked action items:
- Scans `- [ ]` checkboxes in prior `.retro-history/` markdown files
- Carries forward incomplete items into the new report's "Outstanding Actions" section
- Tracks completion rate: "3 of 5 action items from Sprint 22 completed (60%)"

---

## Narrative Generation Guidelines

A retrospective report is not a data dump — it tells the story of the sprint.

### Structure
1. **Tweetable summary** (1 sentence) — the sprint in a tweet. Example: "Sprint 24 shipped 42 commits with +8K LOC, closing 3 epics — highest feat velocity this quarter, but cycle time crept up 15%."
2. **Executive summary** (2-3 sentences) — data-driven, actionable, no filler
3. **Velocity dashboard** — metrics table with deltas vs previous
4. **Commit type distribution** — ASCII bar chart
5. **Work session analysis** — deep/focused/micro breakdown with implications
6. **Contributor spotlights** — per-person metrics, specialization, peak hours
7. **Code health indicators** — churn rate, hotspots, test ratio, refactor frequency
8. **Action items** — 3-5 specific, measurable improvements for next sprint
9. **Outstanding actions** — carry-over from previous retros

### Tone Guidelines
- **Celebratory for wins** — "Highest feature velocity in 4 sprints" not "Feature velocity increased"
- **Constructive for improvements** — "Cycle time crept up, suggesting review bottleneck" not "Cycle time is bad"
- **Never blame-oriented** — Frame around systems and processes, not individuals
- **Data-dense** — Every claim backed by a specific number. No "we shipped a lot" — say "42 commits, +8,247 LOC"
- **Word count target** — 1500-3000 words for a full report. Enough depth to be actionable, short enough to be read.

---

## Integration Points

### With Scrum Master Skill (`project-management/scrum-master/`)

```bash
# Use scrum-master capacity data alongside retro velocity
python scripts/velocity_analyzer.py --repo . --days 14 -f json > velocity.json
# Cross-reference with sprint capacity planning
python ../scrum-master/scripts/sprint_capacity_calculator.py team.json
```

### With Senior PM Skill (`project-management/senior-pm/`)

```bash
# Feed retro insights into stakeholder reports
python scripts/retro_report_generator.py -v velocity.json -c contributors.json -u churn.json -s "Sprint 24" -o retro.md
# Reference in PM executive reporting via senior-pm stakeholder tools
```

### With Delivery Manager Skill (`project-management/delivery-manager/`)

```bash
# Retro metrics inform release planning
# Velocity trends help delivery managers forecast sprint capacity
python scripts/velocity_analyzer.py --days 30 --compare-previous -f json
```

### With Agile Coach Skill (`project-management/agile-coach/`)

The agile coach uses retro trend data to identify systemic patterns:
- Declining deep work sessions → suggest focus time blocks
- Rising cycle time → investigate review process
- Low test ratio → recommend TDD adoption sprint

### CI/CD Integration

```yaml
# .github/workflows/sprint-retro.yml
name: Sprint Retrospective
on:
  schedule:
    - cron: '0 9 * * 5'  # Every Friday at 9am
  workflow_dispatch:
    inputs:
      days:
        description: 'Sprint length in days'
        default: '14'
jobs:
  retrospective:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: |
          python scripts/velocity_analyzer.py --days ${{ inputs.days || '14' }} -f json > velocity.json
          python scripts/contributor_insights.py --days ${{ inputs.days || '14' }} -f json > contributors.json
          python scripts/code_churn_analyzer.py --days ${{ inputs.days || '14' }} -f json > churn.json
          python scripts/retro_report_generator.py -v velocity.json -c contributors.json -u churn.json -s "Sprint $(date +%V)"
```

---

## Retrospective Facilitation

See `references/retrospective_facilitation.md` for:
- 8 retrospective formats (Start/Stop/Continue, 4Ls, Sailboat, DAKI, etc.)
- Facilitation techniques for remote and in-person teams
- Anti-patterns to avoid (blame game, scope creep, no follow-through)
- Psychological safety frameworks

---

## Output Examples

### Velocity Dashboard

```
Sprint Velocity Report — Sprint 24 (Mar 4-18, 2026)
═══════════════════════════════════════════════════════

Throughput:        8.2 commits/day (↑ 12% vs prev)
LOC Net:           +2,847 lines   (↓ 5% vs prev)
PRs Merged:        14             (↑ 17% vs prev)
Avg PR Size:       203 lines      (↓ 8% — smaller PRs!)
Cycle Time:        18.3 hours     (↑ 2h — review bottleneck?)
Deploy Frequency:  1.0/day        (stable)

Commit Types:
  feat     ████████████░░░░░░░░  42%
  fix      ██████░░░░░░░░░░░░░░  18%
  docs     ████░░░░░░░░░░░░░░░░  14%
  refactor ███░░░░░░░░░░░░░░░░░  12%
  test     ██░░░░░░░░░░░░░░░░░░   8%
  chore    ██░░░░░░░░░░░░░░░░░░   6%
```

### Contributor Spotlight

```
Contributor: jane@example.com
  Commits: 34 | LOC: +1,204 / -387 | Files: 28
  Sessions: 12 (deep: 5, focused: 4, micro: 3)
  Peak Hours: 10am-12pm, 2pm-4pm
  Specialization: Backend (67%), Tests (22%), Docs (11%)
  Consistency: 0.82 (highly consistent)
```

### Code Churn Analysis

```
File Hotspots (ranked by churn score)
─────────────────────────────────────────────────
  File                            Chg Auth Score
  ─────────────────────────────  ──── ──── ──────
  src/api/routes.ts                12    3   11.2 ██████████
  src/models/user.ts                8    2    7.4 ███████░░░
  README.md                         7    1    5.8 █████░░░░░

Refactoring Candidates:
  src/api/routes.ts — high churn (0.8/day), 3 authors, consider splitting
```

### Full Report (generated by pipeline)

```markdown
# Sprint Retrospective — Sprint 24

> Sprint 24 shipped 42 commits with +2.8K LOC across 14 PRs — strongest
> feature velocity this quarter, but cycle time crept up 15% suggesting
> a review bottleneck.

## Executive Summary
This sprint delivered 42 commits across 3 contributors, merging 14 PRs
with a net change of +2,847 lines. Feature work dominated at 42% of commits.
Cycle time increased to 18.3 hours (+2h vs Sprint 23), correlating with
larger average PR sizes in the auth migration epic.

## Velocity Dashboard
| Metric          | Sprint 24 | Sprint 23 | Delta   |
|-----------------|-----------|-----------|---------|
| Commits         | 42        | 38        | +10.5%  |
| LOC Net         | +2,847    | +2,996    | -5.0%   |
| PRs Merged      | 14        | 12        | +16.7%  |
| Cycle Time      | 18.3h     | 16.1h     | +13.7%  |

## Action Items
- [ ] Investigate review bottleneck — cycle time up 2h
- [ ] Split src/api/routes.ts — highest churn file (12 changes)
- [ ] Increase test ratio — currently 0.08, target 0.15
```

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| velocity_analyzer.py returns zero commits | Wrong date range, repo not fetched with full history, or branch filter excluding commits | Verify `--since`/`--until` dates; ensure `git fetch --all` was run; check `--repo` path points to a valid git repo |
| Session detection shows 100% micro sessions | Session gap threshold too low, or all commits are atomic (one-line changes) | Increase `--gap-minutes` from 45 to 60-90; micro-heavy patterns may genuinely indicate context-switching |
| Contributor specialization shows "other" for all files | File extensions not matching any SPECIALIZATION_PATTERNS category | Check if your codebase uses non-standard extensions; the tool classifies by extension and path patterns |
| Code churn hotspots dominated by generated files | Auto-generated files (lock files, builds, migrations) inflate churn scores | Use `--path src/` to filter to source code, or add generated file patterns to .gitignore |
| Retro report generator produces empty sections | Input JSON files contain `{}` or data keys do not match expected schema | Verify velocity JSON has `total_commits`, `loc`, `sessions` keys; run individual tools first to confirm output |
| Previous action items not detected in carry-over | Action items in prior retro not formatted as `- [ ]` or `- [x]` markdown checkboxes | Ensure previous retro follows the standard checkbox format; the parser requires `- [ ]` prefix |
| Cycle time estimate is zero or unrealistically low | No merge commits found in the period, or all work merged via squash without branch history | Cycle time requires merge commits; squash-merge workflows lose branch-to-merge timing data |

## Success Criteria

- Retrospective reports consistently generated within 5 minutes of sprint end using the 4-tool pipeline
- Velocity trends tracked over 3+ sprints with sprint-over-sprint delta comparison
- Code churn hotspots identified and addressed, reducing top-file churn rate below 0.5/day
- Test-to-production ratio maintained above 0.3 (healthy range)
- Deep work session ratio maintained above 30% of total sessions
- Action item completion rate from previous retros tracked and exceeds 60%
- Bus factor risks (single-owner directories) reduced sprint-over-sprint

## Scope & Limitations

**In Scope:**
- Git history analysis for velocity, contributor, and code churn metrics
- Session detection using commit timestamp gap analysis
- Commit type classification via conventional commit prefix parsing
- Markdown report generation with executive summary, dashboards, and action item tracking
- Sprint-over-sprint comparison with directional deltas
- Bus factor and knowledge silo identification

**Out of Scope:**
- Sprint planning and capacity calculation (see `scrum-master/` skill)
- JSON-based sprint data analysis with planned vs. completed points (see `scrum-master/velocity_analyzer.py`)
- Product-level OKR tracking or roadmap management (see `execution/` skills)
- Code quality analysis beyond churn (no static analysis, no test coverage measurement)
- Jira/Linear ticket-level cycle time (this skill uses git merge commits as proxy)

**Important Caveats:**
- All metrics are derived from git history only. Teams using squash merges lose branch-level cycle time data.
- Session detection is a heuristic based on commit timestamps; it does not measure actual focused work time.
- The Scrum Guide 2020 de-emphasized velocity as a required artifact. This skill treats velocity as a diagnostic signal, not a performance target. Flow metrics (cycle time, throughput, WIP) are first-class citizens alongside traditional velocity measures.
- Retrospective facilitation formats (4Ls, Starfish, Sailboat, DAKI) rotate every 3-5 sprints to prevent staleness. See `references/retrospective_facilitation.md` for format selection guidance.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `scrum-master/` | Complements | Git-based velocity supplements JSON-based sprint data analysis; cross-reference for fuller picture |
| `senior-pm/` | Feeds into | Retro velocity trends inform executive reporting and portfolio health dashboards |
| `delivery-manager/` | Feeds into | Velocity trends help delivery managers forecast sprint capacity and release timing |
| `agile-coach/` | Feeds into | Retro trend data identifies systemic patterns for coaching interventions |
| `execution/release-notes/` | Feeds into | Sprint commit data and type distribution inform release note generation |
| CI/CD Workflows | Automated | GitHub Actions workflow runs the 4-tool pipeline on a cron schedule (see CI/CD Integration section) |
| `.retro-history/` | Bidirectional | Save sprint snapshots for trend tracking; load previous snapshots for comparison |

## Tool Reference

### velocity_analyzer.py

Analyzes git history for sprint velocity metrics including throughput, cycle time, session detection, and commit type breakdown.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--days` | int | `7` | Number of days to analyze |
| `--since` | string | (none) | Start date YYYY-MM-DD, overrides `--days` |
| `--until` | string | today | End date YYYY-MM-DD |
| `--compare-previous` | flag | off | Compare against preceding period of equal length |
| `--gap-minutes` | int | `45` | Session gap threshold in minutes |
| `--repo` | string | `.` | Path to git repository |
| `-f`, `--format` | choice | `text` | Output format: `text` or `json` |

### contributor_insights.py

Per-contributor analysis of commits, LOC, work patterns, specialization detection, and collaboration metrics.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--days` | int | `7` | Number of days to analyze |
| `--since` | string | (none) | Start date YYYY-MM-DD |
| `--until` | string | today | End date YYYY-MM-DD |
| `--author` | string | (none) | Filter to specific author (partial match) |
| `--collaboration` | flag | off | Include bus factor and knowledge silo metrics |
| `--gap-minutes` | int | `45` | Session gap threshold in minutes |
| `--repo` | string | `.` | Path to git repository |
| `-f`, `--format` | choice | `text` | Output format: `text` or `json` |

### code_churn_analyzer.py

Identifies file hotspots, calculates churn rates, detects oscillation patterns, and flags refactoring candidates.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--days` | int | `7` | Number of days to analyze |
| `--since` | string | (none) | Start date YYYY-MM-DD |
| `--until` | string | today | End date YYYY-MM-DD |
| `--top` | int | `15` | Number of top hotspots to display |
| `--path` | string | (none) | Filter to files under this path prefix |
| `--detect-oscillation` | flag | off | Enable add/remove oscillation pattern detection |
| `--repo` | string | `.` | Path to git repository |
| `-f`, `--format` | choice | `text` | Output format: `text` or `json` |

### retro_report_generator.py

Assembles a comprehensive markdown retrospective report from velocity, contributor, and churn analysis data.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-v`, `--velocity` | string | (required) | Path to velocity analysis JSON file |
| `-c`, `--contributors` | string | (none) | Path to contributor insights JSON file |
| `-u`, `--churn` | string | (none) | Path to code churn analysis JSON file |
| `-s`, `--sprint-name` | string | `Sprint` | Sprint name for report title |
| `--previous-retro` | string | (none) | Path to previous retro markdown for action item tracking |
| `--previous-velocity` | string | (none) | Path to previous velocity JSON for comparison |
| `-o`, `--output` | string | stdout | Output file path |
| `--save` | string | (none) | Save sprint snapshot to directory (e.g., `.retro-history/`) |

---

**Last Updated:** 2026-03-18
**Version:** 2.0.0
**Status:** Production-ready — 4 Python tools, 2 reference guides, 2 asset templates
