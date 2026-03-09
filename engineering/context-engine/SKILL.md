---
name: context-engine
description: Context management engine for AI coding agents. Handles context window optimization, persistent memory across sessions, context retrieval strategies, token budget allocation, and knowledge graph construction from codebases. Use when building agent memory systems, optimizing context windows, designing RAG pipelines for code, or managing multi-session agent state.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-agents
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: context-window-optimization, memory-architecture, knowledge-graphs
---

# Context Engine - AI Agent Context Management

**Tier:** POWERFUL
**Category:** Engineering
**Tags:** context management, AI agents, memory systems, RAG, token optimization, knowledge graphs

## Overview

Context Engine provides production-grade patterns for managing what AI agents know, remember, and retrieve. It covers the full lifecycle: ingestion of project knowledge, optimal packing of context windows, persistent memory across sessions, and retrieval-augmented generation for large codebases. The difference between a useful agent and a hallucinating one is context management.

## Core Capabilities

### 1. Context Window Architecture

Every AI agent operates within a finite context window. Mismanaging it is the #1 cause of degraded agent performance.

#### Token Budget Allocation Framework

| Segment | Budget % | Purpose | Priority |
|---------|----------|---------|----------|
| System Instructions | 5-10% | Agent identity, rules, constraints | Fixed (always loaded) |
| Task Context | 20-30% | Current task description, requirements | High (per-request) |
| Relevant Code | 25-40% | Source files, dependencies, types | Dynamic (retrieved) |
| Conversation History | 10-20% | Prior turns, decisions made | Sliding window |
| Tool Results | 5-15% | Command output, search results | Ephemeral |
| Reserved Buffer | 5-10% | Output generation headroom | Protected |

#### Context Packing Strategies

**Greedy Relevance Packing**
```
1. Score all candidate context by relevance to current task
2. Sort by score descending
3. Pack until budget exhausted
4. Always reserve output buffer
```
- Pros: Simple, fast, works well for focused tasks
- Cons: Misses cross-cutting context, no diversity

**Tiered Loading**
```
Tier 0 (always loaded): System prompt, project rules, active file
Tier 1 (task-specific):  Related files, type definitions, tests
Tier 2 (on-demand):      Documentation, examples, history
Tier 3 (retrieved):      Search results, RAG chunks
```
- Pros: Predictable, debuggable, respects fixed costs
- Cons: Requires upfront tier classification

**Adaptive Compression**
```
1. Load full context for first pass
2. Identify low-signal sections (boilerplate, repetitive code)
3. Summarize or truncate low-signal sections
4. Re-pack with compressed context
5. Preserve high-signal sections verbatim
```
- Pros: Maximizes information density
- Cons: Risk of losing important details in compression

### 2. Memory Architecture

#### Three-Layer Memory Model

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Working Memory (Context Window)        │
│  Scope: Current conversation/task                │
│  Lifetime: Single session                        │
│  Storage: In-context tokens                      │
│  Update: Every turn                              │
├─────────────────────────────────────────────────┤
│  Layer 2: Session Memory (Persistent Store)      │
│  Scope: Project-level learnings                  │
│  Lifetime: Across sessions                       │
│  Storage: MEMORY.md, .claude/rules/, CLAUDE.md   │
│  Update: End of session or on discovery          │
├─────────────────────────────────────────────────┤
│  Layer 3: Knowledge Base (Indexed Corpus)        │
│  Scope: Full codebase + documentation            │
│  Lifetime: Persistent, versioned                 │
│  Storage: Vector store, graph DB, file index     │
│  Update: On commit / scheduled reindex           │
└─────────────────────────────────────────────────┘
```

#### Memory Promotion Protocol

Knowledge flows upward through layers based on recurrence and value:

| Signal | Action | Example |
|--------|--------|---------|
| Pattern seen 1x | Working memory only | "This file uses tabs" |
| Pattern seen 2-3x | Candidate for session memory | "Project uses pnpm everywhere" |
| Pattern confirmed across sessions | Promote to CLAUDE.md/rules | "Always use pnpm, never npm" |
| Pattern is domain knowledge | Add to knowledge base | "Auth flow uses JWT + refresh tokens" |

#### Staleness Detection

Context has a shelf life. Stale context causes hallucinations.

```
Freshness Score = f(last_verified, change_frequency, confidence)

