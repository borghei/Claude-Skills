---
name: observability-designer
description: >
  Designs comprehensive observability strategies including SLI/SLO frameworks,
  alerting optimization, and dashboard generation. Use when implementing
  monitoring for a production service, creating or tuning alert rules, designing
  Grafana dashboards, defining SLOs and error budgets, or reducing alert fatigue
  in on-call rotations.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: observability
  tier: POWERFUL
  updated: 2026-03-31
---
# Observability Designer

The agent designs production-ready observability strategies that combine the three pillars (metrics, logs, traces) with SLI/SLO frameworks, golden signals monitoring, and alert optimization.

## Workflow

1. **Catalogue services** -- List every service in scope with its type (request-driven, pipeline, storage), criticality tier (T1-T3), and owning team. Validate that at least one T1 service exists before proceeding.
2. **Define SLIs per service** -- For each service, select SLIs from the Golden Signals table. Map each SLI to a concrete Prometheus/InfluxDB metric expression.
3. **Set SLO targets** -- Assign SLO targets based on criticality tier and user expectations. Calculate the corresponding error budget (e.g., 99.9% = 43.8 min/month).
4. **Design burn-rate alerts** -- Create multi-window burn-rate alert rules for each SLO. Validate that every alert has a clear runbook link and response action.
5. **Build dashboards** -- Generate dashboard specs following the hierarchy: Overview > Service > Component > Instance. Cap each screen at 7 panels. Include SLO target reference lines.
6. **Configure log aggregation** -- Define structured log format, set log levels, assign correlation IDs, and configure retention policies per tier.
7. **Instrument traces** -- Set up distributed tracing with sampling strategy (head-based for dev, tail-based for production). Define span boundaries at service and database call points.
8. **Validate coverage** -- Confirm every T1 service has metrics, logs, and traces. Confirm every alert has a runbook. Confirm dashboard load time is under 2 seconds.

## SLI/SLO Quick Reference

| SLI Type | Metric Expression (Prometheus) | Typical SLO |
|----------|-------------------------------|-------------|
| Availability | `1 - (sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])))` | 99.9% |
| Latency (P99) | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` | < 500ms |
| Error rate | `sum(rate(grpc_server_handled_total{grpc_code!="OK"}[5m])) / sum(rate(grpc_server_handled_total[5m]))` | < 0.1% |
| Throughput | `sum(rate(http_requests_total[5m]))` | > baseline |

## Error Budget Calculation

```
Error Budget = 1 - SLO target

Example (99.9% availability):
  Monthly budget = 30d x 24h x 60m x 0.001 = 43.2 minutes
  If 20 minutes consumed, remaining = 23.2 minutes (53.7% left)
