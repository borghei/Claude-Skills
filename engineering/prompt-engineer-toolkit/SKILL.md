---
name: prompt-engineer-toolkit
description: >
  Tests, versions and scores production prompts: prompt linting, version diffs, eval-suite
  scoring with a CI gate. Use when changing a production prompt, building an eval suite,
  debugging a regression, or migrating to a new model.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: ai-engineering
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: evaluation-rubrics, regression-testing, version-control
  tags:
    - prompt-engineering
    - few-shot
    - evals
    - regression-testing
    - llm
---
# Prompt Engineer Toolkit

The agent treats production prompts like code: it writes them against a stated goal, tests them with an eval suite, versions every change with a reason and a baseline score, and refuses a change that lowers the score. The tools measure prompt text, diff versions and score eval results, so "looks better" becomes a number.

**Pick this or a sibling:** this skill is the test, version and evaluate loop. `engineering/senior-prompt-engineer` covers authoring techniques and LLM system design in depth; `engineering/prompt-governance` covers catalogs, ownership, approval and injection audits across a team.

## How to Write Prompts for Reasoning Models

Current reasoning models think before they answer, so prompts work best when they state the goal, the constraints with the reason for each, the context the model needs, one or two examples of the output, and an exact output contract. Leave out "think step by step", forced "Thought:" blocks and shouted MUST/NEVER: they cost tokens and cause over-triggering. Control depth with the platform's reasoning-effort or thinking-budget setting. Explicit chain-of-thought is for non-reasoning models only (see the patterns catalog). Sampling parameters such as `temperature` are model-dependent and some reasoning models ignore or reject them; use structured outputs for format stability instead.

## When to Use

- Designing a production prompt or building a prompt library.
- Running regression tests or A/B comparisons on prompt variants.
- Versioning prompts and gating changes on eval scores.
- Debugging a degraded prompt, or migrating one to a new model.

## Clarify First

Before designing or testing the prompt, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task and definition of good:** what the prompt must produce and how success is judged (becomes the eval suite).
- **Target model:** reasoning or non-reasoning, structured-output support, and which parameters it accepts.
- **Lifecycle stage:** design new, debug degraded, or migrate (selects the workflow).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Write the eval suite first:** 10 to 30 cases with real inputs, the model's actual outputs, and `contains` / `regex` / `exact` expectations (shape: `assets/sample_eval_suite.json`). Include edge cases and format checks.
2. **Draft or revise the prompt** using the six-layer structure in the patterns catalog: role, goal, constraints with reasons, context, examples, output contract.
3. **Lint the text** with `prompt_analyzer.py`: it flags vague wording, chain-of-thought scaffolding and all-caps emphasis, and estimates tokens.
4. **Diff against the last version** with `prompt_diff.py` and read the risk findings (removed constraints, changed output format).
5. **Score** the new outputs with `eval_scorer.py --fail-under <baseline>`. Validation checkpoint: the new version must match or beat the baseline score, with no new failures on format cases.
6. Done when the suite passes at or above baseline, the changelog entry records the reason and score, and a rollback version is named.

## Quick Start

```bash
# from engineering/prompt-engineer-toolkit/
python3 scripts/prompt_analyzer.py assets/prompt_v1.txt     # 57/100: CoT scaffold, all-caps, vague words
python3 scripts/prompt_diff.py assets/prompt_v1.txt assets/prompt_v2.txt
python3 scripts/eval_scorer.py assets/sample_eval_suite.json --fail-under 0.9   # exit 1: tc-004 breaks the JSON contract
```

## Tools Overview

| Tool | Purpose | Key flags | Exit codes |
|------|---------|-----------|------------|
| `scripts/prompt_analyzer.py` | Clarity score with deductions (vague words, CoT scaffolding, all-caps emphasis), instruction density, few-shot coverage, layer coverage, token estimate | `files...`, `--json` | 0 analyzed; 2 missing file |
| `scripts/prompt_diff.py` | Structural diff of two versions: sections, instructions added and removed, risk findings | `old new`, `--show-diff`, `--json` | 0 compared; 2 missing file |
| `scripts/eval_scorer.py` | Scores outputs against `exact`, `contains` and `regex` expectations; per-tag and per-case results | `suite.json`, `--fail-under 0.8`, `--json` | 0 scored (at or above threshold); 1 below `--fail-under`; 2 unreadable or malformed suite |

The analyzer and diff are heuristics on text: they catch common smells, not whether the prompt works. Only the eval suite answers that.

## Anti-Patterns

**Mistake:** Shipping a prompt change because the new output "reads better".
**Why it matters:** One impressive example hides regressions on the cases you did not look at.
**Instead:** Run the whole suite and compare against the recorded baseline before merging.

**Mistake:** Adding "think step by step" or a required reasoning block for a reasoning model.
**Why it matters:** The model already reasons; the scaffold costs tokens, and forcing reasoning into the answer can break the output contract or be refused.
**Instead:** State the goal and the checks; raise reasoning effort if the task needs more depth.

**Mistake:** Asking the model to rate its own confidence.
**Why it matters:** Self-ratings are labels, not calibration; a confident wrong answer stays confident.
**Instead:** Require an `evidence` field quoting the source for each claim, and test that unsupported claims are marked as such.

## Reference Documentation

- **[references/prompt-patterns-catalog.md](references/prompt-patterns-catalog.md)**: system-prompt layers, reasoning-model guidance and CoT for non-reasoning models, few-shot design, output structuring, decomposition, sampling and evidence fields. Read when designing a prompt.
- **[references/testing-and-versioning.md](references/testing-and-versioning.md)**: test-case design, suite composition, scoring rubric, regression protocol, versioning and changelog format. Read when building a suite or managing versions.
- **[references/failure-modes-and-workflows.md](references/failure-modes-and-workflows.md)**: failure modes with fixes, the three lifecycle workflows, troubleshooting and success criteria. Read when debugging or migrating.

## Files

| File | Purpose |
|------|---------|
| `scripts/prompt_analyzer.py`, `scripts/prompt_diff.py`, `scripts/eval_scorer.py` | Stdlib CLIs |
| `assets/prompt_v1.txt` | Weak ticket-triage prompt (scaffolding, shouting, vague words) |
| `assets/prompt_v2.txt` | Rewrite with goal, reasons, examples and a JSON contract |
| `assets/sample_eval_suite.json` | Four cases; one breaks the JSON-only contract (75% average) |

## Scope & Limitations

**Covers:** prompt structure, eval suites and scoring, regression gating, versioning and changelogs, failure modes, model migration.

**Does not cover:**
- Fine-tuning or training (see `engineering/senior-ml-engineer`).
- Retrieval pipelines (see `engineering/rag-architect` and `engineering/context-engine`).
- Agent orchestration (see `engineering/agent-designer`).
- Inference cost and routing (see `engineering/llm-cost-optimizer`).
- Model-graded evaluation: `eval_scorer.py` checks text deterministically; it makes no model calls.
