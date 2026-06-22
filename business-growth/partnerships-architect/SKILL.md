---
name: partnerships-architect
description: >
  Design strategic partnerships — technology, channel, co-marketing — and the
  programs that scale them. Use when evaluating a partner, picking a partnership
  type, designing a partner program, structuring a deal, or modeling ROI.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: commercial
  domain: business-growth
  updated: 2026-05-27
  tags: [partnerships, strategic-alliances, channel-strategy, tech-partnerships, partner-program, partnership-design, gtm]
---

# Partnerships Architect

End-to-end strategic partnership design and scaling: partnership type selection (tech integration vs channel vs OEM vs strategic), deal structures, partner program design (tiers, benefits, requirements), partner evaluation, and ROI modeling that justifies (or kills) a partnership investment.

This skill is provider-agnostic and works across SaaS, infrastructure, marketplace, and platform companies.

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| Evaluating a potential partner | Yes — use `scripts/partner_evaluation_scorer.py` + **evaluation framework** |
| Picking partnership type for a specific opportunity | Yes — see **partnership type decision tree** |
| Designing a partner program from scratch | Yes — see **partner program design** + `scripts/partner_program_designer.py` |
| Structuring a specific partnership deal | Yes — see **partnership deal structures** |
| Modeling partnership ROI | Yes — `scripts/partnership_roi_modeler.py` |
| Auditing existing partner portfolio | Yes — use evaluation scorer across all partners |
| Per-deal partner economics | Use `business-growth/channel-economics` |
| Per-deal partner approval | Use `business-growth/deal-desk` |
| Writing the partner contract | Use `business-growth/contract-and-proposal-writer` |

---

## Partnership types — the decision tree

Five primary partnership types. Different goals; different structures; different success metrics.

```
What's the primary goal of this partnership?

Grow our distribution reach
├── Customer-pays-them, they-pay-us → Reseller / Distributor / VAR
├── Customer-pays-us, we-pay-them → Affiliate / Referral
└── Joint sale to mutual customer → Co-sell

Embed our product in their offering
├── Customer doesn't see us (white-label) → OEM
├── Customer sees us as embedded → Embedded ISV / Powered-by
└── We're an option in their marketplace → Marketplace listing

Combine our product with theirs (better together)
├── Pre-integrated, certified → Tech / Integration Partner
├── Bundled offering → Solution Partner
└── Joint product (rare) → Joint Venture

Build market presence together
├── Joint events, content, PR → Co-marketing Partner
├── Industry positioning → Strategic Alliance
└── Standards / consortium → Standards Partner

Achieve a specific strategic goal
├── Block a competitor → Defensive partnership
├── Enter a new market → Market entry partnership
└── Acquire capability → Strategic alliance (often pre-acquisition)
```

See [references/partnership-types.md](references/partnership-types.md) for each type in depth: economic structure, contract patterns, KPIs, when each works / fails.

---

## Partner evaluation framework

Not every potential partner is worth the investment. Use this framework before committing.

### Six evaluation dimensions

| Dimension | What to assess | Score (1-5) |
|-----------|----------------|-------------|
| **Strategic fit** | Does this partnership advance our strategy? Customer base overlap / vertical / region? | |
| **Economic potential** | Realistic pipeline / revenue contribution over 24 months? | |
| **Partner credibility** | Brand, financial stability, technical capability, customer references | |
| **Mutual commitment** | Are they investing equally? Senior sponsor on their side? Resources committed? | |
| **Operational fit** | Can our systems / processes / culture work together? | |
| **Exit-ability** | If it doesn't work, can we wind down cleanly? Are we creating dependencies we can't reverse? |

### Scoring rubric

- 5 — strong yes
- 4 — yes with minor caveats
- 3 — mixed; substantial uncertainty
- 2 — weak; significant concerns
- 1 — no; deal-breaker

**Total 25-30**: green-light; invest with confidence
**Total 18-24**: yellow; structure carefully; small pilot first
**Total < 18**: red; decline or substantially restructure

Use `scripts/partner_evaluation_scorer.py --partner partner.yaml` to score a specific potential partner.

### Killer questions to ask

Before signing any significant partnership:

1. **What does success look like in 12 months?** If both sides can't articulate the same answer, you don't have alignment.
2. **What's their commitment level?** Headcount assigned? Budget? Executive sponsorship?
3. **What's the realistic pipeline in next 12 months?** Specific accounts? Or vague "we have customers"?
4. **Who's the day-to-day owner on each side?** Names + tenure + reporting line.
5. **What happens if we don't hit our shared metrics?** Course-correct? Wind down? Renegotiate?

If you can't get clear answers, the partnership is wishful thinking.

---

## Partnership deal structures

Different deal types call for different structures. Standard patterns:

### Structure A: Standard reseller agreement

