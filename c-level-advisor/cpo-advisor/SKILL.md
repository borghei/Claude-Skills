---
name: cpo-advisor
description: >
  Strategic product leadership for scaling companies. Covers product vision, portfolio
  strategy, product-market fit measurement, product org design, north star metrics,
  investment postures, and board-level product reporting. Not for feature-level work --
  for the decisions that determine what gets built, why, and by whom. Use when setting
  product vision, managing a product portfolio, measuring PMF, designing product teams,
  prioritizing at portfolio level, or when user mentions CPO, product strategy, PMF,
  product organization, portfolio prioritization, roadmap strategy, north star metric,
  or product-led growth.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: c-level
  domain: cpo-leadership
  updated: 2026-03-09
  frameworks:
    - pmf-playbook
    - product-strategy
    - product-org-design
    - portfolio-management
    - north-star-framework
    - investment-posture
  triggers:
    - CPO
    - chief product officer
    - product strategy
    - product vision
    - product-market fit
    - PMF
    - portfolio management
    - product organization
    - roadmap strategy
    - product metrics
    - north star metric
    - retention curve
    - product trio
    - team topologies
    - JTBD
    - jobs to be done
    - product-led growth
    - PLG
    - product board reporting
    - invest maintain kill
    - feature prioritization
    - product portfolio
  cross-references:
    - c-level-advisor/ceo-advisor
    - c-level-advisor/cto-advisor
    - c-level-advisor/cmo-advisor
    - c-level-advisor/cro-advisor
    - product-team/product-strategist
    - product-team/ux-researcher
---

# CPO Advisor

Strategic product leadership. Vision, portfolio, PMF, org design, and metrics. Not for feature-level work -- for the decisions that determine what gets built, why, and by whom.

## Keywords

CPO, chief product officer, product strategy, product vision, product-market fit, PMF, portfolio management, product org, roadmap strategy, product metrics, north star metric, retention curve, product trio, team topologies, jobs to be done, JTBD, category design, product positioning, board product reporting, invest-maintain-kill, BCG matrix, switching costs, network effects, product-led growth, PLG, feature adoption, time to value, activation rate

---

## The CPO Owns Three Things

Everything else is delegation.

| Ownership | What It Means | Key Question |
|-----------|--------------|--------------|
| Portfolio | Which products exist, which get investment, which get killed | "If we could only fund 2 of our 4 products, which 2?" |
| Vision | Where the product goes in 3-5 years and why customers care | "What does the world look like if we succeed?" |
| Organization | The team structure that can execute the vision | "Can this org ship the next 12 months of strategy?" |

---

## Product-Market Fit Assessment

### PMF Scoring Matrix

| Dimension | Weight | Score 1-3 (Weak) | Score 4-6 (Emerging) | Score 7-10 (Strong) |
|-----------|--------|-----------------|---------------------|---------------------|
| Retention | 30% | D30 < 15% (consumer) or < 40% (B2B) | D30 15-30% / 40-60% | D30 > 30% / > 60% |
| Engagement | 25% | DAU/MAU < 15% | DAU/MAU 15-35% | DAU/MAU > 35% |
| Satisfaction | 25% | Sean Ellis < 25% "very disappointed" | 25-40% | > 40% |
| Growth | 20% | No organic growth | Some organic, mostly paid | > 50% organic |

### PMF Decision Tree

```
START: "Do we have PMF?"
  |
  v
[Check retention curve shape]
  |
  +-- Declining to zero --> NO PMF. Stop building. Talk to users.
  |
  +-- Declining but flattening --> EMERGING. Find the segment where it's flat.
  |
  +-- Flat or smiling --> [Check Sean Ellis score]
                          |
                          +-- < 25% "very disappointed" --> Weak PMF. Product is nice, not essential.
                          |
                          +-- 25-40% --> Moderate PMF. Find and double down on power users.
                          |
                          +-- > 40% --> [Check organic growth]
                                        |
                                        +-- < 30% organic --> PMF exists but distribution is weak.
                                        +-- > 30% organic --> STRONG PMF. Scale.
```

### Post-PMF Traps

| Trap | Description | Prevention |
|------|-------------|------------|
| Feature creep | Adding features for new segments dilutes core value | Maintain a "jobs" focus, not feature focus |
| Premature scaling | Scaling sales/marketing before retention proves sustainable | Prove 3+ cohorts retain before scaling spend |
| Metric vanity | Celebrating signups while ignoring retention | North star must be a retention/engagement metric |
| Founder departure from product | CEO stops talking to customers post-PMF | Monthly customer conversations are permanent |
| Platform too early | Building platform capabilities before core is solid | Platform only after 3+ products need shared infra |

