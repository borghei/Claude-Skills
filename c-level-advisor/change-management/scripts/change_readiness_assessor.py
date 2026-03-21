#!/usr/bin/env python3
"""
Change Readiness Assessor - Assess organizational readiness for change using ADKAR.

Evaluates readiness across ADKAR phases, identifies resistance patterns,
measures change fatigue, and generates targeted intervention plans.
"""

import argparse
import json
import sys
from datetime import datetime


ADKAR_PHASES = {
    "awareness": {"weight": 0.20, "failure_symptom": "Nobody told me why", "interventions": ["Re-communicate the WHY with data", "CEO video explaining the change", "FAQ document"]},
    "desire": {"weight": 0.25, "failure_symptom": "I understand but I don't agree", "interventions": ["Address individual concerns in 1:1s", "Involve resisters in HOW", "Show personal benefits"]},
    "knowledge": {"weight": 0.20, "failure_symptom": "I want to but I don't know how", "interventions": ["Training sessions", "Documentation and guides", "Office hours and help desk"]},
    "ability": {"weight": 0.20, "failure_symptom": "I know how but I can't do it yet", "interventions": ["Practice time with reduced workload", "Buddy system", "Support desk"]},
    "reinforcement": {"weight": 0.15, "failure_symptom": "We tried but went back to the old way", "interventions": ["Public wins and recognition", "Remove old system access", "Measure and report adoption"]},
}

RESISTANCE_PATTERNS = {
    "vocal_opposition": {"signal": "I understand but disagree", "phase": "desire", "severity": "medium"},
    "timing_challenge": {"signal": "Why now?", "phase": "awareness", "severity": "low"},
    "process_complaint": {"signal": "I wasn't consulted", "phase": "desire", "severity": "medium"},
    "capacity_excuse": {"signal": "I don't have time", "phase": "ability", "severity": "medium"},
    "historical_reference": {"signal": "We tried this before", "phase": "desire", "severity": "high"},
    "silent_noncompliance": {"signal": "No pushback but doesn't change", "phase": "unknown", "severity": "high"},
    "malicious_compliance": {"signal": "Does it technically but undermines", "phase": "desire", "severity": "critical"},
}

CHANGE_TYPES = {
    "process": {"timeline_weeks": "4-8", "hardest_phase": "ability"},
    "org": {"timeline_weeks": "12-24", "hardest_phase": "desire"},
    "strategy": {"timeline_weeks": "12-48", "hardest_phase": "awareness"},
    "culture": {"timeline_weeks": "48-96", "hardest_phase": "reinforcement"},
}