Fresh   (< 7 days, file unchanged):  Use directly
Aging   (7-30 days, file changed):   Re-verify before using
Stale   (> 30 days):                 Flag, re-retrieve, or discard
Unknown (never verified):            Treat as low-confidence
```

### 3. Retrieval Strategies for Code

#### File-Level Retrieval

Best for: navigating to the right file when the agent knows what it needs.

```
Query: "authentication middleware"
Strategy:
  1. Filename pattern match: *auth*, *middleware*
  2. Import graph: files that import auth modules
  3. Symbol search: exported functions matching auth*
  4. Content search: files containing auth-related patterns
  5. Rank by: recency of edit + import centrality + name match
```

#### Chunk-Level Retrieval (RAG for Code)

Best for: finding specific implementations within large files.

**Chunking Strategy for Source Code:**
- Chunk by function/class boundaries (never mid-function)
- Include the function signature + docstring + body as one chunk
- Attach metadata: file path, language, exports, imports
- Overlap: include 2 lines above/below for context
- Max chunk size: 200 lines (larger functions get sub-chunked by logical block)

**Embedding Considerations:**
- Code-specific embeddings (CodeBERT, StarCoder embeddings) outperform general text embeddings by 15-30% on code retrieval tasks
- Hybrid search (keyword + semantic) outperforms either alone
- Index function signatures separately for fast symbol lookup

#### Dependency-Aware Retrieval

When retrieving a function, also retrieve:
1. Its type definitions (interfaces, types it uses)
2. Its direct dependencies (imported functions it calls)
3. Its tests (to understand expected behavior)
4. Its callers (to understand usage context)

This "context neighborhood" approach prevents the agent from seeing a function in isolation.

### 4. Knowledge Graph Construction

#### Codebase Graph Schema

```
Nodes:
  - File (path, language, size, last_modified)
  - Function (name, signature, docstring, complexity)
  - Class (name, methods, properties, inheritance)
  - Module (name, exports, dependencies)
  - Test (name, covers, assertions)
  - Config (type, values, affects)

Edges:
  - IMPORTS (File → File)
  - CALLS (Function → Function)
  - IMPLEMENTS (Class → Interface)
  - TESTS (Test → Function)
  - CONFIGURES (Config → Module)
  - DEPENDS_ON (Module → Module)
