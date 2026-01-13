---
name: data-analyst
description: Expert data analysis covering SQL, visualization, statistical analysis, business intelligence, and data storytelling.
version: 1.0.0
author: Claude Skills
category: data-analytics
tags: [analytics, sql, visualization, statistics, reporting]
---

# Data Analyst

Expert-level data analysis for business insights.

## Core Competencies

- SQL and database querying
- Data visualization
- Statistical analysis
- Business intelligence
- Data storytelling
- Dashboard development
- Reporting automation
- Stakeholder communication

## SQL Mastery

### Query Patterns

**Aggregation:**
```sql
SELECT
    date_trunc('month', created_at) as month,
    COUNT(*) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value
FROM orders
WHERE created_at >= '2024-01-01'
GROUP BY 1
ORDER BY 1;
```

**Window Functions:**
```sql
SELECT
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) as running_total,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) as order_number,
    LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date) as previous_order
FROM orders;
```

**CTEs for Clarity:**
```sql
WITH monthly_metrics AS (
    SELECT
        date_trunc('month', created_at) as month,
        SUM(amount) as revenue
    FROM orders
    GROUP BY 1
),
growth_calc AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) as prev_revenue
    FROM monthly_metrics
)
SELECT
    month,
    revenue,
    ROUND((revenue - prev_revenue) / prev_revenue * 100, 1) as growth_pct
FROM growth_calc;
```

**Cohort Analysis:**
```sql
WITH first_orders AS (
    SELECT
        customer_id,
        date_trunc('month', MIN(created_at)) as cohort_month
    FROM orders
    GROUP BY 1
),
cohort_data AS (
    SELECT
        f.cohort_month,
        date_trunc('month', o.created_at) as order_month,
        COUNT(DISTINCT o.customer_id) as customers
    FROM orders o
    JOIN first_orders f ON o.customer_id = f.customer_id
    GROUP BY 1, 2
)
SELECT
    cohort_month,
    order_month,
    EXTRACT(MONTH FROM AGE(order_month, cohort_month)) as months_since_cohort,
    customers
FROM cohort_data
ORDER BY 1, 2;
```

### Query Optimization

**Use EXPLAIN:**
```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 123;
```

**Best Practices:**
- Use indexes on filtered columns
- Avoid SELECT * in production
- Use LIMIT for exploratory queries
- Filter early, aggregate late
- Use appropriate data types

## Data Visualization

### Chart Selection Guide

| Data Type | Best Chart | Alternative |
|-----------|------------|-------------|
| Trend over time | Line chart | Area chart |
| Part of whole | Pie/Donut | Stacked bar |
| Comparison | Bar chart | Column chart |
| Distribution | Histogram | Box plot |
| Correlation | Scatter plot | Heatmap |
| Geographic | Map | Choropleth |

### Visualization Best Practices

**Do:**
- Start Y-axis at zero (for bars)
- Use consistent colors
- Label axes clearly
- Include context (benchmarks, targets)
- Order categories meaningfully

**Don't:**
- Use 3D charts
- Use more than 5-7 colors
- Truncate axes misleadingly
- Clutter with gridlines
- Use pie charts for many categories

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  EXECUTIVE SUMMARY                                          │
│  [KPI 1: $X]  [KPI 2: X%]  [KPI 3: X]  [KPI 4: X%]         │
├─────────────────────────────────────────────────────────────┤
│  TRENDS                          │  BREAKDOWN               │
│  [Line Chart - Primary Metric]   │  [Bar Chart - Segments]  │
│                                  │                          │
├──────────────────────────────────┼──────────────────────────┤
│  COMPARISON                      │  DETAIL TABLE            │
│  [Bar Chart - vs Target/LY]      │  [Top N with metrics]    │
│                                  │                          │
└──────────────────────────────────┴──────────────────────────┘
```

## Statistical Analysis

### Descriptive Statistics

```python
import pandas as pd
import numpy as np

