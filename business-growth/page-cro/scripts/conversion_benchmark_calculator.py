#!/usr/bin/env python3
"""
Conversion Benchmark Calculator

Calculate conversion rate benchmarks for a given page type, traffic source,
and industry. Assess current performance and provide improvement targets.

Usage:
    python conversion_benchmark_calculator.py --page-type landing-page --traffic paid --current-rate 8.5
    python conversion_benchmark_calculator.py --page-type homepage --traffic organic --current-rate 3.0 --json
"""

import argparse
import json
import sys


# Benchmarks: (below_avg, average, good, excellent)
BENCHMARKS = {
    "homepage": {
        "saas": {"below": 2.0, "average": 3.0, "good": 5.0, "excellent": 7.0},
        "ecommerce": {"below": 1.5, "average": 2.5, "good": 4.0, "excellent": 6.0},
        "fintech": {"below": 1.0, "average": 2.0, "good": 3.5, "excellent": 5.0},
        "healthcare": {"below": 1.5, "average": 2.5, "good": 4.0, "excellent": 6.0},
        "education": {"below": 2.0, "average": 3.0, "good": 5.0, "excellent": 7.0},
    },
    "landing-page": {
        "saas": {"below": 5.0, "average": 8.0, "good": 15.0, "excellent": 20.0},
        "ecommerce": {"below": 3.0, "average": 5.0, "good": 10.0, "excellent": 15.0},
        "fintech": {"below": 3.0, "average": 6.0, "good": 12.0, "excellent": 18.0},
        "healthcare": {"below": 3.0, "average": 5.0, "good": 10.0, "excellent": 15.0},
        "education": {"below": 5.0, "average": 8.0, "good": 15.0, "excellent": 22.0},
    },
    "pricing": {
        "saas": {"below": 3.0, "average": 5.0, "good": 8.0, "excellent": 12.0},
        "ecommerce": {"below": 2.0, "average": 3.5, "good": 6.0, "excellent": 10.0},
        "fintech": {"below": 2.0, "average": 4.0, "good": 7.0, "excellent": 10.0},
        "healthcare": {"below": 2.0, "average": 3.5, "good": 6.0, "excellent": 9.0},
        "education": {"below": 3.0, "average": 5.0, "good": 8.0, "excellent": 12.0},
    },
    "feature": {
        "saas": {"below": 2.0, "average": 3.5, "good": 6.0, "excellent": 8.0},
        "ecommerce": {"below": 1.5, "average": 3.0, "good": 5.0, "excellent": 7.0},
        "fintech": {"below": 1.5, "average": 3.0, "good": 5.0, "excellent": 7.0},
        "healthcare": {"below": 1.5, "average": 2.5, "good": 4.5, "excellent": 6.0},
        "education": {"below": 2.0, "average": 3.5, "good": 5.5, "excellent": 7.5},
    },
    "blog": {
        "saas": {"below": 1.0, "average": 2.0, "good": 3.5, "excellent": 5.0},
        "ecommerce": {"below": 0.5, "average": 1.5, "good": 3.0, "excellent": 4.5},
        "fintech": {"below": 0.5, "average": 1.5, "good": 2.5, "excellent": 4.0},
        "healthcare": {"below": 0.5, "average": 1.5, "good": 3.0, "excellent": 4.5},
        "education": {"below": 1.0, "average": 2.0, "good": 3.5, "excellent": 5.0},
    },
}

TRAFFIC_MULTIPLIERS = {
    "paid": 1.3,      # Paid traffic typically converts higher (targeted)
    "organic": 1.0,    # Baseline
    "email": 1.5,      # Email traffic is warm
    "social": 0.7,     # Social traffic is cold/interrupted
    "referral": 1.4,   # Referral traffic is pre-sold
}


def calculate_benchmarks(page_type: str, traffic: str, current_rate: float,
                         industry: str) -> dict:
    """Calculate benchmarks and assess performance."""
    base_benchmarks = BENCHMARKS.get(page_type, BENCHMARKS["landing-page"])
    industry_benchmarks = base_benchmarks.get(industry, base_benchmarks.get("saas"))
    multiplier = TRAFFIC_MULTIPLIERS.get(traffic, 1.0)

    # Adjusted benchmarks for traffic source
    adjusted = {
        "below_avg": round(industry_benchmarks["below"] * multiplier, 1),
        "average": round(industry_benchmarks["average"] * multiplier, 1),
        "good": round(industry_benchmarks["good"] * multiplier, 1),
        "excellent": round(industry_benchmarks["excellent"] * multiplier, 1),
    }

    # Performance assessment
    if current_rate >= adjusted["excellent"]:
        performance = "EXCELLENT"
        percentile = "Top 10%"
    elif current_rate >= adjusted["good"]:
        performance = "GOOD"
        percentile = "Top 25%"
    elif current_rate >= adjusted["average"]:
        performance = "AVERAGE"
        percentile = "Top 50%"
    elif current_rate >= adjusted["below_avg"]:
        performance = "BELOW AVERAGE"
        percentile = "Bottom 50%"
    else:
        performance = "POOR"
        percentile = "Bottom 25%"

    # Improvement targets
    targets = []
    if current_rate < adjusted["average"]:
        targets.append({
            "target": "Reach average",
            "target_rate": adjusted["average"],
            "improvement_needed_pct": round(((adjusted["average"] - current_rate) / current_rate) * 100, 1) if current_rate > 0 else 0,
        })
    if current_rate < adjusted["good"]:
        targets.append({
            "target": "Reach good",
            "target_rate": adjusted["good"],
            "improvement_needed_pct": round(((adjusted["good"] - current_rate) / current_rate) * 100, 1) if current_rate > 0 else 0,
        })
    if current_rate < adjusted["excellent"]:
        targets.append({
            "target": "Reach excellent",
            "target_rate": adjusted["excellent"],
            "improvement_needed_pct": round(((adjusted["excellent"] - current_rate) / current_rate) * 100, 1) if current_rate > 0 else 0,
        })

    # Revenue impact estimate (per 1000 monthly visitors)
    per_1k = {
        "current": round(1000 * (current_rate / 100), 1),
        "at_average": round(1000 * (adjusted["average"] / 100), 1),
        "at_good": round(1000 * (adjusted["good"] / 100), 1),
        "at_excellent": round(1000 * (adjusted["excellent"] / 100), 1),
    }

    return {
        "inputs": {
            "page_type": page_type,
            "traffic_source": traffic,
            "current_rate_pct": current_rate,
            "industry": industry,
        },
        "benchmarks": adjusted,
        "traffic_adjustment": {
            "multiplier": multiplier,
            "note": f"Benchmarks adjusted {'+' if multiplier > 1 else ''}{round((multiplier - 1) * 100)}% for {traffic} traffic",
        },
        "assessment": {
            "performance": performance,
            "percentile": percentile,
            "current_rate_pct": current_rate,
        },
        "improvement_targets": targets,
        "conversions_per_1000_visitors": per_1k,
        "recommendations": _generate_recommendations(performance, current_rate, adjusted, page_type, traffic),
    }


