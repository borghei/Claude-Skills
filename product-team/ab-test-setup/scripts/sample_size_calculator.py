#!/usr/bin/env python3
"""
A/B Test Sample Size Calculator

Calculates required sample size per variant for A/B tests using
the normal approximation to the binomial distribution.

Supports power analysis, test duration estimation, and multi-variant corrections.
Uses ONLY Python standard library (no scipy/numpy).

Usage:
    python sample_size_calculator.py --baseline 0.05 --mde 0.10
    python sample_size_calculator.py --baseline 0.12 --mde 0.15 --power 0.9
    python sample_size_calculator.py --baseline 0.05 --mde 0.10 --daily-traffic 5000 --json
"""

import argparse
import json
import math
import sys


def z_score(p: float) -> float:
    """Approximate inverse normal CDF (percent-point function).

    Uses the rational approximation from Abramowitz & Stegun (formula 26.2.23).
    Accurate to ~4.5e-4 for 0 < p < 1.
    """
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1 exclusive")
    if p > 0.5:
        return -z_score(1 - p)

    t = math.sqrt(-2 * math.log(p))
    # Coefficients for rational approximation
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def calculate_sample_size(
    baseline_rate: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_tailed: bool = True,
) -> int:
    """Calculate required sample size per variant.

    Args:
        baseline_rate: Current conversion rate (e.g. 0.05 for 5%).
        mde_relative: Minimum detectable effect as relative change (e.g. 0.10 for 10% lift).
        alpha: Significance level (default 0.05).
        power: Statistical power (default 0.80).
        two_tailed: Whether to use two-tailed test (default True).

    Returns:
        Required sample size per variant (integer, rounded up).
    """
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde_relative)

    if p2 >= 1.0:
        p2 = 0.999
    if p2 <= 0.0:
        p2 = 0.001

    z_alpha = z_score(alpha / 2) if two_tailed else z_score(alpha)
    z_beta = z_score(1 - power)

    p_bar = (p1 + p2) / 2
    numerator = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denominator = (p2 - p1) ** 2

    if denominator == 0:
        return 0

    return math.ceil(numerator / denominator)


def estimate_duration(sample_per_variant: int, num_variants: int, daily_traffic: int) -> dict:
    """Estimate test duration in days.

    Args:
        sample_per_variant: Required sample per variant.
        num_variants: Number of variants including control.
        daily_traffic: Daily eligible traffic.

    Returns:
        Dict with duration estimates.
    """
    total_sample = sample_per_variant * num_variants
    raw_days = math.ceil(total_sample / daily_traffic) if daily_traffic > 0 else 0
    recommended_days = max(raw_days, 14)  # Minimum 2 weeks for day-of-week effects

    return {
        "total_sample_needed": total_sample,
        "raw_days": raw_days,
        "recommended_days": recommended_days,
        "minimum_days": 14,
        "maximum_recommended_days": 42,
        "feasible": raw_days <= 42,
    }


def generate_quick_reference_table(alpha: float = 0.05, power: float = 0.80) -> list:
    """Generate a quick-reference sample size table."""
    baselines = [0.01, 0.02, 0.03, 0.05, 0.10, 0.20, 0.50]
    mdes = [0.05, 0.10, 0.15, 0.20, 0.50]

    rows = []
    for bl in baselines:
        row = {"baseline": f"{bl:.0%}"}
        for mde in mdes:
            n = calculate_sample_size(bl, mde, alpha, power)
            row[f"mde_{mde:.0%}"] = n
        rows.append(row)
    return rows


