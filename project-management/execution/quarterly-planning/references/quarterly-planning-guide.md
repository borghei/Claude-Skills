# Quarterly Planning Guide

A reference for the quarterly planning cycle. Combines Wodtke's *Radical Focus* (the weekly rhythm), Cagan's product strategy cycle (the strategic context), a product strategy cycle (the upstream choices), and the RAD ritual (Reflect-Align-Decide, the meeting format).

---

## 1. Why quarterly planning exists

The quarter is the natural cadence of product work. Sprints are too short to deliver outcomes; annual planning is too coarse to course-correct. A 13-week quarter is long enough to ship something meaningful and short enough to commit to with confidence.

Most teams have OKRs but lack the surrounding ritual. The OKR doc is written in week 0 and ignored until week 12. The result is "OKR theater" -- aspirational targets disconnected from actual work.

The cure is not better OKRs. The cure is a *cycle* -- pre-work, kickoff, weekly rhythm, mid-quarter check-in, close retro -- with each ritual reinforcing the others.

---

## 2. Christina Wodtke: Radical Focus

Wodtke's *Radical Focus* (2016) is the canonical text for OKR practice in startups and product teams. Three core ideas:

### 2.1 One Objective per quarter

Wodtke argues that focus is the rare resource. A team with 5 Objectives has 0 priorities. The discipline of choosing *one* Objective is uncomfortable but transformative.

In practice, most teams flex to 1-3 Objectives. Going beyond 3 is a warning sign.

### 2.2 Monday Commit / Friday Celebrate

The weekly rhythm is the operating system:

- **Monday Commit (15-30 min):** What will I do this week to advance the OKR? Confidence on the top KR (1-10).
- **Friday Celebrate (30 min):** Wins, learning, blockers from the week.

The Monday Commit is forward-looking ("what will happen"); the Friday Celebrate is retrospective ("what happened"). Both are essential.

Wodtke's insight: celebrating small wins is the cultural mechanism that sustains energy through a 13-week quarter. Teams that drop the celebration ritual see morale decay around week 8.

### 2.3 The 0.6-0.7 scoring target

OKRs are scored 0.0 to 1.0 at the end of the quarter. Wodtke's heuristic: average team scores in the 0.6-0.7 range indicate appropriately ambitious goals.

- Consistent 1.0 scores: sandbagging (targets too easy)
- Consistent 0.3 scores: targets too aggressive (or execution misaligned)
- 0.6-0.7 average: the team is reaching, sometimes missing, sometimes exceeding -- the right zone

This is a long-run average, not a per-quarter target. A team will have a 1.0 quarter and a 0.4 quarter; what matters is the trend over 4-6 quarters.

---

## 3. Marty Cagan: Product Strategy and Quarterly Bets

Cagan (in *Inspired* and *Empowered*) places quarterly planning inside a larger product strategy cycle:

```
Vision (10 years)
  |
  V
Product Strategy (2-3 years)
  |
  V
Quarterly Bets (13 weeks)  <-- this skill lives here
  |
  V
Roadmap (quarterly + ongoing)
  |
  V
Discovery + Delivery (continuous)
```

Cagan's argument: each layer must connect to the one above and below. A quarterly bet that does not trace to product strategy is opportunistic. A roadmap item that does not advance a quarterly bet is noise.

### Quarterly bets as forcing functions

Cagan calls quarterly OKRs *bets*. A bet is a hypothesis the team is willing to invest a quarter to test. The bet language reframes OKRs from "things we will do" to "hypotheses we will test" -- which changes the conversation.

When a bet does not work out (a KR scores 0.3), the framing is "we learned this hypothesis was wrong" rather than "we failed." This is the cultural shift that prevents sandbagging.

### Strategy review before quarterly planning

Cagan emphasizes that quarterly planning *starts* with a strategy review. Before committing OKRs for the next quarter, the team confirms:

- The vision is still right
- The product strategy is still right
- The customer signal supports the current direction
- No major shifts (competitive, regulatory, operational) require a re-think

If any of these has shifted, the quarter starts with strategy revision -- not just OKR writing.

---

## 4. The Product Strategy Cycle

A product strategy cycle frames quarterly planning as one node in a continuous strategy cycle:

```
Inputs:                    Process:               Outputs:
- Customer signal     -->  Strategy choices  -->  - Updated strategy doc
- Competitive signal       (build/buy,             - OKRs
- Market signal            grow/retain,            - Roadmap
- Operational signal       segment focus)          - Capacity plan
                                                   - Decision log
```

Quarterly planning is when the team makes (or re-confirms) the strategy choices. Between quarters, the team executes; at the quarter boundary, it re-examines.

### Strategy choices to make explicit

Name the strategy choices, not just the OKRs:

