---
name: bug-diagnosis
description: >
  Find the root cause of hard bugs with a fast pass/fail repro, ranked falsifiable
  hypotheses and bisection. Use when a bug resists quick fixes, a failure is
  intermittent, or a regression needs tracing to its cause.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: debugging
  updated: 2026-11-08
  tags: [debugging, root-cause, bisection, reproduction, hypotheses, redaction, regression-test]
---

# Bug Diagnosis

A disciplined loop for bugs that survived the first obvious fix. The order is
fixed: build a signal that says "bug present / bug absent" in seconds, write down
competing explanations with predictions that could prove them wrong, test the
cheapest likely one, narrow the search space by halving, and lock the cause in
with a regression test that was seen failing. Most wasted debugging time comes
from skipping the first step and reading code to build a theory with nothing to
check it against.

## When to use this skill

- **A bug resisted a first fix** — the patch went in and the symptom came back, or moved
- **The failure is intermittent** — passes locally, fails in CI one run in five
- **A regression appeared between two releases** and nobody knows which change caused it
- **The symptom is far from the cause** — wrong totals, corrupted records, a hang with no error
- **A performance regression** needs a measured cause rather than a guess
- **Logs or traces need sharing** with a teammate, vendor or assistant and may contain credentials

## Inputs the skill expects

- The reported symptom in exact terms: error text, wrong value, measured latency
- Where it reproduces (local, CI, staging, production only) and how often
- The last known-good state if one exists: a release, a commit, a dataset, a flag set
- Access the agent has: can it run the code, the tests, a local database, `git bisect`?
- Any artefacts already captured (logs, dumps, traces) — redacted before they are pasted

## Clarify First

What most shapes a diagnosis is whether a reproduction signal can be built and how far the cause might hide. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The exact symptom:** a signal must assert this specific symptom; "it's broken" yields a check that goes red on the wrong bug.
- **Where it reproduces:** decides the harness — a local test, a recorded request replay, or a request for environment access.
- **Last known-good state:** if one exists, bisection usually beats hypothesis testing and should come first.
- **Blast-radius limits:** whether the agent may touch shared environments, production data or code outside the failing module.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Validate a diagnosis log and see which hypothesis to test next
python3 engineering/bug-diagnosis/scripts/hypothesis_log.py \
  --input engineering/bug-diagnosis/assets/sample_diagnosis_log_passing.json

# Check a log file for secrets before pasting it anywhere
python3 engineering/bug-diagnosis/scripts/redact_scan.py \
  --paths engineering/bug-diagnosis/assets/sample_debug_log.txt --pii
```

## Workflows

### Workflow 1 — Build the reproduction signal [PROVEN]

No signal, no hypotheses. The agent spends disproportionate effort here because every later step consumes this one command.

1. Pick the harness from the bug class: failing test at the narrowest seam, replayed request, fixture-driven CLI run, timing harness for performance, or a differential run between versions (see `references/reproduction-signals.md`).
2. Start from `assets/repro-script-template.sh` so the signal exits 0 for good, 1 for bad and 125 for untestable — directly usable by `git bisect run`.
3. Make it assert the reported symptom. A check for "no exception" is not a signal.
4. Pin clock, random seeds, locale, network and worker count. Run it 3+ times; record runs, red runs and runtime.
5. If the failure is intermittent, raise its rate (loop in-process, parallel copies, smaller timeouts, injected delay) until at least 30% of runs go red.
6. Minimise: remove inputs, records, steps and config one at a time, keeping only what keeps the signal red.

Validation checkpoint: the signal is one command, asserts the symptom, red on 3+ runs (or ≥30% for intermittent bugs), and runs in under 30 seconds. If it cannot be built within the timebox, stop and ask for access, a redacted artefact, or permission for tagged instrumentation.

### Workflow 2 — Hypothesise, rank, test one at a time [PROVEN]

1. Write 3–5 hypotheses before testing any, each naming a mechanism and a prediction in the form "if X is the cause, then changing Y makes the symptom disappear".
2. Give each a prior (0–1) and an experiment cost in minutes. Record them in a diagnosis log JSON (shape: `assets/sample_diagnosis_log_passing.json`).
3. Show the ranked list to the reporter before testing; their context often re-ranks it.
4. Run the validator. It ranks open hypotheses by prior ÷ cost and rejects vague predictions, multi-variable experiments and confirmations with no evidence.
5. Run the top experiment, record the result and evidence, re-run the validator, repeat.

```bash
python3 engineering/bug-diagnosis/scripts/hypothesis_log.py \
  --input engineering/bug-diagnosis/assets/sample_diagnosis_log.json --format text
