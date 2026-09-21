#!/usr/bin/env python3
"""
prototype_handoff_checker.py - Gate a prototype-to-engineering handoff.

Validates that a handoff package carries what a prototype cannot: the
problem, success metrics, validated findings with evidence, a throwaway
list, testable acceptance criteria, and data / security / accessibility /
IP notes. Accepts the JSON schema in assets/handoff_complete.json or a
markdown handoff doc built from assets/handoff_template.md.

Stdlib only. Deterministic.

Usage:
    python3 prototype_handoff_checker.py --input handoff.json
    python3 prototype_handoff_checker.py --input handoff.md --strict
    python3 prototype_handoff_checker.py --input handoff.json --format json

Exit codes:
    0  handoff complete (warnings allowed unless --strict)
    1  tool error (bad path, unreadable or malformed input)
    2  gate failed: one or more blockers (or warnings under --strict)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "pm/ai-prototyping/handoff-check/v1"
REQUIRED = {  # key -> (markdown heading keyword, why it matters)
    "problem": ("problem", "engineering must know what is being solved and for whom"),
    "success_metrics": ("metric", "without metrics nobody can tell if the build worked"),
    "validated_findings": ("finding", "the prototype's value is what it proved, not the screens"),
    "throwaway_list": ("throwaway", "unlabelled prototype code gets shipped by accident"),
    "acceptance_criteria": ("acceptance", "engineering builds to criteria, not to a demo"),
    "non_goals": ("non-goal", "prototype polish invites scope creep"),
    "data_privacy": ("privacy", "prototype tools may retain whatever data was pasted in"),
    "security": ("security", "generated code skips auth, input validation and secrets hygiene"),
    "accessibility": ("accessib", "generated UIs routinely miss keyboard, contrast and labels"),
}
OPTIONAL = {"constraints": "constraint", "risks": "risk", "ip_review": "licens",
            "prototype_link": "prototype link", "disposition": "disposition"}
SKIPPED_BY_DEFAULT = ("auth", "error", "accessib", "security", "performance", "data model")
PLACEHOLDER = re.compile(r"<(?:[A-Za-z][^<>]{2,}|\.\.\.)>")  # unfilled template text
TESTABLE = re.compile(r"\b(given|when|then|must|shall|within|at least|no more than|<|>|%|\d)",
                      re.I)


def fail(msg: str) -> None:
    """Print a tool error and exit 1."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_markdown(text: str) -> dict[str, Any]:
    """Map markdown H2/H3 sections onto the handoff keys by heading keyword."""
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^#{2,3}\s+(.*)", line)
        if m:
            current = m.group(1).strip().lower()
            sections.setdefault(current, [])
        elif current is not None and line.strip():
            sections[current].append(line.strip())
    doc: dict[str, Any] = {}
    for key, kw in {**{k: v[0] for k, v in REQUIRED.items()}, **OPTIONAL}.items():
        for head, body in sections.items():
            if kw in head and (key != "problem" or "non" not in head):
                items = [re.sub(r"^[-*]\s+(\[.\]\s+)?", "", b) for b in body
                         if not b.startswith("<!--") and not PLACEHOLDER.search(b)]
                doc[key] = items
                break
    return doc


def nonempty(v: Any) -> bool:
    """True when a field carries content."""
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return bool(v)
    return v is not None


