---
name: metrics-dashboard
description: >
  Designs a product metrics dashboard in four layers (North Star, inputs, guardrails,
  operational) with owners, comparisons and cadence, and audits the spec. Use when
  building a launch dashboard or pruning one nobody uses.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-11-08
  python-tools: dashboard_designer.py
  tech-stack: metrics, dashboard, north-star, hexagonal-metrics
  tags:
    - metrics
    - dashboard
    - north-star
    - guardrail-metrics
    - product-analytics
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

Before designing the dashboard, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **North Star metric:** defined or not (it is the root of all 4 layers; if undefined, define it first via `north-star-metric`).
- **Audience:** `exec` (board), `team`, `all-hands`, `partner` or `ic` (sets the max top-level metric count, from 12 for a team down to 3 for an IC).
- **Team structure:** which teams act on this (operational metrics are 4-8 per team with named owners).
- **Available instrumentation:** what data you actually capture (you can't show a metric you don't measure; bounds refresh cadence).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

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

### Step 6 — Audit the spec with `dashboard_designer.py`
Write the spec as JSON (shape in the script's `--help`; a sound and a flawed sample ship in
`assets/`) and run the audit. Done when it exits 0 and the remaining warnings are either fixed
or accepted with a reason.

```bash
python3 project-management/discovery/metrics-dashboard/scripts/dashboard_designer.py \
  --input project-management/discovery/metrics-dashboard/assets/sample_dashboard_spec.json --format markdown   # exit 0
python3 project-management/discovery/metrics-dashboard/scripts/dashboard_designer.py \
  --input project-management/discovery/metrics-dashboard/assets/sample_dashboard_spec_flawed.json --format markdown   # exit 1
```

Findings: **fail** for no North Star, no input metrics or no guardrails; **warn** for vanity terms
(page views, total signups, total users, session count, time on site), missing owners,
definitions or comparisons, guardrails without threshold alerts, over 6 inputs, more than 3
real-time metrics, too many top-level or per-team metrics; **info** for missing targets, under 3
inputs or guardrails, unconfirmed actionability. Exit codes: 0 no fail, 1 at least one fail,
2 bad input (missing file, invalid JSON).

### Step 7 — Sunset stale metrics
Quarterly: remove metrics no team looked at; a dashboard nobody prunes stops being read.

## Decision frameworks

Top-level limits per `audience` (`exec`/`board` 8, `team` 12 plus 8 operational per team, `all-hands` 5, `partner` 6, `ic` 3) and the vanity test ("if this moved 10% next week, what would we do?") are in `references/dashboard-architecture.md` section 14.

## Anti-Patterns

### The wall of metrics
**Mistake:** 30+ metrics on one screen, shown to every audience.
**Why it happens:** Adding a chart is cheap and removing one feels like losing information.
**Instead:** Keep to the audience limit above, give each audience its own view, and let the audit's top-level count check enforce it.

### A North Star with no counterweight
**Mistake:** The dashboard has a North Star and inputs but no guardrails.
**Why it happens:** Guardrails measure what you do not want, so nobody asks for them.
**Instead:** Add 3-5 guardrails with threshold alerts, each tied to a way the North Star could be gamed (more messages could mean more spam). The audit fails a spec with none.

### Orphan metrics
**Mistake:** Metrics with no owner and no review cadence.
**Why it happens:** The dashboard is built as a project and handed to nobody.
**Instead:** Name an owning team per metric and a review meeting per layer; the audit warns on every missing owner.

### Real-time everything
**Mistake:** Every metric refreshes in real time.
**Why it happens:** Real time feels more serious.
**Instead:** Reserve real time for triage metrics (3 or fewer); most decisions run weekly. More detail and fixes: `references/dashboard-anti-patterns.md`.

## Scope & Limitations

**In Scope:**
- Dashboard architecture in four layers: North Star, 3-5 input metrics, 3-5 guardrails and 4-8 operational metrics per team
- Visualization, comparison anchor, refresh cadence and named owner for each metric
- Top-level metric limits by audience and the vanity-versus-actionable test
- A spec audit for too many top-level metrics, missing guardrails, vanity metrics, missing owners and missing comparisons (`dashboard_designer.py`)
- Audits of existing dashboards and mapping OKRs to metrics

**Out of Scope:**
- Defining the North Star itself (see `project-management/execution/north-star-metric/`)
- Building the dashboard in a BI tool or writing its queries (see `data-analytics/business-intelligence/`)
- Event tracking and instrumentation (see `marketing/analytics-tracking/`)
- Metric trees, cohort and funnel analysis on real data (see `product-team/product-analytics/`)

**Important Caveats:**
- `dashboard_designer.py` audits a hand-written JSON spec. It reads no live data and does not check that a metric is instrumented.
- Flags such as `drives_ns` and `actionable_test_passed` are self-reported in the spec. The tool trusts them.
- Which metrics count as guardrails or vanity, and the targets behind them, stay team judgments.
- Dashboards go stale. The skill expects a quarterly prune, which the tool does not schedule.

## References

- `references/dashboard-architecture.md` — layers, cadence, visualization patterns
- `references/dashboard-anti-patterns.md` — common failures + fixes

## Related skills

- `project-management/execution/north-star-metric` — define THE one number
- `product-team/product-analytics` — metric tree + cohort + funnel
- `product-team/ab-test-setup` — experimentation
- `c-level-advisor/chief-data-officer-advisor` — platform context

## Files

| File | Purpose |
|------|---------|
| `scripts/dashboard_designer.py` | Audits a dashboard spec for layering, owners, comparisons and vanity terms |
| `assets/sample_dashboard_spec.json`, `assets/sample_dashboard_spec_flawed.json` | Runnable specs: sound (exit 0) and flawed (exit 1) |
| `assets/dashboard_spec_template.md` | Spec worksheet to fill in |
| `references/dashboard-architecture.md`, `references/dashboard-anti-patterns.md` | Layers, cadence, visualization; failures and fixes |
