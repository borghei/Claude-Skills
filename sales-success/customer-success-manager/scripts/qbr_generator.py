#!/usr/bin/env python3
"""Generate quarterly business review (QBR) templates from customer data.

Reads customer metrics, achievements, and goals to produce structured QBR
documents ready for presentation. Supports markdown and JSON output.

Usage:
    python qbr_generator.py --data customer.json
    python qbr_generator.py --data customer.csv --quarter Q1-2026
    python qbr_generator.py --data customer.json --json
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


def load_data(filepath):
    """Load customer data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def safe_float(value, default=0.0):
    """Parse float safely."""
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return default


def calculate_health_summary(customer):
    """Generate health summary from available metrics."""
    health_score = safe_float(customer.get("health_score", 0))

    if health_score >= 80:
        status = "Healthy"
        trend = "strong"
    elif health_score >= 60:
        status = "Needs Attention"
        trend = "moderate"
    else:
        status = "At Risk"
        trend = "concerning"

    return {
        "score": health_score,
        "status": status,
        "trend": trend,
    }


def extract_achievements(customer):
    """Extract achievements from customer data."""
    achievements = []

    # Check for explicitly listed achievements
    for key in ["achievement_1", "achievement_2", "achievement_3", "achievements"]:
        val = customer.get(key, "")
        if val:
            if isinstance(val, list):
                achievements.extend(val)
            elif ";" in str(val):
                achievements.extend([a.strip() for a in str(val).split(";")])
            else:
                achievements.append(str(val))

    # Generate from metrics if no explicit achievements
    if not achievements:
        active = safe_float(customer.get("active_users", 0))
        licensed = safe_float(customer.get("licensed_seats", 0))
        if active > 0 and licensed > 0:
            adoption = round(active / licensed * 100, 1)
            achievements.append(f"Achieved {adoption}% user adoption ({int(active)} of {int(licensed)} seats active)")

        roi = customer.get("roi_achieved", customer.get("roi", ""))
        if roi:
            achievements.append(f"Demonstrated {roi} ROI")

        time_saved = customer.get("time_saved_hours", customer.get("hours_saved", ""))
        if time_saved:
            achievements.append(f"Saved {time_saved} hours through platform usage")

    return achievements if achievements else ["Review customer metrics to identify key achievements"]


def extract_metrics(customer):
    """Extract key metrics for QBR presentation."""
    metrics = []

    metric_mappings = [
        ("active_users", "Active Users", None),
        ("licensed_seats", "Licensed Seats", None),
        ("login_frequency", "Avg Logins / Week", None),
        ("feature_adoption", "Feature Adoption Score", "/10"),
        ("nps_score", "NPS Score", None),
        ("support_tickets", "Support Tickets (Quarter)", None),
        ("time_saved_hours", "Hours Saved", None),
        ("roi", "ROI Achieved", None),
    ]

    for field, label, suffix in metric_mappings:
        val = customer.get(field, "")
        if val and str(val).strip():
            target = customer.get(f"{field}_target", "")
            trend = customer.get(f"{field}_trend", "")
            metrics.append({
                "metric": label,
                "actual": str(val) + (suffix or ""),
                "target": str(target) if target else "N/A",
                "trend": str(trend) if trend else "N/A",
            })

    return metrics


def extract_goals(customer):
    """Extract next quarter goals."""
    goals = []
    for key in ["goal_1", "goal_2", "goal_3", "next_quarter_goals"]:
        val = customer.get(key, "")
        if val:
            if isinstance(val, list):
                goals.extend(val)
            elif ";" in str(val):
                goals.extend([g.strip() for g in str(val).split(";")])
            else:
                goals.append(str(val))

    return goals if goals else [
        "Increase platform adoption to [target]%",
        "Achieve [specific business outcome]",
        "Expand usage to [new department/use case]",
    ]


