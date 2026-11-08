---
name: batch-api-orchestrator
description: >
  Decides batch vs realtime for bulk LLM work, prices both, and plans chunking, idempotency keys
  and partial-failure retries. Use when running evals, backfills, embeddings or bulk extraction
  through a provider batch API.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-engineering
  updated: 2026-11-08
  tags: [batch-api, llm, cost-optimization, throughput, async]
---

# Batch API Orchestrator

> **Category:** Engineering
> **Domain:** AI Engineering

## Overview

Decide when to run LLM work through an asynchronous batch API versus realtime/streaming, then design the job so it is cheap, idempotent, and resilient to partial failure. Batch APIs typically cost roughly half of realtime in exchange for higher latency (results arrive over minutes to hours, not milliseconds), which makes them ideal for evals, backfills, embeddings, and bulk classification/extraction — and wrong for anything a human is waiting on. This skill is model- and vendor-agnostic: it reasons about the batch *pattern*, not any one provider's API.

## When to Use

- A job of thousands of LLM requests where no person waits on each answer (evals, backfills, embeddings, bulk classification).
- Choosing between a provider's batch API and realtime calls on cost and latency.
- Designing chunk sizes, retries and reconciliation for a batch job before writing client code.

## Clarify First

Before recommending or designing a batch job, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Latency tolerance:** is a human waiting (interactive), or can results land in minutes/hours? (sets `--latency-tolerance` and the batch-vs-realtime verdict).
- **Volume & token shape:** how many requests, and the average input/output tokens each? (sets `--requests`, `--avg-input-tokens`, `--avg-output-tokens` for the cost estimate).
- **Pricing & discount:** your realtime per-token prices and the batch discount your vendor offers (sets `--realtime-input-price`, `--realtime-output-price`, `--batch-discount`; defaults are neutral placeholders, not real prices).

Ask about the two or three inputs that matter most for this request. If the user says "just draft it," proceed and list your assumptions.

## Quick Start

