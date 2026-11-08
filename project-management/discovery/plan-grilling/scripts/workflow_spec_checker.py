#!/usr/bin/env python3
"""Check a recurring-workflow spec produced by a multi-session grilling.

A workflow spec is implementable when someone who never heard the grilling
could build it without asking a question. This tool checks the spec for a
concrete trigger, declared inputs, steps with an actor each, human checkpoints
that present a decision-ready brief, outputs with a destination, a testable
done-definition, and no open questions left. Deterministic, stdlib only.

Usage:
    python3 workflow_spec_checker.py --input assets/sample_workflow_spec.json
    python3 workflow_spec_checker.py --input spec.json --format json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

TRIGGER_TYPES = {"event", "schedule", "manual"}
ACTORS = {"agent", "human", "script"}
VAGUE = re.compile(r"\b(properly|correctly|good|nice|as needed|appropriate(ly)?|etc\.?|somehow|"
                   r"reasonable|clean|better|tbd|when possible|when needed|if needed)\b", re.IGNORECASE)
MEASURABLE = re.compile(r"\d|\b(every|each|all|no|zero|none|exists|within|before|after|equals?|"
                        r"contains?|matches|is (sent|filed|posted|written|created))\b", re.IGNORECASE)


def load_spec(path: Path) -> Dict[str, Any]:
    """Load the workflow spec and confirm it is a JSON object."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("workflow spec must be a JSON object")
    if not str(data.get("name", "")).strip():
        raise ValueError("workflow spec has no 'name'")
    return data


def add(findings: List[Dict[str, str]], sev: str, area: str, msg: str) -> None:
    """Append one finding."""
    findings.append({"severity": sev, "area": area, "message": msg})


def check_trigger(spec: Dict[str, Any], findings: List[Dict[str, str]]) -> None:
    """A trigger needs a known type and a concrete detail."""
    trig = spec.get("trigger")
    if not isinstance(trig, dict):
        add(findings, "error", "trigger", "no trigger — say what starts each run")
        return
    if trig.get("type") not in TRIGGER_TYPES:
        add(findings, "error", "trigger", f"trigger type must be one of {sorted(TRIGGER_TYPES)}")
    detail = str(trig.get("detail", "")).strip()
    if not detail:
        add(findings, "error", "trigger", "trigger has no detail (which event, or which schedule)")
    elif VAGUE.search(detail):
        add(findings, "warn", "trigger", f"trigger detail is vague: {detail!r}")
    if trig.get("type") == "schedule" and detail and not re.search(r"\d|daily|weekly|monthly|monday|"
                                                                   r"tuesday|wednesday|thursday|friday",
                                                                   detail, re.IGNORECASE):
        add(findings, "warn", "trigger", "schedule trigger names no time or cadence")


def check_steps(spec: Dict[str, Any], findings: List[Dict[str, str]]) -> List[str]:
    """Steps need ids, actions and actors; returns the step ids."""
    steps = spec.get("steps")
    if not isinstance(steps, list) or not steps:
        add(findings, "error", "steps", "no steps — the workflow does nothing")
        return []
    ids: List[str] = []
    inputs = {str(i.get("name")) for i in spec.get("inputs", []) if isinstance(i, dict)}
    for pos, step in enumerate(steps, start=1):
        sid = str(step.get("id") or f"step{pos}")
        if sid in ids:
            add(findings, "error", sid, "duplicate step id")
        ids.append(sid)
        if not str(step.get("action", "")).strip():
            add(findings, "error", sid, "step has no action")
        if step.get("actor") not in ACTORS:
            add(findings, "error", sid, f"step actor must be one of {sorted(ACTORS)}")
        for used in step.get("uses", []):
            if used not in inputs and not any(used == s for s in ids[:-1]):
                add(findings, "error", sid, f"uses {used!r}, which is neither a declared input nor an earlier step")
        if VAGUE.search(str(step.get("action", ""))):
            add(findings, "warn", sid, "action wording is vague; name the concrete operation")
    return ids


