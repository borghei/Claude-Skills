# Memory Tool & Context Editing

Read this when an agent needs to persist state across sessions outside its context window, or when a long-running loop is exhausting the window and stale content must be pruned or compressed. These two techniques are complementary: the memory tool moves state *out* of the window; context editing reclaims space *inside* it.

## The Memory-Tool Pattern (File-Backed Memory)

The context window is volatile working memory — it disappears when the session ends and shrinks under pressure. A **memory tool** gives the agent a durable store it can read, write, and edit on its own, typically backed by files in a dedicated directory. The agent treats it like a notebook: it writes down what it learns, and reads it back at the start of (or partway through) a later session.

This is the file-backed realization of Layer 2 (Session Memory) in the three-layer model — see `memory-architecture-guide.md`. The difference here is operational: the agent itself decides what to record and when, as a tool call, rather than a human curating `CLAUDE.md`.

### What to store vs. recompute

Persist only what is **expensive to derive and stable enough to reuse**. Recompute anything cheap or volatile.

| Store in memory | Recompute each session |
|-----------------|------------------------|
| Durable decisions and their rationale ("we chose JWT + refresh because…") | Current file contents (always re-read — files change) |
| Project conventions confirmed across sessions ("uses pnpm, never npm") | Token counts, line numbers, search results |
| Hard-won facts that took many tool calls to establish | Anything derivable in one cheap tool call |
| Task progress / a running plan for a multi-session job | The full transcript of how a conclusion was reached |
| User preferences and standing constraints | Ephemeral tool output (command stdout, diffs) |

Rule of thumb: store **conclusions, not transcripts**. If re-deriving a fact costs more than a couple of tool calls and the fact rarely changes, write it down. Otherwise leave it out — stale stored data is worse than no data.

### Structure and retention

- **One concern per file.** `decisions.md`, `conventions.md`, `progress.md` beat a single growing blob. Targeted files let the agent read back only what's relevant and keep memory reads cheap.
- **Write the *why*, not just the *what*.** A decision without its rationale gets re-litigated; a decision with rationale gets respected.
- **Timestamp and source every entry.** Memory inherits the staleness problem from working context. Pair each entry with a `last_verified` marker so the freshness scoring in `memory-architecture-guide.md` applies to persisted memory too.
- **Expire on a schedule.** On read, re-verify aging entries against the live codebase; discard entries that contradict current files. Memory that is never pruned drifts into a confident liar.
- **Cap the size.** Memory should be an index of conclusions, not an archive. If a memory file is too large to load cheaply, it has become a second context-window problem — summarize and trim it.

### Security of persisted memory

Persisted memory is an untrusted, durable input that gets loaded straight into context — treat it as an attack surface.

- **Path-confine all reads/writes** to the memory directory; reject `..`, absolute paths, and symlinks that escape it. A memory tool that can write anywhere is an arbitrary-file-write primitive.
- **Never store secrets** (tokens, keys, credentials, PII) in plain memory files. They outlive the session and may sync to disk or a repo.
- **Treat memory content as data, not instructions.** A poisoned memory file can carry injected directives ("ignore prior rules and…"). Don't let memory silently override system instructions; keep authority with the system prompt.
- **Scope memory per project/tenant.** One project's memory must not leak into another's session.
- **Make memory writes auditable.** Log what the agent persisted so a poisoned or wrong entry can be traced and removed.

## Context Editing / Compaction

Even with memory offloaded, a long agent loop accumulates turns and tool results until the window is exhausted and quality collapses. **Context editing** is the active management of the live window: pruning or compressing material the agent no longer needs so the loop can continue. Compaction is the heavier form — summarizing a swath of history and replacing it with a compact digest.

### What to evict first (eviction priority)

Evict lowest-value, highest-cost material first. Tool results are almost always the biggest, stalest consumers — see "Selective Tool Result Caching" in `context-window-strategies.md`.

1. **Stale tool outputs** — old file reads, search results, and command stdout that have since been superseded by newer reads or by changes on disk. These dominate token usage and age fastest.
2. **Superseded plans and intermediate reasoning** — earlier drafts of a plan once a newer plan replaces them; scratch work whose conclusion is already captured.
3. **Resolved sub-tasks** — full back-and-forth of a sub-task that is done; replace with a one-line outcome.
4. **Verbose duplicates** — the same file or error shown multiple times; keep the latest, drop the rest.
5. **Old conversational turns** — the oldest dialogue, once summarized.

### Never evict (decision-relevant core)

- System instructions and standing constraints.
- The current task definition and active acceptance criteria.
- Pinned decisions and invariants ("must not change the public API").
- The most recent few turns (the agent's immediate working set).
- Unresolved open questions.

These map to the fixed "anchors" in the sliding-window pattern. Compaction slides the *history*; it must not touch the anchors.

### Summarize-and-replace

The core compaction move: take a contiguous block of low-value history, summarize it into a dense digest, and replace the block with the digest.

```
Before:  [turns 1-20: 18k tokens of exploration, reads, dead ends]
After:   [SUMMARY: explored auth module; chose JWT+refresh;
          ruled out session cookies (CSRF); files touched: a.ts, b.ts]  (~300 tokens)
```

Principles:
- **Preserve decision-relevant info verbatim or in the summary** — every decision, constraint, and open question in the evicted block must survive into the digest. Losing those causes the agent to re-litigate or contradict itself.
- **Keep decisions prominent.** Put surviving decisions and constraints at the top of the digest where attention is strongest (see `long-context-strategies.md` on position effects), not buried in prose.
- **Compress, don't paraphrase away facts.** Drop the *narration* of how a fact was found; keep the fact.
- **Offload before you evict, when durable.** If the material being evicted contains a durable conclusion, write it to the memory tool *first* — context editing reclaims the window, memory keeps the knowledge.

### The token-savings payoff

The economics are why this matters in a loop:

- **Continuation:** without eviction a long loop hits the ceiling and stalls. Compaction lets it run indefinitely.
- **Cost and latency:** every turn re-sends the whole window. Pruning 18k stale tokens saves those tokens on *every subsequent turn*, not just once — the savings compound over a long run.
- **Quality:** a window stuffed with stale tool output buries the signal. Removing it raises the relevant-token ratio and reduces distraction (see "when bigger context hurts" in `long-context-strategies.md`).
- **Cache awareness:** editing the middle of the window can invalidate a prefix cache. Prefer evicting in larger, less frequent batches over constant small edits, and evict from the older/middle region while leaving the stable prefix intact.

## How These Interact With the Agent Loop

A robust loop weaves both techniques into the cycle rather than waiting for a hard failure:

```
each turn:
  1. (start of session) read relevant memory files → seed working context
  2. act: reason + call tools
  3. record: write durable conclusions/decisions to memory as they emerge
  4. monitor window utilization
  5. when utilization crosses a high-water mark (not at the ceiling):
        a. offload any durable, not-yet-saved conclusions to memory
        b. evict stale tool outputs and superseded plans
        c. summarize-and-replace oldest history; keep anchors
  6. continue with reclaimed space
```

Key interactions:
- **Memory makes compaction safe.** You can aggressively evict history only because the durable conclusions were already written to memory. Compact without offloading and you lose knowledge.
- **Compact early, not at the cliff.** Trigger on a high-water mark so there's room to do the summarization itself. Compacting at 100% leaves no headroom to think.
- **Memory + compaction enable multi-session work.** Offload at session end, compact within session, reload at session start — the same long task survives across many windows.
- **Both are governed by the same budget.** The `context_budget_planner.py` tool models memory and reserved-output as explicit line items and flags when compaction is needed — run it to decide *how much* to evict, not just *that* you should.
