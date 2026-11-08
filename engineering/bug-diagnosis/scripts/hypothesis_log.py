#!/usr/bin/env python3
"""Validate a bug-diagnosis log and rank its open hypotheses.

Checks the reproduction signal against the gate (command, red rate, runtime,
symptom assertion), checks every hypothesis is falsifiable, checks experiments
change one variable at a time, applies stop rules, and ranks the hypotheses
still open by expected information per minute (prior / cost).

Usage:
  python3 hypothesis_log.py --input diagnosis.json
  python3 hypothesis_log.py --input diagnosis.json --max-runtime 30 --format json

Exit codes: 0 log passes, 1 gate failures found, 2 input could not be read.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

STATUSES = {"open", "refuted", "confirmed", "inconclusive"}
PREDICTION_RE = re.compile(r"\bif\b.+\bthen\b", re.IGNORECASE | re.DOTALL)
VAGUE_WORDS = ("something", "somehow", "maybe", "weird", "flaky", "some issue", "race-y")


def finding(level: str, where: str, message: str) -> Dict[str, str]:
    """Build one finding record."""
    return {"level": level, "where": where, "message": message}


def check_repro(repro: Dict[str, Any], max_runtime: float, min_red_rate: float) -> List[Dict[str, str]]:
    """Check the reproduction signal against the feedback-loop gate."""
    out: List[Dict[str, str]] = []
    if not repro:
        return [finding("error", "repro", "no reproduction signal recorded; build one before hypothesising")]
    if not str(repro.get("command", "")).strip():
        out.append(finding("error", "repro.command", "no runnable command; the loop must be one invocation"))
    runs = int(repro.get("runs", 0) or 0)
    red = int(repro.get("red_runs", 0) or 0)
    if runs < 3:
        out.append(finding("error", "repro.runs", f"loop executed {runs} time(s); run it at least 3 times"))
    elif red / runs < min_red_rate:
        out.append(finding("error", "repro.red_runs",
                           f"red rate {red}/{runs} is below {min_red_rate:.0%}; raise the repro rate first"))
    runtime = float(repro.get("runtime_seconds", 0) or 0)
    if runtime <= 0:
        out.append(finding("warn", "repro.runtime_seconds", "runtime not recorded"))
    elif runtime > max_runtime:
        out.append(finding("warn", "repro.runtime_seconds",
                           f"loop takes {runtime:g}s (budget {max_runtime:g}s); tighten it before bisecting"))
    if not repro.get("asserts_symptom"):
        out.append(finding("error", "repro.asserts_symptom",
                           "loop does not assert the reported symptom; 'does not crash' is not a signal"))
    if not repro.get("minimised"):
        out.append(finding("warn", "repro.minimised", "repro not minimised; extra moving parts widen the search"))
    return out


def check_hypotheses(hyps: List[Dict[str, Any]], min_h: int, max_h: int) -> List[Dict[str, str]]:
    """Check hypothesis count, falsifiability, and status consistency."""
    out: List[Dict[str, str]] = []
    if len(hyps) < min_h:
        out.append(finding("error", "hypotheses",
                           f"{len(hyps)} hypothesis(es); list at least {min_h} before testing any"))
    if len(hyps) > max_h:
        out.append(finding("warn", "hypotheses", f"{len(hyps)} hypotheses; above {max_h} the list stops being ranked"))
    seen = set()
    confirmed = 0
    for i, h in enumerate(hyps):
        hid = str(h.get("id") or f"#{i + 1}")
        where = f"hypothesis {hid}"
        if hid in seen:
            out.append(finding("error", where, "duplicate hypothesis id"))
        seen.add(hid)
        pred = str(h.get("prediction", ""))
        if not PREDICTION_RE.search(pred):
            out.append(finding("error", where, "prediction is not in 'if <cause> then <observable>' form"))
        stmt = str(h.get("statement", "")).lower()
        if any(w in stmt for w in VAGUE_WORDS):
            out.append(finding("warn", where, "statement uses vague wording; name a mechanism"))
        if not str(h.get("experiment", "")).strip():
            out.append(finding("error", where, "no experiment that could refute it"))
        status = str(h.get("status", "open")).lower()
        if status not in STATUSES:
            out.append(finding("error", where, f"unknown status '{status}'"))
        if status in ("confirmed", "refuted") and not str(h.get("evidence", "")).strip():
            out.append(finding("error", where, f"marked {status} with no recorded evidence"))
        prior = h.get("prior")
        if not isinstance(prior, (int, float)) or not 0 < float(prior) <= 1:
            out.append(finding("warn", where, "prior missing or outside (0, 1]; ranking uses 0.2"))
        confirmed += status == "confirmed"
    if confirmed > 1:
        out.append(finding("warn", "hypotheses", f"{confirmed} confirmed causes; check they are not one cause twice"))
    return out


def check_experiments(exps: List[Dict[str, Any]], hyp_ids: set, stop_after: int) -> List[Dict[str, str]]:
    """Check one-variable discipline and the no-progress stop rule."""
    out: List[Dict[str, str]] = []
    streak = 0
    for i, e in enumerate(exps):
        where = f"experiment {i + 1}"
        if str(e.get("hypothesis", "")) not in hyp_ids:
            out.append(finding("error", where, "not linked to a listed hypothesis; probes must test a prediction"))
        changed = e.get("variables_changed", [])
        if isinstance(changed, list) and len(changed) > 1:
            out.append(finding("error", where,
                               f"changed {len(changed)} variables ({', '.join(map(str, changed))}); change one"))
        result = str(e.get("result", "")).lower()
        streak = streak + 1 if result in ("inconclusive", "") else 0
    if streak >= stop_after:
        out.append(finding("error", "experiments",
                           f"{streak} inconclusive experiments in a row; stop rule hit: re-check the repro or escalate"))
    return out


def rank(hyps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank open hypotheses by prior divided by experiment cost in minutes."""
    ranked = []
    for h in hyps:
        if str(h.get("status", "open")).lower() not in ("open", "inconclusive"):
            continue
        prior = h.get("prior")
        prior = float(prior) if isinstance(prior, (int, float)) and 0 < float(prior) <= 1 else 0.2
        cost = float(h.get("cost_minutes", 30) or 30)
        ranked.append({"id": h.get("id"), "statement": h.get("statement", ""),
                       "prior": prior, "cost_minutes": cost, "score": round(prior / max(cost, 1.0) * 60, 3)})
    ranked.sort(key=lambda r: (-r["score"], str(r["id"])))
    return ranked


