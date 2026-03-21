#!/usr/bin/env python3
"""Score evaluation results from JSON test cases against expected outputs.

Supports three matching strategies: exact match, contains, and regex.
Reads a test suite JSON file where each test case defines an input,
the actual output, and expected criteria. Produces per-case and aggregate
scores aligned with the Prompt Engineer Toolkit evaluation rubric.

No external dependencies -- uses Python standard library only.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter


# Default dimension weights from the SKILL.md evaluation rubric.
DEFAULT_WEIGHTS = {
    "adherence": 0.30,
    "accuracy": 0.30,
    "safety": 0.20,
    "format": 0.10,
    "relevance": 0.10,
}

PASS_THRESHOLD = 0.80
WARNING_THRESHOLD = 0.70


def check_exact_match(actual: str, expected: str, case_sensitive: bool = True) -> dict:
    """Check if actual output exactly matches expected string."""
    if case_sensitive:
        matched = actual.strip() == expected.strip()
    else:
        matched = actual.strip().lower() == expected.strip().lower()
    return {
        "method": "exact_match",
        "matched": matched,
        "score": 1.0 if matched else 0.0,
        "expected": expected[:100],
        "actual_preview": actual[:100],
    }


def check_contains(actual: str, expected_phrases: list, case_sensitive: bool = True) -> dict:
    """Check if actual output contains all expected phrases."""
    results = []
    for phrase in expected_phrases:
        if case_sensitive:
            found = phrase in actual
        else:
            found = phrase.lower() in actual.lower()
        results.append({"phrase": phrase, "found": found})

    matched_count = sum(1 for r in results if r["found"])
    total = len(expected_phrases)
    score = matched_count / total if total > 0 else 0.0

    return {
        "method": "contains",
        "matched": matched_count == total,
        "score": round(score, 3),
        "matched_count": matched_count,
        "total": total,
        "details": results,
    }


def check_not_contains(actual: str, forbidden_phrases: list, case_sensitive: bool = True) -> dict:
    """Check that actual output does NOT contain any forbidden phrases."""
    results = []
    for phrase in forbidden_phrases:
        if case_sensitive:
            found = phrase in actual
        else:
            found = phrase.lower() in actual.lower()
        results.append({"phrase": phrase, "found": found})

    violations = sum(1 for r in results if r["found"])
    total = len(forbidden_phrases)
    score = 1.0 - (violations / total) if total > 0 else 1.0

    return {
        "method": "not_contains",
        "matched": violations == 0,
        "score": round(score, 3),
        "violations": violations,
        "total": total,
        "details": results,
    }


def check_regex(actual: str, pattern: str) -> dict:
    """Check if actual output matches a regex pattern."""
    try:
        match = re.search(pattern, actual, re.DOTALL)
        matched = match is not None
        return {
            "method": "regex",
            "matched": matched,
            "score": 1.0 if matched else 0.0,
            "pattern": pattern,
            "match_text": match.group(0)[:80] if match else None,
        }
    except re.error as e:
        return {
            "method": "regex",
            "matched": False,
            "score": 0.0,
            "pattern": pattern,
            "error": str(e),
        }


def check_max_tokens(actual: str, max_tokens: int) -> dict:
    """Check if output is within token budget (approximate)."""
    word_count = len(actual.split())
    estimated_tokens = int(word_count * 1.3 + 0.5)
    within = estimated_tokens <= max_tokens

    return {
        "method": "max_tokens",
        "matched": within,
        "score": 1.0 if within else max(0.0, round(1.0 - (estimated_tokens - max_tokens) / max_tokens, 3)),
        "estimated_tokens": estimated_tokens,
        "max_tokens": max_tokens,
    }


def check_required_fields(actual: str, required_fields: list) -> dict:
    """Check if output (assumed JSON) contains required fields."""
    try:
        parsed = json.loads(actual)
    except (json.JSONDecodeError, TypeError):
        # If not JSON, check for field names as text patterns.
        found = []
        missing = []
        for field in required_fields:
            if field.lower() in actual.lower():
                found.append(field)
            else:
                missing.append(field)
        score = len(found) / len(required_fields) if required_fields else 1.0
        return {
            "method": "required_fields",
            "matched": len(missing) == 0,
            "score": round(score, 3),
            "found": found,
            "missing": missing,
            "note": "Output is not valid JSON; checked as text patterns",
        }

    def flatten_keys(obj, prefix=""):
        keys = set()
        if isinstance(obj, dict):
            for k, v in obj.items():
                full_key = f"{prefix}.{k}" if prefix else k
                keys.add(full_key)
                keys.add(k)  # Also add short name
                keys.update(flatten_keys(v, full_key))
        elif isinstance(obj, list):
            for item in obj:
                keys.update(flatten_keys(item, prefix))
        return keys

    all_keys = flatten_keys(parsed)
    found = [f for f in required_fields if f in all_keys]
    missing = [f for f in required_fields if f not in all_keys]
    score = len(found) / len(required_fields) if required_fields else 1.0

    return {
        "method": "required_fields",
        "matched": len(missing) == 0,
        "score": round(score, 3),
        "found": found,
        "missing": missing,
    }


def score_test_case(test_case: dict) -> dict:
    """Score a single test case against its expected criteria."""
    test_id = test_case.get("test_id", "unknown")
    actual = test_case.get("actual", test_case.get("output", ""))
    expected = test_case.get("expected", {})
    tags = test_case.get("tags", [])

    checks = []
    scores = []

    # Exact match
    if "exact" in expected:
        case_sensitive = expected.get("case_sensitive", True)
        result = check_exact_match(actual, expected["exact"], case_sensitive)
        checks.append(result)
        scores.append(result["score"])

    # Contains
    if "contains" in expected:
        case_sensitive = expected.get("case_sensitive", True)
        result = check_contains(actual, expected["contains"], case_sensitive)
        checks.append(result)
        scores.append(result["score"])

    # Not contains
    if "not_contains" in expected:
        case_sensitive = expected.get("case_sensitive", True)
        result = check_not_contains(actual, expected["not_contains"], case_sensitive)
        checks.append(result)
        scores.append(result["score"])

    # Regex
    if "format_regex" in expected:
        result = check_regex(actual, expected["format_regex"])
        checks.append(result)
        scores.append(result["score"])

    if "regex" in expected:
        result = check_regex(actual, expected["regex"])
        checks.append(result)
        scores.append(result["score"])

    # Max tokens
    if "max_tokens" in expected:
        result = check_max_tokens(actual, expected["max_tokens"])
        checks.append(result)
        scores.append(result["score"])

    # Required fields
    if "required_fields" in expected:
        result = check_required_fields(actual, expected["required_fields"])
        checks.append(result)
        scores.append(result["score"])

    # Compute aggregate score
    if scores:
        aggregate_score = round(sum(scores) / len(scores), 3)
    else:
        aggregate_score = 0.0

    passed = aggregate_score >= PASS_THRESHOLD
    status = "pass" if passed else "warn" if aggregate_score >= WARNING_THRESHOLD else "fail"

    return {
        "test_id": test_id,
        "score": aggregate_score,
        "status": status,
        "checks_run": len(checks),
        "checks_passed": sum(1 for c in checks if c["matched"]),
        "checks": checks,
        "tags": tags,
    }


def score_suite(test_cases: list) -> dict:
    """Score an entire test suite and produce aggregate metrics."""
    results = [score_test_case(tc) for tc in test_cases]

    total = len(results)
    if total == 0:
        return {"error": "No test cases found", "results": [], "summary": {}}

    pass_count = sum(1 for r in results if r["status"] == "pass")
    warn_count = sum(1 for r in results if r["status"] == "warn")
    fail_count = sum(1 for r in results if r["status"] == "fail")
    avg_score = round(sum(r["score"] for r in results) / total, 3)

    # Scores by tag
    tag_scores = {}
    for r in results:
        for tag in r.get("tags", []):
            tag_scores.setdefault(tag, []).append(r["score"])
    tag_averages = {tag: round(sum(s) / len(s), 3) for tag, s in tag_scores.items()}

    suite_status = "pass" if avg_score >= PASS_THRESHOLD else "warn" if avg_score >= WARNING_THRESHOLD else "fail"

    return {
        "summary": {
            "total_cases": total,
            "passed": pass_count,
            "warned": warn_count,
            "failed": fail_count,
            "pass_rate": round(pass_count / total, 3),
            "average_score": avg_score,
            "suite_status": suite_status,
            "pass_threshold": PASS_THRESHOLD,
            "warning_threshold": WARNING_THRESHOLD,
        },
        "by_tag": tag_averages,
        "results": results,
    }


def format_human(suite_result: dict) -> str:
    """Format suite results for human-readable console output."""
    lines = []
    s = suite_result["summary"]

    lines.append("Evaluation Score Report")
    lines.append("=" * 56)
    lines.append(f"  Suite Status:   {s['suite_status'].upper()}")
    lines.append(f"  Average Score:  {s['average_score']:.1%}")
    lines.append(f"  Pass Rate:      {s['pass_rate']:.1%}  ({s['passed']}/{s['total_cases']})")
    lines.append(f"  Passed: {s['passed']}  |  Warned: {s['warned']}  |  Failed: {s['failed']}")
    lines.append(f"  Thresholds:     pass >= {s['pass_threshold']}, warn >= {s['warning_threshold']}")
    lines.append("")

    # By tag
    if suite_result.get("by_tag"):
        lines.append("  Scores by Tag:")
        for tag, avg in sorted(suite_result["by_tag"].items()):
            lines.append(f"    {tag:30s} {avg:.1%}")
        lines.append("")

    # Per-case detail
    lines.append("  Per-Case Results:")
    lines.append("  " + "-" * 52)
    for r in suite_result["results"]:
        status_icon = "PASS" if r["status"] == "pass" else "WARN" if r["status"] == "warn" else "FAIL"
        tag_str = ", ".join(r["tags"][:3]) if r["tags"] else ""
        lines.append(f"  [{status_icon}] {r['test_id']:30s} {r['score']:.1%}  ({r['checks_passed']}/{r['checks_run']} checks)  {tag_str}")

        # Show failing checks
        if r["status"] != "pass":
            for check in r["checks"]:
                if not check["matched"]:
                    method = check["method"]
                    if method == "contains" and "details" in check:
                        missing = [d["phrase"] for d in check["details"] if not d["found"]]
                        lines.append(f"         {method}: missing {missing[:3]}")
                    elif method == "not_contains" and "details" in check:
                        found = [d["phrase"] for d in check["details"] if d["found"]]
                        lines.append(f"         {method}: violations {found[:3]}")
                    elif method == "required_fields" and "missing" in check:
                        lines.append(f"         {method}: missing {check['missing'][:3]}")
                    elif method == "regex":
                        lines.append(f"         {method}: pattern did not match")
                    elif method == "exact_match":
                        lines.append(f"         {method}: output does not match expected")
                    elif method == "max_tokens":
                        lines.append(f"         {method}: {check.get('estimated_tokens', '?')} tokens (max {check.get('max_tokens', '?')})")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score evaluation results from JSON test cases against expected outputs (exact match, contains, regex).",
        epilog=(
            "Test case JSON format:\n"
            '  [{"test_id": "tc-001", "actual": "output text",\n'
            '    "expected": {"contains": ["word1"], "regex": "^pattern$"},\n'
            '    "tags": ["happy-path"]}]\n\n'
            "Example: python eval_scorer.py test_results.json --json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("suite_file", help="Path to JSON file containing test cases with actual outputs and expected criteria")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--fail-under", type=float, default=None,
                        help="Exit with code 1 if average score is below this threshold (e.g., 0.80)")
    args = parser.parse_args()

    if not os.path.isfile(args.suite_file):
        print(f"Error: file not found: {args.suite_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.suite_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON in {args.suite_file}: {e}", file=sys.stderr)
            sys.exit(1)

    # Accept either a list or a dict with a "test_cases" key.
    if isinstance(data, dict):
        test_cases = data.get("test_cases", data.get("tests", []))
    elif isinstance(data, list):
        test_cases = data
    else:
        print("Error: JSON root must be a list of test cases or an object with a 'test_cases' key.", file=sys.stderr)
        sys.exit(1)

    if not test_cases:
        print("Error: no test cases found in input file.", file=sys.stderr)
        sys.exit(1)

    suite_result = score_suite(test_cases)

    if args.json:
        print(json.dumps(suite_result, indent=2))
    else:
        print(format_human(suite_result))

    # Exit code for CI integration.
    if args.fail_under is not None:
        avg = suite_result["summary"]["average_score"]
        if avg < args.fail_under:
            sys.exit(1)


if __name__ == "__main__":
    main()
