# Vendor Risk Tiering

How to decide how much diligence a vendor deserves, and what each tier obliges
you to do. Negotiation and renewal strategy live in
`renewal-negotiation-leverage.md`.

The governing principle: **tier by blast radius, not by spend.** The $8,000/year
tool holding your entire customer email list is a larger risk than the
$400,000/year hosting contract holding nothing sensitive. Spend-based tiering —
which is what most organisations default to because procurement owns the process
— systematically under-scrutinises small SaaS tools and over-scrutinises large
commodity contracts.

---

## 1. The tiering model

Score each dimension, sum, and read the tier.

### Data sensitivity

| Classification | Points | Definition |
|---------------|--------|------------|
| PHI / health data | 4 | Health records; triggers HIPAA-class obligations |
| PII | 3 | Identifiable personal data of customers or staff |
| Financial | 3 | Payment data, bank details, financial records |
| Confidential | 2 | Trade secrets, source code, unreleased plans, contracts |
| Internal | 1 | Ordinary business data, not public, low harm if leaked |
| Public | 0 | Already published or intended for publication |

### Business criticality

| Level | Points | Test |
|-------|--------|------|
| Critical | 4 | Revenue stops or customers are visibly affected within hours |
| High | 3 | A core function stops within a day; workaround is painful |
| Medium | 2 | Productivity loss; work continues by other means |
| Low | 1 | Inconvenience only |

### Modifiers

| Condition | Points |
|-----------|--------|
| No ready alternative (switching takes over 3 months) | +2 |
| Vendor uses subprocessors with your data | +1 |
| Vendor has network access to your systems | +2 |
| Vendor holds data in a jurisdiction with no adequacy arrangement | +1 |
| Vendor is pre-revenue, or under 20 employees | +1 |

### Resulting tiers

| Total | Tier | Meaning |
|-------|------|---------|
| 8+ | **Tier 1 — Critical** | Failure is a business-level event |
| 6-7 | **Tier 2 — High** | Failure is a serious operational incident |
| 4-5 | **Tier 3 — Moderate** | Failure is disruptive but contained |
| Under 4 | **Tier 4 — Low** | Failure is an inconvenience |

---

## 2. What each tier requires

| Obligation | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|-----------|--------|--------|--------|--------|
| Security questionnaire | Full, annual | Full, at onboarding + every 2 yrs | Short form | None |
| SOC 2 Type II or ISO 27001 | Required | Required | Preferred | Not required |
| Penetration test summary | Annual | At onboarding | No | No |
| Named internal owner | Executive | Director | Manager | Any |
| Business review cadence | Quarterly | Semi-annual | Annual | None |
| SLA with credits | Required | Required | Preferred | No |
| Documented exit plan | Required, **tested** | Required | Data export verified | No |
| Continuity / DR evidence | Required | Required | Preferred | No |
| Contract review by legal | Always | Always | Standard terms OK | Standard terms OK |
| Cyber insurance evidence | Required | Required | No | No |
| Breach notification clause | Under 24h | Under 72h | Standard | Standard |
| Right to audit | Required | Preferred | No | No |

**The single most-skipped obligation is the tested exit.** Most organisations
have an exit clause; almost none have ever exported the data and confirmed it is
usable. An untested exit plan is a document, not a capability — and you discover
which one you have during the vendor's outage or price increase, at the worst
possible moment.

Test Tier 1 exits annually: export the data, open it in something else, and
record how long it took and what was lost. The finding is usually that the export
omits history, attachments, or relationships, which is exactly the thing you
needed to know before the renewal negotiation.

---

## 3. Onboarding diligence by tier

### Tier 1 — before signature [PROVEN]

1. Security questionnaire returned and reviewed by a named security owner
2. SOC 2 Type II report read — **the exceptions section, not the opinion page**
3. Subprocessor list obtained and each one tiered in turn
4. Data-flow map: what leaves your environment, where it lands, who can read it
5. Exit plan written with an owner, an estimated timeline, and a data-format check
6. Continuity evidence: RTO/RPO commitments and the last DR test date
7. Reference calls with two customers of similar size — ask specifically about
   support responsiveness and the last incident
