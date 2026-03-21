#!/usr/bin/env python3
"""MarTech Stack Auditor - Audit marketing technology stack for gaps and redundancies.

Evaluates each tool on integration health, utilization, cost efficiency,
and identifies overlaps, gaps, and optimization opportunities.

Usage:
    python martech_stack_auditor.py stack.json
    python martech_stack_auditor.py stack.json --json
    python martech_stack_auditor.py --demo
"""

import argparse
import json
import sys


REQUIRED_CATEGORIES = {
    "crm": {"priority": "critical", "description": "Customer relationship management"},
    "marketing_automation": {"priority": "critical", "description": "Email workflows, lead scoring"},
    "analytics": {"priority": "critical", "description": "Traffic and behavior tracking"},
    "email": {"priority": "critical", "description": "Email sending and deliverability"},
    "ad_platforms": {"priority": "high", "description": "Paid advertising management"},
    "seo": {"priority": "high", "description": "Keyword research and tracking"},
    "social_management": {"priority": "medium", "description": "Social publishing and scheduling"},
    "content_management": {"priority": "high", "description": "Content creation and hosting"},
    "attribution": {"priority": "medium", "description": "Multi-touch attribution"},
    "abm": {"priority": "medium", "description": "Account-based marketing"},
}


def audit_stack(tools):
    """Audit a MarTech stack for gaps, redundancies, and optimization."""
    categories_covered = {}
    total_annual_cost = 0
    tool_results = []

    for tool in tools:
        name = tool.get("name", "Unknown")
        category = tool.get("category", "other")
        annual_cost = tool.get("annual_cost", 0)
        utilization = tool.get("utilization_pct", 50)  # 0-100
        integrations = tool.get("integrations", [])
        has_crm_integration = tool.get("crm_connected", False)
        owner = tool.get("owner", "unassigned")
        users = tool.get("active_users", 0)

        total_annual_cost += annual_cost

        # Score the tool
        scores = {}

        # Integration score
        integration_score = min(100, len(integrations) * 15)
        if has_crm_integration:
            integration_score = min(100, integration_score + 30)
        scores["integration"] = integration_score

        # Utilization score
        scores["utilization"] = utilization

        # Cost efficiency (cost per user per month)
        if users > 0 and annual_cost > 0:
            cost_per_user_month = annual_cost / 12 / users
            scores["cost_efficiency"] = max(0, 100 - cost_per_user_month)  # Lower cost = higher score
        else:
            scores["cost_efficiency"] = 50

        # Ownership
        scores["governance"] = 100 if owner != "unassigned" else 0

        overall = sum(scores.values()) / len(scores)

        # Issues
        issues = []
        if not has_crm_integration:
            issues.append({"severity": "high", "issue": "Not connected to CRM"})
        if utilization < 30:
            issues.append({"severity": "high", "issue": f"Low utilization ({utilization}%)"})
        elif utilization < 60:
            issues.append({"severity": "medium", "issue": f"Moderate utilization ({utilization}%)"})
        if owner == "unassigned":
            issues.append({"severity": "medium", "issue": "No assigned owner"})

        # Track categories
        if category not in categories_covered:
            categories_covered[category] = []
        categories_covered[category].append(name)

        tool_results.append({
            "name": name,
            "category": category,
            "annual_cost": annual_cost,
            "utilization": utilization,
            "crm_connected": has_crm_integration,
            "active_users": users,
            "owner": owner,
            "scores": scores,
            "overall_score": round(overall, 1),
            "issues": issues,
            "recommendation": _recommend(overall, utilization, annual_cost),
        })

    # Identify redundancies (multiple tools in same category)
    redundancies = {cat: tools_list for cat, tools_list in categories_covered.items() if len(tools_list) > 1}

    # Identify gaps (required categories not covered)
    gaps = []
    for cat, config in REQUIRED_CATEGORIES.items():
        if cat not in categories_covered:
            gaps.append({
                "category": cat,
                "priority": config["priority"],
                "description": config["description"],
            })

    # Cost optimization
    low_util_cost = sum(t["annual_cost"] for t in tool_results if t["utilization"] < 30)
    potential_savings = low_util_cost * 0.5  # Assume 50% could be saved

    # Stack health score
    coverage_score = (len(categories_covered) / len(REQUIRED_CATEGORIES)) * 100
    avg_tool_score = sum(t["overall_score"] for t in tool_results) / max(len(tool_results), 1)
    redundancy_penalty = len(redundancies) * 5
    stack_health = max(0, min(100, (coverage_score + avg_tool_score) / 2 - redundancy_penalty))

    return {
        "stack_health": round(stack_health, 1),
        "total_tools": len(tools),
        "total_annual_cost": total_annual_cost,
        "potential_savings": round(potential_savings, 2),
        "categories_covered": len(categories_covered),
        "categories_required": len(REQUIRED_CATEGORIES),
        "tools": sorted(tool_results, key=lambda x: x["overall_score"]),
        "redundancies": redundancies,
        "gaps": sorted(gaps, key=lambda x: {"critical": 0, "high": 1, "medium": 2}[x["priority"]]),
        "recommendations": _stack_recommendations(tool_results, redundancies, gaps),
    }


