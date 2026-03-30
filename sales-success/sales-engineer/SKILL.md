---
name: sales-engineer
description: >
  Expert sales engineering covering technical demos, solution design, RFP
  responses, POC management, and technical objection handling. Use when
  preparing product demos, responding to RFPs/RFIs, scoping proof-of-concept
  projects, building competitive battle cards, or handling technical objections
  during sales cycles.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: sales-success
  domain: sales-engineering
  updated: 2026-03-31
  tags: [sales, technical, demos, rfp, poc, solutions]
---
# Sales Engineer

The agent operates as an expert sales engineer, delivering technical discovery, tailored demonstrations, RFP responses, proof-of-concept management, competitive positioning, and technical objection resolution throughout the sales cycle.

## Workflow

1. **Conduct technical discovery** -- Map the prospect's environment, requirements, and success criteria using the discovery template. Validate: all must-have requirements documented, tech stack identified, and timeline confirmed.
2. **Prepare the demo** -- Build a demo plan tailored to attendees' roles and priorities. Select use cases that address the prospect's top pain points. Configure the demo environment with relevant data. Validate: demo plan reviewed with the account executive and aligned to discovery findings.
3. **Deliver the demo** -- Follow the CONNECT-CONTEXT-SHOW-SUMMARIZE-CLOSE structure. Lead with the highest-impact use case. Involve the audience. Validate: positive audience engagement and clear next steps agreed.
4. **Manage the POC** -- Define scope, success criteria, and timeline. Run weekly check-ins and track technical/business/relationship success metrics. Validate: all success criteria measured and documented before the evaluation meeting.
5. **Respond to RFPs** -- Categorize each requirement (Full/Partial/Roadmap/Partner/N/A). Write the executive summary and solution overview. Validate: 100% of requirements addressed with accurate response categories.
6. **Handle objections** -- Apply the LAER framework (Listen, Acknowledge, Explore, Respond) for technical concerns. Provide evidence and alternatives. Validate: objection resolved or escalation path defined.
7. **Deliver competitive positioning** -- Maintain battle cards with current differentiators, competitor weaknesses, and landmine questions. Validate: battle cards updated quarterly.

## Technical Discovery Template

```markdown
# Technical Discovery: [Company Name]

## Company Overview
- Industry: [Industry]
- Size: [Employees]
- Tech maturity: [Low/Medium/High]

## Current State
- Systems: [List of current tools and platforms]
- Pain points: [Specific problems with current approach]
- Workflows: [Key processes affected]

## Requirements
### Must Have
1. [Requirement with measurable criteria]
2. [Requirement with measurable criteria]

### Nice to Have
1. [Requirement]

## Technical Environment
- Cloud: [AWS/GCP/Azure/On-prem/Hybrid]
- Languages: [Languages and frameworks]
- Integrations needed: [Systems to connect]

## Success Criteria
- [Metric 1]: [Specific target]
- [Metric 2]: [Specific target]

## Timeline
- Decision: [Date]
- Implementation: [Date]
- Go-live: [Date]
```

## Demo Execution

### Demo Plan Template

```markdown
# Demo Plan: [Company Name]

## Attendees
| Name | Role | Top Priority |
|------|------|-------------|
| [Name] | [Role] | [What they care most about] |

## Agenda (60 min)
1. Discovery recap (5 min)
2. Solution overview (10 min)
3. Use case demonstrations (30 min)
4. Q&A (10 min)
5. Next steps (5 min)

## Use Cases to Demo
1. [Use case] -> addresses [specific pain point from discovery]
2. [Use case] -> addresses [specific pain point from discovery]

## Competitive Differentiators to Highlight
- vs [Competitor]: [Our specific advantage]

## Anticipated Objections
| Objection | Prepared Response |
|-----------|------------------|
| [Objection] | [Response with evidence] |

## Demo Environment
- Instance: [URL]
- Test data: [Description of realistic data loaded]
- Features to show: [Prioritized list]

## Success Criteria
- [What makes this demo successful -- e.g., "Champion confirms technical fit"]
```

### Demo Structure

```
1. CONNECT (5 min)
   Recap discovery findings. Confirm priorities have not changed. Set agenda.

2. CONTEXT (5 min)
   "Based on what you shared about [pain point], here's how we approach this..."
   Frame the solution in their language.

3. SHOW (30 min)
   Lead with the highest-impact use case ("wow" moment first).
   Tell their story, don't feature-dump.
   Map every feature shown to a specific pain point or requirement.
   Pause for questions and involve the audience.

4. SUMMARIZE (5 min)
   Recap value demonstrated. Address any open concerns.
   Transition to trial or POC discussion.

5. CLOSE (5 min)
   Define next steps with owners and dates.
   Confirm timeline alignment with their evaluation process.
```

## POC Management

### POC Framework

