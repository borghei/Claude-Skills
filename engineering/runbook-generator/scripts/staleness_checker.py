#!/usr/bin/env python3
"""Staleness Checker — Check runbook freshness against configurable thresholds.

Inspects runbook markdown files for their "Last verified" date and compares
it against configurable staleness thresholds. Also checks whether referenced
config files have been modified more recently than the runbook verification
date. Designed for CI integration to catch stale runbooks before they cause
incident response failures.

Usage:
    python staleness_checker.py docs/runbooks/
    python staleness_checker.py runbook.md --threshold 30
    python staleness_checker.py docs/runbooks/ --repo-root /path/to/repo
    python staleness_checker.py docs/runbooks/ --json
    python staleness_checker.py docs/runbooks/ --config staleness.json
"""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import date, datetime, timedelta
from pathlib import Path


DEFAULT_THRESHOLDS = {
    "stale_days": 90,
    "warning_days": 60,
    "critical_days": 180,
}

CONFIG_FILE_PATTERN = re.compile(
    r"git\s+log\s+.*?--\s+(\S+)|"
    r"(?:config|file|path)[:=]\s*[`\"]?([a-zA-Z0-9_./-]+\.[a-zA-Z]+)[`\"]?"
)

LAST_VERIFIED_PATTERN = re.compile(
    r"(?i)(?:\*\*)?last\s+verified(?:\*\*)?[:]\s*(\d{4}-\d{2}-\d{2})"
)

LAST_UPDATED_PATTERN = re.compile(
    r"(?i)(?:\*\*)?(?:last\s+updated|updated|date)(?:\*\*)?[:]\s*(\d{4}-\d{2}-\d{2})"
)


def parse_date(date_str):
    """Parse a YYYY-MM-DD date string."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def extract_verified_date(content):
    """Extract the 'Last verified' or 'Last updated' date from runbook content."""
    match = LAST_VERIFIED_PATTERN.search(content)
    if match:
        return parse_date(match.group(1))
    match = LAST_UPDATED_PATTERN.search(content)
    if match:
        return parse_date(match.group(1))
    return None


def extract_referenced_configs(content):
    """Extract config file paths referenced in the runbook."""
    configs = set()
    for match in CONFIG_FILE_PATTERN.finditer(content):
        path = match.group(1) or match.group(2)
        if path:
            path = path.strip("`\"'")
            # Filter out obvious non-file-paths
            if "." in path and not path.startswith("http") and len(path) < 200:
                configs.add(path)
    return sorted(configs)


def get_file_modified_date(filepath):
    """Get the last modification date of a file from the filesystem."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime).date()
    except (OSError, FileNotFoundError):
        return None


def get_git_modified_date(filepath, repo_root=None):
    """Get the last modification date of a file from git history."""
    try:
        cwd = repo_root if repo_root else os.path.dirname(filepath) or "."
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", filepath],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip().split(" ")[0]
            return parse_date(date_str)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def classify_staleness(days_since, thresholds):
    """Classify the staleness level based on days since last verification."""
    if days_since >= thresholds["critical_days"]:
        return "critical"
    if days_since >= thresholds["stale_days"]:
        return "stale"
    if days_since >= thresholds["warning_days"]:
        return "warning"
    return "fresh"


def check_config_drift(content, repo_root, verified_date):
    """Check if any referenced config files were modified after verification."""
    drifted = []
    configs = extract_referenced_configs(content)

    for config_path in configs:
        full_path = os.path.join(repo_root, config_path) if repo_root else config_path

        mod_date = get_git_modified_date(config_path, repo_root)
        if mod_date is None:
            mod_date = get_file_modified_date(full_path)

        if mod_date is None:
            continue

        if verified_date and mod_date > verified_date:
            drifted.append({
                "config_file": config_path,
                "modified_date": mod_date.isoformat(),
                "verified_date": verified_date.isoformat(),
                "drift_days": (mod_date - verified_date).days,
            })

    return drifted


