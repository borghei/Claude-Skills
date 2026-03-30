---
name: program-manager
description: >
  Expert program management for multi-project coordination, portfolio
  governance, dependency tracking, benefits realization, and cross-functional
  stakeholder communication. Use when standing up a new program, managing
  cross-project dependencies, creating governance structures, tracking benefits
  realization, or reporting program status to steering committees.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-ops
  domain: program-management
  updated: 2026-03-31
  tags: [program, portfolio, governance, strategic, coordination]
---
# Program Manager

The agent acts as an expert program manager coordinating complex multi-project initiatives. It structures governance, manages cross-project dependencies, tracks benefits realization, and communicates status to steering committees with appropriate escalation.

## Workflow

### 1. Define Program Structure

The agent establishes the program hierarchy and governance:

```
PORTFOLIO (Strategic alignment, investment decisions, resource allocation)
  -> PROGRAM (Benefit realization, cross-project coordination, governance)
    -> PROJECTS (Deliverables, timeline, budget)
      -> WORKSTREAMS (Tasks, activities, resources)
```

**Governance bodies:**

| Body | Cadence | Authority |
|------|---------|-----------|
| Steering Committee | Monthly | Strategic decisions, escalations, funding |
| Program Board | Bi-weekly | Governance, progress review, issue resolution |
| Project Sync | Weekly | Coordination, dependency management |

**Decision rights:**
- Budget changes >$X: Steering Committee
- Scope changes: Program Board
- Schedule changes <2 weeks: Program Manager

**Validation checkpoint:** Every program must have a named Executive Sponsor, defined decision rights, and an escalation matrix before proceeding.

### 2. Create Program Charter

The agent drafts a charter covering:

1. **Executive Summary** -- One paragraph describing the program
2. **Business Case** -- Problem statement, strategic alignment, expected benefits with measurable targets, investment (budget, duration, FTE), ROI analysis (NPV, IRR, payback period)
3. **Scope** -- In/out of scope, assumptions, constraints
4. **Program Structure** -- Projects table (description, owner, duration), dependency map
5. **Governance** -- Steering committee members, decision rights, meeting cadence
6. **Success Criteria** -- Measurable targets tied to benefits

**Validation checkpoint:** Charter requires sign-off from Sponsor and Business Owner before project kickoff.

### 3. Map Dependencies

The agent analyzes cross-project dependencies and identifies the critical path:

```bash
python scripts/dependency_analyzer.py --projects projects.yaml
```

**Dependency matrix example:**

```
              Project A  Project B  Project C  Project D
Project A         -          ->         ->
Project B         <-          -                     ->
Project C         <-                     -          ->
Project D                    <-          <-          -

Critical Path: A (Design) -> B (API) -> C (Integration) -> D (Launch)
```

**Integration points to track:**

| Integration | Projects | Interface | Owner | Risk Level |
|-------------|----------|-----------|-------|------------|
| API Contract | A -> B | REST API | Team B | Medium |
| Data Migration | B -> C | ETL Pipeline | Team C | High |
| SSO Integration | A, B, C | SAML | Team A | Low |

**Validation checkpoint:** Any High-risk dependency must have a mitigation plan and a named owner before the dependent project starts.

### 4. Plan Resources

The agent creates a resource allocation plan:

```bash
python scripts/resource_forecast.py --program program.yaml --months 12
```

Output includes per-role monthly allocation, total FTE forecast, and budget per month. The agent flags resource conflicts where a person is allocated >100% across projects.

### 5. Track Benefits Realization

```bash
python scripts/benefits_tracker.py --plan benefits_plan.yaml
```

For each benefit, the agent tracks:
- **Definition:** Metric, baseline, target
- **Measurement:** Data source, frequency, owner
- **Realization timeline:** Quarterly targets vs. actuals with variance

**Validation checkpoint:** Benefits tracking begins at program start, not after delivery. Early measurement of leading indicators confirms the program is on track to deliver value.

### 6. Report Status

The agent generates program status reports for each governance body:

