#!/usr/bin/env python3
"""Feedback Analyzer - Analyze feedback logs to extract patterns and improvement opportunities.

Reads feedback log files (JSON or JSONL format) containing agent session outcomes,
and produces analysis of success rates, failure patterns, and actionable improvement
recommendations based on the Self-Improving Agent feedback loop model.

Expected log entry format:
{
    "session_id": "abc123",
    "timestamp": "2026-03-15T10:30:00",
    "task_type": "code-review",
    "outcome": "SUCCESS|PARTIAL|FAILURE|REJECTION|TIMEOUT|ERROR",
    "corrections": 0,
    "turns": 5,
    "tools_used": ["Read", "Edit", "Bash"],
    "tool_errors": 0,
    "notes": "optional description"
}

Usage:
    python feedback_analyzer.py analyze --input feedback.jsonl
    python feedback_analyzer.py patterns --input feedback.jsonl --min-count 3
    python feedback_analyzer.py trends --input feedback.jsonl --window 7
    python feedback_analyzer.py opportunities --input feedback.jsonl
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

VALID_OUTCOMES = ["SUCCESS", "PARTIAL", "FAILURE", "REJECTION", "TIMEOUT", "ERROR"]

THRESHOLDS = {
    "first_attempt_success": 0.70,
    "corrections_per_task": 2.0,
    "tool_error_rate": 0.05,
    "completion_turns": 10,
}


def load_feedback(path: str) -> list:
    """Load feedback entries from JSON or JSONL file."""
    entries = []
    with open(path, "r") as f:
        content = f.read().strip()
        if content.startswith("["):
            entries = json.loads(content)
        else:
            for line in content.splitlines():
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    for e in entries:
        if "timestamp" in e:
            e["_dt"] = datetime.fromisoformat(e["timestamp"])
    return entries


def cmd_analyze(args, entries: list) -> dict:
    """Produce summary statistics from feedback entries."""
    if not entries:
        return {"action": "analyze", "error": "No entries found"}

    total = len(entries)
    outcome_counts = Counter(e.get("outcome", "UNKNOWN") for e in entries)
    task_type_counts = Counter(e.get("task_type", "unknown") for e in entries)

    successes = outcome_counts.get("SUCCESS", 0)
    first_attempt = sum(1 for e in entries if e.get("outcome") == "SUCCESS" and e.get("corrections", 0) == 0)
    corrections = [e.get("corrections", 0) for e in entries]
    avg_corrections = sum(corrections) / total if total else 0
    turns = [e.get("turns", 0) for e in entries]
    avg_turns = sum(turns) / total if total else 0

    total_tool_calls = sum(len(e.get("tools_used", [])) for e in entries)
    total_tool_errors = sum(e.get("tool_errors", 0) for e in entries)
    tool_error_rate = total_tool_errors / total_tool_calls if total_tool_calls else 0

    # Per-task-type breakdown
    task_breakdown = {}
    for task_type in task_type_counts:
        task_entries = [e for e in entries if e.get("task_type") == task_type]
        t_total = len(task_entries)
        t_success = sum(1 for e in task_entries if e.get("outcome") == "SUCCESS")
        t_first = sum(1 for e in task_entries if e.get("outcome") == "SUCCESS" and e.get("corrections", 0) == 0)
        task_breakdown[task_type] = {
            "total": t_total,
            "success_rate": round(t_success / t_total, 3) if t_total else 0,
            "first_attempt_rate": round(t_first / t_total, 3) if t_total else 0,
            "avg_corrections": round(sum(e.get("corrections", 0) for e in task_entries) / t_total, 2),
        }

    # Health assessment
    health_flags = []
    fa_rate = first_attempt / total if total else 0
    if fa_rate < THRESHOLDS["first_attempt_success"]:
        health_flags.append(f"First-attempt success rate {fa_rate:.1%} below {THRESHOLDS['first_attempt_success']:.0%} threshold")
    if avg_corrections > THRESHOLDS["corrections_per_task"]:
        health_flags.append(f"Avg corrections {avg_corrections:.1f} exceeds {THRESHOLDS['corrections_per_task']} threshold")
    if tool_error_rate > THRESHOLDS["tool_error_rate"]:
        health_flags.append(f"Tool error rate {tool_error_rate:.1%} exceeds {THRESHOLDS['tool_error_rate']:.0%} threshold")

    return {
        "action": "analyze",
        "total_entries": total,
        "outcome_distribution": dict(outcome_counts),
        "success_rate": round(successes / total, 3),
        "first_attempt_success_rate": round(fa_rate, 3),
        "avg_corrections": round(avg_corrections, 2),
        "avg_turns": round(avg_turns, 2),
        "tool_error_rate": round(tool_error_rate, 4),
        "task_breakdown": task_breakdown,
        "health_flags": health_flags,
    }


def cmd_patterns(args, entries: list) -> dict:
    """Extract recurring patterns from feedback data."""
    min_count = args.min_count

    # Failure patterns by task type
    failure_patterns = defaultdict(list)
    for e in entries:
        if e.get("outcome") in ("FAILURE", "REJECTION", "ERROR"):
            failure_patterns[e.get("task_type", "unknown")].append({
                "outcome": e["outcome"],
                "notes": e.get("notes", ""),
                "corrections": e.get("corrections", 0),
                "session_id": e.get("session_id", ""),
            })

    recurring_failures = {
        k: v for k, v in failure_patterns.items() if len(v) >= min_count
    }

    # Correction patterns -- what task types need most corrections
    correction_patterns = defaultdict(list)
    for e in entries:
        if e.get("corrections", 0) > 0:
            correction_patterns[e.get("task_type", "unknown")].append(e.get("corrections", 0))

    high_correction_tasks = {}
    for task_type, corr_list in correction_patterns.items():
        if len(corr_list) >= min_count:
            high_correction_tasks[task_type] = {
                "occurrences": len(corr_list),
                "avg_corrections": round(sum(corr_list) / len(corr_list), 2),
                "max_corrections": max(corr_list),
            }

    # Tool error patterns
    tool_error_patterns = defaultdict(int)
    for e in entries:
        if e.get("tool_errors", 0) > 0:
            for tool in e.get("tools_used", []):
                tool_error_patterns[tool] += 1

    # Success patterns -- what works well
    success_patterns = defaultdict(int)
    for e in entries:
        if e.get("outcome") == "SUCCESS" and e.get("corrections", 0) == 0:
            success_patterns[e.get("task_type", "unknown")] += 1

    return {
        "action": "patterns",
        "min_count_threshold": min_count,
        "recurring_failures": recurring_failures,
        "high_correction_tasks": high_correction_tasks,
        "tool_error_frequency": dict(tool_error_patterns),
        "strong_success_areas": dict(success_patterns),
    }


def cmd_trends(args, entries: list) -> dict:
    """Analyze trends over time using a sliding window."""
    window_days = args.window
    if not entries or "_dt" not in entries[0]:
        return {"action": "trends", "error": "No timestamped entries found"}

    sorted_entries = sorted(entries, key=lambda e: e["_dt"])
    start = sorted_entries[0]["_dt"]
    end = sorted_entries[-1]["_dt"]

    windows = []
    current = start
    while current <= end:
        window_end = current + timedelta(days=window_days)
        window_entries = [e for e in sorted_entries if current <= e["_dt"] < window_end]
        if window_entries:
            total = len(window_entries)
            successes = sum(1 for e in window_entries if e.get("outcome") == "SUCCESS")
            first_att = sum(1 for e in window_entries if e.get("outcome") == "SUCCESS" and e.get("corrections", 0) == 0)
            avg_corr = sum(e.get("corrections", 0) for e in window_entries) / total
            avg_turns = sum(e.get("turns", 0) for e in window_entries) / total
            windows.append({
                "period_start": current.isoformat(),
                "period_end": window_end.isoformat(),
                "entries": total,
                "success_rate": round(successes / total, 3),
                "first_attempt_rate": round(first_att / total, 3),
                "avg_corrections": round(avg_corr, 2),
                "avg_turns": round(avg_turns, 2),
            })
        current = window_end

    # Compute trend direction
    trend_signals = []
    if len(windows) >= 2:
        first_half = windows[: len(windows) // 2]
        second_half = windows[len(windows) // 2 :]
        fa_first = sum(w["first_attempt_rate"] for w in first_half) / len(first_half)
        fa_second = sum(w["first_attempt_rate"] for w in second_half) / len(second_half)
        delta = fa_second - fa_first
        if delta > 0.05:
            trend_signals.append(f"IMPROVING: First-attempt success up {delta:+.1%}")
        elif delta < -0.05:
            trend_signals.append(f"DEGRADING: First-attempt success down {delta:+.1%}")
        else:
            trend_signals.append("STABLE: First-attempt success rate unchanged")

        corr_first = sum(w["avg_corrections"] for w in first_half) / len(first_half)
        corr_second = sum(w["avg_corrections"] for w in second_half) / len(second_half)
        corr_delta = corr_second - corr_first
        if corr_delta > 0.3:
            trend_signals.append(f"WARNING: Avg corrections increasing ({corr_delta:+.2f})")
        elif corr_delta < -0.3:
            trend_signals.append(f"IMPROVING: Avg corrections decreasing ({corr_delta:+.2f})")

    return {
        "action": "trends",
        "window_days": window_days,
        "total_periods": len(windows),
        "windows": windows,
        "trend_signals": trend_signals,
    }


def cmd_opportunities(args, entries: list) -> dict:
    """Identify concrete improvement opportunities from feedback data."""
    opportunities = []

    # Opportunity 1: Task types with low success rates
    task_outcomes = defaultdict(lambda: {"total": 0, "success": 0, "failures": []})
    for e in entries:
        tt = e.get("task_type", "unknown")
        task_outcomes[tt]["total"] += 1
        if e.get("outcome") == "SUCCESS":
            task_outcomes[tt]["success"] += 1
        elif e.get("outcome") in ("FAILURE", "REJECTION"):
            task_outcomes[tt]["failures"].append(e.get("notes", ""))

    for tt, data in task_outcomes.items():
        rate = data["success"] / data["total"] if data["total"] else 0
        if rate < 0.6 and data["total"] >= 3:
            opportunities.append({
                "type": "low_success_task",
                "priority": "high",
                "task_type": tt,
                "success_rate": round(rate, 3),
                "sample_count": data["total"],
                "recommendation": f"Add dedicated rules for '{tt}' tasks -- success rate is {rate:.0%}",
                "failure_notes": [n for n in data["failures"] if n][:3],
            })

    # Opportunity 2: High correction tasks that could benefit from rules
    for e in entries:
        tt = e.get("task_type", "unknown")
    corr_by_type = defaultdict(list)
    for e in entries:
        corr_by_type[e.get("task_type", "unknown")].append(e.get("corrections", 0))
    for tt, corrs in corr_by_type.items():
        avg = sum(corrs) / len(corrs)
        if avg > 1.5 and len(corrs) >= 3:
            opportunities.append({
                "type": "high_correction_task",
                "priority": "medium",
                "task_type": tt,
                "avg_corrections": round(avg, 2),
                "recommendation": f"Capture correction patterns for '{tt}' and promote to rules",
            })

    # Opportunity 3: Tool reliability issues
    tool_stats = defaultdict(lambda: {"uses": 0, "errors": 0})
    for e in entries:
        for tool in e.get("tools_used", []):
            tool_stats[tool]["uses"] += 1
        if e.get("tool_errors", 0) > 0:
            for tool in e.get("tools_used", []):
                tool_stats[tool]["errors"] += 1

    for tool, stats in tool_stats.items():
        err_rate = stats["errors"] / stats["uses"] if stats["uses"] else 0
        if err_rate > 0.1 and stats["uses"] >= 5:
            opportunities.append({
                "type": "tool_reliability",
                "priority": "medium",
                "tool": tool,
                "error_rate": round(err_rate, 3),
                "uses": stats["uses"],
                "recommendation": f"Investigate '{tool}' reliability -- {err_rate:.0%} error rate",
            })

    # Opportunity 4: Timeout tasks suggesting scope issues
    timeout_count = sum(1 for e in entries if e.get("outcome") == "TIMEOUT")
    if timeout_count >= 2:
        opportunities.append({
            "type": "timeout_pattern",
            "priority": "high",
            "count": timeout_count,
            "recommendation": "Review task scoping -- multiple timeouts suggest tasks are too large or under-specified",
        })

    opportunities.sort(key=lambda o: {"high": 0, "medium": 1, "low": 2}.get(o["priority"], 3))
    return {"action": "opportunities", "count": len(opportunities), "opportunities": opportunities}


def format_human(result: dict) -> str:
    """Format result for human-readable output."""
    action = result.get("action", "unknown")
    lines = []

    if "error" in result:
        return f"Error: {result['error']}"

    if action == "analyze":
        lines.append(f"Feedback Analysis ({result['total_entries']} entries)")
        lines.append("=" * 50)
        lines.append(f"  Success rate:           {result['success_rate']:.1%}")
        lines.append(f"  First-attempt success:  {result['first_attempt_success_rate']:.1%}")
        lines.append(f"  Avg corrections/task:   {result['avg_corrections']:.2f}")
        lines.append(f"  Avg turns/task:         {result['avg_turns']:.1f}")
        lines.append(f"  Tool error rate:        {result['tool_error_rate']:.2%}")
        lines.append("")
        lines.append("Outcome Distribution:")
        for outcome, count in sorted(result["outcome_distribution"].items()):
            bar = "#" * min(count, 40)
            lines.append(f"  {outcome:<12} {count:>4}  {bar}")
        lines.append("")
        lines.append("Per-Task Breakdown:")
        for tt, stats in sorted(result["task_breakdown"].items()):
            lines.append(f"  {tt}: {stats['total']} tasks, {stats['success_rate']:.0%} success, {stats['avg_corrections']:.1f} avg corrections")
        if result["health_flags"]:
            lines.append("")
            lines.append("Health Warnings:")
            for flag in result["health_flags"]:
                lines.append(f"  [!] {flag}")

    elif action == "patterns":
        lines.append("Feedback Patterns")
        lines.append("=" * 50)
        if result["recurring_failures"]:
            lines.append("Recurring Failures:")
            for tt, failures in result["recurring_failures"].items():
                lines.append(f"  {tt}: {len(failures)} occurrences")
        if result["high_correction_tasks"]:
            lines.append("High-Correction Tasks:")
            for tt, stats in result["high_correction_tasks"].items():
                lines.append(f"  {tt}: avg {stats['avg_corrections']} corrections ({stats['occurrences']} occurrences)")
        if result["strong_success_areas"]:
            lines.append("Strong Areas (first-attempt success):")
            for tt, count in sorted(result["strong_success_areas"].items(), key=lambda x: -x[1]):
                lines.append(f"  {tt}: {count} first-attempt successes")

    elif action == "trends":
        lines.append(f"Trend Analysis ({result['window_days']}-day windows)")
        lines.append("=" * 50)
        for w in result["windows"]:
            lines.append(f"  {w['period_start'][:10]} - {w['period_end'][:10]}: "
                         f"{w['entries']} entries, {w['success_rate']:.0%} success, "
                         f"{w['avg_corrections']:.1f} avg corrections")
        if result["trend_signals"]:
            lines.append("")
            for signal in result["trend_signals"]:
                lines.append(f"  >> {signal}")

    elif action == "opportunities":
        lines.append(f"Improvement Opportunities ({result['count']} found)")
        lines.append("=" * 50)
        for i, opp in enumerate(result["opportunities"], 1):
            lines.append(f"\n  {i}. [{opp['priority'].upper()}] {opp['type']}")
            lines.append(f"     {opp['recommendation']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Feedback Analyzer - Extract patterns and opportunities from agent feedback logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output in JSON format")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_analyze = sub.add_parser("analyze", help="Summary statistics of feedback data")
    p_analyze.add_argument("--input", required=True, help="Path to feedback log file (JSON or JSONL)")

    p_patterns = sub.add_parser("patterns", help="Extract recurring patterns")
    p_patterns.add_argument("--input", required=True, help="Path to feedback log file")
    p_patterns.add_argument("--min-count", type=int, default=3, help="Minimum occurrences to flag a pattern")

    p_trends = sub.add_parser("trends", help="Analyze trends over time")
    p_trends.add_argument("--input", required=True, help="Path to feedback log file")
    p_trends.add_argument("--window", type=int, default=7, help="Window size in days")

    p_opp = sub.add_parser("opportunities", help="Identify improvement opportunities")
    p_opp.add_argument("--input", required=True, help="Path to feedback log file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    entries = load_feedback(args.input)

    commands = {
        "analyze": cmd_analyze,
        "patterns": cmd_patterns,
        "trends": cmd_trends,
        "opportunities": cmd_opportunities,
    }

    result = commands[args.command](args, entries)

    # Remove internal fields before output
    if "rules" in result or "windows" in result or "opportunities" in result:
        pass  # keep structured data
    for entry_list_key in ["recurring_failures"]:
        if entry_list_key in result:
            for key, val_list in result[entry_list_key].items():
                for v in val_list:
                    v.pop("_dt", None)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
