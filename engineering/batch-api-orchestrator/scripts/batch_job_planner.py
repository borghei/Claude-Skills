#!/usr/bin/env python3
"""Plan a bulk LLM batch job: chunking, idempotency, and partial-failure handling.

Standard library only. No network, no LLM calls. Produces a deterministic plan
the caller can implement against any vendor's batch API.
"""

import argparse
import json
import math
import sys

RETRY_POLICIES = {
    "none": "Do not retry. Failed items go straight to the dead-letter set.",
    "fixed": "Retry failed items with a constant backoff between attempts.",
    "exponential": "Retry failed items with exponentially growing backoff (recommended).",
}


def plan(args):
    total = args.total_items
    size = args.max_batch_size
    num_chunks = math.ceil(total / size) if total else 0

    chunks = []
    remaining = total
    for idx in range(num_chunks):
        count = min(size, remaining)
        start = idx * size
        chunks.append({
            "chunk_id": "chunk-{:04d}".format(idx),
            "index_start": start,
            "index_end": start + count - 1,
            "item_count": count,
            "idempotency_key_prefix": "{}::chunk-{:04d}::v{}".format(
                args.job_id, idx, args.job_version),
        })
        remaining -= count

    retry = {
        "policy": args.retry_policy,
        "description": RETRY_POLICIES[args.retry_policy],
        "max_retries": args.max_retries if args.retry_policy != "none" else 0,
        "scope": "per-item (re-enqueue only failed request ids, never the whole chunk)",
    }

    idempotency = {
        "scheme": "Per-item key = hash(job_id, job_version, item_index, input_payload).",
        "purpose": "Safe re-submission: a resubmitted item with the same key is deduped, never double-billed or double-written.",
        "key_prefix_example": chunks[0]["idempotency_key_prefix"] if chunks else None,
    }

    reconciliation = {
        "match_by": "request_id / custom_id echoed in each output — never output ordering.",
        "on_unmatched": "Route outputs with no matching request, and requests with no output, to a dead-letter set.",
        "completion_check": "All chunks reached a terminal state AND matched_count + dead_letter_count == total_items.",
    }

    completion_signal = {
        "polling": "Poll each chunk's status on an interval with capped backoff; simplest, vendor-agnostic.",
        "callback": "Register a webhook to be notified on chunk completion; lower latency, needs a public endpoint.",
        "recommendation": "polling" if num_chunks <= 50 else "callback",
    }

    return {
        "inputs": {
            "total_items": total,
            "max_batch_size": size,
            "retry_policy": args.retry_policy,
            "max_retries": args.max_retries,
            "job_id": args.job_id,
            "job_version": args.job_version,
        },
        "chunking": {
            "num_chunks": num_chunks,
            "items_per_full_chunk": size,
            "last_chunk_size": chunks[-1]["item_count"] if chunks else 0,
            "chunks": chunks,
        },
        "idempotency": idempotency,
        "retry": retry,
        "partial_failure": {
            "rule": "Retry the item, not the batch.",
            "detail": "On a chunk with mixed results, extract failed request ids and re-enqueue only those under their original idempotency keys.",
        },
        "reconciliation": reconciliation,
        "completion_signal": completion_signal,
    }


def human(result):
    c = result["chunking"]
    lines = []
    lines.append("Batch Job Plan")
    lines.append("=" * 40)
    i = result["inputs"]
    lines.append("Total items:     {:,}".format(i["total_items"]))
    lines.append("Max batch size:  {:,}".format(i["max_batch_size"]))
    lines.append("Chunks:          {}".format(c["num_chunks"]))
    lines.append("Last chunk size: {}".format(c["last_chunk_size"]))
    lines.append("")
    lines.append("Idempotency:")
    lines.append("  " + result["idempotency"]["scheme"])
    if result["idempotency"]["key_prefix_example"]:
        lines.append("  example key prefix: " + result["idempotency"]["key_prefix_example"])
    lines.append("")
    lines.append("Retry policy: {} (max {})".format(
        result["retry"]["policy"], result["retry"]["max_retries"]))
    lines.append("  " + result["retry"]["description"])
    lines.append("  scope: " + result["retry"]["scope"])
    lines.append("")
    lines.append("Partial failure: " + result["partial_failure"]["rule"])
    lines.append("  " + result["partial_failure"]["detail"])
    lines.append("")
    lines.append("Reconciliation:")
    lines.append("  match by: " + result["reconciliation"]["match_by"])
    lines.append("  unmatched: " + result["reconciliation"]["on_unmatched"])
    lines.append("")
    lines.append("Completion: recommend '{}' for {} chunk(s).".format(
        result["completion_signal"]["recommendation"], c["num_chunks"]))
    lines.append("  polling:  " + result["completion_signal"]["polling"])
    lines.append("  callback: " + result["completion_signal"]["callback"])
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Plan a bulk LLM batch job: chunking, idempotency, partial failures.")
    p.add_argument("--total-items", type=int, required=True,
                   help="Total number of items to process.")
    p.add_argument("--max-batch-size", type=int, required=True,
                   help="Maximum items per chunk (your vendor's batch limit and/or blast-radius cap).")
    p.add_argument("--retry-policy", default="exponential",
                   choices=sorted(RETRY_POLICIES.keys()),
                   help="How to retry failed items (default exponential).")
    p.add_argument("--max-retries", type=int, default=3,
                   help="Max retry attempts per item (ignored when policy=none; default 3).")
    p.add_argument("--job-id", default="job",
                   help="Stable job identifier used in idempotency keys (default 'job').")
    p.add_argument("--job-version", type=int, default=1,
                   help="Job/version number used in idempotency keys (default 1).")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = p.parse_args(argv)

    if args.total_items < 0:
        p.error("--total-items must be non-negative.")
    if args.max_batch_size <= 0:
        p.error("--max-batch-size must be positive.")
    if args.max_retries < 0:
        p.error("--max-retries must be non-negative.")

    result = plan(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
