# Orchestration Patterns — Implementations

The five core multi-agent patterns with framework-specific code. Read the section
that matches the topology chosen from the decision tree in `SKILL.md`.

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
    model = ChatAnthropic(model="claude-sonnet-5", max_tokens=2048)
    result = model.invoke(
        f"Research the following topic thoroughly. Provide key facts, statistics, "
        f"and expert perspectives:\n\n{state['topic']}"
    )
    return {
        "research": result.content,
        "stage_costs": [{"stage": "research", "tokens": result.usage_metadata["total_tokens"]}],
    }

def writing_stage(state: PipelineState) -> dict:
    model = ChatAnthropic(model="claude-sonnet-5", max_tokens=4096)
    result = model.invoke(
        f"Using this research, write a compelling 800-word blog post with a hook, "
        f"3 main sections, and a CTA:\n\n{state['research']}"
    )
    return {
        "draft": result.content,
        "stage_costs": [{"stage": "writing", "tokens": result.usage_metadata["total_tokens"]}],
    }

def editing_stage(state: PipelineState) -> dict:
    model = ChatAnthropic(model="claude-haiku-4-5", max_tokens=4096)
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
    model: str = "claude-sonnet-5"

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
        model="claude-sonnet-5",
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
            model="claude-sonnet-5",
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
            model="claude-sonnet-5",
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
