#!/usr/bin/env python3
"""
Retention Risk Scorer - Assess employee retention risk and generate interventions.

Scores individuals across compensation, manager relationship, career growth,
engagement, tenure, and market demand. Generates prioritized intervention plans.
"""

import argparse
import json
import sys
from datetime import datetime


RISK_FACTORS = {
    "comp_competitiveness": {"weight": 0.20, "scores": {1: "Above P50", 2: "At P50", 3: "Below P50"}},
    "manager_relationship": {"weight": 0.20, "scores": {1: "Strong trust", 2: "Adequate", 3: "Friction or distrust"}},
    "career_growth": {"weight": 0.20, "scores": {1: "Clear path, progressing", 2: "Path exists, slow", 3: "No visible path"}},
    "engagement": {"weight": 0.15, "scores": {1: "High eNPS, advocates", 2: "Neutral", 3: "Disengaged"}},
    "tenure_risk": {"weight": 0.10, "scores": {1: "< 1yr or > 3yr", 2: "1-2 years", 3: "18-24 months (cliff)"}},
    "external_demand": {"weight": 0.15, "scores": {1: "Low market demand", 2: "Moderate", 3: "Hot market, recruiters active"}},
}

INTERVENTIONS = {
    "low": ["Standard: competitive comp, regular 1:1s, career conversations", "Timeline: monitor quarterly"],
    "medium": ["Proactive: skip-level conversation, comp review, stretch project", "Timeline: act within 30 days"],
    "high": ["Urgent: retention package (comp + equity + role change), CEO involvement", "Timeline: act within 7 days"],
}


