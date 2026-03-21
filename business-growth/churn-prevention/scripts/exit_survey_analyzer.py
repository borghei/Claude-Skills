#!/usr/bin/env python3
"""
Exit Survey Analyzer

Analyze exit survey responses to identify churn patterns, save offer
effectiveness, and systemic issues. Produces reason distribution, save
rate analysis, trend detection, and competitive intelligence.

Usage:
    python exit_survey_analyzer.py survey_data.json
    python exit_survey_analyzer.py survey_data.json --json
    python exit_survey_analyzer.py survey_data.json --period "Q1 2026"
"""

import argparse
import json
import sys
from collections import defaultdict


EXIT_REASONS = ["PRICE", "LOW_USAGE", "MISSING_FEATURE", "COMPETITOR",
                "PROJECT_END", "COMPLEXITY", "TESTING", "OTHER"]

BENCHMARKS = {
    "save_rate_good": 15.0,
    "save_rate_excellent": 25.0,
    "survey_completion_good": 70.0,
    "survey_completion_excellent": 90.0,
    "reason_concentration_warning": 30.0,
    "reason_concentration_critical": 40.0,
}


def analyze_surveys(data: dict, period: str) -> dict:
    """Analyze exit survey data."""
    responses = data.get("responses", [])
    if not responses:
        return {"error": "No survey response data provided."}

    total_cancel_attempts = data.get("total_cancel_attempts", len(responses))
    total_responses = len(responses)

    # Reason distribution
    by_reason = defaultdict(lambda: {
        "count": 0, "saved": 0, "mrr_at_risk": 0.0, "mrr_saved": 0.0,
        "competitors_mentioned": defaultdict(int), "features_requested": defaultdict(int),
    })

    for r in responses:
        reason = r.get("reason", "OTHER")
        if reason not in EXIT_REASONS:
            reason = "OTHER"

        by_reason[reason]["count"] += 1
        by_reason[reason]["mrr_at_risk"] += r.get("mrr", 0)

        if r.get("saved", False):
            by_reason[reason]["saved"] += 1
            by_reason[reason]["mrr_saved"] += r.get("mrr", 0)

        if reason == "COMPETITOR" and r.get("competitor_name"):
            by_reason[reason]["competitors_mentioned"][r["competitor_name"]] += 1

        if reason == "MISSING_FEATURE" and r.get("feature_name"):
            by_reason[reason]["features_requested"][r["feature_name"]] += 1

    # Build reason breakdown
    reason_breakdown = []
    total_saved = sum(d["saved"] for d in by_reason.values())
    total_mrr_risk = sum(d["mrr_at_risk"] for d in by_reason.values())
    total_mrr_saved = sum(d["mrr_saved"] for d in by_reason.values())

    for reason in EXIT_REASONS:
        stats = by_reason[reason]
        if stats["count"] == 0:
            continue
        pct = (stats["count"] / total_responses * 100) if total_responses > 0 else 0
        save_rate = (stats["saved"] / stats["count"] * 100) if stats["count"] > 0 else 0
        reason_breakdown.append({
            "reason": reason,
            "count": stats["count"],
            "percentage": round(pct, 1),
            "saved": stats["saved"],
            "save_rate_pct": round(save_rate, 1),
            "mrr_at_risk": round(stats["mrr_at_risk"], 2),
            "mrr_saved": round(stats["mrr_saved"], 2),
        })

    reason_breakdown.sort(key=lambda x: x["count"], reverse=True)

    # Competitive intelligence
    all_competitors = defaultdict(int)
    for stats in by_reason.values():
        for comp, cnt in stats["competitors_mentioned"].items():
            all_competitors[comp] += cnt

    top_competitors = sorted(all_competitors.items(), key=lambda x: x[1], reverse=True)[:5]

    # Feature gaps
    all_features = defaultdict(int)
    for stats in by_reason.values():
        for feat, cnt in stats["features_requested"].items():
            all_features[feat] += cnt

    top_features = sorted(all_features.items(), key=lambda x: x[1], reverse=True)[:5]

    # Overall metrics
    overall_save_rate = (total_saved / total_responses * 100) if total_responses > 0 else 0
    survey_completion = (total_responses / total_cancel_attempts * 100) if total_cancel_attempts > 0 else 0

    # Alerts
    alerts = _generate_alerts(reason_breakdown, overall_save_rate, survey_completion)

    return {
        "period": period,
        "summary": {
            "total_cancel_attempts": total_cancel_attempts,
            "survey_responses": total_responses,
            "survey_completion_rate_pct": round(survey_completion, 1),
            "total_saved": total_saved,
            "overall_save_rate_pct": round(overall_save_rate, 1),
            "total_mrr_at_risk": round(total_mrr_risk, 2),
            "total_mrr_saved": round(total_mrr_saved, 2),
        },
        "reason_breakdown": reason_breakdown,
        "competitive_intelligence": {
            "top_competitors": [{"name": c, "mentions": n} for c, n in top_competitors],
        },
        "feature_gaps": {
            "top_requested_features": [{"feature": f, "mentions": n} for f, n in top_features],
        },
        "alerts": alerts,
        "benchmarks": BENCHMARKS,
    }


