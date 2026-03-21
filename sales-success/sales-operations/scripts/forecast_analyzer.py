#!/usr/bin/env python3
"""Analyze sales forecast accuracy across quarters and categories.

Compares forecasted values against actual outcomes to measure accuracy,
identify bias patterns, and recommend calibration adjustments.

Usage:
    python forecast_analyzer.py --data forecast_history.csv
    python forecast_analyzer.py --data forecast.json --json
    python forecast_analyzer.py --data forecast.csv --quarters 4
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime


FORECAST_CATEGORIES = ["closed", "commit", "best_case", "pipeline", "upside"]

CATEGORY_WEIGHTS = {
    "closed": 1.00,
    "commit": 0.90,
    "best_case": 0.50,
    "pipeline": 0.20,
    "upside": 0.05,
}

ACCURACY_THRESHOLDS = {
    (0, 5): ("Excellent", "Forecast is highly reliable. Maintain current methodology."),
    (5, 10): ("Good", "Within acceptable range. Minor calibration may improve accuracy."),
    (10, 20): ("Fair", "Noticeable deviation. Review stage definitions and commit criteria."),
    (20, 40): ("Poor", "Significant accuracy issues. Overhaul forecast methodology."),
    (40, 200): ("Unreliable", "Forecast not useful for planning. Fundamental process change needed."),
}


def load_data(filepath):
    """Load forecast data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def safe_float(value, default=0.0):
    """Parse float safely."""
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (ValueError, TypeError):
        return default


