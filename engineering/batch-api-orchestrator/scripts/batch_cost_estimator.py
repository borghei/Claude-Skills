#!/usr/bin/env python3
"""Estimate realtime vs. batch LLM cost and recommend a path.

Standard library only. No network, no LLM calls. Prices are USER-SUPPLIED
flags with neutral placeholder defaults — they are NOT real vendor prices.

Per-token prices are expressed per 1,000,000 tokens (the common unit), so a
flag value of 3.0 means $3.00 per 1M tokens.
"""

import argparse
import json
import sys

TOKENS_PER_UNIT = 1_000_000

# Latency tolerance -> whether a human/interactive flow is blocked on the result.
INTERACTIVE_TOLERANCES = {"realtime"}
BATCHABLE_TOLERANCES = {"minutes", "hours", "days"}


def estimate(args):
    total_input_tokens = args.requests * args.avg_input_tokens
    total_output_tokens = args.requests * args.avg_output_tokens

    realtime_input_cost = (total_input_tokens / TOKENS_PER_UNIT) * args.realtime_input_price
    realtime_output_cost = (total_output_tokens / TOKENS_PER_UNIT) * args.realtime_output_price
    realtime_total = realtime_input_cost + realtime_output_cost

    batch_factor = 1.0 - args.batch_discount
    batch_total = realtime_total * batch_factor

    savings = realtime_total - batch_total
    savings_pct = (savings / realtime_total * 100.0) if realtime_total else 0.0

    tol = args.latency_tolerance
    if tol in INTERACTIVE_TOLERANCES:
        recommendation = "realtime"
        rationale = (
            "Latency tolerance is interactive (realtime): a user is waiting, so the "
            "batch discount cannot be claimed without harming UX. Use realtime/streaming."
        )
    else:
        recommendation = "batch"
        rationale = (
            "No interactive deadline (latency tolerance '{}'): the work can absorb "
            "batch latency, so capture the {:.0f}% discount via the batch API."
        ).format(tol, savings_pct)

    return {
        "inputs": {
            "requests": args.requests,
            "avg_input_tokens": args.avg_input_tokens,
            "avg_output_tokens": args.avg_output_tokens,
            "realtime_input_price_per_1m": args.realtime_input_price,
            "realtime_output_price_per_1m": args.realtime_output_price,
            "batch_discount": args.batch_discount,
            "latency_tolerance": tol,
        },
        "totals": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
        },
        "realtime_cost": {
            "input": round(realtime_input_cost, 4),
            "output": round(realtime_output_cost, 4),
            "total": round(realtime_total, 4),
        },
        "batch_cost": {
            "total": round(batch_total, 4),
            "discount_applied": args.batch_discount,
        },
        "savings": {
            "absolute": round(savings, 4),
            "percent": round(savings_pct, 2),
        },
        "recommendation": recommendation,
        "rationale": rationale,
    }


def human(result):
    i = result["inputs"]
    lines = []
    lines.append("Batch vs. Realtime Cost Estimate")
    lines.append("=" * 40)
    lines.append("Requests:           {:,}".format(i["requests"]))
    lines.append("Avg input tokens:   {:,}".format(i["avg_input_tokens"]))
    lines.append("Avg output tokens:  {:,}".format(i["avg_output_tokens"]))
    lines.append("Latency tolerance:  {}".format(i["latency_tolerance"]))
    lines.append("")
    lines.append("Realtime cost:      ${:,.2f}".format(result["realtime_cost"]["total"]))
    lines.append("  input  ${:,.2f}   output ${:,.2f}".format(
        result["realtime_cost"]["input"], result["realtime_cost"]["output"]))
    lines.append("Batch cost:         ${:,.2f}  (discount {:.0%})".format(
        result["batch_cost"]["total"], result["batch_cost"]["discount_applied"]))
    lines.append("Savings:            ${:,.2f}  ({:.1f}%)".format(
        result["savings"]["absolute"], result["savings"]["percent"]))
    lines.append("")
    lines.append("RECOMMENDATION: {}".format(result["recommendation"].upper()))
    lines.append(result["rationale"])
    lines.append("")
    lines.append("Note: prices are user-supplied; defaults are neutral placeholders.")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Estimate realtime vs. batch LLM cost and recommend a path.")
    p.add_argument("--requests", type=int, required=True,
                   help="Number of LLM requests in the job.")
    p.add_argument("--avg-input-tokens", type=int, required=True,
                   help="Average input (prompt) tokens per request.")
    p.add_argument("--avg-output-tokens", type=int, required=True,
                   help="Average output (completion) tokens per request.")
    p.add_argument("--realtime-input-price", type=float, default=1.0,
                   help="Realtime input price per 1M tokens (placeholder default 1.0; supply your vendor's).")
    p.add_argument("--realtime-output-price", type=float, default=1.0,
                   help="Realtime output price per 1M tokens (placeholder default 1.0; supply your vendor's).")
    p.add_argument("--batch-discount", type=float, default=0.5,
                   help="Fractional batch discount vs realtime, 0..1 (default 0.5 = half price).")
    p.add_argument("--latency-tolerance", default="hours",
                   choices=sorted(INTERACTIVE_TOLERANCES | BATCHABLE_TOLERANCES),
                   help="How long results can take. 'realtime' => interactive => recommend realtime.")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = p.parse_args(argv)

    if not 0.0 <= args.batch_discount < 1.0:
        p.error("--batch-discount must be in [0, 1).")
    if args.requests < 0 or args.avg_input_tokens < 0 or args.avg_output_tokens < 0:
        p.error("counts and token sizes must be non-negative.")

    result = estimate(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
