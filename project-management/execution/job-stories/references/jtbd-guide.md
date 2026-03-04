# Jobs-to-Be-Done (JTBD) Guide

## Theory Overview

Jobs-to-Be-Done is a framework for understanding why people use products. The core insight: people do not buy products -- they "hire" products to do a job for them. When you understand the job, you build better products.

**Key concepts:**

- **A job is a progress a person is trying to make** in a particular circumstance.
- **Jobs are stable over time.** People have wanted to "get from A to B quickly" for centuries. The solutions change (horse, car, rideshare), but the job stays the same.
- **Jobs have functional, emotional, and social dimensions.** The functional job is the task. The emotional job is how the person wants to feel. The social job is how they want to be perceived.

**Origin:** Clayton Christensen popularized JTBD in *The Innovator's Solution* (2003). The framework has been further developed by Tony Ulwick (Outcome-Driven Innovation) and Alan Klement (job stories for product design).

## Job Stories vs User Stories

### User Story Format

```
As a [role], I want to [action], so that [benefit].
```

**Strengths:**
- Simple and widely understood.
- Easy to map to personas.
- Good for teams with established persona research.

**Weaknesses:**
- Anchors thinking to roles/personas, which may not reflect real usage patterns.
- The "role" component often becomes a placeholder ("As a user...").
- Can lead to building features for personas instead of real situations.

### Job Story Format

```
When [situation], I want to [motivation], so I can [outcome].
```

**Strengths:**
- Focuses on context and trigger, which are observable and testable.
- Removes persona assumptions -- the same job may apply to multiple roles.
- Provides stronger design direction because the situation constrains the solution space.
- Naturally encourages empathy with the user's real circumstances.

**Weaknesses:**
- Requires deeper understanding of user context (more research investment).
- Less familiar to teams trained on user stories.
- Can feel more complex for simple CRUD features.

### When to Use Each

| Scenario | Recommended Format |
|----------|-------------------|
| Team is new to agile and needs simplicity | User stories |
| Strong persona research exists | User stories |
| Product has diverse users in varied situations | Job stories |
| Building for a new market or unknown users | Job stories |
| Design-heavy work where context matters | Job stories |
| Internal tools with well-defined roles | User stories |
| Mixed team with varying experience | Start with user stories, evolve to job stories |

## Writing Good Situations

The situation is the most important part of a job story. It provides the context that drives design decisions.

### Techniques for Discovering Situations

1. **Customer interviews** -- Ask "Walk me through the last time you needed to [do the job]." Listen for the trigger and context.
2. **Support ticket analysis** -- Look at what users were trying to do when they hit problems.
3. **Session recordings** -- Watch where users hesitate, backtrack, or abandon flows.
4. **"Five Whys" on feature requests** -- When a customer requests a feature, ask why five times to find the underlying situation.

### Situation Quality Checklist

- [ ] Describes a real-world moment, not an abstract need
- [ ] Includes temporal context (when does this happen?)
- [ ] Includes environmental context (where, with what constraints?)
- [ ] Is specific enough to guide design but not so specific it excludes valid use cases
- [ ] Does not mention the product or a specific solution

## Writing Good Motivations

The motivation describes what the user wants to do in the moment. It should be solution-agnostic.

### Common Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Naming a specific UI element | "I want to click the export button" | "I want to get my data out of the system" |
| Combining multiple motivations | "I want to review and approve the request" | Split into two stories |
| Being too vague | "I want to manage things" | "I want to see which tasks are overdue" |
| Describing the system's behavior | "I want the system to send a notification" | "I want to be alerted when something needs my attention" |

## Writing Good Outcomes

The outcome is the user's definition of success. It should be meaningful and measurable.

### Outcome Hierarchy

Outcomes can operate at different levels:

1. **Immediate outcome** -- What happens right now. "So I can see my balance."
2. **End outcome** -- What the immediate outcome enables. "So I can decide whether to make this purchase."
3. **Life outcome** -- The broader life goal. "So I can stay within my financial plan."

For job stories, aim for the **end outcome** level. Immediate outcomes are too small (they describe the UI). Life outcomes are too broad (they do not constrain design).

## INVEST Criteria Applied to Job Stories

### Independent

Each job story should be deliverable on its own. If story A requires story B to be done first, either combine them or ensure B is scheduled first and A is written to work on its own once B exists.

**Test:** Can the team demo this story in isolation?

### Negotiable

The story describes the what and why, not the how. The implementation is open to discussion between product, design, and engineering.

**Test:** Could the team solve this story in more than one way?

### Valuable

The outcome describes clear value to the user. Stories that only deliver value to the business or the system (not the user) should be reframed or classified as technical tasks.

**Test:** Would a user care if this story were done?

### Estimable

The situation is clear enough that the team can estimate the effort. If the team cannot estimate, the story needs more research or should be split.

**Test:** Can the team give a confidence-level estimate (even a range)?

### Small

A story should be completable within one sprint. If it spans multiple sprints, split it by situation, by outcome, or by scope (happy path vs. edge cases).

**Test:** Can the team finish this in one sprint?

### Testable

The acceptance criteria are specific enough to write test cases. If you cannot describe how to verify the outcome, the story is not ready.

**Test:** Can QA write a test plan from the acceptance criteria?

## Story Splitting Techniques

When a job story is too large, split it using one of these strategies:

### Split by Situation

If the story covers multiple situations, create one story per situation.

**Before:** "When I need to communicate with my team, I want to send messages, so I can collaborate."

**After:**
- "When I need a quick answer from a teammate, I want to send a direct message, so I can get unblocked without scheduling a meeting."
- "When I need to share an update with the whole team, I want to post to a channel, so everyone sees it without me messaging each person."

### Split by Outcome

If the story has multiple outcomes, create one story per outcome.

**Before:** "When I review the monthly report, I want to see revenue and churn data, so I can assess business health."

**After:**
- "When I review the monthly report, I want to see revenue trends by product line, so I can identify which products are growing."
- "When I review the monthly report, I want to see churn by customer segment, so I can prioritize retention efforts."

### Split by Complexity

Deliver the simple version first, then enhance.

**Before:** "When I search for a customer, I want to find them by any attribute, so I can quickly pull up their record."

**After:**
- "When I search for a customer, I want to find them by name or email, so I can quickly pull up their record."
- "When name or email search does not find the customer, I want to search by phone number or account ID, so I can still locate their record."

## References

- Clayton Christensen, *The Innovator's Solution* (2003)
- Tony Ulwick, *Jobs to Be Done: Theory to Practice* (2016)
- Alan Klement, *When Coffee and Kale Compete* (2018)
- Bob Moesta and Chris Spiek, *Demand-Side Sales 101* (2020)
- intercom.com/blog/using-job-stories-design-features-ui-ux -- Original job stories blog post
