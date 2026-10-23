# Red Flags: Status Update Generator

> Common ways this skill's output goes wrong -- concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan every weekly status update before it goes to a sponsor, VP, or steering committee. Each red flag has bad and good quoted examples.

---

## Red Flag 1: Watermelon Status

**Symptom.** The traffic-light shows GREEN but the body of the update lists 4 risks and 2 blockers.
**Why it's bad.** Watermelon status (green outside, red inside) is the leading symptom of a culture that punishes bad news. By the time the sponsor sees the red, it is too late to help. Trust craters.
**Bad example:**
> "Status: GREEN.
> Blockers: vendor SDK breaking change blocking integration; QA environment down 3 days.
> Risks: scope expanded by Sales commitment; team lead on PTO for the next 2 weeks."
**Good example:**
> "Status: YELLOW (was GREEN last week).
> Reason: vendor SDK breaking change is a hard blocker; QA env down has lost 3 dev-days. With these resolved this week, recoverable to GREEN. Mitigation in Asks #1 and #3."
**How to catch it.** If the body contains items in Blockers or Risks, the traffic light must be at least YELLOW. Build this as a generator rule.

---

## Red Flag 2: Missing Asks Section

**Symptom.** Status update has Highlights / Blockers / Risks / What's Next, but no Asks.
**Why it's bad.** Asks are the only way the sponsor can actually help. Without them the update is just a report. The sponsor reads, nods, files it away, and the team's blockers do not get unblocked.
**Bad example:**
> "Highlights: A, B, C.
> Blockers: vendor SDK issue.
> Risks: scope creep.
> What's Next: integration testing.
> (No Asks section.)"
**Good example:**
> "...
> **Asks** (decisions / help needed from you this week):
> 1. Approve emergency budget for backup vendor evaluation (~$8k, 2-week trial).
> 2. Decide: ship with degraded SDK or wait 3 weeks for vendor fix.
> 3. Help unblock QA env (need IT director to assign owner)."
**How to catch it.** Status update with no Asks = either the project is dead-perfect (rare) or the team is reporting, not collaborating. Rewrite.

---

## Red Flag 3: Activity Reported as Progress

**Symptom.** Highlights list activities ("had 4 meetings with vendor", "started working on integration spec") instead of outcomes.
**Why it's bad.** Activities consume capacity without producing value. Sponsors care about outcomes -- decisions made, milestones hit, metrics moved. Activity reports signal a team that is busy but not delivering.
**Bad example:**
> "Highlights:
> - Held kickoff with vendor.
> - Started integration spec.
> - Reviewed 3 design proposals."
**Good example:**
> "Highlights:
> - Vendor commercial terms signed (5% discount vs initial quote).
> - Integration spec complete and approved; engineering starts Monday.
> - Picked design proposal C; in build."
**How to catch it.** Each highlight should have a past-tense verb of completion or a measurable change. "Started", "held", "discussed" without a decision = activity, not progress.

---

## Red Flag 4: Same Update Three Weeks in a Row

**Symptom.** The current update is 90% the same text as last week's, which was 90% the same as the week before's.
**Why it's bad.** A static update means nothing moved -- but it is being reported as if work is happening. The sponsor either ignores the update (lost signal) or assumes silent failure. Either way trust drops.
**Bad example:**
> "Week 1: 'Working on vendor integration. ETA 2 weeks.'
> Week 2: 'Working on vendor integration. ETA 2 weeks.'
> Week 3: 'Working on vendor integration. ETA 2 weeks.'"
**Good example:**
> "Week 3: 'Vendor integration paused 5 days due to SDK breaking change (see Blockers). Net: ETA slipped 1 week to <date>. We have used 9 of the 14 planned dev-days; remaining work is integration testing only.'"
**How to catch it.** Diff this week's update against last week's. < 30% changed text = something is wrong; either re-baseline or escalate.

---

## Red Flag 5: Risk Section Recycled Verbatim Each Week

**Symptom.** "Risk: vendor SDK might change before integration is complete" -- copied from week 1 to week 6 unchanged.
**Why it's bad.** Risks should evolve -- get mitigated, get worse, or become issues. Static risks signal nobody is actively managing them, which means by the time they fire there is no plan.
**Bad example:**
> "Risk (week 1, week 6, same text): 'Vendor SDK might change.'"
**Good example:**
> "Risk (week 1): 'Vendor SDK might change; mitigation: SDK pinned to v2.4; spike planned week 3.'
> Risk (week 3, updated): 'Vendor SDK breaking change confirmed in 2.5; mitigation: forking SDK for our use case; cost = 4 dev-days.'
> Risk (week 6, updated): 'Resolved -- vendor accepted our PR upstream; SDK fork merged back.'"
**How to catch it.** Any risk that has not changed wording in 3 status updates = either resolve, escalate, or update mitigation.

---

## Red Flag 6: No Numerical Anchor

