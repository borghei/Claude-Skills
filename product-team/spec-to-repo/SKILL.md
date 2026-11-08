---
name: spec-to-repo
description: >
  Translate product specs (PRDs, user stories) into a ship-ready repo plan:
  ticket decomposition, branch strategy, and PR sequencing. Use when breaking a
  PRD into tickets or designing the branch/PR sequence.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: product-team
  domain: delivery
  updated: 2026-11-08
  tags: [prd, ticket-decomposition, tracer-bullet, branch-strategy, pr, delivery]
---

# Spec to Repo

A delivery-focused skill that bridges product spec to repository work.
Where PRD-writing skills focus on what to build, this skill focuses on
**how to break it down for execution** — the ticket decomposition,
branch strategy, PR sequencing, and acceptance criteria that make a
spec actually ship.

## When to use this skill

- Translating a **PRD or feature brief** into a sequence of tickets
- Designing the **branch + PR sequence** for a multi-week feature
- Auditing an existing **ticket decomposition** for risk (big tickets, hidden dependencies)
- Defining **definition-of-done** that covers code, tests, docs, telemetry
- Planning **incremental shipping** (feature flags, canaries, dark-launch)
- Reviewing a **decomposition before sprint planning** to avoid mid-sprint surprises
- Slicing a spec into **tracer-bullet tickets** with blocking links that people or coding agents can pick up in dependency order

## Inputs the advisor expects

- The PRD or spec document
- Target ship window (1 sprint? 1 month? 1 quarter?)
- Engineering team size + composition (FE, BE, ML, mobile)
- Risk profile (greenfield vs production-impacting)
- Feature-flag and rollout posture

## Clarify First

Before generating the repo plan, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The PRD or spec:** the user-facing capabilities to decompose (drives the epic→ticket tree).
- **Target ship window:** one sprint, month, or quarter (drives ticket sizing and PR sequencing).
- **Team composition:** FE, BE, ML, mobile (decides parallel paths and vertical-slice tickets).
- **Feature-flag and rollout posture:** flagged/dark-launch vs direct ship (drives PR sequencing and definition-of-done).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Validate a tracer-bullet ticket set: vertical slices, blocking links, build waves
# (exits 1 on the sample: one ticket has no acceptance criteria by design)
python3 product-team/spec-to-repo/scripts/ticket_graph_validator.py \
  --input product-team/spec-to-repo/assets/sample_tracer_tickets.json --format text
```

## Workflows

### Workflow 1 — Decompose a PRD into tickets

1. Pull the PRD; identify the user-facing capabilities.
2. Run `prd_to_tickets_decomposer.py` with the user stories + technical
   notes to surface a candidate ticket tree (epic → tickets → subtasks)
   with size estimates and dependencies.
3. Manually review; tune for team-specific patterns.

```bash
python3 spec-to-repo/scripts/prd_to_tickets_decomposer.py \
  --input prd.json --format markdown
```

### Workflow 2 — Validate the branch and PR plan

1. Capture proposed branch + PR sequence.
2. Run `pr_scope_analyzer.py` to flag oversized PRs, missing tests,
   missing telemetry, and risky merges.
3. Adjust before opening PRs.

```bash
python3 spec-to-repo/scripts/pr_scope_analyzer.py \
  --input pr_plan.json --format markdown
```

### Workflow 3 — Lint branch names against convention

1. Capture branch list (e.g., `git branch --list`).
2. Run `branch_naming_validator.py` to flag non-conformant names.

```bash
python3 spec-to-repo/scripts/branch_naming_validator.py \
  --input branches.txt --format markdown
```

### Workflow 4 — Slice a spec into tracer-bullet tickets with blocking links [RECOMMENDED]

A tracer bullet is the thinnest slice that runs end to end through every layer it needs and
can be demonstrated. Slicing this way means every merged ticket is usable, integration
problems surface on ticket one instead of the last, and tickets can be worked in parallel
from a dependency graph. Full method, exceptions and ticket format:
`references/tracer-bullet-slicing.md`.

1. List the spec's user-visible behaviours as one checkable sentence each, ordered by
   product dependency.
2. If the existing code makes the change awkward, put a `prefactor` ticket (no behaviour
   change) at the front.
3. Cut the first behaviour down to the narrowest version that still crosses every layer —
   happy path, hard-coded where possible. That is the first slice.
4. Turn each remaining behaviour into a slice, and give it blocking links only to tickets
   it genuinely cannot be built or verified without.
5. Mark wide mechanical changes as `expand` / `migrate` / `contract` instead of forcing
   them into a slice, and unknowns as a time-boxed `spike`.
6. Write the ticket set as JSON and validate it. Fix every error (missing acceptance
   criteria, unknown blocker, cycle); treat warnings (horizontal slice, not demoable, over
   the size limit, bottleneck) as prompts to re-slice.
7. Show the breakdown — title, blocked by, what it delivers — and iterate on granularity
   and links until approved. Then publish in dependency order using the tracker's native
   blocking link, so later tickets reference real identifiers.

```bash
python3 product-team/spec-to-repo/scripts/ticket_graph_validator.py \
  --input tickets.json --max-days 2 --format json
