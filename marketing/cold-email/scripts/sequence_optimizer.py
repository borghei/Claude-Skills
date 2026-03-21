#!/usr/bin/env python3
"""
Cold Email Sequence Optimizer

Analyzes cold email sequence performance data and recommends
optimizations based on industry benchmarks and best practices.

Usage:
    python sequence_optimizer.py sequence_data.json
    python sequence_optimizer.py sequence_data.json --json
    python sequence_optimizer.py --sample

Input JSON format:
{
    "sequence_name": "Q1 Outbound",
    "emails": [
        {
            "position": 1,
            "subject": "quick question",
            "day": 1,
            "sent": 500,
            "delivered": 485,
            "opened": 180,
            "replied": 12,
            "bounced": 15,
            "unsubscribed": 2
        }
    ]
}
"""

import argparse
import json
import sys
from pathlib import Path

# --- Benchmarks (2025-2026 cold email industry data) ---
BENCHMARKS = {
    "open_rate": {"poor": 15, "average": 25, "good": 40, "excellent": 55},
    "reply_rate": {"poor": 1, "average": 2.5, "good": 5, "excellent": 8},
    "bounce_rate": {"excellent": 1, "good": 2, "warning": 3, "critical": 5},
    "unsubscribe_rate": {"excellent": 0.1, "good": 0.3, "warning": 0.5, "critical": 1.0},
    "spam_complaint_rate": {"threshold": 0.10},
    "deliverability_rate": {"excellent": 98, "good": 95, "warning": 90, "critical": 85},
}

OPTIMAL_CADENCE = [1, 4, 9, 16, 25, 35]  # days
OPTIMAL_SEQUENCE_LENGTH = (4, 6)  # emails

SAMPLE_DATA = {
    "sequence_name": "Q1 Enterprise Outbound",
    "emails": [
        {"position": 1, "subject": "quick question", "day": 1, "sent": 500, "delivered": 485, "opened": 180, "replied": 12, "bounced": 15, "unsubscribed": 2},
        {"position": 2, "subject": "saw your hiring post", "day": 4, "sent": 484, "delivered": 478, "opened": 140, "replied": 8, "bounced": 6, "unsubscribed": 1},
        {"position": 3, "subject": "competitor case study", "day": 9, "sent": 475, "delivered": 470, "opened": 95, "replied": 5, "bounced": 5, "unsubscribed": 3},
        {"position": 4, "subject": "one more thing", "day": 16, "sent": 467, "delivered": 462, "opened": 65, "replied": 3, "bounced": 5, "unsubscribed": 2},
        {"position": 5, "subject": "closing the loop", "day": 25, "sent": 460, "delivered": 455, "opened": 80, "replied": 6, "bounced": 5, "unsubscribed": 4},
    ],
}


def rate(numerator: int, denominator: int) -> float:
    """Calculate percentage rate safely."""
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def classify(value: float, benchmarks: dict, higher_is_better: bool = True) -> str:
    """Classify a value against benchmarks."""
    if higher_is_better:
        if value >= benchmarks.get("excellent", 999):
            return "excellent"
        elif value >= benchmarks.get("good", 999):
            return "good"
        elif value >= benchmarks.get("average", 0):
            return "average"
        else:
            return "poor"
    else:
        if value <= benchmarks.get("excellent", 0):
            return "excellent"
        elif value <= benchmarks.get("good", 0):
            return "good"
        elif value <= benchmarks.get("warning", 999):
            return "warning"
        else:
            return "critical"


