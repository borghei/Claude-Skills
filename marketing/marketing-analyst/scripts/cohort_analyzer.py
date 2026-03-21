#!/usr/bin/env python3
"""Cohort Analyzer - Analyze user retention and behavior by cohort.

Generates cohort retention tables, identifies trends, and calculates
key retention metrics (D1/D7/D30, average lifetime, LTV).

Usage:
    python cohort_analyzer.py cohort_data.json
    python cohort_analyzer.py cohort_data.json --json
    python cohort_analyzer.py --demo
"""

import argparse
import json
import sys


def analyze_cohorts(cohort_data):
    """Analyze cohort retention data."""
    cohorts = cohort_data if isinstance(cohort_data, list) else cohort_data.get("cohorts", [])

    results = []
    all_retention_by_period = {}

    for cohort in cohorts:
        name = cohort.get("name", cohort.get("cohort", "Unknown"))
        initial_users = cohort.get("initial_users", cohort.get("users", 0))
        retention = cohort.get("retention", cohort.get("active_users", []))

        # Calculate retention rates
        retention_rates = []
        for i, active in enumerate(retention):
            rate = (active / max(initial_users, 1)) * 100
            retention_rates.append({
                "period": i,
                "active_users": active,
                "retention_rate": round(rate, 1),
                "churned": initial_users - active if i == 0 else retention[i - 1] - active,
            })

            if i not in all_retention_by_period:
                all_retention_by_period[i] = []
            all_retention_by_period[i].append(rate)

        # Key retention milestones
        d1 = retention_rates[1]["retention_rate"] if len(retention_rates) > 1 else None
        d7 = retention_rates[7]["retention_rate"] if len(retention_rates) > 7 else None
        d30 = retention_rates[30]["retention_rate"] if len(retention_rates) > 30 else None
        w1 = retention_rates[1]["retention_rate"] if len(retention_rates) > 1 else None

        # Calculate average lifetime (simplified)
        total_active_periods = sum(r["active_users"] for r in retention_rates)
        avg_lifetime = total_active_periods / max(initial_users, 1)

        results.append({
            "cohort": name,
            "initial_users": initial_users,
            "retention_rates": retention_rates,
            "milestones": {
                "period_1": round(d1, 1) if d1 else None,
                "period_7": round(d7, 1) if d7 else None,
                "period_30": round(d30, 1) if d30 else None,
            },
            "avg_lifetime_periods": round(avg_lifetime, 1),
            "final_retention": retention_rates[-1]["retention_rate"] if retention_rates else 0,
        })

    # Cross-cohort trend analysis
    trends = {}
    for period, rates in all_retention_by_period.items():
        if len(rates) >= 2:
            trends[period] = {
                "avg_retention": round(sum(rates) / len(rates), 1),
                "min_retention": round(min(rates), 1),
                "max_retention": round(max(rates), 1),
                "improving": rates[-1] > rates[0] if len(rates) >= 2 else None,
            }

    # Identify best and worst cohorts
    if results:
        final_retentions = [(r["cohort"], r["final_retention"]) for r in results]
        best_cohort = max(final_retentions, key=lambda x: x[1])
        worst_cohort = min(final_retentions, key=lambda x: x[1])
    else:
        best_cohort = worst_cohort = None

    return {
        "cohorts": results,
        "trends": trends,
        "summary": {
            "total_cohorts": len(results),
            "best_cohort": {"name": best_cohort[0], "final_retention": best_cohort[1]} if best_cohort else None,
            "worst_cohort": {"name": worst_cohort[0], "final_retention": worst_cohort[1]} if worst_cohort else None,
            "avg_final_retention": round(
                sum(r["final_retention"] for r in results) / max(len(results), 1), 1
            ),
        },
    }


def get_demo_data():
    return {
        "cohorts": [
            {"name": "Jan W1", "initial_users": 1000, "retention": [1000, 450, 350, 280, 250]},
            {"name": "Jan W2", "initial_users": 1100, "retention": [1100, 528, 418, 352, 308]},
            {"name": "Jan W3", "initial_users": 950, "retention": [950, 494, 399, 333, 295]},
            {"name": "Jan W4", "initial_users": 1050, "retention": [1050, 578, 473, 399, 357]},
            {"name": "Feb W1", "initial_users": 1200, "retention": [1200, 684, 564, 480, 432]},
        ],
    }


def format_report(analysis):
    """Format human-readable cohort report."""
    lines = []
    lines.append("=" * 70)
    lines.append("COHORT RETENTION ANALYSIS")
    lines.append("=" * 70)

    s = analysis["summary"]
    lines.append(f"Cohorts Analyzed:       {s['total_cohorts']}")
    lines.append(f"Avg Final Retention:    {s['avg_final_retention']:.1f}%")
    if s["best_cohort"]:
        lines.append(f"Best Cohort:            {s['best_cohort']['name']} ({s['best_cohort']['final_retention']:.1f}%)")
    if s["worst_cohort"]:
        lines.append(f"Worst Cohort:           {s['worst_cohort']['name']} ({s['worst_cohort']['final_retention']:.1f}%)")
    lines.append("")

    # Retention table
    if analysis["cohorts"]:
        max_periods = max(len(c["retention_rates"]) for c in analysis["cohorts"])
        period_headers = [f"P{i}" for i in range(min(max_periods, 8))]

        lines.append("--- RETENTION TABLE (%) ---")
        header = f"{'Cohort':<12} {'Users':>6} " + " ".join(f"{h:>6}" for h in period_headers)
        lines.append(header)
        lines.append("-" * len(header))

        for cohort in analysis["cohorts"]:
            rates = [f"{r['retention_rate']:>5.1f}%" for r in cohort["retention_rates"][:8]]
            line = f"{cohort['cohort']:<12} {cohort['initial_users']:>6} " + " ".join(rates)
            lines.append(line)
        lines.append("")

    # Trends
    if analysis["trends"]:
        lines.append("--- PERIOD TRENDS ---")
        for period, trend in sorted(analysis["trends"].items()):
            if period < 8:
                improving = "improving" if trend.get("improving") else "declining" if trend.get("improving") is False else "stable"
                lines.append(
                    f"  Period {period}: avg {trend['avg_retention']:.1f}% "
                    f"(range: {trend['min_retention']:.1f}%-{trend['max_retention']:.1f}%) [{improving}]"
                )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze user retention by cohort")
    parser.add_argument("input", nargs="?", help="JSON file with cohort data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = analyze_cohorts(data)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
