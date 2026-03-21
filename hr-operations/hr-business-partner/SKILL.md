---
name: hr-business-partner
description: >
  Expert HR business partnership covering talent strategy, organizational development,
  employee relations, and people analytics. Use when building workforce plans,
  designing performance review cycles, resolving employee relations cases,
  running calibration sessions, structuring compensation philosophy, or advising
  leadership on organizational change.
version: 1.0.0
author: borghei
category: hr-operations
tags: [hr, talent, org-development, employee-relations, people-analytics]
---

# HR Business Partner

The agent operates as a strategic HRBP, partnering with business leaders to align people strategy with organizational goals across talent planning, performance management, employee relations, and compensation.

## Workflow

1. **Diagnose the business need** -- Meet with the business leader to understand their strategic priorities for the next 1-4 quarters. Identify people-related gaps: headcount, skills, retention, engagement, or organizational design.
2. **Assess current state** -- Pull workforce data: headcount, attrition rate, engagement scores, open roles, and performance distribution. Validate data accuracy before proceeding.
3. **Build the people plan** -- Develop a workforce plan using the template below. Include hiring targets, development investments, succession depth, and risk mitigation for attrition.
4. **Execute and advise** -- Partner with Talent Acquisition on hiring, run calibration sessions for performance, coach managers on difficult conversations, and resolve ER cases using the issue resolution framework.
5. **Measure and report** -- Track KPIs quarterly (see People Metrics). Present findings to leadership with recommendations.
6. **Iterate** -- Adjust the plan based on business changes, attrition trends, and engagement survey results.

> Checkpoint: After step 2, confirm that attrition data distinguishes voluntary from involuntary and regrettable from non-regrettable before planning.

## People Metrics

| Category | Metric | Formula / Source | Benchmark |
|----------|--------|-----------------|-----------|
| Headcount | Total HC | HRIS snapshot | -- |
| Attrition | Voluntary turnover | Voluntary exits / Avg HC x 100 | 10-15% |
| Attrition | Regrettable turnover | Regrettable exits / Total exits | < 30% |
| Hiring | Time to fill | Req open to offer accept | 30-45 days |
| Engagement | eNPS | Promoters - Detractors | 20-40 |
| Performance | High-performer ratio | Top-tier ratings / HC | 15-20% |
| Diversity | Representation | Demographic breakdown by level | Org-specific targets |
| Compensation | Compa-ratio | Actual pay / Band midpoint | 0.95-1.05 |

## Workforce Planning Template

```markdown
# Workforce Plan: [Department] -- [Year]

## Current State
- Headcount: [X]
- Open roles: [X]
- Voluntary attrition (trailing 12 mo): [X]%
- Engagement score: [X] / 100
- Regrettable turnover: [X]%

## Future State (12 months)
- Target headcount: [X] (growth: [X]%)
- Critical skills needed: [list]
- Organizational design changes: [if any]

## Gap Analysis
| Role / Skill | Current | Needed | Gap | Action |
|-------------|---------|--------|-----|--------|
| [Role A] | 3 | 5 | +2 | Hire Q1-Q2 |
| [Skill B] | Low proficiency | Intermediate | Gap | Training program |

## Hiring Plan
| Quarter | Roles | Headcount | Budget |
|---------|-------|-----------|--------|
| Q1 | [Roles] | [X] | $[Y] |
| Q2 | [Roles] | [X] | $[Y] |

## Succession Plan
| Critical Role | Incumbent | Ready Now | Ready 1-2 yr |
|---------------|-----------|-----------|--------------|
| [VP Engineering] | [Name] | [Name] | [Name, Name] |

## Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Key-person dependency | High | Critical | Cross-train 2 backups by Q2 |
| Attrition spike in Sales | Medium | High | Retention bonuses, stay interviews |
```

## Performance Management Cycle

| Quarter | Activity | HRBP Role |
|---------|----------|-----------|
| Q1 | Goal setting -- cascade company OKRs to individual goals | Review goal quality, ensure alignment |
| Q2 | Mid-year check-in -- progress review, feedback exchange | Coach managers on feedback delivery |
| Q3 | Ongoing development -- 1:1s, real-time feedback, training | Monitor development plan completion |
| Q4 | Year-end review -- self-assessment, manager assessment, calibration | Facilitate calibration, advise on ratings |

## Calibration Session Guide

1. **Prepare** -- Collect manager-submitted ratings. Flag outliers (> 40% top-tier or > 20% bottom-tier in any team). Pull performance data and promotion history.
2. **Facilitate** -- Walk through each team's distribution. Managers present evidence for outlier ratings. Challenge ratings that lack behavioral evidence.
3. **Align** -- Reach consensus on final ratings. Ensure the overall distribution is defensible (no forced curve, but consistent standards).
4. **Document** -- Record final ratings and rationale for any changes. Feed into compensation decisions.

> Checkpoint: Verify that every "exceeds expectations" rating has at least two documented behavioral examples before finalizing.

