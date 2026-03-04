# PRD Writing Guide

A section-by-section guide for writing effective product requirements documents.

---

## Section 1: Summary

### What Makes a Good Summary

- **Length:** 2-3 sentences maximum. If it takes longer, the scope is too large or you do not understand it yet.
- **Structure:** What it is + who it is for + why now.
- **Test:** Can someone who knows nothing about your company read this and understand what you are building?

### Good Example

"TaskFlow is a task management tool for distributed engineering teams that need async collaboration across time zones. It replaces manual standup updates with automated progress tracking. We are building this now because remote-first work has made synchronous updates impractical for 70% of our customer base."

### Bad Example

"TaskFlow is a next-generation, AI-powered productivity platform that leverages cutting-edge technology to synergize cross-functional workflows and empower teams to achieve unprecedented efficiency gains."

The bad example uses jargon, makes vague claims, and does not tell you what the product actually does.

---

## Section 2: Contacts

### Tips

- Only list people who will actively contribute decisions or approvals.
- Include their specific responsibility, not just their job title.
- Keep it under 6 people. If more are involved, the project may be too large for one PRD.

---

## Section 3: Background

### Three Questions to Answer

1. **Context:** Describe the current state as if explaining to a new team member. What exists? What do users do today?
2. **Why now?** Something changed. Name it specifically: competitor launched X, customer churn increased Y%, new API became available, board set a new strategic direction.
3. **What recently became possible?** This is the most overlooked question. It separates "we should do this eventually" from "we can and should do this now."

### Anti-Patterns

- Restating the objective as background ("We need to build this because it is important")
- Including solution details in the background section
- Writing more than one page

---

## Section 4: Objective

### Good Objectives vs Bad Objectives

| Good | Bad |
|------|-----|
| Reduce customer onboarding time from 3 days to 4 hours | Improve onboarding |
| Increase monthly active users from 10K to 25K | Grow our user base |
| Reduce support tickets per user from 2.1/month to 0.8/month | Improve product quality |

**Pattern:** Good objectives include a specific metric, current value, target value, and timeframe.

### Writing Key Results

- Each KR must have a number attached to it.
- KRs measure outcomes, not outputs. "Launch feature X" is an output. "Reduce time-to-task from 5 min to 2 min" is an outcome.
- Aim for 60-70% confidence that you can hit the target. If you are 100% confident, the target is too easy.

---

## Section 5: Market Segments

### Definition Tips

Define segments by shared problems or jobs-to-be-done, not demographics.

**Why:** Demographics describe who people are. Jobs describe what people need. Two people with identical demographics may have completely different needs. Two people with different demographics may share the exact same problem.

### Format

"[Segment name]: People who need to [job/problem] because [context]."

### Examples

- "Overwhelmed managers: People who need to track progress across 5+ direct reports because their organization lacks standardized reporting."
- "Solo founders: People who need to validate product-market fit quickly because they have limited runway and no dedicated research team."

---

## Section 6: Value Proposition

### Frameworks

**Jobs-Gains-Pains:**
- **Jobs:** Functional tasks, social goals, or emotional needs the user is trying to satisfy.
- **Gains:** Outcomes the user wants. Benefits they expect, desire, or would be surprised by.
- **Pains:** Risks, obstacles, and negative outcomes the user wants to avoid.

**Value Curve:**
Plot your product against alternatives on key factors. Identify where you invest heavily (differentiation), where you match (table stakes), and where you deliberately underinvest (strategic tradeoff).

The value curve prevents "me too" products by forcing explicit tradeoff decisions.

---

## Section 7: Solution

### Feature Prioritization

- **P0 (Must-have):** Product does not ship without this. Users cannot accomplish the core job.
- **P1 (Important):** Significantly improves the experience. Ship in v1 if possible, v1.1 at latest.
- **P2 (Nice-to-have):** Adds polish or secondary value. Defer without guilt.

### Assumptions

Every PRD contains assumptions. The dangerous ones are the ones you do not write down. List them explicitly with a plan to validate each one.

Common assumption categories:
- User behavior assumptions ("Users will adopt this workflow")
- Technical assumptions ("The API can handle this load")
- Market assumptions ("Competitors will not ship this first")
- Business assumptions ("This will reduce churn")

---

## Section 8: Release

### Timeline Tips

- Use relative sizing (S/M/L/XL) or Now/Next/Later unless you have firm dates.
- Specific dates create false precision. Stakeholders treat "Q2 2026" as a promise.
- Be explicit about what is NOT in v1. Deferred items show stakeholders their request was heard but intentionally sequenced.

---

## PRD Review Checklist

Use this before sharing the PRD with stakeholders:

### Clarity
- [ ] Can someone outside the team understand the Summary in 10 seconds?
- [ ] Is every acronym defined on first use?
- [ ] Are there zero instances of jargon ("leverage," "synergy," "paradigm")?

### Completeness
- [ ] All 8 sections are filled in (not just placeholder text)?
- [ ] At least 2 Key Results with metrics, baselines, and targets?
- [ ] At least 1 market segment defined by problem, not demographics?
- [ ] At least 3 assumptions listed with validation plans?

### Specificity
- [ ] Objective includes a measurable metric?
- [ ] Features have priority labels (P0/P1/P2)?
- [ ] v1 scope has a clear boundary (what is in and what is out)?
- [ ] Success criteria reference specific Key Results?

### Consistency
- [ ] Summary aligns with Objective aligns with Key Results?
- [ ] Market segments match the value propositions?
- [ ] Features map to at least one value proposition?
- [ ] Deferred items do not contradict v1 scope?

---

## Common PRD Anti-Patterns

1. **The Novel** -- PRD is 20+ pages. Nobody reads it. Solution: If it is longer than 6 pages, split into multiple PRDs.
2. **The Wishlist** -- Everything is P0. Solution: Force-rank. Only 3-5 features can be P0.
3. **The Solution Looking for a Problem** -- Starts with the feature, not the customer need. Solution: Write Sections 3-5 before Section 7.
4. **The Vague Objective** -- "Improve the user experience." Solution: Attach a number.
5. **The Missing Audience** -- Written for engineers but shared with executives (or vice versa). Solution: Summary for execs, Details for engineers, same document.
6. **The Immortal PRD** -- Never updated after initial writing. Solution: Set a review cadence (biweekly during active development).
7. **The Assumption-Free Zone** -- No assumptions listed, as if the team knows everything. Solution: List at least 3 things you believe but have not proven.
