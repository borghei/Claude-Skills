#!/usr/bin/env python3
"""Check that implementation tickets are thin end-to-end tracer-bullet slices.

Reads the same decision map JSON as decision_map_validator.py and inspects only
tickets with kind "implementation". A tracer-bullet slice cuts through every layer
it needs (for example schema, service, API, UI, tests), ends in something a
person can demo or verify, and carries testable acceptance criteria. The one
sanctioned exception is a wide mechanical refactor sequenced as
expand -> migrate -> contract, whose tickets are checked for correct ordering
instead of layer coverage. Deterministic, stdlib only, no network.

Usage:
    python3 tracer_slice_checker.py --input assets/sample_decision_map_clean.json
    python3 tracer_slice_checker.py --input map.json --max-days 3 --format json

Exit codes: 0 no error findings, 1 at least one error finding, 2 bad input.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

REFACTOR_PHASES = {"expand", "migrate", "contract"}
VAGUE_TERMS = ("works", "working", "properly", "correctly", "as expected", "should be fine",
               "is good", "looks good", "etc", "and so on", "handles everything", "robust")
HORIZONTAL_TITLE = re.compile(
    r"^(build|create|set ?up|add|write|implement|design)\s+(the\s+)?"
    r"(database|db|schema|tables?|backend|api|endpoints?|frontend|ui|screens?|tests?|models?)\b",
    re.IGNORECASE)
STALE_REF = re.compile(r"(\b[\w./-]+\.(py|ts|tsx|js|go|rb|java|sql|kt|swift)\b)|(\bline\s+\d+\b)", re.IGNORECASE)


class InputError(Exception):
    """Raised when the input file cannot be used."""


def load_tickets(path: Path) -> List[Dict[str, Any]]:
    """Load a map (object with 'tickets') or a bare ticket list; return implementation tickets."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise InputError(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        raise InputError(f"{path.name} is not valid JSON: {exc}")
    tickets = data.get("tickets") if isinstance(data, dict) else data
    if not isinstance(tickets, list) or not all(isinstance(t, dict) for t in tickets):
        raise InputError("expected a map object with a 'tickets' list, or a list of ticket objects")
    return [t for t in tickets if t.get("kind") == "implementation"]


def finding(sev: str, ticket: str, msg: str) -> Dict[str, str]:
    """Build one finding record."""
    return {"severity": sev, "ticket": ticket, "message": msg}


def check_slice(t: Dict[str, Any], min_layers: int, max_days: float) -> List[Dict[str, str]]:
    """Check one non-refactor ticket for vertical depth, demo, criteria and size."""
    out: List[Dict[str, str]] = []
    tid = str(t.get("id", "?"))
    layers = [str(x).strip().lower() for x in t.get("layers", []) or [] if str(x).strip()]
    if len(set(layers)) < min_layers:
        out.append(finding("error", tid, f"touches {len(set(layers))} layer(s) {sorted(set(layers))}; a tracer "
                                         f"bullet crosses at least {min_layers} — this is a horizontal slice"))
    if HORIZONTAL_TITLE.search(str(t.get("title", ""))):
        out.append(finding("warn", tid, f"title names a layer, not a behaviour: {t.get('title')!r}"))
    if not str(t.get("demo", "")).strip():
        out.append(finding("error", tid, "no demo statement — say what a person can see or run when it lands"))
    out.extend(check_criteria(t))
    days = t.get("estimate_days")
    if isinstance(days, (int, float)) and days > max_days:
        out.append(finding("warn", tid, f"estimated {days} days (> {max_days}); split into thinner slices"))
    return out


def check_criteria(t: Dict[str, Any]) -> List[Dict[str, str]]:
    """Check acceptance criteria exist, are testable, and avoid stale file references."""
    out: List[Dict[str, str]] = []
    tid = str(t.get("id", "?"))
    criteria = [str(c).strip() for c in t.get("acceptance_criteria", []) or [] if str(c).strip()]
    if not criteria:
        return [finding("error", tid, "no acceptance criteria — nobody can tell when it is done")]
    for crit in criteria:
        low = crit.lower()
        hit = next((v for v in VAGUE_TERMS if re.search(r"\b" + re.escape(v) + r"\b", low)), None)
        if hit:
            out.append(finding("warn", tid, f"criterion not testable ('{hit}'): {crit!r}"))
    text = " ".join([str(t.get("description", ""))] + criteria)
    if STALE_REF.search(text):
        out.append(finding("warn", tid, "mentions file paths or line numbers — describe behaviour, paths go stale"))
    return out


