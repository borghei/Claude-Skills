---
name: observability-designer
description: >
  Design observability strategies: SLI/SLO frameworks, alerting, and dashboards. Use when
  instrumenting a production service, tuning alert rules, designing Grafana dashboards,
  defining SLOs and error budgets, or reducing alert fatigue.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: observability
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - observability
    - slo
    - alerting
    - dashboards
    - monitoring
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

Before designing the observability strategy, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Service type & criticality tier:** api / pipeline / storage / ML and T1–T3 (sets SLO targets, error-budget math, and `slo_designer` flags).
- **User-facing vs internal:** determines which golden signals become SLIs and how alert severity is routed.
- **Primary pain: alert noise vs coverage gaps:** decides whether to optimize existing alerts or design new burn-rate rules.
- **Dashboard audience:** SRE / Dev / Exec / Ops sets the role-based panel layout and hierarchy.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Command |
|------|---------|---------|
| `slo_designer.py` | Generate SLI/SLO framework, error budgets, and burn-rate alerts from a service definition | `python scripts/slo_designer.py --service-type api --criticality high --user-facing true` |
| `alert_optimizer.py` | Analyze alert configs for noise, coverage gaps, and duplicates; emit an optimization report | `python scripts/alert_optimizer.py --input alerts.json --analyze-only` |
| `dashboard_generator.py` | Produce Grafana-compatible dashboard JSON with golden signals and role-based views | `python scripts/dashboard_generator.py --service-type api --name "Payment Service"` |

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/slo-and-alerting.md](references/slo-and-alerting.md)** — the 8-step workflow, SLI/SLO quick reference, error-budget math, burn-rate alert windows, alert classification, alert-fatigue prevention, and golden signals. Read when designing SLOs or alerts.
- **[references/dashboards-logs-traces.md](references/dashboards-logs-traces.md)** — dashboard design rules, structured log format, trace sampling strategies, the runbook template, a complete worked payment-service spec, and cost optimization. Read when building dashboards, logs, traces, or runbooks.
- **[references/tools-integration-and-troubleshooting.md](references/tools-integration-and-troubleshooting.md)** — full per-script flag/output reference, the systems integration table (Prometheus/Grafana/Jaeger/PagerDuty), the troubleshooting table, and success-criteria targets. Read when running the scripts or diagnosing failures.
- **[references/slo_cookbook.md](references/slo_cookbook.md)** — a practical, in-depth cookbook for defining and operating Service Level Objectives. Read when you need detailed SLO methodology beyond the quick reference.
- **[references/alert_design_patterns.md](references/alert_design_patterns.md)** — a deep guide to effective alerting patterns and anti-patterns. Read when designing a complete alerting strategy.
- **[references/dashboard_best_practices.md](references/dashboard_best_practices.md)** — comprehensive dashboard design-for-insight best practices. Read when building a dashboard system from scratch.

## Anti-Patterns

**Mistake:** Alerting on causes (CPU, memory, a single pod) instead of symptoms.
**Why it matters:** Cause alerts page people for things users never notice and stay quiet when users are hurting.
**Instead:** Page on SLO burn rate (multi-window), and keep cause metrics on dashboards for diagnosis.

**Mistake:** SLO targets copied from another service or set at 100%.
**Why it matters:** A target with no error budget blocks every release, and an unmeasured target is ignored.
**Instead:** Start from current measured performance, agree the target with the service owner, and review it after a quarter.

**Mistake:** Shipping generated dashboards and alerts without review.
**Why it matters:** Metric names, labels and thresholds are templates; a wrong label silently matches nothing.
**Instead:** Load them in staging, confirm every panel shows data, and fire each alert once on purpose.

## Files

| File | Purpose |
|------|---------|
| `scripts/slo_designer.py`, `scripts/alert_optimizer.py`, `scripts/dashboard_generator.py` | Stdlib CLIs; exit 0 on success, 2 on unusable input |
| `assets/sample_service_api.json`, `assets/sample_service_web.json` | Service definitions for the SLO designer and dashboard generator |
| `assets/sample_alerts.json` | Ten alert rules with noise and duplication for the optimizer |

The dashboard generator emits Grafana JSON with `schemaVersion` 30; current Grafana versions migrate older schema versions on import, so check the result in your Grafana before committing it.

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
