#!/usr/bin/env python3
"""
flag_audit.py — Audit feature flag references in a codebase.

Scans source files for flag-system SDK calls, extracts flag keys, optionally
cross-references against a flag-system export (JSON), and produces a debt
report with per-flag categorization and recommended actions.

Stdlib only. JSON + markdown + human-readable output.

Usage:
    python3 flag_audit.py --path . --format markdown
    python3 flag_audit.py --path ./src --flag-export ./flags.json --format json
    python3 flag_audit.py --path . --format human --owner-team growth-eng
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Patterns that match flag-system SDK calls across common providers.
# Each pattern captures the flag key as group 1.
SDK_CALL_PATTERNS = [
    # LaunchDarkly: client.variation("flag-key", ...), boolVariation(...), etc.
    re.compile(r"""(?:ld_?client|client)\.(?:bool_?|string_?|int_?|json_?|number_?)?variation\(\s*["']([\w\.\-_]+)["']""", re.IGNORECASE),
    re.compile(r"""(?:ld_?client|client)\.(?:bool|string|int|json|number)Variation\(\s*["']([\w\.\-_]+)["']"""),
    # OpenFeature: client.getBooleanValue("flag-key", default, ctx)
    re.compile(r"""client\.get(?:Boolean|String|Integer|Number|Object)(?:Value|Details)\(\s*["']([\w\.\-_]+)["']"""),
    # Generic: flags.is_enabled("flag-key"), flag_client.evaluate("flag-key"), etc.
    re.compile(r"""(?:flags?|feature_?flags?|flag_?client|ff)\.(?:is_?enabled|evaluate|get_?variant|get_?value|variation|check)\(\s*["']([\w\.\-_]+)["']""", re.IGNORECASE),
    # Statsig: Statsig.checkGate("gate-key"), getConfig("config-key")
    re.compile(r"""Statsig\.(?:check_?gate|get_?config|get_?experiment|get_?layer)\(\s*["']([\w\.\-_]+)["']""", re.IGNORECASE),
    # Unleash: unleash.isEnabled("flag-key")
    re.compile(r"""unleash\.(?:is_?enabled|getVariant)\(\s*["']([\w\.\-_]+)["']""", re.IGNORECASE),
    # Generic decorator: @feature_flag("flag-key")
    re.compile(r"""@(?:feature_?flag|flag|require_?flag|require_?entitlement)\(\s*["']([\w\.\-_]+)["']""", re.IGNORECASE),
    # Homegrown and hook helpers: getFlag("x"), isFeatureEnabled("x"), useFlag("x"), get_feature_flag("x")
    re.compile(r"""\b(?:get|use|is|has)_?(?:feature_?)?flag(?:_?enabled|_?value)?\(\s*["']([\w\.\-_]+)["']""", re.IGNORECASE),
    re.compile(r"""\bis_?feature_?enabled\(\s*["']([\w\.\-_]+)["']""", re.IGNORECASE),
    # OpenFeature React hooks: useBooleanFlagValue("x", false)
    re.compile(r"""\buse(?:Boolean|String|Number|Object)Flag(?:Value|Details)\(\s*["']([\w\.\-_]+)["']"""),
]

# Patterns for flag-key constants: SIGNUP_V2_FLAG = "flag.key.here"
CONSTANT_PATTERN = re.compile(
    r"""^\s*([A-Z][A-Z0-9_]*(?:FLAG|_FLAG|_KEY|_FF|FF_KEY))\s*[:=]\s*["']([\w\.\-_]+)["']""",
    re.MULTILINE,
)

# File extensions to scan
SCAN_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".kt", ".rb", ".rs", ".cs", ".php", ".scala"}

# Directories to skip
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "env", ".env", "__pycache__", "dist", "build", "target", ".next", ".nuxt", "coverage", ".pytest_cache", ".mypy_cache"}


@dataclass
class FlagReference:
    path: str
    line: int
    flag_key: str
    matched_pattern: str
    context_snippet: str


