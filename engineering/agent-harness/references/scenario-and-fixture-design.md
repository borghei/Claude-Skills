# Scenario and Fixture Design

How to build the corpus of scenarios an agent harness runs against, and how to
record fixtures so runs are reproducible instead of a fresh roll of the dice
each time.

---

## 1. The unit of evaluation is the scenario, not the prompt

A prompt is an input. A **scenario** is an input plus the world state the agent
acts on plus the assertions that define correct behaviour. Harnesses that store
only prompts fail the first time behaviour depends on what a tool returned.

A complete scenario has five parts:

| Part | Example | Why it matters |
|------|---------|----------------|
| **Input** | "I want a refund for A-10041" | The user turn(s) |
| **World state** | Order A-10041 is 8 days old, $49, unshipped | Determines the correct answer |
| **Tool behaviour** | `lookup_order` returns that record; `issue_refund` succeeds | Makes replay deterministic |
| **Assertions** | Refund tool called with the right ID; no error | Defines pass/fail mechanically |
| **Budget** | ≤ 6s, ≤ $0.05, ≤ 8 turns | Catches the slow, expensive "correct" answer |

If any of the five is missing, the scenario is a demo, not a test.

---

## 2. Scenario taxonomy — the six buckets

A suite that only contains happy paths tells you nothing you did not already
know. Every production agent suite should carry scenarios in all six buckets,
with rough target proportions for a mature suite:

| Bucket | Share | What it tests | Example |
|--------|-------|---------------|---------|
| **Happy path** | 20% | The agent does the obvious thing correctly | In-policy refund |
| **Boundary** | 20% | Behaviour right at a rule's edge | Order is 30 days old exactly |
| **Refusal / negative** | 20% | The agent does *not* act when it shouldn't | Out-of-policy refund; the assertion is `tool_not_called` |
| **Adversarial** | 15% | Injection, jailbreak, social engineering via tool output | Refund instruction hidden in an order note |
| **Failure recovery** | 15% | Tool errors, timeouts, empty results, malformed data | `lookup_order` returns 500 twice |
| **Ambiguity** | 10% | Underspecified input where asking is correct | "Refund my order" with no ID |

**[PROVEN] The negative and adversarial buckets catch the regressions that
matter.** A model or prompt change that makes an agent more eager will raise
happy-path pass rates while silently breaking refusals. That is the exact
failure mode the sample data in `assets/` reproduces: pass rate unchanged at
83%, one critical safety regression underneath.

---

## 3. Deterministic replay

Live tool calls make evals non-reproducible: a failing run cannot be
distinguished from a flaky backend, and a fix cannot be verified.

### The three replay modes

| Mode | Tools | Model | Use for |
|------|-------|-------|---------|
| **Full replay** | Recorded | Recorded transcript | Regression suites, CI, this skill's scripts |
| **Tool replay** | Recorded / stubbed | Live | Prompt and model comparisons |
| **Live** | Live | Live | Pre-release smoke, canary, staging only |

**[RECOMMENDED] Run full replay in CI on every prompt or model change; run tool
replay nightly; run live only against a staging environment before release.**
Full replay is deterministic and free — it re-scores transcripts you already
paid for. Tool replay costs model tokens but no backend side effects. Live runs
are the only ones that catch integration drift, so they cannot be skipped
entirely, just kept out of the inner loop.

### Recording fixtures

Capture, per scenario execution, the fields the harness scores:

```json
{
  "scenario_id": "refund-within-policy",
  "turns": 4,
  "latency_ms": 5120,
  "cost_usd": 0.0312,
  "error": null,
  "tool_calls": [
    {"name": "lookup_order", "arguments": {"order_id": "A-10041"},
     "result": {"id": "A-10041", "age_days": 8, "total": 49.0}}
  ],
  "final_output": "Your refund of $49.00 ..."
}
```

Rules that keep fixtures usable a year later:

1. **Record tool results, not just tool names.** Without results you cannot
   re-run the scenario against a new prompt.
2. **Scrub PII at record time**, not at review time. Replace real names, emails,
   card numbers, and addresses with stable synthetic values so the fixture stays
   diffable.
3. **Version fixtures alongside the prompt.** Store `prompt_sha` and `model` in
   the run file so a report can never be misattributed.
4. **Never edit a fixture to make a test pass.** If the recorded behaviour is
   wrong, that is the finding.
5. **Freeze time.** Any scenario whose correctness depends on "today" must carry
   an explicit `as_of` date in the world state, or it will start failing on a
   Tuesday for no reason.

---

## 4. Writing assertions that survive rewording

The hardest part of agent evaluation is asserting on natural language without
making the test brittle. Order the assertion types you reach for:

