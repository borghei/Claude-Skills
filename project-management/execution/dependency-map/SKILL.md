---
name: dependency-map
description: >
  Cross-team dependency tracking with critical path analysis and Mermaid
  dependency graphs for program coordination.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: dependency_graph.py
  tech-stack: dependencies, critical-path, dsm, conway, mermaid
---
# Cross-Team Dependency Map

## Overview

Dependency tracking for multi-team initiatives: who is blocking whom, what is on the critical path, what is at risk, and what to coordinate this week. The output is a Mermaid dependency diagram, a critical-path list, a risk-ordered blocker list, and a weekly cross-team sync agenda -- all generated from a single JSON file you maintain instead of a sprawling spreadsheet.

Most cross-team programs fail at dependency management, not execution. The teams individually do good work; the gaps are at the seams. This skill makes those seams visible, prioritizes them by criticality, and produces the communication artifacts that keep them visible week over week. The underlying model uses the Critical Path Method (CPM, Kelley and Walker, 1959) for sequencing, optional DSM (Design Structure Matrix) thinking for cluster identification, and Conway's Law (Conway, 1968) framing for the organizational source of recurring dependency patterns. All outputs follow the six standard PM formats per `SHARED_OUTPUT_SCHEMA.md`.

## Core Capabilities

- **Dependency capture** — a six-field model (from/to team, description, needed-by, expected-delivery, status) maintained as one JSON file.
- **Critical-path analysis** — CPM computation of the longest zero-slack chain plus near-critical siblings.
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

Before mapping dependencies, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Teams / workstreams in scope** — the from/to pairs become the nodes; the wrong set produces a graph that maps the wrong program
- [ ] **Needed-by and expected-delivery dates per dependency** — these drive slack, so they determine the critical path and the entire risk ordering
- [ ] **Current status of each dependency** — not-started / in-progress / at-risk / done drives the risk-ordered blocker list and the weekly sync agenda
- [ ] **Named owner per dependency** — an ownerless dependency cannot be walked weekly; owners populate the sync agenda

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/dependency_graph.py --input deps.json --format markdown   # full report
python scripts/dependency_graph.py --input deps.json --format mermaid     # graph LR for README/Notion/Confluence
python scripts/dependency_graph.py --demo --format markdown               # sample output, no input
```

Populate `deps.json` from `assets/dependency-template.json`, run the analyzer, give every critical-path item a named owner, and walk it weekly with `assets/weekly-sync-agenda.md`. Update the JSON *before* each sync.

## References

- **[references/dependency-map-operations.md](references/dependency-map-operations.md)** — read this for the operational detail: the six-field model, slack/risk derivation, critical-path computation, the 8-step weekly workflow, tool flags, input/output JSON schemas, troubleshooting, and success criteria.
- **[references/dependency-management-guide.md](references/dependency-management-guide.md)** — read this for the CPM walkthrough, DSM intro, Conway's Law applied, and recurring-dependency diagnosis.
- **[references/red-flags.md](references/red-flags.md)** — read this to see the common ways dependency-map output goes wrong (with fixes) before publishing a map.
- `assets/dependency-template.json` — starter JSON with the full schema and one worked example per status.
- `assets/weekly-sync-agenda.md` — standard agenda for the cross-team weekly sync.
- Kelley & Walker, "Critical-Path Planning and Scheduling" (1959); Conway, "How Do Committees Invent?" (1968); Steward, "The Design Structure System" (1981).

## Scope & Limitations

**In Scope:** cross-team dependency capture and visualization, Critical Path Method analysis, risk-ordered blocker list, Mermaid `graph LR` rendering, Conway's Law-aware quarterly review, all six formats per `SHARED_OUTPUT_SCHEMA.md`.

**Out of Scope:** resource capacity planning (`senior-pm/resource_capacity_planner.py`), stakeholder mapping (`senior-pm/stakeholder_mapper.py`), sprint-level backlog ordering (`prioritization-frameworks/`), detailed Gantt charting, risk register beyond dependency blockers (`pre-mortem/`).

**Important Caveats:** dependency maps degrade fast without weekly updates (a 4-week-old map is harmful); the critical path identifies the *currently longest* chain and can shift when a single dependency is added (re-run on every change); this skill surfaces what to talk about but does not replace the conversation.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `program-manager/` | Used by | Program managers maintain the dependency JSON across teams |
| `senior-pm/` | Feeds into | Critical-path risks flow into portfolio risk reporting |
| `senior-pm/risk_matrix_analyzer.py` | Complementary | Dependency risks plot alongside other program risks |
| `pre-mortem/` | Complementary | Pre-mortem-identified "tigers" often map to specific dependencies |
| `cycle-time-analyzer/` | Complementary | Long cycle times often correlate with cross-team blocks |
| `launch-playbook/` | Feeds into | Launch RACI references the dependency map for cross-team owners |
| `status-update-generator/` | Feeds into | Weekly status pulls critical-path summary |
| `summarize-meeting/` | Feeds into | Weekly sync notes become structured summaries |
