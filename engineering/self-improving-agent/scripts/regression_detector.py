#!/usr/bin/env python3
"""Regression Detector - Compare before/after performance metrics to detect regressions.

Compares two sets of performance data (baseline vs current) to identify
regressions caused by rule changes, memory updates, or other modifications
to the self-improving agent's knowledge base.

Input format (JSON file with baseline and current periods):
{
    "baseline": {
        "period": "2026-02-01 to 2026-02-15",
        "sessions": [
            {
                "session_id": "s1",
                "task_type": "code-review",
                "outcome": "SUCCESS",
                "corrections": 0,
                "turns": 4,
                "tool_calls": 12,
                "tool_errors": 0,
                "context_items_retrieved": 5,
                "context_items_used": 4
            }
        ]
    },
    "current": {
        "period": "2026-03-01 to 2026-03-15",
        "sessions": [ ... ]
    },
    "changes": [
        {"type": "rule_added", "description": "Added style guide enforcement rule"},
        {"type": "rule_promoted", "description": "Promoted pnpm preference to CLAUDE.md"}
    ]
}

Usage:
    python regression_detector.py compare --input metrics.json
    python regression_detector.py diagnose --input metrics.json --metric first_attempt_rate
    python regression_detector.py report --input metrics.json
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

# Thresholds from the SKILL.md regression detection framework
REGRESSION_THRESHOLDS = {
    "first_attempt_rate": {"direction": "higher_is_better", "warning": -0.05, "critical": -0.10},
    "success_rate": {"direction": "higher_is_better", "warning": -0.05, "critical": -0.10},
    "avg_corrections": {"direction": "lower_is_better", "warning": 0.5, "critical": 1.0},
    "tool_error_rate": {"direction": "lower_is_better", "warning": 0.02, "critical": 0.05},
    "avg_turns": {"direction": "lower_is_better", "warning": 2.0, "critical": 4.0},
    "context_relevance": {"direction": "higher_is_better", "warning": -0.10, "critical": -0.20},
}


def load_data(path: str) -> dict:
    """Load comparison data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def compute_metrics(sessions: list) -> dict:
    """Compute aggregate metrics from a list of sessions."""
    if not sessions:
        return {}

    total = len(sessions)
    successes = sum(1 for s in sessions if s.get("outcome") == "SUCCESS")
    first_attempt = sum(
        1 for s in sessions
        if s.get("outcome") == "SUCCESS" and s.get("corrections", 0) == 0
    )
    corrections = [s.get("corrections", 0) for s in sessions]
    turns = [s.get("turns", 0) for s in sessions]
    tool_calls = sum(s.get("tool_calls", 0) for s in sessions)
    tool_errors = sum(s.get("tool_errors", 0) for s in sessions)
    ctx_retrieved = sum(s.get("context_items_retrieved", 0) for s in sessions)
    ctx_used = sum(s.get("context_items_used", 0) for s in sessions)

    return {
        "total_sessions": total,
        "success_rate": round(successes / total, 4) if total else 0,
        "first_attempt_rate": round(first_attempt / total, 4) if total else 0,
        "avg_corrections": round(sum(corrections) / total, 3) if total else 0,
        "avg_turns": round(sum(turns) / total, 2) if total else 0,
        "tool_error_rate": round(tool_errors / tool_calls, 4) if tool_calls else 0,
        "context_relevance": round(ctx_used / ctx_retrieved, 4) if ctx_retrieved else 0,
        "outcome_distribution": {
            outcome: sum(1 for s in sessions if s.get("outcome") == outcome)
            for outcome in ["SUCCESS", "PARTIAL", "FAILURE", "REJECTION", "TIMEOUT", "ERROR"]
            if any(s.get("outcome") == outcome for s in sessions)
        },
    }


def compute_per_task_metrics(sessions: list) -> dict:
    """Compute metrics broken down by task type."""
    by_type = defaultdict(list)
    for s in sessions:
        by_type[s.get("task_type", "unknown")].append(s)
    return {tt: compute_metrics(ss) for tt, ss in by_type.items()}


