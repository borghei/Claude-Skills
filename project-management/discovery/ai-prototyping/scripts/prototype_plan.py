#!/usr/bin/env python3
"""
prototype_plan.py - Turn discovery hypotheses into a prototype test plan.

For each hypothesis (uncertainty type + impact + existing evidence) the tool
recommends a fidelity rung, a test method, a tool category, a participant
guideline, a timebox and explicit kill criteria. It also says whether the
initiative should be prototype-led or spec-led overall.

Stdlib only. Deterministic: same input, same output.

Usage:
    python3 prototype_plan.py --input hypotheses.json
    python3 prototype_plan.py --input hypotheses.json --format json --output plan.json

Exit codes:
    0  plan produced, no blocking gaps
    1  tool error (bad path, invalid JSON, invalid field values)
    2  gate failed: a hypothesis cannot be tested as written (no success
       metric, no threshold, or no target segment) - fix it before building
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "pm/ai-prototyping/prototype-plan/v1"
UNCERTAINTY = ("desirability", "usability", "feasibility", "viability")
EVIDENCE = {"none": 4, "anecdotal": 3, "qualitative": 2, "quantitative": 1}
FIDELITY = {
    0: "F0 - no prototype: interview, smoke test or spec",
    1: "F1 - prompted mock (static screens)",
    2: "F2 - clickable prototype",
    3: "F3 - working prototype, synthetic data",
    4: "F4 - working prototype, real data",
}
TOOL_CATEGORY = {
    0: "none (interview script, landing page, spreadsheet model)",
    1: "AI design tool or AI app builder (screens only)",
    2: "AI design tool or AI app builder (linked flows)",
    3: "AI app builder or AI coding assistant",
    4: "AI coding assistant in an approved environment",
}
TIMEBOX_DAYS = {0: 1, 1: 1, 2: 2, 3: 4, 4: 6}
PARTICIPANTS = {
    "desirability": "8-12 target users per segment, each asked for a commitment signal",
    "usability": "5-8 target users per segment per round; fix, then run another round",
    "feasibility": "no user sample - an engineering spike judged against a technical bar",
    "viability": "no user sample - a business, pricing or legal review",
}
METHOD = {
    "desirability": "concept test: show the mock, ask for a commitment (sign-up, pilot, pre-order), not an opinion",
    "usability": "moderated task test: scripted tasks, observe success and errors, no help from the facilitator",
    "feasibility": "technical spike: build the riskiest path and measure it (latency, accuracy, integration effort)",
    "viability": "model or review: unit economics, pricing test, legal/compliance sign-off",
}


def fail(msg: str) -> None:
    """Print a tool error and exit 1."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def recommend(h: dict[str, Any], real_data_approved: bool) -> dict[str, Any]:
    """Return the recommendation for one hypothesis."""
    hid = str(h.get("id", "?"))
    kind = str(h.get("uncertainty", "")).lower()
    if kind not in UNCERTAINTY:
        fail(f"hypothesis {hid}: uncertainty must be one of {', '.join(UNCERTAINTY)}")
    ev = str(h.get("evidence", "none")).lower()
    if ev not in EVIDENCE:
        fail(f"hypothesis {hid}: evidence must be one of {', '.join(EVIDENCE)}")
    try:
        impact = int(h.get("impact", 3))
    except (TypeError, ValueError):
        fail(f"hypothesis {hid}: impact must be an integer 1-5")
    if not 1 <= impact <= 5:
        fail(f"hypothesis {hid}: impact must be 1-5")

    notes: list[str] = []
    gaps: list[str] = []
    if kind == "desirability":
        rung = 0 if ev == "none" else (2 if h.get("interactive_flow") else 1)
        if rung == 0:
            notes.append("no evidence yet - interview or smoke-test before generating screens")
    elif kind == "usability":
        rung = 3 if h.get("dynamic_states") else 2
    elif kind == "feasibility":
        rung = 4 if h.get("needs_real_data") else 3
    else:
        rung = 0
        notes.append("a prototype cannot prove viability - model it or get a review")

    if rung == 4 and not real_data_approved:
        rung = 3
        notes.append("real data needed but not approved - downgraded to synthetic data; "
                     "get data-owner and security approval before F4")

    for field in ("success_metric", "threshold", "target_segment"):
        if not str(h.get(field, "")).strip():
            gaps.append(f"missing {field}")

    threshold = str(h.get("threshold", "")).strip() or "<threshold not set>"
    metric = str(h.get("success_metric", "")).strip() or "<metric not set>"
    kill = (f"Kill or pivot if {metric} misses '{threshold}' after the timebox; "
            "do not extend the timebox to rescue the idea")
    if kind == "feasibility":
        kill = f"Kill or re-scope if the spike cannot reach '{threshold}' within the timebox"
    return {
        "id": hid,
        "statement": h.get("statement", ""),
        "uncertainty": kind,
        "priority_score": impact * EVIDENCE[ev],
        "fidelity": FIDELITY[rung],
        "rung": rung,
        "method": METHOD[kind],
        "tool_category": TOOL_CATEGORY[rung],
        "participants": PARTICIPANTS[kind],
        "success_criterion": f"{metric}: {threshold}",
        "kill_criterion": kill,
        "timebox_days": TIMEBOX_DAYS[rung],
        "notes": notes,
        "gaps": gaps,
    }


