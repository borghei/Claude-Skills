---
name: senior-prompt-engineer
description: >
  Prompt engineering and LLM evaluation. Use when optimizing prompts, designing prompt
  templates, evaluating LLM outputs, building agentic systems, implementing RAG, creating few-
  shot examples, or designing structured-output workflows.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: prompt-engineering
  updated: 2026-11-08
  tags: [prompt-optimization, llm-evaluation, agents, prompt-engineering]
---
# Senior Prompt Engineer

Prompt engineering patterns, LLM evaluation frameworks, and agentic system design. Provides static (deterministic) analysis tools to optimize prompts, evaluate RAG retrieval and generation quality, and validate/visualize agent workflows — plus deep reference libraries of prompt patterns, evaluation metrics, and agent architectures.

## Core Capabilities

- **Prompt optimization** — token counting and cost estimation, clarity/structure scoring, ambiguity and redundancy detection, and generation of optimized prompt versions.
- **Few-shot & structured output design** — extract/manage few-shot examples, design diverse example sets (simple/edge/complex/negative), and enforce reliable JSON/XML schema outputs.
- **RAG evaluation** — context relevance, answer faithfulness, groundedness (ROUGE-L), and retrieval metrics (Precision@K, MRR, NDCG) over pre-retrieved contexts.
- **Agentic system design** — validate agent configs, visualize flows (ASCII/Mermaid), estimate token cost per run, and apply ReAct / Plan-Execute / Tool-Use / multi-agent patterns.
- **Pattern library** — 10 prompt patterns, evaluation frameworks (A/B testing, benchmarks, human eval), and agent architectures with pseudocode.

## Prompting Reasoning Models

Current frontier models reason before they answer, which changes what a good prompt looks like:

- **Goal, context, constraints, done.** Say what the output is for, who reads it, what to avoid and why, and how success is judged. Context beats a generic persona.
- **An output contract.** A schema, a filled example, or the provider's structured-output feature.
- **No scripted thinking.** "Think step by step", forced `Thought:` blocks and "explain your reasoning first" are for non-reasoning models. For reasoning models, raise the platform's reasoning control (effort / thinking budget) when a task needs more depth.
- **Calm emphasis with reasons.** ALL-CAPS imperatives make models over-apply rules; a one-line reason lets them handle edge cases.
- **Evals over intuition.** Keep a small set of real inputs with expected outputs and re-run it on every change.

`prompt_optimizer.py` flags forced chain-of-thought and shouted imperatives, so you can run it on an inherited prompt to find them.

## When to Use

- Optimizing an existing prompt's performance or reducing token costs.
- Designing prompt templates, few-shot examples, or structured-output workflows.
- Evaluating LLM outputs or RAG retrieval/generation quality.
- Building or validating agentic systems and tool-calling workflows.

## Clarify First

What shapes this skill's output most is the target model, the job the prompt has to do, and the data you can test it against. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target model:** whether it is a reasoning model decides whether explicit chain-of-thought helps or hurts, and token counts depend on the family (`prompt_optimizer.py --model`). Prices come from the provider's pricing page, passed as flags.
- **Task and output contract:** whether the prompt classifies, extracts, generates or drives an agent decides which of the 10 patterns fits and whether a JSON or XML schema has to be enforced. A missing output format is one of the first issues the optimizer flags.
- **Evaluation data:** without sample inputs, expected outputs or pre-retrieved contexts, the work stays at static clarity and structure scoring. `rag_evaluator.py` needs contexts and questions before it can report relevance, faithfulness or Precision@K, so find out what exists before promising those numbers.
- **Volume and budget:** the daily run count drives the monthly cost projection (`--runs`), and a tight budget shifts the trade-off between more few-shot examples and a shorter prompt.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `prompt_optimizer.py` | Heuristic prompt review: vague wording, missing output format, forced chain-of-thought, ALL-CAPS emphasis, structure, token estimate; `--optimize`, `--extract-examples`, `--compare` | `python scripts/prompt_optimizer.py assets/sample_prompt_flawed.txt --analyze` |
| `rag_evaluator.py` | Lexical RAG scoring: context relevance, faithfulness (numbers absent from the context count as unsupported), groundedness, Precision@K; `--min-faithfulness` gate | `python scripts/rag_evaluator.py --contexts assets/sample_contexts.json --questions assets/sample_questions.json --min-faithfulness 0.7` |
| `agent_orchestrator.py` | Validate an agent config, draw its flow (ASCII/Mermaid), estimate tokens and cost per run | `python scripts/agent_orchestrator.py assets/sample_agent.yaml --estimate-cost --input-price 0.003 --output-price 0.015` |

No tool carries a price table: costs appear only when you pass prices per 1K tokens from the
provider's current pricing page (the numbers above are example values). `--model` only picks
a characters-per-token ratio, so token counts are estimates, not tokenizer output. Scores
are heuristics for finding problems; confirm with an eval set.

