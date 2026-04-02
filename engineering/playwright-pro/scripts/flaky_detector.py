#!/usr/bin/env python3
"""Detect flaky Playwright tests by analyzing multiple test result files.

Scans a directory of Playwright JSON result files from multiple CI runs and
identifies tests that pass intermittently. Produces a flakiness report with
stability scores and recommended actions.

Usage:
    python flaky_detector.py --results-dir ./test-results/ --runs 10
    python flaky_detector.py --results-dir ./test-results/ --runs 10 --threshold 0.9
    python flaky_detector.py --results-dir ./test-results/ --runs 10 --json
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


def load_result_files(results_dir, max_runs):
    """Load Playwright JSON result files from a directory.

    Expects files named like: results-001.json, test-results-20260315.json, etc.
    Sorts by modification time to get the most recent runs.
    """
    result_dir = Path(results_dir)
    if not result_dir.is_dir():
        print(f"Error: '{results_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    json_files = sorted(
        result_dir.glob("*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )[:max_runs]

    runs = []
    for jf in json_files:
        try:
            with open(jf, "r") as f:
                data = json.load(f)
            runs.append({"file": str(jf), "data": data})
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Skipping {jf}: {e}", file=sys.stderr)

    return runs


def extract_test_outcomes(report):
    """Extract test outcomes from a Playwright JSON report."""
    outcomes = {}

    def walk_suites(suites, parent=""):
        for suite in suites:
            title = suite.get("title", "")
            path = f"{parent} > {title}" if parent else title

            for spec in suite.get("specs", []):
                spec_title = spec.get("title", "")
                full_title = f"{path} > {spec_title}".strip(" > ")

                for test in spec.get("tests", []):
                    project = test.get("projectName", "default")
                    test_key = f"[{project}] {full_title}"
                    status = test.get("status", "unknown")
                    results = test.get("results", [])
                    attempt_count = len(results)

                    # Determine effective status
                    if status == "flaky":
                        effective = "flaky"
                    elif status in ("expected", "passed"):
                        # Check if it needed retries
                        attempt_statuses = [r.get("status", "") for r in results]
                        if attempt_count > 1 and any(s in ("failed", "timedOut") for s in attempt_statuses[:-1]):
                            effective = "flaky"
                        else:
                            effective = "passed"
                    elif status in ("unexpected", "failed"):
                        effective = "failed"
                    elif status == "skipped":
                        effective = "skipped"
                    else:
                        effective = status

                    duration = sum(r.get("duration", 0) for r in results)
                    outcomes[test_key] = {
                        "status": effective,
                        "attempts": attempt_count,
                        "duration_ms": duration,
                    }

            if "suites" in suite:
                walk_suites(suite["suites"], path)

    if "suites" in report:
        walk_suites(report["suites"])

    return outcomes


def compute_flakiness(runs):
    """Compute flakiness scores across multiple runs."""
    test_history = defaultdict(lambda: {
        "pass_count": 0,
        "fail_count": 0,
        "flaky_count": 0,
        "skip_count": 0,
        "total_runs": 0,
        "durations": [],
    })

    for run in runs:
        outcomes = extract_test_outcomes(run["data"])
        for test_key, outcome in outcomes.items():
            history = test_history[test_key]
            history["total_runs"] += 1

            if outcome["status"] == "passed":
                history["pass_count"] += 1
            elif outcome["status"] == "failed":
                history["fail_count"] += 1
            elif outcome["status"] == "flaky":
                history["flaky_count"] += 1
            elif outcome["status"] == "skipped":
                history["skip_count"] += 1

            if outcome["duration_ms"] > 0:
                history["durations"].append(outcome["duration_ms"])

    # Compute stability scores
    results = []
    for test_key, history in test_history.items():
        non_skipped = history["total_runs"] - history["skip_count"]
        if non_skipped == 0:
            stability = 1.0
        else:
            # Stability = consistent pass or consistent fail (not mixed)
            pass_rate = history["pass_count"] / non_skipped
            # A test is stable if it always passes or always fails
            stability = max(pass_rate, 1.0 - pass_rate - (history["flaky_count"] / non_skipped))
            stability = max(0.0, min(1.0, stability))

        durations = history["durations"]
        duration_variance = 0.0
        if len(durations) >= 2:
            mean_dur = sum(durations) / len(durations)
            if mean_dur > 0:
                duration_variance = (
                    sum((d - mean_dur) ** 2 for d in durations) / len(durations)
                ) ** 0.5 / mean_dur  # coefficient of variation

        is_flaky = (
            history["flaky_count"] > 0
            or (history["pass_count"] > 0 and history["fail_count"] > 0)
        )

        results.append({
            "test": test_key,
            "total_runs": history["total_runs"],
            "pass_count": history["pass_count"],
            "fail_count": history["fail_count"],
            "flaky_count": history["flaky_count"],
            "skip_count": history["skip_count"],
            "stability_score": round(stability, 3),
            "duration_cv": round(duration_variance, 3),
            "avg_duration_ms": round(sum(durations) / len(durations)) if durations else 0,
            "is_flaky": is_flaky,
        })

    results.sort(key=lambda r: r["stability_score"])
    return results


def classify_action(test_result, threshold):
    """Classify recommended action for a test."""
    if test_result["stability_score"] >= threshold:
        return "OK"
    elif test_result["stability_score"] >= 0.5:
        return "INVESTIGATE"
    elif test_result["fail_count"] > test_result["pass_count"]:
        return "QUARANTINE"
    else:
        return "FIX_URGENTLY"


def format_human(test_results, threshold, runs_analyzed):
    """Format results for human-readable output."""
    output = []
    output.append("=" * 70)
    output.append("FLAKY TEST DETECTOR")
    output.append("=" * 70)
    output.append("")
    output.append(f"  Runs analyzed:      {runs_analyzed}")
    output.append(f"  Tests tracked:      {len(test_results)}")
    output.append(f"  Stability threshold: {threshold:.0%}")

    flaky_tests = [t for t in test_results if t["is_flaky"]]
    stable_tests = [t for t in test_results if not t["is_flaky"]]

    output.append(f"  Flaky tests:        {len(flaky_tests)}")
    output.append(f"  Stable tests:       {len(stable_tests)}")

    if flaky_tests:
        flaky_rate = len(flaky_tests) / len(test_results) * 100 if test_results else 0
        output.append(f"  Flaky rate:         {flaky_rate:.1f}%")
    output.append("")

    if flaky_tests:
        output.append("FLAKY TESTS (sorted by stability, lowest first)")
        output.append("-" * 70)
        output.append(f"  {'Stability':>10} {'P':>4} {'F':>4} {'Fl':>4} {'Action':<15} Test")
        output.append(f"  {'─' * 10} {'─' * 4} {'─' * 4} {'─' * 4} {'─' * 15} {'─' * 30}")

        for t in flaky_tests:
            action = classify_action(t, threshold)
            output.append(
                f"  {t['stability_score']:>10.1%} "
                f"{t['pass_count']:>4} {t['fail_count']:>4} {t['flaky_count']:>4} "
                f"{action:<15} {t['test'][:50]}"
            )

        output.append("")

        # Duration variance warning
        high_variance = [t for t in flaky_tests if t["duration_cv"] > 0.5]
        if high_variance:
            output.append("HIGH DURATION VARIANCE (may indicate timing issues)")
            output.append("-" * 70)
            for t in sorted(high_variance, key=lambda x: -x["duration_cv"]):
                output.append(
                    f"  CV={t['duration_cv']:.2f}  "
                    f"avg={t['avg_duration_ms']}ms  "
                    f"{t['test'][:50]}"
                )
            output.append("")

    # Verdict
    output.append("=" * 70)
    if not flaky_tests:
        output.append("VERDICT: STABLE - No flaky tests detected")
    elif any(classify_action(t, threshold) == "QUARANTINE" for t in flaky_tests):
        output.append("VERDICT: CRITICAL - Tests need quarantine")
    elif any(classify_action(t, threshold) == "FIX_URGENTLY" for t in flaky_tests):
        output.append("VERDICT: URGENT - Flaky tests need immediate attention")
    else:
        output.append("VERDICT: INVESTIGATE - Some tests show intermittent behavior")
    output.append("=" * 70)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Detect flaky Playwright tests by analyzing multiple test result files.",
        epilog="Example: python flaky_detector.py --results-dir ./test-results/ --runs 10",
    )
    parser.add_argument("--results-dir", required=True, help="Directory containing Playwright JSON result files")
    parser.add_argument("--runs", type=int, default=10, help="Number of recent runs to analyze (default: 10)")
    parser.add_argument("--threshold", type=float, default=0.95, help="Stability threshold (default: 0.95)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    runs = load_result_files(args.results_dir, args.runs)
    if not runs:
        print(f"Error: No JSON result files found in '{args.results_dir}'.", file=sys.stderr)
        sys.exit(1)

    test_results = compute_flakiness(runs)

    if args.json_output:
        result = {
            "runs_analyzed": len(runs),
            "total_tests": len(test_results),
            "flaky_count": sum(1 for t in test_results if t["is_flaky"]),
            "stability_threshold": args.threshold,
            "flaky_tests": [t for t in test_results if t["is_flaky"]],
            "all_tests": test_results,
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_human(test_results, args.threshold, len(runs)))


if __name__ == "__main__":
    main()
