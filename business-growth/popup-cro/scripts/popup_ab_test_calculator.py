#!/usr/bin/env python3
"""Popup A/B Test Calculator - Calculate statistical significance for popup experiments.

Takes impressions and conversions for control and variant, computes conversion rates,
relative lift, Z-score, p-value, and confidence level. Recommends ship, continue, or abandon.

Usage:
    python popup_ab_test_calculator.py test.json
    python popup_ab_test_calculator.py test.json --format json
"""

import argparse
import json
import math
import sys
from typing import Any


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    return num / den if den != 0 else default


def normal_cdf(x: float) -> float:
    """Approximate the cumulative distribution function of the standard normal.

    Uses the Abramowitz and Stegun approximation (error < 1.5e-7).
    """
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1.0 / (1.0 + 0.2316419 * x)
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    cdf = 1.0 - d * math.exp(-x * x / 2.0) * poly
    return 0.5 + sign * (cdf - 0.5)


def calculate_z_score(p1: float, p2: float, n1: int, n2: int) -> float:
    """Calculate Z-score for two-proportion Z-test."""
    p_pool = safe_divide(p1 * n1 + p2 * n2, n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1.0 / n1 + 1.0 / n2)) if p_pool > 0 and p_pool < 1 else 0
    if se == 0:
        return 0.0
    return (p2 - p1) / se


def analyze_test(data: dict) -> dict:
    """Analyze an A/B test for statistical significance."""
    tests = data.get("tests", [data]) if "tests" not in data else data["tests"]

    results = []
    for test in tests:
        control = test.get("control", {})
        variant = test.get("variant", {})

        c_impressions = control.get("impressions", 0)
        c_conversions = control.get("conversions", 0)
        v_impressions = variant.get("impressions", 0)
        v_conversions = variant.get("conversions", 0)

        c_rate = safe_divide(c_conversions, c_impressions) * 100
        v_rate = safe_divide(v_conversions, v_impressions) * 100
        absolute_lift = v_rate - c_rate
        relative_lift = safe_divide(absolute_lift, c_rate) * 100

        # Statistical significance
        c_prop = safe_divide(c_conversions, c_impressions)
        v_prop = safe_divide(v_conversions, v_impressions)
        z_score = calculate_z_score(c_prop, v_prop, c_impressions, v_impressions)
        p_value = 2 * (1 - normal_cdf(abs(z_score)))  # Two-tailed
        confidence = (1 - p_value) * 100

        # Sample size check
        min_sample = 1000  # Minimum per variant for popup tests
        sufficient_sample = c_impressions >= min_sample and v_impressions >= min_sample

        # Recommendation
        if confidence >= 95 and absolute_lift > 0 and sufficient_sample:
            recommendation = "Ship Variant"
            reason = f"Variant wins with {confidence:.1f}% confidence and +{absolute_lift:.2f}pp lift"
        elif confidence >= 95 and absolute_lift < 0 and sufficient_sample:
            recommendation = "Keep Control"
            reason = f"Control wins with {confidence:.1f}% confidence"
        elif not sufficient_sample:
            needed = max(min_sample - c_impressions, min_sample - v_impressions, 0)
            recommendation = "Continue Testing"
            reason = f"Need ~{needed:,} more impressions per variant (minimum {min_sample:,} each)"
        elif confidence < 80:
            recommendation = "Continue Testing"
            reason = f"Only {confidence:.1f}% confidence -- need more data or larger effect size"
        else:
            recommendation = "Continue Testing"
            reason = f"At {confidence:.1f}% confidence -- approaching significance but not yet actionable"

        # Check bounce rate impact
        bounce_warning = None
        c_bounce = control.get("bounce_rate_pct")
        v_bounce = variant.get("bounce_rate_pct")
        if c_bounce is not None and v_bounce is not None:
            bounce_diff = v_bounce - c_bounce
            if bounce_diff > 5:
                bounce_warning = f"Variant increases bounce rate by {bounce_diff:.1f}pp -- conversion win may be a net negative"
                if recommendation == "Ship Variant":
                    recommendation = "Investigate Further"
                    reason += f" BUT bounce rate increased {bounce_diff:.1f}pp"

        test_result = {
            "test_name": test.get("name", "Unnamed Test"),
            "control": {
                "impressions": c_impressions,
                "conversions": c_conversions,
                "conversion_rate_pct": round(c_rate, 3),
            },
            "variant": {
                "impressions": v_impressions,
                "conversions": v_conversions,
                "conversion_rate_pct": round(v_rate, 3),
            },
            "analysis": {
                "absolute_lift_pp": round(absolute_lift, 3),
                "relative_lift_pct": round(relative_lift, 2),
                "z_score": round(z_score, 4),
                "p_value": round(p_value, 6),
                "confidence_pct": round(confidence, 2),
                "sufficient_sample": sufficient_sample,
            },
            "recommendation": recommendation,
            "reason": reason,
        }

        if bounce_warning:
            test_result["bounce_warning"] = bounce_warning

        results.append(test_result)

    return {"test_results": results}


def format_text(result: dict) -> str:
    """Format test results as human-readable text."""
    lines = []

    lines.append("=" * 60)
    lines.append("POPUP A/B TEST ANALYSIS")
    lines.append("=" * 60)

    for tr in result["test_results"]:
        lines.append("")
        lines.append(f"Test: {tr['test_name']}")
        lines.append("-" * 40)

        c = tr["control"]
        v = tr["variant"]
        a = tr["analysis"]

        lines.append(f"  Control:  {c['impressions']:>8,} impressions  |  {c['conversions']:>6,} conversions  |  {c['conversion_rate_pct']:.3f}%")
        lines.append(f"  Variant:  {v['impressions']:>8,} impressions  |  {v['conversions']:>6,} conversions  |  {v['conversion_rate_pct']:.3f}%")
        lines.append("")
        lines.append(f"  Absolute Lift: {a['absolute_lift_pp']:+.3f}pp")
        lines.append(f"  Relative Lift: {a['relative_lift_pct']:+.2f}%")
        lines.append(f"  Confidence: {a['confidence_pct']:.2f}%")
        lines.append(f"  p-value: {a['p_value']:.6f}")
        lines.append(f"  Sufficient Sample: {'Yes' if a['sufficient_sample'] else 'No'}")
        lines.append("")
        lines.append(f"  >> RECOMMENDATION: {tr['recommendation']}")
        lines.append(f"     {tr['reason']}")

        if "bounce_warning" in tr:
            lines.append(f"  >> WARNING: {tr['bounce_warning']}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate statistical significance for popup A/B tests."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with A/B test data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = analyze_test(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
