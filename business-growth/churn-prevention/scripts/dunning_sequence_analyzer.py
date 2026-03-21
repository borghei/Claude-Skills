#!/usr/bin/env python3
"""
Dunning Sequence Analyzer

Analyze dunning email sequence effectiveness and recommend retry timing
optimizations. Calculates recovery rates by failure reason, retry attempt,
and timing window.

Usage:
    python dunning_sequence_analyzer.py dunning_data.json
    python dunning_sequence_analyzer.py dunning_data.json --json
"""

import argparse
import json
import sys
from collections import defaultdict


FAILURE_REASONS = {
    "expired_card": {"recoverable": True, "typical_rate": 0.60},
    "insufficient_funds": {"recoverable": True, "typical_rate": 0.50},
    "bank_decline": {"recoverable": True, "typical_rate": 0.30},
    "account_closed": {"recoverable": False, "typical_rate": 0.05},
    "network_error": {"recoverable": True, "typical_rate": 0.85},
    "fraud_flag": {"recoverable": True, "typical_rate": 0.20},
    "unknown": {"recoverable": True, "typical_rate": 0.35},
}

OPTIMAL_RETRY_SCHEDULE = [
    {"retry": 1, "day": 3, "rationale": "Most card issues resolve within 72 hours"},
    {"retry": 2, "day": 7, "rationale": "Paycheck cycle alignment"},
    {"retry": 3, "day": 12, "rationale": "Second paycheck cycle"},
    {"retry": 4, "day": 18, "rationale": "Final attempt before service action"},
]


def analyze_dunning(data: dict) -> dict:
    """Analyze dunning sequence data."""
    payments = data.get("failed_payments", [])
    if not payments:
        return {"error": "No failed payment data provided."}

    total = len(payments)
    total_amount = sum(p.get("amount", 0) for p in payments)
    recovered_count = 0
    recovered_amount = 0.0

    # By failure reason
    by_reason = defaultdict(lambda: {"total": 0, "recovered": 0, "amount": 0.0, "recovered_amount": 0.0})
    # By retry attempt
    by_retry = defaultdict(lambda: {"attempts": 0, "recovered": 0})
    # Recovery timing
    recovery_days = []

    for p in payments:
        reason = p.get("failure_reason", "unknown")
        amount = p.get("amount", 0)
        retries = p.get("retry_attempts", [])

        by_reason[reason]["total"] += 1
        by_reason[reason]["amount"] += amount

        payment_recovered = False
        for i, retry in enumerate(retries):
            by_retry[i]["attempts"] += 1
            if retry.get("recovered", False) and not payment_recovered:
                payment_recovered = True
                recovered_count += 1
                recovered_amount += amount
                by_reason[reason]["recovered"] += 1
                by_reason[reason]["recovered_amount"] += amount
                by_retry[i]["recovered"] += 1
                recovery_days.append(retry.get("day", 0))

    # Build reason breakdown
    reason_breakdown = []
    for reason, stats in sorted(by_reason.items(), key=lambda x: x[1]["total"], reverse=True):
        rate = (stats["recovered"] / stats["total"] * 100) if stats["total"] > 0 else 0
        benchmark = FAILURE_REASONS.get(reason, {})
        typical = benchmark.get("typical_rate", 0.35) * 100
        reason_breakdown.append({
            "reason": reason,
            "total_failures": stats["total"],
            "recovered": stats["recovered"],
            "recovery_rate_pct": round(rate, 1),
            "amount_at_risk": round(stats["amount"], 2),
            "amount_recovered": round(stats["recovered_amount"], 2),
            "benchmark_recovery_pct": round(typical, 1),
            "vs_benchmark": "above" if rate > typical else "below" if rate < typical else "at",
            "recoverable": benchmark.get("recoverable", True),
        })

    # Build retry breakdown
    retry_breakdown = []
    for attempt in sorted(by_retry.keys()):
        stats = by_retry[attempt]
        rate = (stats["recovered"] / stats["attempts"] * 100) if stats["attempts"] > 0 else 0
        retry_breakdown.append({
            "attempt": attempt + 1,
            "total_attempts": stats["attempts"],
            "recovered": stats["recovered"],
            "recovery_rate_pct": round(rate, 1),
        })

    overall_rate = (recovered_count / total * 100) if total > 0 else 0
    avg_recovery_day = (sum(recovery_days) / len(recovery_days)) if recovery_days else 0

    # Recommendations
    recommendations = _generate_recommendations(overall_rate, reason_breakdown, retry_breakdown)

    return {
        "summary": {
            "total_failed_payments": total,
            "total_amount_at_risk": round(total_amount, 2),
            "recovered_count": recovered_count,
            "recovered_amount": round(recovered_amount, 2),
            "overall_recovery_rate_pct": round(overall_rate, 1),
            "average_recovery_day": round(avg_recovery_day, 1),
            "unrecovered_count": total - recovered_count,
            "unrecovered_amount": round(total_amount - recovered_amount, 2),
        },
        "by_failure_reason": reason_breakdown,
        "by_retry_attempt": retry_breakdown,
        "optimal_retry_schedule": OPTIMAL_RETRY_SCHEDULE,
        "recommendations": recommendations,
    }


