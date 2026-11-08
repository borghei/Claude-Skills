#!/usr/bin/env python3
"""Compare two or more candidate interfaces for the same module and recommend one.

Each design lists its entry points (parameters, error modes, ordering rules),
configuration knobs, the responsibilities it hides, the responsibilities it
leaves to callers, the calls the most common caller needs, and its seams with
their adapters. The tool computes interface cost, depth (hidden responsibilities
per unit of interface), caller burden and a combined score, then checks the
rules a design must satisfy: every required responsibility is placed, every
seam has two or more adapters, and the designs are genuinely different.

Usage:
  python3 interface_compare.py --input designs.json
  python3 interface_compare.py --input designs.json --format json

Exit codes: 0 all designs valid, 1 rule violations found, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def as_count(value: Any) -> int:
    """Interpret a list or a number as a count."""
    if isinstance(value, list):
        return len(value)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def interface_cost(design: Dict[str, Any]) -> float:
    """Everything a caller must learn: entry points, params, error modes, ordering rules, knobs."""
    cost = 0.0
    for ep in design.get("entry_points", []):
        cost += 1 + as_count(ep.get("params")) + 0.5 * as_count(ep.get("errors"))
        cost += 2 * as_count(ep.get("ordering"))
    return cost + as_count(design.get("config_knobs"))


def evaluate(design: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    """Score one design and collect its rule violations."""
    name = str(design.get("name", "unnamed"))
    hides = [str(h) for h in design.get("hides", [])]
    leaks = [str(h) for h in design.get("leaks", [])]
    cost = interface_cost(design)
    depth = round(len(hides) / cost, 2) if cost else 0.0
    burden = 3 * len(leaks) + as_count(design.get("common_case_calls"))
    score = round(depth * 10 - burden, 2)
    problems: List[str] = []
    notes: List[str] = []
    placed = {r.lower() for r in hides + leaks}
    for req in required:
        if req.lower() not in placed:
            problems.append(f"responsibility '{req}' is neither hidden nor handed to callers")
    for dup in sorted({h for h in hides if h in leaks}):
        problems.append(f"'{dup}' is listed as both hidden and leaked")
    for seam, adapters in (design.get("seams") or {}).items():
        if as_count(adapters) < 2:
            problems.append(f"seam '{seam}' has {as_count(adapters)} adapter(s); a seam with one adapter is "
                            f"indirection, not a seam")
    if not design.get("entry_points"):
        problems.append("no entry points described")
    for ep in design.get("entry_points", []):
        if as_count(ep.get("params")) > 5:
            notes.append(f"{ep.get('name')}: {as_count(ep.get('params'))} parameters; consider a single "
                         f"request object or splitting responsibilities")
        if as_count(ep.get("ordering")):
            rules = ep.get("ordering")
            rules = "; ".join(map(str, rules)) if isinstance(rules, list) else str(rules)
            notes.append(f"{ep.get('name')}: ordering rule ({rules}) is something every caller must remember")
    if as_count(design.get("common_case_calls")) > 2:
        notes.append(f"the most common caller needs {as_count(design.get('common_case_calls'))} calls")
    if not design.get("usage_example"):
        notes.append("no usage example; write the common caller's code before judging the design")
    return {"name": name, "entry_points": len(design.get("entry_points", [])), "interface_cost": cost,
            "hidden": len(hides), "leaked": len(leaks), "depth": depth, "caller_burden": burden,
            "score": score, "problems": problems, "notes": notes,
            "signature": sorted(str(ep.get("name")) for ep in design.get("entry_points", []))}


def compare(data: Dict[str, Any], similarity: float) -> Dict[str, Any]:
    """Evaluate all designs, check distinctness, and pick a recommendation."""
    designs = data.get("designs", [])
    required = [str(r) for r in data.get("required_responsibilities", [])]
    results = [evaluate(d, required) for d in designs]
    global_problems: List[str] = []
    if len(results) < 2:
        global_problems.append(f"{len(results)} design(s); compare at least two genuinely different shapes")
    for i, a in enumerate(results):
        for b in results[i + 1:]:
            same_names = a["signature"] == b["signature"]
            close = (abs(a["interface_cost"] - b["interface_cost"]) <= similarity * max(a["interface_cost"], 1)
                     and a["hidden"] == b["hidden"])
            if same_names or close:
                global_problems.append(f"designs '{a['name']}' and '{b['name']}' are near-identical; vary the "
                                       f"constraint (minimal surface, common-caller-first, flexible, port-based)")
    valid = [r for r in results if not r["problems"]]
    ranked = sorted(valid, key=lambda r: (-r["score"], r["interface_cost"], r["name"]))
    pick = ranked[0]["name"] if ranked else None
    runner = ranked[1]["name"] if len(ranked) > 1 else None
    margin = round(ranked[0]["score"] - ranked[1]["score"], 2) if len(ranked) > 1 else None
    errors = len(global_problems) + sum(len(r["problems"]) for r in results)
    return {"module": data.get("module", ""), "designs": results, "global_problems": global_problems,
            "recommendation": pick, "runner_up": runner, "margin": margin,
            "close_call": margin is not None and margin < 1.0, "errors": errors,
            "verdict": "FAIL" if errors else "PASS"}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the comparison as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Interface comparison: {report['module'] or '(module)'}")
    print(f"{'design':<24}{'entries':>8}{'cost':>7}{'hidden':>8}{'leaked':>8}{'depth':>7}{'burden':>8}{'score':>8}")
    for r in report["designs"]:
        print(f"{r['name'][:23]:<24}{r['entry_points']:>8}{r['interface_cost']:>7g}{r['hidden']:>8}"
              f"{r['leaked']:>8}{r['depth']:>7}{r['caller_burden']:>8}{r['score']:>8}")
    for r in report["designs"]:
        for prob in r["problems"]:
            print(f"  [ERROR] {r['name']}: {prob}")
        for note in r["notes"]:
            print(f"  [NOTE ] {r['name']}: {note}")
    for prob in report["global_problems"]:
        print(f"  [ERROR] {prob}")
    if report["recommendation"]:
        line = f"\nRecommended: {report['recommendation']}"
        if report["runner_up"]:
            line += f" (runner-up {report['runner_up']}, margin {report['margin']})"
        print(line)
        if report["close_call"]:
            print("Close call: consider a hybrid that keeps the winner's surface and the runner-up's hidden work.")
    else:
        print("\nNo valid design to recommend; fix the errors above and compare again.")
    print(f"Verdict: {report['verdict']}")


def main() -> None:
    """Parse arguments, compare designs, and exit with the gate result."""
    p = argparse.ArgumentParser(description="Compare candidate interfaces for one module and recommend one.")
    p.add_argument("--input", required=True, help="JSON file with 'designs' and 'required_responsibilities'")
    p.add_argument("--similarity", type=float, default=0.1,
                   help="interface-cost difference (fraction) under which designs count as near-identical")
    p.add_argument("--format", choices=("text", "json"), default="text", help="output format (default text)")
    args = p.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("designs", []), list):
            raise ValueError("expected an object with a 'designs' list")
    except (OSError, ValueError) as exc:
        print(f"error: cannot read designs file {args.input}: {exc}", file=sys.stderr)
        sys.exit(2)
    report = compare(data, args.similarity)
    output(report, args.format)
    sys.exit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