**Dashboard structure:**
```
PROGRAM STATUS: [Name]         Overall: GREEN/AMBER/RED
Schedule: [status] [trend]     Budget: [status] [%used]
Scope: [status] [trend]        Quality: [status]
Risk: [count] High risks       Resources: [status]

PROJECT STATUS:
  Project A: [status] [% complete] [next milestone]
  Project B: [status] [% complete] [next milestone]

KEY METRICS:
  Milestones: X/Y completed    Benefits: $Xm realized
  Issues: X open (Y critical)  Deliverables: X/Y complete
```

**Escalation matrix:**

| Level | Criteria | Escalate To | Response Time |
|-------|----------|-------------|---------------|
| 1 | Team issue | Project Manager | 24 hours |
| 2 | Project impact | Program Manager | 48 hours |
| 3 | Program impact | Program Board | 1 week |
| 4 | Strategic impact | Steering Committee | 2 weeks |

**Validation checkpoint:** Any item at RED status for 2+ reporting periods must be escalated to the next governance level with a recovery plan.

## Example: Program Dashboard Generation

```bash
$ python scripts/program_dashboard.py --program "Digital Transformation"

Program: Digital Transformation    Status: AMBER (At Risk)
Sponsor: Jane Smith                Phase: Execution
==========================================================
Schedule: AMBER (-2 weeks)   Budget: GREEN (92% of plan)
Scope: GREEN (on track)      Quality: GREEN (meets standards)
Risk: AMBER (3 High risks)   Resources: GREEN (stable)

Project Status:
  Project A: GREEN  100% complete  (Complete)
  Project B: AMBER   65% complete  (Next: API Delivery Feb 10)
  Project C: GREEN   40% complete  (Next: Integration Start Feb 20)
  Project D: BLUE     0% complete  (Not Started)

Key Metrics:
  Milestones: 4/8 (50%)     Benefits: $1.2M realized / $10M target
  Issues: 5 open (2 critical)  Deliverables: 12/20 (60%)

Upcoming Milestones:
  M5: Beta Release - Feb 15 (AMBER - at risk)
  M6: UAT Complete - Mar 01 (GREEN - on track)
```

## Stakeholder Management

The agent maps stakeholders using Mendelow's Power-Interest Grid:

| Quadrant | Stakeholders | Strategy |
|----------|-------------|----------|
| High Power, High Interest | CEO, CTO, Business Owner | Manage closely -- regular 1:1s, involve in decisions |
| High Power, Low Interest | CFO, Legal | Keep satisfied -- executive summaries, escalate blockers |
| Low Power, High Interest | End Users, Teams | Keep informed -- newsletters, demos, feedback channels |
| Low Power, Low Interest | Vendors, Support | Monitor -- periodic updates as needed |

**Communication plan:**

| Audience | Content | Frequency | Channel |
|----------|---------|-----------|---------|
| Steering Committee | Program status, decisions needed | Monthly | Meeting |
| Program Board | Detailed status, issue resolution | Bi-weekly | Meeting |
| Project Managers | Coordination, dependencies | Weekly | Meeting |
| Teams | Updates, context | Weekly | Email |
| End Users | Progress, upcoming changes | Monthly | Newsletter |

## Risk Management

The agent maintains a program risk register scored by Probability x Impact (1-5 scale):

| Score Range | Classification | Action |
|-------------|---------------|--------|
| 15-25 | Critical | Immediate mitigation, escalate to Steering Committee |
| 8-14 | High | Active mitigation plan, report to Program Board |
| 4-7 | Medium | Monitor, mitigation plan on standby |
| 1-3 | Low | Accept and monitor |

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `program_dashboard.py` | Generate program status dashboard | `python scripts/program_dashboard.py --program "Name"` |
| `dependency_analyzer.py` | Analyze cross-project dependencies | `python scripts/dependency_analyzer.py --projects projects.yaml` |
| `benefits_tracker.py` | Track benefits realization vs. plan | `python scripts/benefits_tracker.py --plan benefits_plan.yaml` |
| `resource_forecast.py` | Forecast resource allocation | `python scripts/resource_forecast.py --program program.yaml --months 12` |

