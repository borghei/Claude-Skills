# Quarterly Planning Cycle Playbook

Read this when you are running any phase of the quarterly cycle and need the detailed pre-quarter homework structure, the kickoff / mid-quarter / close meeting agendas, the weekly Wodtke rhythm scripts, the anti-pattern and troubleshooting tables, the artifacts-produced map, or the success criteria. `quarterly-planning-guide.md` carries the framework theory (Wodtke, Cagan, strategy cycle, RAD) with worked examples.

## The Quarterly Cycle

```
Week -3      -2       -1       0        1-5      6        7-12     13
  |          |        |        |         |       |         |        |
  |   Pre-quarter     |     Kickoff      |   Mid-quarter   |     Close
  |   homework        |     (start)      |   check-in      |     retro
  |                   |                  |                 |
  +--Strategy / Cagan-+--- Wodtke weekly Mon/Fri rhythm ---+
```

### Pre-Quarter Homework (Weeks -3 to -1)

Three workstreams happen in parallel before the kickoff:

1. **Strategy review.** Is the team's strategy still right? (Cagan's product strategy review)
2. **Outcome candidate list.** What outcomes could the team commit to? (Pulled from `discovery/jtbd-workshop/`, `execution/north-star-metric/`, `execution/outcome-roadmap/`)
3. **Capacity assessment.** What is the team actually capable of delivering? (Headcount, capacity, dependencies, on-call rotation)

Output: a 1-page kickoff brief delivered 48 hours before the kickoff meeting.

### Kickoff Meeting (Week 0)

The 2-3 hour meeting that commits the quarter's OKRs, roadmap, and capacity plan. Run as a RAD session (Reflect-Align-Decide).

### Tracking Cadence (Weeks 1-12)

The Wodtke weekly rhythm:

- **Monday Commit.** 15-30 min team huddle. Each person commits to what will move the OKR this week.
- **Friday Celebrate.** 30 min team huddle. Wins, learning, blockers.

Plus a biweekly review of confidence levels on each Key Result (1-10 scale).

### Mid-Quarter Check-in (Week 6)

The 90-minute meeting that course-corrects. Review confidence, kill or carry over, address dependencies.

### Close-of-Quarter Retro (Week 13)

The 90-minute meeting that scores the OKRs (0-1.0), extracts learning, and feeds the next quarter's pre-work.

## Pre-Quarter Homework

The homework is the difference between OKR-as-aspiration and OKR-as-commitment. Skip the homework and the kickoff becomes a brainstorm rather than a commit.

### Workstream 1: Strategy Review

Owner: PM (with EM and Design Lead)

Output: A 1-page "is our strategy still right?" memo.

Questions:

