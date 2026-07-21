---
name: procurement-optimizer
description: >
  Cut software and services spend through seat-utilisation analysis, redundant-tool
  detection, and renewal-timing leverage. Use when auditing SaaS spend, preparing a
  renewal negotiation, or hunting a budget-reduction target.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-operations
  domain: procurement
  updated: 2026-07-21
  tags: [saas-spend, procurement, license-optimization, vendor-negotiation, renewals]
---

# Procurement Optimizer

Most software spend reduction is not a negotiation problem. It is a measurement problem:
organisations buy seats in round numbers, assign them generously, and never look at whether
anyone logs in. The typical mid-size portfolio carries 20-30% reclaimable seat spend before
anyone talks to a vendor, and the reclaim requires no concession from the vendor at all.

This skill works the levers in order of yield: **stop paying for unused seats**, then
**stop paying twice for the same capability**, then **negotiate price**. Reversing that
order — leading with a price negotiation on a bloated contract — is how organisations
congratulate themselves on a 10% discount against 40% more seats than they need.

## When to use this skill

- A **budget-reduction target** has landed and software spend is in scope
- A **renewal is approaching** and you need a defensible position before the vendor call
- **SaaS sprawl audit**: nobody can say how many tools the company pays for
- **Post-merger consolidation** where two portfolios overlap heavily
- Building a **renewal calendar** so contracts stop auto-renewing unexamined
- A vendor has proposed an **uplift** and you need leverage to counter it

## Inputs the skill expects

- **Spend inventory**: tool, category, annual cost, renewal date, contract term
- **Seat data**: purchased, assigned, and — critically — *active in the last 30 days*
- **Contract terms**: notice period, auto-renew flag, term length
- **Criticality** per tool, and whether a capability alternative exists
- **Headcount**, for per-head benchmarking
- The **as-of date**, so renewal-window maths is reproducible

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Whether seat data is assigned or active** — this is the single most consequential input. Assigned seats overstate usage by 30-60%, and an analysis built on them finds almost nothing
- [ ] **Notice periods and auto-renew flags** — a contract inside its notice window is committed for another full term, so its "savings" are not available this cycle and must not be counted toward a target
- [ ] **Whether the goal is in-year cash or run-rate reduction** — seat cuts at renewal reduce run-rate but may deliver nothing this fiscal year, which is the wrong answer to an in-year cash problem
- [ ] **Which tools are politically untouchable** — if the CRM is the CRO's and cannot be cut, that changes which opportunities are worth analysing at all

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Find the wasted seats

Start here always. It requires no vendor conversation and no cross-team negotiation.

1. Assemble the inventory with purchased / assigned / **active-30-day** seat counts. If you
   only have assigned counts, stop and get active counts — the analysis is not meaningful
   without them.
2. Run the analyser. It compares active utilisation against a per-category benchmark (an LMS
   is not used weekly; a CRM is) and sizes reclaimable spend with a 12% safety buffer.
3. Separate the two failure modes it reports. **Over-licensed** means cut seats.
   **Adoption failure** means seats are assigned to people who never log in — cutting seats
   there treats the symptom, and the tool may simply not deserve to survive.

```bash
python3 business-operations/procurement-optimizer/scripts/license_utilization_analyzer.py \
  --input business-operations/procurement-optimizer/assets/sample_spend.json --format text
```

### Workflow 2 — Find the tools you are paying for twice

1. Run the overlap detector. It groups by category and picks a survivor by **displacement
   cost**, not by price — moving 400 active users is expensive regardless of licence cost.
2. Check the umbrella-label warnings first. If it flags a category as an umbrella, your
   tagging is claiming that a wiki and a chat tool are substitutes. Re-tag by the job the
   tool does and re-run before believing any number in the output.
3. Treat the recovery figure as net of an assumed 20% migration cost. Consolidations that
   look marginal at 20% are usually negative in reality once you count the disruption.

```bash
python3 business-operations/procurement-optimizer/scripts/tool_overlap_detector.py \
  --input business-operations/procurement-optimizer/assets/sample_spend.json --format text
```

### Workflow 3 — Rank the opportunities against the renewal calendar

1. Run the ranker with an explicit `--as-of`. It discounts each opportunity by how much
   leverage the renewal timing actually gives you this cycle.
2. Work the shortlist top-down. Time-boxed items (inside the notice window or in the ideal
   T-120 to T-90 negotiation window) are promoted above higher-ROI items on distant renewals,
   because missing a window costs a full contract year.
3. Read the `locked_this_cycle` figure to leadership before committing to a savings number.
   It is the portion of the opportunity that is genuinely unavailable this year, and
   discovering it after committing to a target is a bad conversation.

```bash
python3 business-operations/procurement-optimizer/scripts/savings_opportunity_ranker.py \
  --input business-operations/procurement-optimizer/assets/sample_spend.json \
  --as-of 2026-07-21 --top 10 --format text
```

## Decision frameworks

### Utilisation benchmarks by category [RECOMMENDED]

Active seats in the last 30 days, divided by seats purchased. A single flat benchmark is the
most common analytical error here — it flags an LMS as catastrophically wasteful when quarterly
use is its normal pattern.

