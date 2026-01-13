---
name: project-manager
description: Expert project management covering planning, execution, stakeholder management, risk mitigation, and delivery excellence.
version: 1.0.0
author: Claude Skills
category: project-ops
tags: [project-management, planning, execution, stakeholders, delivery]
---

# Project Manager

Expert-level project management for successful delivery.

## Core Competencies

- Project planning
- Scope management
- Timeline and scheduling
- Resource management
- Risk management
- Stakeholder communication
- Budget management
- Team leadership

## Project Planning

### Project Charter Template

```markdown
# Project Charter: [Project Name]

## Project Overview
- Name: [Project Name]
- Sponsor: [Name]
- Project Manager: [Name]
- Start Date: [Date]
- Target End Date: [Date]

## Business Case
[Why are we doing this project?]

## Objectives
1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

## Scope

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1]
- [Item 2]

## Success Criteria
- [Criterion 1]: [Measure]
- [Criterion 2]: [Measure]

## Key Stakeholders
| Name | Role | Interest | Influence |
|------|------|----------|-----------|
| [Name] | [Role] | [H/M/L] | [H/M/L] |

## High-Level Timeline
| Phase | Start | End | Key Deliverables |
|-------|-------|-----|------------------|
| Initiation | [Date] | [Date] | Charter, team |
| Planning | [Date] | [Date] | Plan, WBS |
| Execution | [Date] | [Date] | Deliverables |
| Closure | [Date] | [Date] | Handoff, lessons |

## Budget
- Estimated: $[X]
- Contingency: [X]%

## Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk] | H/M/L | H/M/L | [Action] |

## Approvals
| Name | Role | Signature | Date |
|------|------|-----------|------|
| | | | |
```

### Work Breakdown Structure

```
PROJECT
├── Phase 1: Discovery
│   ├── 1.1 Requirements gathering
│   │   ├── 1.1.1 Stakeholder interviews
│   │   └── 1.1.2 Requirements documentation
│   └── 1.2 Technical assessment
│       ├── 1.2.1 Architecture review
│       └── 1.2.2 Integration analysis
├── Phase 2: Design
│   ├── 2.1 Solution design
│   └── 2.2 Design review
├── Phase 3: Build
│   ├── 3.1 Development
│   ├── 3.2 Testing
│   └── 3.3 Documentation
├── Phase 4: Deploy
│   ├── 4.1 Deployment preparation
│   ├── 4.2 Go-live
│   └── 4.3 Hypercare
└── Phase 5: Close
    ├── 5.1 Handoff
    └── 5.2 Lessons learned
```

## Schedule Management

### Gantt Chart Structure

```
Task                    | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 |
------------------------|----|----|----|----|----|----|----|----|
Phase 1: Discovery      |████|████|    |    |    |    |    |    |
  Requirements          |████|    |    |    |    |    |    |    |
  Technical assessment  |    |████|    |    |    |    |    |    |
Phase 2: Design         |    |████|████|    |    |    |    |    |
  Solution design       |    |████|    |    |    |    |    |    |
  Design review         |    |    |████|    |    |    |    |    |
Phase 3: Build          |    |    |    |████|████|████|    |    |
  Development           |    |    |    |████|████|    |    |    |
  Testing               |    |    |    |    |████|████|    |    |
Phase 4: Deploy         |    |    |    |    |    |    |████|    |
Phase 5: Close          |    |    |    |    |    |    |    |████|
```

### Critical Path

```
START → [A:5d] → [B:3d] → [C:4d] → [E:2d] → END
              ↘ [D:2d] ↗

Critical Path: A → B → C → E (14 days)
Float on D: 2 days
```

### Meeting Cadence

| Meeting | Frequency | Duration | Attendees | Purpose |
|---------|-----------|----------|-----------|---------|
| Daily Standup | Daily | 15 min | Team | Status, blockers |
| Weekly Status | Weekly | 30 min | Team + PM | Progress review |
| Steering | Bi-weekly | 60 min | Sponsors | Decisions, escalations |
| Retrospective | End of phase | 60 min | Team | Improvements |

