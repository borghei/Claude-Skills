#!/usr/bin/env python3
"""Upgrade Funnel Analyzer - Analyze upgrade funnel conversion step by step.

Calculates stage-over-stage conversion rates, identifies highest-drop steps,
benchmarks against industry targets, and generates improvement recommendations.

Usage:
    python upgrade_funnel_analyzer.py funnel.json
    python upgrade_funnel_analyzer.py funnel.json --format json
"""

import argparse
import json
import sys
from typing import Any


# Industry benchmarks for each funnel stage
BENCHMARKS = {
    "paywall_impression_to_click": {"target": 10.0, "good": 5.0, "label": "Paywall CTR"},
    "click_to_plan_select": {"target": 80.0, "good": 60.0, "label": "Plan Selection"},
    "plan_select_to_payment_start": {"target": 75.0, "good": 55.0, "label": "Payment Start"},
    "payment_start_to_complete": {"target": 70.0, "good": 45.0, "label": "Payment Complete"},
    "complete_to_30day_retain": {"target": 90.0, "good": 80.0, "label": "30-Day Retention"},
}


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    if denominator == 0:
        return default
    return numerator / denominator


def rate_metric(value: float, target: float, good: float) -> str:
    """Rate a metric against benchmarks."""
    if value >= target:
        return "Excellent"
    elif value >= good:
        return "Good"
    elif value >= good * 0.6:
        return "Needs Improvement"
    else:
        return "Critical"


def analyze_funnel(data: dict) -> dict:
    """Analyze upgrade funnel step by step."""
    steps = data.get("steps", [])

    if len(steps) < 2:
        return {"error": "At least 2 funnel steps required for analysis"}

    # Calculate step-over-step conversion
    step_analysis = []
    overall_conversion = safe_divide(steps[-1].get("users", 0), steps[0].get("users", 0)) * 100

    worst_drop_step = None
    worst_drop_rate = 100.0

    for i in range(len(steps) - 1):
        current = steps[i]
        next_step = steps[i + 1]

        current_users = current.get("users", 0)
        next_users = next_step.get("users", 0)

        conversion_rate = safe_divide(next_users, current_users) * 100
        drop_off_rate = 100 - conversion_rate
        users_lost = current_users - next_users

        # Find benchmark for this transition
        step_key = f"{current.get('name', '').lower().replace(' ', '_')}_to_{next_step.get('name', '').lower().replace(' ', '_')}"
        benchmark = BENCHMARKS.get(step_key, {})

        rating = "N/A"
        if benchmark:
            rating = rate_metric(conversion_rate, benchmark.get("target", 100), benchmark.get("good", 50))

        step_data = {
            "from": current.get("name", f"Step {i+1}"),
            "to": next_step.get("name", f"Step {i+2}"),
            "from_users": current_users,
            "to_users": next_users,
            "conversion_rate_pct": round(conversion_rate, 2),
            "drop_off_rate_pct": round(drop_off_rate, 2),
            "users_lost": users_lost,
            "rating": rating,
        }

        if benchmark:
            step_data["benchmark_target"] = benchmark.get("target")
            step_data["benchmark_good"] = benchmark.get("good")
            step_data["gap_to_target"] = round(benchmark.get("target", 0) - conversion_rate, 2)

        step_analysis.append(step_data)

        if conversion_rate < worst_drop_rate:
            worst_drop_rate = conversion_rate
            worst_drop_step = step_data

    # Generate recommendations
    recommendations = generate_recommendations(step_analysis)

    # Revenue impact estimation
    revenue_impact = None
    if data.get("avg_revenue_per_upgrade"):
        avg_rev = data["avg_revenue_per_upgrade"]
        if worst_drop_step and worst_drop_step.get("gap_to_target", 0) > 0:
            potential_extra_users = int(
                worst_drop_step["from_users"] * (worst_drop_step.get("gap_to_target", 0) / 100)
            )
            # Apply downstream conversion to estimate actual additional upgrades
            downstream_rate = safe_divide(steps[-1].get("users", 0), worst_drop_step["to_users"]) if worst_drop_step["to_users"] > 0 else 0
            potential_upgrades = int(potential_extra_users * downstream_rate)
            revenue_impact = {
                "potential_extra_users_at_bottleneck": potential_extra_users,
                "estimated_additional_upgrades": potential_upgrades,
                "estimated_monthly_revenue": round(potential_upgrades * avg_rev, 2),
                "estimated_annual_revenue": round(potential_upgrades * avg_rev * 12, 2),
            }

    return {
        "summary": {
            "total_steps": len(steps),
            "top_of_funnel_users": steps[0].get("users", 0),
            "bottom_of_funnel_users": steps[-1].get("users", 0),
            "overall_conversion_pct": round(overall_conversion, 2),
            "biggest_drop_step": worst_drop_step["from"] + " -> " + worst_drop_step["to"] if worst_drop_step else "N/A",
            "biggest_drop_rate_pct": round(100 - worst_drop_rate, 2) if worst_drop_step else 0,
        },
        "step_analysis": step_analysis,
        "recommendations": recommendations,
        "revenue_impact": revenue_impact,
    }


