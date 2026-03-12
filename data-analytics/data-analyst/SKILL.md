---
name: data-analyst
description: >
  Expert data analysis covering SQL querying, data visualization, statistical
  analysis, business reporting, and data storytelling. Use when writing SQL
  queries, building dashboards, performing cohort or funnel analysis, running
  hypothesis tests, or presenting data-driven recommendations to stakeholders.
version: 1.0.0
author: borghei
category: data-analytics
tags: [analytics, sql, visualization, statistics, reporting]
---

# Data Analyst

The agent operates as a senior data analyst, writing production SQL, designing visualizations, running statistical tests, and translating findings into actionable business recommendations.

## Workflow

1. **Frame the business question** -- Restate the stakeholder's question as a testable hypothesis with a clear metric (e.g., "Did campaign X increase 7-day retention by >= 5%?"). Identify required data sources.
2. **Write and validate SQL** -- Use CTEs for readability. Filter early, aggregate late. Run `EXPLAIN ANALYZE` on complex queries to verify index usage and scan cost.
3. **Explore and profile data** -- Compute descriptive statistics (count, mean, median, std, quartiles, skewness). Check for nulls, duplicates, and outliers before drawing conclusions.
4. **Analyze** -- Apply the appropriate method: cohort analysis for retention, funnel analysis for conversion, hypothesis testing (t-test, chi-square) for group comparisons, regression for relationships.
5. **Visualize** -- Select chart type from the matrix below. Follow the design rules (Y-axis at zero for bars, <=7 colors, labels on axes, context via benchmarks/targets).
6. **Deliver the insight** -- Structure findings as What / So What / Now What. Lead with the headline, support with a chart, close with a concrete recommendation and expected impact.

## SQL Patterns

**Monthly aggregation with growth:**
```sql
WITH monthly AS (
    SELECT
        date_trunc('month', created_at) AS month,
        COUNT(*)                        AS total_orders,
        COUNT(DISTINCT customer_id)     AS unique_customers,
        SUM(amount)                     AS revenue
    FROM orders
    WHERE created_at >= '2024-01-01'
    GROUP BY 1
),
growth AS (
    SELECT month, revenue,
        LAG(revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly
)
SELECT month, revenue,
    ROUND((revenue - prev_revenue) / prev_revenue * 100, 1) AS growth_pct
FROM growth
ORDER BY month;
```

**Cohort retention:**
```sql
WITH first_orders AS (
    SELECT customer_id,
        date_trunc('month', MIN(created_at)) AS cohort_month
    FROM orders GROUP BY 1
),
cohort_data AS (
    SELECT f.cohort_month,
        date_trunc('month', o.created_at) AS order_month,
        COUNT(DISTINCT o.customer_id)     AS customers
    FROM orders o
    JOIN first_orders f ON o.customer_id = f.customer_id
    GROUP BY 1, 2
)
SELECT cohort_month, order_month,
    EXTRACT(MONTH FROM AGE(order_month, cohort_month)) AS months_since,
    customers
FROM cohort_data ORDER BY 1, 2;
```

**Window functions (running total + previous order):**
```sql
SELECT customer_id, order_date, amount,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total,
    LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_amount
FROM orders;
```

## Chart Selection Matrix

| Data question | Best chart | Alternative |
|---------------|-----------|-------------|
| Trend over time | Line | Area |
| Part of whole | Donut | Stacked bar |
| Comparison | Bar | Column |
| Distribution | Histogram | Box plot |
| Correlation | Scatter | Heatmap |
| Geographic | Choropleth | Bubble map |

**Design rules:** Start Y-axis at zero for bar charts. Use <= 7 colors. Label axes. Include benchmarks or targets for context. Avoid 3D charts and pie charts with > 5 slices.

## Dashboard Layout

```
+------------------------------------------------------------+
| KPI CARDS: Revenue | Customers | Conversion | NPS           |
+------------------------------------------------------------+
| TREND (line chart)            | BREAKDOWN (bar chart)       |
+-------------------------------+-----------------------------+
| COMPARISON vs target/LY      | DETAIL TABLE (top N)        |
+-------------------------------+-----------------------------+
```

## Statistical Methods

**Hypothesis testing (t-test):**
```python
from scipy import stats
import numpy as np

def compare_groups(a: np.ndarray, b: np.ndarray, alpha: float = 0.05) -> dict:
    """Compare two groups; return t-stat, p-value, Cohen's d, and significance."""
    stat, p = stats.ttest_ind(a, b)
    d = (a.mean() - b.mean()) / np.sqrt((a.std()**2 + b.std()**2) / 2)
    return {"t_statistic": stat, "p_value": p, "cohens_d": d, "significant": p < alpha}
```

**Chi-square test for independence:**
```python
def test_independence(table, alpha=0.05):
    chi2, p, dof, _ = stats.chi2_contingency(table)
    return {"chi2": chi2, "p_value": p, "dof": dof, "significant": p < alpha}
```

## Key Business Metrics

| Category | Metric | Formula |
|----------|--------|---------|
| Acquisition | CAC | Total S&M spend / New customers |
| Acquisition | Conversion rate | Conversions / Visitors |
| Engagement | DAU/MAU ratio | Daily active / Monthly active |
| Retention | Churn rate | Lost customers / Total at period start |
| Revenue | MRR | SUM(active subscription amounts) |
| Revenue | LTV | ARPU x Gross margin x Avg lifetime |

## Insight Delivery Template

```markdown
## [Headline: action-oriented finding]

**What:** One-sentence description of the observation.
**So What:** Why this matters to the business (revenue, retention, cost).
**Now What:** Recommended action with expected impact.
**Evidence:** [Chart or table supporting the finding]
**Confidence:** High / Medium / Low
```

## Analysis Framework

```markdown
# Analysis: [Topic]
## Business Question -- What are we trying to answer?
## Hypothesis -- What do we expect to find?
## Data Sources -- [Source]: [Description]
## Methodology -- Numbered steps
## Findings -- Finding 1, Finding 2 (with supporting data)
## Recommendations -- [Action]: [Expected impact]
## Limitations -- Known caveats
## Next Steps -- Follow-up actions
```

## Reference Materials

- `references/sql_patterns.md` -- Advanced SQL queries
- `references/visualization.md` -- Chart selection guide
- `references/statistics.md` -- Statistical methods
- `references/storytelling.md` -- Presentation best practices

## Scripts

```bash
python scripts/data_profiler.py --table orders --output profile.html
python scripts/query_analyzer.py --query query.sql --explain
python scripts/dashboard_gen.py --config dashboard.yaml
python scripts/report_gen.py --template monthly --output report.pdf
```
