---
name: scrum-master
description: Expert Scrum mastery covering sprint facilitation, team coaching, impediment removal, and agile transformation.
version: 1.0.0
author: Claude Skills
category: project-ops
tags: [scrum, agile, sprint, facilitation, coaching]
---

# Scrum Master

Expert-level Scrum facilitation and agile coaching.

## Core Competencies

- Sprint facilitation
- Team coaching
- Impediment removal
- Stakeholder management
- Agile metrics
- Continuous improvement
- Conflict resolution
- Process optimization

## Scrum Framework

### Sprint Structure

```
SPRINT (2 weeks typical)
├── Sprint Planning (Day 1)
├── Daily Scrum (Daily, 15 min)
├── Development Work (Days 1-9)
├── Sprint Review (Day 10)
└── Sprint Retrospective (Day 10)

ARTIFACTS
├── Product Backlog
├── Sprint Backlog
└── Increment
```

### Sprint Planning

```markdown
# Sprint Planning: Sprint [Number]

## Sprint Goal
[One sentence describing the sprint objective]

## Capacity
| Team Member | Availability | Story Points |
|-------------|--------------|--------------|
| [Name] | 80% | [Points] |
| [Name] | 100% | [Points] |
| Total | | [Points] |

## Selected Stories
| ID | Story | Points | Owner |
|----|-------|--------|-------|
| [ID] | [Story] | [Points] | [Name] |

## Sprint Backlog
Total Points: [X]
Capacity: [Y]
Buffer: [Z]%

## Dependencies
- [Dependency 1]
- [Dependency 2]

## Risks
- [Risk 1]
- [Risk 2]
```

### Daily Scrum Format

```
EACH TEAM MEMBER (2 min max):

1. What did I complete since last standup?
2. What will I work on today?
3. Are there any blockers?

FACILITATION TIPS:
- Start on time, end on time
- Stand up (creates urgency)
- Park detailed discussions
- Update the sprint board
- Note impediments for follow-up
```

## Sprint Review

### Review Agenda

```
SPRINT REVIEW (1 hour)

1. WELCOME (5 min)
   - Sprint goal recap
   - Attendee introductions

2. DEMO (30 min)
   - Completed features
   - Working software only
   - User-focused narrative

3. DISCUSSION (15 min)
   - Stakeholder feedback
   - Questions and answers
   - Clarifications

4. BACKLOG UPDATE (10 min)
   - Next sprint preview
   - Priority discussions
   - Roadmap context
```

### Demo Best Practices

**Do:**
- Demo working software
- Use real data when possible
- Tell a user story
- Involve the whole team
- Capture feedback

**Don't:**
- Demo incomplete work
- Read from slides
- Show technical details
- Go over time
- Get defensive about feedback

## Sprint Retrospective

### Retrospective Formats

**Start, Stop, Continue:**
```
START: What should we start doing?
STOP: What should we stop doing?
CONTINUE: What should we keep doing?
```

**Mad, Sad, Glad:**
```
MAD: What frustrated us?
SAD: What disappointed us?
GLAD: What made us happy?
```

**4Ls:**
```
LIKED: What did we like?
LEARNED: What did we learn?
LACKED: What did we lack?
LONGED FOR: What did we wish we had?
```

### Retrospective Template

```markdown
# Sprint [X] Retrospective

## What Went Well
- [Item 1]
- [Item 2]

## What Didn't Go Well
- [Item 1]
- [Item 2]

## Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
| [Action] | [Name] | [Date] |

## Metrics This Sprint
- Velocity: [Points]
- Sprint Goal: [Achieved/Partial/Missed]
- Bugs Found: [Count]
- Team Happiness: [1-5]

## Previous Action Items Status
| Action | Status |
|--------|--------|
| [Action] | [Done/In Progress/Carried] |
```

## Agile Metrics

### Velocity Tracking

