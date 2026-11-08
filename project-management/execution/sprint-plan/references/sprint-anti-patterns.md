# Sprint Plan — Anti-Patterns + Fixes

## A1 — 100% commit
**Symptom:** Sprint planned to fill 100% of capacity.

**Fix:** Reduce commits to 75-85%; add 10-15% stretch; reserve 5% buffer.

## A2 — No sprint goal
**Symptom:** Sprint = list of features; no overarching theme.

**Fix:** One sentence describing what the sprint achieves. Inspires + enables "no."

## A3 — Unrefined items committed
**Symptom:** "We'll figure it out as we go."

**Fix:** Per item, before commit:
- Acceptance criteria clear
- Estimated
- Dependencies identified

If not refined, send back; don't commit.

## A4 — Stories sized 13+ points
**Symptom:** Item estimated at 13 / 21 / "L".

**Fix:** Split. Items > 5 days are usually 2-3 stories pretending to be 1.

## A5 — No dependency identification
**Symptom:** "Eng will need design by end of week 1" — assumed.

**Fix:** Per dependency:
- Owner (named person)
- Date needed by
- Confirmed by them before sprint start
- Backup plan if late

## A6 — No risk identification
**Symptom:** "We'll handle issues as they come."

**Fix:** Per item, list 1-2 risks:
- Technical
- Dependency
- Estimation
- Capacity

Per risk: likelihood, severity, mitigation, owner.

## A7 — No definition of done
**Symptom:** "Engineer says it's done; QA disagrees."

**Fix:** Published DoD per item type. Standard:
- Code merged + reviewed
- Tests added
- Telemetry firing in staging
- Docs updated
- Accessibility checked
- Flag configured (if applicable)
- QA passed

## A8 — Mid-sprint scope addition
**Symptom:** New "urgent" work added without descope.

**Fix:** Rule: nothing added without descope. PO discipline.

If genuinely urgent → descope something explicitly.

## A9 — Capacity ignores PTO / on-call
**Symptom:** Capacity = team size × hours per week. Same every sprint.

**Fix:** Per-sprint capacity math accounting for:
- PTO / holidays this sprint
- On-call rotation
- New-hire ramp
- Meetings + interrupts

See `capacity-math.md`.

## A10 — Velocity not tracked
**Symptom:** Same estimation mistakes every sprint.

**Fix:** Per sprint, track:
- Committed points
- Stretch points
- Delivered points
- Carryover

After 3-5 sprints, calibrate next commit using actual velocity.

## A11 — All items "P0"
**Symptom:** Every committed item is P0; no prioritization.

**Fix:** Per sprint, max 1-2 P0. Others P1-P2. Forces priority discipline.

## A12 — No buffer for incidents
**Symptom:** Production incident during sprint = scope blown.

**Fix:** Reserve 5-15% capacity (and an on-call rotation if applicable).
Heavy-incident teams need higher reserve.

## A13 — Estimation by the person who didn't write the story
**Symptom:** PM estimates; engineer surprised by complexity.

**Fix:** Engineer who will build the story estimates. Pair on novel work.

## A14 — Sprint goal not visible
**Symptom:** Goal stated at planning; never referenced again.

**Fix:** Sprint goal posted in team channel; referenced in standup; visible in dashboard.

## A15 — No retro action items
**Symptom:** Retro held; no commitments to change.

**Fix:** Per retro: 1-3 action items with owner + date.

## Worked example — bad → good sprint plan

### Bad

```
Sprint 12

- Feature A (5 pts)
- Feature B (8 pts)
- Feature C (3 pts)
- Bug-fix X (2 pts)
- Bug-fix Y (1 pt)
- Tech debt (5 pts)

Total: 24 pts

(No goal, capacity unclear, no commit/stretch split, no DoD, no risks)
```

### Good