| Category | Healthy active utilisation | Why |
|----------|---------------------------|-----|
| Security / identity | 90% | Near-universal deployment; unused seats are pure waste |
| CRM, chat, support desk | 85% | Daily-use tools with a defined user population |
| Developer tools | 80% | Daily use, but contractor churn creates real slack |
| Finance systems | 80% | Small, well-defined user set |
| Design | 70% | Licence-heavy tools with occasional-use viewers |
| Product analytics | 60% | Genuine long tail of occasional queriers |
| Legal / contract tools | 55% | Episodic use by a small team |
| Knowledge base | 50% | Read-heavy; many users read without a seat action |
| Whiteboard | 40% | Bursty, workshop-driven usage |
| LMS / HR training | 40% | Quarterly or annual cadence by design |

### Renewal timing and leverage [PROVEN]

| Window | Leverage | What to do |
|--------|----------|-----------|
| T-180d and earlier | Low | Too early. Vendors will not discount against a distant renewal. Calendar the opening |
| **T-120d to T-90d** | **Highest** | The ideal window. Open here. You have time to run an alternative evaluation, and the vendor's quarter-end pressure is still ahead of them |
| T-90d to T-60d | Moderate | Workable, but expect to trade term length for price |
| T-60d to notice deadline | Low | Serve notice to preserve optionality even if you intend to renew. Notice is not termination |
| Inside notice on auto-renew | None | Committed for another term. Plan the next cycle |

The most valuable single practice in software procurement is **serving notice by default** on
every auto-renewing contract at the notice deadline. It converts an automatic renewal into a
negotiation and costs nothing — vendors do not walk away from customers who serve notice, they
schedule a call. Organisations that do not do this are negotiating with no alternative and the
vendor knows it.

### Which lever to pull

| Situation | Lever | Typical yield |
|-----------|-------|---------------|
| Utilisation below benchmark | Seat reduction at renewal | 20-40% of that contract |
| Utilisation healthy, price above market | Price concession | 5-12% |
| Two tools, same job, both under-used | Consolidation | 60-80% of the displaced tool, net of migration |
| Seats assigned but nobody logs in | Fix adoption or kill the tool | 0% or 100% — there is no middle |
| Multi-year term offered for a discount | Usually decline | See the anti-pattern below |

## Anti-Patterns

### Counting Assigned Seats as Usage
**Mistake:** Building the utilisation analysis on seats assigned rather than seats active.
**Why it happens:** Assigned counts are what admin consoles show on the front page; active
counts often require an export or an API call.
**Instead:** Insist on 30-day active counts before running any analysis. Assigned seats
overstate real usage by 30-60% in typical portfolios, which is precisely the range of the
savings you are looking for — an analysis on assigned seats finds nothing and concludes the
portfolio is efficient.

### The Multi-Year Discount Trap
**Mistake:** Accepting a 15% discount for a three-year commitment on a tool with 40% unused seats.
**Why it happens:** The discount is concrete, immediate, and easy to report as a win. The
locked-in waste is diffuse and shows up in someone else's quarter.
**Instead:** Right-size the seat count first, then evaluate the multi-year offer against the
corrected baseline. A 15% discount on 40% too many seats is a 26% price increase wearing a
discount's clothing. Multi-year terms are worth taking only on tools you are certain of, where
utilisation is already healthy, and where the discount exceeds 20%.

### Negotiating Without Serving Notice
**Mistake:** Opening a renewal conversation while the contract is set to auto-renew.
**Why it happens:** Serving notice feels adversarial, and nobody wants to trigger an escalation
with a vendor they intend to keep.
**Instead:** Serve notice at the deadline as standard practice on every auto-renewing contract.
It is a procedural step, not a threat, and vendors treat it as one. Without it you have no
alternative to the renewal and no leverage, and the vendor's account team knows your notice
window better than you do.

### Consolidating on Price Instead of Displacement Cost
**Mistake:** Keeping the cheaper of two overlapping tools.
**Why it happens:** The licence cost is the visible number and the comparison is easy.
**Instead:** Keep the tool with more active users and higher criticality, even if it costs more.
Migrating 400 active users costs far more in lost productivity and support load than the annual
licence difference — and consolidations that displace the incumbent frequently fail outright,
leaving you paying for both tools plus the migration.

### Counting Locked Savings Toward This Year's Target
**Mistake:** Reporting the full portfolio opportunity as the savings commitment.
**Why it happens:** The gross number is bigger, and renewal-window nuance is hard to explain.
**Instead:** Report gross opportunity, realisable-this-cycle, and locked separately. Contracts
inside their notice window on auto-renew are committed for another full term; their savings are
real but arrive next year. Committing to a number that includes them guarantees a miss, and it
is a miss you can see coming from the day you commit.

## Files

| File | Purpose |
|------|---------|
| `scripts/license_utilization_analyzer.py` | Scores seat utilisation against category benchmarks and sizes reclaimable spend |
| `scripts/tool_overlap_detector.py` | Groups the portfolio by category, picks consolidation survivors by displacement cost, flags umbrella labels |
| `scripts/savings_opportunity_ranker.py` | Ranks opportunities by ROI per day, discounted by renewal-window leverage; builds the renewal calendar |
| `references/saas-negotiation-levers.md` | Negotiation levers, vendor tactics and counters, discount benchmarks, contract clauses |
| `references/utilization-benchmarks.md` | Per-category benchmarks, spend-per-head ranges, measurement methodology |
| `assets/spend-audit-report-template.md` | Report template for presenting findings and a committed savings number |
| `assets/renewal-negotiation-brief.md` | Pre-call brief template: position, targets, walk-away, concession ladder |
| `assets/sample_spend.json` | Runnable inventory used by all three scripts |
