---
name: deal-desk
description: >
  Deal desk: reviews, approves, and structures non-standard sales deals. Use when
  standing up a deal desk, building approval-threshold matrices, designing
  deal-review packets, routing deals, or auditing deals for compliance.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: commercial
  domain: business-growth
  updated: 2026-05-27
  tags: [deal-desk, sales-operations, discount-approval, commercial-operations, contract-review, deal-velocity, gtm]
---

# Deal Desk

End-to-end deal-desk operational practice: charter, approval thresholds, deal-review packet design, routing automation, velocity analysis, and the governance that turns "every deal is a snowflake" into "we close non-standard deals in 48 hours predictably."

This skill is provider-agnostic: works whether your CRM is Salesforce, HubSpot, Pipedrive, or homegrown. The patterns and decisions transfer.

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| Starting a deal-desk function from scratch | Yes — start with **charter design** |
| Reviewing existing deal-desk for slowness / inconsistency | Yes — use `scripts/deal_velocity_analyzer.py` + **bottleneck patterns** |
| Defining who can approve what discount / term | Yes — use **approval threshold matrix** + `scripts/discount_authority_router.py` |
| Building the deal-review packet template | Yes — see **deal-review packet** section + `scripts/deal_review_packet.py` |
| Approving / declining a specific deal | Use the packet generator + approval router |
| Setting pricing strategy | Use `business-growth/pricing-strategy` first |
| Forecasting / measuring pipeline | Use `business-growth/revenue-operations` |
| Negotiating an individual contract | Pair with `business-growth/contract-and-proposal-writer` |

---

## What deal desk does (and doesn't)

**Does:**
- Review non-standard deals: discounts beyond rep authority, custom legal terms, custom SLAs, multi-product bundles, payment terms outside policy
- Make the approval decision (or route to the right approver)
- Structure the deal: pricing, terms, ramp schedule, success criteria
- Maintain the deal-desk **policy** — what's standard, what needs approval
- Track deal velocity (time from request → decision → signature)
- Produce evidence for finance / audit (every concession traceable)

