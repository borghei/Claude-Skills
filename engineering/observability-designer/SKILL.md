---
name: observability-designer
description: >
  Design observability strategies: SLI/SLO frameworks, alerting, and dashboards. Use when
  instrumenting a production service, tuning alert rules, designing Grafana dashboards,
  defining SLOs and error budgets, or reducing alert fatigue.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: observability
  tier: POWERFUL
  updated: 2026-06-17
---
# Observability Designer

Design production-ready observability strategies that combine the three pillars (metrics, logs, traces) with SLI/SLO frameworks, golden-signals monitoring, multi-window burn-rate alerting, and alert-noise optimization.

## Core Capabilities

- **SLI/SLO frameworks** — select SLIs from the golden signals, map them to Prometheus expressions, set SLO targets by criticality tier, and compute error budgets.
- **Burn-rate alerting** — multi-window burn-rate rules with severity routing, hysteresis, suppression, and grouping to keep alert noise below 10%.
- **Dashboard design** — Grafana specs following the Overview > Service > Component > Instance hierarchy, ≤7 panels per screen, role-based views (SRE/Dev/Exec/Ops).
- **Structured logging & tracing** — JSON log format with correlation IDs, log-level discipline, and head/tail/adaptive trace sampling strategies.
- **Runbooks & validation** — runbook template per critical alert; coverage validation that every T1 service has metrics, logs, traces, and a runbook.
- **Cost optimization** — metric/log/trace retention tiers and cardinality management.

## When to Use

- Instrumenting a new or existing production service.
- Defining SLOs and error budgets for a service tier.
- Tuning alert rules or reducing alert fatigue / alert storms.
- Designing Grafana dashboards or role-based views.
- Choosing a trace sampling strategy or structured log schema.

## Clarify First

Before designing the observability strategy, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Service type & criticality tier** — api / pipeline / storage / ML and T1–T3 (sets SLO targets, error-budget math, and `slo_designer` flags)
- [ ] **User-facing vs internal** — determines which golden signals become SLIs and how alert severity is routed
- [ ] **Primary pain: alert noise vs coverage gaps** — decides whether to optimize existing alerts or design new burn-rate rules
- [ ] **Dashboard audience** — SRE / Dev / Exec / Ops sets the role-based panel layout and hierarchy

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `slo_designer.py` | Generate SLI/SLO framework, error budgets, and burn-rate alerts from a service definition | `python scripts/slo_designer.py --service-type api --criticality high --user-facing true` |
| `alert_optimizer.py` | Analyze alert configs for noise, coverage gaps, and duplicates; emit an optimization report | `python scripts/alert_optimizer.py --input alerts.json --analyze-only` |
| `dashboard_generator.py` | Produce Grafana-compatible dashboard JSON with golden signals and role-based views | `python scripts/dashboard_generator.py --service-type api --name "Payment Service"` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/slo-and-alerting.md](references/slo-and-alerting.md)** — the 8-step workflow, SLI/SLO quick reference, error-budget math, burn-rate alert windows, alert classification, alert-fatigue prevention, and golden signals. Read when designing SLOs or alerts.
- **[references/dashboards-logs-traces.md](references/dashboards-logs-traces.md)** — dashboard design rules, structured log format, trace sampling strategies, the runbook template, a complete worked payment-service spec, and cost optimization. Read when building dashboards, logs, traces, or runbooks.
- **[references/tools-integration-and-troubleshooting.md](references/tools-integration-and-troubleshooting.md)** — full per-script flag/output reference, the systems integration table (Prometheus/Grafana/Jaeger/PagerDuty), the troubleshooting table, and success-criteria targets. Read when running the scripts or diagnosing failures.
- **[references/slo_cookbook.md](references/slo_cookbook.md)** — a practical, in-depth cookbook for defining and operating Service Level Objectives. Read when you need detailed SLO methodology beyond the quick reference.
- **[references/alert_design_patterns.md](references/alert_design_patterns.md)** — a deep guide to effective alerting patterns and anti-patterns. Read when designing a complete alerting strategy.
- **[references/dashboard_best_practices.md](references/dashboard_best_practices.md)** — comprehensive dashboard design-for-insight best practices. Read when building a dashboard system from scratch.

## Scope & Limitations

**Covers:**
- SLI/SLO framework design for request-driven, pipeline, storage, and ML services.
- Multi-window burn-rate alert generation and alert noise optimization.
- Grafana-compatible dashboard specification with role-based layouts (SRE, Developer, Executive, Ops).
- Structured logging format, trace sampling strategy selection, and cost-optimization guidance.

**Does NOT cover:**
- Infrastructure provisioning or Terraform/Helm configuration for Prometheus, Grafana, or Jaeger -- see `ci-cd-pipeline-builder` for deployment pipelines.
- Incident response workflow orchestration or post-mortem facilitation -- see `runbook-generator` for runbook authoring.
- Application Performance Management (APM) agent installation or vendor-specific SDK integration.
- Security monitoring, SIEM rule design, or compliance audit logging -- see `skill-security-auditor` for security-focused analysis.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `runbook-generator` | Every burn-rate alert references a runbook; the runbook generator consumes alert definitions to scaffold investigation steps | Alert YAML --> runbook-generator --> Markdown runbook linked in alert annotations |
| `ci-cd-pipeline-builder` | Deployment events feed into dashboard annotations and alert suppression windows | Pipeline events --> Grafana annotations + Alertmanager silences |
| `performance-profiler` | Latency SLI breaches trigger profiling; profiler results inform SLO target adjustments | SLO burn-rate alert --> profiler invocation --> refined latency thresholds |
| `database-designer` | Database SLIs (query latency, connection success rate, replication lag) align with schema-level health checks | DB schema metadata --> SLI metric expressions for database-type services |
| `tech-debt-tracker` | Error budget depletion signals feed into tech debt prioritization as reliability investments | Error budget reports --> tech debt backlog items with SLO-linked severity |
| `release-manager` | Release readiness gates check remaining error budget before approving deployments | Error budget API --> release gate pass/fail decision |
