#!/usr/bin/env python3
"""Scan commit messages and diff summaries for breaking change indicators.

Analyzes git log output and optional diff stat summaries to detect breaking
changes through multiple heuristic signals: the conventional commit ! suffix,
BREAKING CHANGE footers, removal of public APIs, renamed/deleted files, and
keyword patterns in commit messages and diffs.

Usage:
    git log v1.0.0..HEAD --pretty=format:'%H%n%s%n%b%n---COMMIT_END---' --no-merges | python breaking_change_detector.py
    python breaking_change_detector.py --file git-log.txt
    python breaking_change_detector.py --file git-log.txt --diff-file diff-stat.txt
    python breaking_change_detector.py --file git-log.txt --json
    python breaking_change_detector.py --file git-log.txt --severity high
"""

import argparse
import json
import re
import sys
from collections import OrderedDict

COMMIT_DELIMITER = "---COMMIT_END---"

COMMIT_PATTERN = re.compile(
    r"^(?P<type>feat|fix|perf|refactor|docs|test|build|ci|chore|security|deprecated|remove)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?"
    r":\s*(?P<description>.+)$"
)

BREAKING_FOOTER_PATTERN = re.compile(
    r"BREAKING CHANGE:\s*(.+)", re.DOTALL
)

# Keyword patterns that suggest breaking changes in commit messages
BREAKING_KEYWORDS = [
    (r"\bremov(?:e|ed|ing|es)\b.*\b(?:api|endpoint|field|column|method|function|class|param|argument|route)\b", "high"),
    (r"\brenam(?:e|ed|ing|es)\b.*\b(?:api|endpoint|field|column|method|function|class|param|argument|route)\b", "high"),
    (r"\bdelet(?:e|ed|ing|es)\b.*\b(?:api|endpoint|field|column|table|method|function|class|route)\b", "high"),
    (r"\bdeprecate[ds]?\b", "medium"),
    (r"\bdrop(?:ped|ping|s)?\b.*\bsupport\b", "high"),
    (r"\bmigrat(?:e|ion|ing)\b", "medium"),
    (r"\bincompatible\b", "high"),
    (r"\bbreaking\b", "high"),
    (r"\bnon[- ]?backward[s]?\b", "high"),
    (r"\bbackward[s]?[- ]incompatible\b", "high"),
    (r"\brequire[ds]?\b.*\bmigration\b", "high"),
    (r"\bchanged?\b.*\b(?:signature|return type|schema|contract|interface)\b", "medium"),
    (r"\breplac(?:e|ed|ing)\b.*\b(?:api|endpoint|method|function)\b", "medium"),
    (r"\bmajor\b.*\b(?:version|upgrade|update)\b", "medium"),
    (r"\bv\d+\b.*\b(?:removed|dropped|deleted)\b", "high"),
]

# Patterns in diff stats suggesting breaking changes
DIFF_BREAKING_PATTERNS = [
    (r"(?:^|\s)(?:delete mode|rename)\s.*(?:api|schema|model|migration|interface|proto)", "high"),
    (r"\b\d+\s+files?\s+changed.*\d+\s+deletions", "low"),
    (r"(?:\.proto|schema\.\w+|openapi\.\w+|swagger\.\w+)\s.*\|.*[-]+", "medium"),
    (r"(?:routes|endpoints|api)\.\w+\s.*\|.*[-]+", "medium"),
    (r"migration.*\|", "low"),
]

SEVERITY_LEVELS = {"high": 3, "medium": 2, "low": 1}


def parse_raw_log(text):
    """Split raw git log text into individual commit blocks."""
    blocks = text.split(COMMIT_DELIMITER)
    commits = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        if len(lines) < 2:
            continue
        commit_hash = lines[0].strip()
        subject = lines[1].strip()
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        if commit_hash and subject:
            commits.append({
                "hash": commit_hash,
                "short_hash": commit_hash[:7],
                "subject": subject,
                "body": body,
            })
    return commits