```
Sprint 12 — Apr 14 to Apr 25

Goal: Ship checkout flow MVP enabling first paid customers (target Friday Apr 25)

Capacity:
- 5 engineers × 36 effective hours = 180 hours
- Alice on-call this sprint = effective 28 hrs
- Total: 208 hours (= 26 person-days at 8 h)
- Commit target (80%): 166 hrs
- Stretch (15%): 31 hrs
- Reserve (5%): 10 hrs

Last 3 sprints velocity: 32, 36, 34 pts (avg 34)
This sprint commit: 34 × 0.85 = ~28 pts

COMMITS (target 28 pts):

A. Checkout backend (8 pts) — Bob, Carol
  - DoD: API live + tests + telemetry events firing
  - Dependencies: Stripe integration confirmed (Carol talked w/ Stripe)
  - Risks: PCI compliance review — Eve confirmed clear

B. Checkout frontend (5 pts) — Alice (lighter due to on-call)
  - DoD: UI live + e2e tests + a11y validated
  - Dependencies: Backend A by mid-sprint
  - Risks: 3D Secure flow — first time team has done this; spike planned day 1

C. Pricing display (3 pts) — Dave
  - DoD: Reflects new tier structure + tests
  - Dependencies: Pricing team confirmed by Apr 11
  - Risks: low

D. Order confirmation email (3 pts) — Eve
  - DoD: Email sends + template approved by marketing + tests
  - Dependencies: Marketing template by day 3
  - Risks: low

E. Bug fix: invoice download intermittently fails (3 pts) — Carol
  - DoD: Reproduced + fixed + regression test
  - Dependencies: none
  - Risks: low

F. Tech debt: split monolithic CartService (6 pts) — Bob
  - DoD: Service split + tests pass + no perf regression
  - Dependencies: none
  - Risks: medium (may take longer than estimated; descope candidate)

Total commits: 28 pts (~118 hrs)

STRETCH (target 6 pts):

G. Checkout analytics dashboard (5 pts) — anyone available
H. Coupon code field (2 pts) — anyone available

Pull from stretch only if commits done.

KEY DEPENDENCIES:
- Pricing team: tier structure by Apr 11 (Carol confirming)
- Stripe: PCI confirmation (Eve confirmed clear)
- Marketing: email template by day 3 (Eve owns ping)
- Backend A enables B (sequencing)

KEY RISKS:
- 3D Secure complexity (mitigation: spike day 1)
- Tech debt scope creep (mitigation: descope-first if commit at risk)
- On-call interrupts for Alice (mitigation: pre-allocate her 28 hrs)

DEFINITION OF DONE (this sprint):
- Code merged + reviewed
- Tests added (unit + integration; e2e for user-facing)
- Telemetry events firing in staging (verified by PM)
- Docs updated (Notion + in-product help)
- Accessibility validated (axe-core + keyboard nav)
- Feature flag configured for checkout (CHECKOUT_FLOW_V2)
- QA passed
- 24-hour bake in canary before flag enable

INCIDENT RESERVE: 10 hours (reserve; not allocated)

REVIEW POINTS:
- Mid-sprint check-in: Apr 18
- Dependency confirmation: Apr 11 (pricing)
- Spike result: Apr 15 (3D Secure)
- Final go/no-go: Apr 24
```

The good version is harder to write but easier to ship.

## Checklist

Before declaring a sprint plan ready:

- [ ] Sprint goal: one sentence, outcome-aligned
- [ ] Capacity calculated per-person, including PTO + on-call
- [ ] Commit total ≤ 80% of capacity
- [ ] Stretch ≤ 15% of capacity
- [ ] All items refined (acceptance criteria + estimated)
- [ ] All items ≤ 5 days (else split)
- [ ] Per item: dependencies named with owners
- [ ] Per item: top 1-2 risks with mitigations
- [ ] Per item: definition of done
- [ ] Buffer reserved (5-15%)
- [ ] Velocity history considered
- [ ] Mid-sprint check-in scheduled
- [ ] Engineering + PM + design aligned
