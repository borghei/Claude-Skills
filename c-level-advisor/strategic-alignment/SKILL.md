---
name: strategic-alignment
description: >
  Cascades strategy from boardroom to individual contributor and detects misalignment.
  Covers strategy articulation testing, cascade mapping, orphan goal detection, conflicting
  goal identification, silo diagnosis, communication gap analysis, and realignment protocols.
  Use when teams are pulling in different directions, OKRs don't connect, departments optimize
  locally at company expense, strategy doesn't translate to execution, or when user mentions
  alignment, strategy cascade, silo, conflicting OKRs, strategy communication, goal cascade,
  or misalignment.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: c-level
  domain: strategic-alignment
  updated: 2026-03-09
  frameworks:
    - articulation-test
    - cascade-mapping
    - orphan-detection
    - conflict-detection
    - silo-diagnosis
    - communication-gap
    - realignment-protocol
    - alignment-scoring
  triggers:
    - strategic alignment
    - strategy cascade
    - OKR alignment
    - orphan OKRs
    - conflicting goals
    - silos
    - communication gap
    - department alignment
    - alignment checker
    - strategy articulation
    - cross-functional alignment
    - goal cascade
    - misalignment
    - alignment score
    - teams pulling in different directions
    - departments not aligned
    - OKRs don't connect
    - local optimization
    - strategy communication
  cross-references:
    - c-level-advisor/ceo-advisor
    - c-level-advisor/coo-advisor
    - c-level-advisor/company-os
    - c-level-advisor/chief-of-staff
    - c-level-advisor/change-management
    - c-level-advisor/culture-architect
    - project-management/
---

# Strategic Alignment Engine

Strategy fails at the cascade, not the boardroom. This skill detects misalignment before it becomes dysfunction and builds systems that keep strategy connected from CEO to individual contributor.

## Keywords

strategic alignment, strategy cascade, OKR alignment, orphan OKRs, conflicting goals, silos, communication gap, department alignment, strategy articulation, cross-functional alignment, goal cascade, misalignment, alignment score, local optimization, strategy communication, cascade mapping

---

## The Alignment Problem

**The further a goal gets from the strategy that created it, the less likely it reflects the original intent.**

This is the organizational telephone game. It happens at every stage. The question is how bad it is and how to fix it.

```
CEO says: "We need to win the mid-market healthcare segment"
VP hears: "Healthcare is the priority"
Director translates: "Build healthcare features"
Team executes: "Add HIPAA compliance checkbox to the roadmap"
IC works on: "HIPAA feature that nobody asked for and doesn't close deals"

Result: Effort spent, strategy not advanced.
```

---

## Step 1: Strategy Articulation Test

Before checking cascade, check the source.

### The 5-Person Test

Ask five people from five different teams:

> "What is the company's most important strategic priority right now?"

| Result | Score | Diagnosis |
|--------|-------|-----------|
| All 5 give the same answer | 10/10 | Clear articulation. Check cascade. |
| 4 give similar answers | 7-8/10 | Close. Clarify the outlier. |
| 3 agree | 5-6/10 | Loose alignment. Re-communicate. |
| 2 agree | 2-4/10 | Strategy is unclear. Fix before cascade. |
| No agreement | 0-1/10 | No shared strategy exists. Start here. |

### Strategy Format Test

The strategy must be statable in one sentence.

| Format | Score |
|--------|-------|
| One clear sentence | Good |
| Two sentences | Acceptable |
| A paragraph | Too complex to cascade |
| A document | Too complex to internalize |

**Examples**:

| Bad | Why | Good |
|-----|-----|------|
| "Focus on growth while maintaining enterprise relationships and expanding internationally and investing in platform" | Four priorities = no priority | "Win the mid-market healthcare segment in DACH before Series B" |
| "Be the best at what we do" | Not falsifiable | "Reach $5M ARR by Q4 with 110%+ NRR" |
| "Customer-first approach to innovation" | Sounds nice, means nothing | "Ship the workflow automation feature that our top 10 prospects asked for" |

---

## Step 2: Cascade Mapping

Map the flow from company strategy through every organizational level.

### Cascade Visualization

```
Company Level:  Strategy Statement
                    |
                Company OKR-1    Company OKR-2    Company OKR-3
                    |                 |                 |
Dept Level:    Sales OKRs       Eng OKRs         Product OKRs
                    |                 |                 |
Team Level:    Team A OKRs      Team B OKRs       Team C OKRs
                    |                 |                 |
Individual:    Personal goals    Personal goals    Personal goals
```

### Cascade Validation Questions

For each goal at every level:

| Question | Purpose |
|----------|---------|
| Which company goal does this support? | Tests upward connection |
| If achieved 100%, how much does it move the parent goal? | Tests impact significance |
| Is the connection direct or theoretical? | Tests proximity of impact |
| Who else is working on the same parent goal? | Tests coverage and overlap |

---

## Step 3: Alignment Failure Detection

Three failure patterns to detect:

### Pattern 1: Orphan Goals

Goals that don't connect to any company-level objective.

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| "We've been working on this all quarter and nobody cares" | Goals set bottom-up without reconciliation | Connect or cut. Every goal needs a parent. |
| Team proud of achievement, leadership unaware | Misaligned definition of success | Explicit cascade mapping before quarter starts |
| Individual goals from last quarter carried forward | Inertia, not intention | Fresh cascade each quarter |

### Pattern 2: Conflicting Goals

Two teams' goals, when both succeed, create a worse outcome.

| Example | Conflict | Fix |
|---------|----------|-----|
| Sales: maximize new logos / CS: maximize NPS | Sales closes bad-fit customers, CS suffers | Shared goal: qualified new logos that retain |
| Product: ship fast / Security: no vulnerabilities | Speed vs. quality tension | Shared SLA: ship within X days with Y security checks |
| Marketing: maximize leads / Sales: close enterprise | Marketing optimizes for volume, sales needs quality | Shared metric: qualified pipeline $, not lead count |

### Pattern 3: Coverage Gaps

Company has 3 OKRs. 5 teams support OKR-1, 2 teams support OKR-2, 0 teams support OKR-3.

| Detection | Impact | Fix |
|-----------|--------|-----|
| Company OKR consistently misses while others hit | Nobody actually owns the failing OKR | Explicit team assignment to every company OKR |
| Resource allocation does not match priority | Top priority underfunded | Align resources to stated priorities |
| Strategy says X is important but no team's goals reflect it | Strategy is aspirational, not operational | Translate strategy to owned team goals |

---

## Step 4: Silo Diagnosis

Silos exist when teams optimize for local metrics at the expense of company metrics.

### Silo Detection Matrix

| Signal | Score (1-5) | Weight |
|--------|-------------|--------|
| Department hits goals while company misses | 5 = always | 25% |
| Teams don't know other teams' priorities | 5 = never | 20% |
| "That's not our problem" is common | 5 = daily | 20% |
| Cross-functional escalations only flow up | 5 = always | 15% |
| Data not shared between dependent teams | 5 = never shared | 10% |
| Cross-functional projects take 3x expected time | 5 = always | 10% |

**Score 30+**: Severe silos. Immediate intervention required.
**Score 20-29**: Moderate silos. Address in next quarter.
**Score 10-19**: Minor friction. Monitor and address specific hot spots.
**Score < 10**: Healthy cross-functional operation.

### Silo Root Causes and Fixes

| Root Cause | Fix | Owner |
|-----------|-----|-------|
| Incentive misalignment | Create shared goals where teams interact | CEO + COO |
| No shared goals | Add 1 cross-functional OKR per interacting team pair | COO |
| No shared language | Cross-functional show-and-tell monthly | Culture Architect |
| Geography/timezone | Intentional async overlap + quarterly in-person | COO + CHRO |
| Org design | Consider restructuring to reduce handoffs | CEO + CHRO |

---

## Step 5: Communication Gap Analysis

What the CEO says is not what teams hear. The gap grows with company size.

### Message Decay Model

```
CEO communicates strategy
  |
  v [10-20% loss]
VP interprets through their lens
  |
  v [10-20% loss]
Manager translates for team
  |
  v [10-20% loss]
IC receives modified version
  |
  v [10-20% loss]
IC interprets further based on daily work

Total signal loss: 40-80% from CEO to IC
```

### Communication Gap Sources

| Source | Detection | Fix |
|--------|-----------|-----|
| Ambiguity | Different teams interpret differently | Make strategy specific enough to be wrong |
| Frequency | Said once, expected to stick | Repeat strategy 7x through different channels |
| Medium mismatch | Written doc for visual thinkers | Use multiple formats (written, visual, verbal) |
| Trust deficit | Team doesn't believe strategy is real | Show resource allocation that proves it |
| Filtering | Managers edit the message | Skip-level communication + all-hands |

---

## Step 6: Realignment Protocol

How to fix misalignment without creating fear.

### Realignment Decision Tree

