#!/usr/bin/env python3
"""Delivery Metrics Tracker - Track DORA metrics and delivery health over time.

Reads deployment and incident data, calculates the four DORA metrics, and
classifies the team against industry benchmarks (Elite/High/Medium/Low).

Usage:
    python delivery_metrics_tracker.py --data delivery.json
    python delivery_metrics_tracker.py --data delivery.json --period 30 --json
    python delivery_metrics_tracker.py --example
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


DORA_BENCHMARKS = {
    "deployment_frequency": {
        "elite": {"label": "Multiple per day", "threshold_per_week": 5},
        "high": {"label": "Weekly to daily", "threshold_per_week": 1},
        "medium": {"label": "Monthly to weekly", "threshold_per_week": 0.25},
        "low": {"label": "Less than monthly", "threshold_per_week": 0},
    },
    "lead_time_hours": {
        "elite": {"label": "Less than 1 hour", "threshold": 1},
        "high": {"label": "1 hour to 1 day", "threshold": 24},
        "medium": {"label": "1 day to 1 week", "threshold": 168},
        "low": {"label": "More than 1 week", "threshold": float("inf")},
    },
    "change_failure_rate_pct": {
        "elite": {"label": "0-5%", "threshold": 5},
        "high": {"label": "5-10%", "threshold": 10},
        "medium": {"label": "10-15%", "threshold": 15},
        "low": {"label": "15%+", "threshold": 100},
    },
    "mttr_hours": {
        "elite": {"label": "Less than 1 hour", "threshold": 1},
        "high": {"label": "1-4 hours", "threshold": 4},
        "medium": {"label": "4-24 hours", "threshold": 24},
        "low": {"label": "More than 1 day", "threshold": float("inf")},
    },
}


def load_data(path: str) -> dict:
    """Load delivery data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def parse_dt(s: str) -> datetime:
    """Parse datetime string."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse: {s}")


def classify(metric_name: str, value: float) -> str:
    """Classify a metric value against DORA benchmarks."""
    benchmarks = DORA_BENCHMARKS[metric_name]
    if metric_name == "deployment_frequency":
        if value >= benchmarks["elite"]["threshold_per_week"]:
            return "Elite"
        elif value >= benchmarks["high"]["threshold_per_week"]:
            return "High"
        elif value >= benchmarks["medium"]["threshold_per_week"]:
            return "Medium"
        return "Low"
    else:
        if value <= benchmarks["elite"]["threshold"]:
            return "Elite"
        elif value <= benchmarks["high"]["threshold"]:
            return "High"
        elif value <= benchmarks["medium"]["threshold"]:
            return "Medium"
        return "Low"


def analyze_delivery(data: dict, period_days: int = 30) -> dict:
    """Calculate DORA metrics from delivery data."""
    service = data.get("service", "Unknown")
    deployments = data.get("deployments", [])
    incidents = data.get("incidents", [])

    now = datetime.now()
    cutoff = now - timedelta(days=period_days)

    # Filter to period
    period_deployments = []
    for d in deployments:
        try:
            dt = parse_dt(d["date"])
            if dt >= cutoff:
                period_deployments.append(d)
        except (ValueError, KeyError):
            pass

    period_incidents = []
    for inc in incidents:
        try:
            dt = parse_dt(inc["detected"])
            if dt >= cutoff:
                period_incidents.append(inc)
        except (ValueError, KeyError):
            pass

    # 1. Deployment Frequency
    deploy_count = len(period_deployments)
    weeks = period_days / 7
    deploys_per_week = round(deploy_count / weeks, 2) if weeks > 0 else 0

    # 2. Lead Time for Changes
    lead_times = []
    for d in period_deployments:
        if "commit_time" in d and "deploy_time" in d:
            try:
                commit_dt = parse_dt(d["commit_time"])
                deploy_dt = parse_dt(d["deploy_time"])
                lt_hours = (deploy_dt - commit_dt).total_seconds() / 3600
                if lt_hours >= 0:
                    lead_times.append(round(lt_hours, 1))
            except ValueError:
                pass
    avg_lead_time = round(sum(lead_times) / len(lead_times), 1) if lead_times else 0
    median_lead_time = sorted(lead_times)[len(lead_times) // 2] if lead_times else 0

    # 3. Change Failure Rate
    failed = sum(1 for d in period_deployments if d.get("failed", False) or d.get("rolled_back", False))
    cfr = round(failed / deploy_count * 100, 1) if deploy_count > 0 else 0

    # 4. Mean Time to Recovery
    recovery_times = []
    for inc in period_incidents:
        if "detected" in inc and "resolved" in inc:
            try:
                detected = parse_dt(inc["detected"])
                resolved = parse_dt(inc["resolved"])
                rt_hours = (resolved - detected).total_seconds() / 3600
                if rt_hours >= 0:
                    recovery_times.append(round(rt_hours, 1))
            except ValueError:
                pass
    avg_mttr = round(sum(recovery_times) / len(recovery_times), 1) if recovery_times else 0

    # Classifications
    metrics = {
        "deployment_frequency": {
            "value": deploys_per_week,
            "unit": "deploys/week",
            "total_in_period": deploy_count,
            "classification": classify("deployment_frequency", deploys_per_week),
        },
        "lead_time": {
            "value": avg_lead_time,
            "median": median_lead_time,
            "unit": "hours",
            "sample_size": len(lead_times),
            "classification": classify("lead_time_hours", avg_lead_time),
        },
        "change_failure_rate": {
            "value": cfr,
            "unit": "%",
            "failed_deploys": failed,
            "total_deploys": deploy_count,
            "classification": classify("change_failure_rate_pct", cfr),
        },
        "mttr": {
            "value": avg_mttr,
            "unit": "hours",
            "incidents_in_period": len(period_incidents),
            "sample_size": len(recovery_times),
            "classification": classify("mttr_hours", avg_mttr),
        },
    }

    # Overall classification
    classifications = [m["classification"] for m in metrics.values()]
    class_scores = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1}
    avg_class = sum(class_scores.get(c, 1) for c in classifications) / len(classifications)
    if avg_class >= 3.5:
        overall = "Elite"
    elif avg_class >= 2.5:
        overall = "High"
    elif avg_class >= 1.5:
        overall = "Medium"
    else:
        overall = "Low"

    # Recommendations
    recs = []
    for name, m in metrics.items():
        if m["classification"] in ("Low", "Medium"):
            if name == "deployment_frequency":
                recs.append("Increase deployment frequency by reducing batch size and automating the release pipeline.")
            elif name == "lead_time":
                recs.append("Reduce lead time by improving CI/CD pipeline speed, automating testing, and reducing approval gates.")
            elif name == "change_failure_rate":
                recs.append("Lower change failure rate by improving test coverage, adding canary deployments, and enhancing code review practices.")
            elif name == "mttr":
                recs.append("Improve MTTR by investing in observability (logging, tracing, alerting) and pre-defined runbooks.")

    return {
        "service": service,
        "period_days": period_days,
        "overall_classification": overall,
        "metrics": metrics,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable DORA metrics report."""
    print(f"\nDORA Metrics Report: {result['service']}")
    print(f"Period: Last {result['period_days']} days")
    print("=" * 60)
    print(f"Overall Classification: {result['overall_classification']}")
    print()

    m = result["metrics"]

    df = m["deployment_frequency"]
    print(f"Deployment Frequency:   {df['value']} {df['unit']} ({df['total_in_period']} total)")
    print(f"  Classification: {df['classification']}")

    lt = m["lead_time"]
    print(f"Lead Time for Changes:  {lt['value']}h avg, {lt['median']}h median (n={lt['sample_size']})")
    print(f"  Classification: {lt['classification']}")

    cfr = m["change_failure_rate"]
    print(f"Change Failure Rate:    {cfr['value']}% ({cfr['failed_deploys']}/{cfr['total_deploys']} failed)")
    print(f"  Classification: {cfr['classification']}")

    mttr = m["mttr"]
    print(f"MTTR:                   {mttr['value']}h avg ({mttr['incidents_in_period']} incidents)")
    print(f"  Classification: {mttr['classification']}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example delivery data JSON."""
    example = {
        "service": "payment-api",
        "deployments": [
            {"date": "2026-03-18", "commit_time": "2026-03-18T09:00:00", "deploy_time": "2026-03-18T11:30:00", "failed": False},
            {"date": "2026-03-15", "commit_time": "2026-03-14T14:00:00", "deploy_time": "2026-03-15T10:00:00", "failed": False},
            {"date": "2026-03-12", "commit_time": "2026-03-11T16:00:00", "deploy_time": "2026-03-12T09:30:00", "rolled_back": True},
            {"date": "2026-03-08", "commit_time": "2026-03-07T10:00:00", "deploy_time": "2026-03-08T14:00:00", "failed": False},
        ],
        "incidents": [
            {"id": "INC-001", "severity": "SEV-2", "detected": "2026-03-12T10:00:00", "resolved": "2026-03-12T12:30:00"},
            {"id": "INC-002", "severity": "SEV-3", "detected": "2026-03-05T15:00:00", "resolved": "2026-03-05T16:00:00"},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Track DORA metrics and delivery health."
    )
    parser.add_argument("--data", type=str, help="Path to delivery data JSON file")
    parser.add_argument("--period", type=int, default=30, help="Analysis period in days (default: 30)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example data JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.data:
        parser.error("--data is required (use --example to see the expected format)")

    data = load_data(args.data)
    result = analyze_delivery(data, args.period)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
