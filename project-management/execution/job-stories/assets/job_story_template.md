# Job Story Templates

## Single Job Story Card

### [Title -- Short, Descriptive Name]

**Job Story:**
When [specific situation or trigger], I want to [motivation -- what the user wants to do], so I can [outcome -- the benefit or result the user achieves].

**Design:** [Link to Figma / Sketch / wireframe, or "TBD"]

**Acceptance Criteria:**

1. [ ] [Observable outcome that verifies the story is complete]
2. [ ] [Observable outcome under a specific condition]
3. [ ] [Edge case or error state handling]
4. [ ] [Performance or responsiveness criterion]
5. [ ] [Accessibility or cross-platform criterion]
6. [ ] [Data accuracy or consistency criterion]

**INVEST Check:**

| Criterion | Pass? | Notes |
|-----------|-------|-------|
| Independent | [ ] | Can be delivered without other stories |
| Negotiable | [ ] | Implementation is open to discussion |
| Valuable | [ ] | Outcome is meaningful to the user |
| Estimable | [ ] | Team can estimate the effort |
| Small | [ ] | Completable in one sprint |
| Testable | [ ] | Acceptance criteria are verifiable |

---

## Batch Job Story Worksheet

Use this worksheet to draft multiple job stories in a single session. Fill in the table first, then expand the best candidates into full story cards.

| # | Situation (When...) | Motivation (I want to...) | Outcome (So I can...) | Priority | Notes |
|---|--------------------|--------------------------|-----------------------|----------|-------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |

### Batch Review Checklist

After drafting, review each story against these questions:

- [ ] Is the situation specific and observable (not "when I use the app")?
- [ ] Is the motivation solution-agnostic (not naming a UI element)?
- [ ] Is the outcome meaningful and measurable (not "so I can use it")?
- [ ] Is each story independent enough to deliver on its own?
- [ ] Are any stories too large and need splitting?
- [ ] Are there duplicate or overlapping stories to merge?

---

## Acceptance Criteria Template (Given/When/Then Adapted for JTBD)

For teams that prefer structured acceptance criteria, adapt the Given/When/Then format to align with the job story:

```
Given [the situation from the job story],
When [the user takes the action from the motivation],
Then [the expected outcome is achieved].
```

### Example

**Job Story:** When I am preparing my weekly budget on Sunday evening, I want to see how much I have spent so far this month by category, so I can decide where to cut back before the month ends.

**Acceptance Criteria:**

```
Given I am viewing the budget screen during an active month,
When the spending summary loads,
Then I see all transactions grouped by category with totals for each.

Given a category has exceeded its budget,
When the spending summary is displayed,
Then that category is visually highlighted as over-budget.

Given no transactions exist for the current month,
When the spending summary loads,
Then a message explains that no spending has been recorded yet.

Given I tap on a specific category,
When the category detail view opens,
Then I see all individual transactions within that category for the current month.

Given I am on a mobile device,
When the spending summary is displayed,
Then all content is readable without horizontal scrolling.

Given a new transaction is recorded,
When I refresh the spending summary,
Then the updated totals reflect the new transaction within 5 seconds.
```

---

## Story Mapping Layout

Use this layout to organize job stories into a story map for release planning:

```
Activities (user goals):
[Goal A]                    [Goal B]                    [Goal C]

Steps (situations):
[Situation A1] [A2] [A3]   [Situation B1] [B2]         [Situation C1] [C2] [C3]

Stories (per situation, ordered by priority):
 A1-Story1    A2-Story1     B1-Story1     B2-Story1     C1-Story1
 A1-Story2    A2-Story2     B1-Story2                   C1-Story2
              A2-Story3
------- Release 1 line -------
 A1-Story3                  B1-Story3     B2-Story2     C1-Story3     C3-Story1
------- Release 2 line -------
```

Each row below the release line represents lower-priority stories for future releases.