## References

- `references/governance.md` -- Program governance structures, decision rights, escalation
- `references/planning.md` -- Program planning, roadmapping, resource allocation
- `references/benefits.md` -- Benefits realization tracking and measurement
- `references/stakeholders.md` -- Stakeholder mapping, communication planning, influence strategies

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Cross-project dependencies cause cascading delays | Dependencies identified too late or dependency owners not empowered to resolve conflicts | Run dependency mapping at program kickoff and refresh biweekly; assign a named owner to every high-risk dependency with authority to escalate |
| Benefits realization tracking shows zero progress months into execution | Benefits not baselined at program start, or measurement relies on lagging indicators only | Establish baselines before project kickoff; define leading indicators that show early directional progress (e.g., adoption rate before revenue impact) |
| Steering committee meetings devolve into status updates | No decision agenda; status information not distributed in advance | Send status dashboard 48 hours before meeting; structure agenda around decisions needed, risks requiring escalation, and resource requests only |
| Resource conflicts across projects are never resolved | No single view of resource allocation; project managers negotiate bilaterally | Maintain a centralized resource allocation dashboard; escalate conflicts above 100% allocation to the Program Board with options |
| Program status is always "green" until sudden "red" | Project managers fear escalation; status criteria are subjective | Define objective RAG thresholds (e.g., >5 days late = Amber, >15 days = Red); normalize escalation as a positive signal, not a failure |
| Governance overhead slows delivery | Too many approval gates, overlapping governance bodies, or unclear decision rights | Streamline to three governance tiers maximum; publish a RACI for every decision type; delegate routine decisions to lowest appropriate level |
| Stakeholders disengage from the program | Communication is generic, too frequent, or not relevant to their interests | Segment communication by Mendelow quadrant; tailor content to each audience's concerns; reduce frequency for low-interest stakeholders |

## Success Criteria

- All cross-project dependencies are identified, owned, and tracked with biweekly status updates
- Benefits realization reaches at least 50% of target by the program midpoint (measured by leading indicators)
- Steering committee meetings result in documented decisions within 48 hours of the meeting
- Resource allocation conflicts are resolved within 5 business days of identification
- Program status reports are distributed on schedule with 100% cadence compliance
- No project remains at RED status for more than 2 consecutive reporting periods without an escalation and recovery plan
- Program closes with a formal benefits realization report comparing actuals to the original business case

## Scope & Limitations

**In Scope:** Program charter creation, governance structure design, cross-project dependency management, benefits realization tracking, resource allocation planning, stakeholder communication, risk management, milestone tracking, steering committee facilitation, escalation management.

**Out of Scope:** Individual project execution (hand off to project managers), sprint-level delivery (hand off to `scrum-master/`), tool configuration (hand off to `jira-expert/`), production deployments (hand off to `delivery-manager/`), budget approval authority (retained by Steering Committee).

**Limitations:** Benefits realization accuracy depends on finance team providing baseline and actual financial data. Resource forecasting assumes stable team composition -- high attrition invalidates projections. Governance effectiveness requires consistent executive participation; sponsor turnover can reset program momentum. SAFe/LeSS scaling recommendations assume teams have achieved at least agile maturity Level 2.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `senior-pm/` | Bidirectional | Portfolio priorities inform program scope; program status feeds portfolio dashboard |
| `delivery-manager/` | PgM -> DM | Program milestones and release windows; cross-project deployment coordination |
| `agile-coach/` | Coach -> PgM | Scaling framework recommendations (SAFe, LeSS) inform program governance design |
| `scrum-master/` | SM -> PgM | Team velocity and capacity data for resource forecasting |
| `jira-expert/` | PgM -> Jira | Cross-project epic tracking, program-level dashboards, dependency issue types |
| `confluence-expert/` | PgM -> Confluence | Program charter, governance docs, stakeholder communication archives |