def _generate_recommendations(overall_rate: float, reasons: list, retries: list) -> list:
    """Generate recommendations based on analysis."""
    recs = []

    if overall_rate < 20:
        recs.append({
            "priority": "CRITICAL",
            "area": "Overall recovery",
            "recommendation": "Recovery rate below 20% indicates dunning system is underperforming. Audit email delivery, retry schedule, and payment update UX.",
        })
    elif overall_rate < 35:
        recs.append({
            "priority": "HIGH",
            "area": "Overall recovery",
            "recommendation": "Recovery rate below benchmark (35%). Review retry timing and add in-app payment update prompts.",
        })

    for r in reasons:
        if r["reason"] == "expired_card" and r["recovery_rate_pct"] < 50:
            recs.append({
                "priority": "HIGH",
                "area": "Card updates",
                "recommendation": "Expired card recovery is low. Enable automatic card updater service on your payment processor (Stripe, Braintree, etc.).",
            })
        if r["reason"] == "insufficient_funds" and r["recovery_rate_pct"] < 40:
            recs.append({
                "priority": "MEDIUM",
                "area": "Retry timing",
                "recommendation": "Insufficient funds recovery is low. Ensure retries align with common paycheck dates (1st, 15th of month).",
            })

    if len(retries) < 4:
        recs.append({
            "priority": "MEDIUM",
            "area": "Retry attempts",
            "recommendation": f"Only {len(retries)} retry attempts configured. Best practice is 4 retries over 18 days before service action.",
        })

    recs.append({
        "priority": "MEDIUM",
        "area": "Dunning emails",
        "recommendation": "Ensure every dunning email links directly to the payment update page (not the dashboard). Include amount owed and card last 4 digits.",
    })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("DUNNING SEQUENCE ANALYZER")
    lines.append("=" * 60)

    s = result["summary"]
    lines.append(f"\n--- Summary ---")
    lines.append(f"Total Failed Payments:    {s['total_failed_payments']:>8d}")
    lines.append(f"Total Amount at Risk:     ${s['total_amount_at_risk']:>12,.2f}")
    lines.append(f"Recovered:                {s['recovered_count']:>8d}  (${s['recovered_amount']:>10,.2f})")
    lines.append(f"Unrecovered:              {s['unrecovered_count']:>8d}  (${s['unrecovered_amount']:>10,.2f})")
    lines.append(f"Overall Recovery Rate:    {s['overall_recovery_rate_pct']:>8.1f}%")
    lines.append(f"Avg Recovery Day:         {s['average_recovery_day']:>8.1f}")

    lines.append(f"\n--- By Failure Reason ---")
    lines.append(f"{'Reason':<20} {'Total':>6} {'Recovered':>10} {'Rate':>8} {'Benchmark':>10} {'Status':>8}")
    for r in result["by_failure_reason"]:
        lines.append(f"{r['reason']:<20} {r['total_failures']:>6d} {r['recovered']:>10d} {r['recovery_rate_pct']:>7.1f}% {r['benchmark_recovery_pct']:>9.1f}% {r['vs_benchmark']:>8}")

    lines.append(f"\n--- By Retry Attempt ---")
    lines.append(f"{'Attempt':>8} {'Tried':>8} {'Recovered':>10} {'Rate':>8}")
    for r in result["by_retry_attempt"]:
        lines.append(f"{r['attempt']:>8d} {r['total_attempts']:>8d} {r['recovered']:>10d} {r['recovery_rate_pct']:>7.1f}%")

    lines.append(f"\n--- Optimal Retry Schedule ---")
    for r in result["optimal_retry_schedule"]:
        lines.append(f"  Retry {r['retry']}: Day {r['day']:>2d} -- {r['rationale']}")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['area']}: {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze dunning email sequence effectiveness and recommend optimizations."
    )
    parser.add_argument("input_file", help="JSON file with failed payment and retry data")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

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

    result = analyze_dunning(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