**Symptom.** "Project is going well." -- no numbers, no progress percentage, no metric.
**Why it's bad.** Sponsors cannot compare progress across projects without numbers. They cannot trace trends. They cannot triage where to spend their attention. Narrative-only updates produce vibes-driven leadership.
**Bad example:**
> "Highlights: things are progressing nicely. Most work is on track."
**Good example:**
> "Highlights:
> - 14 of 22 backlog stories complete (64%), up from 9 last week (41%).
> - Beta enrolled 38 of 50 target customers; 4 are actively logging in daily.
> - 2 of 3 launch-readiness gates passed; 1 (security review) in progress."
**How to catch it.** No numbers in the Highlights section = rewrite with at least 3 concrete metrics.

---

## Red Flag 7: Update Includes Internal Drama

**Symptom.** Status update has lines like "frustrated with marketing's lack of engagement" or "engineering pushing back on scope".
**Why it's bad.** Sponsors get the wrong signal -- they see a people problem, not a project problem. The drama gets amplified up the org, and the actual project status is lost. Worse, the targeted team retaliates.
**Bad example:**
> "Blockers: marketing has not delivered the messaging brief despite 3 requests; this is causing slippage."
**Good example:**
> "Blockers: messaging brief outstanding (planned week 2, now 2 weeks late). Asked Marketing for revised ETA in the cross-team sync; owner is <name>. **Ask for sponsor**: escalate prioritization in next CMO 1:1 if not resolved by Friday."
**How to catch it.** Any emotional language ("frustrated", "pushback", "not engaging") in a status update = rewrite with neutral, factual blockers and a specific ask.

---

## Red Flag 8: One Status Update for All Stakeholders

**Symptom.** The same update goes to the engineering team, the exec sponsor, and the customer advisory board.
**Why it's bad.** Each audience has different stakes and different attention budgets. Engineering wants ticket-level detail; sponsors want outcomes; customers want themes. A one-size update annoys all three.
**Bad example:**
> "Single weekly update emailed to: dev-team@, vp-eng@, board-advisors@."
**Good example:**
> "Three views, one source:
> - **Engineering**: full ticket-level update + WIP + cycle time (in Slack #eng-updates).
> - **Exec sponsor**: 5 highlights + traffic light + asks (1-page email).
> - **Customer advisors**: themes + visible-to-customer changes only (Productboard digest)."
**How to catch it.** Same recipient list for two different stakeholder types = split.

---

## Red Flag 9: "What's Next" That Could Have Been Written in Week 1

**Symptom.** Every "What's Next" section reads "continue work on integration; QA next".
**Why it's bad.** Generic "What's Next" signals the team is operating from a static plan, not learning week to week. Sponsors cannot see emerging decisions or new bets. The update becomes a ritual.
**Bad example:**
> "What's Next: continue integration work, then QA, then launch."
**Good example:**
> "What's Next (this week's decisions, in order):
> 1. Mon -- vendor decision (stay or switch).
> 2. Wed -- scope decision (descope flow C or extend by 1 week).
> 3. Fri -- launch-readiness gate review with security."
**How to catch it.** Generic phrasing or no specific decisions in What's Next = rewrite with the week's actual forks.

---

## Red Flag 10: Generated from Stale Data

**Symptom.** The Jira / Linear export feeding the generator is 5 days old, so the update reflects last week's state.
**Why it's bad.** A status update from stale data is worse than no update -- it confidently presents an old reality. Decisions are made on it; teams find out a week later that the data was wrong.
**Bad example:**
> "Highlights: 14 of 22 stories complete. (Generated from `jira-export.json` last refreshed 5 days ago.)"
**Good example:**
> "The export is refreshed every Friday at 09:00, and the PM checks its timestamp before generating. Anything older than 24 hours is re-exported first, and the update states when the data was pulled."
**How to catch it.** `status_generator.py` reports whatever the input file says and does not check its age. Look at the export's timestamp before running it; if it is older than a day, re-export.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Watermelon status | GREEN with > 0 Blockers / Risks = wrong |
| 2 | Missing Asks | Every status has at least 1 Ask |
| 3 | Activity as progress | Each highlight has past-tense outcome verb |
| 4 | Same update 3 weeks running | < 30% changed text = escalate |
| 5 | Risks recycled verbatim | Static risk for 3 weeks = act on it |
| 6 | No numerical anchor | Highlights have >= 3 numbers |
| 7 | Internal drama in body | Emotional language = rewrite |
| 8 | Single update for all | Audience-specific views? |
| 9 | Generic "What's Next" | Specific decisions for the week? |
| 10 | Stale data | Generator rejects > 24-hour-old export |

## Related Reading

- `SKILL.md` -- the SBNR + 6-pager + traffic-light pattern
- `scripts/status_generator.py --help` -- the generator (it does not check how old the input is)
- Sibling skill: `execution/dependency-map/` -- track cross-team blockers
- Sibling skill: `execution/cycle-time-analyzer/` -- numbers to put in Highlights
- Sibling skill: `execution/roadmap-communication/` -- audience segmentation patterns
- Sibling skill: `program-manager/` -- multi-project status aggregation
