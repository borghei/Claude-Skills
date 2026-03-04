---
name: brainstorm-okrs
description: OKR brainstorming expert that generates and validates outcome-focused objectives and key results using the Radical Focus framework.
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

## Overview

Structured OKR creation and validation based on Christina Wodtke's "Radical Focus" methodology. This skill generates high-quality OKR sets with inspirational objectives and measurable key results, then validates them against proven quality criteria. The goal is outcome-focused goal-setting that drives real change rather than task tracking disguised as strategy.

### When to Use

- **Quarterly Planning** -- Setting team or company OKRs for the upcoming quarter.
- **Strategic Alignment** -- Connecting team goals to company-level objectives.
- **Goal Quality Check** -- Validating existing OKRs before committing to them.
- **OKR Training** -- Teaching teams the difference between good and bad OKRs.

## OKR Framework (Radical Focus)

### Anatomy of an Objective

An objective is a qualitative, inspirational statement of what you want to achieve. It should be:

- **Qualitative** -- No numbers in the objective itself. Numbers belong in key results.
- **Inspirational** -- Would you be excited to achieve this? If not, rewrite it.
- **Time-bound** -- Quarterly cadence. If it takes longer than a quarter, it is too big.
- **Actionable** -- The team must be able to influence the outcome directly.
- **SMART-compatible** -- Specific enough to know when you have achieved it.

**Good:** "Become the most trusted onboarding experience in our category"
**Bad:** "Increase NPS by 15 points" (that is a key result, not an objective)
**Bad:** "Improve things" (too vague to be actionable)

### Anatomy of a Key Result

A key result is a quantitative measure of progress toward the objective. Each key result must be:

- **Measurable** -- Has a metric with a number.
- **Outcome-focused** -- Measures the result, not the activity. "Reduce churn to 3%" is an outcome. "Launch 5 features" is an output.
- **Set at 60-70% confidence** -- If you are certain you will hit it, the target is too easy. If you are certain you will miss it, the target is demoralizing.
- **Limited to 3 per objective** -- More than 3 means you lack focus.

### OKRs vs KPIs vs North Star Metric

These are complementary, not alternatives:

| Concept | Purpose | Cadence | Example |
|---------|---------|---------|---------|
| **North Star Metric (NSM)** | Single metric that captures core value delivery | Permanent | Weekly active users who complete a workflow |
| **KPIs** | Health indicators across the business | Ongoing | Revenue, churn rate, response time |
| **OKRs** | Ambitious quarterly goals that move KPIs | Quarterly | "Become the fastest onboarding in our category" |

**Relationship:** OKRs are the lever you pull to move KPIs toward the NSM. KPIs tell you if the business is healthy. The NSM tells you if you are delivering core value. OKRs tell you what you are trying to change this quarter.

## Brainstorming Process

### Step 1: Identify the Theme

Before writing OKRs, answer: "What is the single most important thing we need to change this quarter?" This becomes the theme. Every OKR set should connect back to this theme.

### Step 2: Generate 3 Distinct OKR Sets

For each OKR set, produce:

1. **Objective** -- One inspirational, qualitative statement.
2. **Key Result 1** -- The primary metric that proves progress.
3. **Key Result 2** -- A secondary metric that captures a different dimension.
4. **Key Result 3** -- A counter-metric that ensures you are not gaming KR1 and KR2.
5. **Rationale** -- 2-3 sentences explaining why this OKR set matters and how it connects to the theme.

### Step 3: Apply the Counter-Metric Test

For every pair of key results, ask: "Could we hit these numbers by doing something harmful?" If yes, add a counter-metric.

Example: If KR1 is "Increase sign-ups by 40%", a counter-metric might be "Maintain activation rate above 60%." Without the counter-metric, you could hit KR1 by lowering sign-up barriers so much that unqualified users flood in.

### Step 4: Validate with `okr_validator.py`

Run the validator to score each OKR set and surface quality issues.

## Common OKR Mistakes

1. **Disguised tasks** -- "Launch the mobile app" is a task, not a key result. Ask: "Why are we launching it? What outcome do we expect?"
2. **Too many OKRs** -- More than 3 objectives per team means no focus. Pick one, maybe two.
3. **100% confidence targets** -- If you know you will hit it, you are sandbagging. Stretch.
4. **Measuring activity, not impact** -- "Publish 12 blog posts" is activity. "Increase organic traffic by 30%" is impact.
5. **Set and forget** -- OKRs need weekly check-ins. If you only look at them at quarter end, they are not working.
6. **Top-down only** -- The best OKRs combine top-down strategic direction with bottom-up team insight.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `okr_validator.py` | Validate and score OKR sets | `python scripts/okr_validator.py --input okrs.json` |
| `okr_validator.py` | Run demo validation | `python scripts/okr_validator.py --demo` |

## References

- `references/okr-best-practices.md` -- Detailed OKR guide with examples and common mistakes
- `assets/okr_template.md` -- OKR document template and quarterly review format
