---
name: wayfinder
description: >
  Chart work too big for one sprint as a map of decision tickets, resolve them in
  dependency order, then turn answers into tracer-bullet tickets. Use when the route
  is unclear, open questions block each other, or estimates swing wildly.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: decision_map_validator.py, tracer_slice_checker.py
  tech-stack: decision-tickets, dependency-graph, tracer-bullets, vertical-slicing, expand-contract
  tags:
    - planning
    - decision-tickets
    - tracer-bullets
    - dependencies
    - large-initiatives
---

# Wayfinder

Some work is too large for one session and too foggy to estimate: the build steps depend on choices nobody has made, and those choices block each other. The agent instead charts a **map of decision tickets**, works them one per session in dependency order, and converts each answer into **thin end-to-end tracer-bullet tickets** only once it is made.

The map is an index: destination, notes, decisions so far, fog (in-scope questions not yet sharp enough to ticket) and out of scope.

## When to Use

- An initiative spans several sprints and its estimates range across an order of magnitude
- Planning keeps reopening the same questions, or code is being written "until we decide"
- Several owners (finance, legal, platform) must each make a call before work can start
- Parts of a large effort go to coding agents, who must not guess the design

## Clarify First

The destination fixes the scope of the whole map, so settle it before any ticket. When an input is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Destination:** an observable end state, not an activity; it decides what is fog and what is out of scope.
- **Decision owners:** who can make each kind of call; a ticket without an owner never leaves the frontier.
- **Fixed constraints:** dates, budgets and platform choices that are not up for decision, so they do not become tickets.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Validate a map: cycles, dangling ids, ownerless decisions, premature builds; prints order + frontier
python3 project-management/execution/wayfinder/scripts/decision_map_validator.py \
  --input project-management/execution/wayfinder/assets/sample_decision_map_clean.json --today 2026-11-08
```

```bash
# Check implementation tickets are vertical slices (and expand-migrate-contract is ordered)
python3 project-management/execution/wayfinder/scripts/tracer_slice_checker.py \
  --input project-management/execution/wayfinder/assets/sample_decision_map_flawed.json --format json
```

## Tools Overview

| Tool | Reads | Reports |
|------|-------|---------|
| `decision_map_validator.py` | Map JSON (`destination`, `fog`, `out_of_scope`, `tickets`) | Errors/warnings, stable topological order, frontier |
| `tracer_slice_checker.py` | Same file (implementation tickets only) | Horizontal slices, missing demo/criteria, vague criteria, refactor ordering |

### Exit code contract

`0` no error findings (warnings allowed) · `1` at least one error (the quality gate) · `2` unreadable input or bad arguments. Both tools exit 1 on the flawed sample by design and 0 on the clean one:

```bash
python3 project-management/execution/wayfinder/scripts/decision_map_validator.py   --input project-management/execution/wayfinder/assets/sample_decision_map_flawed.json; echo "exit $?"  # exit 1
```

## Workflow

Tags on the headings below: **[PROVEN]** means the rule is well established in practice and the validators check for it; **[RECOMMENDED]** means a sensible default practice to tune to your team.

1. **Name the destination** [PROVEN]. One or two sentences describing a checkable end state. If stakeholders disagree, that disagreement is the first decision; chart nothing else.
2. **Fan out breadth-first** [RECOMMENDED]. List unknown facts, forks, outside owners, irreversible choices. Sharp question → ticket; vague → fog; past the destination → out of scope.
3. **Write decision tickets.** Question ending in "?", type (research, prototype, discussion, enabling-task), at least two options for discussion and prototype, owner, decide-by date. Use `assets/ticket_templates.md`.
4. **Wire blocking links in a second pass** [RECOMMENDED]. Keep a link only if the blocker's least likely answer would change this ticket's options.
5. **Validate** — quality gate. Run `decision_map_validator.py`; fix every error before taking work.
6. **Take one frontier ticket per session** [PROVEN]. Claim it, resolve it, record chosen / why / rejected / consequences, close it, add one line to Decisions so far.
7. **Update the map.** Graduate fog that is now sharp, open new tickets, rule out anything past the destination.
8. **Convert resolved decisions into tracer bullets** [PROVEN]. Each slice names a behaviour, lists `derived_from`, crosses two or more layers, has a demo, testable criteria and an estimate of three days or less. Wide mechanical refactors become expand → migrate batches → contract.
9. **Check the slices.** Run `tracer_slice_checker.py`, then walk the review checklist in `references/decisions-to-tracer-bullets.md` with the people who will build them.
10. **Close the map** when frontier and fog are empty and each decision is converted or `no_build`.

## Anti-Patterns

### The Map That Became a Backlog
**Mistake:** Charting every task you can imagine, so the map holds forty tickets and no questions.
**Why it happens:** Listing work feels like progress; listing unknowns feels like ignorance.
**Instead:** Tickets resolve decisions or put resolved decisions into effect. Everything else leaves the map.

### Building on Hope
**Mistake:** Starting implementation tickets that depend on decisions still open.
**Why it happens:** Pressure to show progress.
**Instead:** The validator errors on it. Record the decision if it is made, or treat the code as a disposable prototype.

### Corridor Decisions
**Mistake:** Closing a decision ticket with no resolution text.
**Why it happens:** The call was made in a meeting and felt settled.
**Instead:** Write the chosen option, reason and rejected options first.

### Horizontal Implementation Tickets
**Mistake:** Converting good decisions into "schema", "API" and "UI" tickets.
**Why it happens:** Habit and org charts.
**Instead:** Slice by behaviour across every layer; the checker errors on single-layer slices.

## Files

| File | Purpose |
|------|---------|
| `scripts/decision_map_validator.py` | Map gate, order and frontier |
| `scripts/tracer_slice_checker.py` | Slice gate |
| `assets/sample_decision_map_clean.json` | Usage-based billing map mid-flight; both tools exit 0 |
| `assets/sample_decision_map_flawed.json` | Offline-mode map seeded with every failure; both tools exit 1 |
| `assets/decision_map_template.md` | Map page template |
| `assets/ticket_templates.md` | Decision, tracer-bullet and refactor-phase tickets |

## Reference Documentation

- [references/charting-the-map.md](references/charting-the-map.md) — destination, finding decisions, ticket vs fog, types, links, cycles, sessions, worked example. Read when charting or resuming.
- [references/decisions-to-tracer-bullets.md](references/decisions-to-tracer-bullets.md) — converting answers into slices, testable criteria, expand-migrate-contract, review checklist. Read before writing implementation tickets.
- [references/map-health-and-failure-modes.md](references/map-health-and-failure-modes.md) — health signals, each finding with its repair, cadence. Read when the map stalls.

## Scope & Limitations

**In Scope:** destination framing, decision tickets, fog and out-of-scope management, one-decision-per-session cadence, conversion into tracer-bullet and refactor tickets, validation and ordering.

**Out of Scope:**
- Tracking cross-team dependencies and the critical path of already-committed work (`project-management/execution/dependency-map/`).
- Slicing a user journey into releases (`project-management/execution/story-mapping/`).
- Splitting one oversized story (`project-management/execution/story-splitting/`).

**Important Caveats:**
- The tools read a hand-maintained JSON export; they do not call Jira, Linear or GitHub.
- Owners, options and statuses are self-reported. The validator checks that they exist, not that they are right.
- Layer names are free text; read the demo statement too.
