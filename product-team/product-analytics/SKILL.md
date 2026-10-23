---
name: product-analytics
description: >
  Product analytics for instrumenting products, defining metrics, and building
  retention funnels. Use when designing a metric tree, instrumenting a feature,
  auditing instrumentation, defining a North Star, or building an analytics
  roadmap.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-team
  domain: product-analytics
  updated: 2026-05-27
  tags: [analytics, metrics, north-star, retention, activation, funnel, cohort, instrumentation]
---

# Product Analytics

A product analytics skill focused on **decisions from data**, not dashboards.
Covers the metric tree, instrumentation patterns, funnel + retention +
cohort analysis, and the operational rituals that turn measurement into
product changes.

## When to use this skill

- Designing the **North Star metric** and its tree of input metrics
- Auditing **product instrumentation** (events, properties, gaps)
- Building or refreshing an **activation funnel** for a new product or feature
- Designing or analyzing **retention cohorts** (D1/D7/D30/W1/W4/M1/M3)
- Building or refining the **PM analytics dashboard**
- Translating product data into **decisions and roadmap inputs**
- Auditing **dashboards for actionability** (kill the vanity)

## Inputs the advisor expects

- Product type (B2B SaaS, consumer, marketplace, etc.)
- Current analytics stack (Amplitude / Mixpanel / GA4 / Segment / Snowflake + dbt + Looker)
- Existing North Star + input metrics
- Current event taxonomy + instrumentation gaps
- Top product questions you can't answer today
- Org expectations: who consumes analytics, at what cadence

## Clarify First

Before designing the metric tree or audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Product type:** B2B SaaS, consumer, marketplace, etc. (drives the North Star pattern and input metrics).
- **The value moment:** what "delivered value" looks like for a user (defines the North Star and activation event).
- **Current analytics stack and event taxonomy:** Amplitude/Mixpanel/GA4/Segment plus existing events (drives the instrumentation audit and gap list).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflows

### Workflow 1 — Design the metric tree

1. Define the **North Star** (one number that summarizes value delivered).
2. Decompose into **inputs** (drivers of the NS).
3. Add **guardrails / counter-metrics** that catch unintended consequences.
4. Run `metric_tree_designer.py` against your candidate tree to surface
   imbalance, missing layers, anti-patterns.

```bash
python3 product-analytics/scripts/metric_tree_designer.py \
  --input metric_tree.json --format markdown
```

### Workflow 2 — Audit instrumentation

1. Pull the current event taxonomy + properties.
2. Run `event_taxonomy_auditor.py` to flag PII risk, schema drift,
   naming inconsistency, duplication, undocumented events, and gaps.
3. Generate the remediation backlog and assign owners.

```bash
python3 product-analytics/scripts/event_taxonomy_auditor.py \
  --input event_inventory.json --format markdown
```

### Workflow 3 — Analyze retention cohorts

1. Pull cohort retention data (raw counts by cohort week and offset).
2. Run `retention_cohort_analyzer.py` to compute retention rates, identify
   patterns (smile curve, leaky bucket), and surface cohort-level alerts.

```bash
python3 product-analytics/scripts/retention_cohort_analyzer.py \
  --input retention.json --format markdown
```

## Decision frameworks

### North Star metric — what makes one good

A good North Star metric:
- **Measures value delivered to the user** (not just usage)
- **Aligns to business outcome** indirectly via clear chain
- **Is a leading indicator** of long-term success
- **Can move week-over-week** (so it can be acted on)
- **Is hard to game** without delivering real value

Common patterns by product type:

| Product type | Common North Star |
|--------------|-------------------|
| Communication / messaging | Messages sent per WAU |
| Marketplace | Successful transactions per MAU |
| Content | Hours of meaningful content consumed |
| Productivity SaaS | Activated workspaces × engagement depth |
| Consumer payments | Active payment senders per week |
| Developer tool | Weekly active developers performing core action |

Don't pick "DAU" or "Revenue" as North Star — they're outputs, not value drivers.

### Metric tree structure

A clean metric tree has three layers:

1. **North Star** (1 metric)
2. **Input metrics** (3–5 that combine to produce the NS)
3. **Driver metrics** (per input, 3–5 that move the input)

Plus a **guardrails / counter-metrics** sidebar (3–5 that catch
unintended consequences).

If you have 30 KPIs at the top level, you have no top level.

### The activation question

For any new product or feature, ask: "What does it look like when a user
realizes value from this?"

That's the **activation event**. A clear definition makes:
- Onboarding design — clearer
- Funnel analysis — possible
- Eval of marketing channels — sharper
- Customer success interventions — better-timed

