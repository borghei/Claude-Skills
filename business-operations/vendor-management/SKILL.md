---
name: vendor-management
description: >
  Vendor lifecycle — weighted selection scorecards, risk tiering, renewal and
  notice-deadline tracking, spend concentration, and SLA credits. Use when
  selecting a vendor, preparing a renewal, or reviewing a vendor portfolio.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-operations
  domain: procurement
  updated: 2026-07-21
  tags: [vendor-management, procurement, sla, renewal, third-party-risk]
---

# Vendor Management

Covers the vendor lifecycle from selection to exit. Two failures dominate this
discipline: tiering vendors by spend rather than by blast radius, and losing
every point of renewal leverage to a missed notice deadline. This skill is built
around preventing both.

## When to use this skill

- **Selecting a vendor** and needing a scorecard that survives scrutiny
- **A renewal is approaching** and the notice deadline needs to be found before it passes
- **Reviewing the vendor portfolio** for concentration, risk tier coverage, and consolidation
- **Preparing a business review** with SLA performance and credits owed
- **A vendor is underperforming** and the case needs to be built on trend, not anecdote
- **Planning an exit** and needing the sequence right

## Inputs the skill expects

- For selection: weighted criteria, must-have requirements, and 0-10 scores per vendor with evidence
- For the portfolio: annual spend, category, renewal date, notice days, and auto-renew flag per vendor
- Risk inputs per vendor: data classification, business criticality, alternative availability, subprocessor use
- Internal owner per contract
- For SLA reporting: committed metrics with target, actual, direction, credit tiers, and prior-period history
- Annual contract value and the contractual credit cap

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Is the notice deadline known, or only the renewal date?** — the notice deadline is what constrains action, and missing it removes all leverage for a full term
- [ ] **Were the scoring weights set before any vendor was scored?** — weights chosen after seeing candidates produce a justification, not a decision
- [ ] **What does this vendor actually hold or touch?** — data sensitivity and criticality drive the risk tier; spend does not
- [ ] **Which must-haves are genuinely pass/fail?** — every entry on that list eliminates a candidate, so preferences belong in the weighted criteria

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Select a vendor

1. Agree weighted criteria and the must-have list **before** looking at any candidate. Record who agreed them and when.
2. Define anchors for each criterion — what a 10 looks like and what a 5 looks like. This is what stops the scorecard becoming post-hoc justification.
3. Score each candidate against evidence (demo, reference call, document reviewed), not impression. Note the evidence in the scorecard.
4. Run the scorer and read the stability check before the ranking. A margin under 5% is a tie — decide it on commercial terms, exit cost, or reference calls instead.
5. If the result flips when a weight moves 50%, take that criterion back to the decision owner before proceeding.

```bash
python3 business-operations/vendor-management/scripts/vendor_scorecard.py \
  --input business-operations/vendor-management/assets/sample_vendor_candidates.json \
  --format text
```

### Workflow 2 — Review the portfolio

1. Build the vendor list with renewal date, notice days, and auto-renew flag. The notice deadline is derived, and it is the date that matters.
2. Set `as_of` explicitly so the analysis is reproducible and reviewable later.
3. Run the analyser and work the urgent renewals first — anything marked LOCKED has already lost its negotiating window for this term.
4. Check concentration in both forms: single-vendor share above 25-30% is a dependency, and category HHI tells you whether you have leverage or diversification.
5. Treat every unowned contract as a future auto-renewal. Assign an owner before anything else in the report.

```bash
python3 business-operations/vendor-management/scripts/portfolio_analyzer.py \
  --input business-operations/vendor-management/assets/sample_portfolio.json \
  --format text
```

### Workflow 3 — Run an SLA review

1. Collect committed metrics with target, actual, direction, and credit tiers. Include prior periods — the trend is the argument.
2. Run the report and check credits earned against the contractual cap. Credits exceeding the cap mean the remedy structure is too weak to change behaviour.
3. Claim the credits. Unclaimed credits are the norm, and most contracts require you to ask.
4. Escalate severe breaches to the contract owner, not the account manager — the account manager cannot change the terms that caused it.
5. Carry the findings into the renewal ask: credit tiers that bite, and a termination right after repeated breach.

```bash
python3 business-operations/vendor-management/scripts/sla_report.py \
  --input business-operations/vendor-management/assets/sample_sla.json \
  --format json
```

## Decision frameworks

### Risk tiering [PROVEN]

Score data sensitivity plus business criticality, then apply modifiers.

| Data classification | Points | | Business criticality | Points |
|--------------------|--------|---|---------------------|--------|
| PHI / health | 4 | | Critical (revenue stops in hours) | 4 |
| PII | 3 | | High (core function stops in a day) | 3 |
| Financial | 3 | | Medium (productivity loss) | 2 |
| Confidential | 2 | | Low (inconvenience) | 1 |
| Internal | 1 | | | |
| Public | 0 | | | |

Modifiers: no ready alternative +2 · network access to your systems +2 ·
subprocessors +1 · non-adequate jurisdiction +1 · vendor under 20 people +1.

| Total | Tier | Core obligations |
|-------|------|------------------|
| 8+ | **Tier 1 critical** | Annual security review, quarterly business review, **tested** exit plan, SLA with credits |
| 6-7 | **Tier 2 high** | Full questionnaire at onboarding, semi-annual review, documented exit plan |
| 4-5 | **Tier 3 moderate** | Short-form questionnaire, annual review, verified data export |
| Under 4 | **Tier 4 low** | Confirm what data it touches; nothing further |

**Tier by blast radius, not spend.** The $8K tool holding your entire customer
list outranks the $400K hosting contract holding nothing sensitive.

### Where renewal leverage comes from [PROVEN]

