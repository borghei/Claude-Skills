#!/usr/bin/env python3
"""Classify a pull request's merge risk from its changed files (and optionally its diff).

Every path is matched against risk categories. One-way categories (schema
migrations, public API contracts, persisted formats, data deletion) cannot be
undone by reverting the merge; conditional categories (infrastructure, auth,
dependencies, CI, config defaults) can be, but only with care. The overall door
is the most severe category found. With --diff, added and removed lines are also
scanned for destructive SQL and removed contract fields.

Usage:
  python3 risk_classifier.py --files changed.txt
  git diff --name-only main...HEAD | python3 risk_classifier.py --files -
  python3 risk_classifier.py --files ../assets/sample_changed_files.json --diff ../assets/sample_migration.diff
  python3 risk_classifier.py --files changed.txt --emit-section       # print a draft Merge risk section

Exit codes:
  0  classified (and below the --fail-on threshold, if given)
  1  door is at or above --fail-on (one-way | conditional)
  2  usage error (missing or unreadable input)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DOOR_RANK = {"two-way": 0, "conditional": 1, "one-way": 2}

# (category, door, path regex, rollback guidance)
CATEGORIES: List[Tuple[str, str, str, str]] = [
    ("schema-migration", "one-way",
     r"(^|/)(migrations?|migrate|alembic/versions|db/migrate|prisma/migrations|flyway|liquibase|changelog)/"
     r"|(^|/)V\d+(_\d+)*__\w+\.sql$|(^|/)(schema|structure)\.sql$",
     "Reverting the code does not revert the schema. Ship expand/contract: additive change first, "
     "backfill, switch reads, drop in a later PR. State the down-migration or the forward fix."),
    ("public-api-contract", "one-way",
     r"(^|/)(openapi|swagger)[^/]*\.(ya?ml|json)$|\.proto$|\.graphqls?$|(^|/)schema\.graphql$"
     r"|(^|/)api/v\d+/|(^|/)(sdk|public-api|contracts?)/",
     "Clients may already depend on the new shape. Additive changes only, or version the endpoint; "
     "removed or renamed fields need a deprecation window."),
    ("persisted-format", "one-way",
     r"\.avsc$|(^|/)(events?|messages?)/schemas?/|(^|/)(cache_keys?|storage_format|wire_format)",
     "Data written in the new format stays after a revert. Readers must accept both formats "
     "before writers switch."),
    ("data-deletion", "one-way",
     r"(purge|retention|gdpr|erasure|data_deletion|hard_delete|cleanup_job|backfill)",
     "Deleted data does not come back with a revert. Confirm backups, a dry-run count, and batch limits."),
    ("infrastructure", "conditional",
     r"\.tf$|\.tfvars$|(^|/)(terraform|pulumi|cdk|cloudformation|helm|k8s|kubernetes|charts)/"
     r"|(^|/)(Dockerfile|docker-compose[^/]*\.ya?ml)$",
     "Most infra changes roll back by re-applying the previous version, but destroy/replace plans do not. "
     "Attach the plan output and call out any resource replacement."),
    ("auth-security", "conditional",
     r"(^|/)(auth|authn|authz|authentication|authorization|security|permissions?|rbac|acl|sessions?|crypto"
     r"|oauth|sso|jwt)(/|[_.-])",
     "Revertible, but a window of weaker checks may already have been exploited. Name the access paths affected."),
    ("dependencies", "conditional",
     r"(^|/)(package(-lock)?\.json|yarn\.lock|pnpm-lock\.yaml|requirements[^/]*\.txt|poetry\.lock|Pipfile(\.lock)?"
     r"|go\.(mod|sum)|Cargo\.(toml|lock)|Gemfile(\.lock)?|pom\.xml|build\.gradle(\.kts)?)$",
     "Revertible, but transitive upgrades can change runtime behaviour silently. List major-version bumps."),
    ("ci-deploy", "conditional",
     r"(^|/)\.github/workflows/|(^|/)\.gitlab-ci\.yml$|(^|/)\.circleci/|(^|/)Jenkinsfile$|(^|/)deploy/",
     "A broken pipeline can block the revert itself. Confirm the rollback path does not depend on this change."),
    ("config-flags", "conditional",
     r"(^|/)(config|settings)/|\.env(\.\w+)?$|(^|/)feature[_-]?flags?|(^|/)flags/",
     "Usually revertible by config. State the default, who sees the change at merge, and the off switch."),
    ("tests-docs", "two-way",
     r"(^|/)(tests?|spec|__tests__|e2e|docs?)/|_test\.\w+$|\.test\.\w+$|\.spec\.\w+$|\.md$",
     "No runtime effect."),
]
TEST_OR_DOC = re.compile(CATEGORIES[-1][2], re.IGNORECASE)
COMPILED = [(name, door, re.compile(rx, re.IGNORECASE), note) for name, door, rx, note in CATEGORIES]

DIFF_SIGNALS: List[Tuple[str, str, str]] = [
    ("+", r"\bDROP\s+(TABLE|COLUMN|INDEX|SCHEMA|DATABASE)\b", "destructive DDL (DROP)"),
    ("+", r"\bTRUNCATE\b", "TRUNCATE removes every row"),
    ("+", r"\bDELETE\s+FROM\s+\w+\s*;", "DELETE without WHERE"),
    ("+", r"\bALTER\s+TABLE\b.*\bRENAME\b", "rename breaks old readers mid-deploy"),
    ("+", r"\bALTER\s+COLUMN\b.*\b(TYPE|SET\s+NOT\s+NULL)\b", "type change / NOT NULL can rewrite or lock the table"),
    ("+", r"\b(drop_column|remove_column|drop_table|rename_column)\b", "destructive migration helper"),
    ("-", r"^\s*(optional|required|repeated)?\s*\w+\s+\w+\s*=\s*\d+\s*;", "removed protobuf field"),
    ("-", r"^\s{2,}\w+:\s*$|^\s*-\s*name:\s*\w+", "removed contract field or parameter"),
]
DOWN_MARKER = re.compile(r"def\s+(downgrade|down|rollback)\b|migrate\s+down|^\s*--\s*down\b", re.IGNORECASE)


def read_files(arg: str) -> List[str]:
    """Load changed paths from '-', a .json list / {"files": [...]}, or a newline text file."""
    try:
        raw = sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"error: cannot read files list: {exc}")
    text = raw.strip()
    if text.startswith(("[", "{")):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"error: files list looks like JSON but is invalid: {exc}")
        items = data.get("files", []) if isinstance(data, dict) else data
        return [str(i).strip() for i in items if str(i).strip()]
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def classify_files(paths: List[str]) -> List[Dict[str, Any]]:
    """Return one record per path with every matching category; unmatched paths are plain code."""
    out = []
    for path in paths:
        if TEST_OR_DOC.search(path):
            hits = [("tests-docs", "two-way")]
        else:
            hits = [(n, d) for n, d, rx, _ in COMPILED if rx.search(path) and n != "tests-docs"]
        if not hits:
            hits = [("application-code", "two-way")]
        door = max((d for _, d in hits), key=lambda d: DOOR_RANK[d])
        out.append({"path": path, "categories": [n for n, _ in hits], "door": door})
    return out


def scan_diff(diff_text: str) -> List[Dict[str, Any]]:
    """Find destructive statements in added lines and removed contract fields in removed lines."""
    findings: List[Dict[str, Any]] = []
    current, in_down = "", False
    for number, line in enumerate(diff_text.splitlines(), 1):
        if line.startswith("+++ "):
            current = re.sub(r"^\+\+\+ (b/)?", "", line).strip()
            in_down = False
            continue
        if line.startswith(("---", "@@")) or not line[:1] in ("+", "-"):
            continue
        sign, body = line[0], line[1:]
        if sign == "+" and DOWN_MARKER.search(body):
            in_down = True
        if in_down and sign == "+":
            continue
        for want, rx, label in DIFF_SIGNALS:
            if sign != want or not re.search(rx, body, re.IGNORECASE):
                continue
            if want == "-" and not any(rx2.search(current) for n, _, rx2, _ in COMPILED
                                       if n in ("public-api-contract", "persisted-format")):
                continue
            findings.append({"file": current, "line": number, "signal": label, "text": body.strip()[:120]})
            break
    return findings


def summarize(files: List[Dict[str, Any]], diff_hits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Overall door, blast radius and rollback guidance for the whole change."""
    door = max([f["door"] for f in files] + ["two-way"], key=lambda d: DOOR_RANK[d])
    if diff_hits:
        door = "one-way"
    cats = sorted({c for f in files for c in f["categories"]})
    runtime = [f for f in files if f["categories"] != ["tests-docs"]] or files
    tops = sorted({f["path"].split("/")[0] if "/" in f["path"] else "(root)" for f in runtime})
    if len(runtime) <= 3 and len(tops) <= 1:
        radius = "contained"
    elif len(tops) <= 2:
        radius = "module"
    elif len(tops) <= 5:
        radius = "cross-cutting"
    else:
        radius = "platform-wide"
    if any(c in cats for c in ("public-api-contract", "persisted-format", "ci-deploy")) and radius == "contained":
        radius = "module"
    guidance = [{"category": n, "door": d, "rollback": note} for n, d, _, note in COMPILED if n in cats and d != "two-way"]
    return {"door": door, "blast_radius": radius, "categories": cats, "top_level_dirs": tops,
            "file_count": len(files), "diff_signals": diff_hits, "guidance": guidance, "files": files}


