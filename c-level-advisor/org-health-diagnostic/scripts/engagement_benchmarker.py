#!/usr/bin/env python3
"""Engagement Benchmarker - Benchmark engagement metrics against industry standards.

Compares eNPS, attrition, time-to-fill, promotion rate, and other people metrics
against industry benchmarks. Flags gaps and provides improvement recommendations.

Usage:
    python engagement_benchmarker.py --enps 15 --attrition 18 --time-to-fill 60 --promotion-rate 20 --industry saas
    python engagement_benchmarker.py --enps -5 --attrition 28 --time-to-fill 90 --promotion-rate 10 --industry saas --json
"""

import argparse
import json
import sys
from datetime import datetime

BENCHMARKS = {
    "saas": {
        "industry_name": "SaaS / Technology",
        "metrics": {
            "enps": {"benchmark": 20, "green": 30, "yellow": 0, "unit": "score", "direction": "higher_is_better"},
            "attrition": {"benchmark": 15, "green": 10, "yellow": 20, "unit": "% annual", "direction": "lower_is_better"},
            "time_to_fill": {"benchmark": 45, "green": 35, "yellow": 75, "unit": "days", "direction": "lower_is_better"},
            "promotion_rate": {"benchmark": 25, "green": 30, "yellow": 15, "unit": "% internal", "direction": "higher_is_better"},
            "manager_ratio": {"benchmark": 7, "green_range": [5, 8], "unit": "ICs per manager"},
        }
    },
    "fintech": {
        "industry_name": "Fintech",
        "metrics": {
            "enps": {"benchmark": 18, "green": 25, "yellow": -5, "unit": "score", "direction": "higher_is_better"},
            "attrition": {"benchmark": 18, "green": 12, "yellow": 25, "unit": "% annual", "direction": "lower_is_better"},
            "time_to_fill": {"benchmark": 55, "green": 40, "yellow": 85, "unit": "days", "direction": "lower_is_better"},
            "promotion_rate": {"benchmark": 22, "green": 28, "yellow": 12, "unit": "% internal", "direction": "higher_is_better"},
            "manager_ratio": {"benchmark": 7, "green_range": [5, 8], "unit": "ICs per manager"},
        }
    },
    "enterprise": {
        "industry_name": "Enterprise Software",
        "metrics": {
            "enps": {"benchmark": 15, "green": 25, "yellow": -5, "unit": "score", "direction": "higher_is_better"},
            "attrition": {"benchmark": 12, "green": 8, "yellow": 18, "unit": "% annual", "direction": "lower_is_better"},
            "time_to_fill": {"benchmark": 50, "green": 40, "yellow": 80, "unit": "days", "direction": "lower_is_better"},
            "promotion_rate": {"benchmark": 20, "green": 28, "yellow": 12, "unit": "% internal", "direction": "higher_is_better"},
            "manager_ratio": {"benchmark": 6, "green_range": [5, 8], "unit": "ICs per manager"},
        }
    },
    "startup": {
        "industry_name": "Startup (Early Stage)",
        "metrics": {
            "enps": {"benchmark": 25, "green": 35, "yellow": 5, "unit": "score", "direction": "higher_is_better"},
            "attrition": {"benchmark": 20, "green": 12, "yellow": 30, "unit": "% annual", "direction": "lower_is_better"},
            "time_to_fill": {"benchmark": 40, "green": 30, "yellow": 70, "unit": "days", "direction": "lower_is_better"},
            "promotion_rate": {"benchmark": 20, "green": 30, "yellow": 10, "unit": "% internal", "direction": "higher_is_better"},
            "manager_ratio": {"benchmark": 7, "green_range": [5, 9], "unit": "ICs per manager"},
        }
    }
}

METRIC_RECOMMENDATIONS = {
    "enps": {
        "low": [
            "Conduct stay interviews with top performers to understand concerns",
            "Review and address top 3 themes from last engagement survey",
            "Increase leadership visibility and communication frequency",
            "Implement manager coaching program focused on team support"
        ],
        "critical": [
            "URGENT: Negative eNPS indicates fundamental engagement crisis",
            "Conduct skip-level conversations within 2 weeks",
            "CEO to address concerns directly at all-hands",
            "Consider bringing in external engagement consultant"
        ]
    },
    "attrition": {
        "low": [
            "Review compensation against market data for at-risk roles",
            "Implement retention bonuses for critical personnel",
            "Improve career development and growth opportunities",
            "Address exit interview themes systematically"
        ],
        "critical": [
            "URGENT: Attrition above 25% threatens operational continuity",
            "Immediate retention package for top 10 at-risk employees",
            "CEO conversation with each departing senior team member",
            "Conduct emergency engagement pulse survey"
        ]
    },
    "time_to_fill": {
        "low": [
            "Review and streamline interview process (aim for < 3 weeks end-to-end)",
            "Improve job descriptions and employer branding",
            "Expand sourcing channels beyond current methods",
            "Consider adding recruiter headcount"
        ],
        "critical": [
            "Hiring bottleneck affecting growth -- immediate process review",
            "Consider temporary agency support for critical roles",
            "Reduce interview stages to maximum 4",
            "Implement hiring manager accountability metrics"
        ]
    },
    "promotion_rate": {
        "low": [
            "Review career ladder clarity -- are paths well-defined?",
            "Implement quarterly development conversations",
            "Create stretch assignments for high-potential employees",
            "Audit promotion criteria for transparency and fairness"
        ],
        "critical": [
            "Low promotion rate signals development stagnation",
            "Implement individual development plans for all ICs",
            "Review if managers have development as part of their goals",
            "Consider internal mobility program"
        ]
    }
}