def _recommend(score, utilization, cost):
    if score < 40 and utilization < 30:
        return "REMOVE - Low score and utilization"
    elif score < 50:
        return "REVIEW - Consider replacement or better integration"
    elif utilization < 40:
        return "TRAIN - Increase adoption through team training"
    elif score >= 75:
        return "KEEP - Well-utilized and integrated"
    return "OPTIMIZE - Good tool, improve integration or usage"


def _stack_recommendations(tools, redundancies, gaps):
    recs = []
    if gaps:
        critical_gaps = [g for g in gaps if g["priority"] == "critical"]
        if critical_gaps:
            recs.append(f"CRITICAL: Missing {len(critical_gaps)} essential categories: {', '.join(g['category'] for g in critical_gaps)}")
    if redundancies:
        recs.append(f"REDUNDANCY: {len(redundancies)} categories have overlapping tools. Consolidate to reduce cost.")
    low_util = [t for t in tools if t["utilization"] < 30]
    if low_util:
        recs.append(f"WASTE: {len(low_util)} tools have <30% utilization. Review for removal or training.")
    disconnected = [t for t in tools if not t["crm_connected"]]
    if disconnected:
        recs.append(f"INTEGRATION: {len(disconnected)} tools not connected to CRM. Data silos likely.")
    return recs


def get_demo_data():
    return [
        {"name": "HubSpot", "category": "marketing_automation", "annual_cost": 14400, "utilization_pct": 85, "crm_connected": True, "integrations": ["salesforce", "slack", "ga4"], "owner": "Marketing Ops", "active_users": 12},
        {"name": "Google Analytics 4", "category": "analytics", "annual_cost": 0, "utilization_pct": 70, "crm_connected": False, "integrations": ["google_ads", "gtm"], "owner": "Marketing Ops", "active_users": 20},
        {"name": "Ahrefs", "category": "seo", "annual_cost": 2388, "utilization_pct": 45, "crm_connected": False, "integrations": [], "owner": "Content Lead", "active_users": 3},
        {"name": "SEMrush", "category": "seo", "annual_cost": 2400, "utilization_pct": 20, "crm_connected": False, "integrations": [], "owner": "unassigned", "active_users": 1},
        {"name": "Buffer", "category": "social_management", "annual_cost": 600, "utilization_pct": 60, "crm_connected": False, "integrations": ["twitter", "linkedin"], "owner": "Social Lead", "active_users": 3},
        {"name": "Salesforce", "category": "crm", "annual_cost": 36000, "utilization_pct": 80, "crm_connected": True, "integrations": ["hubspot", "slack", "zoom"], "owner": "Sales Ops", "active_users": 25},
    ]


def format_report(analysis):
    """Format human-readable audit report."""
    lines = []
    lines.append("=" * 70)
    lines.append("MARTECH STACK AUDIT REPORT")
    lines.append("=" * 70)
    lines.append(f"Stack Health:      {analysis['stack_health']:.0f}/100")
    lines.append(f"Total Tools:       {analysis['total_tools']}")
    lines.append(f"Annual Cost:       ${analysis['total_annual_cost']:,.0f}")
    lines.append(f"Potential Savings: ${analysis['potential_savings']:,.0f}")
    lines.append(f"Coverage:          {analysis['categories_covered']}/{analysis['categories_required']} required categories")
    lines.append("")

    # Tool breakdown
    lines.append("--- TOOL SCORES ---")
    lines.append(f"{'Tool':<20} {'Category':<22} {'Cost':>8} {'Util':>5} {'Score':>6} {'Action':>8}")
    lines.append("-" * 75)
    for t in sorted(analysis["tools"], key=lambda x: x["overall_score"]):
        lines.append(
            f"{t['name']:<20} {t['category']:<22} ${t['annual_cost']:>7,} {t['utilization']:>4}% {t['overall_score']:>5.0f} {t['recommendation'].split(' - ')[0]:>8}"
        )
    lines.append("")

    # Gaps
    if analysis["gaps"]:
        lines.append("--- GAPS ---")
        for g in analysis["gaps"]:
            lines.append(f"  [{g['priority'].upper()}] Missing: {g['category']} - {g['description']}")
        lines.append("")

    # Redundancies
    if analysis["redundancies"]:
        lines.append("--- REDUNDANCIES ---")
        for cat, tool_names in analysis["redundancies"].items():
            lines.append(f"  {cat}: {', '.join(tool_names)} (consolidate to save cost)")
        lines.append("")

    # Recommendations
    if analysis["recommendations"]:
        lines.append("--- RECOMMENDATIONS ---")
        for rec in analysis["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit MarTech stack for gaps and redundancies")
    parser.add_argument("input", nargs="?", help="JSON file with tool data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        tools = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            tools = data if isinstance(data, list) else data.get("tools", data.get("stack", []))
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = audit_stack(tools)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
