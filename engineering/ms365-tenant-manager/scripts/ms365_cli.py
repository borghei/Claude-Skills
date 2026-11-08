#!/usr/bin/env python3
"""Command-line front end for the Microsoft 365 tenant manager modules.

Generates PowerShell scripts and planning data from local inputs. It never
connects to a tenant: every script it writes must be reviewed and run by an
administrator, report-only or with -WhatIf first.

Subcommands:
    audit              7-category security audit script (Microsoft Graph + Exchange Online)
    conditional-access Conditional Access policy script, created in report-only state
    bulk-license       license assignment script for a CSV of user principal names
    provision          validate a users CSV, then write the bulk-creation script
    offboard           secure offboarding script for one user
    recommend-license  license recommendation for a role and department
    setup              tenant setup checklist, DNS records, setup script or license plan

Exit codes: 0 = output written; 1 = provision input has invalid users (no script
written); 2 = unusable input (missing file, bad JSON/CSV, wrong shape).

Examples:
    python3 ms365_cli.py audit --domain contoso.com -o audit.ps1
    python3 ms365_cli.py provision --domain contoso.com --users ../assets/sample_users.csv
    python3 ms365_cli.py setup --config ../sample_input.json --part dns --format json
"""

import argparse
import csv
import json
import os
import sys


import importlib.util as _ilu  # noqa: E402


def _sibling(name):
    """Load a sibling script as a module (keeps each script standalone)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PowerShellScriptGenerator = _sibling("powershell_generator").PowerShellScriptGenerator
TenantSetupManager = _sibling("tenant_setup").TenantSetupManager
UserLifecycleManager = _sibling("user_management").UserLifecycleManager

USER_FIELDS = ["first_name", "last_name", "username", "display_name", "job_title", "department", "license_sku"]


def fail(msg: str) -> None:
    """Print a one-line error and exit 2 (unusable input)."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return fh.read()
    except OSError as exc:
        fail(f"cannot read {path}: {exc.strerror}")
    return ""


def load_users(path: str):
    """Load users from a CSV (header row) or a JSON array of objects."""
    text = read_text(path)
    if path.lower().endswith(".json"):
        try:
            users = json.loads(text)
        except json.JSONDecodeError as exc:
            fail(f"{path} is not valid JSON: {exc}")
    else:
        rows = list(csv.DictReader(text.splitlines()))
        if not rows or "username" not in rows[0]:
            fail(f"{path} needs a header row with at least first_name,last_name,username")
        users = [{k.strip(): (v or "").strip() for k, v in row.items() if k} for row in rows]
    if not isinstance(users, list) or not all(isinstance(u, dict) for u in users) or not users:
        fail(f"{path} must hold a non-empty list of user objects")
    return users


def load_tenant_config(path: str) -> dict:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON: {exc}")
    config = data.get("tenant_config", data) if isinstance(data, dict) else None
    if not isinstance(config, dict) or not config.get("domain_name"):
        fail(f"{path} must be an object with 'domain_name' (top level or under 'tenant_config')")
    return config


def emit(content, args, as_json=False) -> None:
    """Write text or JSON to --output or stdout."""
    text = json.dumps(content, indent=2) if as_json else str(content)
    if not args.output:
        print(text)
        return
    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + ("\n" if not text.endswith("\n") else ""))
    except OSError as exc:
        fail(f"cannot write {args.output}: {exc.strerror}")
    print(f"wrote {args.output}", file=sys.stderr)


def cmd_audit(args):
    emit(PowerShellScriptGenerator(args.domain).generate_security_audit_script(), args)


def cmd_conditional_access(args):
    config = {"name": args.name, "require_mfa": not args.no_mfa, "include_users": args.include,
              "exclude_users": args.exclude or []}
    if not config["exclude_users"]:
        print("warning: no --exclude break-glass account; a mistaken policy can lock every admin out",
              file=sys.stderr)
    emit(PowerShellScriptGenerator(args.domain).generate_conditional_access_policy_script(config), args)


def cmd_bulk_license(args):
    if not os.path.isfile(args.csv):
        fail(f"cannot read {args.csv}: no such file")
    emit(PowerShellScriptGenerator(args.domain).generate_bulk_license_assignment_script(args.csv, args.sku), args)


def cmd_provision(args):
    users = load_users(args.users)
    manager = UserLifecycleManager(args.domain)
    report = [(u.get("username") or f"row {i + 1}", manager.validate_user_data(u)) for i, u in enumerate(users)]
    invalid = [(name, r) for name, r in report if not r["is_valid"]]
    for name, result in report:
        for warning in result["warnings"]:
            print(f"warning: {name}: {warning}", file=sys.stderr)
    if invalid:
        for name, result in invalid:
            print(f"invalid: {name}: {'; '.join(result['errors'])}", file=sys.stderr)
        print(f"{len(invalid)} of {len(users)} users invalid; no script written", file=sys.stderr)
        sys.exit(1)
    emit(manager.generate_user_creation_script(users), args)