@dataclass
class FlagRecord:
    """A single flag's status across code and (optionally) the control plane."""
    key: str
    type_declared: str = "unknown"
    owner: str = ""
    owner_status: str = "unknown"
    current_value_prod: str = "unknown"
    days_at_current_value: int | None = None
    code_references: list[dict[str, Any]] = field(default_factory=list)
    in_code: bool = False
    in_control_plane: bool = False
    category: str = "unknown"
    recommendation: str = ""
    removal_complexity: str = "unknown"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit feature flag references in a codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--path", required=True, help="Root path of codebase to scan")
    p.add_argument(
        "--flag-export",
        help="Optional path to flag-system export JSON. If provided, cross-references code refs against the control plane to find dead/stranded flags.",
    )
    p.add_argument(
        "--format",
        choices=["json", "markdown", "human"],
        default="human",
        help="Output format (default: human)",
    )
    p.add_argument("--output", help="Output file path. If omitted, writes to stdout.")
    p.add_argument(
        "--owner-team",
        help="Filter results to a specific owner team (matches owner field in flag-export)",
    )
    p.add_argument(
        "--as-of", help="Date (YYYY-MM-DD) to measure flag age from (default: today)",
    )
    p.add_argument(
        "--pattern", action="append", default=[],
        help="Extra regex for your SDK; group 1 must capture the flag key. Repeatable.",
    )
    p.add_argument(
        "--include-active",
        action="store_true",
        help="Include active/healthy flags in the report (default: only debt/issues)",
    )
    return p.parse_args()


def should_skip_dir(dirname: str) -> bool:
    return dirname in SKIP_DIRS or dirname.startswith(".")


def scan_file(path: Path) -> list[FlagReference]:
    """Scan a single file for flag SDK calls and constant definitions."""
    refs: list[FlagReference] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return refs

    # Build a lookup of constant name → flag key so we can resolve indirect refs
    constants: dict[str, str] = {}
    for m in CONSTANT_PATTERN.finditer(text):
        constants[m.group(1)] = m.group(2)

    lines = text.splitlines()

    for pattern in SDK_CALL_PATTERNS:
        for m in pattern.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            flag_key = m.group(1)
            snippet = lines[line_no - 1].strip() if 0 < line_no <= len(lines) else ""
            refs.append(
                FlagReference(
                    path=str(path),
                    line=line_no,
                    flag_key=flag_key,
                    matched_pattern=pattern.pattern[:60] + "...",
                    context_snippet=snippet[:200],
                )
            )

    # Also resolve constants used as flag keys (single-pass heuristic)
    for const_name, flag_key in constants.items():
        # Find usages of the constant
        usage_pattern = re.compile(rf"\b{re.escape(const_name)}\b")
        for m in usage_pattern.finditer(text):
            # Skip the definition line itself
            line_no = text[: m.start()].count("\n") + 1
            snippet = lines[line_no - 1].strip() if 0 < line_no <= len(lines) else ""
            if "=" in snippet and snippet.split("=")[0].strip() == const_name:
                continue
            refs.append(
                FlagReference(
                    path=str(path),
                    line=line_no,
                    flag_key=flag_key,
                    matched_pattern=f"constant {const_name}",
                    context_snippet=snippet[:200],
                )
            )

    return refs


def scan_codebase(root: Path) -> list[FlagReference]:
    """Walk a directory and scan all relevant files."""
    all_refs: list[FlagReference] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        for fn in filenames:
            ext = Path(fn).suffix
            if ext in SCAN_EXTENSIONS:
                refs = scan_file(Path(dirpath) / fn)
                all_refs.extend(refs)
    return all_refs


def load_flag_export(export_path: Path) -> list[dict[str, Any]]:
    """
    Load a flag-system export. Supports several common shapes:
    - {"flags": [...]} (LaunchDarkly export)
    - {"items": [...]} (generic)
    - [...] (bare list)
    Each item should have at minimum: key/name, value/state, optionally type/tags/owner/lastModified.
    """
    data = json.loads(export_path.read_text())
    if isinstance(data, list):
        return data
    for key in ("flags", "items", "features", "data", "results"):
        if isinstance(data.get(key), list):
            return data[key]
    raise ValueError(f"Could not find flag list in export. Tried keys: flags, items, features, data, results.")


