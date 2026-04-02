---
description: RICE-score features or tasks for prioritization.
---

Apply RICE prioritization framework:

1. **Gather items** — ask the user for the list of features, tasks, or ideas to prioritize.
2. **Score each item** on four dimensions:
   - **Reach**: How many users/customers will this impact per quarter? (number)
   - **Impact**: How much will it move the needle per user? (3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal)
   - **Confidence**: How sure are we about these estimates? (100%=high, 80%=medium, 50%=low)
   - **Effort**: How many person-months to implement? (number)
3. **Calculate RICE score**: (Reach x Impact x Confidence) / Effort
4. **Rank by score** — highest RICE score = highest priority.
5. **Output a prioritized table:**
   | Rank | Item | Reach | Impact | Confidence | Effort | RICE Score |
6. **Highlight:**
   - **Quick wins**: high score, low effort (< 0.5 person-months)
   - **Big bets**: high reach and impact, but high effort
   - **Deprioritize**: low score items to explicitly defer
7. **Recommend** the top 3 items to tackle first with justification.