def cmd_offboard(args):
    if "@" not in args.user:
        fail(f"--user must be a user principal name (name@domain), got {args.user!r}")
    emit(UserLifecycleManager(args.domain).generate_user_offboarding_script(args.user), args)


def cmd_recommend(args):
    rec = UserLifecycleManager("example.com").generate_license_assignment_recommendations(args.role, args.department)
    if args.format == "json":
        return emit(rec, args, as_json=True)
    lines = [f"Recommended: {rec['recommended_license']} (list price ${rec['monthly_cost']:.2f}/user/month; "
             "check current Microsoft pricing)", f"Why: {rec['justification']}"]
    emit("\n".join(lines + [f"  - {f}" for f in rec.get("features_needed", [])]), args)


def cmd_setup(args):
    manager = TenantSetupManager(load_tenant_config(args.config))
    if args.part == "script":
        return emit(manager.generate_powershell_setup_script(), args)
    data = {"checklist": manager.generate_setup_checklist, "dns": manager.generate_dns_records,
            "licenses": manager.get_license_recommendations}[args.part]()
    if args.format == "json":
        return emit(data, args, as_json=True)
    if args.part == "dns":
        rows = [f"{r.get('type', kind):<6} {r.get('name', '@'):<16} {r.get('value', '')}  ({r.get('purpose', '')})"
                for kind, records in data.items() for r in (records if isinstance(records, list) else [])]
        return emit("\n".join(rows) or json.dumps(data, indent=2), args)
    if args.part == "licenses":
        dist = data.get("suggested_distribution", {})
        rows = [f"  {k}: {v}" for k, v in dist.items()]
        return emit("\n".join(["Suggested distribution:"] + rows +
                              [f"Estimated monthly cost: ${data['estimated_monthly_cost']:.2f} (list prices; verify)"]), args)
    rows = []
    for phase in data:
        rows.append(f"Phase {phase.get('phase')}: {phase.get('name')} [{phase.get('priority')}]")
        rows += [f"  - {t.get('task', t) if isinstance(t, dict) else t}" for t in phase.get("tasks", [])]
    emit("\n".join(rows), args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Microsoft 365 admin PowerShell scripts and plans "
                                                 "from local inputs (never connects to a tenant).")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, func, help_text, domain=True):
        p = sub.add_parser(name, help=help_text)
        if domain:
            p.add_argument("--domain", required=True, help="Primary tenant domain, e.g. contoso.com")
        p.add_argument("-o", "--output", help="Write to this file instead of stdout")
        p.add_argument("--format", choices=["text", "json"], default="text", help="Output format for data commands")
        p.set_defaults(func=func)
        return p

    add("audit", cmd_audit, "security audit script")
    p = add("conditional-access", cmd_conditional_access, "report-only Conditional Access policy script")
    p.add_argument("--name", default="Require MFA for all users", help="Policy display name")
    p.add_argument("--include", default="All", help="Users to include (default: All)")
    p.add_argument("--exclude", nargs="*", help="Object IDs or UPNs to exclude (put break-glass accounts here)")
    p.add_argument("--no-mfa", action="store_true", help="Do not add the MFA grant control")
    p = add("bulk-license", cmd_bulk_license, "bulk license assignment script")
    p.add_argument("--csv", required=True, help="CSV with a UserPrincipalName column")
    p.add_argument("--sku", required=True, help="License SKU part number, e.g. SPE_E3")
    p = add("provision", cmd_provision, "validate users, then write the creation script")
    p.add_argument("--users", required=True, help=f"CSV (columns: {','.join(USER_FIELDS)}) or JSON array")
    p = add("offboard", cmd_offboard, "secure offboarding script for one user")
    p.add_argument("--user", required=True, help="User principal name to offboard")
    p = add("recommend-license", cmd_recommend, "license recommendation for a role", domain=False)
    p.add_argument("--role", required=True, help="Job title, e.g. 'Finance Director'")
    p.add_argument("--department", default="", help="Department name")
    p = add("setup", cmd_setup, "tenant setup plan from a config JSON", domain=False)
    p.add_argument("--config", required=True, help="JSON with tenant_config (see sample_input.json)")
    p.add_argument("--part", choices=["checklist", "dns", "script", "licenses"], default="checklist")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if getattr(args, "domain", None) is not None and ("." not in args.domain or " " in args.domain):
        fail(f"--domain must be a DNS domain such as contoso.com, got {args.domain!r}")
    args.func(args)


if __name__ == "__main__":
    main()
