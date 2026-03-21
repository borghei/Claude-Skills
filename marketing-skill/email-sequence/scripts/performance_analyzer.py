#!/usr/bin/env python3
"""
Email Sequence Performance Analyzer

Analyzes email sequence metrics against industry benchmarks,
identifies bottlenecks, and recommends optimizations.

Usage:
    python performance_analyzer.py metrics.json
    python performance_analyzer.py metrics.json --json
    python performance_analyzer.py --sample

Input JSON format:
{
    "sequence_name": "Welcome Onboarding",
    "sequence_type": "welcome",
    "emails": [
        {
            "position": 1, "subject": "Welcome", "day": 0,
            "sent": 1000, "delivered": 980, "opened": 620,
            "clicked": 180, "converted": 45, "unsubscribed": 3
        }
    ]
}
"""

import argparse
import json
import sys
from pathlib import Path

BENCHMARKS = {
    "welcome": {"open": (50, 70), "click": (10, 20), "conversion": (5, 15), "unsub": 0.5},
    "nurture": {"open": (25, 40), "click": (3, 8), "conversion": (1, 3), "unsub": 0.3},
    "re_engagement": {"open": (15, 25), "click": (2, 5), "conversion": (3, 8), "unsub": 3.0},
    "trial_expiration": {"open": (40, 60), "click": (8, 15), "conversion": (10, 25), "unsub": 0.5},
    "post_purchase": {"open": (40, 55), "click": (5, 12), "conversion": (2, 8), "unsub": 0.3},
}

SAMPLE = {
    "sequence_name": "SaaS Welcome Onboarding",
    "sequence_type": "welcome",
    "emails": [
        {"position": 1, "subject": "Welcome to Acme", "day": 0, "sent": 1000, "delivered": 985, "opened": 620, "clicked": 180, "converted": 45, "unsubscribed": 3},
        {"position": 2, "subject": "The one feature", "day": 1, "sent": 982, "delivered": 975, "opened": 480, "clicked": 120, "converted": 30, "unsubscribed": 2},
        {"position": 3, "subject": "How Stripe did it", "day": 3, "sent": 950, "delivered": 945, "opened": 350, "clicked": 75, "converted": 15, "unsubscribed": 4},
        {"position": 4, "subject": "Quick question", "day": 5, "sent": 931, "delivered": 925, "opened": 300, "clicked": 50, "converted": 8, "unsubscribed": 3},
        {"position": 5, "subject": "Things you missed", "day": 7, "sent": 920, "delivered": 915, "opened": 280, "clicked": 60, "converted": 12, "unsubscribed": 5},
        {"position": 6, "subject": "Trial halfway done", "day": 10, "sent": 903, "delivered": 898, "opened": 380, "clicked": 95, "converted": 25, "unsubscribed": 3},
        {"position": 7, "subject": "Last day", "day": 13, "sent": 870, "delivered": 865, "opened": 420, "clicked": 110, "converted": 35, "unsubscribed": 8},
    ],
}


def pct(num, den):
    return round(num / den * 100, 2) if den > 0 else 0.0


