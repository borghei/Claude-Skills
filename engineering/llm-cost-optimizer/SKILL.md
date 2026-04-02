---
name: llm-cost-optimizer
description: >
  This skill should be used when the user asks to "estimate LLM costs",
  "count tokens in prompts", "optimize prompt token usage",
  "compare model pricing", or "reduce LLM API costs".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-cost-management
  updated: 2026-04-02
  tags: [llm, tokens, cost-optimization, prompt-engineering, pricing]
---

# LLM Cost Optimizer

> **Category:** Engineering
> **Domain:** AI Cost Management

## Overview

The **LLM Cost Optimizer** skill provides tools for counting tokens, estimating costs across different LLM providers, and optimizing prompts to reduce token usage without sacrificing quality. Essential for teams managing LLM API budgets at scale.

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
