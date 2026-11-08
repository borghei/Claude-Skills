# Writing Agent Briefs

An agent brief is the specification posted on an issue or pull request when
it moves to `ready-for-agent` or `ready-for-human`. Whoever picks the item up
— a coding agent running unattended, or a person next month — works from the
brief, not from the original report and the forty comments under it. The
report is evidence; the brief is the contract.

A good brief has one property above all others: **someone with no access to
the conversation could finish the work and know they were done.** Every rule
below serves that property.

## The six principles

### 1. Self-contained

Assume the reader has the repository and the brief, nothing else. No "as
discussed above", no "per the thread", no reliance on a screenshot three
comments up. If a fact from the thread matters, restate it in the brief.

### 2. Durable: behaviour and contracts, not locations

Items can sit in `ready-for-agent` for weeks. Files are renamed, functions
move, line numbers drift on every commit. A brief that says "edit line 88 of
the CSV writer" is wrong by the time it is read.

| Durable (do) | Perishable (avoid) |
|---|---|
| "The `ExportJob` type gains an optional `delimiter` field" | "Add a field in src/export/job.ts" |
| "`RetryPolicy.next_delay()` is unchanged" | "Don't touch lines 40-60" |
| "The `--json` flag on the list command" | "The function around line 150" |
| "The rate-limit middleware's rejection response" | "middleware/rate.go:212" |

Names of types, functions, CLI flags, config keys, API fields and events are
durable enough: they are part of the contract and the agent can search for
them. File paths and line numbers are not.

### 3. Behavioural, not procedural

Say *what* must be true afterwards, not *how* to make it true. The agent will
read the current code and make its own implementation choices; a brief that
dictates steps either fights the code it finds or gets followed blindly into
a worse design.

- Behavioural: "Each failed delivery attempt schedules exactly one retry."
- Procedural: "Open the dispatcher, go to the timeout handler, then add a
  check before calling schedule."

The exception: when a prototype or an earlier decision fixed a precise shape
(a state table, a schema, a type signature), include that shape. It encodes
a decision, not a procedure.

### 4. Testable acceptance criteria

Each criterion is one observable check that passes or fails on its own.

| Weak | Why it fails | Strong |
|---|---|---|
| "Export works correctly" | No test can decide "correctly" | "Exporting 10,000 rows produces a file with 10,001 lines (header + rows)" |
| "Errors are handled gracefully" | "Gracefully" is taste | "An unreachable endpoint yields exit code 3 and the message `endpoint unreachable`" |
| "Faster export" | Faster than what, measured how | "Exporting 100,000 rows completes in under 5 s on the CI runner" |
| "Adds JSON output and tests and updates docs" | Three checks; a partial pass is ambiguous | Split into three criteria |

Include at least one edge case or error path and one regression guard
("output without `--json` is byte-for-byte unchanged"). Regression guards are
what stop an agent from "improving" adjacent behaviour.

### 5. Explicit scope fence

The out-of-scope list is mandatory. Agents gold-plate: given a retry bug,
they will also tune the backoff, add a dead-letter queue and refactor the
dispatcher. Name the tempting adjacent changes and rule them out. An empty
out-of-scope list is a lint error, not a style choice.

### 6. Runnable verification

End with the exact command or check that proves the criteria: a test target,
a CLI invocation, an HTTP request. "Check it" is not verification. If the
project has no way to verify the change automatically, that is itself a
reason the item may belong in `ready-for-human`.

## Sections

| Section | Required | Content |
|---|---|---|
| Category | yes | bug, enhancement, chore, docs |
| Target state | yes (defaults to agent) | `ready-for-agent` or `ready-for-human` |
| Summary | yes | One line under 120 characters naming the observable change |
| Current behavior | yes | Bug: broken behaviour and its trigger. Enhancement: the status quo. PR: what the diff does and which gaps remain |
| Desired behavior | yes | End state including edge cases and error paths |
| Key interfaces | recommended | Types, functions, flags, fields whose contract changes or must not change |
| Acceptance criteria | yes | Two or more independent checks |
| Out of scope | yes | Adjacent changes the worker must not make |
| Why not delegated | ready-for-human only | The judgment, access, manual test, or contract approval that needs a person |
| Verification | yes | Exact command or check |

## Ready-for-human briefs

Use the same shape, plus the reason. Typical reasons that genuinely need a
person:

- **Contract approval.** The change creates or alters a public API, file
  format, CLI output or schema that others will depend on.
- **Judgment.** UX wording, product trade-offs, or a design choice between
  options the brief cannot settle.
- **Access.** Production data, third-party consoles, credentials, hardware.
- **Manual verification.** Behaviour only observable on a real device,
  printer, payment provider sandbox, or by eye.
- **Security sensitivity.** Authentication, authorisation, secrets handling,
  or anything a policy forbids delegating.

