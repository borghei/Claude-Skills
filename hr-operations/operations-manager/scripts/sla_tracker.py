#!/usr/bin/env python3
"""
SLA Tracker - Track and analyze SLA compliance across service tickets.

Reads a CSV of service tickets with timestamps and SLA targets, then computes
compliance rates, breach analysis, trend detection, and priority-level breakdowns.

Usage:
    python sla_tracker.py --file tickets.csv
    python sla_tracker.py --file tickets.csv --threshold 95 --json
    python sla_tracker.py --file tickets.csv --period month

Input CSV columns:
    ticket_id       - Unique ticket identifier
    category        - Service category or type
    priority        - Priority level (P1/Critical, P2/High, P3/Medium, P4/Low)
    team            - Assigned team
    created_date    - Ticket creation date (YYYY-MM-DD)
    resolved_date   - Ticket resolution date (YYYY-MM-DD, blank if open)
    sla_target_hrs  - SLA target in hours for this ticket
    actual_hrs      - Actual resolution time in hours (blank if open)
    status          - Status: open, resolved, breached, escalated

Output: SLA compliance report with breach analysis, team performance, and trends.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime


PRIORITY_MAP = {
    "p1": "P1-Critical",
    "critical": "P1-Critical",
    "p2": "P2-High",
    "high": "P2-High",
    "p3": "P3-Medium",
    "medium": "P3-Medium",
    "p4": "P4-Low",
    "low": "P4-Low",
}


def read_csv(path: str) -> list:
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"ticket_id", "sla_target_hrs"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            print(f"Error: Missing required columns: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    return rows


def safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def parse_date(val: str) -> datetime:
    if not val or not val.strip():
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(val.strip(), fmt)
        except ValueError:
            continue
    return None


def normalize_priority(val: str) -> str:
    """Normalize priority value."""
    if not val:
        return "P3-Medium"
    return PRIORITY_MAP.get(val.strip().lower(), val.strip())


def get_period_key(dt: datetime, period_type: str) -> str:
    """Get period key from datetime."""
    if not dt:
        return "Unknown"
    if period_type == "week":
        return f"{dt.year}-W{dt.isocalendar()[1]:02d}"
    elif period_type == "month":
        return f"{dt.year}-{dt.month:02d}"
    elif period_type == "quarter":
        q = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{q}"
    else:
        return f"{dt.year}-{dt.month:02d}"


def analyze_tickets(rows: list, period_type: str) -> dict:
    """Analyze all tickets for SLA compliance."""
    tickets = []
    for row in rows:
        sla_target = safe_float(row.get("sla_target_hrs"))
        actual = safe_float(row.get("actual_hrs"))
        status = row.get("status", "").strip().lower()
        priority = normalize_priority(row.get("priority", ""))
        team = row.get("team", "Unknown").strip() or "Unknown"
        category = row.get("category", "Unknown").strip() or "Unknown"
        created = parse_date(row.get("created_date", ""))

        is_resolved = status in ("resolved", "closed") or actual > 0
        is_open = status in ("open", "in_progress", "escalated") and actual <= 0

        if is_resolved and sla_target > 0:
            met_sla = actual <= sla_target
            breach_hours = max(0, actual - sla_target) if not met_sla else 0
            breach_pct = round((actual - sla_target) / sla_target * 100, 1) if not met_sla else 0
        else:
            met_sla = None
            breach_hours = 0
            breach_pct = 0

        period = get_period_key(created, period_type) if created else "Unknown"

        tickets.append({
            "ticket_id": row["ticket_id"],
            "category": category,
            "priority": priority,
            "team": team,
            "period": period,
            "sla_target_hrs": sla_target,
            "actual_hrs": actual,
            "status": status,
            "is_resolved": is_resolved,
            "is_open": is_open,
            "met_sla": met_sla,
            "breach_hours": round(breach_hours, 1),
            "breach_pct": breach_pct,
        })

    return tickets


def compute_overall_metrics(tickets: list) -> dict:
    """Compute overall SLA metrics."""
    total = len(tickets)
    resolved = [t for t in tickets if t["is_resolved"]]
    open_tickets = [t for t in tickets if t["is_open"]]
    sla_measured = [t for t in resolved if t["met_sla"] is not None]
    met = [t for t in sla_measured if t["met_sla"]]
    breached = [t for t in sla_measured if not t["met_sla"]]

    compliance_rate = round(len(met) / max(1, len(sla_measured)) * 100, 1)

    # Average resolution time
    actual_times = [t["actual_hrs"] for t in resolved if t["actual_hrs"] > 0]
    avg_resolution = round(sum(actual_times) / max(1, len(actual_times)), 1) if actual_times else 0

    # Average breach severity
    breach_amounts = [t["breach_hours"] for t in breached]
    avg_breach = round(sum(breach_amounts) / max(1, len(breach_amounts)), 1) if breach_amounts else 0

    return {
        "total_tickets": total,
        "resolved": len(resolved),
        "open": len(open_tickets),
        "sla_measured": len(sla_measured),
        "met_sla": len(met),
        "breached_sla": len(breached),
        "compliance_rate_pct": compliance_rate,
        "avg_resolution_hrs": avg_resolution,
        "avg_breach_hrs": avg_breach,
        "max_breach_hrs": round(max(breach_amounts, default=0), 1),
    }


def compute_priority_breakdown(tickets: list) -> list:
    """Compute SLA metrics by priority."""
    priority_data = defaultdict(lambda: {"total": 0, "met": 0, "breached": 0, "actual_times": [], "breach_times": []})

    for t in tickets:
        if t["met_sla"] is not None:
            priority_data[t["priority"]]["total"] += 1
            if t["met_sla"]:
                priority_data[t["priority"]]["met"] += 1
            else:
                priority_data[t["priority"]]["breached"] += 1
                priority_data[t["priority"]]["breach_times"].append(t["breach_hours"])
            if t["actual_hrs"] > 0:
                priority_data[t["priority"]]["actual_times"].append(t["actual_hrs"])

    results = []
    for priority in sorted(priority_data.keys()):
        data = priority_data[priority]
        compliance = round(data["met"] / max(1, data["total"]) * 100, 1)
        avg_time = round(sum(data["actual_times"]) / max(1, len(data["actual_times"])), 1) if data["actual_times"] else 0
        results.append({
            "priority": priority,
            "total": data["total"],
            "met": data["met"],
            "breached": data["breached"],
            "compliance_pct": compliance,
            "avg_resolution_hrs": avg_time,
        })

    return results


def compute_team_breakdown(tickets: list) -> list:
    """Compute SLA metrics by team."""
    team_data = defaultdict(lambda: {"total": 0, "met": 0, "breached": 0, "actual_times": []})

    for t in tickets:
        if t["met_sla"] is not None:
            team_data[t["team"]]["total"] += 1
            if t["met_sla"]:
                team_data[t["team"]]["met"] += 1
            else:
                team_data[t["team"]]["breached"] += 1
            if t["actual_hrs"] > 0:
                team_data[t["team"]]["actual_times"].append(t["actual_hrs"])

    results = []
    for team in sorted(team_data.keys()):
        data = team_data[team]
        compliance = round(data["met"] / max(1, data["total"]) * 100, 1)
        avg_time = round(sum(data["actual_times"]) / max(1, len(data["actual_times"])), 1) if data["actual_times"] else 0
        results.append({
            "team": team,
            "total": data["total"],
            "met": data["met"],
            "breached": data["breached"],
            "compliance_pct": compliance,
            "avg_resolution_hrs": avg_time,
        })

    results.sort(key=lambda x: x["compliance_pct"])
    return results


def compute_trend(tickets: list) -> list:
    """Compute SLA compliance trend by period."""
    period_data = defaultdict(lambda: {"total": 0, "met": 0})

    for t in tickets:
        if t["met_sla"] is not None:
            period_data[t["period"]]["total"] += 1
            if t["met_sla"]:
                period_data[t["period"]]["met"] += 1

    results = []
    for period in sorted(period_data.keys()):
        data = period_data[period]
        compliance = round(data["met"] / max(1, data["total"]) * 100, 1)
        results.append({
            "period": period,
            "total": data["total"],
            "met": data["met"],
            "breached": data["total"] - data["met"],
            "compliance_pct": compliance,
        })

    return results


def find_worst_breaches(tickets: list, top_n: int = 10) -> list:
    """Find the worst SLA breaches."""
    breached = [t for t in tickets if t["met_sla"] is False]
    breached.sort(key=lambda x: x["breach_hours"], reverse=True)
    return breached[:top_n]


def build_recommendations(overall: dict, priority: list, teams: list, trend: list, threshold: float) -> list:
    """Generate recommendations."""
    recs = []

    if overall["compliance_rate_pct"] < threshold:
        recs.append(
            f"Overall SLA compliance ({overall['compliance_rate_pct']}%) is below the {threshold}% target. "
            f"{overall['breached_sla']} tickets breached SLA with an average overshoot of {overall['avg_breach_hrs']} hours."
        )

    # Priority-specific issues
    for p in priority:
        if "Critical" in p["priority"] and p["compliance_pct"] < 95:
            recs.append(
                f"{p['priority']} compliance at {p['compliance_pct']}% is below 95% target. "
                f"{p['breached']} critical tickets breached SLA. Implement immediate escalation triggers."
            )
        elif "High" in p["priority"] and p["compliance_pct"] < 90:
            recs.append(
                f"{p['priority']} compliance at {p['compliance_pct']}% is below 90% target. "
                "Review triage and assignment processes for high-priority tickets."
            )

    # Underperforming teams
    low_teams = [t for t in teams if t["compliance_pct"] < threshold and t["total"] >= 5]
    for t in low_teams[:3]:
        recs.append(
            f"Team '{t['team']}' compliance at {t['compliance_pct']}% ({t['breached']} breaches). "
            "Investigate capacity, skill gaps, or process issues."
        )

    # Trend analysis
    if len(trend) >= 2:
        recent = trend[-1]["compliance_pct"]
        previous = trend[-2]["compliance_pct"]
        if recent < previous - 5:
            recs.append(
                f"Compliance trending down: {previous}% -> {recent}% in the most recent period. "
                "Investigate whether this is driven by volume increase, staffing changes, or process degradation."
            )

    if not recs:
        recs.append(f"SLA compliance is meeting the {threshold}% target. Continue monitoring and look for incremental improvements.")

    return recs


def format_human(overall: dict, priority: list, teams: list, trend: list,
                 worst: list, recommendations: list, threshold: float) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("SLA COMPLIANCE REPORT")
    lines.append("=" * 70)
    lines.append("")

    status = "MEETING TARGET" if overall["compliance_rate_pct"] >= threshold else "BELOW TARGET"
    lines.append(f"  SLA Compliance:        {overall['compliance_rate_pct']}% ({status}, target: {threshold}%)")
    lines.append(f"  Total Tickets:         {overall['total_tickets']}")
    lines.append(f"  Resolved:              {overall['resolved']}")
    lines.append(f"  Open:                  {overall['open']}")
    lines.append(f"  Met SLA:               {overall['met_sla']}")
    lines.append(f"  Breached SLA:          {overall['breached_sla']}")
    lines.append(f"  Avg Resolution:        {overall['avg_resolution_hrs']} hrs")
    lines.append(f"  Avg Breach Overshoot:  {overall['avg_breach_hrs']} hrs")

    # Priority breakdown
    lines.append("")
    lines.append("-" * 70)
    lines.append("BY PRIORITY")
    lines.append("-" * 70)
    lines.append(f"  {'Priority':<18} {'Total':>6} {'Met':>6} {'Breach':>7} {'Compl%':>7} {'Avg Hrs':>8}")
    lines.append(f"  {'-'*18} {'-'*6} {'-'*6} {'-'*7} {'-'*7} {'-'*8}")
    for p in priority:
        flag = " <<<" if p["compliance_pct"] < threshold else ""
        lines.append(
            f"  {p['priority']:<18} {p['total']:>6} {p['met']:>6} {p['breached']:>7} "
            f"{p['compliance_pct']:>6.1f}% {p['avg_resolution_hrs']:>7.1f}h{flag}"
        )

    # Team breakdown
    lines.append("")
    lines.append("-" * 70)
    lines.append("BY TEAM")
    lines.append("-" * 70)
    lines.append(f"  {'Team':<22} {'Total':>6} {'Met':>6} {'Breach':>7} {'Compl%':>7} {'Avg Hrs':>8}")
    lines.append(f"  {'-'*22} {'-'*6} {'-'*6} {'-'*7} {'-'*7} {'-'*8}")
    for t in teams:
        flag = " <<<" if t["compliance_pct"] < threshold else ""
        lines.append(
            f"  {t['team']:<22} {t['total']:>6} {t['met']:>6} {t['breached']:>7} "
            f"{t['compliance_pct']:>6.1f}% {t['avg_resolution_hrs']:>7.1f}h{flag}"
        )

    # Trend
    if trend:
        lines.append("")
        lines.append("-" * 70)
        lines.append("TREND")
        lines.append("-" * 70)
        for t in trend:
            bar_len = int(t["compliance_pct"] / 5)
            bar = "#" * bar_len + "." * (20 - bar_len)
            lines.append(f"  {t['period']:<12} {t['compliance_pct']:>6.1f}% [{bar}] ({t['met']}/{t['total']})")

    # Worst breaches
    if worst:
        lines.append("")
        lines.append("-" * 70)
        lines.append("WORST BREACHES")
        lines.append("-" * 70)
        for w in worst:
            lines.append(
                f"  {w['ticket_id']} | {w['priority']} | {w['team']} | "
                f"Target: {w['sla_target_hrs']}h | Actual: {w['actual_hrs']}h | "
                f"Breach: +{w['breach_hours']}h ({w['breach_pct']:+.1f}%)"
            )

    # Recommendations
    lines.append("")
    lines.append("-" * 70)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 70)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Track and analyze SLA compliance across service tickets."
    )
    parser.add_argument("--file", required=True, help="Path to tickets CSV")
    parser.add_argument("--threshold", type=float, default=95, help="SLA compliance target percentage (default: 95)")
    parser.add_argument("--period", default="month", choices=["week", "month", "quarter"], help="Trend period grouping (default: month)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    tickets = analyze_tickets(rows, args.period)
    overall = compute_overall_metrics(tickets)
    priority = compute_priority_breakdown(tickets)
    teams = compute_team_breakdown(tickets)
    trend = compute_trend(tickets)
    worst = find_worst_breaches(tickets)
    recommendations = build_recommendations(overall, priority, teams, trend, args.threshold)

    if args.json:
        output = {
            "overall": overall,
            "by_priority": priority,
            "by_team": teams,
            "trend": trend,
            "worst_breaches": worst,
            "recommendations": recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(overall, priority, teams, trend, worst, recommendations, args.threshold))


if __name__ == "__main__":
    main()