def check_refactor_groups(tickets: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Check expand -> migrate -> contract ordering inside each refactor group."""
    out: List[Dict[str, str]] = []
    groups: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for t in tickets:
        phase = t.get("pattern")
        if phase in REFACTOR_PHASES:
            group = str(t.get("refactor_group", "")).strip()
            if not group:
                out.append(finding("error", str(t.get("id")), f"{phase} ticket has no refactor_group"))
                continue
            groups.setdefault(group, {p: [] for p in REFACTOR_PHASES})[phase].append(t)
    for group, phases in sorted(groups.items()):
        expands = {str(t["id"]) for t in phases["expand"]}
        migrates = {str(t["id"]) for t in phases["migrate"]}
        if len(expands) != 1:
            out.append(finding("error", group, f"refactor group needs exactly one expand ticket, has {len(expands)}"))
        if not migrates:
            out.append(finding("warn", group, "refactor group has no migrate batches"))
        for t in phases["migrate"]:
            if not expands & set(t.get("blocked_by", []) or []):
                out.append(finding("error", str(t["id"]), "migrate batch is not blocked by the expand ticket — "
                                                           "callers would break before the new form exists"))
        for t in phases["contract"]:
            missing = migrates - set(t.get("blocked_by", []) or [])
            if missing:
                out.append(finding("error", str(t["id"]), "contract can run before migrate batch(es) "
                                                           f"{sorted(missing)} — the old form would vanish under live callers"))
        if not phases["contract"]:
            out.append(finding("warn", group, "refactor group has no contract ticket — the old form will linger"))
        for t in phases["expand"] + phases["migrate"] + phases["contract"]:
            out.extend(check_criteria(t))
    return out


def analyse(tickets: List[Dict[str, Any]], min_layers: int, max_days: float) -> Dict[str, Any]:
    """Check every implementation ticket and summarise the slicing quality."""
    findings: List[Dict[str, str]] = []
    vertical = 0
    for t in sorted(tickets, key=lambda x: str(x.get("id", ""))):
        if t.get("pattern") in REFACTOR_PHASES:
            continue
        own = check_slice(t, min_layers, max_days)
        if not any(f["severity"] == "error" for f in own):
            vertical += 1
        findings.extend(own)
    findings.extend(check_refactor_groups(tickets))
    findings.sort(key=lambda f: (0 if f["severity"] == "error" else 1, f["ticket"], f["message"]))
    errors = sum(1 for f in findings if f["severity"] == "error")
    slices = sum(1 for t in tickets if t.get("pattern") not in REFACTOR_PHASES)
    return {
        "implementation_tickets": len(tickets), "slices": slices, "vertical_slices": vertical,
        "refactor_tickets": len(tickets) - slices, "findings": findings,
        "errors": errors, "warnings": len(findings) - errors, "passed": errors == 0,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print("Tracer-bullet slice check")
    print(f"Implementation tickets: {report['implementation_tickets']}  "
          f"(slices {report['slices']}, clean vertical {report['vertical_slices']}, "
          f"refactor phases {report['refactor_tickets']})")
    print(f"Findings: {report['errors']} error(s), {report['warnings']} warning(s)")
    for f in report["findings"]:
        print(f"  [{f['severity']:5}] {f['ticket']:<10} {f['message']}")
    if not report["implementation_tickets"]:
        print("  (no implementation tickets yet — convert resolved decisions first)")
    print("\nRESULT: " + ("PASS" if report["passed"] else "FAIL — reslice before handing tickets out"))


def main() -> None:
    """Parse arguments, check the slices, print the report, exit by contract."""
    parser = argparse.ArgumentParser(description="Check implementation tickets are vertical tracer-bullet slices.")
    parser.add_argument("--input", required=True, help="decision map JSON (or a JSON list of tickets)")
    parser.add_argument("--min-layers", type=int, default=2, help="layers a slice must cross (default: 2)")
    parser.add_argument("--max-days", type=float, default=3.0, help="warn above this estimate (default: 3)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    if args.min_layers < 1 or args.max_days <= 0:
        print("error: --min-layers must be >= 1 and --max-days > 0", file=sys.stderr)
        sys.exit(2)
    try:
        report = analyse(load_tickets(Path(args.input)), args.min_layers, args.max_days)
    except (InputError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