```

## Burn-Rate Alert Design

| Window | Burn Rate | Severity | Budget Consumed |
|--------|-----------|----------|-----------------|
| 5 min / 1 hr | 14.4x | Critical (page) | 2% in 1 hour |
| 30 min / 6 hr | 6x | Warning (ticket) | 5% in 6 hours |
| 2 hr / 3 day | 1x | Info (dashboard) | 10% in 3 days |

**Rule**: Every critical alert must have an actionable runbook. If no clear action exists, downgrade to warning.

## Alert Classification

| Severity | Meaning | Response | Routing |
|----------|---------|----------|---------|
| Critical | Service down or SLO burn rate high | Page on-call immediately | PagerDuty escalation |
| Warning | Approaching threshold, non-user-facing | Create ticket, fix in business hours | Slack channel |
| Info | Deployment notification, capacity trend | Review in next standup | Dashboard only |

## Alert Fatigue Prevention

- **Hysteresis**: Set different thresholds for firing (e.g., > 90% CPU for 5 min) and resolving (e.g., < 80% CPU for 10 min).
- **Suppression**: Suppress dependent alerts during known outages (e.g., suppress pod alerts when node is down).
- **Grouping**: Group related alerts into a single notification (e.g., all pods in one deployment).
- **Precision over recall**: A missed alert that would self-resolve is better than 50 false pages per week.

## Golden Signals

| Signal | What to Monitor | Key Metrics |
|--------|----------------|-------------|
| Latency | Request duration | P50, P95, P99 response time; queue wait; DB query time |
| Traffic | Request volume | RPS with burst detection; active sessions; bandwidth |
| Errors | Failure rate | 4xx/5xx rates; error budget consumption; silent failures |
| Saturation | Resource pressure | CPU/memory/disk utilization; queue depth; connection pool usage |

## Dashboard Design Rules

- **Hierarchy**: Overview (all services) > Service (one service) > Component (e.g., database) > Instance
- **Panel limit**: Maximum 7 panels per screen to manage cognitive load
- **Reference lines**: Always show SLO targets and capacity thresholds
- **Time defaults**: 4 hours for incident investigation, 7 days for trend analysis
- **Role-based views**: SRE (operational), Developer (debug), Executive (reliability summary)

## Structured Log Format

```json
{
  "timestamp": "2025-11-05T14:30:00Z",
  "level": "ERROR",
  "service": "payment-api",
  "trace_id": "abc123def456",
  "span_id": "789ghi",
  "message": "Payment processing failed",
  "error_code": "PAYMENT_TIMEOUT",
  "duration_ms": 5023,
  "customer_id": "cust_42",
  "environment": "production"
}
```

**Log levels**: DEBUG (local dev only), INFO (request lifecycle), WARN (degraded but functional), ERROR (failed operation), FATAL (service cannot continue).

## Trace Sampling Strategies

| Strategy | When to Use | Trade-off |
|----------|------------|-----------|
| Head-based (10%) | Development, low-traffic services | Misses rare errors |
| Tail-based | Production, high-traffic | Captures errors/slow requests; higher resource cost |
| Adaptive | Variable traffic patterns | Adjusts rate based on load; more complex to configure |

## Runbook Template

```markdown
# Alert: [Alert Name]

## What It Means
[One sentence explaining the alert condition]

## Impact
[User-facing vs internal; affected services]

## Investigation Steps
1. Check dashboard: [link]  (1 min)
2. Review recent deploys: [link]  (2 min)
3. Check dependent services: [list]  (2 min)
4. Review logs: [query]  (3 min)

## Resolution Actions
- If [condition A]: [action]
- If [condition B]: [action]
- If unclear: Escalate to [team] via [channel]

## Post-Incident
- [ ] Update incident timeline
- [ ] File post-mortem if > 5 min user impact
```

## Example: E-Commerce Payment Service Observability

```yaml
service: payment-api
tier: T1 (revenue-critical)
owner: payments-team

slis:
  availability:
    metric: "1 - rate(http_5xx) / rate(http_total)"
    slo: 99.95%
    error_budget: 21.6 min/month
  latency_p99:
    metric: "histogram_quantile(0.99, http_duration_seconds)"
    slo: < 800ms
  error_rate:
    metric: "rate(payment_failures) / rate(payment_attempts)"
    slo: < 0.5%

alerts:
  - name: PaymentHighErrorRate
    expr: "rate(payment_failures[5m]) / rate(payment_attempts[5m]) > 0.01"
    for: 2m
    severity: critical
    runbook: "https://wiki.internal/runbooks/payment-errors"

dashboard_panels:
  - Payment success rate (gauge)
  - Transaction volume (time series)
  - P50/P95/P99 latency (time series)
  - Error breakdown by type (stacked bar)
  - Downstream dependency health (status map)
  - Error budget remaining (gauge)
