---
name: agent-workflow-designer
description: >
  Design and implement multi-agent orchestration systems with workflow DAGs,
  agent routing, handoff protocols, state management, and cost optimization. Use
  when building AI pipelines with multiple specialized agents, designing
  fan-out/fan-in patterns, or implementing fault-tolerant agent workflows.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-orchestration
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: langgraph, crewai, autogen, claude-agent-teams
---
# Agent Workflow Designer

**Tier:** POWERFUL
**Category:** Engineering / AI Systems
**Maintainer:** Claude Skills Team

## Overview

Design production-grade multi-agent orchestration systems from requirements. Covers five core patterns (sequential pipeline, parallel fan-out/fan-in, hierarchical delegation, event-driven reactor, consensus validation), agent routing strategies, structured handoff protocols, persistent state management, error recovery with circuit breakers, context window budgeting, and cost optimization. Includes framework-specific implementations for LangGraph, CrewAI, AutoGen, and native Claude Code agent teams.

## Keywords

agent workflow, multi-agent orchestration, workflow DAG, agent routing, fan-out fan-in, hierarchical delegation, handoff protocol, state management, agent pipeline, LangGraph, CrewAI, AutoGen, context budgeting

## Core Capabilities

### 1. Pattern Selection and Design
- Sequential pipelines with typed handoffs
- Parallel fan-out/fan-in with merge strategies
- Hierarchical delegation with dynamic subtask discovery
- Event-driven reactors with pub/sub agent triggers
- Consensus validation with voting and arbitration

### 2. Agent Routing
- Intent-based routing with classifier agents
- Skill-based routing using capability matching
- Cost-aware routing (cheap models for simple tasks)
- Load-balanced routing across agent pools
- Fallback chains with graceful degradation

### 3. State and Context Management
- Persistent workflow state across agent hops
- Context window budgeting and summarization
- Checkpoint/resume for long-running workflows
- Conflict resolution for parallel state updates

### 4. Reliability Engineering
- Circuit breakers for failing agents
- Retry with exponential backoff and model fallback
- Dead letter queues for unprocessable tasks
- Timeout enforcement at every agent boundary
- Idempotent operations for safe retries

## When to Use

- Building multi-step AI pipelines that exceed one agent's capability
- Parallelizing research, analysis, or generation tasks
- Creating specialist agent teams with defined roles and contracts
- Designing fault-tolerant AI workflows for production deployment
- Optimizing cost across workflows with mixed model tiers

## Pattern Selection Decision Tree

```
What does the workflow look like?
│
├─ Linear: step A feeds step B feeds step C
│  └─ SEQUENTIAL PIPELINE
│     Best for: content pipelines, code review chains, data transformation
│
├─ Parallel: N independent tasks, then combine
│  └─ FAN-OUT / FAN-IN
│     Best for: competitive research, multi-source analysis, parallel code gen
│
├─ Tree: orchestrator breaks work into subtasks dynamically
│  └─ HIERARCHICAL DELEGATION
│     Best for: complex projects, open-ended research, code generation with planning
│
├─ Reactive: agents respond to events/triggers
│  └─ EVENT-DRIVEN REACTOR
│     Best for: monitoring, alerting, continuous integration, chat workflows
│
└─ Verification: multiple agents must agree on output
   └─ CONSENSUS VALIDATION
      Best for: high-stakes decisions, code review, fact checking, safety-critical output
```

## Pattern 1: Sequential Pipeline

Each stage transforms input and passes structured output to the next. Type-safe handoffs prevent data loss between stages.

### LangGraph Implementation

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_anthropic import ChatAnthropic

class PipelineState(TypedDict):
    topic: str
    research: str
    draft: str
    final: str
    stage_costs: Annotated[list[dict], "append"]  # accumulates cost per stage

def research_stage(state: PipelineState) -> dict:
    model = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=2048)
    result = model.invoke(
        f"Research the following topic thoroughly. Provide key facts, statistics, "
        f"and expert perspectives:\n\n{state['topic']}"
    )
    return {
        "research": result.content,
        "stage_costs": [{"stage": "research", "tokens": result.usage_metadata["total_tokens"]}],
    }