def score_retention(data: dict) -> dict:
    """Score retention risk for employees."""
    employees = data.get("employees", [])

    results = {
        "timestamp": datetime.now().isoformat(),
        "total_assessed": len(employees),
        "risk_distribution": {"low": 0, "medium": 0, "high": 0},
        "employee_scores": [],
        "high_risk_list": [],
        "intervention_plan": [],
        "org_level_risks": [],
        "recommendations": [],
    }

    manager_issues = {}
    dept_risks = {}

    for emp in employees:
        name = emp.get("name", "Employee")
        role = emp.get("role", "")
        department = emp.get("department", "")
        manager = emp.get("manager", "")
        is_key_person = emp.get("key_person", False)

        total_score = 0
        factor_details = {}
        for factor, config in RISK_FACTORS.items():
            score = emp.get(factor, 2)  # Default medium
            score = min(3, max(1, score))
            weighted = score * config["weight"]
            total_score += weighted
            factor_details[factor] = {"score": score, "label": config["scores"].get(score, ""), "weighted": round(weighted, 2)}

        # Normalize to 6-18 range, then categorize
        raw_total = sum(emp.get(f, 2) for f in RISK_FACTORS)
        if raw_total <= 8:
            risk_level = "low"
        elif raw_total <= 13:
            risk_level = "medium"
        else:
            risk_level = "high"

        emp_result = {
            "name": name,
            "role": role,
            "department": department,
            "manager": manager,
            "key_person": is_key_person,
            "raw_score": raw_total,
            "risk_level": risk_level,
            "factors": factor_details,
            "top_risk_factor": max(factor_details.items(), key=lambda x: x[1]["score"])[0],
        }
        results["employee_scores"].append(emp_result)
        results["risk_distribution"][risk_level] += 1

        if risk_level == "high":
            results["high_risk_list"].append(emp_result)
            urgency = "IMMEDIATE" if is_key_person else "This week"
            results["intervention_plan"].append({
                "employee": name,
                "role": role,
                "risk_score": raw_total,
                "urgency": urgency,
                "top_factor": emp_result["top_risk_factor"],
                "interventions": INTERVENTIONS["high"],
            })
        elif risk_level == "medium":
            results["intervention_plan"].append({
                "employee": name,
                "role": role,
                "risk_score": raw_total,
                "urgency": "Within 30 days",
                "top_factor": emp_result["top_risk_factor"],
                "interventions": INTERVENTIONS["medium"],
            })

        # Track manager-level patterns
        if emp.get("manager_relationship", 2) == 3:
            manager_issues[manager] = manager_issues.get(manager, 0) + 1

        # Track department risks
        if department not in dept_risks:
            dept_risks[department] = {"total": 0, "high": 0}
        dept_risks[department]["total"] += 1
        if risk_level == "high":
            dept_risks[department]["high"] += 1

    # Sort intervention plan by urgency
    urgency_order = {"IMMEDIATE": 0, "This week": 1, "Within 30 days": 2}
    results["intervention_plan"].sort(key=lambda x: urgency_order.get(x["urgency"], 3))

    # Org-level risks
    for manager, count in manager_issues.items():
        if count >= 2:
            results["org_level_risks"].append({
                "type": "Manager issue",
                "detail": f"{manager} has {count} reports with manager relationship friction",
                "action": "Investigate manager effectiveness. This is a manager problem, not a culture problem.",
            })

    for dept, stats in dept_risks.items():
        if stats["high"] >= 2:
            results["org_level_risks"].append({
                "type": "Department risk",
                "detail": f"{dept} has {stats['high']}/{stats['total']} employees at high retention risk",
                "action": "Department-wide retention review needed.",
            })

    # Recommendations
    high_count = results["risk_distribution"]["high"]
    total = results["total_assessed"]
    high_pct = (high_count / total * 100) if total > 0 else 0

    if high_pct > 15:
        results["recommendations"].append(f"URGENT: {high_pct:.0f}% of assessed employees are high risk. Structural intervention needed.")
    if high_count > 0:
        key_persons_at_risk = [e for e in results["high_risk_list"] if e["key_person"]]
        if key_persons_at_risk:
            results["recommendations"].append(f"{len(key_persons_at_risk)} key person(s) at high risk. CEO involvement required.")
    if manager_issues:
        results["recommendations"].append(f"{len(manager_issues)} manager(s) flagged for relationship issues across multiple reports.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    rd = results["risk_distribution"]
    lines = [
        "=" * 70,
        "RETENTION RISK ASSESSMENT",
        "=" * 70,
        f"Date: {results['timestamp'][:10]}  |  Employees Assessed: {results['total_assessed']}",
        f"Distribution: {rd['low']} Low  |  {rd['medium']} Medium  |  {rd['high']} High",
        "",
        f"{'Name':<20} {'Role':<18} {'Dept':<12} {'Score':>6} {'Risk':<8} {'Top Factor'}",
        "-" * 70,
    ]

    for e in sorted(results["employee_scores"], key=lambda x: x["raw_score"], reverse=True):
        icon = "[R]" if e["risk_level"] == "high" else "[Y]" if e["risk_level"] == "medium" else "[G]"
        key = " *" if e["key_person"] else ""
        lines.append(
            f"{e['name']:<20} {e['role']:<18} {e['department']:<12} {e['raw_score']:>5}/18 "
            f"{icon} {e['risk_level']:<5}{key} {e['top_risk_factor']}"
        )

    if results["intervention_plan"]:
        lines.extend(["", "INTERVENTION PLAN:"])
        for ip in results["intervention_plan"][:8]:
            lines.append(f"  [{ip['urgency']}] {ip['employee']} ({ip['role']})")
            lines.append(f"    Factor: {ip['top_factor']}  |  {ip['interventions'][0]}")

    if results["org_level_risks"]:
        lines.extend(["", "ORG-LEVEL RISKS:"])
        for r in results["org_level_risks"]:
            lines.append(f"  [{r['type']}] {r['detail']}")
            lines.append(f"    Action: {r['action']}")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "* = key person", "=" * 70])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score employee retention risk")
    parser.add_argument("--input", "-i", help="JSON file with employee data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {"employees": [
            {"name": "Alice Chen", "role": "Sr Engineer", "department": "Engineering", "manager": "Bob", "key_person": True, "comp_competitiveness": 3, "manager_relationship": 2, "career_growth": 3, "engagement": 2, "tenure_risk": 3, "external_demand": 3},
            {"name": "David Kim", "role": "Product Manager", "department": "Product", "manager": "Sarah", "key_person": True, "comp_competitiveness": 2, "manager_relationship": 1, "career_growth": 2, "engagement": 1, "tenure_risk": 1, "external_demand": 2},
            {"name": "Emma Wilson", "role": "SDR Lead", "department": "Sales", "manager": "Tom", "key_person": False, "comp_competitiveness": 2, "manager_relationship": 3, "career_growth": 2, "engagement": 3, "tenure_risk": 3, "external_demand": 2},
            {"name": "Frank Lopez", "role": "DevOps", "department": "Engineering", "manager": "Bob", "key_person": False, "comp_competitiveness": 3, "manager_relationship": 3, "career_growth": 2, "engagement": 2, "tenure_risk": 2, "external_demand": 3},
            {"name": "Grace Park", "role": "Marketing Dir", "department": "Marketing", "manager": "CEO", "key_person": True, "comp_competitiveness": 1, "manager_relationship": 1, "career_growth": 1, "engagement": 1, "tenure_risk": 1, "external_demand": 2},
        ]}

    results = score_retention(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
