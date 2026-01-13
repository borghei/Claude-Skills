---
name: delivery-manager
description: Expert delivery management covering continuous delivery, release management, deployment coordination, and service operations.
version: 1.0.0
author: Claude Skills
category: project-ops
tags: [delivery, release, deployment, operations, devops]
---

# Delivery Manager

Expert-level delivery management for continuous software delivery.

## Core Competencies

- Release management
- Deployment coordination
- Continuous delivery
- Service operations
- Incident management
- Change management
- Capacity planning
- SLA management

## Delivery Framework

### Delivery Pipeline

```
CODE → BUILD → TEST → STAGE → DEPLOY → MONITOR
  │       │       │       │        │        │
  ▼       ▼       ▼       ▼        ▼        ▼
Commit  Compile  Unit   Integr   Prod    Observe
Review  Package  Integr  UAT     Canary   Alert
Lint    Artifact Perf   Approval Blue/Grn Respond
```

### Delivery Maturity Model

```
LEVEL 1: Manual Delivery
├── Manual builds
├── Manual testing
├── Manual deployments
└── Reactive monitoring

LEVEL 2: Automated Build/Test
├── CI pipeline
├── Automated unit tests
├── Manual deployments
└── Basic monitoring

LEVEL 3: Continuous Delivery
├── Full CI/CD pipeline
├── Automated testing
├── Push-button deployments
└── Comprehensive monitoring

LEVEL 4: Continuous Deployment
├── Automated deployments
├── Feature flags
├── Canary releases
└── Self-healing systems

LEVEL 5: DevOps Excellence
├── Zero-downtime deployments
├── Automated rollbacks
├── Chaos engineering
└── Full observability
```

## Release Management

### Release Planning

```markdown
# Release Plan: v2.5.0

## Release Overview
- Version: 2.5.0
- Type: Minor Release (new features)
- Target Date: January 25, 2024
- Release Manager: [Name]

## Scope

### Features
| ID | Feature | Owner | Status |
|----|---------|-------|--------|
| F-101 | New checkout flow | Team A | Ready |
| F-102 | Performance improvements | Team B | Ready |
| F-103 | Admin dashboard updates | Team C | In Testing |

### Bug Fixes
| ID | Description | Priority | Status |
|----|-------------|----------|--------|
| B-201 | Cart total calculation | High | Fixed |
| B-202 | Login timeout issue | Medium | Fixed |

### Dependencies
- Database migration required
- API version update
- Third-party SDK update

## Release Criteria

### Exit Criteria
- [ ] All P1/P2 bugs resolved
- [ ] Performance benchmarks met
- [ ] Security scan passed
- [ ] Load testing complete
- [ ] UAT sign-off received
- [ ] Documentation updated
- [ ] Runbook reviewed

### Go/No-Go Decision
- Decision date: January 24, 2024
- Decision maker: Release Manager + Product Owner
- Criteria: All exit criteria met

## Rollout Strategy
- Deployment window: January 25, 10:00-14:00 UTC
- Method: Blue-green deployment
- Rollback plan: Immediate switch to blue environment

## Communication Plan
| When | Who | What |
|------|-----|------|
| T-7 days | Internal teams | Release scope finalized |
| T-1 day | All stakeholders | Go/No-Go decision |
| T-0 | Customer success | Release notes |
| T+1 day | Customers | Changelog email |

## Post-Release
- Monitoring period: 24 hours
- Success metrics: Error rate <0.1%, latency P99 <500ms
- Retrospective: January 26, 2024
```

### Release Calendar

```
RELEASE CALENDAR - Q1 2024

January
  Week 1    Week 2    Week 3    Week 4
  ─────────────────────────────────────
  Code      Testing   UAT       Release
  Freeze    Phase     Phase     v2.5.0
  v2.5                          ◆

February
  Week 1    Week 2    Week 3    Week 4
  ─────────────────────────────────────
  Dev       Code      Testing   Release
  Sprint    Freeze    Phase     v2.6.0
            v2.6                ◆

RELEASE TYPES
◆ Major Release (quarterly)
● Minor Release (monthly)
○ Patch Release (as needed)
```

### Version Management

```
SEMANTIC VERSIONING: MAJOR.MINOR.PATCH

MAJOR (X.0.0)
├── Breaking changes
├── Major features
└── Quarterly cadence

MINOR (x.X.0)
├── New features
├── Backward compatible
└── Monthly cadence

PATCH (x.x.X)
├── Bug fixes
├── Security patches
└── As needed
```

## Deployment Strategies

### Deployment Patterns