def format_human_output(args, sample_size: int, duration: dict, table: list) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("A/B TEST SAMPLE SIZE CALCULATOR")
    lines.append("=" * 60)

    lines.append(f"\n  Baseline conversion rate:  {args.baseline:.2%}")
    lines.append(f"  Minimum detectable effect: {args.mde:.0%} relative lift")
    abs_effect = args.baseline * args.mde
    lines.append(f"  Absolute effect:           {abs_effect:.4f} ({args.baseline:.2%} -> {args.baseline * (1 + args.mde):.2%})")
    lines.append(f"  Significance level:        {args.alpha:.0%} ({'two-tailed' if args.two_tailed else 'one-tailed'})")
    lines.append(f"  Statistical power:         {args.power:.0%}")
    lines.append(f"  Variants:                  {args.variants}")

    lines.append(f"\n  RESULT: {sample_size:,} visitors per variant")
    lines.append(f"  TOTAL:  {sample_size * args.variants:,} visitors across all variants")

    if args.daily_traffic:
        lines.append(f"\n  DURATION ESTIMATE")
        lines.append(f"  Daily traffic:             {args.daily_traffic:,}")
        lines.append(f"  Minimum duration:          {duration['recommended_days']} days")
        feasibility = "YES" if duration["feasible"] else "NO - consider increasing MDE or testing bolder changes"
        lines.append(f"  Feasible (<6 weeks):       {feasibility}")

        if not duration["feasible"]:
            # Suggest a larger MDE that would be feasible
            for try_mde in [0.15, 0.20, 0.25, 0.30, 0.50]:
                n = calculate_sample_size(args.baseline, try_mde, args.alpha, args.power)
                d = estimate_duration(n, args.variants, args.daily_traffic)
                if d["feasible"]:
                    lines.append(f"\n  SUGGESTION: Use MDE of {try_mde:.0%} to run in ~{d['recommended_days']} days ({n:,}/variant)")
                    break

    lines.append("\n" + "-" * 60)
    lines.append("QUICK REFERENCE TABLE (per variant)")
    lines.append(f"  Confidence: {1 - args.alpha:.0%} | Power: {args.power:.0%}")
    lines.append("-" * 60)

    header = f"{'Baseline':>10} | {'5% lift':>10} | {'10% lift':>10} | {'15% lift':>10} | {'20% lift':>10} | {'50% lift':>10}"
    lines.append(header)
    lines.append("-" * len(header))

    for row in table:
        vals = [row["baseline"]]
        for mde_key in ["mde_5%", "mde_10%", "mde_15%", "mde_20%", "mde_50%"]:
            vals.append(f"{row[mde_key]:,}")
        lines.append(f"{vals[0]:>10} | {vals[1]:>10} | {vals[2]:>10} | {vals[3]:>10} | {vals[4]:>10} | {vals[5]:>10}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="A/B Test Sample Size Calculator - Calculate required visitors per variant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic calculation
  python sample_size_calculator.py --baseline 0.05 --mde 0.10

  # With duration estimate
  python sample_size_calculator.py --baseline 0.05 --mde 0.10 --daily-traffic 5000

  # Higher power, 3 variants
  python sample_size_calculator.py --baseline 0.12 --mde 0.15 --power 0.9 --variants 3

  # JSON output for integration
  python sample_size_calculator.py --baseline 0.05 --mde 0.10 --json
        """,
    )

    parser.add_argument("--baseline", "-b", type=float, required=True, help="Baseline conversion rate (e.g. 0.05 for 5%%)")
    parser.add_argument("--mde", "-m", type=float, required=True, help="Minimum detectable effect as relative lift (e.g. 0.10 for 10%%)")
    parser.add_argument("--alpha", "-a", type=float, default=0.05, help="Significance level (default: 0.05)")
    parser.add_argument("--power", "-p", type=float, default=0.80, help="Statistical power (default: 0.80)")
    parser.add_argument("--variants", "-v", type=int, default=2, help="Number of variants including control (default: 2)")
    parser.add_argument("--daily-traffic", "-d", type=int, default=0, help="Daily eligible traffic for duration estimation")
    parser.add_argument("--two-tailed", action="store_true", default=True, help="Use two-tailed test (default: True)")
    parser.add_argument("--one-tailed", action="store_true", help="Use one-tailed test")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.one_tailed:
        args.two_tailed = False

    # Validate inputs
    if not (0 < args.baseline < 1):
        print("Error: Baseline rate must be between 0 and 1", file=sys.stderr)
        sys.exit(1)
    if args.mde <= 0:
        print("Error: MDE must be positive", file=sys.stderr)
        sys.exit(1)

    # Apply Bonferroni correction for multiple variants
    adjusted_alpha = args.alpha
    if args.variants > 2:
        adjusted_alpha = args.alpha / (args.variants - 1)

    sample_size = calculate_sample_size(args.baseline, args.mde, adjusted_alpha, args.power, args.two_tailed)

    duration = {}
    if args.daily_traffic > 0:
        duration = estimate_duration(sample_size, args.variants, args.daily_traffic)

    table = generate_quick_reference_table(args.alpha, args.power)

    if args.json:
        result = {
            "inputs": {
                "baseline_rate": args.baseline,
                "mde_relative": args.mde,
                "mde_absolute": round(args.baseline * args.mde, 6),
                "alpha": args.alpha,
                "adjusted_alpha": round(adjusted_alpha, 6),
                "power": args.power,
                "variants": args.variants,
                "two_tailed": args.two_tailed,
            },
            "results": {
                "sample_per_variant": sample_size,
                "total_sample": sample_size * args.variants,
            },
            "quick_reference": table,
        }
        if duration:
            result["duration"] = duration
        print(json.dumps(result, indent=2))
    else:
        print(format_human_output(args, sample_size, duration, table))


if __name__ == "__main__":
    main()
