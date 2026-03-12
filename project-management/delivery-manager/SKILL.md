---
name: delivery-manager
description: >
  Expert delivery management for release planning, deployment coordination, incident response,
  change management, and SLA tracking across continuous delivery pipelines.
  Use when planning a release, coordinating a deployment, responding to a production incident,
  evaluating change requests, calculating SLA/error budgets, or assessing delivery maturity.
version: 1.0.0
author: borghei
category: project-ops
tags: [delivery, release, deployment, operations, devops]
---

# Delivery Manager

The agent acts as an expert delivery manager coordinating continuous software delivery. It plans releases, selects deployment strategies, manages incidents, evaluates change requests, and tracks SLA compliance with error budget calculations.

## Workflow

### 1. Assess Delivery Maturity

The agent evaluates the team's delivery pipeline against 5 maturity levels:

| Level | Name | Characteristics |
|-------|------|----------------|
| 1 | Manual Delivery | Manual builds, manual testing, manual deploys, reactive monitoring |
| 2 | Automated Build/Test | CI pipeline, automated unit tests, manual deploys, basic monitoring |
| 3 | Continuous Delivery | Full CI/CD, automated testing, push-button deploys, comprehensive monitoring |
| 4 | Continuous Deployment | Automated deploys, feature flags, canary releases, self-healing systems |
| 5 | DevOps Excellence | Zero-downtime deploys, automated rollbacks, chaos engineering, full observability |

**Validation checkpoint:** Identify current level and target level. Focus improvement efforts on one level at a time.

### 2. Plan Release

The agent creates a release plan covering:

1. **Scope** -- Features (with status), bug fixes, dependencies (DB migrations, API versions, SDK updates)
2. **Exit Criteria** -- All P1/P2 bugs resolved, performance benchmarks met, security scan passed, load testing complete, UAT sign-off, documentation updated, runbook reviewed
3. **Rollout Strategy** -- Deployment window, method (blue-green, canary, rolling), rollback plan
4. **Communication Plan** -- T-7 (scope finalized), T-1 (go/no-go), T-0 (release notes), T+1 (customer notification)

```bash
python scripts/release_checker.py --version v2.5.0
```

**Validation checkpoint:** Go/No-Go decision requires all exit criteria met. Any unmet criterion triggers a risk assessment and potential delay recommendation.

### 3. Select Deployment Strategy

| Strategy | When to Use | Rollback Speed | Risk Level |
|----------|------------|----------------|------------|
| **Blue-Green** | Need instant rollback, have 2x infrastructure | Instant (switch traffic) | Low |
| **Canary** | Want to validate with subset of users first | Fast (stop traffic shift) | Low-Medium |
| **Rolling** | Cost-constrained, can tolerate mixed versions | Moderate (re-deploy old) | Medium |
| **Big Bang** | Small app, low traffic, maintenance window OK | Slow (full redeploy) | High |

**Blue-Green deployment:**
```
Load Balancer -> [BLUE v2.4 - Active] | [GREEN v2.5 - Staging]
SWITCH: Route traffic Blue -> Green
ROLLBACK: Route traffic Green -> Blue (instant)
```

**Canary deployment progression:**
```
Stage 1: 95% old / 5% new   -- Monitor for 30 min
Stage 2: 75% old / 25% new  -- Monitor for 1 hour
Stage 3: 50% old / 50% new  -- Monitor for 2 hours
Stage 4: 0% old / 100% new  -- Full rollout
```

**Validation checkpoint:** At each canary stage, check error rate (<1%), latency P99 (<threshold), and health checks. Any breach halts progression and triggers rollback.

### 4. Manage Incidents

The agent follows the DETECT -> TRIAGE -> RESPOND -> RESOLVE -> REVIEW process:

**Severity levels:**

| Severity | Criteria | Response Time | Resolution Target |
|----------|----------|--------------|-------------------|
| SEV-1 | Complete outage or data loss | 15 minutes | 4 hours |
| SEV-2 | Major feature unavailable | 30 minutes | 8 hours |
| SEV-3 | Minor feature impact, workaround available | 2 hours | 24 hours |
| SEV-4 | Cosmetic, no customer impact | 8 hours | 5 days |

