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
  updated: 2026-06-29
  frameworks: context-window-optimization, memory-architecture, knowledge-graphs
---
# Context Engine - AI Agent Context Management

Context Engine provides production-grade patterns for managing what AI agents know, remember, and retrieve. It covers the full lifecycle: ingestion of project knowledge, optimal packing of context windows, persistent memory across sessions, and retrieval-augmented generation for large codebases. The difference between a useful agent and a hallucinating one is context management.

## Core Capabilities

- **Context window architecture** — token budget allocation plus greedy, tiered, and adaptive-compression packing strategies.
- **Memory architecture** — three-layer model (working / session / knowledge base), promotion protocol, and staleness detection.
- **Code retrieval** — file-level, chunk-level (RAG), and dependency-aware retrieval with code chunking and embedding guidance.
- **Knowledge graph construction** — codebase graph schema (nodes + edges) and graph queries that resolve agent questions.
- **Window optimization patterns** — sliding window with anchors, progressive summarization, selective tool-result caching.
- **Memory tool & context editing** — file-backed persistent memory across sessions, plus context compaction (evict stale tool outputs, summarize-and-replace history) to keep a long loop from exhausting the window.
- **Long-context strategies** — when to use a 1M-token window vs. RAG vs. a hybrid agent loop, budget allocation across a big window, and position/attention effects.
- **Multi-agent context sharing** — shared context bus and a five-element handoff protocol.

## When to Use

- Bootstrapping agent context for a new codebase (index → graph → summary → tiers).
- Optimizing context for a specific task (bug fix, feature, refactor, review).
- Capturing, promoting, and pruning session memory across sessions.
- Designing a RAG pipeline for code retrieval.
- Coordinating context across multiple collaborating agents.

## Clarify First

Before designing or analyzing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which task** — bootstrap context for a codebase, optimize for a specific task, design persistent memory, or build a code RAG (selects the analyzer/pruner/indexer and the playbook)
- [ ] **Token budget** — the context-window ceiling (sets `--budget` and which packing strategy applies)
- [ ] **Source content** — the files/codebase or knowledge base to index (the input the scripts process)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `context_analyzer.py` | Analyze files/prompts for token usage, relevance, and optimization suggestions | `python scripts/context_analyzer.py src/ --budget 128000 --json` |
| `context_pruner.py` | Prune low-relevance content, redundancy, and verbose patterns from context | `python scripts/context_pruner.py src/main.py --aggressive --json` |
| `memory_indexer.py` | Index and search a memory/knowledge base with TF-IDF relevance scoring | `python scripts/memory_indexer.py docs/ --query 'auth middleware' --top 5` |
| `context_budget_planner.py` | Allocate a window across components, flag overflow, and suggest what to compact/evict first | `python scripts/context_budget_planner.py --window-size 200000 --system 4000 --history 60000 --tools 90000 --rag 40000 --reserve-output 8000` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/context-window-strategies.md](references/context-window-strategies.md)** — budget allocation, packing strategies, and window-optimization patterns. Read when planning budgets or optimizing a long conversation.
- **[references/memory-architecture-guide.md](references/memory-architecture-guide.md)** — three-layer memory model, promotion protocol, staleness detection, shared context bus + handoff protocol. Read when designing persistent memory or coordinating agents.
- **[references/code-retrieval-patterns.md](references/code-retrieval-patterns.md)** — file/chunk/dependency-aware retrieval, chunking/embedding guidance, knowledge-graph schema and queries. Read when building RAG for code.
- **[references/memory-and-context-editing.md](references/memory-and-context-editing.md)** — the memory-tool pattern (file-backed memory, what to store vs. recompute, retention, security) and context editing/compaction (eviction priority, summarize-and-replace, token-savings payoff) and how both weave into the agent loop. Read when persisting state across sessions or keeping a long loop from exhausting the window.
- **[references/long-context-strategies.md](references/long-context-strategies.md)** — long-context vs. RAG vs. hybrid decision-making, budget allocation across a 1M-token window, position/attention effects, and when a bigger window hurts (cost, latency, distraction). Read when choosing a window-vs-retrieval strategy.
- **[references/workflows-and-quality.md](references/workflows-and-quality.md)** — the three workflows, anti-patterns, evaluation metrics, troubleshooting, and success criteria. Read before running a workflow and before shipping.

## Scope & Limitations

**This skill covers:**
- Context window token budget planning, allocation strategies, and packing algorithms for AI coding agents.
- Multi-layer memory architecture design (working memory, session memory, knowledge base) with promotion and staleness protocols.
- Code-specific retrieval strategies including file-level, chunk-level, and dependency-aware retrieval for RAG pipelines.
- Knowledge graph construction from codebases and graph-based context queries for agent workflows.

**This skill does NOT cover:**
- Vector store infrastructure setup, embedding model selection, or database deployment — see **rag-architect** for vector store design and embedding strategies.
- Agent role definition, personality design, or multi-agent orchestration logic — see **agent-designer** for agent architecture and **agent-workflow-designer** for orchestration patterns.
- Runtime observability, metrics dashboards, or alerting for agent systems — see **observability-designer** for monitoring and instrumentation.
- Prompt engineering techniques, chain-of-thought design, or instruction tuning — see **prompt-engineer-toolkit** for prompt construction patterns.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **rag-architect** | Context Engine defines retrieval strategies; RAG Architect implements the vector store and embedding pipeline | Retrieval queries flow from Context Engine to RAG Architect's indexed store; ranked results flow back as context chunks |
| **agent-designer** | Agent Designer defines agent roles and capabilities; Context Engine manages per-agent context budgets and memory layers | Agent specifications define context requirements; Context Engine returns tailored context windows per agent role |
| **self-improving-agent** | Self-Improving Agent identifies recurring patterns and corrections; Context Engine decides when to promote learnings to persistent memory | Candidate learnings flow from Self-Improving Agent; promotion decisions and memory updates flow back through Context Engine's staleness and promotion protocols |
| **observability-designer** | Observability Designer instruments context utilization metrics (relevance, staleness, cache hits); Context Engine exposes metric endpoints | Raw metric events flow from Context Engine; Observability Designer aggregates into dashboards and alerts |
| **agent-workflow-designer** | Agent Workflow Designer defines multi-agent handoff sequences; Context Engine implements the shared context bus and handoff protocol | Workflow definitions specify which agents share context; Context Engine manages the context bus, serialization, and handoff payloads |
| **codebase-onboarding** | Codebase Onboarding generates project summaries and architecture maps; Context Engine consumes these as Tier 0 bootstrap context | Onboarding artifacts (project summary, directory map, entry points) feed into Context Engine's initial knowledge graph and context tiers |
