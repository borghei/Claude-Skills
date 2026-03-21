#!/usr/bin/env python3
"""
Creative Fatigue Detector

Analyzes ad performance trends to detect creative fatigue
and recommend refresh timing.

Usage:
    python creative_fatigue_detector.py campaign_data.json
    python creative_fatigue_detector.py campaign_data.json --json
    python creative_fatigue_detector.py --sample

Input JSON:
{
    "campaign": "Q1 Brand Campaign",
    "platform": "meta",
    "weekly_data": [
        {"week": "2026-01-06", "impressions": 50000, "clicks": 800, "conversions": 25, "spend": 1200, "frequency": 1.8}
    ]
}
"""

import argparse
import json
import sys
from pathlib import Path

FATIGUE_THRESHOLDS = {
    "ctr_decline_pct": 20,
    "frequency_display": 3,
    "frequency_retargeting": 5,
    "cpa_increase_pct": 15,
    "engagement_decline_pct": 30,
    "weeks_without_refresh": 3,
}

SAMPLE = {
    "campaign": "Q1 SaaS Demo Campaign",
    "platform": "meta",
    "campaign_type": "conversion",
    "weekly_data": [
        {"week": "2026-01-06", "impressions": 50000, "clicks": 900, "conversions": 28, "spend": 1400, "frequency": 1.5},
        {"week": "2026-01-13", "impressions": 52000, "clicks": 870, "conversions": 26, "spend": 1450, "frequency": 1.8},
        {"week": "2026-01-20", "impressions": 55000, "clicks": 820, "conversions": 24, "spend": 1500, "frequency": 2.1},
        {"week": "2026-01-27", "impressions": 53000, "clicks": 750, "conversions": 20, "spend": 1480, "frequency": 2.5},
        {"week": "2026-02-03", "impressions": 51000, "clicks": 680, "conversions": 17, "spend": 1520, "frequency": 2.9},
        {"week": "2026-02-10", "impressions": 49000, "clicks": 610, "conversions": 14, "spend": 1550, "frequency": 3.3},
    ],
}