```
START: Misalignment detected
  |
  v
[Is the problem at the strategy level or the cascade level?]
  |
  +-- STRATEGY (Step 1 failed)
  |     --> CEO rewrites strategy as one sentence
  |     --> Re-communicate through all channels
  |     --> Re-run 5-person test after 2 weeks
  |
  +-- CASCADE (Step 2-3 failures)
  |     |
  |     v
  |   [Which failure pattern?]
  |     |
  |     +-- Orphan goals --> Connect or cut workshop
  |     +-- Conflicting goals --> Cross-functional OKR review
  |     +-- Coverage gaps --> Assign explicit ownership
  |
  +-- SILOS (Step 4)
  |     --> Fix incentives first
  |     --> Add shared metrics
  |     --> Consider org design change
  |
  +-- COMMUNICATION (Step 5)
        --> Increase frequency (weekly, not quarterly)
        --> Add skip-level communication
        --> Show resource proof (money follows words)
```

### Realignment Workshop (Half-day)

```
Agenda:
  1. CEO restates strategy (15 min)
  2. Each dept maps their goals to strategy (45 min)
  3. Identify orphans, conflicts, gaps together (30 min)
  4. Fix orphans: connect or cut (30 min)
  5. Fix conflicts: shared metrics or priority resolution (30 min)
  6. Fix gaps: assign ownership (15 min)
  7. Communication plan (15 min)
```

---

## Alignment Score

Quick health check. Score each area 0-10.

| Area | Question | Score |
|------|----------|-------|
| Strategy clarity | Can 5 people from different teams state strategy consistently? | /10 |
| Cascade completeness | Do all team goals connect to company goals? | /10 |
| Conflict detection | Have cross-team OKR conflicts been reviewed and resolved? | /10 |
| Coverage | Does each company OKR have explicit team ownership? | /10 |
| Communication | Do teams' behaviors reflect the strategy? | /10 |

### Score Interpretation

| Total (/50) | Status | Action |
|-------------|--------|--------|
| 45-50 | Excellent | Maintain the system. Quarterly check is sufficient. |
| 35-44 | Good | Address specific weak areas in next OKR cycle. |
| 20-34 | Misalignment costing you | Immediate attention. Workshop within 2 weeks. |
| < 20 | Strategic drift | Crisis-level intervention. CEO-led realignment. |

---

## Quarterly Alignment Check

Prevent recurrence with a quarterly check:

| Activity | When | Who | Duration |
|----------|------|-----|----------|
| 5-person articulation test | Week 1 of quarter | Random selection across levels | 15 min |
| Cascade map review | Week 1 | Leadership team | 1 hour |
| Conflict scan | Week 1 | COO + department leads | 30 min |
| Coverage audit | Week 1 | COO | 30 min |
| Silo pulse check | Week 2 | Cross-functional survey | 5 min survey |
| Report to CEO | Week 2 | COO or Chief of Staff | 15 min presentation |

---

## Red Flags

- Teams consistently hit goals while company misses targets -- local optimization
- Cross-functional projects take 3x longer than expected -- coordination failure
- Strategy updated quarterly but team priorities don't change -- cascade is broken
- "That's a leadership problem" at team level -- ownership gap
- New initiatives without connecting to existing OKRs -- strategy drift
- Department heads optimize for headcount/budget, not company outcomes -- incentive misalignment
- Same alignment problems reappear quarter after quarter -- systemic issue, not a one-time fix
- No one can name the company's top priority -- strategy is not communicated

---

## Integration with C-Suite

| When... | Work With... | To... |
|---------|-------------|-------|
| New strategy set | CEO + COO | Cascade into rocks before announcing |
| OKR cycle starts | COO (`coo-advisor`) | Cross-team conflict check before finalizing |
| Team misses goals | CHRO (`chro-advisor`) | Diagnose: capability gap or alignment gap? |
| Silo identified | COO | Design shared metrics or cross-functional OKRs |
| Post-M&A | CEO + Culture Architect | Detect strategy conflicts between merged entities |
| Quarterly planning | Company OS (`company-os`) | Integrate alignment check into planning rhythm |
| Change rollout | Change Management (`change-management`) | Ensure change aligns with strategy |

---

## Output Artifacts

