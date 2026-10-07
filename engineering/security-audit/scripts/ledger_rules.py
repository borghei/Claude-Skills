#!/usr/bin/env python3
"""Unit-level rules behind the coverage-ledger validator.

A coverage unit is one (surface, boundary, subsystem, attack class) cell of
the audit plan. This module holds the state table every unit must obey, the
evidence rules for its checks, and the archive rules for reopened attempts.
Run it directly to print the state table.

Usage:
    python3 ledger_rules.py
    python3 ledger_rules.py --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (  # noqa: E402
    CORE_FILE, ORIGINS, REF_KEYS, UNIT_STATUSES, coverage_id, is_agent_id,
    is_fingerprint, is_repo_path, is_text, parse_block)

# status -> (owner, reviewed_paths + checks, fingerprints, unresolved)
STATE_TABLE: Dict[str, tuple] = {
    "planned": ("none", "empty", "empty", "empty"),
    "in_progress": ("set", "empty", "empty", "empty"),
    "covered": ("set", "filled", "empty", "empty"),
    "candidate": ("set", "filled", "filled", "any"),
    "blocked": ("set", "filled", "empty", "filled"),
    "deferred": ("none", "empty", "empty", "filled"),
    "out_of_scope": ("none", "empty", "empty", "filled"),
    "not_applicable": ("none", "empty", "empty", "filled"),
}
ARCHIVABLE = ("covered", "candidate", "blocked")
UNIT_FIELDS = ["coverage_id", "refs", "label", "starting_paths", "class_blocks",
               "excluded_blocks", "origin", "wave", "status", "owner",
               "reviewed_paths", "checks", "fingerprints", "unresolved",
               "attempts"]
ATTEMPT_FIELDS = ["wave", "status", "owner", "reviewed_paths", "checks",
                  "fingerprints", "unresolved", "reopen_reason"]


def _fill(errors: List[str], base: str, name: str, value: Any, rule: str) -> None:
    """Apply an empty / filled / any rule to one list field."""
    if not isinstance(value, list):
        errors.append(f"{base}.{name}: expected an array")
    elif rule == "empty" and value:
        errors.append(f"{base}.{name}: must be empty for this status")
    elif rule == "filled" and not value:
        errors.append(f"{base}.{name}: must not be empty for this status")


def check_state(record: Dict[str, Any], base: str) -> List[str]:
    """Enforce the state table on a live unit or an archived attempt."""
    errors: List[str] = []
    status = record.get("status")
    if not isinstance(status, str) or status not in STATE_TABLE:
        return [f"{base}.status: {status!r} is not one of {UNIT_STATUSES}"]
    owner_rule, evidence_rule, print_rule, open_rule = STATE_TABLE[status]
    owner = record.get("owner")
    if owner_rule == "none" and owner is not None:
        errors.append(f"{base}.owner: a {status} unit has no owner")
    if owner_rule == "set" and not is_agent_id(owner):
        errors.append(f"{base}.owner: a {status} unit needs a lowercase agent ID")
    _fill(errors, base, "reviewed_paths", record.get("reviewed_paths"), evidence_rule)
    _fill(errors, base, "checks", record.get("checks"), evidence_rule)
    _fill(errors, base, "fingerprints", record.get("fingerprints"), print_rule)
    _fill(errors, base, "unresolved", record.get("unresolved"), open_rule)
    return errors


def check_evidence(record: Dict[str, Any], base: str,
                   run_dir: Optional[Path]) -> List[str]:
    """Validate checks, their evidence files, and the reviewed-path union."""
    errors: List[str] = []
    owned: Set[str] = set()
    checks = record.get("checks") if isinstance(record.get("checks"), list) else []
    for index, item in enumerate(checks):
        where = f"{base}.checks[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: expected an object")
            continue
        agent = item.get("agent_id")
        if not is_agent_id(agent):
            errors.append(f"{where}.agent_id: expected a lowercase agent ID")
        for name in ("invariant", "result"):
            if not is_text(item.get(name)):
                errors.append(f"{where}.{name}: must contain visible text")
        paths = item.get("reviewed_paths")
        if not isinstance(paths, list) or not paths:
            errors.append(f"{where}.reviewed_paths: must not be empty")
        else:
            for path in paths:
                if is_repo_path(path):
                    owned.add(path)
                else:
                    errors.append(f"{where}.reviewed_paths: {path!r} is not a "
                                  "repository-relative path")
        method, evidence = item.get("method"), item.get("evidence_file")
        if method == "source":
            if evidence is not None:
                errors.append(f"{where}.evidence_file: a source check uses null")
        elif method == "local":
            prefix = f"agents/{agent}/evidence/"
            if not (is_repo_path(evidence) and str(evidence).startswith(prefix)
                    and len(str(evidence)) > len(prefix)):
                errors.append(f"{where}.evidence_file: a local check needs a "
                              f"promoted file under {prefix}")
            elif run_dir is not None:
                target = run_dir / str(evidence)
                if target.is_symlink() or not target.is_file():
                    errors.append(f"{where}.evidence_file: {evidence} is not a "
                                  "regular file in the run directory")
        else:
            errors.append(f"{where}.method: expected 'source' or 'local'")
    listed = record.get("reviewed_paths")
    if isinstance(listed, list):
        for path in listed:
            if not is_repo_path(path):
                errors.append(f"{base}.reviewed_paths: {path!r} is not a "
                              "repository-relative path")
        if set(p for p in listed if isinstance(p, str)) != owned:
            errors.append(f"{base}.reviewed_paths: must equal the union of the "
                          "paths owned by its checks")
    for name, test in (("fingerprints", is_fingerprint), ("unresolved", is_text)):
        values = record.get(name) if isinstance(record.get(name), list) else []
        for value in values:
            if not test(value):
                errors.append(f"{base}.{name}: invalid entry {value!r}")
        if len(set(map(str, values))) != len(values):
            errors.append(f"{base}.{name}: entries must be unique")
    return errors


def check_blocks(unit: Dict[str, Any], base: str, ctx: Dict[str, Any]) -> List[str]:
    """Validate the class blocks a hunter is given and those ruled out."""
    errors: List[str] = []
    index: Optional[Dict[str, Set[str]]] = ctx.get("block_index")
    allowed: Optional[List[str]] = ctx.get("companions")
    selected = unit.get("class_blocks")
    if not isinstance(selected, list) or not selected:
        return [f"{base}.class_blocks: list at least the primary attack-class block"]
    refs = unit.get("refs") if isinstance(unit.get("refs"), dict) else {}
    if refs.get("attack_class") not in selected:
        errors.append(f"{base}.class_blocks: must include refs.attack_class")
    excluded = unit.get("excluded_blocks")
    excluded = excluded if isinstance(excluded, list) else []
    ruled_out = []
    for position, entry in enumerate(excluded):
        if not isinstance(entry, dict) or not is_text(entry.get("reason")):
            errors.append(f"{base}.excluded_blocks[{position}]: needs a block "
                          "and a reason")
            continue
        ruled_out.append(entry.get("block"))
    for block in ruled_out:
        if block in selected:
            errors.append(f"{base}.excluded_blocks: {block!r} is also selected")
    if len(set(map(str, selected))) != len(selected):
        errors.append(f"{base}.class_blocks: entries must be unique")
    for block in list(selected) + ruled_out:
        parsed = parse_block(block)
        if not parsed:
            errors.append(f"{base}: {block!r} is not a 'file.md#Heading' block")
            continue
        name, heading = parsed
        if index is not None and heading not in index.get(name, set()):
            errors.append(f"{base}: block {block!r} does not match a heading "
                          f"in references/{name}")
        if allowed is not None and block in selected \
                and name != CORE_FILE and name not in allowed:
            errors.append(f"{base}.class_blocks: {name} is outside the "
                          "companions selected for this run")
    return errors


def check_attempts(unit: Dict[str, Any], base: str,
                   run_dir: Optional[Path]) -> List[str]:
    """Archived attempts keep their own owner and evidence, in wave order."""
    errors: List[str] = []
    attempts = unit.get("attempts")
    if not isinstance(attempts, list):
        return [f"{base}.attempts: expected an array"]
    live_wave = unit.get("wave") if isinstance(unit.get("wave"), int) else 0
    owners: Set[str] = set()
    files: Set[str] = set()
    last_wave = 0
    for position, attempt in enumerate(attempts):
        where = f"{base}.attempts[{position}]"
        if not isinstance(attempt, dict):
            errors.append(f"{where}: expected an object")
            continue
        missing = [name for name in ATTEMPT_FIELDS if name not in attempt]
        if missing:
            errors.append(f"{where}: missing {missing}")
            continue
        if not isinstance(attempt["checks"], list) \
                or not isinstance(attempt["owner"], (str, type(None))):
            errors.append(f"{where}: 'checks' must be an array and 'owner' a string")
            continue
        if attempt["status"] not in ARCHIVABLE:
            errors.append(f"{where}.status: only {list(ARCHIVABLE)} can be archived")
            continue
        errors += check_state(attempt, where) + check_evidence(attempt, where, run_dir)
        wave = attempt["wave"]
        if not isinstance(wave, int) or isinstance(wave, bool) \
                or wave <= last_wave or wave >= live_wave:
            errors.append(f"{where}.wave: waves increase and stay below the "
                          f"live wave {live_wave}")
        else:
            last_wave = wave
        if not is_text(attempt["reopen_reason"]):
            errors.append(f"{where}.reopen_reason: say why the unit was reopened")
        if attempt["owner"] in owners:
            errors.append(f"{where}.owner: each attempt needs a fresh owner")
        owners.add(str(attempt["owner"]))
        files |= {str(c.get("evidence_file")) for c in attempt["checks"]
                  if isinstance(c, dict) and c.get("evidence_file")}
    if isinstance(unit.get("owner"), str) and unit.get("owner") in owners:
        errors.append(f"{base}.owner: a reopened unit needs a fresh owner")
    live = unit.get("checks") if isinstance(unit.get("checks"), list) else []
    for item in live:
        if isinstance(item, dict) and (str(item.get("agent_id")) in owners
                                       or str(item.get("evidence_file")) in files):
            errors.append(f"{base}.checks: evidence from an archived attempt "
                          "cannot be reused in the live state")
    return errors


def check_unit(unit: Any, index: int, ctx: Dict[str, Any]) -> List[str]:
    """Run every rule against one coverage unit."""
    base = f"units[{index}]"
    if not isinstance(unit, dict):
        return [f"{base}: expected an object"]
    missing = [name for name in UNIT_FIELDS if name not in unit]
    if missing:
        return [f"{base}: missing {missing}"]
    errors: List[str] = []
    refs = unit["refs"]
    if not isinstance(refs, dict) or set(refs) - set(REF_KEYS + ["lifecycle"]) \
            or any(not is_text(refs.get(key)) for key in REF_KEYS) \
            or ("lifecycle" in refs and not is_text(refs["lifecycle"])):
        errors.append(f"{base}.refs: needs text for {REF_KEYS} and, optionally, "
                      "lifecycle; no other keys")
    elif unit["coverage_id"] != coverage_id(refs):
        errors.append(f"{base}.coverage_id: expected {coverage_id(refs)} for "
                      "these refs")
    if not is_text(unit["label"]):
        errors.append(f"{base}.label: must contain visible text")
    paths = unit["starting_paths"]
    if not isinstance(paths, list) or not paths \
            or any(not is_repo_path(path) for path in paths):
        errors.append(f"{base}.starting_paths: list repository-relative paths")
    if unit["origin"] not in ORIGINS:
        errors.append(f"{base}.origin: {unit['origin']!r} is not one of {ORIGINS}")
    wave = unit["wave"]
    if not isinstance(wave, int) or isinstance(wave, bool) or wave < 1:
        errors.append(f"{base}.wave: expected a positive integer")
    run_dir = ctx.get("run_dir")
    errors += check_state(unit, base) + check_evidence(unit, base, run_dir)
    errors += check_blocks(unit, base, ctx) + check_attempts(unit, base, run_dir)
    return errors


def main() -> None:
    """Print the unit state table."""
    parser = argparse.ArgumentParser(
        description="Print the state table every coverage unit must obey.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args()
    columns = ["owner", "reviewed_paths_and_checks", "fingerprints", "unresolved"]
    if args.format == "json":
        print(json.dumps({status: dict(zip(columns, rule))
                          for status, rule in STATE_TABLE.items()}, indent=2))
        return
    print(f"{'status':<16}" + "".join(f"{name:<28}" for name in columns))
    for status, rule in STATE_TABLE.items():
        print(f"{status:<16}" + "".join(f"{cell:<28}" for cell in rule))


if __name__ == "__main__":
    main()
