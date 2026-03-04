# Prioritization Frameworks Guide

Detailed reference for each framework with formulas, when to use, common mistakes, and facilitation tips.

---

## Framework Formulas

### Opportunity Score

```
Score = Importance x (1 - Satisfaction)
```

- **Importance** (0-10): Survey customers. Ask: "How important is [problem/need] to you?"
- **Satisfaction** (0-1): Survey customers. Ask: "How satisfied are you with current solutions for [problem/need]?"

**Interpretation:** A score above 6 represents a strong opportunity. The highest-scoring problems are both very important and poorly served by current solutions.

### ICE

```
Score = Impact x Confidence x Ease
```

All on a 1-10 scale:
- **Impact**: Expected effect on the target metric
- **Confidence**: How certain you are about the impact estimate
- **Ease**: How easy to implement (10 = trivial, 1 = very hard)

**Score range:** 1 to 1,000. Items scoring 500+ are strong candidates.

### RICE

```
Score = (Reach x Impact x Confidence) / Effort
```

- **Reach**: Number of users/customers affected per quarter (raw number, e.g., 5000)
- **Impact**: Degree of effect per user (3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal)
- **Confidence**: Certainty as percentage (100% = high data, 80% = some data, 50% = gut feel)
- **Effort**: Person-months of work (e.g., 3 = three person-months)

**Note:** Confidence as a percentage naturally discounts items where you are guessing. A high-impact item with 50% confidence scores half of a high-impact item with 100% confidence.

### Weighted Decision Matrix

```
Score = Sum(criterion_score_i x criterion_weight_i) for all criteria
```

Weights must sum to 1.0 (or 100%).

### MoSCoW

No formula. Categorization only. Rule: Must-Haves should be no more than 60% of total effort.

---

## When to Use Each Framework

| Situation | Recommended Framework | Why |
|-----------|----------------------|-----|
| Ranking customer problems | Opportunity Score | Directly measures problem-solution gap |
| Quick triage of small list | ICE | Fast, low overhead, good enough for short lists |
| Rigorous ranking of large backlog | RICE | Reach dimension matters at scale |
| Personal PM task management | Eisenhower Matrix | Urgent/Important is the right lens for tasks |
| Quick visual group exercise | Impact vs Effort | Physical, collaborative, intuitive |
| High-uncertainty initiatives | Risk vs Reward | Accounts for downside, not just upside |
| Understanding expectations | Kano Model | Classifies needs by type, not priority |
| Multi-stakeholder decisions | Weighted Decision Matrix | Transparent, auditable, builds consensus |
| Scoping a release | MoSCoW | Clear categories for requirement negotiation |

---

## Common Mistakes Per Framework

### Opportunity Score

- **Mistake:** Using internal estimates instead of customer data for importance and satisfaction.
- **Fix:** Survey at least 15-20 customers per segment. Internal estimates are biased toward what the team wants to build.

- **Mistake:** Using demographics to define the segment being surveyed.
- **Fix:** Define segments by the problem they face, then survey that group.

### ICE

- **Mistake:** Scoring in isolation. One person assigns all scores without discussion.
- **Fix:** Have 3-5 people score independently, then discuss discrepancies. The discussion reveals hidden assumptions.

- **Mistake:** All items score 7-8-9 on every dimension (no differentiation).
- **Fix:** Force-rank first, then score. Or use a wider scale to create separation.

### RICE

- **Mistake:** Inflating reach estimates to game the system.
- **Fix:** Define reach precisely: "How many users will encounter this feature in Q2?" Use data, not hopes.

- **Mistake:** Giving everything 100% confidence.
- **Fix:** Reserve 100% for items with strong data. Use 80% for informed estimates, 50% for guesses.

### MoSCoW

- **Mistake:** Everything is "Must Have."
- **Fix:** The test: "If we ship without this, does the product have zero value?" If no, it is not a Must Have.

- **Mistake:** "Won't Have" treated as "never" instead of "not this time."
- **Fix:** Relabel to "Won't Have This Time" to make deferral explicit and non-permanent.

### Weighted Decision Matrix

- **Mistake:** Choosing criteria after seeing the options (biasing toward a preferred choice).
- **Fix:** Define and weight criteria before anyone scores any options.

- **Mistake:** Too many criteria (10+). Dilutes each criterion's influence.
- **Fix:** Maximum 5-6 criteria. If more seem needed, combine related ones.

---

## Combining Frameworks

Frameworks are not mutually exclusive. A common combination:

1. **Opportunity Score** to rank problems worth solving.
2. **RICE** to rank solution ideas for the top problems.
3. **MoSCoW** to scope the first release of the winning solution.

Another combination for team prioritization:

1. **Impact vs Effort** for a quick visual sort in a group setting.
2. **ICE** to add rigor to the top quadrant items.
3. **Eisenhower** for the PM's personal task list afterward.

---

## Facilitating Prioritization Sessions

### Before the Session

1. **Define the decision**: What exactly are we prioritizing? (Features? Problems? Initiatives?)
2. **Choose the framework**: Match to the situation using the decision tree.
3. **Prepare the data**: List all items. Include brief descriptions. Remove duplicates.
4. **Pre-score (optional)**: Have participants score independently before the session. Discuss discrepancies during the session.

### During the Session

1. **Align on criteria** (5 min): Confirm what the scores mean. What is a 9 vs a 7 for impact?
2. **Score independently** (10 min): Each participant scores in silence. No groupthink.
3. **Reveal and discuss** (20 min): Show scores. Focus on items with high variance between scorers. That is where hidden assumptions live.
4. **Converge** (10 min): Agree on final scores. Use the median, not the average (less susceptible to outliers).
5. **Rank and decide** (5 min): Sort by score. Confirm the top 3-5 items feel right. If the ranking feels wrong, you missed a criterion.

### After the Session

1. Document the scores and the rationale.
2. Share with stakeholders who were not in the room.
3. Revisit in 4-6 weeks to see if priorities changed based on new data.

### Facilitation Tips

- **Time-box**: 60 minutes maximum. Prioritization sessions that run long produce worse decisions, not better ones.
- **Separate scoring from debating**: Score first, discuss second. If people discuss first, anchoring bias takes over.
- **Use a parking lot**: Items that spark long debates go on a parking lot list. Score them last, after simpler items calibrate the group.
- **The gut check**: After scoring, ask: "Does this ranking feel right?" If the top item feels wrong, explore why. Sometimes intuition catches what frameworks miss.

---

## Framework Comparison Table

| Framework | Speed | Rigor | Best For | Worst For |
|-----------|-------|-------|----------|-----------|
| Opportunity Score | Medium | High | Customer problems | Internal initiatives |
| ICE | Fast | Low | Quick triage | Large backlogs |
| RICE | Medium | High | Feature prioritization | Early-stage ideation |
| Eisenhower | Fast | Low | Personal tasks | Product decisions |
| Impact vs Effort | Fast | Low | Group visual triage | Detailed ranking |
| Risk vs Reward | Medium | Medium | Uncertain bets | Well-understood items |
| Kano | Slow | High | Understanding needs | Ranking priorities |
| Weighted Matrix | Slow | High | Multi-stakeholder | Quick decisions |
| MoSCoW | Fast | Medium | Release scoping | Strategic planning |
