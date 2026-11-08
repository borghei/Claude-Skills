# LLM Integration Guide

Production patterns for integrating Large Language Models into applications.

---

## Table of Contents

- [API Integration Patterns](#api-integration-patterns)
- [Prompt Engineering](#prompt-engineering)
- [Token Optimization](#token-optimization)
- [Cost Management](#cost-management)
- [Error Handling](#error-handling)

---

## API Integration Patterns

### Provider Abstraction Layer

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> str:
        pass

# Model ids are configuration, not code: read them from settings so a model upgrade is a
# config change. Check each provider's models page for current ids.

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: List[Dict], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    def complete(self, prompt: str, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], **kwargs)

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-5-5"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def chat(self, messages: List[Dict], max_tokens: int = 1024, **kwargs) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,  # required by the Messages API
            messages=messages,
            **kwargs
        )
        return response.content[0].text

    def complete(self, prompt: str, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], **kwargs)
```

### Retry and Fallback Strategy

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def call_llm_with_retry(provider: LLMProvider, prompt: str) -> str:
    """Call LLM with exponential backoff retry."""
    return provider.complete(prompt)

def call_with_fallback(
    primary: LLMProvider,
    fallback: LLMProvider,
    prompt: str
) -> str:
    """Try primary provider, fall back on failure."""
    try:
        return call_llm_with_retry(primary, prompt)
    except Exception as e:
        logger.warning(f"Primary provider failed: {e}, using fallback")
        return call_llm_with_retry(fallback, prompt)
```

---

## Prompt Engineering

### Prompt Templates

| Pattern | Use Case | Structure |
|---------|----------|-----------|
| Zero-shot | Simple tasks | Task description + input |
| Few-shot | Complex tasks | Examples + task + input |
| Chain-of-thought | Reasoning | Reasoning models: state goal and output, raise the reasoning/effort setting; "think step by step" only for non-reasoning models |
| Role-based | Specialized output | System role + task |

### Few-Shot Template

```python
FEW_SHOT_TEMPLATE = """
You are a sentiment classifier. Classify the sentiment as positive, negative, or neutral.

Examples:
Input: "This product is amazing, I love it!"
Output: positive

Input: "Terrible experience, waste of money."
Output: negative

Input: "The product arrived on time."
Output: neutral

Now classify:
Input: "{user_input}"
Output:"""

def classify_sentiment(text: str, provider: LLMProvider) -> str:
    prompt = FEW_SHOT_TEMPLATE.format(user_input=text)
    # Constrain the output with the label list (or structured outputs), not sampling settings:
    # several current models fix or ignore temperature.
    response = provider.complete(prompt, max_tokens=10)
    return response.strip().lower()
```

### System Prompts for Consistency

```python
SYSTEM_PROMPT = """You are a helpful assistant that answers questions about our product.

Guidelines:
- Be concise and direct
- Use bullet points for lists
- If unsure, say "I don't have that information"
- Never make up information
- Keep responses under 200 words

Product context:
{product_context}
"""

def create_chat_messages(user_query: str, context: str) -> List[Dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT.format(product_context=context)},
        {"role": "user", "content": user_query}
    ]
```

---

## Token Optimization

### Token Counting

```python
# Tokenizers differ by provider and model family. Use the provider's own counter:
#   OpenAI models: tiktoken (tiktoken.encoding_for_model(model_id))
#   Claude models: the Messages API token-counting endpoint (client.messages.count_tokens)
#   Open-weight models: the model's tokenizer from its repository
# For budgeting before a call, ~4 characters per token (English) is a usable estimate.

def estimate_tokens(text: str) -> int:
    """Rough, provider-neutral estimate; replace with the provider counter for hard limits."""
    return len(text) // 4

def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Trim text to an approximate token budget, keeping the start."""
    return text[: max_tokens * 4]
```

### Context Window Management

Context windows differ by model and change with releases; read the limit from the model
card rather than hard-coding it. Rules that hold across providers:

- Budget input as window minus the maximum output you request, minus a safety margin.
- Long windows are not free: cost scales with input tokens and quality can drop for facts
  buried mid-context, so retrieve and rank instead of pasting everything.
- Put stable content (instructions, reference docs) first so prompt caching can reuse it.

### Chunking Strategy

```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks
```

---

## Cost Management

### Cost Calculation

Prices change several times a year, so keep them in configuration with an as-of date and
take them from each provider's pricing page. Output tokens usually cost several times more
than input tokens, and cached input is usually discounted, so measure both separately.

### Cost Tracking

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMUsage:
    input_tokens: int
    output_tokens: int
    model: str
    cost: float

def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str
) -> float:
    """Calculate cost from a per-1K-token price table loaded from config (with an as-of date)."""
    prices = PRICING[model]  # e.g. load_pricing("pricing.yaml"); fail loudly on unknown models

    input_cost = (input_tokens / 1000) * prices["input"]
    output_cost = (output_tokens / 1000) * prices["output"]

    return input_cost + output_cost
```

### Cost Optimization Strategies

1. **Use smaller models for simple tasks** - GPT-3.5 for classification, GPT-4 for reasoning
2. **Cache common responses** - Store results for repeated queries
3. **Batch requests** - Combine multiple items in single prompt
4. **Truncate context** - Only include relevant information
5. **Set max_tokens limit** - Prevent runaway responses

---

## Error Handling

### Common Error Types

| Error | Cause | Handling |
|-------|-------|----------|
| RateLimitError | Too many requests | Exponential backoff |
| InvalidRequestError | Bad input | Validate before sending |
| AuthenticationError | Invalid API key | Check credentials |
| ServiceUnavailable | Provider down | Fallback to alternative |
| ContextLengthExceeded | Input too long | Truncate or chunk |

### Error Handling Pattern

```python
from openai import RateLimitError, APIError

def safe_llm_call(provider: LLMProvider, prompt: str, max_retries: int = 3) -> str:
    """Safely call LLM with comprehensive error handling."""
    for attempt in range(max_retries):
        try:
            return provider.complete(prompt)

        except RateLimitError:
            wait_time = 2 ** attempt
            logger.warning(f"Rate limited, waiting {wait_time}s")
            time.sleep(wait_time)

        except APIError as e:
            if e.status_code >= 500:
                logger.warning(f"Server error: {e}, retrying...")
                time.sleep(1)
            else:
                raise

    raise Exception(f"Failed after {max_retries} attempts")
```

### Response Validation

```python
import json
from pydantic import BaseModel, ValidationError

class StructuredResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str]

def parse_structured_response(response: str) -> StructuredResponse:
    """Parse and validate LLM JSON response."""
    try:
        data = json.loads(response)
        return StructuredResponse(**data)
    except json.JSONDecodeError:
        raise ValueError("Response is not valid JSON")
    except ValidationError as e:
        raise ValueError(f"Response validation failed: {e}")
```
