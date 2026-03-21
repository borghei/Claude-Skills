#!/usr/bin/env python3
"""Funnel Drop-Off Analyzer - Analyze conversion funnels and identify drop-off points.

Reads funnel stage data (stage name + count), calculates stage-to-stage conversion
rates, identifies the biggest drop-off points, and suggests investigation priorities.

Usage:
    python funnel_drop_off_analyzer.py funnel_data.json
    python funnel_drop_off_analyzer.py funnel_data.json --json
    python funnel_drop_off_analyzer.py --stages "Visitors:10000,Signups:1200,Activated:480,Paid:120"
"""

import argparse
import json
import sys
import math


def parse_stages_string(stages_str):
    """Parse stages from a comma-separated string like 'Name:Count,Name:Count'."""
    stages = []
    for pair in stages_str.split(","):
        pair = pair.strip()
        if ":" not in pair:
            raise ValueError(f"Invalid stage format: '{pair}'. Use 'Name:Count'")
        name, count = pair.rsplit(":", 1)
        stages.append({"name": name.strip(), "count": int(count.strip())})
    return stages


def analyze_funnel(stages):
    """Analyze funnel stages and return detailed metrics."""
    if len(stages) < 2:
        return {"error": "Need at least 2 stages for funnel analysis"}

    results = []
    total_entry = stages[0]["count"]

    for i, stage in enumerate(stages):
        entry = {
            "stage": stage["name"],
            "count": stage["count"],
            "cumulative_conversion": (stage["count"] / total_entry * 100) if total_entry > 0 else 0,
        }

        if i > 0:
            prev_count = stages[i - 1]["count"]
            drop_off = prev_count - stage["count"]
            conversion_rate = (stage["count"] / prev_count * 100) if prev_count > 0 else 0
            drop_off_rate = 100 - conversion_rate

            entry["from_stage"] = stages[i - 1]["name"]
            entry["drop_off_count"] = drop_off
            entry["stage_conversion_rate"] = round(conversion_rate, 2)
            entry["drop_off_rate"] = round(drop_off_rate, 2)
            entry["drop_off_pct_of_total"] = round(
                (drop_off / total_entry * 100) if total_entry > 0 else 0, 2
            )

        results.append(entry)

    # Find biggest drop-off points
    drop_offs = [r for r in results if "drop_off_rate" in r]
    if drop_offs:
        # By absolute count
        biggest_absolute = max(drop_offs, key=lambda x: x["drop_off_count"])
        # By rate
        biggest_rate = max(drop_offs, key=lambda x: x["drop_off_rate"])
    else:
        biggest_absolute = None
        biggest_rate = None

    # Calculate overall metrics
    overall_conversion = (stages[-1]["count"] / total_entry * 100) if total_entry > 0 else 0

    # Benchmark comparison
    benchmarks = {
        "overall": {"good": 5.0, "average": 2.5, "poor": 1.0},
        "stage": {"good": 70.0, "average": 50.0, "poor": 30.0},
    }

    # Generate recommendations
    recommendations = []
    for r in drop_offs:
        if r["drop_off_rate"] > 70:
            recommendations.append({
                "priority": "critical",
                "stage": f"{r['from_stage']} -> {r['stage']}",
                "drop_off_rate": r["drop_off_rate"],
                "recommendation": f"Critical drop-off ({r['drop_off_rate']:.1f}%). "
                f"Investigate {r['stage'].lower()} experience immediately. "
                f"Check for UX friction, unclear value proposition, or technical issues.",
            })
        elif r["drop_off_rate"] > 50:
            recommendations.append({
                "priority": "high",
                "stage": f"{r['from_stage']} -> {r['stage']}",
                "drop_off_rate": r["drop_off_rate"],
                "recommendation": f"High drop-off ({r['drop_off_rate']:.1f}%). "
                f"Review {r['stage'].lower()} step for friction. "
                f"Consider A/B testing simplified flow or adding social proof.",
            })
        elif r["drop_off_rate"] > 30:
            recommendations.append({
                "priority": "medium",
                "stage": f"{r['from_stage']} -> {r['stage']}",
                "drop_off_rate": r["drop_off_rate"],
                "recommendation": f"Moderate drop-off ({r['drop_off_rate']:.1f}%). "
                f"Optimize {r['stage'].lower()} with better copy, clearer CTAs, or incentives.",
            })

    # Revenue impact estimation
    revenue_impact = []
    for r in drop_offs:
        if r["drop_off_rate"] > 30:
            # If we improve this stage by 10%, how many more reach the end?
            improvement_pct = 10
            additional_passed = int(r["drop_off_count"] * improvement_pct / 100)
            # Estimate downstream conversion
            downstream_rate = (stages[-1]["count"] / r["count"]) if r["count"] > 0 else 0
            additional_final = int(additional_passed * downstream_rate)
            revenue_impact.append({
                "stage": f"{r['from_stage']} -> {r['stage']}",
                "improvement_scenario": f"10% improvement",
                "additional_users_passed": additional_passed,
                "estimated_additional_conversions": additional_final,
            })

    return {
        "stages": results,
        "summary": {
            "total_stages": len(stages),
            "entry_count": total_entry,
            "exit_count": stages[-1]["count"],
            "overall_conversion_rate": round(overall_conversion, 2),
            "biggest_drop_off_absolute": {
                "stage": f"{biggest_absolute['from_stage']} -> {biggest_absolute['stage']}",
                "count": biggest_absolute["drop_off_count"],
                "rate": biggest_absolute["drop_off_rate"],
            } if biggest_absolute else None,
            "biggest_drop_off_rate": {
                "stage": f"{biggest_rate['from_stage']} -> {biggest_rate['stage']}",
                "count": biggest_rate["drop_off_count"],
                "rate": biggest_rate["drop_off_rate"],
            } if biggest_rate else None,
        },
        "recommendations": sorted(recommendations, key=lambda x: x["drop_off_rate"], reverse=True),
        "revenue_impact": revenue_impact,
    }