def describe_data(df, column):
    stats = {
        'count': df[column].count(),
        'mean': df[column].mean(),
        'median': df[column].median(),
        'std': df[column].std(),
        'min': df[column].min(),
        'max': df[column].max(),
        'q25': df[column].quantile(0.25),
        'q75': df[column].quantile(0.75),
        'skewness': df[column].skew(),
        'kurtosis': df[column].kurtosis()
    }
    return stats
```

### Hypothesis Testing

```python
from scipy import stats

# T-test: Compare two groups
def compare_groups(group_a, group_b, alpha=0.05):
    stat, p_value = stats.ttest_ind(group_a, group_b)

    result = {
        't_statistic': stat,
        'p_value': p_value,
        'significant': p_value < alpha,
        'effect_size': (group_a.mean() - group_b.mean()) / np.sqrt(
            (group_a.std()**2 + group_b.std()**2) / 2
        )
    }
    return result

# Chi-square: Test independence
def test_independence(observed, alpha=0.05):
    stat, p_value, dof, expected = stats.chi2_contingency(observed)

    return {
        'chi2': stat,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'significant': p_value < alpha
    }
```

### Regression Analysis

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

def simple_regression(X, y):
    model = LinearRegression()
    model.fit(X.reshape(-1, 1), y)

    predictions = model.predict(X.reshape(-1, 1))

    return {
        'coefficient': model.coef_[0],
        'intercept': model.intercept_,
        'r_squared': r2_score(y, predictions),
        'mae': mean_absolute_error(y, predictions)
    }
```

## Business Analysis

### Analysis Framework

```markdown
# Analysis: [Topic]

## Business Question
[What are we trying to answer?]

## Hypothesis
[What do we expect to find?]

## Data Sources
- [Source 1]: [Description]
- [Source 2]: [Description]

## Methodology
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Findings

### Finding 1: [Title]
[Description with supporting data]

### Finding 2: [Title]
[Description with supporting data]

## Recommendations
1. [Recommendation]: [Expected impact]
2. [Recommendation]: [Expected impact]

## Limitations
- [Limitation 1]
- [Limitation 2]

## Next Steps
- [Action item]
```

### Key Business Metrics

**Acquisition:**
- Customer Acquisition Cost (CAC)
- Cost per Lead (CPL)
- Conversion Rate

**Engagement:**
- Daily/Monthly Active Users
- Session Duration
- Feature Adoption

**Retention:**
- Churn Rate
- Retention Rate
- Net Revenue Retention

**Revenue:**
- Monthly Recurring Revenue (MRR)
- Average Revenue Per User (ARPU)
- Lifetime Value (LTV)

## Data Storytelling

### Presentation Structure

```
1. CONTEXT
   - Why does this matter?
   - What question are we answering?

2. KEY FINDING
   - Lead with the insight
   - Make it memorable

3. EVIDENCE
   - Show the data
   - Use effective visuals

4. IMPLICATIONS
   - What does this mean?
   - So what?

5. RECOMMENDATIONS
   - What should we do?
   - Clear next steps
```

### Insight Template

```markdown
## [Headline: Action-oriented finding]

**What:** [One sentence description of the finding]

**So What:** [Why this matters to the business]

**Now What:** [Recommended action]

**Evidence:**
[Chart or data supporting the finding]

**Confidence:** [High/Medium/Low]
```

## Reference Materials

- `references/sql_patterns.md` - Advanced SQL queries
- `references/visualization.md` - Chart selection guide
- `references/statistics.md` - Statistical methods
- `references/storytelling.md` - Presentation best practices

## Scripts

```bash
# Data profiler
python scripts/data_profiler.py --table orders --output profile.html

# SQL query analyzer
python scripts/query_analyzer.py --query query.sql --explain

# Dashboard generator
python scripts/dashboard_gen.py --config dashboard.yaml

# Report automation
python scripts/report_gen.py --template monthly --output report.pdf
```
