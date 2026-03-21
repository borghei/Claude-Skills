#!/usr/bin/env python3
"""Price Sensitivity Calculator - Van Westendorp Price Sensitivity Meter implementation.

Takes survey responses for the four Van Westendorp questions and calculates:
optimal price point, indifference price, acceptable range, and point of marginal
cheapness/expensiveness.

Usage:
    python price_sensitivity_calculator.py survey.json
    python price_sensitivity_calculator.py survey.json --format json
"""

import argparse
import json
import sys
from typing import Any


def calculate_cumulative_distribution(values: list[float], price_points: list[float], ascending: bool = True) -> list[float]:
    """Calculate cumulative distribution at each price point.

    Args:
        values: Raw survey responses (price values from respondents).
        price_points: The set of price points to evaluate.
        ascending: If True, cumulative from low to high (% who said this or less).
                   If False, cumulative from high to low (% who said this or more).

    Returns:
        List of cumulative percentages (0-100) at each price point.
    """
    n = len(values)
    if n == 0:
        return [0.0] * len(price_points)

    sorted_vals = sorted(values)
    result = []

    for pp in price_points:
        if ascending:
            count = sum(1 for v in sorted_vals if v <= pp)
        else:
            count = sum(1 for v in sorted_vals if v >= pp)
        result.append((count / n) * 100)

    return result


def find_intersection(x_points: list[float], y1: list[float], y2: list[float]) -> float | None:
    """Find approximate intersection point of two curves using linear interpolation."""
    for i in range(len(x_points) - 1):
        diff1 = y1[i] - y2[i]
        diff2 = y1[i + 1] - y2[i + 1]

        if diff1 == 0:
            return x_points[i]
        if diff2 == 0:
            return x_points[i + 1]

        # Sign change indicates intersection
        if (diff1 > 0 and diff2 < 0) or (diff1 < 0 and diff2 > 0):
            # Linear interpolation
            t = diff1 / (diff1 - diff2)
            return x_points[i] + t * (x_points[i + 1] - x_points[i])

    return None


