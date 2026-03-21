#!/usr/bin/env python3
"""
Attrition Predictor - Score employees for attrition risk using rule-based heuristics.

Reads employee data CSV and computes a flight risk score (0-100) for each employee
based on weighted factors: tenure, compensation ratio, engagement, promotion recency,
manager tenure, and performance rating. No ML libraries required.

Usage:
    python attrition_predictor.py --file employees.csv
    python attrition_predictor.py --file employees.csv --threshold 70 --json
    python attrition_predictor.py --file employees.csv --top 20

Input CSV columns:
    employee_id             - Unique employee identifier
    department              - Department name
    tenure_months           - Months of employment
    salary_ratio_to_market  - Ratio of salary to market median (e.g., 0.92 = 8% below)
    performance_rating      - Last performance rating (1-5 scale)
    months_since_promotion  - Months since last promotion
    engagement_score        - Last engagement survey score (1-5)
    manager_tenure_months   - Months the current manager has been in role
    training_hours_ytd      - Training hours year-to-date
    level                   - Job level (optional)
    location                - Location (optional)

Output: Per-employee risk scores with risk factors and organizational summary.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict


# --- Risk factor weights and thresholds ---

WEIGHTS = {
    "compensation": 25,
    "promotion_stagnation": 20,
    "engagement": 20,
    "tenure_risk": 15,
    "manager_instability": 10,
    "development_gap": 10,
}

TENURE_RISK_BANDS = [
    # (min_months, max_months, risk_score, label)
    (0, 6, 30, "New hire - settling in"),
    (6, 18, 60, "High-risk window - 6-18 months"),
    (18, 36, 40, "Moderate - building career capital"),
    (36, 60, 50, "Moderate - may seek growth externally"),
    (60, 120, 35, "Established - lower base risk"),
    (120, 999, 25, "Long-tenure - low mobility risk"),
]


def read_csv(path: str) -> list:
    """Read CSV file and return list of dicts."""
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"employee_id", "tenure_months", "salary_ratio_to_market", "engagement_score"}
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


def score_compensation(ratio: float) -> tuple:
    """Score compensation risk (0-100). Lower ratio = higher risk."""
    if ratio >= 1.05:
        return 10, "Above market"
    elif ratio >= 0.95:
        return 25, "At market"
    elif ratio >= 0.90:
        return 55, "Slightly below market"
    elif ratio >= 0.85:
        return 75, "Below market"
    else:
        return 95, "Significantly below market"


def score_promotion(months_since: float) -> tuple:
    """Score promotion stagnation risk (0-100)."""
    if months_since <= 12:
        return 10, "Recently promoted"
    elif months_since <= 24:
        return 30, "Within normal cycle"
    elif months_since <= 36:
        return 55, "Approaching stagnation"
    elif months_since <= 48:
        return 75, "Promotion overdue"
    else:
        return 90, "Significant stagnation"


def score_engagement(score: float) -> tuple:
    """Score engagement risk (0-100). Lower engagement = higher risk."""
    if score >= 4.5:
        return 10, "Highly engaged"
    elif score >= 4.0:
        return 25, "Engaged"
    elif score >= 3.5:
        return 45, "Neutral"
    elif score >= 3.0:
        return 70, "Disengaged"
    else:
        return 90, "Highly disengaged"


def score_tenure(months: float) -> tuple:
    """Score tenure-based risk (0-100)."""
    for min_m, max_m, risk, label in TENURE_RISK_BANDS:
        if min_m <= months < max_m:
            return risk, label
    return 30, "Unknown tenure band"


def score_manager_instability(months: float) -> tuple:
    """Score manager instability risk (0-100). New managers = higher risk."""
    if months >= 24:
        return 15, "Stable manager relationship"
    elif months >= 12:
        return 30, "Moderate manager tenure"
    elif months >= 6:
        return 55, "Recent manager change"
    else:
        return 80, "Very new manager"


def score_development(training_hours: float) -> tuple:
    """Score development investment risk (0-100). Low training = higher risk."""
    if training_hours >= 40:
        return 10, "Strong development investment"
    elif training_hours >= 20:
        return 30, "Adequate development"
    elif training_hours >= 10:
        return 55, "Below average development"
    else:
        return 80, "Minimal development investment"


def compute_risk_score(row: dict) -> dict:
    """Compute overall risk score for an employee."""
    tenure = safe_float(row.get("tenure_months", 0))
    comp_ratio = safe_float(row.get("salary_ratio_to_market", 1.0))
    engagement = safe_float(row.get("engagement_score", 3.5))
    months_promo = safe_float(row.get("months_since_promotion", 24))
    mgr_tenure = safe_float(row.get("manager_tenure_months", 12))
    training = safe_float(row.get("training_hours_ytd", 20))
    perf = safe_float(row.get("performance_rating", 3.0))

    comp_score, comp_label = score_compensation(comp_ratio)
    promo_score, promo_label = score_promotion(months_promo)
    eng_score, eng_label = score_engagement(engagement)
    tenure_score, tenure_label = score_tenure(tenure)
    mgr_score, mgr_label = score_manager_instability(mgr_tenure)
    dev_score, dev_label = score_development(training)

    # Weighted overall score
    overall = (
        comp_score * WEIGHTS["compensation"]
        + promo_score * WEIGHTS["promotion_stagnation"]
        + eng_score * WEIGHTS["engagement"]
        + tenure_score * WEIGHTS["tenure_risk"]
        + mgr_score * WEIGHTS["manager_instability"]
        + dev_score * WEIGHTS["development_gap"]
    ) / 100

    # Adjust for high performers (higher risk when other factors are negative)
    if perf >= 4.0 and overall > 50:
        overall = min(100, overall * 1.1)  # High performers at risk are extra costly

    overall = round(min(100, max(0, overall)), 1)

    # Risk level
    if overall >= 75:
        risk_level = "CRITICAL"
    elif overall >= 50:
        risk_level = "HIGH"
    elif overall >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Top risk factors (sorted by contribution)
    factors = [
        {"factor": "Compensation", "score": comp_score, "weight": WEIGHTS["compensation"], "detail": f"{comp_label} (ratio: {comp_ratio:.2f})"},
        {"factor": "Promotion", "score": promo_score, "weight": WEIGHTS["promotion_stagnation"], "detail": f"{promo_label} ({months_promo:.0f} months)"},
        {"factor": "Engagement", "score": eng_score, "weight": WEIGHTS["engagement"], "detail": f"{eng_label} (score: {engagement:.1f})"},
        {"factor": "Tenure", "score": tenure_score, "weight": WEIGHTS["tenure_risk"], "detail": f"{tenure_label} ({tenure:.0f} months)"},
        {"factor": "Manager", "score": mgr_score, "weight": WEIGHTS["manager_instability"], "detail": f"{mgr_label} ({mgr_tenure:.0f} months)"},
        {"factor": "Development", "score": dev_score, "weight": WEIGHTS["development_gap"], "detail": f"{dev_label} ({training:.0f} hrs YTD)"},
    ]
    factors.sort(key=lambda x: x["score"] * x["weight"], reverse=True)

    return {
        "employee_id": row["employee_id"],
        "department": row.get("department", ""),
        "level": row.get("level", ""),
        "risk_score": overall,
        "risk_level": risk_level,
        "performance_rating": perf,
        "top_risk_factors": factors[:3],
        "all_factors": factors,
    }


def compute_summary(results: list) -> dict:
    """Compute organizational summary statistics."""
    total = len(results)
    if total == 0:
        return {}

    critical = sum(1 for r in results if r["risk_level"] == "CRITICAL")
    high = sum(1 for r in results if r["risk_level"] == "HIGH")
    medium = sum(1 for r in results if r["risk_level"] == "MEDIUM")
    low = sum(1 for r in results if r["risk_level"] == "LOW")

    scores = [r["risk_score"] for r in results]
    avg_score = sum(scores) / len(scores)

    # High performers at risk
    high_perf_at_risk = [r for r in results if r["performance_rating"] >= 4.0 and r["risk_level"] in ("CRITICAL", "HIGH")]

    # Department breakdown
    dept_risk = defaultdict(list)
    for r in results:
        dept = r.get("department", "Unknown") or "Unknown"
        dept_risk[dept].append(r["risk_score"])

    dept_summary = []
    for dept, scores_list in sorted(dept_risk.items()):
        dept_avg = sum(scores_list) / len(scores_list)
        dept_critical = sum(1 for s in scores_list if s >= 75)
        dept_summary.append({
            "department": dept,
            "employee_count": len(scores_list),
            "avg_risk_score": round(dept_avg, 1),
            "critical_count": dept_critical,
        })
    dept_summary.sort(key=lambda x: x["avg_risk_score"], reverse=True)

    return {
        "total_employees": total,
        "risk_distribution": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
        "avg_risk_score": round(avg_score, 1),
        "high_performers_at_risk": len(high_perf_at_risk),
        "department_summary": dept_summary,
    }


def format_human(results: list, summary: dict, threshold: float) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("ATTRITION RISK ASSESSMENT REPORT")
    lines.append("=" * 70)
    lines.append("")

    dist = summary["risk_distribution"]
    lines.append(f"  Total Employees Scored:    {summary['total_employees']}")
    lines.append(f"  Average Risk Score:        {summary['avg_risk_score']}/100")
    lines.append(f"  High Performers at Risk:   {summary['high_performers_at_risk']}")
    lines.append("")
    lines.append(f"  Risk Distribution:")
    lines.append(f"    CRITICAL (75+): {dist['critical']:>4} ({dist['critical']/summary['total_employees']*100:.1f}%)")
    lines.append(f"    HIGH (50-74):   {dist['high']:>4} ({dist['high']/summary['total_employees']*100:.1f}%)")
    lines.append(f"    MEDIUM (30-49): {dist['medium']:>4} ({dist['medium']/summary['total_employees']*100:.1f}%)")
    lines.append(f"    LOW (0-29):     {dist['low']:>4} ({dist['low']/summary['total_employees']*100:.1f}%)")

    # Department summary
    if summary["department_summary"]:
        lines.append("")
        lines.append("-" * 70)
        lines.append("DEPARTMENT RISK SUMMARY")
        lines.append("-" * 70)
        lines.append(f"  {'Department':<25} {'Employees':>10} {'Avg Risk':>10} {'Critical':>10}")
        lines.append(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*10}")
        for dept in summary["department_summary"]:
            lines.append(f"  {dept['department']:<25} {dept['employee_count']:>10} {dept['avg_risk_score']:>10.1f} {dept['critical_count']:>10}")

    # Individual results above threshold
    flagged = [r for r in results if r["risk_score"] >= threshold]
    flagged.sort(key=lambda x: x["risk_score"], reverse=True)

    if flagged:
        lines.append("")
        lines.append("-" * 70)
        lines.append(f"EMPLOYEES ABOVE RISK THRESHOLD ({threshold})")
        lines.append("-" * 70)
        for r in flagged[:30]:
            perf_tag = " [HIGH PERFORMER]" if r["performance_rating"] >= 4.0 else ""
            lines.append(f"\n  {r['employee_id']} | {r['department']} | Risk: {r['risk_score']}/100 ({r['risk_level']}){perf_tag}")
            for f in r["top_risk_factors"]:
                lines.append(f"    - {f['factor']}: {f['detail']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score employees for attrition risk using rule-based heuristics."
    )
    parser.add_argument("--file", required=True, help="Path to employee data CSV")
    parser.add_argument("--threshold", type=float, default=50, help="Risk score threshold for flagging (default: 50)")
    parser.add_argument("--top", type=int, default=None, help="Show only top N highest-risk employees")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    results = [compute_risk_score(row) for row in rows]
    results.sort(key=lambda x: x["risk_score"], reverse=True)

    if args.top:
        results = results[:args.top]

    summary = compute_summary(results)

    if args.json:
        output = {
            "summary": summary,
            "employees": results,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(results, summary, args.threshold))


if __name__ == "__main__":
    main()
