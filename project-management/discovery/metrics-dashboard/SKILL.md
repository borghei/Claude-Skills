---
name: metrics-dashboard
description: >
  Design a product metrics dashboard — North Star, input metrics, and
  guardrails — that a team actually uses to make decisions. Use when
  building dashboard architecture: layers, owners, cadence, and
  visualization.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-05-27
  python-tools: dashboard_designer.py
  tech-stack: metrics, dashboard, north-star, hexagonal-metrics
---

# Metrics Dashboard

A dashboard architecture skill: which metrics go where, at which cadence,
for which audience, with which visualization. Focused on producing the
ONE artifact a team uses to make decisions — not the 30-chart dashboard
nobody opens.

## When to use this skill

- **New product / feature launch** — what to instrument and watch
- **Existing dashboard audit** — what to cut, add, refactor
- **Team-level OKR tracking** — operational dashboard for the team
- **Exec readouts** — board / monthly business review dashboard
- **Cross-functional alignment** — what does "success" look like?

## The 4 dashboard layers

1. **North Star** — 1 metric that summarizes value delivered
2. **Input metrics** (3-5) — the drivers of NS
3. **Guardrails** (3-5) — what we DON'T want to sacrifice (counter-metrics)
4. **Operational metrics** (4-8 per team) — what we actually act on weekly

A dashboard ≠ all metrics. A dashboard = these 11-22 metrics presented
for fast decision-making.

## Clarify First

Before designing the dashboard, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **North Star metric** — defined or not (it is the root of all 4 layers; if undefined, define it first via `north-star-metric`)
- [ ] **Audience** — board/exec / functional team / all-hands / IC (sets the max top-level metric count, 5-8 down to 1-3)
- [ ] **Team structure** — which teams act on this (operational metrics are 4-8 per team with named owners)
- [ ] **Available instrumentation** — what data you actually capture (you can't show a metric you don't measure; bounds refresh cadence)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Confirm the North Star
Already defined? Use it. Not defined? See `project-management/execution/north-star-metric`.

A good NS:
- Behavioral or business
- Moves week-over-week
- Hard to game without delivering real value
- One number

### Step 2 — Decompose to input metrics
For each NS, identify 3-5 inputs whose combined movement drives it.

Example for NS "Weekly Active Companies × Messages Sent per Company":
- Acquisition rate
- Activation rate (% reaching 50 messages in 14 days)
- Retention rate (W4 cohort)
- Expansion (adds users / channels)

### Step 3 — Identify guardrails
What could move the NS up while damaging the underlying value?

Example guardrails:
- Spam rate (if NS = messages, more messages can include spam)
- User-reported complaints
- Power-user churn (vs total churn)
- Support ticket volume
- Latency / error rate

### Step 4 — Identify operational metrics per team
The 4-8 metrics each team needs to act weekly:
- Growth team: funnel conversion, channel CAC, signup quality
- Retention team: cohort retention, save-room saves
- Platform team: SLO posture, on-call health, deploy freq
- Trust & safety: spam reports, removed accounts, false-positive rate

### Step 5 — Define visualization + cadence per metric
Each metric needs:
- **Visualization:** line chart / funnel / cohort heatmap / bar
- **Comparison:** vs prior period / vs target / vs cohort baseline
- **Refresh cadence:** real-time / hourly / daily / weekly / monthly
- **Owner:** named team

### Step 6 — Run `dashboard_designer.py`
Audit: too many top-level metrics, no guardrails, vanity metrics, missing
owners, missing comparisons.

```bash
python3 project-management/discovery/metrics-dashboard/scripts/dashboard_designer.py \
  --input dashboard_spec.json --format markdown
```

### Step 7 — Sunset stale metrics
Quarterly: kill metrics no team looked at. Dashboards rot; pruning is
healthy.

## Decision frameworks

### Top-level metric count

| Audience | Max top-level | Why |
|----------|---------------|-----|
| Board / exec | 5-8 | Limited attention; high signal/noise |
| Functional team | 4-8 | Actionable; weekly review |
| All-hands | 3-5 | Communicable; team rallies |
| Individual contributor | 1-3 | Their direct impact |

### Visualization fit

| Question | Best visualization |
|----------|---------------------|
| Is it changing over time? | Line chart |
| How much vs target? | Gauge / bullet |
| Drop-off at each step? | Funnel |
| Retention over time? | Cohort heatmap |
| Distribution? | Histogram |
| Composition? | Stacked area / pie (rare) |
| Comparison across groups? | Grouped bar |
| Relationship? | Scatter |

Avoid pie charts beyond 3 slices. Avoid 3D charts always.

### Vanity vs actionable test

For each candidate metric: "If this moved up 10% next week, what would we do?"

- Have answer → actionable; keep
- No answer → vanity; cut

### Comparison discipline

Every chart needs a comparison anchor:
- vs prior period (week / month / quarter)
- vs target
- vs cohort baseline
- vs competitor benchmark (rare; usually unreliable)

A chart with no comparison is a number floating in space.

## Common engagements

### "Build us a dashboard for the new product line"
1. Confirm North Star.
2. Decompose to 3-5 inputs.
3. Identify 3-5 guardrails.
4. Per team: 4-8 operational metrics.
5. Spec viz + cadence + owner per metric.
6. Pilot for 4 weeks; cut what nobody opens.

### "Audit our existing dashboard"
1. List every metric currently shown.
2. Tag each: NS / input / guardrail / operational / vanity.
3. Cut all vanity.
4. Cut operational that no team looks at.
5. Add missing guardrails.
6. Limit each audience to its max.

### "Help us track an OKR"
1. Map OKR to metric: KR → metric.
2. KR should be the metric.
3. Inputs = what moves the KR.
4. Guardrails = what we won't sacrifice.

## Anti-patterns to avoid

- **30+ metrics on one screen.** Decision-making dies.
- **No guardrails.** NS optimization without counter-balance.
- **All metrics for all audiences.** Exec doesn't need eng team metrics.
- **No comparisons.** Numbers without context.
- **Real-time everything.** Most metrics don't need it (and it's expensive).
- **No owner per metric.** Orphan metrics rot.
- **Vanity metrics (page views, signups alone).** Not action-driving.
- **No cadence on review.** Dashboard exists; team doesn't use it.

## References

- `references/dashboard-architecture.md` — layers, cadence, visualization patterns
- `references/dashboard-anti-patterns.md` — common failures + fixes

## Related skills

- `project-management/execution/north-star-metric` — define THE one number
- `product-team/product-analytics` — metric tree + cohort + funnel
- `product-team/ab-test-setup` — experimentation
- `c-level-advisor/chief-data-officer-advisor` — platform context
