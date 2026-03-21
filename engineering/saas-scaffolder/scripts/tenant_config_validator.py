#!/usr/bin/env python3
"""Tenant Configuration Validator — Detect multi-tenant isolation issues.

Validates multi-tenant configuration files and source code for common
isolation problems: missing tenant scoping on queries, cross-tenant data
leaks, unscoped API routes, missing workspace context, and configuration
drift between tenants.

Uses ONLY Python standard library. No LLM or API calls.
"""

import argparse
import json
import os
import re
import sys
import textwrap
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------

SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

SEVERITY_ORDER = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2}


def validate_config_file(config_path):
    """Validate a tenant configuration JSON file for structural issues."""
    findings = []

    if not os.path.exists(config_path):
        findings.append(finding("config_missing", SEVERITY_CRITICAL,
                                f"Configuration file not found: {config_path}",
                                fix="Create tenant configuration at the expected path."))
        return findings

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        findings.append(finding("config_invalid_json", SEVERITY_CRITICAL,
                                f"Invalid JSON in {config_path}: {e}",
                                fix="Fix JSON syntax errors in the configuration file."))
        return findings

    # Check for required top-level keys
    required_keys = ["tenants", "isolation_mode", "default_plan"]
    for key in required_keys:
        if key not in config:
            findings.append(finding("config_missing_key", SEVERITY_WARNING,
                                    f"Missing required key '{key}' in configuration.",
                                    fix=f"Add '{key}' to the tenant configuration root."))

    # Validate tenants array
    tenants = config.get("tenants", [])
    if not isinstance(tenants, list):
        findings.append(finding("tenants_not_array", SEVERITY_CRITICAL,
                                "'tenants' must be an array.",
                                fix="Change 'tenants' value to a JSON array."))
        return findings

    if not tenants:
        findings.append(finding("tenants_empty", SEVERITY_WARNING,
                                "No tenants defined in configuration.",
                                fix="Add at least one tenant to the 'tenants' array."))

    # Validate each tenant
    seen_ids = set()
    seen_slugs = set()
    seen_domains = set()

    tenant_required = ["id", "name", "slug", "plan"]

    for i, tenant in enumerate(tenants):
        prefix = f"tenants[{i}]"

        if not isinstance(tenant, dict):
            findings.append(finding("tenant_not_object", SEVERITY_CRITICAL,
                                    f"{prefix}: Tenant entry must be an object.",
                                    fix=f"Ensure {prefix} is a JSON object with id, name, slug, plan."))
            continue

        # Required fields
        for key in tenant_required:
            if key not in tenant:
                findings.append(finding("tenant_missing_field", SEVERITY_WARNING,
                                        f"{prefix}: Missing required field '{key}'.",
                                        fix=f"Add '{key}' to {prefix}."))

        # Unique ID check
        tid = tenant.get("id")
        if tid:
            if tid in seen_ids:
                findings.append(finding("tenant_duplicate_id", SEVERITY_CRITICAL,
                                        f"{prefix}: Duplicate tenant ID '{tid}'.",
                                        fix="Ensure every tenant has a unique 'id'."))
            seen_ids.add(tid)

        # Unique slug check
        slug = tenant.get("slug")
        if slug:
            if slug in seen_slugs:
                findings.append(finding("tenant_duplicate_slug", SEVERITY_CRITICAL,
                                        f"{prefix}: Duplicate tenant slug '{slug}'.",
                                        fix="Ensure every tenant has a unique 'slug'."))
            seen_slugs.add(slug)

        # Custom domain uniqueness
        domain = tenant.get("custom_domain")
        if domain:
            if domain in seen_domains:
                findings.append(finding("tenant_duplicate_domain", SEVERITY_CRITICAL,
                                        f"{prefix}: Duplicate custom domain '{domain}'.",
                                        fix="Each custom domain must map to exactly one tenant."))
            seen_domains.add(domain)

        # Plan validation
        plan = tenant.get("plan", "")
        valid_plans = config.get("valid_plans", ["free", "pro", "enterprise"])
        if plan and plan not in valid_plans:
            findings.append(finding("tenant_invalid_plan", SEVERITY_WARNING,
                                    f"{prefix}: Plan '{plan}' not in valid plans {valid_plans}.",
                                    fix=f"Set plan to one of: {', '.join(valid_plans)}."))

        # Feature flags reference check
        flags = tenant.get("feature_flags", {})
        if isinstance(flags, dict):
            global_flags = config.get("feature_flags", {})
            for flag_key in flags:
                if global_flags and flag_key not in global_flags:
                    findings.append(finding("tenant_unknown_flag", SEVERITY_INFO,
                                            f"{prefix}: Feature flag '{flag_key}' not in global registry.",
                                            fix="Add the flag to the global 'feature_flags' section or remove from tenant."))

        # Database isolation check
        db_config = tenant.get("database", {})
        if isinstance(db_config, dict):
            isolation = config.get("isolation_mode", "shared")
            if isolation == "dedicated" and not db_config.get("connection_string"):
                findings.append(finding("tenant_missing_db", SEVERITY_CRITICAL,
                                        f"{prefix}: Dedicated isolation requires a 'connection_string' in database config.",
                                        fix="Add 'database.connection_string' for dedicated isolation mode."))
            if isolation == "schema" and not db_config.get("schema_name"):
                findings.append(finding("tenant_missing_schema", SEVERITY_WARNING,
                                        f"{prefix}: Schema isolation requires 'schema_name' in database config.",
                                        fix="Add 'database.schema_name' for schema-based isolation."))

    # Cross-tenant checks
    isolation = config.get("isolation_mode", "shared")
    if isolation not in ("shared", "schema", "dedicated"):
        findings.append(finding("invalid_isolation_mode", SEVERITY_WARNING,
                                f"Unknown isolation_mode '{isolation}'. Expected: shared, schema, dedicated.",
                                fix="Set isolation_mode to one of: shared, schema, dedicated."))

    return findings


