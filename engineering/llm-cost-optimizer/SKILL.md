---
name: llm-cost-optimizer
description: >
  This skill should be used when the user asks to "estimate LLM costs",
  "count tokens in prompts", "optimize prompt token usage",
  "compare model pricing", or "reduce LLM API costs".
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-cost-management
  updated: 2026-06-29
  tags: [llm, tokens, cost-optimization, prompt-engineering, pricing]
---

# LLM Cost Optimizer

> **Category:** Engineering
> **Domain:** AI Cost Management

## Overview

The **LLM Cost Optimizer** skill provides tools for counting tokens, estimating costs across different LLM providers, and optimizing prompts to reduce token usage without sacrificing quality. Essential for teams managing LLM API budgets at scale.

## Clarify First

Before estimating or optimizing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Input prompt/text** — the prompt file or text to count or optimize (the input via `--file`/`--text`/`--stdin`)
- [ ] **Target models** — which models to estimate cost for (sets `--models` and the pricing comparison)
- [ ] **Goal** — cost estimation vs prompt optimization, and any target reduction (selects `token_counter.py` vs `prompt_optimizer.py` and sets `--target-reduction`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Count tokens in a prompt file and estimate costs
python scripts/token_counter.py --file prompt.txt --models gpt-4o claude-sonnet

# Count tokens from stdin
echo "Hello world" | python scripts/token_counter.py --stdin --models all

# Analyze a prompt for optimization opportunities
python scripts/prompt_optimizer.py --file system_prompt.txt

# Optimize with target reduction
python scripts/prompt_optimizer.py --file prompt.txt --target-reduction 30
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `token_counter.py` | Count tokens and estimate costs across models | `--file`, `--text`, `--stdin`, `--models` |
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

## Reference Documentation

- [LLM Pricing Guide](references/llm-pricing-guide.md) - Current pricing for major LLM providers, token estimation methods
- [Caching & Batch Economics](references/caching-and-batch-economics.md) - Prompt/context caching break-even math, batch-API cost tradeoff, reasoning-effort cost impact, structured-output token overhead (model-agnostic, user-supplied rates)

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
