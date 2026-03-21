#!/usr/bin/env python3
"""
Activation Funnel Analyzer

Analyze an onboarding activation funnel to identify the biggest drop-off
points and estimate the impact of fixing each step.

Usage:
    python activation_funnel_analyzer.py funnel_data.json
    python activation_funnel_analyzer.py funnel_data.json --json
"""

import argparse
import json
import sys


def analyze_funnel(data: dict) -> dict:
    """Analyze activation funnel."""
    steps = data.get("steps", [])
    if not steps or len(steps) < 2:
        return {"error": "At least 2 funnel steps are required."}

    total_users = steps[0].get("users", 0)
    if total_users == 0:
        return {"error": "First step must have users > 0."}

    step_results = []
    biggest_drop_idx = 0
    biggest_drop_pct = 0

    for i, step in enumerate(steps):
        name = step.get("name", f"Step {i + 1}")
        users = step.get("users", 0)
        pct_of_total = (users / total_users * 100) if total_users > 0 else 0

        if i == 0:
            drop_from_prev = 0
            drop_pct = 0
            conversion_from_prev = 100
        else:
            prev_users = steps[i - 1].get("users", 0)
            drop_from_prev = prev_users - users
            drop_pct = (drop_from_prev / prev_users * 100) if prev_users > 0 else 0
            conversion_from_prev = (users / prev_users * 100) if prev_users > 0 else 0

            if drop_from_prev > biggest_drop_pct:
                biggest_drop_pct = drop_from_prev
                biggest_drop_idx = i

        step_results.append({
            "step": i + 1,
            "name": name,
            "users": users,
            "pct_of_total": round(pct_of_total, 1),
            "drop_from_previous": drop_from_prev,
            "drop_pct": round(drop_pct, 1),
            "conversion_from_previous_pct": round(conversion_from_prev, 1),
        })

    # Overall funnel metrics
    final_users = steps[-1].get("users", 0)
    overall_rate = (final_users / total_users * 100) if total_users > 0 else 0

    # Impact analysis: what if we improve each step by 20%?
    impact_analysis = []
    for i in range(1, len(steps)):
        step_name = steps[i].get("name", f"Step {i + 1}")
        current_drop = step_results[i]["drop_from_previous"]
        recovered_users = int(current_drop * 0.20)  # 20% improvement

        # Cascade impact (simplified: additional users flow through remaining steps)
        remaining_conversion = 1.0
        for j in range(i + 1, len(steps)):
            prev_u = steps[j - 1].get("users", 1)
            curr_u = steps[j].get("users", 0)
            if prev_u > 0:
                remaining_conversion *= (curr_u / prev_u)

        additional_activations = int(recovered_users * remaining_conversion)

        impact_analysis.append({
            "step": step_name,
            "current_drop": current_drop,
            "users_recovered_at_20pct_improvement": recovered_users,
            "additional_activations": additional_activations,
            "impact_rank": additional_activations,
        })

    impact_analysis.sort(key=lambda x: x["impact_rank"], reverse=True)

    # Biggest bottleneck
    bottleneck = step_results[biggest_drop_idx] if biggest_drop_idx > 0 else None

    return {
        "summary": {
            "total_entry_users": total_users,
            "final_activated_users": final_users,
            "overall_activation_rate_pct": round(overall_rate, 1),
            "total_steps": len(steps),
            "biggest_bottleneck": bottleneck["name"] if bottleneck else "None",
            "biggest_drop_pct": round(bottleneck["drop_pct"], 1) if bottleneck else 0,
        },
        "funnel_steps": step_results,
        "impact_analysis": impact_analysis,
        "recommendations": _generate_recommendations(step_results, overall_rate, impact_analysis),
    }


def _generate_recommendations(steps: list, overall_rate: float, impacts: list) -> list:
    """Generate recommendations."""
    recs = []

    if overall_rate < 25:
        recs.append({
            "priority": "CRITICAL",
            "recommendation": f"Overall activation rate is {overall_rate:.1f}%. Target 25-40% for B2B. Focus on the biggest drop-off step first.",
        })
    elif overall_rate < 40:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Activation rate of {overall_rate:.1f}% has room for improvement. Target 40%+ for B2C, 30%+ for B2B.",
        })

    if impacts:
        top = impacts[0]
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Highest-impact fix: '{top['step']}' -- a 20% improvement here would add ~{top['additional_activations']} activated users.",
        })

    # Look for steps with >30% drop
    high_drops = [s for s in steps if s["drop_pct"] > 30 and s["step"] > 1]
    for hd in high_drops[:2]:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"'{hd['name']}' has {hd['drop_pct']:.1f}% drop-off. Investigate blank state, complexity, or missing guidance at this step.",
        })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("ACTIVATION FUNNEL ANALYZER")
    lines.append("=" * 70)

    s = result["summary"]
    lines.append(f"\nEntry Users:         {s['total_entry_users']:>8,d}")
    lines.append(f"Activated Users:     {s['final_activated_users']:>8,d}")
    lines.append(f"Activation Rate:     {s['overall_activation_rate_pct']:>8.1f}%")
    lines.append(f"Biggest Bottleneck:  {s['biggest_bottleneck']} ({s['biggest_drop_pct']}% drop)")

    lines.append(f"\n--- Funnel Steps ---")
    lines.append(f"{'Step':<25} {'Users':>8} {'% Total':>8} {'Drop':>8} {'Drop%':>7}")
    for step in result["funnel_steps"]:
        lines.append(
            f"{step['name']:<25} {step['users']:>8,d} {step['pct_of_total']:>7.1f}% "
            f"{step['drop_from_previous']:>8,d} {step['drop_pct']:>6.1f}%"
        )

    # Visual funnel
    lines.append(f"\n--- Visual Funnel ---")
    max_users = result["funnel_steps"][0]["users"] if result["funnel_steps"] else 1
    for step in result["funnel_steps"]:
        bar_len = int((step["users"] / max_users) * 40)
        bar = "#" * bar_len
        lines.append(f"  {step['name']:<20} {bar} {step['users']:,d} ({step['pct_of_total']}%)")

    lines.append(f"\n--- Impact Analysis (20% improvement per step) ---")
    lines.append(f"{'Step':<25} {'Current Drop':>12} {'Recovered':>10} {'+Activations':>13}")
    for ia in result["impact_analysis"]:
        lines.append(
            f"{ia['step']:<25} {ia['current_drop']:>12,d} "
            f"{ia['users_recovered_at_20pct_improvement']:>10,d} {ia['additional_activations']:>13,d}"
        )

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze onboarding activation funnel for drop-off points and improvement impact."
    )
    parser.add_argument("input_file", help="JSON file with funnel step names and user counts")
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

    result = analyze_funnel(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
