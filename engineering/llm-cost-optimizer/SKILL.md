---
name: llm-cost-optimizer
description: >
  Estimates LLM token counts and per-request cost across models, flags wasteful prompt text,
  and models prompt-cache break-even. Use when budgeting LLM spend, comparing models on
  cost, or trimming prompt tokens.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: ai-cost-management
  updated: 2026-11-08
  tags: [llm, tokens, cost-optimization, prompt-engineering, pricing]
---

# LLM Cost Optimizer

The agent turns "what will this cost?" into a number with its assumptions shown: estimated tokens, cost per request and per 1,000 requests by model, savings from caching, and prompt text that costs tokens without changing the result. The built-in price table is an illustrative snapshot, not verified current pricing: for real numbers, copy rates from each provider's pricing page into a JSON file and pass it with `--prices FILE` (shape: `assets/sample_prices.json`).

## When to Use

- Budgeting a new LLM feature, or comparing models on cost at expected volume.
- Finding token waste in a long system prompt (repetition, filler, reasoning scaffolds, shouting).
- Deciding whether prompt caching pays off for a given reuse pattern.

## Overview

The **LLM Cost Optimizer** skill provides tools for counting tokens, estimating costs across different LLM providers, and optimizing prompts to reduce token usage without sacrificing quality. Essential for teams managing LLM API budgets at scale.

## Clarify First

Before estimating or optimizing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Input prompt/text:** the prompt file or text to count or optimize (the input via `--file`/`--text`/`--stdin`).
- **Target models:** which models to estimate cost for (sets `--models` and the pricing comparison).
- **Goal:** cost estimation vs prompt optimization, and any target reduction (selects `token_counter.py` vs `prompt_optimizer.py` and sets `--target-reduction`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Count tokens and estimate costs. Built-in prices are illustrative; real numbers come from --prices FILE
python3 scripts/token_counter.py --text "Summarize the attached contract in five bullets." --models claude-opus-5-5 claude-sonnet gpt-4o-mini

# Count tokens from stdin
echo "Hello world" | python3 scripts/token_counter.py --stdin --models all

# Costs from your own price file (copy current rates from the providers' pricing pages)
python3 scripts/token_counter.py --file assets/sample_prompt.txt --prices assets/sample_prices.json

# Analyze a prompt: three findings, one per line (role preamble, CoT scaffold, all-caps emphasis)
python3 scripts/prompt_optimizer.py --file assets/sample_prompt.txt
```

**Exit codes:** 0 report produced; 2 unusable input (missing file, empty input, invalid numbers, unreadable `--prices`).

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `token_counter.py` | Count tokens and estimate costs across models | `--file`, `--text`, `--stdin`, `--models`, `--output-ratio`, `--prices FILE` |
| `prompt_optimizer.py` | Analyze prompts for token reduction opportunities | `--file`, `--target-reduction`, `--format` |
| `cache_savings_calculator.py` | Model prompt-cache economics: naive vs cached cost, break-even reuse, % savings | `--requests`, `--cached-tokens`, `--cache-write-multiplier`, `--cache-read-multiplier`, `--base-input-price`, `--json` |

## Workflows

### Cost Estimation for New Project
1. Collect sample prompts (system prompt + user messages)
2. Run `token_counter.py` with target models
3. Multiply per-request cost by expected daily volume
4. Compare models on cost-quality tradeoff

### Prompt Optimization Sprint
1. Identify highest-cost prompts from usage logs
2. Run `prompt_optimizer.py` on each
3. Apply suggested optimizations
4. Re-count tokens to verify reduction
5. A/B test optimized vs. original for quality

## Scope & Limitations

**In Scope:**
- Token estimates for a prompt from a file, text or stdin, and per-request cost estimates across the OpenAI, Anthropic and Google models in `token_counter.py`'s built-in catalog, using an assumed output/input ratio (`--output-ratio`, default 1.5).
- Rule-based prompt review with `prompt_optimizer.py`: repeated content, filler phrases, redundant instructions and formatting overhead, with estimated savings checked against an optional `--target-reduction`.
- Prompt-cache economics with `cache_savings_calculator.py`: naive versus cached cost, break-even reuse count and percentage savings from user-supplied prices and multipliers.
- Guidance on model tiering, caching, batch processing, reasoning effort and structured-output overhead in `references/`.

**Out of Scope:**
- Exact token counts from a provider tokenizer, or actual spend from a billing dashboard or usage API. The scripts make no network calls.
- Measuring whether a shortened prompt still performs as well (see `engineering/agentic-evaluation-framework/`).
- Running batch jobs (see `engineering/batch-api-orchestrator/`) or designing context and memory management (see `engineering/context-engine/`).
- Security, bias and safety review of prompts (see `engineering/prompt-governance/`).

**Important Caveats:**
- Token counts are heuristic estimates blended from character, word and piece counts with a per-model adjustment. The pricing guide notes that counts can differ by 10-20% between tokenizers.
- Model prices and IDs in `token_counter.py` and `references/llm-pricing-guide.md` are an illustrative snapshot assembled in Q1 2026 and not verified against current provider pages. Use `--prices FILE` with rates from each provider's pricing page for any budget decision.
- `prompt_optimizer.py` lists suggested edits. It does not rewrite the prompt or judge whether a removed phrase mattered, so each change needs a quality check against the original.
- The calculator's defaults (1.25 write multiplier, 0.1 read multiplier, price unit 1.0) are placeholders, not any vendor's published rates.

## Reference Documentation

- [LLM Pricing Guide](references/llm-pricing-guide.md) - Current pricing for major LLM providers, token estimation methods
- [Caching & Batch Economics](references/caching-and-batch-economics.md) - Prompt/context caching break-even math, batch-API cost tradeoff, reasoning-effort cost impact, structured-output token overhead (model-agnostic, user-supplied rates)

## Anti-Patterns

**Mistake:** Budgeting from the built-in price snapshot.
**Why it matters:** Prices and model lines change several times a year; a stale table can be off by a factor of two or more.
**Instead:** Pass `--prices` with rates copied from each provider's pricing page, and record the date.

**Mistake:** Picking the cheapest model from a one-request estimate.
**Why it matters:** At small sizes every model rounds to fractions of a cent; quality differences cost far more than the token bill.
**Instead:** Compare per-1K-request cost at real volume, and only among models that pass the quality bar.

**Mistake:** Applying every optimizer suggestion.
**Why it matters:** Some "redundant" text carries meaning; removing it can lower quality more than it saves.
**Instead:** Apply edits, then run the prompt's eval suite before shipping the shorter version.

## Common Patterns

### Token Reduction Techniques
- Remove redundant instructions and examples
- Use shorter variable names in few-shot examples
- Compress verbose system prompts
- Replace repeated context with references
- Use structured output formats (JSON) to reduce response tokens
- Batch multiple requests into single prompts where possible

### Cost-Effective Model Selection
- Use smaller models for classification/extraction tasks
- Reserve large models for complex reasoning
- Implement model routing based on query complexity
- Cache responses for identical or similar queries
- Cache the stable system-prompt/context/schema prefix (most-stable first, volatile last) and check the reuse break-even with `cache_savings_calculator.py`
- Route bulk, non-interactive work to the batch API (~half cost for added latency); right-size reasoning effort per route — high only where accuracy demands it