- **Term**: 1-3 years, auto-renew
- **Discount**: per published tier matrix
- **Exclusivity**: usually non-exclusive
- **Termination**: 90-day notice both sides
- **Use when**: typical channel relationship

### Structure B: Co-sell agreement (mutual customer)

- **Term**: 1-2 years
- **Compensation**: shared commission OR referral fee
- **Joint marketing commitment**: optional
- **Use when**: complementary offerings; existing or target shared customers

### Structure C: OEM agreement

- **Term**: 3-7 years (long; relationship-heavy)
- **Royalty / rev-share**: % of partner revenue OR per-instance fee
- **Exclusivity**: often partial (specific use case / market)
- **Source code escrow**: usually required
- **Termination**: complex (typically 12-24 months notice; transition rights)
- **Use when**: deeply embedded technical relationship; high mutual investment

### Structure D: Strategic alliance

- **Term**: open-ended; reviewed annually
- **Resources committed**: explicit (e.g., 2 FTEs per side, $X budget per year, joint roadmap session quarterly)
- **Governance**: steering committee (executive sponsors meet quarterly)
- **Specific deliverables**: joint product features, joint customer wins, joint thought leadership
- **Use when**: 5+ year strategic relationship; not transactional

### Structure E: Tech / integration partnership

- **Term**: 1-3 years
- **Compensation**: typically none direct; mutual value from joint customers
- **Certification process**: defined (testing, documentation)
- **Marketplace listing**: typically included
- **Co-marketing**: optional but common
- **Use when**: integration creates joint customer value; no direct revenue flow

See [references/partnership-deal-structures.md](references/partnership-deal-structures.md) for the full deal-structure templates with negotiation guides.

---

## Partner program design

When you scale beyond a few partners, you need a program.

### Three pillars of a partner program

| Pillar | Components |
|--------|------------|
| **Recruitment** | Target partner profile; outreach motion; intake / qualification; onboarding |
| **Enablement** | Training; certification; technical resources; sandbox; partner portal; marketing materials |
| **Activation** | Deal registration; lead sharing; MDF / co-marketing; co-selling motion; quarterly business reviews |

### Standard program elements

- **Partner agreement** (master): tenant-of-the-relationship
- **Tier structure** (Authorized → Silver → Gold → Platinum): different benefits + requirements per tier
- **Deal registration**: protect partner-developed opportunities
- **Certification program**: train + test partners on your product
- **Partner portal**: deal reg, MDF, training, marketing materials, lead sharing
- **MDF (Marketing Development Funds)**: co-funded marketing
- **Channel manager(s)**: 1 per 10-15 active partners
- **Annual partner conference**: community building + recognition

See [references/partner-program-design.md](references/partner-program-design.md) for the full program template including tier definitions, benefit / requirement matrices, and the "Year 1 / Year 2 / Year 3" maturity model.

Use `scripts/partner_program_designer.py --org-spec org.yaml` to generate a baseline program design based on company stage + ICP + target partner volume.

---

## Partnership ROI modeling

Partnerships consume real investment. Headcount, MDF, technology, executive time. Model the ROI before committing.

### ROI model template

```
3-year cumulative partnership P&L

Year 1 (investment year):
  Revenue from partnership: $X
  Costs:
    Partnership manager headcount: $200k
    Engineering integration (one-time): $300k
    Marketing / co-launch: $50k
    Partner enablement (content, training): $50k
    Travel / events: $30k
    TOTAL Y1 cost: $630k
  Y1 net: $X - $630k

Year 2:
  Revenue from partnership: $Y (growth)
  Costs:
    Partnership manager: $200k
    Engineering ongoing: $100k
    Marketing: $80k
    Enablement: $30k
    Travel / events: $40k
    TOTAL Y2 cost: $450k
  Y2 net: $Y - $450k

Year 3:
  Revenue: $Z (mature)
  Costs: $400k (stable)
  Y3 net: $Z - $400k

3-year cumulative net: ($X + $Y + $Z) - $1,480k
```

If 3-year cumulative net is negative, the partnership doesn't pay back. Common reasons:
- Revenue estimates too optimistic
- Forgotten costs (executive time, opportunity cost)
- Partner under-performs on commitments
- Market shift makes the partnership less relevant

Use `scripts/partnership_roi_modeler.py --partnership partnership.yaml` for the full model.

---

## Clarify First

Before designing the partnership, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Partnership goal + type** — distribution, embed (OEM/ISV), better-together (tech/integration), market presence, or strategic (selects the decision-tree branch and deal structure)
- [ ] **Single deal vs scaled program** — structuring one partnership vs designing tiers/portfolio (determines deal-structure vs program-design output)
- [ ] **Partner specifics for evaluation** — their pipeline expectation, commitment, and credibility (feeds the 6-dimension scorer and green/yellow/red call)
- [ ] **ROI inputs** — expected revenue and the real costs (headcount, integration, MDF) (drives the 3-year P&L payback)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the deliverable.

