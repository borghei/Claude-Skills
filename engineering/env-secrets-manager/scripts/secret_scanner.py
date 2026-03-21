#!/usr/bin/env python3
"""Scan a codebase for hardcoded secrets using pattern matching.

Detects API keys, tokens, passwords, private keys, and other credentials
embedded directly in source files. Uses regex patterns against known secret
formats (AWS, Stripe, GitHub, Slack, etc.) plus generic heuristics for
password assignments and high-entropy strings.

Usage:
    python secret_scanner.py /path/to/project
    python secret_scanner.py . --include "*.py" "*.ts" --json
    python secret_scanner.py src/ --severity high --exclude node_modules .git
"""

import argparse
import fnmatch
import json
import math
import os
import re
import sys
from pathlib import Path

# ── Secret Patterns ──────────────────────────────────────────────────────────
# Each tuple: (compiled_regex, description, severity)
SECRET_PATTERNS = [
    # Cloud Provider Keys
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key ID", "high"),
    (re.compile(r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"),
     "Possible AWS Secret Access Key (40-char base64)", "low"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "Google API Key", "high"),

    # Payment
    (re.compile(r"sk_(live|test)_[0-9a-zA-Z]{24,}"), "Stripe Secret Key", "high"),
    (re.compile(r"rk_(live|test)_[0-9a-zA-Z]{24,}"), "Stripe Restricted Key", "high"),
    (re.compile(r"whsec_[0-9a-zA-Z]{32,}"), "Stripe Webhook Secret", "high"),

    # Version Control
    (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "GitHub Personal Access Token", "high"),
    (re.compile(r"gho_[0-9a-zA-Z]{36}"), "GitHub OAuth Token", "high"),
    (re.compile(r"ghs_[0-9a-zA-Z]{36}"), "GitHub App Token", "high"),
    (re.compile(r"github_pat_[0-9a-zA-Z_]{82}"), "GitHub Fine-Grained PAT", "high"),
    (re.compile(r"glpat-[0-9a-zA-Z\-]{20,}"), "GitLab Personal Access Token", "high"),

    # Communication
    (re.compile(r"xox[bpras]-[0-9a-zA-Z\-]{10,}"), "Slack Token", "high"),
    (re.compile(r"https://hooks\.slack\.com/services/T[0-9A-Z]+/B[0-9A-Z]+/[0-9a-zA-Z]+"),
     "Slack Webhook URL", "high"),

    # Email / SaaS
    (re.compile(r"SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}"), "SendGrid API Key", "high"),
    (re.compile(r"key-[0-9a-zA-Z]{32}"), "Mailgun API Key", "medium"),

    # Private Keys
    (re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
     "Private Key", "high"),

    # JWT / Bearer Tokens (long ones are suspicious)
    (re.compile(r"eyJ[A-Za-z0-9\-_]{20,}\.eyJ[A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_.+/=]{20,}"),
     "JSON Web Token", "medium"),

    # Generic password assignments
    (re.compile(r"""(?:password|passwd|pwd|secret|token|api_key|apikey|auth)\s*[:=]\s*['"][^'"]{8,}['"]""",
                re.IGNORECASE),
     "Hardcoded password/secret assignment", "medium"),

    # Connection strings with embedded credentials
    (re.compile(r"(?:mysql|postgres|postgresql|mongodb|redis|amqp)://[^:]+:[^@]+@[^\s'\"]+"),
     "Connection string with embedded credentials", "high"),
]

# ── File Filters ─────────────────────────────────────────────────────────────
DEFAULT_EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".tox",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".next", ".nuxt",
    "vendor", "target", ".gradle", ".idea", ".vscode",
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2",
    ".ttf", ".eot", ".mp3", ".mp4", ".zip", ".tar", ".gz", ".bz2",
    ".pdf", ".exe", ".dll", ".so", ".dylib", ".class", ".jar", ".pyc",
    ".wasm", ".o", ".a", ".lib",
}

# Files that commonly contain example/test secrets (lower severity)
EXAMPLE_FILE_PATTERNS = {"*.example", "*.sample", "*.template", "*.test.*", "*.spec.*"}

MAX_FILE_SIZE = 1_000_000  # 1 MB — skip large files
MAX_LINE_LENGTH = 2000      # skip extremely long lines (minified JS, etc.)


def shannon_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def is_binary_file(filepath: Path) -> bool:
    """Quick heuristic check for binary files."""
    if filepath.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(512)
            return b"\x00" in chunk
    except (OSError, PermissionError):
        return True


def should_skip_dir(dirname: str, exclude_dirs: set) -> bool:
    """Check if directory should be skipped."""
    return dirname in exclude_dirs or dirname.startswith(".")


def is_example_file(filepath: Path) -> bool:
    """Check if file is an example/template (lower severity)."""
    name = filepath.name
    return any(fnmatch.fnmatch(name, pat) for pat in EXAMPLE_FILE_PATTERNS)