def generate_qbr(customer, quarter):
    """Generate QBR content for a single customer."""
    name = customer.get("customer_name", customer.get("name", customer.get("account", "Unknown")))
    arr = customer.get("arr", customer.get("revenue", "N/A"))
    since = customer.get("customer_since", customer.get("start_date", "N/A"))
    csm = customer.get("csm", customer.get("account_manager", "N/A"))

    health = calculate_health_summary(customer)
    achievements = extract_achievements(customer)
    metrics = extract_metrics(customer)
    goals = extract_goals(customer)

    active = safe_float(customer.get("active_users", 0))
    licensed = safe_float(customer.get("licensed_seats", 0))

    value_items = []
    time_saved = customer.get("time_saved_hours", "")
    cost_reduction = customer.get("cost_reduction", "")
    other_impact = customer.get("business_impact", customer.get("impact", ""))
    if time_saved:
        value_items.append(f"Time saved: {time_saved} hours")
    if cost_reduction:
        value_items.append(f"Cost reduction: ${cost_reduction}")
    if other_impact:
        value_items.append(f"Business impact: {other_impact}")

    risks = []
    for key in ["risk_1", "risk_2", "risks"]:
        val = customer.get(key, "")
        if val:
            if isinstance(val, list):
                risks.extend(val)
            elif ";" in str(val):
                risks.extend([r.strip() for r in str(val).split(";")])
            else:
                risks.append(str(val))

    return {
        "customer_name": name,
        "quarter": quarter,
        "arr": arr,
        "customer_since": since,
        "csm": csm,
        "active_users": int(active) if active else "N/A",
        "licensed_seats": int(licensed) if licensed else "N/A",
        "health_summary": health,
        "achievements": achievements,
        "metrics": metrics,
        "value_delivered": value_items,
        "next_quarter_goals": goals,
        "risks": risks,
    }


def format_markdown(qbr):
    """Generate QBR as markdown document."""
    lines = []
    lines.append(f"# Quarterly Business Review: {qbr['customer_name']}")
    lines.append(f"\n**Quarter:** {qbr['quarter']}")
    lines.append(f"**Prepared:** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**CSM:** {qbr['csm']}")

    lines.append(f"\n## Partnership Summary")
    lines.append(f"- Customer since: {qbr['customer_since']}")
    lines.append(f"- Current ARR: {qbr['arr']}")
    lines.append(f"- Users: {qbr['active_users']} active / {qbr['licensed_seats']} licensed")
    lines.append(f"- Health Score: {qbr['health_summary']['score']}/100 ({qbr['health_summary']['status']})")

    lines.append(f"\n## Quarter in Review")
    lines.append(f"\n### Achievements")
    for a in qbr["achievements"]:
        lines.append(f"- {a}")

    if qbr["metrics"]:
        lines.append(f"\n### Key Metrics")
        lines.append(f"| Metric | Actual | Target | Trend |")
        lines.append(f"|--------|--------|--------|-------|")
        for m in qbr["metrics"]:
            lines.append(f"| {m['metric']} | {m['actual']} | {m['target']} | {m['trend']} |")

    if qbr["value_delivered"]:
        lines.append(f"\n## Value Delivered")
        for v in qbr["value_delivered"]:
            lines.append(f"- {v}")

    lines.append(f"\n## Next Quarter Goals")
    for i, g in enumerate(qbr["next_quarter_goals"], 1):
        lines.append(f"{i}. {g}")

    if qbr["risks"]:
        lines.append(f"\n## Risks & Concerns")
        for r in qbr["risks"]:
            lines.append(f"- {r}")

    lines.append(f"\n## Discussion Topics")
    lines.append(f"1. Review of achievements and value delivered this quarter")
    lines.append(f"2. Alignment on next quarter priorities and success metrics")
    lines.append(f"3. Product roadmap items relevant to {qbr['customer_name']}")
    lines.append(f"4. Expansion opportunities and growth planning")
    lines.append(f"5. Open items and action plan")

    lines.append(f"\n---")
    lines.append(f"*Generated by QBR Generator | {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def format_human(qbrs):
    """Format multiple QBRs for console output."""
    lines = []
    lines.append("=" * 70)
    lines.append("QBR GENERATION REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Customers: {len(qbrs)}")
    lines.append("=" * 70)

    for qbr in qbrs:
        lines.append(f"\n{format_markdown(qbr)}")
        lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate quarterly business review templates from customer data."
    )
    parser.add_argument("--data", required=True, help="Path to customer data CSV or JSON file")
    parser.add_argument(
        "--quarter", default=None, help="Quarter label (e.g., Q1-2026). Auto-detected if omitted."
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect quarter if not specified
    quarter = args.quarter
    if not quarter:
        now = datetime.now()
        q = (now.month - 1) // 3 + 1
        quarter = f"Q{q}-{now.year}"

    customers = load_data(args.data)
    if not customers:
        print("Error: No customers found in input file.", file=sys.stderr)
        sys.exit(1)

    qbrs = [generate_qbr(c, quarter) for c in customers]

    if args.json:
        print(json.dumps(qbrs, indent=2))
    else:
        print(format_human(qbrs))

    sys.exit(0)


if __name__ == "__main__":
    main()