```

## Cost Optimization

- **Metric retention**: 15-day full resolution, 90-day downsampled, 1-year aggregated
- **Log sampling**: Sample DEBUG/INFO at 10% in high-throughput services; always keep ERROR/FATAL at 100%
- **Trace sampling**: Tail-based sampling retains only errors and slow requests (> P99)
- **Cardinality management**: Alert on any metric with > 10K unique label combinations

## Scripts

### SLO Designer (`slo_designer.py`)
Generates SLI/SLO frameworks from service description JSON. Outputs SLI definitions, SLO targets, error budgets, burn-rate alerts, and SLA recommendations.

### Alert Optimizer (`alert_optimizer.py`)
Analyzes existing alert configurations for noise, coverage gaps, and duplicate rules. Outputs an optimization report with improved thresholds.

### Dashboard Generator (`dashboard_generator.py`)
Creates Grafana-compatible dashboard JSON from service/system descriptions. Covers golden signals, RED/USE methods, and role-based views.

## Integration Points

| System | Integration |
|--------|------------|
| Prometheus | Metric collection and alerting rules |
| Grafana | Dashboard creation and visualization |
| Elasticsearch/Kibana | Log analysis and search |
| Jaeger/Zipkin | Distributed tracing |
| PagerDuty/VictorOps | Alert routing and escalation |
| Slack/Teams | Notification delivery |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Burn-rate alerts never fire | SLO target set too low or error budget too generous for actual traffic | Tighten SLO target incrementally (e.g., 99.5% to 99.9%) and verify metric expressions return non-zero values using `rate()` over a short window |
| Alert storm during deployments | No suppression rules for planned rollouts; alerts lack hysteresis | Add deployment-aware silence windows in Alertmanager and configure `for:` clauses of at least 2-5 minutes on all alerts |
| Dashboard panels show "No Data" | Metric names or label selectors do not match what the exporter publishes | Run `curl localhost:9090/api/v1/label/__name__/values` to list available metrics and cross-check label filters in panel queries |
| High cardinality causing Prometheus OOM | Unbounded labels (user ID, request ID) on metrics | Remove high-cardinality labels from instrumentation; use `metric_relabel_configs` to drop offending series and set a cardinality alert at 10K unique combinations |
| Error budget drains faster than expected | SLI numerator counts partial failures (e.g., retried requests counted twice) | Ensure good/total event counters use the same request scope; deduplicate at the instrumentation layer, not the query layer |
| Trace sampling misses critical errors | Head-based sampling drops error spans at the same rate as success spans | Switch to tail-based sampling in production so 100% of error and slow spans are retained regardless of base sample rate |
| Runbooks go stale after service changes | No ownership or review cadence tied to alerts | Link each alert YAML to a runbook file in version control; add a CI check that fails if an alert references a missing or outdated runbook |

## Success Criteria

- Alert noise ratio below 10% -- fewer than 1 in 10 pages should be false positives or non-actionable.
- SLO compliance above 99.5% across all Tier-1 services measured over a rolling 30-day window.
- Mean time to detect (MTTD) under 5 minutes for Tier-1 service degradations via burn-rate alerts.
- Every critical alert has an associated runbook that was reviewed within the last 90 days.
- Dashboard load time under 2 seconds with default time range for all role-based views.
- Trace coverage spans 100% of Tier-1 service boundaries with tail-based sampling retaining all error and P99+ latency spans.
- Error budget consumption is reviewed weekly by the owning team with documented decisions on whether to freeze or proceed with deployments.

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

## Tool Reference

### SLO Designer (`scripts/slo_designer.py`)

**Purpose:** Generates complete SLI/SLO frameworks from service definitions, including SLI metric expressions, SLO targets, error budgets, multi-window burn-rate alerts, and SLA recommendations.

**Usage:**
```bash
python slo_designer.py --input service_definition.json --output slo_framework.json
python slo_designer.py --service-type api --criticality high --user-facing true
python slo_designer.py --service-type web --criticality critical --user-facing true --summary-only
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | No* | Input service definition JSON file |
| `--output` | `-o` | No | Output framework JSON file (defaults to `{service_name}_slo_framework.json`) |
| `--service-type` | -- | No* | Service type: `api`, `web`, `database`, `queue`, `batch`, `ml` |
| `--criticality` | -- | No* | Service criticality level: `critical`, `high`, `medium`, `low` |
| `--user-facing` | -- | No* | Whether service is user-facing: `true`, `false` |
| `--service-name` | -- | No | Service name (defaults to `{service_type}_service`) |
| `--summary-only` | -- | No | Only display summary, do not save JSON |

