#!/usr/bin/env python3
"""Predict customer churn risk from health, engagement, and contract data.

Scores each customer's churn likelihood based on multiple weighted signals
including health score trends, support patterns, usage decline, NPS, and
contract timing. Outputs risk tiers with recommended interventions.

Usage:
    python churn_predictor.py --data customers.csv
    python churn_predictor.py --data customers.json --json
    python churn_predictor.py --data customers.csv --horizon 90
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta


RISK_WEIGHTS = {
    "health_trend": 0.25,
    "usage_decline": 0.20,
    "support_severity": 0.15,
    "nps_sentiment": 0.15,
    "engagement_drop": 0.10,
    "contract_proximity": 0.10,
    "executive_change": 0.05,
}

RISK_TIERS = {
    (0, 25): ("Low", "green", "Maintain standard cadence. Monitor for signal changes."),
    (25, 50): ("Moderate", "yellow", "Increase touchpoint frequency. Schedule proactive check-in."),
    (50, 75): ("High", "orange", "Activate retention playbook. Engage executive sponsor within 1 week."),
    (75, 101): ("Critical", "red", "Immediate intervention required. Executive escalation within 48 hours."),
}


def load_data(filepath):
    """Load customer data from CSV or JSON file."""
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
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def parse_date(value):
    """Parse date from common formats."""
    if not value:
        return None
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(str(value).strip(), fmt)
        except ValueError:
            continue
    return None


def score_health_trend(customer):
    """Score churn risk from health score trend (0-100, higher = more risk)."""
    current = safe_float(customer.get("health_score", customer.get("current_health", 50)))
    previous = safe_float(customer.get("previous_health", customer.get("prior_health", current)))

    if current >= 80 and previous >= 80:
        return 5  # Stable healthy
    elif current >= 80:
        return 15  # Recovered
    elif current >= 60 and current >= previous:
        return 30  # Yellow but improving
    elif current >= 60:
        return 50  # Yellow and declining
    elif current >= 40:
        return 75  # Red zone
    else:
        return 95  # Critical


def score_usage_decline(customer):
    """Score churn risk from usage patterns (0-100)."""
    current_usage = safe_float(customer.get("current_usage", customer.get("active_users", 0)))
    previous_usage = safe_float(customer.get("previous_usage", customer.get("prior_active_users", 0)))
    licensed = safe_float(customer.get("licensed_seats", customer.get("licenses", 0)))

    if previous_usage <= 0 and current_usage <= 0:
        return 50  # No data; moderate concern

    # Usage ratio
    adoption_rate = (current_usage / licensed * 100) if licensed > 0 else 0

    # Usage trend
    if previous_usage > 0:
        change = ((current_usage - previous_usage) / previous_usage) * 100
    else:
        change = 0

    risk = 0
    if adoption_rate < 30:
        risk += 50
    elif adoption_rate < 50:
        risk += 30
    elif adoption_rate < 70:
        risk += 15

    if change < -30:
        risk += 40
    elif change < -15:
        risk += 25
    elif change < 0:
        risk += 10

    return min(risk, 100)


def score_support_severity(customer):
    """Score churn risk from support interactions (0-100)."""
    open_tickets = safe_float(customer.get("open_tickets", 0))
    escalations = safe_float(customer.get("escalations", 0))
    avg_resolution_days = safe_float(customer.get("avg_resolution_days", 0))

    risk = 0
    if open_tickets > 10:
        risk += 40
    elif open_tickets > 5:
        risk += 25
    elif open_tickets > 2:
        risk += 10

    if escalations > 3:
        risk += 40
    elif escalations > 1:
        risk += 25
    elif escalations > 0:
        risk += 10

    if avg_resolution_days > 7:
        risk += 20
    elif avg_resolution_days > 3:
        risk += 10

    return min(risk, 100)


def score_nps_sentiment(customer):
    """Score churn risk from NPS/sentiment data (0-100)."""
    nps = safe_float(customer.get("nps", customer.get("nps_score", 50)))

    if nps >= 9:
        return 5  # Promoter
    elif nps >= 7:
        return 20  # Passive
    elif nps >= 5:
        return 50  # Low passive
    elif nps >= 3:
        return 75  # Detractor
    else:
        return 95  # Strong detractor


def score_engagement_drop(customer):
    """Score churn risk from engagement decline (0-100)."""
    meetings_attended = safe_float(customer.get("meetings_attended", customer.get("meetings", 0)))
    meetings_scheduled = safe_float(customer.get("meetings_scheduled", customer.get("total_meetings", 0)))
    response_days = safe_float(customer.get("avg_response_days", customer.get("response_time", 1)))

    risk = 0

    if meetings_scheduled > 0:
        attendance_rate = meetings_attended / meetings_scheduled
        if attendance_rate < 0.5:
            risk += 50
        elif attendance_rate < 0.75:
            risk += 25
    else:
        risk += 30  # No meetings = concern

    if response_days > 7:
        risk += 40
    elif response_days > 3:
        risk += 20

    return min(risk, 100)


def score_contract_proximity(customer, horizon_days):
    """Score urgency based on contract renewal proximity (0-100)."""
    renewal_str = customer.get("renewal_date", customer.get("contract_end", ""))
    renewal_date = parse_date(renewal_str)

    if not renewal_date:
        return 30  # Unknown = moderate concern

    today = datetime.now()
    days_to_renewal = (renewal_date - today).days

    if days_to_renewal < 0:
        return 95  # Past due
    elif days_to_renewal <= 30:
        return 80
    elif days_to_renewal <= 60:
        return 60
    elif days_to_renewal <= 90:
        return 40
    elif days_to_renewal <= horizon_days:
        return 20
    else:
        return 5


def score_executive_change(customer):
    """Score risk from executive sponsor changes (0-100)."""
    changed = str(customer.get("executive_change", customer.get("sponsor_change", "false"))).lower()
    if changed in ("true", "1", "yes"):
        return 80
    return 0


def predict_churn(customer, horizon_days):
    """Calculate overall churn risk score for a customer."""
    signals = {
        "health_trend": score_health_trend(customer),
        "usage_decline": score_usage_decline(customer),
        "support_severity": score_support_severity(customer),
        "nps_sentiment": score_nps_sentiment(customer),
        "engagement_drop": score_engagement_drop(customer),
        "contract_proximity": score_contract_proximity(customer, horizon_days),
        "executive_change": score_executive_change(customer),
    }

    weighted_score = sum(
        signals[signal] * RISK_WEIGHTS[signal] for signal in signals
    )
    churn_risk = round(min(weighted_score, 100), 1)

    tier_label = "Unknown"
    tier_color = "gray"
    tier_action = ""
    for (lo, hi), (label, color, action) in RISK_TIERS.items():
        if lo <= churn_risk < hi:
            tier_label = label
            tier_color = color
            tier_action = action
            break

    top_risks = sorted(signals.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "customer_name": customer.get(
            "customer_name", customer.get("name", customer.get("account", "Unknown"))
        ),
        "arr": customer.get("arr", customer.get("revenue", "N/A")),
        "renewal_date": customer.get("renewal_date", customer.get("contract_end", "N/A")),
        "churn_risk_score": churn_risk,
        "risk_tier": tier_label,
        "risk_color": tier_color,
        "recommended_action": tier_action,
        "signal_scores": signals,
        "top_risk_factors": [{"signal": s, "score": v} for s, v in top_risks],
    }


def format_human(results, horizon):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("CHURN RISK PREDICTION REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Prediction Horizon: {horizon} days")
    lines.append("=" * 70)

    total = len(results)
    critical = sum(1 for r in results if r["risk_tier"] == "Critical")
    high = sum(1 for r in results if r["risk_tier"] == "High")
    moderate = sum(1 for r in results if r["risk_tier"] == "Moderate")
    low = sum(1 for r in results if r["risk_tier"] == "Low")
    avg_risk = sum(r["churn_risk_score"] for r in results) / total if total > 0 else 0

    lines.append(f"\n  Portfolio Risk Summary")
    lines.append(f"  Total Customers:     {total}")
    lines.append(f"  Critical Risk:       {critical}")
    lines.append(f"  High Risk:           {high}")
    lines.append(f"  Moderate Risk:       {moderate}")
    lines.append(f"  Low Risk:            {low}")
    lines.append(f"  Avg Churn Risk:      {avg_risk:.1f}/100")

    at_risk_arr = sum(
        safe_float(r.get("arr", 0))
        for r in results
        if r["risk_tier"] in ("Critical", "High")
    )
    if at_risk_arr > 0:
        lines.append(f"  At-Risk ARR:         ${at_risk_arr:,.2f}")

    sorted_results = sorted(results, key=lambda r: r["churn_risk_score"], reverse=True)

    for result in sorted_results:
        tier_tag = f"[{result['risk_tier'].upper()}]"
        lines.append(f"\n  {tier_tag} {result['customer_name']}")
        lines.append(f"  Churn Risk: {result['churn_risk_score']}/100  |  ARR: {result['arr']}  |  Renewal: {result['renewal_date']}")
        lines.append(f"  Action: {result['recommended_action']}")

        lines.append(f"\n  Signal Breakdown:")
        for signal, score in sorted(result["signal_scores"].items(), key=lambda x: x[1], reverse=True):
            bar_len = int(score / 10)
            bar = "#" * bar_len + "." * (10 - bar_len)
            weight = RISK_WEIGHTS[signal]
            flag = " << TOP RISK" if score >= 60 else ""
            lines.append(
                f"    {signal.replace('_', ' '):<22} [{bar}] {score:>5.1f} (wt: {weight:.0%}){flag}"
            )

        lines.append("-" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Predict customer churn risk from health and engagement data."
    )
    parser.add_argument("--data", required=True, help="Path to customer data CSV or JSON file")
    parser.add_argument(
        "--horizon",
        type=int,
        default=90,
        help="Prediction horizon in days (default: 90)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    customers = load_data(args.data)
    if not customers:
        print("Error: No customers found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [predict_churn(c, args.horizon) for c in customers]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results, args.horizon))

    critical_count = sum(1 for r in results if r["risk_tier"] in ("Critical", "High"))
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == "__main__":
    main()