---

## Portfolio Management

### Investment Posture Framework

Every product gets exactly one posture. "Wait and see" is a decision to lose share.

| Posture | Signal | Resource Allocation | Review Cadence |
|---------|--------|-------------------|----------------|
| **Invest** | High growth, strong/improving retention, clear PMF | Full team, aggressive roadmap, dedicated marketing | Monthly |
| **Maintain** | Stable revenue, slow growth, good margins | Bug fixes, incremental improvement, minimal new features | Quarterly |
| **Harvest** | Declining growth, still profitable, no recovery path | Minimal investment, maximize cash extraction | Quarterly |
| **Kill** | Declining, negative margins, no recovery evidence | Set sunset date, migration plan, team reallocation | Immediate |

### Portfolio Health Scorecard

| Metric | Healthy | Unhealthy |
|--------|---------|-----------|
| % revenue from "Invest" products | > 60% | < 40% |
| % engineering on "Kill" candidates | < 10% | > 20% |
| Number of products without clear posture | 0 | > 1 |
| Portfolio D30 retention (weighted) | Improving QoQ | Declining QoQ |
| # of "question marks" > 2 quarters | 0 | > 2 |

### Portfolio Review Process

```
Quarterly Portfolio Review (Half-day workshop)

Step 1: Data Preparation (pre-meeting)
  - Revenue, growth rate, retention, margin per product
  - Engineering investment % per product
  - Customer satisfaction per product

Step 2: BCG Classification
  - Plot each product on Growth Rate (Y) vs Market Share (X)
  - Stars: high growth, high share --> Invest
  - Cash Cows: low growth, high share --> Maintain/Harvest
  - Question Marks: high growth, low share --> Invest or Kill (decide now)
  - Dogs: low growth, low share --> Kill

Step 3: Investment Allocation
  - Align engineering capacity to posture
  - Reallocate from Kill/Harvest to Invest
  - Set clear milestones for Question Marks (90-day decision point)

Step 4: Communication
  - Share portfolio decisions with all product teams
  - Update roadmaps to reflect postures
  - Communicate sunset plans for Kill products
```

---

## North Star Metric Framework

### Selection Criteria

The north star metric must satisfy ALL of these:

| Criterion | Test |
|-----------|------|
| Measures customer value | Does improvement mean customers got more value? |
| Leading indicator | Does it predict future revenue? |
| Actionable | Can product teams influence it? |
| Single number | Can you state it as one metric? |
| Non-gameable | Is it hard to improve without genuinely helping customers? |

### North Star by Business Model

| Model | North Star | Why It Works |
|-------|-----------|-------------|
| B2B SaaS | Weekly active accounts using core feature | Combines adoption + engagement + stickiness |
| Consumer social | Daily content creators | Creators drive consumer engagement |
| Marketplace | Successful transactions per week | Both sides active = healthy marketplace |
| PLG | Accounts reaching activation within 14 days | Activation predicts retention |
| Data/Analytics | Queries per active user per week | Usage intensity = value received |
| Fintech | Monthly active transactors | Transaction activity = core value |
| E-commerce | Repeat purchase rate (90-day) | Retention is everything in commerce |

### Metrics Hierarchy

```
North Star Metric (1, owned by CPO)
  |
  +-- Leading Indicator 1 (owned by PM Team A)
  |     e.g., Activation rate within 7 days
  |
  +-- Leading Indicator 2 (owned by PM Team B)
  |     e.g., Feature X adoption rate
  |
  +-- Leading Indicator 3 (owned by PM Team C)
  |     e.g., D7 retention rate
  |
  +-- Guard Rail Metrics (owned by CPO)
        e.g., NPS, support ticket volume, revenue per user
```

---

## Product Organization Design

### Team Topology Selection

| Topology | When to Use | Optimal Size | Communication |
|----------|------------|-------------|---------------|
| Stream-aligned | Default. Teams own end-to-end customer journey. | 5-9 people | Low cross-team dependency |
| Platform | Shared infrastructure multiple streams need | 4-8 people | API-first, self-service |
| Enabling | Temporary teams to upskill stream teams | 2-4 people | Coaching mode, time-limited |
| Complicated subsystem | Deep specialist domain (ML, payments) | 3-6 people | Provides service to streams |

### Product Team Ratios

| Company Size | PM : Engineers | PM : Designer | Total Product Team |
|-------------|---------------|---------------|-------------------|
| 10-30 | 1:4-6 | 1:1 | 1 PM, 1 Designer, 4-6 Eng |
| 30-80 | 1:5-8 | 1:1-2 | 2-4 PMs, 2-3 Designers |
| 80-200 | 1:6-10 | 1:1-2 | 5-10 PMs, 4-6 Designers |
| 200+ | 1:8-12 | 1:2 | 10+ PMs, 8+ Designers |

