---
name: business-intelligence
description: Expert business intelligence covering dashboard design, data visualization, reporting automation, and executive insights delivery.
version: 1.0.0
author: Claude Skills
category: data-analytics
tags: [bi, dashboards, visualization, reporting, insights]
---

# Business Intelligence

Expert-level business intelligence for data-driven decisions.

## Core Competencies

- Dashboard design
- Data visualization
- Reporting automation
- KPI development
- Executive reporting
- Self-service BI
- Data storytelling
- Tool administration

## BI Architecture

### Data Flow

```
DATA SOURCES → ETL/ELT → DATA WAREHOUSE → SEMANTIC LAYER → DASHBOARDS
     │            │            │              │              │
     ▼            ▼            ▼              ▼              ▼
  CRM, ERP    Transform    Star Schema    Metrics Def    Tableau/PBI
  APIs, DBs   Clean, Load  Fact/Dims      Calculations   Looker/etc
```

### BI Stack Components

```
PRESENTATION LAYER
├── Executive dashboards
├── Operational reports
├── Self-service exploration
└── Embedded analytics

SEMANTIC LAYER
├── Business metrics definitions
├── Calculated fields
├── Hierarchies
└── Row-level security

DATA LAYER
├── Data warehouse (Snowflake/BigQuery/Redshift)
├── Data marts
├── Materialized views
└── Cached datasets
```

## Dashboard Design

### Dashboard Types

**Executive Dashboard:**
```
┌─────────────────────────────────────────────────────────────┐
│                   EXECUTIVE SUMMARY                          │
├─────────────────────────────────────────────────────────────┤
│  Revenue        Pipeline       Customers      NPS            │
│  $12.4M         $45.2M         2,847          72             │
│  +15% YoY       +22% QoQ       +340 MTD       +5 pts         │
├─────────────────────────────────────────────────────────────┤
│  REVENUE TREND                 │  REVENUE BY SEGMENT         │
│  [Line chart: 12 months]       │  [Pie chart: segments]      │
├────────────────────────────────┼─────────────────────────────┤
│  TOP ACCOUNTS                  │  KEY METRICS STATUS         │
│  [Table: top 10]               │  [KPI cards with RAG]       │
└─────────────────────────────────────────────────────────────┘
```

