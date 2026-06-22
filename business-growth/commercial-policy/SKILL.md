---
name: commercial-policy
description: >
  Commercial policy: the governance framework defining what terms sales can offer
  and what triggers approval. Use when authoring a policy charter, defining
  discount/payment/liability rules, auditing deals, or generating a regional policy.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: commercial
  domain: business-growth
  updated: 2026-05-27
  tags: [commercial-policy, governance, contract-policy, pricing-policy, sales-governance, deal-policy, gtm]
---

# Commercial Policy

End-to-end commercial-policy authoring and governance: defining the rules that govern what sales can offer, what triggers approval, and what's prohibited. Pairs with our deal-desk (operational enforcement) and pricing-strategy (price-setting) skills — this is the policy that those execute against.

A good commercial policy:
- Makes deal-desk faster (fewer ambiguous cases)
- Makes sales reps more autonomous (clearer authority)
- Makes legal reviews lighter (most cases already covered)
- Reduces concession drift over time
- Provides audit-ready governance documentation

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| Authoring commercial policy from scratch | Yes — start with **policy charter template** + `scripts/commercial_policy_generator.py` |
| Refreshing an existing policy (annual) | Yes — see **annual policy review** workflow |
| Auditing recent deals for policy compliance | Yes — `scripts/policy_compliance_checker.py` |
| Analyzing terms-deviation patterns | Yes — `scripts/terms_deviation_analyzer.py` |
| Tailoring policy for new region / vertical | Yes — `scripts/commercial_policy_generator.py --region <X>` |
| Drafting sales training on policy | Yes — see **training section** |
| Setting prices (not policy on deviations) | Use `business-growth/pricing-strategy` |
| Per-deal approval | Use `business-growth/deal-desk` |
| Writing the specific contract | Use `business-growth/contract-and-proposal-writer` |

---

## What commercial policy covers

Standard scope:

| Domain | Policy area |
|--------|-------------|
| **Pricing** | Standard pricing, discount thresholds, MFN, rebates, custom-bundle pricing |
| **Contract** | Standard term length, payment terms, renewal terms, termination, customer audit rights |
| **Legal** | Acceptable MSA modifications, liability cap, indemnification, jurisdiction, IP |
| **Operational** | SLA tiers, custom SLAs, security commitments, dedicated infrastructure |
| **Customer commitments** | Reference / case study / press release obligations |
| **Channel** | Partner discount tiers, channel-conflict rules, deal-registration |
| **Special terms** | Performance-based payment, acceptance criteria, ramp deals |

