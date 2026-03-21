#!/usr/bin/env python3
"""Lint GitHub Actions and GitLab CI YAML files for common CI/CD issues.

Checks for missing permissions, hardcoded secrets, missing timeouts,
unpinned actions, missing concurrency controls, and more.

Usage:
    python pipeline_linter.py .github/workflows/ci.yml
    python pipeline_linter.py .gitlab-ci.yml --json
    python pipeline_linter.py --dir .github/workflows/
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"


def _lines_containing(text, pattern):
    """Return list of (line_number, line_text) tuples matching *pattern*."""
    results = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if re.search(pattern, line):
            results.append((idx, line.strip()))
    return results


def check_hardcoded_secrets(text, _platform):
    """Detect potential hardcoded secrets or tokens in the YAML."""
    findings = []
    patterns = [
        (r'(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*["\']?[A-Za-z0-9+/=]{16,}',
         "Possible hardcoded secret value"),
        (r'(?i)(ghp_|gho_|github_pat_|sk-|AKIA)[A-Za-z0-9]{10,}',
         "Possible hardcoded API token"),
        (r'(?i)BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE\s+KEY',
         "Private key embedded in pipeline file"),
    ]
    for pat, msg in patterns:
        for lineno, line in _lines_containing(text, pat):
            findings.append({
                "rule": "no-hardcoded-secrets",
                "severity": SEVERITY_ERROR,
                "line": lineno,
                "message": f"{msg}: {line[:80]}",
            })
    return findings


def check_unpinned_actions(text, platform):
    """Warn when GitHub Actions use @main or @master instead of a pinned SHA/tag."""
    if platform != "github-actions":
        return []
    findings = []
    pat = r'uses:\s+([^@\s]+)@(main|master)\s*$'
    for lineno, line in _lines_containing(text, pat):
        findings.append({
            "rule": "pin-action-versions",
            "severity": SEVERITY_WARNING,
            "line": lineno,
            "message": f"Action pinned to mutable branch: {line}",
        })
    return findings


def check_missing_timeout(text, platform):
    """Flag jobs that lack a timeout setting."""
    findings = []
    if platform == "github-actions":
        # Heuristic: look for 'runs-on' (marks a job) without a nearby timeout-minutes
        in_job = False
        job_name = ""
        job_line = 0
        has_timeout = False
        for idx, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if re.match(r'^[a-zA-Z0-9_-]+:\s*$', stripped) or re.match(r'^[a-zA-Z0-9_-]+:$', stripped):
                if in_job and not has_timeout:
                    findings.append({
                        "rule": "require-timeout",
                        "severity": SEVERITY_WARNING,
                        "line": job_line,
                        "message": f"Job '{job_name}' has no timeout-minutes (default is 6 hours)",
                    })
                in_job = False
                has_timeout = False
            if "runs-on:" in stripped:
                in_job = True
                job_name = stripped
                job_line = idx
            if "timeout-minutes:" in stripped:
                has_timeout = True
        if in_job and not has_timeout:
            findings.append({
                "rule": "require-timeout",
                "severity": SEVERITY_WARNING,
                "line": job_line,
                "message": f"Job '{job_name}' has no timeout-minutes (default is 6 hours)",
            })
    elif platform == "gitlab-ci":
        if "timeout:" not in text:
            findings.append({
                "rule": "require-timeout",
                "severity": SEVERITY_INFO,
                "line": 1,
                "message": "No global or per-job timeout set (GitLab default is 1 hour)",
            })
    return findings


def check_missing_concurrency(text, platform):
    """Flag GitHub Actions workflows missing a concurrency group."""
    if platform != "github-actions":
        return []
    if "concurrency:" not in text:
        return [{
            "rule": "require-concurrency",
            "severity": SEVERITY_WARNING,
            "line": 1,
            "message": "Workflow has no concurrency group; duplicate runs can waste resources",
        }]
    return []


def check_missing_permissions(text, platform):
    """Flag GitHub Actions workflows without explicit permissions."""
    if platform != "github-actions":
        return []
    if "permissions:" not in text:
        return [{
            "rule": "require-permissions",
            "severity": SEVERITY_WARNING,
            "line": 1,
            "message": "No explicit permissions block; workflow runs with default (often broad) token scope",
        }]
    return []


def check_missing_path_filters(text, platform):
    """Info-level hint when pushes trigger on all paths."""
    if platform != "github-actions":
        return []
    if re.search(r'on:\s*\n\s+push:', text) and "paths" not in text:
        return [{
            "rule": "suggest-path-filters",
            "severity": SEVERITY_INFO,
            "line": 1,
            "message": "No path filters; documentation-only changes will trigger full CI",
        }]
    return []


def check_artifact_retention(text, platform):
    """Warn when upload-artifact has no retention-days."""
    findings = []
    if platform == "github-actions":
        in_upload = False
        upload_line = 0
        has_retention = False
        for idx, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if "actions/upload-artifact" in stripped:
                if in_upload and not has_retention:
                    findings.append({
                        "rule": "set-artifact-retention",
                        "severity": SEVERITY_WARNING,
                        "line": upload_line,
                        "message": "upload-artifact without retention-days; artifacts kept for 90 days by default",
                    })
                in_upload = True
                upload_line = idx
                has_retention = False
            if in_upload and "retention-days:" in stripped:
                has_retention = True
            if in_upload and stripped.startswith("- ") and "upload-artifact" not in stripped:
                if not has_retention:
                    findings.append({
                        "rule": "set-artifact-retention",
                        "severity": SEVERITY_WARNING,
                        "line": upload_line,
                        "message": "upload-artifact without retention-days; artifacts kept for 90 days by default",
                    })
                in_upload = False
                has_retention = False
    elif platform == "gitlab-ci":
        if "artifacts:" in text and "expire_in:" not in text:
            findings.append({
                "rule": "set-artifact-retention",
                "severity": SEVERITY_WARNING,
                "line": 1,
                "message": "Artifacts defined without expire_in; storage costs grow indefinitely",
            })
    return findings


def check_deploy_without_gate(text, platform):
    """Flag deploy jobs that lack environment protection or branch guards."""
    findings = []
    if platform == "github-actions":
        for idx, line in enumerate(text.splitlines(), start=1):
            if re.search(r'deploy.*production', line, re.IGNORECASE):
                # Check next ~15 lines for environment or if guard
                block = "\n".join(text.splitlines()[idx:idx + 15])
                if "environment:" not in block and 'if:' not in block:
                    findings.append({
                        "rule": "gate-production-deploy",
                        "severity": SEVERITY_ERROR,
                        "line": idx,
                        "message": "Production deploy job lacks environment gate or branch condition",
                    })
    elif platform == "gitlab-ci":
        for idx, line in enumerate(text.splitlines(), start=1):
            if re.search(r'deploy.*production', line, re.IGNORECASE):
                block = "\n".join(text.splitlines()[idx:idx + 15])
                if "when: manual" not in block and "rules:" not in block:
                    findings.append({
                        "rule": "gate-production-deploy",
                        "severity": SEVERITY_ERROR,
                        "line": idx,
                        "message": "Production deploy job lacks manual gate or rules guard",
                    })
    return findings


# ---------------------------------------------------------------------------
# Platform detection & orchestration
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    check_hardcoded_secrets,
    check_unpinned_actions,
    check_missing_timeout,
    check_missing_concurrency,
    check_missing_permissions,
    check_missing_path_filters,
    check_artifact_retention,
    check_deploy_without_gate,
]


def detect_platform(filepath, text):
    """Determine CI platform from path and content."""
    name = os.path.basename(filepath)
    parent = os.path.basename(os.path.dirname(filepath))
    if parent == "workflows" or ".github" in filepath:
        return "github-actions"
    if name == ".gitlab-ci.yml" or "stages:" in text:
        return "gitlab-ci"
    # Fallback heuristic
    if "runs-on:" in text:
        return "github-actions"
    if "image:" in text and "script:" in text:
        return "gitlab-ci"
    return "unknown"


def lint_file(filepath):
    """Run all checks on a single file. Returns dict with findings."""
    filepath = str(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "file": filepath,
            "platform": "unknown",
            "findings": [{
                "rule": "file-read-error",
                "severity": SEVERITY_ERROR,
                "line": 0,
                "message": str(exc),
            }],
        }

    platform = detect_platform(filepath, text)
    findings = []
    for check_fn in ALL_CHECKS:
        findings.extend(check_fn(text, platform))

    findings.sort(key=lambda f: (f["line"], f["severity"]))
    return {"file": filepath, "platform": platform, "findings": findings}


def collect_files(path):
    """Collect YAML files from a file path or directory."""
    p = Path(path)
    if p.is_file():
        return [p]
    if p.is_dir():
        yamls = sorted(p.glob("**/*.yml")) + sorted(p.glob("**/*.yaml"))
        return yamls
    return []


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

_SEVERITY_SYMBOL = {
    SEVERITY_ERROR: "E",
    SEVERITY_WARNING: "W",
    SEVERITY_INFO: "I",
}


def format_human(results):
    """Return human-readable report string."""
    lines = []
    total_errors = 0
    total_warnings = 0
    for result in results:
        lines.append(f"\n--- {result['file']} (platform: {result['platform']}) ---")
        if not result["findings"]:
            lines.append("  No issues found.")
            continue
        for f in result["findings"]:
            sym = _SEVERITY_SYMBOL.get(f["severity"], "?")
            lines.append(f"  [{sym}] L{f['line']:>4d}  {f['rule']}: {f['message']}")
            if f["severity"] == SEVERITY_ERROR:
                total_errors += 1
            elif f["severity"] == SEVERITY_WARNING:
                total_warnings += 1
    lines.append(f"\nSummary: {total_errors} error(s), {total_warnings} warning(s)")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Lint CI/CD pipeline YAML files for common issues.",
        epilog="Examples:\n"
               "  %(prog)s .github/workflows/ci.yml\n"
               "  %(prog)s --dir .github/workflows/ --json\n"
               "  %(prog)s .gitlab-ci.yml --severity warning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="*", help="Pipeline YAML files to lint")
    parser.add_argument("--dir", help="Directory to scan recursively for YAML files")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    parser.add_argument("--severity", choices=["error", "warning", "info"],
                        default="info",
                        help="Minimum severity to report (default: info)")
    args = parser.parse_args()

    files_to_lint = []
    for f in (args.files or []):
        files_to_lint.extend(collect_files(f))
    if args.dir:
        files_to_lint.extend(collect_files(args.dir))

    if not files_to_lint:
        parser.error("No files provided. Pass YAML files or use --dir.")

    severity_rank = {"error": 3, "warning": 2, "info": 1}
    min_rank = severity_rank[args.severity]

    results = []
    for fpath in files_to_lint:
        result = lint_file(fpath)
        result["findings"] = [
            f for f in result["findings"]
            if severity_rank.get(f["severity"], 0) >= min_rank
        ]
        results.append(result)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    has_errors = any(
        f["severity"] == SEVERITY_ERROR
        for r in results for f in r["findings"]
    )
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
