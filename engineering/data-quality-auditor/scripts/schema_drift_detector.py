#!/usr/bin/env python3
"""
schema_drift_detector.py — Detect schema drift between a baseline and current schema.

Reads JSON or YAML schema documents and reports differences:
  - Added columns
  - Removed columns
  - Type changes
  - Nullability changes
  - Ordinal changes (position shifts)

Severity tagging: critical (type change, removed required column),
warning (added column, nullability tightened), info (ordinal shift, added optional column).

Stdlib only. Markdown or JSON output.

Usage:
    python3 schema_drift_detector.py --baseline baseline.json --current current.json
    python3 schema_drift_detector.py --baseline baseline.json --current current.json --format json
    python3 schema_drift_detector.py --snapshot mytable.json  # generate baseline from inferred data

Exit codes: 0 no drift at or above --fail-on (default critical), 1 drift at or
above --fail-on, 2 bad input (missing file, bad JSON, wrong shape).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class Column:
    name: str
    type: str
    nullable: bool
    ordinal: int


@dataclass
class DriftFinding:
    severity: str  # info / warning / critical
    change_type: str
    column: str
    detail: str
    recommendation: str


SEVERITY_LEVEL = {"info": 0, "warning": 1, "critical": 2}


def load_schema(path: Path) -> list[Column]:
    """
    Load schema from JSON. Supports two shapes:
      [{"name": "col1", "type": "STRING", "nullable": true, "ordinal": 1}, ...]
      {"columns": [...]} (with same column dicts)
    """
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        cols_raw = data.get("columns", [])
    else:
        cols_raw = data
    cols: list[Column] = []
    for i, c in enumerate(cols_raw):
        cols.append(Column(
            name=str(c.get("name", "")),
            type=str(c.get("type", "")).lower(),
            nullable=bool(c.get("nullable", True)),
            ordinal=int(c.get("ordinal", i + 1)),
        ))
    return cols


def diff_schemas(baseline: list[Column], current: list[Column]) -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    base_by_name = {c.name: c for c in baseline}
    cur_by_name = {c.name: c for c in current}

    # Removed columns
    for name, bc in base_by_name.items():
        if name not in cur_by_name:
            severity = "critical" if not bc.nullable else "warning"
            findings.append(DriftFinding(
                severity=severity,
                change_type="removed",
                column=name,
                detail=f"Column {name} (type {bc.type}) removed from schema",
                recommendation="If intentional, update consumer pipelines + baseline. If accidental, restore.",
            ))

    # Added columns
    for name, cc in cur_by_name.items():
        if name not in base_by_name:
            severity = "warning" if not cc.nullable else "info"
            findings.append(DriftFinding(
                severity=severity,
                change_type="added",
                column=name,
                detail=f"New column {name} (type {cc.type}, nullable={cc.nullable})",
                recommendation="Verify intentional. Update baseline + consumer pipelines if so.",
            ))

    # Changed columns
    for name, bc in base_by_name.items():
        if name not in cur_by_name:
            continue
        cc = cur_by_name[name]
        if bc.type != cc.type:
            findings.append(DriftFinding(
                severity="critical",
                change_type="type_changed",
                column=name,
                detail=f"Type changed: {bc.type} → {cc.type}",
                recommendation="Type changes often break consumer parsers. Confirm intentional + coordinated with consumers.",
            ))
        if bc.nullable != cc.nullable:
            severity = "warning" if cc.nullable else "critical"  # tightening nullability is more severe
            direction = "loosened" if cc.nullable else "tightened"
            findings.append(DriftFinding(
                severity=severity,
                change_type="nullability_changed",
                column=name,
                detail=f"Nullability {direction}: {bc.nullable} → {cc.nullable}",
                recommendation="Nullable→NOT NULL can break existing data. NOT NULL→Nullable affects downstream assumptions.",
            ))
        if bc.ordinal != cc.ordinal:
            findings.append(DriftFinding(
                severity="info",
                change_type="ordinal_changed",
                column=name,
                detail=f"Ordinal {bc.ordinal} → {cc.ordinal}",
                recommendation="Usually safe unless consumers read by position (which they shouldn't).",
            ))

    return findings


def infer_schema_from_data(path: Path) -> list[Column]:
    """Infer a schema from CSV / JSON data — for generating baselines."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    elif suffix == ".json":
        data = json.loads(path.read_text())
        rows = data if isinstance(data, list) else data.get("data", [])
    else:
        raise ValueError(f"Unsupported format: {suffix}")
    if not rows:
        return []
    cols: list[Column] = []
    for i, col_name in enumerate(rows[0].keys()):
        values = [r.get(col_name) for r in rows]
        nullable = any(v in (None, "", "null") for v in values)
        # type inference
        non_null = [v for v in values if v not in (None, "", "null")]
        col_type = "string"
        if non_null:
            try:
                [int(v) for v in non_null]
                col_type = "integer"
            except (ValueError, TypeError):
                try:
                    [float(v) for v in non_null]
                    col_type = "float"
                except (ValueError, TypeError):
                    if all(str(v).lower() in ("true", "false") for v in non_null):
                        col_type = "boolean"
        cols.append(Column(name=col_name, type=col_type, nullable=nullable, ordinal=i + 1))
    return cols


