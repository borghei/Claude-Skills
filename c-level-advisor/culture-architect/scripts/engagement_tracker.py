#!/usr/bin/env python3
"""
Engagement Tracker - Track employee engagement metrics over time.

Tracks eNPS, survey scores, participation rates, and retention correlation.
Detects trends, flags declining dimensions, and generates quarterly engagement reports.

Usage:
    python engagement_tracker.py --input engagement_data.json
    python engagement_tracker.py --input engagement_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def classify_enps(score):
    if score > 50:
        return "Exceptional"
    elif score > 30:
        return "Good"
    elif score > 10:
        return "Acceptable"
    elif score > 0:
        return "Concerning"
    else:
        return "Crisis"


def detect_trend(values):
    """Detect trend from a list of values (oldest to newest)."""
    if len(values) < 2:
        return "insufficient_data"

    recent = values[-1]
    previous = values[-2]

    if len(values) >= 3:
        avg_earlier = sum(values[:-1]) / len(values[:-1])
        if recent > avg_earlier * 1.05:
            return "improving"
        elif recent < avg_earlier * 0.95:
            return "declining"
        return "stable"
    else:
        if recent > previous * 1.05:
            return "improving"
        elif recent < previous * 0.95:
            return "declining"
        return "stable"


def calculate_correlation(engagement_scores, attrition_rates):
    """Simple correlation indicator between engagement and attrition."""
    if len(engagement_scores) < 3 or len(attrition_rates) < 3:
        return None

    n = min(len(engagement_scores), len(attrition_rates))
    eng = engagement_scores[:n]
    att = attrition_rates[:n]

    # Check if engagement drops precede attrition increases
    lag_matches = 0
    for i in range(1, n):
        if eng[i] < eng[i - 1] and att[i] > att[i - 1]:
            lag_matches += 1
        elif eng[i] > eng[i - 1] and att[i] < att[i - 1]:
            lag_matches += 1

    correlation_strength = round(lag_matches / max(n - 1, 1), 2)

    if correlation_strength >= 0.7:
        return {"strength": "strong", "score": correlation_strength, "insight": "Engagement changes strongly predict attrition changes"}
    elif correlation_strength >= 0.4:
        return {"strength": "moderate", "score": correlation_strength, "insight": "Some relationship between engagement and attrition"}
    else:
        return {"strength": "weak", "score": correlation_strength, "insight": "Engagement and attrition may be driven by different factors"}


def analyze_engagement(data):
    """Run full engagement analysis."""
    org_name = data.get("organization", "Organization")
    periods = data.get("periods", [])

    results = {
        "timestamp": datetime.now().isoformat(),
        "organization": org_name,
        "periods_analyzed": len(periods),
        "current_state": {},
        "period_results": [],
        "trends": {},
        "alerts": [],
        "attrition_correlation": None,
        "recommendations": [],
    }

    enps_values = []
    overall_scores = []
    participation_values = []
    attrition_values = []

    for period in periods:
        period_name = period.get("period", "Unknown")
        enps = period.get("enps_score", 0)
        overall = period.get("overall_engagement_score", 0)
        participation = period.get("participation_rate_pct", 0)
        attrition = period.get("attrition_rate_pct", 0)
        dimension_scores = period.get("dimension_scores", {})

        enps_values.append(enps)
        overall_scores.append(overall)
        participation_values.append(participation)
        if attrition > 0:
            attrition_values.append(attrition)

        period_result = {
            "period": period_name,
            "enps": enps,
            "enps_label": classify_enps(enps),
            "overall_score": overall,
            "participation_rate": participation,
            "attrition_rate": attrition,
            "dimension_scores": dimension_scores,
            "respondents": period.get("respondents", 0),
        }
        results["period_results"].append(period_result)

    # Current state (latest period)
    if results["period_results"]:
        latest = results["period_results"][-1]
        results["current_state"] = {
            "enps": latest["enps"],
            "enps_label": latest["enps_label"],
            "overall_score": latest["overall_score"],
            "participation_rate": latest["participation_rate"],
            "attrition_rate": latest["attrition_rate"],
        }

    # Trends
    results["trends"] = {
        "enps": detect_trend(enps_values),
        "overall_score": detect_trend(overall_scores),
        "participation": detect_trend(participation_values),
    }

    # Dimension trends (if available across periods)
    all_dim_names = set()
    for p in periods:
        all_dim_names.update(p.get("dimension_scores", {}).keys())

    dimension_trends = {}
    for dim in all_dim_names:
        dim_values = [p.get("dimension_scores", {}).get(dim) for p in periods]
        dim_values = [v for v in dim_values if v is not None]
        if dim_values:
            trend = detect_trend(dim_values)
            dimension_trends[dim] = {
                "latest": dim_values[-1] if dim_values else 0,
                "trend": trend,
            }
            if trend == "declining":
                results["alerts"].append({
                    "dimension": dim,
                    "severity": "high" if dim_values[-1] < 50 else "medium",
                    "message": f"{dim} declining (latest: {dim_values[-1]})",
                })

    results["trends"]["dimensions"] = dimension_trends

    # Attrition correlation
    if overall_scores and attrition_values:
        results["attrition_correlation"] = calculate_correlation(overall_scores, attrition_values)

    # Alerts
    if results["current_state"].get("enps", 0) < 10:
        results["alerts"].append({
            "dimension": "eNPS",
            "severity": "high",
            "message": f"eNPS at {results['current_state']['enps']} -- investigate detractor feedback",
        })

    if results["current_state"].get("participation_rate", 0) < 50:
        results["alerts"].append({
            "dimension": "Participation",
            "severity": "high",
            "message": f"Participation at {results['current_state']['participation_rate']}% -- trust in anonymity may be low",
        })

    if results["trends"]["enps"] == "declining":
        results["alerts"].append({
            "dimension": "eNPS Trend",
            "severity": "high",
            "message": "eNPS declining -- pattern requires root cause analysis",
        })

    # Recommendations
    recs = results["recommendations"]
    for alert in results["alerts"]:
        if alert["severity"] == "high":
            recs.append(f"URGENT: {alert['message']}")

    if results["attrition_correlation"] and results["attrition_correlation"]["strength"] == "strong":
        recs.append("Strong engagement-attrition correlation -- engagement improvements will likely reduce attrition")

    if results["trends"]["overall_score"] == "declining":
        recs.append("Overall engagement declining -- conduct focused listening sessions to identify root causes")

    declining_dims = [d for d, info in dimension_trends.items() if info["trend"] == "declining"]
    if declining_dims:
        recs.append(f"Declining dimensions: {', '.join(declining_dims)} -- prioritize these in next action plan")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "ENGAGEMENT TRACKING REPORT",
        "=" * 60,
        f"Organization: {results['organization']}",
        f"Periods Analyzed: {results['periods_analyzed']}",
        f"Report Date: {results['timestamp'][:10]}",
    ]

    cs = results["current_state"]
    if cs:
        lines.extend([
            "",
            "CURRENT STATE",
            f"  eNPS: {cs.get('enps', 0)} ({cs.get('enps_label', 'N/A')})",
            f"  Overall Score: {cs.get('overall_score', 0)}/100",
            f"  Participation: {cs.get('participation_rate', 0)}%",
            f"  Attrition: {cs.get('attrition_rate', 0)}%",
        ])

    lines.append("")
    lines.append("TRENDS")
    for metric, trend in results["trends"].items():
        if isinstance(trend, dict):
            continue  # Skip nested dimension trends
        arrow = {"improving": "+", "declining": "-", "stable": "=", "insufficient_data": "?"}
        lines.append(f"  [{arrow.get(trend, '?')}] {metric}: {trend}")

    dim_trends = results["trends"].get("dimensions", {})
    if dim_trends:
        lines.append("")
        lines.append("DIMENSION TRENDS")
        for dim, info in sorted(dim_trends.items(), key=lambda x: x[1]["latest"]):
            arrow = {"improving": "+", "declining": "-", "stable": "=", "insufficient_data": "?"}
            lines.append(f"  [{arrow.get(info['trend'], '?')}] {dim}: {info['latest']}/100 ({info['trend']})")

    lines.append("")
    lines.append("PERIOD HISTORY")
    for p in results["period_results"]:
        lines.append(f"  {p['period']}: eNPS={p['enps']} ({p['enps_label']}), score={p['overall_score']}, "
                      f"participation={p['participation_rate']}%, attrition={p['attrition_rate']}%")

    if results["attrition_correlation"]:
        ac = results["attrition_correlation"]
        lines.extend([
            "",
            "ENGAGEMENT-ATTRITION CORRELATION",
            f"  Strength: {ac['strength']} (score: {ac['score']})",
            f"  Insight: {ac['insight']}",
        ])

    if results["alerts"]:
        lines.append("")
        lines.append("ALERTS")
        for a in results["alerts"]:
            lines.append(f"  [{a['severity'].upper()}] {a['message']}")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track employee engagement metrics over time with trend detection")
    parser.add_argument("--input", required=True, help="Path to JSON engagement data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_engagement(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
