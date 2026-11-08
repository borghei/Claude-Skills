#!/usr/bin/env python3
"""Route detector findings to refinement commands, or validate a refinement plan.

Route mode reads a ui_slop_detector.py JSON report and returns the two or
three commands worth running next, in triage order (access and blocking
defects, then structure, then expression and copy), always closing with
polish. It never runs anything; the user confirms the pick.

Plan mode validates a refinement plan JSON before any edit: every step names
a known command, edit steps say what changes, what must not be touched and
how the result will be verified, evaluation steps edit nothing, context work
comes first, polish comes last, and no target gets both quieter and bolder.

Usage:
  python3 command_router.py --report detector.json --mode operate --format text
  python3 command_router.py --plan refinement_plan.json --format json

Exit codes: 0 routed with no access-blocking work / plan valid; 1 routing
found access-blocking findings (contrast, tiny text, focus, reduced motion)
or the plan has errors (warnings too under --strict); 2 bad input
(unreadable or malformed JSON, missing fields).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional

EVALUATE = {"critique", "audit"}
CONTEXT = {"init", "document"}
EDIT = {"polish", "distill", "quieter", "bolder", "clarify", "harden", "typeset", "colorize",
        "layout", "animate", "adapt", "onboard", "delight", "extract", "optimize"}
COMMANDS = EVALUATE | CONTEXT | EDIT
MODES = {"persuade", "operate", "read", "showcase"}
# Triage bucket: lower runs first. Polish is always the closing pass.
BUCKET = {"harden": 0, "optimize": 1, "extract": 1, "adapt": 1, "distill": 1, "layout": 1, "onboard": 2,
          "clarify": 2, "typeset": 2, "colorize": 2, "quieter": 3, "animate": 3, "bolder": 3, "delight": 4, "polish": 9}
WEIGHT = {"high": 3, "medium": 2, "advisory": 1}
ACCESS_RULES = {"low-contrast-pair", "faint-gray-text", "tiny-text", "focus-ring-removed", "missing-reduced-motion"}
EVIDENCE = re.compile(r"rerun|re-run|detector|screenshot|contrast|ratio|keyboard|\btab\b|screen ?reader|zoom|"
                      r"viewport|\d+px|\d+ms|breakpoint|exit|lint|reduced[- ]motion|focus|voiceover|talkback|"
                      r"simulator|emulator|\d+%|before/after|diff", re.I)
NEW_PRIMITIVE = re.compile(r"\bnew (colou?r|font|typeface|radius|shadow|token|palette)\b|\badd (a )?(colou?r|font)\b", re.I)


class InputError(Exception):
    """Raised when the input cannot be routed or validated at all."""


def load(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError(f"{path} must hold a JSON object")
    return data


def route(report: dict, mode: Optional[str], platform: str) -> dict:
    findings = report.get("findings")
    if not isinstance(findings, list):
        raise InputError("report has no 'findings' list; pass ui_slop_detector.py --format json output")
    if platform in ("ios", "android"):
        return {"picks": [{"command": "critique", "reason": "native target: the web detector does not read native "
                           "code; run a design review against the native platform checks"},
                          {"command": "audit", "reason": "native audit: accessibility labels, Dynamic Type / sp, "
                           "touch targets, platform controls"}], "then": "polish", "notes": []}
    score: Dict[str, int] = defaultdict(int)
    rules: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    example: Dict[str, str] = {}
    urgent = set()
    for f in findings:
        if not isinstance(f, dict) or not all(isinstance(f.get(k, ""), str) for k in ("command", "severity", "rule")) \
                or f.get("command") not in COMMANDS:
            raise InputError(f"finding without a known command: {str(f)[:80]}")
        cmd = f["command"]
        score[cmd] += WEIGHT.get(f.get("severity"), 1)
        rules[cmd][f.get("rule", "?")] += 1
        example.setdefault(cmd, f"{f.get('file')}:{f.get('line')}")
        if f.get("rule") in ACCESS_RULES:
            urgent.add(cmd)
    notes: List[str] = []
    if mode in ("operate", "read"):
        for cmd in ("bolder", "delight"):
            if cmd in score:
                notes.append(f"{cmd} dropped: {mode} surfaces earn expression through precision, not volume")
                score.pop(cmd)
    if not score and findings:
        return {"picks": [{"command": "polish", "reason": "only closing-pass or mode-dropped findings: "
                           + ", ".join(sorted({f.get("rule", "?") for f in findings}))}], "then": "done", "notes": notes}
    if not score:
        return {"picks": [{"command": "critique", "reason": "the scan is clean, which proves only the floor; "
                           "a design review judges hierarchy, specificity and fit"}], "then": "polish",
                "notes": notes + ["no findings to route"]}
    order = sorted((c for c in score if c != "polish" or len(score) == 1),
                   key=lambda c: (0 if c in urgent else 1, BUCKET.get(c, 5), -score[c]))
    picks = []
    for cmd in order[:3]:
        top = sorted(rules[cmd].items(), key=lambda kv: (kv[0] not in ACCESS_RULES, -kv[1]))[:3]  # access rules lead
        reason = ", ".join(f"{r} x{n}" for r, n in top)
        if cmd in urgent:
            reason = "access first: " + reason
        picks.append({"command": cmd, "score": score[cmd], "reason": reason, "first_hit": example[cmd]})
    if len(order) > 3:
        notes.append("also queued: " + ", ".join(order[3:]))
    if len(findings) >= 25 or len(order) >= 5:
        notes.append("wide spread of findings: run audit to score the surface before fixing piecemeal")
    return {"picks": picks, "then": "polish", "notes": notes,
            "plan_skeleton": [{"command": "audit", "target": "", "changes": [], "must_not_touch": [], "verify": []}]
            + [{"command": p["command"], "target": "", "changes": [], "must_not_touch": [], "verify": []} for p in picks]
            + [{"command": "polish", "target": "", "changes": [], "must_not_touch": [], "verify": []}]}


def as_list(step: dict, key: str) -> List[str]:
    value = step.get(key, [])
    if isinstance(value, str):
        return [value] if value.strip() else []
    if not isinstance(value, list):
        raise InputError(f"step '{step.get('command')}' field '{key}' must be a list of strings")
    return [str(v) for v in value if str(v).strip()]


def validate(plan: dict) -> dict:
    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        raise InputError("plan needs a non-empty 'steps' list")
    errors: List[str] = []
    warns: List[str] = []
    mode = plan.get("mode")
    for i, step in enumerate(steps, 1):
        if not isinstance(step, dict) or not all(isinstance(step.get(k, ""), str) for k in ("command", "target")):
            raise InputError(f"step {i} must be an object whose 'command' and 'target' are strings")
    if not isinstance(mode, (str, type(None))) or not isinstance(plan.get("target", ""), str):
        raise InputError("plan 'mode' and 'target' must be strings")
    if mode not in MODES:
        errors.append(f"plan mode '{mode}' must be one of {', '.join(sorted(MODES))}")
    default_target = plan.get("target", "")
    seen_edit = False
    by_target: Dict[str, set] = defaultdict(set)
    pairs = set()
    edit_indexes = []
    for i, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            raise InputError(f"step {i} is not an object")
        cmd = step.get("command")
        target = step.get("target") or default_target
        label = f"step {i} ({cmd})"
        if cmd not in COMMANDS:
            errors.append(f"{label}: unknown command; use one of {', '.join(sorted(COMMANDS))}")
            continue
        if not target:
            errors.append(f"{label}: no target (file, component or route)")
        changes, keep, verify = as_list(step, "changes"), as_list(step, "must_not_touch"), as_list(step, "verify")
        if (cmd, target) in pairs:
            warns.append(f"{label}: {cmd} already planned for {target}")
        pairs.add((cmd, target))
        if cmd in EVALUATE and changes:
            errors.append(f"{label}: {cmd} reports findings and edits nothing; move the changes to a refine step")
        if cmd in CONTEXT and seen_edit:
            errors.append(f"{label}: {cmd} writes the context file; it must run before any edit step")
        if cmd in EDIT:
            seen_edit = True
            edit_indexes.append(i)
            by_target[target].add(cmd)
            if not changes:
                errors.append(f"{label}: list what this step changes")
            if not keep:
                errors.append(f"{label}: list what must not be touched (scope is the contract)")
            if not verify:
                errors.append(f"{label}: list how the result will be verified")
            vague = [v for v in verify if not EVIDENCE.search(v)]
            for v in vague:
                warns.append(f"{label}: verification '{v[:50]}' names no evidence (rerun, screenshot, ratio, keyboard ...)")
            if cmd == "bolder" and any(NEW_PRIMITIVE.search(c) and "approved" not in c.lower() for c in changes):
                warns.append(f"{label}: bolder amplifies what the system owns; a new primitive needs sign-off ('approved')")
            if cmd in ("bolder", "delight") and mode in ("operate", "read"):
                warns.append(f"{label}: {cmd} on a {mode} surface; keep it to one earned moment")
    for target, cmds in by_target.items():
        if {"quieter", "bolder"} <= cmds:
            errors.append(f"quieter and bolder both target {target}; pick the direction first")
    if edit_indexes:
        last = steps[-1].get("command")
        if last != "polish":
            errors.append(f"plan edits but ends with '{last}'; polish is the closing pass")
        polish_at = [i for i in edit_indexes if steps[i - 1].get("command") == "polish"]
        if polish_at and polish_at[0] != edit_indexes[-1]:
            errors.append(f"polish at step {polish_at[0]} runs before other edits; it belongs last")
        first_edit = edit_indexes[0]
        if not any(s.get("command") in EVALUATE for s in steps[:first_edit - 1]) and not plan.get("evidence"):
            warns.append("no critique/audit step and no 'evidence' (detector report) before the first edit")
    return {"verdict": "FAIL" if errors else "PASS", "errors": errors, "warnings": warns, "steps": len(steps)}


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Route detector findings to commands, or validate a refinement plan.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--report", help="ui_slop_detector.py JSON report to route")
    src.add_argument("--plan", help="Refinement plan JSON to validate")
    p.add_argument("--mode", choices=sorted(MODES), help="Surface mode (route mode)")
    p.add_argument("--platform", default="web", choices=("web", "ios", "android", "cross-platform"),
                   help="Target platform (route mode, default web)")
    p.add_argument("--strict", action="store_true", help="Plan mode: warnings fail the plan")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    try:
        if args.report:
            result = route(load(args.report), args.mode, args.platform)
            code = 1 if any(str(x.get("reason", "")).startswith("access first") for x in result["picks"]) else 0
        else:
            result = validate(load(args.plan))
            code = 1 if result["errors"] or (args.strict and result["warnings"]) else 0
    except (InputError, TypeError, AttributeError) as exc:
        print(f"error: malformed input: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
    elif args.report:
        for n, pick in enumerate(result["picks"], 1):
            hit = f"  (first hit {pick['first_hit']})" if pick.get("first_hit") else ""
            print(f"{n}. {pick['command']:<9} {pick['reason']}{hit}")
        print(f"then: {result['then']} (closing pass)")
        for note in result["notes"]:
            print(f"note: {note}")
    else:
        for e in result["errors"]:
            print(f"ERROR {e}")
        for w in result["warnings"]:
            print(f"WARN  {w}")
        print(f"{result['verdict']}  {len(result['errors'])} error(s), {len(result['warnings'])} warning(s), "
              f"{result['steps']} step(s)")
    return code


if __name__ == "__main__":
    sys.exit(main())