**Blue-Green Deployment:**
```
┌─────────────────────────────────────────────────┐
│                  LOAD BALANCER                   │
└─────────────────────┬───────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│  BLUE (v2.4)  │           │ GREEN (v2.5)  │
│   [Active]    │           │  [Staging]    │
│               │           │               │
│ ● ● ● ● ●     │           │ ● ● ● ● ●     │
│  5 instances  │           │  5 instances  │
└───────────────┘           └───────────────┘

SWITCH: Route traffic from Blue → Green
ROLLBACK: Route traffic from Green → Blue
```

**Canary Deployment:**
```
┌─────────────────────────────────────────────────┐
│               TRAFFIC DISTRIBUTION               │
├─────────────────────────────────────────────────┤
│                                                  │
│  Stage 1:  [█████████████████████████░] 95%/5%  │
│  Stage 2:  [████████████████████░░░░░░] 75%/25% │
│  Stage 3:  [██████████░░░░░░░░░░░░░░░░] 50%/50% │
│  Stage 4:  [░░░░░░░░░░░░░░░░░░░░░░░░░█] 0%/100% │
│                                                  │
│  ████ = Old Version    ░░░░ = New Version       │
└─────────────────────────────────────────────────┘
```

**Rolling Deployment:**
```
TIME →
────────────────────────────────────────────────────
t0:  [v1][v1][v1][v1][v1]  All instances v1
t1:  [v2][v1][v1][v1][v1]  1 instance updated
t2:  [v2][v2][v1][v1][v1]  2 instances updated
t3:  [v2][v2][v2][v1][v1]  3 instances updated
t4:  [v2][v2][v2][v2][v1]  4 instances updated
t5:  [v2][v2][v2][v2][v2]  All instances v2
```

### Deployment Checklist

```markdown
# Deployment Checklist

## Pre-Deployment
- [ ] All tests passing
- [ ] Security scan complete
- [ ] Change request approved
- [ ] Runbook reviewed
- [ ] Rollback plan documented
- [ ] Communication sent
- [ ] On-call team notified
- [ ] Maintenance window confirmed

## Deployment
- [ ] Database backup complete
- [ ] Configuration verified
- [ ] Health checks configured
- [ ] Deployment initiated
- [ ] Progress monitored
- [ ] Health checks passing
- [ ] Smoke tests passing

## Post-Deployment
- [ ] All services healthy
- [ ] Metrics within thresholds
- [ ] No increase in errors
- [ ] User acceptance verified
- [ ] Documentation updated
- [ ] Stakeholders notified
- [ ] Change request closed

## Rollback Triggers
- Error rate > 1%
- Latency P99 > 2s
- Health check failures
- Critical bug discovered
```

## Incident Management

### Incident Response

```
INCIDENT SEVERITY LEVELS

SEV-1: Critical
├── Complete service outage
├── Data loss or security breach
├── Response: Immediate (15 min)
└── Resolution target: 4 hours

SEV-2: High
├── Major feature unavailable
├── Significant performance degradation
├── Response: 30 minutes
└── Resolution target: 8 hours

SEV-3: Medium
├── Minor feature impact
├── Workaround available
├── Response: 2 hours
└── Resolution target: 24 hours

SEV-4: Low
├── Cosmetic issues
├── No customer impact
├── Response: 8 hours
└── Resolution target: 5 days
```

### Incident Process

```
DETECT → TRIAGE → RESPOND → RESOLVE → REVIEW
   │        │         │         │         │
   ▼        ▼         ▼         ▼         ▼
Alert    Assess    Incident   Fix &    Post-
Fire     Severity  Commander  Verify   mortem
Monitor  Assign    Coordinate Deploy   Action
Page     Notify    Communicate Test    Items
```

### Incident Template

```markdown
# Incident Report: INC-2024-0125

## Summary
[One sentence description of the incident]

## Timeline
| Time (UTC) | Event |
|------------|-------|
| 10:15 | Alert triggered |
| 10:18 | On-call paged |
| 10:25 | Incident declared |
| 10:45 | Root cause identified |
| 11:00 | Fix deployed |
| 11:15 | Service restored |

## Impact
- Duration: 1 hour
- Affected services: [List]
- Customer impact: [Description]
- SLA impact: [Yes/No, details]

## Root Cause
[Description of what caused the incident]

## Resolution
[What was done to resolve the incident]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action 1] | [Name] | [Date] | Open |
| [Action 2] | [Name] | [Date] | Open |

## Lessons Learned
- What went well: [List]
- What could improve: [List]
- Follow-up items: [List]
```

## Change Management

### Change Types

