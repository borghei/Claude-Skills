# When to Use Extended Thinking

A decision reference for spending an LLM reasoning/thinking budget. **Model-agnostic:**
"extended thinking" here means any control that lets a model deliberate before
answering — exposed as an effort knob (e.g. *low / medium / high*) or a thinking-token
budget. The principles hold regardless of provider, parameter name, or price.

---

## 1. The core question

Reasoning effort is not free: thinking tokens are billed and add latency. Spending it
is worthwhile only when **the task contains deduction that a single forward pass gets
wrong, and you can tell whether the answer is right.** Three things must be true for
extended thinking to pay:

1. **There is real reasoning to do** — multiple interacting steps, constraints, or
   cases, not a lookup or a deterministic mapping.
2. **The answer is verifiable** — ground truth, a checker, tests, or a clear rubric.
   Without it, more thinking produces more confident prose, not more correct answers.
3. **Being wrong is expensive** — relative to the extra cost/latency of thinking. If a
   mistake is cheap to detect and retry, buy the retry, not the deliberation.

If any one is missing, default to the cheapest option that works and look elsewhere
(better prompt, smaller model, retrieval, tools).

---

## 2. Decision matrix: where reasoning pays vs. is wasted

| Task class | Reasoning payoff | Why | Default effort |
|---|---|---|---|
| Math / symbolic / constraint solving | **High** | Sequential deduction; verifiable | medium-high |
| Multi-step logical reasoning | **High** | Errors compound without a plan | medium-high |
| Debugging from a stack trace / failing test | **High** | Hypothesis → check loop; verifiable | medium |
| Planning / decomposition for an agent run | **High (once)** | One good plan steers many cheap steps | medium (front-loaded) |
| Code generation (non-trivial) | **Medium** | Helps on algorithmic logic, less on boilerplate | low-medium |
| Retrieval-grounded QA | **Low-medium** | Value is in retrieval, not deliberation | none-low |
| Summarization / rewrite / tone change | **Low** | Transformation, not deduction | none-low |
| Classification / routing / extraction | **~None** | Deterministic mapping; a smaller model wins | none |
| Open-ended creative writing | **Low** | No ground truth; thinking ≠ better, just longer | none-low |
| Casual conversation | **~None** | Latency matters more than depth | none |

**Rule of thumb:** the more a task looks like *search through a solution space with a
checkable target*, the more effort pays. The more it looks like *map input to output
by a known rule*, the more a cheaper model with a sharper prompt wins.

---

## 3. Three alternatives to spending reasoning

Before turning the effort knob up, check whether a cheaper lever solves it:

- **Prompt-first.** If the request is ambiguous, reasoning amplifies whatever target
  you gave it — confidently. Clarify the goal, add 1-2 examples, or tighten the spec.
  Underspecification is a prompt bug, not a thinking deficit.
- **Cheaper model + better prompt.** For classification, extraction, and formatting,
  a smaller/faster model with a good prompt beats a reasoning model on cost, latency,
  *and* often accuracy (less room to overthink).
- **Tools / retrieval / code.** If the model needs *facts* or *exact computation*,
  give it retrieval or a calculator/code tool. Don't pay it to "reason" its way to
  something a tool returns deterministically.

The advisor script encodes these as the **prompt-first** and **cheaper-model** verdicts.

---

## 4. Interaction with tool use and agent loops

In an agent loop the failure mode is **uniform high effort on every turn**. The
efficient shape is front-loaded and event-driven:

- **Plan / decompose — think hard, once.** The highest-leverage place to spend. A good
  plan makes the rest of the loop cheap and short.
- **Act / tool-selection — think little.** Choosing the next tool is mostly routing.
  Routine turns should run at none/low effort.
- **Observe / parse results — usually none.** Reading a tool result rarely needs
  deduction; reserve effort for when a result is surprising.
- **Recover / replan — think hard, but only when stuck.** Escalate effort *on a failure
  signal* (errors, repeated actions, low confidence), not on every step "to be safe".
- **Finalize / synthesize — medium.** A coherent pass over gathered results pays off.

This is what `reasoning_loop_allocator.py` produces. The corollary: instrument
per-phase token spend. Reasoning being burned on observe/act turns is a regression.

---

## 5. Capping and guarding budgets

Two caps, always:

1. **Per-call cap.** Bound the thinking budget of any single call so one call cannot run
   unbounded. A model that "isn't done thinking" should hit a ceiling and answer.
2. **Loop-level total cap.** Bound the whole task at a multiple of one no-thinking call
   (e.g. 30x) and wire it as a real circuit breaker — abort or hand to a human past it.
   "High effort x many steps" is the canonical runaway shape.

Additional guards:

- **Escalate, don't pre-spend.** Start at the lowest plausible effort; retry one notch
  higher only on failure. Starting high "to be safe" is how budgets evaporate.
- **Budget belongs to the task, not the turn.** Track cumulative spend across the loop,
  not just per call.
- **Fail loud on the cap.** A silently truncated thinking budget can yield a confident,
  half-reasoned answer — log and surface when a cap bites.

---

## 6. Overthinking failure modes

More thinking is not monotonically better. Watch for:

- **Diminishing then negative returns.** Past a point, extra deliberation second-guesses
  a correct answer into a wrong one — common on easy items and on tasks with no checker.
- **Verbose elaboration mistaken for quality.** Without ground truth, effort buys
  length and confidence, not correctness. Don't pay for prose.
- **Analysis paralysis in loops.** The model re-plans instead of acting, or loops over
  the same step. A total cap plus event-driven recovery prevents this.
- **Latency blowups.** On realtime paths, thinking tokens can dominate response time;
  cap effort low regardless of how much it might help.
- **Confident wrong plans.** High effort on an ambiguous goal yields an elaborate plan
  for the wrong objective. Resolve ambiguity first (prompt-first).

---

## 7. Eval signals: prove effort is worth it

Don't guess — measure on your own traffic:

- **Accuracy vs. effort curve.** Plot task accuracy at none/low/medium/high. Adopt the
  *lowest* effort on the plateau, not the highest you can afford.
- **Cost & latency per solved task.** Normalize by *solved*, not per call — high effort
  that needs fewer retries can be cheaper end-to-end.
- **Error-class shift.** Check whether higher effort fixes the errors you care about or
  just trades them for verbosity/overthinking errors.
- **Per-phase spend (loops).** Token spend by phase; reasoning on observe/act = clamp it.
- **Stuck/runaway rate.** How often the loop hits the total cap. Rising rate means the
  task is mis-scoped or the plan phase is under-resourced.
- **Segment by difficulty.** Bucket items easy/medium/hard; route effort by predicted
  difficulty instead of applying one global level.
