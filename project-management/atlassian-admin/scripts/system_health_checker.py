#!/usr/bin/env python3
"""System Health Checker - Monitor Atlassian instance health metrics.

Reads system health data and produces a status report with performance
indicators, usage trends, and maintenance recommendations.

Usage:
    python system_health_checker.py --health health.json
    python system_health_checker.py --health health.json --json
    python system_health_checker.py --example
"""

import argparse
import json
import sys
from datetime import datetime


THRESHOLDS = {
    "storage_used_pct": {"warning": 75, "critical": 90},
    "api_rate_used_pct": {"warning": 70, "critical": 90},
    "avg_response_ms": {"warning": 2000, "critical": 5000},
    "error_rate_pct": {"warning": 1, "critical": 5},
    "automation_used_pct": {"warning": 80, "critical": 95},
}


def load_data(path: str) -> dict:
    """Load health data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def check_metric(name: str, value: float) -> dict:
    """Check a metric against thresholds."""
    thresholds = THRESHOLDS.get(name, {})
    warning = thresholds.get("warning", float("inf"))
    critical = thresholds.get("critical", float("inf"))

    if value >= critical:
        return {"status": "CRITICAL", "value": value}
    elif value >= warning:
        return {"status": "WARNING", "value": value}
    return {"status": "OK", "value": value}


def analyze_health(data: dict) -> dict:
    """Analyze system health and produce report."""
    org = data.get("organization", "Unknown")
    products = data.get("products", [])

    product_results = []
    overall_issues = []

    for product in products:
        name = product.get("name", "Unknown")
        metrics = product.get("metrics", {})

        checks = {}

        # Storage
        storage_total = metrics.get("storage_total_gb", 0)
        storage_used = metrics.get("storage_used_gb", 0)
        storage_pct = round(storage_used / storage_total * 100, 1) if storage_total > 0 else 0
        checks["storage"] = check_metric("storage_used_pct", storage_pct)
        checks["storage"]["total_gb"] = storage_total
        checks["storage"]["used_gb"] = storage_used
        checks["storage"]["pct"] = storage_pct

        # API Rate Limits
        api_limit = metrics.get("api_rate_limit", 0)
        api_used = metrics.get("api_rate_used", 0)
        api_pct = round(api_used / api_limit * 100, 1) if api_limit > 0 else 0
        checks["api_rate"] = check_metric("api_rate_used_pct", api_pct)
        checks["api_rate"]["limit"] = api_limit
        checks["api_rate"]["used"] = api_used
        checks["api_rate"]["pct"] = api_pct

        # Response Time
        avg_response = metrics.get("avg_response_ms", 0)
        checks["response_time"] = check_metric("avg_response_ms", avg_response)

        # Error Rate
        error_rate = metrics.get("error_rate_pct", 0)
        checks["error_rate"] = check_metric("error_rate_pct", error_rate)

        # Automation Usage
        auto_limit = metrics.get("automation_limit_monthly", 0)
        auto_used = metrics.get("automation_used_monthly", 0)
        auto_pct = round(auto_used / auto_limit * 100, 1) if auto_limit > 0 else 0
        checks["automation"] = check_metric("automation_used_pct", auto_pct)
        checks["automation"]["limit"] = auto_limit
        checks["automation"]["used"] = auto_used
        checks["automation"]["pct"] = auto_pct

        # Usage stats
        usage = {
            "active_users_daily": metrics.get("active_users_daily", 0),
            "active_users_monthly": metrics.get("active_users_monthly", 0),
            "issues_created_30d": metrics.get("issues_created_30d", 0),
            "pages_created_30d": metrics.get("pages_created_30d", 0),
        }

        # Product-level status
        statuses = [c["status"] for c in checks.values()]
        if "CRITICAL" in statuses:
            product_status = "CRITICAL"
        elif "WARNING" in statuses:
            product_status = "WARNING"
        else:
            product_status = "HEALTHY"

        # Collect issues
        for check_name, check_result in checks.items():
            if check_result["status"] != "OK":
                overall_issues.append({
                    "product": name,
                    "check": check_name,
                    "status": check_result["status"],
                    "value": check_result["value"],
                })

        product_results.append({
            "product": name,
            "status": product_status,
            "checks": checks,
            "usage": usage,
        })

    # Overall health
    all_statuses = [p["status"] for p in product_results]
    if "CRITICAL" in all_statuses:
        overall = "CRITICAL"
    elif "WARNING" in all_statuses:
        overall = "WARNING"
    else:
        overall = "HEALTHY"

    # Recommendations
    recs = []
    for issue in overall_issues:
        if issue["check"] == "storage" and issue["status"] == "CRITICAL":
            recs.append(f"{issue['product']}: Storage critical. Archive old projects/spaces and compress attachments immediately.")
        elif issue["check"] == "storage":
            recs.append(f"{issue['product']}: Storage warning. Plan cleanup of inactive content within 30 days.")
        elif issue["check"] == "api_rate" and issue["status"] == "CRITICAL":
            recs.append(f"{issue['product']}: API rate limit nearly exhausted. Audit integrations and optimize API calls.")
        elif issue["check"] == "response_time":
            recs.append(f"{issue['product']}: Response times elevated ({issue['value']}ms). Check for heavy JQL queries or misbehaving apps.")
        elif issue["check"] == "automation":
            recs.append(f"{issue['product']}: Automation executions nearing limit. Optimize rules or upgrade plan tier.")

    if not recs:
        recs.append("All systems healthy. Continue regular monitoring.")

    return {
        "organization": org,
        "check_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "overall_status": overall,
        "products": product_results,
        "issues": overall_issues,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable health report."""
    print(f"\nSystem Health: {result['organization']}")
    print(f"Checked: {result['check_date']}")
    print("=" * 60)
    print(f"Overall Status: {result['overall_status']}")

    for pr in result["products"]:
        print(f"\n  [{pr['status']}] {pr['product']}")
        c = pr["checks"]
        print(f"    Storage:     {c['storage']['used_gb']:.1f}/{c['storage']['total_gb']:.0f} GB ({c['storage']['pct']:.0f}%)  [{c['storage']['status']}]")
        print(f"    API Rate:    {c['api_rate']['used']}/{c['api_rate']['limit']} ({c['api_rate']['pct']:.0f}%)  [{c['api_rate']['status']}]")
        print(f"    Response:    {c['response_time']['value']}ms  [{c['response_time']['status']}]")
        print(f"    Error Rate:  {c['error_rate']['value']}%  [{c['error_rate']['status']}]")
        print(f"    Automation:  {c['automation']['used']}/{c['automation']['limit']} ({c['automation']['pct']:.0f}%)  [{c['automation']['status']}]")
        u = pr["usage"]
        print(f"    Usage: {u['active_users_daily']} DAU / {u['active_users_monthly']} MAU")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example health data JSON."""
    example = {
        "organization": "Acme Corp",
        "products": [
            {
                "name": "Jira",
                "metrics": {
                    "storage_total_gb": 50, "storage_used_gb": 38,
                    "api_rate_limit": 100000, "api_rate_used": 72000,
                    "avg_response_ms": 1200, "error_rate_pct": 0.3,
                    "automation_limit_monthly": 1500, "automation_used_monthly": 1350,
                    "active_users_daily": 85, "active_users_monthly": 120,
                    "issues_created_30d": 450,
                },
            },
            {
                "name": "Confluence",
                "metrics": {
                    "storage_total_gb": 30, "storage_used_gb": 12,
                    "api_rate_limit": 50000, "api_rate_used": 8000,
                    "avg_response_ms": 800, "error_rate_pct": 0.1,
                    "automation_limit_monthly": 500, "automation_used_monthly": 100,
                    "active_users_daily": 45, "active_users_monthly": 95,
                    "pages_created_30d": 120,
                },
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Atlassian instance health metrics."
    )
    parser.add_argument("--health", type=str, help="Path to health data JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example health data and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.health:
        parser.error("--health is required (use --example to see the expected format)")

    data = load_data(args.health)
    result = analyze_health(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