def analyze_sequence(data: dict) -> dict:
    """Analyze a cold email sequence and generate recommendations."""
    emails = data.get("emails", [])
    if not emails:
        return {"error": "No email data provided"}

    results = {
        "sequence_name": data.get("sequence_name", "Unnamed"),
        "email_count": len(emails),
        "email_analysis": [],
        "sequence_metrics": {},
        "diagnoses": [],
        "recommendations": [],
        "cadence_analysis": {},
        "overall_health": "",
    }

    # --- Per-email analysis ---
    total_sent = 0
    total_delivered = 0
    total_opened = 0
    total_replied = 0
    total_bounced = 0
    total_unsubscribed = 0

    for email in emails:
        sent = email.get("sent", 0)
        delivered = email.get("delivered", sent)
        opened = email.get("opened", 0)
        replied = email.get("replied", 0)
        bounced = email.get("bounced", 0)
        unsub = email.get("unsubscribed", 0)

        open_rate_val = rate(opened, delivered)
        reply_rate_val = rate(replied, delivered)
        bounce_rate_val = rate(bounced, sent)
        delivery_rate_val = rate(delivered, sent)

        email_result = {
            "position": email.get("position", 0),
            "subject": email.get("subject", ""),
            "day": email.get("day", 0),
            "metrics": {
                "sent": sent,
                "delivered": delivered,
                "open_rate": open_rate_val,
                "reply_rate": reply_rate_val,
                "bounce_rate": bounce_rate_val,
                "delivery_rate": delivery_rate_val,
            },
            "classifications": {
                "open_rate": classify(open_rate_val, BENCHMARKS["open_rate"]),
                "reply_rate": classify(reply_rate_val, BENCHMARKS["reply_rate"]),
                "bounce_rate": classify(bounce_rate_val, BENCHMARKS["bounce_rate"], higher_is_better=False),
            },
        }
        results["email_analysis"].append(email_result)

        total_sent += sent
        total_delivered += delivered
        total_opened += opened
        total_replied += replied
        total_bounced += bounced
        total_unsubscribed += unsub

    # --- Sequence-level metrics ---
    results["sequence_metrics"] = {
        "total_sent": total_sent,
        "total_delivered": total_delivered,
        "total_replies": total_replied,
        "overall_open_rate": rate(total_opened, total_delivered),
        "overall_reply_rate": rate(total_replied, total_delivered),
        "overall_bounce_rate": rate(total_bounced, total_sent),
        "overall_delivery_rate": rate(total_delivered, total_sent),
        "overall_unsubscribe_rate": rate(total_unsubscribed, total_delivered),
        "reply_per_sequence": round(total_replied / max(emails[0].get("sent", 1), 1) * 100, 2) if emails else 0,
    }

    sm = results["sequence_metrics"]

    # --- Cadence analysis ---
    days = [e.get("day", 0) for e in emails]
    gaps = [days[i+1] - days[i] for i in range(len(days)-1)] if len(days) > 1 else []
    is_escalating = all(gaps[i] <= gaps[i+1] for i in range(len(gaps)-1)) if len(gaps) > 1 else True

    results["cadence_analysis"] = {
        "send_days": days,
        "gaps_between_emails": gaps,
        "is_escalating_gaps": is_escalating,
        "total_sequence_days": max(days) - min(days) if days else 0,
        "recommended_cadence": OPTIMAL_CADENCE[:len(emails)],
    }

    # --- Diagnoses ---
    # Open rate diagnosis
    if sm["overall_open_rate"] < BENCHMARKS["open_rate"]["poor"]:
        results["diagnoses"].append({
            "issue": "Very low open rates",
            "likely_cause": "Subject lines or deliverability",
            "severity": "critical",
        })
        results["recommendations"].append("Test new subject line patterns: 2-4 words, internal-email style, no spam triggers.")
        results["recommendations"].append("Check SPF/DKIM/DMARC authentication and sending domain reputation.")
    elif sm["overall_open_rate"] < BENCHMARKS["open_rate"]["average"]:
        results["diagnoses"].append({
            "issue": "Below-average open rates",
            "likely_cause": "Subject lines need improvement",
            "severity": "warning",
        })
        results["recommendations"].append("A/B test subject lines with 100+ sends per variant.")

    # Reply rate diagnosis
    if sm["overall_reply_rate"] < BENCHMARKS["reply_rate"]["poor"]:
        results["diagnoses"].append({
            "issue": "Very low reply rates despite opens",
            "likely_cause": "Email body, CTA, or audience mismatch",
            "severity": "critical",
        })
        results["recommendations"].append("Rewrite with stronger relevance and lower-friction CTA (question, not statement).")
        results["recommendations"].append("Verify ICP targeting -- wrong audience produces opens but not replies.")

    # Bounce rate
    if sm["overall_bounce_rate"] > BENCHMARKS["bounce_rate"]["critical"]:
        results["diagnoses"].append({
            "issue": "Critical bounce rate",
            "likely_cause": "List quality or email verification",
            "severity": "critical",
        })
        results["recommendations"].append("URGENT: Verify all email addresses before sending. Bounce rate above 5% damages domain reputation.")
    elif sm["overall_bounce_rate"] > BENCHMARKS["bounce_rate"]["warning"]:
        results["diagnoses"].append({
            "issue": "Elevated bounce rate",
            "likely_cause": "Some unverified addresses",
            "severity": "warning",
        })
        results["recommendations"].append("Run email verification on your list. Target under 2% bounce rate.")

    # Cadence
    if not is_escalating and len(gaps) > 1:
        results["recommendations"].append("Use escalating gaps between emails (e.g., +3, +5, +7, +9, +10 days) to avoid fatigue.")

    # Sequence length
    if len(emails) < OPTIMAL_SEQUENCE_LENGTH[0]:
        results["recommendations"].append(f"Sequence is short ({len(emails)} emails). Most replies come from follow-ups. Add {OPTIMAL_SEQUENCE_LENGTH[0] - len(emails)} more emails.")
    elif len(emails) > OPTIMAL_SEQUENCE_LENGTH[1]:
        results["recommendations"].append(f"Sequence is long ({len(emails)} emails). Consider trimming to {OPTIMAL_SEQUENCE_LENGTH[1]} to avoid fatigue.")

    # Open rate decay
    open_rates = [e["metrics"]["open_rate"] for e in results["email_analysis"]]
    if len(open_rates) >= 3:
        decay = open_rates[0] - open_rates[-1]
        if decay > 20:
            results["diagnoses"].append({
                "issue": "Steep open rate decay across sequence",
                "likely_cause": "Recipients losing interest or marking as spam",
                "severity": "warning",
            })
            results["recommendations"].append("Each follow-up needs a distinct angle. Avoid 'just checking in' patterns.")

    # Breakup email check
    last_email = results["email_analysis"][-1]
    if last_email["metrics"]["reply_rate"] > results["email_analysis"][-2]["metrics"]["reply_rate"] if len(results["email_analysis"]) > 1 else False:
        results["diagnoses"].append({
            "issue": "Breakup email has higher reply rate",
            "likely_cause": "Urgency effect -- 'last chance' psychology works",
            "severity": "positive",
        })

    # --- Overall health ---
    critical_count = sum(1 for d in results["diagnoses"] if d["severity"] == "critical")
    warning_count = sum(1 for d in results["diagnoses"] if d["severity"] == "warning")

    if critical_count > 0:
        results["overall_health"] = "CRITICAL -- Immediate attention needed"
    elif warning_count > 1:
        results["overall_health"] = "NEEDS IMPROVEMENT -- Several areas to optimize"
    elif warning_count == 1:
        results["overall_health"] = "FAIR -- Minor optimizations recommended"
    else:
        results["overall_health"] = "HEALTHY -- Sequence performing well"

    return results