Exit codes: `0` ok; `1` `rag_evaluator.py` faithfulness below `--min-faithfulness`, or
`agent_orchestrator.py --validate` found errors; `2` bad input (missing or empty file,
invalid JSON, wrong shape, `--estimate-cost` without prices).

Samples: `sample_prompt_flawed.txt` (vague verbs, "think step by step", four shouted
imperatives, no output format) against `sample_prompt_clean.txt` (goal, context, criteria,
JSON contract, one example); `sample_questions.json` has one answer that invents a rate limit,
so faithfulness is 0.50 and the 0.7 gate exits 1.

## Workflow

1. Collect 10-20 real inputs with the outputs you expect before changing the prompt.
2. Run `prompt_optimizer.py --analyze` on the current prompt and fix the flagged issues: add the goal, audience and output contract; remove scripted reasoning and shouted rules.
3. Validate on the eval set with the target model and compare against the baseline (`--compare` keeps the static metrics side by side).
4. For RAG, run `rag_evaluator.py` on the retrieved contexts and answers; read every answer it marks unsupported.
5. Done when the eval set meets the agreed pass rate, the faithfulness gate passes, and the prompt states goal, constraints and output format without forced reasoning steps.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tools-and-workflows.md](references/tools-and-workflows.md)** — full tool usage with sample outputs, the prompt-optimization / few-shot / structured-output workflows, common-patterns and command quick references, troubleshooting table, success criteria, and complete per-script parameter/output-format reference. Read when running any tool or executing a workflow.
- **[references/prompt_engineering_patterns.md](references/prompt_engineering_patterns.md)** — what changes for reasoning models, then 10 prompt patterns (zero/few-shot, CoT, role, structured output, self-consistency, ReAct, tree-of-thoughts, RAG) with when each still applies. Read when choosing or applying a prompt technique.
- **[references/llm_evaluation_frameworks.md](references/llm_evaluation_frameworks.md)** — evaluation metrics, text-generation and RAG-specific scoring, human-eval frameworks, A/B testing, benchmark datasets, and pipeline design. Read when measuring quality or comparing prompts.
- **[references/agentic_system_design.md](references/agentic_system_design.md)** — agent architectures (ReAct, Plan-and-Execute, Tool Use, multi-agent, memory/state) and design patterns with pseudocode. Read when building agents or tool-calling systems.

## Scope & Limitations

**This skill covers:**
- Static prompt analysis: token counting, clarity scoring, structure detection, and optimization suggestions
- RAG evaluation: context relevance, answer faithfulness, groundedness, and retrieval metrics (Precision@K, ROUGE-L, MRR, NDCG)
- Agent workflow design: configuration validation, ASCII/Mermaid visualization, and token cost estimation
- Few-shot example extraction and management from existing prompts

**This skill does NOT cover:**
- Live LLM calls or runtime prompt testing --- all analysis is static/deterministic (see `senior-ml-engineer` for LLM integration)
- Vector database setup or embedding generation --- RAG evaluator scores pre-retrieved contexts only (see `senior-data-engineer` for pipeline orchestration)
- Fine-tuning, RLHF, or model training workflows (see `senior-ml-engineer` for model deployment)
- Production monitoring, A/B test execution, or real-time drift detection (see `senior-data-scientist` for experiment design)

## Anti-Patterns

### Scripting the Model's Thinking
**Mistake:** Adding "think step by step" or a forced `Thought:` / `Answer:` template to every prompt.
**Why it happens:** It was the single most reliable trick on earlier models.
**Instead:** Reasoning models already think; the scaffold costs tokens and can degrade the answer. State the goal and output contract, and raise the reasoning setting if depth is lacking. Keep explicit steps only for non-reasoning models or when the steps are the deliverable.

### Shouting the Rules
**Mistake:** "You MUST ALWAYS... NEVER..." for ordinary preferences.
**Why it happens:** Emphasis seems to make rules stick.
**Instead:** Current models follow instructions closely; capitals make them apply a rule where it does not fit. Write the rule calmly with its reason so the model can generalise.

### Tuning Without an Eval Set
**Mistake:** Editing a prompt until one or two hand-picked inputs look right.
**Why it happens:** It is fast and feels like progress.
**Instead:** Keep a small set of real inputs with expected outputs and score every version against it. A heuristic score from `prompt_optimizer.py` finds smells; it does not measure quality.

## Files

| File | Purpose |
|------|---------|
| `scripts/prompt_optimizer.py` | Heuristic prompt analysis and cleanup |
| `scripts/rag_evaluator.py` | Lexical RAG retrieval and faithfulness scoring with a gate |
| `scripts/agent_orchestrator.py` | Agent config validation, flow diagrams, token and cost estimates |
| `assets/sample_prompt_flawed.txt`, `sample_prompt_clean.txt` | Before/after prompts for the optimizer |
| `assets/sample_contexts.json`, `sample_questions.json` | RAG inputs with one fabricated answer (gate exits 1) |
| `assets/sample_agent.yaml` | Two-tool ReAct agent config |
| `references/*.md` | Patterns for reasoning and non-reasoning models, evaluation, agent design, tool reference |