def classify_delta(metric_name: str, delta: float) -> str:
    """Classify a metric delta as ok, warning, or critical."""
    threshold = REGRESSION_THRESHOLDS.get(metric_name)
    if not threshold:
        return "unknown"

    direction = threshold["direction"]
    if direction == "higher_is_better":
        effective_delta = delta  # negative = regression
    else:
        effective_delta = -delta  # positive = regression for lower-is-better

    if effective_delta <= threshold["critical"]:
        return "critical"
    elif effective_delta <= threshold["warning"]:
        return "warning"
    return "ok"


def cmd_compare(args, data: dict) -> dict:
    """Compare baseline vs current metrics and flag regressions."""
    baseline_metrics = compute_metrics(data["baseline"]["sessions"])
    current_metrics = compute_metrics(data["current"]["sessions"])

    comparisons = []
    regressions = []

    for metric in REGRESSION_THRESHOLDS:
        b_val = baseline_metrics.get(metric, 0)
        c_val = current_metrics.get(metric, 0)
        delta = c_val - b_val
        severity = classify_delta(metric, delta)

        entry = {
            "metric": metric,
            "baseline": b_val,
            "current": c_val,
            "delta": round(delta, 4),
            "severity": severity,
        }
        comparisons.append(entry)
        if severity in ("warning", "critical"):
            regressions.append(entry)

    # Per-task-type comparison
    baseline_by_task = compute_per_task_metrics(data["baseline"]["sessions"])
    current_by_task = compute_per_task_metrics(data["current"]["sessions"])
    all_tasks = set(list(baseline_by_task.keys()) + list(current_by_task.keys()))

    task_regressions = []
    for tt in sorted(all_tasks):
        b = baseline_by_task.get(tt, {})
        c = current_by_task.get(tt, {})
        b_rate = b.get("success_rate", 0)
        c_rate = c.get("success_rate", 0)
        delta = c_rate - b_rate
        if delta < -0.1:
            task_regressions.append({
                "task_type": tt,
                "baseline_success": b_rate,
                "current_success": c_rate,
                "delta": round(delta, 4),
            })

    return {
        "action": "compare",
        "baseline_period": data["baseline"].get("period", "unknown"),
        "current_period": data["current"].get("period", "unknown"),
        "baseline_sessions": baseline_metrics["total_sessions"],
        "current_sessions": current_metrics["total_sessions"],
        "comparisons": comparisons,
        "regressions": regressions,
        "task_regressions": task_regressions,
        "regression_detected": len(regressions) > 0,
        "changes_applied": data.get("changes", []),
    }


def cmd_diagnose(args, data: dict) -> dict:
    """Diagnose a specific metric regression by analyzing contributing factors."""
    metric = args.metric
    if metric not in REGRESSION_THRESHOLDS:
        return {"action": "diagnose", "error": f"Unknown metric: {metric}. Valid: {list(REGRESSION_THRESHOLDS.keys())}"}

    baseline_sessions = data["baseline"]["sessions"]
    current_sessions = data["current"]["sessions"]
    baseline_metrics = compute_metrics(baseline_sessions)
    current_metrics = compute_metrics(current_sessions)

    b_val = baseline_metrics.get(metric, 0)
    c_val = current_metrics.get(metric, 0)
    delta = c_val - b_val
    severity = classify_delta(metric, delta)

    # Identify which task types contributed most to the regression
    baseline_by_task = compute_per_task_metrics(baseline_sessions)
    current_by_task = compute_per_task_metrics(current_sessions)

    contributing_tasks = []
    for tt in set(list(baseline_by_task.keys()) + list(current_by_task.keys())):
        b = baseline_by_task.get(tt, {}).get(metric, 0)
        c = current_by_task.get(tt, {}).get(metric, 0)
        task_delta = c - b
        task_severity = classify_delta(metric, task_delta)
        if task_severity != "ok":
            contributing_tasks.append({
                "task_type": tt,
                "baseline": b,
                "current": c,
                "delta": round(task_delta, 4),
                "severity": task_severity,
            })

    contributing_tasks.sort(key=lambda x: abs(x["delta"]), reverse=True)

    # Generate recommendations
    recommendations = []
    changes = data.get("changes", [])

    if severity == "critical":
        recommendations.append("ROLLBACK: Consider reverting recent rule changes immediately")
    if contributing_tasks:
        top = contributing_tasks[0]
        recommendations.append(f"INVESTIGATE: '{top['task_type']}' tasks show largest regression ({top['delta']:+.2%})")
    if changes:
        recommendations.append(f"REVIEW: {len(changes)} changes applied between periods -- test each in isolation")
    recommendations.append(f"MONITOR: Track '{metric}' for next 3 sessions after any fix")

    return {
        "action": "diagnose",
        "metric": metric,
        "baseline_value": b_val,
        "current_value": c_val,
        "delta": round(delta, 4),
        "severity": severity,
        "contributing_tasks": contributing_tasks,
        "changes_between_periods": changes,
        "recommendations": recommendations,
    }


