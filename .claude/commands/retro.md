---
description: Run a sprint retrospective with data-driven insights from git history.
---

Facilitate a sprint retrospective:

1. **Gather data** from the sprint period:
   - `git log --since="2 weeks ago"` for commit activity
   - Count commits per author, per day
   - Identify large PRs (> 500 lines changed)
   - Find reverted commits or fix-after-fix patterns
   - Check for weekend/late-night commits (burnout signal)
2. **What went well:**
   - Features shipped on time
   - Clean PRs (small, focused, well-reviewed)
   - Fast cycle times (commit to merge)
   - Good test coverage on new code
3. **What didn't go well:**
   - Blocked items and their root causes
   - Scope creep indicators (PRs that grew significantly)
   - Incidents or hotfixes during the sprint
   - Commits with "fix fix" or "wip" messages (rushed work)
4. **Metrics:**
   - Velocity: story points or tasks completed
   - Cycle time: average PR open-to-merge duration
   - Bug rate: fixes as % of total commits
5. **Action items:**
   - Generate 3-5 specific, assignable improvements
   - Each item: what to change, who owns it, how to measure success
   - Prioritize by impact on team velocity
6. Output as a structured retro document ready to share with the team.