**Doesn't:**
- Set the published pricing (that's pricing strategy)
- Negotiate with the customer (that's the sales rep / AE)
- Close the sale (that's the rep + customer success)
- Run the order-to-cash workflow (that's billing / RevOps)
- Replace legal review (legal is one of the approvers, not the function itself)

A clean deal-desk = the lubricant. Without it, every non-standard deal turns into a multi-week negotiation among engineering / product / legal / finance / executive. With it, those people are consulted by deal desk as needed and the rep gets a yes/no in days.

---

## Deal-desk charter (template)

Every deal desk needs a written charter. Use this template:

```yaml
purpose:
  Deal Desk reviews, approves, and structures non-standard deals to enable
  sales to close faster while keeping commercial / legal / financial risk
  within company tolerance.

scope:
  In-scope:
    - All deals > $X ARR
    - All deals with discount > Y%
    - All deals with non-standard terms (custom SLAs, custom legal language,
      payment terms beyond Net 30, ramp deals, multi-year discounts > 12 months
      of standard, bundles spanning multiple product lines)
    - All renewals with > 20% expansion or > 10% contraction
    - All deals to enterprise (>1000 employees) or regulated industries
  Out-of-scope:
    - Self-serve / PLG transactions
    - Standard renewals within auto-renewal terms
    - Trial extensions < 30 days
    - Add-ons < $X per existing customer

sla:
  - Standard deal-desk review (no exec approval needed): 1 business day
  - Deal needing CFO/CRO approval: 2 business days
  - Deal needing CEO/Board approval: 5 business days
  - Legal-only review (no commercial concession): 2 business days

intake_format:
  Sales submits via [Salesforce form / CPQ tool / Slack form]. Required fields:
    - Customer name + size + industry
    - Product(s) + ACV
    - Requested deviation from standard (specific list)
    - Justification (competitor situation, customer constraint, strategic value)
    - Standard-pricing total + requested total
    - Contract length + payment terms
    - Implementation / SLA requirements

decision_inputs:
  - Customer LTV estimate
  - Strategic value (logo, reference, vertical foothold)
  - Risk (credit, compliance, integration)
  - Margin impact

outputs:
  - Approve / decline / counter
  - If approve: signed approval packet with terms, conditions, expiration date
  - If counter: list of negotiable items + non-negotiables
  - If decline: reasoning + alternatives

team:
  Deal-desk lead: <name>
  Deal-desk analysts: <names>
  Standing approvers: CRO, CFO, General Counsel, VP Product (escalation paths)
  Consulted as-needed: Engineering Lead, Security Lead, Customer Success Lead

metrics:
  - Median time-to-decision (target: 1 business day)
  - Decision distribution (% approved, % declined, % countered)
  - Discount-on-discount %  (deals where requested discount was further negotiated up)
  - Discount % vs ACV (correlation; outliers reviewed monthly)
  - Win rate of deal-desk-approved deals
  - Concession follow-through (did the customer keep their side?)
```

See [references/deal-desk-charter-and-process.md](references/deal-desk-charter-and-process.md) for the full charter template, including sub-charters per region, intake form spec, and the standard SLAs.

---

## Approval threshold matrix

The matrix defines: for each deal characteristic (discount %, contract length, custom term type), who can approve it.

### Standard matrix template

| Deal characteristic | Rep | Sales Manager | Director | VP Sales | CRO | CFO | CEO |
|---------------------|-----|---------------|----------|----------|-----|-----|-----|
| Discount 0-10% | ✓ | | | | | | |
| Discount 10-20% | | ✓ | | | | | |
| Discount 20-30% | | | ✓ | | | | |
| Discount 30-40% | | | | ✓ | | | |
| Discount 40-50% | | | | | ✓ | | |
| Discount > 50% | | | | | | | ✓ |
| ACV > $250k | | ✓ | | | | | |
| ACV > $1M | | | | ✓ | | | |
| ACV > $5M | | | | | | | ✓ |
| Multi-year > 12mo standard | | ✓ | | | | | |
| Non-standard payment terms | | | | | | ✓ | |
| Custom SLA / penalties | | | | (with CCO) | | | |
| Custom legal language | | | | | | | (Legal must concur) |
| MSA red-line on liability cap | | | | | | | (Legal must concur) |
| Most-favored-nation clause | | | | | | ✓ | |
| Acceptance criteria / payment-on-acceptance | | | | | | ✓ | |
| Multi-product / cross-BU bundle | | | (each BU lead approves) | | | | |
| Whitelabel / OEM rights | | | | | | | ✓ |

Customize per company stage, ACV distribution, and authority preference (some orgs want CRO at 30%, others delegate further down).

### Stacking rule

When multiple non-standard items apply, **the highest required approver applies.** A $1M deal at 25% discount with custom SLA needs VP Sales (ACV) AND Director (discount) AND VP Sales+CCO (custom SLA) → effectively requires VP Sales sign-off + CCO + Legal concurrence.

Use `scripts/discount_authority_router.py --deal deal.yaml` to compute the required approvers for any deal.

See [references/approval-thresholds-and-routing.md](references/approval-thresholds-and-routing.md) for the full matrix design guide, regional variants, escalation paths, and routing automation patterns.

---

## The deal-review packet

Every non-standard deal gets a packet. Without it, approvers ask the same questions repeatedly and decisions take days instead of hours.

### Standard packet structure

```markdown
# Deal Review: <Customer Name>

## Summary
- Customer: <name, size, industry>
- ACV: $<amount>
- Discount %: <%> (vs standard $<list-price>)
- Contract: <length>, <payment terms>
- Decision needed by: <date>

## Standard vs Requested
| Item | Standard | Requested | Delta |
|------|----------|-----------|-------|
| ACV  | $X       | $Y        | -Z%   |
| Term | 12mo     | 36mo      | +24mo |
| Payment | Net 30 | Net 60   | +30d  |
| SLA  | 99.5%    | 99.9%     | +0.4% |
| Liability cap | 1x fees | 2x fees | +1x |
| Termination for convenience | No | Yes (90d) | New |

## Justification
- Why customer wants this: <competitor situation, budget cycle, etc.>
- Why we're considering: <strategic value, logo, vertical>
- Customer leverage: <alternatives they have>

## Financial impact
- Standard ARR: $X
- Discounted ARR: $Y (Z% off)
- Net new gross margin: $A (with cost overlay)
- Projected LTV with this discount: $B
- Discount payback if customer renews: <years>

## Strategic value
- Logo value: <high/medium/low — reasoning>
- Reference value: <will they be a public ref? case study?>
- Vertical foothold: <do we want this vertical?>
- Competitive replacement: <who are we displacing?>

## Risk
- Credit risk: <score / payment history>
- Compliance risk: <regulated? data residency?>
- Technical fit risk: <integration complexity>
- Concession follow-through: <are they likely to honor commitments?>

## Required approvers (per matrix)
- [ ] Director: <name>
- [ ] VP Sales: <name>
- [ ] CFO: <name>
- [ ] Legal: <name>

## Recommendation (from deal desk)
<Approve / Counter / Decline> — with reasoning

## Conditions if approved
- Discount expires <date>
- Customer must agree to: <reference call, case study, etc.>
- Customer agrees this is single-instance (not precedent)
- Payment must close by <date>
```

Use `scripts/deal_review_packet.py --deal deal.yaml` to generate this packet from a deal spec.

---

## Velocity analysis

A slow deal desk strangles sales. Measure and tune.

### Key metrics

| Metric | Healthy | Warning |
|--------|---------|---------|
| Median time-to-decision | < 1 business day | > 3 days |
| 90th percentile time-to-decision | < 3 business days | > 7 days |
| % of deals waiting on a single approver > 24h | < 10% | > 30% |
| Deals stuck > 7 days | 0 | > 5 |
| Sales rep satisfaction with deal desk (NPS) | > 50 | < 0 |
| % approved (high approval rate may mean threshold too low) | 60-80% | > 95% or < 40% |
| Discount-on-discount: deals where customer negotiated up after deal-desk approval | < 10% | > 30% |

Run `scripts/deal_velocity_analyzer.py --deals deals.csv` to compute these from a CRM export.

### Common bottlenecks

| Bottleneck | Diagnosis | Fix |
|------------|-----------|-----|
| Single approver bottleneck (one person on everything) | Routing matrix concentrated authority | Delegate; add back-ups; raise thresholds |
| Legal review takes a week | Legal sees every deal | Standard MSA + pre-approved clause library; Legal only on deviations |
| Engineering needed for SLA review | Custom SLAs every time | Publish standard SLA tiers; only deviations route to eng |
| Approval cycle back-and-forth | Packet missing key info | Use the standard packet template; reject incomplete submissions |
| Long executive lag | Exec doesn't have context for every deal | Weekly deal review meeting for batch decisions on smaller items |
| Sales submits incomplete packets | Reps don't know what to include | Intake form that enforces required fields |
| No SLA enforcement | Deals sit in queue with no urgency | Publish + report SLA; aging dashboard visible to leadership |

See [references/discount-and-concession-playbook.md](references/discount-and-concession-playbook.md) for the discount/concession patterns: legitimate reasons for each concession type, how to evaluate, alternatives to discounting, and how to structure performance-based discounts.

---

## Clarify First

Before generating the deal-desk artifact, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task type** — standing up the desk (charter + matrix) vs reviewing one deal (packet) (determines which template you produce)
- [ ] **Deal specifics: ACV + requested deviation** — discount %, term, payment, custom SLA/legal (sets the Standard-vs-Requested table and which approvers the matrix requires)
- [ ] **Approval authority structure** — who can approve what (Rep→Manager→Director→VP→CRO/CFO/CEO + Legal) (drives the threshold matrix and routing)
- [ ] **Strategic value + risk** — logo/reference value, credit/compliance risk (drives the packet's justification and recommendation)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## End-to-end workflows

### Workflow: A rep submits a non-standard deal

1. **Rep submits** via intake form: customer + ACV + requested deviation + justification
2. **Deal desk triages** within 4h: assigns analyst, validates packet completeness, requests missing info
3. **Deal desk reviews** within 1 business day: financial impact, strategic value, risk
4. **Deal desk recommends** approve / counter / decline
5. **Route to approver(s)** per matrix (auto via `scripts/discount_authority_router.py`)
6. **Approver decides** within SLA
7. **If approved**: packet signed off, conditions sent to rep with expiration
8. **If countered**: deal desk works with rep on alternative structure
9. **If declined**: clear reason + alternatives sent to rep + customer

### Workflow: Stand up a deal desk from scratch

1. **Draft charter** with sales, finance, legal sign-off
2. **Build the approval matrix** — interview key stakeholders, document existing tribal knowledge
3. **Design intake form** — CRM-integrated or Slack-bot
4. **Hire / appoint deal desk lead + analyst(s)**
5. **Train sales** — what triggers deal desk, what info is needed, what to expect
6. **Soft launch** — manual operation for 1 month; track metrics
7. **Iterate** — refine thresholds, automate routing, publish SLAs
8. **Quarterly review** — metrics, threshold adjustments, charter updates

### Workflow: Audit deal-desk performance

1. **Export deals** from CRM for the period (CSV with deal IDs, stages, approval timestamps, discounts)
2. **Run velocity analyzer** — compute medians, percentiles, aging, approver bottlenecks
3. **Sample 10-20 deals** for qualitative review (was the packet complete? were conditions met?)
4. **Identify patterns** — are certain reps over-discounting? are certain customers getting MFN clauses inappropriately?
5. **Propose adjustments** — to charter, thresholds, intake form, training
6. **Present to leadership** with metrics + recommendations

### Workflow: Quarterly threshold review

Thresholds drift. Quarterly:

1. **Pull discount distribution** for the quarter
2. **Identify outliers** — deals where discount % was anomalous for ACV / segment
3. **Compare approval rates** by threshold — if 30%+ discount deals get approved 95%+ of the time, the threshold is too low
4. **Compare win rates** by discount band — does deeper discount actually improve win rate, or does it just give up margin?
5. **Adjust thresholds** based on data + market shift
6. **Publish new matrix** with effective date; train sales

---

## Anti-patterns

- **Deal desk as bottleneck.** SLAs published but ignored; deals stack up; sales builds workarounds. Measure + enforce SLAs.
- **Deal desk that always says yes.** Approval rate > 95% means thresholds are too low — you're rubber-stamping. Tighten or raise thresholds.
- **Deal desk that always says no.** Approval rate < 40% means policy is too strict OR sales doesn't understand it. Investigate root cause.
- **No deal-desk policy.** Every deal evaluated case-by-case. Inconsistent decisions; legal exposure; reps gaming the system.
- **Concentrated authority.** One person approves everything → bottleneck + bus factor. Delegate.
- **Pricing strategy disguised as deal-desk policy.** If 80% of deals need discounting, the published price is wrong. Fix pricing.
- **Discount creep.** Each deal raises the bar for the next; eventually published price is irrelevant. Track + reset.
- **Concession with no quid pro quo.** Customer asks for 20% discount; you give 20% discount. Always trade: 20% for case study, 20% for 3yr contract, etc.
- **No expiration on quotes.** Customer can come back in 6 months and demand the same terms. Always time-box (typically 30-60 days).
- **Single-instance language never enforced.** "This is a one-time exception" → next year the customer cites it as precedent.

---

## Tooling outputs

| Script | Input | Output |
|--------|-------|--------|
| `scripts/deal_review_packet.py` | Deal spec YAML | Markdown deal-review packet with summary, financials, strategic value, risk, approver list, recommendation template |
| `scripts/discount_authority_router.py` | Deal spec YAML + approval matrix YAML | Required approver(s), routing order, escalation path, SLA-aware ordering |
| `scripts/deal_velocity_analyzer.py` | CSV of deals from CRM export | Median / p90 time-to-decision, aging dashboard, approver bottleneck identification, discount-on-discount analysis |

All scripts: stdlib only, argparse CLI, JSON or markdown output.

---

## References

- [deal-desk-charter-and-process.md](references/deal-desk-charter-and-process.md) — full charter template, intake form spec, SLA framework
- [approval-thresholds-and-routing.md](references/approval-thresholds-and-routing.md) — matrix design, regional variants, escalation paths, automation patterns
- [discount-and-concession-playbook.md](references/discount-and-concession-playbook.md) — concession types, legitimate reasons, alternatives, performance-based structures

---

## Related skills

- `business-growth/pricing-strategy` — sets the prices that deal desk enforces deviations from
- `business-growth/revenue-operations` — measures the pipeline; deal-desk metrics flow into RevOps dashboards
- `business-growth/contract-and-proposal-writer` — drafts the final contract once deal desk approves
- `business-growth/channel-economics` — channel deals have their own deal-desk patterns
- `business-growth/partnerships-architect` — partner-mediated deals route through both deal desk + partnerships
- `business-growth/commercial-policy` — the broader governance framework deal desk enforces
- `sales-success/sales-engineer` — provides technical validation in packet
- `sales-success/sales-operations` — owns CRM / forecast accuracy that deal desk feeds
