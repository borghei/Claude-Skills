# LLM Pricing Guide

## Token Estimation

### What is a Token?
Tokens are the basic units LLMs process. Roughly:
- 1 token ~ 4 characters in English
- 1 token ~ 0.75 words
- 100 tokens ~ 75 words
- 1,000 tokens ~ 750 words

### Tokenizer Differences
Different models use different tokenizers:
- **GPT-4/GPT-4o**: cl100k_base (100K vocabulary)
- **Claude**: Custom BPE tokenizer (~100K vocabulary)
- **Llama/Mistral**: SentencePiece-based
- **Gemini**: SentencePiece-based

Token counts can vary 10-20% between tokenizers for the same text.

## Pricing Table (as of Q1 2026)

### OpenAI Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| GPT-4o | $2.50 | $10.00 | 128K |
| GPT-4o-mini | $0.15 | $0.60 | 128K |
| GPT-4 Turbo | $10.00 | $30.00 | 128K |
| o1 | $15.00 | $60.00 | 200K |
| o1-mini | $3.00 | $12.00 | 128K |
| o3-mini | $1.10 | $4.40 | 200K |

### Anthropic Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| Claude Opus 4 | $15.00 | $75.00 | 200K |
| Claude Sonnet 4 | $3.00 | $15.00 | 200K |
| Claude Haiku 3.5 | $0.80 | $4.00 | 200K |

### Google Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| Gemini 2.0 Pro | $1.25 | $5.00 | 1M |
| Gemini 2.0 Flash | $0.075 | $0.30 | 1M |
| Gemini 1.5 Pro | $1.25 | $5.00 | 2M |

### Open Source (Self-Hosted Cost Estimates)

| Model | GPU Required | Approx. Cost/hr | Equivalent per 1M tokens |
|-------|-------------|-----------------|--------------------------|
| Llama 3 70B | 2x A100 80GB | $6.00 | ~$0.50 |
| Llama 3 8B | 1x A100 40GB | $3.00 | ~$0.10 |
| Mistral 7B | 1x A100 40GB | $3.00 | ~$0.08 |

## Cost Optimization Strategies

### 1. Model Tiering
Route requests to the cheapest model that meets quality requirements:
- **Tier 1** (cheap): Classification, extraction, formatting -> GPT-4o-mini, Haiku
- **Tier 2** (mid): Summarization, Q&A, code review -> GPT-4o, Sonnet
- **Tier 3** (premium): Complex reasoning, creative writing -> o1, Opus

### 2. Prompt Compression
- Remove filler words and redundant instructions
- Use abbreviations in system prompts
- Replace examples with schema definitions
- Typical savings: 20-40% token reduction

### 3. Response Caching
- Cache responses for identical prompts (exact match)
- Use semantic caching for similar prompts (embedding similarity)
- Typical savings: 30-60% cost reduction for repetitive workloads

### 4. Batching
- Combine multiple small requests into one prompt
- Use structured output to parse multiple results
- Typical savings: 15-30% from reduced overhead tokens

### 5. Context Window Management
- Summarize long conversations instead of sending full history
- Use RAG to inject only relevant context
- Implement sliding window for chat applications