### The Product Trio

Every product team should operate as a trio: PM + Designer + Tech Lead.

| Role | Owns | Decides |
|------|------|---------|
| PM | What to build and why | Prioritization, scope |
| Designer | User experience and usability | Interaction patterns, research |
| Tech Lead | How to build and technical feasibility | Architecture, implementation |

**Anti-pattern**: PM writes spec, hands to design, design hands to engineering. This is waterfall with agile labels.

---

## CPO Dashboard

| Category | Metric | Frequency | Target |
|----------|--------|-----------|--------|
| Growth | North star metric | Weekly | Improving MoM |
| Retention | D30 / D90 retention by cohort | Weekly | Flattening or improving |
| Acquisition | New activations | Weekly | Per plan |
| Activation | Time to first value | Weekly | Decreasing |
| Engagement | DAU/MAU ratio | Weekly | > 30% (B2B) / > 20% (consumer) |
| Satisfaction | NPS trend | Monthly | > 40 |
| Portfolio | Revenue per product | Monthly | Aligned to posture |
| Portfolio | Engineering investment % per product | Monthly | Aligned to posture |
| Quality | Support tickets per 1K users | Monthly | Decreasing |
| Moat | Feature adoption depth | Monthly | Increasing |

---

## Red Flags

- Products stuck as "question marks" for 2+ quarters without a decision -- make the call
- Engineering allocated to highest-revenue product while highest-growth product is understaffed -- misallocation
- > 30% of team time on products with declining revenue -- sunk cost fallacy
- Retention curve never flattens -- no PMF, stop building features and start talking to users
- PMs writing specs without talking to users -- product theater
- Platform team has 6-week queue -- platform should be self-service, not a bottleneck
- CPO has not talked to a customer in 30+ days -- disconnected from reality
- North star trending up while retention trends down -- wrong metric
- Roadmap built from sales requests instead of user data -- sales-driven product is a trap
- No user research conducted in 90+ days -- team is guessing, not learning

---

## Integration with C-Suite

| When... | CPO Works With... | To... |
|---------|-------------------|-------|
| Company direction | CEO (`ceo-advisor`) | Translate vision into product bets |
| Roadmap funding | CFO (`cfo-advisor`) | Justify investment allocation per product |
| Scaling product org | COO + CHRO | Align hiring with product growth needs |
| Technical feasibility | CTO (`cto-advisor`) | Co-own features vs. platform trade-off |
| Launch timing | CMO (`cmo-advisor`) | Align releases with demand gen capacity |
| Sales-requested features | CRO (`cro-advisor`) | Separate revenue-critical from noise |
| Compliance deadlines | CISO (`ciso-advisor`) | Identify non-negotiable security items |
| Product strategy | Product Team (`product-team/`) | Execute strategy through product managers |
| User research | UX Research (`product-team/ux-researcher`) | Validate assumptions with data |

---

## Proactive Triggers

- Retention curve not flattening -- PMF at risk, stop feature work and investigate
- Feature requests piling up without prioritization framework -- propose RICE scoring
- No user research in 90+ days -- product team is building on assumptions
- NPS declining QoQ -- dig into detractor feedback, find the pattern
- Portfolio has a "dog" everyone avoids discussing -- force the kill/invest decision
- Engineering spending > 20% on a product with < 5% of revenue -- investment misalignment
- New competitor launched with similar positioning -- competitive response needed

---

## Output Artifacts

| Request | Deliverable |
|---------|-------------|
| "Do we have PMF?" | PMF scorecard across 4 dimensions with cohort data |
| "Prioritize our roadmap" | Scored backlog with framework (RICE/ICE), stack-ranked |
| "Evaluate our portfolio" | BCG map with invest/maintain/kill recommendations per product |
| "Design our product org" | Org proposal with topology, ratios, reporting, and transition plan |
| "Product board section" | Board slide: north star, retention, roadmap highlights, risks |
| "Set our north star" | North star proposal with hierarchy, leading indicators, and guard rails |
| "Kill a product" | Sunset plan: timeline, migration, communication, team reallocation |

---

## Tool Reference

### 1. product_portfolio_analyzer.py

Analyzes a product portfolio using BCG matrix classification (Star/Cash Cow/Question Mark/Dog), calculates portfolio health scores, identifies investment misalignment, and generates rebalancing recommendations.

```bash
python scripts/product_portfolio_analyzer.py --input portfolio.json --json
python scripts/product_portfolio_analyzer.py --input portfolio.json
```

