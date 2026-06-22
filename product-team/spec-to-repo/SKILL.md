---
name: spec-to-repo
description: >
  Translate product specs (PRDs, user stories) into a ship-ready repo plan:
  ticket decomposition, branch strategy, and PR sequencing. Use when breaking a
  PRD into tickets or designing the branch/PR sequence.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-team
  domain: delivery
  updated: 2026-05-27
  tags: [prd, ticket-decomposition, branch-strategy, pr, definition-of-done, delivery]
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

## Inputs the advisor expects

- The PRD or spec document
- Target ship window (1 sprint? 1 month? 1 quarter?)
- Engineering team size + composition (FE, BE, ML, mobile)
- Risk profile (greenfield vs production-impacting)
- Feature-flag and rollout posture

## Clarify First

Before generating the repo plan, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The PRD or spec** — the user-facing capabilities to decompose (drives the epic→ticket tree)
- [ ] **Target ship window** — one sprint, month, or quarter (drives ticket sizing and PR sequencing)
- [ ] **Team composition** — FE, BE, ML, mobile (decides parallel paths and vertical-slice tickets)
- [ ] **Feature-flag and rollout posture** — flagged/dark-launch vs direct ship (drives PR sequencing and definition-of-done)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

- **Decomposition as wishful thinking.** "3-day estimate" with no break-down is a 2-week-actual.
- **Sequential ticket tree (everyone waits).** Plan parallel paths.
- **Hidden dependencies on other teams.** Surface them in decomposition.
- **No feature flag.** Shippable in chunks but every change goes to all users immediately.
- **PRs > 1000 lines.** Reviewability dies; bugs hide.
- **DoD that's just "code merged."** Forgets tests, docs, telemetry.
- **Ticket = a day of work.** Sometimes tickets are 30 minutes; sometimes 3 days.

## References

- `references/spec-to-ticket-decomposition.md` — patterns for breaking specs into tickets
- `references/branch-strategy-for-features.md` — branching, feature flags, dark-launch
- `references/pr-discipline-and-conventions.md` — PR size, review, definition-of-done

## Related skills

- `product-team/agile-product-owner` — sprint planning, prioritization
- `engineering/feature-flags-architect` — flag strategy
- `engineering/observability-designer` — SLO / telemetry
- `c-level-advisor/vpe-advisor` — broader delivery context
- `project-management/` skills — ticket / sprint management tooling