def analyse(data: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """Run all checks and return the report."""
    hyps = data.get("hypotheses", []) or []
    findings = check_repro(data.get("repro", {}) or {}, args.max_runtime, args.min_red_rate)
    findings += check_hypotheses(hyps, args.min_hypotheses, args.max_hypotheses)
    findings += check_experiments(data.get("experiments", []) or [],
                                  {str(h.get("id")) for h in hyps}, args.stop_after)
    if data.get("status") == "fixed":
        reg = data.get("regression_test", {}) or {}
        if not reg.get("path") and not reg.get("no_seam_reason"):
            findings.append(finding("error", "regression_test",
                                    "marked fixed with no regression test and no recorded reason"))
        elif reg.get("path") and not reg.get("seen_failing"):
            findings.append(finding("error", "regression_test", "regression test was never seen failing"))
        if data.get("instrumentation_tag") and not data.get("instrumentation_removed"):
            findings.append(finding("error", "instrumentation", "tagged debug output not confirmed removed"))
    errors = sum(f["level"] == "error" for f in findings)
    ranked = rank(hyps)
    return {"bug": data.get("bug", ""), "errors": errors,
            "warnings": sum(f["level"] == "warn" for f in findings),
            "verdict": "FAIL" if errors else "PASS", "findings": findings,
            "next_to_test": ranked[0] if ranked else None, "ranking": ranked}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Diagnosis log: {report['bug'] or '(unnamed bug)'}")
    print(f"Verdict: {report['verdict']}  ({report['errors']} error(s), {report['warnings']} warning(s))")
    for f in report["findings"]:
        print(f"  [{f['level'].upper():5}] {f['where']}: {f['message']}")
    if report["ranking"]:
        print("\nOpen hypotheses by information per hour (prior / cost):")
        for r in report["ranking"]:
            print(f"  {str(r['id']):>4}  score {r['score']:<6} prior {r['prior']:<4} "
                  f"cost {r['cost_minutes']:g}m  {r['statement']}")
        print(f"\nTest next: {report['next_to_test']['id']}")


def main() -> None:
    """Parse arguments, load the log, and exit with the gate result."""
    p = argparse.ArgumentParser(description="Validate a diagnosis log and rank open hypotheses.")
    p.add_argument("--input", required=True, help="diagnosis log JSON file")
    p.add_argument("--max-runtime", type=float, default=30.0, help="loop runtime budget in seconds (default 30)")
    p.add_argument("--min-red-rate", type=float, default=0.3, help="minimum red-run fraction (default 0.3)")
    p.add_argument("--min-hypotheses", type=int, default=3, help="minimum hypotheses before testing (default 3)")
    p.add_argument("--max-hypotheses", type=int, default=6, help="warn above this many (default 6)")
    p.add_argument("--stop-after", type=int, default=4, help="inconclusive streak that trips the stop rule")
    p.add_argument("--format", choices=("text", "json"), default="text", help="output format (default text)")
    args = p.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("top level must be a JSON object")
    except (OSError, ValueError) as exc:
        print(f"error: cannot read diagnosis log {args.input}: {exc}", file=sys.stderr)
        sys.exit(2)
    report = analyse(data, args)
    output(report, args.format)
    sys.exit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
