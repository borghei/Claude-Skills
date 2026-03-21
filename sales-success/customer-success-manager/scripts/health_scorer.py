#!/usr/bin/env python3
"""Calculate customer health scores from usage, support, and relationship data.

Implements a multi-dimensional health scoring model with configurable weights
across Product (usage), Relationship (engagement), and Outcomes (results).

Usage:
    python health_scorer.py --data customers.csv
    python health_scorer.py --data customers.json --json
    python health_scorer.py --data customers.csv --weights 40,30,30
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


DEFAULT_WEIGHTS = {
    "product": 0.40,
    "relationship": 0.30,
    "outcomes": 0.30,
}

PRODUCT_FIELDS = [
    "login_frequency",
    "feature_adoption",
    "active_users_ratio",
    "support_tickets_inverse",
]

RELATIONSHIP_FIELDS = [
    "executive_engagement",
    "meeting_attendance",
    "nps_score",
    "response_time",
]

OUTCOMES_FIELDS = [
    "goals_achieved",
    "roi_demonstrated",
    "business_impact",
]

HEALTH_THRESHOLDS = {
    "green": 80,
    "yellow": 60,
    "red": 0,
}


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


def parse_score(value, max_val=10):
    """Parse a score value, clamping to 0-max_val."""
    try:
        score = float(value)
        return max(0, min(score, max_val))
    except (ValueError, TypeError):
        return 0


def calculate_dimension(customer, fields, max_per_field=10):
    """Calculate average score for a dimension."""
    scores = []
    populated = 0
    for field in fields:
        val = customer.get(field, None)
        if val is not None and str(val).strip() != "":
            scores.append(parse_score(val, max_per_field))
            populated += 1
        else:
            scores.append(0)

    if populated == 0:
        return 0, {f: 0 for f in fields}, 0

    avg = sum(scores) / len(fields)
    details = dict(zip(fields, [round(s, 1) for s in scores]))
    return round(avg, 2), details, populated


def score_customer(customer, weights):
    """Calculate health score for a single customer."""
    product_avg, product_details, product_populated = calculate_dimension(
        customer, PRODUCT_FIELDS
    )
    relationship_avg, relationship_details, rel_populated = calculate_dimension(
        customer, RELATIONSHIP_FIELDS
    )
    outcomes_avg, outcomes_details, out_populated = calculate_dimension(
        customer, OUTCOMES_FIELDS
    )

    weighted_product = product_avg * weights["product"]
    weighted_relationship = relationship_avg * weights["relationship"]
    weighted_outcomes = outcomes_avg * weights["outcomes"]

    total_weighted = weighted_product + weighted_relationship + weighted_outcomes
    health_score = round(total_weighted * 10, 1)  # Scale to 0-100

    if health_score >= HEALTH_THRESHOLDS["green"]:
        status = "green"
        label = "Healthy"
        action = "Maintain cadence; pursue expansion opportunities"
    elif health_score >= HEALTH_THRESHOLDS["yellow"]:
        status = "yellow"
        label = "Attention"
        action = "Increase touchpoints; address gaps in weak dimensions"
    else:
        status = "red"
        label = "At Risk"
        action = "Activate risk playbook immediately; escalate within 48 hours"

    # Identify weak and strong dimensions
    dim_scores = {
        "product": product_avg,
        "relationship": relationship_avg,
        "outcomes": outcomes_avg,
    }
    weak = [d for d, s in dim_scores.items() if s < 5]
    strong = [d for d, s in dim_scores.items() if s >= 7]

    # Risk factors
    risk_factors = []
    if product_details.get("support_tickets_inverse", 10) < 4:
        risk_factors.append("High support ticket volume")
    if product_details.get("active_users_ratio", 10) < 5:
        risk_factors.append("Low user adoption vs. licensed seats")
    if relationship_details.get("executive_engagement", 10) < 4:
        risk_factors.append("Weak executive engagement")
    if relationship_details.get("nps_score", 10) < 5:
        risk_factors.append("Low NPS / negative sentiment")
    if outcomes_details.get("goals_achieved", 10) < 4:
        risk_factors.append("Goals not being achieved")

    return {
        "customer_name": customer.get(
            "customer_name", customer.get("name", customer.get("account", "Unknown"))
        ),
        "arr": customer.get("arr", customer.get("revenue", "N/A")),
        "renewal_date": customer.get("renewal_date", "N/A"),
        "health_score": health_score,
        "status": status,
        "label": label,
        "action": action,
        "dimensions": {
            "product": {
                "score": product_avg,
                "weight": weights["product"],
                "weighted": round(weighted_product, 2),
                "details": product_details,
                "fields_populated": product_populated,
            },
            "relationship": {
                "score": relationship_avg,
                "weight": weights["relationship"],
                "weighted": round(weighted_relationship, 2),
                "details": relationship_details,
                "fields_populated": rel_populated,
            },
            "outcomes": {
                "score": outcomes_avg,
                "weight": weights["outcomes"],
                "weighted": round(weighted_outcomes, 2),
                "details": outcomes_details,
                "fields_populated": out_populated,
            },
        },
        "weak_dimensions": weak,
        "strong_dimensions": strong,
        "risk_factors": risk_factors,
    }


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("CUSTOMER HEALTH SCORE REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    # Portfolio summary
    total = len(results)
    green = sum(1 for r in results if r["status"] == "green")
    yellow = sum(1 for r in results if r["status"] == "yellow")
    red = sum(1 for r in results if r["status"] == "red")
    avg_score = sum(r["health_score"] for r in results) / total if total > 0 else 0

    lines.append(f"\n  Portfolio Summary")
    lines.append(f"  Total Customers:  {total}")
    lines.append(f"  Green (Healthy):  {green} ({green/total*100:.0f}%)" if total else "  Green: 0")
    lines.append(f"  Yellow (Attn):    {yellow} ({yellow/total*100:.0f}%)" if total else "  Yellow: 0")
    lines.append(f"  Red (At Risk):    {red} ({red/total*100:.0f}%)" if total else "  Red: 0")
    lines.append(f"  Avg Health Score: {avg_score:.1f}/100")

    # Sort: red first, then yellow, then green
    status_order = {"red": 0, "yellow": 1, "green": 2}
    sorted_results = sorted(results, key=lambda r: (status_order.get(r["status"], 3), r["health_score"]))

    for result in sorted_results:
        status_icon = {"green": "[GREEN]", "yellow": "[YELLOW]", "red": "[RED]"}
        lines.append(f"\n  {status_icon.get(result['status'], '[???]')} {result['customer_name']}")
        lines.append(f"  Health Score: {result['health_score']}/100  |  Status: {result['label']}")
        lines.append(f"  ARR: {result['arr']}  |  Renewal: {result['renewal_date']}")
        lines.append(f"  Action: {result['action']}")

        dims = result["dimensions"]
        lines.append(f"\n  Dimensions:")
        for dim_name, dim_data in dims.items():
            bar_len = int(dim_data["score"])
            bar = "#" * bar_len + "." * (10 - bar_len)
            flag = " << WEAK" if dim_data["score"] < 5 else ""
            lines.append(
                f"    {dim_name:<14} [{bar}] {dim_data['score']:.1f}/10 "
                f"(wt: {dim_data['weight']:.0%}, contrib: {dim_data['weighted']:.2f}){flag}"
            )

        if result["risk_factors"]:
            lines.append(f"\n  Risk Factors:")
            for rf in result["risk_factors"]:
                lines.append(f"    - {rf}")

        lines.append("-" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate customer health scores from usage and engagement data."
    )
    parser.add_argument("--data", required=True, help="Path to customer data CSV or JSON file")
    parser.add_argument(
        "--weights",
        default="40,30,30",
        help="Dimension weights as product,relationship,outcomes (default: 40,30,30)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    # Parse weights
    try:
        w = [float(x) for x in args.weights.split(",")]
        if len(w) != 3:
            raise ValueError("Need exactly 3 weights")
        total_w = sum(w)
        weights = {
            "product": w[0] / total_w,
            "relationship": w[1] / total_w,
            "outcomes": w[2] / total_w,
        }
    except (ValueError, IndexError) as e:
        print(f"Error: Invalid weights format. Use 'P,R,O' e.g. '40,30,30'. {e}", file=sys.stderr)
        sys.exit(1)

    customers = load_data(args.data)
    if not customers:
        print("Error: No customers found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [score_customer(c, weights) for c in customers]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    red_count = sum(1 for r in results if r["status"] == "red")
    sys.exit(1 if red_count > 0 else 0)


if __name__ == "__main__":
    main()
