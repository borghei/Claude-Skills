# Agent Routing, Context Budgeting & Cost Optimization

Read this when choosing how requests reach agents and how to control spend.

## Agent Routing Strategies

### Intent-Based Router

```python
class IntentRouter:
    """Route requests to specialized agents based on intent classification."""

    ROUTING_TABLE = {
        "code_generation": {"agent": "coder", "model": "claude-sonnet-5"},
        "code_review": {"agent": "reviewer", "model": "claude-sonnet-5"},
        "research": {"agent": "researcher", "model": "claude-sonnet-5"},
        "simple_question": {"agent": "assistant", "model": "claude-haiku-4-5"},
        "creative_writing": {"agent": "writer", "model": "claude-sonnet-5"},
        "complex_analysis": {"agent": "analyst", "model": "claude-sonnet-5"},
    }

    async def route(self, message: str) -> dict:
        # Use a fast, cheap model for classification
        classification = await self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=50,
            system="Classify the user intent. Respond with ONLY one of: code_generation, code_review, research, simple_question, creative_writing, complex_analysis",
            messages=[{"role": "user", "content": message}],
        )
        intent = classification.content[0].text.strip().lower()
        return self.ROUTING_TABLE.get(intent, self.ROUTING_TABLE["simple_question"])
```

## Context Window Budgeting

```python
MODEL_LIMITS = {
    "claude-sonnet-5": 1_000_000,
    "claude-haiku-4-5": 200_000,
    "claude-opus-5": 1_000_000,
    "gpt-4o": 128_000,
}

class ContextBudget:
    def __init__(self, model: str, pipeline_stages: int, reserve_pct: float = 0.15):
        self.total = MODEL_LIMITS.get(model, 128_000)
        self.reserve = int(self.total * reserve_pct)
        self.per_stage = (self.total - self.reserve) // pipeline_stages
        self.used = 0

    def allocate(self, stage: str) -> int:
        available = self.total - self.reserve - self.used
        allocation = min(self.per_stage, int(available * 0.6))
        return max(allocation, 1000)  # minimum 1000 tokens per stage

    def consume(self, tokens: int):
        self.used += tokens

    def summarize_if_needed(self, text: str, budget: int) -> str:
        estimated_tokens = len(text) // 4
        if estimated_tokens <= budget:
            return text
        # Truncate to budget with marker
        char_limit = budget * 4
        return text[:char_limit] + "\n\n[Content truncated to fit context budget]"
```

## Cost Optimization Matrix

| Strategy | Cost Reduction | Quality Impact | When to Use |
|----------|---------------|----------------|-------------|
| Haiku for routing/classification | 85-90% | Minimal | Always for intent routing |
| Haiku for editing/formatting | 60-70% | Low | Mechanical tasks |
| Sonnet for most stages | Baseline | Baseline | Default choice |
| Opus only for final synthesis | +50% on that stage | Higher quality | High-stakes output |
| Prompt caching (system prompts) | 50-90% per call | None | Repeated system prompts |
| Truncate intermediate outputs | 20-40% | May lose detail | Long pipelines |
| Parallel + early termination | 30-50% | None if threshold met | Search/validation tasks |
| Batch similar requests | Up to 50% | Increased latency | Non-real-time workloads |