def writing_stage(state: PipelineState) -> dict:
    model = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=4096)
    result = model.invoke(
        f"Using this research, write a compelling 800-word blog post with a hook, "
        f"3 main sections, and a CTA:\n\n{state['research']}"
    )
    return {
        "draft": result.content,
        "stage_costs": [{"stage": "writing", "tokens": result.usage_metadata["total_tokens"]}],
    }

def editing_stage(state: PipelineState) -> dict:
    model = ChatAnthropic(model="claude-haiku-4-20250514", max_tokens=4096)
    result = model.invoke(
        f"Edit this draft for clarity, flow, and grammar. Return only the improved "
        f"version:\n\n{state['draft']}"
    )
    return {
        "final": result.content,
        "stage_costs": [{"stage": "editing", "tokens": result.usage_metadata["total_tokens"]}],
    }

# Build the graph
graph = StateGraph(PipelineState)
graph.add_node("research", research_stage)
graph.add_node("write", writing_stage)
graph.add_node("edit", editing_stage)
graph.add_edge("research", "write")
graph.add_edge("write", "edit")
graph.add_edge("edit", END)
graph.set_entry_point("research")

pipeline = graph.compile()

# Execute
result = pipeline.invoke({"topic": "The future of AI agents in enterprise software"})
print(f"Total cost: {sum(s['tokens'] for s in result['stage_costs'])} tokens")
```

## Pattern 2: Parallel Fan-Out / Fan-In

Independent tasks run concurrently. A merge function combines results.

```python
import asyncio
from dataclasses import dataclass

@dataclass
class FanOutTask:
    name: str
    system_prompt: str
    user_message: str
    model: str = "claude-sonnet-4-20250514"

@dataclass
class FanOutResult:
    task_name: str
    output: str
    tokens_used: int
    success: bool
    error: str | None = None

async def fan_out_fan_in(
    tasks: list[FanOutTask],
    merge_prompt: str,
    max_concurrent: int = 5,
    timeout_seconds: float = 60.0,
) -> dict:
    """Execute tasks in parallel with concurrency limit and timeout."""
    import anthropic

    client = anthropic.AsyncAnthropic()
    semaphore = asyncio.Semaphore(max_concurrent)

    async def run_one(task: FanOutTask) -> FanOutResult:
        async with semaphore:
            try:
                response = await asyncio.wait_for(
                    client.messages.create(
                        model=task.model,
                        max_tokens=2048,
                        system=task.system_prompt,
                        messages=[{"role": "user", "content": task.user_message}],
                    ),
                    timeout=timeout_seconds,
                )
                return FanOutResult(
                    task_name=task.name,
                    output=response.content[0].text,
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                    success=True,
                )
            except Exception as e:
                return FanOutResult(
                    task_name=task.name, output="", tokens_used=0,
                    success=False, error=str(e),
                )

    # FAN-OUT: run all tasks concurrently
    results = await asyncio.gather(*[run_one(t) for t in tasks])
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    if not successful:
        raise RuntimeError(f"All {len(tasks)} fan-out tasks failed: {[f.error for f in failed]}")

    # FAN-IN: merge results
    combined = "\n\n---\n\n".join(
        f"## {r.task_name}\n{r.output}" for r in successful
    )

    merge_response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="Synthesize the following parallel analyses into a unified report.",
        messages=[{"role": "user", "content": f"{merge_prompt}\n\n{combined}"}],
    )

    return {
        "synthesis": merge_response.content[0].text,
        "individual_results": successful,
        "failures": failed,
        "total_tokens": sum(r.tokens_used for r in results) + merge_response.usage.input_tokens + merge_response.usage.output_tokens,
    }
```

## Pattern 3: Hierarchical Delegation

An orchestrator agent dynamically decomposes work and delegates to specialists.

```python
from typing import Literal

SPECIALISTS = {
    "researcher": "Find accurate information with sources. Be thorough and cite evidence.",
    "coder": "Write clean, tested code. Include error handling and type hints.",
    "writer": "Create clear, engaging content. Match the requested tone and format.",
    "analyst": "Analyze data and produce evidence-backed conclusions with visualizations.",
    "reviewer": "Review work product for quality, accuracy, and completeness.",
}

@dataclass
class SubTask:
    id: str
    agent: Literal["researcher", "coder", "writer", "analyst", "reviewer"]
    task: str
    depends_on: list[str]
    priority: int = 0  # higher = run first when deps are equal

