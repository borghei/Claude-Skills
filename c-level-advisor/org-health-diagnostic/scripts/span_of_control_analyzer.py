#!/usr/bin/env python3
"""Span of Control Analyzer - Analyze manager-to-IC ratios across the organization.

Reads an organization structure (CSV or inline) and calculates span of control
metrics, flagging unhealthy ratios. Healthy range: 1:5 to 1:8 for most roles.

Usage:
    python span_of_control_analyzer.py --org-file org_structure.csv
    python span_of_control_analyzer.py --managers "CEO:5,VP Eng:8,VP Sales:12,Eng Manager:3,Sales Manager:15" --json
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime

HEALTHY_RANGE = {"min": 5, "max": 8}
ROLE_ADJUSTMENTS = {
    "engineering": {"min": 5, "max": 9, "notes": "Engineering managers can handle slightly larger spans with senior ICs"},
    "sales": {"min": 6, "max": 10, "notes": "Sales managers can manage larger teams with clear metrics"},
    "support": {"min": 8, "max": 15, "notes": "Support teams can have larger spans with process-driven work"},
    "executive": {"min": 4, "max": 7, "notes": "Executives need smaller spans for strategic leadership"},
    "default": {"min": 5, "max": 8, "notes": "Standard management span"}
}


def classify_span(direct_reports, role_type="default"):
    adj = ROLE_ADJUSTMENTS.get(role_type, ROLE_ADJUSTMENTS["default"])
    if direct_reports < adj["min"]:
        return {"status": "TOO_NARROW", "color": "YELLOW", "issue": f"Span too narrow ({direct_reports}); healthy range: {adj['min']}-{adj['max']}. Risk: management overhead, micromanagement"}
    elif direct_reports > adj["max"]:
        return {"status": "TOO_WIDE", "color": "RED" if direct_reports > adj["max"] * 1.5 else "YELLOW", "issue": f"Span too wide ({direct_reports}); healthy range: {adj['min']}-{adj['max']}. Risk: insufficient coaching, burnout"}
    return {"status": "HEALTHY", "color": "GREEN", "issue": None}


def analyze_from_managers(managers_data):
    """Analyze from a dictionary of manager: direct_reports."""
    results = []
    for manager, reports in managers_data.items():
        role_type = "default"
        lower = manager.lower()
        if any(k in lower for k in ["eng", "tech", "cto"]):
            role_type = "engineering"
        elif any(k in lower for k in ["sale", "cro", "revenue"]):
            role_type = "sales"
        elif any(k in lower for k in ["support", "cs ", "service"]):
            role_type = "support"
        elif any(k in lower for k in ["ceo", "coo", "cfo", "vp", "chief", "svp"]):
            role_type = "executive"

        classification = classify_span(reports, role_type)
        results.append({
            "manager": manager,
            "direct_reports": reports,
            "role_type": role_type,
            "status": classification["status"],
            "color": classification["color"],
            "issue": classification["issue"]
        })
    return results


def analyze_from_csv(filepath):
    """Read CSV with columns: employee_name, manager_name, role."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    manager_counts = {}
    manager_roles = {}
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mgr = row.get("manager_name", row.get("manager", "")).strip()
            if mgr:
                manager_counts[mgr] = manager_counts.get(mgr, 0) + 1
                if mgr not in manager_roles:
                    manager_roles[mgr] = row.get("manager_role", row.get("role", "default"))

    managers_data = {}
    for mgr, count in manager_counts.items():
        managers_data[mgr] = count
    return analyze_from_managers(managers_data)


def generate_report(results):
    total_managers = len(results)
    healthy = [r for r in results if r["status"] == "HEALTHY"]
    too_narrow = [r for r in results if r["status"] == "TOO_NARROW"]
    too_wide = [r for r in results if r["status"] == "TOO_WIDE"]

    avg_span = round(sum(r["direct_reports"] for r in results) / total_managers, 1) if total_managers > 0 else 0
    median_span = sorted(r["direct_reports"] for r in results)[total_managers // 2] if total_managers > 0 else 0

    health_pct = round(len(healthy) / total_managers * 100) if total_managers > 0 else 0

    recommendations = []
    for r in too_wide:
        if r["direct_reports"] > 12:
            recommendations.append(f"URGENT: {r['manager']} has {r['direct_reports']} reports -- split team or add manager layer")
        else:
            recommendations.append(f"{r['manager']} has {r['direct_reports']} reports -- consider adding team lead")
    for r in too_narrow:
        if r["direct_reports"] < 3:
            recommendations.append(f"{r['manager']} has only {r['direct_reports']} reports -- consider merging teams or expanding scope")

    return {
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "total_managers": total_managers,
        "average_span": avg_span,
        "median_span": median_span,
        "healthy_percentage": health_pct,
        "summary": {
            "healthy": len(healthy),
            "too_narrow": len(too_narrow),
            "too_wide": len(too_wide)
        },
        "managers": sorted(results, key=lambda r: -r["direct_reports"]),
        "recommendations": recommendations
    }


def print_human(report):
    print(f"\n{'='*70}")
    print(f"SPAN OF CONTROL ANALYSIS")
    print(f"Date: {report['analysis_date']}")
    print(f"{'='*70}\n")

    print(f"Managers Analyzed: {report['total_managers']}")
    print(f"Average Span: {report['average_span']}")
    print(f"Median Span: {report['median_span']}")
    print(f"Healthy: {report['healthy_percentage']}%")
    print(f"  Green: {report['summary']['healthy']}  |  Narrow: {report['summary']['too_narrow']}  |  Wide: {report['summary']['too_wide']}\n")

    print("MANAGER DETAILS:")
    print("-" * 70)
    for m in report["managers"]:
        status_icon = {"GREEN": "+", "YELLOW": "~", "RED": "!"}[m["color"]]
        print(f"  [{status_icon}] {m['manager']:<30s} {m['direct_reports']:>3} reports  ({m['role_type']})  {m['status']}")

    if report["recommendations"]:
        print(f"\nRECOMMENDATIONS:")
        for r in report["recommendations"]:
            print(f"  -> {r}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Analyze manager-to-IC span of control ratios")
    parser.add_argument("--org-file", help="CSV file with employee_name, manager_name columns")
    parser.add_argument("--managers", help="Inline format: 'Manager1:reports,Manager2:reports'")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.org_file:
        results = analyze_from_csv(args.org_file)
    elif args.managers:
        managers_data = {}
        for pair in args.managers.split(","):
            parts = pair.strip().rsplit(":", 1)
            if len(parts) == 2:
                managers_data[parts[0].strip()] = int(parts[1].strip())
        results = analyze_from_managers(managers_data)
    else:
        print("Error: Provide either --org-file or --managers", file=sys.stderr)
        sys.exit(1)

    report = generate_report(results)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)


if __name__ == "__main__":
    main()
