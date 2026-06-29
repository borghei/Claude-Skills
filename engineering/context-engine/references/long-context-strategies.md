# Long-Context (1M-Token) Strategies

Read this when deciding whether to use a very large context window (hundreds of thousands to ~1M tokens) versus retrieval, how to allocate a big budget, and why a bigger window is not automatically a better one.

## Long-Context vs. RAG vs. Hybrid

A large window and retrieval (RAG) solve the same problem — *get the right information in front of the model* — with opposite trade-offs. Long-context **loads broadly and reasons across everything at once**; RAG **fetches narrowly and reasons over a small set**. The choice is an engineering decision, not a default.

| Dimension | Long-context (load it all) | RAG / agent-loop retrieval |
|-----------|----------------------------|----------------------------|
| Best when | Corpus is small-to-moderate and *bounded*; the task needs cross-document synthesis | Corpus is large or unbounded; each query needs a small, identifiable slice |
| Freshness | Snapshot at load time; re-load to refresh | Fetch live each query; naturally fresh |
| Cost per query | High and flat — you pay for the whole window every turn | Low — you pay only for retrieved chunks |
| Latency | Grows with window size | Retrieval overhead, but a smaller prompt |
| Recall | Total within the window; nothing missed *that was loaded* | Bounded by retrieval quality; a bad query misses relevant content |
| Failure mode | Distraction, "lost in the middle", high bill | Missed/irrelevant chunks, fragmented context |

**Decision heuristics:**

- **Whole artifact, deep reasoning → long-context.** Reviewing one large repo, a long spec, or a contract end-to-end where any part may bear on any other. Chunking would sever the cross-references the task depends on.
- **Huge or growing knowledge base, pinpoint queries → RAG.** Company-wide docs, an entire monorepo, anything that won't fit or changes constantly. Retrieve the relevant slice per query.
- **Most real agent systems → hybrid.** Use RAG (and an agent loop) to *select* the right large chunks, then load those into a generous window for deep reasoning. Retrieval handles "which 200k of the 50M tokens," long-context handles "reason hard over those 200k." The agent loop adds iterative retrieval — read, decide, retrieve more — instead of one-shot packing.

A practical default: reach for RAG first when the corpus clearly exceeds the window or updates frequently; reach for long-context when the relevant material is bounded and tightly interconnected; combine them when the corpus is large but each task touches a coherent, sizable region.

## Budget Allocation Across a Big Window

A 1M-token window is a bigger pool, not a free one — the allocation discipline from `context-window-strategies.md` still applies; the absolute numbers just scale. Two things change at scale:

- **Reserve output headroom in absolute terms, not just percent.** A 5% buffer of 1M is 50k tokens — usually far more than any single response needs. Pin the output reserve to the actual expected output size and reclaim the rest for input rather than letting a percentage rule waste 40k tokens.
- **Spend the surplus on breadth, not filler.** The win of a big window is loading *more distinct, relevant* material (more files, more of the dependency graph, more history) — not loading the same thing padded. Every token still costs money and attention; loading low-signal content to "use the space" is pure waste.

A sane large-window allocation keeps fixed costs small, gives the bulk to retrieved/loaded source material, holds a right-sized output reserve, and leaves slack for the agent loop to retrieve more mid-task. Use `context_budget_planner.py` to lay out the line items and catch overflow before it happens.

## Position & Attention Considerations

Attention is not uniform across a long window. Two well-documented effects shape *where* you put things:

- **Lost in the middle.** Models attend most strongly to the **beginning and end** of the context and weakest to the middle. Information buried mid-window can be effectively ignored even when it's present.
- **Recency and primacy.** The system prompt/task at the very start and the most recent turns at the very end carry disproportionate weight.

Placement guidance:
- Put the **task, key instructions, and decision-relevant constraints at the start or end** — never only in the middle of a huge dump.
- For a critical fact inside a large corpus, **restate it near the query** (end of the window) rather than relying on the model to find it deep in the body.
- **Order retrieved chunks by relevance toward the edges**, lowest-signal toward the middle, when you control ordering.
- **Re-anchor after compaction.** When you summarize-and-replace (see `memory-and-context-editing.md`), keep surviving decisions at the top of the digest so they land in a high-attention zone.

## When Bigger Context Hurts

Filling a large window is often the wrong move even when it fits. A bigger window adds cost and risk that must be justified by the task.

- **Cost.** You pay for every input token on **every turn**. A near-full 1M window re-sent across a long loop is the single largest driver of an agent's bill. Load only what the task needs.
- **Latency.** Time-to-first-token and per-turn latency grow with prompt size. A window stuffed "just in case" makes every turn slower for the user.
- **Distraction / signal dilution.** More irrelevant tokens lower the relevant-token ratio. Models can be pulled toward plausible-but-off-task content; a focused 50k window often **outperforms** a padded 500k one on a narrow task. Precision beats volume.
- **Diminishing and negative returns.** Beyond the material the task actually needs, added context yields little and can degrade accuracy (the middle gets ignored, contradictions creep in). The goal is the *right* tokens, not the *most* tokens.
- **Debuggability.** A 5k focused prompt is inspectable when something goes wrong; a 900k prompt is nearly impossible to reason about. Smaller windows fail more legibly.

Bottom line: treat a large window as **capacity to be spent deliberately**, the same as any budget. Load broadly only when the task genuinely requires cross-cutting synthesis; otherwise retrieve narrowly, keep the window tight, and use the compaction and memory techniques to stay lean as the loop runs.
