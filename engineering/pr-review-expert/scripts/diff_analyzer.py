#!/usr/bin/env python3
"""Analyze git diff output for risk indicators.

Scans unified diff input for large file changes, sensitive path patterns,
configuration modifications, breaking change signals, and security red flags.
Produces a prioritized risk report in human-readable or JSON format.

Usage:
    git diff main...HEAD | python diff_analyzer.py
    python diff_analyzer.py --file /tmp/pr-123.diff
    python diff_analyzer.py --file /tmp/pr-123.diff --json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple


# --- Risk pattern definitions ---

SENSITIVE_PATHS = [
    (r"(^|/)\.env", "Environment config file", "HIGH"),
    (r"(^|/)auth/", "Authentication module", "HIGH"),
    (r"(^|/)security/", "Security module", "HIGH"),
    (r"(^|/)middleware/", "Middleware layer", "MEDIUM"),
    (r"(^|/)migrations?/", "Database migration", "HIGH"),
    (r"(^|/)config/", "Configuration directory", "MEDIUM"),
    (r"(^|/)secrets?/", "Secrets directory", "CRITICAL"),
    (r"(^|/)payments?/", "Payment processing", "CRITICAL"),
    (r"(^|/)crypto/", "Cryptography module", "HIGH"),
    (r"(^|/)docker-compose", "Docker orchestration", "MEDIUM"),
    (r"(^|/)Dockerfile", "Container definition", "MEDIUM"),
    (r"(^|/)k8s/|kubernetes/", "Kubernetes config", "HIGH"),
    (r"(^|/)terraform/|\.tf$", "Infrastructure as code", "HIGH"),
    (r"(^|/)ci/|\.github/workflows/", "CI/CD pipeline", "MEDIUM"),
    (r"(^|/)nginx|apache|caddy", "Web server config", "MEDIUM"),
]

CONFIG_FILE_PATTERNS = [
    r"\.ya?ml$", r"\.json$", r"\.toml$", r"\.ini$", r"\.cfg$",
    r"\.conf$", r"\.env", r"Makefile$", r"\.lock$",
    r"requirements.*\.txt$", r"package\.json$", r"go\.mod$",
    r"Cargo\.toml$", r"pom\.xml$", r"build\.gradle$",
]

BREAKING_PATTERNS = [
    (r"^\+.*\bDROP\s+(TABLE|COLUMN|INDEX)", "SQL destructive operation", "CRITICAL"),
    (r"^\+.*\bTRUNCATE\b", "SQL truncate", "CRITICAL"),
    (r"^\+.*\bALTER.*NOT\s+NULL", "Non-nullable column addition", "HIGH"),
    (r"^-.*\brouter\.(get|post|put|delete|patch)\(", "API endpoint removal", "HIGH"),
    (r"^-.*\b@(app|api)\.(get|post|put|delete)\b", "API route removal", "HIGH"),
    (r"^-.*\bexport\s+(interface|type)\s+", "Exported type removal", "HIGH"),
    (r"^-.*\bexport\s+(function|const|class)\s+", "Exported symbol removal", "HIGH"),
    (r"^\+.*\bDEPRECAT", "Deprecation notice added", "MEDIUM"),
    (r"^-.*\benv\.[A-Z_]+", "Environment variable removal", "MEDIUM"),
]

SECURITY_PATTERNS = [
    (r"^\+.*\b(password|secret|api_key|token|private_key)\s*=\s*['\"][^'\"]{8,}", "Hardcoded secret", "CRITICAL"),
    (r"^\+.*AKIA[0-9A-Z]{16}", "AWS access key", "CRITICAL"),
    (r"^\+.*\beval\s*\(", "Dynamic code execution (eval)", "HIGH"),
    (r"^\+.*\bexec\s*\(", "Dynamic code execution (exec)", "HIGH"),
    (r"^\+.*dangerouslySetInnerHTML", "XSS vector (React)", "HIGH"),
    (r"^\+.*innerHTML\s*=", "XSS vector (innerHTML)", "HIGH"),
    (r"^\+.*__proto__", "Prototype pollution", "HIGH"),
    (r"^\+.*\bcreateHash\(['\"]md5", "Weak hash (MD5)", "MEDIUM"),
    (r"^\+.*\bcreateHash\(['\"]sha1", "Weak hash (SHA1)", "MEDIUM"),
    (r"^\+.*subprocess\.call\(.*shell\s*=\s*True", "Shell injection risk", "HIGH"),
    (r"^\+.*path\.join\(.*req\.", "Potential path traversal", "MEDIUM"),
]

# Thresholds
LARGE_FILE_THRESHOLD = 200  # lines changed
LARGE_PR_THRESHOLD = 500    # total lines changed


def parse_diff(diff_text: str) -> List[Dict]:
    """Parse unified diff into per-file records."""
    files = []
    current_file = None
    current_lines = []

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current_file:
                files.append({"path": current_file, "lines": current_lines})
            match = re.search(r"b/(.+)$", line)
            current_file = match.group(1) if match else "unknown"
            current_lines = []
        elif current_file is not None:
            current_lines.append(line)

    if current_file:
        files.append({"path": current_file, "lines": current_lines})

    return files


def count_changes(lines: List[str]) -> Tuple[int, int]:
    """Count additions and deletions in diff lines."""
    additions = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    return additions, deletions


def check_sensitive_paths(file_path: str) -> List[Dict]:
    """Check if file path matches sensitive patterns."""
    findings = []
    for pattern, desc, severity in SENSITIVE_PATHS:
        if re.search(pattern, file_path, re.IGNORECASE):
            findings.append({
                "type": "sensitive_path",
                "severity": severity,
                "description": desc,
                "file": file_path,
            })
    return findings


def check_config_file(file_path: str) -> bool:
    """Check if a file is a configuration file."""
    return any(re.search(p, file_path, re.IGNORECASE) for p in CONFIG_FILE_PATTERNS)


def scan_patterns(lines: List[str], file_path: str, patterns, category: str) -> List[Dict]:
    """Scan diff lines against a list of regex patterns."""
    findings = []
    for i, line in enumerate(lines, 1):
        for pattern, desc, severity in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "type": category,
                    "severity": severity,
                    "description": desc,
                    "file": file_path,
                    "line_number": i,
                    "content": line.strip()[:120],
                })
    return findings


def analyze_diff(diff_text: str, large_file_thresh: int = LARGE_FILE_THRESHOLD, large_pr_thresh: int = LARGE_PR_THRESHOLD) -> Dict:
    """Run full analysis on diff text and return structured results."""
    files = parse_diff(diff_text)
    all_findings = []
    file_stats = []
    total_additions = 0
    total_deletions = 0
    large_files = []
    config_files = []

    for f in files:
        path = f["path"]
        lines = f["lines"]
        additions, deletions = count_changes(lines)
        total_additions += additions
        total_deletions += deletions
        total_changed = additions + deletions

        stat = {
            "path": path,
            "additions": additions,
            "deletions": deletions,
            "total": total_changed,
        }
        file_stats.append(stat)

        # Large file check
        if total_changed > large_file_thresh:
            large_files.append(stat)
            all_findings.append({
                "type": "large_file",
                "severity": "MEDIUM",
                "description": f"Large change: {total_changed} lines modified",
                "file": path,
            })

        # Sensitive path check
        all_findings.extend(check_sensitive_paths(path))

        # Config file check
        if check_config_file(path):
            config_files.append(path)
            all_findings.append({
                "type": "config_change",
                "severity": "MEDIUM",
                "description": "Configuration file modified",
                "file": path,
            })

        # Breaking pattern scan
        all_findings.extend(scan_patterns(lines, path, BREAKING_PATTERNS, "breaking_change"))

        # Security pattern scan
        all_findings.extend(scan_patterns(lines, path, SECURITY_PATTERNS, "security"))

    # PR-level size check
    total_changed = total_additions + total_deletions
    if total_changed > large_pr_thresh:
        all_findings.append({
            "type": "large_pr",
            "severity": "HIGH",
            "description": f"Large PR: {total_changed} total lines changed across {len(files)} files. Consider splitting.",
            "file": "PR-level",
        })

    # Deduplicate findings
    seen = set()
    unique_findings = []
    for f in all_findings:
        key = (f["type"], f["severity"], f["file"], f.get("line_number", 0))
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)

    # Compute overall risk
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    max_sev = max((severity_order.get(f["severity"], 0) for f in unique_findings), default=0)
    risk_map = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW", 0: "LOW"}
    overall_risk = risk_map[max_sev]

    severity_counts = defaultdict(int)
    for f in unique_findings:
        severity_counts[f["severity"]] += 1

    return {
        "overall_risk": overall_risk,
        "total_files": len(files),
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "total_changed": total_changed,
        "severity_counts": dict(severity_counts),
        "large_files": large_files,
        "config_files_changed": config_files,
        "findings": sorted(unique_findings, key=lambda x: severity_order.get(x["severity"], 0), reverse=True),
    }


def format_human(result: Dict) -> str:
    """Format analysis results for human consumption."""
    lines = []
    lines.append("=" * 60)
    lines.append("  DIFF RISK ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Overall Risk:   {result['overall_risk']}")
    lines.append(f"Files Changed:  {result['total_files']}")
    lines.append(f"Lines Added:    +{result['total_additions']}")
    lines.append(f"Lines Removed:  -{result['total_deletions']}")
    lines.append(f"Total Changed:  {result['total_changed']}")
    lines.append("")

    sc = result["severity_counts"]
    if sc:
        lines.append("Findings by Severity:")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if sev in sc:
                lines.append(f"  {sev}: {sc[sev]}")
        lines.append("")

    if result["config_files_changed"]:
        lines.append("Config Files Modified:")
        for cf in result["config_files_changed"]:
            lines.append(f"  - {cf}")
        lines.append("")

    if result["large_files"]:
        lines.append("Large File Changes (>{} lines):".format(LARGE_FILE_THRESHOLD))
        for lf in result["large_files"]:
            lines.append(f"  - {lf['path']} (+{lf['additions']}/-{lf['deletions']})")
        lines.append("")

    findings = result["findings"]
    if findings:
        lines.append("-" * 60)
        lines.append("FINDINGS")
        lines.append("-" * 60)
        for i, f in enumerate(findings, 1):
            lines.append("")
            lines.append(f"[{f['severity']}] #{i}: {f['description']}")
            lines.append(f"  Type: {f['type']}")
            lines.append(f"  File: {f['file']}")
            if "line_number" in f:
                lines.append(f"  Line: {f['line_number']}")
            if "content" in f:
                lines.append(f"  Code: {f['content']}")
    else:
        lines.append("No risk indicators found.")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze git diff output for risk indicators (large files, "
                    "sensitive paths, config changes, breaking patterns, security red flags).",
        epilog="Example: git diff main...HEAD | python diff_analyzer.py",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to a diff file. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON.",
    )
    parser.add_argument(
        "--large-file-threshold",
        type=int,
        default=LARGE_FILE_THRESHOLD,
        help=f"Lines changed to flag a file as large (default: {LARGE_FILE_THRESHOLD}).",
    )
    parser.add_argument(
        "--large-pr-threshold",
        type=int,
        default=LARGE_PR_THRESHOLD,
        help=f"Total lines changed to flag PR as large (default: {LARGE_PR_THRESHOLD}).",
    )
    args = parser.parse_args()

    file_threshold = args.large_file_threshold
    pr_threshold = args.large_pr_threshold

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
                diff_text = fh.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Reading diff from stdin (pipe a diff or use --file)...", file=sys.stderr)
        diff_text = sys.stdin.read()

    if not diff_text.strip():
        print("Error: Empty diff input.", file=sys.stderr)
        sys.exit(1)

    result = analyze_diff(diff_text, file_threshold, pr_threshold)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
