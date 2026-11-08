#!/usr/bin/env python3
"""Check a plan-grilling question log for coverage, ordering and closure.

Reads a JSON question log and reports taxonomy coverage, questions asked before
their prerequisites were settled, decisions that were silently assumed, facts
that were pushed onto the user, dependency cycles, and the current frontier —
the questions whose prerequisites are all settled and that belong in the next
round. Deterministic: no clock reads, no network.

Usage:
    python3 question_log_checker.py --input assets/sample_question_log.json
    python3 question_log_checker.py --input log.json --stage round --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

CORE_CATEGORIES = ["goal", "users", "constraints", "failure_modes",
                   "reversibility", "sequencing", "unknowns"]
EXTRA_CATEGORIES = ["success", "ownership"]
STATUSES = {"open", "asked", "answered", "deferred", "assumed"}
SETTLED = {"answered", "assumed"}
KINDS = {"decision", "fact"}


def load_log(path: Path) -> Dict[str, Any]:
    """Load the question log and check its top-level shape."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError("question log must be an object with a 'questions' list")
    if not data["questions"]:
        raise ValueError("question log has no questions")
    return data


def finding(sev: str, qid: str, msg: str) -> Dict[str, str]:
    """Build one finding record."""
    return {"severity": sev, "question": qid, "message": msg}