| Request | Deliverable |
|---------|-------------|
| "Check our alignment" | Full 6-step diagnostic with alignment score |
| "Are our OKRs aligned?" | Cascade map with orphans, conflicts, and gaps identified |
| "We have silos" | Silo diagnosis with root causes and specific fixes |
| "Strategy isn't translating to execution" | Communication gap analysis + fix plan |
| "Run an alignment workshop" | Workshop agenda + facilitation guide |
| "Quarterly alignment check" | Quarterly check process + report template |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| 5-person test scores below 5/10 despite strategy existing | Strategy too complex, too vague, or communicated only once | Rewrite strategy as one falsifiable sentence; communicate through 7+ channels; repeat weekly for 4 weeks then re-test |
| Cascade map shows orphan goals but teams resist cutting them | Teams emotionally attached to work-in-progress; sunk cost fallacy | Frame as "connect or cut": every goal must have a parent OKR; if no parent exists, either create the connection or stop the work |
| Conflicting goals identified but no resolution reached | Department heads unwilling to compromise; incentive misalignment | Escalate to CEO for priority decision; create shared metric that both teams own; use balanced scorecard perspective alignment |
| Silo score above 30 but no one acknowledges the problem | Each silo operates well internally; pain is only felt at interfaces | Show cross-functional project data: 3x expected timeline; present customer impact of handoff failures; use strategy map visualization |
| Communication gap persists despite increased frequency | Wrong medium, wrong messenger, or message too abstract | Vary communication format (written, visual, verbal); use skip-level conversations; show resource allocation as proof of strategy ("money follows words") |
| Alignment workshop produces action items that are never implemented | No follow-up mechanism; workshop treated as event not process | Assign every action item an owner and deadline during the workshop; review at next weekly leadership meeting; track completion rate |
| Quarterly alignment check becomes a checkbox exercise | No consequences for misalignment; diagnostic not connected to decisions | Tie alignment score to OKR cycle planning; Red alignment areas must be addressed before new OKRs are finalized |

---

## Success Criteria

- 5-person articulation test scores 8/10 or higher within 30 days of strategy communication
- Zero orphan goals remain after quarterly cascade mapping review
- All identified goal conflicts have documented resolution with shared metrics within 2 weeks
- Silo detection score below 20 (minor friction or healthy) maintained across 3 consecutive quarters
- Communication gap analysis shows < 30% signal loss from CEO to IC level (measured by strategy comprehension survey)
- Alignment score (5 areas, /50) at 35 or above and trending stable or improving
- Quarterly alignment check completed within first 2 weeks of every quarter

---

## Scope & Limitations

- **In scope:** Strategy articulation testing, cascade mapping and validation, orphan goal detection, conflicting goal identification, coverage gap analysis, silo diagnosis, communication gap analysis, realignment protocols, alignment scoring, quarterly check cadence
- **Out of scope:** OKR writing and goal-setting methodology (use project management or Company OS skills); individual performance management (use CHRO Advisor); strategy formulation (use CEO Advisor -- this skill assumes strategy exists and tests its cascade)
- **Limitation:** Alignment diagnostics are point-in-time assessments; alignment degrades continuously and requires quarterly maintenance
- **Limitation:** The 5-person test is a heuristic, not a statistically rigorous survey; for organizations > 200 people, supplement with broader pulse survey
- **Limitation:** Silo detection matrix relies on self-reported data; supplement with objective measures (cross-functional project timelines, escalation patterns)
- **Limitation:** Framework assumes a hierarchical OKR cascade; matrix organizations and flat structures may need adapted cascade mapping

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `ceo-advisor` | Strategy must exist before alignment can be tested | CEO strategy statement → Alignment articulation test |
| `coo-advisor` | Operations owns the alignment cadence and cross-functional OKRs | Alignment conflicts → COO shared metric design |
| `company-os` | Alignment check integrates into planning rhythm | Alignment cadence → Company OS quarterly cycle |
| `chief-of-staff` | CoS facilitates alignment workshops and tracks follow-through | Alignment action items → CoS tracking |
| `culture-architect` | Silos are both structural and cultural problems | Alignment silo diagnosis → Culture intervention |
| `change-management` | Strategy changes require alignment cascade update | Change plan → Alignment re-cascade |
| `org-health-diagnostic` | Operational Health dimension reflects alignment quality | Health operations score → Alignment priority |
| `internal-narrative` | Strategy communication depends on narrative clarity | Alignment communication gaps → Narrative improvement |

---

## Python Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `scripts/okr_cascade_validator.py` | Validate that team OKRs connect to company OKRs, detecting orphans, conflicts, and coverage gaps | `python scripts/okr_cascade_validator.py --company-okrs company_okrs.csv --team-okrs team_okrs.csv --json` |
| `scripts/strategy_map_generator.py` | Generate a balanced scorecard strategy map linking financial, customer, process, and learning perspectives | `python scripts/strategy_map_generator.py --objective "Win mid-market healthcare in DACH" --financial "5M ARR by Q4" --customer "NPS > 40" --process "Ship workflow automation" --learning "Hire 3 healthcare domain experts" --json` |
| `scripts/alignment_scorer.py` | Calculate alignment score across 5 dimensions with trend tracking and recommendations | `python scripts/alignment_scorer.py --clarity 8 --cascade 6 --conflicts 7 --coverage 5 --communication 6 --previous-score 28 --json` |