def detect_conventional_breaking(commit):
    """Detect breaking changes from conventional commit markers."""
    indicators = []
    subject = commit["subject"]
    body = commit["body"]

    match = COMMIT_PATTERN.match(subject)
    if match and match.group("breaking"):
        indicators.append({
            "source": "conventional_commit_bang",
            "severity": "high",
            "detail": f"Commit type has '!' breaking change marker: {subject}",
            "evidence": subject,
        })

    if body:
        footer_match = BREAKING_FOOTER_PATTERN.search(body)
        if footer_match:
            description = footer_match.group(1).strip()
            # Truncate long descriptions for display
            if len(description) > 200:
                description = description[:200] + "..."
            indicators.append({
                "source": "breaking_change_footer",
                "severity": "high",
                "detail": f"BREAKING CHANGE footer found",
                "evidence": description,
            })

    return indicators


def detect_keyword_breaking(commit):
    """Detect potential breaking changes from keyword patterns."""
    indicators = []
    full_text = f"{commit['subject']} {commit['body']}".lower()

    for pattern, severity in BREAKING_KEYWORDS:
        if re.search(pattern, full_text, re.IGNORECASE):
            # Find the matching line for evidence
            evidence_line = None
            for line in f"{commit['subject']}\n{commit['body']}".split("\n"):
                if re.search(pattern, line, re.IGNORECASE):
                    evidence_line = line.strip()
                    break

            indicators.append({
                "source": "keyword_heuristic",
                "severity": severity,
                "detail": f"Keyword pattern matched: {pattern}",
                "evidence": evidence_line or full_text[:100],
            })
            # Only report the first keyword match per pattern category
            break

    return indicators


def detect_diff_breaking(diff_text):
    """Detect breaking changes from diff stat output."""
    indicators = []
    if not diff_text:
        return indicators

    for line in diff_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        for pattern, severity in DIFF_BREAKING_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                indicators.append({
                    "source": "diff_heuristic",
                    "severity": severity,
                    "detail": f"Diff pattern matched: {pattern}",
                    "evidence": line[:150],
                })
                break

    return indicators


def analyze_commit(commit, diff_text=None):
    """Run all detection methods on a single commit."""
    indicators = []
    indicators.extend(detect_conventional_breaking(commit))
    indicators.extend(detect_keyword_breaking(commit))
    if diff_text:
        indicators.extend(detect_diff_breaking(diff_text))

    if not indicators:
        return None

    # Determine overall severity (highest found)
    max_severity = max(
        (SEVERITY_LEVELS.get(i["severity"], 0) for i in indicators),
        default=0,
    )
    severity_name = {v: k for k, v in SEVERITY_LEVELS.items()}.get(max_severity, "low")

    return {
        "hash": commit["hash"],
        "short_hash": commit["short_hash"],
        "subject": commit["subject"],
        "severity": severity_name,
        "indicator_count": len(indicators),
        "indicators": indicators,
        "confirmed": any(
            i["source"] in ("conventional_commit_bang", "breaking_change_footer")
            for i in indicators
        ),
    }


def filter_by_severity(results, min_severity):
    """Filter results to only include entries at or above the minimum severity."""
    min_level = SEVERITY_LEVELS.get(min_severity, 0)
    return [r for r in results if SEVERITY_LEVELS.get(r["severity"], 0) >= min_level]


