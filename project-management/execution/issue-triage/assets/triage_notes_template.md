# Triage Notes Templates

Three comment shapes cover almost every triage outcome. Each one records what
is already settled so the next session (or the next maintainer) never re-asks.

## 1. Needs-info notes (state:needs-info)

```markdown
## Triage notes

**Established so far:**
- <fact confirmed from the report, logs, or our own check>
- <what we tried and what happened, e.g. "could not reproduce on 4.2.1 with default config">

**What we need from you:**
1. <one specific question the reporter can answer in a sentence or a paste>
2. <a second question only if it changes the decision>

**What happens next:** once you reply, this goes back into the triage queue.
If there is no reply by <date = nudge window + close window>, it will be closed
as stale; replying reopens it.
```

Questions must be answerable without guessing what we mean. "Please provide
more information" is never acceptable; "Which version does `app --version`
print, and does the crash happen with an empty project?" is.

## 2. Duplicate closure (state:duplicate)

```markdown
Closing as a duplicate of <#canonical>, which tracks the same root cause:
<one sentence naming the shared symptom or concept>. Anything new in this
report (<the extra detail, if any>) has been copied there. Follow
<#canonical> for progress.
```

## 3. Out-of-scope closure (state:out-of-scope)

```markdown
Thanks for the detailed request. This falls outside what the project will
take on: <one-sentence durable reason>. The full reasoning lives in the
out-of-scope register under `<concept-name>`, and this issue has been added
to its prior requests so the decision stays findable.
```

## 4. Already-implemented closure (state:already-implemented)

```markdown
Good news: this already exists. <Where it lives and how to reach it, in user
terms, e.g. "Reports > Export > CSV" or "`app export --csv`">. If it does not
cover your case, reply with what is missing and we will re-triage.
```

Do not add already-implemented items to the out-of-scope register; that
register is only for rejected requests, and mixing the two poisons future
prior-rejection checks.
