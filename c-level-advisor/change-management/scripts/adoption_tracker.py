#!/usr/bin/env python3
"""
Adoption Tracker - Measure and track change adoption vs compliance.

Tracks usage rates, reversion rates, satisfaction, and support requests
to distinguish real adoption from surface compliance.
"""

import argparse
import json
import sys
from datetime import datetime


def track_adoption(data: dict) -> dict:
    """Track adoption metrics and generate report."""
    change_name = data.get("change_name", "Change Initiative")
    go_live_date = data.get("go_live_date", "")
    weekly_data = data.get("weekly_data", [])
    targets = data.get("targets", {})

    results = {
        "timestamp": datetime.now().isoformat(),
        "change_name": change_name,
        "go_live_date": go_live_date,
        "current_week": len(weekly_data),
        "metrics": {},
        "trend_analysis": [],
        "adoption_vs_compliance": {},
        "at_risk_groups": [],
        "recommendations": [],
    }

    # Default targets
    usage_target = targets.get("usage_rate_pct", 80)
    reversion_target = targets.get("reversion_rate_pct", 10)
    satisfaction_target = targets.get("satisfaction_pct", 60)
    target_week = targets.get("target_week", 8)

    # Current state (latest week)
    if weekly_data:
        latest = weekly_data[-1]
        results["metrics"] = {
            "usage_rate_pct": latest.get("usage_rate_pct", 0),
            "usage_target": usage_target,
            "usage_on_track": latest.get("usage_rate_pct", 0) >= usage_target * (len(weekly_data) / target_week),
            "reversion_rate_pct": latest.get("reversion_rate_pct", 0),
            "reversion_target": reversion_target,
            "reversion_ok": latest.get("reversion_rate_pct", 0) <= reversion_target,
            "satisfaction_pct": latest.get("satisfaction_pct", 0),
            "satisfaction_target": satisfaction_target,
            "satisfaction_met": latest.get("satisfaction_pct", 0) >= satisfaction_target,
            "support_requests": latest.get("support_requests", 0),
            "support_trend": "Declining" if len(weekly_data) > 1 and latest.get("support_requests", 0) < weekly_data[-2].get("support_requests", 0) else "Increasing" if len(weekly_data) > 1 and latest.get("support_requests", 0) > weekly_data[-2].get("support_requests", 0) else "Flat",
            "active_users": latest.get("active_users", 0),
            "total_users": latest.get("total_users", 0),
        }

    # Trend analysis
    for i, week in enumerate(weekly_data):
        week_num = i + 1
        results["trend_analysis"].append({
            "week": week_num,
            "usage_rate_pct": week.get("usage_rate_pct", 0),
            "reversion_rate_pct": week.get("reversion_rate_pct", 0),
            "satisfaction_pct": week.get("satisfaction_pct", 0),
            "support_requests": week.get("support_requests", 0),
        })

    # Adoption vs compliance assessment
    m = results["metrics"]
    if m:
        high_usage = m.get("usage_rate_pct", 0) >= 70
        high_satisfaction = m.get("satisfaction_pct", 0) >= 60
        low_reversion = m.get("reversion_rate_pct", 0) <= 15
        declining_support = m.get("support_trend") == "Declining"

        if high_usage and high_satisfaction and low_reversion:
            adoption_type = "True Adoption"
            description = "People use it because it is better. Sustained without enforcement."
        elif high_usage and not high_satisfaction:
            adoption_type = "Compliance Only"
            description = "High usage but low satisfaction. Will revert when enforcement relaxes."
        elif not high_usage and high_satisfaction:
            adoption_type = "Partial Adoption"
            description = "Those using it like it, but many haven't switched. Training/ability gap."
        else:
            adoption_type = "Failed Adoption"
            description = "Low usage and low satisfaction. Reassess the change itself."

        results["adoption_vs_compliance"] = {
            "type": adoption_type,
            "description": description,
            "high_usage": high_usage,
            "high_satisfaction": high_satisfaction,
            "low_reversion": low_reversion,
            "declining_support": declining_support,
        }

    # At-risk groups
    groups = data.get("group_data", [])
    for group in groups:
        if group.get("usage_rate_pct", 100) < 50:
            results["at_risk_groups"].append({
                "group": group.get("name", "Unknown"),
                "usage_rate_pct": group.get("usage_rate_pct", 0),
                "primary_concern": group.get("primary_concern", "Unknown"),
                "recommended_action": "1:1 with group lead to diagnose ADKAR gap",
            })

    # Recommendations
    if results.get("adoption_vs_compliance", {}).get("type") == "Compliance Only":
        results["recommendations"].append("Compliance without adoption detected. Investigate satisfaction drivers. Don't rely on enforcement alone.")
    if results.get("adoption_vs_compliance", {}).get("type") == "Failed Adoption":
        results["recommendations"].append("Consider rolling back or fundamentally redesigning the change.")
    if m and not m.get("usage_on_track"):
        gap = usage_target - m.get("usage_rate_pct", 0)
        results["recommendations"].append(f"Usage {gap:.0f}pp below target trajectory. Increase training and support.")
    if m and m.get("support_trend") == "Increasing":
        results["recommendations"].append("Support requests increasing. Review training materials and common issues.")
    if results["at_risk_groups"]:
        results["recommendations"].append(f"{len(results['at_risk_groups'])} group(s) at risk of non-adoption. Targeted intervention needed.")
    if len(weekly_data) >= target_week and m and m.get("usage_rate_pct", 0) >= usage_target:
        results["recommendations"].append("Adoption target met. Consider deprecating the old system.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    m = results["metrics"]
    avc = results.get("adoption_vs_compliance", {})
    lines = [
        "=" * 60,
        "ADOPTION TRACKER",
        "=" * 60,
        f"Change: {results['change_name']}",
        f"Go-Live: {results['go_live_date']}  |  Current Week: {results['current_week']}",
        "",
    ]

    if m:
        lines.extend([
            "CURRENT METRICS:",
            f"  Usage Rate:      {m.get('usage_rate_pct', 0):>5.0f}% (target: {m.get('usage_target', 0)}%) {'[OK]' if m.get('usage_on_track') else '[BEHIND]'}",
            f"  Reversion Rate:  {m.get('reversion_rate_pct', 0):>5.0f}% (target: <{m.get('reversion_target', 0)}%) {'[OK]' if m.get('reversion_ok') else '[HIGH]'}",
            f"  Satisfaction:    {m.get('satisfaction_pct', 0):>5.0f}% (target: {m.get('satisfaction_target', 0)}%) {'[OK]' if m.get('satisfaction_met') else '[LOW]'}",
            f"  Support Tickets: {m.get('support_requests', 0):>5} ({m.get('support_trend', 'N/A')})",
            f"  Active Users:    {m.get('active_users', 0)}/{m.get('total_users', 0)}",
            "",
        ])

    if avc:
        lines.extend([
            f"ADOPTION TYPE: {avc.get('type', 'N/A')}",
            f"  {avc.get('description', '')}",
            "",
        ])

    if results["trend_analysis"]:
        lines.extend(["WEEKLY TREND:", f"{'Week':>5} {'Usage':>7} {'Revert':>8} {'Satis':>7} {'Support':>8}"])
        for t in results["trend_analysis"]:
            lines.append(f"  W{t['week']:>2}  {t['usage_rate_pct']:>6.0f}% {t['reversion_rate_pct']:>7.0f}% {t['satisfaction_pct']:>6.0f}% {t['support_requests']:>8}")
        lines.append("")

    if results["at_risk_groups"]:
        lines.append("AT-RISK GROUPS:")
        for g in results["at_risk_groups"]:
            lines.append(f"  [!] {g['group']}: {g['usage_rate_pct']}% usage - {g['primary_concern']}")
        lines.append("")

    if results["recommendations"]:
        lines.append("RECOMMENDATIONS:")
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track change adoption metrics")
    parser.add_argument("--input", "-i", help="JSON file with adoption data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "change_name": "New CRM System",
            "go_live_date": "2025-11-01",
            "targets": {"usage_rate_pct": 80, "reversion_rate_pct": 10, "satisfaction_pct": 60, "target_week": 8},
            "weekly_data": [
                {"usage_rate_pct": 25, "reversion_rate_pct": 30, "satisfaction_pct": 40, "support_requests": 45, "active_users": 12, "total_users": 48},
                {"usage_rate_pct": 40, "reversion_rate_pct": 22, "satisfaction_pct": 48, "support_requests": 38, "active_users": 19, "total_users": 48},
                {"usage_rate_pct": 55, "reversion_rate_pct": 18, "satisfaction_pct": 52, "support_requests": 28, "active_users": 26, "total_users": 48},
                {"usage_rate_pct": 62, "reversion_rate_pct": 14, "satisfaction_pct": 55, "support_requests": 20, "active_users": 30, "total_users": 48},
                {"usage_rate_pct": 68, "reversion_rate_pct": 12, "satisfaction_pct": 58, "support_requests": 15, "active_users": 33, "total_users": 48},
            ],
            "group_data": [
                {"name": "Sales Team", "usage_rate_pct": 82, "primary_concern": "None"},
                {"name": "Marketing", "usage_rate_pct": 65, "primary_concern": "Missing integrations"},
                {"name": "Finance", "usage_rate_pct": 35, "primary_concern": "Reporting limitations"},
            ],
        }

    results = track_adoption(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