## End-to-end workflows

### Workflow: Evaluate a new partner opportunity

1. **Initial conversation** with potential partner — understand their pitch
2. **Gather data** for evaluation: their company, their pipeline expectations, their commitment
3. **Score using evaluation framework** — `scripts/partner_evaluation_scorer.py`
4. **If score < 18**: decline or pilot-scope only
5. **If score 18-24**: pilot scope (3-6 months, limited investment)
6. **If score 25+**: standard partnership agreement; full investment

### Workflow: Stand up a partner program

1. **Define target partner profile (TPP)**: ideal partner attributes (size, vertical, region, capability)
2. **Pick partnership types** in scope (resellers? OEM? tech partners?)
3. **Design tier structure** — `scripts/partner_program_designer.py`
4. **Build foundational tools**: partner portal, deal-reg, certification
5. **Recruit pilot cohort** (3-5 partners) — manual, high-touch
6. **Iterate based on pilot feedback** — usually 6 months
7. **Scale recruitment** — content marketing, outbound, partner events
8. **Add channel managers** as portfolio grows (1 per 10-15 active partners)

### Workflow: Structure a specific partnership deal

1. **Identify partnership type** using the decision tree
2. **Score the partner** — `scripts/partner_evaluation_scorer.py`
3. **Pick deal structure** matching the type
4. **Model ROI** — `scripts/partnership_roi_modeler.py`
5. **Draft term sheet** (key business terms)
6. **Negotiate** — alignment on commitment, timelines, exit
7. **Legal review** + contract — `business-growth/contract-and-proposal-writer`
8. **Internal approval** — Deal Desk + CRO/CFO/CEO depending on scale

### Workflow: Audit existing partner portfolio

1. **List all active partners** + key data: revenue, costs, deals, tier
2. **Score each** against evaluation framework — `scripts/partner_evaluation_scorer.py`
3. **Identify low-ROI partners** — bottom quartile by contribution per investment hour
4. **Decide per partner**:
   - **Invest more** (top quartile, expand commitment)
   - **Maintain** (middle, status quo)
   - **Wind down** (bottom; explicit timeline to exit gracefully)
5. **Quarterly review** of portfolio with CRO

---

## Anti-patterns

- **"Strategic" partnership that's actually transactional.** If the only thing exchanging is money, it's transactional; call it that. Strategic means joint goals + shared roadmap + executive commitment.
- **Partner stack with no portfolio strategy.** Signing every partner that asks. Quality > quantity. 10 productive partners beat 100 zombies.
- **No partnership owner.** Partnership exists in nobody's job. It withers.
- **Resource asymmetry.** You commit 3 FTEs; they commit 0.5. The partnership skews to their convenience.
- **Promises without commitments.** "We'll do joint webinars." When? With what budget? Whose role to organize?
- **Open-ended exclusivity.** "Exclusive in this region forever" without performance gates. Lose flexibility for nothing in return.
- **OEM deal with no source-code escrow.** Customer-impact risk if your company goes away.
- **Strategic alliance with no governance.** No quarterly review = no executive engagement = partnership drifts.
- **Partner program with no enablement.** Partners can't sell what they don't understand.
- **Tier benefits that aren't worth tier requirements.** Partners don't advance because there's no incentive.
- **Co-marketing dollars wasted on activities without pipeline.** Great event, zero attribution.

---

## Tooling outputs

| Script | Input | Output |
|--------|-------|--------|
| `scripts/partner_evaluation_scorer.py` | Partner spec YAML | 6-dimension score (1-5 each), total, recommendation (green-light / yellow / red) |
| `scripts/partnership_roi_modeler.py` | Partnership spec YAML | 3-year P&L, payback period, sensitivity analysis |
| `scripts/partner_program_designer.py` | Org spec YAML | Recommended program structure: tiers, benefits, requirements, headcount needed |

All scripts: stdlib only, argparse CLI, JSON or markdown output.

---

## References

- [partnership-types.md](references/partnership-types.md) — 5 partnership types in depth + economic structure + when each works
- [partnership-deal-structures.md](references/partnership-deal-structures.md) — deal templates per type + negotiation guides
- [partner-program-design.md](references/partner-program-design.md) — full program design with tier matrices + maturity model

---

## Related skills

- `business-growth/channel-economics` — per-deal financial mechanics underneath partnership structure
- `business-growth/deal-desk` — per-deal approval mechanics for partner-mediated deals
- `business-growth/pricing-strategy` — pricing flexibility / floor for partner deals
- `business-growth/contract-and-proposal-writer` — partner contracts (MSA, partner agreement, OEM agreement)
- `c-level-advisor/cs-cro-advisor` — strategic-level partnership decisions
- `c-level-advisor/cs-ceo-advisor` — board-level alliance decisions
