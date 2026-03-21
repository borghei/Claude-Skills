#!/usr/bin/env python3
"""Parse Playwright JSON test reports and generate summaries with flaky test detection.

Reads Playwright's JSON reporter output and produces a summary including
pass/fail/skip counts, duration statistics, flaky test identification
(tests that passed on retry), slowest tests, and failure details.

Usage:
    python test_report_parser.py test-results.json
    python test_report_parser.py test-results.json --flaky-threshold 5
    python test_report_parser.py test-results.json --json
    python test_report_parser.py test-results.json --top-slow 10
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import timedelta
from pathlib import Path


def parse_report(filepath):
    """Parse a Playwright JSON report file."""
    try:
        content = Path(filepath).read_text(encoding="utf-8")
        return json.loads(content)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading report: {e}", file=sys.stderr)
        sys.exit(1)


def extract_test_results(report):
    """Extract individual test results from the report structure.

    Playwright JSON reports can have different structures depending on version.
    This handles both the nested (suites) and flat formats.
    """
    results = []

    def _walk_suites(suites, parent_path=""):
        for suite in suites:
            suite_title = suite.get("title", "")
            current_path = f"{parent_path} > {suite_title}" if parent_path else suite_title

            # Process specs in this suite
            for spec in suite.get("specs", []):
                spec_title = spec.get("title", "")
                full_title = f"{current_path} > {spec_title}" if current_path else spec_title
                spec_file = spec.get("file", suite.get("file", ""))

                for test in spec.get("tests", []):
                    project = test.get("projectName", test.get("projectId", "unknown"))
                    status = test.get("status", test.get("expectedStatus", "unknown"))
                    annotations = test.get("annotations", [])

                    # Collect all results (attempts) for this test
                    attempts = test.get("results", [])
                    durations = [r.get("duration", 0) for r in attempts]
                    total_duration = sum(durations)
                    attempt_count = len(attempts)

                    # Determine flakiness: passed on retry means flaky
                    attempt_statuses = [r.get("status", "unknown") for r in attempts]
                    is_flaky = (
                        status == "expected"
                        and attempt_count > 1
                        and any(s in ("failed", "timedOut") for s in attempt_statuses[:-1])
                        and attempt_statuses[-1] == "passed"
                    )

                    # Also check explicit flaky status
                    if test.get("status") == "flaky" or status == "flaky":
                        is_flaky = True

                    # Extract error details from failed attempts
                    errors = []
                    for r in attempts:
                        if r.get("status") in ("failed", "timedOut"):
                            error_msg = r.get("error", {})
                            if isinstance(error_msg, dict):
                                msg = error_msg.get("message", "")
                                snippet = error_msg.get("snippet", "")
                            elif isinstance(error_msg, str):
                                msg = error_msg
                                snippet = ""
                            else:
                                msg = str(error_msg) if error_msg else ""
                                snippet = ""
                            if msg:
                                errors.append({"message": msg[:500], "snippet": snippet[:300]})

                    # Determine final status
                    if is_flaky:
                        final_status = "flaky"
                    elif status in ("expected", "passed"):
                        final_status = "passed"
                    elif status in ("unexpected", "failed"):
                        final_status = "failed"
                    elif status in ("skipped",):
                        final_status = "skipped"
                    elif status == "timedOut":
                        final_status = "timedOut"
                    else:
                        # Fallback: check last attempt
                        last_status = attempt_statuses[-1] if attempt_statuses else "unknown"
                        final_status = last_status

                    results.append({
                        "title": full_title.strip(" > "),
                        "file": spec_file,
                        "project": project,
                        "status": final_status,
                        "duration_ms": total_duration,
                        "attempts": attempt_count,
                        "is_flaky": is_flaky,
                        "errors": errors,
                        "annotations": annotations,
                    })

            # Recurse into nested suites
            if "suites" in suite:
                _walk_suites(suite["suites"], current_path)

    # Handle top-level structure
    if "suites" in report:
        _walk_suites(report["suites"])
    elif "specs" in report:
        _walk_suites([report])

    return results


def compute_stats(results):
    """Compute summary statistics from test results."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    flaky = sum(1 for r in results if r["is_flaky"])
    skipped = sum(1 for r in results if r["status"] == "skipped")
    timed_out = sum(1 for r in results if r["status"] == "timedOut")

    durations = [r["duration_ms"] for r in results if r["duration_ms"] > 0]
    total_duration = sum(durations)
    avg_duration = total_duration / len(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    min_duration = min(durations) if durations else 0
    p90_duration = sorted(durations)[int(len(durations) * 0.9)] if durations else 0

    # Per-project breakdown
    by_project = defaultdict(lambda: {"passed": 0, "failed": 0, "flaky": 0, "skipped": 0, "total": 0})
    for r in results:
        proj = r["project"]
        by_project[proj]["total"] += 1
        if r["is_flaky"]:
            by_project[proj]["flaky"] += 1
        elif r["status"] == "passed":
            by_project[proj]["passed"] += 1
        elif r["status"] == "failed":
            by_project[proj]["failed"] += 1
        elif r["status"] == "skipped":
            by_project[proj]["skipped"] += 1

    # Flaky rate
    non_skipped = total - skipped
    flaky_rate = (flaky / non_skipped * 100) if non_skipped > 0 else 0
    pass_rate = (passed / non_skipped * 100) if non_skipped > 0 else 0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "flaky": flaky,
        "skipped": skipped,
        "timed_out": timed_out,
        "pass_rate": round(pass_rate, 1),
        "flaky_rate": round(flaky_rate, 1),
        "total_duration_ms": total_duration,
        "avg_duration_ms": round(avg_duration),
        "max_duration_ms": max_duration,
        "min_duration_ms": min_duration,
        "p90_duration_ms": p90_duration,
        "by_project": dict(by_project),
    }


