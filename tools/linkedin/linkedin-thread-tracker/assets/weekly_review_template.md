# Weekly Thread Review

Fill in once a week, after updating the log and running the full report.

- **Week ending:** <date>
- **Log file:** <path>
- **Report run as of:** <ISO timestamp passed to `--as-of`>
- **Log confirmed current before running?** <yes | no — what might be missing>

## 1. State counts

Copy from the report's second line.

| overdue | your-turn | lapsed | watching | awaiting | quiet | settled | dead | closed |
|---------|-----------|--------|----------|----------|-------|---------|------|--------|
| <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> |

## 2. Actions taken this week

| Thread | Author | State at review | What I did | Recorded in log? |
|--------|--------|-----------------|------------|------------------|
| <T-000> | <name> | <overdue> | <answered \| messaged \| closed> | <yes> |
| <T-000> | <name> | <…> | <…> | <…> |

## 3. Lapsed threads — each one decided

| Thread | Author | Who replied | What they asked | Decision | Reason |
|--------|--------|-------------|-----------------|----------|--------|
| <T-000> | <name> | <author \| other> | <…> | <message \| late reply \| close> | <…> |

## 4. Closed this week

| Thread | Author | Reason for closing | Comment on this author again? |
|--------|--------|--------------------|-------------------------------|
| <T-000> | <name> | <…> | <yes \| no \| for the readers only> |

## 5. Metrics

| Metric | This week's report | Previous review | Note |
|--------|--------------------|-----------------|------|
| Comments logged in window | <n> | <n> | Under ~20, treat rates as anecdotes |
| Author reply rate | <%> | <%> | <…> |
| Priority-tier author reply rate | <%> | <%> | The one that matters |
| Any-reply rate | <%> | <%> | <…> |
| Median hours to author's first reply | <h> | <h> | Compare with `--watch-days` |
| Replies I never answered | <n> | <n> | Target: 0 |

## 6. What the numbers and the threads suggest

- **Authors who answered and are worth returning to:** <names>
- **Authors who never engage:** <names — comment for the readers, or stop>
- **Comments that drew a question, and what they had in common:** <…>
- **Comments that drew nothing, and what they had in common:** <…>
- **Replies I missed, and why I missed them:** <…>

## 7. Changes for next week

- [ ] Priority tier: add <names>, remove <names>
- [ ] Thresholds: <e.g. `--reply-due-hours 48` because I check every other day>
- [ ] Routine: <e.g. update the log straight after the morning notification check>
- [ ] Log hygiene: <archive closed threads older than … >

## 8. Checklist

- [ ] Log updated with everything seen before the report was run
- [ ] `thread_log.py validate` passes
- [ ] Every thread under "Close now" closed with a reason
- [ ] Every lapsed thread has a decision
- [ ] No second comment added to a silent thread
- [ ] No message sent to anyone who had not replied publicly
