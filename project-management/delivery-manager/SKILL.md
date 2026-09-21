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
| `delivery_metrics_tracker.py` | DORA metrics vs 2024 levels (deployment frequency, change lead time, change fail rate, failed deployment recovery time) plus optional rework rate | `python scripts/delivery_metrics_tracker.py --data delivery.json --period 30` |

## References

- `references/release_process.md` -- Delivery maturity levels, release planning + exit criteria, change-request types, the release-readiness example, DORA metrics, cross-skill integration, troubleshooting, and success criteria. Read when planning a release or improving the pipeline.
- `references/deployment_patterns.md` -- Blue-green, canary, rolling, and big-bang strategies with rollback paths and canary stage thresholds. Read when selecting how to ship.
- `references/incident_management.md` -- Severity matrix (SEV-1–SEV-4), the 5-step incident workflow, and post-mortem requirements. Read during incident triage and response.
- `references/sla_management.md` -- SLA framework, error-budget calculation example, and burn-rate freeze thresholds. Read when tracking reliability budgets.
- `references/red-flags.md` -- Bad-vs-good examples of delivery-management output. Read this to review a release/incident plan before committing to it.

## AI-Assisted Delivery

AI coding assistants change the shape of the delivery pipeline: more code arrives faster, and the constraint moves to review, testing, and recovery. What DORA's research says (as of September 2026):

- **2024 report:** every 25% increase in AI adoption was associated with an estimated 1.5% reduction in delivery throughput and 7.2% reduction in delivery stability, even as documentation quality, code quality, and review speed improved ([2024 report](https://dora.dev/research/2024/dora-report/)).
- **2025 report ("State of AI-assisted Software Development"):** 90% of respondents use AI at work and more than 80% believe it has raised their productivity, while 30% report little or no trust in AI-generated code. AI adoption now shows a positive relationship with throughput but still a negative one with stability. DORA's framing is that AI is an amplifier of an organization's existing strengths and weaknesses ([announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)).
- **DORA AI Capabilities Model** (2025): seven capabilities that amplify AI's benefit: clear and communicated AI stance, healthy data ecosystems, AI-accessible internal data, strong version control practices, working in small batches, user-centric focus, and quality internal platforms ([dora.dev](https://dora.dev/ai/capabilities-model/report/)).
- **Team profiles:** the 2025 report groups teams into seven profiles (for example "foundational challenges", "legacy bottleneck", "harmonious high achievers") rather than leading with the Elite-to-Low levels. Use the profile to find the constraint before rolling out more AI tooling.

What to do as a delivery manager:

1. **Track instability, not just speed.** Report change fail rate and deployment rework rate (`delivery_metrics_tracker.py`, `"rework": true` on unplanned fix deploys) next to deployment frequency. Rising throughput with rising rework is the AI failure mode DORA describes.
2. **Measure review load.** PR count per reviewer, review wait time, and PR size. AI-generated volume that outruns review capacity shows up as longer lead time or weaker review, not as faster delivery.
3. **Keep batches small.** Hold PR size and release scope limits regardless of how fast code is produced; small batches are both a DORA capability and the main guard against AI-driven instability.
4. **Guard stability explicitly.** Canary or feature-flag every AI-heavy change set, keep rollback rehearsed, and treat a rising rework rate as a trigger to slow intake, not to add more AI.
5. **Keep a human accountable.** Every change, AI-assisted or not, has a named human owner who meets the same Definition of Done and review bar.

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
