#!/usr/bin/env python3
"""
Process Efficiency Scorer - Score process efficiency and identify bottlenecks.

Evaluates processes across cycle time, first-time completion, cost per transaction,
automation rate, error rate, and rework. Identifies bottlenecks and prioritizes
improvement opportunities using the Automation Priority Matrix.

Usage:
    python process_efficiency_scorer.py --input processes.json
    python process_efficiency_scorer.py --input processes.json --json
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def score_dimension(actual, target, lower_is_better=True):
    """Score a dimension 0-100."""
    if target == 0:
        return 50
    if lower_is_better:
        ratio = target / max(actual, 0.001)
    else:
        ratio = actual / max(target, 0.001)
    return max(0, min(100, round(ratio * 100, 1)))


def identify_bottlenecks(steps):
    """Identify bottleneck steps in a process."""
    if not steps:
        return []
    bottlenecks = []
    avg_time = sum(s.get("duration_hours", 0) for s in steps) / max(len(steps), 1)

    for step in steps:
        duration = step.get("duration_hours", 0)
        wait_time = step.get("wait_time_hours", 0)
        error_rate = step.get("error_rate_pct", 0)
        is_manual = step.get("is_manual", True)

        issues = []
        if duration > avg_time * 1.5:
            issues.append(f"Duration {duration}h exceeds avg {avg_time:.1f}h by {((duration/avg_time)-1)*100:.0f}%")
        if wait_time > duration * 0.5:
            issues.append(f"Wait time {wait_time}h is {(wait_time/max(duration,0.1))*100:.0f}% of step duration")
        if error_rate > 5:
            issues.append(f"Error rate {error_rate}% exceeds 5% threshold")
        if is_manual and duration > 2:
            issues.append("Manual step taking >2 hours -- automation candidate")

        if issues:
            bottlenecks.append({
                "step": step.get("name", "Unknown"),
                "severity": "high" if len(issues) >= 2 else "medium",
                "issues": issues,
                "duration_hours": duration,
                "wait_time_hours": wait_time,
                "is_manual": is_manual,
            })

    bottlenecks.sort(key=lambda x: 0 if x["severity"] == "high" else 1)
    return bottlenecks


def classify_automation_priority(value_score, effort_score):
    """Classify using the Automation Priority Matrix."""
    if value_score >= 60 and effort_score <= 40:
        return "Quick Win (Do First)"
    elif value_score >= 60 and effort_score > 40:
        return "Strategic Project (Plan Carefully)"
    elif value_score < 60 and effort_score <= 40:
        return "Fill-in (Do When Available)"
    else:
        return "Reconsider (May Not Be Worth It)"


def analyze_processes(data):
    """Analyze all processes."""
    processes = data.get("processes", [])
    org_name = data.get("organization", "Organization")

    results = {
        "timestamp": datetime.now().isoformat(),
        "organization": org_name,
        "process_count": len(processes),
        "processes": [],
        "overall_efficiency_score": 0,
        "top_bottlenecks": [],
        "automation_opportunities": [],
        "recommendations": [],
    }

    total_scores = []

    for proc in processes:
        name = proc.get("name", "Unknown Process")
        metrics = proc.get("metrics", {})
        steps = proc.get("steps", [])
        benchmarks = proc.get("benchmarks", {})

        # Score each dimension
        dimensions = {}
        dimension_list = [
            ("cycle_time", metrics.get("cycle_time_hours", 0), benchmarks.get("cycle_time_hours", 24), True),
            ("first_time_completion", metrics.get("first_time_completion_pct", 0), benchmarks.get("first_time_completion_pct", 90), False),
            ("cost_per_transaction", metrics.get("cost_per_transaction", 0), benchmarks.get("cost_per_transaction", 50), True),
            ("automation_rate", metrics.get("automation_rate_pct", 0), benchmarks.get("automation_rate_pct", 60), False),
            ("error_rate", metrics.get("error_rate_pct", 0), benchmarks.get("error_rate_pct", 2), True),
            ("rework_pct", metrics.get("rework_pct", 0), benchmarks.get("rework_pct", 5), True),
        ]

        for dim_name, actual, target, lower_better in dimension_list:
            score = score_dimension(actual, target, lower_better)
            dimensions[dim_name] = {
                "actual": actual,
                "target": target,
                "score": score,
            }

        avg_score = round(sum(d["score"] for d in dimensions.values()) / max(len(dimensions), 1), 1)
        total_scores.append(avg_score)

        # Identify bottlenecks
        bottlenecks = identify_bottlenecks(steps)

        # Automation opportunities from steps
        auto_opps = []
        for step in steps:
            if step.get("is_manual", True):
                volume = step.get("volume_per_month", 1)
                duration = step.get("duration_hours", 1)
                value_score = min(100, volume * duration / 10)
                effort_score = step.get("automation_effort", 50)
                priority = classify_automation_priority(value_score, effort_score)

                auto_opps.append({
                    "step": step.get("name", "Unknown"),
                    "process": name,
                    "value_score": round(value_score, 1),
                    "effort_score": effort_score,
                    "priority_class": priority,
                    "time_saved_hours": round(duration * 0.7, 1),
                })

        process_result = {
            "name": name,
            "overall_score": avg_score,
            "health": "Healthy" if avg_score >= 70 else ("At Risk" if avg_score >= 50 else "Critical"),
            "dimensions": dimensions,
            "bottleneck_count": len(bottlenecks),
            "bottlenecks": bottlenecks,
            "volume_per_month": proc.get("volume_per_month", 0),
            "owner": proc.get("owner", "Unassigned"),
        }
        results["processes"].append(process_result)
        results["top_bottlenecks"].extend(bottlenecks)
        results["automation_opportunities"].extend(auto_opps)

    # Overall score
    results["overall_efficiency_score"] = round(
        sum(total_scores) / max(len(total_scores), 1), 1
    )

    # Sort processes by score (worst first for prioritization)
    results["processes"].sort(key=lambda x: x["overall_score"])

    # Sort automation opportunities by value
    results["automation_opportunities"].sort(key=lambda x: x["value_score"], reverse=True)
    results["automation_opportunities"] = results["automation_opportunities"][:10]

    # Top bottlenecks
    results["top_bottlenecks"] = [b for b in results["top_bottlenecks"] if b["severity"] == "high"][:10]

    # Recommendations
    recs = results["recommendations"]
    critical = [p for p in results["processes"] if p["health"] == "Critical"]
    if critical:
        recs.append(f"PRIORITY: {len(critical)} process(es) in critical state -- immediate intervention needed")
    quick_wins = [a for a in results["automation_opportunities"] if "Quick Win" in a["priority_class"]]
    if quick_wins:
        recs.append(f"Automation: {len(quick_wins)} quick-win automation opportunities identified")
    if results["overall_efficiency_score"] < 50:
        recs.append("Overall efficiency below 50% -- consider dedicated process improvement initiative")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "PROCESS EFFICIENCY REPORT",
        "=" * 60,
        f"Organization: {results['organization']}",
        f"Processes Analyzed: {results['process_count']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        f"OVERALL EFFICIENCY: {results['overall_efficiency_score']}/100",
        "",
        "PROCESS SCORES (worst first)",
    ]

    for proc in results["processes"]:
        lines.append(f"\n  {proc['name']} -- {proc['overall_score']}/100 ({proc['health']})")
        lines.append(f"    Owner: {proc['owner']} | Volume: {proc['volume_per_month']}/mo | Bottlenecks: {proc['bottleneck_count']}")
        for dim_name, dim_data in proc["dimensions"].items():
            lines.append(f"      {dim_name}: {dim_data['actual']} (target: {dim_data['target']}, score: {dim_data['score']})")

    if results["top_bottlenecks"]:
        lines.append("")
        lines.append("TOP BOTTLENECKS (high severity)")
        for b in results["top_bottlenecks"][:5]:
            lines.append(f"  {b['step']} ({b['duration_hours']}h, wait: {b['wait_time_hours']}h)")
            for issue in b["issues"]:
                lines.append(f"    - {issue}")

    if results["automation_opportunities"]:
        lines.append("")
        lines.append("AUTOMATION OPPORTUNITIES")
        for a in results["automation_opportunities"][:5]:
            lines.append(f"  {a['step']} ({a['process']}): {a['priority_class']} -- saves ~{a['time_saved_hours']}h/occurrence")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score process efficiency and identify bottlenecks")
    parser.add_argument("--input", required=True, help="Path to JSON process data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_processes(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