def analyze_forecast(records, num_quarters=None):
    """Analyze forecast accuracy from historical data."""
    quarterly_data = defaultdict(lambda: {
        "forecast": 0, "actual": 0, "quota": 0,
        "categories": defaultdict(lambda: {"forecast": 0, "actual": 0}),
        "rep_data": defaultdict(lambda: {"forecast": 0, "actual": 0}),
    })

    for record in records:
        quarter = record.get("quarter", record.get("period", "Unknown"))
        forecast = safe_float(record.get("forecast", record.get("forecast_amount", 0)))
        actual = safe_float(record.get("actual", record.get("actual_amount", 0)))
        quota = safe_float(record.get("quota", 0))
        category = record.get("category", record.get("forecast_category", "")).lower().strip().replace(" ", "_")
        rep = record.get("rep", record.get("rep_name", record.get("owner", "")))

        quarterly_data[quarter]["forecast"] += forecast
        quarterly_data[quarter]["actual"] += actual
        if quota > 0:
            quarterly_data[quarter]["quota"] = max(quarterly_data[quarter]["quota"], quota)

        if category:
            quarterly_data[quarter]["categories"][category]["forecast"] += forecast
            quarterly_data[quarter]["categories"][category]["actual"] += actual

        if rep:
            quarterly_data[quarter]["rep_data"][rep]["forecast"] += forecast
            quarterly_data[quarter]["rep_data"][rep]["actual"] += actual

    # Limit to recent quarters
    quarters = sorted(quarterly_data.keys(), reverse=True)
    if num_quarters:
        quarters = quarters[:num_quarters]

    # Quarterly analysis
    quarter_results = []
    accuracy_values = []
    bias_values = []

    for q in quarters:
        data = quarterly_data[q]
        fc = data["forecast"]
        act = data["actual"]
        quota = data["quota"]

        if act > 0:
            accuracy_pct = abs(fc - act) / act * 100
            bias_pct = (fc - act) / act * 100  # Positive = over-forecast
        elif fc > 0:
            accuracy_pct = 100
            bias_pct = 100
        else:
            accuracy_pct = 0
            bias_pct = 0

        accuracy_values.append(accuracy_pct)
        bias_values.append(bias_pct)

        attainment = round(act / quota * 100, 1) if quota > 0 else 0

        # Category breakdown
        cat_results = {}
        for cat in FORECAST_CATEGORIES:
            cd = data["categories"].get(cat, {"forecast": 0, "actual": 0})
            if cd["actual"] > 0:
                cat_acc = abs(cd["forecast"] - cd["actual"]) / cd["actual"] * 100
            else:
                cat_acc = 0 if cd["forecast"] == 0 else 100
            cat_results[cat] = {
                "forecast": round(cd["forecast"], 2),
                "actual": round(cd["actual"], 2),
                "accuracy_error": round(cat_acc, 1),
            }

        # Rep analysis
        rep_results = {}
        for rep, rd in data["rep_data"].items():
            if rd["actual"] > 0:
                rep_acc = abs(rd["forecast"] - rd["actual"]) / rd["actual"] * 100
                rep_bias = (rd["forecast"] - rd["actual"]) / rd["actual"] * 100
            else:
                rep_acc = 100 if rd["forecast"] > 0 else 0
                rep_bias = 100 if rd["forecast"] > 0 else 0
            rep_results[rep] = {
                "forecast": round(rd["forecast"], 2),
                "actual": round(rd["actual"], 2),
                "accuracy_error": round(rep_acc, 1),
                "bias": round(rep_bias, 1),
            }

        quarter_results.append({
            "quarter": q,
            "forecast": round(fc, 2),
            "actual": round(act, 2),
            "quota": round(quota, 2),
            "accuracy_error_pct": round(accuracy_pct, 1),
            "bias_pct": round(bias_pct, 1),
            "quota_attainment_pct": attainment,
            "category_breakdown": cat_results,
            "rep_accuracy": dict(sorted(rep_results.items(), key=lambda x: x[1]["accuracy_error"], reverse=True)),
        })

    # Overall metrics
    avg_accuracy = sum(accuracy_values) / len(accuracy_values) if accuracy_values else 0
    avg_bias = sum(bias_values) / len(bias_values) if bias_values else 0

    label = "Unknown"
    advice = ""
    for (lo, hi), (lbl, adv) in ACCURACY_THRESHOLDS.items():
        if lo <= avg_accuracy < hi:
            label = lbl
            advice = adv
            break

    bias_direction = "over-forecasting" if avg_bias > 0 else "under-forecasting" if avg_bias < 0 else "neutral"
    calibration_factor = round(1 - (avg_bias / 100), 3) if avg_bias != 0 else 1.0

    return {
        "summary": {
            "quarters_analyzed": len(quarters),
            "avg_accuracy_error_pct": round(avg_accuracy, 1),
            "avg_bias_pct": round(avg_bias, 1),
            "accuracy_rating": label,
            "accuracy_advice": advice,
            "bias_direction": bias_direction,
            "recommended_calibration_factor": calibration_factor,
            "improving": accuracy_values[-1] < accuracy_values[0] if len(accuracy_values) >= 2 else None,
        },
        "quarterly_results": quarter_results,
    }


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("FORECAST ACCURACY ANALYSIS")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    s = results["summary"]
    lines.append(f"\n  Quarters Analyzed:       {s['quarters_analyzed']}")
    lines.append(f"  Avg Accuracy Error:      {s['avg_accuracy_error_pct']}%")
    lines.append(f"  Accuracy Rating:         {s['accuracy_rating']}")
    lines.append(f"  Avg Bias:                {s['avg_bias_pct']}% ({s['bias_direction']})")
    lines.append(f"  Calibration Factor:      {s['recommended_calibration_factor']}")
    lines.append(f"  Recommendation:          {s['accuracy_advice']}")
    if s["improving"] is not None:
        trend = "IMPROVING" if s["improving"] else "DECLINING"
        lines.append(f"  Trend:                   {trend}")

    for qr in results["quarterly_results"]:
        lines.append(f"\n{'=' * 50}")
        lines.append(f"  Quarter: {qr['quarter']}")
        lines.append(f"  Forecast: ${qr['forecast']:,.2f}  |  Actual: ${qr['actual']:,.2f}")
        lines.append(f"  Accuracy Error: {qr['accuracy_error_pct']}%  |  Bias: {qr['bias_pct']}%")
        lines.append(f"  Quota: ${qr['quota']:,.2f}  |  Attainment: {qr['quota_attainment_pct']}%")

        if qr["category_breakdown"]:
            lines.append(f"\n  Category Breakdown:")
            lines.append(f"    {'Category':<14} {'Forecast':>12} {'Actual':>12} {'Error':>8}")
            lines.append("    " + "-" * 48)
            for cat, cd in qr["category_breakdown"].items():
                if cd["forecast"] > 0 or cd["actual"] > 0:
                    lines.append(
                        f"    {cat:<14} ${cd['forecast']:>10,.2f} ${cd['actual']:>10,.2f} "
                        f"{cd['accuracy_error']:>7.1f}%"
                    )

        if qr["rep_accuracy"]:
            lines.append(f"\n  Rep Accuracy (worst to best):")
            lines.append(f"    {'Rep':<20} {'Forecast':>12} {'Actual':>12} {'Error':>8} {'Bias':>8}")
            lines.append("    " + "-" * 62)
            for rep, rd in list(qr["rep_accuracy"].items())[:10]:
                bias_flag = " OVR" if rd["bias"] > 20 else " UND" if rd["bias"] < -20 else ""
                lines.append(
                    f"    {rep:<20} ${rd['forecast']:>10,.2f} ${rd['actual']:>10,.2f} "
                    f"{rd['accuracy_error']:>7.1f}% {rd['bias']:>7.1f}%{bias_flag}"
                )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze sales forecast accuracy and identify improvement areas."
    )
    parser.add_argument("--data", required=True, help="Path to forecast history CSV or JSON file")
    parser.add_argument(
        "--quarters", type=int, default=None, help="Number of recent quarters to analyze"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    records = load_data(args.data)
    if not records:
        print("Error: No forecast records found in input file.", file=sys.stderr)
        sys.exit(1)

    results = analyze_forecast(records, args.quarters)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    accuracy = results["summary"]["avg_accuracy_error_pct"]
    sys.exit(0 if accuracy <= 15 else 1)


if __name__ == "__main__":
    main()
