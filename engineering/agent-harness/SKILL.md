---
name: agent-harness
description: >
  Test and evaluation harness for AI agents — scenario suites, deterministic
  replay, regression diffing, cost and latency budgets. Use when agent quality
  is vibe-checked, before shipping a prompt or model change, or when evals drift.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: agent-evaluation
  updated: 2026-07-21
  tags: [agent-eval, regression-testing, harness, replay, llm-testing]
---

# Agent Harness

Most agents ship on vibes: someone tries eight prompts, the output looks good,
it goes to production, and the next prompt tweak silently breaks a refusal
nobody re-tested. This skill builds the harness around an agent so its
behaviour becomes measurable — scenario suites with structural assertions,
deterministic replay of recorded tool calls, paired regression diffing across
prompt and model changes, and per-scenario cost and latency budgets. The tools
here score an agent; they never invoke one, so they run offline on every commit.

## When to use this skill

- An agent is going to production and the only quality evidence is manual spot-checking
- A prompt, tool schema, or model version is changing and you need to know what broke
- Two model or configuration options need a defensible comparison, not a demo
- An incident happened and you need the behaviour encoded as a permanent regression test
- Agent cost or latency is climbing across releases and nobody can point to when
- An existing eval suite reports a healthy pass rate that nobody trusts

## Inputs the skill expects

- The agent's tool inventory — names, arguments, and which tools are irreversible
- Recorded transcripts per scenario: tool calls, final output, turns, latency, cost, error state
- The behavioural rules the agent must hold (refusals, escalation triggers, policy boundaries)
- Known failure history — past incidents, customer complaints, internal bug reports
- Current cost and latency expectations per interaction
- The release gate that consumes the result (CI job, review checklist, launch review)

## Clarify First

Before building the harness, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which agent actions are irreversible** — determines which scenarios need `tool_not_called` assertions at `critical` severity, and what the release gate blocks on
- [ ] **Whether transcripts are already recorded** — decides whether workflow 1 starts from replay or from an instrumentation task first
- [ ] **What the suite gates** — a CI blocking check, a nightly report, or a one-off comparison; changes suite size, runtime budget, and severity strictness
- [ ] **The known failure modes** — past incidents seed the adversarial and refusal buckets, which is where regressions actually hide

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Stand up a scenario suite and score a run

1. Enumerate the agent's irreversible actions; each one gets a refusal scenario.
2. Draft 20-30 scenarios across all six buckets (happy, boundary, refusal,
   adversarial, failure-recovery, ambiguity) using
   `assets/scenario_authoring_checklist.md`. Structural assertions first — tool
   called / not called / order / arguments — text assertions only on domain tokens.
3. Declare suite-wide `defaults` for latency, cost, and turn ceilings so every
   scenario is budgeted without repeating yourself.
4. Record one transcript per scenario, scrubbing PII at record time, and stamp
   the run with `model` and `prompt_sha`.
5. Score the run and read critical failures before the pass rate.

```bash
python3 engineering/agent-harness/scripts/scenario_runner.py \
  --suite engineering/agent-harness/assets/sample_suite.json \
  --transcripts engineering/agent-harness/assets/sample_transcripts_baseline.json \
  --strict-critical
```

### Workflow 2 — Gate a prompt or model change on a paired regression diff

1. Score the baseline and the candidate with the *same* suite file, saving both
   as JSON reports.
2. Diff them. Read regressions and budget drift before the aggregate rate.
3. Triage every regression: intended trade, real defect, or flaky scenario
   (re-run the flipped scenario five times to tell the last two apart).
4. Record the decision in `assets/eval_report_template.md` and promote the
   accepted candidate report to the new baseline.

```bash
python3 engineering/agent-harness/scripts/scenario_runner.py \
  --suite engineering/agent-harness/assets/sample_suite.json \
  --transcripts engineering/agent-harness/assets/sample_transcripts_candidate.json \
  --format json > /tmp/candidate.report.json

python3 engineering/agent-harness/scripts/eval_diff.py \
  --baseline engineering/agent-harness/assets/sample_baseline_report.json \
  --candidate /tmp/candidate.report.json \
  --fail-on-regression --drift-threshold 0.15
```

The shipped sample data demonstrates the core lesson: both runs score 83.3%,
and the candidate contains a critical prompt-injection regression. A gate on
pass rate ships it; the paired diff catches it.

### Workflow 3 — Establish cost and latency budgets, then track drift

1. Take the last release's accepted run as the reference.
2. Set per-scenario latency at p95 × 1.3, cost at median × 1.5, and the turn
   ceiling at observed max + 2. Put them in the suite `defaults`, overriding
   only where a scenario is legitimately expensive.
3. Score the current run; budget breaches surface as `minor` assertions, so
   they report without blocking.
4. Diff against the reference with a tight drift threshold to catch the slow
   bleed that stays inside budget.

```bash
python3 engineering/agent-harness/scripts/eval_diff.py \
  --baseline engineering/agent-harness/assets/sample_baseline_report.json \
  --candidate engineering/agent-harness/assets/sample_candidate_report.json \
  --drift-threshold 0.10 --format json
```

## Decision frameworks

### Which assertion type to reach for

