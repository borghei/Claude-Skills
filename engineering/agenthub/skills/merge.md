# Sub-Skill: Merge Outputs

**Parent:** agenthub
**Trigger:** "merge agent outputs", "combine results", "synthesize findings"

## Purpose

Merge outputs from multiple agents into a coherent final deliverable. Handles different merge strategies depending on whether outputs are complementary (different aspects) or competing (same aspect, multiple attempts).

## Workflow

### Step 1: Identify Merge Strategy

| Pattern | Strategy | Description |
|---------|----------|-------------|
| Fan-in | **Synthesize** | Each agent covers different aspect; weave together |
| Reducer | **Rank and select** | Multiple agents did same task; pick best |
| Pipeline | **Chain** | Each agent transforms previous output; use final |
| Validator | **Conditional** | Use output only if validation passed |

### Step 2: Collect Terminal Outputs

Gather all outputs from terminal nodes (agents with no dependents):
```bash
python scripts/result_ranker.py --session <session-id> --list-outputs
```

### Step 3: Apply Merge

**Synthesize (fan-in):**
- Organize outputs by topic/section
- Identify overlaps and contradictions
- Create a unified document with proper transitions
- Cite which agent produced each section

**Rank and select (reducer):**
- Score each output using eval criteria
- Select the highest-scoring output
- Optionally incorporate unique good ideas from runner-ups

**Chain (pipeline):**
- The last agent's output is the final result
- Verify it incorporates all upstream transformations

### Step 4: Quality Check

Run a final eval on the merged output:
- Does it address the original objective?
- Is it internally consistent?
- Does it incorporate key findings from all agents?

### Step 5: Format Final Output

Produce the deliverable in the requested format:
- Structured JSON for programmatic consumption
- Markdown document for human reading
- Summary + detailed sections for executive review

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Terminal outputs | Yes | Outputs from all terminal agents |
| Merge strategy | No | Auto-detected from DAG pattern |
| Output format | No | JSON, markdown, or structured (default: markdown) |

## Outputs

- Merged final deliverable
- Merge report (what was combined, any conflicts resolved)
- Attribution (which agent contributed which section)
