#!/usr/bin/env python3
"""
Time-to-Value (TTV) Estimator

Estimate time-to-value based on onboarding steps and identify bottlenecks
that can be reduced or eliminated. Produces optimization recommendations
with projected TTV reduction.

Usage:
    python ttv_estimator.py onboarding_steps.json
    python ttv_estimator.py onboarding_steps.json --json
"""

import argparse
import json
import sys


OPTIMIZATION_STRATEGIES = {
    "setup_required": {
        "label": "Required setup before use",
        "strategy": "Reduce required setup steps, use smart defaults",
        "typical_reduction_pct": 40,
    },
    "waiting_for_data": {
        "label": "Waiting for data import/sync",
        "strategy": "Provide sample/demo data immediately",
        "typical_reduction_pct": 50,
    },
    "waiting_for_team": {
        "label": "Waiting for team members to join",
        "strategy": "Enable solo value first, then team",
        "typical_reduction_pct": 30,
    },
    "integration_required": {
        "label": "Integration with external tool required",
        "strategy": "Offer manual input as alternative",
        "typical_reduction_pct": 40,
    },
    "learning_curve": {
        "label": "Product too complex for quick win",
        "strategy": "Guided first action with templates",
        "typical_reduction_pct": 25,
    },
    "verification_required": {
        "label": "Email verification or approval needed",
        "strategy": "Defer verification to after first value",
        "typical_reduction_pct": 50,
    },
    "configuration": {
        "label": "Settings/preferences configuration",
        "strategy": "Use smart defaults, allow customization later",
        "typical_reduction_pct": 35,
    },
    "content_creation": {
        "label": "User must create content from scratch",
        "strategy": "Provide templates and pre-filled examples",
        "typical_reduction_pct": 30,
    },
}


def estimate_ttv(data: dict) -> dict:
    """Estimate TTV and identify optimization opportunities."""
    steps = data.get("steps", [])
    if not steps:
        return {"error": "No onboarding steps provided."}

    total_minutes = 0
    step_analysis = []
    optimizations = []

    for i, step in enumerate(steps):
        name = step.get("name", f"Step {i + 1}")
        minutes = step.get("estimated_minutes", 0)
        bottleneck = step.get("bottleneck_type", "")
        is_required = step.get("required", True)
        can_be_deferred = step.get("can_be_deferred", False)
        blocks_value = step.get("blocks_value", True)

        total_minutes += minutes

        # Optimization potential
        optimized_minutes = minutes
        optimization_note = ""

        if bottleneck and bottleneck in OPTIMIZATION_STRATEGIES:
            opt = OPTIMIZATION_STRATEGIES[bottleneck]
            reduction = minutes * (opt["typical_reduction_pct"] / 100.0)
            optimized_minutes = max(0.5, minutes - reduction)
            optimization_note = opt["strategy"]

            optimizations.append({
                "step": name,
                "current_minutes": minutes,
                "optimized_minutes": round(optimized_minutes, 1),
                "reduction_minutes": round(reduction, 1),
                "strategy": opt["strategy"],
                "bottleneck_type": opt["label"],
            })
        elif can_be_deferred and not blocks_value:
            optimized_minutes = 0
            optimization_note = "Defer to after first value delivery"
            optimizations.append({
                "step": name,
                "current_minutes": minutes,
                "optimized_minutes": 0,
                "reduction_minutes": minutes,
                "strategy": "Defer to after first value",
                "bottleneck_type": "Deferrable step",
            })

        step_analysis.append({
            "step": i + 1,
            "name": name,
            "estimated_minutes": minutes,
            "optimized_minutes": round(optimized_minutes, 1),
            "bottleneck_type": bottleneck,
            "required": is_required,
            "can_be_deferred": can_be_deferred,
            "blocks_value": blocks_value,
            "optimization": optimization_note,
        })

    # Calculate optimized TTV
    optimized_total = sum(s["optimized_minutes"] for s in step_analysis)
    reduction_pct = ((total_minutes - optimized_total) / total_minutes * 100) if total_minutes > 0 else 0

    # Benchmarks
    if total_minutes <= 5:
        current_rating = "EXCELLENT"
    elif total_minutes <= 15:
        current_rating = "GOOD"
    elif total_minutes <= 30:
        current_rating = "NEEDS_IMPROVEMENT"
    else:
        current_rating = "CRITICAL"

    if optimized_total <= 5:
        optimized_rating = "EXCELLENT"
    elif optimized_total <= 15:
        optimized_rating = "GOOD"
    elif optimized_total <= 30:
        optimized_rating = "NEEDS_IMPROVEMENT"
    else:
        optimized_rating = "CRITICAL"

    # Sort optimizations by reduction (biggest first)
    optimizations.sort(key=lambda x: x["reduction_minutes"], reverse=True)

    return {
        "current_ttv": {
            "total_minutes": round(total_minutes, 1),
            "total_steps": len(steps),
            "required_steps": sum(1 for s in step_analysis if s["required"]),
            "deferrable_steps": sum(1 for s in step_analysis if s["can_be_deferred"]),
            "rating": current_rating,
        },
        "optimized_ttv": {
            "total_minutes": round(optimized_total, 1),
            "reduction_minutes": round(total_minutes - optimized_total, 1),
            "reduction_pct": round(reduction_pct, 1),
            "rating": optimized_rating,
        },
        "step_analysis": step_analysis,
        "top_optimizations": optimizations[:5],
        "recommendations": _generate_recommendations(total_minutes, optimized_total, optimizations, step_analysis),
    }