def format_report(analysis):
    """Format human-readable funnel report."""
    lines = []
    lines.append("=" * 65)
    lines.append("FUNNEL DROP-OFF ANALYSIS")
    lines.append("=" * 65)

    summary = analysis["summary"]
    lines.append(f"Stages:              {summary['total_stages']}")
    lines.append(f"Entry count:         {summary['entry_count']:,}")
    lines.append(f"Final count:         {summary['exit_count']:,}")
    lines.append(f"Overall conversion:  {summary['overall_conversion_rate']:.2f}%")
    lines.append("")

    # Stage breakdown
    lines.append("--- STAGE BREAKDOWN ---")
    lines.append(f"{'Stage':<25} {'Count':>10} {'Conv %':>8} {'Drop-off':>10} {'Drop %':>8}")
    lines.append("-" * 65)

    for stage in analysis["stages"]:
        conv = f"{stage.get('stage_conversion_rate', 100):.1f}%" if "stage_conversion_rate" in stage else "entry"
        drop = f"{stage.get('drop_off_count', 0):,}" if "drop_off_count" in stage else "-"
        drop_pct = f"{stage.get('drop_off_rate', 0):.1f}%" if "drop_off_rate" in stage else "-"
        lines.append(f"{stage['stage']:<25} {stage['count']:>10,} {conv:>8} {drop:>10} {drop_pct:>8}")

    lines.append("")

    # Biggest drop-offs
    if summary.get("biggest_drop_off_absolute"):
        lines.append("--- BIGGEST DROP-OFFS ---")
        ba = summary["biggest_drop_off_absolute"]
        lines.append(f"  By count: {ba['stage']} ({ba['count']:,} users lost, {ba['rate']:.1f}%)")
        br = summary["biggest_drop_off_rate"]
        if br["stage"] != ba["stage"]:
            lines.append(f"  By rate:  {br['stage']} ({br['count']:,} users lost, {br['rate']:.1f}%)")
        lines.append("")

    # Recommendations
    if analysis["recommendations"]:
        lines.append("--- RECOMMENDATIONS ---")
        for rec in analysis["recommendations"]:
            priority_marker = {"critical": "!!!", "high": "!!", "medium": "!"}.get(rec["priority"], "")
            lines.append(f"  [{rec['priority'].upper()}] {priority_marker} {rec['recommendation']}")
        lines.append("")

    # Revenue impact
    if analysis["revenue_impact"]:
        lines.append("--- REVENUE IMPACT SCENARIOS ---")
        for impact in analysis["revenue_impact"]:
            lines.append(
                f"  {impact['stage']}: {impact['improvement_scenario']} -> "
                f"+{impact['additional_users_passed']:,} pass through, "
                f"+{impact['estimated_additional_conversions']:,} final conversions"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze conversion funnels and identify drop-off points"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file with funnel stages [{name, count}, ...]",
    )
    parser.add_argument(
        "--stages",
        help='Inline stages: "Visitors:10000,Signups:1200,Paid:120"',
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    args = parser.parse_args()

    if not args.input and not args.stages:
        parser.print_help()
        sys.exit(1)

    if args.stages:
        try:
            stages = parse_stages_string(args.stages)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            stages = data if isinstance(data, list) else data.get("stages", data.get("funnel", []))
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    analysis = analyze_funnel(stages)

    if "error" in analysis:
        print(f"Error: {analysis['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
