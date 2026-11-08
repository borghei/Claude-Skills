---
name: dependency-map
description: >
  Track cross-team dependencies in one JSON file and get a risk-ranked blocker
  list, the longest hand-off chain and a Mermaid graph. Use when several teams
  depend on each other and you need to know what to chase this week.
license: MIT + Commons Clause
metadata:
  version: 1.0.2
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: dependency_graph.py
  tech-stack: dependencies, critical-path, dsm, conway, mermaid
  tags:
    - dependencies
    - critical-path
    - program-management
    - mermaid
---
# Cross-Team Dependency Map

## Overview

Dependency tracking for multi-team initiatives: who is blocking whom, what is on the critical path, what is at risk, and what to coordinate this week. The output is a Mermaid dependency diagram, a critical-path list, a risk-ordered blocker list, and a weekly cross-team sync agenda -- all generated from a single JSON file you maintain instead of a sprawling spreadsheet.

Most cross-team programs fail at dependency management, not execution. The teams individually do good work; the gaps are at the seams. This skill makes those seams visible, prioritizes them by criticality, and produces the communication artifacts that keep them visible week over week. The underlying model uses the Critical Path Method (CPM, Kelley and Walker, 1959) for sequencing, optional DSM (Design Structure Matrix) thinking for cluster identification, and Conway's Law (Conway, 1968) framing for the organizational source of recurring dependency patterns. All outputs follow the six standard PM formats per `SHARED_OUTPUT_SCHEMA.md`.

## Core Capabilities

- **Dependency capture** — a six-field model (from/to team, description, needed-by, expected-delivery, status) maintained as one JSON file.
- **Critical path** — the longest chain of open hand-offs (A's `to_team` is B's `from_team`, dates within 30 days), with slack shown per link. It is the chain to watch, not a strict zero-slack CPM path; links with positive slack can sit on it.
- **Risk ordering** — slack and status combine into a risk-ranked blocker list.
- **Visualization & comms** — Mermaid `graph LR` rendering plus a weekly cross-team sync agenda.
- **Org diagnosis** — Conway's Law framing for recurring team-pair dependencies.

## When to Use

