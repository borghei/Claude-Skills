# Interview Synthesis Methodology Guide

This guide bundles three complementary methodologies into a single end-to-end synthesis playbook: Teresa Torres' Opportunity Solution Tree, Steve Portigal's interview-listening discipline, and Alan Klement's Jobs-To-Be-Done synthesis.

---

## 1. Why a structured synthesis matters

Raw interview notes have a half-life of about a week. Without a structured synthesis pass, teams remember the loudest quote rather than the strongest evidence, and they jump straight to solutions before mapping the opportunity space.

The synthesis discipline answers four questions:

1. **What did we actually hear?** (Snippets)
2. **What patterns repeat?** (Themes)
3. **What opportunities does this open?** (Opportunity tree)
4. **What evidence is still missing?** (Follow-ups)

A team that answers these four questions before any backlog work happens reduces feature-build-and-toss waste dramatically.

---

## 2. Snippet extraction (Portigal)

Steve Portigal, in *Interviewing Users*, argues that the interviewer's job is to listen for four signal types:

### Stories

A story has a time anchor ("Last Wednesday"), a specific context, an action sequence, and an outcome. Stories carry the highest evidence weight because the participant is reconstructing real behavior rather than imagining a future.

> Good story snippet: "Last Wednesday I was closing the month. I pulled the bank feed at 4pm, but two transactions were duplicates from the prior period, so I had to manually re-key the entire ledger. I left at 9pm and still was not sure the numbers were right."

### Contradictions

Contradictions appear when a participant claims one thing but their stories show another. They are the richest source of latent needs.

> Contradiction: "I said earlier that I trust the automation, but then I described checking every entry manually for the first three weeks. That's not trust -- that's verification."

### Surprises

Anything that violates the interviewer's mental model. Surprises are honesty signals: the participant said something the team did not script.

### Emotions

Frustration, delight, fear, and relief mark motivational intensity. Pay attention to the moments where the participant's tone changes.

### What to drop

Drop hypothetical-future statements ("I would use X if..."). They are low evidence. Drop solution suggestions ("You should add..."). Those belong in a separate ideation backlog, not the synthesis.

---

## 3. Coding (Klement-flavored JTBD)

Alan Klement, in *When Coffee and Kale Compete*, proposes that every meaningful customer behavior can be decomposed into:

- **Situation** -- The context that triggers the job
- **Motivation** -- The change the customer wants to make
- **Outcome** -- The improved state they expect

The coding pass tags each snippet with:

| Code Type | Question Answered | Example |
|-----------|-------------------|---------|
| Need | What underlying need does this point to? | "trust-in-automated-data" |
| Job | What job-to-be-done is invoked? | "When closing the month, I want to verify automated matches, so I can sign off without re-keying" |
| Pain | What friction or workaround appears? | "manual-reconciliation-of-duplicates" |
| Gain | What positive outcome would matter? | "audit-trail-per-rule" |
| Strength | How well-evidenced is this snippet? | 1 (single mention) / 2 (multi-participant) / 3 (multi-participant + behavioral) |

Coding is best done by 2 people independently, then reconciled. Single-coder synthesis is faster but biased.

---

## 4. Theme clustering

A theme is a coherent group of coded snippets. The discipline:

- **Threshold:** >=3 snippets, from >=2 participants
- **Headline:** 1 sentence that a stakeholder can read in 5 seconds
- **Evidence trail:** Each theme links back to its source snippets

### Worked example

Snippets coded with `pain = manual-reconciliation` and `need = trust-in-data`:

1. "I re-key every duplicate manually." (P1)
2. "I do not trust the matches until I check them." (P3)
3. "The automation flags conflicts but does not explain why." (P3)
4. "I export to Excel and rebuild." (P5)

**Theme headline:** *Finance leads do not trust automated matches because they cannot inspect the rule that produced each match.*

This headline is actionable: it points at an opportunity (visible rule trace) without prescribing a solution.

