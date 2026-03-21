#!/usr/bin/env python3
"""Runbook Validator — Validate runbooks for completeness and quality.

Checks runbook markdown files against a set of required sections, contact
information, rollback steps, monitoring links, verification blocks, and
time estimates. Reports missing elements with severity levels.

Usage:
    python runbook_validator.py runbook.md
    python runbook_validator.py runbook.md another.md
    python runbook_validator.py --dir docs/runbooks/
    python runbook_validator.py runbook.md --json
    python runbook_validator.py runbook.md --strict
"""

import argparse
import json
import os
import re
import sys
import textwrap
from pathlib import Path


# Required sections (heading text to search for, case-insensitive)
REQUIRED_SECTIONS = {
    "deployment": [
        "pre-deployment checklist",
        "rollback",
        "escalation",
    ],
    "incident": [
        "triage",
        "diagnose",
        "mitigate",
        "escalation",
    ],
    "database": [
        "backup",
        "rollback",
    ],
    "general": [
        "rollback",
        "escalation",
    ],
}

# Patterns that indicate quality markers
QUALITY_PATTERNS = {
    "verify_blocks": {
        "pattern": r"(?i)^VERIFY[:.]",
        "description": "VERIFY block after steps",
        "severity": "error",
        "min_count": 1,
    },
    "time_estimates": {
        "pattern": r"\(\d+\s*(?:min|minutes|hour|hours|sec|seconds)\)",
        "description": "Time estimate in step heading",
        "severity": "warning",
        "min_count": 1,
    },
    "code_blocks": {
        "pattern": r"^```",
        "description": "Code block with commands",
        "severity": "error",
        "min_count": 1,
    },
    "last_verified": {
        "pattern": r"(?i)last\s+verified[:]\s*\d{4}-\d{2}-\d{2}",
        "description": "Last verified date",
        "severity": "error",
        "min_count": 1,
    },
    "owner_field": {
        "pattern": r"(?i)\*\*owner\*\*[:]\s*\S+",
        "description": "Owner field",
        "severity": "error",
        "min_count": 1,
    },
    "env_vars_not_hardcoded": {
        "pattern": r"(?:postgres|mysql|mongodb)://\w+:\w+@[\w.]+",
        "description": "Hardcoded database URL (should use env var)",
        "severity": "error",
        "min_count": 0,  # 0 means we want zero matches (inverted check)
    },
    "checklist_items": {
        "pattern": r"^- \[[ x]\]",
        "description": "Checklist item",
        "severity": "warning",
        "min_count": 1,
    },
    "escalation_table": {
        "pattern": r"\|\s*L[123]\s*\|",
        "description": "Escalation table with L1/L2/L3",
        "severity": "warning",
        "min_count": 1,
    },
    "monitoring_links": {
        "pattern": r"(?i)dashboard[:]\s*(?:https?://\S+|\[.*\]\(.*\)|FILL IN)",
        "description": "Monitoring dashboard link or placeholder",
        "severity": "warning",
        "min_count": 1,
    },
}


def detect_runbook_type(content):
    """Detect the type of runbook from its content."""
    lower = content.lower()
    if "deployment runbook" in lower or "pre-deployment" in lower:
        return "deployment"
    if "incident response" in lower or "triage" in lower:
        return "incident"
    if "database maintenance" in lower or "vacuum" in lower:
        return "database"
    return "general"


def extract_headings(content):
    """Extract all markdown headings from content."""
    headings = []
    for line in content.split("\n"):
        match = re.match(r"^(#{1,6})\s+(.+)", line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({"level": level, "text": text})
    return headings


def count_pattern_matches(content, pattern):
    """Count how many lines match a regex pattern."""
    count = 0
    for line in content.split("\n"):
        if re.search(pattern, line):
            count += 1
    return count


def check_required_sections(content, runbook_type):
    """Check for required sections based on runbook type."""
    findings = []
    headings_lower = [h["text"].lower() for h in extract_headings(content)]
    required = REQUIRED_SECTIONS.get(runbook_type, REQUIRED_SECTIONS["general"])

    for section in required:
        found = any(section in h for h in headings_lower)
        if not found:
            findings.append({
                "check": "required_section",
                "severity": "error",
                "message": f"Missing required section: '{section}'",
                "suggestion": f"Add a '## {section.title()}' section",
            })

    return findings


def check_quality_patterns(content):
    """Check for quality patterns in the runbook."""
    findings = []

    for name, spec in QUALITY_PATTERNS.items():
        count = count_pattern_matches(content, spec["pattern"])

        if spec["min_count"] == 0:
            # Inverted check: we want zero matches
            if count > 0:
                findings.append({
                    "check": name,
                    "severity": spec["severity"],
                    "message": f"Found {count} instance(s) of: {spec['description']}",
                    "suggestion": "Use environment variables instead of hardcoded values",
                })
        else:
            if count < spec["min_count"]:
                findings.append({
                    "check": name,
                    "severity": spec["severity"],
                    "message": f"Missing: {spec['description']} (found {count}, need >= {spec['min_count']})",
                    "suggestion": f"Add at least {spec['min_count']} {spec['description'].lower()}",
                })

    return findings


def check_rollback_coverage(content):
    """Check that destructive steps have corresponding rollback instructions."""
    findings = []
    destructive_keywords = [
        "delete", "drop", "truncate", "migrate", "deploy",
        "scale", "restart", "terminate", "remove",
    ]

    lines = content.split("\n")
    has_rollback_section = any(
        re.match(r"^#{1,4}\s+.*rollback", line, re.IGNORECASE) for line in lines
    )

    destructive_found = False
    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in destructive_keywords):
            if re.search(r"```|^\s*(#|--|//)", line):
                continue  # skip comments and code fence markers
            if any(kw in lower for kw in destructive_keywords):
                destructive_found = True
                break

    if destructive_found and not has_rollback_section:
        findings.append({
            "check": "rollback_coverage",
            "severity": "error",
            "message": "Runbook contains destructive operations but no rollback section",
            "suggestion": "Add a '## Rollback' section with undo steps for each destructive action",
        })

    return findings