```

Work then proceeds from the **frontier**: any ticket whose blockers are all done. The
validator's waves show the frontier at each step and the length of the critical path.

## Decision frameworks

### Ticket sizing

| Size | Effort | Description |
|------|--------|-------------|
| XS | < 0.5 day | Trivial; usually skip ticketing |
| S | 0.5–1 day | One simple change |
| M | 1–3 days | Single feature, well-scoped |
| L | 3–5 days | Multi-day work; should split if possible |
| XL | > 5 days | Always split — too big for confident estimate |

A ticket that's L or XL almost always hides a missing decomposition. Push
back on yourself.

### The ticket tree

```
Epic — large product feature ("Notifications v2")
├── Story — user-facing capability ("As a user I can mute by channel")
│   ├── Ticket — one engineering work item (backend, frontend, infra)
│   │   └── Subtask — atomic step (optional)
```

Most orgs:
- Epic ≈ PRD-sized scope
- Story ≈ one user-facing slice
- Ticket ≈ one PR (or pair of PRs: BE + FE)

### The "vertical slice"

Best ticket: ships a small user-visible improvement end-to-end.
- Backend change + frontend change + tests + telemetry + docs in one ship
- Better than: BE-only ticket waiting for FE-only ticket waiting for QA

When you can't slice vertically (e.g., backend is weeks before frontend):
- Use feature flags to ship behind a switch
- Dark-launch backend to validate before frontend
- Communicate the lag explicitly

### PR sequencing

For a multi-PR feature:

1. **PR 1 — Infrastructure / scaffolding** (no behavior change)
2. **PR 2 — Backend changes** (behind flag; no frontend uses it)
3. **PR 3 — Frontend changes** (behind flag; tests pass with flag on/off)
4. **PR 4 — Telemetry + analytics events**
5. **PR 5 — Documentation + runbook**
6. **PR 6 — Flag enablement** (small change; reviewable cleanly)

Each PR < 400 lines if possible. Reviewability collapses above 400.

### Definition of done

Per ticket:
- Code: written, reviewed, merged
- Tests: unit + integration as appropriate
- Telemetry: events fired (and verified)
- Docs: README / runbook / API doc updated as needed
- Accessibility: meets the project bar
- Feature flag: configured (if applicable)
- Rollout plan: defined for non-flagged ships

Per epic:
- All tickets complete
- Feature behind flag in production for 1+ week (if risky)
- Flag enabled for X% (canary), then ramped
- Telemetry shows expected behavior
- Customer-facing comms drafted (if applicable)

## Common engagements

### "Help me decompose this PRD"
1. List user-facing capabilities (1-line each).
2. For each, list the backend, frontend, infra, telemetry, docs work.
3. Estimate; flag anything > 3 days for further breakdown.
4. Sequence: scaffolding first, behavior next, flag enablement last.
5. Identify cross-team dependencies; engage before sprint start.

### "Our team is shipping huge PRs"
1. Audit the last 10 PRs: median size, P95 size.
2. Identify the patterns: monolithic services + flag-less work + slow review.
3. Pilot: feature flags + ticket-first decomposition + PR size SLA.
4. Track: median PR size + lead time week-over-week.

### "Help me plan the rollout"
1. Define a successful launch criterion (e.g., < 0.5% error rate at 50%).
2. Identify the kill switch (feature flag or quick-revert).
3. Plan ramps: 1% → 5% → 25% → 50% → 100% with bake time.
4. Define rollback criteria + comms plan.
5. Coordinate with on-call + support.

## Anti-patterns to avoid

### The Layer Cake
**Mistake:** Tickets cut by layer — "create tables", "build API", "build UI", "write tests".
**Why it happens:** It mirrors how the system is drawn and how teams are split, so it feels natural to estimate.
**Instead:** Cut by behaviour. Each ticket crosses the layers its behaviour needs and is demoable when it merges. The validator flags single-layer tickets that are not marked as a declared exception.

### Blocking Links as Preferences
**Mistake:** Linking tickets because one "should" come after another, until the graph is a single line.
**Why it happens:** A straight sequence feels safer and easier to explain.
**Instead:** Link only real gates — the second ticket cannot be built or verified without the first. Fewer links mean a wider frontier and more parallel work.

### The Fat First Slice
**Mistake:** Making ticket one "the whole save feature, with validation, sharing and error states".
**Why it happens:** The first slice feels like the foundation, so it gets everything.
**Instead:** Make the first slice the thinnest path that proves every layer connects. Widen it in later tickets.

Also avoid:

- **Decomposition as wishful thinking.** "3-day estimate" with no break-down is a 2-week-actual.
- **Sequential ticket tree (everyone waits).** Plan parallel paths.
- **Hidden dependencies on other teams.** Surface them in decomposition.
- **No feature flag.** Shippable in chunks but every change goes to all users immediately.
- **PRs > 1000 lines.** Reviewability dies; bugs hide.
- **DoD that's just "code merged."** Forgets tests, docs, telemetry.
- **Ticket = a day of work.** Sometimes tickets are 30 minutes; sometimes 3 days.

## Scope & Limitations

**In Scope:**
- Decomposing a PRD, described as user capabilities, technical notes and team, into an epic, story and ticket tree with `prd_to_tickets_decomposer.py`, flagging oversized tickets and cross-team dependencies
- Checking a planned PR sequence with `pr_scope_analyzer.py` for oversized PRs, missing tests, telemetry or docs, risky merges and ordering problems
- Linting branch names against a configurable pattern with `branch_naming_validator.py`
- Guidance on ticket sizing, vertical slices, PR sequencing, definition of done and staged rollout
- Slicing a spec into tracer-bullet tickets with blocking links, and validating the ticket graph with `ticket_graph_validator.py`

**Out of Scope:**
- Writing the PRD itself (see `project-management/execution/create-prd/`)
- Capturing a spec from a conversation, and the test-first implement-from-spec loop (see `spec-driven-workflow`)
- Creating tickets in Jira or Linear (see `project-management/jira-expert/` and `project-management/linear-expert/`)
- Feature flag platform design (see `engineering/feature-flags-architect/`)
- Reviewing actual code changes (see `engineering/pr-review-expert/`)

**Important Caveats:**
- The decomposer does not parse PRD prose. It works from a JSON of capabilities, and effort comes from the `estimated_days` the user enters.
- The PR analyzer reads a plan with estimated line counts, not real diffs. The branch validator checks a list of names and does not touch the git repository.
- Size limits such as splitting tickets over 3 days or keeping PRs under 400 lines are rules of thumb. Teams should tune them to their own history.

## Files

| File | Purpose |
|------|---------|
| `scripts/prd_to_tickets_decomposer.py` | Epic, story and ticket tree from a capabilities JSON, with size flags and dependencies |
| `scripts/pr_scope_analyzer.py` | Checks a planned PR sequence for size, missing tests, telemetry, docs and ordering |
| `scripts/branch_naming_validator.py` | Lints branch names against a pattern |
| `scripts/ticket_graph_validator.py` | Validates tracer-bullet tickets: vertical slices, acceptance criteria, blocking links, cycles, build waves |
| `assets/sample_tracer_tickets.json` | Seven-ticket saved-search plan with two deliberate defects |

## Tools Overview

`ticket_graph_validator.py` exits 0 when there are no errors, 1 on any error (unknown
blocker, cycle, missing acceptance criteria, no free starting ticket), and 2 on unreadable
input. The other three tools are described in Workflows 1–3.

## Reference Documentation

- `references/tracer-bullet-slicing.md` — slicing rules, blocking links, the frontier, expand/migrate/contract and other exceptions, ticket format, worked example
- `references/spec-to-ticket-decomposition.md` — patterns for breaking specs into tickets
- `references/branch-strategy-for-features.md` — branching, feature flags, dark-launch
- `references/pr-discipline-and-conventions.md` — PR size, review, definition-of-done

## Related skills

- `product-team/agile-product-owner` — sprint planning, prioritization
- `engineering/feature-flags-architect` — flag strategy
- `engineering/observability-designer` — SLO / telemetry
- `c-level-advisor/vpe-advisor` — broader delivery context
- `project-management/` skills — ticket / sprint management tooling