Common mistake: defining activation as "completed signup." Signup is
table stakes; activation is the moment of value.

### Retention curve shapes

| Shape | Diagnosis | Action |
|-------|-----------|--------|
| Power-law smile | Healthy product-market fit | Invest in scale |
| Slow decay then flat | Product-market fit | Investigate the flatline cohort segment |
| Steep then zero | Novelty product | Re-evaluate the value proposition |
| Linear decline | Leaky bucket | Improve retention features |
| Inverted (rising) | Network effects kicking in | Acquire harder |

Read shape before reading numbers.

### Vanity vs actionable metrics

| Metric | Vanity if | Actionable if |
|--------|-----------|---------------|
| DAU / MAU | Tracked alone | Decomposed by segment, action |
| Pageviews | Tracked alone | Tied to conversion funnel |
| Total revenue | Tracked alone | Decomposed by cohort, channel, segment |
| App downloads | Tracked alone | Paired with activation rate |
| Total accounts | Tracked alone | Paired with active accounts |

The test: "If this metric goes up 10% next week, what do we change?"
If you don't have an answer, it's vanity.

## Common engagements

### "Help me design our analytics for the launch"
1. Define activation event and 3–5 input metrics.
2. Spec event taxonomy (event names, properties, user/account context).
3. Pilot dashboards (one for the team, one for execs).
4. Set the review cadence; don't let dashboards rot.

### "Our funnel rate is dropping. What's wrong?"
1. Decompose: which step's conversion dropped?
2. Segment: which user segment is driving it?
3. Cross-check: is the dropping segment newly acquired?
4. Test hypotheses against the data; don't guess.

### "Help me audit our instrumentation"
1. Pull the event inventory (last 30 days, all events fired ≥10x).
2. Tag PII risk, naming inconsistency, gaps.
3. Identify the events that should be fired but aren't.
4. Build the remediation backlog with owners.

## Anti-patterns to avoid

- **More dashboards = more insight.** Usually inverse. Cull aggressively.
- **Confusing event volume for insight.** Tracking everything badly is worse than tracking a few things well.
- **PII in event properties.** Privacy + compliance nightmare.
- **Custom event names per developer.** Naming convention or chaos.
- **No event documentation.** Future you and the next analyst will hate present you.
- **One metric for the whole product.** Different surfaces need different metrics.
- **Vanity North Star.** "Total signups" tells you nothing about value.

## Scope & Limitations

**In Scope:**
- North Star and metric tree design (North Star, inputs, drivers, guardrails), checked by `metric_tree_designer.py` for imbalance, unowned metrics, vanity North Stars and missing guardrails
- Event taxonomy audits with `event_taxonomy_auditor.py` for naming consistency, PII risk, duplication, undocumented events and gaps, with a remediation backlog
- Retention cohort analysis with `retention_cohort_analyzer.py`: retention rates, trend and curve shape (smile, slow decay, leaky bucket, steep, rising)
- Activation definition, vanity versus actionable metric tests, and the reference guides on instrumentation and funnel analysis

**Out of Scope:**
- Building data pipelines, warehouse models or dbt projects (see `data-analytics/analytics-engineer/`)
- Designing and analyzing A/B tests (see `product-team/ab-test-setup/`)
- Building BI dashboards in a specific tool (see `data-analytics/business-intelligence/`)
- Ongoing data quality monitoring (see `engineering/data-quality-auditor/`)
- Legal review of personal data in events (see `ra-qm-team/gdpr-dsgvo-expert/`)

**Important Caveats:**
- The tools have no connection to Amplitude, Mixpanel, GA4, Segment or a warehouse. Event inventories, metric trees and cohort counts are supplied as JSON.
- PII detection matches property names against a keyword list and the declared PII tier. It can miss personal data stored under neutral names.
- Curve-shape and trend labels come from fixed thresholds. They point to where to look and do not prove product-market fit or its absence.

## References

- `references/metric-tree-and-north-star.md` — patterns by product type, tree structure, anti-patterns
- `references/instrumentation-and-event-design.md` — event taxonomy, naming, PII, schema discipline
- `references/cohort-retention-and-funnel-analysis.md` — analysis techniques, segmentation, anti-patterns

## Related skills

- `product-team/ab-test-setup` — experimentation (paired with metrics)
- `product-team/product-strategist` — strategy upstream of metrics
- `data-analytics/` skills — for the data engineering side
- `engineering/data-quality-auditor` — for instrumentation data quality
- `c-level-advisor/chief-data-officer-advisor` — for platform decisions