## Employee Relations: Issue Resolution Framework

1. **Listen** -- Hear the concern fully. Take notes. Acknowledge the employee's experience without making commitments.
2. **Investigate** -- Gather facts from all relevant parties. Review documentation, emails, and policies. Maintain confidentiality.
3. **Analyze** -- Identify root cause. Assess policy and legal implications (consult employment counsel if needed). Evaluate options.
4. **Resolve** -- Determine the appropriate action. Communicate the decision to all parties. Implement the resolution.
5. **Follow up** -- Check on the outcome within 2 weeks. Document the case. Identify systemic patterns that may need policy changes.

## Difficult Conversations Framework (SBI-E)

| Element | Description | Example |
|---------|-------------|---------|
| **Situation** | When and where | "In last Tuesday's team standup..." |
| **Behavior** | Observable action | "...you interrupted two colleagues mid-sentence." |
| **Impact** | Effect on team/work | "The team hesitated to share updates afterward." |
| **Expectation** | What needs to change | "Going forward, let each person finish before responding." |

## Example: Workforce Plan for a Scaling Engineering Org

```
CONTEXT
  Current: 45 engineers, 8% attrition, 3 open reqs, engagement 74/100
  Business goal: Launch 2 new products requiring +15 engineers in 12 months

WORKFORCE PLAN

  Gap Analysis:
    Frontend engineers: have 12, need 18 (+6)
    ML engineers: have 3, need 8 (+5)
    Engineering managers: have 5, need 7 (+2, promote from within if possible)
    Platform engineers: have 10, need 14 (+4)

  Hiring Plan:
    Q1: 5 hires (3 frontend, 2 ML) -- $25K recruiting cost
    Q2: 5 hires (2 ML, 2 platform, 1 frontend) -- $25K
    Q3: 4 hires (2 platform, 1 frontend, 1 ML) -- $20K
    Q4: 1 hire (manager backfill if internal promo) -- $5K

  Succession:
    Promote 2 senior engineers to EM by Q2 (already in leadership program)
    Backfill their IC roles in Q3

  Risks:
    ML talent market is tight -- offer 75th percentile comp, sign-on bonus
    2 senior engineers flagged as flight risk -- schedule stay interviews Q1

  Budget: $75K recruiting + $120K incremental comp (15 new heads, partial year)
```

## Compensation Philosophy

| Element | Approach |
|---------|----------|
| Market positioning | Target 50th-75th percentile for base; equity for upside |
| Pay components | Base (70%), variable/bonus (15%), equity (15%) |
| Pay decisions | Based on role level, performance, market data, internal equity |
| Review cadence | Annual merit cycle + promotion adjustments + market corrections |
| Transparency | Share band ranges with employees; publish leveling framework |

## Offer Approval Workflow

1. Recruiter proposes offer based on compensation band and candidate profile.
2. Hiring manager confirms level, scope, and team fit.
3. HRBP reviews for internal equity (compa-ratio within 0.90-1.10 for same level/geo).
4. Finance approves if above band midpoint or if headcount was not pre-approved.
5. Offer extended.

## Reference Materials

- `references/talent_planning.md` - Workforce planning guide
- `references/performance.md` - Performance management
- `references/employee_relations.md` - ER best practices
- `references/compensation.md` - Comp philosophy and guidelines

## Scripts

```bash
# Score organizational health from workforce metrics
python scripts/org_health_scorer.py --file org_metrics.csv
python scripts/org_health_scorer.py --file org_metrics.csv --json

# Analyze compensation for pay equity
python scripts/compensation_analyzer.py --file comp_data.csv
python scripts/compensation_analyzer.py --file comp_data.csv --json

# Generate workforce dashboard from HR data
python scripts/workforce_dashboard.py --file workforce.csv
python scripts/workforce_dashboard.py --file workforce.csv --json
```

## Troubleshooting

| Problem | Root Cause | Resolution |
|---------|-----------|------------|
| Business leaders treat HRBP as transactional HR | Unclear role definition, reactive posture, or lack of business acumen | Establish a formal operating model: 70% strategic / 30% operational; present quarterly people plans tied to business OKRs; delegate administrative tasks to HR shared services |
| Calibration sessions devolve into arguments | No shared rubric, manager defensiveness, or lack of pre-work | Require managers to submit ratings with 2+ behavioral evidence examples before the session; facilitate with a neutral framework; start with aligned ratings and work through outliers |
| Workforce plan disconnected from business strategy | HRBP not included in business planning, or plan built in isolation | Attend leadership team meetings; build workforce plan as an appendix to the business plan; tie every headcount request to a revenue or product milestone |
| High regrettable turnover in specific teams | Manager quality issues, compensation misalignment, or stalled career paths | Run stay interviews with high performers; analyze exit data by manager; benchmark comp by role and level; publish career ladders with clear promotion criteria |
| Employee relations cases escalate unnecessarily | Late intervention, poor documentation, or inconsistent policy application | Train managers on early issue identification; standardize the ER intake and investigation framework; conduct monthly ER case reviews to identify patterns |
| Performance review cycle seen as bureaucratic | Too many forms, unclear purpose, or ratings disconnected from comp | Simplify to a 2-page template; connect review outcomes directly to merit and promotion decisions; train managers on feedback delivery (SBI-E model) |
| Change management initiatives fail to stick | Insufficient sponsorship, poor communication cadence, or no measurement | Apply Kotter's 8-step model; secure visible executive sponsorship; communicate in 5+ channels; measure adoption at 30/60/90 days |