def cmd_report(args, data: dict) -> dict:
    """Generate a full regression report combining comparison and diagnosis."""
    compare_result = cmd_compare(args, data)

    diagnosed = []
    for reg in compare_result["regressions"]:
        diag_args = argparse.Namespace(metric=reg["metric"], input=args.input)
        diagnosis = cmd_diagnose(diag_args, data)
        diagnosed.append(diagnosis)

    overall_status = "PASS"
    if any(r["severity"] == "critical" for r in compare_result["regressions"]):
        overall_status = "CRITICAL"
    elif compare_result["regressions"]:
        overall_status = "WARNING"

    return {
        "action": "report",
        "overall_status": overall_status,
        "baseline_period": compare_result["baseline_period"],
        "current_period": compare_result["current_period"],
        "summary": {
            "total_metrics_checked": len(compare_result["comparisons"]),
            "regressions_found": len(compare_result["regressions"]),
            "critical_regressions": sum(1 for r in compare_result["regressions"] if r["severity"] == "critical"),
            "warning_regressions": sum(1 for r in compare_result["regressions"] if r["severity"] == "warning"),
            "task_type_regressions": len(compare_result["task_regressions"]),
        },
        "comparisons": compare_result["comparisons"],
        "diagnoses": diagnosed,
        "changes_applied": compare_result["changes_applied"],
        "generated_at": datetime.now().isoformat(),
    }


