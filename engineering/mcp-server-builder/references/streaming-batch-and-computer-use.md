# Streaming, Batch, and Computer-Use Tool Design

Read this when a tool runs long enough to need progress, when it wraps screen/browser/desktop
actions, or when callers process many items at once. These three patterns share one root concern:
keep the conversation efficient and predictable while the work itself is slow, stateful, or risky.

The guidance here is conceptual and model-agnostic. MCP transports and SDKs evolve, so reason about
the *capabilities* below (progress, cancellation, partial results) rather than memorizing exact
field names. Confirm the precise wire format against your SDK version before implementing.

---

## 1. Streaming and Progress for Long-Running Tools

### When a tool needs streaming or progress

Default to a single request/response. Add progress or streaming only when one of these is true:

- The call routinely exceeds a few seconds (builds, crawls, large queries, multi-step automation).
- The result is naturally incremental (log tails, search hits arriving over time, generated chunks).
- A human or agent benefits from seeing intermediate state to decide whether to keep waiting.

If a tool finishes in well under a second, streaming adds complexity for no benefit — return once.

### Progress updates

MCP lets a long call emit progress notifications while the final result is still pending. Treat
progress as *advisory UX*, not as the result:

- **Carry a stable correlation handle.** Tie each progress update to the originating call so a client
  can route it to the right place when several tools run concurrently.
- **Report fraction or step, plus a short label.** "3/10 repositories scanned" is more useful to an
  agent than a raw percentage with no unit.
- **Send a known total when you have one.** When the total is unknown (streaming an open-ended feed),
  send monotonic counts and say so, rather than faking a denominator.
- **Throttle.** Coalesce updates to a sane cadence (e.g., a few per second at most). Flooding the
  channel with thousands of ticks wastes tokens and can starve the actual result.
- **Never put load-bearing data only in progress.** The final response must stand alone; a client
  that ignored every progress update should still get a complete, correct result.

### Chunking incremental results

When the payload itself is large or arrives over time:

- Stream **semantically whole units** (a complete log line, one search hit, one record), never bytes
  split mid-token. A consumer should be able to act on each chunk without buffering the whole stream.
- Make each chunk **self-describing** — include enough identity (index, id, offset) that an
  interrupted stream can be resumed or de-duplicated.
- Mark the **terminal chunk** explicitly (an end/complete signal). Don't make clients infer completion
  from a timeout.
- Decide up front whether order matters. If chunks can arrive out of order, stamp them with a sequence
  number; if order is guaranteed by the transport, document that you rely on it.

### Cancellation and timeouts

Long tools must be interruptible, or a single stuck call can hang an agent indefinitely.

- **Honor cancellation.** MCP supports cancelling an in-flight request; wire it through to the
  underlying work (abort the HTTP request, kill the subprocess, close the cursor). Cancellation that
  only stops *reporting* but lets the job run on is a resource leak.
- **Set an internal deadline.** Don't rely solely on the client to time out. Cap the operation and
  return a clear "timed out after N s, partial results included" response instead of hanging.
- **Make cancellation safe.** If the work mutates state, define what a cancelled call leaves behind —
  ideally nothing (transactional) or a clearly-reported partial state. See idempotency below.
- **Clean up on disconnect.** If the client goes away mid-stream, release the subprocess, file handle,
  or browser session. Orphaned automation sessions are a common leak in computer-use servers.

---

## 2. Wrapping Computer-Use / Browser / Desktop Actions

Some MCP servers expose *actions on a live surface* — a browser tab, a desktop, a VM — rather than a
pure API. (For building the automation engine itself, see the `computer-use-automation` skill; this
section is about the MCP boundary around it.) These tools are stateful, slow, and often irreversible,
so they need extra discipline.

### Action granularity

Pick a level of granularity that is expressive but not chatty:

- **Too fine** ("move mouse 10px", "press key A") forces the agent into long, fragile click-by-click
  sequences and burns turns. Avoid raw primitive-per-call as the *only* interface.
- **Too coarse** ("accomplish this goal") hides what actually happened and makes failures
  undebuggable.
- **Prefer intent-level actions** that map to one user-meaningful step: `navigate(url)`,
  `click(target)`, `type_text(target, text)`, `read_page()`, `take_screenshot()`. Offer a batched
  "do these steps" action (see §3) for known sequences so the agent isn't forced into a round-trip per
  keystroke.
- Give actions a **stable way to name targets** (role + accessible name, a selector, or a labeled
  element from a prior read) rather than only raw pixel coordinates, which break across viewports.

### Returning screenshots and state

The agent cannot see the screen; the tool's response *is* its eyes. After an action, return enough to
ground the next decision:

- **Current observable state** — a screenshot and/or a structured/text snapshot (accessibility tree,
  visible text, URL, focused element). Structured text is cheaper and more reliable than an image when
  it suffices; reserve screenshots for when layout/visual state actually matters.