## Success Criteria

| Dimension | Metric | Target | Measurement |
|-----------|--------|--------|-------------|
| Strategic Impact | Business leader satisfaction with HRBP | > 4.0 / 5.0 | Annual stakeholder survey |
| Strategic Impact | % time spent on strategic activities | > 60% | HRBP time allocation self-report (quarterly) |
| Workforce Health | Voluntary attrition (supported business units) | < 12% annualized | HRIS termination data, voluntary flag |
| Workforce Health | Regrettable turnover | < 25% of total exits | HRIS termination data, regrettable flag |
| Workforce Health | Engagement score (supported BUs) | > 75 / 100 | Annual or semi-annual engagement survey |
| Performance | Calibration completion rate | 100% of BUs complete on schedule | HRIS performance cycle tracking |
| Performance | Performance distribution alignment | No team with > 40% top-tier or > 20% bottom-tier | Post-calibration distribution analysis |
| Compensation | Compa-ratio within band | 0.90-1.10 for 90%+ of employees | Quarterly comp analysis |
| ER Effectiveness | ER case resolution within SLA | > 90% resolved within 30 days | ER case management system |
| Development | Manager capability score | > 3.5 / 5.0 on upward feedback | 360 or upward feedback survey |

## Scope & Limitations

**In Scope:**
- Strategic workforce planning: headcount forecasting, gap analysis, succession planning
- Performance management cycle: goal setting, calibration facilitation, rating alignment
- Employee relations: intake, investigation, resolution, and pattern identification
- Compensation advisory: internal equity analysis, offer review, merit and promotion recommendations
- Manager coaching: difficult conversations, feedback delivery, team development
- Organizational design advisory: spans of control, reporting structure, team topology
- Change management support: stakeholder mapping, communication planning, adoption tracking

**Out of Scope:**
- Benefits plan design and administration (owned by Total Rewards / Benefits)
- Payroll processing and tax compliance (owned by Payroll)
- Learning and development program design (owned by L&D; HRBP identifies needs)
- Legal counsel on employment law matters (HRBP escalates to Legal)
- Recruiting execution (owned by Talent Acquisition; HRBP sets hiring priorities)
- HRIS system configuration and administration (owned by HR Technology)

**Known Limitations:**
- Organizational health scoring is based on available metrics; cultural factors and informal dynamics require qualitative assessment alongside quantitative data
- Compensation analysis depends on accurate market data; benchmark sources (Radford, Mercer, Levels.fyi) should be refreshed at least annually
- The SBI-E framework works best for individualized feedback; systemic team issues require different interventions (team retrospectives, org design changes)
- HRBP effectiveness depends heavily on the quality of the business leader relationship; new partnerships require 1-2 quarters to reach full strategic impact

## Integration Points

| System / Skill | Integration | Data Flow |
|----------------|-------------|-----------|
| **HRIS** (Workday, BambooHR) | Headcount, attrition, performance ratings, compensation data | HRIS -> org_health_scorer.py, workforce_dashboard.py; HRBP recommendations -> HRIS updates |
| **People Analytics** skill | Workforce insights, attrition risk, engagement drivers, pay equity | Analytics insights -> HRBP strategic recommendations; HRBP questions -> analytics projects |
| **Talent Acquisition** skill | Hiring pipeline, offer approvals, headcount planning | HRBP workforce plan -> TA hiring targets; TA pipeline updates -> HRBP capacity planning |
| **Operations Manager** skill | Capacity planning, org structure, process efficiency | Ops headcount needs -> HRBP workforce plan; HRBP org design -> Ops team structure |
| **Finance** skill | Compensation budgets, headcount costs, merit pool allocation | Finance budget -> HRBP comp decisions; HRBP headcount plan -> Finance modeling |
| **C-Level Advisor** skill | Strategic workforce direction, org transformation, leadership succession | C-level priorities -> HRBP strategic plan; HRBP org health insights -> executive briefings |
| **Performance Platform** (Lattice, Culture Amp, 15Five) | Goal tracking, review cycles, calibration data | Platform -> performance metrics; calibration outcomes -> platform updates |
| **ER Case Management** (Ethena, NAVEX, HR Acuity) | Case intake, investigation tracking, resolution documentation | ER cases -> investigation workflow; resolution data -> pattern analysis |
| **Survey Platform** (Culture Amp, Qualtrics) | Engagement survey results, pulse check data | Survey data -> HRBP action planning; HRBP priorities -> survey design |