```
┌─────────────────────────────────────────────────────────────┐
│                    Velocity Trend                            │
├─────────────────────────────────────────────────────────────┤
│  45 │                              ██                       │
│  40 │                    ██        ██  ██                   │
│  35 │          ██  ██    ██  ██    ██  ██  ██              │
│  30 │    ██    ██  ██    ██  ██    ██  ██  ██              │
│  25 │    ██    ██  ██    ██  ██    ██  ██  ██              │
│  20 │    ██    ██  ██    ██  ██    ██  ██  ██              │
│     └──────────────────────────────────────────────────────│
│       S1   S2   S3   S4   S5   S6   S7   S8   S9           │
│                                                              │
│  Average Velocity: 35 points                                │
│  Trend: Stable                                               │
└─────────────────────────────────────────────────────────────┘
```

### Sprint Health Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│               Sprint [X] Health Dashboard                    │
├─────────────────────────────────────────────────────────────┤
│  Burndown              │  Velocity               │  Quality  │
│  ████████░░ On Track   │  38 pts (avg: 35)      │  2 bugs   │
│  5 days remaining      │  +9% vs last sprint    │  0 P1     │
├─────────────────────────────────────────────────────────────┤
│  Sprint Goal: 🟢 On Track                                    │
│                                                              │
│  Stories: 8/12 Complete                                      │
│  Points: 25/38 Complete                                      │
├─────────────────────────────────────────────────────────────┤
│  Team Mood: 😊 Good                                          │
│  Blockers: 1 (being addressed)                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Metrics

| Metric | What It Measures | Target |
|--------|------------------|--------|
| Velocity | Work completed per sprint | Stable trend |
| Sprint Burndown | Progress within sprint | Steady decline |
| Sprint Goal Success | Goals achieved | 80%+ |
| Cycle Time | Time from start to done | Decreasing |
| Escaped Defects | Bugs found post-sprint | <5% |

## Impediment Management

### Impediment Log

```markdown
# Impediment Log

| ID | Description | Impact | Status | Owner | Resolution |
|----|-------------|--------|--------|-------|------------|
| I-1 | [Description] | [H/M/L] | Open | [Name] | [Action] |
| I-2 | [Description] | [H/M/L] | Resolved | [Name] | [How] |

## Escalation Path
1. Scrum Master attempts resolution
2. Escalate to Product Owner (if product-related)
3. Escalate to Engineering Manager (if resource-related)
4. Escalate to Leadership (if organizational)
```

### Resolution Strategies

**Technical Impediments:**
- Pair programming
- Technical spike
- Expert consultation
- Tool/process change

**People Impediments:**
- One-on-one conversation
- Conflict mediation
- Role clarification
- Workload adjustment

**Process Impediments:**
- Process review
- Simplification
- Automation
- Training

## Team Coaching

### Team Health Check

| Dimension | Score | Action |
|-----------|-------|--------|
| Collaboration | 1-5 | [Action if needed] |
| Communication | 1-5 | [Action if needed] |
| Technical Skills | 1-5 | [Action if needed] |
| Process Adherence | 1-5 | [Action if needed] |
| Psychological Safety | 1-5 | [Action if needed] |

### Coaching Conversations

```
SITUATION: [What's happening]
BEHAVIOR: [What you observed]
IMPACT: [Effect on team/project]
ALTERNATIVE: [What could be done differently]
COMMITMENT: [What will change]
```

## Reference Materials

- `references/scrum_guide.md` - Scrum framework reference
- `references/facilitation.md` - Meeting facilitation techniques
- `references/metrics.md` - Agile metrics guide
- `references/coaching.md` - Team coaching strategies

## Scripts

```bash
# Sprint report generator
python scripts/sprint_report.py --sprint 15

# Velocity calculator
python scripts/velocity.py --team "Team Alpha" --sprints 10

# Retrospective action tracker
python scripts/retro_tracker.py --team "Team Alpha"

# Health check survey
python scripts/health_check.py --team "Team Alpha" --send
```
