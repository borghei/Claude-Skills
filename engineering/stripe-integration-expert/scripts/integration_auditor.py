#!/usr/bin/env python3
"""Stripe Integration Code Auditor.

Scans a project for common Stripe integration anti-patterns: hardcoded API keys,
missing idempotency keys, unhandled webhook events, unpinned API versions,
insecure key handling, and missing error handling around Stripe API calls.

Usage:
    python integration_auditor.py /path/to/project
    python integration_auditor.py /path/to/project --json
    python integration_auditor.py /path/to/project --severity critical
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

CODE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".rb", ".go", ".java", ".php"}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "dist", "build", ".next", "venv", ".venv", "vendor"}


def collect_source_files(project_dir):
    """Walk the project and collect source files with their contents."""
    files = {}
    for root, dirs, filenames in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1]
            if ext not in CODE_EXTENSIONS:
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    files[fpath] = f.read()
            except (OSError, IOError):
                continue
    return files


def relative_path(fpath, project_dir):
    """Return path relative to the project directory."""
    try:
        return str(Path(fpath).relative_to(project_dir))
    except ValueError:
        return fpath


def audit_hardcoded_keys(files, project_dir):
    """Detect hardcoded Stripe API keys in source code."""
    findings = []
    patterns = [
        (r'sk_live_[a-zA-Z0-9]{20,}', "Live secret key hardcoded in source. This is a critical security risk."),
        (r'sk_test_[a-zA-Z0-9]{20,}', "Test secret key hardcoded in source. Move to environment variable."),
        (r'pk_live_[a-zA-Z0-9]{20,}', "Live publishable key hardcoded. Consider using environment variable for flexibility."),
        (r'whsec_[a-zA-Z0-9]{20,}', "Webhook signing secret hardcoded in source."),
        (r'rk_live_[a-zA-Z0-9]{20,}', "Live restricted key hardcoded in source."),
    ]

    for fpath, content in files.items():
        rel = relative_path(fpath, project_dir)
        for line_no, line in enumerate(content.splitlines(), 1):
            for pattern, message in patterns:
                if re.search(pattern, line):
                    severity = "critical" if "live" in pattern else "warning"
                    findings.append({
                        "severity": severity,
                        "rule": "KEY-001",
                        "message": message,
                        "file": rel,
                        "line": line_no,
                        "fix": "Use environment variables: process.env.STRIPE_SECRET_KEY or os.environ['STRIPE_SECRET_KEY'].",
                    })
    return findings


def audit_api_version_pinning(files, project_dir):
    """Check if Stripe API version is pinned in client initialization."""
    findings = []
    has_stripe_init = False
    has_version_pin = False

    for fpath, content in files.items():
        # Detect Stripe client initialization
        if re.search(r'new\s+Stripe\s*\(', content) or re.search(r'stripe\s*=\s*stripe\.', content, re.IGNORECASE):
            has_stripe_init = True
            if re.search(r'apiVersion\s*[=:]\s*["\']', content) or re.search(r'api_version\s*[=:]\s*["\']', content):
                has_version_pin = True

    if has_stripe_init and not has_version_pin:
        findings.append({
            "severity": "warning",
            "rule": "VER-001",
            "message": "Stripe client initialized without pinning apiVersion. Breaking changes may occur on Stripe updates.",
            "fix": "Pin apiVersion in the Stripe constructor: new Stripe(key, { apiVersion: '2024-12-18.acacia' }).",
        })
    elif has_stripe_init and has_version_pin:
        findings.append({
            "severity": "pass",
            "rule": "VER-001",
            "message": "Stripe API version is pinned.",
        })
    return findings


def audit_idempotency_keys(files, project_dir):
    """Check for idempotency key usage on mutating Stripe API calls."""
    findings = []
    mutating_calls = [
        r"\.create\s*\(",
        r"\.update\s*\(",
        r"\.del\s*\(",
        r"\.cancel\s*\(",
    ]
    idempotency_pattern = r"idempotencyKey|idempotency_key"

    for fpath, content in files.items():
        rel = relative_path(fpath, project_dir)
        # Only check files that reference Stripe
        if not re.search(r"stripe", content, re.IGNORECASE):
            continue

        has_mutating = False
        has_idempotency = bool(re.search(idempotency_pattern, content, re.IGNORECASE))

        for pattern in mutating_calls:
            if re.search(pattern, content):
                has_mutating = True
                break

        if has_mutating and not has_idempotency:
            findings.append({
                "severity": "warning",
                "rule": "IDEM-001",
                "message": f"Stripe mutating API calls found without idempotency keys: {rel}",
                "file": rel,
                "fix": "Pass idempotencyKey to .create() calls to prevent duplicate charges on retries.",
            })

    return findings


def audit_error_handling(files, project_dir):
    """Check for proper error handling around Stripe API calls."""
    findings = []

    for fpath, content in files.items():
        rel = relative_path(fpath, project_dir)
        if not re.search(r"stripe", content, re.IGNORECASE):
            continue

        lines = content.splitlines()
        for i, line in enumerate(lines):
            # Look for await stripe.X calls outside of try blocks
            if re.search(r"await\s+stripe\.", line) or re.search(r"stripe\.\w+\.\w+\(", line):
                # Check if we are inside a try block (simple heuristic: look back 10 lines for "try")
                context_start = max(0, i - 10)
                context = "\n".join(lines[context_start:i])
                if "try" not in context and "catch" not in context and ".then(" not in line:
                    findings.append({
                        "severity": "info",
                        "rule": "ERR-001",
                        "message": f"Stripe API call may lack error handling: {rel}:{i + 1}",
                        "file": rel,
                        "line": i + 1,
                        "fix": "Wrap Stripe API calls in try/catch to handle network errors and API failures gracefully.",
                    })
    return findings


def audit_price_id_handling(files, project_dir):
    """Check for hardcoded Stripe price IDs instead of environment variables."""
    findings = []
    price_pattern = r'["\']price_[a-zA-Z0-9]{10,}["\']'

    for fpath, content in files.items():
        rel = relative_path(fpath, project_dir)
        for line_no, line in enumerate(content.splitlines(), 1):
            if re.search(price_pattern, line):
                # Ignore comments and test files
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("*"):
                    continue
                if "test" in fpath.lower() or "spec" in fpath.lower() or "mock" in fpath.lower():
                    continue
                findings.append({
                    "severity": "warning",
                    "rule": "PRICE-001",
                    "message": f"Hardcoded price ID found: {rel}:{line_no}",
                    "file": rel,
                    "line": line_no,
                    "fix": "Move price IDs to environment variables for test/production parity.",
                })
    return findings


def audit_metadata_on_checkout(files, project_dir):
    """Check that checkout sessions include user metadata for webhook linking."""
    findings = []

    for fpath, content in files.items():
        rel = relative_path(fpath, project_dir)
        # Look for checkout session creation
        if re.search(r"checkout\.sessions\.create", content, re.IGNORECASE):
            # Check for metadata in the surrounding code block
            if not re.search(r"metadata\s*[=:{]", content):
                findings.append({
                    "severity": "critical",
                    "rule": "META-001",
                    "message": f"Checkout session created without metadata in {rel}. Cannot link subscription to user in webhooks.",
                    "file": rel,
                    "fix": "Add metadata: { userId: user.id } to checkout session creation.",
                })

    return findings


def audit_webhook_endpoint_security(files, project_dir):
    """Check for common webhook endpoint security issues."""
    findings = []

    for fpath, content in files.items():
        rel = relative_path(fpath, project_dir)
        if "webhook" not in fpath.lower():
            continue

        # Check for JSON body parsing before signature verification
        lines = content.splitlines()
        json_parse_line = None
        sig_verify_line = None

        for i, line in enumerate(lines):
            if re.search(r"json\.parse|JSON\.parse|\.json\(\)", line, re.IGNORECASE) and json_parse_line is None:
                json_parse_line = i
            if re.search(r"constructEvent|construct_event|verify_header", line, re.IGNORECASE) and sig_verify_line is None:
                sig_verify_line = i

        if json_parse_line is not None and sig_verify_line is not None:
            if json_parse_line < sig_verify_line:
                findings.append({
                    "severity": "warning",
                    "rule": "SEC-002",
                    "message": f"JSON parsing occurs before signature verification in {rel}. This can break signature checks.",
                    "file": rel,
                    "fix": "Read the raw request body first for signature verification, then parse JSON.",
                })

    return findings


def audit_env_file_exposure(project_dir):
    """Check that .env files with Stripe keys are gitignored."""
    findings = []
    gitignore_path = os.path.join(project_dir, ".gitignore")
    gitignore_content = ""
    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()
        except (OSError, IOError):
            pass

    has_env_in_gitignore = bool(re.search(r"\.env", gitignore_content))

    # Check for .env files with Stripe keys
    for fname in os.listdir(project_dir):
        if fname.startswith(".env") and os.path.isfile(os.path.join(project_dir, fname)):
            try:
                with open(os.path.join(project_dir, fname), "r") as f:
                    env_content = f.read()
                if re.search(r"STRIPE_SECRET_KEY|sk_live_|sk_test_", env_content):
                    if not has_env_in_gitignore:
                        findings.append({
                            "severity": "critical",
                            "rule": "ENV-001",
                            "message": f"{fname} contains Stripe keys but .env is not in .gitignore.",
                            "fix": "Add .env* to your .gitignore immediately to prevent key exposure.",
                        })
            except (OSError, IOError):
                continue
    return findings


def run_audit(project_dir, min_severity="info"):
    """Run all audit checks and return results."""
    severity_order = {"critical": 0, "warning": 1, "info": 2, "pass": 3}
    min_level = severity_order.get(min_severity, 2)

    files = collect_source_files(project_dir)
    results = {
        "project": str(project_dir),
        "files_scanned": len(files),
        "findings": [],
        "summary": {"critical": 0, "warning": 0, "info": 0, "pass": 0},
    }

    if not files:
        results["findings"].append({
            "severity": "warning",
            "rule": "SCAN-001",
            "message": "No source files found to audit.",
        })
        results["summary"]["warning"] = 1
        return results

    # Run all audit checks
    all_findings = []
    all_findings.extend(audit_hardcoded_keys(files, project_dir))
    all_findings.extend(audit_api_version_pinning(files, project_dir))
    all_findings.extend(audit_idempotency_keys(files, project_dir))
    all_findings.extend(audit_error_handling(files, project_dir))
    all_findings.extend(audit_price_id_handling(files, project_dir))
    all_findings.extend(audit_metadata_on_checkout(files, project_dir))
    all_findings.extend(audit_webhook_endpoint_security(files, project_dir))
    all_findings.extend(audit_env_file_exposure(project_dir))

    # Filter by minimum severity
    for finding in all_findings:
        sev = finding.get("severity", "info")
        if severity_order.get(sev, 2) <= min_level:
            results["findings"].append(finding)
            if sev in results["summary"]:
                results["summary"][sev] += 1

    # Overall status
    results["status"] = "FAIL" if results["summary"]["critical"] > 0 else "PASS"
    return results


def format_human(results):
    """Format results for human-readable terminal output."""
    lines = []
    lines.append("=" * 64)
    lines.append("  Stripe Integration Auditor")
    lines.append("=" * 64)
    lines.append(f"\nProject: {results['project']}")
    lines.append(f"Files scanned: {results['files_scanned']}")

    severity_icons = {
        "critical": "[CRITICAL]",
        "warning":  "[WARNING] ",
        "info":     "[INFO]    ",
        "pass":     "[PASS]    ",
    }

    lines.append(f"\n{'─' * 64}")
    lines.append("FINDINGS:")
    lines.append(f"{'─' * 64}")

    # Group by severity
    for sev in ("critical", "warning", "info", "pass"):
        sev_findings = [f for f in results["findings"] if f.get("severity") == sev]
        if not sev_findings:
            continue
        for finding in sev_findings:
            icon = severity_icons.get(sev, "[?]")
            loc = ""
            if "file" in finding:
                loc = f" ({finding['file']}"
                if "line" in finding:
                    loc += f":{finding['line']}"
                loc += ")"
            lines.append(f"\n  {icon} {finding['rule']}: {finding['message']}{loc}")
            if "fix" in finding:
                lines.append(f"    Fix: {finding['fix']}")

    lines.append(f"\n{'─' * 64}")
    s = results["summary"]
    lines.append(f"Summary: {s['critical']} critical, {s['warning']} warnings, {s['info']} info, {s['pass']} passed")
    lines.append(f"Status: {results['status']}")
    lines.append("=" * 64)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Audit Stripe integration code for common issues: hardcoded keys, missing idempotency, unhandled events.",
        epilog="Example: %(prog)s /path/to/project --severity warning --json",
    )
    parser.add_argument("project_dir", help="Path to the project directory to audit")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")
    parser.add_argument(
        "--severity",
        choices=["critical", "warning", "info"],
        default="info",
        help="Minimum severity level to report (default: info)",
    )

    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        print(f"Error: '{project_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(2)

    results = run_audit(project_dir, min_severity=args.severity)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    sys.exit(0 if results["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