def emit_section(report: Dict[str, Any]) -> str:
    """Draft a Merge risk section; the author must still fill the bracketed parts."""
    door = report["door"]
    label = {"one-way": "One-way door (not reversible by revert)",
             "conditional": "Two-way door, with conditions",
             "two-way": "Two-way door (revert is a full rollback)"}[door]
    lines = ["## Merge risk", "", f"**Classification:** {label}",
             f"**Blast radius:** {report['blast_radius']} ({report['file_count']} files, "
             f"{', '.join(report['top_level_dirs'])})", ""]
    for g in report["guidance"]:
        lines.append(f"- **{g['category']}**: {g['rollback']}")
    for hit in report["diff_signals"]:
        lines.append(f"- `{hit['file']}`: {hit['signal']}: `{hit['text']}`")
    lines += ["", "**Rollback plan:** [exact steps, who runs them, how long they take]" if door != "two-way"
              else "**Rollback plan:** revert this PR; no data or contract changes."]
    return "\n".join(lines)


def main() -> None:
    """Entry point."""
    p = argparse.ArgumentParser(description="Classify PR merge risk from changed files and an optional diff.")
    p.add_argument("--files", required=True, help="changed paths: '-' for stdin, .json list, or text file")
    p.add_argument("--diff", help="optional unified diff to scan for destructive statements")
    p.add_argument("--fail-on", choices=["one-way", "conditional"], help="exit 1 when the door is at least this")
    p.add_argument("--emit-section", action="store_true", help="print a draft '## Merge risk' markdown section")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = p.parse_args()
    paths = read_files(args.files)
    if not paths:
        print("error: no changed files supplied", file=sys.stderr)
        sys.exit(2)
    diff_hits: List[Dict[str, Any]] = []
    if args.diff:
        try:
            diff_hits = scan_diff(Path(args.diff).read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            print(f"error: cannot read diff: {exc}", file=sys.stderr)
            sys.exit(2)
    report = summarize(classify_files(paths), diff_hits)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    elif args.emit_section:
        print(emit_section(report))
    else:
        print(f"Door: {report['door']}   Blast radius: {report['blast_radius']}   Files: {report['file_count']}")
        for f in report["files"]:
            print(f"  {f['door']:<11} {', '.join(f['categories']):<34} {f['path']}")
        for hit in report["diff_signals"]:
            print(f"  diff: {hit['file']}:{hit['line']} {hit['signal']} -> {hit['text']}")
        for g in report["guidance"]:
            print(f"\n  [{g['category']}] {g['rollback']}")
    threshold: Optional[str] = args.fail_on
    sys.exit(1 if threshold and DOOR_RANK[report["door"]] >= DOOR_RANK[threshold] else 0)


if __name__ == "__main__":
    main()
