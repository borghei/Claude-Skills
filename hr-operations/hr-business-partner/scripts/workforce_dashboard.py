#!/usr/bin/env python3
"""
Workforce Dashboard - Generate HR metrics dashboard from workforce data.

Reads a workforce CSV and produces a comprehensive dashboard covering
headcount, attrition, tenure distribution, performance distribution,
diversity metrics, and department-level breakdowns.

Usage:
    python workforce_dashboard.py --file workforce.csv
    python workforce_dashboard.py --file workforce.csv --json
    python workforce_dashboard.py --file workforce.csv --period Q1-2026

Input CSV columns:
    employee_id     - Unique employee identifier
    department      - Department name
    level           - Job level
    status          - Employment status (Active, Terminated, Resigned, etc.)
    hire_date       - Date of hire (YYYY-MM-DD)
    term_date       - Termination date if applicable (YYYY-MM-DD)
    term_type       - Termination type (Voluntary, Involuntary, blank if active)
    salary          - Current annual salary
    performance     - Last performance rating (1-5)
    gender          - Gender (optional)
    ethnicity       - Ethnicity (optional)
    location        - Office location (optional)
    manager_id      - Manager's employee ID (optional)

Output: Workforce dashboard with headcount, attrition, tenure, performance, diversity metrics.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, date


def read_csv(path: str) -> list:
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"employee_id", "department", "status"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            print(f"Error: Missing required columns: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    return rows


def parse_date(val: str) -> date:
    if not val or not val.strip():
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(val.strip(), fmt).date()
        except ValueError:
            continue
    return None


def safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def compute_headcount(rows: list) -> dict:
    """Compute headcount metrics."""
    active = [r for r in rows if r.get("status", "").strip().lower() == "active"]
    terminated = [r for r in rows if r.get("status", "").strip().lower() in ("terminated", "resigned")]

    dept_counts = defaultdict(int)
    level_counts = defaultdict(int)
    location_counts = defaultdict(int)

    for r in active:
        dept_counts[r.get("department", "Unknown")] += 1
        level_counts[r.get("level", "Unknown")] += 1
        loc = r.get("location", "Unknown") or "Unknown"
        location_counts[loc] += 1

    return {
        "total_active": len(active),
        "total_terminated": len(terminated),
        "total_records": len(rows),
        "by_department": dict(sorted(dept_counts.items(), key=lambda x: -x[1])),
        "by_level": dict(sorted(level_counts.items())),
        "by_location": dict(sorted(location_counts.items(), key=lambda x: -x[1])),
    }


def compute_attrition(rows: list) -> dict:
    """Compute attrition metrics."""
    today = date.today()
    active = [r for r in rows if r.get("status", "").strip().lower() == "active"]
    terminated = [r for r in rows if r.get("status", "").strip().lower() in ("terminated", "resigned")]

    voluntary = [r for r in terminated if r.get("term_type", "").strip().lower() == "voluntary"]
    involuntary = [r for r in terminated if r.get("term_type", "").strip().lower() == "involuntary"]

    avg_hc = (len(active) + len(active) + len(terminated)) / 2  # Approximation

    total_rate = round(len(terminated) / max(1, avg_hc) * 100, 1)
    voluntary_rate = round(len(voluntary) / max(1, avg_hc) * 100, 1)
    involuntary_rate = round(len(involuntary) / max(1, avg_hc) * 100, 1)

    # Attrition by department
    dept_attrition = defaultdict(lambda: {"active": 0, "terminated": 0})
    for r in active:
        dept_attrition[r.get("department", "Unknown")]["active"] += 1
    for r in terminated:
        dept_attrition[r.get("department", "Unknown")]["terminated"] += 1

    dept_rates = {}
    for dept, counts in dept_attrition.items():
        total = counts["active"] + counts["terminated"]
        dept_rates[dept] = round(counts["terminated"] / max(1, total) * 100, 1)

    return {
        "total_exits": len(terminated),
        "voluntary_exits": len(voluntary),
        "involuntary_exits": len(involuntary),
        "total_attrition_rate": total_rate,
        "voluntary_attrition_rate": voluntary_rate,
        "involuntary_attrition_rate": involuntary_rate,
        "by_department": dict(sorted(dept_rates.items(), key=lambda x: -x[1])),
    }


def compute_tenure(rows: list) -> dict:
    """Compute tenure distribution."""
    today = date.today()
    active = [r for r in rows if r.get("status", "").strip().lower() == "active"]

    tenures = []
    for r in active:
        hire = parse_date(r.get("hire_date", ""))
        if hire:
            months = (today.year - hire.year) * 12 + (today.month - hire.month)
            tenures.append(months)

    if not tenures:
        return {"avg_tenure_months": 0, "distribution": {}}

    bands = {
        "< 6 months": 0,
        "6-12 months": 0,
        "1-2 years": 0,
        "2-5 years": 0,
        "5-10 years": 0,
        "10+ years": 0,
    }

    for t in tenures:
        if t < 6:
            bands["< 6 months"] += 1
        elif t < 12:
            bands["6-12 months"] += 1
        elif t < 24:
            bands["1-2 years"] += 1
        elif t < 60:
            bands["2-5 years"] += 1
        elif t < 120:
            bands["5-10 years"] += 1
        else:
            bands["10+ years"] += 1

    avg_tenure = sum(tenures) / len(tenures)
    sorted_t = sorted(tenures)
    median_tenure = sorted_t[len(sorted_t) // 2]

    return {
        "avg_tenure_months": round(avg_tenure, 1),
        "median_tenure_months": median_tenure,
        "distribution": bands,
    }


def compute_performance(rows: list) -> dict:
    """Compute performance distribution."""
    active = [r for r in rows if r.get("status", "").strip().lower() == "active"]

    ratings = []
    for r in active:
        perf = safe_float(r.get("performance"))
        if 1 <= perf <= 5:
            ratings.append(perf)

    if not ratings:
        return {"avg_rating": 0, "distribution": {}}

    dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in ratings:
        dist[int(round(r))] += 1

    total = len(ratings)
    dist_pct = {k: round(v / total * 100, 1) for k, v in dist.items()}

    high_performers = sum(1 for r in ratings if r >= 4) / total * 100
    low_performers = sum(1 for r in ratings if r <= 2) / total * 100

    return {
        "avg_rating": round(sum(ratings) / total, 2),
        "rated_count": total,
        "distribution": dist,
        "distribution_pct": dist_pct,
        "high_performer_pct": round(high_performers, 1),
        "low_performer_pct": round(low_performers, 1),
    }


def compute_diversity(rows: list) -> dict:
    """Compute diversity metrics."""
    active = [r for r in rows if r.get("status", "").strip().lower() == "active"]

    gender_counts = defaultdict(int)
    ethnicity_counts = defaultdict(int)
    gender_by_level = defaultdict(lambda: defaultdict(int))

    for r in active:
        gender = r.get("gender", "").strip()
        ethnicity = r.get("ethnicity", "").strip()
        level = r.get("level", "Unknown")

        if gender:
            gender_counts[gender] += 1
            gender_by_level[level][gender] += 1
        if ethnicity:
            ethnicity_counts[ethnicity] += 1

    total = len(active)

    def to_pct(counts):
        return {k: round(v / max(1, total) * 100, 1) for k, v in sorted(counts.items(), key=lambda x: -x[1])}

    return {
        "gender_distribution": to_pct(gender_counts),
        "ethnicity_distribution": to_pct(ethnicity_counts),
        "gender_by_level": {level: dict(genders) for level, genders in sorted(gender_by_level.items())},
    }


def compute_compensation_summary(rows: list) -> dict:
    """Compute basic compensation summary."""
    active = [r for r in rows if r.get("status", "").strip().lower() == "active"]
    salaries = [safe_float(r.get("salary")) for r in active if safe_float(r.get("salary")) > 0]

    if not salaries:
        return {"avg_salary": 0, "total_payroll": 0}

    s = sorted(salaries)
    n = len(s)

    return {
        "avg_salary": round(sum(s) / n),
        "median_salary": round(s[n // 2]),
        "min_salary": round(s[0]),
        "max_salary": round(s[-1]),
        "total_payroll": round(sum(s)),
        "employee_count": n,
    }


def compute_manager_spans(rows: list) -> dict:
    """Compute span of control metrics."""
    active = [r for r in rows if r.get("status", "").strip().lower() == "active"]

    manager_counts = defaultdict(int)
    for r in active:
        mgr = r.get("manager_id", "").strip()
        if mgr:
            manager_counts[mgr] += 1

    if not manager_counts:
        return {"avg_span": 0, "managers": 0}

    spans = list(manager_counts.values())
    avg_span = sum(spans) / len(spans)

    span_dist = {"1-3": 0, "4-6": 0, "7-9": 0, "10-12": 0, "13+": 0}
    for s in spans:
        if s <= 3:
            span_dist["1-3"] += 1
        elif s <= 6:
            span_dist["4-6"] += 1
        elif s <= 9:
            span_dist["7-9"] += 1
        elif s <= 12:
            span_dist["10-12"] += 1
        else:
            span_dist["13+"] += 1

    return {
        "total_managers": len(manager_counts),
        "avg_span_of_control": round(avg_span, 1),
        "max_span": max(spans),
        "min_span": min(spans),
        "span_distribution": span_dist,
    }


def format_human(headcount: dict, attrition: dict, tenure: dict, performance: dict,
                 diversity: dict, comp: dict, spans: dict, period: str) -> str:
    """Format dashboard for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"WORKFORCE DASHBOARD{' - ' + period if period else ''}")
    lines.append("=" * 70)

    # Headcount
    lines.append("")
    lines.append("-" * 70)
    lines.append("HEADCOUNT")
    lines.append("-" * 70)
    lines.append(f"  Active Employees:  {headcount['total_active']}")
    lines.append(f"  Total Records:     {headcount['total_records']}")
    lines.append("")
    lines.append("  By Department:")
    for dept, count in headcount["by_department"].items():
        pct = round(count / max(1, headcount["total_active"]) * 100, 1)
        bar = "#" * int(pct / 2)
        lines.append(f"    {dept:<25} {count:>5} ({pct:>5.1f}%)  {bar}")

    lines.append("")
    lines.append("  By Level:")
    for level, count in headcount["by_level"].items():
        lines.append(f"    {level:<15} {count:>5}")

    # Attrition
    lines.append("")
    lines.append("-" * 70)
    lines.append("ATTRITION")
    lines.append("-" * 70)
    lines.append(f"  Total Exits:       {attrition['total_exits']}")
    lines.append(f"  Voluntary:         {attrition['voluntary_exits']} ({attrition['voluntary_attrition_rate']}%)")
    lines.append(f"  Involuntary:       {attrition['involuntary_exits']} ({attrition['involuntary_attrition_rate']}%)")
    lines.append(f"  Total Rate:        {attrition['total_attrition_rate']}%")
    if attrition["by_department"]:
        lines.append("")
        lines.append("  By Department:")
        for dept, rate in attrition["by_department"].items():
            flag = " <<<" if rate > 15 else ""
            lines.append(f"    {dept:<25} {rate:>5.1f}%{flag}")

    # Tenure
    lines.append("")
    lines.append("-" * 70)
    lines.append("TENURE DISTRIBUTION")
    lines.append("-" * 70)
    lines.append(f"  Average Tenure:    {tenure['avg_tenure_months']:.1f} months ({tenure['avg_tenure_months']/12:.1f} years)")
    lines.append(f"  Median Tenure:     {tenure.get('median_tenure_months', 0)} months")
    if tenure.get("distribution"):
        for band, count in tenure["distribution"].items():
            lines.append(f"    {band:<20} {count:>5}")

    # Performance
    lines.append("")
    lines.append("-" * 70)
    lines.append("PERFORMANCE DISTRIBUTION")
    lines.append("-" * 70)
    lines.append(f"  Average Rating:    {performance.get('avg_rating', 0):.2f}/5.0")
    lines.append(f"  High Performers:   {performance.get('high_performer_pct', 0):.1f}%")
    lines.append(f"  Low Performers:    {performance.get('low_performer_pct', 0):.1f}%")
    if performance.get("distribution_pct"):
        for rating, pct in performance["distribution_pct"].items():
            bar = "#" * int(pct / 2)
            lines.append(f"    Rating {rating}: {pct:>5.1f}%  {bar}")

    # Compensation
    if comp.get("avg_salary"):
        lines.append("")
        lines.append("-" * 70)
        lines.append("COMPENSATION SUMMARY")
        lines.append("-" * 70)
        lines.append(f"  Average Salary:    ${comp['avg_salary']:,}")
        lines.append(f"  Median Salary:     ${comp['median_salary']:,}")
        lines.append(f"  Salary Range:      ${comp['min_salary']:,} - ${comp['max_salary']:,}")
        lines.append(f"  Total Payroll:     ${comp['total_payroll']:,}")

    # Diversity
    if diversity.get("gender_distribution"):
        lines.append("")
        lines.append("-" * 70)
        lines.append("DIVERSITY METRICS")
        lines.append("-" * 70)
        lines.append("  Gender:")
        for gender, pct in diversity["gender_distribution"].items():
            lines.append(f"    {gender:<20} {pct:>5.1f}%")
        if diversity.get("ethnicity_distribution"):
            lines.append("  Ethnicity:")
            for eth, pct in diversity["ethnicity_distribution"].items():
                lines.append(f"    {eth:<20} {pct:>5.1f}%")

    # Span of control
    if spans.get("total_managers"):
        lines.append("")
        lines.append("-" * 70)
        lines.append("SPAN OF CONTROL")
        lines.append("-" * 70)
        lines.append(f"  Total Managers:    {spans['total_managers']}")
        lines.append(f"  Avg Span:          {spans['avg_span_of_control']:.1f}")
        lines.append(f"  Range:             {spans['min_span']} - {spans['max_span']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate workforce metrics dashboard from HR data."
    )
    parser.add_argument("--file", required=True, help="Path to workforce data CSV")
    parser.add_argument("--period", default=None, help="Reporting period label (e.g., Q1-2026)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    headcount = compute_headcount(rows)
    attrition = compute_attrition(rows)
    tenure = compute_tenure(rows)
    performance = compute_performance(rows)
    diversity = compute_diversity(rows)
    comp = compute_compensation_summary(rows)
    spans = compute_manager_spans(rows)

    if args.json:
        output = {
            "period": args.period,
            "headcount": headcount,
            "attrition": attrition,
            "tenure": tenure,
            "performance": performance,
            "diversity": diversity,
            "compensation": comp,
            "span_of_control": spans,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(headcount, attrition, tenure, performance, diversity, comp, spans, args.period))


if __name__ == "__main__":
    main()
