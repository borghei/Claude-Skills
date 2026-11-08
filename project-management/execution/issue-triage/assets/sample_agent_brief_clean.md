# Agent briefs ready for hand-off

Both briefs below pass the linter (exit 0). The first goes to a coding agent;
the second stays with a human and says why.

## Agent Brief

**ID:** #231
**Target state:** ready-for-agent
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

## Agent Brief

**ID:** #238
**Target state:** ready-for-human
**Category:** enhancement
**Summary:** Finish the contributor's machine-readable output flag for the list command

**Current behavior:**
The pull request adds a `--json` flag that serialises the item list. Success
output works; errors still print as plain text and the flag has no tests.

**Desired behavior:**
With `--json`, all output including errors is one well-formed JSON document on
stdout, and exit codes match the plain-text command. Without the flag, output
is byte-for-byte unchanged.

**Key interfaces:**
- Error payload under `--json`: `{"error": string}`
- The serialiser the pull request already adds is reused, not duplicated

**Acceptance criteria:**
- [ ] `list --json` emits valid JSON when the command succeeds
- [ ] `list --json` emits `{"error": ...}` when the command fails
- [ ] Exit codes with `--json` equal the exit codes without it
- [ ] Output without `--json` is byte-for-byte unchanged

**Out of scope:**
- Adding `--json` to any other command
- Changing the success payload shape the pull request defines

**Why not delegated:** The JSON shape becomes a public contract that downstream scripts will parse; a maintainer has to approve it.

**Verification:** `make test TEST=cli_list`
