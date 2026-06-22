---
name: delivery-manager
description: >
  Expert delivery management for release planning, deployment strategy, incident
  response, change management, SLA/error-budget tracking, and DORA metrics across
  continuous delivery pipelines.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-ops
  domain: delivery
  updated: 2026-06-15
  tags: [delivery, release, deployment, operations, devops]
---
# Delivery Manager

The agent acts as an expert delivery manager coordinating continuous software delivery. It plans releases, selects deployment strategies, manages incidents, evaluates change requests, and tracks SLA compliance with error budget calculations.

## Core Capabilities

- **Delivery maturity assessment** — locate the team on a 5-level scale (Manual → DevOps Excellence) and target one level at a time.
- **Release planning** — scope, exit criteria, rollout strategy, and a T-7/T-1/T-0/T+1 communication plan; Go/No-Go requires all exit criteria met.
- **Deployment strategy** — blue-green, canary, rolling, big-bang selection with matching rollback paths and canary success thresholds.
- **Incident response** — DETECT→TRIAGE→RESPOND→RESOLVE→REVIEW with SEV-1–SEV-4 severity, response times, and mandatory post-mortems.
- **Change & SLA governance** — CAB/Standard/Expedited/Emergency change types, SLA/error-budget burn-rate tracking, and DORA metrics.

## When to Use

- Planning a release and running a Go/No-Go against exit criteria
- Choosing a deployment strategy and its rollback plan
- Responding to a production incident or running a post-mortem
- Evaluating a change request or calculating SLA/error-budget burn
- Assessing delivery maturity or interpreting DORA metrics

## Clarify First

Before generating the plan or report, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which task** — release readiness/Go-No-Go, deployment strategy, incident response, or SLA/error-budget tracking (each is a different workflow and artifact)
- [ ] **Exit criteria or SLA target** — the bar the release or service is measured against (Go/No-Go requires all criteria met; SLA math needs the target)
- [ ] **Deployment strategy** — blue-green, canary, rolling, or big-bang, when shipping (sets the rollout gates and rollback path)
- [ ] **Incident severity** — SEV-1 through SEV-4, when responding (sets response time, escalation, and whether a post-mortem is mandatory)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/release_checker.py --version v2.5.0            # release readiness vs exit criteria
python scripts/deploy.py --env production --strategy canary    # coordinate a deployment
python scripts/sla_calculator.py --service portal --period month  # SLA + error budget
python scripts/incident_report.py --id INC-2024-0125           # incident report from timeline
```

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `release_checker.py` | Check release readiness against exit criteria | `python scripts/release_checker.py --version v2.5.0` |
| `deploy.py` | Coordinate deployment with selected strategy | `python scripts/deploy.py --env production --strategy canary` |
| `sla_calculator.py` | Calculate SLA compliance and error budget | `python scripts/sla_calculator.py --service portal --period month` |
| `incident_report.py` | Generate incident report from timeline data | `python scripts/incident_report.py --id INC-2024-0125` |

## References

- `references/release_process.md` -- Delivery maturity levels, release planning + exit criteria, change-request types, the release-readiness example, DORA metrics, cross-skill integration, troubleshooting, and success criteria. Read when planning a release or improving the pipeline.
- `references/deployment_patterns.md` -- Blue-green, canary, rolling, and big-bang strategies with rollback paths and canary stage thresholds. Read when selecting how to ship.
- `references/incident_management.md` -- Severity matrix (SEV-1–SEV-4), the 5-step incident workflow, and post-mortem requirements. Read during incident triage and response.
- `references/sla_management.md` -- SLA framework, error-budget calculation example, and burn-rate freeze thresholds. Read when tracking reliability budgets.
- `references/red-flags.md` -- Bad-vs-good examples of delivery-management output. Read this to review a release/incident plan before committing to it.

## Scope & Limitations

**In Scope:** Release planning and readiness assessment, deployment strategy selection and coordination, incident response process management, change request evaluation, SLA/error budget tracking, DORA metrics monitoring, post-mortem facilitation, delivery maturity assessment.

**Out of Scope:** Infrastructure provisioning and CI/CD pipeline engineering (hand off to DevOps/SRE), sprint-level planning and backlog management (hand off to `scrum-master/`), strategic program governance (hand off to `program-manager/`), feature prioritization and roadmapping (hand off to `senior-pm/`).

**Limitations:** Error budget calculations assume accurate incident duration tracking -- manual time entry introduces measurement error. Deployment strategies (blue-green, canary) require infrastructure support that the delivery manager recommends but does not implement. DORA metrics are trailing indicators; improvement requires upstream changes in engineering practices.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `scrum-master/` | SM -> DM | Sprint completion data, demo-ready confirmation, velocity for release sizing |
| `senior-pm/` | PM -> DM | Release calendar, stakeholder communication requirements |
| `program-manager/` | PgM -> DM | Cross-project release dependencies, milestone alignment |
| `jira-expert/` | Bidirectional | Release version tracking in Jira; deployment status field updates |
| `agile-coach/` | Coach -> DM | Delivery maturity assessment inputs, DevOps culture recommendations |
| `confluence-expert/` | DM -> Confluence | Post-mortem documentation, runbook maintenance, release notes publishing |
