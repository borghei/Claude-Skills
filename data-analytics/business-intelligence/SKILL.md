---
name: business-intelligence
description: >
  Expert business intelligence covering dashboard design, data visualization,
  reporting automation, and executive insights delivery. Use when designing
  dashboards, building KPI frameworks, automating scheduled reports, creating
  data stories for stakeholders, or optimizing BI tool performance.
version: 1.0.0
author: borghei
category: data-analytics
tags: [bi, dashboards, visualization, reporting, insights]
---

# Business Intelligence

The agent operates as a senior BI specialist, designing dashboards, defining KPI frameworks, automating reporting pipelines, and translating data into executive-ready narratives.

## Workflow

1. **Clarify the reporting need** -- Identify the audience (executive, operational, self-service), the key questions the dashboard must answer, and the refresh cadence. Validate that required data sources exist and are accessible.
2. **Define KPIs and metrics** -- For each metric, specify the formula, data source, granularity, owner, and RAG thresholds using the KPI definition template below.
3. **Design the dashboard layout** -- Apply the visual hierarchy (most important metric top-left, summary-to-detail flow top-to-bottom). Select chart types using the chart selection matrix. Limit to 5-8 visualizations per page.
4. **Build the semantic layer** -- Define metric calculations, hierarchies, and row-level security in the BI tool's semantic model so consumers get consistent numbers.
5. **Automate reporting** -- Configure scheduled delivery (PDF/email, Slack alerts) and threshold-based alerts with the patterns below.
6. **Validate and iterate** -- Confirm KPI values match source-of-truth queries. Check dashboard load time (<5 s target). Gather stakeholder feedback and refine.

## KPI Definition Template

```yaml
# Copy and fill for each metric
kpi:
  name: "Monthly Recurring Revenue"
  owner: "Finance"
  purpose: "Track subscription revenue health"
  formula: "SUM(subscription_amount) WHERE status = 'active'"
  data_source: "billing.subscriptions"
  granularity: "monthly"
  target: 1200000
  warning_threshold: 1080000   # 90% of target
  critical_threshold: 960000   # 80% of target
  dimensions: ["region", "plan_tier", "cohort_month"]
  caveats:
    - "Excludes one-time setup fees"
    - "Currency normalized to USD at month-end rate"
```

## Dashboard Design Principles

**Visual hierarchy:**
1. Most important metrics at top-left
2. Summary cards flow into trend charts flow into detail tables (top to bottom)
3. Related metrics grouped; white space separates logical sections
4. RAG status colors: Green `#28A745` | Yellow `#FFC107` | Red `#DC3545` | Gray `#6C757D`

**Chart selection matrix:**

| Data question | Chart type | Alternative |
|---------------|-----------|-------------|
| Trend over time | Line | Area |
| Part of whole | Donut / Treemap | Stacked bar |
| Comparison across categories | Bar / Column | Bullet |
| Distribution | Histogram | Box plot |
| Relationship | Scatter | Bubble |
| Geographic | Choropleth | Filled map |

## Executive Dashboard Example

```
+------------------------------------------------------------+
|                   EXECUTIVE SUMMARY                         |
| Revenue: $12.4M (+15% YoY)   Pipeline: $45.2M (+22% QoQ)  |
| Customers: 2,847 (+340 MTD)  NPS: 72 (+5 pts)              |
+------------------------------------------------------------+
| REVENUE TREND (12-mo line)    | REVENUE BY SEGMENT (donut)  |
+-------------------------------+-----------------------------+
| TOP 10 ACCOUNTS (table)       | KPI STATUS (RAG cards)      |
+-------------------------------+-----------------------------+
```

## Report Automation Patterns

**Scheduled report (cron-style):**
```yaml
report:
  name: Weekly Sales Report
  schedule: "0 8 * * MON"
  recipients: [sales-team@company.com, leadership@company.com]
  format: PDF
  pages: [Executive Summary, Pipeline Analysis, Rep Performance]
```

**Threshold alert:**
```yaml
alert:
  name: Revenue Below Target
  metric: daily_revenue
  condition: "actual < target * 0.9"
  channels:
    email: finance@company.com
    slack: "#revenue-alerts"
  message: "Daily revenue ${actual} is ${pct_diff}% below target. Top factors: ${top_factors}"
```

**Automated generation workflow (Python):**
```python
def generate_report(config: dict) -> str:
    """Generate and distribute a scheduled report."""
    # 1. Refresh data sources
    refresh_data_sources(config["sources"])
    # 2. Calculate metrics
    metrics = calculate_metrics(config["metrics"])
    # 3. Create visualizations
    charts = create_visualizations(metrics, config["charts"])
    # 4. Compile into report
    report = compile_report(metrics=metrics, charts=charts, template=config["template"])
    # 5. Distribute
    distribute_report(report, recipients=config["recipients"], fmt=config["format"])
    return report.path
```

## Self-Service BI Maturity Model

| Level | Capability | Users can... |
|-------|-----------|-------------|
| 1 - Consumers | View & filter | Open dashboards, apply filters, export data |
| 2 - Explorers | Ad-hoc queries | Write simple queries, create basic charts, share findings |
| 3 - Builders | Design dashboards | Combine data sources, create calculated fields, publish reports |
| 4 - Modelers | Define data models | Create semantic models, define metrics, optimize performance |

## Performance Optimization Checklist

- [ ] Limit visualizations per page (5-8 max)
- [ ] Use data extracts or materialized views instead of live connections for heavy dashboards
- [ ] Minimize calculated fields in the visualization layer; push logic to the semantic layer or warehouse
- [ ] Apply context filters to reduce query scope
- [ ] Aggregate at source when granularity allows
- [ ] Schedule data refreshes during off-peak hours
- [ ] Monitor and log query execution times; target < 5 s per dashboard load

