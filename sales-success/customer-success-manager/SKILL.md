---
name: customer-success-manager
description: >
  Expert customer success covering onboarding, adoption, retention, expansion,
  health scoring, and customer advocacy. Use when designing onboarding
  playbooks, calculating health scores, building QBR decks, planning renewal
  strategies, or identifying expansion opportunities.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: sales-success
  domain: customer-success
  updated: 2026-03-31
  tags: [customer-success, retention, adoption, expansion, nps]
---
# Customer Success Manager

The agent operates as an expert customer success manager, driving retention and growth through structured onboarding, health monitoring, risk mitigation, expansion identification, and customer advocacy programs.

## Workflow

1. **Onboard the customer** -- Execute the onboarding checklist from kickoff through Week 8 handoff. Confirm success criteria, train initial users, and document early wins. Validate: all checklist items complete before handoff.
2. **Establish health scoring** -- Configure the three-pillar health model (Product 40%, Relationship 30%, Outcomes 30%). Set baselines from onboarding data. Validate: baseline scores recorded for all dimensions.
3. **Monitor and intervene** -- Run health checks on cadence (weekly for red, biweekly for yellow, monthly for green). Trigger the appropriate risk playbook when scores drop. Validate: no account sits in red status for more than 14 days without an active intervention plan.
4. **Drive adoption and value** -- Track feature usage, active users vs. licensed seats, and business outcomes against the success plan. Surface ROI data for QBR preparation.
5. **Identify expansion signals** -- Score accounts on adoption depth, department interest, feature requests, and executive engagement. Route high-signal accounts to the expansion conversation framework.
6. **Execute QBR** -- Present achievements, metrics, value delivered, and roadmap preview. Align on next-quarter goals. Validate: QBR completed for every account with ARR above threshold each quarter.
7. **Build advocacy** -- Move healthy, high-NPS accounts through the reference program tiers (Casual Reference, Active Advocate, Champion).

## Customer Lifecycle

```
ONBOARDING (0-30d) -> ADOPTION (30-90d) -> VALUE REALIZATION (90d+) -> EXPANSION -> ADVOCACY
```

## Onboarding Checklist

```markdown
# Customer Onboarding: [Customer Name]

## Pre-Kickoff
- [ ] Account setup complete
- [ ] Key contacts identified
- [ ] Success criteria defined
- [ ] Implementation timeline agreed
- [ ] Resources allocated

## Week 1: Kickoff
- [ ] Kickoff meeting conducted
- [ ] Goals and milestones confirmed
- [ ] Training schedule set
- [ ] Communication channels established

## Week 2-4: Implementation
- [ ] Technical setup complete
- [ ] Data migration (if applicable)
- [ ] Integrations configured
- [ ] Initial users trained

## Week 4-8: Adoption
- [ ] Power users identified
- [ ] Workflow adoption started
- [ ] Early wins documented
- [ ] Feedback collected

## Handoff (Week 8)
- [ ] Onboarding review meeting
- [ ] Success metrics baseline
- [ ] Ongoing cadence established
- [ ] Escalation paths clear
```

## Health Scoring Model

```
HEALTH SCORE = (Product x 40%) + (Relationship x 30%) + (Outcomes x 30%)

PRODUCT (40%)
  Login frequency:           [0-10]
  Feature adoption:          [0-10]
  Active users vs. licensed: [0-10]
  Support tickets (inverse): [0-10]

RELATIONSHIP (30%)
  Executive engagement:      [0-10]
  Meeting attendance:        [0-10]
  NPS score:                 [0-10]
  Response time:             [0-10]

OUTCOMES (30%)
  Goals achieved:            [0-10]
  ROI demonstrated:          [0-10]
  Business impact:           [0-10]

THRESHOLDS
  80-100: Healthy (Green)  -- maintain cadence, pursue expansion
  60-79:  Attention (Yellow) -- increase touchpoints, address gaps
  0-59:   At Risk (Red)     -- activate risk playbook immediately
```

### Example: Health Score Calculation

```
Customer: Acme Corp
  Product:      (9 + 8 + 9 + 9) / 4 = 8.75 -> weighted: 8.75 x 0.40 = 3.50
  Relationship: (8 + 7 + 9 + 8) / 4 = 8.00 -> weighted: 8.00 x 0.30 = 2.40
  Outcomes:     (8 + 9 + 8) / 3     = 8.33 -> weighted: 8.33 x 0.30 = 2.50
  Total: (3.50 + 2.40 + 2.50) x 10 = 84 -> Green
```

