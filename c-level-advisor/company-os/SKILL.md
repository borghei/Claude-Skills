---
name: company-os
description: >
  The meta-framework for how a company runs -- the connective tissue between all C-suite
  roles. Covers operating system selection (EOS, Scaling Up, OKR-native, hybrid), accountability
  charts, scorecards, meeting pulse design, issue resolution (IDS), 90-day rocks, and
  communication cadence. Use when setting up company operations, selecting a management
  framework, designing meeting rhythms, building accountability systems, implementing OKRs,
  or when user mentions EOS, Scaling Up, operating system, L10 meetings, rocks, scorecard,
  accountability chart, quarterly planning, or meeting cadence.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: c-level
  domain: company-operations
  updated: 2026-03-09
  frameworks:
    - os-comparison
    - accountability-chart
    - scorecard-design
    - meeting-pulse
    - ids-resolution
    - rocks-framework
    - communication-cadence
  triggers:
    - operating system
    - company OS
    - EOS
    - Scaling Up
    - Rockefeller Habits
    - OKR
    - OKRs
    - L10 meeting
    - rocks
    - scorecard
    - accountability chart
    - issues list
    - IDS
    - meeting pulse
    - quarterly planning
    - weekly scorecard
    - management framework
    - company rhythm
    - traction
    - meeting cadence
    - weekly meeting
    - annual planning
  cross-references:
    - c-level-advisor/ceo-advisor
    - c-level-advisor/coo-advisor
    - c-level-advisor/strategic-alignment
    - c-level-advisor/culture-architect
    - c-level-advisor/chief-of-staff
    - project-management/
---

# Company Operating System

The operating system is the collection of tools, rhythms, and agreements that determine how the company functions. Every company has one -- most just do not know what it is. Making it explicit makes it improvable.

## Keywords

operating system, EOS, Entrepreneurial Operating System, Scaling Up, Rockefeller Habits, OKR, Holacracy, L10 meeting, rocks, scorecard, accountability chart, issues list, IDS, meeting pulse, quarterly planning, weekly scorecard, management framework, company rhythm, traction, annual planning, communication cadence

---

## Operating System Selection

### Decision Tree

```
START: "Which operating system?"
  |
  v
[Company size?]
  |
  +-- 10-50 people
  |     |
  |     v
  |   [Is the founder operational or visionary?]
  |     |
  |     +-- Operational --> EOS / Traction (structured, simple)
  |     +-- Visionary --> Scaling Up (ambitious, strategy-heavy)
  |
  +-- 50-200 people
  |     |
  |     v
  |   [Engineering-led or sales-led?]
  |     |
  |     +-- Engineering-led --> OKR-native (hypothesis-driven)
  |     +-- Sales-led --> Scaling Up or EOS (execution-focused)
  |
  +-- 200+ people
  |     |
  |     v
  |   [High autonomy or high alignment needed?]
  |     |
  |     +-- High autonomy --> Holacracy (only if patient)
  |     +-- High alignment --> Custom hybrid (best of EOS + OKR)
  |
  +-- Not sure --> Start with EOS. It is the simplest to implement.
```

### Framework Comparison Matrix

| Feature | EOS | Scaling Up | OKR-Native | Holacracy |
|---------|-----|-----------|------------|-----------|
| Complexity | Low | Medium | Medium | High |
| Implementation time | 30-90 days | 90-180 days | 60-120 days | 6-12 months |
| Best company size | 10-250 | 50-500 | 20-500 | 50-300 |
| Goal framework | Rocks (binary) | OKRs + Priorities | OKRs (graded) | Roles + accountabilities |
| Meeting cadence | Weekly L10 | Daily huddle + weekly | Weekly + quarterly | Governance + tactical |
| Issue resolution | IDS | Keep/Kill/Combine | Retrospective | Governance process |
| Accountability | Accountability chart | Function accountability | OKR ownership | Role-based |
| Scorecard | Weekly numbers | Weekly KPIs | Quarterly KRs | Metrics per role |
| Strengths | Simple, fast to implement | Rigorous, strategy-heavy | Flexible, tech-friendly | Distributed authority |
| Weaknesses | Can feel rigid | Complex, requires discipline | Can drift without structure | Steep learning curve |

---

## The Six Core Components

Every effective operating system has these six, regardless of framework:

### Component 1: Accountability Chart

Not an org chart. An accountability chart answers: "Who owns this outcome?"

#### Design Principles

| Principle | Implementation |
|-----------|---------------|
| Single ownership | One person owns each function. Multiple may work in it. |
| Explicit gaps | Functions nobody owns are identified and assigned. |
| No overlap | If two people think they own it, neither does. Resolve immediately. |
| Stage-appropriate | One person can own multiple seats early. Be explicit about it. |
| Quarterly review | Ownership shifts as company grows. Review every quarter. |

