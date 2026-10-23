---
name: sprint-retrospective
description: >
  Data-driven sprint retrospectives from git history — velocity, cycle/lead
  time, contributor insights, and churn hotspots. Use to run a
  retrospective, analyze team velocity or throughput, or generate a retro
  report from commit history.
license: MIT + Commons Clause
metadata:
  version: 2.0.1
  author: borghei
  category: project-management
  domain: agile-ceremonies
  updated: 2026-06-15
  tags: [retrospective, agile, continuous-improvement, team]
  python-tools: velocity_analyzer.py, contributor_insights.py, code_churn_analyzer.py, retro_report_generator.py
  tech-stack: python, git, agile, scrum, analytics
---
# Sprint Retrospective Expert

The agent acts as a data-driven retrospective facilitator that mines git history, PR metadata, and commit patterns to generate comprehensive sprint retrospective reports. It goes beyond simple commit counts — analyzing velocity trends, contributor work patterns, code health indicators, and team collaboration dynamics to surface actionable insights. Four stdlib Python tools (velocity, contributor, churn, report generator) chain into a single pipeline.

**Keywords:** sprint retrospective, velocity analytics, contributor insights, code churn, work sessions, cycle time, lead time, throughput, burndown, team health, collaboration metrics, bus factor, refactor ratio, hotspot analysis, conventional commits, session detection, deep work, improvement tracking

## Core Capabilities

- **Velocity analysis** — throughput, cycle/lead time, deploy frequency, commit-type breakdown, work-session detection (deep/focused/micro)
- **Contributor deep dive** — per-person LOC, peak hours, specialization (frontend/backend/infra/docs/tests/data), consistency, collaboration
- **Code quality trends** — churn hotspots, oscillation, test-to-production ratio, refactor frequency, healthy-range indicators
- **Team health** — review coverage, bus factor / knowledge-silo detection, cross-boundary work
- **Report generation & trend tracking** — narrative markdown reports, sprint snapshots, sprint-over-sprint deltas, action-item carry-over

## When to Use

- Running a weekly (7d), standard sprint (14d), or monthly/PI (30d) retrospective
- Producing a data-dense retro report or executive sprint summary from git history
- Diagnosing velocity, cycle-time, or review-bottleneck trends across sprints
- Identifying churn hotspots, refactoring candidates, or bus-factor / knowledge-silo risks
- Tracking follow-through on action items from previous retros
- Automating retrospectives on a CI/CD schedule

## Clarify First

Before generating the retro report, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Time window:** sprint length via `--days` or `--since/--until` (defines which commits count; the wrong window skews velocity and cycle-time).
- **Repo and merge style:** which repo/branch and whether squash-merges are used (squash merges lose branch-level cycle-time data).
- **Prior snapshot:** whether a previous retro snapshot exists (enables sprint-over-sprint deltas and action-item carry-over).
- **Audience:** team retrospective vs executive sprint summary (sets the narrative depth and which dashboards lead).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Full pipeline (last 14 days) → markdown report
python scripts/velocity_analyzer.py --days 14 -f json > /tmp/v.json && \
python scripts/contributor_insights.py --days 14 -f json > /tmp/c.json && \
python scripts/code_churn_analyzer.py --days 14 -f json > /tmp/ch.json && \
python scripts/retro_report_generator.py -v /tmp/v.json -c /tmp/c.json -u /tmp/ch.json -s "Sprint 23"
```

All tools support `--format text|json`, `--days N`, `--since/--until YYYY-MM-DD`, and `--repo /path`.

## Anti-Patterns

### Generating the retro without the team
**Mistake:** Someone runs the pipeline, writes conclusions from the report alone and sends them out as the retro.
**Why it happens:** The git analysis produces a full narrative report, so the retro looks done already.
**Instead:** Use the report as the data input to a live retro with the team (see `references/retrospective_facilitation.md`). The conclusions come out of that conversation. A retro doc with one author and no team input means a real retro still has to happen.

### Blame framing
**Mistake:** The retro output says "<name> did not finish the integration in time, which blocked the sprint."
**Why it happens:** Per-person data from `contributor_insights.py` makes it easy to tie a slip to one name.
**Instead:** Rewrite any line that names a person and a fault as a root cause and a systemic fix. Use contributor data for patterns such as bus-factor risk, not for blame. Once blame appears, nobody admits anything at the next retro.

### Action items reborn each sprint
**Mistake:** "Improve cross-team comms" appears as the action item three sprints running.
**Why it happens:** The item is vague enough that everyone agrees with it and too vague for anyone to act on.
**Instead:** Save a snapshot each sprint so carry-over shows repeats. If the wording repeats, root-cause the problem instead of re-adding it. Give each new action an owner, a due date and a definition of done.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-output.md](references/workflows-and-output.md)** — the five core analysis workflows (velocity, contributor, churn, team health, improvement tracking), tool flag tables, time-window guidance, session/code-health/collaboration deep dives, state persistence & trend tracking, narrative generation guidelines, output examples, CI/CD integration, troubleshooting, success criteria, and full Python tool reference. Read this for any hands-on retro analysis or report generation.
- **[references/retrospective_facilitation.md](references/retrospective_facilitation.md)** — 8 retro formats (Start/Stop/Continue, 4Ls, Sailboat, DAKI, etc.), facilitation techniques for remote/in-person teams, anti-patterns, and psychological safety frameworks. Read when facilitating the live ceremony.
- **[references/velocity_benchmarks.md](references/velocity_benchmarks.md)** — industry benchmarks by team size, healthy velocity patterns, and when velocity metrics mislead. Read when interpreting velocity numbers.
- **[references/red-flags.md](references/red-flags.md)** — common ways this skill's output goes wrong, with fixes. Read before finalizing a retro report.

## Scope & Limitations

**In Scope:** Git history analysis for velocity, contributor, and code churn metrics; session detection via commit-timestamp gaps; commit-type classification via conventional-commit prefixes; markdown report generation with executive summary, dashboards, and action-item tracking; sprint-over-sprint comparison; bus factor and knowledge-silo identification.

**Out of Scope:** Sprint planning and capacity calculation (see `scrum-master/`); JSON-based planned-vs-completed point analysis (see `scrum-master/velocity_analyzer.py`); product-level OKR/roadmap management (see `execution/`); code quality beyond churn (no static analysis or coverage measurement); Jira/Linear ticket-level cycle time (this skill uses git merge commits as proxy).

**Important Caveats:** All metrics derive from git history only — squash merges lose branch-level cycle-time data. Session detection is a heuristic on commit timestamps, not measured focus time. Per the Scrum Guide 2020, this skill treats velocity as a diagnostic signal, not a performance target; flow metrics (cycle time, throughput, WIP) are first-class. Rotate facilitation formats every 3-5 sprints to prevent staleness.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `scrum-master/` | Complements | Git-based velocity supplements JSON-based sprint data; cross-reference for fuller picture |
| `senior-pm/` | Feeds into | Retro velocity trends inform executive reporting and portfolio health dashboards |
| `delivery-manager/` | Feeds into | Velocity trends help forecast sprint capacity and release timing |
| `agile-coach/` | Feeds into | Retro trend data identifies systemic patterns for coaching interventions |
| `execution/release-notes/` | Feeds into | Sprint commit data and type distribution inform release note generation |
| CI/CD Workflows | Automated | GitHub Actions runs the 4-tool pipeline on a cron schedule (see workflows reference) |
| `.retro-history/` | Bidirectional | Save sprint snapshots for trend tracking; load previous snapshots for comparison |