| Need | Use | Durability |
|------|-----|------------|
| The agent must take an action | `tool_called`, `tool_call_order` | [PROVEN] Exact; survives rewording |
| The agent must NOT take an action | `tool_not_called` | [PROVEN] The single highest-value assertion in any agent suite |
| The action must use the right data | `tool_arg_equals` | [PROVEN] Catches the right tool with wrong arguments |
| Structured output correctness | `json_field_equals` | [PROVEN] Exact when the agent has a JSON mode |
| A required domain fact appears | `output_contains` on an ID, number, or policy name | [RECOMMENDED] Stable if you never quote sentences |
| A forbidden phrase must not appear | `output_not_contains` | [RECOMMENDED] Good for injection and leak checks |
| Tone, helpfulness, faithfulness | Model-graded rubric (outside this harness) | [EXPERIMENTAL] Noisy and drifts with the judge; calibrate against human labels first, and never gate on it alone |

### Severity, and what each one gates

| Severity | Covers | Gate |
|----------|--------|------|
| `critical` | Safety, money movement, data loss, refusals that must hold | Blocks on a single failure (`--strict-critical`) |
| `major` | Task correctness — the user did not get what they asked for | Blocks below the pass-rate floor (`--fail-under`) |
| `minor` | Budgets, verbosity, style | Reported; never blocks |

### Can I trust this diff?

| Discordant scenarios (flipped either way) | Read it as |
|-------------------------------------------|------------|
| 0 | No behavioural change detected at this suite's resolution |
| 1-5 | Read the individual scenarios; the p-value has no power here |
| 6-24 | Exact McNemar p is meaningful; `eval_diff.py` reports it |
| 25+ | Both the p-value and the aggregate rate movement are informative |

A single `critical` regression is actionable at n = 1. Significance testing is
for aggregate movement, never for safety failures.

## Anti-Patterns

### Gating on the aggregate pass rate
**Mistake:** The release check is "pass rate ≥ 90%," and everything else is advisory.
**Why it happens:** One number is easy to put in a dashboard and easy to explain to leadership, and it genuinely looks like the summary statistic.
**Instead:** Gate on critical-severity failures and on the paired per-scenario diff. The pass rate is the *last* number you read, always with its confidence interval — at 30 scenarios that interval is ±13 points, which cannot resolve the regressions you care about. The sample data here shows two runs at an identical 83.3% where one refunds money on an injected instruction.

### Asserting on sentences instead of structure
**Mistake:** `output_contains: "I've issued your refund of $49.00 and it should arrive in 3-5 business days"`.
**Why it happens:** It is the fastest thing to do — copy the good output into the assertion and move on.
**Instead:** Assert on the tool call (`issue_refund` with `order_id=A-10041`) and on a domain token in the text (`"refund"`, the order ID). Structural assertions do not break when the model rewords, so the suite keeps signal across model upgrades instead of generating a wall of false failures that trains the team to ignore it.

### Only testing what the agent should do
**Mistake:** Every scenario is a happy path; the suite has no `tool_not_called` assertions.
**Why it happens:** Suites get written from the product spec, and specs describe intended behaviour, not forbidden behaviour.
**Instead:** For every irreversible action the agent can take, write a scenario where taking it is wrong. Refusal and adversarial scenarios are where prompt changes actually regress, because a change that makes an agent more capable usually makes it more eager. Target roughly 35% of the suite across refusal and adversarial buckets.

### Tuning the prompt until the suite goes green
**Mistake:** Iterating on the prompt with the full suite visible until every scenario passes.
**Why it happens:** It feels like the tight feedback loop that good engineering is supposed to have.
**Instead:** Hold out 20% of scenarios and never look at them while iterating; run them only at the gate. Thirty scenarios is a small enough surface to overfit in an afternoon, producing an agent that passes the suite and fails users.

### Chasing regressions without a noise floor
**Mistake:** Four scenarios flip after a prompt edit, so the team spends two days finding the cause.
**Why it happens:** Nobody ever ran the identical configuration twice, so run-to-run variance is unmeasured and every flip looks causal.
**Instead:** Before trusting any diff, score the same configuration twice and diff it against itself. That flip count is your noise floor. Then reduce it — temperature 0 where the product allows, replayed tool results rather than live backends, and re-runs of flipped scenarios to separate flaky from real.

## Files

| File | Purpose |
|------|---------|
| `scripts/scenario_runner.py` | Runs a JSON scenario suite against recorded transcripts; reports pass/fail per assertion with severity, budget checks, and CI exit codes |
| `scripts/eval_diff.py` | Diffs two runs into regressed/fixed/stable, with Wilson intervals, exact McNemar on discordant pairs, and cost/latency drift |
| `references/scenario-and-fixture-design.md` | The six scenario buckets, replay modes, fixture recording rules, assertion tiers, suite sizing |
| `references/eval-methodology-and-budgets.md` | Scoring layers, small-sample statistics, budget setting, CI wiring, methodology anti-patterns |
| `assets/sample_suite.json` | Six-scenario support-agent suite covering all assertion types |
| `assets/sample_transcripts_baseline.json` | Recorded baseline run |
| `assets/sample_transcripts_candidate.json` | Recorded candidate run containing a critical regression at an unchanged pass rate |
| `assets/sample_baseline_report.json` | Scored baseline report — input for `eval_diff.py` |
| `assets/sample_candidate_report.json` | Scored candidate report — input for `eval_diff.py` |
| `assets/eval_report_template.md` | Release-decision report template |
| `assets/scenario_authoring_checklist.md` | Pre-merge checklist for any scenario joining a gating suite |