| Type | Description | Approval | Lead Time |
|------|-------------|----------|-----------|
| Standard | Pre-approved, low risk | None | 0 |
| Normal | Regular change | CAB | 5 days |
| Expedited | Urgent business need | Manager | 24 hours |
| Emergency | Critical fix | On-call | 0 |

### Change Request

```markdown
# Change Request: CHG-2024-0150

## Change Details
- Title: Database schema migration
- Type: Normal
- Risk: Medium
- Environment: Production

## Requestor
- Name: [Name]
- Team: [Team]
- Date: January 20, 2024

## Description
[Detailed description of the change]

## Justification
[Business reason for the change]

## Impact Analysis
- Systems affected: [List]
- Services affected: [List]
- Users affected: [Number]
- Downtime required: [Duration]

## Implementation Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Rollback Plan
1. [Rollback step 1]
2. [Rollback step 2]

## Testing Plan
- [ ] Unit tests
- [ ] Integration tests
- [ ] UAT sign-off

## Schedule
- Proposed date: January 25, 2024
- Start time: 02:00 UTC
- Duration: 2 hours
- Change freeze exception: No

## Approvals
| Role | Name | Status | Date |
|------|------|--------|------|
| Technical Lead | | Pending | |
| Product Owner | | Pending | |
| CAB | | Pending | |
```

## SLA Management

### SLA Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                        SLA DASHBOARD                             │
├─────────────────────────────────────────────────────────────────┤
│  Service: Customer Portal     Period: January 2024              │
├─────────────────────────────────────────────────────────────────┤
│  AVAILABILITY                                                    │
│  Target: 99.9%    Actual: 99.95%    Status: ✓ Met              │
│  Downtime allowed: 43.8 min    Used: 21.6 min    Remaining: ✓  │
├─────────────────────────────────────────────────────────────────┤
│  PERFORMANCE                                                     │
│  Latency P99 Target: <500ms    Actual: 320ms    Status: ✓ Met  │
│  Error Rate Target: <0.1%      Actual: 0.05%    Status: ✓ Met  │
├─────────────────────────────────────────────────────────────────┤
│  SUPPORT                                                         │
│  SEV-1 Response Target: 15 min    Avg: 12 min    Status: ✓ Met │
│  SEV-2 Response Target: 30 min    Avg: 25 min    Status: ✓ Met │
└─────────────────────────────────────────────────────────────────┘
```

### Error Budget

```
ERROR BUDGET CALCULATION

SLA: 99.9% availability
Error Budget: 0.1% = 43.8 minutes/month

BUDGET CONSUMPTION
├── Incident 1: 15 min
├── Incident 2: 5 min
├── Maintenance: 0 min (scheduled)
└── Total used: 20 min

REMAINING BUDGET
└── 23.8 min (54% remaining)

BURN RATE
└── Current: 0.8x (on track)
```

## Metrics & Reporting

### Delivery Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Deployment Frequency | Deploys per day/week | 10+/week |
| Lead Time | Commit to production | <1 day |
| Change Failure Rate | Failed deployments | <5% |
| MTTR | Mean time to recovery | <1 hour |
| Availability | Uptime percentage | 99.9% |

### Delivery Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              DELIVERY PERFORMANCE - [Month]                      │
├─────────────────────────────────────────────────────────────────┤
│  Deployments     Lead Time      Failure Rate      MTTR          │
│  48              4.2 hours      2.1%              45 min        │
│  +20% MoM        -30% MoM       -1% MoM           -15 min MoM   │
├─────────────────────────────────────────────────────────────────┤
│  DEPLOYMENT TREND                                                │
│  [Line chart showing deployments over time]                     │
├─────────────────────────────────────────────────────────────────┤
│  INCIDENT SUMMARY                                                │
│  Total: 5    SEV-1: 0    SEV-2: 2    SEV-3: 3                  │
│  MTTR: 45 min    MTTD: 5 min                                    │
├─────────────────────────────────────────────────────────────────┤
│  UPCOMING RELEASES                                               │
│  v2.6.0: Feb 28    v2.7.0: Mar 28    v3.0.0: Apr 30            │
└─────────────────────────────────────────────────────────────────┘
```

## Reference Materials

- `references/release_process.md` - Release management guide
- `references/deployment_patterns.md` - Deployment strategies
- `references/incident_management.md` - Incident response
- `references/sla_management.md` - SLA framework

## Scripts

```bash
# Release readiness checker
python scripts/release_checker.py --version v2.5.0

# Deployment coordinator
python scripts/deploy.py --env production --strategy canary

# SLA calculator
python scripts/sla_calculator.py --service portal --period month

# Incident reporter
python scripts/incident_report.py --id INC-2024-0125
```
