---
name: observability-designer
description: >
  Designs comprehensive observability strategies including SLI/SLO frameworks,
  alerting optimization, and dashboard generation. Use when implementing
  monitoring for a production service, creating or tuning alert rules,
  designing Grafana dashboards, defining SLOs and error budgets, or
  reducing alert fatigue in on-call rotations.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: observability
  tier: POWERFUL
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