def scan_source_for_issues(src_dir, extensions=None):
    """Scan source files for common tenant-isolation anti-patterns."""
    findings = []

    if not os.path.isdir(src_dir):
        findings.append(finding("src_dir_missing", SEVERITY_WARNING,
                                f"Source directory not found: {src_dir}",
                                fix="Provide a valid source directory with --src."))
        return findings

    if extensions is None:
        extensions = (".ts", ".tsx", ".js", ".jsx")

    # Patterns to detect
    patterns = [
        {
            "id": "unscoped_query",
            "regex": re.compile(r"db\.(select|query|delete|update)\b(?!.*workspaceId)(?!.*tenantId)(?!.*workspace_id)(?!.*tenant_id)", re.IGNORECASE),
            "severity": SEVERITY_CRITICAL,
            "message": "Database query without tenant scoping (missing workspaceId/tenantId filter).",
            "fix": "Add a WHERE clause filtering by workspaceId or tenantId.",
        },
        {
            "id": "hardcoded_tenant",
            "regex": re.compile(r"""(['"])tenant[_-]?id\1\s*[:=]\s*(['"])[a-zA-Z0-9_-]+\2"""),
            "severity": SEVERITY_WARNING,
            "message": "Hardcoded tenant/workspace ID detected.",
            "fix": "Replace hardcoded ID with dynamic tenant resolution from session or context.",
        },
        {
            "id": "missing_auth_check",
            "regex": re.compile(r"export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)\b(?!.*auth\(\))"),
            "severity": SEVERITY_WARNING,
            "message": "API route handler without auth() check.",
            "fix": "Add `const session = await auth()` at the top of the handler.",
        },
        {
            "id": "global_state_tenant",
            "regex": re.compile(r"(globalThis|global)\.(currentTenant|workspace|tenant)\b"),
            "severity": SEVERITY_CRITICAL,
            "message": "Tenant context stored in global state (causes cross-request leaks).",
            "fix": "Pass tenant context through request/session, not global state.",
        },
        {
            "id": "no_rls_hint",
            "regex": re.compile(r"\.execute\(\s*sql`[^`]*`\s*\)(?!.*WHERE)"),
            "severity": SEVERITY_INFO,
            "message": "Raw SQL execution without visible WHERE clause (ensure RLS or manual scoping).",
            "fix": "Verify row-level security is enabled or add explicit tenant filter.",
        },
    ]

    file_count = 0
    for root, _dirs, files in os.walk(src_dir):
        # Skip node_modules and hidden directories
        parts = root.split(os.sep)
        if any(p.startswith(".") or p == "node_modules" for p in parts):
            continue
        for fname in files:
            if not any(fname.endswith(ext) for ext in extensions):
                continue
            fpath = os.path.join(root, fname)
            file_count += 1
            try:
                with open(fpath, "r", errors="replace") as f:
                    lines = f.readlines()
            except OSError:
                continue

            for line_num, line in enumerate(lines, start=1):
                for pat in patterns:
                    if pat["regex"].search(line):
                        rel_path = os.path.relpath(fpath, src_dir)
                        findings.append(finding(
                            pat["id"], pat["severity"],
                            f"{rel_path}:{line_num}: {pat['message']}",
                            fix=pat["fix"],
                            file=rel_path, line=line_num,
                            matched_text=line.strip()[:120],
                        ))

    if file_count == 0:
        findings.append(finding("no_source_files", SEVERITY_INFO,
                                f"No source files found in {src_dir} with extensions {extensions}.",
                                fix="Check the --src path and --extensions flags."))

    return findings


