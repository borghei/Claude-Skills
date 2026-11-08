# Session Retro — <session or task name>

**Session:** <transcript path or session id>  ·  **Date:** <YYYY-MM-DD>  ·  **Reviewer:** <name>
**Task the session was given:** <one sentence>
**Outcome:** <shipped / partly shipped / abandoned> in <N> tool calls, <M> failed

## Analyzer summary

<Paste the text output of session_log_analyzer.py here. Delete detectors that fired on
legitimate work and say why in one line.>

## What cost the most

List the three moments that burned the most calls or time, with call numbers. One line each:
what the agent was trying to do, what it did instead, and what it lacked.

1. <calls #a-#b: ...>
2. <calls #c-#d: ...>
3. <calls #e-#f: ...>

## Action items (ranked, high first)

| rank | category | change | file | evidence | severity |
|------|----------|--------|------|----------|----------|
| 1 | missing-check | <imperative change> | <path/to/file> | <calls #n-#m: what happened> | high |
| 2 | navigation | <imperative change> | <path/to/file> | <calls #n: what happened> | medium |

Categories: navigation, missing-check, standards, steering-file, tool-economy,
permission-friction, skill-miss, information-access.

## Parked

Items that are real but not worth a change yet, each with the trigger that would promote it
(for example "promote if it recurs in a second session").

- <item> — promote when <trigger>

## Verification

How the next session proves each shipped item worked (re-run the same task, or watch for the
same call pattern in the next transcript).

- Item 1: <check>
