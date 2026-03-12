---
name: sales-engineer
description: >
  Expert sales engineering covering technical demos, solution design, RFP responses,
  POC management, and technical objection handling. Use when preparing product demos,
  responding to RFPs/RFIs, scoping proof-of-concept projects, building competitive
  battle cards, or handling technical objections during sales cycles.
version: 1.0.0
author: borghei
category: sales-success
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

## Reference Materials

- `references/demo_playbook.md` -- Demo best practices
- `references/objections.md` -- Objection handling guide
- `references/competitive.md` -- Competitive intelligence
- `references/rfp_templates.md` -- RFP response templates