def render_markdown(findings: list[DriftFinding], min_sev: str) -> str:
    rel = [f for f in findings if SEVERITY_LEVEL[f.severity] >= SEVERITY_LEVEL[min_sev]]
    out = ["# Schema Drift Report", ""]
    out.append(f"_Total drift findings (>= {min_sev}): {len(rel)}_")
    out.append("")
    if not rel:
        out.append("_No drift detected._")
        return "\n".join(out)
    by_sev: dict[str, list[DriftFinding]] = {}
    for f in rel:
        by_sev.setdefault(f.severity, []).append(f)
    for sev in ["critical", "warning", "info"]:
        items = by_sev.get(sev, [])
        if not items:
            continue
        out.append(f"## {sev.upper()} ({len(items)})")
        out.append("")
        out.append("| Change | Column | Detail | Recommendation |")
        out.append("|--------|--------|--------|----------------|")
        for f in items:
            out.append(f"| {f.change_type} | `{f.column}` | {f.detail} | {f.recommendation[:80]} |")
        out.append("")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Detect schema drift between baseline and current schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--baseline", help="Baseline schema JSON")
    p.add_argument("--current", help="Current schema JSON")
    p.add_argument("--snapshot", help="Generate baseline by inferring from this data file (CSV/JSON)")
    p.add_argument("--severity", choices=["info", "warning", "critical"], default="info")
    p.add_argument("--fail-on", choices=["info", "warning", "critical"], default="critical",
                   help="Exit 1 when any finding is at or above this severity (default: critical)")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.snapshot:
        try:
            cols = infer_schema_from_data(Path(args.snapshot))
        except (OSError, ValueError, AttributeError) as e:
            print(f"error: cannot snapshot {args.snapshot}: {e}", file=sys.stderr)
            return 2
        out = json.dumps({"columns": [asdict(c) for c in cols]}, indent=2)
        if args.output:
            Path(args.output).write_text(out)
            print(f"wrote {args.output}", file=sys.stderr)
        else:
            print(out)
        return 0

    if not args.baseline or not args.current:
        print("error: --baseline and --current required (or use --snapshot)", file=sys.stderr)
        return 2

    try:
        baseline = load_schema(Path(args.baseline))
        current = load_schema(Path(args.current))
    except (OSError, ValueError, AttributeError, TypeError) as e:
        print(f"error: cannot load schema: {e}", file=sys.stderr)
        return 2

    findings = diff_schemas(baseline, current)

    if args.format == "json":
        out = json.dumps(
            {
                "baseline_column_count": len(baseline),
                "current_column_count": len(current),
                "findings": [asdict(f) for f in findings],
            },
            indent=2,
        )
    else:
        out = render_markdown(findings, args.severity)

    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    gate = SEVERITY_LEVEL[args.fail_on]
    return 1 if any(SEVERITY_LEVEL[f.severity] >= gate for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