def check_runbook_staleness(filepath, thresholds, repo_root=None, today=None):
    """Check staleness of a single runbook file."""
    if today is None:
        today = date.today()

    filepath = str(filepath)
    result = {
        "file": filepath,
        "verified_date": None,
        "days_since_verified": None,
        "status": "unknown",
        "config_drift": [],
        "issues": [],
    }

    try:
        with open(filepath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        result["status"] = "error"
        result["issues"].append(f"File not found: {filepath}")
        return result

    if not content.strip():
        result["status"] = "error"
        result["issues"].append("Runbook file is empty")
        return result

    verified_date = extract_verified_date(content)

    if verified_date is None:
        result["status"] = "unknown"
        result["issues"].append(
            "No 'Last verified' or 'Last updated' date found. "
            "Add '**Last verified:** YYYY-MM-DD' to the runbook header."
        )
        # Fall back to git modification date of the runbook itself
        git_date = get_git_modified_date(filepath, repo_root)
        fs_date = get_file_modified_date(filepath)
        fallback = git_date or fs_date
        if fallback:
            verified_date = fallback
            result["issues"].append(
                f"Using file modification date as fallback: {fallback.isoformat()}"
            )

    if verified_date:
        result["verified_date"] = verified_date.isoformat()
        days = (today - verified_date).days
        result["days_since_verified"] = days
        result["status"] = classify_staleness(days, thresholds)

        if result["status"] in ("stale", "critical"):
            result["issues"].append(
                f"Runbook was last verified {days} days ago ({verified_date.isoformat()}). "
                f"Threshold: {thresholds['stale_days']} days."
            )

    # Check config drift
    effective_root = repo_root or os.path.dirname(os.path.abspath(filepath))
    drift = check_config_drift(content, effective_root, verified_date)
    result["config_drift"] = drift
    for d in drift:
        result["issues"].append(
            f"Config drift: {d['config_file']} was modified {d['drift_days']} days "
            f"after the runbook was last verified (modified: {d['modified_date']}, "
            f"verified: {d['verified_date']})"
        )
        if result["status"] == "fresh":
            result["status"] = "drift"

    return result


def load_config(config_path):
    """Load threshold configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
        thresholds = dict(DEFAULT_THRESHOLDS)
        for key in DEFAULT_THRESHOLDS:
            if key in data:
                thresholds[key] = int(data[key])
        return thresholds
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(2)


def format_human_output(results, thresholds):
    """Format staleness results for human consumption."""
    lines = []
    lines.append(f"Staleness Checker Report — {date.today().isoformat()}")
    lines.append(f"Thresholds: warning={thresholds['warning_days']}d, "
                 f"stale={thresholds['stale_days']}d, "
                 f"critical={thresholds['critical_days']}d")
    lines.append("")

    status_counts = {"fresh": 0, "warning": 0, "stale": 0, "critical": 0,
                     "drift": 0, "unknown": 0, "error": 0}

    for result in results:
        status = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

        icon_map = {
            "fresh": "OK   ",
            "warning": "WARN ",
            "stale": "STALE",
            "critical": "CRIT ",
            "drift": "DRIFT",
            "unknown": "?????",
            "error": "ERROR",
        }
        icon = icon_map.get(status, "?????")
        lines.append(f"  [{icon}] {result['file']}")

        if result["verified_date"]:
            days = result["days_since_verified"]
            lines.append(f"         Last verified: {result['verified_date']} ({days} days ago)")

        for issue in result["issues"]:
            lines.append(f"         - {issue}")

        if result["config_drift"]:
            lines.append(f"         Config drift detected in {len(result['config_drift'])} file(s)")

        lines.append("")

    lines.append("=" * 60)
    lines.append("SUMMARY")
    lines.append(f"  Files checked: {len(results)}")
    for status, count in sorted(status_counts.items()):
        if count > 0:
            lines.append(f"  {status.upper():>10}: {count}")
    lines.append("=" * 60)

    stale_count = status_counts["stale"] + status_counts["critical"]
    if stale_count > 0:
        lines.append(f"\n{stale_count} runbook(s) need review.")
    elif status_counts["drift"] > 0:
        lines.append(f"\n{status_counts['drift']} runbook(s) have config drift.")
    else:
        lines.append("\nAll runbooks are up to date.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check runbook freshness against configurable staleness thresholds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Status levels:
              fresh    — verified within the warning threshold
              warning  — approaching staleness (default: 60+ days)
              stale    — exceeds staleness threshold (default: 90+ days)
              critical — severely stale (default: 180+ days)
              drift    — referenced config files changed after verification
              unknown  — no verification date found in runbook
              error    — file not found or empty

            Config file format (JSON):
              {
                "warning_days": 60,
                "stale_days": 90,
                "critical_days": 180
              }

            Exit codes:
              0 = all runbooks fresh or warning-level
              1 = one or more stale or critical runbooks
              2 = input error
        """),
    )
    parser.add_argument("paths", nargs="*", help="Runbook files or directories to check")
    parser.add_argument("--threshold", "-t", type=int, default=None,
                        help=f"Staleness threshold in days (default: {DEFAULT_THRESHOLDS['stale_days']})")
    parser.add_argument("--warning", "-w", type=int, default=None,
                        help=f"Warning threshold in days (default: {DEFAULT_THRESHOLDS['warning_days']})")
    parser.add_argument("--critical", type=int, default=None,
                        help=f"Critical threshold in days (default: {DEFAULT_THRESHOLDS['critical_days']})")
    parser.add_argument("--config", "-c", help="Path to JSON config file with thresholds")
    parser.add_argument("--repo-root", "-r", help="Repository root for resolving config file paths")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not args.paths:
        parser.print_help()
        print("\nError: No paths specified.", file=sys.stderr)
        sys.exit(2)

    # Build thresholds
    if args.config:
        thresholds = load_config(args.config)
    else:
        thresholds = dict(DEFAULT_THRESHOLDS)

    if args.threshold is not None:
        thresholds["stale_days"] = args.threshold
    if args.warning is not None:
        thresholds["warning_days"] = args.warning
    if args.critical is not None:
        thresholds["critical_days"] = args.critical

    # Collect files
    files = []
    for path_str in args.paths:
        p = Path(path_str)
        if p.is_dir():
            files.extend(sorted(p.glob("**/*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Warning: Path not found — {path_str}", file=sys.stderr)

    if not files:
        print("Error: No markdown files found.", file=sys.stderr)
        sys.exit(2)

    # Check each file
    results = [
        check_runbook_staleness(f, thresholds, repo_root=args.repo_root)
        for f in files
    ]

    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human_output(results, thresholds))

    # Exit code
    has_stale = any(r["status"] in ("stale", "critical") for r in results)
    sys.exit(1 if has_stale else 0)


if __name__ == "__main__":
    main()