```

The sample is deliberately flawed (2 runs, no symptom assertion, a vague confirmed hypothesis, a two-variable experiment) and exits 1.

### Workflow 3 — Bisect when a good state exists [PROVEN]

1. Confirm the endpoints by hand: the signal is green on the good state and red on the bad one.
2. Commits: `git bisect start; git bisect bad; git bisect good <tag>; git bisect run ./repro.sh`. Save `git bisect log`.
3. Inputs: halve the failing input, keep the half that fails, repeat; if neither half fails alone, test combinations of quarters.
4. Config or dependencies: write the difference list between good and bad environments first, then apply half at a time.
5. Read the first bad state as "where the bug became visible", then form hypotheses about that diff.

### Workflow 4 — Instrument and redact [RECOMMENDED]

1. Prefer a debugger breakpoint where hypotheses diverge; otherwise add log lines that print values at that boundary.
2. Tag every temporary line with a unique marker (`[DBG-7c1e]`) and record the tag in the log.
3. Never log whole request objects, headers or environment dumps.
4. Before sharing any output, scan it, write a redacted copy, read the copy by eye, and paste only the lines that carry the signal.

```bash
python3 engineering/bug-diagnosis/scripts/redact_scan.py \
  --paths engineering/bug-diagnosis/assets/sample_debug_log.txt --pii --format json