class HierarchicalOrchestrator:
    def __init__(self, client):
        self.client = client

    async def plan(self, request: str) -> list[SubTask]:
        """Orchestrator creates an execution plan with dependencies."""
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=f"""You are a task orchestrator. Break down the request into subtasks.
Available specialists: {', '.join(SPECIALISTS.keys())}
Respond with JSON: {{"subtasks": [{{"id": "1", "agent": "researcher", "task": "...", "depends_on": []}}]}}
Rules:
- Minimize the number of subtasks (prefer fewer, more substantial tasks)
- Only add dependencies when output is genuinely needed
- Independent tasks should have empty depends_on for parallel execution""",
            messages=[{"role": "user", "content": request}],
        )
        import json
        plan = json.loads(response.content[0].text)
        return [SubTask(**st) for st in plan["subtasks"]]

    async def execute(self, request: str) -> str:
        """Plan, execute with dependency resolution, and synthesize."""
        subtasks = await self.plan(request)
        results = {}

        # Execute in dependency order, parallelize where possible
        for batch in self._batch_by_dependencies(subtasks):
            batch_results = await asyncio.gather(*[
                self._run_specialist(st, results) for st in batch
            ])
            for st, result in zip(batch, batch_results):
                results[st.id] = result

        # Final synthesis
        all_outputs = "\n\n".join(f"### {k}\n{v}" for k, v in results.items())
        synthesis = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system="Synthesize specialist outputs into a coherent final response.",
            messages=[{"role": "user", "content": f"Request: {request}\n\nOutputs:\n{all_outputs}"}],
        )
        return synthesis.content[0].text

    def _batch_by_dependencies(self, subtasks: list[SubTask]) -> list[list[SubTask]]:
        """Group subtasks into batches that can run in parallel."""
        completed = set()
        remaining = list(subtasks)
        batches = []
        while remaining:
            batch = [t for t in remaining if all(d in completed for d in t.depends_on)]
            if not batch:
                raise ValueError("Circular dependency detected in subtask plan")
            batches.append(sorted(batch, key=lambda t: -t.priority))
            completed.update(t.id for t in batch)
            remaining = [t for t in remaining if t.id not in completed]
        return batches
```

## Pattern 4: Event-Driven Reactor

Agents react to events from a message bus. Decoupled and scalable.

```python
from collections import defaultdict
from typing import Callable, Any

