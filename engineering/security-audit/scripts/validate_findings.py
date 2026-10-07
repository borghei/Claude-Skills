#!/usr/bin/env python3
"""Validate an audit run's findings.json before it is reported.

Checks the document against assets/findings.schema.json, then enforces the
rules a schema cannot express: fingerprint ordering and uniqueness, safe
repository-relative paths, trace shape, the severity ceiling, and a usable
resolution plan on every unresolved lead.

Exit codes: 0 valid, 1 invalid, 2 unreadable input or usage error.

Usage:
    python3 validate_findings.py findings.json
    python3 validate_findings.py findings.json --format json
    python3 validate_findings.py findings.json --schema custom.schema.json
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (  # noqa: E402
    SEVERITIES, AuditInputError, emit, is_repo_path, is_text, load_json)

TYPES = {"object": dict, "array": list, "string": str, "integer": int,
         "boolean": bool}


def default_schema() -> Path:
    """Path of the schema shipped with the skill."""
    return Path(__file__).resolve().parent.parent / "assets" / "findings.schema.json"


def resolve(node: Dict[str, Any], root: Dict[str, Any]) -> Dict[str, Any]:
    """Follow a local `#/$defs/name` reference."""
    ref = node.get("$ref")
    if not ref:
        return node
    return root.get("$defs", {}).get(ref.rsplit("/", 1)[-1], {})


def pick_branch(value: Any, branches: List[Dict[str, Any]],
                root: Dict[str, Any], where: str, errors: List[str]) -> None:
    """Validate against the branch whose verdict matches the record."""
    verdict = value.get("verdict") if isinstance(value, dict) else None
    known = []
    for branch in branches:
        schema = resolve(branch, root)
        const = schema.get("properties", {}).get("verdict", {}).get("const")
        known.append(const)
        if const == verdict:
            check(value, schema, root, where, errors)
            return
    errors.append(f"{where}.verdict: expected one of {known}, got {verdict!r}")


def check(value: Any, node: Dict[str, Any], root: Dict[str, Any],
          where: str, errors: List[str]) -> None:
    """Validate a value against the schema subset this skill uses."""
    schema = resolve(node, root)
    if "oneOf" in schema:
        pick_branch(value, schema["oneOf"], root, where, errors)
        return
    expected = schema.get("type")
    if expected:
        kind = TYPES[expected]
        if not isinstance(value, kind) or (expected == "integer"
                                           and isinstance(value, bool)):
            errors.append(f"{where}: expected {expected}, got {type(value).__name__}")
            return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{where}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{where}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, str):
        if schema.get("minLength") and not is_text(value):
            errors.append(f"{where}: must contain visible text")
        if "pattern" in schema and not re.match(schema["pattern"], value):
            errors.append(f"{where}: does not match {schema['pattern']}")
    if isinstance(value, int) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{where}: must be at least {schema['minimum']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{where}: needs at least {schema['minItems']} item(s)")
        for index, item in enumerate(value):
            check(item, schema.get("items", {}), root, f"{where}[{index}]", errors)
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                errors.append(f"{where}: missing required field {name!r}")
        for name, item in value.items():
            if name in props:
                check(item, props[name], root, f"{where}.{name}", errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{where}: field {name!r} is not allowed here")


def check_trace(record: Dict[str, Any], where: str, errors: List[str]) -> None:
    """A trace starts at an entry, ends at a sink, and flows in between."""
    trace = record.get("trace")
    if not isinstance(trace, list) or not trace:
        return
    steps = [step.get("step") if isinstance(step, dict) else None for step in trace]
    if len(steps) == 1:
        if steps[0] not in ("entry", "sink"):
            errors.append(f"{where}.trace[0].step: a one-step trace is 'entry' or 'sink'")
        return
    if steps[0] != "entry":
        errors.append(f"{where}.trace[0].step: must be 'entry'")
    if steps[-1] != "sink":
        errors.append(f"{where}.trace[{len(steps) - 1}].step: must be 'sink'")
    for index, step in enumerate(steps[1:-1], start=1):
        if step != "flow":
            errors.append(f"{where}.trace[{index}].step: must be 'flow'")


def check_paths(record: Dict[str, Any], where: str, errors: List[str]) -> None:
    """Every cited file must be a path inside the repository."""
    groups = [("trace", record.get("trace")), ("evidence", record.get("evidence"))]
    fix = record.get("fix")
    if isinstance(fix, dict):
        groups.append(("fix.changes", fix.get("changes")))
    for name, entries in groups:
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if isinstance(entry, dict) and "file" in entry \
                    and not is_repo_path(entry["file"]):
                errors.append(f"{where}.{name}[{index}].file: must be a "
                              "repository-relative path with no '..' or leading '/'")


def check_confirmed(record: Dict[str, Any], where: str, errors: List[str]) -> None:
    """Severity may not outrun what the reproduction demonstrated."""
    severity = record.get("severity")
    if not isinstance(severity, dict):
        return
    overall = severity.get("overall")
    impact = (severity.get("impact") or {}).get("level") \
        if isinstance(severity.get("impact"), dict) else None
    if overall in SEVERITIES and impact in SEVERITIES \
            and SEVERITIES.index(overall) > SEVERITIES.index(impact):
        errors.append(f"{where}.severity.overall: {overall!r} exceeds "
                      f"demonstrated impact {impact!r}")
    confidence = record.get("confidence")
    level = confidence.get("level") if isinstance(confidence, dict) else None
    if overall in ("high", "critical") and level == "low":
        errors.append(f"{where}.confidence.level: a {overall} finding held with "
                      "low confidence is an unresolved lead; record it as "
                      "needs_validation or lower the severity")


def check_semantics(findings: List[Any], errors: List[str]) -> None:
    """Rules that span records or depend on the verdict."""
    seen: Dict[str, int] = {}
    previous = None
    for index, record in enumerate(findings):
        if not isinstance(record, dict):
            continue
        where = f"findings[{index}]"
        fingerprint = record.get("fingerprint")
        if isinstance(fingerprint, str):
            if fingerprint in seen:
                errors.append(f"{where}.fingerprint: duplicates findings"
                              f"[{seen[fingerprint]}]; one record per root cause")
            seen.setdefault(fingerprint, index)
            if previous is not None and fingerprint < previous:
                errors.append(f"{where}.fingerprint: records must be sorted "
                              "by fingerprint")
            previous = fingerprint
        check_trace(record, where, errors)
        check_paths(record, where, errors)
        verdict = record.get("verdict")
        if verdict == "confirmed":
            check_confirmed(record, where, errors)
        elif verdict == "needs_validation":
            plan = record.get("resolution")
            if isinstance(plan, dict) and not (is_text(plan.get("local"))
                                               or is_text(plan.get("owner_check"))):
                errors.append(f"{where}.resolution: give a 'local' check, an "
                              "'owner_check', or both")


def validate(document: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Run every check and return a report with errors and verdict counts."""
    errors: List[str] = []
    check(document, schema, schema, "$", errors)
    findings = document.get("findings") if isinstance(document, dict) else None
    stats: Dict[str, int] = {}
    if isinstance(findings, list):
        check_semantics(findings, errors)
        for record in findings:
            verdict = record.get("verdict") if isinstance(record, dict) else None
            if isinstance(verdict, str):
                stats[verdict] = stats.get(verdict, 0) + 1
        stats["total"] = len(findings)
    return {"valid": not errors, "error_count": len(errors), "errors": errors,
            "stats": stats}


def main() -> None:
    """Parse arguments, validate the findings file, and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Validate findings.json from a security audit run.")
    parser.add_argument("findings", type=Path, help="path to findings.json")
    parser.add_argument("--schema", type=Path, default=default_schema(),
                        help="schema file (default: the skill's findings.schema.json)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args()
    try:
        schema = load_json(args.schema)
        document = load_json(args.findings)
    except AuditInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    report = validate(document, schema)
    report["file"] = str(args.findings)
    emit(report, args.format)
    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
