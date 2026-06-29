# Subagent Scoping & Lead→Specialist Orchestration

Read this when designing a **lead agent that delegates to specialist subagents** — each with its
own narrow toolset, focused instructions, and isolated context — rather than running all the work
inside a single conversational loop. This complements `orchestration-patterns.md` (the hierarchical
delegation pattern) with the *scoping* discipline that makes delegation pay off.

This file is deliberately model- and framework-agnostic. Where it says "tool allow-list" or "scoped
permissions" it means *the set of tools/actions you grant a given agent* — express it however your
runtime does (an allow-list, a permission profile, a registered toolset). Do not assume any specific
API field name.

## 1. When to split into subagents vs keep it in one loop

Splitting buys **context isolation** and **parallelism** at the cost of **coordination overhead** and
**handoff token tax**. Split when the gains exceed the tax.

**Split into subagents when:**
- The task has **independent sub-questions** that can run in parallel (e.g. research three vendors,
  audit four directories) — wall-clock latency drops roughly to the slowest branch.
- A subtask needs a **different, narrower toolset** than the rest (e.g. only the "writer" should touch
  the filesystem; only the "searcher" should hit the web). Scoping the toolset per role shrinks the
  blast radius of a misbehaving step.
- Intermediate work produces **large, throwaway context** (raw search dumps, full file contents) that
  would otherwise bloat the main loop's window. A subagent reads the bulk and returns only a summary.
- Subtasks have **different reliability or cost profiles** — a cheap narrow model is fine for
  extraction, a stronger model is reserved for synthesis (see `routing-and-cost.md` and the
  `multi_agent_cost_estimator.py` tool).

**Keep it in one loop when:**
- The steps are **tightly sequential and share most context** — splitting just re-serializes the same
  state across handoffs, paying the token tax twice.
- The whole job **fits comfortably in one context window** and finishes in a few turns.
- The task is **interactive / conversational** with the user — a single coherent agent is easier to
  steer than a tree.
- Coordination logic would be **more code than the work itself**. Two agents that always run in lockstep
  are one agent.

Rule of thumb: **the number of subagents should equal the number of genuinely independent
responsibilities, not the number of steps.** If two roles never run without each other and share a
toolset, merge them.

## 2. Scoping a single subagent

A well-scoped subagent is defined by four things. Under-specify any of them and the lead loses the
isolation it delegated for.

### a. Minimal tool allow-list
Grant only the tools the role needs to fulfill its contract — nothing more. A "summarizer" needs read
access to a shared scratch file and nothing else; it should not be able to call the web, write code, or
spawn further agents. Benefits:
- **Blast-radius containment** — a confused or prompt-injected subagent can only do what it was granted.
- **Cheaper, clearer reasoning** — fewer tools means a shorter system prompt and fewer wrong turns.
- **Auditability** — you can reason about what each role *could* have done from its allow-list alone.

Start from an empty allow-list and add the minimum; don't start from "all tools" and remove.

### b. Focused instructions
The subagent's instructions should describe **one job** and the **shape of its output**, not the whole
mission. Include: the single objective, the inputs it will receive, hard constraints (what it must not
do), and the exact return format. Omit everything about sibling roles and the lead's larger goal — that
context is noise that invites scope creep.

### c. Isolated context
Each subagent runs in its **own context window**, seeded only with what it needs: its instructions plus
the specific inputs the lead hands it. It does **not** inherit the lead's full transcript or its siblings'
working memory. This is the core efficiency win — the lead's window stays small because the heavy,
disposable context lives and dies inside the subagent.

### d. Clear return contract
Define what the subagent returns **before** you spawn it: a typed result, a fixed-key JSON object, a
bounded summary ("≤ 200 words, with citations"), or a path to an artifact it wrote. The contract is the
*only* thing that crosses back into the lead's context, so make it small and structured. A subagent that
returns its entire reasoning transcript defeats context isolation — it re-bloats the parent. Treat the
return value like a function signature: the lead depends on its shape, not on how it was produced.

## 3. The lead → parallel specialists → merge pattern

The canonical shape for this skill:

```
                 ┌─────────────────────────────┐
                 │  LEAD / ORCHESTRATOR         │
                 │  (stronger model)            │
                 │  - decomposes the task       │
                 │  - assigns scoped subagents  │
                 │  - merges results            │
                 └──────────────┬──────────────┘
            spawn (scoped) ┌────┼────┐ spawn (scoped)
                           ▼    ▼    ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ Spec. A  │ │ Spec. B  │ │ Spec. C  │   each:
              │ tools:[x]│ │ tools:[y]│ │ tools:[z]│   - own context
              │ cheap mdl│ │ cheap mdl│ │ cheap mdl│   - own toolset
              └────┬─────┘ └────┬─────┘ └────┬─────┘   - returns contract
                   │ return     │ return     │ return
                   └────────────┼────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │ SHARED WORKSPACE         │
                    │ (scratch files / state)  │
                    └─────────────────────────┘
```

