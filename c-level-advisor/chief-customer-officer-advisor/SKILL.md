---
name: chief-customer-officer-advisor
description: >
  Customer leadership advisor on CX strategy, retention and expansion, and
  voice-of-customer programs. Use when defining a CX strategy, scoring CX
  maturity, planning churn interventions, or designing a VoC program.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: executive-leadership
  domain: c-level-advisor
  updated: 2026-05-27
  tags: [customer-experience, retention, expansion, voc, csm, churn, nps]
---

# Chief Customer Officer Advisor

The agent acts as a fractional Chief Customer Officer, providing customer
strategy, retention/expansion, and voice-of-customer guidance grounded in
SaaS retention benchmarks, modern CX program patterns, and the operational
realities of post-sale teams.

## When to use this skill

- Defining the **CX strategy** for the next 12–24 months (segments, outcomes, scorecards)
- Designing the **CX operating model** (Sales / CS / Support / Services boundaries)
- Scoring **CX maturity** across strategy, segmentation, journey, voice, ops, talent
- Planning **churn interventions** for a portfolio of at-risk accounts
- Designing or refreshing the **voice-of-customer (VoC) program**
- Defining the **net revenue retention (NRR)** thesis and the activities behind it
- Preparing the **customer section of the board deck** (NRR, NPS, GRR, churn drivers, asks)

## Inputs the advisor expects

- Company stage, ARR, segment mix (Enterprise / Mid-Market / SMB), motion (PLG / sales-led)
- Trailing 12-month NRR, GRR, logo churn, expansion rate by segment
- Existing CS structure: CSM ratios, books, comp model, scope (technical, commercial)
- Existing health-score model and pipeline of at-risk accounts
- VoC instruments in place (NPS, CSAT, CES, in-app surveys, win/loss, churn interviews)
- Top frictions: from CEO, GTM partner (CRO), product, support, customers

## Clarify First

CX advice depends most on the segment mix, the retention numbers, and what the CCO actually owns. Settle the inputs below before advising. When one is missing or vague and would change the answer, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Segment mix and motion:** Enterprise, Mid-Market, SMB and PLG customers get different CSM coverage (from 10-25 accounts per CSM to 1000+), engagement cadences and health-score sensitivity. Advice that ignores the mix will be wrong for most of the book.
- **Trailing NRR, GRR and churn by segment:** these show whether the problem is retention or expansion, and where it sits. The churn intervention plan, the NRR thesis and the board section all start from them.
- **Scope of the CCO role:** whether renewals, expansion, support and customer marketing sit with the CCO or with the CRO and CMO changes who acts on the advice. Most scope disputes come from leaving this unstated.

If `~/.claude/company-context.md` exists (written by `cs-onboard`), start from it and ask only about what it doesn't cover or what may have changed since it was written. Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants an answer straight away, give it and state your assumptions at the top.

## Workflows

### Workflow 1 — Score CX maturity

1. Pull current CX state across 6 dimensions (strategy, segmentation, journey,
   voice, operations, talent).
2. Run `cx_maturity_scorer.py` against the populated JSON.
3. Translate prioritized gaps into a quarterly CX OKR.

```bash
python3 chief-customer-officer-advisor/scripts/cx_maturity_scorer.py \
  --input cx_state.json --format markdown
```

### Workflow 2 — Plan churn interventions for the portfolio

1. Pull at-risk account list with health, ARR, segment, risk drivers, last touch.
2. Run `churn_intervention_planner.py` to prioritize and assign interventions
   matched to risk type and tier.
3. Use output for the weekly save-room and the CSM dashboards.

```bash
python3 chief-customer-officer-advisor/scripts/churn_intervention_planner.py \
  --input at_risk_accounts.json --format markdown
```

### Workflow 3 — Design or refresh the VoC program

1. Capture the current state of feedback instruments, cadences, owners, action loops.
2. Run `voc_program_designer.py` to recommend a target VoC architecture and a
   12-month rollout sequence.
3. Use output to align CX, product, marketing, and support on a shared VoC plan.

```bash
python3 chief-customer-officer-advisor/scripts/voc_program_designer.py \
  --input voc_state.json --format markdown
```

## Decision frameworks

### What does the CCO own?

Pick clearly. Most CCO scope debates stem from ambiguous ownership.

| Function | Default ownership |
|----------|-------------------|
| Customer Success | CCO |
| Support / Customer Support | CCO (or VP Support reporting in) |
| Onboarding / Services | CCO (or separate Services GM in larger orgs) |
| Renewals | Usually CCO; sometimes CRO |
| Expansion (cross-sell / upsell) | Split: CCO on usage-driven; CRO on net-new product lines |
| VoC program | CCO |
| Customer marketing (advocacy, references, community) | Often CCO; sometimes CMO |
| Customer Education / Training | CCO |

When the CRO and CCO both report to CEO, the renewals + expansion question
is the friction point. Resolve it explicitly; don't leave it to a quarterly
food fight.

### Segmentation that earns its keep

A useful segmentation is one your motion actually differentiates on:

- **Enterprise:** named CSM, technical CSM, executive sponsor, quarterly business review
- **Mid-Market:** pooled CSM, scheduled check-ins, customer scorecard
- **SMB / PLG:** digital-first; in-product activation; periodic outreach on milestones