| Source | Worth | Requires |
|--------|-------|----------|
| A real alternative | 10-30% | 3-6 weeks of genuine evaluation, an internal sponsor willing to switch |
| Vendor fiscal timing | 10-25% | Knowing their year-end and aligning your close to it |
| Multi-year commitment | 10-20% | Price protection, exit-on-SLA-failure, and an increase cap — all three |
| Volume / consolidation | 15-30% | Real growth, not aspirational seat counts |
| Reference or case study | 5-15% | Marketing time, not money |
| Annual prepay | 5-10% | Cash-flow float, and a viability check first |

Not leverage: complaining about price, threatening to leave without an
alternative, escalating without a specific ask, or loyalty — long tenure lowers
vendor risk, which is why tenured accounts are often priced higher.

### Renewal calendar [PROVEN]

| Days before renewal | Action |
|--------------------|--------|
| 180 | Usage vs entitlement; confirm owner; decide renew / renegotiate / exit |
| 150 | Open the alternative evaluation if renegotiating seriously |
| 120 | First vendor conversation — signal expectations before they build the quote |
| 90 | **Notice deadline on most annual contracts. Serve notice if there is any doubt.** |
| 60 | Negotiate substance: price, increase cap, true-down, SLA credits, exit rights |
| 30 | Close; anything open now resolves in the vendor's favour |

Serving notice is not leaving — it converts an auto-renewal into a negotiation.

### Terms worth more than price [RECOMMENDED]

| Term | Target |
|------|--------|
| Annual increase cap | CPI, or 3-5% maximum |
| Seat true-down rights | At renewal, without penalty |
| Termination for SLA failure | Defined breach threshold, no penalty |
| Data export format | Open, documented, and tested |
| Subprocessor change notice | 30 days with an objection right |
| Assignment on acquisition | Consent required, or an exit right |

Seat true-down is the most valuable and least-requested term: nearly every SaaS
contract lets you add seats mid-term and forbids reducing them.

## Anti-Patterns

### Tiering by spend
**Mistake:** Applying diligence proportional to contract value — heavy scrutiny on the big infrastructure contract, a credit card and no questions for the $8,000 tool.
**Why it happens:** Procurement owns the process and procurement thresholds are denominated in money. Approval workflows trigger on spend because that is what finance systems can see.
**Instead:** Tier on data sensitivity and business criticality, with modifiers for substitutability and subprocessors. The small tool holding your customer list has a far larger blast radius than the large contract holding nothing sensitive, and it is exactly the one that gets bought on a card without a security review.

### Discovering the notice deadline after it passes
**Mistake:** Tracking renewal dates only, then finding at day 60 that the 90-day notice window closed a month ago and the contract has auto-renewed for another year.
**Why it happens:** Renewal dates are what contracts and calendars display. The notice deadline is a derived date nobody computes, and auto-renew clauses are written to be easy to miss.
**Instead:** Track both dates per contract, and treat the notice deadline as the real one. Serve notice at the deadline as routine on anything you intend to renegotiate — it reopens the contract without committing you to leave. An unowned contract is the one this happens to, so assign an internal owner to every vendor.

### The scorecard that ratifies a decision already made
**Mistake:** Choosing the vendor, then building a weighted scorecard whose weights and scores produce that vendor as the winner.
**Why it happens:** Rarely cynical. Someone forms a view during the demos, and weights get set afterwards with that view in the room — each individual weight feels defensible while the set of them is not.
**Instead:** Set and record the weights, with named anchors for what a 10 and a 5 look like, before any candidate is scored. Then run the sensitivity check: if the winner changes when one weight moves 50%, the result is an artifact of the weighting rather than a finding about the vendors, and the decision owner needs to see that before signing.

### Treating the SLA as a control
**Mistake:** Accepting a 99.9% uptime commitment with a 2% service credit and considering the risk managed.
**Why it happens:** The SLA exists, it has numbers in it, and it satisfies the checklist item. Nobody computes what the credit is actually worth against what an outage costs.
**Instead:** Price the remedy. A 2% credit on a $20K quarter is $400 for an outage that may cost you far more — that is a rounding error the vendor has already priced in, not a control. Negotiate tiered credits (5/10/25%), a cap above 20% of period fees, and a termination right after repeated breach. Losing the account changes vendor behaviour; credits do not. And measure availability against the error budget, not the percentage — missing 99.9% by half a point is nearly six times the permitted downtime.

## Files

| File | Purpose |
|------|---------|
| `scripts/vendor_scorecard.py` | Must-have gating, weighted scoring, cost-value ratio, and a weight-sensitivity check on the result |
| `scripts/portfolio_analyzer.py` | Renewal and notice-deadline tracking, derived risk tiers, HHI spend concentration, consolidation candidates |
| `scripts/sla_report.py` | SLA compliance with error-budget severity, credit tiers against the contractual cap, and multi-period trend |
| `references/vendor-risk-tiering.md` | Tiering model, per-tier obligations, onboarding diligence, concentration risk, monitoring signals, vendor distress indicators |
| `references/renewal-negotiation-leverage.md` | Renewal calendar, ranked leverage sources, terms beyond price, making SLAs bite, negotiation sequence, exit execution |
| `assets/vendor-selection-scorecard.md` | Selection deliverable: must-haves, weighted criteria with anchors, stability check, risk tier, commercial position |
| `assets/vendor-review-template.md` | Business review: SLA performance, usage vs entitlement, risk checks, renewal plan with milestone dates |
| `assets/sample_vendor_candidates.json` | Four candidates including one disqualified on a must-have and a near-tie between the top two |
| `assets/sample_portfolio.json` | Ten-vendor portfolio with a locked auto-renewal, an unowned contract, and a consolidation candidate |
| `assets/sample_sla.json` | Five metrics in both directions with credit tiers, a capped credit total, and a degrading trend |