"It's complicated" is not a reason. Complicated but well-specified work is
exactly what a good brief makes delegable. If the honest reason is that the
problem is not understood yet, the item is not ready for anyone; move it back
to `accepted` or `needs-info`.

## Briefs for pull requests

For an external PR, the brief describes what is left to do **to the existing
diff**:

- Current behavior: what the diff already achieves, what it gets wrong, what
  is missing (tests, error paths, docs).
- Desired behavior: the end state of the PR when merged.
- Key interfaces: reuse what the PR introduced; do not let the worker build a
  second serializer next to the contributor's.
- Out of scope: other commands, unrelated cleanups, reshaping what the
  contributor already got right.

Keep the contributor's work as the base. A brief that effectively says
"rewrite this PR" should instead be a polite rejection or a fresh issue.

## Worked example: from report to brief

**Report (abridged):** "Since the update our endpoint gets every webhook
retry twice when we return 503. See logs. Please fix ASAP."

**Triage path:** `new → reproduced` (two deliveries logged per 503 in the
integration suite) `→ accepted` (`priority:p1`, duplicate side effects for
customers) `→ ready-for-agent`.

**Brief:**

```markdown
## Agent Brief

**Category:** bug
**Summary:** A webhook delivery that receives a 503 is retried twice instead of once

**Current behavior:**
When the receiving endpoint answers 503, a retry is scheduled from the failure
callback and again from the timeout watchdog, so the receiver gets two
identical retries about 30 seconds apart.

**Desired behavior:**
Each failed delivery attempt schedules exactly one retry, whichever failure
path observes the error. Retries keep the existing backoff schedule and carry
the idempotency key of the original attempt.

**Key interfaces:**
- `DeliveryAttempt` status: an attempt reaches `retry_scheduled` at most once
- `RetryPolicy.next_delay(attempt_number)` is unchanged

**Acceptance criteria:**
- [ ] A 503 response produces exactly one scheduled retry for that attempt
- [ ] A timeout followed by a late 503 for the same attempt produces exactly one scheduled retry
- [ ] Every retry carries the idempotency key of the original delivery
- [ ] The backoff delays (10s, 30s, 90s) are unchanged

**Out of scope:**
- Changing the retry schedule or the maximum attempt count
- Dead-letter queue behaviour after the final attempt

**Verification:** `make test-integration TEST=webhook_retry`
```

Notice what is absent: no file names, no "ASAP", no speculation about the
cause beyond what reproduction established, no instruction about where to put
the guard.

## Anatomy of a failing brief

```markdown
## Agent Brief
**Summary:** Fix the export
**Current behavior:** Export is slow.
**Desired behavior:** Open the file src/export/csv_writer.py and go to line 88, then add a buffer.
**Acceptance criteria:**
- [ ] Export works correctly and is faster
**Verification:** check it
```

What the linter reports, and why each matters:

| Finding | Why it matters |
|---|---|
| `missing-section: out of scope` | Nothing stops the agent rewriting the whole export module |
| `file-path` | The path will move; the agent may edit a stale location |
| `line-number` | Wrong after the next commit |
| `vague-criterion: works` | No test decides it; the agent will declare victory |
| `procedural` | Dictates a fix (buffering) before anyone measured the cause |
| `thin-criteria` | One criterion cannot cover the edge cases |
| `verification` | "check it" cannot be run |
| `missing-interfaces` | The agent has no contract to anchor on |

The underlying problem is that this item was never really triaged: "slow" was
never measured, so there is no baseline to write a criterion against. The
right move is `accepted → needs-info` (or a measurement task), not a better
sentence.

## Linter rule reference

| Rule | Severity | Detects |
|---|---|---|
| `missing-section` | error | Any required section absent or empty |
| `human-reason` | error | `ready-for-human` without "Why not delegated" |
| `file-path` | error | Path-like tokens with a source-file extension, or `file.ext:NN` |
| `line-number` | error | "line 88", "L88" |
| `placeholder` | error | Unfilled `<...>` template placeholders |
| `vague-criterion` | error | works, correctly, properly, as expected, gracefully, appropriate, fast/faster, better, improved, robust, seamless, user-friendly, intuitive, etc. |
| `missing-interfaces` | warn | No key interfaces named |
| `procedural` | warn | "open the file", "go to", "add a line", "then edit", "step 1" in summary or desired behaviour |
| `thin-criteria` | warn | Exactly one acceptance criterion |
| `compound-criterion` | warn | Semicolons, or long criteria joined with "and"/"also" |
| `long-summary` | warn | Summary over 120 characters |
| `verification` | warn | Verification without a backticked command or a known runner |

The linter is a floor, not a judge. A brief can pass every rule and still be
wrong about the desired behaviour; a human reads every brief before the state
changes.
