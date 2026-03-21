#!/usr/bin/env python3
"""Risk Register - Manage and score delivery risks with mitigation tracking.

Reads a risk register and produces a scored, prioritized risk report with
heat map, mitigation status, and trend analysis.

Usage:
    python risk_register.py --risks risks.json
    python risk_register.py --risks risks.json --json
    python risk_register.py --example
"""

import argparse
import json
import sys
from datetime import datetime


SEVERITY_MAP = {
    (4, 4): "Critical", (4, 5): "Critical", (5, 4): "Critical", (5, 5): "Critical",
    (3, 4): "High", (3, 5): "High", (4, 3): "High", (5, 3): "High",
    (3, 3): "High", (4, 2): "High", (5, 2): "High",
    (2, 4): "Medium", (2, 5): "Medium", (2, 3): "Medium",
    (3, 2): "Medium", (4, 1): "Medium", (5, 1): "Medium",
    (1, 4): "Medium", (1, 5): "Medium",
    (2, 2): "Low", (3, 1): "Low", (1, 3): "Low",
    (1, 1): "Low", (1, 2): "Low", (2, 1): "Low",
}


def load_data(path: str) -> dict:
    """Load risk data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def score_risk(risk: dict) -> dict:
    """Score and classify a single risk."""
    probability = risk.get("probability", 1)
    impact = risk.get("impact", 1)
    probability = max(1, min(5, probability))
    impact = max(1, min(5, impact))
    score = probability * impact
    severity = SEVERITY_MAP.get((probability, impact), "Medium")

    mitigation = risk.get("mitigation", {})
    mit_status = mitigation.get("status", "Not Started")
    mit_owner = mitigation.get("owner", "Unassigned")
    mit_actions = mitigation.get("actions", [])

    # Residual risk (after mitigation)
    if mit_status == "Complete":
        residual_prob = max(1, probability - 2)
        residual_impact = max(1, impact - 1)
    elif mit_status == "In Progress":
        residual_prob = max(1, probability - 1)
        residual_impact = impact
    else:
        residual_prob = probability
        residual_impact = impact
    residual_score = residual_prob * residual_impact

    return {
        "id": risk.get("id", "RISK-???"),
        "title": risk.get("title", "Untitled Risk"),
        "category": risk.get("category", "General"),
        "probability": probability,
        "impact": impact,
        "score": score,
        "severity": severity,
        "residual_score": residual_score,
        "mitigation_status": mit_status,
        "mitigation_owner": mit_owner,
        "mitigation_actions": mit_actions,
        "description": risk.get("description", ""),
        "trigger": risk.get("trigger", ""),
    }


def analyze_risks(data: dict) -> dict:
    """Analyze all risks and produce aggregate report."""
    project = data.get("project", "Unknown")
    risks = data.get("risks", [])

    scored_risks = [score_risk(r) for r in risks]
    scored_risks.sort(key=lambda x: x["score"], reverse=True)

    # Aggregate stats
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    mitigation_counts = {"Complete": 0, "In Progress": 0, "Not Started": 0, "Accepted": 0}
    category_counts = {}

    for r in scored_risks:
        severity_counts[r["severity"]] = severity_counts.get(r["severity"], 0) + 1
        mitigation_counts[r["mitigation_status"]] = mitigation_counts.get(r["mitigation_status"], 0) + 1
        cat = r["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    total_exposure = sum(r["score"] for r in scored_risks)
    residual_exposure = sum(r["residual_score"] for r in scored_risks)
    mitigation_effectiveness = round((1 - residual_exposure / total_exposure) * 100, 1) if total_exposure > 0 else 0

    # Overall risk level
    if severity_counts.get("Critical", 0) > 0:
        overall = "Critical"
    elif severity_counts.get("High", 0) > 2:
        overall = "High"
    elif severity_counts.get("High", 0) > 0:
        overall = "Elevated"
    else:
        overall = "Normal"

    # Recommendations
    recs = []
    unmitigated_critical = [r for r in scored_risks if r["severity"] == "Critical" and r["mitigation_status"] in ("Not Started", "Accepted")]
    if unmitigated_critical:
        recs.append(f"{len(unmitigated_critical)} critical risk(s) without active mitigation -- escalate to steering committee immediately.")

    unassigned = [r for r in scored_risks if r["mitigation_owner"] == "Unassigned" and r["severity"] in ("Critical", "High")]
    if unassigned:
        recs.append(f"{len(unassigned)} high/critical risk(s) with no mitigation owner -- assign owners within 48 hours.")

    if mitigation_effectiveness < 30 and len(scored_risks) > 3:
        recs.append("Mitigation effectiveness is low. Review mitigation plans for completeness and execution progress.")

    return {
        "project": project,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_risks": len(scored_risks),
        "overall_risk_level": overall,
        "total_exposure": total_exposure,
        "residual_exposure": residual_exposure,
        "mitigation_effectiveness_pct": mitigation_effectiveness,
        "severity_distribution": severity_counts,
        "mitigation_status": mitigation_counts,
        "category_distribution": category_counts,
        "risks": scored_risks,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable risk register report."""
    print(f"\nRisk Register: {result['project']}")
    print(f"Date: {result['date']}  |  Total Risks: {result['total_risks']}")
    print("=" * 70)
    print(f"Overall Risk Level: {result['overall_risk_level']}")
    print(f"Total Exposure: {result['total_exposure']}  |  Residual: {result['residual_exposure']}  |  Mitigation Effect: {result['mitigation_effectiveness_pct']:.0f}%")
    print()

    sd = result["severity_distribution"]
    print(f"Severity: Critical={sd.get('Critical',0)}, High={sd.get('High',0)}, Medium={sd.get('Medium',0)}, Low={sd.get('Low',0)}")

    print(f"\nRisk Details:")
    print(f"  {'ID':<12} {'Title':<30} {'P':>2} {'I':>2} {'Score':>5} {'Severity':<10} {'Mitigation':<12} {'Owner'}")
    print(f"  {'-'*12} {'-'*30} {'-'*2} {'-'*2} {'-'*5} {'-'*10} {'-'*12} {'-'*15}")
    for r in result["risks"]:
        title = r["title"][:28] + ".." if len(r["title"]) > 30 else r["title"]
        print(f"  {r['id']:<12} {title:<30} {r['probability']:>2} {r['impact']:>2} {r['score']:>5} {r['severity']:<10} {r['mitigation_status']:<12} {r['mitigation_owner']}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"  {i}. {rec}")
    print()


def print_example() -> None:
    """Print example risk register JSON."""
    example = {
        "project": "Platform Migration",
        "risks": [
            {
                "id": "RISK-001",
                "title": "Database migration data loss",
                "category": "Technical",
                "description": "Complex schema migration may cause data corruption",
                "trigger": "Migration script fails during production execution",
                "probability": 3,
                "impact": 5,
                "mitigation": {
                    "status": "In Progress",
                    "owner": "Alice Chen",
                    "actions": ["Run migration on staging with production data copy", "Create rollback script"],
                },
            },
            {
                "id": "RISK-002",
                "title": "Key engineer leaves during migration",
                "category": "Resource",
                "description": "Single point of failure on legacy system knowledge",
                "trigger": "Resignation notice during critical phase",
                "probability": 2,
                "impact": 4,
                "mitigation": {
                    "status": "Not Started",
                    "owner": "Unassigned",
                    "actions": ["Document legacy system architecture", "Cross-train second engineer"],
                },
            },
            {
                "id": "RISK-003",
                "title": "Third-party API rate limit changes",
                "category": "External",
                "description": "Vendor may reduce API limits in next billing cycle",
                "trigger": "Vendor announcement or unexpected 429 errors",
                "probability": 2,
                "impact": 3,
                "mitigation": {
                    "status": "Complete",
                    "owner": "Bob Martinez",
                    "actions": ["Implemented request caching", "Added rate limit monitoring"],
                },
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Manage and score delivery risks with mitigation tracking."
    )
    parser.add_argument("--risks", type=str, help="Path to risk register JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example risk register and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.risks:
        parser.error("--risks is required (use --example to see the expected format)")

    data = load_data(args.risks)
    result = analyze_risks(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