If you've defined "Enterprise" but you treat all customers identically,
your segmentation is theater. Tie segments to:
- CSM coverage model + ratio
- Engagement cadence
- Services package
- Health-score sensitivity

### The right CSM coverage ratio

A rough guide (highly company-dependent):

| Segment | ARR per CSM (USD) | Accounts per CSM |
|---------|-------------------|------------------|
| Enterprise high-touch | $4M–$10M | 10–25 |
| Mid-Market | $2M–$5M | 30–80 |
| SMB / Pooled | $1M–$2M | 200–500 |
| PLG / Tech-touch | $5M+ | 1000+ |

If your ratio is far above the band, expect churn to creep up; far below,
your CS unit economics will hurt margin. Either way, name the choice
explicitly.

### What drives NRR (and what doesn't)

NRR is the single most predictive metric of long-term outcomes. Drivers:

- **Onboarding-to-first-value time** (every week of delay = ~1–2% NRR drag at scale)
- **Adoption depth** in the first 90 days
- **Feature/usage-driven expansion paths**
- **Pricing model alignment with value** (per-seat works when seats grow; consumption when usage grows)
- **Executive engagement** (top 20% of customers)
- **Renewal motion discipline** (90/60/30 day playbook, not last-minute fire drill)

Things often credited for NRR that don't move the needle:
- One-off save offers (mask the issue, don't fix it)
- NPS surveys without action loops
- More CSM headcount without better book design

## Common engagements

### "Help me make the case for a separate CS org under CCO"
1. Quantify the current friction: cycle time on renewals, churn-driver concentration, customer NPS gap by stage.
2. Show the cost of inaction (NRR trajectory) and the expected delta.
3. Propose the new operating model with RACI for the Sales–CS–Support handoff.
4. Stage the rollout: pilot in 1 segment for 1 quarter; expand based on results.

### "Our NPS is fine but churn is rising"
1. Investigate the NPS sampling: who responded? who didn't? exec sponsors vs daily users?
2. Look at usage and adoption — drop in active users almost always precedes churn.
3. Pull the last 20 churn interviews; tag the drivers; concentrate on the top 3.
4. Pilot a save program targeting the most common driver before expanding.

### "Help me build the CCO board section"
1. NRR / GRR for the trailing quarter + 4-quarter trend.
2. NPS (relationship + transactional) with segment breakdown.
3. Top 3 churn drivers, with a counter-action and an owner.
4. Top 3 expansion drivers and their adoption rate.
5. Asks: one budgetary, one organizational, one priority alignment.

## Anti-patterns to avoid

- **Customer-first as a slogan.** Without scorecards and consequences, it's marketing copy.
- **CSM as the universal solvent.** CSMs are not free; pair them to the right segment, not every customer.
- **Health-score voodoo.** A 17-component health score that no one understands rots. Start with 4–6 components; tune.
- **VoC without action loops.** Surveying customers without closing the loop trains them not to respond.
- **Renewals as a finance task.** Renewals are a strategic moment; insist on a 90/60/30 motion.
- **Expansion as cross-sell-only.** Usage-driven expansion is durable; cross-sell is volatile.

## Scope & Limitations

**In Scope:**
- CX strategy, CCO scope definition and the Sales, CS, Support and Services operating model
- CX maturity scoring (0-100) across strategy, segmentation, journey, voice, operations and talent with `cx_maturity_scorer.py`
- Prioritized churn interventions for at-risk accounts, with owner and SLA, from `churn_intervention_planner.py`
- VoC program scoring, target architecture and a 12-month rollout from `voc_program_designer.py`
- NRR thesis, CSM coverage ratios and the customer section of a board deck

**Out of Scope:**
- Day-to-day CSM playbooks and account management (see `business-growth/customer-success-manager/`)
- Running save campaigns and cancel flows (see `business-growth/churn-prevention/`)
- Renewal and expansion forecasting owned by the revenue org (see `c-level-advisor/cro-advisor/`)
- Fielding surveys, running interviews or pulling data from a CRM or support tool

**Important Caveats:**
- The tools read JSON you prepare by hand. They do not connect to a CRM, CS platform or survey tool, so results are only as current as the export behind them.
- Priority scores and intervention choices come from a fixed catalog keyed by risk driver and segment. They are heuristics, not a churn prediction model.
- CSM coverage ratios and NRR benchmarks are rough guides that vary by company. Treat them as a starting point, not a target.

## References

- `references/customer-experience-strategy.md` — CX strategy framing, segmentation, scorecards
- `references/retention-and-expansion-frameworks.md` — NRR thesis, save programs, expansion motions
- `references/voice-of-customer-program.md` — VoC architecture, action loops, instruments

## Related skills

- `business-growth/customer-success-manager` — operational CSM tactics
- `business-growth/churn-prevention` — execution of save programs
- `c-level-advisor/cmo-advisor` — customer marketing alignment
- `c-level-advisor/cro-advisor` — renewals + expansion boundary
- `c-level-advisor/cpo-advisor` — feedback loop to product
- `product-team/ux-researcher-designer` — interview frameworks for churn / expansion