```

`--write-redacted` writes `<name>.redacted<ext>` beside each input, replacing each secret with a typed placeholder such as `<REDACTED:jwt>`. Findings print a four-character masked preview, never the value.

### Workflow 5 — Fix, regression test, clean up [PROVEN]

1. Turn the minimised reproduction into a test at a seam where the real failure pattern occurs.
2. Watch it fail with the reported symptom before changing code.
3. Apply the smallest fix that addresses the confirmed cause; run the test, then the original unminimised signal.
4. `grep -rn "<debug tag>" .` must return nothing; delete throwaway harnesses.
5. Put the confirmed hypothesis and its evidence in the commit message. Set `status: fixed` in the log and re-run the validator — it fails if the test was never seen failing or the tag was not removed.

If no seam reaches the failure pattern, record `regression_test.no_seam_reason`; that is a design finding to raise, not a reason to skip silently.

## Decision frameworks

### Bisect or hypothesise first?

| Situation | Start with | Why |
|-----------|-----------|-----|
| Known-good commit or release exists, signal < 2 min | `git bisect run` | ~10 runs cover 1,000 commits unattended |
| Large failing input, small inputs pass | Input bisection | Shrinks to the triggering record before theorising |
| Works in one environment, fails in another | Config / dependency bisection over a written diff list | The cause is in the difference set by definition |
| No good state, symptom in a known module | Hypotheses | Nothing to bisect between |
| Performance regression | Baseline measurement, then bisect | A number with a threshold is the only valid signal |

### Stop rules [RECOMMENDED]

| Trigger | Action |
|---------|--------|
| No signal after a 90-minute timebox | Stop; report what was tried and what access or artefact is needed |
| 4 inconclusive experiments in a row (validator enforces) | Re-check the signal's specificity; rewrite the hypothesis list |
| All hypotheses refuted | The mental model is wrong; re-read the minimised repro, ask the code owner |
| Fix requires changes outside the agreed blast radius | Stop and report cause plus proposed change |
| Reproduction needs production data or writes | Stop; request explicit permission |

### Hypothesis ranking

Rank by prior ÷ experiment cost, not by prior alone. A 0.4 cause checked in 5 minutes (score 4.8/hour) goes before a 0.6 cause needing 60 minutes of setup (0.6/hour). Re-rank after every result.

## Anti-Patterns

### Theory Before Signal
**Mistake:** Reading code for an hour to build an explanation, then patching it, with no command that shows whether the bug is gone.
**Why it happens:** Reading code feels like progress, and building a harness feels like a detour from "the real work".
**Instead:** Build the reproduction signal first and treat it as the deliverable of the first hour. A theory with no signal cannot be confirmed; a signal without a theory can still be bisected.

### The Shotgun Change
**Mistake:** Changing the numeric type, upgrading a library and adding a retry in one experiment, then declaring victory when the symptom disappears.
**Why it happens:** Pressure to close the ticket rewards anything that turns the build green.
**Instead:** One variable per experiment. If the bug vanishes after a multi-change patch, back changes out one at a time until the signal goes red again — that change is the evidence.

### "Does Not Crash" as the Assertion
**Mistake:** A reproduction that only checks the exit code, so it stays green when the wrong total is computed and goes red on unrelated flakiness.
**Why it happens:** Exit codes are easy to check; the actual symptom often needs a reference value.
**Instead:** Assert the reported symptom exactly: the expected value, the specific exception type and message, the latency budget.

### Pasting Raw Logs
**Mistake:** Pasting a full debug log, request dump or environment printout into a ticket, chat or assistant session.
**Why it happens:** The log looks harmless at a glance and redacting feels slow.
**Instead:** Run `redact_scan.py --pii --write-redacted`, read the copy, and quote only the lines that carry the signal. Read secrets from environment variables inside the repro so they never reach output.

### The Regression Test That Never Failed
**Mistake:** Writing the test after the fix, watching it pass, and assuming it guards the bug.
**Why it happens:** The fix is done and the test feels like paperwork.
**Instead:** Write the test from the minimised reproduction before the fix and watch it fail with the reported symptom. A test that never went red has not been shown to detect anything.

## Files

### Tools Overview

| Script | Purpose | Exit codes |
|--------|---------|------------|
| `scripts/hypothesis_log.py` | Gate a diagnosis log: repro quality, falsifiable predictions, one-variable experiments, stop rule, fix completeness; rank open hypotheses by prior ÷ cost | 0 pass, 1 gate failures, 2 unreadable input |
| `scripts/redact_scan.py` | Detect secrets (keys, tokens, JWTs, auth/cookie headers, URL credentials, secret assignments, high-entropy blobs) and optional PII; write redacted copies | 0 clean, 1 findings, 2 read error |

Both take `--format text|json`. Thresholds are flags: `--max-runtime`, `--min-red-rate`, `--min-hypotheses`, `--stop-after`, `--min-entropy`.

### Reference Documentation

| File | Purpose |
|------|---------|
| `references/reproduction-signals.md` | Signal properties, harness choice per bug class, pinning non-determinism, raising flake rates, minimising, signal checklist |
| `references/bisection-instrumentation-redaction.md` | Commit, input and config bisection; hypothesis fields; instrumentation rules; redaction coverage table; stop rules; regression-test procedure |
| `assets/diagnosis-log-template.md` | Human-readable diagnosis log to fill in and attach to the ticket |
| `assets/repro-script-template.sh` | Signal skeleton with 0 / 1 / 125 exit contract for `git bisect run` |
| `assets/sample_diagnosis_log.json` | Deliberately flawed log — validator exits 1 |
| `assets/sample_diagnosis_log_passing.json` | Well-formed log — validator exits 0 and ranks H1 first |
| `assets/sample_debug_log.txt` | Log with placeholder credentials and PII — scanner exits 1 |

## Scope & Limitations

**In Scope:**
- Root-cause diagnosis for functional bugs, intermittent failures and performance regressions.
- Building and validating reproduction signals; hypothesis ranking; commit, input and configuration bisection.
- Secret and PII scanning plus redaction of logs and captured artefacts before sharing.
- The regression test that locks a confirmed cause in.

**Out of Scope:**
- Scoping the minimal code change once the cause is known — the focused-fix skill covers blast radius and minimal edits; this skill hands over at "cause confirmed".
- Production incident command, paging and customer communication.
- Security vulnerability triage and exploit analysis.
- Attaching debuggers or profilers; the skill tells you where to point them.

**Important Caveats:**
- `redact_scan.py` matches known formats and entropy; it misses proprietary token formats, split secrets and context-sensitive personal data. Always read the redacted copy before sharing.
- Priors in the hypothesis log are judgement, not measurement. The ranking is only as good as those estimates; re-rank after each result.
- The validator checks the log's structure and discipline, not whether the stated evidence is true.
