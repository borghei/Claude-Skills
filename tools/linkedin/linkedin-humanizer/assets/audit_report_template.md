# Draft Audit: {post working title}

- **Author:** {name}
- **Auditor:** {name}
- **Date:** {YYYY-MM-DD}
- **Draft file:** {path}
- **Mode:** {audit only / audit and proposed rewrite}
- **Voice file used:** {path, or "none: no past posts available"}

## Assumptions

List anything that was assumed rather than confirmed. If the author said "just
clean it up", every assumption goes here.

- {assumption}

## Verdict

| Check | Result | Detail |
|-------|--------|--------|
| Tell audit gate | {PASS / FAIL} | blockers {n}, habit load {n} of {limit} |
| Emoji pattern | {PASS / FAIL} | score {n} of 100 |
| Voice comparison | {PASS / FAIL / not run} | {n} measures outside range |

**One-sentence summary:** {what is wrong with the draft, in plain words, or
"nothing that needs changing"}

## Must fix before publishing (remove tier)

| Rule | Text | Fix |
|------|------|-----|
| {RM-xx} | "{quoted text}" | {delete / fill with …} |

## Recommended changes (reduce tier)

Ordered by load. For each, the original, the proposed text, and the reason.

### {RD-xx} {rule name}

- **Original:** "{text}"
- **Proposed:** "{text}"
- **Why:** {one line; from `tell_rules.py --explain`}
- **Keep the original if:** {the catalogue's keep-when condition}

## Facts needed from the author

Nothing below has been invented or estimated. The draft cannot be finished
without these.

| Needed | Question | Answer |
|--------|----------|--------|
| {a figure} | {what was the number before and after, and over what period?} | {…} |
| {a name} | {who did this work, and can they be named?} | {…} |

## Left alone on purpose

Findings that were considered and not acted on.

| Rule | Text | Reason for leaving it |
|------|------|-----------------------|
| {RV-xx / RD-xx} | "{text}" | {author habit per fingerprint / under allowance / literal use} |

## Over-edit check (rewrites only)

- [ ] No new fragments
- [ ] No dash replaced by a full stop
- [ ] No added candor, hesitation or confession
- [ ] No figure, name or date that the author did not supply
- [ ] Contractions and at least one long sentence still present
- [ ] Claim strength unchanged
- [ ] Drift against the fingerprint is no worse than the original

## Proposed final text

```
{the full post, exactly as it should be pasted}
```

Character count: {n}. Re-run both gates on this text before handing it back.
