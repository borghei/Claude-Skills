# Dashboard Architecture Reference

## 1. The dashboard layers

```
┌──────────────────────────────────────────┐
│  NORTH STAR (1)                          │
│  ────────────────                        │
│  [headline metric + trend + vs target]   │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  INPUTS (3-5)                            │
│  ────────────                            │
│  [3-5 chart cards, each driving NS]      │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  GUARDRAILS (3-5)                        │
│  ──────────────                          │
│  [counter-metrics; "what we don't want   │
│   to sacrifice"]                         │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  OPERATIONAL (4-8 per team)              │
│  ───────────                             │
│  [team-specific metrics for weekly       │
│   action]                                │
└──────────────────────────────────────────┘
```

## 2. Per-layer design

### North Star layer
- Single metric, displayed prominently
- Comparison: vs prior period + vs target
- Trendline showing direction
- Annotated with major events (releases, campaigns)

### Inputs layer
- 3-5 metrics laid out as cards
- Each labeled "drives [NS]"
- Same comparisons
- Smaller charts (don't compete with NS visually)

### Guardrails layer
- 3-5 counter-metrics
- Distinct color (red / orange) to signal "watch out"
- Threshold alerts when crossed
- Often less-frequent refresh

### Operational layer
- 4-8 per team
- Live or daily refresh
- Team-specific framing
- Filterable by segment / channel / cohort

## 3. Audience-specific dashboards

### Exec dashboard (board / monthly business review)
- NS layer + inputs + 1-2 strategic guardrails
- Trends: month-over-month, quarter-over-quarter
- Highly summarized
- 1 page max

### Functional team dashboard (eng / growth / CS)
- NS (reminder) + their inputs + their operational metrics
- Daily / hourly refresh
- Drill-down capability
- 1-2 pages

### Individual contributor view
- Their KPIs (1-3)
- Their pipeline / queue / activity
- Personal — not exposed across team

### All-hands / company-wide
- NS + 3-5 inputs
- Mostly narrative (story per metric)
- 1 page; high signal/noise

## 4. Cadence by metric type

| Metric type | Cadence |
|-------------|---------|
| Real-time operational (active users now, errors) | Live |
| Daily ops (deploys, support tickets) | Daily |
| Weekly review (funnel, cohort, growth) | Daily refresh; weekly review |
| Monthly business review | Monthly refresh; monthly review |
| Quarterly board / strategy | Monthly refresh; quarterly review |

Don't refresh real-time what doesn't need it — it's expensive and noisy.

## 5. Common visualization patterns

### Time series (line)
- For: NS, inputs, most operational
- Comparison: same metric, prior period overlaid
- Annotations: deployment markers, campaign launches

### Funnel
- For: conversion / activation / checkout
- Comparison: vs cohort baseline / vs target
- Drill-down: by segment, channel

### Cohort heatmap
- For: retention, engagement over time
- Comparison: across cohorts (down a column)
- Read: vertically to spot improvement

### Bar / grouped bar
- For: comparison across discrete groups
- Comparison: same group prior period

### Bullet chart
- For: actual vs target gauge
- One per goal

### Sparkline (small embedded line)
- For: many metrics at-a-glance
- Comparison: implied trend

### What to avoid
- Pie charts beyond 3 slices
- 3D anything
- Default Excel charts (low information density)
- Dual y-axis (confusing)

## 6. Metric naming

Naming matters more than people think:

### Good
- "Activation Rate (W1)" — clear, specific, time-bounded
- "Daily Active Companies / MAC" — specific cohort, definition implied
- "P95 Lead Time" — specific statistic

### Weak
- "Engagement" — what kind?
- "Health Score" — composite; opaque
- "User Activity" — too vague
- "Volume" — of what?

Per metric, document:
- Name (precise)
- Definition (the exact calculation)
- Source (which table / event)
- Filters applied
- Caveats (known biases)

## 7. Metric ownership

Each metric needs a named owner:

- Owner is accountable for the metric moving (or for understanding why it's not)
- Owner answers questions about definition / data quality
- Owner authorizes changes to the metric

Without owners, metrics rot.

## 8. Threshold alerts

For guardrails and critical operational metrics:

- Define normal range
- Alert when outside range (3-sigma; or absolute threshold)
- Route to owner
- Acknowledge required

Don't over-alert. Alert fatigue kills response discipline.

## 9. Drill-down design

A good dashboard supports:

- **Click metric → see definition + history**
- **Filter by segment / channel / cohort**
- **Time-range adjuster**
- **Export to CSV / share link**
- **Annotations layer**

Without drill-down, the dashboard answers some questions and creates more.

## 10. Anti-vanity test

For each metric on the dashboard, ask:

1. "If it moved +10% next week, what would we do?"
2. "If it moved -10% next week, what would we do?"

If both answers are "nothing" → vanity → cut.

## 11. Tooling

Common dashboard tools (2026):

- Looker (Google) — strong semantic layer
- Mode — analyst-focused
- Hex — notebook + dashboard hybrid
- Sigma — spreadsheet-flavored
- Metabase — open-source
- Superset — open-source
- Tableau — enterprise classic
- PowerBI — enterprise + Microsoft shop
- Custom (Grafana + Metabase + Looker mix)

Tool < discipline. A spreadsheet dashboard reviewed weekly > a Looker
masterpiece nobody opens.

## 12. The 4-week pilot

Before commiting a new dashboard:

- Week 1-2: build with team input
- Week 3: weekly review attended
- Week 4: cut metrics nobody asked about
- Week 5+: locked in

Most dashboards bloat over time. Annual pruning is healthy.

## 13. Common pitfalls

- **30+ metrics, no hierarchy.** No prioritization possible.
- **No NS.** Optimizing nothing.
- **No guardrails.** Optimizing NS at any cost.
- **Live everything.** Cost + noise.
- **No owners.** Metric rot.
- **No comparisons.** Numbers in space.
- **Pretty charts, no decisions.** Decoration.
- **Built once, never reviewed.** Dashboard rot.

---

## 14. Audit limits by audience and the vanity test

These are the limits `dashboard_designer.py` applies.

### Top-level metric count (NS + inputs + guardrails)

| `audience` | Max top-level | Why |
|------------|---------------|-----|
| `exec` (alias `board`) | 8 | Limited attention; high signal/noise |
| `team` (alias `functional`) | 12, plus up to 8 operational per team | Acted on weekly |
| `all-hands` | 5 | Communicable; the company rallies on it |
| `partner` | 6 | External; share only what you will defend |
| `ic` | 3 | Their direct impact |

### Vanity vs actionable test

For each candidate metric: "If this moved 10% next week, what would we do?" No answer means it is vanity: cut it. Every chart also needs a comparison anchor (prior period, target or cohort baseline). Visualization and cadence patterns are in section 5.