def format_human(result: dict) -> str:
    """Format result for human reading."""
    lines = []
    lines.append("\n" + "=" * 65)
    lines.append("  COLD EMAIL SEQUENCE OPTIMIZER")
    lines.append("=" * 65)
    lines.append(f"\n  Sequence: {result['sequence_name']}")
    lines.append(f"  Health: {result['overall_health']}")

    sm = result["sequence_metrics"]
    lines.append(f"\n  Sequence Metrics:")
    lines.append(f"    Total Sent: {sm['total_sent']} | Delivered: {sm['total_delivered']}")
    lines.append(f"    Overall Open Rate: {sm['overall_open_rate']}%")
    lines.append(f"    Overall Reply Rate: {sm['overall_reply_rate']}%")
    lines.append(f"    Overall Bounce Rate: {sm['overall_bounce_rate']}%")
    lines.append(f"    Sequence Reply Rate: {sm['reply_per_sequence']}% (replies / initial sends)")

    lines.append(f"\n  Per-Email Breakdown:")
    lines.append(f"    {'#':<4} {'Day':<6} {'Open%':<8} {'Reply%':<8} {'Bounce%':<9} {'Subject'}")
    lines.append(f"    {'-'*4} {'-'*5} {'-'*7} {'-'*7} {'-'*8} {'-'*20}")
    for e in result["email_analysis"]:
        m = e["metrics"]
        lines.append(
            f"    {e['position']:<4} {e['day']:<6} {m['open_rate']:<8} {m['reply_rate']:<8} {m['bounce_rate']:<9} {e['subject'][:30]}"
        )

    ca = result["cadence_analysis"]
    lines.append(f"\n  Cadence:")
    lines.append(f"    Current: Days {ca['send_days']} (gaps: {ca['gaps_between_emails']})")
    lines.append(f"    Recommended: Days {ca['recommended_cadence']}")
    lines.append(f"    Escalating gaps: {'Yes' if ca['is_escalating_gaps'] else 'No (should be escalating)'}")

    if result["diagnoses"]:
        lines.append(f"\n  Diagnoses:")
        for d in result["diagnoses"]:
            icon = {"critical": "X", "warning": "!", "positive": "+"}
            lines.append(f"    [{icon.get(d['severity'], '?')}] {d['issue']}")
            lines.append(f"        Cause: {d['likely_cause']}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            lines.append(f"    {i}. {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze cold email sequence performance and recommend optimizations."
    )
    parser.add_argument("file", nargs="?", help="JSON file with sequence data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument("--sample", action="store_true", help="Run with sample data")
    args = parser.parse_args()

    if args.sample:
        data = SAMPLE_DATA
    elif args.file:
        try:
            data = json.loads(Path(args.file).read_text())
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = analyze_sequence(data)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