def generate_recommendations(steps: list[dict]) -> list[dict]:
    """Generate prioritized recommendations based on funnel analysis."""
    recs = []

    for step in steps:
        conversion = step["conversion_rate_pct"]
        from_name = step["from"].lower()
        to_name = step["to"].lower()

        if conversion < 5 and "impression" in from_name and "click" in to_name:
            recs.append({
                "priority": "Critical",
                "step": f"{step['from']} -> {step['to']}",
                "issue": f"Paywall CTR at {conversion}% is critically low",
                "actions": [
                    "Delay paywall trigger until after activation event",
                    "Switch to outcome-based headline copy",
                    "Add feature preview or blurred screenshot above CTA",
                    "Test soft gate (preview + lock) vs hard gate (block + explain)",
                ],
            })
        elif conversion < 50 and "payment" in to_name:
            recs.append({
                "priority": "High",
                "step": f"{step['from']} -> {step['to']}",
                "issue": f"Payment conversion at {conversion}% indicates high friction",
                "actions": [
                    "Keep upgrade flow in-context (modal, not redirect)",
                    "Pre-fill all known user information",
                    "Add saved payment methods and one-click upgrade",
                    "Show price clearly before payment step",
                ],
            })
        elif step.get("gap_to_target", 0) > 10:
            recs.append({
                "priority": "Medium",
                "step": f"{step['from']} -> {step['to']}",
                "issue": f"Conversion at {conversion}% is {step['gap_to_target']}pp below target",
                "actions": [
                    f"Investigate user behavior between {step['from']} and {step['to']}",
                    "Run qualitative user research on this step",
                    "A/B test copy, layout, and CTA variations",
                ],
            })

    # Sort by priority
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    recs.sort(key=lambda r: priority_order.get(r["priority"], 99))

    return recs


def format_text(result: dict) -> str:
    """Format funnel analysis as human-readable text."""
    lines = []

    if "error" in result:
        return f"Error: {result['error']}"

    summary = result["summary"]
    lines.append("=" * 60)
    lines.append("UPGRADE FUNNEL ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Overall Conversion: {summary['overall_conversion_pct']}%")
    lines.append(f"Top of Funnel: {summary['top_of_funnel_users']:,} users")
    lines.append(f"Bottom of Funnel: {summary['bottom_of_funnel_users']:,} users")
    lines.append(f"Biggest Drop: {summary['biggest_drop_step']} ({summary['biggest_drop_rate_pct']}% drop)")
    lines.append("")

    lines.append("-" * 40)
    lines.append("STEP-BY-STEP ANALYSIS")
    lines.append("-" * 40)
    for step in result["step_analysis"]:
        lines.append(f"\n{step['from']} -> {step['to']}")
        lines.append(f"  Users: {step['from_users']:,} -> {step['to_users']:,}")
        lines.append(f"  Conversion: {step['conversion_rate_pct']}%  |  Drop-off: {step['drop_off_rate_pct']}%  |  Lost: {step['users_lost']:,}")
        lines.append(f"  Rating: {step['rating']}")
        if "benchmark_target" in step:
            lines.append(f"  Benchmark: {step['benchmark_target']}% target  |  Gap: {step['gap_to_target']}pp")

    if result["recommendations"]:
        lines.append("")
        lines.append("-" * 40)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        for rec in result["recommendations"]:
            lines.append(f"\n[{rec['priority']}] {rec['step']}")
            lines.append(f"  Issue: {rec['issue']}")
            for action in rec["actions"]:
                lines.append(f"  - {action}")

    if result.get("revenue_impact"):
        ri = result["revenue_impact"]
        lines.append("")
        lines.append("-" * 40)
        lines.append("REVENUE IMPACT ESTIMATE")
        lines.append("-" * 40)
        lines.append(f"Potential extra users at bottleneck: {ri['potential_extra_users_at_bottleneck']:,}")
        lines.append(f"Estimated additional upgrades: {ri['estimated_additional_upgrades']:,}")
        lines.append(f"Estimated monthly revenue: ${ri['estimated_monthly_revenue']:,.2f}")
        lines.append(f"Estimated annual revenue: ${ri['estimated_annual_revenue']:,.2f}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze upgrade funnel conversion step by step."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with funnel step data",
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

    result = analyze_funnel(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