def scan_file(filepath: Path, severity_filter: str | None = None) -> list[dict]:
    """Scan a single file for secrets. Returns list of findings."""
    findings = []
    severity_rank = {"low": 0, "medium": 1, "high": 2}
    min_rank = severity_rank.get(severity_filter, 0) if severity_filter else 0

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                if len(line) > MAX_LINE_LENGTH:
                    continue
                stripped = line.strip()
                # Skip comments
                if stripped.startswith(("#", "//", "/*", "*", "<!--")):
                    continue

                for pattern, description, severity in SECRET_PATTERNS:
                    if severity_rank.get(severity, 0) < min_rank:
                        continue
                    match = pattern.search(line)
                    if match:
                        matched_text = match.group(0)
                        # Truncate display of the matched secret
                        if len(matched_text) > 16:
                            display = matched_text[:8] + "..." + matched_text[-4:]
                        else:
                            display = matched_text[:4] + "****"

                        findings.append({
                            "file": str(filepath),
                            "line": line_num,
                            "severity": severity,
                            "type": description,
                            "match_preview": display,
                            "in_example_file": is_example_file(filepath),
                        })
    except (OSError, PermissionError, UnicodeDecodeError):
        pass

    return findings


def scan_directory(
    root: str,
    include_patterns: list[str] | None = None,
    exclude_dirs: set | None = None,
    severity_filter: str | None = None,
) -> list[dict]:
    """Walk a directory tree and scan all eligible files."""
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS

    all_findings = []
    root_path = Path(root).resolve()

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d, exclude_dirs)]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            # Skip binary and oversized files
            if is_binary_file(filepath):
                continue
            try:
                if filepath.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            # Apply include filter
            if include_patterns:
                if not any(fnmatch.fnmatch(filename, p) for p in include_patterns):
                    continue

            findings = scan_file(filepath, severity_filter)
            all_findings.extend(findings)

    return all_findings


def print_human(findings: list[dict], root: str) -> None:
    """Pretty-print scan results."""
    print(f"Secret Scanner: {root}")
    print(f"  Total findings: {len(findings)}")

    if not findings:
        print("  No hardcoded secrets detected.")
        return

    high = [f for f in findings if f["severity"] == "high"]
    medium = [f for f in findings if f["severity"] == "medium"]
    low = [f for f in findings if f["severity"] == "low"]

    print(f"  High: {len(high)}  Medium: {len(medium)}  Low: {len(low)}")
    print()

    severity_order = {"high": 0, "medium": 1, "low": 2}
    sorted_findings = sorted(findings, key=lambda f: (severity_order.get(f["severity"], 3), f["file"], f["line"]))

    # Group by file
    current_file = None
    for finding in sorted_findings:
        if finding["file"] != current_file:
            current_file = finding["file"]
            # Show relative path if possible
            try:
                display_path = str(Path(current_file).relative_to(Path(root).resolve()))
            except ValueError:
                display_path = current_file
            print(f"  {display_path}:")

        sev = finding["severity"].upper()
        line = finding["line"]
        desc = finding["type"]
        preview = finding["match_preview"]
        example_tag = " [example file]" if finding["in_example_file"] else ""
        print(f"    L{line:<5} [{sev:<6}] {desc}: {preview}{example_tag}")

    print()
    if high:
        print("  ACTION REQUIRED: High-severity findings should be rotated immediately.")
        print("  Remove secrets from source, use environment variables or a secret manager.")


def build_summary(findings: list[dict], root: str) -> dict:
    """Build a JSON-friendly summary."""
    high = [f for f in findings if f["severity"] == "high"]
    medium = [f for f in findings if f["severity"] == "medium"]
    low = [f for f in findings if f["severity"] == "low"]
    unique_files = len(set(f["file"] for f in findings))

    return {
        "scan_root": str(Path(root).resolve()),
        "total_findings": len(findings),
        "high_count": len(high),
        "medium_count": len(medium),
        "low_count": len(low),
        "files_affected": unique_files,
        "passed": len(high) == 0,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan a codebase for hardcoded secrets (API keys, tokens, passwords, "
                    "private keys) using pattern matching. No external dependencies required.",
        epilog="Examples:\n"
               "  %(prog)s /path/to/project\n"
               "  %(prog)s . --include '*.py' '*.ts' --json\n"
               "  %(prog)s src/ --severity high --exclude node_modules .git dist\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="Directory or file to scan")
    parser.add_argument("--include", nargs="+", metavar="PATTERN",
                        help="Only scan files matching these glob patterns (e.g., '*.py' '*.js')")
    parser.add_argument("--exclude", nargs="+", metavar="DIR",
                        help="Directory names to exclude (added to defaults)")
    parser.add_argument("--severity", choices=["low", "medium", "high"],
                        help="Minimum severity to report")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")

    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        return 2

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    if args.exclude:
        exclude_dirs.update(args.exclude)

    if target.is_file():
        findings = scan_file(target, args.severity)
    else:
        findings = scan_directory(str(target), args.include, exclude_dirs, args.severity)

    if args.json_output:
        summary = build_summary(findings, args.path)
        print(json.dumps(summary, indent=2))
    else:
        print_human(findings, args.path)

    # Exit 1 if high-severity findings exist
    has_high = any(f["severity"] == "high" for f in findings)
    return 1 if has_high else 0


if __name__ == "__main__":
    sys.exit(main())