def _generate_recommendations(current: float, optimized: float,
                              optimizations: list, steps: list) -> list:
    """Generate recommendations."""
    recs = []

    if current > 30:
        recs.append({
            "priority": "CRITICAL",
            "recommendation": f"TTV is {current:.0f} minutes. Products exceeding 30-minute TTV experience 3x higher abandonment. Target under 15 minutes.",
        })
    elif current > 15:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"TTV is {current:.0f} minutes. Reducing to under 5 minutes typically increases 7-day retention by 25-40%.",
        })

    if optimizations:
        top = optimizations[0]
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Biggest opportunity: '{top['step']}' -- {top['strategy']}. Saves {top['reduction_minutes']:.0f} minutes.",
        })

    deferrable = [s for s in steps if s["can_be_deferred"] and s["blocks_value"]]
    if deferrable:
        names = ", ".join(s["name"] for s in deferrable[:3])
        recs.append({
            "priority": "MEDIUM",
            "recommendation": f"Steps that can be deferred: {names}. Move these after first value delivery.",
        })

    recs.append({
        "priority": "MEDIUM",
        "recommendation": "Deliver a 'quick win' within the first 3 minutes. Pre-populate inputs, use smart defaults, celebrate the output.",
    })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("TIME-TO-VALUE (TTV) ESTIMATOR")
    lines.append("=" * 60)

    ct = result["current_ttv"]
    lines.append(f"\n--- Current TTV ---")
    lines.append(f"Total Time:     {ct['total_minutes']:>8.1f} minutes")
    lines.append(f"Total Steps:    {ct['total_steps']:>8d}")
    lines.append(f"Required Steps: {ct['required_steps']:>8d}")
    lines.append(f"Deferrable:     {ct['deferrable_steps']:>8d}")
    lines.append(f"Rating:         {ct['rating']:>8}")

    ot = result["optimized_ttv"]
    lines.append(f"\n--- Optimized TTV ---")
    lines.append(f"Projected Time: {ot['total_minutes']:>8.1f} minutes")
    lines.append(f"Reduction:      {ot['reduction_minutes']:>8.1f} minutes ({ot['reduction_pct']:.0f}%)")
    lines.append(f"Rating:         {ot['rating']:>8}")

    lines.append(f"\n--- Step-by-Step Analysis ---")
    lines.append(f"{'Step':<25} {'Current':>8} {'Optimized':>10} {'Bottleneck':<20} {'Strategy'}")
    for s in result["step_analysis"]:
        bn = s["bottleneck_type"][:18] if s["bottleneck_type"] else "-"
        opt = s["optimization"][:40] if s["optimization"] else "-"
        lines.append(
            f"{s['name']:<25} {s['estimated_minutes']:>7.1f}m {s['optimized_minutes']:>9.1f}m "
            f"{bn:<20} {opt}"
        )

    if result["top_optimizations"]:
        lines.append(f"\n--- Top Optimizations ---")
        for o in result["top_optimizations"]:
            lines.append(f"  {o['step']}: {o['strategy']} (saves {o['reduction_minutes']:.0f}min)")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Estimate time-to-value and identify onboarding bottlenecks."
    )
    parser.add_argument("input_file", help="JSON file with onboarding steps and time estimates")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = estimate_ttv(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