**Query optimization example:**
```sql
-- Before: full table scan
SELECT * FROM large_table WHERE date >= '2024-01-01';

-- After: partitioned, filtered, and column-pruned
SELECT order_id, customer_id, amount
FROM large_table
WHERE partition_date >= '2024-01-01'
  AND status = 'active'
LIMIT 10000;
```

## Data Storytelling Structure

The agent frames every insight using Situation-Complication-Resolution:

1. **Situation** -- "Last quarter we targeted 10% retention improvement."
2. **Complication** -- "Enterprise churn rose 5%, driven by 30-day onboarding delays."
3. **Resolution** -- "Reducing onboarding to 14 days correlates with 40% lower churn and could save $2M annually."

## Governance

```yaml
security_model:
  row_level_security:
    - rule: region_access
      filter: "region = user.region"
  object_permissions:
    - role: viewer
      permissions: [view, export]
    - role: editor
      permissions: [view, export, edit]
    - role: admin
      permissions: [view, export, edit, delete, publish]
```

## Reference Materials

- `references/dashboard_patterns.md` -- Dashboard design patterns
- `references/visualization_guide.md` -- Chart selection guide
- `references/kpi_library.md` -- Standard KPI definitions
- `references/storytelling.md` -- Data storytelling techniques

## Scripts

```bash
python scripts/kpi_tracker.py --definitions kpis.json --data sales.csv
python scripts/kpi_tracker.py --definitions kpis.json --data sales.csv --json
python scripts/dashboard_spec_generator.py --definitions kpis.json --title "Sales Dashboard"
python scripts/dashboard_spec_generator.py --definitions kpis.json --layout 3-column --json
python scripts/metric_validator.py --definitions metrics.json --strict
python scripts/metric_validator.py --definitions metrics.json --json
```

## Tool Reference

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `kpi_tracker.py` | Calculate KPIs from data against targets; report RAG status and variance | `--definitions <json>`, `--data <csv/json>`, `--json` |
| `dashboard_spec_generator.py` | Generate dashboard layout specs (chart types, positions, filters) from KPI definitions | `--definitions <json>`, `--title`, `--layout 2-column/3-column`, `--json` |
| `metric_validator.py` | Validate metric definitions for completeness, naming, threshold logic, and consistency | `--definitions <json>`, `--strict`, `--json` |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Dashboard loads slowly (> 5 s) | Too many visualizations or live-connection queries hitting raw tables | Reduce widgets to 5-8 per page; switch to extracts or materialized views for heavy dashboards |
| KPI values differ between dashboard and source query | Dashboard applies additional filters, currency conversion, or calculated fields not in the semantic layer | Centralize all metric logic in the semantic layer; remove dashboard-level computed fields |
| RAG thresholds trigger false alerts | Warning/critical percentages are miscalibrated for seasonal patterns | Adjust thresholds per season or use rolling baselines; validate with `metric_validator.py --strict` |
| Stakeholders ignore dashboards | Dashboard answers the wrong questions or lacks actionable context | Redesign using the Situation-Complication-Resolution storytelling framework; add annotations and targets |
| Row-level security hides data unexpectedly | Security rules are too broad or user-role mapping is incorrect | Audit RLS rules; test with a sample user from each role; log filtered row counts |
| Scheduled report emails land in spam | Large PDF attachments or sender reputation issues | Reduce attachment size; switch to embedded links; work with IT to whitelist the sender domain |
| `metric_validator.py` reports formula-aggregation mismatch | The `formula` field (e.g., "SUM(...)") does not match the declared `aggregation` | Align the two fields; the aggregation field drives the tool while the formula documents intent |

## Success Criteria

- Dashboard load time is under 5 seconds for 95% of page views.
- KPI definitions pass `metric_validator.py --strict` with zero errors before production deployment.
- Executive dashboards follow the visual hierarchy: summary cards at top-left, trends in the middle, detail tables at the bottom.
- Every KPI has a defined owner, target, and RAG thresholds documented in the definitions file.
- Self-service BI adoption reaches Level 2 (Explorers) for at least 60% of target users within 90 days.
- Scheduled reports are delivered within 15 minutes of the configured schedule window.
- Data storytelling follows the What / So What / Now What structure with quantified impact in every insight.

## Scope & Limitations

**In scope:** Dashboard design and layout, KPI framework definition, report automation patterns, data storytelling, self-service BI enablement, row-level security configuration, and visualization best practices.

**Out of scope:** Data warehouse infrastructure, ETL/ELT pipeline development, raw data ingestion, machine learning model building, and BI tool installation or licensing.

**Limitations:** The Python tools (`kpi_tracker.py`, `dashboard_spec_generator.py`, `metric_validator.py`) operate on local JSON and CSV files only -- they do not connect to live databases or BI platforms. All scripts use the Python standard library with no external dependencies. Dashboard specifications are platform-agnostic and require manual translation to specific BI tools (Tableau, Power BI, Looker, etc.).

## Integration Points

- **Analytics Engineer** (`data-analytics/analytics-engineer`): Provides the mart models and semantic-layer metrics that dashboards consume; schema changes require dashboard updates.
- **Data Analyst** (`data-analytics/data-analyst`): Creates ad-hoc analyses that may evolve into repeatable dashboards; shares visualization standards.
- **Product Team** (`product-team/`): Defines product KPIs and user-facing analytics requirements.
- **C-Level Advisor** (`c-level-advisor/`): Executive dashboards translate strategic objectives into measurable KPIs.
- **Finance** (`finance/`): Financial KPIs (MRR, CAC, LTV) require alignment between BI dashboards and finance team definitions.