- **Vision check.** Does the current vision still hold? (Use `execution/product-vision/`'s Vision Review Checklist)
- **NSM check.** Is the North Star Metric still the right one? (See `execution/north-star-metric/`)
- **Customer signal.** What has changed in the customer's world in the last quarter? (Pull from `discovery/customer-interview-script/` recent sessions)
- **Competitive signal.** What competitor moves are worth responding to?
- **Operational signal.** What has changed inside the team or company (org changes, budget shifts, exec mandates)?

If any of these has materially shifted, the strategy review escalates to a *strategy reset* before kickoff -- which may require more than one kickoff meeting.

### Workstream 2: Outcome Candidate List

Owner: PM

Output: A list of 5-10 candidate outcomes, each scored for impact and feasibility.

Sources:

- Top desired outcomes from the last `discovery/jtbd-workshop/`
- Themes in the outcome roadmap (`execution/outcome-roadmap/`)
- Open bets carried from prior quarter
- Customer-feedback opportunities surfaced in `discovery/interview-synthesis/`
- Reactive items (incidents, SLA misses, churn drivers) -- these are necessary but should not crowd the list

For each candidate, capture:

- The outcome statement (in Ulwick format from `discovery/jtbd-workshop/`)
- The hypothesis: "If we [X], then [outcome] will improve from [Y] to [Z]"
- Confidence (1-10) -- how confident are we in the hypothesis?
- Effort estimate (S/M/L/XL)

### Workstream 3: Capacity Assessment

Owner: EM (with PM)

Output: A capacity plan in person-weeks.

Account for:

- Headcount at start and end of quarter (planned hires, planned departures)
- Holidays, PTO commitments
- On-call rotation overhead
- Maintenance and support load (typically 20-30%)
- Cross-team dependencies (`execution/dependency-map/`)
- Reserve for unplanned work (typically 15-20%)

Output: "We have X person-weeks of productive capacity for new work."

### The Kickoff Brief

48 hours before kickoff, the PM circulates a 1-page brief:

```markdown
# Q[X] [Year] Kickoff Brief

**Team:** [...]
**Strategy status:** Unchanged / Updated / Reset (see attached memo)
**Vision link:** [link]
**Last quarter's score:** [average OKR score 0-1.0]

## Candidate Outcomes (5-10)

| # | Outcome | Hypothesis | Confidence | Effort |
|---|---------|-----------|------------|--------|
| 1 | [...] | [...] | 7 | M |
| ... | ... | ... | ... | ... |

## Capacity

- Total person-weeks: [X]
- Reserved (maintenance, on-call, unplanned): [Y]
- Available for new work: [X-Y]

## Carry-overs from last quarter

| # | Item | Why incomplete | Recommendation |
|---|------|----------------|-----------------|
| 1 | [...] | [...] | Kill / Carry / Restart |

## Open questions for the kickoff

- [Decision needed 1]
- [Decision needed 2]
- [Decision needed 3]
```

## Kickoff Meeting Agenda (Week 0)

**Length:** 2-3 hours (or 2 x 90 min)
**Participants:** PM, EM, Design Lead, +/- exec sponsor, +/- key cross-functional partners
**Format:** RAD (Reflect-Align-Decide)
**Materials:** Kickoff brief; whiteboard or shared doc

### 0:00 - 0:15 | Reflect: Last Quarter (15 min)

- Quick review of last quarter's OKR scores
- Top 2 learnings from the close retro
- Carry-overs: any items the team has agreed to continue?

### 0:15 - 0:45 | Align: Strategy Context (30 min)

- Strategy review memo: still valid? changes needed?
- Vision sanity check: still inspiring? Roadmap items must trace to it.
- NSM context: where do we stand? what trend are we trying to move?
- Top customer/competitive signals from pre-work

### 0:45 - 1:15 | Reflect: Candidate Outcomes Review (30 min)

- PM walks through the 5-10 candidate outcomes
- For each: hypothesis, confidence, effort
- Open Q&A and challenge

### 1:15 - 1:30 | Break (15 min)

### 1:30 - 2:15 | Decide: Commit to OKRs (45 min)

- Vote on 1-3 Objectives (Wodtke: prefer 1)
- For each Objective: 3-5 Key Results
- Each Key Result has a baseline, target, and owner
- Apply the `execution/brainstorm-okrs/` SMART validation

### 2:15 - 2:45 | Decide: Roadmap and Capacity (30 min)

- Map committed OKRs to the roadmap (Now / Next / Later)
- Confirm capacity covers commitments (with reserve)
- Identify and assign cross-team dependencies

### 2:45 - 3:00 | Decide: Tracking Cadence (15 min)

- Confirm Monday Commit / Friday Celebrate is on calendars
- Confirm biweekly KR-confidence review on calendars
- Set the mid-quarter check-in date (week 6)
- Set the close retro date (week 13)
- Assign artifact owners (OKR doc, roadmap doc, capacity plan)

## The Weekly Wodtke Rhythm

Christina Wodtke's *Radical Focus* defines a weekly rhythm that converts OKRs from posters into commitments.

### Monday Commit (15-30 min)

Format:

```text
Each team member shares:
- One thing they will do this week to advance the OKR
- Confidence level on the top KR (1-10)
- Help they need
```

The Monday Commit is not a status meeting. It is a *forward-looking* meeting -- what will happen this week, not what happened last week.

### Friday Celebrate (30 min)

Format:

```text
Each team member shares:
- One win from the week
- One thing they learned
- One blocker they could not resolve
```

The Friday Celebrate is *retrospective* -- reflecting on the week. The celebration of wins, even small ones, is the cultural mechanism that keeps the team energized through a long quarter.

### Biweekly KR Confidence Review (15 min)

Every two weeks, the team reviews each Key Result and assigns a confidence (1-10).

```text
KR1: NPS from 32 to 45 by Q[X] end. Confidence: [1-10]
KR2: Activation rate from 28% to 40%. Confidence: [1-10]
```

If confidence drops below 5 for 2+ consecutive reviews, escalate to the mid-quarter check-in (or earlier).

## Mid-Quarter Check-in Agenda (Week 6)

**Length:** 90 minutes
**Participants:** Same as kickoff
**Goal:** Course-correct -- carry, kill, or escalate

### 0:00 - 0:15 | Where are we? (15 min)

- Quick walk through each KR with current data and confidence score
- Visual: target line vs. actual progress

### 0:15 - 0:45 | What is working? (30 min)

- For each KR scoring >= 6: what is driving the progress? Can we double down?
- Wins to scale across the team

### 0:45 - 1:15 | What is not working? (30 min)

- For each KR scoring <= 5: what is the bottleneck?
- Decision per KR:
  - **Carry:** Keep going; add resources or unblock dependencies
  - **Kill:** Drop the KR; the hypothesis was wrong
  - **Pivot:** Reframe the KR with what we have learned
  - **Escalate:** Decision needs an exec or cross-team owner

### 1:15 - 1:30 | Adjust roadmap and capacity (15 min)

- Killed KRs free up capacity -- where does it go?
- Pivoted KRs may need new roadmap items
- Update the OKR doc with the changes (versioned, not overwritten)

## Close-of-Quarter Retro Agenda (Week 13)

**Length:** 90 minutes
**Participants:** Same as kickoff
**Goal:** Score the OKRs, extract learning, set up next quarter's pre-work

### 0:00 - 0:30 | Score the OKRs (30 min)

For each KR, score 0.0 to 1.0:

| Score | Interpretation |
|-------|----------------|
| 0.0 - 0.3 | Failed to move; hypothesis or execution was wrong |
| 0.4 - 0.6 | Partial progress; learn from what worked and what did not |
| 0.7 - 0.9 | Strong outcome (Wodtke's target zone) |
| 1.0 | Maximum success -- if this is too easy to achieve, KR was sandbagged |

Wodtke's heuristic: average team OKR scores in the 0.6-0.7 range over the long run indicate appropriately ambitious goals. Consistent 1.0 scores indicate sandbagging.

### 0:30 - 1:00 | What did we learn? (30 min)

Each participant shares:

- One lesson about the customer
- One lesson about the product
- One lesson about the team / process

Capture into a shared learning doc.

### 1:00 - 1:30 | What carries to next quarter? (30 min)

- Which incomplete KRs deserve to continue? Why?
- Which should be killed? (More important than which should continue)
- Which new opportunities have emerged from the quarter's learning?
- Pre-quarter homework assignments for next cycle

## Anti-Patterns

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| **OKR theater** | OKRs written for the deck, never referenced after week 2 | Enforce Monday Commit + Friday Celebrate; biweekly KR review |
| **Sandbagging** | Team consistently scores 1.0 on every KR | Wodtke 0.6-0.7 heuristic; in retro, ask "should the target have been higher?" |
| **Scope creep** | New work added mid-quarter without removing existing work | Mid-quarter check-in formalizes carry/kill/pivot decisions |
| **No carry-over discipline** | Items from Q1 quietly continue into Q2 without re-commit | Carry-over decisions are explicit and require re-commitment |
| **Capacity ignored** | Team commits to more than capacity allows | EM-owned capacity plan; reserve 15-20% for unplanned |
| **No customer signal in planning** | Kickoff is internally-driven; no recent customer insight | Pre-quarter homework includes customer signal from `discovery/customer-interview-script/` |
| **OKRs disconnected from vision** | Team's Q3 OKRs don't trace to the long-term direction | Each Objective references a vision pillar; if it doesn't, ask why |
| **Cross-team dependencies surprise late** | Dependencies discovered in week 6 instead of week 0 | Pre-quarter dependency mapping (`execution/dependency-map/`) |
| **Retro skipped** | Quarter ends without a retro; learning lost | Schedule the retro at kickoff (week 13 date); never let it slip |

## Workflow

1. **Three weeks before quarter start:** Open the pre-work. PM kicks off strategy review, outcome candidate list, capacity assessment.
2. **Two days before kickoff:** Circulate the kickoff brief to all participants.
3. **Week 0:** Run the 2-3 hour kickoff meeting. Commit OKRs, roadmap, capacity, cadence.
4. **Weeks 1-12:** Run Monday Commit / Friday Celebrate / biweekly KR review consistently. Do not skip.
5. **Week 6:** Run the mid-quarter check-in. Make carry/kill/pivot/escalate decisions explicitly.
6. **Week 13:** Run the close retro. Score OKRs, extract learning, set up next quarter's pre-work.
7. **Document everything.** OKR scores, lessons, carry-overs into the team wiki. The history is more valuable than the deck.
8. **Repeat.** The cycle is not optional. It is the operating system.

## Tools and Artifacts Produced

| Artifact | Owner | Cadence | Stored Where |
|----------|-------|---------|---------------|
| Strategy review memo | PM | Quarterly (pre-work) | Wiki / `documentation/delivery/` |
| Outcome candidate list | PM | Quarterly (pre-work) | Shared doc |
| Capacity plan | EM | Quarterly (pre-work) | Shared doc |
| Kickoff brief | PM | Quarterly (pre-kickoff) | Email + wiki |
| Committed OKRs | PM | Quarterly | OKR doc (versioned) |
| Roadmap (Now/Next/Later) | PM | Quarterly + updates | Roadmap tool (`execution/outcome-roadmap/`) |
| KR confidence log | PM | Biweekly | OKR doc |
| Mid-quarter check-in notes | PM | Once per quarter | Wiki |
| Close retro notes | PM | Once per quarter | Wiki |
| Quarterly review deck | PM | Once per quarter | Slides |

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| OKRs are never referenced after kickoff | Weekly rhythm not enforced; Monday Commit absent | Calendar lock Monday Commit + Friday Celebrate; tie KR confidence to biweekly review |
| Team consistently overcommits | Capacity assessment skipped or aspirational | EM-owned capacity plan; reserve 15-20% for unplanned; mid-quarter check-in adjusts |
| Mid-quarter check-in becomes a status update | No carry/kill/pivot decisions made | Force a decision per KR scoring <= 5; document the decision in the OKR log |
| Close retro skipped or rushed | Calendar pressure; perceived low value | Schedule retro at kickoff; treat it as the highest-leverage 90 min of the cycle |
| OKRs disconnect from vision | Quarterly planning becomes self-contained | Each Objective must cite a vision pillar in the OKR doc |
| Sandbagged KRs (every KR hits 1.0) | Targets set to ensure success, not stretch | In retro, ask "should the target have been higher?"; aim for 0.6-0.7 average over time |
| Cross-team dependencies surprise late | Dependencies not mapped during pre-work | Use `execution/dependency-map/` during pre-work; circulate dependency commitments before kickoff |
| Team morale drops mid-quarter | Friday Celebrate dropped; no recognition rhythm | Reinstate the celebrate ritual even if wins are small; energy compounds |

## Success Criteria

- Pre-quarter homework completed and kickoff brief circulated 48 hours before kickoff
- Kickoff produces 1-3 Objectives with 3-5 KRs each; every KR has baseline, target, owner
- Capacity plan covers committed work with 15-20% reserve
- Monday Commit + Friday Celebrate held every week (>= 90% attendance)
- Biweekly KR confidence review held without exception
- Mid-quarter check-in produces explicit carry/kill/pivot/escalate decisions
- Close retro scores every KR (0.0-1.0) and extracts >= 3 documented learnings
- Average team OKR score in the 0.6-0.7 range over multiple quarters
- Every Objective traces to a vision pillar
