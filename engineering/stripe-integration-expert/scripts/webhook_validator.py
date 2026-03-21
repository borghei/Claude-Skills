#!/usr/bin/env python3
"""Stripe Webhook Endpoint Configuration Validator.

Validates webhook endpoint configurations, signature verification setup,
and event handling completeness. Scans project files for common webhook
misconfigurations that cause silent billing failures in production.

Usage:
    python webhook_validator.py /path/to/project
    python webhook_validator.py /path/to/project --json
    python webhook_validator.py /path/to/project --strict
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Critical webhook events that every SaaS billing integration must handle
CRITICAL_EVENTS = [
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",
    "invoice.payment_failed",
]

# Recommended events for a production-quality integration
RECOMMENDED_EVENTS = [
    "customer.subscription.trial_will_end",
    "invoice.payment_action_required",
    "customer.updated",
    "payment_intent.payment_failed",
    "charge.dispute.created",
]

# File extensions to scan
CODE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".rb", ".go", ".java", ".php"}

# Patterns that indicate webhook handling code
WEBHOOK_FILE_PATTERNS = [
    r"webhook",
    r"stripe.*route",
    r"stripe.*handler",
    r"stripe.*endpoint",
]


def find_webhook_files(project_dir):
    """Locate files likely containing webhook handler code."""
    matches = []
    for root, _dirs, files in os.walk(project_dir):
        # Skip common non-source directories
        basename = os.path.basename(root)
        if basename in ("node_modules", ".git", "__pycache__", "dist", "build", ".next", "venv"):
            continue
        for fname in files:
            ext = os.path.splitext(fname)[1]
            if ext not in CODE_EXTENSIONS:
                continue
            fpath = os.path.join(root, fname)
            name_lower = fname.lower()
            if any(re.search(p, name_lower) for p in WEBHOOK_FILE_PATTERNS):
                matches.append(fpath)
    return matches


def read_file_safe(fpath):
    """Read file contents, returning empty string on failure."""
    try:
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, IOError):
        return ""


def scan_all_source_files(project_dir):
    """Collect all source file contents for broad pattern matching."""
    contents = {}
    for root, _dirs, files in os.walk(project_dir):
        basename = os.path.basename(root)
        if basename in ("node_modules", ".git", "__pycache__", "dist", "build", ".next", "venv"):
            continue
        for fname in files:
            ext = os.path.splitext(fname)[1]
            if ext not in CODE_EXTENSIONS:
                continue
            fpath = os.path.join(root, fname)
            contents[fpath] = read_file_safe(fpath)
    return contents


def check_signature_verification(webhook_files, all_contents):
    """Check that webhook signature verification is implemented."""
    findings = []
    sig_patterns = [
        r"constructEvent",               # stripe.webhooks.constructEvent (Node)
        r"Webhook\.construct_event",      # stripe.Webhook.construct_event (Python)
        r"webhook\.ConstructEvent",       # Go
        r"Stripe::Webhook\.construct",    # Ruby
        r"verify_header",                 # Alternative pattern
        r"stripe-signature",             # Reading the header
    ]

    has_verification = False
    for fpath in webhook_files:
        content = all_contents.get(fpath, "")
        for pattern in sig_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                has_verification = True
                break

    if not has_verification:
        findings.append({
            "severity": "critical",
            "rule": "SIG-001",
            "message": "No webhook signature verification detected. Webhooks are vulnerable to forgery.",
            "fix": "Use stripe.webhooks.constructEvent(body, sig, secret) to verify signatures before processing.",
        })
    else:
        findings.append({
            "severity": "pass",
            "rule": "SIG-001",
            "message": "Webhook signature verification detected.",
        })

    # Check for raw body parsing (required for signature verification)
    raw_body_patterns = [
        r"req\.text\(\)",           # Next.js App Router
        r"raw\s*[:(]",             # express.raw() or bodyParser.raw()
        r"getRawBody",             # raw-body package
        r"bodyParser\.raw",        # Express
        r"request\.body",          # Django/Flask raw
    ]
    has_raw_body = False
    for fpath in webhook_files:
        content = all_contents.get(fpath, "")
        for pattern in raw_body_patterns:
            if re.search(pattern, content):
                has_raw_body = True
                break

    if has_verification and not has_raw_body:
        findings.append({
            "severity": "warning",
            "rule": "SIG-002",
            "message": "Signature verification found but raw body parsing not detected. JSON-parsed bodies will fail verification.",
            "fix": "Ensure the request body is read as raw text/buffer before passing to constructEvent.",
        })

    return findings


def check_event_handling(webhook_files, all_contents):
    """Check which Stripe events are handled."""
    findings = []
    handled_events = set()
    all_webhook_content = ""

    for fpath in webhook_files:
        content = all_contents.get(fpath, "")
        all_webhook_content += content
        # Match event type strings in code
        event_matches = re.findall(r'["\']([a-z]+\.[a-z_.]+)["\']', content)
        for ev in event_matches:
            if ev.count(".") >= 1 and any(
                ev.startswith(prefix)
                for prefix in ("checkout.", "customer.", "invoice.", "payment_intent.", "charge.", "subscription_schedule.")
            ):
                handled_events.add(ev)

    # Check critical events
    missing_critical = []
    for event in CRITICAL_EVENTS:
        if event not in handled_events:
            missing_critical.append(event)

    if missing_critical:
        findings.append({
            "severity": "critical",
            "rule": "EVT-001",
            "message": f"Missing {len(missing_critical)} critical webhook event(s): {', '.join(missing_critical)}",
            "fix": "Add handlers for all critical billing events to prevent silent payment failures.",
            "missing_events": missing_critical,
        })
    else:
        findings.append({
            "severity": "pass",
            "rule": "EVT-001",
            "message": f"All {len(CRITICAL_EVENTS)} critical webhook events are handled.",
        })

    # Check recommended events
    missing_recommended = []
    for event in RECOMMENDED_EVENTS:
        if event not in handled_events:
            missing_recommended.append(event)

    if missing_recommended:
        findings.append({
            "severity": "info",
            "rule": "EVT-002",
            "message": f"Missing {len(missing_recommended)} recommended event(s): {', '.join(missing_recommended)}",
            "fix": "Consider handling these events for a more robust integration.",
            "missing_events": missing_recommended,
        })

    return findings, handled_events


def check_idempotency(webhook_files, all_contents):
    """Check for idempotent webhook processing."""
    findings = []
    idempotency_patterns = [
        r"isProcessed|already.?processed|event.?id.*find|findUnique.*event",
        r"markProcessed|mark.?as.?processed|stripeEvent.*create",
        r"idempoten",
        r"dedup|de.?dup|deduplicate",
        r"processed.?event",
    ]

    has_idempotency = False
    for fpath in webhook_files:
        content = all_contents.get(fpath, "")
        for pattern in idempotency_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                has_idempotency = True
                break

    if not has_idempotency:
        findings.append({
            "severity": "critical",
            "rule": "IDEM-001",
            "message": "No idempotency mechanism detected in webhook handlers. Stripe retries will cause duplicate processing.",
            "fix": "Track processed event IDs in a database table and skip already-handled events.",
        })
    else:
        findings.append({
            "severity": "pass",
            "rule": "IDEM-001",
            "message": "Webhook idempotency mechanism detected.",
        })

    return findings


def check_error_handling(webhook_files, all_contents):
    """Check for proper error handling and retry behavior."""
    findings = []

    for fpath in webhook_files:
        content = all_contents.get(fpath, "")
        # Check for catch blocks that always return 200
        if re.search(r"catch.*\{[^}]*200[^}]*\}", content, re.DOTALL):
            findings.append({
                "severity": "warning",
                "rule": "ERR-001",
                "message": f"Webhook handler may return 200 on errors, preventing Stripe retries: {os.path.basename(fpath)}",
                "fix": "Return 500 on processing errors so Stripe retries the webhook delivery.",
                "file": fpath,
            })

    # Check for try/catch around event processing
    has_try_catch = False
    for fpath in webhook_files:
        content = all_contents.get(fpath, "")
        if re.search(r"try\s*\{", content) or re.search(r"try:", content):
            has_try_catch = True
            break

    if not has_try_catch and webhook_files:
        findings.append({
            "severity": "warning",
            "rule": "ERR-002",
            "message": "No try/catch blocks found in webhook handlers. Unhandled errors may crash the endpoint.",
            "fix": "Wrap event processing in try/catch and return appropriate HTTP status codes.",
        })

    return findings


def check_webhook_secret_config(all_contents):
    """Check that webhook secret is loaded from environment, not hardcoded."""
    findings = []

    for fpath, content in all_contents.items():
        # Look for hardcoded webhook secrets
        if re.search(r'whsec_[a-zA-Z0-9]{20,}', content):
            findings.append({
                "severity": "critical",
                "rule": "SEC-001",
                "message": f"Hardcoded webhook signing secret found in {os.path.basename(fpath)}",
                "fix": "Move webhook secrets to environment variables (STRIPE_WEBHOOK_SECRET).",
                "file": fpath,
            })

    # Check for env var usage
    has_env_secret = False
    for content in all_contents.values():
        if re.search(r"STRIPE_WEBHOOK_SECRET|webhook.?secret", content, re.IGNORECASE):
            has_env_secret = True
            break

    if not has_env_secret:
        findings.append({
            "severity": "warning",
            "rule": "SEC-002",
            "message": "No STRIPE_WEBHOOK_SECRET environment variable reference found.",
            "fix": "Define STRIPE_WEBHOOK_SECRET in your environment and reference it in webhook verification.",
        })

    return findings


def run_validation(project_dir, strict=False):
    """Run all webhook validation checks."""
    results = {
        "project": str(project_dir),
        "webhook_files": [],
        "findings": [],
        "summary": {"critical": 0, "warning": 0, "info": 0, "pass": 0},
    }

    # Find webhook files
    webhook_files = find_webhook_files(project_dir)
    results["webhook_files"] = [str(f) for f in webhook_files]

    if not webhook_files:
        results["findings"].append({
            "severity": "critical",
            "rule": "SETUP-001",
            "message": "No webhook handler files found in the project.",
            "fix": "Create a webhook endpoint (e.g., /api/webhooks/stripe) to handle Stripe events.",
        })
        results["summary"]["critical"] = 1
        return results

    # Scan all source files
    all_contents = scan_all_source_files(project_dir)

    # Run all checks
    checks = [
        check_signature_verification(webhook_files, all_contents),
        check_idempotency(webhook_files, all_contents),
        check_error_handling(webhook_files, all_contents),
        check_webhook_secret_config(all_contents),
    ]

    for check_findings in checks:
        results["findings"].extend(check_findings)

    # Event handling check returns extra data
    event_findings, handled_events = check_event_handling(webhook_files, all_contents)
    results["findings"].extend(event_findings)
    results["handled_events"] = sorted(handled_events)

    # Tally summary
    for finding in results["findings"]:
        sev = finding.get("severity", "info")
        if sev in results["summary"]:
            results["summary"][sev] += 1

    # Determine overall status
    if results["summary"]["critical"] > 0:
        results["status"] = "FAIL"
    elif strict and results["summary"]["warning"] > 0:
        results["status"] = "FAIL"
    else:
        results["status"] = "PASS"

    return results


def format_human(results):
    """Format results for human-readable terminal output."""
    lines = []
    lines.append("=" * 60)
    lines.append("  Stripe Webhook Validator")
    lines.append("=" * 60)
    lines.append(f"\nProject: {results['project']}")
    lines.append(f"Webhook files found: {len(results['webhook_files'])}")
    for wf in results["webhook_files"]:
        lines.append(f"  - {wf}")

    if results.get("handled_events"):
        lines.append(f"\nHandled events ({len(results['handled_events'])}):")
        for ev in results["handled_events"]:
            lines.append(f"  - {ev}")

    lines.append(f"\n{'─' * 60}")
    lines.append("FINDINGS:")
    lines.append(f"{'─' * 60}")

    severity_icons = {"critical": "[CRITICAL]", "warning": "[WARNING]", "info": "[INFO]", "pass": "[PASS]"}

    for finding in results["findings"]:
        sev = finding.get("severity", "info")
        icon = severity_icons.get(sev, "[?]")
        lines.append(f"\n  {icon} {finding['rule']}: {finding['message']}")
        if "fix" in finding:
            lines.append(f"    Fix: {finding['fix']}")

    lines.append(f"\n{'─' * 60}")
    s = results["summary"]
    lines.append(f"Summary: {s['critical']} critical, {s['warning']} warnings, {s['info']} info, {s['pass']} passed")
    lines.append(f"Status: {results['status']}")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Stripe webhook endpoint configurations and signature verification setup.",
        epilog="Example: %(prog)s /path/to/project --strict --json",
    )
    parser.add_argument("project_dir", help="Path to the project directory to scan")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures (non-zero exit code)")

    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        print(f"Error: '{project_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(2)

    results = run_validation(project_dir, strict=args.strict)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    sys.exit(0 if results["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