#### Accountability Chart Template

```
CEO
  |
  +-- Revenue (CRO/VP Sales)
  |     +-- Inbound pipeline
  |     +-- Outbound pipeline
  |     +-- Customer success
  |
  +-- Product & Engineering (CTO/CPO)
  |     +-- Product roadmap
  |     +-- Engineering delivery
  |     +-- Technical operations
  |
  +-- Operations (COO)
  |     +-- Finance & legal
  |     +-- People operations
  |     +-- Business operations
  |
  +-- Marketing (CMO/VP Marketing)
        +-- Demand generation
        +-- Brand & content
        +-- Product marketing
```

#### Workshop Protocol (2 hours)

```
Step 1: List all functions the company performs (30 min)
Step 2: Assign ONE owner per function (30 min)
Step 3: Identify gaps (functions nobody owns) (15 min)
Step 4: Identify overlaps (2+ people claiming ownership) (15 min)
Step 5: Resolve gaps and overlaps (20 min)
Step 6: Publish and communicate (10 min)
```

### Component 2: Scorecard

Weekly metrics that tell you if the company is on track. Not monthly. Not quarterly. Weekly.

#### Scorecard Rules

| Rule | Rationale |
|------|-----------|
| 5-15 metrics maximum | More than 15 = nothing gets attention |
| Each metric has an owner | Ownership drives accountability |
| Each metric has a weekly target | Not a range -- a specific number |
| Red/Yellow/Green status | Not paragraphs -- traffic lights |
| Only Red metrics get discussion | Green = no discussion needed in meeting |

#### Example Scorecard

| Metric | Owner | Target | Week | Status |
|--------|-------|--------|------|--------|
| New MRR | CRO | $50K | $43K | [R] |
| Logo churn | CS Lead | < 1% | 0.8% | [G] |
| Active users | CPO | 2,000 | 2,150 | [G] |
| Deployments | CTO | 3/week | 3 | [G] |
| Critical bugs open | CTO | 0 | 2 | [R] |
| Runway | CFO | > 18mo | 16mo | [Y] |
| Offer acceptance | CHRO | > 85% | 90% | [G] |

### Component 3: Meeting Pulse

#### Full Meeting Rhythm

| Meeting | Frequency | Duration | Who | Purpose |
|---------|-----------|----------|-----|---------|
| Daily standup | Daily | 15 min | Each team | Blockers only |
| L10 / Leadership sync | Weekly | 90 min | Leadership team | Scorecard + issues |
| Department review | Monthly | 60 min | Dept + leadership | Deep dive on dept metrics |
| Quarterly planning | Quarterly | 1-2 days | Leadership | Set rocks, review strategy |
| Annual planning | Annual | 2-3 days | Leadership | 1-year + 3-year vision |

#### L10 Meeting Agenda (Weekly Leadership)

| Segment | Duration | Activity |
|---------|----------|----------|
| Good news | 5 min | Personal + business wins |
| Scorecard review | 5 min | Flag red items only |
| Rock review | 5 min | On/off track for each rock |
| Customer/employee headlines | 5 min | Notable events |
| Issues list (IDS) | 60 min | Identify, Discuss, Solve |
| To-dos review | 5 min | Last week's commitments: done or not? |
| Conclude | 5 min | Rate meeting 1-10, what would make it 10 next time |

### Component 4: Issue Resolution (IDS)

Maximum 15 minutes per issue. This is the core problem-solving loop.

```
IDENTIFY: What is the actual issue? (One sentence, root cause, not symptom)
  |
DISCUSS: Relevant facts + perspectives. Time-boxed.
  |       When discussion starts repeating, STOP.
  |
SOLVE: One owner. One action. One due date. Written down.
```

#### IDS Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| "Let's take this offline" | Things taken offline rarely get resolved | Solve it now or put it on next week's list |
| Discussing without deciding | Great discussion, no action item = wasted | Every discussion must end with a decision |
| Revisiting decided issues | Undermines the system | Once solved, off the list. Reopen only with new data. |
| Issue on list 3+ meetings | Either not real or too scary to address | Force it: address this week or remove it |
| Multiple issues conflated | Impossible to solve a bundled problem | One issue per entry. Separate if needed. |

### Component 5: Rocks (90-Day Priorities)

#### Rock Rules

| Rule | Rationale |
|------|-----------|
| 3-7 per person maximum | More than 7 = none get done |
| 3-7 company-level rocks | Shared leadership priorities |
| Binary status: done or not done | No "60% complete" |
| Set at quarterly planning | Reviewed weekly (on/off track) |
| Not a to-do list | Rocks take 90 days of sustained work |

