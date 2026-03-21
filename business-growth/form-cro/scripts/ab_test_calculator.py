#!/usr/bin/env python3
"""
A/B Test Calculator

Calculate A/B test sample size, duration, and statistical significance
for form optimization experiments. Uses standard statistical formulas
for two-proportion z-test.

Usage:
    python ab_test_calculator.py --baseline 25 --lift 10 --traffic 500
    python ab_test_calculator.py --baseline 25 --lift 10 --traffic 500 --json
"""

import argparse
import json
import math
import sys


def norm_ppf(p: float) -> float:
    """Approximate inverse normal CDF (percent-point function).

    Uses Abramowitz and Stegun approximation 26.2.23.
    Accurate to ~4.5e-4 for 0 < p < 1.
    """
    if p <= 0 or p >= 1:
        return 0.0

    if p < 0.5:
        sign = -1
        p = 1 - p
    else:
        sign = 1
        p = p

    t = math.sqrt(-2.0 * math.log(1.0 - p))

    # Rational approximation
    c0 = 2.515517
    c1 = 0.802853
    c2 = 0.010328
    d1 = 1.432788
    d2 = 0.189269
    d3 = 0.001308

    numerator = c0 + c1 * t + c2 * t * t
    denominator = 1.0 + d1 * t + d2 * t * t + d3 * t * t * t

    result = sign * (t - numerator / denominator)
    return result


def calculate_sample_size(baseline_rate: float, min_detectable_lift: float,
                          confidence: float = 0.95, power: float = 0.80) -> int:
    """Calculate required sample size per variant.

    Uses the formula for two-proportion z-test:
    n = (Z_alpha/2 + Z_beta)^2 * (p1(1-p1) + p2(1-p2)) / (p2 - p1)^2
    """
    p1 = baseline_rate / 100.0
    relative_lift = min_detectable_lift / 100.0
    p2 = p1 * (1 + relative_lift)

    if p2 >= 1.0:
        p2 = 0.99
    if p1 == p2:
        return 0

    alpha = 1 - confidence
    z_alpha = norm_ppf(1 - alpha / 2)
    z_beta = norm_ppf(power)

    numerator = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    denominator = (p2 - p1) ** 2

    if denominator == 0:
        return 0

    n = math.ceil(numerator / denominator)
    return n


def calculate_test(baseline: float, lift: float, daily_traffic: int,
                   confidence: float) -> dict:
    """Calculate complete A/B test plan."""
    sample_per_variant = calculate_sample_size(baseline, lift, confidence / 100.0)
    total_sample = sample_per_variant * 2

    # Duration calculation
    traffic_per_variant = daily_traffic / 2  # Split traffic
    if traffic_per_variant > 0:
        days_needed = math.ceil(sample_per_variant / traffic_per_variant)
    else:
        days_needed = float('inf')

    # Minimum 14 days for business cycle coverage
    days_needed = max(14, days_needed)
    weeks_needed = math.ceil(days_needed / 7)

    # Expected conversion rates
    expected_variant_rate = baseline * (1 + lift / 100.0)

    # Conversions needed
    min_conversions_per_variant = max(200, math.ceil(sample_per_variant * (baseline / 100.0)))

    # Risk assessment
    if daily_traffic < 100:
        traffic_risk = "HIGH -- low traffic may require 2+ months"
    elif daily_traffic < 500:
        traffic_risk = "MEDIUM -- adequate for testing major changes"
    else:
        traffic_risk = "LOW -- sufficient traffic for reliable results"

    # Alternative lift scenarios
    lift_scenarios = []
    for alt_lift in [5, 10, 15, 20, 25, 30]:
        alt_sample = calculate_sample_size(baseline, alt_lift, confidence / 100.0)
        alt_days = max(14, math.ceil(alt_sample / max(1, traffic_per_variant)))
        lift_scenarios.append({
            "lift_pct": alt_lift,
            "sample_per_variant": alt_sample,
            "days_needed": alt_days,
            "weeks_needed": math.ceil(alt_days / 7),
        })

    return {
        "inputs": {
            "baseline_rate_pct": baseline,
            "minimum_detectable_lift_pct": lift,
            "daily_traffic": daily_traffic,
            "confidence_level_pct": confidence,
            "statistical_power_pct": 80,
        },
        "test_plan": {
            "sample_per_variant": sample_per_variant,
            "total_sample_needed": total_sample,
            "days_needed": days_needed,
            "weeks_needed": weeks_needed,
            "min_conversions_per_variant": min_conversions_per_variant,
            "expected_variant_rate_pct": round(expected_variant_rate, 2),
        },
        "traffic_assessment": {
            "daily_traffic": daily_traffic,
            "traffic_per_variant": int(traffic_per_variant),
            "risk_level": traffic_risk,
        },
        "lift_scenarios": lift_scenarios,
        "recommendations": _generate_recommendations(days_needed, daily_traffic, lift, baseline),
    }


