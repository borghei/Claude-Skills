# Software Spend Audit — <period>

**As-of date:** <YYYY-MM-DD> **Prepared by:** <name> **Headcount:** <n>
**Scope:** <which cost centres / categories are included, and what is excluded>

---

## Headline

| Figure | Amount | Note |
|--------|--------|------|
| Total annual software spend | | |
| Spend per head | | Benchmark for our profile: <range> |
| Gross annual opportunity | | Everything identified, regardless of timing |
| **Realisable this fiscal year** | | **This is the commitable number** |
| Locked this cycle | | Inside notice window on auto-renew; arrives next year |
| Effort to realise | <n> days | |

**Committed savings target: <amount>** — realisable only, never gross. Committing to a number
that includes locked contracts guarantees a miss you can see coming from the day you commit.

## Where the money is

| Category | Spend | Reclaimable | % | Tools |
|----------|-------|------------|---|-------|
| | | | | |

## Top opportunities

From `savings_opportunity_ranker.py`. Time-boxed items first — missing a renewal window
costs a full contract year.

| # | Tool | Lever | Gross | Realisable | Effort | Renewal | Owner |
|---|------|-------|-------|-----------|--------|---------|-------|
| 1 | | seat-reduction | | | | T-<n>d (<phase>) | |

## Utilisation detail

| Tool | Purchased | Assigned | Active 30d | Utilisation | Benchmark | Verdict |
|------|-----------|----------|-----------|-------------|-----------|---------|
| | | | | | | |

**Data quality note:** <state which tools used active-seat data and which used an SSO-login
proxy. An analysis built on assigned seats is not valid — say so explicitly if any tool
lacked active counts.>

## Consolidation candidates

| Category | Tools | Survivor | Displaced | Net recovery | Migration effort |
|----------|-------|----------|-----------|-------------|------------------|
| | | | | | |

Survivors are chosen by displacement cost (active users × criticality), not by licence price.
Recovery figures are net of an assumed 20% migration and retained-access cost.

**Umbrella-label warnings:** <list any categories the detector flagged as umbrella labels.
These must be re-tagged by job before their numbers are believed.>

## Renewal calendar — next 12 months

| Renewal date | Tool | Notice deadline | Auto-renew | Annual cost | Action | Owner |
|-------------|------|----------------|-----------|-------------|--------|-------|
| | | | | | | |

**Standing policy:** serve notice by default at the deadline on every auto-renewing contract.
Notice is procedural, not termination, and it is the difference between a negotiation and an
automatic renewal.

## Adoption failures

Tools where seats are assigned but unused. These are not seat-reduction problems — cutting
seats leaves the same people not using the tool.

| Tool | Assigned | Active | Adoption | Decision needed |
|------|----------|--------|----------|-----------------|
| | | | | Fix adoption / retire |

## Risks and dependencies

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Seat cuts trigger emergency re-purchase at list | | 12% safety buffer applied above active count |
| Consolidation displaces a critical workflow | | Verify `has_alternative` with the owning team before acting |
| Politically protected tools excluded | | <list them; they change what is worth analysing> |

## Decisions needed

- [ ] <Decision> — owner: <name>, needed by: <date, driven by the notice deadline>

## Next audit

**Date:** <six months out> | **Same `--as-of` convention:** yes