def analyze(data: dict) -> dict:
    seq_type = data.get("sequence_type", "welcome")
    bench = BENCHMARKS.get(seq_type, BENCHMARKS["welcome"])
    emails = data.get("emails", [])

    result = {
        "sequence_name": data.get("sequence_name", "Unnamed"),
        "sequence_type": seq_type,
        "email_count": len(emails),
        "email_metrics": [],
        "aggregate": {},
        "bottlenecks": [],
        "health_signals": [],
        "recommendations": [],
    }

    totals = {"sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "converted": 0, "unsub": 0}

    for email in emails:
        sent = email.get("sent", 0)
        delivered = email.get("delivered", sent)
        opened = email.get("opened", 0)
        clicked = email.get("clicked", 0)
        converted = email.get("converted", 0)
        unsub = email.get("unsubscribed", 0)

        open_r = pct(opened, delivered)
        click_r = pct(clicked, delivered)
        conv_r = pct(converted, delivered)
        unsub_r = pct(unsub, delivered)
        ctr = pct(clicked, opened) if opened > 0 else 0

        em = {
            "position": email.get("position"),
            "subject": email.get("subject", ""),
            "day": email.get("day", 0),
            "open_rate": open_r,
            "click_rate": click_r,
            "conversion_rate": conv_r,
            "unsubscribe_rate": unsub_r,
            "click_to_open": ctr,
            "status": "healthy",
        }

        # Benchmark comparison
        if open_r < bench["open"][0]:
            em["status"] = "underperforming"
            em["issue"] = "Open rate below benchmark"
        if click_r < bench["click"][0]:
            em["status"] = "underperforming"
            em["issue"] = em.get("issue", "") + " | Click rate below benchmark"
        if unsub_r > bench["unsub"]:
            em["status"] = "warning"
            em["issue"] = em.get("issue", "") + " | High unsubscribe rate"

        result["email_metrics"].append(em)

        totals["sent"] += sent
        totals["delivered"] += delivered
        totals["opened"] += opened
        totals["clicked"] += clicked
        totals["converted"] += converted
        totals["unsub"] += unsub

    # Aggregate
    result["aggregate"] = {
        "total_sent": totals["sent"],
        "total_converted": totals["converted"],
        "overall_open_rate": pct(totals["opened"], totals["delivered"]),
        "overall_click_rate": pct(totals["clicked"], totals["delivered"]),
        "overall_conversion_rate": pct(totals["converted"], totals["delivered"]),
        "overall_unsubscribe_rate": pct(totals["unsub"], totals["delivered"]),
        "sequence_conversion_rate": pct(totals["converted"], emails[0].get("sent", 1)) if emails else 0,
    }

    # Bottleneck detection
    metrics = result["email_metrics"]
    if len(metrics) >= 2:
        # Find biggest open rate drop
        max_open_drop = 0
        max_open_drop_pos = 0
        for i in range(1, len(metrics)):
            drop = metrics[i-1]["open_rate"] - metrics[i]["open_rate"]
            if drop > max_open_drop:
                max_open_drop = drop
                max_open_drop_pos = metrics[i]["position"]

        if max_open_drop > 10:
            result["bottlenecks"].append({
                "type": "open_rate_drop",
                "at_email": max_open_drop_pos,
                "drop": round(max_open_drop, 1),
                "fix": "Improve subject line or check if previous email fatigued recipients",
            })

        # Find high-open low-click emails
        for m in metrics:
            if m["open_rate"] > 30 and m["click_to_open"] < 10:
                result["bottlenecks"].append({
                    "type": "high_open_low_click",
                    "at_email": m["position"],
                    "open_rate": m["open_rate"],
                    "cto": m["click_to_open"],
                    "fix": "Subject line works but body/CTA is weak. Rewrite body copy and simplify CTA.",
                })

    # Health signals
    agg = result["aggregate"]
    if agg["overall_open_rate"] >= bench["open"][1]:
        result["health_signals"].append({"signal": "Open rates above benchmark", "status": "positive"})
    elif agg["overall_open_rate"] < bench["open"][0]:
        result["health_signals"].append({"signal": "Open rates below benchmark", "status": "negative"})
        result["recommendations"].append("Improve subject lines. Test 3+ variants per email position.")

    if agg["overall_unsubscribe_rate"] > bench["unsub"] * 2:
        result["health_signals"].append({"signal": "High unsubscribe rate", "status": "negative"})
        result["recommendations"].append("Reduce sending frequency or improve content relevance.")

    # Decay analysis
    if len(metrics) >= 3:
        early_open = sum(m["open_rate"] for m in metrics[:2]) / 2
        late_open = sum(m["open_rate"] for m in metrics[-2:]) / 2
        decay = round(early_open - late_open, 1)
        if decay > 15:
            result["recommendations"].append(f"Open rate decays by {decay}pp across sequence. Add variety in angles and formats.")

    if not result["recommendations"]:
        result["recommendations"].append("Sequence is performing well. Continue A/B testing subject lines and CTAs.")

    return result


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 65, "  EMAIL SEQUENCE PERFORMANCE ANALYZER", "=" * 65]
    lines.append(f"\n  {result['sequence_name']} ({result['sequence_type']})")
    agg = result["aggregate"]
    lines.append(f"  Sent: {agg['total_sent']} | Converted: {agg['total_converted']} | Seq. Conv: {agg['sequence_conversion_rate']}%")
    lines.append(f"  Open: {agg['overall_open_rate']}% | Click: {agg['overall_click_rate']}% | Unsub: {agg['overall_unsubscribe_rate']}%")

    lines.append(f"\n  {'#':<4} {'Day':<5} {'Open%':<8} {'Click%':<8} {'Conv%':<8} {'CTO%':<7} {'Status':<15} Subject")
    lines.append(f"  {'-'*80}")
    for m in result["email_metrics"]:
        lines.append(f"  {m['position']:<4} {m['day']:<5} {m['open_rate']:<8} {m['click_rate']:<8} {m['conversion_rate']:<8} {m['click_to_open']:<7} {m['status']:<15} {m['subject'][:25]}")

    if result["bottlenecks"]:
        lines.append(f"\n  Bottlenecks:")
        for b in result["bottlenecks"]:
            lines.append(f"    Email {b['at_email']}: {b['type']} -- {b['fix']}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            lines.append(f"    {i}. {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze email sequence performance metrics.")
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

    result = analyze(data)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
