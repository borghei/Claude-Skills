# Release Process: Maturity, Planning, Change Management & DORA

Read this when assessing delivery maturity, building a release plan and exit criteria, evaluating change requests, or interpreting DORA metrics. Also contains the release-readiness worked example, the cross-skill integration map, the troubleshooting matrix, and success criteria — all moved verbatim from `SKILL.md`.

## 1. Assess Delivery Maturity

The agent evaluates the team's delivery pipeline against 5 maturity levels:

| Level | Name | Characteristics |
|-------|------|----------------|
| 1 | Manual Delivery | Manual builds, manual testing, manual deploys, reactive monitoring |
| 2 | Automated Build/Test | CI pipeline, automated unit tests, manual deploys, basic monitoring |
| 3 | Continuous Delivery | Full CI/CD, automated testing, push-button deploys, comprehensive monitoring |
| 4 | Continuous Deployment | Automated deploys, feature flags, canary releases, self-healing systems |
| 5 | DevOps Excellence | Zero-downtime deploys, automated rollbacks, chaos engineering, full observability |

**Validation checkpoint:** Identify current level and target level. Focus improvement efforts on one level at a time.

## 2. Plan Release

The agent creates a release plan covering:

1. **Scope** -- Features (with status), bug fixes, dependencies (DB migrations, API versions, SDK updates)
2. **Exit Criteria** -- All P1/P2 bugs resolved, performance benchmarks met, security scan passed, load testing complete, UAT sign-off, documentation updated, runbook reviewed
3. **Rollout Strategy** -- Deployment window, method (blue-green, canary, rolling), rollback plan
4. **Communication Plan** -- T-7 (scope finalized), T-1 (go/no-go), T-0 (release notes), T+1 (customer notification)

```bash
python scripts/release_checker.py --version v2.5.0
```

**Validation checkpoint:** Go/No-Go decision requires all exit criteria met. Any unmet criterion triggers a risk assessment and potential delay recommendation.

## 3. Evaluate Change Requests

| Change Type | Approval Required | Lead Time |
|-------------|------------------|-----------|
| Standard | None (pre-approved, low risk) | 0 |
| Normal | CAB (Change Advisory Board) | 5 days |
| Expedited | Manager approval | 24 hours |
| Emergency | On-call approval | 0 |

Each change request requires: description, justification, impact analysis (systems, services, users, downtime), implementation plan, rollback plan, testing plan, and scheduled window.

**Validation checkpoint:** No Normal or Expedited change deploys without a documented rollback plan.

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

DORA now defines five software delivery performance metrics, grouped as throughput and instability (as of September 2026, [dora.dev/guides/dora-metrics](https://dora.dev/guides/dora-metrics/)). The level values below are the 2024 report's cluster descriptions (2024 Accelerate State of DevOps Report, "Performance levels").

| Metric | Definition | Elite (2024) | High | Medium | Low |
|--------|-----------|--------------|------|--------|-----|
| Deployment Frequency | How often changes are deployed to production | On demand (multiple deploys per day) | Once per day to once per week | Once per week to once per month | Once per month to once every six months |
| Change Lead Time | Commit to version control to deployed in production | Less than one day | One day to one week | One week to one month | One month to six months |
| Change Fail Rate | Share of deployments that require immediate intervention | 5% | 20% | 10% | 40% |
| Failed Deployment Recovery Time (formerly MTTR) | Time to recover from a deployment that fails and needs immediate intervention | Less than one hour | Less than one day | Less than one day | One week to one month |
| Deployment Rework Rate | Share of deployments that are unplanned and made because of a production incident | No level benchmark published | | | |

Reading notes:

- The 2024 change fail rate values are not monotonic (High 20%, Medium 10%). `scripts/delivery_metrics_tracker.py` uses monotonic bands (5/10/20%) so a lower fail rate never scores worse, and treats recovery between one day and one week as Medium.
- "MTTR" is still common in tooling. The tracker reports `failed_deployment_recovery_time` and keeps `mttr` as a JSON alias.
- Rework rate is optional. Mark unplanned fix deploys with `"rework": true` in the input and the tracker reports the rate without classifying it.
- The 2025 DORA report ("State of AI-assisted Software Development") centres on seven team profiles from cluster analysis rather than leading with the Elite/High/Medium/Low levels, alongside the DORA AI Capabilities Model. Treat the 2024 levels as the latest published cut-offs, and use the profiles to diagnose *where* a team is constrained (throughput, instability, or well-being) rather than to rank teams.

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

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Canary deployment shows elevated errors but feature works in staging | Environment parity gap -- staging lacks production data volume, traffic patterns, or third-party integrations | Improve staging fidelity; use traffic shadowing before canary; define canary success thresholds based on production baselines, not staging |
| Release go/no-go keeps getting deferred | Exit criteria too rigid or too many items flagged as blockers at the last moment | Separate "must-have" from "nice-to-have" criteria upfront; run readiness checks at T-7 and T-3 to surface issues early |
| Incident post-mortems produce action items that never get implemented | Actions lack owners, due dates, or priority relative to feature work | Assign every action to a named owner with a calendar date; reserve sprint capacity for reliability work; track post-mortem actions in a dedicated Jira board |
| Error budget burns through in the first week of the month | Single large incident or multiple small incidents compounding | Implement burn-rate alerting at 50% and 75% thresholds; auto-freeze non-critical deployments when burn rate exceeds 1.5x |
| Change requests bypass the CAB process | Emergency change pathway overused; teams lack awareness of change types | Audit emergency changes monthly; retrain teams on change classification; add automation to flag changes missing required approvals |
| DORA metrics stagnate despite tooling investment | Measuring deployment frequency without addressing batch size, or measuring failed deployment recovery time (MTTR) without improving observability | Focus on leading indicators (batch size, test coverage, observability depth) before expecting DORA improvement |
| Rollback takes longer than expected | Rollback plan not tested; database migrations are not backward-compatible | Require rollback rehearsal for every major release; enforce backward-compatible migration policy; blue-green with instant switch as default strategy |

## Success Criteria

- Change failure rate stays below 5% measured over a rolling 30-day window
- Failed deployment recovery time (formerly MTTR) for SEV-1/SEV-2 incidents is under 1 hour
- 100% of SEV-1/SEV-2 incidents produce a post-mortem with action items within 48 hours
- Error budget consumption stays below 80% in any given month
- Release cadence meets or exceeds the target deployment frequency (weekly or better)
- Zero deployments proceed without a documented rollback plan
- DORA metrics show quarter-over-quarter improvement across all four classified measures, with rework rate trending down where tracked