def assess_readiness(data: dict) -> dict:
    """Assess organizational change readiness."""
    change_type = data.get("change_type", "process")
    adkar_scores = data.get("adkar_scores", {})
    resistance_observed = data.get("resistance_patterns", [])
    active_changes = data.get("active_changes", [])
    stakeholder_count = data.get("affected_stakeholders", 0)

    type_config = CHANGE_TYPES.get(change_type, CHANGE_TYPES["process"])

    results = {
        "timestamp": datetime.now().isoformat(),
        "change_type": change_type,
        "change_description": data.get("change_description", ""),
        "timeline": type_config["timeline_weeks"],
        "hardest_phase": type_config["hardest_phase"],
        "overall_readiness": 0,
        "readiness_label": "",
        "adkar_assessment": {},
        "weakest_phase": "",
        "resistance_analysis": [],
        "fatigue_assessment": {},
        "intervention_plan": [],
        "communication_plan": [],
        "recommendations": [],
    }

    # ADKAR scoring
    total_readiness = 0
    weakest_score = 100
    weakest_phase = ""

    for phase, config in ADKAR_PHASES.items():
        score = adkar_scores.get(phase, 50)  # 0-100
        weighted = score * config["weight"]
        total_readiness += weighted

        if score < weakest_score:
            weakest_score = score
            weakest_phase = phase

        status = "Strong" if score >= 70 else "Adequate" if score >= 50 else "Weak" if score >= 30 else "Critical"
        results["adkar_assessment"][phase] = {
            "score": score,
            "weighted": round(weighted, 1),
            "status": status,
            "failure_symptom": config["failure_symptom"],
            "interventions": config["interventions"] if score < 70 else [],
        }

    results["overall_readiness"] = round(total_readiness, 1)
    results["weakest_phase"] = weakest_phase
    results["readiness_label"] = (
        "Ready" if total_readiness >= 75 else
        "Conditionally Ready" if total_readiness >= 55 else
        "Not Ready" if total_readiness >= 35 else
        "High Risk"
    )

    # Resistance analysis
    for pattern_name in resistance_observed:
        pattern = RESISTANCE_PATTERNS.get(pattern_name, {})
        if pattern:
            results["resistance_analysis"].append({
                "pattern": pattern_name.replace("_", " ").title(),
                "signal": pattern.get("signal", ""),
                "broken_phase": pattern.get("phase", "unknown"),
                "severity": pattern.get("severity", "medium"),
                "recommended_response": ADKAR_PHASES.get(pattern.get("phase", ""), {}).get("interventions", ["Diagnose in 1:1 conversation"])[0],
            })

    # Fatigue assessment
    active_count = len(active_changes)
    avg_absorption = sum(c.get("absorption_pct", 50) for c in active_changes) / max(1, active_count)
    fatigue_level = "Critical" if active_count >= 4 else "High" if active_count >= 3 and avg_absorption < 60 else "Moderate" if active_count >= 2 else "Low"

    results["fatigue_assessment"] = {
        "active_changes": active_count,
        "avg_absorption_pct": round(avg_absorption, 1),
        "fatigue_level": fatigue_level,
        "can_add_change": fatigue_level in ["Low", "Moderate"],
        "recommendation": (
            "Safe to proceed" if fatigue_level == "Low" else
            "Proceed with caution - communicate stability" if fatigue_level == "Moderate" else
            "Pause non-critical changes first" if fatigue_level == "High" else
            "Freeze all new changes. Rebuild trust."
        ),
        "active_change_inventory": active_changes,
    }

    # Intervention plan for weakest phases
    for phase, assessment in results["adkar_assessment"].items():
        if assessment["status"] in ["Weak", "Critical"]:
            for intervention in assessment["interventions"]:
                results["intervention_plan"].append({
                    "phase": phase,
                    "intervention": intervention,
                    "priority": "Immediate" if assessment["status"] == "Critical" else "This week",
                    "owner": "Change sponsor" if phase in ["awareness", "desire"] else "Change team",
                })

    # Communication plan
    results["communication_plan"] = [
        {"audience": "Leadership team", "order": 1, "channel": "In-person meeting", "content": "Full context + their role in rollout"},
        {"audience": "Directly affected employees", "order": 2, "channel": "Manager 1:1 or small group", "content": "Personal impact + support available"},
        {"audience": "All employees", "order": 3, "channel": "All-hands + written Q&A", "content": "WHY + WHAT + timeline + FAQ"},
        {"audience": "External stakeholders", "order": 4, "channel": "Appropriate channel", "content": "Need-to-know only"},
    ]

    # Recommendations
    if results["readiness_label"] == "High Risk":
        results["recommendations"].append("Do not proceed. Address Critical ADKAR gaps first.")
    if results["weakest_phase"]:
        results["recommendations"].append(f"Focus on '{results['weakest_phase']}' phase - scored {weakest_score}/100.")
    if not results["fatigue_assessment"]["can_add_change"]:
        results["recommendations"].append("Change fatigue detected. Complete or pause existing changes before adding new ones.")
    if resistance_observed:
        critical = [r for r in results["resistance_analysis"] if r["severity"] == "critical"]
        if critical:
            results["recommendations"].append(f"URGENT: {len(critical)} critical resistance pattern(s) detected. Address immediately.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    lines = [
        "=" * 60,
        "CHANGE READINESS ASSESSMENT",
        "=" * 60,
        f"Change: {results['change_description'] or results['change_type'].title()}",
        f"Type: {results['change_type'].title()}  |  Timeline: {results['timeline']} weeks",
        f"Overall Readiness: {results['overall_readiness']:.0f}/100 ({results['readiness_label']})",
        f"Weakest Phase: {results['weakest_phase'].upper()}",
        "",
        "ADKAR ASSESSMENT:",
        f"{'Phase':<16} {'Score':>6} {'Status':<12} {'Symptom'}",
        "-" * 60,
    ]

    for phase, a in results["adkar_assessment"].items():
        icon = "[G]" if a["status"] == "Strong" else "[Y]" if a["status"] == "Adequate" else "[R]"
        lines.append(f"{phase.title():<16} {a['score']:>5}/100 {icon} {a['status']:<9} {a['failure_symptom']}")

    if results["resistance_analysis"]:
        lines.extend(["", "RESISTANCE PATTERNS:"])
        for r in results["resistance_analysis"]:
            lines.append(f"  [{r['severity'].upper()}] {r['pattern']}: '{r['signal']}' -> Fix: {r['recommended_response']}")

    fa = results["fatigue_assessment"]
    lines.extend([
        "",
        f"CHANGE FATIGUE: {fa['fatigue_level']} ({fa['active_changes']} active changes, {fa['avg_absorption_pct']:.0f}% avg absorption)",
        f"  {fa['recommendation']}",
    ])

    if results["intervention_plan"]:
        lines.extend(["", "INTERVENTION PLAN:"])
        for ip in results["intervention_plan"][:6]:
            lines.append(f"  [{ip['priority']}] {ip['phase'].title()}: {ip['intervention']} (Owner: {ip['owner']})")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Assess organizational change readiness")
    parser.add_argument("--input", "-i", help="JSON file with assessment data")
    parser.add_argument("--type", choices=["process", "org", "strategy", "culture"], default="process", help="Change type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "change_type": args.type,
            "change_description": "New CRM system rollout",
            "affected_stakeholders": 45,
            "adkar_scores": {"awareness": 70, "desire": 45, "knowledge": 55, "ability": 35, "reinforcement": 60},
            "resistance_patterns": ["process_complaint", "capacity_excuse", "historical_reference"],
            "active_changes": [
                {"name": "Engineering reorg", "absorption_pct": 65},
                {"name": "Values refresh", "absorption_pct": 75},
            ],
        }

    results = assess_readiness(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