def _generate_alerts(reasons: list, save_rate: float, completion: float) -> list:
    """Generate alerts based on analysis."""
    alerts = []

    if completion < BENCHMARKS["survey_completion_good"]:
        alerts.append({
            "severity": "HIGH",
            "type": "low_completion",
            "message": f"Survey completion rate is {completion:.1f}%. Target is {BENCHMARKS['survey_completion_good']}%+. Make the single-question survey required before showing save offers.",
        })

    if save_rate < 5:
        alerts.append({
            "severity": "CRITICAL",
            "type": "low_save_rate",
            "message": f"Overall save rate is {save_rate:.1f}%. Offers likely do not match exit reasons. Rebuild reason-to-offer mapping.",
        })
    elif save_rate < BENCHMARKS["save_rate_good"]:
        alerts.append({
            "severity": "HIGH",
            "type": "below_benchmark_save_rate",
            "message": f"Save rate {save_rate:.1f}% is below benchmark of {BENCHMARKS['save_rate_good']}%. Test stronger offers.",
        })

    for r in reasons:
        if r["percentage"] > BENCHMARKS["reason_concentration_critical"]:
            alerts.append({
                "severity": "CRITICAL",
                "type": "reason_concentration",
                "message": f"'{r['reason']}' accounts for {r['percentage']}% of cancellations. This indicates a systemic issue requiring product or leadership escalation.",
            })
        elif r["percentage"] > BENCHMARKS["reason_concentration_warning"]:
            alerts.append({
                "severity": "HIGH",
                "type": "reason_concentration",
                "message": f"'{r['reason']}' accounts for {r['percentage']}% of cancellations. Monitor trend and investigate root cause.",
            })

        if r["save_rate_pct"] < 5 and r["reason"] != "TESTING" and r["count"] >= 5:
            alerts.append({
                "severity": "HIGH",
                "type": "ineffective_offer",
                "message": f"Save rate for '{r['reason']}' is only {r['save_rate_pct']}%. The current offer for this reason is not working.",
            })

    return alerts


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"EXIT SURVEY ANALYZER -- Period: {result['period']}")
    lines.append("=" * 60)

    s = result["summary"]
    lines.append(f"\n--- Summary ---")
    lines.append(f"Cancel Attempts:       {s['total_cancel_attempts']:>8d}")
    lines.append(f"Survey Responses:      {s['survey_responses']:>8d}")
    lines.append(f"Survey Completion:     {s['survey_completion_rate_pct']:>8.1f}%")
    lines.append(f"Customers Saved:       {s['total_saved']:>8d}")
    lines.append(f"Overall Save Rate:     {s['overall_save_rate_pct']:>8.1f}%")
    lines.append(f"MRR at Risk:           ${s['total_mrr_at_risk']:>10,.2f}")
    lines.append(f"MRR Saved:             ${s['total_mrr_saved']:>10,.2f}")

    lines.append(f"\n--- Reason Breakdown ---")
    lines.append(f"{'Reason':<18} {'Count':>6} {'%':>6} {'Saved':>6} {'Save%':>7} {'MRR Risk':>10}")
    for r in result["reason_breakdown"]:
        lines.append(
            f"{r['reason']:<18} {r['count']:>6d} {r['percentage']:>5.1f}% "
            f"{r['saved']:>6d} {r['save_rate_pct']:>6.1f}% ${r['mrr_at_risk']:>8,.0f}"
        )

    ci = result["competitive_intelligence"]
    if ci["top_competitors"]:
        lines.append(f"\n--- Top Competitors Mentioned ---")
        for c in ci["top_competitors"]:
            lines.append(f"  {c['name']}: {c['mentions']} mentions")

    fg = result["feature_gaps"]
    if fg["top_requested_features"]:
        lines.append(f"\n--- Top Requested Features ---")
        for f in fg["top_requested_features"]:
            lines.append(f"  {f['feature']}: {f['mentions']} mentions")

    if result["alerts"]:
        lines.append(f"\n--- Alerts ---")
        for a in result["alerts"]:
            lines.append(f"[{a['severity']}] {a['message']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze exit survey responses to identify churn patterns and save offer effectiveness."
    )
    parser.add_argument("input_file", help="JSON file with exit survey response data")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--period", default="current", help="Analysis period label (default: current)")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = analyze_surveys(data, args.period)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
