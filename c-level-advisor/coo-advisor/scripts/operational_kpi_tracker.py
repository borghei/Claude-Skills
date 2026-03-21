#!/usr/bin/env python3
"""
Operational KPI Tracker - Track operational KPIs across efficiency, quality, scalability.

Calculates health scores, detects trends, flags at-risk metrics, and generates
improvement recommendations based on operational maturity level.

Usage:
    python operational_kpi_tracker.py --input kpi_data.json
    python operational_kpi_tracker.py --input kpi_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


KPI_CATEGORIES = {
    "efficiency": {
        "weight": 0.35,
        "metrics": ["cycle_time", "first_time_completion", "cost_per_transaction", "automation_rate"],
    },
    "quality": {
        "weight": 0.35,
        "metrics": ["error_rate", "rework_pct", "customer_satisfaction", "sla_compliance"],
    },
    "scalability": {
        "weight": 0.30,
        "metrics": ["volume_growth_handling", "cost_per_unit_trend", "capacity_utilization", "bottleneck_count"],
    },
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def score_metric(metric_name, actual, target, direction="lower_better"):
    """Score a single metric 0-100 based on target achievement."""
    if target == 0:
        return 50.0

    if direction == "lower_better":
        # For metrics where lower is better (error_rate, cycle_time, cost)
        if actual <= target:
            return min(100, round((target / max(actual, 0.01)) * 50 + 50, 1))
        else:
            return max(0, round((target / actual) * 50, 1))
    else:
        # For metrics where higher is better (satisfaction, completion rate)
        if actual >= target:
            return min(100, round((actual / target) * 50 + 50, 1))
        else:
            return max(0, round((actual / max(target, 0.01)) * 50, 1))


METRIC_DIRECTIONS = {
    "cycle_time": "lower_better",
    "first_time_completion": "higher_better",
    "cost_per_transaction": "lower_better",
    "automation_rate": "higher_better",
    "error_rate": "lower_better",
    "rework_pct": "lower_better",
    "customer_satisfaction": "higher_better",
    "sla_compliance": "higher_better",
    "volume_growth_handling": "higher_better",
    "cost_per_unit_trend": "lower_better",
    "capacity_utilization": "higher_better",
    "bottleneck_count": "lower_better",
}


def get_health_label(score):
    if score >= 80:
        return "Healthy"
    elif score >= 60:
        return "Acceptable"
    elif score >= 40:
        return "At Risk"
    else:
        return "Critical"


def detect_trend(periods):
    """Detect trend direction from period-over-period data."""
    if len(periods) < 2:
        return "insufficient_data"
    last = periods[-1]
    prev = periods[-2]
    if last > prev * 1.05:
        return "improving" if last > prev else "declining"
    elif last < prev * 0.95:
        return "declining" if last < prev else "improving"
    return "stable"


def analyze_kpis(data):
    """Run full KPI analysis."""
    org_name = data.get("organization", "Organization")
    maturity_level = data.get("maturity_level", 2)
    kpi_data = data.get("kpis", {})
    periods = data.get("periods", [])

    results = {
        "timestamp": datetime.now().isoformat(),
        "organization": org_name,
        "maturity_level": maturity_level,
        "overall_health_score": 0,
        "overall_health_label": "",
        "category_scores": {},
        "metric_details": [],
        "at_risk_metrics": [],
        "trends": [],
        "recommendations": [],
    }

    total_weighted_score = 0

    for category, config in KPI_CATEGORIES.items():
        cat_data = kpi_data.get(category, {})
        cat_scores = []

        for metric_name in config["metrics"]:
            metric_info = cat_data.get(metric_name, {})
            actual = metric_info.get("actual", 0)
            target = metric_info.get("target", 0)
            direction = METRIC_DIRECTIONS.get(metric_name, "lower_better")
            history = metric_info.get("history", [])

            score = score_metric(metric_name, actual, target, direction)
            cat_scores.append(score)

            trend = detect_trend(history) if history else "no_data"

            detail = {
                "category": category,
                "metric": metric_name,
                "actual": actual,
                "target": target,
                "score": score,
                "health": get_health_label(score),
                "trend": trend,
            }
            results["metric_details"].append(detail)

            if score < 50:
                results["at_risk_metrics"].append({
                    "metric": metric_name,
                    "category": category,
                    "score": score,
                    "actual": actual,
                    "target": target,
                    "gap": round(abs(actual - target), 2),
                })

            if trend in ("improving", "declining"):
                results["trends"].append({
                    "metric": metric_name,
                    "trend": trend,
                    "current": actual,
                })

        cat_avg = round(sum(cat_scores) / max(len(cat_scores), 1), 1)
        weighted = round(cat_avg * config["weight"], 1)
        total_weighted_score += weighted

        results["category_scores"][category] = {
            "score": cat_avg,
            "weighted_score": weighted,
            "health": get_health_label(cat_avg),
            "metrics_count": len(cat_scores),
        }

    results["overall_health_score"] = round(total_weighted_score, 1)
    results["overall_health_label"] = get_health_label(total_weighted_score)

    # Sort at-risk by score (worst first)
    results["at_risk_metrics"].sort(key=lambda x: x["score"])

    # Generate recommendations
    recs = results["recommendations"]
    if total_weighted_score < 40:
        recs.append("CRITICAL: Overall operational health below 40 -- immediate leadership attention required")
    if maturity_level < 3 and total_weighted_score > 60:
        recs.append("Consider advancing to Maturity Level 3 (Managed) -- metrics support the transition")

    for ar in results["at_risk_metrics"][:3]:
        if ar["category"] == "efficiency":
            recs.append(f"Improve {ar['metric']}: current {ar['actual']} vs target {ar['target']} -- review process automation opportunities")
        elif ar["category"] == "quality":
            recs.append(f"Address {ar['metric']}: current {ar['actual']} vs target {ar['target']} -- implement quality gates and root cause analysis")
        elif ar["category"] == "scalability":
            recs.append(f"Scale {ar['metric']}: current {ar['actual']} vs target {ar['target']} -- evaluate capacity and infrastructure")

    declining = [t for t in results["trends"] if t["trend"] == "declining"]
    if declining:
        recs.append(f"Declining trends detected in: {', '.join(t['metric'] for t in declining[:3])}")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "OPERATIONAL KPI DASHBOARD",
        "=" * 60,
        f"Organization: {results['organization']}",
        f"Maturity Level: {results['maturity_level']}/4",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        f"OVERALL HEALTH: {results['overall_health_score']}/100 ({results['overall_health_label']})",
        "",
        "CATEGORY SCORES",
    ]

    for cat, scores in results["category_scores"].items():
        lines.append(f"  {cat.title()}: {scores['score']}/100 ({scores['health']})")

    if results["at_risk_metrics"]:
        lines.append("")
        lines.append("AT-RISK METRICS")
        for ar in results["at_risk_metrics"]:
            lines.append(f"  {ar['metric']} ({ar['category']}): score={ar['score']}, actual={ar['actual']}, target={ar['target']}")

    lines.append("")
    lines.append("METRIC DETAILS")
    for detail in results["metric_details"]:
        trend_arrow = {"improving": "+", "declining": "-", "stable": "=", "no_data": "?", "insufficient_data": "?"}
        lines.append(
            f"  [{trend_arrow.get(detail['trend'], '?')}] {detail['metric']}: "
            f"{detail['actual']} (target: {detail['target']}) -- {detail['health']}"
        )

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track operational KPIs with health scoring and trend detection")
    parser.add_argument("--input", required=True, help="Path to JSON KPI data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_kpis(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
