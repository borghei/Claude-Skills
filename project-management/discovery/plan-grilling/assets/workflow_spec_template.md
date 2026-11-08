# Workflow Spec — <name>

**Status:** draft | implementable
**Grilling sessions:** <n> (log: <link to question log>)
**Owner:** <person who runs or answers for this workflow>

## Summary

<Two sentences: what recurs, and what each run leaves behind.>

## Trigger

- **Type:** event | schedule | manual
- **Detail:** <the exact event, or the cadence with time and timezone>
- **Not triggered when:** <the cases that look like triggers but are not>

## Inputs

| Name | Source | Shape / example |
|------|--------|-----------------|

## Steps

| ID | Actor (agent / human / script) | Action | Uses |
|----|--------------------------------|--------|------|

## Human checkpoints

Put each checkpoint as late as it can go, so the person is asked once and
handed everything they need.

| After step | Decision asked | Brief presented (not raw output) | Default if no answer by |
|------------|----------------|----------------------------------|-------------------------|

Or: **Autonomous** — no checkpoint, because <reason the risk is acceptable>.

## Outputs

| Output | Destination | Who reads it |
|--------|-------------|--------------|

## Failure handling

<What happens when a step fails, when an input is missing, and who hears about it.>

## Done definition

Each line must be checkable by someone who was not in the grilling.

- <Every … / No … / … within N minutes>

## Vocabulary

| Term | Meaning in this workflow |
|------|--------------------------|

## Open questions

Must be empty before the status changes to implementable.