**Tier 1 — structural (always prefer these).** Tool called / not called, call
order, argument values, turn count, error state. These are exact, they do not
break when the model rewords a sentence, and they encode most of what "correct"
means for an agent. Roughly 70% of your assertions should be Tier 1.

**Tier 2 — structured output.** If the agent has a JSON mode, assert on parsed
fields (`json_field_equals`). Exact and stable.

**Tier 3 — text constraints.** `output_contains` on a *domain token* the answer
must include (an order ID, a policy name, "30-day"), `output_not_contains` on a
forbidden phrase, `output_matches` for a loose regex. Never assert on a full
sentence — it will break on the next model version for no behavioural reason.

**Tier 4 — model-graded rubrics.** Reserve for tone, helpfulness, and
faithfulness, which the tiers above cannot express. Costly, noisy, and outside
this harness (which runs offline and calls no models); see
`eval-methodology.md` for how to keep them honest when you do add them.

### The negative assertion is the valuable one

```json
{"type": "tool_not_called", "tool": "issue_refund", "severity": "critical"}
```

One line that encodes a company's money-safety rule. It costs nothing to run
and fails loudly the moment a prompt change makes the agent looser. Write one
for every irreversible action your agent can take: refunds, sends, deletes,
writes, escalations, purchases.

---

## 5. Severity, not just pass/fail

Tag every assertion `critical`, `major`, or `minor`:

| Severity | Meaning | Gate behaviour |
|----------|---------|----------------|
| **critical** | Safety, money, data loss, or a refusal that must hold | Blocks release on any single failure |
| **major** | Task correctness — the user did not get what they asked for | Blocks if the pass rate drops below threshold |
| **minor** | Budget, verbosity, style | Reported, never blocks |

Without severity, a 95% pass rate is meaningless: it may hide the one scenario
where the agent refunds money it should not. `scenario_runner.py
--strict-critical` exits non-zero on any critical failure regardless of the
aggregate rate, which is the gate you actually want in CI.

---

## 6. How many scenarios, and when to add one

**[RECOMMENDED] Start at 20-30 scenarios covering all six buckets, and grow the
suite from incidents, not from imagination.** Twenty well-chosen scenarios beat
two hundred generated variations, because every scenario you add costs
maintenance forever and dilutes the signal in the aggregate rate.

Growth rules:

- **Every production incident becomes a scenario before the fix merges.** This
  is the single highest-value source of scenarios and the one teams skip.
- **Every ambiguous behaviour argument becomes a scenario.** If two people
  disagree about what the agent should do, write the scenario and settle it.
- **Prune scenarios that have passed unchanged for six months and cover a code
  path no longer touched.** Suites rot; a stale suite that takes 40 minutes gets
  disabled.

Sizing guidance for the aggregate pass rate to be meaningful at all:

| Suite size | Pass-rate 95% CI half-width (at ~85% pass) | Verdict |
|-----------|-------------------------------------------|---------|
| 10 | ±22 pts | Aggregate rate is decoration; read scenarios individually |
| 30 | ±13 pts | Detects large shifts only |
| 100 | ±7 pts | Usable for release gating |
| 300 | ±4 pts | Detects the 5-point regressions that matter |

At every size, the paired per-scenario diff (`eval_diff.py`) is far more
sensitive than the aggregate, because the same scenarios appear in both arms.

---

## 7. Fixture directory layout

```
evals/
├── suites/
│   ├── core.json              # the always-on regression suite
│   ├── safety.json            # adversarial + refusal only, gates every release
│   └── longtail.json          # nightly, larger, noisier
├── runs/
│   ├── 2026-07-14-baseline.json
│   └── 2026-07-21-candidate.json
└── reports/
    ├── 2026-07-14-baseline.report.json
    └── 2026-07-21-candidate.report.json
```

Keep `suites/` in version control and reviewed like code — a PR that weakens an
assertion should be as visible as a PR that weakens a unit test. Keep `runs/`
in version control too if they are small enough; they are the evidence behind
every release decision.

---

## 8. Common fixture smells

| Smell | Why it hurts | Fix |
|-------|--------------|-----|
| Every scenario is a happy path | Suite cannot detect over-eagerness | Add refusal + adversarial buckets |
| Assertions quote full sentences | Breaks on every reword | Assert on domain tokens and tool calls |
| Fixtures recorded from production with live PII | Legal exposure; undiffable | Scrub at record time with stable synthetics |
| One giant suite of 400 scenarios | 40-minute CI; gets disabled | Split core (fast, gating) from longtail (nightly) |
| No `prompt_sha` in run files | Reports cannot be attributed | Record prompt + model version per run |
| Scenario depends on the current date | Random Tuesday failures | Pin `as_of` in world state |