- **What changed** — new URL, dialog appeared, element count, error banner — so the agent isn't forced
  to diff two screenshots.
- **Identity for follow-up** — element references the next call can reuse, so the agent doesn't
  re-scrape the page each step.
- Keep images **right-sized**: downscale to legible-but-small, and don't return a full-resolution
  screenshot after every trivial action. Let the agent request a screenshot explicitly when needed.

### Safety gates for destructive or sensitive actions

Live-surface actions can spend money, send messages, delete data, or leak credentials. Build the gate
into the tool, not just the prompt:

- **Separate read from write.** Navigation/reading is low-risk; submitting forms, purchasing, sending,
  or deleting is not. Don't bundle an irreversible action into an innocuous-looking read tool.
- **Require explicit confirmation or a dry-run for irreversible steps.** A `confirm: true` (or a
  preceding `dry_run` that returns *what would happen*) forces the agent — and any human-in-the-loop —
  to commit deliberately. Default to the safe path.
- **Scope and allowlist.** Constrain which domains, files, or apps the server can touch. A computer-use
  server with unbounded reach is a standing security risk.
- **Never echo secrets.** Redact passwords, tokens, and card numbers from screenshots, page dumps, and
  logs. Treat any returned state as something the model and transcript will see.
- **Make actions observable and reversible where possible.** Log every action; prefer flows that can
  be undone or that stage changes before a final commit.

---

## 3. Batch-Friendly Tool Design

A tool that handles exactly one item forces an agent into N chatty round-trips to process N items —
slow, token-expensive, and error-prone. Design tools so the common "do this to many things" case is
one call.

### Accept arrays

- **Let the primary input take a list.** `delete_records(ids: [...])` beats N calls to
  `delete_record(id)`. Accept a single-element list rather than maintaining two tools.
- **Keep per-item structure explicit.** A batch of objects (each with its own fields) is clearer than
  parallel arrays the caller must keep aligned.
- **Bound the batch.** Document and enforce a max items / max payload per call so one request can't
  blow past timeouts or memory. Reject oversized batches with a clear message telling the caller to
  split.
- Don't force batching where it makes no sense — a singleton "get current user" stays singular. Batch
  the operations that are genuinely repeated.

### Idempotency

Batches make retries likely (a partial failure, a timeout, a cancelled stream), so repeated calls must
be safe:

- **Prefer idempotent operations** keyed by a stable id, so re-running a batch doesn't double-apply.
- **Support client-supplied operation keys** (an idempotency token per item) when the action creates
  something, so a retry recognizes already-done work instead of duplicating it.
- State idempotency guarantees in the tool description — the agent decides retry behavior based on them.

### Partial-failure results

The biggest design trap: a 100-item batch where item 37 fails. Do **not** fail the whole call or you
force the agent to re-do the 99 that worked.

- **Return a per-item result list**, each entry carrying the item's id, a success/failure status, and
  its output or error. The agent can then retry only the failures.
- **Use a summary + details shape**: counts of succeeded/failed up top, per-item detail below, so the
  agent can branch on the summary without parsing everything.
- **Make errors actionable per item** — which item, why, and whether retrying could help (transient vs.
  permanent) — rather than one opaque top-level error.
- **Don't silently drop items.** Every input item should appear in the output (success or failure) so
  the caller can reconcile.

### Pagination for list/read tools

The mirror image of batching: a tool that *returns* many items must page, or it floods the context and
risks truncation.

- **Page large result sets** with a limit plus a cursor/offset; return a `next_cursor` (or
  `has_more`) so the agent knows whether to continue.
- **Cap and document the default page size.** Never return an unbounded list "because the dataset is
  usually small" — datasets grow.
- **Prefer opaque cursors** over offset where the underlying data shifts, to avoid skips/duplicates.
- **Support server-side filtering and field selection** so the agent can narrow results instead of
  paging through everything — fewer tokens, fewer round-trips.
- Echo enough context (total count if cheap, current cursor) for the agent to reason about progress.

---

## Quick Checklist

- [ ] Long tools (>~ a few seconds) emit throttled progress with a stable correlation handle.
- [ ] Streamed results are whole units, self-describing, and end with an explicit terminal signal.
- [ ] Cancellation aborts the real work and cleans up sessions; an internal deadline caps runtime.
- [ ] Computer-use actions are intent-level, return current state (text-first, screenshots when needed).
- [ ] Destructive/sensitive actions require confirm/dry-run, are scoped to an allowlist, and redact secrets.
- [ ] Repeated operations accept a bounded array; ops are idempotent or take an idempotency key.
- [ ] Batch tools return per-item success/failure, never a single all-or-nothing error.
- [ ] List/read tools paginate with a documented cap and a cursor, plus filtering to narrow results.
