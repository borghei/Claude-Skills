#!/usr/bin/env python3
"""
Org Health Scorer - Score organizational health from workforce metrics.

Reads a CSV of organizational metrics per department/team and computes a
composite health score across six dimensions: retention, engagement,
performance, development, compensation, and diversity.

Usage:
    python org_health_scorer.py --file org_metrics.csv
    python org_health_scorer.py --file org_metrics.csv --json
    python org_health_scorer.py --file org_metrics.csv --threshold 60

Input CSV columns:
    department              - Department or team name
    headcount               - Total headcount
    voluntary_turnover_pct  - Voluntary turnover rate (e.g., 12 for 12%)
    regrettable_turnover_pct - Regrettable turnover as % of total exits
    engagement_score        - Engagement survey score (1-100 scale)
    enps                    - Employee Net Promoter Score (-100 to 100)
    high_performer_pct      - Percentage rated as high performers
    low_performer_pct       - Percentage rated as low performers
    promotion_rate_pct      - Annual promotion rate
    training_hours_avg      - Average training hours per employee
    compa_ratio_avg         - Average compa-ratio (actual/midpoint)
    open_role_pct           - Open roles as % of headcount
    diversity_pct           - Underrepresented group representation %
    manager_score           - Manager effectiveness score (1-5)
    span_of_control         - Average direct reports per manager

Output: Per-department health scores with dimension breakdowns and recommendations.
"""

import argparse
import csv
import json
import os
import sys


# --- Scoring functions for each dimension (0-100) ---

def score_retention(turnover_pct: float, regrettable_pct: float) -> tuple:
    """Score retention health."""
    # Voluntary turnover: <10% excellent, 10-15% good, 15-20% concerning, >20% critical
    if turnover_pct <= 8:
        turn_score = 100
    elif turnover_pct <= 12:
        turn_score = 85
    elif turnover_pct <= 15:
        turn_score = 70
    elif turnover_pct <= 20:
        turn_score = 50
    elif turnover_pct <= 25:
        turn_score = 30
    else:
        turn_score = 15

    # Regrettable: <20% excellent, 20-30% good, >30% concerning
    if regrettable_pct <= 15:
        reg_score = 100
    elif regrettable_pct <= 25:
        reg_score = 80
    elif regrettable_pct <= 35:
        reg_score = 60
    else:
        reg_score = 35

    score = round(turn_score * 0.6 + reg_score * 0.4)
    issues = []
    if turnover_pct > 15:
        issues.append(f"Voluntary turnover at {turnover_pct:.1f}% exceeds 15% threshold")
    if regrettable_pct > 30:
        issues.append(f"Regrettable turnover at {regrettable_pct:.1f}% exceeds 30% threshold")
    return score, issues


def score_engagement(engagement: float, enps: float) -> tuple:
    """Score engagement health."""
    # Engagement: 80+ excellent, 70-80 good, 60-70 fair, <60 poor
    if engagement >= 80:
        eng_score = 100
    elif engagement >= 70:
        eng_score = 80
    elif engagement >= 60:
        eng_score = 60
    elif engagement >= 50:
        eng_score = 40
    else:
        eng_score = 20

    # eNPS: 40+ excellent, 20-40 good, 0-20 fair, <0 poor
    if enps >= 40:
        enps_score = 100
    elif enps >= 20:
        enps_score = 80
    elif enps >= 0:
        enps_score = 55
    elif enps >= -20:
        enps_score = 30
    else:
        enps_score = 15

    score = round(eng_score * 0.6 + enps_score * 0.4)
    issues = []
    if engagement < 65:
        issues.append(f"Engagement score {engagement:.0f} below 65 threshold")
    if enps < 10:
        issues.append(f"eNPS at {enps:.0f} below minimum of 10")
    return score, issues


def score_performance(high_perf_pct: float, low_perf_pct: float) -> tuple:
    """Score performance distribution health."""
    # High performers: 15-25% is healthy
    if 15 <= high_perf_pct <= 25:
        hp_score = 100
    elif 10 <= high_perf_pct < 15 or 25 < high_perf_pct <= 35:
        hp_score = 75
    elif high_perf_pct > 35:
        hp_score = 50  # Rating inflation
    else:
        hp_score = 50

    # Low performers: 5-10% is healthy (shows differentiation)
    if 5 <= low_perf_pct <= 10:
        lp_score = 100
    elif 3 <= low_perf_pct < 5:
        lp_score = 80
    elif low_perf_pct < 3:
        lp_score = 60  # Possible lack of differentiation
    elif low_perf_pct <= 20:
        lp_score = 50
    else:
        lp_score = 30

    score = round(hp_score * 0.6 + lp_score * 0.4)
    issues = []
    if high_perf_pct > 35:
        issues.append(f"High performer rate {high_perf_pct:.1f}% suggests rating inflation")
    if low_perf_pct < 3:
        issues.append(f"Low performer rate {low_perf_pct:.1f}% suggests lack of differentiation")
    if low_perf_pct > 15:
        issues.append(f"Low performer rate {low_perf_pct:.1f}% is elevated")
    return score, issues


