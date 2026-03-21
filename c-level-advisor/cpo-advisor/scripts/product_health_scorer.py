#!/usr/bin/env python3
"""
Product Health Scorer - Score product health across 5 dimensions with PMF assessment.

Evaluates retention (D30/D90), engagement (DAU/MAU), satisfaction (NPS/Sean Ellis),
growth (organic %), and activation (time to value). Generates PMF scoring and trend analysis.

Usage:
    python product_health_scorer.py --input product_data.json
    python product_health_scorer.py --input product_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


DIMENSIONS = {
    "retention": {"weight": 0.30, "metrics": ["d30_retention_pct", "d90_retention_pct"]},
    "engagement": {"weight": 0.25, "metrics": ["dau_mau_ratio_pct"]},
    "satisfaction": {"weight": 0.25, "metrics": ["nps_score", "sean_ellis_pct"]},
    "growth": {"weight": 0.10, "metrics": ["organic_growth_pct"]},
    "activation": {"weight": 0.10, "metrics": ["activation_rate_pct", "time_to_value_days"]},
}

# Business model specific benchmarks
BENCHMARKS = {
    "b2b_saas": {
        "d30_retention_pct": {"weak": 40, "emerging": 60, "strong": 75},
        "d90_retention_pct": {"weak": 25, "emerging": 45, "strong": 60},
        "dau_mau_ratio_pct": {"weak": 15, "emerging": 25, "strong": 35},
        "nps_score": {"weak": 10, "emerging": 30, "strong": 50},
        "sean_ellis_pct": {"weak": 25, "emerging": 35, "strong": 45},
        "organic_growth_pct": {"weak": 10, "emerging": 30, "strong": 50},
        "activation_rate_pct": {"weak": 20, "emerging": 40, "strong": 60},
        "time_to_value_days": {"weak": 14, "emerging": 7, "strong": 2},
    },
    "consumer": {
        "d30_retention_pct": {"weak": 15, "emerging": 25, "strong": 35},
        "d90_retention_pct": {"weak": 8, "emerging": 15, "strong": 25},
        "dau_mau_ratio_pct": {"weak": 15, "emerging": 25, "strong": 40},
        "nps_score": {"weak": 10, "emerging": 30, "strong": 50},
        "sean_ellis_pct": {"weak": 25, "emerging": 35, "strong": 45},
        "organic_growth_pct": {"weak": 20, "emerging": 40, "strong": 60},
        "activation_rate_pct": {"weak": 15, "emerging": 30, "strong": 50},
        "time_to_value_days": {"weak": 3, "emerging": 1, "strong": 0.1},
    },
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def score_metric(value, benchmarks, lower_is_better=False):
    """Score a metric 1-10 based on benchmarks."""
    weak = benchmarks.get("weak", 0)
    emerging = benchmarks.get("emerging", 0)
    strong = benchmarks.get("strong", 0)

    if lower_is_better:
        if value <= strong:
            return 10
        elif value <= emerging:
            return 7
        elif value <= weak:
            return 4
        else:
            return 2
    else:
        if value >= strong:
            return 10
        elif value >= emerging:
            return 7
        elif value >= weak:
            return 4
        else:
            return 2


def assess_pmf(dimension_scores, metrics):
    """Assess product-market fit based on dimension scores and key metrics."""
    retention_score = dimension_scores.get("retention", {}).get("score", 0)
    satisfaction_score = dimension_scores.get("satisfaction", {}).get("score", 0)
    growth_score = dimension_scores.get("growth", {}).get("score", 0)

    sean_ellis = metrics.get("sean_ellis_pct", 0)
    organic = metrics.get("organic_growth_pct", 0)

    if retention_score >= 7 and sean_ellis >= 40 and organic >= 30:
        return {"level": "Strong PMF", "score": 9, "action": "Scale. Invest in acquisition and expansion."}
    elif retention_score >= 5 and sean_ellis >= 25:
        if organic >= 30:
            return {"level": "Moderate PMF", "score": 7, "action": "Double down on power users. Find the segment where retention is strongest."}
        else:
            return {"level": "PMF with weak distribution", "score": 6, "action": "PMF exists but growth engine is broken. Fix distribution."}
    elif retention_score >= 4:
        return {"level": "Emerging PMF", "score": 4, "action": "Find the segment where retention curve flattens. Do not scale yet."}
    else:
        return {"level": "No PMF", "score": 2, "action": "Stop building features. Talk to users. Find the problem worth solving."}


def analyze_product(data):
    """Run product health analysis."""
    product_name = data.get("product_name", "Product")
    business_model = data.get("business_model", "b2b_saas")
    metrics = data.get("metrics", {})
    previous_metrics = data.get("previous_period_metrics", {})

    model_benchmarks = BENCHMARKS.get(business_model, BENCHMARKS["b2b_saas"])

    results = {
        "timestamp": datetime.now().isoformat(),
        "product": product_name,
        "business_model": business_model,
        "overall_health_score": 0,
        "overall_health_label": "",
        "dimension_scores": {},
        "metric_details": [],
        "pmf_assessment": {},
        "trends": [],
        "recommendations": [],
    }

    total_weighted = 0

    for dim_name, dim_config in DIMENSIONS.items():
        dim_scores = []

        for metric_name in dim_config["metrics"]:
            value = metrics.get(metric_name, 0)
            benchmark = model_benchmarks.get(metric_name, {"weak": 0, "emerging": 50, "strong": 100})
            lower_is_better = metric_name in ("time_to_value_days",)

            score = score_metric(value, benchmark, lower_is_better)
            dim_scores.append(score)

            # Trend detection
            prev_value = previous_metrics.get(metric_name)
            trend = "no_data"
            if prev_value is not None:
                if lower_is_better:
                    trend = "improving" if value < prev_value else ("declining" if value > prev_value else "stable")
                else:
                    trend = "improving" if value > prev_value else ("declining" if value < prev_value else "stable")

            detail = {
                "dimension": dim_name,
                "metric": metric_name,
                "value": value,
                "score": score,
                "benchmark_weak": benchmark.get("weak"),
                "benchmark_strong": benchmark.get("strong"),
                "trend": trend,
            }
            results["metric_details"].append(detail)

            if trend in ("improving", "declining"):
                results["trends"].append({
                    "metric": metric_name,
                    "trend": trend,
                    "current": value,
                    "previous": prev_value,
                })

        dim_avg = round(sum(dim_scores) / max(len(dim_scores), 1), 1)
        weighted = round(dim_avg * dim_config["weight"], 2)
        total_weighted += weighted

        label = "Strong" if dim_avg >= 7 else ("Emerging" if dim_avg >= 4 else "Weak")
        results["dimension_scores"][dim_name] = {
            "score": dim_avg,
            "weighted_score": weighted,
            "label": label,
            "weight": dim_config["weight"],
        }

    results["overall_health_score"] = round(total_weighted, 1)
    results["overall_health_label"] = (
        "Healthy" if total_weighted >= 7 else (
            "Moderate" if total_weighted >= 4 else "Critical"
        )
    )

    # PMF assessment
    results["pmf_assessment"] = assess_pmf(results["dimension_scores"], metrics)

    # Recommendations
    recs = results["recommendations"]
    for dim_name, dim_data in results["dimension_scores"].items():
        if dim_data["label"] == "Weak":
            if dim_name == "retention":
                recs.append("PRIORITY: Retention is weak -- stop building new features, investigate why users leave")
            elif dim_name == "engagement":
                recs.append("Engagement below threshold -- review core loop, identify habit-forming features")
            elif dim_name == "satisfaction":
                recs.append("Satisfaction low -- conduct NPS detractor analysis, identify top pain points")
            elif dim_name == "activation":
                recs.append("Activation needs work -- reduce time to first value, simplify onboarding")

    declining = [t for t in results["trends"] if t["trend"] == "declining"]
    if declining:
        recs.append(f"Declining metrics: {', '.join(t['metric'] for t in declining)}")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "PRODUCT HEALTH SCORECARD",
        "=" * 60,
        f"Product: {results['product']}",
        f"Business Model: {results['business_model']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        f"OVERALL HEALTH: {results['overall_health_score']}/10 ({results['overall_health_label']})",
        "",
        f"PMF ASSESSMENT: {results['pmf_assessment']['level']} (score: {results['pmf_assessment']['score']}/10)",
        f"  Action: {results['pmf_assessment']['action']}",
        "",
        "DIMENSION SCORES",
    ]

    for dim, data in results["dimension_scores"].items():
        lines.append(f"  {dim.title()}: {data['score']}/10 ({data['label']}) [weight: {data['weight']}]")

    lines.append("")
    lines.append("METRIC DETAILS")
    for d in results["metric_details"]:
        trend_arrow = {"improving": "+", "declining": "-", "stable": "=", "no_data": "?"}
        lines.append(
            f"  [{trend_arrow.get(d['trend'], '?')}] {d['metric']}: {d['value']} "
            f"(score: {d['score']}/10, weak={d['benchmark_weak']}, strong={d['benchmark_strong']})"
        )

    if results["trends"]:
        lines.append("")
        lines.append("TRENDS")
        for t in results["trends"]:
            lines.append(f"  {t['metric']}: {t['previous']} -> {t['current']} ({t['trend']})")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score product health across 5 dimensions with PMF assessment")
    parser.add_argument("--input", required=True, help="Path to JSON product data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_product(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
