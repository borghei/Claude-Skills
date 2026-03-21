#!/usr/bin/env python3
"""
Compensation Analyzer - Analyze compensation data for pay equity and band alignment.

Reads employee compensation data and performs compa-ratio analysis, pay gap
calculations by demographic group, band positioning analysis, and outlier detection.
Uses standard library only -- no statsmodels or scipy required.

Usage:
    python compensation_analyzer.py --file comp_data.csv
    python compensation_analyzer.py --file comp_data.csv --json
    python compensation_analyzer.py --file comp_data.csv --group gender

Input CSV columns:
    employee_id     - Unique employee identifier
    department      - Department name
    level           - Job level (e.g., IC1, IC2, IC3, M1)
    salary          - Current annual base salary
    band_min        - Compensation band minimum for role/level
    band_max        - Compensation band maximum for role/level
    band_midpoint   - Compensation band midpoint (optional, calculated if absent)
    gender          - Gender (optional, for equity analysis)
    ethnicity       - Ethnicity (optional, for equity analysis)
    tenure_years    - Years of tenure (optional, for controlled analysis)
    performance     - Last performance rating 1-5 (optional, for controlled analysis)
    location        - Location (optional, for segmentation)

Output: Compa-ratio analysis, pay equity gaps, band positioning, outliers, and recommendations.
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict


MIN_GROUP_SIZE = 5  # Minimum group size for equity analysis


def read_csv(path: str) -> list:
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"employee_id", "salary", "level"}
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


def compute_compa_ratios(rows: list) -> list:
    """Compute compa-ratio for each employee."""
    results = []
    for row in rows:
        salary = safe_float(row.get("salary"))
        band_min = safe_float(row.get("band_min"))
        band_max = safe_float(row.get("band_max"))
        midpoint = safe_float(row.get("band_midpoint"))

        if not midpoint and band_min and band_max:
            midpoint = (band_min + band_max) / 2

        compa_ratio = salary / midpoint if midpoint > 0 else 0
        # Band position: 0% = at min, 100% = at max
        band_range = band_max - band_min if band_max > band_min else 1
        band_position = (salary - band_min) / band_range * 100 if band_range > 0 else 50

        # Outlier flags
        below_band = salary < band_min if band_min > 0 else False
        above_band = salary > band_max if band_max > 0 else False

        results.append({
            "employee_id": row["employee_id"],
            "department": row.get("department", ""),
            "level": row.get("level", ""),
            "salary": salary,
            "band_min": band_min,
            "band_midpoint": round(midpoint, 2),
            "band_max": band_max,
            "compa_ratio": round(compa_ratio, 3),
            "band_position_pct": round(band_position, 1),
            "below_band": below_band,
            "above_band": above_band,
            "gender": row.get("gender", ""),
            "ethnicity": row.get("ethnicity", ""),
            "tenure_years": safe_float(row.get("tenure_years")),
            "performance": safe_float(row.get("performance")),
            "location": row.get("location", ""),
        })

    return results


def compute_summary_stats(employees: list) -> dict:
    """Compute overall summary statistics."""
    salaries = [e["salary"] for e in employees if e["salary"] > 0]
    compa_ratios = [e["compa_ratio"] for e in employees if e["compa_ratio"] > 0]

    def percentile(values, pct):
        if not values:
            return 0
        s = sorted(values)
        k = (len(s) - 1) * pct / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return s[int(k)]
        return s[f] * (c - k) + s[c] * (k - f)

    below = sum(1 for e in employees if e["below_band"])
    above = sum(1 for e in employees if e["above_band"])

    return {
        "total_employees": len(employees),
        "avg_salary": round(sum(salaries) / max(1, len(salaries)), 2),
        "median_salary": round(percentile(salaries, 50), 2),
        "avg_compa_ratio": round(sum(compa_ratios) / max(1, len(compa_ratios)), 3),
        "median_compa_ratio": round(percentile(compa_ratios, 50), 3),
        "p25_compa_ratio": round(percentile(compa_ratios, 25), 3),
        "p75_compa_ratio": round(percentile(compa_ratios, 75), 3),
        "below_band_count": below,
        "above_band_count": above,
        "within_band_count": len(employees) - below - above,
        "below_band_pct": round(below / max(1, len(employees)) * 100, 1),
        "above_band_pct": round(above / max(1, len(employees)) * 100, 1),
    }


def compute_level_analysis(employees: list) -> list:
    """Analyze compensation by level."""
    level_data = defaultdict(list)
    for e in employees:
        if e["level"]:
            level_data[e["level"]].append(e)

    results = []
    for level, emps in sorted(level_data.items()):
        salaries = [e["salary"] for e in emps]
        compa_ratios = [e["compa_ratio"] for e in emps if e["compa_ratio"] > 0]
        below = sum(1 for e in emps if e["below_band"])
        above = sum(1 for e in emps if e["above_band"])

        results.append({
            "level": level,
            "count": len(emps),
            "avg_salary": round(sum(salaries) / max(1, len(salaries))),
            "avg_compa_ratio": round(sum(compa_ratios) / max(1, len(compa_ratios)), 3),
            "below_band": below,
            "above_band": above,
        })

    return results


def compute_equity_analysis(employees: list, group_field: str) -> dict:
    """Compute pay equity analysis by demographic group."""
    groups = defaultdict(list)
    for e in employees:
        group_val = e.get(group_field, "").strip()
        if group_val:
            groups[group_val].append(e)

    # Filter groups below minimum size
    valid_groups = {k: v for k, v in groups.items() if len(v) >= MIN_GROUP_SIZE}
    suppressed = {k: len(v) for k, v in groups.items() if len(v) < MIN_GROUP_SIZE}

    if len(valid_groups) < 2:
        return {
            "field": group_field,
            "sufficient_data": False,
            "reason": f"Need at least 2 groups with {MIN_GROUP_SIZE}+ members for equity analysis",
            "suppressed_groups": suppressed,
        }

    # Raw gap analysis
    group_stats = {}
    for group, emps in valid_groups.items():
        salaries = [e["salary"] for e in emps]
        compa_ratios = [e["compa_ratio"] for e in emps if e["compa_ratio"] > 0]
        group_stats[group] = {
            "group": group,
            "count": len(emps),
            "avg_salary": round(sum(salaries) / len(salaries)),
            "avg_compa_ratio": round(sum(compa_ratios) / max(1, len(compa_ratios)), 3),
        }

    # Calculate gaps relative to highest-paid group
    max_salary_group = max(group_stats.values(), key=lambda x: x["avg_salary"])
    ref_salary = max_salary_group["avg_salary"]

    gaps = []
    for group, stats in group_stats.items():
        gap_pct = round((stats["avg_salary"] - ref_salary) / ref_salary * 100, 1) if ref_salary > 0 else 0
        gaps.append({
            **stats,
            "raw_gap_pct": gap_pct,
            "is_reference": group == max_salary_group["group"],
        })

    gaps.sort(key=lambda x: x["raw_gap_pct"])

    # Controlled gap: group by level, then compute within-level gaps
    level_gaps = []
    level_groups = defaultdict(lambda: defaultdict(list))
    for e in employees:
        group_val = e.get(group_field, "").strip()
        if group_val and group_val in valid_groups:
            level_groups[e["level"]][group_val].append(e["salary"])

    for level, grps in level_groups.items():
        if len(grps) >= 2:
            grp_avgs = {}
            for g, sals in grps.items():
                if len(sals) >= MIN_GROUP_SIZE:
                    grp_avgs[g] = sum(sals) / len(sals)
            if len(grp_avgs) >= 2:
                max_avg = max(grp_avgs.values())
                for g, avg in grp_avgs.items():
                    gap = round((avg - max_avg) / max_avg * 100, 1) if max_avg > 0 else 0
                    if gap != 0:
                        level_gaps.append({
                            "level": level,
                            "group": g,
                            "avg_salary": round(avg),
                            "controlled_gap_pct": gap,
                        })

    return {
        "field": group_field,
        "sufficient_data": True,
        "reference_group": max_salary_group["group"],
        "group_comparison": gaps,
        "controlled_gaps_by_level": level_gaps,
        "suppressed_groups": suppressed,
    }


def find_outliers(employees: list) -> list:
    """Find compensation outliers."""
    outliers = []
    for e in employees:
        reasons = []
        if e["below_band"]:
            reasons.append(f"Below band minimum (salary ${e['salary']:,.0f} vs min ${e['band_min']:,.0f})")
        if e["above_band"]:
            reasons.append(f"Above band maximum (salary ${e['salary']:,.0f} vs max ${e['band_max']:,.0f})")
        if e["compa_ratio"] > 0 and (e["compa_ratio"] < 0.85 or e["compa_ratio"] > 1.15):
            reasons.append(f"Compa-ratio {e['compa_ratio']:.3f} outside 0.85-1.15 range")

        if reasons:
            outliers.append({
                "employee_id": e["employee_id"],
                "department": e["department"],
                "level": e["level"],
                "salary": e["salary"],
                "compa_ratio": e["compa_ratio"],
                "reasons": reasons,
            })

    outliers.sort(key=lambda x: abs(x["compa_ratio"] - 1.0), reverse=True)
    return outliers


def build_recommendations(summary: dict, equity: dict, outliers: list) -> list:
    """Generate recommendations."""
    recs = []

    if summary["below_band_pct"] > 5:
        recs.append(
            f"{summary['below_band_count']} employees ({summary['below_band_pct']}%) are below band minimum. "
            "Prioritize market adjustments to bring these employees to at least band minimum within the next review cycle."
        )

    if summary["avg_compa_ratio"] < 0.93:
        recs.append(
            f"Average compa-ratio is {summary['avg_compa_ratio']:.3f}, indicating the organization is paying "
            "below band midpoints. Review market data currency and consider whether bands need updating or salaries need adjusting."
        )

    if equity.get("sufficient_data") and equity.get("controlled_gaps_by_level"):
        significant_gaps = [g for g in equity["controlled_gaps_by_level"] if abs(g["controlled_gap_pct"]) > 5]
        if significant_gaps:
            recs.append(
                f"Found {len(significant_gaps)} level-controlled pay gaps exceeding 5%. "
                "Conduct a detailed pay equity review with Legal and Total Rewards to determine root causes and remediation."
            )

    if len(outliers) > 0:
        recs.append(
            f"{len(outliers)} employees flagged as compensation outliers. "
            "Review each case with the relevant HRBP and manager to determine if adjustments are needed."
        )

    if not recs:
        recs.append("Compensation is well-aligned across the organization. Continue monitoring quarterly.")

    return recs


def format_human(summary: dict, levels: list, equity: dict, outliers: list, recommendations: list) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("COMPENSATION ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  Total Employees:       {summary['total_employees']}")
    lines.append(f"  Average Salary:        ${summary['avg_salary']:,.0f}")
    lines.append(f"  Median Salary:         ${summary['median_salary']:,.0f}")
    lines.append(f"  Average Compa-Ratio:   {summary['avg_compa_ratio']:.3f}")
    lines.append(f"  Median Compa-Ratio:    {summary['median_compa_ratio']:.3f}")
    lines.append(f"  Below Band:            {summary['below_band_count']} ({summary['below_band_pct']}%)")
    lines.append(f"  Above Band:            {summary['above_band_count']} ({summary['above_band_pct']}%)")
    lines.append(f"  Within Band:           {summary['within_band_count']}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("BY LEVEL")
    lines.append("-" * 70)
    lines.append(f"  {'Level':<10} {'Count':>6} {'Avg Salary':>12} {'Avg CR':>8} {'Below':>6} {'Above':>6}")
    lines.append(f"  {'-'*10} {'-'*6} {'-'*12} {'-'*8} {'-'*6} {'-'*6}")
    for lv in levels:
        lines.append(
            f"  {lv['level']:<10} {lv['count']:>6} ${lv['avg_salary']:>10,} {lv['avg_compa_ratio']:>8.3f} "
            f"{lv['below_band']:>6} {lv['above_band']:>6}"
        )

    if equity.get("sufficient_data"):
        lines.append("")
        lines.append("-" * 70)
        lines.append(f"PAY EQUITY ANALYSIS (by {equity['field']})")
        lines.append("-" * 70)
        lines.append(f"  Reference group: {equity['reference_group']}")
        lines.append(f"  {'Group':<20} {'Count':>6} {'Avg Salary':>12} {'Avg CR':>8} {'Raw Gap':>8}")
        lines.append(f"  {'-'*20} {'-'*6} {'-'*12} {'-'*8} {'-'*8}")
        for g in equity["group_comparison"]:
            ref = " (ref)" if g["is_reference"] else ""
            lines.append(
                f"  {g['group']:<20} {g['count']:>6} ${g['avg_salary']:>10,} {g['avg_compa_ratio']:>8.3f} "
                f"{g['raw_gap_pct']:>+7.1f}%{ref}"
            )

        if equity.get("controlled_gaps_by_level"):
            lines.append("\n  Controlled gaps (within-level):")
            for g in equity["controlled_gaps_by_level"]:
                lines.append(f"    {g['level']}: {g['group']} gap = {g['controlled_gap_pct']:+.1f}% (avg ${g['avg_salary']:,})")

    if outliers:
        lines.append("")
        lines.append("-" * 70)
        lines.append(f"OUTLIERS ({len(outliers)} flagged)")
        lines.append("-" * 70)
        for o in outliers[:15]:
            lines.append(f"  {o['employee_id']} | {o['department']} | {o['level']} | ${o['salary']:,.0f} | CR: {o['compa_ratio']:.3f}")
            for r in o["reasons"]:
                lines.append(f"    - {r}")

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
        description="Analyze compensation data for pay equity and band alignment."
    )
    parser.add_argument("--file", required=True, help="Path to compensation data CSV")
    parser.add_argument("--group", default="gender", help="Demographic field for equity analysis (default: gender)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    employees = compute_compa_ratios(rows)
    summary = compute_summary_stats(employees)
    levels = compute_level_analysis(employees)
    equity = compute_equity_analysis(employees, args.group)
    outliers = find_outliers(employees)
    recommendations = build_recommendations(summary, equity, outliers)

    if args.json:
        output = {
            "summary": summary,
            "level_analysis": levels,
            "equity_analysis": equity,
            "outliers": outliers,
            "recommendations": recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(summary, levels, equity, outliers, recommendations))


if __name__ == "__main__":
    main()