def _generate_recommendations(days: int, traffic: int, lift: float, baseline: float) -> list:
    """Generate test recommendations."""
    recs = []

    if days > 60:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Test requires {days} days. Consider testing a bigger change (higher expected lift) to reduce required sample size.",
        })

    if traffic < 200:
        recs.append({
            "priority": "HIGH",
            "recommendation": "Low daily traffic. Focus on high-impact changes (field removal, CTA rewrite) rather than subtle tweaks.",
        })

    if lift < 10:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": "Detecting small lifts requires large samples. Test bigger changes or accept a higher minimum detectable lift.",
        })

    recs.append({
        "priority": "MEDIUM",
        "recommendation": "Run test for full business cycles (minimum 2 weeks). Avoid ending on weekends or holidays.",
    })

    recs.append({
        "priority": "MEDIUM",
        "recommendation": f"Track downstream metrics (lead quality, SQL rate) not just form completion rate. A test that increases quantity but decreases quality is not a win.",
    })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("A/B TEST CALCULATOR")
    lines.append("=" * 60)

    inp = result["inputs"]
    lines.append(f"\nBaseline Rate:      {inp['baseline_rate_pct']:>8.1f}%")
    lines.append(f"Min Detectable Lift:{inp['minimum_detectable_lift_pct']:>8.1f}%")
    lines.append(f"Daily Traffic:      {inp['daily_traffic']:>8d}")
    lines.append(f"Confidence:         {inp['confidence_level_pct']:>8.0f}%")
    lines.append(f"Power:              {inp['statistical_power_pct']:>8d}%")

    tp = result["test_plan"]
    lines.append(f"\n--- Test Plan ---")
    lines.append(f"Sample per Variant:   {tp['sample_per_variant']:>8,d}")
    lines.append(f"Total Sample Needed:  {tp['total_sample_needed']:>8,d}")
    lines.append(f"Days Needed:          {tp['days_needed']:>8d}")
    lines.append(f"Weeks Needed:         {tp['weeks_needed']:>8d}")
    lines.append(f"Expected Variant Rate:{tp['expected_variant_rate_pct']:>8.2f}%")

    ta = result["traffic_assessment"]
    lines.append(f"\n--- Traffic Assessment ---")
    lines.append(f"Risk Level: {ta['risk_level']}")

    lines.append(f"\n--- Lift Scenarios ---")
    lines.append(f"{'Lift':>6}  {'Sample/Var':>12}  {'Days':>6}  {'Weeks':>6}")
    for s in result["lift_scenarios"]:
        lines.append(f"{s['lift_pct']:>5d}%  {s['sample_per_variant']:>12,d}  {s['days_needed']:>6d}  {s['weeks_needed']:>6d}")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate A/B test sample size, duration, and statistical significance."
    )
    parser.add_argument("--baseline", type=float, required=True,
                        help="Current conversion rate as percentage (e.g., 25 for 25%%)")
    parser.add_argument("--lift", type=float, required=True,
                        help="Minimum detectable lift as percentage (e.g., 10 for 10%% relative lift)")
    parser.add_argument("--traffic", type=int, required=True,
                        help="Daily traffic (visitors per day)")
    parser.add_argument("--confidence", type=float, default=95,
                        help="Confidence level as percentage (default: 95)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if args.baseline <= 0 or args.baseline >= 100:
        print("Error: --baseline must be between 0 and 100.", file=sys.stderr)
        sys.exit(1)
    if args.lift <= 0:
        print("Error: --lift must be positive.", file=sys.stderr)
        sys.exit(1)
    if args.traffic <= 0:
        print("Error: --traffic must be positive.", file=sys.stderr)
        sys.exit(1)

    result = calculate_test(args.baseline, args.lift, args.traffic, args.confidence)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
