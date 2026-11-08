# Out-of-Scope Register Entry Template

One entry per **concept**, not per issue. File name or key: a short
kebab-case concept name a newcomer would recognise (`per-user-themes`,
`plugin-runtime`, `graphql-api`). When a new request matches the concept,
append it to **Prior requests** instead of creating a second entry.

In JSON (what `triage_state_validator.py` reads under `out_of_scope_register`):

```json
{
  "concept": "per-user-themes",
  "decision": "rejected",
  "reason": "<durable reason: scope, architecture, or strategy, not 'busy right now'>",
  "revisit_if": "<the condition that would reopen the question>",
  "prior_requests": ["#212", "#239"]
}
```

As a markdown record:

```markdown
# <Concept name>

**Decision:** rejected — <one sentence stating what the project will not do>
**Decided:** <YYYY-MM-DD> by <role>

## Why
<Two or three short paragraphs. Name the constraint (scope, architecture,
cost, strategy) and the trade-off. A newcomer should understand it without
reading the original threads.>

## What we suggest instead
<Workaround, extension point, or downstream option, if one exists.>

## Revisit if
<The concrete change that would make this worth reopening, e.g. "runtime
rendering replaces build-time palette resolution".>

## Prior requests
- <#id> — "<title as the reporter phrased it>"
```

Checks before saving:

- The reason survives a change of team or quarter. "No capacity this
  quarter" is a deferral, not a rejection: keep the issue open and
  unprioritised instead.
- Bugs do not go here. A bug you will not fix is closed with an explanation.
- Already-implemented requests do not go here.
