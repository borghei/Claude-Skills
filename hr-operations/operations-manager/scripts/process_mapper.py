#!/usr/bin/env python3
"""
Process Mapper - Map and analyze business processes for optimization.

Reads a CSV of process steps and produces a process analysis including
cycle time calculation, bottleneck identification, handoff analysis,
value-add vs non-value-add classification, and improvement recommendations.

Usage:
    python process_mapper.py --file process_steps.csv
    python process_mapper.py --file process_steps.csv --json
    python process_mapper.py --file process_steps.csv --target-cycle 480

Input CSV columns:
    step_id         - Step sequence number or ID
    step_name       - Name/description of the step
    owner           - Role or team responsible
    duration_min    - Average duration in minutes
    wait_time_min   - Average wait/queue time before this step (minutes)
    type            - Step type: process, decision, handoff, rework, inspection
    value_add       - Is this step value-adding? (yes/no)
    error_rate_pct  - Error/rework rate at this step (percentage, optional)
    automation      - Automation level: manual, semi-auto, automated (optional)
    notes           - Additional notes (optional)

Output: Process analysis with cycle time, bottlenecks, efficiency metrics, and recommendations.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict


def read_csv(path: str) -> list:
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {"step_id", "step_name", "duration_min"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            print(f"Error: Missing required columns: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    return rows


def safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def analyze_process(steps: list, target_cycle: float = None) -> dict:
    """Analyze process steps."""
    total_duration = 0
    total_wait = 0
    total_steps = len(steps)
    value_add_time = 0
    non_value_add_time = 0
    handoffs = 0
    decisions = 0
    rework_steps = 0
    manual_steps = 0
    errors_weighted = 0

    step_details = []
    owners = set()
    prev_owner = None

    for step in steps:
        duration = safe_float(step.get("duration_min", 0))
        wait = safe_float(step.get("wait_time_min", 0))
        error_rate = safe_float(step.get("error_rate_pct", 0))
        step_type = step.get("type", "process").strip().lower()
        is_value_add = step.get("value_add", "yes").strip().lower() in ("yes", "true", "1", "y")
        automation = step.get("automation", "manual").strip().lower()
        owner = step.get("owner", "Unknown").strip()

        total_duration += duration
        total_wait += wait

        if is_value_add:
            value_add_time += duration
        else:
            non_value_add_time += duration

        if step_type == "handoff" or (prev_owner and owner != prev_owner):
            handoffs += 1
        if step_type == "decision":
            decisions += 1
        if step_type == "rework":
            rework_steps += 1
        if automation == "manual":
            manual_steps += 1

        errors_weighted += duration * error_rate / 100
        owners.add(owner)
        prev_owner = owner

        # Cycle time contribution
        step_cycle = duration + wait
        cycle_pct = 0  # Will calculate after totals

        step_details.append({
            "step_id": step.get("step_id", ""),
            "step_name": step.get("step_name", ""),
            "owner": owner,
            "duration_min": duration,
            "wait_time_min": wait,
            "total_time_min": step_cycle,
            "type": step_type,
            "value_add": is_value_add,
            "error_rate_pct": error_rate,
            "automation": automation,
        })

    total_cycle = total_duration + total_wait

    # Calculate percentages
    for sd in step_details:
        sd["cycle_pct"] = round(sd["total_time_min"] / max(1, total_cycle) * 100, 1)

    # Process efficiency
    process_efficiency = round(value_add_time / max(1, total_duration) * 100, 1)
    flow_efficiency = round(value_add_time / max(1, total_cycle) * 100, 1)

    return {
        "total_steps": total_steps,
        "total_duration_min": round(total_duration, 1),
        "total_wait_time_min": round(total_wait, 1),
        "total_cycle_time_min": round(total_cycle, 1),
        "total_cycle_time_hours": round(total_cycle / 60, 2),
        "target_cycle_min": target_cycle,
        "cycle_gap_min": round(total_cycle - target_cycle, 1) if target_cycle else None,
        "cycle_gap_pct": round((total_cycle - target_cycle) / target_cycle * 100, 1) if target_cycle else None,
        "value_add_time_min": round(value_add_time, 1),
        "non_value_add_time_min": round(non_value_add_time, 1),
        "process_efficiency_pct": process_efficiency,
        "flow_efficiency_pct": flow_efficiency,
        "handoffs": handoffs,
        "decisions": decisions,
        "rework_steps": rework_steps,
        "manual_steps": manual_steps,
        "unique_owners": len(owners),
        "owners": sorted(owners),
        "steps": step_details,
    }


def identify_bottlenecks(analysis: dict) -> list:
    """Identify process bottlenecks."""
    bottlenecks = []
    steps = analysis["steps"]
    avg_duration = analysis["total_duration_min"] / max(1, analysis["total_steps"])
    avg_wait = analysis["total_wait_time_min"] / max(1, analysis["total_steps"])

    for step in steps:
        issues = []

        # Long duration (> 2x average)
        if step["duration_min"] > avg_duration * 2:
            issues.append(f"Duration {step['duration_min']:.0f} min is {step['duration_min']/max(1,avg_duration):.1f}x the average")

        # Long wait time (> 2x average)
        if step["wait_time_min"] > avg_wait * 2 and step["wait_time_min"] > 30:
            issues.append(f"Wait time {step['wait_time_min']:.0f} min is {step['wait_time_min']/max(1,avg_wait):.1f}x the average")

        # High error rate
        if step["error_rate_pct"] > 5:
            issues.append(f"Error rate {step['error_rate_pct']:.1f}% exceeds 5% threshold")

        # Large cycle contribution
        if step["cycle_pct"] > 25:
            issues.append(f"Accounts for {step['cycle_pct']:.1f}% of total cycle time")

        if issues:
            severity = "HIGH" if len(issues) >= 2 or step["cycle_pct"] > 30 else "MEDIUM"
            bottlenecks.append({
                "step_id": step["step_id"],
                "step_name": step["step_name"],
                "owner": step["owner"],
                "severity": severity,
                "issues": issues,
                "duration_min": step["duration_min"],
                "wait_time_min": step["wait_time_min"],
                "cycle_pct": step["cycle_pct"],
            })

    bottlenecks.sort(key=lambda x: x["cycle_pct"], reverse=True)
    return bottlenecks


def compute_owner_analysis(analysis: dict) -> list:
    """Analyze workload by owner/team."""
    owner_data = defaultdict(lambda: {"steps": 0, "duration": 0, "wait": 0, "errors_weighted": 0})

    for step in analysis["steps"]:
        owner = step["owner"]
        owner_data[owner]["steps"] += 1
        owner_data[owner]["duration"] += step["duration_min"]
        owner_data[owner]["wait"] += step["wait_time_min"]
        owner_data[owner]["errors_weighted"] += step["duration_min"] * step["error_rate_pct"] / 100

    results = []
    for owner, data in sorted(owner_data.items()):
        total_time = data["duration"] + data["wait"]
        results.append({
            "owner": owner,
            "steps": data["steps"],
            "duration_min": round(data["duration"], 1),
            "wait_time_min": round(data["wait"], 1),
            "total_time_min": round(total_time, 1),
            "pct_of_cycle": round(total_time / max(1, analysis["total_cycle_time_min"]) * 100, 1),
        })

    results.sort(key=lambda x: x["total_time_min"], reverse=True)
    return results


def build_recommendations(analysis: dict, bottlenecks: list) -> list:
    """Generate improvement recommendations."""
    recs = []

    # Flow efficiency
    if analysis["flow_efficiency_pct"] < 25:
        recs.append(
            f"Flow efficiency is {analysis['flow_efficiency_pct']:.1f}% (target: >25%). "
            f"Total wait time ({analysis['total_wait_time_min']:.0f} min) exceeds processing time. "
            "Focus on reducing queue and handoff delays between steps."
        )

    # Handoffs
    if analysis["handoffs"] > analysis["total_steps"] * 0.3:
        recs.append(
            f"Process has {analysis['handoffs']} handoffs across {analysis['unique_owners']} owners. "
            "Consider consolidating steps under fewer owners to reduce handoff delays and communication overhead."
        )

    # Manual steps
    manual_pct = analysis["manual_steps"] / max(1, analysis["total_steps"]) * 100
    if manual_pct > 60:
        recs.append(
            f"{analysis['manual_steps']}/{analysis['total_steps']} steps ({manual_pct:.0f}%) are manual. "
            "Identify repetitive, rule-based steps for automation to reduce cycle time and error rates."
        )

    # Top bottlenecks
    high_bottlenecks = [b for b in bottlenecks if b["severity"] == "HIGH"]
    for bn in high_bottlenecks[:2]:
        recs.append(
            f"Bottleneck at '{bn['step_name']}' ({bn['cycle_pct']:.1f}% of cycle): "
            + "; ".join(bn["issues"][:2]) + ". "
            "Apply 5 Whys root cause analysis to this step."
        )

    # Non-value-add
    nva_pct = analysis["non_value_add_time_min"] / max(1, analysis["total_duration_min"]) * 100
    if nva_pct > 30:
        recs.append(
            f"Non-value-add activities account for {nva_pct:.0f}% of processing time. "
            "Review each non-value-add step: can it be eliminated, combined, or automated?"
        )

    # Target gap
    if analysis.get("cycle_gap_min") and analysis["cycle_gap_min"] > 0:
        recs.append(
            f"Current cycle time ({analysis['total_cycle_time_min']:.0f} min) exceeds target "
            f"({analysis['target_cycle_min']:.0f} min) by {analysis['cycle_gap_pct']:.1f}%. "
            "Address the top bottlenecks above to close the gap."
        )

    if not recs:
        recs.append("Process metrics are within acceptable ranges. Consider incremental improvements through Kaizen events.")

    return recs


def format_human(analysis: dict, bottlenecks: list, owners: list, recommendations: list) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("PROCESS ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  Total Steps:           {analysis['total_steps']}")
    lines.append(f"  Processing Time:       {analysis['total_duration_min']:.0f} min ({analysis['total_duration_min']/60:.1f} hrs)")
    lines.append(f"  Wait/Queue Time:       {analysis['total_wait_time_min']:.0f} min ({analysis['total_wait_time_min']/60:.1f} hrs)")
    lines.append(f"  Total Cycle Time:      {analysis['total_cycle_time_min']:.0f} min ({analysis['total_cycle_time_hours']:.1f} hrs)")
    if analysis.get("target_cycle_min"):
        lines.append(f"  Target Cycle Time:     {analysis['target_cycle_min']:.0f} min")
        lines.append(f"  Gap:                   {analysis['cycle_gap_min']:+.0f} min ({analysis['cycle_gap_pct']:+.1f}%)")
    lines.append(f"  Flow Efficiency:       {analysis['flow_efficiency_pct']:.1f}%")
    lines.append(f"  Process Efficiency:    {analysis['process_efficiency_pct']:.1f}%")
    lines.append(f"  Handoffs:              {analysis['handoffs']}")
    lines.append(f"  Unique Owners:         {analysis['unique_owners']}")
    lines.append(f"  Manual Steps:          {analysis['manual_steps']}/{analysis['total_steps']}")

    # Step-by-step map
    lines.append("")
    lines.append("-" * 70)
    lines.append("PROCESS MAP")
    lines.append("-" * 70)
    lines.append(f"  {'#':<4} {'Step':<25} {'Owner':<15} {'Dur':>5} {'Wait':>5} {'Err%':>5} {'%Cyc':>5} {'VA':>3}")
    lines.append(f"  {'-'*4} {'-'*25} {'-'*15} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*3}")
    for step in analysis["steps"]:
        va = "Y" if step["value_add"] else "N"
        lines.append(
            f"  {step['step_id']:<4} {step['step_name']:<25} {step['owner']:<15} "
            f"{step['duration_min']:>5.0f} {step['wait_time_min']:>5.0f} {step['error_rate_pct']:>5.1f} "
            f"{step['cycle_pct']:>5.1f} {va:>3}"
        )

    # Owner analysis
    lines.append("")
    lines.append("-" * 70)
    lines.append("WORKLOAD BY OWNER")
    lines.append("-" * 70)
    lines.append(f"  {'Owner':<20} {'Steps':>6} {'Dur (min)':>10} {'Wait (min)':>10} {'% Cycle':>8}")
    lines.append(f"  {'-'*20} {'-'*6} {'-'*10} {'-'*10} {'-'*8}")
    for o in owners:
        lines.append(f"  {o['owner']:<20} {o['steps']:>6} {o['duration_min']:>10.0f} {o['wait_time_min']:>10.0f} {o['pct_of_cycle']:>7.1f}%")

    # Bottlenecks
    if bottlenecks:
        lines.append("")
        lines.append("-" * 70)
        lines.append("BOTTLENECKS")
        lines.append("-" * 70)
        for bn in bottlenecks:
            lines.append(f"\n  [{bn['severity']}] Step {bn['step_id']}: {bn['step_name']} ({bn['cycle_pct']:.1f}% of cycle)")
            for issue in bn["issues"]:
                lines.append(f"    - {issue}")

    # Recommendations
    lines.append("")
    lines.append("-" * 70)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 70)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Map and analyze business processes for optimization opportunities."
    )
    parser.add_argument("--file", required=True, help="Path to process steps CSV")
    parser.add_argument("--target-cycle", type=float, default=None, help="Target cycle time in minutes")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    steps = read_csv(args.file)
    if not steps:
        print("Error: No data found in CSV file.", file=sys.stderr)
        sys.exit(1)

    analysis = analyze_process(steps, args.target_cycle)
    bottlenecks = identify_bottlenecks(analysis)
    owners = compute_owner_analysis(analysis)
    recommendations = build_recommendations(analysis, bottlenecks)

    if args.json:
        output = {
            "process_summary": {k: v for k, v in analysis.items() if k != "steps"},
            "steps": analysis["steps"],
            "bottlenecks": bottlenecks,
            "owner_analysis": owners,
            "recommendations": recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(analysis, bottlenecks, owners, recommendations))


if __name__ == "__main__":
    main()
