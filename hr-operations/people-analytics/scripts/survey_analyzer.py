#!/usr/bin/env python3
"""
Survey Analyzer - Analyze employee engagement survey results.

Reads survey response CSV data and computes category scores, response rates,
driver analysis (impact on overall engagement), period-over-period comparison,
and segment breakdowns with priority matrix classification.

Usage:
    python survey_analyzer.py --file survey_results.csv
    python survey_analyzer.py --file survey_results.csv --prior prior_survey.csv --json
    python survey_analyzer.py --file survey_results.csv --segment department

Input CSV columns:
    respondent_id   - Unique anonymous respondent ID
    department      - Department name (optional, for segmentation)
    level           - Job level (optional, for segmentation)
    tenure_band     - Tenure grouping (optional, for segmentation)
    location        - Office location (optional, for segmentation)
    category        - Survey question category (e.g., Manager, Growth, Culture, Compensation, Workload)
    question        - Survey question text
    score           - Likert score (1-5)

Output: Category scores, driver analysis, eNPS, segment breakdowns, and recommendations.
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict


CATEGORY_BENCHMARKS = {
    "manager": 3.8,
    "growth": 3.5,
    "culture": 3.7,
    "compensation": 3.3,
    "workload": 3.4,
    "belonging": 3.6,
    "communication": 3.5,
    "recognition": 3.4,
    "autonomy": 3.6,
    "mission": 3.8,
}

MIN_SEGMENT_SIZE = 5  # Anonymity threshold


def read_csv(path: str) -> list:
    """Read CSV file and return list of dicts."""
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"respondent_id", "category", "score"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            print(f"Error: Missing required columns: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    return rows


def parse_score(val: str) -> float:
    """Parse score value."""
    try:
        s = float(val)
        if 1 <= s <= 5:
            return s
    except (ValueError, TypeError):
        pass
    return None


def compute_response_rate(rows: list, total_employees: int = None) -> dict:
    """Compute response rate metrics."""
    respondents = set()
    for row in rows:
        respondents.add(row["respondent_id"])
    count = len(respondents)
    rate = round(count / total_employees * 100, 1) if total_employees else None
    return {
        "respondents": count,
        "total_employees": total_employees,
        "response_rate_pct": rate,
        "meets_threshold": rate >= 80 if rate else None,
    }


def compute_category_scores(rows: list) -> list:
    """Compute average score per category."""
    cat_scores = defaultdict(list)
    for row in rows:
        score = parse_score(row["score"])
        if score is not None:
            cat = row["category"].strip().lower()
            cat_scores[cat].append(score)

    results = []
    for cat, scores in sorted(cat_scores.items()):
        avg = sum(scores) / len(scores)
        benchmark = CATEGORY_BENCHMARKS.get(cat, 3.5)
        favorable = sum(1 for s in scores if s >= 4) / len(scores) * 100
        results.append({
            "category": cat.title(),
            "avg_score": round(avg, 2),
            "favorable_pct": round(favorable, 1),
            "response_count": len(scores),
            "benchmark": benchmark,
            "vs_benchmark": round(avg - benchmark, 2),
        })

    results.sort(key=lambda x: x["avg_score"])
    return results


def compute_overall_engagement(rows: list) -> dict:
    """Compute overall engagement score."""
    scores = []
    for row in rows:
        score = parse_score(row["score"])
        if score is not None:
            scores.append(score)

    if not scores:
        return {"avg_score": 0, "favorable_pct": 0, "response_count": 0}

    avg = sum(scores) / len(scores)
    favorable = sum(1 for s in scores if s >= 4) / len(scores) * 100
    # eNPS approximation: promoters (5) - detractors (1-3)
    promoters = sum(1 for s in scores if s == 5) / len(scores) * 100
    detractors = sum(1 for s in scores if s <= 3) / len(scores) * 100
    enps = round(promoters - detractors)

    return {
        "avg_score": round(avg, 2),
        "favorable_pct": round(favorable, 1),
        "enps": enps,
        "response_count": len(scores),
    }


def compute_driver_analysis(rows: list) -> list:
    """
    Simple driver analysis: compute correlation between each category
    and overall engagement (respondent-level average).
    Uses Pearson correlation approximation with standard library.
    """
    # Build respondent-level data
    respondent_cats = defaultdict(lambda: defaultdict(list))
    respondent_overall = defaultdict(list)

    for row in rows:
        score = parse_score(row["score"])
        if score is not None:
            rid = row["respondent_id"]
            cat = row["category"].strip().lower()
            respondent_cats[rid][cat].append(score)
            respondent_overall[rid].append(score)

    # Average per respondent per category and overall
    respondent_cat_avg = {}
    respondent_overall_avg = {}
    for rid in respondent_overall:
        respondent_overall_avg[rid] = sum(respondent_overall[rid]) / len(respondent_overall[rid])
        respondent_cat_avg[rid] = {}
        for cat, scores in respondent_cats[rid].items():
            respondent_cat_avg[rid][cat] = sum(scores) / len(scores)

    # Compute correlation per category
    all_cats = set()
    for rid in respondent_cat_avg:
        all_cats.update(respondent_cat_avg[rid].keys())

    drivers = []
    for cat in all_cats:
        x_vals = []
        y_vals = []
        for rid in respondent_cat_avg:
            if cat in respondent_cat_avg[rid]:
                x_vals.append(respondent_cat_avg[rid][cat])
                y_vals.append(respondent_overall_avg[rid])

        if len(x_vals) < 5:
            continue

        # Pearson correlation
        n = len(x_vals)
        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n
        cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals)) / n
        std_x = math.sqrt(sum((x - mean_x) ** 2 for x in x_vals) / n)
        std_y = math.sqrt(sum((y - mean_y) ** 2 for y in y_vals) / n)
        if std_x > 0 and std_y > 0:
            r = cov / (std_x * std_y)
        else:
            r = 0

        avg_score = sum(x_vals) / len(x_vals)
        drivers.append({
            "category": cat.title(),
            "impact": round(r, 3),
            "avg_score": round(avg_score, 2),
        })

    drivers.sort(key=lambda x: x["impact"], reverse=True)
    return drivers


def classify_priorities(drivers: list) -> list:
    """
    Classify categories into priority matrix quadrants:
    High Impact + Low Score = Priority Action
    High Impact + High Score = Maintain
    Low Impact + Low Score = Monitor
    Low Impact + High Score = Celebrate
    """
    if not drivers:
        return []

    median_impact = sorted([d["impact"] for d in drivers])[len(drivers) // 2]
    median_score = sorted([d["avg_score"] for d in drivers])[len(drivers) // 2]

    for d in drivers:
        high_impact = d["impact"] >= median_impact
        high_score = d["avg_score"] >= median_score
        if high_impact and not high_score:
            d["quadrant"] = "PRIORITY_ACTION"
        elif high_impact and high_score:
            d["quadrant"] = "MAINTAIN"
        elif not high_impact and not high_score:
            d["quadrant"] = "MONITOR"
        else:
            d["quadrant"] = "CELEBRATE"

    return drivers


def compute_segment_breakdown(rows: list, segment_field: str) -> list:
    """Compute scores by segment (department, level, etc.)."""
    seg_scores = defaultdict(list)
    for row in rows:
        score = parse_score(row["score"])
        seg_val = row.get(segment_field, "").strip()
        if score is not None and seg_val:
            seg_scores[seg_val].append(score)

    results = []
    for seg, scores in sorted(seg_scores.items()):
        if len(set(row["respondent_id"] for row in rows if row.get(segment_field, "").strip() == seg)) < MIN_SEGMENT_SIZE:
            results.append({
                "segment": seg,
                "suppressed": True,
                "reason": f"Fewer than {MIN_SEGMENT_SIZE} respondents (anonymity protection)",
            })
            continue

        avg = sum(scores) / len(scores)
        favorable = sum(1 for s in scores if s >= 4) / len(scores) * 100
        results.append({
            "segment": seg,
            "avg_score": round(avg, 2),
            "favorable_pct": round(favorable, 1),
            "response_count": len(scores),
            "suppressed": False,
        })

    results.sort(key=lambda x: x.get("avg_score", 0))
    return results


def compare_periods(current: list, prior: list) -> list:
    """Compare current period scores to prior period."""
    prior_cats = {}
    for row in prior:
        score = parse_score(row["score"])
        if score is not None:
            cat = row["category"].strip().lower()
            if cat not in prior_cats:
                prior_cats[cat] = []
            prior_cats[cat].append(score)

    prior_avgs = {cat: sum(s) / len(s) for cat, s in prior_cats.items()}

    current_cats = compute_category_scores(current)
    for cat_data in current_cats:
        cat_key = cat_data["category"].lower()
        if cat_key in prior_avgs:
            cat_data["prior_score"] = round(prior_avgs[cat_key], 2)
            cat_data["change"] = round(cat_data["avg_score"] - prior_avgs[cat_key], 2)
        else:
            cat_data["prior_score"] = None
            cat_data["change"] = None

    return current_cats


def build_recommendations(category_scores: list, drivers: list) -> list:
    """Generate recommendations from analysis."""
    recs = []

    # Find priority action items
    priority_items = [d for d in drivers if d.get("quadrant") == "PRIORITY_ACTION"]
    for item in priority_items[:3]:
        recs.append(
            f"[PRIORITY] {item['category']} has high impact on engagement (r={item['impact']}) "
            f"but scores below median ({item['avg_score']}/5.0). Investigate root causes and develop a targeted action plan."
        )

    # Low-scoring categories
    for cat in category_scores[:2]:
        if cat["vs_benchmark"] < -0.3:
            recs.append(
                f"{cat['category']} scores {abs(cat['vs_benchmark']):.2f} below benchmark "
                f"({cat['avg_score']} vs {cat['benchmark']}). Review with department leaders and identify specific pain points."
            )

    if not recs:
        recs.append("All categories are at or above benchmark. Focus on maintaining momentum and addressing any segment-specific gaps.")

    return recs


def format_human(overall: dict, categories: list, drivers: list, segments: list,
                 recommendations: list, response_rate: dict) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 65)
    lines.append("ENGAGEMENT SURVEY ANALYSIS REPORT")
    lines.append("=" * 65)
    lines.append("")
    lines.append(f"  Overall Engagement Score: {overall['avg_score']} / 5.0")
    lines.append(f"  Favorable Response Rate:  {overall['favorable_pct']}%")
    lines.append(f"  eNPS:                     {overall['enps']}")
    lines.append(f"  Total Responses:          {overall['response_count']}")
    if response_rate.get("response_rate_pct"):
        lines.append(f"  Survey Response Rate:     {response_rate['response_rate_pct']}%")
    lines.append("")

    lines.append("-" * 65)
    lines.append("CATEGORY SCORES")
    lines.append("-" * 65)
    lines.append(f"  {'Category':<20} {'Score':>6} {'Fav%':>6} {'Bench':>6} {'Delta':>7}")
    lines.append(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*6} {'-'*7}")
    for cat in categories:
        delta = f"{cat['vs_benchmark']:+.2f}" if cat['vs_benchmark'] else "--"
        lines.append(f"  {cat['category']:<20} {cat['avg_score']:>6.2f} {cat['favorable_pct']:>5.1f}% {cat['benchmark']:>6.2f} {delta:>7}")

    if drivers:
        lines.append("")
        lines.append("-" * 65)
        lines.append("DRIVER ANALYSIS (Impact on Overall Engagement)")
        lines.append("-" * 65)
        lines.append(f"  {'Category':<20} {'Impact':>8} {'Score':>6} {'Quadrant':<20}")
        lines.append(f"  {'-'*20} {'-'*8} {'-'*6} {'-'*20}")
        for d in drivers:
            quad = d.get("quadrant", "--").replace("_", " ").title()
            lines.append(f"  {d['category']:<20} {d['impact']:>8.3f} {d['avg_score']:>6.2f} {quad:<20}")

    if segments:
        lines.append("")
        lines.append("-" * 65)
        lines.append("SEGMENT BREAKDOWN")
        lines.append("-" * 65)
        for seg in segments:
            if seg.get("suppressed"):
                lines.append(f"  {seg['segment']:<25} [SUPPRESSED - {seg['reason']}]")
            else:
                lines.append(f"  {seg['segment']:<25} Score: {seg['avg_score']:.2f}  Favorable: {seg['favorable_pct']:.1f}%  (n={seg['response_count']})")

    lines.append("")
    lines.append("-" * 65)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 65)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze employee engagement survey results."
    )
    parser.add_argument("--file", required=True, help="Path to survey results CSV")
    parser.add_argument("--prior", default=None, help="Path to prior period survey CSV for comparison")
    parser.add_argument("--segment", default="department", help="Segment field for breakdown (default: department)")
    parser.add_argument("--total-employees", type=int, default=None, help="Total employee count for response rate calculation")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    rows = read_csv(args.file)
    if not rows:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    prior_rows = read_csv(args.prior) if args.prior else None

    overall = compute_overall_engagement(rows)
    response_rate = compute_response_rate(rows, args.total_employees)

    if prior_rows:
        categories = compare_periods(rows, prior_rows)
    else:
        categories = compute_category_scores(rows)

    drivers = compute_driver_analysis(rows)
    drivers = classify_priorities(drivers)
    segments = compute_segment_breakdown(rows, args.segment)
    recommendations = build_recommendations(categories, drivers)

    if args.json:
        output = {
            "overall_engagement": overall,
            "response_rate": response_rate,
            "category_scores": categories,
            "driver_analysis": drivers,
            "segment_breakdown": segments,
            "recommendations": recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(overall, categories, drivers, segments, recommendations, response_rate))


if __name__ == "__main__":
    main()
