#!/usr/bin/env python3
"""
A/B Test Sample Size Calculator

Calculates required sample sizes for statistical significance in A/B tests.
Supports conversion rate (proportion) tests with configurable significance
level, power, and minimum detectable effect.

Usage:
    python sample_size_calculator.py --baseline 0.05 --mde 0.10
    python sample_size_calculator.py --baseline 0.05 --mde 0.10 --power 0.90
    python sample_size_calculator.py --baseline 0.05 --mde 0.10 --daily-traffic 5000
    python sample_size_calculator.py --baseline 0.05 --mde 0.10 --format json
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional, Tuple


# Standard normal distribution quantiles (using rational approximation)
def norm_ppf(p: float) -> float:
    """Inverse normal CDF (percent point function) using rational approximation.
    Abramowitz and Stegun approximation 26.2.23. Accurate to ~4.5e-4."""
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1 exclusive")
    if p < 0.5:
        return -norm_ppf(1 - p)

    t = math.sqrt(-2 * math.log(1 - p))
    # Coefficients for rational approximation
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t**2) / (1 + d1 * t + d2 * t**2 + d3 * t**3)


def norm_cdf(x: float) -> float:
    """Standard normal CDF using error function approximation."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def calculate_sample_size(
    baseline: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
    variants: int = 2,
) -> Dict[str, Any]:
    """
    Calculate required sample size per variant for a proportion test.

    Args:
        baseline: Baseline conversion rate (e.g., 0.05 for 5%)
        mde_relative: Minimum detectable effect as relative change (e.g., 0.10 for 10% lift)
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.80)
        two_sided: Whether to use two-sided test (default True)
        variants: Number of variants including control (default 2)
    """
    # Calculate treatment rate
    absolute_effect = baseline * mde_relative
    treatment_rate = baseline + absolute_effect

    if treatment_rate <= 0 or treatment_rate >= 1:
        return {"error": f"Treatment rate ({treatment_rate}) must be between 0 and 1"}

    # Z-scores
    if two_sided:
        z_alpha = norm_ppf(1 - alpha / 2)
    else:
        z_alpha = norm_ppf(1 - alpha)
    z_beta = norm_ppf(power)

    # Sample size formula for two-proportion z-test
    p1 = baseline
    p2 = treatment_rate
    p_bar = (p1 + p2) / 2

    numerator = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) +
                 z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denominator = (p1 - p2) ** 2

    n_per_variant = math.ceil(numerator / denominator)
    n_total = n_per_variant * variants

    return {
        "baseline_rate": baseline,
        "treatment_rate": round(treatment_rate, 6),
        "absolute_effect": round(absolute_effect, 6),
        "relative_effect_pct": round(mde_relative * 100, 2),
        "significance_level": alpha,
        "power": power,
        "two_sided": two_sided,
        "variants": variants,
        "sample_per_variant": n_per_variant,
        "total_sample": n_total,
        "z_alpha": round(z_alpha, 4),
        "z_beta": round(z_beta, 4),
    }


def calculate_duration(total_sample: int, daily_traffic: int,
                       allocation_pct: float = 1.0) -> Dict[str, Any]:
    """Calculate test duration from sample size and traffic."""
    effective_daily = daily_traffic * allocation_pct
    if effective_daily <= 0:
        return {"error": "Effective daily traffic must be positive"}

    days_needed = math.ceil(total_sample / effective_daily)
    weeks_needed = math.ceil(days_needed / 7)

    # Minimum recommended duration (2 full weeks for day-of-week effects)
    min_days = 14
    recommended_days = max(days_needed, min_days)

    return {
        "daily_traffic": daily_traffic,
        "allocation_pct": allocation_pct,
        "effective_daily_traffic": int(effective_daily),
        "days_needed": days_needed,
        "weeks_needed": weeks_needed,
        "recommended_days": recommended_days,
        "recommended_weeks": math.ceil(recommended_days / 7),
    }


def sensitivity_table(baseline: float, alpha: float, power: float,
                      mde_values: Optional[List[float]] = None) -> List[Dict[str, Any]]:
    """Generate sensitivity table across different MDE values."""
    if mde_values is None:
        mde_values = [0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]

    rows = []
    for mde in mde_values:
        result = calculate_sample_size(baseline, mde, alpha, power)
        if "error" not in result:
            rows.append({
                "mde_pct": round(mde * 100, 1),
                "absolute_effect": round(baseline * mde, 6),
                "treatment_rate": round(baseline * (1 + mde), 6),
                "sample_per_variant": result["sample_per_variant"],
                "total_sample": result["total_sample"],
            })
    return rows


def power_table(baseline: float, mde_relative: float, alpha: float,
                power_values: Optional[List[float]] = None) -> List[Dict[str, Any]]:
    """Generate table across different power levels."""
    if power_values is None:
        power_values = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]

    rows = []
    for pwr in power_values:
        result = calculate_sample_size(baseline, mde_relative, alpha, pwr)
        if "error" not in result:
            rows.append({
                "power_pct": round(pwr * 100, 0),
                "sample_per_variant": result["sample_per_variant"],
                "total_sample": result["total_sample"],
            })
    return rows


