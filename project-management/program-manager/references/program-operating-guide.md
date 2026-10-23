# Program Operating Guide

Read this when running the program end-to-end: the six-step workflow, dashboard format, stakeholder/risk management, tool commands, troubleshooting, and success criteria. Pull the section that matches your current step.

---

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

This skill has no dependency tool. Build the matrix from each project's plan, or run `dependency_mapper.py --deps deps.json` from `project-management/delivery-manager/` for a cross-team dependency map with critical-path flags.

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
python scripts/resource_allocator.py --resources resources.json
```

Output shows each person's total and effective allocation across projects, FTE per project, average utilization, and flags anyone over-allocated (above 100%) or under-utilized. It reports the current allocation; a month-by-month forecast and budget have to be built from it by hand.

### 5. Track Benefits Realization

Benefits are part of the portfolio data: give each program a benefits target and the realized amount, and `python scripts/portfolio_dashboard.py --portfolio portfolio.json` reports realized against target per program.

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

`portfolio.json` follows the template that `python scripts/portfolio_dashboard.py --example` prints.

```text
$ python scripts/portfolio_dashboard.py --portfolio portfolio.json
Portfolio Dashboard: Digital Transformation Portfolio
Date: 2026-10-23  |  Programs: 2
======================================================================
Portfolio Health: ON TRACK
RAG: GREEN=1 | AMBER=1 | RED=0
Budget: $1,520,000 / $2,800,000 (54.3%)
Milestones: 8/12 (66.7%)

  [AMBER] Customer Platform Modernization  (Phase: Execution)
       Schedule: -3 days  |  Budget: 70%  |  Risks: 1 high
       Benefits: $1,200,000 / $5,000,000 (24%)
         - API Migration: Complete (100%)  Next: N/A (Done)
         - Frontend Rebuild: In Progress (60%)  Next: Beta Release (2026-04-15)

  [GREEN] Data Analytics Platform  (Phase: Planning)
       Schedule: +0 days  |  Budget: 15%  |  Risks: 0 high
       Benefits: $0 / $2,000,000 (0%)
         - Data Lake Setup: In Progress (33%)  Next: Schema Design Complete (2026-04-01)
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
| `portfolio_dashboard.py` | Portfolio and program status: RAG, budget, milestones, benefits realized | `python scripts/portfolio_dashboard.py --portfolio portfolio.json` |
| `milestone_tracker.py` | Milestone status and trend analysis | `python scripts/milestone_tracker.py --milestones milestones.json` |
| `resource_allocator.py` | Allocation across projects, over- and under-allocation | `python scripts/resource_allocator.py --resources resources.json` |

Each tool prints an input template with `--example` and supports `--json`.

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