## Risk Management

### Risk Register

| ID | Risk | Category | Probability | Impact | Score | Owner | Mitigation | Status |
|----|------|----------|-------------|--------|-------|-------|------------|--------|
| R1 | [Description] | Technical | H/M/L | H/M/L | [1-25] | [Name] | [Action] | Open |

### Risk Matrix

```
              │ Low Impact │ Medium │ High Impact
──────────────┼────────────┼────────┼────────────
High Prob     │ Medium     │ High   │ Critical
Medium Prob   │ Low        │ Medium │ High
Low Prob      │ Low        │ Low    │ Medium
```

### Risk Response Strategies

**Threats:**
- Avoid: Eliminate the threat
- Mitigate: Reduce probability or impact
- Transfer: Shift to third party
- Accept: Acknowledge and monitor

**Opportunities:**
- Exploit: Ensure it happens
- Enhance: Increase probability
- Share: Partner with others
- Accept: Take advantage if it occurs

## Status Reporting

### Status Report Template

```markdown
# Project Status Report
## [Project Name] - [Date]

### Overall Status: 🟢 Green / 🟡 Yellow / 🔴 Red

### Executive Summary
[2-3 sentences on overall progress]

### Key Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Schedule | On time | +2 days | 🟡 |
| Budget | $100K | $95K | 🟢 |
| Scope | 100% | 90% | 🟢 |
| Quality | 95% pass | 97% | 🟢 |

### Accomplishments This Period
- [Accomplishment 1]
- [Accomplishment 2]

### Planned Next Period
- [Plan 1]
- [Plan 2]

### Issues
| Issue | Impact | Owner | Target Date | Status |
|-------|--------|-------|-------------|--------|
| [Issue] | [Impact] | [Name] | [Date] | Open |

### Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk] | [H/M/L] | [H/M/L] | [Action] |

### Decisions Needed
- [Decision 1]: [Options]

### Budget Summary
- Approved: $[X]
- Spent: $[Y]
- Remaining: $[Z]
- Forecast: $[W]
```

## Stakeholder Management

### RACI Matrix

| Activity | PM | Sponsor | Tech Lead | Team |
|----------|-----|---------|-----------|------|
| Requirements | A | C | R | I |
| Design | A | I | R | C |
| Development | A | I | C | R |
| Testing | A | I | C | R |
| Go-Live | R | A | C | I |

**R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed

### Communication Plan

| Stakeholder | Information | Frequency | Method | Owner |
|-------------|-------------|-----------|--------|-------|
| Sponsor | Status, Decisions | Weekly | Email, Meeting | PM |
| Team | Tasks, Blockers | Daily | Standup | PM |
| Users | Progress, Training | Bi-weekly | Newsletter | PM |

## Change Management

### Change Request Template

```markdown
# Change Request: [CR-XXX]

## Request Details
- Submitted by: [Name]
- Date: [Date]
- Priority: High/Medium/Low

## Change Description
[What is being requested?]

## Business Justification
[Why is this change needed?]

## Impact Analysis
- Schedule: [Impact]
- Budget: [Impact]
- Scope: [Impact]
- Resources: [Impact]

## Options
1. [Option 1]: [Pros/Cons]
2. [Option 2]: [Pros/Cons]
3. [Option 3]: [Pros/Cons]

## Recommendation
[Recommended approach]

## Approval
| Role | Name | Decision | Date |
|------|------|----------|------|
| PM | | | |
| Sponsor | | | |
```

## Reference Materials

- `references/planning.md` - Planning templates
- `references/risk_management.md` - Risk frameworks
- `references/communication.md` - Communication templates
- `references/agile_pm.md` - Agile project management

## Scripts

```bash
# Project timeline generator
python scripts/timeline_gen.py --wbs wbs.yaml --output gantt.html

# Risk analyzer
python scripts/risk_analyzer.py --register risks.csv

# Status report generator
python scripts/status_report.py --project "Project Name" --period weekly

# Resource planner
python scripts/resource_plan.py --team team.yaml --tasks tasks.csv
```
