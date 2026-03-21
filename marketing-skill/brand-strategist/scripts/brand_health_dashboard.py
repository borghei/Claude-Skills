#!/usr/bin/env python3
"""Brand Health Dashboard - Calculate and visualize brand health metrics.

Processes survey and performance data to generate a brand health scorecard
covering awareness, perception, consideration, and loyalty.

Usage:
    python brand_health_dashboard.py survey_data.json
    python brand_health_dashboard.py survey_data.json --json
    python brand_health_dashboard.py --demo
"""

import argparse
import json
import sys


HEALTH_DIMENSIONS = {
    "awareness": {
        "metrics": ["unaided_awareness", "aided_awareness", "top_of_mind"],
        "weight": 0.25,
    },
    "perception": {
        "metrics": ["nps", "brand_sentiment", "attribute_association"],
        "weight": 0.25,
    },
    "consideration": {
        "metrics": ["purchase_intent", "preference_vs_competitors", "recommendation_likelihood"],
        "weight": 0.25,
    },
    "loyalty": {
        "metrics": ["repeat_purchase_rate", "share_of_wallet", "advocacy_rate"],
        "weight": 0.25,
    },
}

BENCHMARKS = {
    "unaided_awareness": {"poor": 10, "average": 25, "good": 50, "excellent": 70},
    "aided_awareness": {"poor": 30, "average": 50, "good": 70, "excellent": 85},
    "top_of_mind": {"poor": 5, "average": 15, "good": 30, "excellent": 50},
    "nps": {"poor": -10, "average": 20, "good": 45, "excellent": 70},
    "brand_sentiment": {"poor": 40, "average": 60, "good": 75, "excellent": 85},
    "attribute_association": {"poor": 30, "average": 50, "good": 65, "excellent": 80},
    "purchase_intent": {"poor": 15, "average": 30, "good": 50, "excellent": 70},
    "preference_vs_competitors": {"poor": 20, "average": 35, "good": 50, "excellent": 65},
    "recommendation_likelihood": {"poor": 20, "average": 40, "good": 60, "excellent": 75},
    "repeat_purchase_rate": {"poor": 20, "average": 40, "good": 60, "excellent": 80},
    "share_of_wallet": {"poor": 15, "average": 30, "good": 50, "excellent": 70},
    "advocacy_rate": {"poor": 5, "average": 15, "good": 30, "excellent": 50},
}


def rate_metric(metric_name, value):
    """Rate a metric against benchmarks."""
    bench = BENCHMARKS.get(metric_name, {"poor": 20, "average": 40, "good": 60, "excellent": 80})
    if value >= bench["excellent"]:
        return "excellent"
    elif value >= bench["good"]:
        return "good"
    elif value >= bench["average"]:
        return "average"
    return "poor"


def normalize_score(metric_name, value):
    """Normalize metric to 0-100 scale."""
    bench = BENCHMARKS.get(metric_name, {"poor": 0, "excellent": 100})
    # NPS ranges from -100 to 100
    if metric_name == "nps":
        return max(0, min(100, (value + 100) / 2))
    return max(0, min(100, value))


