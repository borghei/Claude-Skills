#!/usr/bin/env python3
"""Price Increase Modeler - Model revenue impact of price increases at various retention scenarios.

Takes current customer base, pricing, and proposed increase, then projects revenue
impact at multiple retention scenarios with break-even analysis.

Usage:
    python price_increase_modeler.py increase.json
    python price_increase_modeler.py increase.json --format json
"""

import argparse
import json
import sys
from typing import Any


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide."""
    return num / den if den != 0 else default


def model_increase(data: dict) -> dict:
    """Model a price increase across multiple retention scenarios."""
    current = data.get("current", {})
    proposed = data.get("proposed", {})

    current_price = current.get("price_monthly", 0)
    current_customers = current.get("customer_count", 0)
    current_mrr = current_price * current_customers

    new_price = proposed.get("new_price_monthly", 0)
    increase_pct = safe_divide(new_price - current_price, current_price) * 100

    # Affected vs unaffected customers
    affected_pct = proposed.get("affected_customer_pct", 100) / 100
    affected_customers = int(current_customers * affected_pct)
    unaffected_customers = current_customers - affected_customers

    # Retention scenarios
    retention_rates = proposed.get("retention_scenarios", [100, 95, 90, 85, 80])

    scenarios = []
    for retention_pct in retention_rates:
        retention = retention_pct / 100
        retained_customers = int(affected_customers * retention)
        churned_customers = affected_customers - retained_customers

        # Revenue calculation
        new_mrr_affected = retained_customers * new_price
        new_mrr_unaffected = unaffected_customers * current_price
        new_total_mrr = new_mrr_affected + new_mrr_unaffected

        mrr_change = new_total_mrr - current_mrr
        mrr_change_pct = safe_divide(mrr_change, current_mrr) * 100

        annual_impact = mrr_change * 12

        # Revenue from increase vs revenue lost from churn
        revenue_gained = retained_customers * (new_price - current_price)
        revenue_lost = churned_customers * current_price

        scenario = {
            "retention_pct": retention_pct,
            "retained_customers": retained_customers,
            "churned_customers": churned_customers,
            "new_mrr": round(new_total_mrr, 2),
            "mrr_change": round(mrr_change, 2),
            "mrr_change_pct": round(mrr_change_pct, 2),
            "annual_revenue_impact": round(annual_impact, 2),
            "revenue_gained_from_increase": round(revenue_gained, 2),
            "revenue_lost_from_churn": round(revenue_lost, 2),
            "net_positive": mrr_change > 0,
        }
        scenarios.append(scenario)

    # Break-even calculation
    # At what retention rate does the increase become net-negative?
    # Break-even: retained * new_price = affected * current_price
    # retention_break_even = (affected * current_price) / (affected * new_price)
    if new_price > 0:
        break_even_retention = safe_divide(current_price, new_price) * 100
    else:
        break_even_retention = 0

    # Lock-in offer analysis
    lock_in = proposed.get("lock_in_offer", {})
    lock_in_analysis = None
    if lock_in:
        lock_in_uptake = lock_in.get("expected_uptake_pct", 30) / 100
        lock_in_months = lock_in.get("lock_in_months", 12)
        lock_in_price = lock_in.get("lock_in_price_monthly", current_price)

        locked_customers = int(affected_customers * lock_in_uptake)
        non_locked = affected_customers - locked_customers

        # Revenue during lock-in period
        locked_revenue = locked_customers * lock_in_price * lock_in_months
        # Non-locked face the increase (assume 90% retention)
        non_locked_retained = int(non_locked * 0.9)
        non_locked_revenue = non_locked_retained * new_price * lock_in_months

        total_lock_in_revenue = locked_revenue + non_locked_revenue
        baseline_revenue = affected_customers * current_price * lock_in_months

        lock_in_analysis = {
            "locked_in_customers": locked_customers,
            "lock_in_price": lock_in_price,
            "lock_in_period_months": lock_in_months,
            "revenue_during_lock_in": round(total_lock_in_revenue, 2),
            "baseline_revenue_same_period": round(baseline_revenue, 2),
            "net_impact": round(total_lock_in_revenue - baseline_revenue, 2),
        }

    # Timeline
    timeline = [
        {"week": -12, "action": "Decide strategy, model revenue impact"},
        {"week": -8, "action": "Segment customers by risk (annual, champions, detractors, usage)"},
        {"week": -6, "action": "Prepare communications (email, in-app, FAQ, CS talking points)"},
        {"week": -4, "action": "Announce to existing customers (60+ day notice for annual)"},
        {"week": 0, "action": "New pricing live for new customers"},
        {"week": 4, "action": "Existing customer pricing changes (if not grandfathered)"},
        {"week": 12, "action": "Review: churn rate, downgrade rate, support tickets, revenue"},
    ]

    return {
        "summary": {
            "current_price": current_price,
            "new_price": new_price,
            "increase_pct": round(increase_pct, 1),
            "current_mrr": round(current_mrr, 2),
            "total_customers": current_customers,
            "affected_customers": affected_customers,
            "break_even_retention_pct": round(break_even_retention, 1),
        },
        "scenarios": scenarios,
        "lock_in_analysis": lock_in_analysis,
        "recommended_timeline": timeline,
    }


def format_text(result: dict) -> str:
    """Format model results as human-readable text."""
    lines = []
    s = result["summary"]

    lines.append("=" * 60)
    lines.append("PRICE INCREASE IMPACT MODEL")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Current Price:     ${s['current_price']:>10,.2f}/mo")
    lines.append(f"New Price:         ${s['new_price']:>10,.2f}/mo  (+{s['increase_pct']}%)")
    lines.append(f"Current MRR:       ${s['current_mrr']:>10,.2f}")
    lines.append(f"Total Customers:   {s['total_customers']:>10,}")
    lines.append(f"Affected:          {s['affected_customers']:>10,}")
    lines.append(f"Break-even:        {s['break_even_retention_pct']:>10.1f}% retention")
    lines.append("")

    lines.append("-" * 60)
    lines.append("RETENTION SCENARIOS")
    lines.append("-" * 60)
    lines.append(f"{'Retention':<12} {'New MRR':>12} {'MRR Change':>14} {'Annual':>14} {'Net?':>8}")
    lines.append("-" * 60)
    for sc in result["scenarios"]:
        net = "+" if sc["net_positive"] else "-"
        lines.append(
            f"{sc['retention_pct']:>6}%      "
            f"${sc['new_mrr']:>10,.2f} "
            f"${sc['mrr_change']:>+12,.2f} "
            f"${sc['annual_revenue_impact']:>+12,.2f} "
            f"  {net}"
        )

    lines.append("")
    for sc in result["scenarios"]:
        if not sc["net_positive"]:
            lines.append(f"  >> Net-negative below {sc['retention_pct']+5}% retention")
            break

    if result.get("lock_in_analysis"):
        li = result["lock_in_analysis"]
        lines.append("")
        lines.append("-" * 40)
        lines.append("LOCK-IN OFFER ANALYSIS")
        lines.append("-" * 40)
        lines.append(f"  Customers who lock in:  {li['locked_in_customers']:,}")
        lines.append(f"  Lock-in price:          ${li['lock_in_price']:,.2f}/mo for {li['lock_in_period_months']} months")
        lines.append(f"  Revenue during period:  ${li['revenue_during_lock_in']:,.2f}")
        lines.append(f"  Baseline same period:   ${li['baseline_revenue_same_period']:,.2f}")
        lines.append(f"  Net impact:             ${li['net_impact']:+,.2f}")

    lines.append("")
    lines.append("-" * 40)
    lines.append("RECOMMENDED TIMELINE")
    lines.append("-" * 40)
    for step in result["recommended_timeline"]:
        week = step["week"]
        prefix = f"Week {week:+d}" if week != 0 else "Week 0 "
        lines.append(f"  {prefix:>10}: {step['action']}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Model revenue impact of price increases at various retention scenarios."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with price increase scenario data",
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

    result = model_increase(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
