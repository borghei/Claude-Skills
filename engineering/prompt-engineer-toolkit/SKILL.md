---
name: prompt-engineer-toolkit
description: >
  Prompt engineering frameworks for building, testing, versioning, and evaluating prompts:
  chain-of-thought, few-shot, regression testing, and rubrics. Use when designing production
  prompts, running A/B tests, or building prompt libraries.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-engineering
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: prompt-patterns, evaluation-rubrics, regression-testing, version-control
---
# Prompt Engineer Toolkit — Production Prompt Engineering

The complete lifecycle for production prompts: design patterns that work, testing frameworks that catch regressions, versioning systems that track changes, and evaluation rubrics that replace subjective "looks good" with measurable quality. This treats prompts as production code with the same rigor — not clever tricks.

**Tags:** prompt engineering, chain-of-thought, few-shot, evaluation, testing, prompt versioning

## Core Capabilities

- **Prompt patterns** — 6-layer system-prompt architecture, chain-of-thought (standard, scratchpad, self-consistency), few-shot design + dynamic selection, JSON/section output structuring, decomposition pipelines, calibration (temperature + confidence levels).
- **Testing framework** — test-case structure, suite composition (40/30/15/15), a 5-dimension automated scoring rubric with a weighted formula, and a regression-testing protocol.
- **Versioning** — version-control layout, changelog format with rationale/baselines/rollback, and a prompt-diff risk checklist.
- **Failure-mode catalog** — instruction override, format drift, sycophancy, verbosity, hallucination, anchoring, lost-in-the-middle, each with fixes.
- **Lifecycle workflows** — design a prompt, debug a degraded prompt, migrate a prompt to a new model.

## When to Use

- Designing production prompts or building a prompt library.
- Running A/B tests or regression tests on prompt variants.
- Versioning prompts and gating changes on test scores.
- Debugging a degraded prompt or migrating prompts across models.

## Clarify First

Before designing or testing the prompt, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task & definition of "good"** — what the prompt must produce and how success is judged (drives the 5-dimension evaluation rubric)
- [ ] **Target model** — calibration (temperature, few-shot count) and migration paths differ by model
- [ ] **Lifecycle stage** — design new / debug a degraded prompt / migrate to a new model (selects the workflow)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `eval_scorer.py` | Score evaluation results from JSON test cases (exact/contains/regex) | `python scripts/eval_scorer.py suite.json --fail-under 0.80 --json` |
| `prompt_analyzer.py` | Analyze prompt files for clarity, instruction density, few-shot coverage, tokens | `python scripts/prompt_analyzer.py my_prompt.txt --json` |
| `prompt_diff.py` | Compare two prompt versions for structural changes, instruction deltas, risk | `python scripts/prompt_diff.py v2.txt v3.txt --show-diff --json` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/prompt-patterns-catalog.md](references/prompt-patterns-catalog.md)** — complete catalog of prompting techniques with examples: system-prompt architecture, chain-of-thought, few-shot, output structuring, decomposition, and calibration. Read when designing or structuring a prompt.
- **[references/testing-and-versioning.md](references/testing-and-versioning.md)** — test-case design, suite composition, the evaluation rubric and scoring formula, the regression protocol, version-control strategy, changelog format, and diff analysis. Read when building a test suite or managing versions.
- **[references/failure-modes-and-workflows.md](references/failure-modes-and-workflows.md)** — common failure modes, the three lifecycle workflows, a quick-view integration table, the troubleshooting matrix, and success criteria. Read when debugging a prompt or running a workflow.

## Scope & Limitations

**This skill covers:**
- Designing, structuring, and layering system prompts for production AI applications
- Building and running test suites, evaluation rubrics, and regression tests for prompt quality
- Versioning prompts with changelogs, baselines, and rollback plans
- Calibration techniques including temperature tuning, confidence levels, and few-shot selection

**This skill does NOT cover:**
- Fine-tuning or training models -- see `engineering/model-training-pipeline` for training workflows
- Retrieval-augmented generation (RAG) pipeline design -- see `engineering/context-engine` for context retrieval architecture
- Agent orchestration and multi-step tool use -- see `engineering/agent-designer` for agent system design
- LLM infrastructure, hosting, or cost optimization -- see `engineering/llm-gateway-design` for inference infrastructure patterns

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **agent-designer** | Agent system prompts are the highest-stakes prompts; use this toolkit to test and version them | Agent specs → prompt layers → tested system prompts |
| **self-improving-agent** | Prompt degradation signals feed into self-improvement loops for automatic correction | Test suite results → regression alerts → prompt iteration |
| **context-engine** | Retrieved context quality directly impacts prompt effectiveness; coordinate retrieval tuning with prompt testing | Retrieved chunks → prompt context layer → evaluation scores |
| **ab-test-setup** | A/B test prompt variants in production with statistical rigor before full rollout | Prompt candidates → traffic split → scoring comparison → winner promotion |
| **llm-gateway-design** | Gateway handles prompt routing, versioning, and model fallback at the infrastructure layer | Versioned prompts → gateway config → model routing → response logging |
| **code-review-automation** | Code review prompts are high-frequency production prompts that benefit from this toolkit's testing framework | Review criteria → prompt design → test suite → deployed reviewer prompt |