def calculate_health(data):
    """Calculate brand health scores from input data."""
    current = data.get("current", {})
    previous = data.get("previous", {})

    dimension_scores = {}

    for dim_name, dim_config in HEALTH_DIMENSIONS.items():
        metrics_results = []
        for metric in dim_config["metrics"]:
            value = current.get(metric)
            if value is not None:
                prev_value = previous.get(metric)
                change = None
                if prev_value is not None:
                    if metric == "nps":
                        change = value - prev_value
                    else:
                        change = round(value - prev_value, 1)

                normalized = normalize_score(metric, value)
                rating = rate_metric(metric, value)

                metrics_results.append({
                    "metric": metric,
                    "value": value,
                    "previous": prev_value,
                    "change": change,
                    "change_direction": "up" if change and change > 0 else ("down" if change and change < 0 else "flat"),
                    "normalized": round(normalized, 1),
                    "rating": rating,
                })

        if metrics_results:
            dim_avg = sum(m["normalized"] for m in metrics_results) / len(metrics_results)
            dimension_scores[dim_name] = {
                "score": round(dim_avg, 1),
                "weight": dim_config["weight"],
                "weighted_score": round(dim_avg * dim_config["weight"], 1),
                "metrics": metrics_results,
            }

    # Overall brand health index
    total_weighted = sum(d["weighted_score"] for d in dimension_scores.values())
    total_weight = sum(d["weight"] for d in dimension_scores.values())
    overall = (total_weighted / total_weight) if total_weight > 0 else 0

    # Strengths and weaknesses
    all_metrics = []
    for dim in dimension_scores.values():
        all_metrics.extend(dim["metrics"])

    strengths = sorted([m for m in all_metrics if m["rating"] in ("good", "excellent")],
                       key=lambda x: x["normalized"], reverse=True)[:3]
    weaknesses = sorted([m for m in all_metrics if m["rating"] in ("poor", "average")],
                        key=lambda x: x["normalized"])[:3]

    # Trends
    improving = [m for m in all_metrics if m.get("change_direction") == "up"]
    declining = [m for m in all_metrics if m.get("change_direction") == "down"]

    return {
        "brand_health_index": round(overall, 1),
        "grade": _grade(overall),
        "dimensions": dimension_scores,
        "strengths": [{"metric": s["metric"], "value": s["value"], "rating": s["rating"]} for s in strengths],
        "weaknesses": [{"metric": w["metric"], "value": w["value"], "rating": w["rating"]} for w in weaknesses],
        "trends": {
            "improving": [{"metric": m["metric"], "change": m["change"]} for m in improving],
            "declining": [{"metric": m["metric"], "change": m["change"]} for m in declining],
        },
    }


def _grade(score):
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    return "F"


def get_demo_data():
    """Return demo data for testing."""
    return {
        "current": {
            "unaided_awareness": 42,
            "aided_awareness": 68,
            "top_of_mind": 18,
            "nps": 45,
            "brand_sentiment": 78,
            "attribute_association": 62,
            "purchase_intent": 55,
            "preference_vs_competitors": 48,
            "recommendation_likelihood": 61,
            "repeat_purchase_rate": 72,
            "share_of_wallet": 38,
            "advocacy_rate": 28,
        },
        "previous": {
            "unaided_awareness": 38,
            "aided_awareness": 65,
            "top_of_mind": 15,
            "nps": 38,
            "brand_sentiment": 74,
            "attribute_association": 58,
            "purchase_intent": 52,
            "preference_vs_competitors": 45,
            "recommendation_likelihood": 57,
            "repeat_purchase_rate": 68,
            "share_of_wallet": 35,
            "advocacy_rate": 25,
        },
    }


def format_report(analysis):
    """Format human-readable dashboard."""
    lines = []
    lines.append("=" * 65)
    lines.append("BRAND HEALTH DASHBOARD")
    lines.append("=" * 65)
    lines.append(f"Brand Health Index: {analysis['brand_health_index']}/100 (Grade: {analysis['grade']})")
    lines.append("")

    # Dimension scores
    lines.append("--- DIMENSION SCORES ---")
    for dim_name, dim_data in analysis["dimensions"].items():
        bar_len = int(dim_data["score"] / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        lines.append(f"  {dim_name.title():<20} [{bar}] {dim_data['score']:.0f}/100")

        for m in dim_data["metrics"]:
            change_str = ""
            if m["change"] is not None:
                arrow = "+" if m["change"] > 0 else ""
                change_str = f" ({arrow}{m['change']})"
            lines.append(f"    {m['metric']:<30} {m['value']:>6}{change_str:<10} [{m['rating']}]")
    lines.append("")

    # Strengths
    if analysis["strengths"]:
        lines.append("--- STRENGTHS ---")
        for s in analysis["strengths"]:
            lines.append(f"  {s['metric']}: {s['value']} [{s['rating']}]")
        lines.append("")

    # Weaknesses
    if analysis["weaknesses"]:
        lines.append("--- AREAS FOR IMPROVEMENT ---")
        for w in analysis["weaknesses"]:
            lines.append(f"  {w['metric']}: {w['value']} [{w['rating']}]")
        lines.append("")

    # Trends
    trends = analysis["trends"]
    if trends["improving"]:
        lines.append("--- IMPROVING ---")
        for t in trends["improving"]:
            lines.append(f"  {t['metric']}: +{t['change']}")
    if trends["declining"]:
        lines.append("--- DECLINING ---")
        for t in trends["declining"]:
            lines.append(f"  {t['metric']}: {t['change']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate brand health metrics dashboard")
    parser.add_argument("input", nargs="?", help="JSON file with brand metrics data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = calculate_health(data)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
