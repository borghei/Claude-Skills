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
  updated: 2026-06-17
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

## When to Use

- Optimizing an existing prompt's performance or reducing token costs.
- Designing prompt templates, few-shot examples, or structured-output workflows.
- Evaluating LLM outputs or RAG retrieval/generation quality.
- Building or validating agentic systems and tool-calling workflows.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `prompt_optimizer.py` | Analyze/optimize prompts: tokens, clarity, structure, few-shot extraction | `python scripts/prompt_optimizer.py prompt.txt --analyze` |
| `rag_evaluator.py` | Evaluate RAG context relevance, faithfulness, retrieval metrics | `python scripts/rag_evaluator.py --contexts ctx.json --questions q.json` |
| `agent_orchestrator.py` | Validate, visualize, and cost-estimate agent configs | `python scripts/agent_orchestrator.py agent.yaml --validate` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tools-and-workflows.md](references/tools-and-workflows.md)** — full tool usage with sample outputs, the prompt-optimization / few-shot / structured-output workflows, common-patterns and command quick references, troubleshooting table, success criteria, and complete per-script parameter/output-format reference. Read when running any tool or executing a workflow.
- **[references/prompt_engineering_patterns.md](references/prompt_engineering_patterns.md)** — 10 prompt patterns (zero/few-shot, CoT, role, structured output, self-consistency, ReAct, tree-of-thoughts, RAG) with example inputs and expected outputs. Read when choosing or applying a prompt technique.
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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-ml-engineer` | LLM integration and model deployment | Optimized prompts from this skill feed into the prompt templates of its LLM integration layer |
| `senior-data-scientist` | A/B test design for prompt experiments | `experiment_designer.py` defines test parameters; this skill provides the prompt variants to compare |
| `senior-data-engineer` | RAG pipeline orchestration | `pipeline_orchestrator.py` builds the retrieval pipeline; this skill evaluates its output quality |
| `senior-fullstack` | End-to-end application scaffolding | Fullstack apps consume agent configs validated by `agent_orchestrator.py` |
| `senior-security` | Prompt injection and adversarial input review | Security analysis covers the attack surface; this skill ensures prompts include defensive constraints |
| `senior-qa` | Quality assurance for AI-powered features | QA test suites validate that optimized prompts produce consistent outputs in production |
