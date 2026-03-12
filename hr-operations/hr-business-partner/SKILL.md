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
# Workforce planning calculator
python scripts/workforce_plan.py --current headcount.csv --growth 0.2

# Attrition analyzer
python scripts/attrition_analyzer.py --data terminations.csv

# Compensation analyzer
python scripts/comp_analyzer.py --roles roles.csv --market market_data.csv

# Engagement survey analyzer
python scripts/engagement_analyzer.py --survey survey_results.csv
```
