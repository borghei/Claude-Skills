---
title: Research Ops Skills
description: Applied, operational research — market sizing, product discovery operations, clinical study operations, and research budgeting. Running research as a funded, staffed, repeatable function, with stdlib Python tools that state their assumptions.
---

# Research Ops Skills

**4 skills** with **12 stdlib-only Python tools** for running research as an operational function.

This domain covers **applied, operational** research — research as something funded, staffed, and repeatable. It is deliberately distinct from the academic `research/` domain (litreview, grants, patent, dossier), which covers scholarly synthesis and intelligence work.

Rule of thumb: **`research/` answers *what is known*; `research-ops/` answers *how we run studies to find out, and what they cost*.**

!!! info "New domain (July 2026)"
    Statistical scripts state their method in the output (`method_note`) and warn on inputs that invite misuse — zero dropout, an SD taken from a small pilot, thin cells — rather than silently computing.

## Skills

### market-research — Market sizing and structure

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/research-ops/market-research){ .md-button }

Applied market research for people who have to defend a number in a room: constructing a market size two independent ways, reconciling the gap, cutting the market into segments that behave differently, and fielding instruments that do not manufacture the answer you hoped for.

**Workflows:**

- Build and reconcile TAM/SAM/SOM → `tam_sam_som_builder.py` (top-down filter chain with retention fractions and justifications, independent bottom-up chain, layer-by-layer reconciliation, divergence flags)
- Triangulate demand signals → `demand_signal_triangulator.py` (source independence and directional strength; surfaces contradicting signals rather than averaging them away)
- Audit a survey before fielding → `survey_instrument_auditor.py` (leading language, double-barrelled items, absolutes, unbalanced scales, missing escape options, required-n from population and target margin of error)

**Use when:** sizing a market for a board deck or investor memo, reconciling an inherited TAM against a bottom-up build, segmenting before a pricing or GTM decision, triangulating demand, designing a survey, or auditing someone else's sizing before signing off.

### product-research — Product discovery operations

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/research-ops/product-research){ .md-button }

The operational layer of continuous discovery: choosing a method that answers the question actually asked, recruiting without poisoning the sample, and converting session notes into insights with an honest confidence attached.

**Workflows:**

- Pick the method → `method_recommender.py` (question classified generative / evaluative / descriptive, plus reversibility, timeline, participant access; returns a primary method, a cheaper fallback, minimum sample, and the methods ruled out with reasons)
- Validate the screener → `screener_validator.py` (transparent qualifying answers, missing disqualification logic, professional-respondent exposure, quota coverage, criteria no item tests)
- Score insight confidence → `insight_confidence_scorer.py` (weights observed behaviour above reported opinion, rewards source and participant diversity, penalises single-session or single-channel claims)

**Use when:** a team is about to build on three sales anecdotes, someone has asked for "a survey" before writing down the question, designing a screener where the wrong participants would be worse than no study, running a guide consistently across sessions, synthesising with a defensible confidence level, or standing up a continuous discovery cadence.

### clinical-research — Clinical study operations

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/research-ops/clinical-research){ .md-button }

Operational support for running clinical studies: structuring a protocol so it survives review, choosing analysable endpoints, designing eligibility that does not strangle accrual, planning sample size and power, and testing whether the site network can deliver the enrolment target.

!!! warning "Scope and limits"
    This skill supports **study operations planning** — structuring, sizing, and auditing. It does not replace a qualified biostatistician, medical monitor, or regulatory affairs sign-off. The sample-size calculator assumes a simple parallel design with no interim analyses, multiplicity adjustment, covariate adjustment, or clustering, and reports its method in every result; it is a planning aid, not a submission artefact. Every artifact produced here needs qualified biostatistics, clinical, and regulatory sign-off before it enters a submission. For regulatory submission and quality-system work, see [Compliance](compliance.md).

**Workflows:**

- Plan sample size and power → `sample_size_calculator.py` (endpoint type selects the formula; reports analysed n and enrol n separately, or achieved power from a fixed `planned_n_per_group`)
- Audit a protocol outline → `protocol_auditor.py` (ICH E6 element coverage, endpoints that cannot be analysed as written, conflicting or duplicated eligibility criteria, statistical and safety gaps)
- Test the site network → `site_feasibility_scorer.py` (discounts self-reported accrual estimates, blends historical attainment, caps against eligible population, subtracts startup time; `--select` tests a smaller high-quality site set)

**Use when:** planning a study and needing a defensible sample size before budget and site count, auditing a draft protocol before ethics or sponsor review, choosing between candidate endpoints, seeing the accrual cost of each eligibility restriction, assessing site feasibility, or diagnosing an under-accruing study.

### research-finance — Research budgeting and portfolio funding

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/research-ops/research-finance){ .md-button }

The money side of research operations: building a budget that funds what the study will actually consume, tracking spend against delivery rather than against the calendar, and deciding which research to fund when the portfolio asks for more than the budget holds.

**Workflows:**

- Build a study budget → `study_budget_builder.py` (four cost blocks — per participant, per site, per site-month, fixed; costs incurred on screened rather than enrolled participants; contingency and overhead; cost per enrolled participant and cost per insight)
- Track burn against delivery → `burn_vs_milestone_tracker.py` (work-weighted milestones, earned value, cost and schedule performance, estimate at completion — the spend-versus-delivery gap, not spend-versus-calendar)
- Prioritise the portfolio → `portfolio_prioritizer.py` (expected decision value, reversibility discount, zeroes out studies arriving after the decision, greedy allocation against `--budget`)

**Use when:** costing a study before a funding request, answering "what does this cost per participant", tracking a programme mid-flight, forecasting an overrun early enough to descope, prioritising a portfolio that exceeds its budget, or defending a research budget to a finance partner.

## Quality standard

Each skill in this domain:

- Uses stdlib-only Python (no external dependencies)
- Supports both JSON and human-readable output (`--format` flag)
- States the statistical or methodological assumption behind every number
- Warns on inputs that produce misleading results rather than silently computing
- Separates what the evidence supports from what it merely suggests

## Related skills

- **[Research](research.md)** — the academic counterpart: literature review, grants, patent, intelligence dossiers (*what is known*, rather than *how we run studies*)
- **[Product Team](product.md)** — `research-summarizer` for synthesising findings, `product-analytics` for behavioural product data
- **[`data-analytics/statistical-analyst`](https://github.com/borghei/Claude-Skills/tree/main/data-analytics/statistical-analyst)** — general applied statistics and test choice
- **[Compliance](compliance.md)** — regulatory submission and quality systems
- **[Business & Sales](business.md)** — `competitive-teardown` for competitive positioning (a different lens on the market)
