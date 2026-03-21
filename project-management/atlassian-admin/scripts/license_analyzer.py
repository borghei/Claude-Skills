#!/usr/bin/env python3
"""License Analyzer - Analyze Atlassian license usage and optimize costs.

Reads license and usage data, identifies inactive users consuming licenses,
and provides cost optimization recommendations.

Usage:
    python license_analyzer.py --usage usage.json
    python license_analyzer.py --usage usage.json --json
    python license_analyzer.py --example
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


def load_data(path: str) -> dict:
    """Load license usage data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def parse_date(s: str) -> datetime:
    """Parse date string."""
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


def analyze_licenses(data: dict) -> dict:
    """Analyze license usage and identify optimization opportunities."""
    org = data.get("organization", "Unknown")
    products = data.get("products", [])
    today = datetime.now()

    product_results = []
    total_annual_cost = 0
    total_potential_savings = 0

    for product in products:
        name = product.get("name", "Unknown")
        tier = product.get("tier", "Standard")
        cost_per_user_month = product.get("cost_per_user_month", 0)
        total_licenses = product.get("total_licenses", 0)
        users = product.get("users", [])

        active_users = []
        inactive_users = []
        never_logged_in = []

        for user in users:
            last_active = user.get("last_active")
            if not last_active:
                never_logged_in.append(user)
                continue

            try:
                last_dt = parse_date(last_active)
                days_since = (today - last_dt).days
                user["days_inactive"] = days_since

                if days_since > 90:
                    inactive_users.append(user)
                else:
                    active_users.append(user)
            except ValueError:
                active_users.append(user)

        used_licenses = len(users)
        utilization = round(used_licenses / total_licenses * 100, 1) if total_licenses > 0 else 0
        active_pct = round(len(active_users) / len(users) * 100, 1) if users else 0

        # Cost analysis
        annual_cost = cost_per_user_month * used_licenses * 12
        recoverable_licenses = len(inactive_users) + len(never_logged_in)
        potential_savings = cost_per_user_month * recoverable_licenses * 12

        total_annual_cost += annual_cost
        total_potential_savings += potential_savings

        product_results.append({
            "product": name,
            "tier": tier,
            "total_licenses": total_licenses,
            "used_licenses": used_licenses,
            "utilization_pct": utilization,
            "active_users": len(active_users),
            "inactive_users_90d": len(inactive_users),
            "never_logged_in": len(never_logged_in),
            "active_pct": active_pct,
            "annual_cost": round(annual_cost, 2),
            "recoverable_licenses": recoverable_licenses,
            "potential_annual_savings": round(potential_savings, 2),
            "inactive_details": [
                {"name": u.get("name"), "email": u.get("email"), "days_inactive": u.get("days_inactive", "N/A")}
                for u in sorted(inactive_users, key=lambda x: x.get("days_inactive", 0), reverse=True)[:10]
            ],
            "never_active_details": [
                {"name": u.get("name"), "email": u.get("email")}
                for u in never_logged_in[:10]
            ],
        })

    # Recommendations
    recs = []
    for pr in product_results:
        if pr["recoverable_licenses"] > 0:
            recs.append(
                f"{pr['product']}: Recover {pr['recoverable_licenses']} unused license(s) "
                f"for ${pr['potential_annual_savings']:,.0f}/year savings."
            )
        if pr["utilization_pct"] < 70:
            recs.append(
                f"{pr['product']}: License utilization is {pr['utilization_pct']:.0f}%. "
                f"Consider downsizing from {pr['total_licenses']} to {pr['used_licenses']} licenses at next renewal."
            )

    if total_potential_savings > 0:
        recs.append(f"Total potential savings: ${total_potential_savings:,.0f}/year by removing inactive users.")

    return {
        "organization": org,
        "analysis_date": today.strftime("%Y-%m-%d"),
        "total_annual_cost": round(total_annual_cost, 2),
        "total_potential_savings": round(total_potential_savings, 2),
        "savings_pct": round(total_potential_savings / total_annual_cost * 100, 1) if total_annual_cost > 0 else 0,
        "products": product_results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable license analysis."""
    print(f"\nLicense Analysis: {result['organization']}")
    print(f"Date: {result['analysis_date']}")
    print("=" * 65)
    print(f"Total Annual Cost:      ${result['total_annual_cost']:>12,.0f}")
    print(f"Potential Savings:      ${result['total_potential_savings']:>12,.0f} ({result['savings_pct']:.1f}%)")

    for pr in result["products"]:
        print(f"\n  {pr['product']} ({pr['tier']})")
        print(f"    Licenses: {pr['used_licenses']}/{pr['total_licenses']} ({pr['utilization_pct']:.0f}% utilized)")
        print(f"    Active: {pr['active_users']}  |  Inactive (90d+): {pr['inactive_users_90d']}  |  Never Active: {pr['never_logged_in']}")
        print(f"    Annual Cost: ${pr['annual_cost']:,.0f}  |  Recoverable: {pr['recoverable_licenses']} licenses (${pr['potential_annual_savings']:,.0f}/yr)")

        if pr["inactive_details"]:
            print(f"    Top Inactive Users:")
            for u in pr["inactive_details"][:5]:
                print(f"      - {u['name']} ({u['email']}): {u['days_inactive']} days inactive")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example usage data JSON."""
    example = {
        "organization": "Acme Corp",
        "products": [
            {
                "name": "Jira",
                "tier": "Premium",
                "cost_per_user_month": 14,
                "total_licenses": 100,
                "users": [
                    {"name": "Alice", "email": "alice@acme.com", "last_active": "2026-03-20"},
                    {"name": "Bob", "email": "bob@acme.com", "last_active": "2026-03-18"},
                    {"name": "Carol", "email": "carol@acme.com", "last_active": "2025-11-01"},
                    {"name": "Dave", "email": "dave@acme.com", "last_active": None},
                ],
            },
            {
                "name": "Confluence",
                "tier": "Standard",
                "cost_per_user_month": 6,
                "total_licenses": 100,
                "users": [
                    {"name": "Alice", "email": "alice@acme.com", "last_active": "2026-03-19"},
                    {"name": "Eve", "email": "eve@acme.com", "last_active": "2025-09-15"},
                ],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Atlassian license usage and optimize costs."
    )
    parser.add_argument("--usage", type=str, help="Path to license usage JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example usage data and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.usage:
        parser.error("--usage is required (use --example to see the expected format)")

    data = load_data(args.usage)
    result = analyze_licenses(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