def format_duration(ms):
    """Format milliseconds as human-readable duration."""
    if ms < 1000:
        return f"{ms}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remaining_secs = seconds % 60
    return f"{minutes}m {remaining_secs:.0f}s"


def format_human(results, stats, top_slow, flaky_threshold):
    """Format results as human-readable output."""
    output = []
    output.append("=" * 70)
    output.append("PLAYWRIGHT TEST REPORT SUMMARY")
    output.append("=" * 70)
    output.append("")

    # Overall stats
    output.append("RESULTS")
    output.append("-" * 70)
    total_bar_width = 40
    pass_pct = stats["passed"] / stats["total"] if stats["total"] else 0
    fail_pct = stats["failed"] / stats["total"] if stats["total"] else 0
    flaky_pct = stats["flaky"] / stats["total"] if stats["total"] else 0

    pass_bar = int(pass_pct * total_bar_width)
    fail_bar = int(fail_pct * total_bar_width)
    flaky_bar = int(flaky_pct * total_bar_width)
    skip_bar = total_bar_width - pass_bar - fail_bar - flaky_bar

    bar = "+" * pass_bar + "~" * flaky_bar + "x" * fail_bar + "." * max(0, skip_bar)
    output.append(f"  [{bar}]")
    output.append(f"  + passed  ~ flaky  x failed  . skipped")
    output.append("")
    output.append(f"  Total:     {stats['total']}")
    output.append(f"  Passed:    {stats['passed']}  ({stats['pass_rate']}%)")
    output.append(f"  Failed:    {stats['failed']}")
    output.append(f"  Flaky:     {stats['flaky']}  ({stats['flaky_rate']}% flaky rate)")
    output.append(f"  Skipped:   {stats['skipped']}")
    if stats["timed_out"] > 0:
        output.append(f"  Timed out: {stats['timed_out']}")
    output.append("")

    # Duration stats
    output.append("DURATION")
    output.append("-" * 70)
    output.append(f"  Total:   {format_duration(stats['total_duration_ms'])}")
    output.append(f"  Average: {format_duration(stats['avg_duration_ms'])}")
    output.append(f"  P90:     {format_duration(stats['p90_duration_ms'])}")
    output.append(f"  Slowest: {format_duration(stats['max_duration_ms'])}")
    output.append("")

    # Per-project breakdown
    if stats["by_project"]:
        output.append("BY PROJECT")
        output.append("-" * 70)
        for project, pstats in sorted(stats["by_project"].items()):
            status_parts = []
            if pstats["passed"]:
                status_parts.append(f"{pstats['passed']} passed")
            if pstats["failed"]:
                status_parts.append(f"{pstats['failed']} failed")
            if pstats["flaky"]:
                status_parts.append(f"{pstats['flaky']} flaky")
            if pstats["skipped"]:
                status_parts.append(f"{pstats['skipped']} skipped")
            status_str = ", ".join(status_parts)
            output.append(f"  {project:<20} {pstats['total']:>4} tests  ({status_str})")
        output.append("")

    # Flaky tests
    flaky_tests = [r for r in results if r["is_flaky"]]
    if flaky_tests:
        output.append("FLAKY TESTS")
        output.append("-" * 70)
        for ft in sorted(flaky_tests, key=lambda x: -x["attempts"]):
            output.append(f"  [{ft['project']}] {ft['title']}")
            output.append(f"    Attempts: {ft['attempts']} | Duration: {format_duration(ft['duration_ms'])}")
            if ft["errors"]:
                output.append(f"    Last error: {ft['errors'][-1]['message'][:100]}")
            output.append("")

        if stats["flaky_rate"] > flaky_threshold:
            output.append(f"  WARNING: Flaky rate ({stats['flaky_rate']}%) exceeds threshold ({flaky_threshold}%)")
            output.append(f"  Action: Quarantine flaky tests and fix within 48 hours")
            output.append("")

    # Failed tests
    failed_tests = [r for r in results if r["status"] == "failed" or r["status"] == "timedOut"]
    if failed_tests:
        output.append("FAILED TESTS")
        output.append("-" * 70)
        for ft in failed_tests:
            status_label = "TIMEOUT" if ft["status"] == "timedOut" else "FAILED"
            output.append(f"  [{status_label}] [{ft['project']}] {ft['title']}")
            output.append(f"    File: {ft['file']}")
            output.append(f"    Duration: {format_duration(ft['duration_ms'])}")
            if ft["errors"]:
                error = ft["errors"][-1]
                # Truncate for readability
                msg_lines = error["message"].split("\n")
                for msg_line in msg_lines[:3]:
                    output.append(f"    Error: {msg_line.strip()[:100]}")
            output.append("")

    # Slowest tests
    sorted_by_duration = sorted(results, key=lambda x: -x["duration_ms"])
    slow_tests = sorted_by_duration[:top_slow]
    if slow_tests:
        output.append(f"TOP {top_slow} SLOWEST TESTS")
        output.append("-" * 70)
        for i, st in enumerate(slow_tests, 1):
            dur = format_duration(st["duration_ms"])
            output.append(f"  {i:>2}. {dur:>8}  [{st['project']}] {st['title']}")
        output.append("")

    # Verdict
    output.append("=" * 70)
    if stats["failed"] > 0:
        output.append("VERDICT: FAILED - Fix failing tests before merging")
    elif stats["flaky_rate"] > flaky_threshold:
        output.append(f"VERDICT: UNSTABLE - Flaky rate ({stats['flaky_rate']}%) exceeds {flaky_threshold}% threshold")
    elif stats["total_duration_ms"] > 600000:
        output.append(f"VERDICT: SLOW - Suite took {format_duration(stats['total_duration_ms'])} (target: <10min)")
    else:
        output.append("VERDICT: PASSED")
    output.append("=" * 70)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Parse Playwright JSON test reports and generate summary with flaky test detection.",
        epilog="Example: python test_report_parser.py test-results.json --flaky-threshold 3",
    )
    parser.add_argument("report", help="Path to Playwright JSON report file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")
    parser.add_argument(
        "--flaky-threshold",
        type=float,
        default=5.0,
        help="Flaky rate percentage threshold for warnings (default: 5.0)",
    )
    parser.add_argument(
        "--top-slow",
        type=int,
        default=5,
        help="Number of slowest tests to display (default: 5)",
    )

    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: Report file '{args.report}' not found.", file=sys.stderr)
        sys.exit(1)

    report = parse_report(report_path)
    results = extract_test_results(report)

    if not results:
        print("Warning: No test results found in the report.", file=sys.stderr)
        # Still produce output with zeros
        results = []

    stats = compute_stats(results)

    if args.json_output:
        output = {
            "stats": stats,
            "flaky_tests": [r for r in results if r["is_flaky"]],
            "failed_tests": [r for r in results if r["status"] in ("failed", "timedOut")],
            "slowest_tests": sorted(results, key=lambda x: -x["duration_ms"])[:args.top_slow],
            "flaky_threshold": args.flaky_threshold,
            "threshold_exceeded": stats["flaky_rate"] > args.flaky_threshold,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(results, stats, args.top_slow, args.flaky_threshold))


if __name__ == "__main__":
    main()