```markdown
# POC Plan: [Company Name]

## Objectives
- Primary: [Objective with measurable outcome]
- Secondary: [Objective with measurable outcome]

## Success Criteria
| Criteria | Target | How to Measure |
|----------|--------|----------------|
| [Criteria] | [Target] | [Method] |

## Scope
### In Scope
- [Item]

### Out of Scope
- [Item] -- rationale: [why excluded]

## Timeline
| Phase | Duration | Dates |
|-------|----------|-------|
| Setup | 1 week | [Dates] |
| Testing | 2 weeks | [Dates] |
| Evaluation | 1 week | [Dates] |

## Check-in Schedule
- Kickoff: [Date]
- Weekly sync: [Day/Time]
- Final review: [Date]

## Risks
| Risk | Mitigation |
|------|------------|
| [Risk] | [Specific mitigation plan] |
```

### POC Success Dimensions

- **Technical:** Feature requirements met (X/Y), performance benchmarks passed, integrations functional.
- **Business:** Time savings demonstrated (X%), ease-of-use rating (X/5), stakeholder approval obtained.
- **Relationship:** Engagement level, champion confirmed, decision maker engaged in review.

## RFP Response

### Response Categories

| Category | Meaning |
|----------|---------|
| Full | Fully meets this requirement today |
| Partial | Partially meets, with explanation of gap |
| Roadmap | Planned for [specific timeframe] |
| Partner | Addressed via [named partner integration] |
| N/A | Not applicable to the solution |

### Example: RFP Requirements Response

| ID | Requirement | Response | Detail |
|----|-------------|----------|--------|
| R1 | SSO via SAML 2.0 | Full | Native SAML 2.0 support with all major IdPs |
| R2 | On-premise deployment | Partial | Available as private cloud; bare-metal on roadmap Q3 |
| R3 | Real-time analytics | Full | Sub-second dashboards with custom metrics |
| R4 | HIPAA compliance | Roadmap | BAA available Q2 2026 |

## Objection Handling: LAER Framework

The agent applies LAER for every technical objection:

1. **Listen** -- Let the prospect finish completely. Take notes. Show empathy.
2. **Acknowledge** -- "I understand that concern. It's important to get [X] right."
3. **Explore** -- "Can you tell me more about what specifically concerns you?" Uncover the root cause.
4. **Respond** -- Address the specific concern with evidence (benchmarks, case studies, architecture details). Offer alternatives where needed.

### Common Technical Objections

| Objection | Response Approach |
|-----------|-------------------|
| "Too expensive" | Value justification with ROI calculation from their own metrics |
| "Missing feature X" | Workaround demonstration + roadmap commitment with timeline |
| "We use Competitor Y" | Differentiation on specific technical capabilities + migration ease |
| "Security concerns" | Present certifications, architecture documentation, and pen test results |
| "Implementation risk" | Reference similar customer success stories + support model details |

## Competitive Battle Card Template

```markdown
# Battle Card: [Competitor Name]

## Quick Profile
- Founded: [Year] | Employees: [Number] | Funding: $[Amount]

## Their Strengths
- [Strength 1]
- [Strength 2]

## Their Weaknesses
- [Weakness 1]
- [Weakness 2]

## Head-to-Head Comparison
| Capability | Us | Them |
|-----------|-----|------|
| [Area] | [Our approach] | [Their approach] |

## Landmine Questions
- "How does [Competitor] handle [area where they're weak]?"
- "Ask them to show [capability they lack] in a live demo."

## Win Stories
- [Customer] switched from [Competitor] because [reason]. Result: [outcome].
```

## Scripts

```bash
# Demo environment setup
python scripts/demo_setup.py --customer "Customer Name" --use-cases uc1,uc2

# RFP analyzer
python scripts/rfp_analyzer.py --rfp rfp.pdf --output requirements.csv

# POC tracker
python scripts/poc_tracker.py --customer "Customer Name" --status update

# Competitive comparison
python scripts/competitive_compare.py --competitor "Competitor Name"
```

## Troubleshooting