**Operational Dashboard:**
```
┌─────────────────────────────────────────────────────────────┐
│                   DAILY OPERATIONS                           │
├─────────────────────────────────────────────────────────────┤
│  Orders Today    Tickets Open   Avg Response   SLA Met       │
│  1,247           89             12 min         98.5%         │
│  vs Avg: +8%     vs Avg: -12%   vs Target: ✓  vs Target: ✓  │
├─────────────────────────────────────────────────────────────┤
│  HOURLY VOLUME                 │  QUEUE STATUS               │
│  [Area chart: 24h]             │  [Stacked bar by team]      │
├────────────────────────────────┼─────────────────────────────┤
│  ALERTS                        │  TEAM PERFORMANCE           │
│  [Alert list with severity]    │  [Table: agents + metrics]  │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

**Visual Hierarchy:**
1. Most important metrics at top-left
2. Summary → Detail flow (top to bottom)
3. Related metrics grouped together
4. White space for readability

**Color Usage:**
```
STATUS COLORS
├── Green (#28A745): Good/On Track
├── Yellow (#FFC107): Warning/At Risk
├── Red (#DC3545): Critical/Off Track
└── Gray (#6C757D): Neutral/No Status

BRAND COLORS
├── Primary: Use for emphasis
├── Secondary: Supporting elements
└── Accent: Highlights only

DATA COLORS
├── Sequential: Light → Dark for ranges
├── Diverging: Different hues for pos/neg
└── Categorical: Distinct colors per category
```

**Chart Selection:**

| Data Type | Best Charts |
|-----------|-------------|
| Trend over time | Line, Area |
| Part of whole | Pie, Donut, Treemap |
| Comparison | Bar, Column |
| Distribution | Histogram, Box Plot |
| Relationship | Scatter, Bubble |
| Geographic | Map, Choropleth |

## KPI Framework

### KPI Development

```markdown
# KPI Definition: [Metric Name]

## Business Context
- Owner: [Department/Role]
- Purpose: [Why this metric matters]
- Strategic alignment: [Goal it supports]

## Definition
- Formula: [Calculation]
- Data source: [System/Table]
- Granularity: [Daily/Weekly/Monthly]

## Targets
- Target: [Value]
- Threshold (Yellow): [Value]
- Critical (Red): [Value]

## Dimensions
- Time: [Day/Week/Month/Quarter/Year]
- Segments: [By region, product, etc.]

## Caveats
- [Known limitations]
- [Data quality issues]
```

### Metric Categories

**Financial:**
| Metric | Formula | Frequency |
|--------|---------|-----------|
| Revenue | Sum of closed won | Daily |
| MRR | Monthly recurring | Monthly |
| Gross Margin | (Rev - COGS) / Rev | Monthly |
| CAC | S&M Spend / New Customers | Monthly |
| LTV | ARPU × Margin × Lifetime | Quarterly |

**Customer:**
| Metric | Formula | Frequency |
|--------|---------|-----------|
| Active Users | DAU, WAU, MAU | Daily |
| Churn Rate | Lost / Total | Monthly |
| NPS | Promoters - Detractors | Quarterly |
| CSAT | Satisfied / Responses | Weekly |

**Operations:**
| Metric | Formula | Frequency |
|--------|---------|-----------|
| Throughput | Units / Time | Hourly |
| Error Rate | Errors / Total | Daily |
| Cycle Time | End - Start | Daily |
| Utilization | Active / Capacity | Daily |

## Report Automation

### Report Types

**Scheduled Reports:**
```yaml
report:
  name: Weekly Sales Report
  schedule: "0 8 * * MON"  # Every Monday 8am
  recipients:
    - sales-team@company.com
    - leadership@company.com
  format: PDF
  pages:
    - Executive Summary
    - Pipeline Analysis
    - Rep Performance
    - Forecast
```

**Threshold Alerts:**
```yaml
alert:
  name: Revenue Below Target
  metric: daily_revenue
  condition: actual < target * 0.9
  frequency: daily
  channels:
    - email: finance@company.com
    - slack: #revenue-alerts
  message: |
    Daily revenue of ${actual} is ${pct_diff}% below target.
    Top contributing factors: ${top_factors}
```

### Automation Patterns

```python
def generate_report(report_config):
    """
    Automated report generation workflow
    """
    # 1. Refresh data
    refresh_data_sources(report_config['sources'])

    # 2. Calculate metrics
    metrics = calculate_metrics(report_config['metrics'])

    # 3. Generate visualizations
    charts = create_visualizations(metrics, report_config['charts'])

    # 4. Build report
    report = compile_report(
        metrics=metrics,
        charts=charts,
        template=report_config['template']
    )

    # 5. Distribute
    distribute_report(
        report=report,
        recipients=report_config['recipients'],
        format=report_config['format']
    )

    return report
```

## Self-Service BI

### Enablement Framework

```
SELF-SERVICE MATURITY MODEL

Level 1: Report Consumers
├── View existing dashboards
├── Apply filters
└── Export data

Level 2: Data Explorers
├── Ad-hoc queries
├── Create simple charts
└── Share findings

Level 3: Report Builders
├── Design dashboards
├── Combine data sources
└── Create calculated fields

Level 4: Data Modelers
├── Create data models
├── Define metrics
└── Optimize performance
```

### Data Catalog

```markdown
# Data Catalog Entry

## Dataset: sales_opportunities

### Description
Contains all sales opportunities from CRM

### Schema
| Column | Type | Description |
|--------|------|-------------|
| opp_id | STRING | Unique identifier |
| account_id | STRING | Related account |
| amount | DECIMAL | Deal value |
| stage | STRING | Pipeline stage |
| close_date | DATE | Expected close |
| owner_id | STRING | Sales rep |

### Refresh
- Frequency: Every 4 hours
- Source: Salesforce API
- Last refresh: 2024-01-15 08:00 UTC

### Usage Notes
- Filter by is_deleted = false
- Amount is always in USD
- Stage values: Prospect, Discovery, Demo, Proposal, Negotiation, Closed Won, Closed Lost

### Related Datasets
- accounts
- sales_reps
- products
```

## Data Storytelling

### Narrative Structure

```
SITUATION → COMPLICATION → RESOLUTION

1. SITUATION (Context)
   "Last quarter, we set a goal to increase customer retention by 10%"

2. COMPLICATION (Problem/Opportunity)
   "However, churn increased by 5% in our enterprise segment"

3. RESOLUTION (Insight + Action)
   "Analysis shows onboarding time correlates with churn.
    Reducing onboarding from 30 to 14 days could save $2M annually"
```

### Insight Framework

```markdown
# Insight: [Title]

## What happened?
[Describe the observation in data]

## Why does it matter?
[Business impact and context]

## Why did it happen?
[Root cause analysis]

## What should we do?
[Recommended actions]

## Supporting Data
[Charts and metrics]
```

### Presentation Template

```
EXECUTIVE PRESENTATION STRUCTURE

1. Headlines First (2-3 key takeaways)
2. Context (why we're looking at this)
3. Key Findings (data + insights)
4. Implications (what it means)
5. Recommendations (what to do)
6. Appendix (detailed data)
```

## Tool Administration

### Performance Optimization

**Dashboard Performance:**
```
OPTIMIZATION CHECKLIST
□ Limit visualizations per page (5-8 max)
□ Use data extracts vs live connections
□ Minimize calculated fields in viz
□ Use context filters effectively
□ Aggregate data at source when possible
□ Schedule refreshes during off-peak
□ Monitor query execution times
```

**Query Optimization:**
```sql
-- Bad: Full table scan
SELECT * FROM large_table
WHERE date >= '2024-01-01';

-- Good: Partitioned and filtered
SELECT required_columns
FROM large_table
WHERE partition_date >= '2024-01-01'
  AND status = 'active'
LIMIT 10000;
```

### Governance

**Access Control:**
```yaml
security_model:
  row_level_security:
    - rule: region_access
      filter: "region = user.region"
    - rule: team_access
      filter: "team_id IN user.teams"

  object_permissions:
    - role: viewer
      permissions: [view, export]
    - role: editor
      permissions: [view, export, edit]
    - role: admin
      permissions: [view, export, edit, delete, publish]
```

**Data Quality Monitoring:**
```
DATA QUALITY CHECKS
├── Freshness: Is data current?
├── Completeness: Are all records present?
├── Accuracy: Do values make sense?
├── Consistency: Do related metrics align?
└── Uniqueness: Are there duplicates?
```

## Reference Materials

- `references/dashboard_patterns.md` - Dashboard design patterns
- `references/visualization_guide.md` - Chart selection guide
- `references/kpi_library.md` - Standard KPI definitions
- `references/storytelling.md` - Data storytelling techniques

## Scripts

```bash
# Dashboard performance analyzer
python scripts/dashboard_analyzer.py --dashboard "Sales Overview"

# KPI calculator
python scripts/kpi_calculator.py --config metrics.yaml --output report.json

# Report generator
python scripts/report_generator.py --template weekly_sales --format pdf

# Data quality checker
python scripts/data_quality.py --dataset sales_opportunities --checks all
```