---

## 5. Opportunity Solution Tree (Torres)

Teresa Torres' tree has four mandatory layers:

```
Outcome
  |
  +-- Opportunity (customer need)
        +-- Solution (candidate)
              +-- Experiment (validation)
```

### Outcome rules

- One outcome per tree (you can build multiple trees for multiple outcomes)
- The outcome is **measurable**: "Reduce time to first import from 14 days to 3 days"
- Not a feature: "Add onboarding wizard" is wrong; "Reduce time to first import" is right

### Opportunity rules

- Customer-side framing only
- Traces to >=1 themed insight (no opportunities invented from thin air)
- Mutually exclusive when possible (overlapping opportunities suggest the outcome is too broad)
- 3-7 opportunities per outcome (more = re-scope; fewer = under-explored)

### Solution rules

- Multiple solutions per opportunity (the tree exists to compare alternatives)
- Each solution will need a validation experiment before commitment
- Solutions are de-prioritized at this stage; opportunity selection comes first

### Common anti-patterns

- **Pet-feature tree** -- The team puts their favorite solution at the top and works backward. The fix: start from outcome and themes; never start from solution.
- **Theme = opportunity** -- Themes describe what is true today; opportunities describe what the customer needs. They are related but not identical.
- **One solution per opportunity** -- Defeats the purpose of the tree. Force >=2 solutions per opportunity, even if one is "do nothing".

---

## 6. Follow-up question generation

After synthesis, identify:

- **Weak-evidence themes** (strength <= 2) that the team wants to commit on
- **Unmapped assumptions** -- things the team believes but no interview snippet supports
- **Surprises** -- moments that violated the team's model and need confirmation

For each, write 2-3 follow-up questions for the next interview round.

### Good follow-up patterns

- **Story-prompt:** "Tell me about the last time you [behavior]."
- **Contradiction-probe:** "Earlier you said X, but you also described Y. Can you walk me through that?"
- **Counterfactual:** "If [current workaround] disappeared tomorrow, what would you do?"
- **Day-in-the-life:** "Walk me through your morning yesterday from start to finish."

### Anti-patterns to avoid

- "Would you use this?" (leading, opinion-based)
- "Do you like X?" (closed, low signal)
- "How important is X on a scale of 1-10?" (false precision)

---

## 7. Synthesis ceremony (4-hour workshop)

A repeatable synthesis ceremony with the product trio (PM, Design, Engineering):

| Time | Activity | Output |
|------|----------|--------|
| 0:00-0:30 | Walk-through of interview tags and audio clips | Shared context |
| 0:30-1:30 | Independent snippet extraction (each person, every interview) | Snippet wall |
| 1:30-2:00 | Reconcile coding (resolve disagreements) | Coded snippet wall |
| 2:00-2:45 | Theme clustering (affinity diagram) | Themed clusters |
| 2:45-3:30 | Build opportunity solution tree | Draft tree |
| 3:30-4:00 | Generate follow-ups + next-step decisions | Action items |

Run this every 2 weeks during continuous discovery. The cadence keeps insights fresh and the tree alive.

---

## 8. Output and handoff

The synthesis produces three artifacts that flow into downstream PM skills:

| Artifact | Consumed by |
|----------|-------------|
| Themed insights | `create-prd/` (Background, Market Segments sections) |
| Opportunity solution tree | `outcome-roadmap/`, `prioritization-frameworks/` |
| Job-codes (Klement format) | `job-stories/` (When/Want/So format) |
| Follow-up questions | Next discovery round, `identify-assumptions/` |

---

## References

- Torres, T. (2021). *Continuous Discovery Habits*. Product Talk LLC.
- Portigal, S. (2013, 2nd ed. 2023). *Interviewing Users*. Rosenfeld Media.
- Klement, A. (2018). *When Coffee and Kale Compete*. NYC Publishing.
