---
title: Business Operations Skills
description: The internal operating layer of a company — capacity planning, process mapping, vendor lifecycle, internal communications, knowledge base health, and software spend optimisation. Each skill ships stdlib Python tools with real benchmarks and gate flags for CI.
---

# Business Operations Skills

**6 skills** with **18 stdlib-only Python tools** for the internal operating machinery of a company.

This domain covers how work capacity is planned, how processes run, how vendors and spend are managed, and how information and announcements move through the organisation. It is distinct from `c-level-advisor/` (strategic counsel at the executive altitude) and `project-management/` (delivery of specific initiatives) — this is the recurring operational layer underneath both.

!!! info "New domain (July 2026)"
    Every script accepts `--input <sample>.json --format {text,json}`, and several expose a gate flag (`--fail-on`, `--min-*`) that exits non-zero so the tool can run in CI or a scheduled review.

## Skills

### capacity-planner — Headcount and delivery capacity

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/business-operations/capacity-planner){ .md-button }

Turns headcount into hours you can actually commit. Computes effective capacity independently of the roadmap, matches it against risk-adjusted demand, and publishes the cut line.

**Workflows:**

- Model effective capacity → `capacity_model.py` (roster with real FTE and tenure, booked PTO, on-call, meeting load; effective-hours ratio checked against a sanity band)
- Find the cut line → `commitment_gap.py` (risk-adjusted demand in priority order, `--buffer-pct` for the unplanned-work reserve, below-the-line list as the deliverable)
- Compare hire / contract / defer → `scenario_compare.py` (four axes: time to relief, cost per delivered hour, reversibility, knowledge retention)

**Use when:** quarterly planning, testing whether a roadmap fits, building a hiring ask, choosing how to close a shortfall, mid-quarter replan, modelling onboarding impact.

### process-mapper — Process mapping and improvement

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/business-operations/process-mapper){ .md-button }

Turns "this takes forever and nobody knows why" into a measured map with a payback-ranked backlog. Built to prevent the two standard failures: mapping what people describe rather than what runs, and costing wait-time savings as if they were labour savings.

**Workflows:**

- Capture and measure → `process_analyzer.py` (SIPOC scope, median and 85th-percentile wait times, value-added classification, modelled vs measured lead time)
- Diagnose handoffs and rework → `handoff_analyzer.py` (handoff density, share of wait sitting at handoffs, system switches, ping-pong owners)
- Build the improvement backlog → `improvement_scorer.py` (touch minutes costed separately from lead minutes; payback tiers)

**Use when:** a process is slow and the responsible step is unknown, work bounces between teams, rework is high, before automating anything, onboarding onto an inherited process, or building an improvement backlog ranked by payback.

### vendor-management — Vendor lifecycle

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/business-operations/vendor-management){ .md-button }

Selection through exit. Built around preventing the two failures that dominate the discipline: tiering vendors by spend rather than by blast radius, and losing renewal leverage to a missed notice deadline.

**Workflows:**

- Select a vendor → `vendor_scorecard.py` (weights agreed before scoring, evidence-based 0-10 scores, stability check read before the ranking)
- Review the portfolio → `portfolio_analyzer.py` (derived notice deadlines, LOCKED renewals, single-vendor share and category HHI, unowned contracts)
- Run an SLA review → `sla_report.py` (committed metrics vs actuals, credit tiers against the contractual cap, prior-period trend)

**Use when:** selecting a vendor, a renewal is approaching, reviewing the portfolio for concentration and risk-tier coverage, preparing a business review, building an underperformance case on trend, or planning an exit.

### internal-comms — Internal communication strategy

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/business-operations/internal-comms){ .md-button }

Treats an announcement as an artifact with a blast radius, a sequence, and a pass/fail quality bar — not as a writing exercise. The three levers are who hears it in what order, what the message must contain, and which channel carries it.

**Workflows:**

- Audit a draft before it sends → `announcement_auditor.py` (five required elements, reading grade, jargon density, hedging; `--min-score` gate)
- Sequence a change communication → `comms_sequencer.py` (blast radius, impact-then-influence audience ordering, T-offsets, manager-enablement step)
- Pick the channel → `channel_fit_scorer.py` (six dimensions; ranks channels and names the disqualified ones)

**Use when:** announcing a reorg or leadership change, rolling out a policy people must act on, communicating a migration with a deadline, structuring a recurring all-hands or exec update, pressure-testing a draft, or choosing channel and cadence for a multi-week programme.

### knowledge-ops — Knowledge base health

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/business-operations/knowledge-ops){ .md-button }

Treats the KB as an operational system with owners, freshness SLAs, and a measurable health score. The core position: deletion is the highest-value action available — most struggling knowledge bases need 30% fewer pages, not more.

**Workflows:**

- Score KB health → `kb_health_auditor.py` (JSON inventory or `--root` over a markdown directory with YAML frontmatter; explicit `--as-of` for reproducibility)
- Find orphans, dead links, and duplicates → `orphan_detector.py` (link graph, unlinked pages, dead targets, hub pages; orphan-with-traffic and orphan-without-traffic need opposite fixes)
- Rank documentation debt → `doc_debt_ranker.py` (value from traffic × criticality × severity, against effort; do-now / schedule / batch / drop)

**Use when:** the wiki is large and distrusted, a doc audit is due before onboarding or a compliance review, search consistently returns the wrong page, large parts of the KB are unowned, planning a documentation-debt sprint, or migrating between wiki platforms.

### procurement-optimizer — Software and services spend

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/business-operations/procurement-optimizer){ .md-button }

Works the levers in order of yield: stop paying for unused seats, then stop paying twice for the same capability, then negotiate price. Most spend reduction is a measurement problem before it is a negotiation problem.

**Workflows:**

- Find the wasted seats → `license_utilization_analyzer.py` (active-30-day utilisation against per-category benchmarks; separates over-licensing from adoption failure)
- Find duplicate capability → `tool_overlap_detector.py` (survivor chosen by displacement cost, not price; umbrella-category warnings; recovery net of migration cost)
- Rank against the renewal calendar → `savings_opportunity_ranker.py` (`--as-of` renewal-window maths, time-boxed items promoted, `locked_this_cycle` reported before any target is committed)

**Use when:** a budget-reduction target lands on software spend, a renewal needs a defensible position, auditing SaaS sprawl, post-merger portfolio consolidation, building a renewal calendar, or countering a proposed uplift.

## Quality standard

Each skill in this domain:

- Uses stdlib-only Python (no external dependencies)
- Supports both JSON and human-readable output (`--format` flag)
- Carries real benchmark numbers and thresholds, not generic advice
- States an opinionated default with the escape hatch named
- Ships runnable sample data for every documented workflow

## Related skills

- **[Project Management](project-management.md)** — delivery of specific initiatives (this domain is the recurring operational layer beneath it)
- **[C-Level Advisory](c-level.md)** — `coo-advisor` for strategic operations counsel at the executive altitude
- **[Data, HR & Other](other.md)** — `hr-operations/` for people processes specifically
- **[Business & Sales](business.md)** — external commercial motion, and `finance/` for FP&A (procurement-optimizer covers spend, not planning)
