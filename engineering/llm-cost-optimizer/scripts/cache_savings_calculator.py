#!/usr/bin/env python3
"""
Cache Savings Calculator - Model the economics of prompt/context caching.

Compares the naive cost (paying full input price for a stable prefix on every
request) against the cached cost (one premium-priced cache write followed by
steeply discounted cache reads). Reports break-even reuse count and % savings.

This is a deterministic calculator: NO network, NO third-party libraries, NO
LLM calls. All prices and multipliers are USER-SUPPLIED. The neutral defaults
for the cache multipliers reflect only the *shape* of common pricing (a write
premium and a read discount); the base input price defaults to a neutral 1.0
"price unit" so results scale linearly to whatever currency/rate you plug in.

Cost model
----------
Let P = cacheable prefix tokens, b = base input price per token,
    w = cache-write multiplier (typically > 1), r = cache-read multiplier (< 1),
    N = number of requests sharing the prefix.

    naive_cost  = N * P * b
    cached_cost = (P * b * w)              # one cache write
                + (N - 1) * (P * b * r)    # N-1 cache reads

The volatile/uncached tokens per request are priced identically in both worlds,
so they cancel out of the comparison. --uncached-tokens is accepted and reported
for context (total bill) but does not affect savings on the cached prefix.

    break_even_N = (w - 1) / (1 - r) + 1
    savings_pct  = (naive_cost - cached_cost) / naive_cost * 100

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import sys


def compute(requests, cached_tokens, uncached_tokens,
            write_mult, read_mult, base_input_price):
    """Compute naive vs cached cost on the cacheable prefix, plus break-even."""
    P = cached_tokens
    N = requests
    b = base_input_price
    w = write_mult
    r = read_mult

    # Cost attributable to the cacheable prefix only.
    naive_prefix_cost = N * P * b
    cached_prefix_cost = (P * b * w) + max(0, N - 1) * (P * b * r)
    prefix_savings = naive_prefix_cost - cached_prefix_cost

    # Uncached/volatile tokens are billed identically either way; include them
    # so the totals reflect the real bill, but they do not change the savings.
    uncached_cost = N * uncached_tokens * b
    naive_total = naive_prefix_cost + uncached_cost
    cached_total = cached_prefix_cost + uncached_cost
    total_savings = naive_total - cached_total  # == prefix_savings

    savings_pct_prefix = (
        (prefix_savings / naive_prefix_cost * 100) if naive_prefix_cost else 0.0
    )
    savings_pct_total = (
        (total_savings / naive_total * 100) if naive_total else 0.0
    )

    # Break-even reuse count: smallest N where caching is net-positive.
    if r >= 1:
        # Degenerate: read multiplier not a discount -> caching never wins.
        break_even_n = float("inf")
    else:
        break_even_n = (w - 1) / (1 - r) + 1

    return {
        "inputs": {
            "requests": N,
            "cached_tokens": P,
            "uncached_tokens": uncached_tokens,
            "cache_write_multiplier": w,
            "cache_read_multiplier": r,
            "base_input_price_per_token": b,
        },
        "naive_prefix_cost": round(naive_prefix_cost, 6),
        "cached_prefix_cost": round(cached_prefix_cost, 6),
        "prefix_savings": round(prefix_savings, 6),
        "prefix_savings_pct": round(savings_pct_prefix, 2),
        "uncached_cost": round(uncached_cost, 6),
        "naive_total_cost": round(naive_total, 6),
        "cached_total_cost": round(cached_total, 6),
        "total_savings": round(total_savings, 6),
        "total_savings_pct": round(savings_pct_total, 2),
        "break_even_reuse_count": (
            None if break_even_n == float("inf") else round(break_even_n, 4)
        ),
        "caching_worthwhile": (
            break_even_n != float("inf") and N >= break_even_n
        ),
    }


def format_human(res):
    inp = res["inputs"]
    lines = []
    lines.append("=" * 60)
    lines.append("PROMPT CACHE SAVINGS")
    lines.append("=" * 60)
    lines.append(f"Requests sharing prefix : {inp['requests']:,}")
    lines.append(f"Cached prefix tokens    : {inp['cached_tokens']:,}")
    lines.append(f"Uncached tokens/request : {inp['uncached_tokens']:,}")
    lines.append(f"Base input price/token  : {inp['base_input_price_per_token']}")
    lines.append(f"Cache write multiplier  : {inp['cache_write_multiplier']}x")
    lines.append(f"Cache read multiplier   : {inp['cache_read_multiplier']}x")
    lines.append("")
    lines.append("Cacheable prefix (where caching acts):")
    lines.append(f"  Naive  cost : {res['naive_prefix_cost']:.6f}")
    lines.append(f"  Cached cost : {res['cached_prefix_cost']:.6f}")
    lines.append(f"  Savings     : {res['prefix_savings']:.6f} "
                 f"({res['prefix_savings_pct']:.1f}%)")
    lines.append("")
    lines.append("Total bill (prefix + uncached/volatile tokens):")
    lines.append(f"  Naive  total: {res['naive_total_cost']:.6f}")
    lines.append(f"  Cached total: {res['cached_total_cost']:.6f}")
    lines.append(f"  Savings     : {res['total_savings']:.6f} "
                 f"({res['total_savings_pct']:.1f}%)")
    lines.append("")
    if res["break_even_reuse_count"] is None:
        lines.append("Break-even reuse count : never "
                     "(read multiplier is not a discount)")
    else:
        lines.append(f"Break-even reuse count : "
                     f"{res['break_even_reuse_count']:.2f} requests")
    verdict = "YES" if res["caching_worthwhile"] else "NO"
    lines.append(f"Caching worthwhile here: {verdict}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Cache Savings Calculator - model prompt/context caching economics.\n\n"
            "Cost model (prefix tokens P, base price b, write mult w, read mult r,\n"
            "N requests sharing the prefix):\n"
            "  naive_cost   = N * P * b\n"
            "  cached_cost  = (P*b*w) + (N-1)*(P*b*r)\n"
            "  break_even_N = (w - 1) / (1 - r) + 1\n\n"
            "Volatile/uncached tokens are billed the same either way and cancel\n"
            "out of the savings; they are included only in the reported totals.\n"
            "All prices/multipliers are USER-SUPPLIED -- plug in YOUR provider's\n"
            "published rates. The base-input-price default (1.0) is a neutral\n"
            "price unit, not a real vendor price."
        ),
    )
    parser.add_argument("--requests", type=int, required=True,
                        help="Number of requests sharing the cached prefix (N)")
    parser.add_argument("--cached-tokens", type=int, required=True,
                        help="Tokens in the stable, cacheable prefix (P)")
    parser.add_argument("--uncached-tokens", type=int, default=0,
                        help="Volatile input tokens per request (default: 0). "
                             "Reported in totals; does not affect savings.")
    parser.add_argument("--cache-write-multiplier", type=float, default=1.25,
                        help="Cache-write price vs base input (default: 1.25)")
    parser.add_argument("--cache-read-multiplier", type=float, default=0.1,
                        help="Cache-read price vs base input (default: 0.1)")
    parser.add_argument("--base-input-price", type=float, default=1.0,
                        help="Base input price per token, YOUR rate "
                             "(default: 1.0 neutral price unit)")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of human-readable output")

    args = parser.parse_args()

    if args.requests < 1:
        print("Error: --requests must be >= 1", file=sys.stderr)
        sys.exit(1)
    if args.cached_tokens < 0 or args.uncached_tokens < 0:
        print("Error: token counts must be >= 0", file=sys.stderr)
        sys.exit(1)
    if args.base_input_price < 0:
        print("Error: --base-input-price must be >= 0", file=sys.stderr)
        sys.exit(1)

    res = compute(
        requests=args.requests,
        cached_tokens=args.cached_tokens,
        uncached_tokens=args.uncached_tokens,
        write_mult=args.cache_write_multiplier,
        read_mult=args.cache_read_multiplier,
        base_input_price=args.base_input_price,
    )

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(format_human(res))


if __name__ == "__main__":
    main()
