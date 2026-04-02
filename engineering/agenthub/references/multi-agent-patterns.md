# Multi-Agent Orchestration Patterns Reference

## DAG Patterns

### 1. Fan-Out / Fan-In (Most Common)

```
         ┌── Agent A ──┐
Input ───┼── Agent B ──┼──> Merge ──> Output
         └── Agent C ──┘
```

**When to use:** Task decomposes into independent sub-tasks that can run in parallel, then need to be combined.

**Examples:**
- Research from multiple sources, then synthesize
- Generate multiple drafts, then pick the best
- Analyze different aspects of a dataset, then combine findings

**Merge strategy:** Synthesize (each agent contributes different aspects)

### 2. Pipeline (Sequential)

```
Extract ──> Transform ──> Enrich ──> Validate ──> Output
```

**When to use:** Each step depends on the previous step's output and transforms it further.

**Examples:**
- Data processing: extract -> clean -> transform -> load
- Content: research -> outline -> draft -> edit -> polish
- Code: spec -> implement -> test -> review -> deploy

**Merge strategy:** Chain (final agent output is the result)

### 3. Reducer (Competitive)

```
Agent 1 ──┐
Agent 2 ──┼──> Rank ──> Best Output
Agent 3 ──┘
```

**When to use:** Multiple agents attempt the same task independently, and you pick the best result.

**Examples:**
- Multiple code solutions ranked by test pass rate
- Multiple summaries ranked by completeness
- Multiple designs ranked by criteria scores

**Merge strategy:** Rank-select (pick highest scoring output)

### 4. Validator Chain

```
Generate ──> Review ──> Fix ──> Re-Review ──> Approve
```

**When to use:** Quality is critical and each step validates/improves the previous step's work.

**Examples:**
- Code generation with review and fix cycle
- Document drafting with editorial review
- Test generation with coverage validation

**Merge strategy:** Chain (final validated output)

### 5. Map-Reduce

```
Split ──> [Agent per chunk] ──> Reduce ──> Output
```

**When to use:** Input is large and can be split into independent chunks processed in parallel.

**Examples:**
- Analyzing a large codebase file-by-file
- Processing multiple documents in a corpus
- Running tests across multiple environments

**Merge strategy:** Synthesize with deduplication

### 6. Diamond Dependency

```
Agent A ──> Agent B ──┐
    └────> Agent C ──┼──> Agent D
```

**When to use:** Two paths share a common ancestor and a common descendant.

**Warning:** Ensure Agent D correctly handles inputs from both B and C without duplication.

## Agent Design Principles

### Single Responsibility

Each agent should have ONE clear objective. If you cannot describe the agent's job in one sentence, split it.

**Good:**
- "Research competitor pricing data"
- "Generate TypeScript test code from spec"
- "Review code for security vulnerabilities"

**Bad:**
- "Research competitors, analyze pricing, and write a report" (3 agents)
- "Generate and review tests" (2 agents)

### Explicit Contracts

Every agent must declare:
- **Inputs:** What data it needs (with types/schemas)
- **Outputs:** What data it produces (with types/schemas)
- **Constraints:** Time limit, quality threshold, format requirements

### Idempotency

Given the same inputs, an agent should produce the same outputs. This enables:
- Safe retries on failure
- Caching of completed work
- Deterministic debugging

### Context Isolation

Agents should not share mutable state. All data flows through declared inputs and outputs. This prevents:
- Race conditions in parallel execution
- Hidden dependencies between agents
- State corruption from failed agents

## Quality Gate Patterns

### Threshold Gate

```
Output Score >= 0.7 → PASS
Output Score >= 0.55 → REVISE (retry with feedback)
Output Score < 0.55 → FAIL
```

### Rubric Gate

Define specific criteria and grade each:
```
Completeness: 0-1 (all required fields present)
Accuracy:     0-1 (claims supported by evidence)
Format:       pass/fail (matches expected schema)
Relevance:    0-1 (addresses the assigned task)
```

### Consensus Gate

Multiple evaluators must agree:
```
If 2/3 evaluators rate PASS → PASS
If 2/3 evaluators rate FAIL → FAIL
Otherwise → HUMAN_REVIEW
```

## Failure Handling

### Retry with Context

When an agent fails, retry with additional context:
```
Retry 1: Original prompt + error message
Retry 2: Original prompt + error message + hint from evaluator
Retry 3: FAIL (escalate to human)
```

### Skip and Continue

If a non-critical agent fails, skip it and continue the workflow. Downstream agents must handle missing inputs gracefully.

### Fallback Agent

If the primary agent fails, a simpler fallback agent takes over:
```
Primary Agent (complex) ──> FAIL ──> Fallback Agent (simple) ──> Output
```

### Circuit Breaker

After N consecutive failures across agents, halt the workflow:
```
If 3+ agents fail → HALT workflow → notify human
```

## Scaling Considerations

| Agents | Max Parallel | Strategy |
|--------|-------------|----------|
| 2-4 | All parallel | Simple fan-out |
| 5-10 | 3-5 parallel | Batched execution with priority |
| 10-20 | 5-8 parallel | Phased execution with checkpoints |
| 20+ | Consider decomposing into sub-workflows | Hierarchical orchestration |

## Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Parallelization efficiency | parallel_time / sequential_time | > 0.6 |
| Quality gate pass rate | first_attempt_passes / total_attempts | > 0.8 |
| Workflow completion rate | completed_workflows / started_workflows | > 0.95 |
| Critical path ratio | critical_path_time / total_wall_time | < 0.7 |
| Retry rate | retried_agents / total_agents | < 0.15 |