def format_human(result: dict) -> str:
    """Format result for human-readable output."""
    action = result.get("action", "unknown")
    lines = []

    if "error" in result:
        return f"Error: {result['error']}"

    if action == "compare":
        status = "REGRESSION DETECTED" if result["regression_detected"] else "NO REGRESSION"
        lines.append(f"Regression Comparison: {status}")
        lines.append(f"  Baseline: {result['baseline_period']} ({result['baseline_sessions']} sessions)")
        lines.append(f"  Current:  {result['current_period']} ({result['current_sessions']} sessions)")
        lines.append("")
        lines.append(f"{'Metric':<25} {'Baseline':>10} {'Current':>10} {'Delta':>10} {'Status':>10}")
        lines.append("-" * 70)
        for c in result["comparisons"]:
            indicator = {"ok": "  OK", "warning": " WARN", "critical": " CRIT"}.get(c["severity"], "  ?")
            lines.append(
                f"{c['metric']:<25} {c['baseline']:>10.4f} {c['current']:>10.4f} "
                f"{c['delta']:>+10.4f} {indicator:>10}"
            )
        if result["task_regressions"]:
            lines.append("")
            lines.append("Task-Level Regressions:")
            for tr in result["task_regressions"]:
                lines.append(f"  {tr['task_type']}: {tr['baseline_success']:.0%} -> {tr['current_success']:.0%} ({tr['delta']:+.1%})")
        if result["changes_applied"]:
            lines.append("")
            lines.append("Changes Applied Between Periods:")
            for ch in result["changes_applied"]:
                lines.append(f"  [{ch.get('type', '?')}] {ch.get('description', '')}")

    elif action == "diagnose":
        lines.append(f"Diagnosis: {result['metric']}")
        lines.append(f"  Severity: {result['severity'].upper()}")
        lines.append(f"  Baseline: {result['baseline_value']:.4f}")
        lines.append(f"  Current:  {result['current_value']:.4f}")
        lines.append(f"  Delta:    {result['delta']:+.4f}")
        if result["contributing_tasks"]:
            lines.append("")
            lines.append("Contributing Task Types:")
            for ct in result["contributing_tasks"]:
                lines.append(f"  {ct['task_type']}: {ct['baseline']:.4f} -> {ct['current']:.4f} ({ct['delta']:+.4f}) [{ct['severity']}]")
        if result["changes_between_periods"]:
            lines.append("")
            lines.append("Changes to Review:")
            for ch in result["changes_between_periods"]:
                lines.append(f"  [{ch.get('type', '?')}] {ch.get('description', '')}")
        lines.append("")
        lines.append("Recommendations:")
        for rec in result["recommendations"]:
            lines.append(f"  -> {rec}")

    elif action == "report":
        lines.append(f"{'=' * 60}")
        lines.append(f"  REGRESSION REPORT: {result['overall_status']}")
        lines.append(f"{'=' * 60}")
        lines.append(f"  Baseline: {result['baseline_period']}")
        lines.append(f"  Current:  {result['current_period']}")
        lines.append(f"  Generated: {result['generated_at'][:19]}")
        lines.append("")
        s = result["summary"]
        lines.append(f"  Metrics checked:          {s['total_metrics_checked']}")
        lines.append(f"  Regressions found:        {s['regressions_found']}")
        lines.append(f"    Critical:               {s['critical_regressions']}")
        lines.append(f"    Warning:                {s['warning_regressions']}")
        lines.append(f"  Task-type regressions:    {s['task_type_regressions']}")
        lines.append("")
        lines.append("Metric Details:")
        lines.append(f"  {'Metric':<25} {'Baseline':>10} {'Current':>10} {'Delta':>10} {'Status':>8}")
        lines.append("  " + "-" * 66)
        for c in result["comparisons"]:
            tag = {"ok": "OK", "warning": "WARN", "critical": "CRIT"}.get(c["severity"], "?")
            lines.append(
                f"  {c['metric']:<25} {c['baseline']:>10.4f} {c['current']:>10.4f} "
                f"{c['delta']:>+10.4f} {tag:>8}"
            )
        for diag in result.get("diagnoses", []):
            lines.append("")
            lines.append(f"  --- Diagnosis: {diag['metric']} [{diag['severity'].upper()}] ---")
            if diag.get("contributing_tasks"):
                for ct in diag["contributing_tasks"]:
                    lines.append(f"    {ct['task_type']}: {ct['delta']:+.4f} [{ct['severity']}]")
            for rec in diag.get("recommendations", []):
                lines.append(f"    -> {rec}")
        if result["changes_applied"]:
            lines.append("")
            lines.append("  Changes Applied:")
            for ch in result["changes_applied"]:
                lines.append(f"    [{ch.get('type', '?')}] {ch.get('description', '')}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Regression Detector - Compare before/after performance metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output in JSON format")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_compare = sub.add_parser("compare", help="Compare baseline vs current metrics")
    p_compare.add_argument("--input", required=True, help="Path to metrics JSON file")

    p_diagnose = sub.add_parser("diagnose", help="Diagnose a specific metric regression")
    p_diagnose.add_argument("--input", required=True, help="Path to metrics JSON file")
    p_diagnose.add_argument("--metric", required=True, choices=list(REGRESSION_THRESHOLDS.keys()),
                            help="Metric to diagnose")

    p_report = sub.add_parser("report", help="Generate full regression report")
    p_report.add_argument("--input", required=True, help="Path to metrics JSON file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    data = load_data(args.input)
    commands = {
        "compare": cmd_compare,
        "diagnose": cmd_diagnose,
        "report": cmd_report,
    }

    result = commands[args.command](args, data)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