def format_human_readable(results, stats):
    """Render detection results as human-readable text."""
    lines = []
    lines.append("=" * 65)
    lines.append("BREAKING CHANGE DETECTION REPORT")
    lines.append("=" * 65)
    lines.append("")
    lines.append(f"Commits scanned:        {stats['total_scanned']}")
    lines.append(f"Breaking changes found:  {stats['breaking_found']}")
    lines.append(f"  Confirmed (explicit):  {stats['confirmed']}")
    lines.append(f"  Suspected (heuristic): {stats['suspected']}")
    lines.append(f"Severity breakdown:")
    lines.append(f"  High:   {stats['severity_high']}")
    lines.append(f"  Medium: {stats['severity_medium']}")
    lines.append(f"  Low:    {stats['severity_low']}")
    lines.append(f"Recommended bump:        {stats['recommended_bump']}")
    lines.append("")

    if not results:
        lines.append("No breaking changes detected.")
        return "\n".join(lines)

    for result in results:
        confirmed_tag = "CONFIRMED" if result["confirmed"] else "SUSPECTED"
        severity_tag = result["severity"].upper()
        lines.append("-" * 65)
        lines.append(f"[{severity_tag}] [{confirmed_tag}] {result['short_hash']}  {result['subject']}")
        lines.append("")

        for indicator in result["indicators"]:
            source_label = indicator["source"].replace("_", " ").title()
            lines.append(f"  Source:   {source_label}")
            lines.append(f"  Severity: {indicator['severity']}")
            if indicator.get("evidence"):
                evidence = indicator["evidence"]
                if len(evidence) > 120:
                    evidence = evidence[:120] + "..."
                lines.append(f"  Evidence: {evidence}")
            lines.append("")

    # Migration guidance reminder
    lines.append("=" * 65)
    lines.append("RECOMMENDED ACTIONS")
    lines.append("=" * 65)
    lines.append("")

    confirmed_results = [r for r in results if r["confirmed"]]
    suspected_results = [r for r in results if not r["confirmed"]]

    if confirmed_results:
        lines.append("Confirmed breaking changes require:")
        lines.append("  1. Major version bump (semver)")
        lines.append("  2. Migration guide in release notes")
        lines.append("  3. Deprecation notice for removed features")
        lines.append("")

    if suspected_results:
        lines.append("Suspected breaking changes should be reviewed:")
        lines.append("  1. Verify if the change affects the public API")
        lines.append("  2. If confirmed, add BREAKING CHANGE footer to commit")
        lines.append("  3. Document migration path for affected users")
        lines.append("")

    return "\n".join(lines)


def read_input(args):
    """Read git log text from file or stdin."""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Error: No input provided. Pipe git log output or use --file.", file=sys.stderr)
    print("Example: git log v1.0.0..HEAD --pretty=format:'%H%n%s%n%b%n---COMMIT_END---' "
          "--no-merges | python breaking_change_detector.py", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Scan commit messages and diffs for breaking change indicators.",
        epilog="Reads git log output formatted with ---COMMIT_END--- delimiters. "
               "Detects breaking changes via conventional commit markers, keyword "
               "heuristics, and optional diff analysis.",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to file containing git log output (default: read from stdin)",
    )
    parser.add_argument(
        "--diff-file",
        help="Path to file containing diff stat output for additional analysis",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of human-readable text",
    )
    parser.add_argument(
        "--severity", "-s",
        choices=["low", "medium", "high"],
        default="low",
        help="Minimum severity level to report (default: low)",
    )
    parser.add_argument(
        "--confirmed-only", "-c",
        action="store_true",
        help="Only show confirmed breaking changes (conventional commit markers)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)",
    )

    args = parser.parse_args()

    raw_text = read_input(args)
    commits = parse_raw_log(raw_text)

    diff_text = None
    if args.diff_file:
        with open(args.diff_file, "r", encoding="utf-8") as f:
            diff_text = f.read()

    # Analyze each commit
    results = []
    for commit in commits:
        result = analyze_commit(commit, diff_text=diff_text)
        if result:
            results.append(result)

    # Apply filters
    results = filter_by_severity(results, args.severity)
    if args.confirmed_only:
        results = [r for r in results if r["confirmed"]]

    # Compute stats
    confirmed_count = sum(1 for r in results if r["confirmed"])
    stats = {
        "total_scanned": len(commits),
        "breaking_found": len(results),
        "confirmed": confirmed_count,
        "suspected": len(results) - confirmed_count,
        "severity_high": sum(1 for r in results if r["severity"] == "high"),
        "severity_medium": sum(1 for r in results if r["severity"] == "medium"),
        "severity_low": sum(1 for r in results if r["severity"] == "low"),
        "recommended_bump": "major" if results else "see commit types",
    }

    if args.json_output:
        output = {
            "stats": stats,
            "results": results,
        }
        print(json.dumps(output, indent=args.indent, default=str))
    else:
        print(format_human_readable(results, stats))


if __name__ == "__main__":
    main()
