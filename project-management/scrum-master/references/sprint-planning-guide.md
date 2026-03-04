# Sprint Planning Guide: Comprehensive Reference for Scrum Masters

## Table of Contents
- [Overview](#overview)
- [Pre-Planning Checklist](#pre-planning-checklist)
- [Sprint Goal Setting](#sprint-goal-setting)
- [Capacity Planning Methodology](#capacity-planning-methodology)
- [Story Selection Criteria](#story-selection-criteria)
- [Commitment vs Forecast](#commitment-vs-forecast)
- [Sprint Planning Meeting Facilitation](#sprint-planning-meeting-facilitation)
- [Common Anti-Patterns](#common-anti-patterns)
- [Tool Integration](#tool-integration)

---

## Overview

Sprint planning is the ceremony that sets the direction for each sprint. Effective sprint planning requires preparation, data-driven capacity analysis, clear goal setting, and collaborative story selection. This guide provides a structured approach for Scrum Masters to facilitate productive sprint planning sessions.

### Key Principles
1. **Data-Informed Decisions**: Use historical velocity and capacity data, not gut feel
2. **Team Ownership**: The team commits to the sprint backlog, not the Scrum Master or Product Owner
3. **Goal-Driven Selection**: Every story should map to the sprint goal
4. **Realistic Capacity**: Account for ceremony overhead, PTO, and focus factor
5. **Preparation Is Everything**: 80% of sprint planning success happens before the meeting

---

## Pre-Planning Checklist

Complete these steps before the sprint planning meeting begins.

### Velocity Analysis (2-3 days before planning)
- [ ] Pull velocity data for the last 3-6 sprints
- [ ] Calculate rolling 3-sprint and 5-sprint averages
- [ ] Note any anomalies or outliers and their causes
- [ ] Identify velocity trend (improving, stable, or declining)
- [ ] Run `velocity_analyzer.py` on recent sprint data for statistical analysis
- [ ] Review the volatility level (low, moderate, high)

### Backlog Readiness (2-3 days before planning)
- [ ] Confirm top 2x sprint capacity worth of stories meet Definition of Ready
- [ ] Verify story points are assigned to candidate stories
- [ ] Check for missing acceptance criteria
- [ ] Identify and document inter-story dependencies
- [ ] Ensure Product Owner has prioritized the backlog
- [ ] Confirm technical spikes or research items are resolved

### Capacity Check (1 day before planning)
- [ ] Collect PTO and out-of-office plans for the sprint
- [ ] Confirm team member allocation percentages
- [ ] Note any team composition changes (new members, departures)
- [ ] Run `sprint_capacity_calculator.py` with team data
- [ ] Calculate available hours with ceremony overhead deducted
- [ ] Apply 80-85% focus factor for realistic planning

### Stakeholder Alignment (1-2 days before planning)
- [ ] Product Owner has reviewed and refined the sprint goal
- [ ] Known external dependencies are identified
- [ ] Release commitments and deadlines are visible
- [ ] Cross-team coordination items are flagged

---

## Sprint Goal Setting

### SMART Sprint Goals

Every sprint should have a single, clear goal that follows the SMART format:

| Element | Description | Example |
|---------|-------------|---------|
| **Specific** | Clear, unambiguous outcome | "Complete user authentication flow" |
| **Measurable** | Quantifiable success criteria | "All 5 auth stories pass QA" |
| **Achievable** | Realistic given capacity | "Within team's velocity range" |
| **Relevant** | Aligned with product goals | "Supports Q2 launch milestone" |
| **Time-bound** | Fits within the sprint | "Done by sprint end" |

### Sprint Goal Templates

**Feature-Focused:**
> "By the end of this sprint, users will be able to [capability], enabling [business outcome]."

**Technical-Focused:**
> "Reduce [technical metric] by [target]% to improve [user-facing outcome]."

**Discovery-Focused:**
> "Validate [hypothesis] through [method] to inform [decision]."

**Debt-Focused:**
> "Resolve [specific debt items] to unblock [future capability] and reduce [risk/maintenance cost]."

### Alignment with Product Goals
- Sprint goal should trace to a product roadmap item or OKR
- The Product Owner should explain WHY this goal matters now
- Team should understand the business context behind the goal
- Sprint goal is the tiebreaker when prioritizing work during the sprint

---

## Capacity Planning Methodology

### Step 1: Calculate Gross Available Hours

For each team member:
```
Gross Hours = (Available Days - PTO Days) x Hours Per Day x (Allocation% / 100)
```

### Step 2: Deduct Ceremony Overhead

Standard ceremony overhead per team member per sprint (10-day sprint):

| Ceremony | Duration | Frequency | Total |
|----------|----------|-----------|-------|
| Sprint Planning | 2h | Once | 2.0h |
| Daily Standup | 15min | Per day | 2.5h |
| Sprint Review | 1h | Once | 1.0h |
| Sprint Retrospective | 1h | Once | 1.0h |
| Backlog Refinement | 1h | Once | 1.0h |
| **Total Per Member** | | | **7.5h** |

```
Net Hours = Gross Hours - Ceremony Hours
```

### Step 3: Apply Focus Factor

The focus factor accounts for interruptions, context switching, ad-hoc meetings, email, and general productivity loss:

| Team Maturity | Focus Factor | Use When |
|---------------|-------------|----------|
| New team / high interrupts | 70-75% | Forming/storming teams, support rotation |
| Established team | 80% | Most teams, recommended default |
| Highly focused team | 85% | Performing teams, protected from interrupts |

```
Realistic Capacity = Net Hours x Focus Factor
```

### Step 4: Convert to Story Points (Optional)

If the team uses story points and has historical velocity:
```
Estimated Points = Historical Velocity x (Current Capacity / Typical Capacity)
```

Use `sprint_capacity_calculator.py` to automate this calculation:
```bash
python scripts/sprint_capacity_calculator.py team_data.json --format text
```

### Capacity Planning Example

| Member | Days | PTO | Alloc% | Gross | Ceremony | Net |
|--------|------|-----|--------|-------|----------|-----|
| Alice | 10 | 0 | 100% | 60.0h | 7.5h | 52.5h |
| Bob | 10 | 2 | 100% | 48.0h | 7.5h | 40.5h |
| Carol | 10 | 0 | 80% | 48.0h | 6.0h | 42.0h |
| **Total** | | | | **156.0h** | **21.0h** | **135.0h** |

With 80% focus factor: **108.0h** realistic capacity

---

## Story Selection Criteria

### Definition of Ready Checklist

A story must meet ALL of these criteria before it can be pulled into a sprint:

- [ ] User story or job story format is complete
- [ ] Acceptance criteria are written in Given/When/Then format
- [ ] Story is sized (story points assigned)
- [ ] Story is small enough to complete within one sprint
- [ ] Dependencies are identified and resolved (or plan exists)
- [ ] UX designs or wireframes are available (if applicable)
- [ ] Technical approach is understood by at least 2 team members
- [ ] Product Owner can answer clarifying questions
- [ ] Story is prioritized in the backlog

### Dependency Assessment

For each candidate story, evaluate:

| Dependency Type | Risk Level | Action |
|----------------|------------|--------|
| No dependencies | Low | Safe to include |
| Internal dependency (same team) | Low-Medium | Sequence stories in sprint |
| Cross-team dependency (committed) | Medium | Include with buffer |
| Cross-team dependency (uncommitted) | High | Avoid or create contingency |
| External vendor dependency | High | Do not commit; make stretch goal |

### Risk Evaluation

Rate each story on these dimensions before inclusion:

1. **Complexity**: Is the technical approach well understood?
2. **Uncertainty**: How much discovery is still needed?
3. **Size**: Is this the right size or should it be split?
4. **Dependencies**: Are all inputs available?
5. **Testing**: Is the test strategy clear?

Stories with high risk scores should be:
- Placed early in the sprint (fail fast)
- Paired with a buffer or contingency plan
- Split into smaller, lower-risk pieces

---

## Commitment vs Forecast

### The Shift from Commitment to Forecast

Modern Scrum practice has moved from "commitment" (a promise to deliver) to "forecast" (a best estimate of what can be done). Understanding this distinction is critical.

| Aspect | Commitment Model | Forecast Model |
|--------|-----------------|----------------|
| **Language** | "We will deliver X" | "We expect to deliver X" |
| **Flexibility** | Low; scope is locked | High; scope adjusts to reality |
| **Failure mode** | Blame and pressure | Learning and adaptation |
| **Planning basis** | Optimistic estimates | Probabilistic ranges |
| **Sprint goal** | Must complete all stories | Must achieve the sprint goal |

### When to Use Each

**Use commitment language when:**
- Release deadlines are fixed and non-negotiable
- External stakeholders need firm delivery dates
- The team has high velocity stability (low volatility)

**Use forecast language when:**
- Sprint goal is clear but exact scope may flex
- Team is still stabilizing or has high volatility
- Stories have significant uncertainty
- You want to encourage healthy risk-taking

### Practical Application

Present the sprint plan as:
> "Based on our capacity of X hours and historical velocity of Y points, we forecast completing these stories. Our sprint goal is [GOAL]. Stories A, B, and C directly support the goal. Stories D and E are stretch goals if capacity allows."

---

## Sprint Planning Meeting Facilitation

### Meeting Setup
- **Duration**: 2 hours for a 2-week sprint (1 hour for 1-week sprint)
- **Attendees**: Scrum Master, Product Owner, Development Team
- **Pre-work**: All items from Pre-Planning Checklist completed
- **Materials**: Capacity report, prioritized backlog, sprint board

### Part 1: The WHAT (45-60 minutes)

**Purpose**: Establish the sprint goal and select candidate stories.

**Facilitation Flow:**

1. **Product Owner presents sprint goal** (5 min)
   - Business context and why this goal matters now
   - Alignment with product roadmap and OKRs
   - Success criteria for the sprint

2. **Scrum Master presents capacity** (5 min)
   - Team availability and PTO
   - Ceremony overhead deductions
   - Focus-adjusted capacity in hours and estimated points
   - Reference `sprint_capacity_calculator.py` output

3. **Velocity context** (5 min)
   - Last 3-sprint rolling average
   - Trend direction and confidence
   - Reference `velocity_analyzer.py` output

4. **Product Owner walks through candidate stories** (20-30 min)
   - Present stories in priority order
   - Team asks clarifying questions
   - Confirm each story meets Definition of Ready
   - Flag dependencies and risks

5. **Team selects stories for the sprint** (10-15 min)
   - Pull stories up to forecast capacity
   - Confirm sprint goal alignment
   - Identify stretch goals (clearly labeled)
   - Team verbally confirms the forecast

### Part 2: The HOW (45-60 minutes)

**Purpose**: Break stories into tasks and create a plan for delivery.

**Facilitation Flow:**

1. **Task breakdown** (30-40 min)
   - For each story, identify implementation tasks
   - Estimate task durations (optional, in hours)
   - Identify task owners or pairs
   - Note technical dependencies between tasks

2. **Sequencing and scheduling** (10 min)
   - Identify which stories to start first
   - Highlight critical path items
   - Plan for early validation of risky stories

3. **Final capacity check** (5 min)
   - Verify total task estimates fit within capacity
   - Adjust scope if over-committed
   - Confirm the sprint backlog

4. **Sprint plan confirmation** (5 min)
   - Scrum Master reads back the sprint goal
   - Team confirms the forecast
   - Note any open questions or risks to monitor

### Facilitation Tips

- **Timebox aggressively**: Use a visible timer for each section
- **Redirect deep dives**: "Great topic, let's take that offline after planning"
- **Ensure everyone speaks**: Directly ask quieter team members for input
- **Capture parking lot items**: Keep a visible list of deferred discussions
- **Energy management**: Take a 5-minute break between Part 1 and Part 2
- **Make it visual**: Update the sprint board in real-time during planning

---

## Common Anti-Patterns

### 1. Over-Commitment
**Symptom**: Team consistently carries over stories sprint after sprint.
**Root Cause**: Planning to velocity ceiling instead of average; ignoring capacity changes.
**Fix**: Use 80% focus factor, plan to rolling average velocity, track carry-over rate.

### 2. No Sprint Goal
**Symptom**: Sprint is just a random collection of stories.
**Root Cause**: Product Owner not engaged in planning; no strategic direction.
**Fix**: Require a sprint goal before story selection begins; tie stories to the goal.

### 3. Ignoring Velocity Data
**Symptom**: Team plans "by feel" and velocity is unpredictable.
**Root Cause**: Lack of data collection or distrust of metrics.
**Fix**: Run `velocity_analyzer.py` regularly; use data to inform, not dictate.

### 4. Stories Not Ready
**Symptom**: Planning takes 3+ hours due to clarification questions.
**Root Cause**: Insufficient backlog refinement; Definition of Ready not enforced.
**Fix**: Enforce DoR check before planning; invest in refinement sessions.

### 5. Scope Creep During Sprint
**Symptom**: Stories added mid-sprint, original goal abandoned.
**Root Cause**: Weak sprint protection; stakeholder pressure; unclear sprint goal.
**Fix**: Scrum Master shields the team; any addition requires equal removal.

### 6. Skipping Part 2 (The How)
**Symptom**: Team starts sprint without a plan; stories sit untouched for days.
**Root Cause**: Time pressure; belief that Part 2 is optional.
**Fix**: Protect Part 2 time; even 30 minutes of task breakdown reduces surprises.

### 7. One Person Dominates Planning
**Symptom**: Tech lead or senior developer makes all decisions.
**Root Cause**: Low psychological safety; habit; perceived efficiency.
**Fix**: Use round-robin for story discussion; explicitly ask for input from all.

### 8. Padding with Stretch Goals
**Symptom**: Team always pulls in "stretch goals" as buffer items.
**Root Cause**: Stretch goals used to mask over-commitment or under-commitment.
**Fix**: Clearly separate committed forecast from stretch items; track both.

---

## Tool Integration

### velocity_analyzer.py

Use before sprint planning to understand velocity trends:

```bash
# Analyze recent velocity data
python scripts/velocity_analyzer.py sprint_data.json --format text

# Get JSON output for dashboards
python scripts/velocity_analyzer.py sprint_data.json --format json
```

**Key outputs for sprint planning:**
- Rolling 3-sprint and 5-sprint velocity averages
- Trend direction and confidence level
- Volatility assessment (low/moderate/high)
- Anomaly detection for recent sprints
- Monte Carlo forecast for upcoming sprints

### sprint_capacity_calculator.py

Use to calculate team capacity for the upcoming sprint:

```bash
# Calculate capacity from team data
python scripts/sprint_capacity_calculator.py team_data.json --format text

# Demo mode to see expected output
python scripts/sprint_capacity_calculator.py --demo

# JSON output for integration
python scripts/sprint_capacity_calculator.py team_data.json --format json
```

**Input JSON format:**
```json
{
  "sprint_length_days": 10,
  "historical_velocity": 42,
  "team_members": [
    {
      "name": "Alice",
      "role": "Developer",
      "available_days": 10,
      "hours_per_day": 6,
      "allocation_percent": 100,
      "planned_pto_days": 0
    }
  ]
}
```

**Key outputs for sprint planning:**
- Per-member capacity breakdown
- Ceremony overhead calculation
- Focus-adjusted capacity (80% and 85%)
- Story point estimates based on historical velocity
- Warnings for low allocation or high PTO

### Combined Workflow

1. Run `velocity_analyzer.py` to understand team velocity trends
2. Prepare team data JSON with PTO and allocation for the sprint
3. Run `sprint_capacity_calculator.py` to get capacity numbers
4. Use both outputs to inform the sprint planning discussion
5. Document the sprint plan using `assets/sprint_plan_template.md`

---

## Quick Reference Card

### Sprint Planning Checklist (Day-Of)

```
BEFORE THE MEETING:
[ ] Velocity report generated (velocity_analyzer.py)
[ ] Capacity calculated (sprint_capacity_calculator.py)
[ ] Backlog groomed; top stories meet Definition of Ready
[ ] Product Owner has sprint goal prepared
[ ] Sprint board is clean (previous sprint closed)

DURING THE MEETING:
[ ] Sprint goal presented and understood by team
[ ] Capacity shared (hours and estimated points)
[ ] Stories selected up to forecast capacity
[ ] Stretch goals clearly labeled
[ ] Tasks broken down for each story
[ ] Sprint plan confirmed by the team

AFTER THE MEETING:
[ ] Sprint board updated with committed stories
[ ] Sprint goal posted visibly
[ ] Sprint plan template filled out
[ ] Calendar blocked for ceremonies
[ ] Stakeholders notified of sprint scope
```

---

*This guide provides a comprehensive framework for sprint planning. Adapt the practices to your team's maturity level, sprint length, and organizational context. The goal is continuous improvement in planning effectiveness, measured by commitment reliability and sprint goal achievement.*