def build_plan(doc: dict[str, Any]) -> dict[str, Any]:
    """Build the full plan from the input document."""
    hyps = doc.get("hypotheses")
    if not isinstance(hyps, list) or not hyps:
        fail("input needs a non-empty 'hypotheses' list")
    cons = doc.get("constraints", {}) or {}
    approved = bool(cons.get("real_data_approved", False))
    recs = [recommend(h, approved) for h in hyps]
    recs.sort(key=lambda r: (-r["priority_score"], r["id"]))

    weight = {k: 0 for k in UNCERTAINTY}
    for r in recs:
        weight[r["uncertainty"]] += r["priority_score"]
    proto_weight = weight["desirability"] + weight["usability"] + weight["feasibility"]
    total = sum(weight.values()) or 1
    if proto_weight / total >= 0.5:
        mode = "prototype-led: most risk sits in desirability/usability/feasibility"
    else:
        mode = "spec-led: most risk is viability - write the spec and model first"

    days = sum(r["timebox_days"] for r in recs if r["rung"] > 0)
    warnings: list[str] = []
    max_days = cons.get("max_days")
    if isinstance(max_days, (int, float)) and days > max_days:
        warnings.append(f"prototype timeboxes total {days} days, over the {max_days}-day budget; "
                        "test the top-priority hypotheses first")
    if sum(1 for r in recs if r["uncertainty"] == "usability") and not any(
            r["uncertainty"] == "desirability" for r in recs):
        warnings.append("usability is tested but desirability is not - a usable product "
                        "nobody wants still fails")
    blocking = [f"{r['id']}: {g}" for r in recs for g in r["gaps"]]
    return {
        "initiative": doc.get("initiative", ""),
        "as_of": doc.get("as_of", ""),
        "mode": mode,
        "risk_weight": weight,
        "total_prototype_days": days,
        "recommendations": recs,
        "warnings": warnings,
        "blocking": blocking,
        "passed": not blocking,
    }


def render_markdown(plan: dict[str, Any]) -> str:
    """Render the plan as GitHub-flavored markdown."""
    out = [f"# Prototype Plan: {plan['initiative'] or 'untitled'}", ""]
    if plan["as_of"]:
        out.append(f"As of: {plan['as_of']}")
    out += [f"**Mode:** {plan['mode']}",
            f"**Total prototype timebox:** {plan['total_prototype_days']} days", "",
            "## Hypotheses (highest priority first)", "",
            "| # | ID | Uncertainty | Priority | Fidelity | Timebox (d) |",
            "|---|----|-------------|----------|----------|-------------|"]
    for i, r in enumerate(plan["recommendations"], 1):
        out.append(f"| {i} | {r['id']} | {r['uncertainty']} | {r['priority_score']} | "
                   f"{r['fidelity']} | {r['timebox_days']} |")
    out.append("")
    for r in plan["recommendations"]:
        out += [f"### {r['id']} - {r['statement']}", "",
                f"- **Method:** {r['method']}",
                f"- **Tool category:** {r['tool_category']}",
                f"- **Participants:** {r['participants']}",
                f"- **Success criterion:** {r['success_criterion']}",
                f"- **Kill criterion:** {r['kill_criterion']}"]
        out += [f"- **Note:** {n}" for n in r["notes"]]
        out += [f"- **GAP:** {g}" for g in r["gaps"]]
        out.append("")
    if plan["warnings"]:
        out += ["## Warnings", ""] + [f"- {w}" for w in plan["warnings"]] + [""]
    verdict = "PASS" if plan["passed"] else "FAIL - fix these before building anything"
    out += ["## Gate", "", f"**{verdict}**"]
    out += [f"- {b}" for b in plan["blocking"]]
    return "\n".join(out) + "\n"


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(
        description="Recommend prototype fidelity, test method, and kill criteria per hypothesis.",
        epilog="Exit codes: 0 pass, 1 tool error, 2 gate failed (untestable hypothesis).")
    ap.add_argument("--input", required=True, help="hypotheses JSON file (see assets/)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown",
                    help="output format (default: markdown)")
    ap.add_argument("--output", help="write to this file instead of stdout")
    args = ap.parse_args()
    try:
        doc = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"input file not found: {args.input}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {args.input}: {exc}")
    if not isinstance(doc, dict):
        fail("top-level JSON must be an object")
    plan = build_plan(doc)
    if args.format == "json":
        text = json.dumps({"schema": SCHEMA, "generated_at": plan["as_of"], "data": plan},
                          indent=2) + "\n"
    else:
        text = render_markdown(plan)
    try:
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    except OSError as exc:
        fail(f"cannot write output: {exc}")
    sys.exit(0 if plan["passed"] else 2)


if __name__ == "__main__":
    main()
