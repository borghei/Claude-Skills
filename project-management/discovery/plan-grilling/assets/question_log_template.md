# Question Log — <plan or idea, one line>

**Mode:** single-session | multi-session (session <n> of <expected>)
**Started:** <YYYY-MM-DD>   **Last round:** <n>
**Decision-maker:** <who answers the decision questions>

Keep this file next to the plan. Every question the grilling raises lands here,
including the ones the agent answered itself. Mirror it into the JSON shape in
`sample_question_log.json` when you want the checker to gate it.

## Round <n>

| ID | Category | Kind | Depends on | Question | Recommended answer | Answer | Status |
|----|----------|------|------------|----------|--------------------|--------|--------|
| Q1 | goal | decision | — | <one idea, no compound questions> | <the agent's pick, worded so "yes" accepts it> | <verbatim> | answered |
| Q2 | users | fact | — | <fact the agent looked up> | — | <finding> (source: <where>) | answered |

Category: goal · users · constraints · success · failure_modes · reversibility ·
sequencing · ownership · unknowns
Kind: decision (the user's call) · fact (look it up; ask only if it cannot be found)
Status: open · asked · answered · deferred · assumed

## Decisions so far

One line per settled decision, in the order they were made:

- Q1 — <gist of the answer>

## Assumptions (stated, not silent)

| ID | Assumption | Fact or decision | Confirmed by | Source / how to verify |
|----|------------|------------------|--------------|------------------------|

## Deferred

| ID | Question | Owner | Reason | Revisit when |
|----|----------|-------|--------|--------------|

## Open questions (next round)

Paste the checker's "Next round" list here and draft each question with a
recommended answer before asking.

## Exit check

- [ ] Frontier empty: no open or asked questions remain
- [ ] Every core category has at least one settled question
- [ ] No decision sits under "assumed" without the decision-maker's confirmation
- [ ] Every deferral has an owner and a reason
- [ ] The decision-maker read the "Decisions so far" list back and agreed it is the plan
