#!/usr/bin/env python3
"""
Pipeline Coverage Calculator - Calculate coverage ratios and analyze pipeline health.

Calculates pipeline coverage by quarter position, analyzes stage distribution,
detects deal aging risks, and generates adequacy assessments with action recommendations.

Usage:
    python pipeline_coverage_calculator.py --input pipeline_data.json
    python pipeline_coverage_calculator.py --input pipeline_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime, date


COVERAGE_TARGETS = {
    "q_minus_1": {"target": 4.0, "label": "Planning (Q-1)"},
    "q_start": {"target": 3.0, "label": "Quarter Start"},
    "mid_quarter": {"target": 2.0, "label": "Mid-Quarter"},
    "q_end": {"target": 1.5, "label": "Quarter End"},
}

STAGE_BENCHMARKS = {
    "lead": {"typical_conversion": 0.25, "max_age_days": 14},
    "discovery": {"typical_conversion": 0.55, "max_age_days": 21},
    "evaluation": {"typical_conversion": 0.45, "max_age_days": 30},
    "proposal": {"typical_conversion": 0.55, "max_age_days": 21},
    "negotiation": {"typical_conversion": 0.75, "max_age_days": 14},
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def calculate_coverage(pipeline_value, quota):
    """Calculate pipeline coverage ratio."""
    if quota <= 0:
        return 0
    return round(pipeline_value / quota, 2)


def assess_coverage(coverage, quarter_position):
    """Assess coverage adequacy based on quarter position."""
    target_config = COVERAGE_TARGETS.get(quarter_position, COVERAGE_TARGETS["q_start"])
    target = target_config["target"]

    if coverage >= target:
        return {"status": "Adequate", "gap": 0, "action": "Maintain pipeline generation pace"}
    elif coverage >= target * 0.75:
        gap = round((target - coverage) * 100, 0)  # as percentage of quota
        return {"status": "At Risk", "gap": gap, "action": "Accelerate top-of-funnel activity"}
    else:
        gap = round((target - coverage) * 100, 0)
        return {"status": "Critical", "gap": gap, "action": "Emergency pipeline generation -- all hands"}


def analyze_stage_distribution(deals, stages):
    """Analyze pipeline health by stage."""
    distribution = {}
    total_value = 0

    for stage_name in stages:
        stage_deals = [d for d in deals if d.get("stage", "").lower() == stage_name.lower()]
        stage_value = sum(d.get("value", 0) for d in stage_deals)
        total_value += stage_value

        # Aging analysis
        aged_deals = []
        benchmark = STAGE_BENCHMARKS.get(stage_name.lower(), {})
        max_age = benchmark.get("max_age_days", 30)

        for d in stage_deals:
            age = d.get("age_days", 0)
            if age > max_age:
                aged_deals.append({
                    "name": d.get("name", "Unknown"),
                    "value": d.get("value", 0),
                    "age_days": age,
                    "over_by": age - max_age,
                })

        distribution[stage_name] = {
            "deal_count": len(stage_deals),
            "total_value": stage_value,
            "avg_value": round(stage_value / max(len(stage_deals), 1), 0),
            "aged_deals": sorted(aged_deals, key=lambda x: x["over_by"], reverse=True),
            "aged_deal_count": len(aged_deals),
            "typical_conversion": benchmark.get("typical_conversion", 0),
        }

    # Add percentages
    for stage_name, info in distribution.items():
        info["value_pct"] = round((info["total_value"] / max(total_value, 1)) * 100, 1)

    return distribution, total_value


def calculate_weighted_pipeline(distribution):
    """Calculate probability-weighted pipeline value."""
    weighted = 0
    for stage_name, info in distribution.items():
        weighted += info["total_value"] * info["typical_conversion"]
    return round(weighted, 0)


def detect_concentration_risk(deals, threshold_pct=25):
    """Detect deal concentration risks."""
    total_value = sum(d.get("value", 0) for d in deals)
    if total_value == 0:
        return []

    risks = []
    for d in deals:
        pct = (d.get("value", 0) / total_value) * 100
        if pct >= threshold_pct:
            risks.append({
                "deal": d.get("name", "Unknown"),
                "value": d.get("value", 0),
                "pct_of_pipeline": round(pct, 1),
                "risk": f"Single deal is {round(pct, 1)}% of pipeline",
            })

    return risks


def analyze_pipeline(data):
    """Run full pipeline analysis."""
    deals = data.get("deals", [])
    quota = data.get("quota", 0)
    quarter_position = data.get("quarter_position", "q_start")
    stages = data.get("stages", ["lead", "discovery", "evaluation", "proposal", "negotiation"])
    company = data.get("company", "Company")

    total_pipeline = sum(d.get("value", 0) for d in deals)
    coverage = calculate_coverage(total_pipeline, quota)
    adequacy = assess_coverage(coverage, quarter_position)

    stage_distribution, _ = analyze_stage_distribution(deals, stages)
    weighted_pipeline = calculate_weighted_pipeline(stage_distribution)
    weighted_coverage = calculate_coverage(weighted_pipeline, quota)

    concentration_risks = detect_concentration_risk(deals)

    # Total aged deals
    total_aged = sum(info["aged_deal_count"] for info in stage_distribution.values())
    aged_value = sum(
        sum(d["value"] for d in info["aged_deals"])
        for info in stage_distribution.values()
    )

    results = {
        "timestamp": datetime.now().isoformat(),
        "company": company,
        "quarter_position": quarter_position,
        "quota": quota,
        "total_pipeline": total_pipeline,
        "coverage_ratio": coverage,
        "coverage_target": COVERAGE_TARGETS.get(quarter_position, {}).get("target", 3.0),
        "adequacy": adequacy,
        "weighted_pipeline": weighted_pipeline,
        "weighted_coverage": weighted_coverage,
        "deal_count": len(deals),
        "stage_distribution": stage_distribution,
        "aged_deals_count": total_aged,
        "aged_deals_value": aged_value,
        "concentration_risks": concentration_risks,
        "recommendations": [],
    }

    # Recommendations
    recs = results["recommendations"]
    if adequacy["status"] == "Critical":
        recs.append(f"CRITICAL: Coverage at {coverage}x vs {results['coverage_target']}x target -- emergency pipeline generation needed")
    elif adequacy["status"] == "At Risk":
        recs.append(f"AT RISK: Coverage at {coverage}x vs {results['coverage_target']}x target -- increase top-of-funnel activity")

    if weighted_coverage < 1.0:
        recs.append(f"Weighted coverage {weighted_coverage}x suggests likely quota miss even with all deals progressing normally")

    if total_aged > 0:
        recs.append(f"{total_aged} deals ({aged_value:,.0f} value) past stage age limits -- review for deal acceleration or removal")

    if concentration_risks:
        recs.append(f"{len(concentration_risks)} deal(s) represent concentration risk -- diversify pipeline")

    # Stage health
    for stage, info in stage_distribution.items():
        if info["deal_count"] == 0 and stage in ("discovery", "evaluation"):
            recs.append(f"No deals in {stage} stage -- pipeline gap developing")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "PIPELINE COVERAGE ANALYSIS",
        "=" * 60,
        f"Company: {results['company']}",
        f"Quarter Position: {results['quarter_position']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        "COVERAGE",
        f"  Quota: ${results['quota']:,.0f}",
        f"  Total Pipeline: ${results['total_pipeline']:,.0f}",
        f"  Coverage Ratio: {results['coverage_ratio']}x (target: {results['coverage_target']}x)",
        f"  Status: {results['adequacy']['status']}",
        f"  Weighted Pipeline: ${results['weighted_pipeline']:,.0f}",
        f"  Weighted Coverage: {results['weighted_coverage']}x",
        "",
        "STAGE DISTRIBUTION",
    ]

    for stage, info in results["stage_distribution"].items():
        lines.append(
            f"  {stage}: {info['deal_count']} deals, ${info['total_value']:,.0f} "
            f"({info['value_pct']}%), conv={info['typical_conversion']*100:.0f}%, "
            f"aged={info['aged_deal_count']}"
        )

    if results["aged_deals_count"] > 0:
        lines.append("")
        lines.append(f"AGING RISKS ({results['aged_deals_count']} deals, ${results['aged_deals_value']:,.0f})")
        for stage, info in results["stage_distribution"].items():
            for d in info["aged_deals"][:3]:
                lines.append(f"  {stage}: {d['name']} -- ${d['value']:,.0f}, {d['age_days']}d (over by {d['over_by']}d)")

    if results["concentration_risks"]:
        lines.append("")
        lines.append("CONCENTRATION RISKS")
        for r in results["concentration_risks"]:
            lines.append(f"  {r['deal']}: ${r['value']:,.0f} ({r['pct_of_pipeline']}% of pipeline)")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate pipeline coverage ratios and analyze pipeline health")
    parser.add_argument("--input", required=True, help="Path to JSON pipeline data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_pipeline(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