def check_checkpoints(spec: Dict[str, Any], step_ids: List[str], findings: List[Dict[str, str]]) -> None:
    """Checkpoints must point at a step, ask a decision and present a brief."""
    cps = spec.get("checkpoints", [])
    if not isinstance(cps, list):
        add(findings, "error", "checkpoints", "checkpoints must be a list")
        return
    if not cps and spec.get("autonomous") is not True:
        add(findings, "error", "checkpoints",
            "no human checkpoint and not marked autonomous — decide which it is")
    positions = {sid: i for i, sid in enumerate(step_ids)}
    for cp in cps:
        at = str(cp.get("after_step", ""))
        if at not in positions:
            add(findings, "error", "checkpoints", f"checkpoint after unknown step {at!r}")
            continue
        if not str(cp.get("decision", "")).strip():
            add(findings, "error", at, "checkpoint states no decision for the human")
        if not str(cp.get("brief", "")).strip():
            add(findings, "error", at, "checkpoint presents no brief — the human would read raw output")
        if positions[at] < len(step_ids) // 3 and len(step_ids) >= 4:
            add(findings, "warn", at, "checkpoint sits early; push it later so the human is asked once, prepared")


def check_outputs_and_done(spec: Dict[str, Any], findings: List[Dict[str, str]]) -> None:
    """Outputs need destinations; done-criteria must be testable; no open questions."""
    outputs = spec.get("outputs", [])
    if not outputs:
        add(findings, "error", "outputs", "no outputs — say what each run leaves behind")
    for out in outputs:
        if isinstance(out, dict) and not str(out.get("destination", "")).strip():
            add(findings, "error", "outputs", f"output {out.get('name', '?')!r} has no destination")
    done = spec.get("done_definition", [])
    if not done:
        add(findings, "error", "done", "no done-definition — nobody can tell a run succeeded")
    for crit in done:
        text = str(crit)
        if VAGUE.search(text):
            add(findings, "error", "done", f"done-criterion is not testable: {text!r}")
        elif not MEASURABLE.search(text):
            add(findings, "warn", "done", f"done-criterion has no observable check: {text!r}")
    if not spec.get("inputs"):
        add(findings, "warn", "inputs", "no inputs declared; most workflows read something")
    if not spec.get("failure_handling"):
        add(findings, "warn", "failure", "no failure_handling — what happens when a step fails?")
    for q in spec.get("open_questions", []):
        add(findings, "error", "open", f"open question blocks implementation: {q}")


def analyse(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Run all checks and return the report."""
    findings: List[Dict[str, str]] = []
    check_trigger(spec, findings)
    step_ids = check_steps(spec, findings)
    check_checkpoints(spec, step_ids, findings)
    check_outputs_and_done(spec, findings)
    errors = sum(1 for f in findings if f["severity"] == "error")
    findings.sort(key=lambda f: (0 if f["severity"] == "error" else 1, f["area"]))
    return {
        "workflow": spec["name"],
        "steps": len(step_ids),
        "checkpoints": len(spec.get("checkpoints", []) or []),
        "errors": errors,
        "warnings": len(findings) - errors,
        "implementable": errors == 0,
        "findings": findings,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    verdict = "IMPLEMENTABLE" if report["implementable"] else "NOT READY"
    print(f"{verdict}  {report['workflow']}  ({report['steps']} steps, {report['checkpoints']} checkpoints, "
          f"{report['errors']} errors, {report['warnings']} warnings)")
    for f in report["findings"]:
        print(f"  [{f['severity']:5}] {f['area']:<12} {f['message']}")
    if not report["findings"]:
        print("  clean — an implementer could build this without asking a question")


def main() -> None:
    """Parse arguments, check the spec and exit with the gate status."""
    parser = argparse.ArgumentParser(description="Check a workflow spec for implementability.")
    parser.add_argument("--input", required=True, help="path to the workflow spec JSON")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        report = analyse(load_spec(Path(args.input)))
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: {args.input} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    except (ValueError, AttributeError, TypeError) as exc:
        print(f"error: malformed spec: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["implementable"] else 1)


if __name__ == "__main__":
    main()