- **Build vs. buy vs. partner.** For each major capability, what is the path?
- **Grow vs. retain.** Where is the team investing -- new logo acquisition or existing-customer expansion?
- **Segment focus.** Which customer segments get priority? Which are deprioritized?
- **Risk posture.** Are we taking aggressive bets or safe bets this quarter?

These choices are upstream of the OKRs. Two teams with the same OKR ("grow MRR by 15%") may make completely different strategy choices to get there.

---

## 5. The RAD Ritual: Reflect-Align-Decide

The RAD format is the meeting structure used inside the kickoff, mid-quarter check-in, and close retro. It is a 3-step format:

### Reflect

Look back. What did we learn? What is the current state? What signals are coming in?

Time allocation: 20-30% of the meeting.

### Align

Discuss. What do these signals mean? Where do we agree? Where do we disagree?

Time allocation: 30-40% of the meeting.

### Decide

Commit. What are we doing? Who owns what? When do we revisit?

Time allocation: 30-40% of the meeting.

The RAD format prevents two common meeting failures:

- **Pure Reflect (status updates with no decision):** Time is spent re-stating what everyone already knows. No decisions made.
- **Pure Decide (decisions without reflection):** Decisions made without grounding in evidence. Often reversed.

A well-run RAD meeting moves through all three steps in order, with clear time-boxes per step.

---

## 6. Detailed cycle: pre-quarter through close

### Pre-Quarter (Weeks -3 to -1)

Three workstreams run in parallel:

#### Workstream 1: Strategy Review (PM owns)

Output: A 1-page memo answering "is our strategy still right?"

Questions to address:
- Vision check (`execution/product-vision/` Vision Review Checklist)
- NSM check (`execution/north-star-metric/`)
- Customer signal (recent interviews, synthesis themes)
- Competitive signal
- Operational signal (org changes, budget, exec mandates)

If any answer triggers a re-think, escalate to a strategy reset (may require additional kickoff time).

#### Workstream 2: Outcome Candidate List (PM owns)

Output: 5-10 candidate outcomes, each scored.

Sources:
- `discovery/jtbd-workshop/` top desired outcomes
- `execution/outcome-roadmap/` themes
- Carry-overs from prior quarter
- `discovery/interview-synthesis/` opportunities
- Reactive items (incidents, churn drivers, SLA misses)

For each candidate:
- Outcome statement (Ulwick format)
- Hypothesis ("If we X, then [outcome] improves from Y to Z")
- Confidence (1-10)
- Effort estimate (S/M/L/XL)

#### Workstream 3: Capacity Assessment (EM owns)

Output: "We have X person-weeks of productive capacity for new work."

Account for:
- Headcount transitions (planned hires, departures)
- Holidays, PTO
- On-call rotation overhead
- Maintenance and support (20-30% typical)
- Cross-team dependencies (`execution/dependency-map/`)
- Reserve for unplanned work (15-20%)

#### Kickoff Brief

48 hours before kickoff, PM circulates a 1-page brief combining all three workstreams (template in `assets/`).

### Kickoff Meeting (Week 0)

RAD-format meeting, 2-3 hours.

| Phase | Block | Time |
|-------|-------|------|
| Reflect | Last quarter's scores and learnings | 15 min |
| Align | Strategy context (vision, NSM, signals) | 30 min |
| Reflect | Candidate outcomes walk-through | 30 min |
| (Break) | | 15 min |
| Decide | Commit to OKRs (1-3 Objectives) | 45 min |
| Decide | Roadmap + capacity | 30 min |
| Decide | Tracking cadence + meeting dates | 15 min |

### Weekly Rhythm (Weeks 1-12)

- **Monday Commit:** 15-30 min, full team
- **Friday Celebrate:** 30 min, full team
- **Biweekly KR Confidence Review:** 15 min embedded in Friday Celebrate

### Mid-Quarter Check-in (Week 6)

90-minute RAD-format meeting.

| Phase | Block | Time |
|-------|-------|------|
| Reflect | Where are we? (KR data, confidence) | 15 min |
| Reflect | What is working? (scaling wins) | 30 min |
| Align + Decide | What is not working? (carry/kill/pivot/escalate) | 30 min |
| Decide | Adjust roadmap and capacity | 15 min |

### Close-of-Quarter Retro (Week 13)

90-minute RAD-format meeting.

| Phase | Block | Time |
|-------|-------|------|
| Reflect | Score each KR (0.0-1.0) | 30 min |
| Reflect | What did we learn? (customer, product, process) | 30 min |
| Decide | What carries to next quarter? | 30 min |

---

## 7. The carry/kill/pivot/escalate decision (mid-quarter)

At the mid-quarter check-in, every KR with confidence <= 5 requires an explicit decision:

| Decision | When to use |
|----------|-------------|
| **Carry** | The hypothesis is still right; we need more time, resources, or unblocking. Continue as planned. |
| **Kill** | The hypothesis was wrong. Drop the KR; redirect capacity. |
| **Pivot** | The general direction is right but the specific KR or approach is wrong. Reframe the KR with what we have learned. |
| **Escalate** | The decision is above the team's authority. Bring to exec or cross-team owner. |

The discipline of explicit decisions prevents the worst quarterly planning failure mode: KRs that quietly survive without progress and surprise everyone at the close.

---

## 8. Quarterly review deck outline

At the end of the quarter, most teams present results upward (to a leadership team, all-hands, or board). The deck is *not* the close retro -- it is the communication of results. Typical structure:

1. **Quarter at a glance** -- 1 slide with average OKR score and headline outcomes
2. **OKRs scored** -- 1 slide per Objective with KR scores and brief commentary
3. **Wins** -- 2-3 slides on what worked and why
4. **Learnings** -- 2-3 slides on what did not work and what we learned
5. **Carry-overs** -- 1 slide on what continues into next quarter
6. **Next quarter teaser** -- 1 slide on the proposed Objectives for next quarter (subject to kickoff)
7. **Ask** -- 1 slide on what the team needs from leadership (resources, decisions, unblocking)

---

## 9. Anti-patterns and remedies

| Anti-pattern | Remedy |
|---------------|--------|
| OKR theater (written, never referenced) | Enforce Monday Commit + Friday Celebrate |
| Sandbagging (every KR hits 1.0) | Wodtke 0.6-0.7 heuristic; retro asks "should the target have been higher?" |
| Scope creep mid-quarter | Mid-quarter check-in formalizes carry/kill/pivot decisions |
| Implicit carry-overs | Carry-over decisions are explicit and require re-commitment |
| Capacity over-commit | EM-owned capacity plan; reserve 15-20% |
| Internally-driven OKRs (no customer signal) | Strategy review includes customer signal from `discovery/customer-interview-script/` |
| OKRs disconnected from vision | Each Objective cites a vision pillar |
| Dependencies surprise late | Pre-quarter dependency mapping (`execution/dependency-map/`) |
| Retro skipped | Schedule at kickoff; never let it slip |

---

## 10. Worked example: Reconcile Q3

### Pre-quarter homework summary

- **Strategy review:** Unchanged. Vision still inspires. NSM (% of customers closing in <5 days) at 38%, target 60% by year-end.
- **Outcome candidate list (7 candidates):** Top three:
  1. Reduce close time from 5d to 3d for cohort A (B2B SaaS, 100-500 employees)
  2. Launch Xero integration (~30% of pipeline)
  3. Migrate audit log export to v2 schema
- **Capacity:** 80 person-weeks productive, 15 PW reserve (19%). Headcount steady.

### Kickoff outcome

- **Objective:** Make month-end close fast and trusted for mid-market B2B SaaS
- **KR1:** Close time for cohort A from 5 days to 3 days
- **KR2:** Xero integration shipped and adopted by 5+ paying customers
- **KR3:** Audit log v2 launched with zero customer-reported correctness issues
- **Roadmap:** Now = KR1 + KR2 work; Next = KR3; Later = multi-entity (Q4 candidate)
- **Cadence:** Monday Commit Mon 10am; Friday Celebrate Fri 4pm; Mid-check Aug 15; Close retro Sep 26

### Mid-quarter check-in (week 6)

- KR1 confidence: 7 (on track)
- KR2 confidence: 8 (Xero integration in beta with 4 customers; on track)
- KR3 confidence: 4 (audit log migration discovered schema-compat issues -- PIVOT to phased rollout, defer half to Q4)

### Close retro (week 13)

- KR1 score: 0.7 (cohort A close time 5d -> 3.5d)
- KR2 score: 0.9 (8 paying customers adopted Xero integration)
- KR3 score: 0.5 (audit log v2 phase 1 shipped; phase 2 deferred -- expected outcome of mid-quarter pivot)
- Average: 0.70 (in the Wodtke target zone)

Learnings:
- Customer: SMB segment values Xero more than enterprise expected
- Product: Audit log migrations should always be phased; lesson for future schema work
- Process: Mid-quarter pivot worked; team had confidence to make the call

---

## 11. References

- Wodtke, Christina. *Radical Focus: Achieving Your Most Important Goals with OKRs*. Cucina Media, 2016 (2nd ed. 2021).
- Cagan, Marty. *Inspired: How to Create Tech Products Customers Love*. Wiley, 2nd ed. 2017.
- Cagan, Marty & Jones, Chris. *Empowered: Ordinary People, Extraordinary Products*. Wiley, 2020.
- Doerr, John. *Measure What Matters*. Portfolio, 2018 (the canonical OKR origin text).
- Grove, Andrew S. *High Output Management*. Vintage, 1983 (foundational management cadence text).
