# Stakeholder Map

**Project:** [Project Name]
**Version:** [Version Number]
**Date:** [Creation/Update Date]
**Owner:** [Project Manager Name]
**Next Review:** [Scheduled Review Date]

---

## Stakeholder Registry

| # | Name | Role | Organization | Power (1-10) | Interest (1-10) | Classification | Attitude |
|---|------|------|--------------|:------------:|:---------------:|----------------|----------|
| 1 | [Name] | [Role/Title] | [Dept/Org] | [1-10] | [1-10] | Manage Closely | Supporter |
| 2 | [Name] | [Role/Title] | [Dept/Org] | [1-10] | [1-10] | Keep Satisfied | Neutral |
| 3 | [Name] | [Role/Title] | [Dept/Org] | [1-10] | [1-10] | Keep Informed | Supporter |
| 4 | [Name] | [Role/Title] | [Dept/Org] | [1-10] | [1-10] | Monitor | Neutral |
| 5 | [Name] | [Role/Title] | [Dept/Org] | [1-10] | [1-10] | [Quadrant] | Blocker |

**Classification Threshold:** Power > 5 = High, Interest > 5 = High

**Attitude Key:** Supporter = actively advocates | Neutral = no strong position | Blocker = actively resists

---

## Power/Interest Grid

```
  Power
  10 |                                                          |
     |         KEEP SATISFIED            MANAGE CLOSELY         |
   8 |                                                          |
     |       (high power, low interest)  (high power, high      |
   6 |                                    interest)             |
     +---------------------------------------------------------+
   5 |                                                          |
     |         MONITOR                   KEEP INFORMED          |
   4 |                                                          |
     |       (low power, low interest)   (low power, high       |
   2 |                                    interest)             |
     |                                                          |
   0 +----+----+----+----+----+----+----+----+----+----+----+--+
     0    1    2    3    4    5    6    7    8    9   10
                              Interest
```

### Grid Placement

**Manage Closely (High Power / High Interest)**
- [ ] [Name] - Power: __, Interest: __
- [ ] [Name] - Power: __, Interest: __

**Keep Satisfied (High Power / Low Interest)**
- [ ] [Name] - Power: __, Interest: __
- [ ] [Name] - Power: __, Interest: __

**Keep Informed (Low Power / High Interest)**
- [ ] [Name] - Power: __, Interest: __
- [ ] [Name] - Power: __, Interest: __

**Monitor (Low Power / Low Interest)**
- [ ] [Name] - Power: __, Interest: __
- [ ] [Name] - Power: __, Interest: __

---

## Communication Plan

### Manage Closely

| Stakeholder | Frequency | Channel | Key Message | Owner |
|-------------|-----------|---------|-------------|-------|
| [Name] | Weekly | 1:1 meeting | [Tailored message] | [PM Name] |
| [Name] | Weekly | Steering committee | [Tailored message] | [PM Name] |

### Keep Satisfied

| Stakeholder | Frequency | Channel | Key Message | Owner |
|-------------|-----------|---------|-------------|-------|
| [Name] | Monthly | Executive summary email | [Tailored message] | [PM Name] |
| [Name] | Quarterly | Business review | [Tailored message] | [PM Name] |

### Keep Informed

| Stakeholder | Frequency | Channel | Key Message | Owner |
|-------------|-----------|---------|-------------|-------|
| [Name] | Bi-weekly | Newsletter | [Tailored message] | [PM Name] |
| [Name] | Per sprint | Demo invite | [Tailored message] | [PM Name] |

### Monitor

| Stakeholder | Frequency | Channel | Key Message | Owner |
|-------------|-----------|---------|-------------|-------|
| [Name] | Quarterly | All-hands update | General project status | [PM Name] |
| [Name] | Quarterly | Intranet page | Milestone announcements | [PM Name] |

---

## Engagement Strategy

### Supporters - Leverage Plan

| Supporter | How to Leverage |
|-----------|-----------------|
| [Name] | [How they can champion the project - e.g., advocate in leadership meetings] |
| [Name] | [How they can champion the project - e.g., early adopter, provide testimonials] |

### Blockers - Resolution Plan

| Blocker | Concern | Resolution Approach | Status | Target Date |
|---------|---------|---------------------|--------|-------------|
| [Name] | [Root cause of resistance] | [Specific actions to address] | Open | [Date] |
| [Name] | [Root cause of resistance] | [Specific actions to address] | Open | [Date] |

### Neutral - Conversion Plan

| Stakeholder | Opportunity to Convert | Approach |
|-------------|----------------------|----------|
| [Name] | [What could shift them to supporter] | [Actions to take] |
| [Name] | [What could shift them to supporter] | [Actions to take] |

---

## Risk Assessment for Key Stakeholders

| Stakeholder | Risk | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
|-------------|------|:-------------------:|:---------------:|------------|
| [Name] | [Risk of disengagement, blocking, etc.] | H | H | [Mitigation action] |
| [Name] | [Risk of scope creep requests, etc.] | M | H | [Mitigation action] |
| [Name] | [Risk of negative influence on others] | L | M | [Mitigation action] |

### Critical Stakeholder Dependencies

| Dependency | Stakeholder(s) | Impact if Unavailable | Contingency |
|------------|----------------|----------------------|-------------|
| [Budget approval] | [Name] | [Project pause] | [Delegate authority pre-approved] |
| [Technical sign-off] | [Name] | [Milestone delay] | [Backup reviewer identified] |

---

## Review Schedule

| Review Type | Frequency | Next Date | Participants |
|-------------|-----------|-----------|--------------|
| Classification review | Monthly | [Date] | PM, Sponsor |
| Communication effectiveness | Bi-weekly | [Date] | PM |
| Blocker status check | Weekly | [Date] | PM, relevant leads |
| Full stakeholder audit | Quarterly | [Date] | PM, Sponsor, key leads |
| Post-milestone review | At milestones | [Date] | PM, Sponsor |

---

## Change Log

| Date | Change | Reason | Updated By |
|------|--------|--------|------------|
| [Date] | Initial stakeholder map created | Project kickoff | [Name] |
| [Date] | [Description of change] | [Reason for reclassification] | [Name] |

---

**Companion Tool:** Run `python scripts/stakeholder_mapper.py --demo` to generate a sample map automatically.
**Reference Guide:** See `references/stakeholder-engagement-guide.md` for detailed engagement strategies.
