# Agent Routing, Context Budgeting & Cost Optimization

Read this when choosing how requests reach agents and how to control spend.

## Agent Routing Strategies

### Intent-Based Router

```python
class IntentRouter:
    """Route requests to specialized agents based on intent classification."""

    ROUTING_TABLE = {
        "code_generation": {"agent": "coder", "model": "claude-sonnet-5-5"},
        "code_review": {"agent": "reviewer", "model": "claude-sonnet-5-5"},
        "research": {"agent": "researcher", "model": "claude-sonnet-5-5"},
        "simple_question": {"agent": "assistant", "model": "claude-haiku-5-5"},
        "creative_writing": {"agent": "writer", "model": "claude-sonnet-5-5"},
        "complex_analysis": {"agent": "analyst", "model": "claude-sonnet-5-5"},
    }

    async def route(self, message: str) -> dict:
        # Use a fast, cheap model for classification
        classification = await self.client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=50,
            system="Classify the user intent. Respond with ONLY one of: code_generation, code_review, research, simple_question, creative_writing, complex_analysis",
            messages=[{"role": "user", "content": message}],
        )
        intent = classification.content[0].text.strip().lower()
        return self.ROUTING_TABLE.get(intent, self.ROUTING_TABLE["simple_question"])
```

## Context Window Budgeting

```python
# Fill in the context window of each model you route to, from the provider's model docs.
# Windows differ by model and plan, so the code never assumes one.
MODEL_LIMITS: dict[str, int] = {}

class ContextBudget:
    def __init__(self, model: str, pipeline_stages: int, reserve_pct: float = 0.15):
        self.total = MODEL_LIMITS.get(model, 128_000)  # conservative fallback
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

Savings are relative and depend on the provider's current rates; check them on its pricing
page and model the workflow with `scripts/cost_estimator.py --prices` before deciding.

| Strategy | Typical effect on cost | Quality Impact | When to Use |
|----------|---------------|----------------|-------------|
| Small tier (e.g. Haiku) for routing/classification | Large cut on those steps | Minimal | Always for intent routing |
| Small tier for editing/formatting | Moderate cut | Low | Mechanical tasks |
| Mid tier (e.g. Sonnet) for most stages | Baseline | Baseline | Default choice |
| Large tier (e.g. Opus) only for final synthesis | Higher on that stage | Higher quality | High-stakes output |
| Prompt caching (stable system prompt prefix) | Input billed at cache-read rate | None | Repeated system prompts |
| Truncate intermediate outputs | 20-40% | May lose detail | Long pipelines |
| Parallel + early termination | 30-50% | None if threshold met | Search/validation tasks |
| Batch similar requests | Up to 50% | Increased latency | Non-real-time workloads |
