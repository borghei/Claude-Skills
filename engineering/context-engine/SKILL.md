---
name: context-engine
description: >
  Context management engine for AI coding agents. Use when building agent memory systems,
  optimizing context windows, allocating token budgets, designing RAG pipelines for code, or
  managing persistent multi-session agent state.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: ai-agents
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: context-window-optimization, memory-architecture, knowledge-graphs
  tags:
    - context-management
    - ai-agents
    - memory
    - rag
    - token-budget
---
# Context Engine - AI Agent Context Management

Decide what an agent should have in its context window, what it should keep in persistent memory, and what it should retrieve on demand, then measure and trim the window to fit. The goal is an agent that has the facts it needs for the current step and nothing that crowds them out.

## When to Use

- Bootstrapping agent context for a new codebase, or tailoring it to a task (bug fix, feature, refactor, review).
- A long agent loop is running out of window, or quality drops late in a session.
- Designing persistent memory across sessions, or a retrieval pipeline over code.
- Coordinating what context several agents share and hand off.

## Clarify First

Before designing or analyzing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which task:** bootstrap context for a codebase, optimize for a specific task, design persistent memory, or build a code RAG (selects the analyzer/pruner/indexer and the playbook).
- **Token budget:** the context-window ceiling (sets `--budget` and which packing strategy applies).
- **Source content:** the files/codebase or knowledge base to index (the input the scripts process).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Measure.** Run `context_analyzer.py` on the files or prompt you plan to load. Token counts are estimates (about 4 characters per token); use the provider's token-counting endpoint when you need exact numbers.
2. **Budget.** Run `context_budget_planner.py` with the window size and each component's size. It flags components outside their band and, on overflow, lists what to evict first.
3. **Decide where each piece lives**, using these rules:
   - Needed on every step and small (instructions, task spec, key interfaces): keep it in the window as an anchor.
   - Needed across sessions (decisions, conventions, open questions): write it to the memory tool or a memory file, and reload it at session start. Recomputable facts (file contents, test output) do not belong in memory.
   - Large, and only some of it is relevant per step (a codebase, a doc set): retrieve it. Use `memory_indexer.py` for a quick lexical index; move to embeddings plus code-aware chunking when lexical search misses.
   - Fits comfortably and the task needs cross-references across all of it: load it into a long window instead of building retrieval.
4. **Compact before the cliff.** Trigger compaction at a high-water mark (around 70-80% of the window), not at 100%: evict superseded tool outputs first, then summarize-and-replace old history, never the anchors. Write durable conclusions to memory before evicting them. Where the platform offers server-side context editing or compaction, prefer it to hand-rolled summaries.
5. **Prune what you load.** `context_pruner.py` strips comments, docstrings, import blocks and duplicates from code; for Markdown and text it only removes duplicate blocks and extra blank lines, so headings and structure survive.
6. **Verify** the result: the task still succeeds with the trimmed context (rerun the step or an eval), and the budget planner reports no overflow.

## Quick Start

```bash
python3 scripts/context_analyzer.py references/ --budget 128000
python3 scripts/context_budget_planner.py --window-size 200000 --system 4000 --history 60000 --tools 90000 --rag 40000 --reserve-output 8000
python3 scripts/context_pruner.py scripts/memory_indexer.py --aggressive
python3 scripts/memory_indexer.py references/ --query "compaction high-water mark" --top 3
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `context_analyzer.py` | Estimated tokens, relevance and suggestions for files or a prompt | `<path>` or `--prompt`, `--budget`, `--json` | 0 ok, 2 nothing to analyze |
| `context_budget_planner.py` | Allocate a window across system, memory, history, tools, RAG and reserved output; flag bands and overflow; eviction order | `--window-size` (required), component sizes, `--json` | 0 fits, 1 overflow, 2 bad arguments |
| `context_pruner.py` | Prune code (comments, docstrings, imports, braces, duplicates) or prose (duplicates, blank runs only) | `<path>` or `--stdin [--prose]`, `--level light|moderate|aggressive`, `--output <dir>`, `--json` | 0 ok, 2 no files / no input |
| `memory_indexer.py` | TF-IDF index and search over a directory of notes or docs | `<dir>`, `--query`, `--top`, `--index-only`, `--stats` | 0 ok, 2 not a directory / nothing indexable |

## Anti-Patterns

**Mistake:** Loading everything that might be relevant "to be safe".
**Why it happens:** Large windows make it possible, and missing context feels riskier than extra context.
**Instead:** Irrelevant tokens dilute attention and cost money on every turn. Load anchors, retrieve the rest, and check the budget.

**Mistake:** Compacting at the limit.
**Why it happens:** Nothing forces action until the window is full.
**Instead:** Set a high-water mark and compact while there is headroom to write a good summary.

**Mistake:** Evicting history without saving what was learned.
**Why it happens:** Compaction is treated as deletion.
**Instead:** Write decisions and open questions to memory first; then evict. Compaction is only safe when memory holds the conclusions.

## Files

- `scripts/context_analyzer.py`, `scripts/context_budget_planner.py`, `scripts/context_pruner.py`, `scripts/memory_indexer.py` — the tools above. They run on any files; the Quick Start uses this skill's own `references/` and `scripts/` as input.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/context-window-strategies.md](references/context-window-strategies.md)** — budget allocation, packing strategies, and window-optimization patterns. Read when planning budgets or optimizing a long conversation.
- **[references/memory-architecture-guide.md](references/memory-architecture-guide.md)** — three-layer memory model, promotion protocol, staleness detection, shared context bus + handoff protocol. Read when designing persistent memory or coordinating agents.
- **[references/code-retrieval-patterns.md](references/code-retrieval-patterns.md)** — file/chunk/dependency-aware retrieval, chunking/embedding guidance, knowledge-graph schema and queries. Read when building RAG for code.
- **[references/memory-and-context-editing.md](references/memory-and-context-editing.md)** — the memory-tool pattern (file-backed memory, what to store vs. recompute, retention, security) and context editing/compaction (eviction priority, summarize-and-replace, token-savings payoff) and how both weave into the agent loop. Read when persisting state across sessions or keeping a long loop from exhausting the window.
- **[references/long-context-strategies.md](references/long-context-strategies.md)** — long-context vs. RAG vs. hybrid decision-making, budget allocation across a 1M-token window, position/attention effects, and when a bigger window hurts (cost, latency, distraction). Read when choosing a window-vs-retrieval strategy.
- **[references/workflows-and-quality.md](references/workflows-and-quality.md)** — the three workflows, anti-patterns, evaluation metrics, troubleshooting, and success criteria. Read before running a workflow and before shipping.

## Scope & Limitations

Covers context budgeting, memory layering, compaction, code retrieval strategy and multi-agent context hand-off. Does not cover vector store or embedding infrastructure, agent role design or orchestration, monitoring, or prompt writing.

Related skills: `engineering/rag-architect` (vector stores, embeddings), `engineering/agent-designer` and `engineering/agent-workflow-designer` (agent roles, orchestration), `engineering/llm-cost-optimizer` (caching and token cost), `engineering/codebase-onboarding` (project summaries to bootstrap context).
