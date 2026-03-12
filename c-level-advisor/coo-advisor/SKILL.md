---
name: coo-advisor
description: >
  Operations leadership advisor for COOs on business operations, process
  optimization, scaling infrastructure, cross-functional alignment, and
  operational excellence. Use when designing operational processes, planning
  headcount capacity, optimizing vendor relationships, building business
  continuity plans, or scaling operations for rapid growth.
version: 1.0.0
author: borghei
category: executive-leadership
tags: [operations, process, scaling, efficiency, execution]
---

# COO Advisor

The agent acts as a fractional COO, providing operational strategy and process design grounded in maturity-model thinking and data-driven optimization.

## Workflow

1. **Assess operational maturity** -- Place the organization on the Operations Maturity Model (Levels 1-4). Validate the assessment by checking for documented processes, KPI dashboards, and automation coverage.
2. **Map critical processes** -- Identify the top 5 processes by volume or business impact. Document each using the Process Documentation Standard.
3. **Identify waste** -- For each mapped process, catalogue waiting time, rework loops, manual steps, and approval bottlenecks. Quantify cycle time and cost per transaction.
4. **Prioritize improvements** -- Plot identified improvements on the Automation Priority Matrix. Select quick wins (high value, low effort) for immediate action.
5. **Design operating rhythm** -- Establish the meeting cadence (daily, weekly, monthly, quarterly) and assign owners. Verify each meeting has a defined purpose and output.
6. **Build capacity model** -- Apply the headcount formula to forecast resource needs. Factor in attrition, ramp time, and seasonal variation.
7. **Establish metrics and reporting** -- Configure the Operational Dashboard and set targets for efficiency, quality, and scalability KPIs.

## Operations Maturity Model

| Level | Name | Characteristics |
|-------|------|-----------------|
| 1 | Ad Hoc | Informal processes, tribal knowledge, reactive problem solving |
| 2 | Defined | Documented processes, basic metrics, some automation |
| 3 | Managed | KPI dashboards, regular reviews, continuous improvement |
| 4 | Optimized | Data-driven decisions, automated workflows, industry-leading efficiency |

## Process Documentation Standard

```markdown
# Process Name

## Purpose
[Why this process exists]

## Owner
[Single accountable person]

## Trigger
[What initiates this process]

## Inputs
[What is needed to start]

## Steps
1. [Step with responsible party]
2. [Step with responsible party]
3. [Step with responsible party]

## Outputs
[What is produced]

## SLAs
[Time and quality expectations]

## Exceptions
[How to handle edge cases]
```

## Operating Rhythm

| Meeting | Frequency | Duration | Attendees | Purpose |
|---------|-----------|----------|-----------|---------|
| Standup | Daily | 15 min | Team | Issue escalation, key metrics |
| Dept Sync | Weekly | 45 min | Dept heads | Cross-functional coordination |
| Leadership Sync | Weekly | 60 min | Execs | Alignment |
| Business Review | Monthly | 90 min | Leadership | Performance deep-dive |
| QBR | Quarterly | Half day | Leadership | Strategy and OKR assessment |

## Headcount Capacity Model

```
Required HC = Volume / (Productivity x Utilization)

Volume:       Work units per period
Productivity: Units per person per period
Utilization:  Available time percentage (typically 75-85%)
```

**Adjustment factors**: Attrition rate (10-20%), ramp time for new hires, seasonal variation, growth assumptions.

## Automation Priority Matrix

```
                    High Value
                        |
    Quick Wins     -----+-----   Strategic Projects
    (Do First)          |        (Plan Carefully)
                        |
    Low Effort ---------+--------- High Effort
                        |
    Fill-ins       -----+-----   Reconsider
    (Do When Available) |        (May Not Be Worth It)
                        |
                    Low Value
```

## Operational KPIs

| Category | Metrics |
|----------|---------|
| Efficiency | Process cycle time, first-time completion rate, cost per transaction, automation rate |
| Quality | Error rate, rework %, customer satisfaction, SLA compliance |
| Scalability | Volume growth handling, cost per unit trend, capacity utilization, bottleneck count |

## Operational Dashboard Structure

```
OPERATIONAL HEALTH
+-- Volume metrics (transactions, requests, tickets)
+-- Quality metrics (errors, rework, satisfaction)
+-- Efficiency metrics (cycle time, cost per unit)
+-- Capacity metrics (utilization, backlog)

TEAM PERFORMANCE
+-- Productivity per person
+-- SLA achievement
+-- Training completion
+-- Engagement score

SYSTEM HEALTH
+-- System uptime
+-- Integration status
+-- Processing latency
+-- Error rates
```

## Incident Classification

| Level | Impact | Response Time | Communication |
|-------|--------|---------------|---------------|
| P1 | Business critical | 15 min | Exec + all stakeholders |
| P2 | Major impact | 1 hour | Leadership + affected teams |
| P3 | Moderate impact | 4 hours | Team leads |
| P4 | Minor impact | 24 hours | Direct reports |

## Vendor Management

**Selection criteria**: Capability fit, financial stability, reference quality, service levels, pricing competitiveness, contract flexibility.

**Review cadence**: Weekly (operational issues), Monthly (performance metrics), Quarterly (business review), Annual (contract renewal).

## BCP Framework

1. **Risk assessment** -- Identify critical processes, assess disruption impact, determine recovery priorities, document dependencies.
2. **Continuity planning** -- Define RTO/RPO, identify alternate resources, document procedures, assign responsibilities.
3. **Testing** -- Annual tabletop exercises, periodic recovery drills, plan updates after changes, post-incident reviews.

## Example: Scaling Customer Onboarding (Series B SaaS)

A Series-B SaaS company onboards 40 new customers/month with a 5-person onboarding team. Current cycle time is 21 days.

```
Current state:
  Volume: 40 customers/month
  Productivity: 8 customers/person/month
  Utilization: 80%
  Required HC: 40 / (8 x 0.80) = 6.25 -> 7 FTEs (gap: 2 hires)

Optimization targets:
  Automate provisioning step (saves 3 days) -> cycle time: 18 days
  Self-serve data migration portal (saves 2 days) -> cycle time: 16 days
  Revised productivity: 10 customers/person/month
  Required HC at 80 customers/month: 80 / (10 x 0.80) = 10 FTEs

Investment: 1 eng sprint for automation + $15K/yr portal tooling
ROI: Handles 2x volume with 43% fewer incremental hires
```

## Budget Variance Analysis

1. Compare actual vs budget by category (personnel, technology, facilities, services, travel)
2. Identify root causes for variances exceeding 10%
3. Adjust rolling forecast
4. Document corrective actions with owners and deadlines

## Scripts

```bash
# Process efficiency analyzer
python scripts/process_analyzer.py --process onboarding

# Capacity planning calculator
python scripts/capacity_planner.py --forecast demand.csv

# Vendor scorecard generator
python scripts/vendor_scorecard.py --vendors vendors.yaml

# Operational dashboard builder
python scripts/ops_dashboard.py --metrics metrics.json
```

## References

- `references/process_templates.md` -- Standard process documentation
- `references/scaling_playbook.md` -- Scaling operations guide
- `references/vendor_management.md` -- Vendor relationship framework
- `references/bcp_template.md` -- Business continuity planning
