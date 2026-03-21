#!/usr/bin/env python3
"""
Capacity Planner - Resource capacity planning and demand-supply analysis.

Reads resource data and demand forecast CSVs to compute capacity utilization,
identify shortfalls, and model staffing scenarios across planning horizons.

Usage:
    python capacity_planner.py --file resources.csv --forecast demand.csv
    python capacity_planner.py --file resources.csv --forecast demand.csv --json
    python capacity_planner.py --file resources.csv --forecast demand.csv --productivity 0.85

Input - resources.csv columns:
    team            - Team or department name
    role            - Role type
    headcount       - Number of FTEs
    hours_per_day   - Available hours per person per day
    days_per_week   - Working days per week
    productivity    - Productivity factor 0-1 (optional, default from --productivity flag)

Input - demand.csv columns:
    period          - Time period (e.g., Week 1, Jan, Q1)
    team            - Team or department name
    demand_hours    - Required hours for the period
    priority        - Priority level: critical, high, medium, low (optional)
    project         - Project or workstream name (optional)

Output: Capacity analysis with utilization, gaps, and staffing recommendations.
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict


def read_csv(path: str) -> list:
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val: str, default: int = 0) -> int:
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def compute_capacity(resources: list, default_productivity: float) -> dict:
    """Compute available capacity by team."""
    team_capacity = defaultdict(lambda: {
        "headcount": 0,
        "weekly_hours": 0,
        "roles": defaultdict(int),
    })

    for r in resources:
        team = r.get("team", "Unknown").strip()
        role = r.get("role", "General").strip()
        hc = safe_int(r.get("headcount", 1))
        hours_day = safe_float(r.get("hours_per_day", 8))
        days_week = safe_float(r.get("days_per_week", 5))
        productivity = safe_float(r.get("productivity")) or default_productivity

        weekly_hours = hc * hours_day * days_week * productivity

        team_capacity[team]["headcount"] += hc
        team_capacity[team]["weekly_hours"] += weekly_hours
        team_capacity[team]["roles"][role] += hc

    return dict(team_capacity)


def compute_demand(forecast: list) -> dict:
    """Compute demand by team and period."""
    team_demand = defaultdict(lambda: defaultdict(lambda: {
        "demand_hours": 0,
        "projects": [],
        "critical_hours": 0,
    }))

    periods = []
    for f in forecast:
        period = f.get("period", "Unknown").strip()
        team = f.get("team", "Unknown").strip()
        demand = safe_float(f.get("demand_hours", 0))
        priority = f.get("priority", "medium").strip().lower()
        project = f.get("project", "").strip()

        if period not in periods:
            periods.append(period)

        team_demand[team][period]["demand_hours"] += demand
        if project and project not in team_demand[team][period]["projects"]:
            team_demand[team][period]["projects"].append(project)
        if priority == "critical":
            team_demand[team][period]["critical_hours"] += demand

    return dict(team_demand), periods


def analyze_capacity(capacity: dict, demand: dict, periods: list) -> dict:
    """Analyze capacity vs demand."""
    all_teams = sorted(set(list(capacity.keys()) + list(demand.keys())))

    team_analysis = []
    for team in all_teams:
        cap = capacity.get(team, {"headcount": 0, "weekly_hours": 0, "roles": {}})
        weekly_capacity = cap["weekly_hours"]

        period_details = []
        total_demand = 0
        total_surplus = 0
        total_deficit = 0
        max_utilization = 0

        for period in periods:
            period_demand = demand.get(team, {}).get(period, {"demand_hours": 0, "critical_hours": 0, "projects": []})
            demand_hrs = period_demand["demand_hours"]
            total_demand += demand_hrs

            gap = weekly_capacity - demand_hrs
            utilization = round(demand_hrs / max(1, weekly_capacity) * 100, 1)
            max_utilization = max(max_utilization, utilization)

            if gap >= 0:
                total_surplus += gap
            else:
                total_deficit += abs(gap)

            # Status
            if utilization > 100:
                status = "OVER_CAPACITY"
            elif utilization > 90:
                status = "NEAR_CAPACITY"
            elif utilization > 70:
                status = "OPTIMAL"
            elif utilization > 50:
                status = "UNDER_UTILIZED"
            else:
                status = "SIGNIFICANTLY_UNDER"

            period_details.append({
                "period": period,
                "capacity_hours": round(weekly_capacity, 1),
                "demand_hours": round(demand_hrs, 1),
                "gap_hours": round(gap, 1),
                "utilization_pct": utilization,
                "status": status,
                "critical_hours": period_demand["critical_hours"],
                "projects": period_demand["projects"],
            })

        avg_utilization = round(total_demand / max(1, weekly_capacity * len(periods)) * 100, 1)

        # FTE gap calculation
        fte_surplus_deficit = 0
        if weekly_capacity > 0 and len(periods) > 0:
            avg_demand = total_demand / len(periods)
            fte_surplus_deficit = round((avg_demand - weekly_capacity) / (weekly_capacity / max(1, cap["headcount"])), 1)

        team_analysis.append({
            "team": team,
            "headcount": cap["headcount"],
            "weekly_capacity_hours": round(weekly_capacity, 1),
            "avg_utilization_pct": avg_utilization,
            "peak_utilization_pct": max_utilization,
            "total_demand_hours": round(total_demand, 1),
            "total_surplus_hours": round(total_surplus, 1),
            "total_deficit_hours": round(total_deficit, 1),
            "fte_adjustment_needed": fte_surplus_deficit,
            "roles": dict(cap.get("roles", {})),
            "periods": period_details,
        })

    return team_analysis


def compute_org_summary(analysis: list, periods: list) -> dict:
    """Compute organization-level summary."""
    total_hc = sum(a["headcount"] for a in analysis)
    total_capacity = sum(a["weekly_capacity_hours"] for a in analysis)
    total_demand = sum(a["total_demand_hours"] for a in analysis)
    total_deficit = sum(a["total_deficit_hours"] for a in analysis)
    total_surplus = sum(a["total_surplus_hours"] for a in analysis)

    over_capacity = [a for a in analysis if a["peak_utilization_pct"] > 100]
    under_utilized = [a for a in analysis if a["avg_utilization_pct"] < 60]

    avg_util = round(total_demand / max(1, total_capacity * len(periods)) * 100, 1)

    # Additional FTEs needed
    total_fte_adj = sum(max(0, a["fte_adjustment_needed"]) for a in analysis)

    return {
        "total_headcount": total_hc,
        "total_weekly_capacity_hours": round(total_capacity, 1),
        "planning_periods": len(periods),
        "avg_utilization_pct": avg_util,
        "total_deficit_hours": round(total_deficit, 1),
        "total_surplus_hours": round(total_surplus, 1),
        "teams_over_capacity": len(over_capacity),
        "teams_under_utilized": len(under_utilized),
        "additional_ftes_needed": round(total_fte_adj, 1),
    }


def build_recommendations(analysis: list, summary: dict) -> list:
    """Generate staffing recommendations."""
    recs = []

    # Over-capacity teams
    over = [a for a in analysis if a["peak_utilization_pct"] > 100]
    for team in over:
        recs.append(
            f"{team['team']}: Peak utilization {team['peak_utilization_pct']:.0f}% exceeds capacity. "
            f"Need {max(0, team['fte_adjustment_needed']):.1f} additional FTEs or redistribute "
            f"{team['total_deficit_hours']:.0f} hours of demand to other teams."
        )

    # Near-capacity teams at risk
    near = [a for a in analysis if 90 <= a["peak_utilization_pct"] <= 100 and a["avg_utilization_pct"] > 85]
    for team in near:
        recs.append(
            f"{team['team']}: Running near capacity (avg {team['avg_utilization_pct']:.0f}%, "
            f"peak {team['peak_utilization_pct']:.0f}%). Any demand increase or attrition will cause overload. "
            "Consider cross-training or contingent staffing."
        )

    # Under-utilized teams
    under = [a for a in analysis if a["avg_utilization_pct"] < 50]
    for team in under:
        recs.append(
            f"{team['team']}: Utilization at {team['avg_utilization_pct']:.0f}%. "
            f"Surplus of {team['total_surplus_hours']:.0f} hours available for redeployment."
        )

    # Cross-team rebalancing opportunity
    if over and under:
        recs.append(
            "Cross-team rebalancing opportunity: redistribute work from over-capacity teams "
            f"({', '.join(a['team'] for a in over)}) to under-utilized teams "
            f"({', '.join(a['team'] for a in under)}) where skill overlap permits."
        )

    if not recs:
        recs.append("Capacity is well-balanced across all teams. Continue monitoring for demand changes.")

    return recs


def format_human(analysis: list, summary: dict, periods: list, recommendations: list) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 75)
    lines.append("CAPACITY PLANNING REPORT")
    lines.append("=" * 75)
    lines.append("")
    lines.append(f"  Total Headcount:           {summary['total_headcount']}")
    lines.append(f"  Weekly Capacity:           {summary['total_weekly_capacity_hours']:.0f} hours")
    lines.append(f"  Planning Periods:          {summary['planning_periods']}")
    lines.append(f"  Avg Utilization:           {summary['avg_utilization_pct']:.1f}%")
    lines.append(f"  Teams Over Capacity:       {summary['teams_over_capacity']}")
    lines.append(f"  Teams Under-Utilized:      {summary['teams_under_utilized']}")
    lines.append(f"  Additional FTEs Needed:    {summary['additional_ftes_needed']:.1f}")
    lines.append(f"  Total Deficit Hours:       {summary['total_deficit_hours']:.0f}")
    lines.append(f"  Total Surplus Hours:       {summary['total_surplus_hours']:.0f}")

    # Team summary
    lines.append("")
    lines.append("-" * 75)
    lines.append("TEAM CAPACITY SUMMARY")
    lines.append("-" * 75)
    lines.append(f"  {'Team':<20} {'HC':>4} {'Cap/wk':>8} {'Avg Util':>9} {'Peak':>6} {'FTE +/-':>8} {'Status':>15}")
    lines.append(f"  {'-'*20} {'-'*4} {'-'*8} {'-'*9} {'-'*6} {'-'*8} {'-'*15}")

    for a in sorted(analysis, key=lambda x: -x["peak_utilization_pct"]):
        if a["peak_utilization_pct"] > 100:
            status = "OVER_CAPACITY"
        elif a["peak_utilization_pct"] > 90:
            status = "NEAR_CAPACITY"
        elif a["avg_utilization_pct"] > 70:
            status = "OPTIMAL"
        elif a["avg_utilization_pct"] > 50:
            status = "UNDER_USED"
        else:
            status = "LOW_USAGE"

        lines.append(
            f"  {a['team']:<20} {a['headcount']:>4} {a['weekly_capacity_hours']:>7.0f}h "
            f"{a['avg_utilization_pct']:>8.1f}% {a['peak_utilization_pct']:>5.0f}% "
            f"{a['fte_adjustment_needed']:>+7.1f} {status:>15}"
        )

    # Period-by-period for flagged teams
    flagged = [a for a in analysis if a["peak_utilization_pct"] > 90 or a["avg_utilization_pct"] < 50]
    if flagged:
        lines.append("")
        lines.append("-" * 75)
        lines.append("PERIOD DETAIL (Flagged Teams)")
        lines.append("-" * 75)
        for a in flagged:
            lines.append(f"\n  {a['team']} (HC: {a['headcount']}, Cap: {a['weekly_capacity_hours']:.0f}h/wk)")
            lines.append(f"  {'Period':<12} {'Demand':>8} {'Gap':>8} {'Util':>7} {'Status':>18}")
            lines.append(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*7} {'-'*18}")
            for p in a["periods"]:
                lines.append(
                    f"  {p['period']:<12} {p['demand_hours']:>7.0f}h {p['gap_hours']:>+7.0f}h "
                    f"{p['utilization_pct']:>6.1f}% {p['status']:>18}"
                )

    # Recommendations
    lines.append("")
    lines.append("-" * 75)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 75)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Resource capacity planning and demand-supply analysis."
    )
    parser.add_argument("--file", required=True, help="Path to resources CSV")
    parser.add_argument("--forecast", required=True, help="Path to demand forecast CSV")
    parser.add_argument("--productivity", type=float, default=0.80, help="Default productivity factor 0-1 (default: 0.80)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    resources = read_csv(args.file)
    forecast = read_csv(args.forecast)

    if not resources:
        print("Error: No data in resources file.", file=sys.stderr)
        sys.exit(1)
    if not forecast:
        print("Error: No data in forecast file.", file=sys.stderr)
        sys.exit(1)

    capacity = compute_capacity(resources, args.productivity)
    demand, periods = compute_demand(forecast)
    analysis = analyze_capacity(capacity, demand, periods)
    summary = compute_org_summary(analysis, periods)
    recommendations = build_recommendations(analysis, summary)

    if args.json:
        output = {
            "summary": summary,
            "teams": analysis,
            "recommendations": recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(analysis, summary, periods, recommendations))


if __name__ == "__main__":
    main()
