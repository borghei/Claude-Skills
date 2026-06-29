---
name: batch-api-orchestrator
description: >
  This skill should be used when the user asks to "batch LLM requests", "should I use
  the batch API", "estimate batch vs realtime cost", "design a bulk LLM job", or
  "process thousands of prompts cheaply".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-engineering
  updated: 2026-06-29
  tags: [batch-api, llm, cost-optimization, throughput, async]
---

# Batch API Orchestrator

> **Category:** Engineering
> **Domain:** AI Engineering

## Overview

Decide when to run LLM work through an asynchronous batch API versus realtime/streaming, then design the job so it is cheap, idempotent, and resilient to partial failure. Batch APIs typically cost roughly half of realtime in exchange for higher latency (results arrive over minutes to hours, not milliseconds), which makes them ideal for evals, backfills, embeddings, and bulk classification/extraction — and wrong for anything a human is waiting on. This skill is model- and vendor-agnostic: it reasons about the batch *pattern*, not any one provider's API.

## Clarify First

Before recommending or designing a batch job, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Latency tolerance** — is a human waiting (interactive), or can results land in minutes/hours? (sets `--latency-tolerance` and the batch-vs-realtime verdict)
- [ ] **Volume & token shape** — how many requests, and the average input/output tokens each? (sets `--requests`, `--avg-input-tokens`, `--avg-output-tokens` for the cost estimate)
- [ ] **Pricing & discount** — your realtime per-token prices and the batch discount your vendor offers (sets `--realtime-input-price`, `--realtime-output-price`, `--batch-discount`; defaults are neutral placeholders, not real prices)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions.

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
