#!/usr/bin/env python3
"""Delivery Metrics Tracker - Track DORA metrics and delivery health over time.

Reads deployment and incident data, calculates the four classic DORA metrics
(deployment frequency, change lead time, change fail rate, failed deployment
recovery time) and classifies the team against the 2024 DORA report
performance levels (Elite/High/Medium/Low).

Optionally computes DORA's fifth metric, deployment rework rate, when the
input marks deployments with "rework": true (unplanned deploys made to fix a
user-facing bug / production incident). Rework rate is reported only, never
classified, because DORA publishes no per-level benchmark for it.

Notes:
- "Failed deployment recovery time" is DORA's current name for the metric
  previously called MTTR / time to restore service. The JSON output keeps the
  legacy "mttr" key as an alias so existing consumers do not break.
- The 2025 DORA report ("State of AI-assisted Software Development") presents
  seven team profiles rather than leading with these four levels. The levels below remain
  the most recent published cut-offs (2024 report, v. 2024.3).

Usage:
    python delivery_metrics_tracker.py --data delivery.json
    python delivery_metrics_tracker.py --data delivery.json --period 30 --json
    python delivery_metrics_tracker.py --example
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


# Source: 2024 Accelerate State of DevOps Report (DORA), "Performance levels".
# The report gives cluster descriptions, not hard cut-offs; the numeric
# thresholds here are the band edges those descriptions imply.
# Change fail rate cluster values in 2024 were Elite 5%, High 20%, Medium 10%,
# Low 40% (not monotonic). The tool uses monotonic bands at 5/10/20% so a
# lower fail rate never scores worse.
DORA_BENCHMARKS = {
    "deployment_frequency": {
        # On demand = multiple deploys per day; ~10/week = 2 per working day
        "elite": {"label": "On demand (multiple deploys per day)", "threshold_per_week": 10},
        "high": {"label": "Between once per day and once per week", "threshold_per_week": 1},
        "medium": {"label": "Between once per week and once per month", "threshold_per_week": 0.25},
        "low": {"label": "Between once per month and once every six months", "threshold_per_week": 0},
    },
    "lead_time_hours": {
        "elite": {"label": "Less than one day", "threshold": 24},
        "high": {"label": "Between one day and one week", "threshold": 168},
        "medium": {"label": "Between one week and one month", "threshold": 720},
        "low": {"label": "Between one month and six months", "threshold": float("inf")},
    },
    "change_failure_rate_pct": {
        "elite": {"label": "5% or less", "threshold": 5},
        "high": {"label": "5-10% (tool band)", "threshold": 10},
        "medium": {"label": "10-20% (tool band)", "threshold": 20},
        "low": {"label": "Over 20% (2024 Low cluster: 40%)", "threshold": 100},
    },
    "failed_deployment_recovery_hours": {
        "elite": {"label": "Less than one hour", "threshold": 1},
        "high": {"label": "Less than one day", "threshold": 24},
        # 2024 Medium cluster was also "less than one day"; the tool treats
        # one day to one week as Medium to avoid a gap before Low.
        "medium": {"label": "One day to one week (tool band)", "threshold": 168},
        "low": {"label": "Between one week and one month or longer", "threshold": float("inf")},
    },
}
# Legacy alias kept for any code importing DORA_BENCHMARKS["mttr_hours"].
DORA_BENCHMARKS["mttr_hours"] = DORA_BENCHMARKS["failed_deployment_recovery_hours"]


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

    # 4. Failed Deployment Recovery Time (formerly MTTR)
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

    # 5. Deployment Rework Rate (optional) - only when the data marks rework
    rework_rate = None
    if any("rework" in d for d in period_deployments):
        rework_count = sum(1 for d in period_deployments if d.get("rework", False))
        rework_rate = {
            "value": round(rework_count / deploy_count * 100, 1) if deploy_count > 0 else 0,
            "unit": "%",
            "rework_deploys": rework_count,
            "total_deploys": deploy_count,
            "classification": "Not classified (no published DORA benchmark)",
        }

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
        "failed_deployment_recovery_time": {
            "value": avg_mttr,
            "unit": "hours",
            "incidents_in_period": len(period_incidents),
            "sample_size": len(recovery_times),
            "classification": classify("failed_deployment_recovery_hours", avg_mttr),
        },
    }
    # Legacy alias: same object under the old key for existing consumers.
    metrics["mttr"] = metrics["failed_deployment_recovery_time"]
    if rework_rate is not None:
        metrics["deployment_rework_rate"] = rework_rate

    # Overall classification (the four classified metrics only)
    classified = ["deployment_frequency", "lead_time", "change_failure_rate",
                  "failed_deployment_recovery_time"]
    classifications = [metrics[k]["classification"] for k in classified]
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
    for name in classified:
        m = metrics[name]
        if m["classification"] in ("Low", "Medium"):
            if name == "deployment_frequency":
                recs.append("Increase deployment frequency by reducing batch size and automating the release pipeline.")
            elif name == "lead_time":
                recs.append("Reduce lead time by improving CI/CD pipeline speed, automating testing, and reducing approval gates.")
            elif name == "change_failure_rate":
                recs.append("Lower change failure rate by improving test coverage, adding canary deployments, and enhancing code review practices.")
            elif name == "failed_deployment_recovery_time":
                recs.append("Improve failed deployment recovery time (formerly MTTR) by investing in observability (logging, tracing, alerting) and pre-defined runbooks.")

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

    mttr = m["failed_deployment_recovery_time"]
    print(f"Failed Deploy Recovery: {mttr['value']}h avg ({mttr['incidents_in_period']} incidents) [formerly MTTR]")
    print(f"  Classification: {mttr['classification']}")

    rw = m.get("deployment_rework_rate")
    if rw is not None:
        print(f"Deployment Rework Rate: {rw['value']}% ({rw['rework_deploys']}/{rw['total_deploys']} unplanned fix deploys)")
        print(f"  Classification: {rw['classification']}")

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
            {"date": "2026-03-12", "commit_time": "2026-03-12T10:15:00", "deploy_time": "2026-03-12T12:00:00", "failed": False, "rework": True},
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
