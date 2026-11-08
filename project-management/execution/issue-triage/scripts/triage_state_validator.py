#!/usr/bin/env python3
"""Validate an issue-triage history against the triage state machine.

Reads a JSON export of issues and external PRs, each with its labels and the
ordered list of state transitions, plus the out-of-scope register. Flags
illegal transitions, broken label invariants (exactly one type and one state
label), ready-for-agent items with no brief, duplicates with no canonical link,
out-of-scope closures missing from the register, bugs accepted without a
reproduction, and needs-info items left past the nudge and close windows.
Deterministic: dates come from the file or --today, never from the clock.

Usage:
    python3 triage_state_validator.py --input assets/sample_triage_history.json
    python3 triage_state_validator.py --input history.json --today 2026-11-08 --format json
    python3 triage_state_validator.py --input history.json --nudge-days 7 --stale-days 21

Exit codes: 0 no errors, 1 at least one error finding, 2 unreadable or invalid input.
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

STATES = {"new", "needs-info", "reproduced", "accepted", "ready-for-agent", "ready-for-human",
          "duplicate", "out-of-scope", "already-implemented", "stale-closed", "resolved"}
TERMINAL = {"duplicate", "out-of-scope", "already-implemented", "stale-closed", "resolved"}
CLOSURES = ["duplicate", "out-of-scope", "already-implemented"]
LEGAL: Dict[str, set] = {
    "new": {"needs-info", "reproduced", "accepted", *CLOSURES},
    "needs-info": {"new", "reproduced", "stale-closed", *CLOSURES},
    "reproduced": {"accepted", "needs-info", "duplicate", "already-implemented"},
    "accepted": {"ready-for-agent", "ready-for-human", "out-of-scope"},
    "ready-for-agent": {"ready-for-human", "accepted", "resolved"},
    "ready-for-human": {"ready-for-agent", "accepted", "resolved"},
    # Reopening a closed item always re-enters at "new" so it is re-triaged.
    "duplicate": {"new"}, "out-of-scope": {"new"}, "already-implemented": {"new"},
    "stale-closed": {"new"}, "resolved": {"new"},
}
NEEDS_REPRO = {"bug"}


def parse_day(value: Any, where: str) -> date:
    """Parse a YYYY-MM-DD (or ISO datetime) string into a date."""
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{where}: bad date {value!r} (expected YYYY-MM-DD)")


def prefixed(labels: List[str], prefix: str) -> List[str]:
    """Return label values carrying a given prefix, with the prefix removed."""
    return [lab[len(prefix):] for lab in labels if isinstance(lab, str) and lab.startswith(prefix)]


def finding(out: List[Dict[str, str]], sev: str, item: str, rule: str, msg: str) -> None:
    """Append one finding record."""
    out.append({"severity": sev, "item": item, "rule": rule, "message": msg})


def register_index(register: List[Dict[str, Any]], out: List[Dict[str, str]]) -> Dict[str, str]:
    """Validate the out-of-scope register and map each listed issue id to its concept."""
    index: Dict[str, str] = {}
    for entry in register:
        concept = str(entry.get("concept") or "").strip()
        if not concept:
            finding(out, "error", "register", "register-concept", "register entry has no concept name")
            continue
        if not str(entry.get("reason") or "").strip():
            finding(out, "error", concept, "register-reason", "register entry has no durable reason")
        if str(entry.get("decision") or "").lower() == "already-implemented":
            finding(out, "error", concept, "register-misuse",
                    "already-implemented work does not belong in the out-of-scope register")
        for ref in entry.get("prior_requests") or []:
            index[str(ref)] = concept
    return index


def check_labels(iid: str, issue: Dict[str, Any], current: str, out: List[Dict[str, str]]) -> str:
    """Enforce one type label, one state label matching history, at most one priority."""
    labels = issue.get("labels") or []
    types, states, prios = prefixed(labels, "type:"), prefixed(labels, "state:"), prefixed(labels, "priority:")
    if len(types) != 1:
        finding(out, "error", iid, "type-label", f"needs exactly one type: label, found {len(types)}")
    if len(states) != 1:
        finding(out, "error", iid, "state-label", f"needs exactly one state: label, found {len(states)}")
    elif current and states[0] != current:
        finding(out, "error", iid, "state-drift",
                f"label says state:{states[0]} but last transition is {current}")
    if len(prios) > 1:
        finding(out, "error", iid, "priority-label", f"{len(prios)} priority labels; keep one")
    if not prios and current in {"accepted", "ready-for-agent", "ready-for-human"}:
        finding(out, "warn", iid, "priority-label", f"{current} item has no priority: label")
    return types[0] if len(types) == 1 else ""


def check_history(iid: str, issue: Dict[str, Any], out: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Walk the transition list and flag illegal moves, gaps, and date regressions."""
    steps = issue.get("transitions") or []
    if not steps:
        finding(out, "error", iid, "history", "no transitions recorded")
        return []
    first = steps[0]
    if first.get("from") not in (None, "") or first.get("to") != "new":
        finding(out, "error", iid, "entry-state", "history must start with a transition into 'new'")
    prev_to: Optional[str] = None
    prev_day: Optional[date] = None
    for n, step in enumerate(steps):
        src, dst = step.get("from"), step.get("to")
        day = parse_day(step.get("at"), f"{iid} transition {n + 1}")
        if dst not in STATES:
            finding(out, "error", iid, "unknown-state", f"transition {n + 1} targets unknown state {dst!r}")
        if n > 0:
            if src != prev_to:
                finding(out, "error", iid, "broken-chain",
                        f"transition {n + 1} starts at {src!r} but previous ended at {prev_to!r}")
            elif src in LEGAL and dst not in LEGAL[src]:
                finding(out, "error", iid, "illegal-transition", f"{src} -> {dst} is not a legal move")
            if src == "needs-info" and dst == "new" and step.get("actor") != issue.get("reporter"):
                finding(out, "warn", iid, "reply-actor",
                        "needs-info -> new should be triggered by the reporter's reply")
        if prev_day and day < prev_day:
            finding(out, "error", iid, "date-order", f"transition {n + 1} is dated before the previous one")
        if dst in TERMINAL - {"resolved"} and not str(step.get("note") or "").strip():
            finding(out, "warn", iid, "closing-note", f"closing as {dst} without an explanatory note")
        prev_to, prev_day = dst, day
    return steps


