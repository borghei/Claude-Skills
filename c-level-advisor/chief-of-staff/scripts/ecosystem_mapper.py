#!/usr/bin/env python3
"""
C-Suite Ecosystem Mapper - Visualize advisor relationships and coverage.

Maps the C-suite advisory ecosystem, identifies coverage gaps,
tracks cross-functional dependencies, and generates ecosystem health reports.
"""

import argparse
import json
import sys
from datetime import datetime


ECOSYSTEM = {
    "c_suite": {
        "CEO": {"domain": "Vision, strategy, investor relations", "path": "ceo-advisor"},
        "CTO": {"domain": "Technology, architecture, engineering", "path": "cto-advisor"},
        "CFO": {"domain": "Finance, fundraising, budgets", "path": "cfo-advisor"},
        "CMO": {"domain": "Marketing, positioning, brand", "path": "cmo-advisor"},
        "COO": {"domain": "Operations, process, execution", "path": "coo-advisor"},
        "CHRO": {"domain": "People, hiring, org design", "path": "chro-advisor"},
        "CPO": {"domain": "Product, PMF, portfolio", "path": "cpo-advisor"},
        "CRO": {"domain": "Revenue, sales, pricing", "path": "cro-advisor"},
        "CISO": {"domain": "Security, compliance, risk", "path": "ciso-advisor"},
    },
    "orchestration": {
        "Chief of Staff": {"domain": "Routing, synthesis, decision log", "path": "chief-of-staff"},
        "Board Meeting": {"domain": "Multi-agent deliberation protocol", "path": "board-meeting"},
        "Board Deck Builder": {"domain": "Board presentation assembly", "path": "board-deck-builder"},
        "Decision Logger": {"domain": "Two-layer decision memory", "path": "decision-logger"},
    },
    "strategic": {
        "Competitive Intel": {"domain": "Market and competitor tracking", "path": "competitive-intel"},
        "M&A Playbook": {"domain": "Acquisition and merger strategy", "path": "ma-playbook"},
        "Company OS": {"domain": "Operating system design", "path": "company-os"},
        "Change Management": {"domain": "Organizational change rollout", "path": "change-management"},
        "Culture Architect": {"domain": "Culture as operational system", "path": "culture-architect"},
        "Strategic Alignment": {"domain": "Goal cascade and alignment", "path": "strategic-alignment"},
    },
}

CROSS_DEPENDENCIES = [
    {"from": "CEO", "to": "CFO", "on": "Fundraising, board prep"},
    {"from": "CEO", "to": "CHRO", "on": "Org design, culture"},
    {"from": "CFO", "to": "CHRO", "on": "Headcount budget, equity"},
    {"from": "CTO", "to": "CISO", "on": "Security architecture"},
    {"from": "CTO", "to": "CPO", "on": "Technical feasibility"},
    {"from": "CMO", "to": "CRO", "on": "Pipeline, demand gen"},
    {"from": "CRO", "to": "CFO", "on": "Revenue forecasting"},
    {"from": "CISO", "to": "CRO", "on": "Security questionnaires for deals"},
    {"from": "COO", "to": "CHRO", "on": "Process + people alignment"},
    {"from": "Change Management", "to": "COO", "on": "Process change rollout"},
    {"from": "Change Management", "to": "CHRO", "on": "People impact"},
]


