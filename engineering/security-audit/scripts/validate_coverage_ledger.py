#!/usr/bin/env python3
"""Validate an audit run's coverage-ledger.json.

The ledger is the audit's coverage claim, so it is checked after seeding and
after every update: deterministic unit IDs, sort order, the per-status state
table, owned evidence, resolvable attack-class blocks, and reopened-attempt
archives. Optional inputs tighten the check: run metadata confines companion
blocks to the selected breadth tier, findings are cross-linked by fingerprint,
and --final refuses a ledger that still has unassigned or running work.

Exit codes: 0 valid, 1 invalid, 2 unreadable input or usage error.

Usage:
    python3 validate_coverage_ledger.py coverage-ledger.json
    python3 validate_coverage_ledger.py coverage-ledger.json \
        --metadata run-metadata.json --findings findings.json \
        --run-dir . --final --format json
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (  # noqa: E402
    AuditInputError, emit, is_text, load_block_index, load_json, references_dir)
from ledger_rules import check_unit  # noqa: E402

MAX_UNITS = 5000


def check_order(units: List[Any], errors: List[str]) -> None:
    """Units are sorted by coverage ID and each ID appears once."""
    seen: Dict[str, int] = {}
    previous: Optional[str] = None
    for index, unit in enumerate(units):
        identifier = unit.get("coverage_id") if isinstance(unit, dict) else None
        if not isinstance(identifier, str):
            continue
        if identifier in seen:
            errors.append(f"units[{index}].coverage_id: duplicates units"
                          f"[{seen[identifier]}]; the same refs describe one unit")
        seen.setdefault(identifier, index)
        if previous is not None and identifier < previous:
            errors.append(f"units[{index}].coverage_id: units must be sorted "
                          "by coverage_id")
        previous = identifier


def live_fingerprints(units: List[Any], status: Optional[str] = None) -> Set[str]:
    """Fingerprints linked from live unit state, optionally for one status."""
    found: Set[str] = set()
    for unit in units:
        if not isinstance(unit, dict):
            continue
        if status is not None and unit.get("status") != status:
            continue
        values = unit.get("fingerprints")
        if isinstance(values, list):
            found |= {value for value in values if isinstance(value, str)}
    return found


def check_findings(units: List[Any], findings_doc: Any, final: bool,
                   incomplete: bool, errors: List[str],
                   stats: Dict[str, Any]) -> None:
    """Every record links to a unit, and every candidate reaches a verdict."""
    records = findings_doc.get("findings") if isinstance(findings_doc, dict) else None
    if not isinstance(records, list):
        errors.append("findings: expected an object with a 'findings' array")
        return
    recorded = {record.get("fingerprint") for record in records
                if isinstance(record, dict)}
    linked = live_fingerprints(units)
    for fingerprint in sorted(str(value) for value in recorded - linked):
        errors.append(f"findings: {fingerprint!r} is not linked from any "
                      "coverage unit")
    pending = sorted(live_fingerprints(units, "candidate") - recorded)
    stats["unvalidated_candidates"] = len(pending)
    if final and pending and not incomplete:
        for fingerprint in pending:
            errors.append(f"ledger: candidate {fingerprint!r} has no final "
                          "record; validate it or mark the run incomplete")


def check_run_ids(ledger: Dict[str, Any], metadata: Any, findings_doc: Any,
                  errors: List[str]) -> None:
    """All shared files of a run carry the same run ID."""
    run_id = ledger.get("run_id")
    for name, document in (("metadata", metadata), ("findings", findings_doc)):
        if isinstance(document, dict) and document.get("run_id") != run_id:
            errors.append(f"{name}.run_id: {document.get('run_id')!r} does not "
                          f"match the ledger run_id {run_id!r}")


def validate(ledger: Any, ctx: Dict[str, Any], metadata: Any = None,
             findings_doc: Any = None, final: bool = False) -> Dict[str, Any]:
    """Run every ledger rule and return a report with status counts."""
    errors: List[str] = []
    stats: Dict[str, Any] = {}
    if not isinstance(ledger, dict) or not isinstance(ledger.get("units"), list):
        return {"valid": False, "error_count": 1, "stats": stats, "errors": [
            "$: expected an object with schema_version, run_id, and a 'units' array"]}
    if ledger.get("schema_version") != 1:
        errors.append("$.schema_version: must equal 1")
    if not is_text(ledger.get("run_id")):
        errors.append("$.run_id: must contain visible text")
    units = ledger["units"]
    if len(units) > MAX_UNITS:
        errors.append(f"$.units: {len(units)} units exceeds the {MAX_UNITS} limit; "
                      "split the audit into scoped runs")
        units = units[:MAX_UNITS]
    for index, unit in enumerate(units):
        errors += check_unit(unit, index, ctx)
    check_order(units, errors)
    for unit in units:
        status = unit.get("status") if isinstance(unit, dict) else None
        if isinstance(status, str):
            stats[status] = stats.get(status, 0) + 1
    stats["total"] = len(units)
    incomplete = isinstance(metadata, dict) and metadata.get("run_status") == "incomplete"
    check_run_ids(ledger, metadata, findings_doc, errors)
    if findings_doc is not None:
        check_findings(units, findings_doc, final, incomplete, errors, stats)
    if final:
        open_work = stats.get("planned", 0) + stats.get("in_progress", 0)
        if open_work:
            errors.append(f"ledger: {open_work} unit(s) are still planned or "
                          "in_progress; finish them or mark them deferred "
                          "with a reason")
    return {"valid": not errors, "error_count": len(errors), "errors": errors,
            "stats": stats}


def build_context(args: argparse.Namespace, metadata: Any) -> Dict[str, Any]:
    """Assemble the optional checks requested on the command line."""
    ctx: Dict[str, Any] = {"run_dir": args.run_dir, "block_index": None,
                           "companions": None}
    if not args.no_resolve_blocks:
        index = load_block_index(args.references)
        if not index:
            raise AuditInputError(
                f"no reference files in {args.references}; pass --references "
                "or --no-resolve-blocks")
        ctx["block_index"] = index
    if isinstance(metadata, dict) and isinstance(metadata.get("companions"), list):
        ctx["companions"] = metadata["companions"]
    return ctx


def main() -> None:
    """Parse arguments, validate the ledger, and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Validate coverage-ledger.json from a security audit run.")
    parser.add_argument("ledger", type=Path, help="path to coverage-ledger.json")
    parser.add_argument("--metadata", type=Path,
                        help="run-metadata.json; confines companion blocks to "
                             "the run's selected companions")
    parser.add_argument("--findings", type=Path,
                        help="findings.json; cross-links records and units")
    parser.add_argument("--run-dir", type=Path,
                        help="run directory; verifies promoted evidence files exist")
    parser.add_argument("--references", type=Path, default=references_dir(),
                        help="directory holding the attack-class reference files")
    parser.add_argument("--no-resolve-blocks", action="store_true",
                        help="skip checking block references against headings")
    parser.add_argument("--final", action="store_true",
                        help="pre-report gate: no open work, every candidate decided")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args()
    try:
        ledger = load_json(args.ledger)
        metadata = load_json(args.metadata) if args.metadata else None
        findings_doc = load_json(args.findings) if args.findings else None
        ctx = build_context(args, metadata)
    except AuditInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    report = validate(ledger, ctx, metadata, findings_doc, args.final)
    report["file"] = str(args.ledger)
    emit(report, args.format)
    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
