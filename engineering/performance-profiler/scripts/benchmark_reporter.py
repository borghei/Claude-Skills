#!/usr/bin/env python3
"""Benchmark Reporter — Parse benchmark results and generate comparison reports.

Reads JSON benchmark results (baseline and current), computes deltas,
detects regressions, and generates a formatted comparison report.

Input format: JSON with "baseline" and "current" keys, each containing
a list of benchmark entries with name, iterations, and timing metrics.
"""

import argparse
import json
import math
import sys
from collections import defaultdict


def parse_input(source):
    """Read JSON benchmark data from file or stdin."""
    if source == "-":
        raw = sys.stdin.read()
    else:
        with open(source, "r") as f:
            raw = f.read()

    data = json.loads(raw.strip())
    return data


def normalize_entries(entries):
    """Normalize benchmark entries into a consistent format."""
    by_name = {}
    for entry in entries:
        name = entry.get("name") or entry.get("benchmark") or entry.get("test", "unknown")
        by_name[name] = {
            "name": name,
            "iterations": entry.get("iterations") or entry.get("runs") or entry.get("n", 1),
            "mean_ms": entry.get("mean_ms") or entry.get("avg_ms") or entry.get("mean", 0),
            "median_ms": entry.get("median_ms") or entry.get("median", 0),
            "min_ms": entry.get("min_ms") or entry.get("min", 0),
            "max_ms": entry.get("max_ms") or entry.get("max", 0),
            "stddev_ms": entry.get("stddev_ms") or entry.get("stddev") or entry.get("sd", 0),
            "ops_per_sec": entry.get("ops_per_sec") or entry.get("ops_s") or entry.get("throughput", 0),
            "memory_mb": entry.get("memory_mb") or entry.get("memory") or entry.get("mem_mb", 0),
        }
    return by_name


def compute_delta(baseline_val, current_val):
    """Calculate percentage change. Negative means improvement for latency."""
    if baseline_val == 0:
        return 0.0 if current_val == 0 else float("inf")
    return ((current_val - baseline_val) / baseline_val) * 100


def classify_change(delta_pct, regression_threshold, improvement_threshold):
    """Classify a change as regression, improvement, or stable."""
    if delta_pct > regression_threshold:
        return "regression"
    elif delta_pct < -improvement_threshold:
        return "improvement"
    else:
        return "stable"


def compare_benchmarks(baseline, current, regression_pct, improvement_pct):
    """Compare baseline vs current benchmark results."""
    base_map = normalize_entries(baseline)
    curr_map = normalize_entries(current)

    all_names = sorted(set(list(base_map.keys()) + list(curr_map.keys())))

    comparisons = []
    for name in all_names:
        base = base_map.get(name)
        curr = curr_map.get(name)

        if base and curr:
            mean_delta = compute_delta(base["mean_ms"], curr["mean_ms"])
            median_delta = compute_delta(base["median_ms"], curr["median_ms"]) if base["median_ms"] else 0
            ops_delta = compute_delta(base["ops_per_sec"], curr["ops_per_sec"]) if base["ops_per_sec"] else 0
            mem_delta = compute_delta(base["memory_mb"], curr["memory_mb"]) if base["memory_mb"] else 0

            # For latency: positive delta = regression (slower)
            latency_status = classify_change(mean_delta, regression_pct, improvement_pct)
            # For ops/sec: negative delta = regression (lower throughput)
            ops_status = classify_change(-ops_delta, regression_pct, improvement_pct) if curr["ops_per_sec"] else "n/a"
            # For memory: positive delta = regression (more memory)
            mem_status = classify_change(mem_delta, regression_pct, improvement_pct) if curr["memory_mb"] else "n/a"

            comparisons.append({
                "name": name,
                "status": "compared",
                "baseline_mean_ms": base["mean_ms"],
                "current_mean_ms": curr["mean_ms"],
                "mean_delta_pct": round(mean_delta, 2),
                "baseline_median_ms": base["median_ms"],
                "current_median_ms": curr["median_ms"],
                "median_delta_pct": round(median_delta, 2),
                "baseline_ops_per_sec": base["ops_per_sec"],
                "current_ops_per_sec": curr["ops_per_sec"],
                "ops_delta_pct": round(ops_delta, 2),
                "baseline_memory_mb": base["memory_mb"],
                "current_memory_mb": curr["memory_mb"],
                "memory_delta_pct": round(mem_delta, 2),
                "latency_classification": latency_status,
                "throughput_classification": ops_status,
                "memory_classification": mem_status,
                "iterations": curr["iterations"],
                "current_stddev_ms": curr["stddev_ms"],
            })
        elif curr and not base:
            comparisons.append({
                "name": name,
                "status": "new",
                "current_mean_ms": curr["mean_ms"],
                "current_ops_per_sec": curr["ops_per_sec"],
                "current_memory_mb": curr["memory_mb"],
                "iterations": curr["iterations"],
                "latency_classification": "new",
            })
        elif base and not curr:
            comparisons.append({
                "name": name,
                "status": "removed",
                "baseline_mean_ms": base["mean_ms"],
                "latency_classification": "removed",
            })

    return comparisons