```bash
cd engineering/batch-api-orchestrator

# 1. Should this be batch or realtime, and what does it cost?
python scripts/batch_cost_estimator.py \
  --requests 50000 --avg-input-tokens 800 --avg-output-tokens 200 \
  --realtime-input-price 3.0 --realtime-output-price 15.0 \
  --batch-discount 0.5 --latency-tolerance hours

# 2. Plan the chunking / idempotency / retry strategy for the job
python scripts/batch_job_planner.py \
  --total-items 50000 --max-batch-size 10000 --retry-policy exponential --json
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `scripts/batch_cost_estimator.py` | Compare realtime vs batch cost, show savings, and recommend batch or realtime given latency tolerance | `--requests`, `--avg-input-tokens`, `--avg-output-tokens`, `--realtime-input-price`, `--realtime-output-price`, `--batch-discount`, `--latency-tolerance`, `--json` |
| `scripts/batch_job_planner.py` | Produce a chunking + idempotency + partial-failure plan for a bulk job | `--total-items`, `--max-batch-size`, `--retry-policy`, `--max-retries`, `--json` |

Both scripts: Python 3 standard library only, argparse CLI, `--json` and human-readable output. Run `--help` for full usage.

**Exit codes (both).** `0` estimate or plan printed; `2` invalid arguments (negative or zero counts,
discount outside 0-1, unknown latency tolerance or retry policy).

### Provider limits to check (as of 2026-11, from the providers' batch API docs; confirm before sizing a job)

| | Anthropic Message Batches | OpenAI Batch API |
|---|---|---|
| Discount vs realtime | 50% | 50% |
| Max per batch | 100,000 requests or 256 MB | 50,000 requests per input file, input file up to 200 MB |
| Completion window | most finish within an hour; expire after 24 h | 24 h window |
| Result retention | 29 days | output file deleted 30 days after the batch completes (set 1 hour to 30 days with `output_expires_after`) |
| Prompt caching | stacks with the batch discount | check current docs |

Use these to set `--max-batch-size` and `--batch-discount`. Limits change, so read the provider's
batch documentation before sizing a production job.

**Done when:**
1. The cost comparison used your provider's current prices and discount, not the placeholders.
2. Every request carries an idempotency key and every result is joined back to its request by id.
3. A small pilot batch (a few hundred items) completed, and failed items were retried on their own.

## Workflows

### 1. Decide batch vs realtime, then size the cost

1. Gather volume and token shape (`--requests`, `--avg-input-tokens`, `--avg-output-tokens`).
2. Plug in *your* vendor prices and batch discount — never assume them.
3. Run `batch_cost_estimator.py` with the real `--latency-tolerance` (`realtime`, `minutes`, or `hours`).
4. Read the verdict: if work is interactive, the tool recommends realtime regardless of savings; otherwise it quantifies the batch savings.
5. Sanity-check against the decision tree in `references/batch-patterns-and-decision-tree.md`.

### 2. Design a resilient bulk job

1. Run `batch_job_planner.py` with `--total-items`, `--max-batch-size`, and a `--retry-policy`.
2. Adopt the generated idempotency-key scheme so re-submitting a chunk never double-charges or double-writes.
3. Wire result reconciliation: match every output back to its request id, and collect the unmatched into a dead-letter set.
4. Apply the partial-failure handling (retry only failed items, never the whole batch) from the reference.
5. Choose polling vs callback for completion, per the reference guidance.

## Scope & Limitations

**In Scope:**
- The batch versus realtime decision, based on latency tolerance (`realtime`, `minutes`, `hours`, `days`)
- Cost comparison of realtime and batch runs with `batch_cost_estimator.py` from request volume, average token counts, the user's own per-token prices and batch discount
- Job plans from `batch_job_planner.py`: chunk sizes, an idempotency-key scheme, retry policy (exponential, fixed or none) and partial-failure handling
- Job design guidance from the references: reconciliation by request id, dead-letter sets, polling versus callbacks, chunk sizing and break-even modelling

**Out of Scope:**
- Submitting, polling or downloading batch jobs; the skill does not call any vendor API or include client code for one
- Wider LLM cost work such as token counting, caching and model routing (see `engineering/llm-cost-optimizer/`)
- Designing the evaluations that often run as batch jobs (see `engineering/agentic-evaluation-framework/` and `engineering/agent-harness/`)
- Streaming and interactive request handling

**Important Caveats:**
- The default prices in `batch_cost_estimator.py` are neutral placeholders, not real prices. Estimates mean something only after the user supplies current vendor prices and discount.
- The roughly half-price batch discount is a rule of thumb. Discounts, maximum batch sizes, completion windows and result retention differ by vendor and change over time.
- Estimates assume every request costs the average token count. Long-tail inputs, retries and failed items add cost the model does not show.

## Anti-Patterns

### Batching interactive work
**Mistake:** Sending user-facing requests through the batch API to save money.
**Why it happens:** The discount is large and the latency cost is invisible in a spreadsheet.
**Instead:** Batch only work nobody waits on. `batch_cost_estimator.py` recommends realtime whenever `--latency-tolerance realtime` is set.

### One giant batch
**Mistake:** Submitting a whole backfill as a single maximum-size batch.
**Why it happens:** Fewer jobs feel simpler to track.
**Instead:** Chunk below the provider limit so a bad prompt or schema error costs one chunk, not the run. Pilot a small chunk first.

### Trusting output order
**Mistake:** Zipping results to inputs by position.
**Why it happens:** Small tests come back in order.
**Instead:** Join on the request id you set (`custom_id` or equivalent) and send unmatched results to a dead-letter set.

## Files

- `scripts/batch_cost_estimator.py` — realtime vs batch cost and a batch/realtime verdict from latency tolerance.
- `scripts/batch_job_planner.py` — chunk plan, idempotency-key scheme and retry plan.
- `references/` — decision tree and job design; cost and throughput economics.

## Reference Documentation

- **[references/batch-patterns-and-decision-tree.md](references/batch-patterns-and-decision-tree.md)** — when-to-batch decision tree; job design (idempotency keys, partial failures, reconciliation, polling vs callback); fitting use cases (evals, backfills, embeddings, bulk classification/extraction); and anti-patterns such as batching interactive requests.
- **[references/cost-and-throughput-economics.md](references/cost-and-throughput-economics.md)** — the cost/throughput tradeoff in depth: the ~half-cost rule of thumb, throughput vs latency, queueing, chunk sizing, and how to model the break-even between a faster realtime path and a cheaper batch path.

## Common Patterns

- **Batch the patient, stream the impatient** — if no human is blocked on the result, default to batch for the cost win; reserve realtime/streaming for interactive UX.
- **Idempotency key per item** — derive a stable key (e.g. hash of input + job version) so retries and re-submissions are safe and never double-billed.
- **Retry the item, not the batch** — on partial failure, re-enqueue only the failed request ids; resubmitting the whole chunk wastes money and re-runs successes.
- **Reconcile by request id** — never rely on output ordering; join results back to inputs by id and route the unmatched to a dead-letter queue for inspection.
- **Right-size chunks** — split by the vendor's max-batch limit and by your own blast-radius tolerance, not into one giant job whose failure is all-or-nothing.
- **Embeddings and evals are the sweet spot** — large, latency-insensitive, embarrassingly parallel workloads capture the full batch discount with the least risk.