def detect_fatigue(data: dict) -> dict:
    weekly = data.get("weekly_data", [])
    if len(weekly) < 2:
        return {"error": "Need at least 2 weeks of data"}

    # Calculate metrics per week
    metrics = []
    for w in weekly:
        imp = w.get("impressions", 0)
        clicks = w.get("clicks", 0)
        conv = w.get("conversions", 0)
        spend = w.get("spend", 0)

        ctr = (clicks / imp * 100) if imp > 0 else 0
        cvr = (conv / clicks * 100) if clicks > 0 else 0
        cpa = spend / conv if conv > 0 else 0

        metrics.append({
            "week": w["week"],
            "ctr": round(ctr, 2),
            "cvr": round(cvr, 2),
            "cpa": round(cpa, 2),
            "frequency": w.get("frequency", 0),
            "impressions": imp,
            "clicks": clicks,
            "conversions": conv,
            "spend": spend,
        })

    # Detect trends
    first = metrics[0]
    last = metrics[-1]

    ctr_change = ((last["ctr"] - first["ctr"]) / first["ctr"] * 100) if first["ctr"] > 0 else 0
    cpa_change = ((last["cpa"] - first["cpa"]) / first["cpa"] * 100) if first["cpa"] > 0 else 0
    cvr_change = ((last["cvr"] - first["cvr"]) / first["cvr"] * 100) if first["cvr"] > 0 else 0

    signals = []
    severity = "none"

    # CTR decline
    if ctr_change < -FATIGUE_THRESHOLDS["ctr_decline_pct"]:
        signals.append({
            "signal": "CTR declining",
            "detail": f"CTR dropped {abs(ctr_change):.1f}% ({first['ctr']}% -> {last['ctr']}%)",
            "severity": "high",
        })
        severity = "high"
    elif ctr_change < -10:
        signals.append({
            "signal": "CTR softening",
            "detail": f"CTR dropped {abs(ctr_change):.1f}%",
            "severity": "medium",
        })
        if severity != "high":
            severity = "medium"

    # Frequency
    max_freq = max(m["frequency"] for m in metrics)
    campaign_type = data.get("campaign_type", "conversion")
    freq_threshold = FATIGUE_THRESHOLDS["frequency_retargeting"] if campaign_type == "retargeting" else FATIGUE_THRESHOLDS["frequency_display"]

    if max_freq > freq_threshold:
        signals.append({
            "signal": "Frequency too high",
            "detail": f"Frequency reached {max_freq:.1f} (threshold: {freq_threshold})",
            "severity": "high",
        })
        severity = "high"
    elif max_freq > freq_threshold * 0.7:
        signals.append({
            "signal": "Frequency approaching limit",
            "detail": f"Frequency at {max_freq:.1f} (threshold: {freq_threshold})",
            "severity": "medium",
        })

    # CPA increase
    if cpa_change > FATIGUE_THRESHOLDS["cpa_increase_pct"]:
        signals.append({
            "signal": "CPA increasing",
            "detail": f"CPA up {cpa_change:.1f}% (${first['cpa']:.0f} -> ${last['cpa']:.0f})",
            "severity": "high",
        })
        severity = "high"

    # Weeks of decline
    consecutive_ctr_decline = 0
    for i in range(1, len(metrics)):
        if metrics[i]["ctr"] < metrics[i-1]["ctr"]:
            consecutive_ctr_decline += 1
        else:
            consecutive_ctr_decline = 0

    if consecutive_ctr_decline >= FATIGUE_THRESHOLDS["weeks_without_refresh"]:
        signals.append({
            "signal": "Sustained decline",
            "detail": f"{consecutive_ctr_decline} consecutive weeks of CTR decline",
            "severity": "critical",
        })
        severity = "critical"

    # Recommendations
    recs = []
    if severity in ("high", "critical"):
        recs.append("REFRESH CREATIVE NOW: Launch 3-5 new creative variants immediately.")
        recs.append("Preserve the winning pattern (hook type, emotional driver) but change angle and visuals.")
        recs.append("Test new formats: if using static images, try video. If using video, try carousel.")
    elif severity == "medium":
        recs.append("Prepare new creative variants. Fatigue signals are emerging.")
        recs.append("Begin A/B testing new angles alongside current creative.")
    else:
        recs.append("Creative is performing steadily. Monitor weekly and prepare refresh for 2-4 weeks out.")

    if max_freq > freq_threshold:
        recs.append("Expand audience targeting to reduce frequency.")

    return {
        "campaign": data.get("campaign", "Unknown"),
        "platform": data.get("platform", "unknown"),
        "weeks_analyzed": len(metrics),
        "fatigue_severity": severity,
        "signals": signals,
        "trend_summary": {
            "ctr_change_pct": round(ctr_change, 1),
            "cpa_change_pct": round(cpa_change, 1),
            "cvr_change_pct": round(cvr_change, 1),
            "max_frequency": round(max_freq, 1),
            "consecutive_ctr_decline_weeks": consecutive_ctr_decline,
        },
        "weekly_metrics": metrics,
        "recommendations": recs,
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 60, "  CREATIVE FATIGUE DETECTOR", "=" * 60]
    sev_label = {"none": "No Fatigue", "medium": "Early Warning", "high": "Fatigue Detected", "critical": "Critical Fatigue"}
    lines.append(f"\n  Campaign: {result['campaign']} ({result['platform']})")
    lines.append(f"  Status: {sev_label.get(result['fatigue_severity'], result['fatigue_severity'])}")

    ts = result["trend_summary"]
    lines.append(f"  CTR: {ts['ctr_change_pct']:+.1f}% | CPA: {ts['cpa_change_pct']:+.1f}% | Max Freq: {ts['max_frequency']}")

    if result["signals"]:
        lines.append(f"\n  Fatigue Signals:")
        for s in result["signals"]:
            icon = {"low": "~", "medium": "!", "high": "!!", "critical": "X"}
            lines.append(f"    [{icon.get(s['severity'], '?')}] {s['signal']}: {s['detail']}")

    lines.append(f"\n  Weekly Trend:")
    lines.append(f"  {'Week':<12} {'CTR%':<7} {'CVR%':<7} {'CPA':<8} {'Freq'}")
    for m in result["weekly_metrics"]:
        lines.append(f"  {m['week']:<12} {m['ctr']:<7} {m['cvr']:<7} ${m['cpa']:<7.0f} {m['frequency']}")

    lines.append(f"\n  Recommendations:")
    for r in result["recommendations"]:
        lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Detect ad creative fatigue from performance trends.")
    parser.add_argument("file", nargs="?")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    if args.sample:
        data = SAMPLE
    elif args.file:
        try:
            data = json.loads(Path(args.file).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = detect_fatigue(data)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
