#!/usr/bin/env python3
"""
Proposal Cost Estimator

Generate a project cost estimate with phase breakdown, payment schedule,
and margin analysis. Supports multiple billing models and currencies.

Usage:
    python proposal_cost_estimator.py --hourly-rate 150 --hours 200 --phases 4
    python proposal_cost_estimator.py --hourly-rate 150 --hours 200 --phases 4 --json
"""

import argparse
import json
import math
import sys


DEFAULT_PHASE_NAMES = [
    "Discovery & Planning",
    "Development",
    "Testing & QA",
    "Launch & Handoff",
    "Post-Launch Support",
]

DEFAULT_PHASE_WEIGHTS = [0.10, 0.50, 0.20, 0.15, 0.05]

PAYMENT_SCHEDULES = {
    "milestone": {
        "description": "Milestone-based (recommended for >$10K)",
        "schedule": [
            {"milestone": "Contract signing", "percentage": 50},
            {"milestone": "Beta delivery", "percentage": 25},
            {"milestone": "Final acceptance", "percentage": 25},
        ],
    },
    "monthly": {
        "description": "Monthly invoicing (recommended for hourly/retainer)",
        "schedule": [
            {"milestone": "Monthly invoice", "percentage": "pro-rata"},
        ],
    },
    "phased": {
        "description": "Per-phase payment (recommended for multi-phase projects)",
        "schedule": [],  # Generated dynamically
    },
}


def estimate_cost(hourly_rate: float, hours: float, num_phases: int,
                  margin: float, currency: str) -> dict:
    """Generate project cost estimate."""
    base_cost = hourly_rate * hours
    margin_amount = base_cost * (margin / 100.0)
    total_cost = base_cost + margin_amount

    # Phase breakdown
    phases = []
    phase_names = DEFAULT_PHASE_NAMES[:num_phases]
    phase_weights = DEFAULT_PHASE_WEIGHTS[:num_phases]

    # Normalize weights
    weight_sum = sum(phase_weights)
    phase_weights = [w / weight_sum for w in phase_weights]

    for i, (name, weight) in enumerate(zip(phase_names, phase_weights)):
        phase_hours = round(hours * weight, 1)
        phase_cost = round(total_cost * weight, 2)
        phases.append({
            "phase": i + 1,
            "name": name,
            "weight_pct": round(weight * 100, 1),
            "estimated_hours": phase_hours,
            "estimated_cost": phase_cost,
        })

    # Payment schedule options
    milestone_schedule = []
    milestone_schedule.append({
        "event": "Contract signing (50%)",
        "amount": round(total_cost * 0.50, 2),
    })
    if num_phases >= 3:
        milestone_schedule.append({
            "event": "Beta delivery (25%)",
            "amount": round(total_cost * 0.25, 2),
        })
        milestone_schedule.append({
            "event": "Final acceptance (25%)",
            "amount": round(total_cost * 0.25, 2),
        })
    else:
        milestone_schedule.append({
            "event": "Final delivery (50%)",
            "amount": round(total_cost * 0.50, 2),
        })

    phased_schedule = []
    for p in phases:
        phased_schedule.append({
            "event": f"{p['name']} completion",
            "amount": p["estimated_cost"],
        })

    # Estimated duration (assuming 6 productive hours per day, 5 days per week)
    productive_hours_per_week = 30
    estimated_weeks = math.ceil(hours / productive_hours_per_week)

    # Risk buffer
    risk_buffer_hours = round(hours * 0.15, 1)
    risk_buffer_cost = round(risk_buffer_hours * hourly_rate, 2)

    return {
        "inputs": {
            "hourly_rate": hourly_rate,
            "total_hours": hours,
            "num_phases": num_phases,
            "margin_pct": margin,
            "currency": currency,
        },
        "cost_summary": {
            "base_cost": round(base_cost, 2),
            "margin_amount": round(margin_amount, 2),
            "total_project_cost": round(total_cost, 2),
            "effective_hourly_rate": round(total_cost / hours, 2),
            "currency": currency,
        },
        "phase_breakdown": phases,
        "timeline": {
            "estimated_weeks": estimated_weeks,
            "productive_hours_per_week": productive_hours_per_week,
            "total_hours": hours,
        },
        "payment_options": {
            "milestone": milestone_schedule,
            "phased": phased_schedule,
        },
        "risk_buffer": {
            "buffer_hours": risk_buffer_hours,
            "buffer_cost": risk_buffer_cost,
            "total_with_buffer": round(total_cost + risk_buffer_cost, 2),
            "note": "15% contingency for scope changes and unforeseen complexity",
        },
        "recommendations": _generate_recommendations(total_cost, hours, num_phases),
    }


