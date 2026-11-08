# Bisection, Instrumentation and Redaction

Three techniques that turn a reproduction signal into a located cause: bisect
to shrink where the bug can live, instrument to observe what the code actually
does there, and redact before anything leaves your machine.

## Contents

- [Bisection](#bisection)
  - [Commit bisection with git](#commit-bisection-with-git)
  - [Input bisection](#input-bisection)
  - [Configuration and dependency bisection](#configuration-and-dependency-bisection)
- [Hypothesis discipline](#hypothesis-discipline)
- [Instrumentation](#instrumentation)
- [Redaction](#redaction)
- [Stop rules](#stop-rules)
- [The regression test](#the-regression-test)

## Bisection

Bisection is the cheapest search there is: each run halves the space. It needs
two things — a known-good state, a known-bad state — and a signal that exits 0
on good and 1 on bad.

### Commit bisection with git

```bash
git bisect start
git bisect bad HEAD
git bisect good v4.1.0            # last release where the signal was green
git bisect run ./repro.sh         # exit 0 = good, 1-124 = bad, 125 = skip this commit
git bisect log > bisect.log       # keep the trail for the write-up
git bisect reset
```

Rules that keep it honest:

- Confirm the endpoints first: run the signal on the good and bad commits by hand before starting.
- Make `repro.sh` build what it needs. A stale build artefact turns every commit "bad".
- Exit 125 when a commit cannot be tested (does not compile, migration missing). Treating it as bad sends the search the wrong way.
- 1,000 commits take about 10 runs. If each run is 3 minutes, that is 30 minutes unattended — usually cheaper than an hour of reading diffs.
- The first bad commit is where the bug became visible, not always where it was written. Read its diff with that in mind.

### Input bisection

When a large input fails and a small one does not, bisect the input:

1. Split the failing input into halves (records, lines, JSON keys, steps in a script).
2. Run the signal on each half.
3. Keep a half that still fails and repeat.
4. If neither half fails alone, the bug needs parts from both: split into quarters and test combinations, keeping the smallest failing combination.

Stop when removing any remaining element turns the signal green. The result is
usually a single record or a pair of interacting records, which then becomes the
regression fixture.

### Configuration and dependency bisection

The same halving works on any list of differences between a good and a bad
environment:

| Difference set | How to bisect it |
|----------------|------------------|
| Feature flags | Copy the good flag set; flip half of the differing flags to their bad values; rerun |
| Environment variables | Diff the two environments' variables; apply half the differences |
| Dependency versions | Diff the two lockfiles; upgrade half the differing packages in a scratch branch |
| Infrastructure settings | Diff the deployed configuration; apply half in a disposable environment |

Write the difference list down before starting. Bisection over an unrecorded
list degrades into random flipping.

## Hypothesis discipline

Write 3 to 5 hypotheses before testing any. One hypothesis anchors you; a long
list is a sign the reproduction is not minimised yet.

Each entry in the diagnosis log carries:

| Field | Content |
|-------|---------|
| `statement` | The mechanism, named: "per-line discounts are rounded before summing" — not "rounding issue" |
| `prediction` | "If X is the cause, then changing Y makes the symptom disappear (or Z makes it worse)" |
| `experiment` | The single change that could refute it, and what you will observe |
| `prior` | Your probability estimate, 0 to 1. Rough is fine; it exists to force ranking |
| `cost_minutes` | Time to run the experiment |
| `status` / `evidence` | open, refuted, confirmed or inconclusive, with the observation that decided it |

`hypothesis_log.py` ranks open hypotheses by prior divided by cost. Test the
highest score first: a 40%-likely cause that takes 5 minutes to check beats a
60%-likely cause that needs an hour of setup. Share the ranked list with the
person who reported the bug before testing — one sentence of context from them
("we changed the paginator last week") can re-rank everything.

One experiment changes one variable. Two changes at once produce a result you
cannot attribute, and the log validator rejects it.

## Instrumentation

Prefer, in order:

1. A debugger breakpoint or REPL at the point where hypotheses diverge. One stop answers what ten log lines guess at.
2. Targeted log lines at the boundaries that distinguish the open hypotheses — inputs and outputs of the suspect function, not its every step.
3. Assertions that crash loudly when an invariant breaks, placed upstream of where the symptom shows.

Rules:

- Tag every temporary log line with a unique marker such as `[DBG-7c1e]`, and record the tag in the diagnosis log. Cleanup is then one search: `grep -rn "DBG-7c1e" .` must return nothing before the fix merges.
- Log values, not just "reached here". `line_discounts=[0.335, 0.335, 0.335] rounded=[0.34, 0.34, 0.34]` settles a hypothesis; `in apply_discounts` does not.
- Never log full request objects, headers, environment dumps or configuration objects. That is how secrets reach log aggregators.
- For performance, measure instead of logging: a timer around the suspect block, a profile, or a query plan.

## Redaction

Anything copied out of a terminal — into a ticket, a chat, a pull request, an
assistant session — is published. Assume it will be read by people who should
not have your credentials.

Before sharing any log, trace, stack dump or command output:

1. Run `redact_scan.py --paths <file> --pii`. Exit 1 means something was found.
2. Run again with `--write-redacted` and share only the `.redacted` copy.
3. Read the copy by eye. Pattern scanners miss custom token formats and secrets split across lines.
4. Quote only the lines that carry the signal. Ten relevant lines beat a 4,000-line paste.

Keep secrets out of the reproduction itself: read credentials from environment
variables inside the script so that the command line and its output stay clean.
If a redacted artefact is not enough to diagnose the bug, say so and ask for the
specific missing detail rather than the raw file.

| What the scanner catches | What it does not |
|--------------------------|------------------|
| Private key headers, cloud access key ids, code-host, chat and payment tokens | Proprietary token formats with no fixed prefix |
| JWTs, Authorization and Cookie headers | Secrets split across lines or base64-wrapped inside larger blobs below the entropy threshold |
| Credentials embedded in URLs | Customer data that is sensitive by context (account notes, free text) |
| `password=`, `token:`, `api_key=` style assignments | Values in binary dumps |
| High-entropy blobs of 32+ characters | Short secrets such as PINs |
| Email and IPv4 addresses with `--pii` | Names, postal addresses, phone numbers |

## Stop rules

Stop and report instead of continuing when any of these holds:

| Condition | Why stop | What to report |
|-----------|----------|----------------|
| No reproduction signal after a timeboxed attempt (default 90 minutes) | Further work is guessing | What was tried; the access, artefact or instrumentation you need |
| 4 inconclusive experiments in a row | The signal or the hypothesis list is wrong | Re-check the signal's specificity; widen the hypothesis list |
| Every listed hypothesis refuted | The model of the system is wrong | Re-read the minimised reproduction; ask someone who owns the code |
| The fix needs a change outside the agreed blast radius | Scope decision, not a debugging decision | The cause, the proposed change and its reach |
| Reproducing requires production data or production writes | Safety gate | The exact access needed and why |

## The regression test

Write it before the fix, from the minimised reproduction, at a seam where the
real failure pattern occurs. A test at too shallow a seam (a helper tested alone
when the bug lives in how two callers use it) passes before and after the fix and
proves nothing.

1. Turn the minimised reproduction into a test at that seam.
2. Run it and watch it fail with the reported symptom. If you forced the failure by editing a fixture, diff against the original to confirm the edit took.
3. Apply the fix. Run the test: green.
4. Run the original, unminimised signal: green.
5. Remove tagged instrumentation and throwaway harnesses.
6. Write the confirmed hypothesis and its evidence into the commit or pull-request message.

If no seam reaches the failure pattern, record that as a finding
(`regression_test.no_seam_reason` in the log). It is a design problem worth
raising, not a reason to skip the test silently.
