#!/usr/bin/env python3
"""Analyze Playwright test files for anti-patterns and quality issues.

Scans Playwright test files (.spec.ts, .test.ts) for common anti-patterns
including hardcoded waits, missing assertions, fragile selectors, flaky
indicators, and violations of the 10 golden rules.

Usage:
    python test_analyzer.py path/to/tests/
    python test_analyzer.py path/to/tests/ --severity high
    python test_analyzer.py path/to/tests/ --json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ANTI_PATTERNS = [
    {
        "id": "WAIT_TIMEOUT",
        "name": "Hardcoded waitForTimeout",
        "pattern": r"waitForTimeout\s*\(",
        "severity": "high",
        "message": "Replace waitForTimeout() with web-first assertions like expect(locator).toBeVisible()",
        "rule": "Rule #2: Never page.waitForTimeout()",
    },
    {
        "id": "WAIT_SLEEP",
        "name": "setTimeout / sleep pattern",
        "pattern": r"(?:setTimeout|sleep)\s*\(",
        "severity": "high",
        "message": "Avoid manual sleep/setTimeout; use Playwright auto-waiting assertions",
        "rule": "Rule #2: Never page.waitForTimeout()",
    },
    {
        "id": "CSS_SELECTOR",
        "name": "Raw CSS selector as primary locator",
        "pattern": r"page\.locator\s*\(\s*['\"][\.\#\[]",
        "severity": "medium",
        "message": "Prefer getByRole(), getByLabel(), getByText() over CSS selectors",
        "rule": "Rule #1: getByRole() over CSS/XPath",
    },
    {
        "id": "XPATH_SELECTOR",
        "name": "XPath selector usage",
        "pattern": r"page\.locator\s*\(\s*['\"]\/\/",
        "severity": "high",
        "message": "XPath selectors are fragile; use semantic locators instead",
        "rule": "Rule #1: getByRole() over CSS/XPath",
    },
    {
        "id": "HARDCODED_URL",
        "name": "Hardcoded URL in test",
        "pattern": r"(?:goto|navigate)\s*\(\s*['\"]https?://",
        "severity": "medium",
        "message": "Use baseURL in playwright.config.ts; pass relative paths to goto()",
        "rule": "Rule #5: baseURL in config",
    },
    {
        "id": "NO_ASSERTION",
        "name": "Test block without expect()",
        "pattern": None,
        "severity": "high",
        "message": "Test has no assertions; every test should verify expected behavior",
        "rule": "Rule #9: One behavior per test",
    },
    {
        "id": "SNAPSHOT_NO_AWAIT",
        "name": "Non-awaited locator value in expect",
        "pattern": r"expect\s*\(\s*await\s+\w+\.(?:textContent|innerText|innerHTML|getAttribute|inputValue)\s*\(",
        "severity": "high",
        "message": "Use expect(locator).toHaveText() instead of expect(await locator.textContent()); the latter does not auto-retry",
        "rule": "Rule #3: expect(locator) auto-retries",
    },
    {
        "id": "SHARED_STATE",
        "name": "Mutable shared variable between tests",
        "pattern": r"(?:let|var)\s+\w+\s*[=;]\s*$",
        "severity": "medium",
        "message": "Shared mutable state between tests causes flakiness; use fixtures or beforeEach",
        "rule": "Rule #4: Isolate every test",
    },
    {
        "id": "FORCE_CLICK",
        "name": "Force click bypassing actionability",
        "pattern": r"\.click\s*\(\s*\{\s*force\s*:\s*true",
        "severity": "medium",
        "message": "force:true bypasses actionability checks; fix the underlying visibility/overlay issue instead",
        "rule": "Rule #2: Never page.waitForTimeout()",
    },
    {
        "id": "NTH_CHILD",
        "name": "Fragile nth-child / nth-of-type selector",
        "pattern": r"(?:nth-child|nth-of-type)\s*\(",
        "severity": "medium",
        "message": "nth-child selectors break on DOM changes; use semantic locators or data-testid",
        "rule": "Rule #1: getByRole() over CSS/XPath",
    },
    {
        "id": "PAGE_WAIT_SELECTOR",
        "name": "Deprecated waitForSelector usage",
        "pattern": r"waitForSelector\s*\(",
        "severity": "low",
        "message": "waitForSelector is rarely needed; use web-first assertions (expect) for waiting",
        "rule": "Rule #2: Never page.waitForTimeout()",
    },
    {
        "id": "GLOBAL_PAGE",
        "name": "Global page variable outside fixtures",
        "pattern": r"(?:^|\n)\s*(?:let|var|const)\s+page\s*[=:]",
        "severity": "low",
        "message": "Use Playwright fixtures (test.extend) instead of global page variables",
        "rule": "Rule #8: Fixtures over globals",
    },
    {
        "id": "MULTIPLE_GOTO",
        "name": "Multiple goto() calls in single test",
        "pattern": None,
        "severity": "low",
        "message": "Multiple navigations in one test may indicate testing multiple behaviors; consider splitting",
        "rule": "Rule #9: One behavior per test",
    },
]

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def find_test_files(path):
    """Recursively find Playwright test files."""
    test_files = []
    p = Path(path)
    if p.is_file():
        test_files.append(p)
    else:
        for ext_pattern in ["**/*.spec.ts", "**/*.test.ts", "**/*.spec.js", "**/*.test.js"]:
            test_files.extend(p.glob(ext_pattern))
    return sorted(set(test_files))


def extract_test_blocks(content):
    """Extract individual test blocks with their line ranges."""
    blocks = []
    lines = content.split("\n")
    # Find test(...) or it(...) calls
    test_pattern = re.compile(r"^\s*(?:test|it)\s*\(\s*['\"](.+?)['\"]")
    brace_depth = 0
    current_test = None
    start_line = 0

    for i, line in enumerate(lines, 1):
        match = test_pattern.match(line)
        if match and current_test is None:
            current_test = match.group(1)
            start_line = i
            brace_depth = 0

        if current_test is not None:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "{" in content[sum(len(l) + 1 for l in lines[:start_line - 1]):]:
                block_content = "\n".join(lines[start_line - 1:i])
                blocks.append({
                    "name": current_test,
                    "start_line": start_line,
                    "end_line": i,
                    "content": block_content,
                })
                current_test = None
    return blocks


def check_no_assertion(test_block):
    """Check if a test block contains no expect() calls."""
    return "expect(" not in test_block["content"] and "expect (" not in test_block["content"]


def check_multiple_goto(test_block):
    """Check if a test block has multiple goto() calls."""
    goto_count = len(re.findall(r"\.goto\s*\(", test_block["content"]))
    return goto_count > 1


def analyze_file(filepath):
    """Analyze a single test file for anti-patterns."""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [{"file": str(filepath), "error": str(e)}]

    lines = content.split("\n")
    test_blocks = extract_test_blocks(content)

    # Regex-based pattern checks
    for ap in ANTI_PATTERNS:
        if ap["pattern"] is None:
            continue
        regex = re.compile(ap["pattern"])
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                findings.append({
                    "file": str(filepath),
                    "line": i,
                    "code": line.strip(),
                    "anti_pattern": ap["id"],
                    "name": ap["name"],
                    "severity": ap["severity"],
                    "message": ap["message"],
                    "rule": ap["rule"],
                })

    # Structural checks on test blocks
    for block in test_blocks:
        if check_no_assertion(block):
            ap = next(a for a in ANTI_PATTERNS if a["id"] == "NO_ASSERTION")
            findings.append({
                "file": str(filepath),
                "line": block["start_line"],
                "code": f"test('{block['name']}', ...)",
                "anti_pattern": ap["id"],
                "name": ap["name"],
                "severity": ap["severity"],
                "message": ap["message"],
                "rule": ap["rule"],
            })

        if check_multiple_goto(block):
            ap = next(a for a in ANTI_PATTERNS if a["id"] == "MULTIPLE_GOTO")
            findings.append({
                "file": str(filepath),
                "line": block["start_line"],
                "code": f"test('{block['name']}', ...)",
                "anti_pattern": ap["id"],
                "name": ap["name"],
                "severity": ap["severity"],
                "message": ap["message"],
                "rule": ap["rule"],
            })

    return findings


def format_human(findings, stats):
    """Format findings as human-readable output."""
    output = []
    output.append("=" * 70)
    output.append("PLAYWRIGHT TEST ANALYZER")
    output.append("=" * 70)
    output.append("")

    if not findings:
        output.append("No anti-patterns detected. Your tests look clean!")
        return "\n".join(output)

    # Group by file
    by_file = defaultdict(list)
    for f in findings:
        by_file[f["file"]].append(f)

    for filepath, file_findings in sorted(by_file.items()):
        output.append(f"File: {filepath}")
        output.append("-" * 70)
        sorted_findings = sorted(file_findings, key=lambda x: SEVERITY_ORDER.get(x["severity"], 9))
        for finding in sorted_findings:
            sev = finding["severity"].upper()
            output.append(f"  [{sev}] Line {finding['line']}: {finding['name']}")
            output.append(f"         Code: {finding['code'][:80]}")
            output.append(f"         Fix:  {finding['message']}")
            output.append(f"         Ref:  {finding['rule']}")
            output.append("")
        output.append("")

    # Summary
    output.append("=" * 70)
    output.append("SUMMARY")
    output.append("=" * 70)
    output.append(f"  Files scanned:    {stats['files_scanned']}")
    output.append(f"  Total findings:   {stats['total_findings']}")
    output.append(f"  High severity:    {stats['high']}")
    output.append(f"  Medium severity:  {stats['medium']}")
    output.append(f"  Low severity:     {stats['low']}")
    output.append("")

    if stats["high"] > 0:
        output.append("  VERDICT: NEEDS ATTENTION - High severity issues found")
    elif stats["medium"] > 0:
        output.append("  VERDICT: ACCEPTABLE - Consider fixing medium issues")
    else:
        output.append("  VERDICT: GOOD - Only minor suggestions")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Playwright test files for anti-patterns and quality issues.",
        epilog="Example: python test_analyzer.py ./tests/e2e/ --severity medium",
    )
    parser.add_argument("path", help="Path to test file or directory containing test files")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")
    parser.add_argument(
        "--severity",
        choices=["high", "medium", "low"],
        default="low",
        help="Minimum severity to report (default: low, shows all)",
    )
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    test_files = find_test_files(target)
    if not test_files:
        print(f"No test files (.spec.ts/.test.ts) found in '{args.path}'.", file=sys.stderr)
        sys.exit(1)

    all_findings = []
    for tf in test_files:
        all_findings.extend(analyze_file(tf))

    # Filter by severity
    min_sev = SEVERITY_ORDER[args.severity]
    filtered = [f for f in all_findings if SEVERITY_ORDER.get(f.get("severity", "low"), 9) <= min_sev]

    stats = {
        "files_scanned": len(test_files),
        "total_findings": len(filtered),
        "high": sum(1 for f in filtered if f.get("severity") == "high"),
        "medium": sum(1 for f in filtered if f.get("severity") == "medium"),
        "low": sum(1 for f in filtered if f.get("severity") == "low"),
    }

    if args.json_output:
        result = {"stats": stats, "findings": filtered}
        print(json.dumps(result, indent=2))
    else:
        print(format_human(filtered, stats))


if __name__ == "__main__":
    main()