What it doesn't cover:
- Day-to-day pricing decisions (that's pricing strategy)
- Per-deal approval mechanics (that's deal-desk operations)
- Sales targets / quota (that's compensation policy)
- Customer success / churn-prevention tactics

---

## Commercial policy charter (template)

The foundational document. Every company that does $5M+ ARR needs one. Use this template:

```markdown
# Commercial Policy Charter

## Purpose
This Commercial Policy defines the rules that govern commercial terms
offered to customers. It is binding on all customer-facing functions
(Sales, Customer Success, Partner / Channel) and is enforced by Deal Desk.

## Scope
Applies to:
- All new customer agreements
- All renewals (with material change)
- All partner-mediated deals
- All custom / non-standard agreements

Does not apply to:
- Self-serve / PLG transactions per standard published terms
- Auto-renewals at standard terms

## Owners and Approvers
- Policy owner: CRO + CFO + General Counsel (jointly)
- Operational enforcement: Deal Desk
- Updates: quarterly review by policy owners
- Material changes: board awareness

## Pricing Policy

### Standard pricing
- All new customers offered at published list pricing
- Published price is canonical; deviations require approval per matrix

### Discount approval matrix
[Per the deal-desk approval matrix — see business-growth/deal-desk]

### Maximum allowed discount
- Standard maximum: 50%
- Beyond 50%: CEO + Board awareness required
- Discount > 60%: only with explicit strategic-rationale documented and CEO sign-off

### Most Favored Nation (MFN)
- Not granted by default
- Granted only with: strategic-tier customer + CRO + CFO + GC approval
- Always scoped narrowly: same product, same volume, same term length, same geography
- Disclosure-only (never automatic price-match)

### Rebates
- Performance-based rebates allowed per partner-program tier
- Customer-tier rebates: discouraged; if granted, time-bounded and explicit

## Contract Policy

### Standard term
- 12-month contract with annual prepay
- Auto-renew unless 90-day notice

### Term flexibility
- < 12 months: requires Director approval
- 24-36 months: Director approval
- > 36 months: VP Sales approval
- Multi-year discounts: per discount matrix

### Payment terms
- Standard: Net 30, annual prepay
- Net 45-60: Director approval
- Net 90+: CFO approval
- Custom milestone-based: CFO approval; revenue recognition impact reviewed

### Renewal
- Standard: auto-renew, same terms, same price (or per published renewal pricing)
- Renewal expansion > 20%: deal-desk review
- Renewal contraction > 10%: deal-desk review + customer success consultation

### Termination
- Standard: termination for convenience requires 90-day notice
- Termination for cause: 30-day cure period
- Customer-requested termination flexibility: Director approval
- Mid-term termination rights: VP Sales approval

## Legal Policy

### MSA modifications
- Pre-approved modifications: tracked list in approved-modifications appendix
- Custom modifications: General Counsel approval required
- Customer-supplied MSA: full GC review; default to push back to our MSA

### Liability cap
- Standard: 1x annual fees
- 2x annual fees: GC + CFO approval
- > 2x annual fees: CEO sign-off
- Carve-outs: IP infringement, gross negligence, willful misconduct — always uncapped

### Indemnification
- Standard mutual indemnification per template
- Customer-favorable indemnification: GC approval
- Defense / settlement control: vendor by default; customer-controlled needs CEO

### Jurisdiction and governing law
- Standard: vendor's jurisdiction
- Customer jurisdiction: GC approval
- Arbitration vs litigation: per template; deviations need GC

### IP
- Standard: each party retains pre-existing; joint inventions per default
- Customer-favorable IP terms: GC approval
- Source code escrow: only for OEM / strategic; never standard customer

## Operational Policy

### SLA tiers
- Standard published SLA (99.5%)
- Enhanced SLA (99.9%): per published pricing
- Custom SLA: Customer Success + Engineering approval; pricing premium per agreement
- Custom SLA with penalties: CRO + CCO + Engineering approval

### Security commitments
- Standard SOC 2 / ISO 27001 commitments per template
- Custom security: CISO + GC approval
- Customer audit rights: GC approval (limited to annual, with notice, third-party auditor)

### Dedicated infrastructure
- Not standard; available only with CTO + GC approval
- Premium pricing required

## Customer Commitments

### Reference / case study requests
- Standard: requested but not required
- Discounted deals (> 15%): case study or reference required as condition
- Strategic logos: explicit case study + press release commitment

## Channel Policy

### Partner-mediated deals
- Per Partner Agreement; discount per tier
- Deal registration governs conflict
- Direct rep authority same as direct deals on partner-led opportunities

## Special Terms

### Performance-based payment
- Payment-on-acceptance / acceptance criteria: CFO + GC approval
- Milestone payments: CFO approval

### Ramp deals
- ≤ 3 months: Sales Manager
- 3-12 months: Director
- > 12 months: VP Sales

### Source code escrow (for customer)
- Not standard; available only with CTO + GC approval

## Documentation Requirements

Every non-standard deal documented per Deal Desk packet template:
- Deviation explicitly listed
- Justification documented
- Approver identified
- Customer commitments (if any) explicit
- Expiration / conditions clear

## Annual Review

This policy is reviewed annually by CRO + CFO + GC.
Material changes communicated to sales with training.

## Effective Date
<date>
## Last Updated
<date>
## Approved By
- CRO: <signature>
- CFO: <signature>
- GC: <signature>
- Board (acknowledgement): <date>
```

See [references/commercial-policy-charter.md](references/commercial-policy-charter.md) for the full annotated charter with notes on each section's typical contentious issues.

---

## Discount and terms policy details

See [references/discount-and-terms-policy.md](references/discount-and-terms-policy.md) for deeper guidance on:

- Discount-percentage policy by ACV bracket
- MFN clause design (when to allow, how to scope)
- Performance-based rebate structures
- Multi-year discount mechanics
- Payment-term flexibility and revenue-recognition implications
- Renewal pricing policy (escalators, holds, contraction)

---

## Contract and commercial guardrails

See [references/contract-and-commercial-guardrails.md](references/contract-and-commercial-guardrails.md) for deeper guidance on:

- Acceptable MSA modifications (a list-based, not case-by-case approach)
- Liability cap negotiation
- Termination rights design
- IP and joint-development clauses
- Customer audit rights
- Cross-jurisdictional terms (EU vs US vs APAC)

---

## Clarify First

Before generating the policy, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Company stage + ARR scale** — drives whether a full charter is warranted and how tight thresholds should be
- [ ] **Approver structure** — who owns the policy and sits in the chain (CRO/CFO/GC, VP Sales, Director) (populates Owners/Approvers and every approval line)
- [ ] **Region / jurisdiction** — US / EU / APAC (changes payment norms, governing law, and triggers a regional overlay)
- [ ] **Max discount + liability risk appetite** — the discount ceiling and liability-cap tolerance (drives the Pricing and Legal policy sections)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the policy.

## End-to-end workflows

### Workflow: Author commercial policy from scratch

1. **Assemble policy committee** — CRO + CFO + GC sponsors + Deal Desk Lead + Sales Operations
2. **Inventory current deals** — what terms have been offered? What's been ad-hoc?
3. **Identify policy gaps** — areas where ad-hoc behavior is hurting (concession drift, customer surprises)
4. **Draft charter** using template; one section per domain
5. **Internal review** — Sales VP, Eng VP, CISO, Customer Success VP, Finance for revenue recognition
6. **Pilot** with sales managers for 30 days — collect feedback
7. **Final approval** — CRO + CFO + GC sign-off; board awareness
8. **Sales training** — workshop + recorded session + quick-reference cards
9. **Publish** to sales wiki / partner portal / customer-facing communications team
10. **Quarterly review** thereafter

### Workflow: Refresh existing policy (annual)

1. **Pull deal data** for past 12 months: discount distribution, terms deviations, approvals
2. **Identify drift** — what's the deviation rate by policy category?
3. **Survey sales managers** — what's working / what's blocking
4. **Survey customers** — what terms have been requested but declined?
5. **Identify market shifts** — competitive landscape, customer expectations
6. **Draft amendments** — specific policy changes with rationale
7. **Approve** with CRO + CFO + GC
8. **Communicate changes** to sales with training
9. **Update charter** + effective date

### Workflow: Audit deal compliance

1. **Export deals** from CRM for the period
2. **Run compliance checker** — `scripts/policy_compliance_checker.py --deals deals.csv --policy policy.yaml`
3. **Review non-compliant deals** — investigate each: was the deviation approved? was it documented?
4. **Categorize**:
   - Compliant with approved deviation: OK
   - Non-compliant unapproved: investigate; corrective action
   - Compliant but suggests policy gap: amend policy
5. **Report** to policy committee; track corrective actions

### Workflow: Generate region-specific policy

1. **Identify region-specific requirements** — currency, jurisdiction, payment norms, regulatory
2. **Run** `scripts/commercial_policy_generator.py --base policy.yaml --region <region>` to get base + regional overlay
3. **Tailor** further with local team (regional VP Sales, regional GC, regional CFO)
4. **Approve** through standard governance
5. **Communicate** to regional sales

---

## Anti-patterns

- **Policy without enforcement.** Written policy + ad-hoc execution = policy is theater.
- **Policy that's never updated.** Markets shift; competitive landscape changes; policy goes stale.
- **Policy with no compliance audit.** Without measurement, you can't tell if policy is followed.
- **Policy too restrictive.** When sales bypasses constantly, the policy is wrong; tighten or loosen.
- **Policy too lax.** When everyone "complies" but margin still erodes, policy doesn't constrain enough.
- **Policy authored without sales input.** Reps see it as imposed; comply minimally.
- **Policy with no training.** Reps don't know what they can offer; default to over-asking deal desk.
- **Policy that's a contract appendix.** Buried in legal docs; never read.
- **Same policy across regions** when market conditions differ substantially.
- **Policy reviewed only after a customer complaint.** Reactive only.

---

## Tooling outputs

| Script | Input | Output |
|--------|-------|--------|
| `scripts/policy_compliance_checker.py` | Deal CSV + policy YAML | Per-deal: compliant / non-compliant with policy violation listing; aggregate compliance metrics |
| `scripts/terms_deviation_analyzer.py` | Deal CSV | Deviation patterns: which terms most often deviate? from which standard? by what magnitude? |
| `scripts/commercial_policy_generator.py` | Base policy YAML + optional region overlay | Generated policy document (markdown), tailored to company stage, ICP, region |

All scripts: stdlib only, argparse CLI, JSON or markdown output.

---

## References

- [commercial-policy-charter.md](references/commercial-policy-charter.md) — full annotated charter with notes on each section
- [discount-and-terms-policy.md](references/discount-and-terms-policy.md) — discount, MFN, rebate, payment-terms policy depth
- [contract-and-commercial-guardrails.md](references/contract-and-commercial-guardrails.md) — MSA modifications, liability, termination, IP

---

## Related skills

- `business-growth/deal-desk` — operational enforcement of policy
- `business-growth/pricing-strategy` — sets prices that policy governs deviations from
- `business-growth/contract-and-proposal-writer` — drafts contracts respecting policy
- `business-growth/channel-economics` — channel deals subject to policy (with overlay for partners)
- `business-growth/partnerships-architect` — partnership terms subject to commercial-policy oversight
- `c-level-advisor/cs-cro-advisor` — CRO is co-owner of policy
- `c-level-advisor/cs-cfo-advisor` — CFO is co-owner of policy
- `ra-qm-team/soc2-compliance-expert` — policy compliance is audit-relevant evidence