def check_issue(issue: Dict[str, Any], register: Dict[str, str], today: date,
                nudge: int, stale: int, out: List[Dict[str, str]]) -> None:
    """Run every rule for one issue or PR."""
    iid = str(issue.get("id") or "?")
    kind = issue.get("kind", "issue")
    if kind not in ("issue", "pr"):
        finding(out, "error", iid, "kind", f"kind must be 'issue' or 'pr', got {kind!r}")
    steps = check_history(iid, issue, out)
    current = steps[-1].get("to", "") if steps else ""
    itype = check_labels(iid, issue, current, out)
    visited = [s.get("to") for s in steps]
    if itype in NEEDS_REPRO and "accepted" in visited:
        if "reproduced" not in visited[: visited.index("accepted")]:
            what = "diff verified" if kind == "pr" else "reproduction"
            finding(out, "error", iid, "skipped-repro", f"bug accepted with no {what} on record")
    if current in ("ready-for-agent", "ready-for-human") and not issue.get("brief"):
        finding(out, "error", iid, "missing-brief", f"{current} with no brief attached")
    if current == "ready-for-human" and not str(issue.get("human_reason") or "").strip():
        finding(out, "error", iid, "human-reason", "ready-for-human must say why it cannot be delegated")
    if current == "duplicate":
        canon = str(issue.get("duplicate_of") or "")
        if not canon:
            finding(out, "error", iid, "duplicate-link", "duplicate closed with no canonical issue link")
        elif canon == iid:
            finding(out, "error", iid, "duplicate-link", "duplicate points at itself")
    if current == "out-of-scope" and iid not in register:
        finding(out, "error", iid, "register-missing", "out-of-scope closure has no out-of-scope register entry")
    if current == "already-implemented" and iid in register:
        finding(out, "error", iid, "register-misuse", "already-implemented item is listed in the out-of-scope register")
    if current == "needs-info" and steps:
        waited = (today - parse_day(steps[-1].get("at"), iid)).days
        if waited > stale:
            finding(out, "error", iid, "stale-needs-info",
                    f"in needs-info {waited} days (close policy {stale}); close as stale-closed")
        elif waited > nudge:
            finding(out, "warn", iid, "nudge-needs-info", f"in needs-info {waited} days; nudge the reporter")


def latest_date(issues: List[Dict[str, Any]]) -> date:
    """Return the newest transition date in the file (deterministic default for --today)."""
    days = [parse_day(s.get("at"), "transition") for i in issues for s in (i.get("transitions") or [])]
    if not days:
        raise ValueError("no dated transitions found and no --today given")
    return max(days)


def validate(data: Dict[str, Any], today: Optional[str], nudge: int, stale: int) -> Dict[str, Any]:
    """Validate the whole history and return a report dict."""
    issues = data.get("issues")
    if not isinstance(issues, list) or not issues:
        raise ValueError("input must contain a non-empty 'issues' list")
    out: List[Dict[str, str]] = []
    register = register_index(data.get("out_of_scope_register") or [], out)
    ref_day = parse_day(today, "--today") if today else latest_date(issues)
    for issue in issues:
        check_issue(issue, register, ref_day, nudge, stale, out)
    counts: Dict[str, int] = {}
    for issue in issues:
        steps = issue.get("transitions") or []
        state = steps[-1].get("to", "?") if steps else "?"
        counts[state] = counts.get(state, 0) + 1
    errors = sum(1 for f in out if f["severity"] == "error")
    return {"today": ref_day.isoformat(), "issues": len(issues), "state_counts": counts,
            "errors": errors, "warnings": len(out) - errors, "passed": errors == 0, "findings": out}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    status = "PASS" if report["passed"] else "FAIL"
    print(f"Triage state validation: {status}  ({report['issues']} items, as of {report['today']})")
    print("Queue: " + ", ".join(f"{k}={v}" for k, v in sorted(report["state_counts"].items())))
    print(f"Errors: {report['errors']}  Warnings: {report['warnings']}")
    for f in sorted(report["findings"], key=lambda x: (x["severity"] != "error", x["item"])):
        print(f"  [{f['severity']:5}] {f['item']:<10} {f['rule']:<20} {f['message']}")


def main() -> None:
    """Parse arguments, validate the history, and exit with the gate code."""
    parser = argparse.ArgumentParser(description="Validate issue/PR triage history against the state machine.")
    parser.add_argument("--input", required=True, help="JSON file with 'issues' and optional 'out_of_scope_register'")
    parser.add_argument("--today", help="reference date YYYY-MM-DD (default: newest transition date in the file)")
    parser.add_argument("--nudge-days", type=int, default=7, help="warn when needs-info waits longer (default 7)")
    parser.add_argument("--stale-days", type=int, default=21, help="error when needs-info waits longer (default 21)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("top level must be a JSON object")
        report = validate(data, args.today, args.nudge_days, args.stale_days)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    except (json.JSONDecodeError, ValueError, AttributeError, TypeError) as exc:
        print(f"error: invalid triage history: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