| Flag | Type | Description |
|------|------|-------------|
| `--input` | required | Path to JSON file with products (revenue, growth rate, market share, engineering investment %, retention) |
| `--json` | optional | Output in JSON format instead of human-readable text |

### 2. feature_prioritizer.py

Prioritizes features using RICE scoring (Reach x Impact x Confidence / Effort). Supports custom weights, generates stack-ranked backlogs, and flags scoring anomalies.

```bash
python scripts/feature_prioritizer.py --input features.json --json
python scripts/feature_prioritizer.py --input features.json --method rice
```

| Flag | Type | Description |
|------|------|-------------|
| `--input` | required | Path to JSON file with features (reach, impact, confidence, effort, optional category) |
| `--method` | optional | Scoring method: `rice` (default), `ice`, or `weighted` |
| `--json` | optional | Output in JSON format instead of human-readable text |

### 3. product_health_scorer.py

Scores product health across 5 dimensions: retention (D30/D90), engagement (DAU/MAU), satisfaction (NPS/Sean Ellis), growth (organic %), and activation (time to value). Generates PMF assessment and trend analysis.

```bash
python scripts/product_health_scorer.py --input product_data.json --json
python scripts/product_health_scorer.py --input product_data.json
```

| Flag | Type | Description |
|------|------|-------------|
| `--input` | required | Path to JSON file with product metrics across retention, engagement, satisfaction, growth, and activation |
| `--json` | optional | Output in JSON format instead of human-readable text |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Products stuck as "question marks" for 2+ quarters | No decision framework or leadership avoidance | Force invest-or-kill decision at next portfolio review; set 90-day milestones with automatic kill trigger |
| Engineering allocated to highest-revenue product while highest-growth product starves | Investment posture not aligned to growth potential | Run portfolio analyzer to quantify misalignment; reallocate using BCG classification |
| RICE scores gamed by PMs inflating reach or impact | No calibration process or shared scoring standards | Require evidence for each score dimension; run quarterly calibration sessions across PM teams |
| North star metric trending up while retention trends down | Wrong north star metric selected or metric is gameable | Re-evaluate north star against the 5 selection criteria; add retention as a guard rail metric |
| Roadmap built from sales requests instead of user data | No structured intake process or CPO not filtering | Implement feature request triage; require user research evidence before roadmap inclusion |
| Platform team has 6-week queue blocking stream teams | Platform not self-service; too many dependencies | Redesign platform for self-service APIs; add enabling team to unblock highest-priority streams |
| No user research conducted in 90+ days | Research not embedded in team workflow or understaffed | Embed researcher in product trio; set minimum research cadence (2 studies per quarter minimum) |

---

## Success Criteria

- Every product has a clear investment posture (Invest/Maintain/Harvest/Kill) reviewed quarterly
- North star metric improving month-over-month for "Invest" products
- D30 retention flattening or improving for all active products
- Engineering investment percentage aligned to portfolio posture within 10% tolerance
- Feature prioritization uses a consistent scoring framework across all PM teams
- Time to first value decreasing quarter-over-quarter
- No product classified as "question mark" for more than 2 consecutive quarters

---

## Scope & Limitations

**In scope:** Product-market fit assessment, portfolio management (BCG classification, investment postures), north star metric framework, product organization design (team topologies, ratios, product trio), feature prioritization (RICE/ICE scoring), product health scoring, CPO dashboard metrics, and board-level product reporting.

**Out of scope:** Feature-level product management (use product-team/product-strategist), UX design and research execution (use product-team/ux-researcher), engineering implementation planning (use engineering/ skills), pricing strategy (use cro-advisor pricing section), and customer success management. Tools analyze product metrics snapshots; continuous product analytics requires integration with analytics platforms.

**Limitations:** PMF scoring depends on cohort-level retention data that early-stage products may not have. BCG classification requires market share estimates that are inherently imprecise. RICE scoring is subjective; quality depends on calibration rigor. Product health benchmarks vary significantly by business model (B2B vs consumer, SaaS vs marketplace).

---

## Integration Points

- **ceo-advisor** -- Product strategy translates CEO vision into product bets; portfolio health feeds board reporting
- **cto-advisor** -- Technical feasibility co-owned; features vs platform trade-off decisions require CTO partnership
- **cro-advisor** -- Sales-requested features filtered through CPO; expansion revenue depends on product roadmap
- **cmo-advisor** -- Launch timing aligned with demand gen capacity; product positioning informs marketing
- **cfo-advisor** -- Investment allocation per product justified with portfolio health data
- **product-team/** -- CPO strategy executed through product managers; research and prioritization cascade down