def build_report(comparisons, regression_pct):
    """Build the full report with summary statistics."""
    regressions = [c for c in comparisons if c.get("latency_classification") == "regression"]
    improvements = [c for c in comparisons if c.get("latency_classification") == "improvement"]
    stable = [c for c in comparisons if c.get("latency_classification") == "stable"]
    new_benchmarks = [c for c in comparisons if c.get("status") == "new"]
    removed = [c for c in comparisons if c.get("status") == "removed"]

    has_regressions = len(regressions) > 0
    worst_regression = max((c["mean_delta_pct"] for c in regressions), default=0)
    best_improvement = min((c["mean_delta_pct"] for c in improvements), default=0)

    return {
        "summary": {
            "total_benchmarks": len(comparisons),
            "compared": len([c for c in comparisons if c["status"] == "compared"]),
            "regressions": len(regressions),
            "improvements": len(improvements),
            "stable": len(stable),
            "new": len(new_benchmarks),
            "removed": len(removed),
            "has_regressions": has_regressions,
            "regression_threshold_pct": regression_pct,
            "worst_regression_pct": round(worst_regression, 2),
            "best_improvement_pct": round(best_improvement, 2),
            "verdict": "FAIL" if has_regressions else "PASS",
        },
        "regressions": regressions,
        "improvements": improvements,
        "stable": stable,
        "new_benchmarks": new_benchmarks,
        "removed_benchmarks": removed,
        "all_comparisons": comparisons,
    }


def format_delta(delta_pct):
    """Format delta with sign and color hint."""
    if delta_pct > 0:
        return f"+{delta_pct:.2f}%"
    elif delta_pct < 0:
        return f"{delta_pct:.2f}%"
    return "0.00%"