```

#### Graph Queries for Context

| Agent Question | Graph Query | Context Retrieved |
|---------------|-------------|-------------------|
| "How does auth work?" | Subgraph around auth module, 2 hops | Auth files + dependencies + tests |
| "What breaks if I change X?" | Reverse dependency traversal from X | All callers + their tests |
| "What's the API surface?" | All exported functions from API modules | Route handlers + types + middleware |
| "How is this tested?" | TEST edges from target function | Test files + fixtures + mocks |

### 5. Context Window Optimization Patterns

#### Pattern: Sliding Window with Anchors

For long conversations, maintain fixed "anchor" messages while sliding recent history.

```
[System Prompt]           ← Fixed anchor (never evicted)
[Task Definition]         ← Fixed anchor
[Key Decision #1]         ← Pinned (user marked as important)
[Key Decision #2]         ← Pinned
...
[Turn N-4]                ← Sliding window starts here
[Turn N-3]
[Turn N-2]
[Turn N-1]
[Current Turn]
[Output Buffer]           ← Reserved
```

#### Pattern: Progressive Summarization

When conversation exceeds budget:
1. Summarize oldest turns into a "conversation summary" block
2. Keep the summary as a single anchor message
3. Update summary every N turns
4. Always keep: first system message, task definition, last 5 turns

#### Pattern: Selective Tool Result Caching

Tool outputs (file reads, search results, command output) consume the most tokens.

```
Strategy:
  - Cache tool results keyed by (tool, args, file_hash)
  - On re-request: serve from cache (0 new tokens)
  - On file change: invalidate cache for that file
  - Always truncate: command output > 200 lines → first 50 + last 50
  - Never cache: error output (always show in full)
```

### 6. Multi-Agent Context Sharing

When multiple agents collaborate, context synchronization becomes critical.

#### Shared Context Bus

```
┌──────────┐     ┌──────────────────┐     ┌──────────┐
│ Agent A   │────▶│  Shared Context   │◀────│ Agent B   │
│ (Planner) │     │  - Task state     │     │ (Coder)   │
└──────────┘     │  - Decisions log  │     └──────────┘
                  │  - File changes   │
┌──────────┐     │  - Constraints    │     ┌──────────┐
│ Agent C   │────▶│  - Artifacts      │◀────│ Agent D   │
│ (Reviewer)│     └──────────────────┘     │ (Tester)  │
└──────────┘                               └──────────┘
```

#### Context Handoff Protocol

When Agent A passes work to Agent B:
1. **State Summary**: What was done, decisions made, current state
2. **Relevant Artifacts**: Files created/modified, with paths
3. **Constraints**: What must not be changed, invariants
4. **Open Questions**: Unresolved decisions that need Agent B's input
5. **Next Steps**: Explicit instructions for what Agent B should do

Anti-pattern: Passing the entire conversation history. Always summarize.

## Workflows

### Workflow 1: Bootstrap Agent Context for a New Codebase

```
Step 1: Index the codebase
  - Build file tree with metadata (language, size, last modified)
  - Extract all exports, imports, and dependency edges
  - Identify entry points (main files, route handlers, CLI commands)

Step 2: Construct initial knowledge graph
  - Map module dependencies
  - Identify architectural layers (API, service, data, config)
  - Detect frameworks and conventions (naming, structure, patterns)

Step 3: Generate project summary
  - One paragraph: what this project does
  - Architecture diagram (text-based)
  - Key directories and their roles
  - Critical files (config, entry points, shared types)

Step 4: Configure context tiers
  - Tier 0: Project summary, CLAUDE.md, active file
  - Tier 1: Related files within same module
  - Tier 2: Cross-module dependencies
  - Tier 3: Documentation and examples
```

### Workflow 2: Optimize Context for a Specific Task

```
Step 1: Parse task requirements
  - Extract entities (files, functions, features mentioned)
  - Identify task type (bug fix, feature, refactor, review)

Step 2: Retrieve relevant context
  - File-level: files matching entities
  - Dependency-level: imports/exports of matched files
  - Test-level: tests covering matched code
  - History-level: recent changes to matched files

Step 3: Budget allocation
  - Calculate total tokens available
  - Allocate per tier (see Token Budget Framework)
  - Pack context with greedy relevance

Step 4: Verify coverage
  - Check: all mentioned files included?
  - Check: type definitions for used types included?
  - Check: test examples for expected behavior included?
  - If gaps: retrieve missing context from lower tiers
```

### Workflow 3: Session Memory Management

```
Step 1: During session - capture learnings
  - New patterns discovered: log to working memory
  - Corrections received: mark as high-confidence learning
  - Errors encountered: log with resolution

Step 2: End of session - evaluate learnings
  - Which learnings are project-specific vs session-specific?
  - Which patterns recurred during this session?
  - Which corrections should become rules?

Step 3: Promote valuable learnings
  - Recurring patterns → CLAUDE.md or .claude/rules/
  - Project conventions → project documentation
  - Error resolutions → knowledge base

Step 4: Prune stale memory
  - Remove learnings about deleted files
  - Update learnings contradicted by new information
  - Archive session-specific context
```

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| Dumping entire files into context | Wastes tokens on irrelevant code | Retrieve specific functions/sections |
| No output buffer reservation | Agent output gets truncated | Always reserve 10-15% for output |
| Static context loading | Same context regardless of task | Dynamic retrieval based on task type |
| No staleness tracking | Using outdated information | Timestamp and verify before using |
| Full conversation replay | Older turns crowd out relevant code | Sliding window with summarization |
| Ignoring import graph | Missing type definitions, broken understanding | Always include direct dependencies |

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Context Relevance | % of loaded context actually used in response | > 70% |
| Retrieval Precision | % of retrieved items that are relevant | > 80% |
| Token Utilization | % of context budget used productively | > 85% |
| Staleness Rate | % of context items that are outdated | < 5% |
| Cache Hit Rate | % of tool results served from cache | > 40% |
| Handoff Completeness | % of required context passed between agents | 100% |

## Integration Points

| Skill | Integration |
|-------|-------------|
| **rag-architect** | Use RAG Architect for vector store design; Context Engine for retrieval strategy |
| **agent-designer** | Agent Designer defines agent roles; Context Engine manages what each agent knows |
| **self-improving-agent** | Self-Improving Agent promotes learnings; Context Engine decides when/how to load them |
| **observability-designer** | Monitor context utilization metrics alongside agent performance |

## References

- `references/context-window-strategies.md` - Detailed packing algorithms and benchmarks
- `references/code-retrieval-patterns.md` - RAG for code: chunking, embedding, and ranking strategies
- `references/memory-architecture-guide.md` - Multi-layer memory system design patterns