def analyze_sensitivity(data: dict) -> dict:
    """Run Van Westendorp price sensitivity analysis."""
    responses = data.get("responses", [])

    if len(responses) < 10:
        return {"error": f"Need at least 10 responses for valid analysis (got {len(responses)}). Recommended: 30+."}

    # Extract the four price arrays
    too_cheap = [r["too_cheap"] for r in responses if "too_cheap" in r]
    bargain = [r["bargain"] for r in responses if "bargain" in r]
    expensive = [r["expensive"] for r in responses if "expensive" in r]
    too_expensive = [r["too_expensive"] for r in responses if "too_expensive" in r]

    if not all([too_cheap, bargain, expensive, too_expensive]):
        return {"error": "Each response must have: too_cheap, bargain, expensive, too_expensive"}

    # Validate ordering within each response
    validation_issues = []
    for i, r in enumerate(responses):
        if not all(k in r for k in ["too_cheap", "bargain", "expensive", "too_expensive"]):
            continue
        if not (r["too_cheap"] <= r["bargain"] <= r["expensive"] <= r["too_expensive"]):
            validation_issues.append(f"Response {i+1}: prices not in expected order (too_cheap <= bargain <= expensive <= too_expensive)")

    # Generate price points for analysis
    all_prices = too_cheap + bargain + expensive + too_expensive
    min_price = min(all_prices)
    max_price = max(all_prices)

    # Create fine-grained price points
    step = max((max_price - min_price) / 200, 0.01)
    price_points = []
    p = min_price
    while p <= max_price:
        price_points.append(round(p, 2))
        p += step

    # Calculate cumulative distributions
    # "Too cheap" - % who said this price or HIGHER is too cheap (descending)
    too_cheap_cum = calculate_cumulative_distribution(too_cheap, price_points, ascending=False)
    # "Bargain" - % who said this price or HIGHER is a bargain (descending)
    bargain_cum = calculate_cumulative_distribution(bargain, price_points, ascending=False)
    # "Expensive" - % who said this price or LOWER is expensive (ascending)
    expensive_cum = calculate_cumulative_distribution(expensive, price_points, ascending=True)
    # "Too expensive" - % who said this price or LOWER is too expensive (ascending)
    too_expensive_cum = calculate_cumulative_distribution(too_expensive, price_points, ascending=True)

    # Find key intersection points
    # OPP (Optimal Price Point): intersection of "too cheap" and "too expensive"
    opp = find_intersection(price_points, too_cheap_cum, too_expensive_cum)

    # IDP (Indifference Price Point): intersection of "bargain" and "expensive"
    idp = find_intersection(price_points, bargain_cum, expensive_cum)

    # PMC (Point of Marginal Cheapness): intersection of "too cheap" and "expensive"
    pmc = find_intersection(price_points, too_cheap_cum, expensive_cum)

    # PME (Point of Marginal Expensiveness): intersection of "bargain" and "too expensive"
    pme = find_intersection(price_points, bargain_cum, too_expensive_cum)

    # Summary statistics
    summary_stats = {
        "respondent_count": len(responses),
        "too_cheap_median": round(sorted(too_cheap)[len(too_cheap) // 2], 2),
        "bargain_median": round(sorted(bargain)[len(bargain) // 2], 2),
        "expensive_median": round(sorted(expensive)[len(expensive) // 2], 2),
        "too_expensive_median": round(sorted(too_expensive)[len(too_expensive) // 2], 2),
    }

    # Recommendations
    recommendations = []
    if opp:
        recommendations.append(f"Optimal Price Point (OPP): ${opp:.2f} -- the price that maximizes the number of buyers while minimizing resistance")
    if pmc and pme:
        recommendations.append(f"Acceptable Price Range: ${pmc:.2f} to ${pme:.2f} -- pricing outside this range risks losing significant market share")
    if idp:
        recommendations.append(f"Indifference Price Point: ${idp:.2f} -- equal number of respondents find this cheap vs expensive")

    if opp and pmc and pme:
        if pmc <= opp <= pme:
            recommendations.append("OPP falls within the acceptable range -- pricing model is viable")
        else:
            recommendations.append("WARNING: OPP falls outside the acceptable range -- review survey data quality")

    return {
        "key_price_points": {
            "optimal_price_point": round(opp, 2) if opp else None,
            "indifference_price_point": round(idp, 2) if idp else None,
            "point_of_marginal_cheapness": round(pmc, 2) if pmc else None,
            "point_of_marginal_expensiveness": round(pme, 2) if pme else None,
            "acceptable_range": {
                "low": round(pmc, 2) if pmc else None,
                "high": round(pme, 2) if pme else None,
            },
        },
        "summary_stats": summary_stats,
        "recommendations": recommendations,
        "validation_issues": validation_issues[:5],  # Cap at 5
        "methodology": "Van Westendorp Price Sensitivity Meter (4-question model)",
    }


def format_text(result: dict) -> str:
    """Format analysis as human-readable text."""
    lines = []

    if "error" in result:
        return f"Error: {result['error']}"

    lines.append("=" * 60)
    lines.append("VAN WESTENDORP PRICE SENSITIVITY ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    kp = result["key_price_points"]
    lines.append("-" * 40)
    lines.append("KEY PRICE POINTS")
    lines.append("-" * 40)
    lines.append(f"  Optimal Price Point (OPP):      ${kp['optimal_price_point']:>8.2f}" if kp["optimal_price_point"] else "  Optimal Price Point: Could not be calculated")
    lines.append(f"  Indifference Price (IDP):        ${kp['indifference_price_point']:>8.2f}" if kp["indifference_price_point"] else "  Indifference Price: Could not be calculated")
    lines.append(f"  Marginal Cheapness (PMC):        ${kp['point_of_marginal_cheapness']:>8.2f}" if kp["point_of_marginal_cheapness"] else "  Marginal Cheapness: Could not be calculated")
    lines.append(f"  Marginal Expensiveness (PME):    ${kp['point_of_marginal_expensiveness']:>8.2f}" if kp["point_of_marginal_expensiveness"] else "  Marginal Expensiveness: Could not be calculated")

    ar = kp.get("acceptable_range", {})
    if ar.get("low") and ar.get("high"):
        lines.append(f"\n  ACCEPTABLE RANGE: ${ar['low']:.2f} - ${ar['high']:.2f}")
    lines.append("")

    ss = result["summary_stats"]
    lines.append("-" * 40)
    lines.append(f"SURVEY SUMMARY ({ss['respondent_count']} respondents)")
    lines.append("-" * 40)
    lines.append(f"  Too Cheap median:      ${ss['too_cheap_median']:>8.2f}")
    lines.append(f"  Bargain median:        ${ss['bargain_median']:>8.2f}")
    lines.append(f"  Expensive median:      ${ss['expensive_median']:>8.2f}")
    lines.append(f"  Too Expensive median:  ${ss['too_expensive_median']:>8.2f}")
    lines.append("")

    if result["recommendations"]:
        lines.append("-" * 40)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        for rec in result["recommendations"]:
            lines.append(f"  - {rec}")
        lines.append("")

    if result["validation_issues"]:
        lines.append("-" * 40)
        lines.append("VALIDATION WARNINGS")
        lines.append("-" * 40)
        for vi in result["validation_issues"]:
            lines.append(f"  - {vi}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Van Westendorp Price Sensitivity Meter calculator."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with Van Westendorp survey responses",
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

    result = analyze_sensitivity(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
