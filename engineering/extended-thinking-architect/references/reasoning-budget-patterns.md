# Reasoning Budget Patterns

Reusable patterns for allocating, escalating, and capping reasoning effort, plus the
cost/quality/latency model behind the advisor scripts. **Model-agnostic:** effort is
described conceptually (none / low / medium / high) — map it to whatever effort knob or
thinking-token budget your provider exposes.

---

## 1. The cost / quality / latency triangle

Every effort decision trades three quantities:

- **Cost** — thinking tokens are billed. Effort raises output cost super-linearly.
- **Latency** — deliberation adds wall-clock time before the first useful output.
- **Quality** — only rises where genuine, verifiable reasoning exists, and only up to a
  plateau (see overthinking).

You can optimize two at the expense of the third, never all three. Name the binding
constraint *before* choosing effort:

| Binding constraint | Implication |
|---|---|
| Latency (realtime UX) | Cap effort low; lean on a better model/prompt, not deliberation |
| Cost (high volume) | Default none/low; reserve high effort for a small hard slice |
| Quality (high error cost) | Spend up the accuracy curve — but only where verifiable |

The advisor's rough multipliers (relative to one no-thinking call on the same model):
**none = 1x, low ≈ 1.5-3x, medium ≈ 3-8x, high ≈ 8-25x.** Treat these as planning
ranges, not guarantees — actual thinking length varies by task and model.

---

## 2. The escalation ladder (start low, climb on failure)

The default policy for an unknown task:

1. **Start at the floor.** Lowest plausible effort (often none/low). Many tasks never
   need more.
2. **Detect failure cheaply.** A checker, test, validator, self-consistency vote, or
   confidence signal decides if the answer is good enough.
3. **Climb one rung on failure.** Retry at the next effort level. Most gains arrive in
   the first one or two escalations.
4. **Stop at a ceiling.** A max effort and a max retry count. Past it, hand off (human,
   fallback path, or "I'm not sure").

Why this beats "start high to be safe": the expensive level runs only on the fraction
of inputs that actually need it, so average cost tracks the *easy* case while worst-case
quality tracks the *hard* case.

---

## 3. Difficulty-routed effort

When inputs vary in hardness, route effort by *predicted* difficulty instead of a single
global level:

- **Cheap difficulty estimate** — a small classifier, heuristics (length, presence of
  multiple constraints, numeric content), or a fast low-effort pass that flags "this is
  hard".
- **Map difficulty → effort** — easy: none/low; medium: low/medium; hard: medium/high.
- **Re-bucket from production traffic** — measure accuracy by bucket and shift the
  thresholds toward the lowest effort that holds quality.

This is the same idea as model routing (cheap model for easy queries), applied to the
effort knob.

---

## 4. Front-loaded loop allocation

For agent loops, concentrate reasoning where it compounds:

```
plan  (think hard, once)  ──►  act  ──► observe ──► act ──► observe ──► ... 
   ▲                              (none/low effort each)                  │
   └────────── recover (high effort, only on a failure signal) ◄──────────┘
                                                                          │
                                                        finalize (medium, once)
```

- **One good plan** makes many steps cheap. Under-resourcing the plan phase is a common
  cause of long, thrashing loops.
- **Routine turns stay thin.** Tool selection and output parsing rarely need deduction.
- **Recovery is event-driven.** Spend high effort only when a failure signal fires
  (error, repeated action, low confidence) — never on a schedule.

`reasoning_loop_allocator.py` encodes this and projects a total cost multiplier so you
can check it against a budget cap before running.

---

## 5. Caps and circuit breakers

| Guard | Scope | Purpose |
|---|---|---|
| Per-call effort cap | One model call | Stop a single call thinking unbounded |
| Loop total cap | Whole task | Hard stop on cumulative spend (e.g. 30x a no-think call) |
| Retry / escalation cap | Escalation ladder | Bound how many times effort climbs |
| Wall-clock cap | Realtime paths | Protect user-facing latency regardless of tokens |
| Step/iteration cap | Agent loop | Prevent infinite act/observe cycling |

Wire caps as **real circuit breakers**: when one bites, abort or hand off, and **log it
loudly**. A silently truncated thinking budget can emit a confident, half-reasoned
answer that looks fine.

---

## 6. Anti-patterns

- **Always-on high effort.** Pays the worst-case cost on every input, including the easy
  majority. Almost always wrong as a default.
- **Effort instead of a prompt fix.** Throwing reasoning at an ambiguous or
  under-specified task — it confidently solves the wrong problem. Fix the prompt first.
- **Effort instead of a tool.** Paying the model to "reason out" facts or arithmetic a
  retrieval/calculator tool returns deterministically.
- **Uniform effort across loop phases.** Spending the same high effort on observe/act
  turns that need none — the dominant source of runaway agent budgets.
- **No checker.** High effort with no way to verify the output: you pay for length and
  confidence, not correctness.
- **No total cap.** Per-call caps without a task-level cap let many steps sum into a
  runaway bill.

---

## 7. Putting it together (worked policy)

A reasonable default policy for a new feature:

1. Run `reasoning_budget_advisor.py` per task type to get a starting effort (or a
   prompt-first / cheaper-model verdict).
2. For anything above "none", implement the **escalation ladder** with a checker.
3. For agent flows, run `reasoning_loop_allocator.py` and adopt the front-loaded
   per-phase plan plus the total budget cap.
4. Instrument: accuracy-vs-effort, cost/latency per *solved* task, per-phase spend,
   and cap-hit rate.
5. Re-tune thresholds toward the **lowest effort on the quality plateau**. Revisit when
   the model, prompt, or traffic mix changes.
