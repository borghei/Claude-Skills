---
name: delivery-manager
description: >
  Plans releases, picks deployment strategies, runs incidents and tracks DORA metrics
  and error budgets. Use when preparing a Go/No-Go, choosing canary or blue-green,
  handling a production incident or reporting delivery health.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-ops
  domain: delivery
  updated: 2026-11-08
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

Before generating the plan or report, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which task:** release readiness/Go-No-Go, deployment strategy, incident response, or SLA/error-budget tracking (each is a different workflow and artifact).
- **Exit criteria or SLA target:** the bar the release or service is measured against (Go/No-Go requires all criteria met; SLA math needs the target).
- **Deployment strategy:** blue-green, canary, rolling, or big-bang, when shipping (sets the rollout gates and rollback path).
- **Incident severity:** SEV-1 through SEV-4, when responding (sets response time, escalation, and whether a post-mortem is mandatory).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. Settle the Clarify First inputs; each task maps to one reference below.
2. Measure first: run the matching tool on the team's own export (deployments, dependencies or risks).
3. Build the artifact from the reference (release plan, rollout and rollback, incident timeline, budget burn).
4. Done when Go/No-Go checks every exit criterion against evidence, every rollback path has a rehearsal date, and every DORA figure shows its sample size.

## Tools

Each tool reads one JSON file and prints a text report (`--json` for machine output).
`--example` prints the input shape; samples ship in `assets/`. Exit 0 on success, 2 on bad
input (missing file, invalid JSON, wrong shape) with a one-line error.

```bash
python3 project-management/delivery-manager/scripts/delivery_metrics_tracker.py --data project-management/delivery-manager/assets/sample_delivery.json --period 30
python3 project-management/delivery-manager/scripts/dependency_mapper.py --deps project-management/delivery-manager/assets/sample_dependencies.json
python3 project-management/delivery-manager/scripts/risk_register.py --risks project-management/delivery-manager/assets/sample_risks.json
```

| Tool | What it does |
|------|--------------|
| `delivery_metrics_tracker.py` | Deployment frequency, change lead time, change fail rate and failed-deployment recovery time against the 2024 DORA levels, plus rework rate when deploys carry `"rework": true`. The `--period` window ends at the file's `as_of`, else its latest deploy or incident, so a fixed export gives a fixed answer. A tier needs a minimum sample: 5 deploys for lead time and change fail rate (below that one failure moves the rate by 20+ points), 2 incidents for recovery time, and 5 deploys or a 28+ day window for frequency. Below it the metric reads "Insufficient data" and is left out of the overall level; with none classified, the overall level is "Insufficient data" too |
| `dependency_mapper.py` | Delivery order (each dependency before what needs it), cycles, bottlenecks, high-risk and unowned dependencies. Edges are `{"from": dependent, "to": dependency}` |
| `risk_register.py` | Probability x impact scores, severity, residual exposure after mitigation, unowned high risks |

## Anti-Patterns

### Rollback plan never rehearsed
**Mistake:** The release plan documents a rollback procedure that has never been run in production-like conditions.
**Why it happens:** Writing the steps feels like enough, and rehearsal takes time from the release.
**Instead:** Rehearse the rollback at least every 90 days and measure how long it takes. If it hasn't been rehearsed, treat the rollback path as theoretical in the Go/No-Go.

### Error budget that never bites
**Mistake:** The team has SLOs and an error budget but keeps shipping features when the budget is burned.
**Why it happens:** Roadmap pressure wins the argument every time the budget runs out.
**Instead:** Agree the consequence before the budget burns: feature freeze until reliability work restores it. Track burn rate with the SLA/error-budget workflow. If feature work has never paused for a burned budget, the budget is decoration.

### Severity that doesn't match the criteria
**Mistake:** Minor issues get logged as SEV-1, or real outages stay at SEV-3 to avoid the paperwork.
**Why it happens:** Severity drives response time and post-mortem duty, so people bend it up or down.
**Instead:** Classify against the documented SEV-1 to SEV-4 criteria. Sample 10 recent SEV-1s. If fewer than 80% meet the criteria, fix the classification before you trust the dashboard.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

- `references/release_process.md` -- Delivery maturity levels, release planning + exit criteria, change-request types, the release-readiness example, DORA metrics, cross-skill integration, troubleshooting, and success criteria. Read when planning a release or improving the pipeline.
- `references/deployment_patterns.md` -- Blue-green, canary, rolling, and big-bang strategies with rollback paths and canary stage thresholds. Read when selecting how to ship.
- `references/incident_management.md` -- Severity matrix (SEV-1–SEV-4), the 5-step incident workflow, and post-mortem requirements. Read during incident triage and response.
- `references/sla_management.md` -- SLA framework, error-budget calculation example, and burn-rate freeze thresholds. Read when tracking reliability budgets.
- `references/red-flags.md` -- Bad-vs-good examples of delivery-management output. Read this to review a release/incident plan before committing to it.
- `references/ai-assisted-delivery.md` -- What DORA's 2024 and 2025 research says about AI assistants and delivery stability, and what to track. Read when AI tooling is changing throughput or review load.

## Scope & Limitations

**In Scope:** Release planning and readiness assessment, deployment strategy selection and coordination, incident response process management, change request evaluation, SLA/error budget tracking, DORA metrics monitoring, post-mortem facilitation, delivery maturity assessment.

**Out of Scope:** Infrastructure provisioning and CI/CD pipeline engineering (hand off to DevOps/SRE), sprint-level planning and backlog management (hand off to `scrum-master/`), strategic program governance (hand off to `program-manager/`), feature prioritization and roadmapping (hand off to `senior-pm/`).

**Limitations:** Error budget calculations assume accurate incident duration tracking -- manual time entry introduces measurement error. Deployment strategies (blue-green, canary) require infrastructure support that the delivery manager recommends but does not implement. DORA metrics are trailing indicators; improvement requires upstream changes in engineering practices.

## Files

| File | Purpose |
|------|---------|
| `scripts/delivery_metrics_tracker.py`, `scripts/dependency_mapper.py`, `scripts/risk_register.py` | See Tools |
| `assets/sample_delivery.json`, `assets/sample_dependencies.json`, `assets/sample_risks.json` | Runnable inputs for each tool |
| `references/*.md` | See References |