def check(doc: dict[str, Any], from_markdown: bool) -> tuple[list[str], list[str]]:
    """Return (blockers, warnings) for a handoff document."""
    blockers: list[str] = []
    warnings: list[str] = []
    for key, (_, why) in REQUIRED.items():
        if not nonempty(doc.get(key)):
            blockers.append(f"missing {key}: {why}")
    for key in OPTIONAL:
        if not nonempty(doc.get(key)):
            warnings.append(f"missing {key}")

    prob = doc.get("problem")
    prob = " ".join(prob) if isinstance(prob, list) else str(prob or "")
    if prob and len(prob.split()) < 15:
        warnings.append("problem statement is under 15 words - name who, the pain, and the evidence")
    for i, m in enumerate(doc.get("success_metrics") or []):
        if isinstance(m, dict) and not (nonempty(m.get("baseline")) and nonempty(m.get("target"))):
            blockers.append(f"success_metrics[{i}] needs a baseline and a target")
    for i, f in enumerate(doc.get("validated_findings") or []):
        if isinstance(f, dict):
            if str(f.get("status", "")).lower() in ("open", "untested"):
                warnings.append(f"validated_findings[{i}] is still open - carry it as a risk")
                continue
            if not f.get("participants"):
                blockers.append(f"validated_findings[{i}] has no participant count")
            if not nonempty(f.get("result")) or not nonempty(f.get("threshold")):
                blockers.append(f"validated_findings[{i}] must state the result against a "
                                "pre-set threshold")
    acs = doc.get("acceptance_criteria") or []
    untestable = [a for a in acs if isinstance(a, str) and not TESTABLE.search(a)]
    if untestable:
        warnings.append(f"{len(untestable)} acceptance criteria look untestable "
                        f"(e.g. '{untestable[0][:60]}')")
    tl = " ".join(json.dumps(x) if not isinstance(x, str) else x
                  for x in doc.get("throwaway_list") or []).lower()
    missing = [s for s in SKIPPED_BY_DEFAULT if tl and s not in tl]
    if missing:
        warnings.append("throwaway list does not mention: " + ", ".join(missing))

    dp = doc.get("data_privacy")
    if isinstance(dp, dict):
        if dp.get("real_customer_data_used") and not nonempty(dp.get("approval_ref")):
            blockers.append("real customer data used in a prototype tool without an approval "
                            "reference")
    elif from_markdown and dp:
        text = " ".join(dp)
        if re.search(r"real (customer )?data[^:]*:\s*yes", text, re.I) \
                and not re.search(r"approv\w*\s*(ref\w*)?\s*[:#]?\s*\w", text, re.I):
            blockers.append("real customer data used in a prototype tool without an approval "
                            "reference")
        elif not re.search(r"real (customer )?data[^:]*:\s*(yes|no)", text, re.I):
            warnings.append("data_privacy does not state 'Real customer data used: yes/no'")
    disp = str(doc.get("disposition", "")).lower() if not from_markdown else \
        " ".join(doc.get("disposition") or []).lower()
    if disp and "throwaway" not in disp and "starting" not in disp:
        warnings.append("disposition should say 'throwaway' or 'starting point'")
    return blockers, warnings


def render_markdown(res: dict[str, Any]) -> str:
    """Render the check result as markdown."""
    out = [f"# Prototype Handoff Check: {res['input']}", "",
           f"**Result:** {'PASS' if res['passed'] else 'FAIL'} "
           f"({len(res['blockers'])} blockers, {len(res['warnings'])} warnings"
           f"{', strict' if res['strict'] else ''})", ""]
    if res["blockers"]:
        out += ["## Blockers", ""] + [f"- {b}" for b in res["blockers"]] + [""]
    if res["warnings"]:
        out += ["## Warnings", ""] + [f"- {w}" for w in res["warnings"]] + [""]
    if res["passed"]:
        out.append("Handoff carries the problem, evidence and guardrails engineering needs.")
    return "\n".join(out) + "\n"


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(
        description="Validate a prototype-to-engineering handoff (JSON or markdown).",
        epilog="Exit codes: 0 pass, 1 tool error, 2 gate failed.")
    ap.add_argument("--input", required=True, help="handoff .json or .md file")
    ap.add_argument("--strict", action="store_true", help="treat warnings as blockers")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown",
                    help="output format (default: markdown)")
    ap.add_argument("--output", help="write to this file instead of stdout")
    args = ap.parse_args()
    path = Path(args.input)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"input file not found: {args.input}")
    except OSError as exc:
        fail(f"cannot read {args.input}: {exc}")
    is_md = path.suffix.lower() in (".md", ".markdown")
    if is_md:
        doc = parse_markdown(raw)
    else:
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON in {args.input}: {exc}")
        if not isinstance(doc, dict):
            fail("top-level JSON must be an object")
    blockers, warnings = check(doc, is_md)
    passed = not blockers and not (args.strict and warnings)
    res = {"input": path.name, "format": "markdown" if is_md else "json", "strict": args.strict,
           "blockers": blockers, "warnings": warnings, "passed": passed}
    text = (json.dumps({"schema": SCHEMA, "generated_at": str(doc.get("as_of", "")),
                        "data": res}, indent=2) + "\n") if args.format == "json" \
        else render_markdown(res)
    try:
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    except OSError as exc:
        fail(f"cannot write output: {exc}")
    sys.exit(0 if passed else 2)


if __name__ == "__main__":
    main()