**Decompose (lead).** The lead, on a stronger model, reads the goal and produces a set of independent
work items, each with: an objective, the inputs, the tool allow-list, and the return contract. It does
not do the specialist work itself.

**Fan out (specialists).** Each specialist runs in parallel in its own isolated context on a cheaper,
narrower model. It uses only its granted tools and writes bulky intermediate output to a **shared
workspace** (a scratch directory, a state store, a branch) rather than streaming it back through the
lead.

**Shared workspace, not shared chat.** Specialists coordinate through artifacts in the workspace, not by
seeing each other's transcripts. Give each role a **disjoint write area** (its own file or key prefix) so
parallel writers never collide; reads can be shared. This is the multi-agent analogue of avoiding shared
mutable state across threads.

**Merge (lead).** Each specialist returns only its small contract (a summary + a pointer to its artifact).
The lead assembles these into the final answer, resolving conflicts. Because only contracts cross back,
the lead's context stays an order of magnitude smaller than the sum of the work it supervised.

When merging conflicting results, prefer an explicit rule (most-recent, highest-confidence, or a
consensus check — see the consensus validation pattern in `orchestration-patterns.md`) over letting the
lead silently pick.

## 4. Failure isolation & retries

The point of isolation is that **one subagent failing should not corrupt the others or the lead.**

- **Contain failures at the boundary.** A subagent that errors, times out, or returns an off-contract
  result fails *only its branch*. The lead treats a missing/invalid contract as a recoverable gap, not a
  crash. Validate every returned contract before merging — never trust shape.
- **Retry the branch, not the world.** Re-run the failed subagent with the same scoped inputs (it is
  isolated, so a retry is clean) rather than restarting the whole fan-out. Cap attempts and add backoff;
  see the circuit-breaker and retry patterns in `reliability-and-troubleshooting.md`.
- **Idempotent writes.** Because specialists write to a shared workspace, a retried branch must overwrite
  its own disjoint area deterministically, not append — otherwise a retry doubles its output.
- **Degrade gracefully.** Decide up front whether the lead can finish with a partial set (e.g. 4 of 5
  research branches returned) or must have all branches. Make the lead's merge step explicit about which
  branches are required vs best-effort.
- **Budget a timeout per branch.** A hung subagent must not stall the merge. Enforce a per-branch
  timeout so the lead can proceed (or retry) on the slow one.

## 5. Cost & latency tradeoffs: multi-agent vs single-agent

Multi-agent is not automatically cheaper or faster. Reason about both axes explicitly.

**Where multi-agent wins:**
- **Latency** on independent work — parallel branches collapse to ~the slowest branch instead of the sum.
- **Cost** when narrow subtasks run on **cheaper models** while only the lead pays for a strong model. A
  fan-out of five extraction tasks on an economy tier with one frontier-tier merge is far cheaper than
  doing all six steps on the frontier tier.
- **Context economy** — isolated windows mean no single agent carries the whole task's tokens, avoiding
  context-window limits and the quadratic re-reading cost of one ever-growing transcript.

**Where multi-agent loses:**
- **Handoff token tax** — every spawn re-sends instructions and inputs; every return re-injects a
  contract. For small tasks this overhead can exceed the work itself.
- **Orchestration cost** — the lead spends tokens decomposing and merging. With many tiny subagents the
  coordination tokens dominate.
- **Reasoning effort scales cost super-linearly.** A subagent told to "think hard" (high reasoning
  effort) emits far more output/thinking tokens than a quick extractor. Match effort to the job: low
  effort for mechanical extraction/formatting, reserve high effort (and the strong model) for the lead's
  synthesis and any genuinely hard branch. Mixing effort per role is a primary lever — model it.

**A practical heuristic:** estimate both topologies before committing. Run
`scripts/multi_agent_cost_estimator.py` with your per-role tiers, call counts, token sizes, and reasoning
effort to compare the multi-agent design against a single-strong-agent baseline. If the multi-agent
design isn't meaningfully cheaper *and* the latency win is small, the single loop is the simpler, more
reliable choice.

| Lever | Effect on cost | Effect on latency | When to pull |
|-------|----------------|-------------------|--------------|
| Move narrow subagents to a cheaper tier | Large reduction | None | Mechanical extraction/formatting/classification |
| Keep only the lead on a strong tier | Large reduction | None | Synthesis/judgment lives in the lead |
| Increase parallel branches | Roughly linear increase | Decrease (to slowest branch) | Independent subtasks, latency-bound |
| Raise a branch's reasoning effort | Increase (super-linear) | Increase | Only for genuinely hard branches |
| Merge two always-coupled subagents | Removes one handoff tax | Slight decrease | Roles that never run independently |
| Tighten return contracts (smaller summaries) | Reduces merge-side input | None | Lead context is the bottleneck |
