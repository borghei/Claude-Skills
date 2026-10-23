---
name: extended-thinking-architect
description: >
  This skill should be used when the user asks to "decide reasoning effort",
  "set a thinking budget", "when to use extended thinking",
  "tune reasoning vs cost", or "should this task use a reasoning model".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-engineering
  updated: 2026-06-29
  tags: [extended-thinking, reasoning-effort, llm, cost-optimization, agents]
---

# Extended Thinking Architect

> **Category:** Engineering
> **Domain:** AI Engineering

## Overview

The **Extended Thinking Architect** skill helps you decide *when* an LLM task should spend a reasoning/thinking budget, *how much* (no-thinking / low / medium / high), and when the better move is a cheaper model with a sharper prompt instead. It turns task signals — error cost, ambiguity, step count, latency budget — into a deterministic recommendation with a rough cost multiplier, and allocates effort across the phases of an agent loop so you front-load reasoning where it pays and avoid runaway budgets.

## Clarify First

Before recommending an effort level, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task type & verifiability:** what the model is actually doing (extraction, classification, planning, code-debug, math…) and whether the output is checkable (sets `--task-type` and `--verifiable`).
- **Cost of a wrong answer:** how expensive a bad output is, plus the latency budget the task must fit (sets `--error-cost` and `--latency-budget`).
- **Shape of the work:** how many reasoning/tool steps are expected and how ambiguous the request is (sets `--steps` and `--ambiguity`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Recommend a reasoning effort level for a single task
python scripts/reasoning_budget_advisor.py --task-type code-debug \
  --error-cost high --steps 4 --ambiguity low --latency-budget interactive

# A cheap, high-volume classification task — expect "cheaper model + better prompt"
python scripts/reasoning_budget_advisor.py --task-type classification \
  --error-cost low --latency-budget realtime --json

# Allocate reasoning effort across the phases of an agent loop
python scripts/reasoning_loop_allocator.py --difficulty high --steps 8 \
  --max-budget-multiplier 30

# Tight-latency loop — see effort capped per phase
python scripts/reasoning_loop_allocator.py --difficulty medium --steps 5 --realtime --json
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `reasoning_budget_advisor.py` | Recommend an effort level (none/low/medium/high) or "prompt-first / cheaper-model" for one task, with rationale + cost multiplier | `--task-type`, `--error-cost`, `--steps`, `--ambiguity`, `--latency-budget`, `--verifiable`, `--json` |
| `reasoning_loop_allocator.py` | Allocate reasoning effort across agent-loop phases (plan/act/observe/recover/finalize) under a total budget cap | `--difficulty`, `--steps`, `--max-budget-multiplier`, `--realtime`, `--json` |

## Workflows

### Choosing Effort for a New Task
1. Identify the task type and whether the output is verifiable (ground truth or a checker exists).
2. Run `reasoning_budget_advisor.py` with the error cost, step count, ambiguity, and latency budget.
3. If the result is **prompt-first**, fix the prompt/spec (clarify, add examples) before spending any reasoning, then re-run.
4. If the result is **cheaper-model**, route to a smaller/faster model and invest the savings in a better prompt.
5. Otherwise adopt the recommended effort, note the cost multiplier, and set a per-call budget cap.

### Budgeting Reasoning Across an Agent Loop
1. Estimate overall task difficulty and the expected number of steps.
2. Run `reasoning_loop_allocator.py` to get per-phase effort (front-loaded at plan/recover, thin at act/observe).
3. Apply the total budget cap as a hard stop so a stuck loop cannot run away.
4. Instrument per-phase token spend; if observe/act phases consume high reasoning, that is an overthinking signal — clamp them.

## Scope & Limitations

**In Scope:**
- Recommending a reasoning effort level (none, low, medium or high), or a prompt-first or cheaper-model route, with `reasoning_budget_advisor.py` from task type, error cost, step count, ambiguity, latency budget and verifiability
- A rough cost multiplier range for each effort level, relative to a no-thinking call on the same model
- Allocating effort across agent-loop phases (plan, act, observe, recover, finalize) under a total budget cap with `reasoning_loop_allocator.py`
- Guidance on where reasoning pays off, overthinking failure modes, escalation ladders and circuit breakers from the references

**Out of Scope:**
- Calling a model or measuring real thinking-token use; the scripts make rule-based recommendations only
- Token pricing, caching and model routing in general (see `engineering/llm-cost-optimizer/`)
- Measuring whether more reasoning improved quality (see `engineering/agentic-evaluation-framework/`)
- Prompt rewriting when the advice is prompt-first (see `engineering/prompt-engineer-toolkit/`)
- Agent workflow structure beyond reasoning budgets (see `engineering/agent-workflow-designer/`)

**Important Caveats:**
- Recommendations come from fixed rules over coarse inputs that the user supplies. They are a starting point to confirm with an eval, not a measured optimum.
- The cost multipliers are broad ranges. Real thinking-token use varies a lot by task and by model.
- The skill is vendor-agnostic. How effort or thinking budgets are exposed, and what they cost, differs by provider and model version and changes often.

## Reference Documentation

- [When to Use Extended Thinking](references/when-to-use-extended-thinking.md) - Decision matrix of task classes where reasoning pays off vs. is wasted, interaction with tool use and agent loops, budget guards, overthinking failure modes, and eval signals.
- [Reasoning Budget Patterns](references/reasoning-budget-patterns.md) - Allocation patterns, escalation ladders, caps and circuit breakers, and the cost/quality/latency tradeoff model.

## Common Patterns

### When Reasoning Pays Off
- Multi-step deduction with a verifiable answer (math, constraint solving, debugging from a stack trace)
- Planning and decomposition before a long agent run — front-load thinking once, not on every tool call
- High error-cost decisions where a wrong answer is expensive to detect or undo

### When Reasoning Is Wasted
- Extraction, classification, and formatting — deterministic mappings, not deduction; a cheaper model usually wins
- Underspecified requests — extra thinking confidently elaborates on the wrong goal; fix the prompt first
- Realtime/latency-tight paths where thinking tokens blow the budget more than they improve quality

### Guarding the Budget
- Set a per-call effort cap *and* a loop-level total cap (e.g. a multiple of one no-thinking call)
- Escalate effort only on failure (retry at higher effort), never start high "to be safe"
- Treat reasoning spent on trivial sub-steps as a regression — alert on per-phase token spend