def check_step_numbering(content):
    """Check that steps are numbered consistently."""
    findings = []
    step_headings = re.findall(r"^#{2,3}\s+Step\s+(\d+)", content, re.MULTILINE)

    if not step_headings:
        findings.append({
            "check": "step_numbering",
            "severity": "warning",
            "message": "No numbered steps found (e.g., '## Step 1: ...')",
            "suggestion": "Use numbered step headings for clarity: '## Step 1: Description (X min)'",
        })
    else:
        numbers = [int(n) for n in step_headings]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            findings.append({
                "check": "step_numbering",
                "severity": "warning",
                "message": f"Step numbering is not sequential: found {numbers}, expected {expected}",
                "suggestion": "Re-number steps sequentially starting from 1",
            })

    return findings


def check_placeholder_commands(content):
    """Check for placeholder values in commands that should be env vars."""
    findings = []
    placeholder_patterns = [
        (r"<[A-Z_]+>", "angle-bracket placeholder"),
        (r"YOUR_[A-Z_]+", "YOUR_ placeholder"),
        (r"CHANGEME", "CHANGEME placeholder"),
        (r"TODO", "TODO marker"),
        (r"xxx+", "xxx placeholder"),
    ]

    in_code_block = False
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            for pattern, desc in placeholder_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "check": "placeholder_command",
                        "severity": "warning",
                        "message": f"Line {i}: Found {desc} in command — '{line.strip()}'",
                        "suggestion": "Replace with environment variable reference (e.g., $PROD_DB_URL)",
                    })

    return findings


def validate_runbook(filepath):
    """Run all validation checks on a single runbook file."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return {
            "file": str(filepath),
            "valid": False,
            "errors": 1,
            "warnings": 0,
            "findings": [{
                "check": "file_exists",
                "severity": "error",
                "message": f"File not found: {filepath}",
                "suggestion": "Verify the file path",
            }],
        }

    if not content.strip():
        return {
            "file": str(filepath),
            "valid": False,
            "errors": 1,
            "warnings": 0,
            "findings": [{
                "check": "file_empty",
                "severity": "error",
                "message": "Runbook file is empty",
                "suggestion": "Add runbook content or generate using runbook_scaffolder.py",
            }],
        }

    runbook_type = detect_runbook_type(content)
    findings = []
    findings.extend(check_required_sections(content, runbook_type))
    findings.extend(check_quality_patterns(content))
    findings.extend(check_rollback_coverage(content))
    findings.extend(check_step_numbering(content))
    findings.extend(check_placeholder_commands(content))

    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")

    return {
        "file": str(filepath),
        "runbook_type": runbook_type,
        "valid": errors == 0,
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
    }


def format_human_output(results):
    """Format validation results for human consumption."""
    lines = []
    total_errors = 0
    total_warnings = 0

    for result in results:
        total_errors += result["errors"]
        total_warnings += result["warnings"]

        status = "PASS" if result["valid"] else "FAIL"
        lines.append(f"\n{'=' * 60}")
        lines.append(f"[{status}] {result['file']}")
        if "runbook_type" in result:
            lines.append(f"  Type: {result['runbook_type']}")
        lines.append(f"  Errors: {result['errors']}  Warnings: {result['warnings']}")
        lines.append(f"{'=' * 60}")

        for finding in result["findings"]:
            icon = "ERROR" if finding["severity"] == "error" else "WARN "
            lines.append(f"  [{icon}] {finding['message']}")
            lines.append(f"         -> {finding['suggestion']}")

        if not result["findings"]:
            lines.append("  All checks passed.")

    lines.append(f"\n{'=' * 60}")
    lines.append(f"SUMMARY: {len(results)} file(s) checked")
    lines.append(f"  Total errors:   {total_errors}")
    lines.append(f"  Total warnings: {total_warnings}")
    passed = sum(1 for r in results if r["valid"])
    lines.append(f"  Passed: {passed}/{len(results)}")
    lines.append(f"{'=' * 60}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate runbook markdown files for completeness and quality.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Checks performed:
              - Required sections (rollback, escalation, etc.) based on runbook type
              - VERIFY blocks after steps
              - Time estimates in step headings
              - Code blocks with copy-paste commands
              - Last verified date
              - Owner field
              - Hardcoded credentials (flags them as errors)
              - Checklist items
              - Escalation table with L1/L2/L3
              - Monitoring dashboard links
              - Sequential step numbering
              - Placeholder values in commands

            Exit codes:
              0 = all runbooks valid
              1 = one or more errors found
              2 = input error
        """),
    )
    parser.add_argument("files", nargs="*", help="Runbook markdown files to validate")
    parser.add_argument("--dir", "-d", help="Directory containing runbook markdown files")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors (exit 1 if any warnings)")

    args = parser.parse_args()

    files = list(args.files) if args.files else []

    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_dir():
            print(f"Error: Directory not found — {args.dir}", file=sys.stderr)
            sys.exit(2)
        files.extend(str(p) for p in sorted(dir_path.glob("*.md")))

    if not files:
        parser.print_help()
        print("\nError: No files specified. Provide file paths or use --dir.", file=sys.stderr)
        sys.exit(2)

    results = [validate_runbook(f) for f in files]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human_output(results))

    has_errors = any(r["errors"] > 0 for r in results)
    has_warnings = any(r["warnings"] > 0 for r in results)

    if has_errors:
        sys.exit(1)
    if args.strict and has_warnings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