8. Financial viability check: funding stage, runway signals, ownership changes

The SOC 2 detail matters. A clean opinion with fourteen exceptions in the detail
is a common and easily missed signal. Reading the exceptions takes twenty
minutes and is the highest-yield step in the entire list.

### Tier 2 — before signature

Items 1, 2, 4, 5 above, plus one reference call.

### Tier 3

Short-form questionnaire; confirm a data export path exists.

### Tier 4

Confirm what data it touches. That is all — diligence beyond this costs more
than the risk it addresses.

---

## 4. Concentration risk

Two separate exposures, often confused.

### Single-vendor concentration

| Share of total vendor spend | Reading |
|----------------------------|---------|
| Above 30% | High dependency. Their price increase is your budget crisis. |
| 15-30% | Material. Ensure an alternative is at least identified. |
| Under 15% | Normal |

### Category concentration (Herfindahl-Hirschman Index)

Sum the squared percentage shares of spend by category.

| HHI | Band | Reading |
|-----|------|---------|
| Above 2500 | Concentrated | Deep relationships, high switching cost, strong per-vendor leverage |
| 1500-2500 | Moderate | Typical for a mid-size organisation |
| Below 1500 | Diverse | Low lock-in, but weak negotiating leverage everywhere and high admin overhead |

Neither extreme is correct. **Diverse portfolios feel safe and negotiate badly** —
spreading $300K across eight vendors means being a small account to all eight.
Concentration buys leverage at the cost of switching freedom; the judgement is
where you want that trade, category by category.

### Consolidation candidates

Three or more vendors in one category is a consolidation signal. Typical savings
from consolidating overlapping tools run **15-30% of combined spend**, from
volume tiering and eliminated duplicate seats.

Consolidate when: functionality genuinely overlaps, the surviving vendor covers
the union of needs, and switching cost is under one year of the saving.

Do not consolidate when: the tools serve genuinely different workflows despite
similar categories, or when consolidation creates a Tier 1 dependency where three
Tier 3 dependencies existed. Trading three replaceable vendors for one
irreplaceable one is a risk increase disguised as a saving — and it is a common
outcome of consolidation programmes measured purely on spend.

---

## 5. Ongoing monitoring

| Signal | Check | Frequency | Response |
|--------|-------|-----------|----------|
| SLA performance | Credits, breach trend | Per period | Trend beats incident — three declining periods is a pattern |
| Security posture | Report currency, new CVEs, breach news | Quarterly (T1/T2) | Re-run diligence on material change |
| Financial health | Funding, layoffs, ownership change | Quarterly (T1) | Acquisition or down-round triggers exit-plan review |
| Usage vs entitlement | Seats used vs paid | Quarterly | Reclaim unused seats before renewal, not after |
| Support quality | Ticket volume, escalation rate | Per period | Deterioration often precedes SLA breach |
| Roadmap alignment | Delivered vs promised | Semi-annual | Repeated slippage is a viability signal |

**Usage-versus-entitlement is the most reliably profitable check.** Seat counts
ratchet up during the year and are almost never reviewed downward before a
renewal quote is issued based on them. Checking quarterly typically recovers
10-20% of seat spend at renewal, and it must happen *before* the vendor's renewal
proposal, because the proposal anchors on current entitlement.

### Vendor distress signals

Escalate to an exit-plan review when two or more appear: unexplained senior
departures, support quality decline, roadmap slippage past two cycles, aggressive
multi-year prepay discounts, acquisition by a private-equity holder with a
roll-up history, or a sudden unwillingness to commit to SLAs they previously
accepted.

The prepay signal is worth naming specifically: a vendor abruptly offering deep
discounts for three-year upfront payment is often managing a cash problem. The
discount is real; so is the risk that you have prepaid a company that will not
be independent in eighteen months.
