# Reproduction Signals

A reproduction signal is one command that answers "is the bug present?" with a
yes or no. Everything later in a diagnosis — bisection, hypothesis tests,
instrumentation, the regression test — consumes that answer. This reference
covers how to build one for each class of bug, how to make it trustworthy, and
what to do when the bug refuses to appear on demand.

## Contents

- [Properties of a usable signal](#properties-of-a-usable-signal)
- [Picking the harness by bug class](#picking-the-harness-by-bug-class)
- [Pinning down non-determinism](#pinning-down-non-determinism)
- [Raising the rate of intermittent failures](#raising-the-rate-of-intermittent-failures)
- [Minimising the reproduction](#minimising-the-reproduction)
- [When no signal can be built](#when-no-signal-can-be-built)
- [Signal quality checklist](#signal-quality-checklist)

## Properties of a usable signal

| Property | Bar | Why it matters |
|----------|-----|----------------|
| Specific | Asserts the reported symptom: the wrong value, the exact exception, the latency over budget | A check for "exit code 0" goes green on a different bug and red on unrelated noise |
| Repeatable | Same verdict across at least 3 consecutive runs, or a measured red rate for intermittent bugs | One red run proves the bug exists once; it proves nothing about your change |
| Fast | Under 30 seconds; under 5 is where bisection becomes cheap | Bisection over 200 commits is 8 runs; at 5 minutes a run, nobody does it |
| Unattended | Runs from a shell with no clicking, no manual login, no reading a dashboard | If a human must be present, every experiment waits on them |
| Isolated | Uses fixtures, a local database or recorded traffic rather than shared environments | Shared staging data changes underneath you and invalidates yesterday's runs |

Record these values in the diagnosis log (`runs`, `red_runs`, `runtime_seconds`,
`asserts_symptom`, `minimised`); `hypothesis_log.py` gates on them.

## Picking the harness by bug class

Start at the top of the list for the bug's class and move down only when the
option above it cannot reach the failing code path.

### Wrong output from a function or service

1. A failing unit or integration test at the narrowest seam that still shows the wrong value.
2. A CLI invocation with a fixture file, diffing stdout against a stored known-good output.
3. A differential run: the same input through the last good version and the current one, diffing results.

### Error or crash in a request path

1. A recorded request replayed against a local instance (save the body and the non-secret headers to a file, then send it with any HTTP client in a loop).
2. An integration test that builds the request object directly and calls the handler.
3. A minimal harness that starts only the failing service with its downstream calls stubbed.

### UI behaviour

1. A component-level test that renders the component with the triggering props or store state.
2. A headless browser script that drives the page and asserts on the DOM, console errors or network calls.
3. A scripted manual loop: a shell script that prints each step for a human, waits for Enter, and captures the answer to a file. Use it only when the two options above cannot reach the bug.

### Performance regression

1. A timing harness that runs the slow operation N times and prints the median and p95, failing above a stated budget.
2. A query-plan capture: the database's explain output for the slow query, compared against the plan from the last good release.
3. A profiler run saved to a file, so that two profiles can be compared rather than read once and forgotten.

For performance work, the signal is a number with a threshold, never "feels slow".
Take the baseline measurement before touching any code.

### Data-dependent bugs

1. Capture the offending record (redacted) as a fixture and load it in a test.
2. If the record is unknown, run the job against a copy of the dataset and bisect the dataset (see the bisection reference).
3. Property-based or randomised inputs with a fixed seed: generate many inputs, keep the first that fails, save it as a fixture.

### Regressions between two known states

Write the signal as a script that exits 0 for good and 1 for bad, so it can be
handed straight to `git bisect run`. The same script then serves for dependency
version bisection and configuration bisection.

## Pinning down non-determinism

A signal that changes verdict on the same code is worse than none: it produces
false confirmations. Remove each source of variation explicitly.

| Source | How to pin it |
|--------|---------------|
| Wall clock | Inject a clock, or freeze time in the test; never compare against `now()` |
| Random numbers | Seed every generator and print the seed on failure |
| Ordering of sets, maps, directory listings | Sort before comparing; check whether the code relies on iteration order |
| Concurrency | Run with one worker first; if the bug vanishes, that is itself evidence |
| Network | Replace remote calls with recorded responses |
| Shared state between tests | Run the failing test alone, then with its neighbours, to detect leakage |
| Locale and time zone | Set them explicitly in the harness environment |
| Caches and build artefacts | Clear them at the start of each run, or run in a fresh temporary directory |

## Raising the rate of intermittent failures

The goal with an intermittent bug is not a perfect reproduction but a rate high
enough to compare before and after. As a rule of thumb, a rate of 30% or more
lets 10 runs distinguish "fixed" from "still broken" with reasonable confidence;
at 1% you need hundreds of runs and every experiment becomes a batch job.

Ways to raise the rate:

- Loop the trigger many times inside one process instead of restarting.
- Run several copies in parallel to increase contention.
- Shrink timeouts, pool sizes and buffer sizes to their minimum.
- Inject a short sleep at the suspected race window to widen it.
- Add artificial load on the CPU or disk while the loop runs.

Report the rate as red runs over total runs, and keep the same run count when
comparing before and after a change. A change that takes the rate from 6/10 to
0/10 is evidence; one that takes it from 1/10 to 0/10 is not.

## Minimising the reproduction

Once the signal is red, remove parts until every remaining part is necessary:

1. List the moving parts: input fields, records, configuration keys, steps, services, callers.
2. Remove one part and rerun the signal.
3. If it stays red, the part was irrelevant — leave it out. If it goes green, restore it; it is load-bearing.
4. Repeat until no single removal keeps the signal red.

For large inputs, halve instead of removing one at a time (the delta-debugging
idea, covered in the bisection reference). A minimised reproduction does double
duty: it narrows the hypotheses and becomes the body of the regression test.

## When no signal can be built

Stop and say so, with what was tried. Do not move on to hypotheses: without a
signal, every hypothesis test is an opinion. Ask for one of:

- Access to the environment where the bug occurs, or a copy of the relevant data.
- A captured artefact — request log, crash dump, trace export, screen recording with timestamps — run through `redact_scan.py` before it is shared.
- Permission to ship temporary, tagged instrumentation to the environment that shows the bug, with a removal date.

## Signal quality checklist

- [ ] One command, written in the diagnosis log, that anyone on the team can run
- [ ] Asserts the user's symptom, not merely "no crash"
- [ ] Red on at least 3 consecutive runs, or a recorded red rate of 30% or more
- [ ] Runs in under 30 seconds (re-measure after each tightening)
- [ ] All clocks, seeds, locales and network calls pinned
- [ ] Minimised: removing any remaining part turns it green
- [ ] Contains no secrets in its command line, fixtures or output