def print_human(result: Dict, duration: Optional[Dict], sens_table: List[Dict],
                pwr_table: List[Dict]) -> None:
    """Print results in human-readable format."""
    print("=" * 60)
    print("  A/B Test Sample Size Calculator")
    print("=" * 60)

    if "error" in result:
        print(f"\n  Error: {result['error']}")
        return

    print(f"\n  --- Test Parameters ---")
    print(f"  Baseline Rate:       {result['baseline_rate']*100:.2f}%")
    print(f"  Treatment Rate:      {result['treatment_rate']*100:.2f}%")
    print(f"  Relative MDE:        {result['relative_effect_pct']:.1f}%")
    print(f"  Absolute Effect:     {result['absolute_effect']*100:.3f}pp")
    print(f"  Significance Level:  {result['significance_level']*100:.0f}% (alpha)")
    print(f"  Statistical Power:   {result['power']*100:.0f}%")
    print(f"  Test Type:           {'Two-sided' if result['two_sided'] else 'One-sided'}")
    print(f"  Variants:            {result['variants']}")

    print(f"\n  --- Required Sample Size ---")
    print(f"  Per Variant:         {result['sample_per_variant']:,}")
    print(f"  Total:               {result['total_sample']:,}")

    if duration and "error" not in duration:
        print(f"\n  --- Duration Estimate ---")
        print(f"  Daily Traffic:       {duration['daily_traffic']:,}")
        if duration["allocation_pct"] < 1:
            print(f"  Traffic Allocation:  {duration['allocation_pct']*100:.0f}%")
            print(f"  Effective Daily:     {duration['effective_daily_traffic']:,}")
        print(f"  Days Needed:         {duration['days_needed']}")
        print(f"  Recommended:         {duration['recommended_days']} days ({duration['recommended_weeks']} weeks)")
        if duration['recommended_days'] > duration['days_needed']:
            print(f"  (Extended to {duration['recommended_days']} days minimum for day-of-week coverage)")

    # Sensitivity table
    if sens_table:
        print(f"\n  --- Sensitivity: Sample Size by MDE ---")
        print(f"  {'MDE':>6} {'Abs Effect':>11} {'Treatment':>10} {'Per Variant':>12} {'Total':>10}")
        print(f"  {'-'*6} {'-'*11} {'-'*10} {'-'*12} {'-'*10}")
        for row in sens_table:
            current = " <--" if abs(row["mde_pct"] - result["relative_effect_pct"]) < 0.01 else ""
            print(f"  {row['mde_pct']:>5.1f}% {row['absolute_effect']*100:>10.3f}pp "
                  f"{row['treatment_rate']*100:>9.2f}% {row['sample_per_variant']:>11,} "
                  f"{row['total_sample']:>9,}{current}")

    # Power table
    if pwr_table:
        print(f"\n  --- Sensitivity: Sample Size by Power ---")
        print(f"  {'Power':>6} {'Per Variant':>12} {'Total':>10}")
        print(f"  {'-'*6} {'-'*12} {'-'*10}")
        for row in pwr_table:
            current = " <--" if abs(row["power_pct"] - result["power"] * 100) < 0.01 else ""
            print(f"  {row['power_pct']:>5.0f}% {row['sample_per_variant']:>11,} "
                  f"{row['total_sample']:>9,}{current}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Calculate required sample sizes for A/B test statistical significance"
    )
    parser.add_argument("--baseline", type=float, required=True,
                        help="Baseline conversion rate (e.g., 0.05 for 5%%)")
    parser.add_argument("--mde", type=float, required=True,
                        help="Minimum detectable effect as relative change (e.g., 0.10 for 10%% lift)")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="Significance level (default: 0.05)")
    parser.add_argument("--power", type=float, default=0.80,
                        help="Statistical power (default: 0.80)")
    parser.add_argument("--daily-traffic", type=int, help="Daily traffic for duration estimation")
    parser.add_argument("--allocation", type=float, default=1.0,
                        help="Fraction of traffic allocated to test (default: 1.0)")
    parser.add_argument("--one-sided", action="store_true", help="Use one-sided test")
    parser.add_argument("--variants", type=int, default=2, help="Number of variants (default: 2)")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    args = parser.parse_args()

    result = calculate_sample_size(
        baseline=args.baseline,
        mde_relative=args.mde,
        alpha=args.alpha,
        power=args.power,
        two_sided=not args.one_sided,
        variants=args.variants,
    )

    duration = None
    if args.daily_traffic:
        duration = calculate_duration(result["total_sample"], args.daily_traffic, args.allocation)

    sens = sensitivity_table(args.baseline, args.alpha, args.power)
    pwr = power_table(args.baseline, args.mde, args.alpha)

    if args.format == "json":
        output = {"sample_size": result}
        if duration:
            output["duration"] = duration
        output["sensitivity_by_mde"] = sens
        output["sensitivity_by_power"] = pwr
        print(json.dumps(output, indent=2))
    else:
        print_human(result, duration, sens, pwr)


if __name__ == "__main__":
    main()