def benchmark(enps, attrition, time_to_fill, promotion_rate, industry):
    industry_key = industry.lower()
    if industry_key not in BENCHMARKS:
        industry_key = "saas"  # Default

    bench = BENCHMARKS[industry_key]
    results = []

    metrics_input = {
        "enps": enps,
        "attrition": attrition,
        "time_to_fill": time_to_fill,
        "promotion_rate": promotion_rate
    }

    for metric_key, value in metrics_input.items():
        b = bench["metrics"][metric_key]
        direction = b["direction"]

        if direction == "higher_is_better":
            if value >= b["green"]:
                status = "GREEN"
            elif value >= b["yellow"]:
                status = "YELLOW"
            else:
                status = "RED"
            vs_benchmark = round(value - b["benchmark"], 1)
            vs_label = f"{'+' if vs_benchmark > 0 else ''}{vs_benchmark} vs benchmark"
        else:  # lower_is_better
            if value <= b["green"]:
                status = "GREEN"
            elif value <= b["yellow"]:
                status = "YELLOW"
            else:
                status = "RED"
            vs_benchmark = round(value - b["benchmark"], 1)
            vs_label = f"{'+' if vs_benchmark > 0 else ''}{vs_benchmark} vs benchmark"

        recs = []
        if status in ("RED", "YELLOW"):
            rec_key = "critical" if status == "RED" else "low"
            recs = METRIC_RECOMMENDATIONS.get(metric_key, {}).get(rec_key, [])

        results.append({
            "metric": metric_key,
            "value": value,
            "unit": b["unit"],
            "benchmark": b["benchmark"],
            "vs_benchmark": vs_label,
            "status": status,
            "recommendations": recs
        })

    # Overall engagement health
    red_count = sum(1 for r in results if r["status"] == "RED")
    yellow_count = sum(1 for r in results if r["status"] == "YELLOW")
    green_count = sum(1 for r in results if r["status"] == "GREEN")

    if red_count >= 2:
        overall = "CRITICAL"
    elif red_count >= 1:
        overall = "AT RISK"
    elif yellow_count >= 2:
        overall = "NEEDS ATTENTION"
    else:
        overall = "HEALTHY"

    return {
        "benchmark_date": datetime.now().strftime("%Y-%m-%d"),
        "industry": bench["industry_name"],
        "overall_status": overall,
        "metrics": results,
        "summary": {"green": green_count, "yellow": yellow_count, "red": red_count},
        "priority_actions": [r["recommendations"][0] for r in results if r["status"] == "RED" and r["recommendations"]]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"ENGAGEMENT BENCHMARKER - {result['industry']}")
    print(f"Date: {result['benchmark_date']}")
    print(f"Overall: {result['overall_status']}")
    print(f"{'='*70}\n")

    print("METRICS vs BENCHMARK:")
    print("-" * 65)
    for m in result["metrics"]:
        status_icon = {"GREEN": "+", "YELLOW": "~", "RED": "!"}[m["status"]]
        print(f"  [{status_icon}] {m['metric']:<18s} {m['value']:>6}  {m['unit']:<12s}  (benchmark: {m['benchmark']})  {m['vs_benchmark']}")

    for m in result["metrics"]:
        if m["recommendations"]:
            print(f"\n  {m['metric'].upper()} [{m['status']}] Recommendations:")
            for r in m["recommendations"]:
                print(f"    -> {r}")

    if result["priority_actions"]:
        print(f"\nPRIORITY ACTIONS:")
        for a in result["priority_actions"]:
            print(f"  [!] {a}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Benchmark engagement metrics against industry standards")
    parser.add_argument("--enps", type=float, required=True, help="Employee NPS score")
    parser.add_argument("--attrition", type=float, required=True, help="Annual attrition rate (%)")
    parser.add_argument("--time-to-fill", type=float, required=True, help="Average days to fill a position")
    parser.add_argument("--promotion-rate", type=float, required=True, help="Internal promotion rate (%)")
    parser.add_argument("--industry", default="saas", choices=list(BENCHMARKS.keys()), help="Industry for benchmarking")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = benchmark(args.enps, args.attrition, args.time_to_fill, args.promotion_rate, args.industry)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