def score_development(promotion_rate: float, training_hours: float) -> tuple:
    """Score development investment health."""
    # Promotion rate: 8-12% is healthy
    if 8 <= promotion_rate <= 15:
        promo_score = 100
    elif 5 <= promotion_rate < 8:
        promo_score = 70
    elif promotion_rate > 15:
        promo_score = 70  # Possible title inflation
    else:
        promo_score = 40

    # Training hours: 40+ excellent, 20-40 good, <20 concerning
    if training_hours >= 40:
        train_score = 100
    elif training_hours >= 25:
        train_score = 80
    elif training_hours >= 15:
        train_score = 60
    else:
        train_score = 35

    score = round(promo_score * 0.5 + train_score * 0.5)
    issues = []
    if promotion_rate < 5:
        issues.append(f"Promotion rate {promotion_rate:.1f}% below 5% may indicate career stagnation")
    if training_hours < 15:
        issues.append(f"Average training {training_hours:.0f} hrs below 15 hr minimum")
    return score, issues


def score_compensation(compa_ratio: float) -> tuple:
    """Score compensation health."""
    # Target: 0.95-1.05
    if 0.95 <= compa_ratio <= 1.05:
        score = 100
    elif 0.90 <= compa_ratio < 0.95 or 1.05 < compa_ratio <= 1.10:
        score = 80
    elif 0.85 <= compa_ratio < 0.90 or 1.10 < compa_ratio <= 1.15:
        score = 60
    elif 0.80 <= compa_ratio < 0.85:
        score = 40
    else:
        score = 25

    issues = []
    if compa_ratio < 0.90:
        issues.append(f"Compa-ratio {compa_ratio:.2f} significantly below midpoint")
    if compa_ratio > 1.10:
        issues.append(f"Compa-ratio {compa_ratio:.2f} significantly above midpoint")
    return score, issues


def score_structure(open_role_pct: float, span: float, manager_score: float) -> tuple:
    """Score organizational structure health."""
    # Open roles: <5% healthy, 5-10% manageable, >10% strained
    if open_role_pct <= 5:
        open_score = 100
    elif open_role_pct <= 10:
        open_score = 75
    elif open_role_pct <= 15:
        open_score = 50
    else:
        open_score = 25

    # Span of control: 5-8 is optimal
    if 5 <= span <= 8:
        span_score = 100
    elif 4 <= span < 5 or 8 < span <= 10:
        span_score = 75
    elif 3 <= span < 4 or 10 < span <= 12:
        span_score = 50
    else:
        span_score = 30

    # Manager score: 4.0+ excellent
    if manager_score >= 4.0:
        mgr_score = 100
    elif manager_score >= 3.5:
        mgr_score = 75
    elif manager_score >= 3.0:
        mgr_score = 50
    else:
        mgr_score = 30

    score = round(open_score * 0.3 + span_score * 0.3 + mgr_score * 0.4)
    issues = []
    if open_role_pct > 10:
        issues.append(f"Open role rate {open_role_pct:.1f}% indicates capacity strain")
    if span < 4 or span > 10:
        issues.append(f"Span of control {span:.1f} outside 5-8 optimal range")
    if manager_score < 3.5:
        issues.append(f"Manager effectiveness {manager_score:.1f} below 3.5 threshold")
    return score, issues


DIMENSION_WEIGHTS = {
    "retention": 25,
    "engagement": 25,
    "performance": 15,
    "development": 15,
    "compensation": 10,
    "structure": 10,
}


def safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def read_csv_file(path: str) -> list:
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"department", "headcount"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            print(f"Error: Missing required columns: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    return rows


def score_department(row: dict) -> dict:
    """Score a single department."""
    dept = row["department"]
    hc = safe_float(row.get("headcount", 0))

    retention_score, retention_issues = score_retention(
        safe_float(row.get("voluntary_turnover_pct", 12)),
        safe_float(row.get("regrettable_turnover_pct", 25)),
    )
    engagement_s, engagement_issues = score_engagement(
        safe_float(row.get("engagement_score", 70)),
        safe_float(row.get("enps", 20)),
    )
    performance_s, performance_issues = score_performance(
        safe_float(row.get("high_performer_pct", 18)),
        safe_float(row.get("low_performer_pct", 7)),
    )
    development_s, development_issues = score_development(
        safe_float(row.get("promotion_rate_pct", 10)),
        safe_float(row.get("training_hours_avg", 25)),
    )
    compensation_s, compensation_issues = score_compensation(
        safe_float(row.get("compa_ratio_avg", 1.0)),
    )
    structure_s, structure_issues = score_structure(
        safe_float(row.get("open_role_pct", 5)),
        safe_float(row.get("span_of_control", 6)),
        safe_float(row.get("manager_score", 3.8)),
    )

    # Weighted overall
    overall = round(
        retention_score * DIMENSION_WEIGHTS["retention"] / 100
        + engagement_s * DIMENSION_WEIGHTS["engagement"] / 100
        + performance_s * DIMENSION_WEIGHTS["performance"] / 100
        + development_s * DIMENSION_WEIGHTS["development"] / 100
        + compensation_s * DIMENSION_WEIGHTS["compensation"] / 100
        + structure_s * DIMENSION_WEIGHTS["structure"] / 100
    )

    # Health level
    if overall >= 80:
        health = "HEALTHY"
    elif overall >= 65:
        health = "WATCH"
    elif overall >= 50:
        health = "AT_RISK"
    else:
        health = "CRITICAL"

    all_issues = retention_issues + engagement_issues + performance_issues + development_issues + compensation_issues + structure_issues

    return {
        "department": dept,
        "headcount": int(hc),
        "overall_score": overall,
        "health_level": health,
        "dimensions": {
            "retention": {"score": retention_score, "weight": DIMENSION_WEIGHTS["retention"], "issues": retention_issues},
            "engagement": {"score": engagement_s, "weight": DIMENSION_WEIGHTS["engagement"], "issues": engagement_issues},
            "performance": {"score": performance_s, "weight": DIMENSION_WEIGHTS["performance"], "issues": performance_issues},
            "development": {"score": development_s, "weight": DIMENSION_WEIGHTS["development"], "issues": development_issues},
            "compensation": {"score": compensation_s, "weight": DIMENSION_WEIGHTS["compensation"], "issues": compensation_issues},
            "structure": {"score": structure_s, "weight": DIMENSION_WEIGHTS["structure"], "issues": structure_issues},
        },
        "all_issues": all_issues,
    }


def compute_org_summary(results: list) -> dict:
    """Compute org-level summary."""
    total_hc = sum(r["headcount"] for r in results)
    # Weighted average by headcount
    if total_hc > 0:
        weighted_score = sum(r["overall_score"] * r["headcount"] for r in results) / total_hc
    else:
        weighted_score = sum(r["overall_score"] for r in results) / max(1, len(results))

    health_dist = {"HEALTHY": 0, "WATCH": 0, "AT_RISK": 0, "CRITICAL": 0}
    for r in results:
        health_dist[r["health_level"]] += 1

    return {
        "total_departments": len(results),
        "total_headcount": int(total_hc),
        "org_health_score": round(weighted_score),
        "health_distribution": health_dist,
    }


def format_human(results: list, summary: dict, threshold: float) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("ORGANIZATIONAL HEALTH REPORT")
    lines.append("=" * 70)
    lines.append("")

    health_label = "HEALTHY" if summary["org_health_score"] >= 80 else "WATCH" if summary["org_health_score"] >= 65 else "AT RISK" if summary["org_health_score"] >= 50 else "CRITICAL"
    lines.append(f"  Org Health Score:      {summary['org_health_score']}/100 ({health_label})")
    lines.append(f"  Total Headcount:       {summary['total_headcount']}")
    lines.append(f"  Departments Assessed:  {summary['total_departments']}")
    dist = summary["health_distribution"]
    lines.append(f"  Health Distribution:   Healthy: {dist['HEALTHY']} | Watch: {dist['WATCH']} | At Risk: {dist['AT_RISK']} | Critical: {dist['CRITICAL']}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("DEPARTMENT SCORES")
    lines.append("-" * 70)
    lines.append(f"  {'Department':<22} {'HC':>5} {'Score':>6} {'Status':<10} {'Ret':>4} {'Eng':>4} {'Perf':>5} {'Dev':>4} {'Comp':>5} {'Str':>4}")
    lines.append(f"  {'-'*22} {'-'*5} {'-'*6} {'-'*10} {'-'*4} {'-'*4} {'-'*5} {'-'*4} {'-'*5} {'-'*4}")

    for r in sorted(results, key=lambda x: x["overall_score"]):
        d = r["dimensions"]
        lines.append(
            f"  {r['department']:<22} {r['headcount']:>5} {r['overall_score']:>5}/100 {r['health_level']:<10} "
            f"{d['retention']['score']:>4} {d['engagement']['score']:>4} {d['performance']['score']:>5} "
            f"{d['development']['score']:>4} {d['compensation']['score']:>5} {d['structure']['score']:>4}"
        )

    # Issues for departments below threshold
    flagged = [r for r in results if r["overall_score"] < threshold]
    if flagged:
        lines.append("")
        lines.append("-" * 70)
        lines.append(f"ISSUES (Departments Below {threshold} Threshold)")
        lines.append("-" * 70)
        for r in sorted(flagged, key=lambda x: x["overall_score"]):
            lines.append(f"\n  {r['department']} ({r['overall_score']}/100 - {r['health_level']})")
            for issue in r["all_issues"]:
                lines.append(f"    - {issue}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score organizational health from workforce metrics."
    )
    parser.add_argument("--file", required=True, help="Path to org metrics CSV")
    parser.add_argument("--threshold", type=float, default=65, help="Score threshold for flagging (default: 65)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv_file(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    results = [score_department(row) for row in rows]
    summary = compute_org_summary(results)

    if args.json:
        output = {"summary": summary, "departments": results}
        print(json.dumps(output, indent=2))
    else:
        print(format_human(results, summary, args.threshold))


if __name__ == "__main__":
    main()