def _generate_recommendations(performance: str, current: float,
                              benchmarks: dict, page_type: str, traffic: str) -> list:
    """Generate recommendations."""
    recs = []

    if performance in ("POOR", "BELOW AVERAGE"):
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Current rate ({current}%) is below average ({benchmarks['average']}%). Focus on value proposition clarity and CTA hierarchy.",
        })

    if traffic == "paid" and current < benchmarks["average"]:
        recs.append({
            "priority": "HIGH",
            "recommendation": "Paid traffic underperforming. Audit message match between ads and landing page. Consider dedicated landing pages per campaign.",
        })

    if traffic == "social" and current < benchmarks["below_avg"]:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": "Social traffic converts low. Ensure the page hooks attention quickly -- social visitors are interrupted, not searching.",
        })

    if page_type == "pricing" and current < benchmarks["average"]:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": "Pricing page underperforming. Highlight recommended plan, add FAQ ('Which plan is right for me?'), include plan-specific social proof.",
        })

    if performance in ("GOOD", "EXCELLENT"):
        recs.append({
            "priority": "INFO",
            "recommendation": f"Performance is {performance.lower()}. Focus on incremental A/B testing rather than major redesigns.",
        })

    recs.append({
        "priority": "MEDIUM",
        "recommendation": "Track downstream metrics (lead quality, revenue per visitor) not just conversion rate. High conversion with low quality is a net negative.",
    })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("CONVERSION BENCHMARK CALCULATOR")
    lines.append("=" * 60)

    inp = result["inputs"]
    lines.append(f"\nPage Type:      {inp['page_type']}")
    lines.append(f"Traffic Source:  {inp['traffic_source']}")
    lines.append(f"Industry:       {inp['industry']}")
    lines.append(f"Current Rate:   {inp['current_rate_pct']}%")

    bm = result["benchmarks"]
    ta = result["traffic_adjustment"]
    lines.append(f"\n--- Benchmarks ({ta['note']}) ---")
    lines.append(f"  Below Average:  < {bm['below_avg']}%")
    lines.append(f"  Average:          {bm['average']}%")
    lines.append(f"  Good:             {bm['good']}%")
    lines.append(f"  Excellent:        {bm['excellent']}%")

    a = result["assessment"]
    lines.append(f"\n--- Your Performance ---")
    lines.append(f"  Rating:     {a['performance']}")
    lines.append(f"  Percentile: {a['percentile']}")

    if result["improvement_targets"]:
        lines.append(f"\n--- Improvement Targets ---")
        for t in result["improvement_targets"]:
            lines.append(f"  {t['target']}: {t['target_rate']}% (+{t['improvement_needed_pct']}% relative improvement)")

    p = result["conversions_per_1000_visitors"]
    lines.append(f"\n--- Conversions per 1,000 Visitors ---")
    lines.append(f"  Current:     {p['current']:>6.1f}")
    lines.append(f"  At Average:  {p['at_average']:>6.1f}")
    lines.append(f"  At Good:     {p['at_good']:>6.1f}")
    lines.append(f"  At Excellent:{p['at_excellent']:>6.1f}")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate conversion rate benchmarks and assess performance."
    )
    parser.add_argument("--page-type", required=True,
                        choices=["homepage", "landing-page", "pricing", "feature", "blog"],
                        help="Page type")
    parser.add_argument("--traffic", required=True,
                        choices=["organic", "paid", "email", "social", "referral"],
                        help="Traffic source")
    parser.add_argument("--current-rate", type=float, required=True,
                        help="Current conversion rate as percentage")
    parser.add_argument("--industry", default="saas",
                        choices=["saas", "ecommerce", "fintech", "healthcare", "education"],
                        help="Industry for benchmarks (default: saas)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    result = calculate_benchmarks(args.page_type, args.traffic, args.current_rate,
                                  args.industry)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