def format_human(report):
    """Format the report as human-readable text."""
    lines = []
    s = report["summary"]
    verdict_marker = "FAIL" if s["verdict"] == "FAIL" else "PASS"

    lines.append("=" * 72)
    lines.append(f"BENCHMARK COMPARISON REPORT                         [{verdict_marker}]")
    lines.append("=" * 72)
    lines.append(f"Total benchmarks: {s['total_benchmarks']}  |  Compared: {s['compared']}  |  New: {s['new']}  |  Removed: {s['removed']}")
    lines.append(f"Regression threshold: {s['regression_threshold_pct']}%")
    lines.append(f"Regressions: {s['regressions']}  |  Improvements: {s['improvements']}  |  Stable: {s['stable']}")
    if s["worst_regression_pct"] > 0:
        lines.append(f"Worst regression: {format_delta(s['worst_regression_pct'])}")
    if s["best_improvement_pct"] < 0:
        lines.append(f"Best improvement: {format_delta(s['best_improvement_pct'])}")
    lines.append("")

    if report["regressions"]:
        lines.append("-" * 72)
        lines.append("REGRESSIONS (performance degraded)")
        lines.append("-" * 72)
        for c in sorted(report["regressions"], key=lambda x: x["mean_delta_pct"], reverse=True):
            lines.append(f"  [REGRESS] {c['name']}")
            lines.append(f"            Mean: {c['baseline_mean_ms']:.2f}ms -> {c['current_mean_ms']:.2f}ms ({format_delta(c['mean_delta_pct'])})")
            if c.get("current_ops_per_sec"):
                lines.append(f"            Ops/s: {c['baseline_ops_per_sec']:.0f} -> {c['current_ops_per_sec']:.0f} ({format_delta(c['ops_delta_pct'])})")
            if c.get("current_memory_mb"):
                lines.append(f"            Memory: {c['baseline_memory_mb']:.1f}MB -> {c['current_memory_mb']:.1f}MB ({format_delta(c['memory_delta_pct'])})")
        lines.append("")

    if report["improvements"]:
        lines.append("-" * 72)
        lines.append("IMPROVEMENTS (performance improved)")
        lines.append("-" * 72)
        for c in sorted(report["improvements"], key=lambda x: x["mean_delta_pct"]):
            lines.append(f"  [IMPROVE] {c['name']}")
            lines.append(f"            Mean: {c['baseline_mean_ms']:.2f}ms -> {c['current_mean_ms']:.2f}ms ({format_delta(c['mean_delta_pct'])})")
            if c.get("current_ops_per_sec"):
                lines.append(f"            Ops/s: {c['baseline_ops_per_sec']:.0f} -> {c['current_ops_per_sec']:.0f} ({format_delta(c['ops_delta_pct'])})")
        lines.append("")

    if report["stable"]:
        lines.append("-" * 72)
        lines.append("STABLE (within threshold)")
        lines.append("-" * 72)
        for c in sorted(report["stable"], key=lambda x: x["name"]):
            lines.append(f"  [STABLE ] {c['name']}  |  Mean: {c['current_mean_ms']:.2f}ms ({format_delta(c['mean_delta_pct'])})")
        lines.append("")

    if report["new_benchmarks"]:
        lines.append("-" * 72)
        lines.append("NEW BENCHMARKS (no baseline)")
        lines.append("-" * 72)
        for c in report["new_benchmarks"]:
            lines.append(f"  [NEW    ] {c['name']}  |  Mean: {c['current_mean_ms']:.2f}ms")
        lines.append("")

    if report["removed_benchmarks"]:
        lines.append("-" * 72)
        lines.append("REMOVED BENCHMARKS (no longer present)")
        lines.append("-" * 72)
        for c in report["removed_benchmarks"]:
            lines.append(f"  [REMOVED] {c['name']}  |  Was: {c['baseline_mean_ms']:.2f}ms")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Parse benchmark results and generate comparison reports with regression detection.",
        epilog='Input: JSON with "baseline" and "current" arrays of benchmark entries.',
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input file path or '-' for stdin (default: stdin)")
    parser.add_argument("--regression-threshold", type=float, default=5.0,
                        help="Percentage increase in latency to flag as regression (default: 5.0)")
    parser.add_argument("--improvement-threshold", type=float, default=5.0,
                        help="Percentage decrease in latency to flag as improvement (default: 5.0)")
    parser.add_argument("--fail-on-regression", action="store_true",
                        help="Exit with code 1 if any regressions are detected (useful for CI)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    try:
        data = parse_input(args.input)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    baseline = data.get("baseline") or data.get("before") or []
    current = data.get("current") or data.get("after") or data.get("results") or []

    if not baseline:
        print("Error: no baseline benchmark data found (expected 'baseline' or 'before' key)", file=sys.stderr)
        sys.exit(1)
    if not current:
        print("Error: no current benchmark data found (expected 'current' or 'after' key)", file=sys.stderr)
        sys.exit(1)

    comparisons = compare_benchmarks(baseline, current, args.regression_threshold, args.improvement_threshold)
    report = build_report(comparisons, args.regression_threshold)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_human(report))

    if args.fail_on_regression and report["summary"]["has_regressions"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