def map_ecosystem(data: dict) -> dict:
    """Map the ecosystem and identify gaps."""
    active_skills = data.get("active_skills", [])
    recent_queries = data.get("recent_queries", [])
    decision_count = data.get("decisions_logged", 0)

    results = {
        "timestamp": datetime.now().isoformat(),
        "ecosystem_summary": {
            "total_skills": sum(len(cat) for cat in ECOSYSTEM.values()),
            "active_skills": len(active_skills),
            "categories": {},
        },
        "category_details": {},
        "coverage_gaps": [],
        "dependency_map": CROSS_DEPENDENCIES,
        "utilization": {},
        "recommendations": [],
    }

    # Category breakdown
    for cat_name, skills in ECOSYSTEM.items():
        active_in_cat = [s for s in skills if s in active_skills or skills[s]["path"] in active_skills]
        coverage = len(active_in_cat) / len(skills) * 100 if skills else 0

        results["ecosystem_summary"]["categories"][cat_name] = {
            "total": len(skills),
            "active": len(active_in_cat),
            "coverage_pct": round(coverage),
        }

        results["category_details"][cat_name] = {}
        for skill_name, config in skills.items():
            is_active = skill_name in active_skills or config["path"] in active_skills
            results["category_details"][cat_name][skill_name] = {
                "domain": config["domain"],
                "path": config["path"],
                "active": is_active,
            }
            if not is_active:
                results["coverage_gaps"].append({
                    "skill": skill_name,
                    "category": cat_name,
                    "domain": config["domain"],
                    "path": config["path"],
                })

    # Utilization from recent queries
    role_usage = {}
    for query in recent_queries:
        role = query.get("routed_to", "")
        if role:
            role_usage[role] = role_usage.get(role, 0) + 1

    results["utilization"] = {
        "queries_analyzed": len(recent_queries),
        "by_role": role_usage,
        "most_consulted": max(role_usage.items(), key=lambda x: x[1])[0] if role_usage else "N/A",
        "least_consulted": min(role_usage.items(), key=lambda x: x[1])[0] if role_usage else "N/A",
        "decisions_logged": decision_count,
    }

    # Recommendations
    if results["coverage_gaps"]:
        gap_count = len(results["coverage_gaps"])
        results["recommendations"].append(f"{gap_count} skills inactive. Consider activating for full coverage.")

    c_suite_gaps = [g for g in results["coverage_gaps"] if g["category"] == "c_suite"]
    if c_suite_gaps:
        results["recommendations"].append(f"C-suite gaps: {', '.join(g['skill'] for g in c_suite_gaps)}. These are core advisory roles.")

    if decision_count == 0:
        results["recommendations"].append("No decisions logged. Implement decision logging to prevent repeated debates.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable ecosystem map."""
    lines = [
        "=" * 60,
        "C-SUITE ECOSYSTEM MAP",
        "=" * 60,
        f"Date: {results['timestamp'][:10]}",
        f"Total Skills: {results['ecosystem_summary']['total_skills']}  |  Active: {results['ecosystem_summary']['active_skills']}",
        "",
    ]

    for cat_name, details in results["category_details"].items():
        cat_summary = results["ecosystem_summary"]["categories"][cat_name]
        lines.append(f"{cat_name.upper().replace('_', ' ')} ({cat_summary['active']}/{cat_summary['total']} active, {cat_summary['coverage_pct']}%)")
        for skill_name, config in details.items():
            icon = "[x]" if config["active"] else "[ ]"
            lines.append(f"  {icon} {skill_name:<20} {config['domain']}")
        lines.append("")

    if results["coverage_gaps"]:
        lines.extend(["COVERAGE GAPS:"])
        for gap in results["coverage_gaps"][:8]:
            lines.append(f"  - {gap['skill']} ({gap['category']}): {gap['domain']}")
        lines.append("")

    lines.extend(["KEY DEPENDENCIES:"])
    for dep in CROSS_DEPENDENCIES[:8]:
        lines.append(f"  {dep['from']} <-> {dep['to']}: {dep['on']}")

    util = results["utilization"]
    if util.get("by_role"):
        lines.extend(["", "UTILIZATION:"])
        for role, count in sorted(util["by_role"].items(), key=lambda x: x[1], reverse=True):
            bar = "#" * min(20, count)
            lines.append(f"  {role:<8} {bar} ({count})")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Map C-suite advisory ecosystem")
    parser.add_argument("--input", "-i", help="JSON file with ecosystem data")
    parser.add_argument("--active", nargs="*", default=[], help="List of active skills")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "active_skills": args.active or ["CEO", "CFO", "CTO", "CMO", "CHRO", "CISO", "CPO", "CRO", "COO", "Chief of Staff", "Board Meeting"],
            "recent_queries": [
                {"routed_to": "CFO"}, {"routed_to": "CFO"}, {"routed_to": "CEO"},
                {"routed_to": "CTO"}, {"routed_to": "CHRO"}, {"routed_to": "CFO"},
                {"routed_to": "CMO"}, {"routed_to": "CISO"},
            ],
            "decisions_logged": 12,
        }

    results = map_ecosystem(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