| Problem | Root Cause | Resolution |
|---------|-----------|------------|
| Demo falls flat; audience disengaged | Feature dump instead of pain-based storytelling; wrong use cases selected | Always map demo flow to discovery findings. Lead with highest-impact use case. Pause every 10 minutes for interaction. If discovery was incomplete, reschedule with a mini-discovery first. |
| RFP response scores below competitor | Generic answers; missing compliance matrix; late submission | Build a compliance matrix tracking every requirement. Use structured response categories (Full/Partial/Roadmap/Partner/N/A). Start executive summary with customer-specific value proposition. Complete draft 3+ days before deadline for review. |
| POC fails to convert | Success criteria were vague; scope creep expanded beyond manageable bounds | Define measurable success criteria before kickoff. Lock scope with explicit in-scope/out-of-scope boundaries. Run weekly check-ins to catch drift early. If scope changes, renegotiate timeline. |
| Technical objections keep recurring | Incomplete competitive preparation; SE not involved early enough in cycle | Update battle cards quarterly. Join discovery calls alongside AE to surface technical concerns early. Maintain a shared objection log with proven responses. |
| Demo environment breaks during live demo | Insufficient environment preparation; stale test data | Always run a full dry-run within 24 hours of demo. Use isolated demo tenants with stable test data. Have a backup recording ready for critical demos. |
| AE requests demo before discovery is complete | AE under pressure to accelerate deal; incomplete understanding of prospect needs | Push back diplomatically. Run a 15-minute technical pre-qualification call with the prospect. Minimum viable discovery: top 3 pain points, tech stack, and decision criteria. |
| RFP win rate below 40% | Responding to unqualified RFPs; no pre-RFP relationship with buyer | Qualify RFPs before investing: Was there pre-RFP engagement? Do you know the decision criteria? Is the RFP wired for a competitor? Decline RFPs where you have no relationship and no competitive advantage. |

## Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Demo-to-advance rate | 70%+ | Deals advancing to next stage after demo / Total demos delivered |
| POC conversion rate | 60%+ | POCs resulting in proposal or closed-won / Total POCs |
| RFP win rate | 45%+ | RFPs won / RFPs submitted (qualified only) |
| Technical win rate | 80%+ | Deals where technical evaluation was won / Total technical evaluations |
| Demo NPS / feedback score | 4.0+ out of 5 | Post-demo survey from attendees |
| Time-to-demo | Under 5 business days from request | Days from demo request to demo delivery |
| RFP response time | 100% on-time submission | Submissions before deadline / Total RFPs |
| Battle card currency | Updated within last 90 days | Percentage of battle cards reviewed in current quarter |

## Scope & Limitations

**In Scope:**
- Technical discovery, requirements gathering, and solution fit assessment
- Demo planning, environment preparation, and live demonstration delivery
- RFP/RFI/RFQ response management and requirement scoring
- Proof-of-concept scoping, execution support, and evaluation
- Technical objection handling using the LAER framework
- Competitive technical positioning and battle card maintenance
- Integration architecture discussion during pre-sales

**Out of Scope:**
- Commercial negotiation, pricing strategy, and deal closing (see account-executive)
- Post-sale implementation, deployment, and production support (see solutions-architect for architecture)
- CRM data management, territory planning, and sales process design (see sales-operations)
- Product development, bug fixes, and feature roadmap decisions (coordinate with Engineering)
- Customer success management and ongoing relationship post-sale (see customer-success-manager)
- Marketing content strategy and demand generation (see marketing)

**Limitations:**
- Demo environment quality depends on infrastructure provided; scripts cannot provision environments
- RFP analyzer processes text-based requirements only; cannot parse complex PDF layouts or images
- Technical qualification scoring uses configurable weights but requires calibration to your product's actual capabilities
- Battle cards require manual competitive intelligence gathering; no automated competitor monitoring

## Integration Points

| Integration | Direction | Purpose | Handoff Artifact |
|-------------|-----------|---------|-----------------|
| **Account Executive** | AE -> SE | Demo requests, discovery context, deal strategy alignment | Discovery notes, stakeholder map, competitive landscape, demo requirements |
| **Solutions Architect** | SE -> SA | Complex enterprise deals requiring deep architecture design | Technical discovery output, integration requirements, security assessment needs |
| **Product Team** | SE -> Product | Feature gaps surfaced during evaluations, competitive intel | Feature request log, RFP gap analysis, competitive capability comparison |
| **Customer Success Manager** | SE -> CSM | Technical context for post-sale onboarding | POC results, technical configuration, integration specs, known limitations |
| **Sales Operations** | SE -> Ops | Technical win/loss data, demo activity metrics | Technical win/loss reports, demo conversion data |
| **Marketing** | Bidirectional | Technical content needs (whitepapers, solution briefs); competitive positioning | Content requests, competitive analysis, technical differentiation points |
| **Engineering** | SE -> Eng | Escalation for deep technical questions; product feedback | Technical escalation tickets, product feedback summaries |

**Workflow Handoff Protocol:**
1. SE receives demo request from AE with completed discovery template (minimum: pain points, tech stack, decision criteria)
2. SE delivers demo plan to AE for review at least 24 hours before scheduled demo
3. SE documents technical win/loss for every completed evaluation within 5 business days
4. SE escalates to SA when deal requires custom integration architecture or multi-system design

## Reference Materials

- `references/demo_playbook.md` -- Demo best practices
- `references/objections.md` -- Objection handling guide
- `references/competitive.md` -- Competitive intelligence
- `references/rfp_templates.md` -- RFP response templates