AS_OF: datetime | None = None  # set by --as-of so ages are reproducible


def normalize_flag_record(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a flag-export entry into a canonical shape."""
    key = raw.get("key") or raw.get("name") or raw.get("id") or ""
    # Type
    tag_list = raw.get("tags", []) or []
    type_declared = "unknown"
    if "kind" in raw:
        type_declared = str(raw["kind"]).lower()
    for t in tag_list:
        for type_name in ("release", "ops", "experiment", "permission", "entitlement"):
            if type_name in str(t).lower():
                type_declared = "permission" if "entitlement" in str(t).lower() else type_name
                break
    # Current value
    current_value = raw.get("currentValue") or raw.get("value") or raw.get("state") or "unknown"
    if isinstance(current_value, dict):
        # nested form: {"prod": {"value": X}}
        if "prod" in current_value or "production" in current_value:
            current_value = current_value.get("prod") or current_value.get("production")
        if isinstance(current_value, dict):
            current_value = current_value.get("value", "unknown")
    # Days at value
    days = None
    last_mod = raw.get("lastModified") or raw.get("updated_at") or raw.get("modifiedAt")
    if last_mod:
        try:
            if isinstance(last_mod, (int, float)):
                # Unix timestamp (ms or s)
                ts = last_mod / 1000 if last_mod > 10**11 else last_mod
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            else:
                # ISO 8601
                dt = datetime.fromisoformat(str(last_mod).replace("Z", "+00:00"))
            days = ((AS_OF or datetime.now(timezone.utc)) - dt).days
        except (ValueError, TypeError):
            days = None
    # Owner
    owner = raw.get("owner") or raw.get("maintainer") or ""
    if isinstance(owner, dict):
        owner = owner.get("name") or owner.get("email") or owner.get("team") or ""
    return {
        "key": key,
        "type_declared": type_declared,
        "owner": str(owner),
        "current_value_prod": str(current_value),
        "days_at_current_value": days,
    }


def categorize(record: FlagRecord) -> tuple[str, str, str]:
    """
    Return (category, recommendation, removal_complexity).

    Categories:
      dead_unreferenced — in control plane, not in code
      orphan_reference  — in code, not in control plane
      stranded_at_0     — value=off/0% for > 30 days
      stranded_at_100   — value=on/100% for > 30 days
      permanent_should_be_config — same value > 180 days, not a kill switch
      ghost_owner       — owner left or empty
      active_healthy    — everything else
    """
    in_code = bool(record.code_references)
    in_cp = record.in_control_plane
    days = record.days_at_current_value or 0
    value = record.current_value_prod.lower()
    type_ = record.type_declared.lower()

    if in_cp and not in_code:
        return ("dead_unreferenced", "Delete from control plane immediately — no code references.", "trivial")

    if in_code and not in_cp:
        return ("orphan_reference", "Code reads a flag that doesn't exist in control plane — using default. Investigate.", "low")

    is_at_100 = value in ("true", "1", "100", "100%", "on", "enabled") or "100" in value
    is_at_0 = value in ("false", "0", "0%", "off", "disabled") or value == "0"

    if type_ == "release" and is_at_100 and days > 30:
        return ("stranded_at_100", f"Release flag at 100% for {days} days. Remove flag + dead branch.", "medium")

    if type_ == "release" and is_at_0 and days > 30:
        return ("stranded_at_0", f"Release flag at 0% for {days} days. Either ship or kill.", "low")

    if type_ != "ops" and days > 180:
        return ("permanent_should_be_config", f"Same value for {days} days, not an ops flag. Move to config system.", "medium")

    if record.owner_status == "ghost":
        return ("ghost_owner", "Owner no longer at the company. Reassign or remove.", "low")

    return ("active_healthy", "Active and healthy. No action.", "n/a")


def build_records(
    code_refs: list[FlagReference],
    flag_export: list[dict[str, Any]] | None,
    owner_filter: str | None,
) -> dict[str, FlagRecord]:
    by_key: dict[str, FlagRecord] = {}

    # Code references first
    for ref in code_refs:
        rec = by_key.setdefault(ref.flag_key, FlagRecord(key=ref.flag_key))
        rec.in_code = True
        rec.code_references.append(
            {"path": ref.path, "line": ref.line, "snippet": ref.context_snippet}
        )

    # Then control-plane records
    if flag_export:
        for raw in flag_export:
            norm = normalize_flag_record(raw)
            if owner_filter and norm["owner"] != owner_filter:
                continue
            key = norm["key"]
            if not key:
                continue
            rec = by_key.setdefault(key, FlagRecord(key=key))
            rec.in_control_plane = True
            rec.type_declared = norm["type_declared"]
            rec.owner = norm["owner"]
            rec.current_value_prod = norm["current_value_prod"]
            rec.days_at_current_value = norm["days_at_current_value"]

    # Categorize
    for rec in by_key.values():
        rec.category, rec.recommendation, rec.removal_complexity = categorize(rec)

    return by_key


def render_json(records: dict[str, FlagRecord], include_active: bool) -> str:
    items = [r for r in records.values() if include_active or r.category != "active_healthy"]
    summary = build_summary(records)
    out = {
        "summary": summary,
        "flags": [asdict(r) for r in sorted(items, key=lambda r: (r.category, r.key))],
    }
    return json.dumps(out, indent=2, default=str)


def build_summary(records: dict[str, FlagRecord]) -> dict[str, Any]:
    by_cat: dict[str, int] = {}
    for r in records.values():
        by_cat[r.category] = by_cat.get(r.category, 0) + 1
    return {
        "total_flags": len(records),
        "flags_in_code": sum(1 for r in records.values() if r.in_code),
        "flags_in_control_plane": sum(1 for r in records.values() if r.in_control_plane),
        "by_category": by_cat,
        "recommended_immediate_removals": by_cat.get("dead_unreferenced", 0),
        "recommended_after_review": (
            by_cat.get("stranded_at_100", 0)
            + by_cat.get("stranded_at_0", 0)
            + by_cat.get("permanent_should_be_config", 0)
            + by_cat.get("ghost_owner", 0)
        ),
        "audit_run_at": datetime.now(timezone.utc).isoformat(),
    }


def render_markdown(records: dict[str, FlagRecord], include_active: bool) -> str:
    summary = build_summary(records)
    out: list[str] = ["# Feature Flag Audit Report", ""]
    out.append(f"_Generated: {summary['audit_run_at']}_")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- **Total flags tracked**: {summary['total_flags']}")
    out.append(f"- **Flags in code**: {summary['flags_in_code']}")
    out.append(f"- **Flags in control plane**: {summary['flags_in_control_plane']}")
    out.append(f"- **Immediate removals (zero risk)**: {summary['recommended_immediate_removals']}")
    out.append(f"- **Removals after review**: {summary['recommended_after_review']}")
    out.append("")
    out.append("### By category")
    out.append("")
    out.append("| Category | Count |")
    out.append("|----------|-------|")
    for cat, n in sorted(summary["by_category"].items(), key=lambda kv: -kv[1]):
        out.append(f"| {cat} | {n} |")
    out.append("")

    items = [r for r in records.values() if include_active or r.category != "active_healthy"]
    if not items:
        out.append("_No debt to report._")
        return "\n".join(out)

    out.append("## Debt items")
    out.append("")
    for cat in [
        "dead_unreferenced",
        "stranded_at_100",
        "stranded_at_0",
        "permanent_should_be_config",
        "ghost_owner",
        "orphan_reference",
    ]:
        cat_items = [r for r in items if r.category == cat]
        if not cat_items:
            continue
        out.append(f"### {cat} ({len(cat_items)})")
        out.append("")
        out.append("| Flag | Type | Owner | Current | Days | Refs | Recommendation |")
        out.append("|------|------|-------|---------|------|------|----------------|")
        for r in sorted(cat_items, key=lambda r: r.key):
            refs = len(r.code_references)
            owner = r.owner[:30] or "—"
            cur = (r.current_value_prod or "—")[:15]
            days = str(r.days_at_current_value) if r.days_at_current_value is not None else "—"
            out.append(f"| `{r.key}` | {r.type_declared} | {owner} | {cur} | {days} | {refs} | {r.recommendation[:80]} |")
        out.append("")

    if include_active:
        active = [r for r in items if r.category == "active_healthy"]
        if active:
            out.append(f"### active_healthy ({len(active)})")
            out.append("")
            for r in sorted(active, key=lambda r: r.key):
                out.append(f"- `{r.key}` ({r.type_declared}, owner: {r.owner or '—'})")
            out.append("")

    return "\n".join(out)


def render_human(records: dict[str, FlagRecord], include_active: bool) -> str:
    summary = build_summary(records)
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("FEATURE FLAG AUDIT REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {summary['audit_run_at']}")
    lines.append("")
    lines.append(f"Total flags:                  {summary['total_flags']}")
    lines.append(f"In code:                      {summary['flags_in_code']}")
    lines.append(f"In control plane:             {summary['flags_in_control_plane']}")
    lines.append(f"Immediate removal candidates: {summary['recommended_immediate_removals']}")
    lines.append(f"After-review candidates:      {summary['recommended_after_review']}")
    lines.append("")
    lines.append("By category:")
    for cat, n in sorted(summary["by_category"].items(), key=lambda kv: -kv[1]):
        lines.append(f"  {cat:<35} {n}")
    lines.append("")

    items = [r for r in records.values() if include_active or r.category != "active_healthy"]
    if not items:
        lines.append("No debt items to report.")
        return "\n".join(lines)

    lines.append("-" * 60)
    lines.append("DEBT ITEMS")
    lines.append("-" * 60)
    for r in sorted(items, key=lambda r: (r.category, r.key)):
        lines.append(f"\n[{r.category}] {r.key}")
        lines.append(f"  Type:        {r.type_declared}")
        lines.append(f"  Owner:       {r.owner or '—'}")
        lines.append(f"  Value(prod): {r.current_value_prod}")
        lines.append(f"  Days at val: {r.days_at_current_value or '—'}")
        lines.append(f"  Refs:        {len(r.code_references)}")
        lines.append(f"  Action:      {r.recommendation}")
        lines.append(f"  Complexity:  {r.removal_complexity}")
        if r.code_references:
            for ref in r.code_references[:3]:
                lines.append(f"    @ {ref['path']}:{ref['line']}  {ref['snippet'][:80]}")
            if len(r.code_references) > 3:
                lines.append(f"    ... and {len(r.code_references) - 3} more refs")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    for extra in args.pattern:
        try:
            SDK_CALL_PATTERNS.append(re.compile(extra))
        except re.error as exc:
            print(f"error: invalid --pattern {extra!r}: {exc}", file=sys.stderr)
            return 2
    global AS_OF
    if args.as_of:
        try:
            AS_OF = datetime.fromisoformat(args.as_of).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"error: invalid --as-of {args.as_of!r} (use YYYY-MM-DD)", file=sys.stderr)
            return 2
    root = Path(args.path).resolve()
    if not root.exists():
        print(f"error: path not found: {root}", file=sys.stderr)
        return 2

    code_refs = scan_codebase(root)

    flag_export = None
    if args.flag_export:
        try:
            flag_export = load_flag_export(Path(args.flag_export))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: failed to load flag export: {exc}", file=sys.stderr)
            return 2

    records = build_records(code_refs, flag_export, args.owner_team)

    if args.format == "json":
        out = render_json(records, args.include_active)
    elif args.format == "markdown":
        out = render_markdown(records, args.include_active)
    else:
        out = render_human(records, args.include_active)

    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
