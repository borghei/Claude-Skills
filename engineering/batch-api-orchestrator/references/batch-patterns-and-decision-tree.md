# Batch Patterns and Decision Tree

A model- and vendor-agnostic guide to deciding *when* to use an asynchronous batch
LLM API and *how* to design the job so it is cheap, idempotent, and resilient. The
"batch API" here is a conceptual pattern — you submit a large set of requests, the
provider processes them asynchronously over minutes to hours, and you fetch results
when the job completes — typically at a meaningful discount versus realtime.

## The core tradeoff

A batch API trades **latency for cost and throughput**:

- **Cost:** batch is commonly priced well below realtime — a useful rule of thumb is
  roughly half, but always confirm your vendor's actual discount (supply it via the
  estimator's `--batch-discount`).
- **Latency:** results are not immediate. Expect minutes to hours, sometimes with a
  completion-window SLA rather than a guarantee.
- **Throughput:** batch lanes often have separate, higher rate limits, so a huge job
  finishes without hammering your realtime quota.

The single decision that dominates everything else: **is a human waiting on the
result?** If yes, you are in interactive territory and batch is the wrong tool.

## When-to-batch decision tree

```
Is a human/interactive flow blocked on each result?
├─ YES  -> Realtime / streaming. Stop. (Batch latency breaks UX.)
└─ NO
   └─ Is the workload large and parallelizable (hundreds+ of independent requests)?
      ├─ NO  -> Realtime is fine; batch overhead isn't worth it for a handful.
      └─ YES
         └─ Can results tolerate minutes-to-hours latency?
            ├─ NO (need < seconds, e.g. near-real-time pipeline)
            │     -> Realtime, possibly with concurrency + caching.
            └─ YES
               └─ Is the work idempotent / safe to retry?
                  ├─ NO  -> Make it idempotent first (stable keys), then batch.
                  └─ YES -> BATCH. Capture the discount.
```

## Where batch fits (good use cases)

- **Evals** — scoring a model/prompt against a large fixed dataset. No user waiting;
  embarrassingly parallel; latency-insensitive. The canonical batch workload.
- **Backfills** — applying a new prompt/model to a historical corpus (re-tagging,
  re-summarizing, migrating outputs to a new schema).
- **Embeddings at scale** — vectorizing large document sets for search/RAG indexing.
- **Bulk classification / extraction** — labeling, moderation passes, entity or field
  extraction over millions of records feeding an offline pipeline or warehouse.
- **Synthetic data generation** — producing large training/eval datasets offline.

## Where batch does NOT fit (anti-patterns)

- **Interactive requests** — chat turns, autocomplete, anything in a request/response
  UX. The latency makes it unusable; never batch a user-facing call.
- **Tiny jobs** — a few dozen requests rarely justify the orchestration overhead.
- **Hard real-time pipelines** — sub-second SLAs cannot wait for a batch window.
- **Tight sequential dependencies** — if request N needs the output of request N-1,
  the work isn't parallelizable and batch buys you nothing.
- **One giant all-or-nothing chunk** — a single failure can sink the whole job; chunk
  it so failures are isolated.

## Job design

### Idempotency keys

Give every item a **stable idempotency key** derived from inputs, not from time or a
random id: `key = hash(job_id, job_version, item_index, input_payload)`. Then:

- Re-submitting an item (after a crash, timeout, or retry) is safe — the provider or
  your own dedupe layer recognizes the key and won't double-process or double-bill.
- Bumping `job_version` intentionally re-runs the whole set under fresh keys when you
  change the prompt or model.

### Partial-failure handling

Batches return mixed results: most items succeed, some fail (rate-limited, malformed,
content-filtered, transient errors). The rule is **retry the item, not the batch**:

1. Parse the result set and separate successes from failures.
2. Re-enqueue *only* the failed request ids, under their original idempotency keys.
3. Apply a retry policy (prefer exponential backoff, capped attempts).
4. After max retries, move the item to a **dead-letter set** for inspection — do not
   silently drop it and do not block the whole job on it.

### Result reconciliation

Batch results often come back **out of order** and asynchronously. Always:

- Echo a `request_id` / `custom_id` on every request and match outputs back by that id
  — never rely on positional ordering.
- Track three counts: matched outputs, dead-lettered items, and still-pending. The job
  is complete only when `matched + dead_letter == total` and every chunk is terminal.
- Persist a manifest (item id -> status) so a crashed orchestrator can resume without
  re-running completed work.

### Polling vs. callback for completion

- **Polling** — periodically check each chunk's status with capped backoff. Simplest,
  fully vendor-agnostic, needs no inbound endpoint. Good default for a modest number of
  chunks.
- **Callback / webhook** — the provider notifies you on completion. Lower latency to
  "results ready," but requires a reachable endpoint and handling for missed/duplicate
  notifications. Prefer it when you have many chunks or want to avoid poll overhead.

## Chunking guidance

- Split by the vendor's **max batch size** and by your own **blast-radius** tolerance —
  a smaller chunk fails smaller.
- Keep chunks independently retryable; never let one chunk's failure cascade.
- Size so that a single chunk's cost and re-run time are acceptable if it must be
  retried wholesale.

## Quick checklist before shipping a batch job

- [ ] No human is blocked on the results (else use realtime).
- [ ] Items are independent and idempotent (stable keys in place).
- [ ] Chunked under the vendor limit and your blast-radius cap.
- [ ] Partial-failure path retries items, not whole batches; dead-letter exists.
- [ ] Reconciliation matches outputs by id, with a resumable manifest.
- [ ] Completion detected via polling or callback, with terminal-state checks.