#### Good vs. Bad Rocks

| Bad Rock | Why | Good Rock |
|----------|-----|-----------|
| "Improve sales process" | Not measurable or specific | "Implement CRM with pipeline stages and reporting by Mar 31" |
| "Hire more engineers" | No target, no deadline | "Hire 3 senior engineers with offers accepted by Apr 15" |
| "Reduce churn" | No target | "Reduce monthly logo churn from 3% to 1.5% by end of Q2" |
| "Get better at communication" | Not observable | "Ship weekly company update every Friday for 12 weeks" |

### Component 6: Communication Cadence

| Audience | What | When | Format |
|----------|------|------|--------|
| All employees | Company update | Monthly | Written + Q&A |
| All employees | Quarterly results + priorities | Quarterly | All-hands meeting |
| Leadership team | Scorecard | Weekly | Dashboard |
| Board | Company performance | Monthly or quarterly | Board memo/deck |
| Investors | Key metrics + narrative | Monthly or quarterly | Investor update |
| Customers | Product updates | Per release | Release notes |

**Default rule**: If deciding whether to share internally, share it. Under-communication always costs more than over-communication.

---

## Implementation Roadmap

### 30-Day Quick Start

| Week | Activity | Time Investment |
|------|----------|-----------------|
| 1 | Build accountability chart | 2-hour workshop |
| 2 | Define 5-10 weekly scorecard metrics | 1-hour alignment session |
| 3 | Start weekly L10 meeting | 90 min/week (ongoing) |
| 4 | Set first round of 90-day rocks | Half-day planning session |

These four alone improve coordination more than most companies achieve in a year.

### 90-Day Full Implementation

| Month | Focus | Deliverables |
|-------|-------|-------------|
| 1 | Foundation | Accountability chart, scorecard, L10 meetings |
| 2 | Depth | Rocks defined, issues list active, daily standups |
| 3 | Cadence | Full meeting rhythm, communication cadence, first quarterly review |

---

## Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Partial implementation | "We do OKRs but skip check-ins" | Half an OS is worse than none. Commit to the full system. |
| Meeting fatigue | Added rhythm on top of existing meetings | Replace meetings, do not add them |
| Metric overload | 30 KPIs because "they all matter" | Start with 5. Add only when cadence is established. |
| Rock inflation | 12 rocks per person | Hard limit: 7 per person, 7 for the company. |
| Leader non-compliance | Leadership skips L10 or ignores IDS | The OS mirrors leadership respect. Leaders go first. |
| No quarterly review | Annual goals checked at year-end | Quarterly is the minimum review cycle. |
| Scorecard without targets | Tracking numbers without thresholds | Every metric needs a target to be actionable. |

---

## Red Flags

- Five team leads give different answers when asked "What are the top 3 company priorities?" -- alignment failure
- Same issue on the issues list for 4+ weeks -- avoidance or structural problem
- No weekly scorecard exists -- flying blind
- Rocks set but never reviewed weekly -- goals without accountability
- Accountability chart has not been updated in 6+ months -- reality has drifted
- Meetings consistently end without decisions -- meeting design problem
- Communication is all top-down, never bottom-up -- feedback loop broken

---

## Integration with C-Suite

| Role | OS Dependency |
|------|---------------|
| CEO (`ceo-advisor`) | Sets vision that feeds 1-year plan and rocks |
| COO (`coo-advisor`) | Owns meeting pulse and issue resolution cadence |
| CFO (`cfo-advisor`) | Owns financial metrics in the scorecard |
| CTO (`cto-advisor`) | Owns engineering rocks and tech scorecard metrics |
| CHRO (`chro-advisor`) | Owns people metrics (attrition, hiring velocity) |
| Culture Architect (`culture-architect`) | Culture rituals integrate into meeting pulse |
| Strategic Alignment (`strategic-alignment`) | Validates team rocks cascade from company rocks |
| Change Management (`change-management`) | New OS rollout follows ADKAR model |

---

## Output Artifacts

| Request | Deliverable |
|---------|-------------|
| "Set up our operating system" | Framework recommendation + 30-day implementation plan |
| "Design our meeting cadence" | Full meeting rhythm with agendas and owners |
| "Build our scorecard" | 5-15 metrics with owners, targets, and thresholds |
| "Help with quarterly planning" | Planning session agenda + rock-setting framework |
| "Fix our accountability" | Accountability chart workshop + gap/overlap analysis |
| "We keep discussing the same issues" | IDS training + issues list audit |