def _generate_recommendations(total_cost: float, hours: float, phases: int) -> list:
    """Generate recommendations for proposal."""
    recs = []
    if total_cost > 50000:
        recs.append({
            "priority": "HIGH",
            "recommendation": "Project over $50K -- use milestone-based payments and include legal review.",
        })
    if total_cost > 10000:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": "Use milestone payments over net-30 to reduce cash flow risk.",
        })
    if hours > 500:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": "Large project -- consider phased contracting with go/no-go gates between phases.",
        })
    recs.append({
        "priority": "MEDIUM",
        "recommendation": "Include a change order clause for scope changes with pricing mechanism.",
    })
    recs.append({
        "priority": "LOW",
        "recommendation": "Present the client with 2-3 pricing options (basic, recommended, premium) to avoid a yes/no decision.",
    })
    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    cur = result["inputs"]["currency"]
    lines.append("=" * 60)
    lines.append("PROPOSAL COST ESTIMATOR")
    lines.append("=" * 60)

    cs = result["cost_summary"]
    lines.append(f"\n--- Cost Summary ---")
    lines.append(f"Hourly Rate:           {cur} {result['inputs']['hourly_rate']:>10,.2f}")
    lines.append(f"Total Hours:           {result['inputs']['total_hours']:>10,.1f}")
    lines.append(f"Base Cost:             {cur} {cs['base_cost']:>10,.2f}")
    lines.append(f"Margin ({result['inputs']['margin_pct']}%):          {cur} {cs['margin_amount']:>10,.2f}")
    lines.append(f"Total Project Cost:    {cur} {cs['total_project_cost']:>10,.2f}")
    lines.append(f"Effective Rate:        {cur} {cs['effective_hourly_rate']:>10,.2f}/hr")

    lines.append(f"\n--- Phase Breakdown ---")
    lines.append(f"{'Phase':<25} {'Hours':>8} {'Cost':>12} {'%':>6}")
    for p in result["phase_breakdown"]:
        lines.append(f"{p['name']:<25} {p['estimated_hours']:>8.1f} {cur} {p['estimated_cost']:>8,.2f} {p['weight_pct']:>5.1f}%")

    tl = result["timeline"]
    lines.append(f"\n--- Timeline ---")
    lines.append(f"Estimated Duration: {tl['estimated_weeks']} weeks")
    lines.append(f"Productive Hours/Week: {tl['productive_hours_per_week']}")

    rb = result["risk_buffer"]
    lines.append(f"\n--- Risk Buffer ---")
    lines.append(f"Buffer Hours: {rb['buffer_hours']}")
    lines.append(f"Buffer Cost: {cur} {rb['buffer_cost']:,.2f}")
    lines.append(f"Total with Buffer: {cur} {rb['total_with_buffer']:,.2f}")

    lines.append(f"\n--- Payment Options ---")
    lines.append(f"\n  Milestone-based:")
    for m in result["payment_options"]["milestone"]:
        lines.append(f"    {m['event']:<35} {cur} {m['amount']:>10,.2f}")

    lines.append(f"\n  Per-phase:")
    for m in result["payment_options"]["phased"]:
        lines.append(f"    {m['event']:<35} {cur} {m['amount']:>10,.2f}")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate project cost estimate with phase breakdown and payment schedule."
    )
    parser.add_argument("--hourly-rate", type=float, required=True,
                        help="Hourly rate in dollars")
    parser.add_argument("--hours", type=float, required=True,
                        help="Estimated total hours")
    parser.add_argument("--phases", type=int, default=3,
                        help="Number of project phases (default: 3, max: 5)")
    parser.add_argument("--margin", type=float, default=20,
                        help="Desired profit margin percentage (default: 20)")
    parser.add_argument("--currency", default="USD",
                        help="Currency code (default: USD)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    if args.hourly_rate <= 0:
        print("Error: --hourly-rate must be positive.", file=sys.stderr)
        sys.exit(1)
    if args.hours <= 0:
        print("Error: --hours must be positive.", file=sys.stderr)
        sys.exit(1)

    num_phases = max(1, min(5, args.phases))

    result = estimate_cost(args.hourly_rate, args.hours, num_phases,
                           args.margin, args.currency)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
