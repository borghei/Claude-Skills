#!/usr/bin/env python3
"""
Revenue Waterfall Analyzer - Analyze ARR waterfall with NRR/GRR and trend detection.

Calculates net new ARR, NRR, GRR across multiple periods. Detects retention trends,
flags risk signals, and benchmarks against SaaS industry standards.

Usage:
    python revenue_waterfall_analyzer.py --input revenue_data.json
    python revenue_waterfall_analyzer.py --input revenue_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


NRR_BENCHMARKS = {
    "world_class": {"min": 130, "label": "World-class (Snowflake/Twilio tier)"},
    "excellent": {"min": 110, "label": "Excellent"},
    "healthy": {"min": 100, "label": "Healthy"},
    "concerning": {"min": 90, "label": "Concerning"},
    "critical": {"min": 0, "label": "Critical -- leaky bucket"},
}

GRR_BENCHMARKS = {
    "excellent": {"min": 95, "label": "Excellent"},
    "good": {"min": 90, "label": "Good"},
    "acceptable": {"min": 85, "label": "Acceptable"},
    "concerning": {"min": 80, "label": "Concerning"},
    "critical": {"min": 0, "label": "Critical"},
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def get_benchmark_label(value, benchmarks):
    """Get benchmark label for a value."""
    for level, config in benchmarks.items():
        if value >= config["min"]:
            return config["label"]
    return "Below all benchmarks"


def analyze_period(period):
    """Analyze a single period's revenue waterfall."""
    opening = period.get("opening_arr", 0)
    new_logo = period.get("new_logo_arr", 0)
    expansion = period.get("expansion_arr", 0)
    contraction = period.get("contraction_arr", 0)
    churned = period.get("churned_arr", 0)

    closing = opening + new_logo + expansion - contraction - churned
    net_new = new_logo + expansion - contraction - churned

    nrr = round(((opening + expansion - contraction - churned) / max(opening, 1)) * 100, 1)
    grr = round(((opening - contraction - churned) / max(opening, 1)) * 100, 1)

    expansion_rate = round((expansion / max(opening, 1)) * 100, 1)
    churn_rate = round((churned / max(opening, 1)) * 100, 1)
    contraction_rate = round((contraction / max(opening, 1)) * 100, 1)

    return {
        "period": period.get("period", "Unknown"),
        "opening_arr": opening,
        "new_logo_arr": new_logo,
        "expansion_arr": expansion,
        "contraction_arr": contraction,
        "churned_arr": churned,
        "closing_arr": round(closing, 0),
        "net_new_arr": round(net_new, 0),
        "nrr_pct": nrr,
        "grr_pct": grr,
        "expansion_rate_pct": expansion_rate,
        "churn_rate_pct": churn_rate,
        "contraction_rate_pct": contraction_rate,
        "nrr_benchmark": get_benchmark_label(nrr, NRR_BENCHMARKS),
        "grr_benchmark": get_benchmark_label(grr, GRR_BENCHMARKS),
    }


def detect_trends(period_results):
    """Detect trends across periods."""
    trends = []

    if len(period_results) < 2:
        return trends

    nrr_values = [p["nrr_pct"] for p in period_results]
    grr_values = [p["grr_pct"] for p in period_results]
    churn_values = [p["churn_rate_pct"] for p in period_results]

    # NRR trend
    if len(nrr_values) >= 2:
        recent_avg = sum(nrr_values[-2:]) / 2
        older_avg = sum(nrr_values[:max(1, len(nrr_values) - 2)]) / max(1, len(nrr_values) - 2)
        if recent_avg < older_avg - 2:
            trends.append({"metric": "NRR", "direction": "declining", "severity": "high" if recent_avg < 100 else "medium"})
        elif recent_avg > older_avg + 2:
            trends.append({"metric": "NRR", "direction": "improving", "severity": "positive"})

    # Churn trend
    if len(churn_values) >= 2:
        if churn_values[-1] > churn_values[-2] * 1.1:
            trends.append({"metric": "Churn Rate", "direction": "increasing", "severity": "high"})

    # Expansion vs churn balance
    last = period_results[-1]
    if last["expansion_arr"] < last["churned_arr"]:
        trends.append({"metric": "Expansion vs Churn", "direction": "churn exceeds expansion", "severity": "high"})

    return trends