- **Multi-team feature** -- A feature requires platform, mobile, and data teams to coordinate.
- **Program management** -- Tracking 5-20 dependent workstreams across a quarter (see `program-manager/`).
- **Release coordination** -- A launch depends on legal review + DevOps capacity + design assets all converging.
- **Quarterly planning** -- Identifying which dependencies threaten quarterly OKR commitments.
- **Org-design diagnosis** -- Recurring dependencies between the same two teams may signal a structural problem (Conway's Law).

**When NOT to use:** single-team backlogs (use `wwas/` or `job-stories/`), pure technical dependencies inside one codebase (use Git), or stakeholder relationships (use `senior-pm/stakeholder_mapper.py`).

## Clarify First

Before mapping dependencies, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Teams / workstreams in scope:** the from/to pairs become the nodes; the wrong set produces a graph that maps the wrong program.
- **Needed-by and expected-delivery dates per dependency:** these drive slack, so they determine the critical path and the entire risk ordering.
- **Current status of each dependency:** not-started / in-progress / at-risk / done drives the risk-ordered blocker list and the weekly sync agenda.
- **Named owner per dependency:** an ownerless dependency cannot be walked weekly; owners populate the sync agenda.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. Copy `assets/dependency-template.json` and fill one entry per cross-team dependency (`from_team` needs, `to_team` owes). Set `"as_of"` to the date of the snapshot.
2. Run the analyzer:

```bash
python3 project-management/execution/dependency-map/scripts/dependency_graph.py \
  --input project-management/execution/dependency-map/assets/dependency-template.json --format markdown
# --format mermaid for the graph; --criticality critical,high or --team Mobile to filter
```

3. Give every critical-path and at-risk item a named owner and a next action; walk them weekly with `assets/weekly-sync-agenda.md`. Update the JSON before each sync.
4. **Done when** no blocked or high-risk item lacks an owner and a date for its next conversation.

**As-of date:** `--as-of`, else the file's `as_of` field, else today. The template and `--demo` carry `as_of: 2026-05-25`, so they show the same risk mix on any day (1 blocked, 1 high, 3 medium, 2 low). Risk is driven by slack (needed-by minus expected delivery), status, and days left to the needed-by date.

**Exit codes:** 0 report written; 2 missing file, invalid JSON, empty or wrong-shape `dependencies`, bad dates or an invalid `--criticality` value.

## Anti-Patterns

### Dependencies that never reach the JSON
**Mistake:** The JSON lists 8 dependencies while 22 exist. The rest live in Slack DMs and people's heads, and one team blocks another for three weeks before anyone notices.
**Why it happens:** Only the dependencies someone remembers to report get added.
**Instead:** Run a 90-minute inventory with each team lead at the start of the planning period, and log any dependency found outside the JSON within 24 hours. If a fresh round finds more than 30% new ones, the map is incomplete.

### Tracking tasks instead of cross-team work
**Mistake:** The JSON holds 80 task-level items such as "Frontend needs button asset from Design", and the Mermaid diagram becomes unreadable.
**Why it happens:** Teams log every handoff to be thorough.
**Instead:** Track at the epic level, roughly 1-2 weeks of cross-team work each, and keep intra-team handoffs on the team's sprint board. More than about 25 dependencies per program means you should aggregate.

### Arrows pointing the wrong way
**Mistake:** A dependency is entered with `from_team` as the team delivering the work and `to_team` as the team waiting for it.
**Why it happens:** "From" reads naturally as where the work comes from.
**Instead:** `from_team` is the team that needs the work, and `to_team` is the team that owes it. Spot-check a few descriptions before running `dependency_graph.py`, because a reversed arrow breaks the critical path and the risk ordering.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## Files

| File | Purpose |
|---|---|
| `scripts/dependency_graph.py` | The analyzer |
| `assets/dependency-template.json` | Starter file and sample: 8 dependencies, one per status |
| `assets/weekly-sync-agenda.md` | Agenda for the weekly cross-team sync |
| `examples/q4-launch-cross-team-deps.md` | Worked program example |

## References

- **[references/dependency-map-operations.md](references/dependency-map-operations.md)** — read this for the operational detail: the six-field model, slack/risk derivation, critical-path computation, the 8-step weekly workflow, tool flags, input/output JSON schemas, troubleshooting, and success criteria.
- **[references/dependency-management-guide.md](references/dependency-management-guide.md)** — read this for the CPM walkthrough, DSM intro, Conway's Law applied, and recurring-dependency diagnosis.
- **[references/red-flags.md](references/red-flags.md)** — read this to see the common ways dependency-map output goes wrong (with fixes) before publishing a map.
- Kelley & Walker, "Critical-Path Planning and Scheduling" (1959); Conway, "How Do Committees Invent?" (1968); Steward, "The Design Structure System" (1981).

## Scope & Limitations

**In Scope:** cross-team dependency capture and visualization, Critical Path Method analysis, risk-ordered blocker list, Mermaid `graph LR` rendering, Conway's Law-aware quarterly review, all six formats per `SHARED_OUTPUT_SCHEMA.md`.

**Out of Scope:** resource capacity planning (`senior-pm/resource_capacity_planner.py`), stakeholder mapping (`senior-pm/stakeholder_mapper.py`), sprint-level backlog ordering (`prioritization-frameworks/`), detailed Gantt charting, risk register beyond dependency blockers (`discovery/pre-mortem/`).

**Important Caveats:** dependency maps degrade fast without weekly updates (a 4-week-old map is harmful); the critical path identifies the *currently longest* chain and can shift when a single dependency is added (re-run on every change); this skill surfaces what to talk about but does not replace the conversation.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `program-manager/` | Used by | Program managers maintain the dependency JSON across teams |
| `senior-pm/` | Feeds into | Critical-path risks flow into portfolio risk reporting |
| `senior-pm/risk_matrix_analyzer.py` | Complementary | Dependency risks plot alongside other program risks |
| `discovery/pre-mortem/` | Complementary | Pre-mortem-identified "tigers" often map to specific dependencies |
| `cycle-time-analyzer/` | Complementary | Long cycle times often correlate with cross-team blocks |
| `launch-playbook/` | Feeds into | Launch RACI references the dependency map for cross-team owners |
| `status-update-generator/` | Feeds into | Weekly status pulls critical-path summary |
| `summarize-meeting/` | Feeds into | Weekly sync notes become structured summaries |
