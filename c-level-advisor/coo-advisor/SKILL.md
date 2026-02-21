---
name: coo-advisor
description: Operations leadership advisor for COOs on business operations, process optimization, scaling infrastructure, cross-functional alignment, and operational excellence.
version: 1.0.0
author: borghei
category: executive-leadership
tags: [operations, process, scaling, efficiency, execution]
---

# COO Advisor

Operations leadership advisory for Chief Operating Officers.

## Core Competencies

- Business operations management
- Process design and optimization
- Cross-functional coordination
- Operational scaling
- Vendor and partner management
- Business continuity
- Operational metrics
- Resource allocation

## Operational Framework

### Operations Maturity Model

**Level 1 - Ad Hoc:**
- Processes are informal
- Tribal knowledge
- Reactive problem solving
- Inconsistent outcomes

**Level 2 - Defined:**
- Documented processes
- Basic metrics tracking
- Some automation
- Repeatable outcomes

**Level 3 - Managed:**
- KPIs and dashboards
- Regular reviews
- Continuous improvement
- Predictable outcomes

**Level 4 - Optimized:**
- Data-driven decisions
- Automated workflows
- Proactive optimization
- Industry-leading efficiency

### Process Documentation Standard

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

## Cross-Functional Alignment

### Operating Rhythm

**Daily:**
- Standup meetings (15 min)
- Issue escalation
- Key metrics review

**Weekly:**
- Department syncs
- Cross-functional coordination
- Pipeline/project reviews
- Customer escalations

**Monthly:**
- Business reviews
- Metric deep dives
- Process improvements
- Resource planning

**Quarterly:**
- Strategic reviews
- OKR assessment
- Planning cycles
- All-hands communication

### Meeting Cadence Template

| Meeting | Frequency | Duration | Attendees | Purpose |
|---------|-----------|----------|-----------|---------|
| Leadership Sync | Weekly | 60 min | Execs | Alignment |
| Ops Review | Weekly | 45 min | Dept heads | Execution |
| Business Review | Monthly | 90 min | Leadership | Performance |
| All Hands | Monthly | 60 min | Company | Communication |
| QBR | Quarterly | Half day | Leadership | Strategy |

## Scaling Operations

### Headcount Planning

**Capacity Model:**
```
Required HC = Volume / (Productivity × Utilization)

Volume: Work units per period
Productivity: Units per person per period
Utilization: Available time percentage
```

**Planning Factors:**
- Attrition rate (typically 10-20%)
- Ramp time for new hires
- Seasonal variations
- Growth assumptions

### Vendor Management

**Vendor Selection Criteria:**
1. Capability fit
2. Financial stability
3. Reference quality
4. Service levels
5. Pricing competitiveness
6. Contract flexibility

**Vendor Review Cadence:**
- Weekly: Operational issues
- Monthly: Performance metrics
- Quarterly: Business review
- Annual: Contract renewal

### Tool Stack Assessment

**Evaluation Framework:**
- User adoption rate
- Process efficiency gain
- Integration capability
- Total cost of ownership
- Vendor reliability
- Security compliance

## Operational Metrics

### Key Performance Indicators

**Efficiency:**
- Process cycle time
- First-time completion rate
- Cost per transaction
- Automation rate

**Quality:**
- Error rate
- Rework percentage
- Customer satisfaction
- SLA compliance

**Scalability:**
- Volume growth handling
- Cost per unit trend
- Capacity utilization
- Bottleneck identification

### Dashboard Structure

```
OPERATIONAL HEALTH
├── Volume metrics (transactions, requests, tickets)
├── Quality metrics (errors, rework, satisfaction)
├── Efficiency metrics (cycle time, cost per unit)
└── Capacity metrics (utilization, backlog)

TEAM PERFORMANCE
├── Productivity per person
├── SLA achievement
├── Training completion
└── Engagement score

SYSTEM HEALTH
├── System uptime
├── Integration status
├── Processing latency
└── Error rates
```

## Process Optimization

### Improvement Methodology

**1. Map Current State:**
- Document as-is process
- Identify handoffs
- Measure cycle times
- Calculate costs

**2. Identify Waste:**
- Waiting time
- Rework loops
- Manual steps
- Approval bottlenecks

**3. Design Future State:**
- Eliminate non-value steps
- Automate where possible
- Reduce handoffs
- Parallelize activities

**4. Implement Changes:**
- Pilot with subset
- Gather feedback
- Iterate and refine
- Roll out broadly

**5. Measure Impact:**
- Compare metrics
- Document savings
- Share learnings
- Sustain improvements

### Automation Priority Matrix

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

## Business Continuity

### BCP Framework

**Risk Assessment:**
1. Identify critical processes
2. Assess impact of disruption
3. Determine recovery priorities
4. Document dependencies

**Continuity Planning:**
1. Define recovery objectives (RTO/RPO)
2. Identify alternate sites/resources
3. Document procedures
4. Assign responsibilities

**Testing and Maintenance:**
1. Annual tabletop exercises
2. Periodic recovery drills
3. Plan updates after changes
4. Post-incident reviews

### Incident Classification

| Level | Impact | Response Time | Communication |
|-------|--------|---------------|---------------|
| P1 | Business critical | 15 min | Exec + all stakeholders |
| P2 | Major impact | 1 hour | Leadership + affected teams |
| P3 | Moderate impact | 4 hours | Team leads |
| P4 | Minor impact | 24 hours | Direct reports |

## Resource Allocation

### Capacity Planning

**Demand Forecasting:**
- Historical trend analysis
- Seasonality adjustments
- Growth rate assumptions
- Initiative impact

**Supply Planning:**
- Current headcount
- Hiring pipeline
- Contractor availability
- Automation roadmap

**Gap Analysis:**
- Capacity vs demand
- Skill gaps
- Location constraints
- Budget limitations

### Budget Management

**Operating Expense Categories:**
- Personnel (salary, benefits, contractors)
- Technology (software, hardware, hosting)
- Facilities (office, utilities, equipment)
- Services (professional, consulting)
- Travel and events

**Variance Analysis:**
- Actual vs budget comparison
- Root cause identification
- Forecast adjustment
- Corrective actions

## Common Scenarios

### Scenario: Rapid Scaling

When volume doubles in 6 months:
1. Identify bottleneck processes
2. Prioritize automation investments
3. Adjust hiring plan forward
4. Negotiate vendor capacity
5. Implement parallel processing
6. Monitor quality closely

### Scenario: Cost Reduction

When cutting operating costs by 20%:
1. Categorize all expenses
2. Identify non-essential spend
3. Renegotiate vendor contracts
4. Consolidate tools/systems
5. Automate manual processes
6. Rightsize team structure

### Scenario: System Outage

When critical system fails:
1. Activate incident response
2. Assess customer impact
3. Enable manual workarounds
4. Communicate to stakeholders
5. Restore service
6. Conduct post-mortem

## Reference Materials

- `references/process_templates.md` - Standard process documentation
- `references/scaling_playbook.md` - Scaling operations guide
- `references/vendor_management.md` - Vendor relationship framework
- `references/bcp_template.md` - Business continuity planning

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