*Either `--input` or all three of `--service-type`, `--criticality`, and `--user-facing` are required.

**Example:**
```bash
python slo_designer.py --service-type api --criticality high --user-facing true --service-name payment-api --output payment_slo.json
```

**Output Formats:** JSON file containing `metadata`, `slis`, `slos`, `error_budgets`, `sla_recommendations`, `monitoring_recommendations`, and `implementation_guide`. Also prints a human-readable summary to stdout.

---

### Alert Optimizer (`scripts/alert_optimizer.py`)

**Purpose:** Analyzes existing alert configurations to identify noisy alerts, coverage gaps, duplicate rules, poor thresholds, missing runbooks, and routing issues. Generates an optimization report and optionally an improved configuration.

**Usage:**
```bash
python alert_optimizer.py --input alerts.json --analyze-only
python alert_optimizer.py --input alerts.json --output optimized_alerts.json
python alert_optimizer.py --input alerts.json --report report.html --format html
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input alert configuration JSON file |
| `--output` | `-o` | No | Output optimized configuration JSON file (defaults to `optimized_alerts.json`) |
| `--report` | `-r` | No | Generate analysis report to specified file path |
| `--format` | -- | No | Report format: `json` (default), `html` |
| `--analyze-only` | -- | No | Only perform analysis, do not generate optimized config |

**Example:**
```bash
python alert_optimizer.py --input prod_alerts.json --analyze-only --report analysis.json --format json
```

**Output Formats:** JSON or HTML report containing noise analysis (scored alerts with reasons and recommendations), coverage gap analysis (missing categories and golden signals), duplicate detection (exact and semantic duplicates), and optimization recommendations. When not using `--analyze-only`, also outputs a rewritten alert configuration file.

---

### Dashboard Generator (`scripts/dashboard_generator.py`)

**Purpose:** Creates Grafana-compatible dashboard JSON specifications from service definitions. Covers golden signals, RED/USE methods, role-based views (SRE, Developer, Executive, Ops), and drill-down paths for troubleshooting workflows.

**Usage:**
```bash
python dashboard_generator.py --input service_definition.json --output dashboard_spec.json
python dashboard_generator.py --service-type api --name "Payment Service" --output payment_dashboard.json
python dashboard_generator.py --service-type web --name "Frontend" --role developer --format grafana
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | No* | Input service definition JSON file |
| `--output` | `-o` | No | Output dashboard specification file (defaults to `{service_name}_dashboard.json`) |
| `--service-type` | -- | No* | Service type: `api`, `web`, `database`, `queue`, `batch`, `ml` |
| `--name` | -- | No* | Service name |
| `--criticality` | -- | No | Service criticality level: `critical`, `high`, `medium` (default), `low` |
| `--role` | -- | No | Target role for dashboard optimization: `sre` (default), `developer`, `executive`, `ops` |
| `--format` | -- | No | Output format: `json` (default), `grafana` |
| `--doc-output` | -- | No | Generate documentation file at specified path |
| `--summary-only` | -- | No | Only display summary, do not save files |

*Either `--input` or both `--service-type` and `--name` are required.

**Example:**
```bash
python dashboard_generator.py --service-type database --name "orders-db" --criticality high --role sre --format grafana --output orders_db_dashboard.json
```

**Output Formats:** JSON specification or Grafana-compatible JSON containing `metadata`, `configuration`, `layout`, `panels` (with Prometheus query expressions, visualization types, grid positions), `variables`, `alerts_integration`, and `drill_down_paths`. Optionally generates a Markdown documentation file via `--doc-output`.