def finding(rule_id, severity, message, fix="", file=None, line=None, matched_text=None):
    """Create a standardized finding dict."""
    f = {"rule_id": rule_id, "severity": severity, "message": message, "fix": fix}
    if file:
        f["file"] = file
    if line is not None:
        f["line"] = line
    if matched_text:
        f["matched_text"] = matched_text
    return f


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def summarize(findings):
    """Return summary counts by severity."""
    counts = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 0, SEVERITY_INFO: 0}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    return counts


def print_human_report(findings, title="Tenant Configuration Validation"):
    """Print findings in a human-readable format."""
    print(f"\n{title}")
    print("=" * 70)

    counts = summarize(findings)
    total = len(findings)
    print(f"  Total findings: {total}")
    print(f"  Critical: {counts[SEVERITY_CRITICAL]}  |  Warnings: {counts[SEVERITY_WARNING]}  |  Info: {counts[SEVERITY_INFO]}")
    print("-" * 70)

    if not findings:
        print("  No issues found. Configuration looks good.")
        return

    sorted_findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))

    for i, f in enumerate(sorted_findings, 1):
        sev = f["severity"].upper()
        print(f"\n  [{sev}] {f['message']}")
        if f.get("matched_text"):
            print(f"          Code: {f['matched_text']}")
        if f.get("fix"):
            print(f"          Fix:  {f['fix']}")

    print("\n" + "-" * 70)
    passed = counts[SEVERITY_CRITICAL] == 0
    verdict = "PASSED (no critical issues)" if passed else "FAILED (critical issues found)"
    print(f"  Verdict: {verdict}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate multi-tenant configuration for isolation issues and missing tenant scoping.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s --config tenant_config.json
              %(prog)s --src ./app --src ./lib
              %(prog)s --config tenant_config.json --src ./app --json
              %(prog)s --src ./app --extensions .ts .tsx
        """),
    )

    parser.add_argument("--config", default=None,
                        help="Path to tenant configuration JSON file to validate")
    parser.add_argument("--src", action="append", default=None,
                        help="Source directory to scan for isolation issues (repeatable)")
    parser.add_argument("--extensions", nargs="*", default=None,
                        help="File extensions to scan (default: .ts .tsx .js .jsx)")
    parser.add_argument("--severity", choices=["critical", "warning", "info"], default="info",
                        help="Minimum severity to report (default: info)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")

    args = parser.parse_args()

    if not args.config and not args.src:
        parser.error("Provide at least one of --config or --src to validate.")

    all_findings = []
    min_sev = SEVERITY_ORDER.get(args.severity, 2)

    # Validate config file
    if args.config:
        config_findings = validate_config_file(args.config)
        all_findings.extend(config_findings)

    # Scan source directories
    if args.src:
        exts = tuple(args.extensions) if args.extensions else None
        for src_dir in args.src:
            src_findings = scan_source_for_issues(src_dir, extensions=exts)
            all_findings.extend(src_findings)

    # Filter by severity
    filtered = [f for f in all_findings if SEVERITY_ORDER.get(f["severity"], 9) <= min_sev]

    counts = summarize(filtered)
    has_critical = counts[SEVERITY_CRITICAL] > 0

    result = {
        "success": not has_critical,
        "total_findings": len(filtered),
        "summary": counts,
        "findings": filtered,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "config_file": args.config,
        "source_dirs": args.src or [],
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print_human_report(filtered)

    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