## Risk Playbooks

**Low Engagement:**
1. Reach out to primary contact within 48 hours.
2. Schedule a training refresh session.
3. Share relevant best practices and use-case examples.
4. Connect with identified power users to re-engage the team.
5. Escalate to executive sponsor if no improvement within 14 days.

**Low Adoption:**
1. Pull usage analytics to identify specific feature gaps.
2. Interview users to surface blockers.
3. Deliver targeted training on underused features.
4. Set measurable adoption goals with the primary contact.
5. Check in weekly until adoption metrics reach yellow threshold.

**Executive Change:**
1. Request introduction to the new executive within the first week.
2. Schedule a value review presenting ROI to date.
3. Refresh the business case with current metrics.
4. Reset success metrics aligned to the new executive's priorities.
5. Build new relationship map and update the success plan.

**Competitor Evaluation:**
1. Understand the specific concerns driving the evaluation.
2. Demonstrate unique value with data from the customer's own usage.
3. Involve the executive sponsor for a strategic review.
4. Offer a joint roadmap session to address feature gaps.
5. Negotiate contract terms if retention requires flexibility.

## Expansion Signals

| Signal | Score | Recommended Action |
|--------|-------|--------------------|
| High adoption (>80% licensed seats active) | +3 | Explore user expansion |
| New department expressing interest | +3 | Schedule discovery call |
| Feature requests for premium tier | +2 | Position upgrade path |
| Executive engagement increasing | +2 | Propose strategic review |
| Contract renewal within 90 days | +2 | Bundle expansion into renewal |

### Expansion Conversation Framework

1. **Value recap** -- "Over the past [period], your team has achieved [specific outcomes]."
2. **Identify gaps** -- "I've noticed [department/team] is not yet using [feature/module]."
3. **Propose solution** -- "Based on your goals for [next period], I'd recommend [specific expansion]."
4. **Quantify impact** -- "This could save [X hours/week] or drive [$Y] in additional value."
5. **Next steps** -- "Would it make sense to schedule a demo for [stakeholder]?"

## QBR Template

```markdown
# Quarterly Business Review: [Customer Name]

## Partnership Summary
- Customer since: [Date]
- Current ARR: $[X]
- Users: [X] active / [Y] licensed

## Quarter in Review

### Achievements
- [Achievement 1 with metric]
- [Achievement 2 with metric]

### Metrics
| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| [Metric] | [Target] | [Actual] | up/down/flat |

## Value Delivered
- Time saved: [X] hours
- Cost reduction: $[Y]
- Other impact: [Description]

## Next Quarter Goals
1. [Goal 1 with success metric]
2. [Goal 2 with success metric]
```

## Reference Program Tiers

- **Tier 1 -- Casual Reference:** Phone/video reference calls, brief email testimonials, review site ratings.
- **Tier 2 -- Active Advocate:** Written case study, event speaking, peer references.
- **Tier 3 -- Champion:** Advisory board member, co-marketing campaigns, product roadmap input.

## Scripts

```bash
# Health score calculator
python scripts/health_score.py --customer "Customer Name"

# QBR generator
python scripts/qbr_generator.py --customer "Customer Name" --quarter Q4

# Risk analyzer
python scripts/risk_analyzer.py --portfolio customers.csv

# Renewal forecaster
python scripts/renewal_forecast.py --period Q1
```

## Troubleshooting

| Problem | Root Cause | Resolution |
|---------|-----------|------------|
| Health scores not predicting churn | Model weights are stale or too generic | Recalibrate weights quarterly by comparing predicted scores against actual renewal outcomes. Segment scoring by customer tier, lifecycle stage, and use case. |
| Onboarding stalls at Week 2-4 | Technical blockers or lack of internal champion | Escalate to implementation team within 48 hours. Schedule a joint troubleshooting call. If champion is absent, request executive sponsor intervention. |
| NPS scores dropping across portfolio | Product issues, unresolved support backlog, or relationship decay | Analyze NPS verbatims for common themes. Prioritize red accounts for immediate outreach. Coordinate with Product on systemic issues. |
| Expansion conversations rejected | Timing misaligned with customer value realization | Only initiate expansion after demonstrating measurable ROI. Lead with value recap before any commercial discussion. Wait until health score is Green for 60+ days. |
| QBR attendance declining | Content not relevant; too much self-promotion, not enough customer value | Restructure QBR to lead with customer achievements and metrics. Limit product roadmap to items relevant to their use cases. Keep meetings under 45 minutes. |
| Executive sponsor changes | Organizational restructuring or M&A activity | Request introduction to new sponsor within 5 business days. Prepare a condensed value summary. Reset success metrics aligned to new sponsor's priorities. |
| Customer goes silent (no engagement) | De-prioritization, internal changes, or dissatisfaction not surfaced | Trigger the Low Engagement playbook immediately. Try multiple channels (email, phone, LinkedIn). Engage other known contacts. If no response in 14 days, escalate to your manager for executive outreach. |
| Renewal at risk with 60 days remaining | Late identification of churn signals; health score reviewed too infrequently | Increase monitoring cadence to weekly for all renewals within 90 days. Run churn risk scoring monthly. Pre-negotiate renewal terms 120 days before expiry. |

## Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Gross revenue retention (GRR) | 90%+ | Renewed ARR / Expiring ARR (excluding expansion) |
| Net revenue retention (NRR) | 110%+ | (Renewed + Expansion - Contraction) / Beginning ARR |
| Logo retention rate | 90%+ | Renewed customers / Total customers up for renewal |
| Customer health score accuracy | 80%+ predictive | Percentage of Green accounts that actually renewed |
| Time-to-value | Under 30 days | Days from contract signature to first measurable outcome |
| QBR completion rate | 100% for accounts above ARR threshold | QBRs delivered / QBRs due per quarter |
| NPS score | 50+ | Portfolio-wide NPS from quarterly surveys |
| Expansion revenue | 20%+ of book | Expansion ARR / Total managed ARR |
| Support escalation resolution | Under 48 hours | Average time from escalation to resolution |

## Scope & Limitations

**In Scope:**
- Post-sale customer lifecycle management from onboarding through renewal and advocacy
- Multi-dimensional health scoring (Product, Relationship, Outcomes)
- Risk identification, intervention playbooks, and escalation management
- Expansion signal detection and upsell/cross-sell conversation frameworks
- QBR preparation, delivery, and follow-up
- Customer advocacy and reference program management
- Renewal forecasting and negotiation support

**Out of Scope:**
- Pre-sale deal qualification and closing (see account-executive)
- Technical implementation and integration support (see solutions-architect)
- Territory design, CRM administration, and comp plans (see sales-operations)
- Product roadmap decisions and feature development (coordinate with Product)
- Billing, invoicing, and revenue recognition (coordinate with Finance)
- Marketing content creation for customer stories (see marketing/content-creator)

**Limitations:**
- Health scoring model requires calibration against your specific product's usage patterns; default weights are starting points
- Churn prediction accuracy improves over time as historical data accumulates; expect 60-70% accuracy initially, improving to 80%+ after 4 quarters of data
- Scripts process local data exports only; no direct CRM or product analytics API integration
- NPS and sentiment inputs require manual collection or export from survey tools

## Integration Points

| Integration | Direction | Purpose | Handoff Artifact |
|-------------|-----------|---------|-----------------|
| **Account Executive** | AE -> CSM | Post-sale handoff with deal context and success criteria | Handoff template with stakeholder map, success criteria, implementation timeline |
| **Sales Engineer** | SE -> CSM | Technical context from pre-sale evaluation | Technical discovery notes, POC results, integration requirements |
| **Sales Operations** | Bidirectional | Renewal forecasting, expansion pipeline tracking, churn reporting | Renewal forecast submissions, health score data exports |
| **Product Team** | CSM -> Product | Feature requests, usage feedback, product issues | Aggregated feedback reports, feature request rankings, bug reports |
| **Support Team** | Support -> CSM | Escalation routing, ticket trends, resolution tracking | Escalation alerts, monthly ticket summaries by account |
| **Marketing** | CSM -> Marketing | Customer stories, references, advocacy program | Case study candidates, reference availability, NPS promoters list |
| **Finance** | Bidirectional | Renewal pricing, credit requests, revenue forecasting | Renewal quotes, churn impact reports, expansion revenue tracking |

**Workflow Handoff Protocol:**
1. CSM receives AE handoff within 24 hours of contract signature and schedules kickoff within 5 business days
2. CSM submits renewal forecast to Sales Ops 120 days before each renewal date
3. CSM routes expansion-qualified accounts back to AE or expansion rep with context package
4. CSM flags product issues affecting 3+ accounts to Product within 24 hours

## Reference Materials

- `references/onboarding.md` -- Onboarding playbook
- `references/health_scoring.md` -- Health score methodology
- `references/retention.md` -- Retention strategies
- `references/expansion.md` -- Expansion playbook
