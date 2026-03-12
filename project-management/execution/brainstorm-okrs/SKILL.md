---
name: brainstorm-okrs
description: >
  OKR brainstorming and validation using the Radical Focus framework. Generates
  outcome-focused objectives with measurable key results and counter-metrics.
  Use when setting quarterly OKRs, validating existing OKRs against quality criteria,
  aligning team goals to company objectives, or teaching teams the difference between
  outputs and outcomes in goal-setting.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  python-tools: okr_validator.py
  tech-stack: okr, radical-focus, goal-setting, strategic-planning
---

# OKR Brainstorming Expert

The agent generates and validates outcome-focused OKR sets using Christina Wodtke's Radical Focus methodology. It produces inspirational objectives with measurable key results, applies counter-metric tests, and scores quality against proven criteria.

## Workflow

### 1. Identify the Theme

The agent asks: "What is the single most important thing this team needs to change this quarter?" The answer becomes the theme. Every OKR must connect back to this theme.

**Validation checkpoint:** If the user provides more than one theme, the agent pushes back. One theme per team per quarter. Multiple themes means no focus.

### 2. Generate 3 Distinct OKR Sets

For each set, the agent produces:

1. **Objective** -- One qualitative, inspirational statement (no numbers)
2. **Key Result 1** -- Primary metric proving progress
3. **Key Result 2** -- Secondary metric capturing a different dimension
4. **Key Result 3** -- Counter-metric preventing gaming of KR1 and KR2
5. **Rationale** -- 2-3 sentences on why this set matters and how it connects to the theme

**Objective quality criteria:**
- Qualitative (numbers belong in key results)
- Inspirational (team would be excited to achieve it)
- Time-bound (achievable within one quarter)
- Actionable (team can directly influence the outcome)

**Key result quality criteria:**
- Measurable (has a metric with a number)
- Outcome-focused (measures results, not activities)
- Set at 60-70% confidence (not sandbagging, not demoralizing)
- Limited to 3 per objective

### 3. Apply the Counter-Metric Test

For every pair of key results, the agent asks: "Could we hit these numbers by doing something harmful?" If yes, it adds a counter-metric.

Example: If KR1 is "Increase sign-ups by 40%", a counter-metric is "Maintain activation rate above 60%." Without it, the team could game KR1 by lowering sign-up barriers so far that unqualified users flood in.

### 4. Validate with Tool

```bash
python scripts/okr_validator.py --input okrs.json
```

The validator scores each OKR set and surfaces quality issues: disguised tasks, missing metrics, output-framed key results, or missing counter-metrics.

**Validation checkpoint:** Any OKR set scoring below 70% must be revised before committing.

## Example: Quarterly OKR Generation

**Input:** Theme is "retention" for a SaaS product team.

**Output:**

```
OKR Set 1:
  Objective: "Become the product teams can't imagine leaving"
  KR1: Reduce monthly churn from 4.2% to 2.5%
  KR2: Increase 90-day retention cohort from 68% to 82%
  KR3 (counter): Maintain NPS score above 45 (prevent forced lock-in tactics)
  Rationale: Churn is the top revenue leak. Improving retention directly
  increases LTV and reduces pressure on acquisition spend.

OKR Set 2:
  Objective: "Make our onboarding so good that users hit value in their first session"
  KR1: Increase Day-1 activation rate from 34% to 55%
  KR2: Reduce time-to-first-value from 12 minutes to under 4 minutes
  KR3 (counter): Maintain support ticket volume below 200/week (don't hide complexity)
  Rationale: Users who activate on Day 1 retain at 3x the rate. Onboarding
  is the highest-leverage retention lever.

OKR Set 3:
  Objective: "Turn our power users into vocal advocates"
  KR1: Increase referral-sourced signups from 8% to 20% of new users
  KR2: Grow active community members from 500 to 2,000
  KR3 (counter): Maintain power user retention above 95% (don't distract them)
  Rationale: Advocacy compounds. Referred users have 37% higher retention
  than paid-acquisition users.
```

```bash
$ python scripts/okr_validator.py --input okrs.json

OKR Validation Results
======================
Set 1: 92/100 - PASS
  Objective: Qualitative, inspirational, time-bound
  KR1: Measurable, outcome-focused, stretch target
  KR2: Measurable, different dimension from KR1
  KR3: Valid counter-metric for churn reduction

Set 2: 88/100 - PASS
  Objective: Qualitative, inspirational, time-bound
  KR1: Measurable, outcome-focused
  KR2: Measurable, tracks different dimension
  KR3: Valid counter-metric
  Note: "under 4 minutes" - verify baseline measurement exists

Set 3: 85/100 - PASS
  Objective: Qualitative, inspirational
  KR1: Measurable, outcome-focused
  KR2: Measurable, but "active" needs precise definition
  KR3: Valid counter-metric
```

## Common OKR Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Disguised task | "Launch the mobile app" | Ask "why?" -- measure the outcome the launch enables |
| Too many OKRs | 5 objectives per team | Pick 1, maybe 2. More means no focus |
| 100% confidence | Target you know you will hit | Stretch to 60-70% confidence |
| Activity metric | "Publish 12 blog posts" | Measure impact: "Increase organic traffic by 30%" |
| Set and forget | Review only at quarter end | Weekly check-ins with confidence scoring |
| Top-down only | All OKRs from leadership | Combine top-down direction with bottom-up team insight |

## OKRs vs KPIs vs North Star Metric

| Concept | Purpose | Cadence | Example |
|---------|---------|---------|---------|
| North Star Metric | Single metric capturing core value delivery | Permanent | Weekly active users completing a workflow |
| KPIs | Health indicators across the business | Ongoing | Revenue, churn rate, response time |
| OKRs | Ambitious quarterly goals that move KPIs | Quarterly | "Become the fastest onboarding in our category" |

**Relationship:** OKRs are the lever pulled to move KPIs toward the North Star Metric. KPIs indicate business health. The NSM indicates core value delivery. OKRs define what changes this quarter.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `okr_validator.py` | Validate and score OKR sets | `python scripts/okr_validator.py --input okrs.json` |
| `okr_validator.py` | Run demo validation | `python scripts/okr_validator.py --demo` |

## References

- `references/okr-best-practices.md` -- Detailed OKR guide with examples and anti-patterns
- `assets/okr_template.md` -- OKR document template and quarterly review format