def validate_fields(questions: List[Dict[str, Any]], findings: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    """Validate per-question fields and return an id -> question index."""
    index: Dict[str, Dict[str, Any]] = {}
    for pos, q in enumerate(questions, start=1):
        qid = str(q.get("id") or f"#{pos}")
        if qid in index:
            findings.append(finding("error", qid, "duplicate question id"))
            continue
        index[qid] = q
        if not str(q.get("question", "")).strip():
            findings.append(finding("error", qid, "question text is empty"))
        cat = q.get("category")
        if cat not in CORE_CATEGORIES + EXTRA_CATEGORIES:
            findings.append(finding("error", qid, f"unknown category {cat!r}"))
        if q.get("status") not in STATUSES:
            findings.append(finding("error", qid, f"status must be one of {sorted(STATUSES)}"))
        if q.get("kind") not in KINDS:
            findings.append(finding("error", qid, "kind must be 'decision' or 'fact'"))
        if not isinstance(q.get("depends_on", []), list):
            findings.append(finding("error", qid, "depends_on must be a list"))
            q["depends_on"] = []
    return index


def find_cycles(index: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """Return dependency cycles found with a colouring depth-first search."""
    colour: Dict[str, int] = {qid: 0 for qid in index}
    cycles: List[List[str]] = []

    def visit(node: str, stack: List[str]) -> None:
        colour[node] = 1
        stack.append(node)
        for dep in index[node].get("depends_on", []):
            if dep not in index:
                continue
            if colour[dep] == 1:
                cycles.append(stack[stack.index(dep):] + [dep])
            elif colour[dep] == 0:
                visit(dep, stack)
        stack.pop()
        colour[node] = 2

    for qid in sorted(index):
        if colour[qid] == 0:
            visit(qid, [])
    return cycles


def check_questions(index: Dict[str, Dict[str, Any]], stage: str, findings: List[Dict[str, str]]) -> None:
    """Apply ordering, recommendation, assumption and closure rules."""
    for qid, q in index.items():
        status, kind = q.get("status"), q.get("kind")
        deps = q.get("depends_on", [])
        for dep in deps:
            if dep not in index:
                findings.append(finding("error", qid, f"depends on unknown question {dep!r}"))
        asked = status in {"asked", "answered", "deferred"} and q.get("resolved_by") != "agent"
        if asked and isinstance(q.get("round"), int):
            for dep in deps:
                d = index.get(dep)
                if d is None:
                    continue
                d_round = d.get("round") if isinstance(d.get("round"), int) else 0
                if d.get("status") not in SETTLED or d_round >= q["round"]:
                    findings.append(finding("error", qid,
                                            f"asked in round {q['round']} before prerequisite {dep} was settled"))
        if kind == "decision" and status != "open" and not str(q.get("recommended", "")).strip():
            findings.append(finding("error", qid, "decision put to the user without a recommended answer"))
        if kind == "decision" and status == "assumed" and not q.get("confirmed"):
            findings.append(finding("error", qid,
                                    "decision recorded as an assumption the user never confirmed"))
        if kind == "fact" and q.get("resolved_by") == "user":
            findings.append(finding("warn", qid, "fact was put to the user; look facts up before asking"))
        if kind == "fact" and status == "assumed" and not q.get("source"):
            findings.append(finding("warn", qid, "fact assumed with no source; verify it or log where it came from"))
        if status == "answered" and not str(q.get("answer", "")).strip():
            findings.append(finding("error", qid, "marked answered but the answer is empty"))
        if status == "deferred" and not (q.get("owner") and q.get("reason")):
            findings.append(finding("error", qid, "deferred without both an owner and a reason"))
        if stage == "final" and status in {"open", "asked"}:
            findings.append(finding("error", qid, f"still {status} at the final gate"))


def coverage(index: Dict[str, Dict[str, Any]], findings: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    """Count settled questions per category and flag uncovered categories."""
    table: Dict[str, Dict[str, int]] = {}
    for cat in CORE_CATEGORIES + EXTRA_CATEGORIES:
        qs = [q for q in index.values() if q.get("category") == cat]
        settled = sum(1 for q in qs if q.get("status") in SETTLED)
        table[cat] = {"total": len(qs), "settled": settled}
        if cat in CORE_CATEGORIES and not qs:
            findings.append(finding("error", "-", f"core category '{cat}' has no questions"))
        elif cat in EXTRA_CATEGORIES and not qs:
            findings.append(finding("warn", "-", f"category '{cat}' was never asked about"))
    return table


def frontier(index: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """Split open questions into the next round and the still-blocked set."""
    dependents: Dict[str, int] = {qid: 0 for qid in index}
    for q in index.values():
        for dep in q.get("depends_on", []):
            if dep in dependents:
                dependents[dep] += 1
    ready: List[str] = []
    blocked: List[str] = []
    for qid, q in index.items():
        if q.get("status") != "open":
            continue
        deps = [d for d in q.get("depends_on", []) if d in index]
        if all(index[d].get("status") in SETTLED for d in deps):
            ready.append(qid)
        else:
            blocked.append(qid)
    ready.sort(key=lambda i: (-dependents[i], i))
    return {"next_round": ready, "blocked": sorted(blocked)}


def analyse(data: Dict[str, Any], stage: str) -> Dict[str, Any]:
    """Run every check and assemble the report."""
    findings: List[Dict[str, str]] = []
    index = validate_fields(data["questions"], findings)
    for cycle in find_cycles(index):
        findings.append(finding("error", cycle[0], "dependency cycle: " + " -> ".join(cycle)))
    check_questions(index, stage, findings)
    cov = coverage(index, findings)
    front = frontier(index)
    statuses: Dict[str, int] = {s: 0 for s in sorted(STATUSES)}
    for q in index.values():
        if q.get("status") in statuses:
            statuses[q["status"]] += 1
    open_decisions: Set[str] = {qid for qid, q in index.items()
                                if q.get("kind") == "decision" and q.get("status") in {"open", "asked"}}
    errors = sum(1 for f in findings if f["severity"] == "error")
    order = {"error": 0, "warn": 1}
    findings.sort(key=lambda f: (order[f["severity"]], f["question"]))
    return {
        "subject": data.get("subject", "(untitled)"),
        "stage": stage,
        "questions": len(index),
        "status_counts": statuses,
        "coverage": cov,
        "frontier": front,
        "open_decisions": sorted(open_decisions),
        "done": not front["next_round"] and not front["blocked"] and not open_decisions,
        "errors": errors,
        "warnings": len(findings) - errors,
        "passed": errors == 0,
        "findings": findings,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    verdict = "PASS" if report["passed"] else "FAIL"
    print(f"{verdict}  {report['subject']}  (stage: {report['stage']}, {report['questions']} questions, "
          f"{report['errors']} errors, {report['warnings']} warnings)")
    print("\nCoverage (settled / asked)")
    for cat, row in report["coverage"].items():
        bar = "#" * row["settled"] + "." * (row["total"] - row["settled"])
        print(f"  {cat:<14} {row['settled']}/{row['total']}  {bar}")
    front = report["frontier"]
    print("\nNext round: " + (", ".join(front["next_round"]) or "none"))
    print("Blocked:    " + (", ".join(front["blocked"]) or "none"))
    print("Tree resolved: " + ("yes" if report["done"] else "no"))
    if report["findings"]:
        print("\nFindings")
        for f in report["findings"]:
            print(f"  [{f['severity']:5}] {f['question']:<5} {f['message']}")


def main() -> None:
    """Parse arguments, run the checks and exit with the gate status."""
    parser = argparse.ArgumentParser(description="Check a plan-grilling question log.")
    parser.add_argument("--input", required=True, help="path to the question log JSON")
    parser.add_argument("--stage", choices=["round", "final"], default="final",
                        help="round: structural checks + next round; final: also require closure (default)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        report = analyse(load_log(Path(args.input)), args.stage)
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: {args.input} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