class AgentEventBus:
    """Simple event bus for agent-to-agent communication."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._history: list[dict] = []

    def subscribe(self, event_type: str, handler: Callable):
        self._handlers[event_type].append(handler)

    async def publish(self, event_type: str, payload: Any, source: str):
        event = {"type": event_type, "payload": payload, "source": source}
        self._history.append(event)
        handlers = self._handlers.get(event_type, [])
        results = await asyncio.gather(
            *[h(event) for h in handlers],
            return_exceptions=True,
        )
        errors = [(h, r) for h, r in zip(handlers, results) if isinstance(r, Exception)]
        if errors:
            for handler, error in errors:
                print(f"Handler {handler.__name__} failed: {error}")
        return results

# Usage: code review pipeline triggered by PR events
bus = AgentEventBus()

async def on_pr_opened(event):
    """Security agent scans PR for vulnerabilities."""
    diff = event["payload"]["diff"]
    # ... scan and publish results
    await bus.publish("security_scan_complete", {"findings": findings}, "security-agent")

async def on_security_complete(event):
    """Review agent incorporates security findings into review."""
    # ... generate review with security context

bus.subscribe("pr_opened", on_pr_opened)
bus.subscribe("security_scan_complete", on_security_complete)
```

## Pattern 5: Consensus Validation

Multiple agents independently evaluate the same input. A quorum determines the final output.

```python
@dataclass
class Vote:
    agent: str
    verdict: str  # "approve" | "reject" | "revise"
    confidence: float  # 0.0 - 1.0
    reasoning: str

async def consensus_validate(
    content: str,
    validators: list[dict],  # [{"name": "...", "system": "..."}]
    quorum: float = 0.66,
    confidence_threshold: float = 0.7,
) -> dict:
    """Run content through multiple validators and determine consensus."""
    votes: list[Vote] = []

    # Collect independent votes (no agent sees another's vote)
    vote_tasks = []
    for v in validators:
        vote_tasks.append(get_agent_vote(v["name"], v["system"], content))
    raw_votes = await asyncio.gather(*vote_tasks)
    votes = [v for v in raw_votes if v is not None]

    # Calculate consensus
    approvals = [v for v in votes if v.verdict == "approve"]
    approval_rate = len(approvals) / len(votes) if votes else 0
    avg_confidence = sum(v.confidence for v in votes) / len(votes) if votes else 0

    if approval_rate >= quorum and avg_confidence >= confidence_threshold:
        return {"decision": "approved", "approval_rate": approval_rate, "votes": votes}
    elif any(v.verdict == "reject" for v in votes):
        rejections = [v for v in votes if v.verdict == "reject"]
        return {"decision": "rejected", "reasons": [r.reasoning for r in rejections], "votes": votes}
    else:
        return {"decision": "needs_revision", "feedback": [v.reasoning for v in votes], "votes": votes}
```

## Agent Routing Strategies

### Intent-Based Router

```python
class IntentRouter:
    """Route requests to specialized agents based on intent classification."""

    ROUTING_TABLE = {
        "code_generation": {"agent": "coder", "model": "claude-sonnet-4-20250514"},
        "code_review": {"agent": "reviewer", "model": "claude-sonnet-4-20250514"},
        "research": {"agent": "researcher", "model": "claude-sonnet-4-20250514"},
        "simple_question": {"agent": "assistant", "model": "claude-haiku-4-20250514"},
        "creative_writing": {"agent": "writer", "model": "claude-sonnet-4-20250514"},
        "complex_analysis": {"agent": "analyst", "model": "claude-sonnet-4-20250514"},
    }

    async def route(self, message: str) -> dict:
        # Use a fast, cheap model for classification
        classification = await self.client.messages.create(
            model="claude-haiku-4-20250514",
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
    "claude-sonnet-4-20250514": 200_000,
    "claude-haiku-4-20250514": 200_000,
    "claude-opus-4-20250514": 200_000,
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

## Reliability Patterns

### Circuit Breaker

```python
import time

class CircuitBreaker:
    """Prevent cascading failures when an agent/model is down."""

    def __init__(self, failure_threshold: int = 5, recovery_time: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.state = "closed"  # closed = healthy, open = failing, half-open = testing
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_time:
                self.state = "half-open"
                return True
            return False
        return True  # half-open: allow one test request

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "open"
```

## Common Pitfalls

- **Over-orchestration** — if a single prompt can handle it, adding agents adds cost and latency, not value
- **Circular dependencies** in subtask graphs causing infinite loops; always validate DAG structure before execution
- **Context bleed** — passing entire previous outputs to every stage; summarize or extract only what is needed
- **No timeout enforcement** — a stuck agent blocks the entire pipeline; set wall-clock timeouts at every boundary
- **Silent failures** — agent returns plausible but incorrect output; add validation stages for critical paths
- **Ignoring cost** — 10 parallel Opus calls is expensive; model selection is a cost decision, not just a quality one
- **Stateless retries** on stateful operations — ensure idempotency before enabling automatic retries
- **Single point of failure** in orchestrator — if the orchestrator agent fails, the entire workflow fails

## Best Practices

1. **Start with a single prompt** — only add agents when you prove one cannot handle the task
2. **Type your handoffs** — use dataclasses or TypedDicts for inter-agent data, not raw strings
3. **Budget context upfront** — calculate token allocations before running the pipeline
4. **Use cheap models for routing** — Haiku for classification costs 10x less than Sonnet
5. **Validate DAG structure** at build time, not runtime
6. **Log every agent call** with input hash, output hash, tokens, latency, and cost
7. **Set SLAs per stage** — if research takes >30s, timeout and use cached results
8. **Test with production-scale inputs** — a pipeline that works on 100 words may fail on 10,000

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Pipeline hangs indefinitely | Missing timeout enforcement on one or more agent stages | Add `asyncio.wait_for()` with explicit `timeout_seconds` at every agent boundary; use the Circuit Breaker pattern to fail fast |
| Circular dependency error at runtime | Subtask graph contains a cycle (e.g., task A depends on B which depends on A) | Validate DAG structure at build time with topological sort; the `_batch_by_dependencies` method catches this but validation should happen earlier |
| Context window exceeded mid-pipeline | Intermediate outputs grow beyond the model's token limit | Use the `ContextBudget` class to allocate tokens per stage; summarize or truncate outputs before passing to the next stage |
| Fan-out tasks return inconsistent formats | Each parallel agent interprets the output schema differently | Define a shared `TypedDict` or `dataclass` for all fan-out results; add a validation step before the merge function |
| Orchestrator plan creates too many subtasks | The planning prompt does not constrain subtask count, leading to over-decomposition | Add explicit constraints in the planner system prompt (e.g., "maximum 5 subtasks"); review and approve plans before execution in high-stakes workflows |
| Consensus never reaches quorum | Validators disagree consistently or confidence scores are too low | Lower the `quorum` threshold, add a tiebreaker agent, or revise validator prompts to align on evaluation criteria |
| Cost spikes on parallel workflows | Expensive models (Opus) used for all fan-out branches instead of routing by complexity | Apply cost-aware routing: use Haiku for classification and simple tasks, Sonnet for most work, Opus only for final synthesis or high-stakes decisions |

## Success Criteria

- Pipeline end-to-end latency stays within the defined SLA (e.g., under 60 seconds for a 5-stage workflow) with no stage exceeding its individual timeout
- Agent routing accuracy exceeds 90% when measured against a labeled test set of at least 100 representative requests
- Fan-out/fan-in workflows complete with fewer than 5% task failures across all parallel branches under normal operating conditions
- Total token cost per workflow run decreases by at least 40% after applying model tiering (Haiku for routing, Sonnet for core work, Opus for synthesis)
- Circuit breakers trigger correctly within 5 consecutive failures and recover automatically after the defined recovery window
- Context window utilization stays below 85% of model limits at every pipeline stage, with no truncation-related quality degradation
- All inter-agent handoffs pass schema validation with zero type errors across 100 consecutive workflow executions

## Scope & Limitations

**This skill covers:**
- Design and implementation of five core multi-agent orchestration patterns (sequential, parallel, hierarchical, event-driven, consensus)
- Agent routing strategies including intent-based, skill-based, and cost-aware routing
- Reliability engineering patterns: circuit breakers, retries, timeouts, and dead letter queues
- Context window budgeting, cost optimization, and framework-specific implementations (LangGraph, CrewAI, AutoGen)

**This skill does NOT cover:**
- Training or fine-tuning the underlying LLMs used by agents (see `engineering/ml-pipeline-architect` for ML training workflows)
- Infrastructure provisioning, container orchestration, or deployment pipelines (see `engineering/cloud-infrastructure-designer` for cloud architecture)
- Human-in-the-loop approval workflows or UI design for agent dashboards (see `product-team/ux-researcher` for user-facing workflow design)
- Long-term agent memory, vector database setup, or RAG pipeline construction (see `engineering/rag-pipeline-architect` for retrieval-augmented generation)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/ml-pipeline-architect` | Agent workflows that include ML inference stages use ML Pipeline Architect for model serving and batch prediction design | Workflow DAG exports stage specs to ML pipeline; ML pipeline returns inference endpoints for agent consumption |
| `engineering/rag-pipeline-architect` | Research and retrieval agents within workflows rely on RAG pipelines for grounded knowledge access | Agent sends queries to RAG pipeline; RAG returns ranked document chunks with citations for agent context |
| `engineering/cloud-infrastructure-designer` | Production deployment of agent workflows requires infrastructure design for scaling, queuing, and monitoring | Workflow resource requirements feed into infrastructure specs; infra returns endpoint URLs, queue ARNs, and scaling policies |
| `engineering/api-design-architect` | Inter-agent communication contracts and external API boundaries follow API design standards | Agent handoff schemas are validated against API design specs; API architect provides OpenAPI definitions for external integrations |
| `engineering/system-design-architect` | Overall system architecture decisions (sync vs async, monolith vs distributed) shape workflow topology choices | System design constraints (latency budgets, availability targets) inform pattern selection; workflow requirements feed back into system capacity planning |
| `project-management/technical-project-planning` | Complex multi-agent projects require structured planning for phased rollout, risk management, and milestone tracking | Workflow complexity estimates feed into project plans; PM skill provides sprint boundaries and dependency timelines for staged deployment |