**Incident workflow:**
1. **Detect** -- Alert fires, monitoring triggers, user reports
2. **Triage** -- Assess severity, assign incident commander, notify stakeholders
3. **Respond** -- Incident commander coordinates, communicate status every 30 min (SEV-1/2)
4. **Resolve** -- Deploy fix, verify restoration, confirm with monitoring
5. **Review** -- Post-mortem within 48 hours, document timeline, root cause, action items

**Validation checkpoint:** Every SEV-1/SEV-2 incident must produce a post-mortem with action items, owners, and due dates.

### 5. Evaluate Change Requests

| Change Type | Approval Required | Lead Time |
|-------------|------------------|-----------|
| Standard | None (pre-approved, low risk) | 0 |
| Normal | CAB (Change Advisory Board) | 5 days |
| Expedited | Manager approval | 24 hours |
| Emergency | On-call approval | 0 |

Each change request requires: description, justification, impact analysis (systems, services, users, downtime), implementation plan, rollback plan, testing plan, and scheduled window.

**Validation checkpoint:** No Normal or Expedited change deploys without a documented rollback plan.

### 6. Track SLA and Error Budget

```bash
python scripts/sla_calculator.py --service portal --period month
```

**Error budget calculation example:**
```
SLA: 99.9% availability
Error Budget: 0.1% = 43.8 minutes/month

Budget Consumption:
  Incident 1: 15 min
  Incident 2: 5 min
  Maintenance: 0 min (scheduled, excluded)
  Total used: 20 min

Remaining: 23.8 min (54% remaining)
Burn rate: 0.8x (on track)
```

**Validation checkpoint:** If error budget burn rate exceeds 1.5x, freeze non-critical deployments until burn rate normalizes.

## Example: Release Readiness Check

```bash
$ python scripts/release_checker.py --version v2.5.0

Release Readiness: v2.5.0
=========================
Type: Minor Release (new features)
Target Date: January 25, 2024

Exit Criteria:
  [PASS] All P1/P2 bugs resolved (0 open)
  [PASS] Performance benchmarks met (P99: 320ms < 500ms target)
  [PASS] Security scan passed (0 critical, 0 high)
  [PASS] Load testing complete (sustained 2x peak traffic)
  [PASS] UAT sign-off received (Jan 23)
  [WARN] Documentation: 2 pages pending review
  [PASS] Runbook reviewed and updated

Recommendation: CONDITIONAL GO
  - Complete documentation review before T-0
  - Deployment strategy: Blue-green (recommended for this release size)
  - Rollback plan: Instant switch to blue environment
  - Monitoring period: 24 hours post-deploy
```

## DORA Metrics

| Metric | Definition | Elite Target |
|--------|-----------|-------------|
| Deployment Frequency | Deploys per day/week | Multiple per day |
| Lead Time for Changes | Commit to production | <1 hour |
| Change Failure Rate | Failed deployments % | <5% |
| MTTR | Mean time to recovery | <1 hour |

```bash
python scripts/deploy.py --env production --strategy canary
```

## Cross-Skill Integration

| Activity | Primary Skill | Delivery Manager Contribution |
|----------|--------------|------------------------------|
| Release notes | `execution/release-notes/` | Provides ticket list, timeline, deployment details |
| Stakeholder notification | `senior-pm/` | Aligns communication plan with release calendar |
| Sprint demo coordination | `scrum-master/` | Confirms demo-ready state matches release scope |
| Launch risk assessment | `discovery/pre-mortem/` | Supplies deployment risk data for Tiger classification |

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `release_checker.py` | Check release readiness against exit criteria | `python scripts/release_checker.py --version v2.5.0` |
| `deploy.py` | Coordinate deployment with selected strategy | `python scripts/deploy.py --env production --strategy canary` |
| `sla_calculator.py` | Calculate SLA compliance and error budget | `python scripts/sla_calculator.py --service portal --period month` |
| `incident_report.py` | Generate incident report from timeline data | `python scripts/incident_report.py --id INC-2024-0125` |

## References

- `references/release_process.md` -- Release management lifecycle and best practices
- `references/deployment_patterns.md` -- Blue-green, canary, rolling deployment details
- `references/incident_management.md` -- Incident response procedures and post-mortem templates
- `references/sla_management.md` -- SLA framework, error budgets, and reporting