def analyze_revenue(data):
    """Run full revenue waterfall analysis."""
    periods = data.get("periods", [])
    company = data.get("company", "Company")

    results = {
        "timestamp": datetime.now().isoformat(),
        "company": company,
        "periods_analyzed": len(periods),
        "period_results": [],
        "trends": [],
        "risk_signals": [],
        "recommendations": [],
        "summary": {},
    }

    for period in periods:
        results["period_results"].append(analyze_period(period))

    # Detect trends
    results["trends"] = detect_trends(results["period_results"])

    # Risk signals
    if results["period_results"]:
        latest = results["period_results"][-1]

        if latest["nrr_pct"] < 90:
            results["risk_signals"].append({
                "signal": f"NRR at {latest['nrr_pct']}% -- CRISIS level",
                "action": "Stop scaling sales. Fix retention first.",
                "severity": "critical",
            })
        elif latest["nrr_pct"] < 100:
            results["risk_signals"].append({
                "signal": f"NRR at {latest['nrr_pct']}% -- churn eating expansion",
                "action": "Diagnose: product gap, CS gap, or ICP problem?",
                "severity": "warning",
            })

        if latest["grr_pct"] < 80:
            results["risk_signals"].append({
                "signal": f"GRR at {latest['grr_pct']}% -- base is eroding",
                "action": "Immediate churn and contraction analysis needed",
                "severity": "critical",
            })

        if latest["expansion_rate_pct"] < 5:
            results["risk_signals"].append({
                "signal": "Expansion revenue below 5% -- upsell motion weak or missing",
                "action": "Design expansion triggers, usage-based upsell alerts, cross-sell bundles",
                "severity": "warning",
            })

    # Summary
    if results["period_results"]:
        latest = results["period_results"][-1]
        first = results["period_results"][0]
        results["summary"] = {
            "latest_arr": latest["closing_arr"],
            "arr_growth": round(latest["closing_arr"] - first["opening_arr"], 0),
            "avg_nrr": round(sum(p["nrr_pct"] for p in results["period_results"]) / len(results["period_results"]), 1),
            "avg_grr": round(sum(p["grr_pct"] for p in results["period_results"]) / len(results["period_results"]), 1),
            "total_new_logo": sum(p["new_logo_arr"] for p in results["period_results"]),
            "total_expansion": sum(p["expansion_arr"] for p in results["period_results"]),
            "total_churned": sum(p["churned_arr"] for p in results["period_results"]),
        }

    # Recommendations
    recs = results["recommendations"]
    for risk in results["risk_signals"]:
        recs.append(f"[{risk['severity'].upper()}] {risk['action']}")

    declining = [t for t in results["trends"] if t["direction"] in ("declining", "increasing") and t["severity"] == "high"]
    for t in declining:
        recs.append(f"Address {t['metric']} trend ({t['direction']}) -- investigate root cause")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "REVENUE WATERFALL ANALYSIS",
        "=" * 60,
        f"Company: {results['company']}",
        f"Periods Analyzed: {results['periods_analyzed']}",
        f"Analysis Date: {results['timestamp'][:10]}",
    ]

    if results["summary"]:
        s = results["summary"]
        lines.extend([
            "",
            "SUMMARY",
            f"  Latest ARR: ${s['latest_arr']:,.0f}",
            f"  ARR Growth: ${s['arr_growth']:,.0f}",
            f"  Avg NRR: {s['avg_nrr']}%",
            f"  Avg GRR: {s['avg_grr']}%",
            f"  Total New Logo: ${s['total_new_logo']:,.0f}",
            f"  Total Expansion: ${s['total_expansion']:,.0f}",
            f"  Total Churned: ${s['total_churned']:,.0f}",
        ])

    lines.append("")
    lines.append("PERIOD DETAIL")
    for p in results["period_results"]:
        lines.append(f"\n  {p['period']}")
        lines.append(f"    Opening: ${p['opening_arr']:,.0f} -> Closing: ${p['closing_arr']:,.0f}")
        lines.append(f"    + New Logo: ${p['new_logo_arr']:,.0f}")
        lines.append(f"    + Expansion: ${p['expansion_arr']:,.0f} ({p['expansion_rate_pct']}%)")
        lines.append(f"    - Contraction: ${p['contraction_arr']:,.0f} ({p['contraction_rate_pct']}%)")
        lines.append(f"    - Churn: ${p['churned_arr']:,.0f} ({p['churn_rate_pct']}%)")
        lines.append(f"    = Net New: ${p['net_new_arr']:,.0f}")
        lines.append(f"    NRR: {p['nrr_pct']}% ({p['nrr_benchmark']})")
        lines.append(f"    GRR: {p['grr_pct']}% ({p['grr_benchmark']})")

    if results["risk_signals"]:
        lines.append("")
        lines.append("RISK SIGNALS")
        for r in results["risk_signals"]:
            lines.append(f"  [{r['severity'].upper()}] {r['signal']}")
            lines.append(f"    Action: {r['action']}")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze ARR waterfall with NRR/GRR and trend detection")
    parser.add_argument("--input", required=True, help="Path to JSON revenue data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_revenue(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
