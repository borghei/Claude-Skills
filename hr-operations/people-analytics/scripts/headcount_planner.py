#!/usr/bin/env python3
"""
Headcount Planner - Workforce planning calculations and scenario modeling.

Reads current workforce data and computes future headcount needs based on
growth targets, attrition assumptions, and hiring capacity. Supports
multi-quarter forecasting and department-level breakdowns.

Usage:
    python headcount_planner.py --file workforce.csv --growth 0.15 --attrition 0.12
    python headcount_planner.py --file workforce.csv --growth 0.15 --attrition 0.12 --quarters 4 --json
    python headcount_planner.py --file workforce.csv --growth 0.20 --attrition 0.10 --hiring-capacity 15

Input CSV columns:
    department          - Department name
    current_headcount   - Current headcount in department
    open_roles          - Number of open/approved roles
    attrition_rate      - Department-specific attrition rate (optional, overrides --attrition)
    avg_cost_per_hire   - Average cost per hire for department (optional)
    avg_salary          - Average salary for department (optional)
    growth_rate         - Department-specific growth rate (optional, overrides --growth)

Output: Quarter-by-quarter headcount plan with hiring needs, costs, and gap analysis.
"""

import argparse
import csv
import json
import math
import os
import sys


def read_csv(path: str) -> list:
    """Read CSV file and return list of dicts."""
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"department", "current_headcount"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            print(f"Error: Missing required columns: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    return rows


def safe_float(val: str, default: float = 0.0) -> float:
    """Safely parse float."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val: str, default: int = 0) -> int:
    """Safely parse int."""
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def forecast_department(dept: dict, growth_rate: float, attrition_rate: float,
                        quarters: int, hiring_capacity: int = None) -> dict:
    """Forecast headcount for a single department over N quarters."""
    name = dept["department"]
    current_hc = safe_int(dept.get("current_headcount", 0))
    open_roles = safe_int(dept.get("open_roles", 0))
    dept_attrition = safe_float(dept.get("attrition_rate"), attrition_rate)
    dept_growth = safe_float(dept.get("growth_rate"), growth_rate)
    avg_cost = safe_float(dept.get("avg_cost_per_hire", 4500))
    avg_salary = safe_float(dept.get("avg_salary", 100000))

    # Quarterly rates
    quarterly_attrition = dept_attrition / 4
    quarterly_growth = dept_growth / 4

    # Target headcount at end of planning horizon
    target_hc = math.ceil(current_hc * (1 + dept_growth))

    quarterly_plan = []
    running_hc = current_hc
    total_hires_needed = 0
    total_cost = 0
    total_salary_cost = 0

    for q in range(1, quarters + 1):
        # Expected attrition this quarter
        expected_attrition = math.ceil(running_hc * quarterly_attrition)

        # Growth hires this quarter
        growth_target = math.ceil(current_hc * quarterly_growth)

        # Total hires needed = backfill + growth + remaining open roles
        backfill = expected_attrition
        growth_hires = growth_target
        open_fill = open_roles if q == 1 else 0  # Fill open roles in Q1

        total_q_hires = backfill + growth_hires + open_fill

        # Apply hiring capacity constraint
        if hiring_capacity is not None:
            total_q_hires = min(total_q_hires, hiring_capacity)

        # Net change
        net_change = total_q_hires - expected_attrition

        # End of quarter headcount
        end_hc = running_hc + net_change

        # Costs
        hiring_cost = total_q_hires * avg_cost
        incremental_salary = total_q_hires * avg_salary * 0.25  # Partial quarter

        quarterly_plan.append({
            "quarter": f"Q{q}",
            "start_headcount": running_hc,
            "expected_attrition": expected_attrition,
            "backfill_hires": backfill,
            "growth_hires": growth_hires,
            "open_role_fills": open_fill,
            "total_hires": total_q_hires,
            "net_change": net_change,
            "end_headcount": end_hc,
            "hiring_cost": round(hiring_cost),
            "incremental_salary_cost": round(incremental_salary),
        })

        total_hires_needed += total_q_hires
        total_cost += hiring_cost
        total_salary_cost += incremental_salary
        running_hc = end_hc

    gap = target_hc - running_hc

    return {
        "department": name,
        "current_headcount": current_hc,
        "open_roles": open_roles,
        "target_headcount": target_hc,
        "final_headcount": running_hc,
        "gap_to_target": gap,
        "growth_rate": dept_growth,
        "attrition_rate": dept_attrition,
        "total_hires_needed": total_hires_needed,
        "total_hiring_cost": round(total_cost),
        "total_incremental_salary": round(total_salary_cost),
        "quarterly_plan": quarterly_plan,
    }


def compute_org_summary(forecasts: list) -> dict:
    """Compute organization-level summary."""
    total_current = sum(f["current_headcount"] for f in forecasts)
    total_target = sum(f["target_headcount"] for f in forecasts)
    total_final = sum(f["final_headcount"] for f in forecasts)
    total_hires = sum(f["total_hires_needed"] for f in forecasts)
    total_hiring_cost = sum(f["total_hiring_cost"] for f in forecasts)
    total_salary_cost = sum(f["total_incremental_salary"] for f in forecasts)
    total_open = sum(f["open_roles"] for f in forecasts)

    # Aggregate quarterly
    quarters_count = len(forecasts[0]["quarterly_plan"]) if forecasts else 0
    quarterly_totals = []
    for q in range(quarters_count):
        q_data = {
            "quarter": f"Q{q+1}",
            "total_hires": sum(f["quarterly_plan"][q]["total_hires"] for f in forecasts),
            "total_attrition": sum(f["quarterly_plan"][q]["expected_attrition"] for f in forecasts),
            "net_change": sum(f["quarterly_plan"][q]["net_change"] for f in forecasts),
            "hiring_cost": sum(f["quarterly_plan"][q]["hiring_cost"] for f in forecasts),
        }
        quarterly_totals.append(q_data)

    return {
        "current_total_headcount": total_current,
        "target_total_headcount": total_target,
        "projected_final_headcount": total_final,
        "total_open_roles": total_open,
        "total_hires_needed": total_hires,
        "total_hiring_cost": total_hiring_cost,
        "total_incremental_salary_cost": total_salary_cost,
        "total_investment": total_hiring_cost + total_salary_cost,
        "net_growth": total_final - total_current,
        "net_growth_pct": round((total_final - total_current) / total_current * 100, 1) if total_current > 0 else 0,
        "quarterly_totals": quarterly_totals,
    }


def format_human(forecasts: list, summary: dict, quarters: int) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 75)
    lines.append("WORKFORCE HEADCOUNT PLAN")
    lines.append("=" * 75)
    lines.append("")
    lines.append(f"  Planning Horizon:          {quarters} quarters")
    lines.append(f"  Current Headcount:         {summary['current_total_headcount']}")
    lines.append(f"  Target Headcount:          {summary['target_total_headcount']}")
    lines.append(f"  Projected Final:           {summary['projected_final_headcount']}")
    lines.append(f"  Net Growth:                {summary['net_growth']} ({summary['net_growth_pct']}%)")
    lines.append(f"  Open Roles to Fill:        {summary['total_open_roles']}")
    lines.append(f"  Total Hires Needed:        {summary['total_hires_needed']}")
    lines.append(f"  Total Hiring Cost:         ${summary['total_hiring_cost']:,.0f}")
    lines.append(f"  Incremental Salary Cost:   ${summary['total_incremental_salary_cost']:,.0f}")
    lines.append(f"  Total Investment:          ${summary['total_investment']:,.0f}")

    # Quarterly overview
    lines.append("")
    lines.append("-" * 75)
    lines.append("QUARTERLY OVERVIEW (ALL DEPARTMENTS)")
    lines.append("-" * 75)
    lines.append(f"  {'Quarter':<10} {'Hires':>8} {'Attrition':>10} {'Net':>8} {'Hiring Cost':>14}")
    lines.append(f"  {'-'*10} {'-'*8} {'-'*10} {'-'*8} {'-'*14}")
    for qt in summary["quarterly_totals"]:
        lines.append(f"  {qt['quarter']:<10} {qt['total_hires']:>8} {qt['total_attrition']:>10} {qt['net_change']:>+8} ${qt['hiring_cost']:>12,.0f}")

    # Department detail
    lines.append("")
    lines.append("-" * 75)
    lines.append("DEPARTMENT BREAKDOWN")
    lines.append("-" * 75)
    lines.append(f"  {'Department':<20} {'Current':>8} {'Target':>8} {'Final':>8} {'Hires':>8} {'Gap':>6} {'Cost':>12}")
    lines.append(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*6} {'-'*12}")
    for f in forecasts:
        lines.append(
            f"  {f['department']:<20} {f['current_headcount']:>8} {f['target_headcount']:>8} "
            f"{f['final_headcount']:>8} {f['total_hires_needed']:>8} {f['gap_to_target']:>+6} "
            f"${f['total_hiring_cost']:>10,.0f}"
        )

    # Detailed quarterly plans per department
    for f in forecasts:
        lines.append("")
        lines.append(f"  --- {f['department']} (Attrition: {f['attrition_rate']*100:.0f}%, Growth: {f['growth_rate']*100:.0f}%) ---")
        lines.append(f"  {'Qtr':<6} {'Start':>7} {'Attrit':>7} {'Back':>6} {'Grow':>6} {'Open':>6} {'Total':>6} {'End':>7}")
        for qp in f["quarterly_plan"]:
            lines.append(
                f"  {qp['quarter']:<6} {qp['start_headcount']:>7} {qp['expected_attrition']:>7} "
                f"{qp['backfill_hires']:>6} {qp['growth_hires']:>6} {qp['open_role_fills']:>6} "
                f"{qp['total_hires']:>6} {qp['end_headcount']:>7}"
            )

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Workforce headcount planning and scenario modeling."
    )
    parser.add_argument("--file", required=True, help="Path to workforce data CSV")
    parser.add_argument("--growth", type=float, required=True, help="Annual growth rate (e.g., 0.15 for 15%)")
    parser.add_argument("--attrition", type=float, required=True, help="Annual attrition rate (e.g., 0.12 for 12%)")
    parser.add_argument("--quarters", type=int, default=4, help="Number of quarters to forecast (default: 4)")
    parser.add_argument("--hiring-capacity", type=int, default=None, help="Max hires per quarter per department")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    forecasts = []
    for row in rows:
        forecast = forecast_department(row, args.growth, args.attrition, args.quarters, args.hiring_capacity)
        forecasts.append(forecast)

    summary = compute_org_summary(forecasts)

    if args.json:
        output = {
            "summary": summary,
            "departments": forecasts,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(forecasts, summary, args.quarters))


if __name__ == "__main__":
    main()
