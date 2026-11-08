#!/usr/bin/env python3
"""Validate a wayfinding decision map and compute its dependency order and frontier.

Reads a JSON map (destination, fog, out-of-scope list, decision and implementation
tickets with blocking links) and checks the structure that makes the map usable:
no cycles, no dangling ids, every decision ticket answerable (question, owner,
options), every resolved decision recorded, and no implementation ticket built on
a decision that has not been made. Prints a stable topological order (Kahn's
algorithm, ties broken by id) and the current frontier: open, unblocked,
unclaimed tickets. Deterministic: no clock reads unless --today is passed.

Usage:
    python3 decision_map_validator.py --input assets/sample_decision_map_clean.json
    python3 decision_map_validator.py --input map.json --today 2026-11-08 --format json

Exit codes: 0 no error findings, 1 at least one error finding, 2 bad input.
"""

import argparse
import heapq
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

KINDS = {"decision", "implementation"}
DECISION_TYPES = {"research", "prototype", "discussion", "enabling-task"}
DECISION_STATUSES = {"open", "claimed", "resolved", "out-of-scope"}
IMPL_STATUSES = {"open", "claimed", "in-progress", "done", "out-of-scope"}
CLOSED = {"resolved", "done", "out-of-scope"}
NEEDS_OPTIONS = {"discussion", "prototype"}


class InputError(Exception):
    """Raised when the map file cannot be used at all."""


def load_map(path: Path) -> Dict[str, Any]:
    """Load and shape-check the decision map JSON."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise InputError(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        raise InputError(f"{path.name} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise InputError("map must be a JSON object with 'destination' and 'tickets'")
    tickets = data.get("tickets")
    if not isinstance(tickets, list) or not all(isinstance(t, dict) for t in tickets):
        raise InputError("'tickets' must be a list of objects")
    return data


def finding(sev: str, ticket: str, msg: str) -> Dict[str, str]:
    """Build one finding record."""
    return {"severity": sev, "ticket": ticket, "message": msg}


def check_ticket(t: Dict[str, Any], by_id: Dict[str, Dict[str, Any]],
                 today: Optional[date]) -> List[Dict[str, str]]:
    """Check one ticket's own fields and its links to other tickets."""
    out: List[Dict[str, str]] = []
    tid = str(t.get("id", "?"))
    kind = t.get("kind")
    status = t.get("status", "open")
    if kind not in KINDS:
        return [finding("error", tid, f"kind must be one of {sorted(KINDS)}, got {kind!r}")]
    for ref in t.get("blocked_by", []) or []:
        if ref not in by_id:
            out.append(finding("error", tid, f"blocked_by references unknown ticket {ref!r}"))
    if status == "claimed" and not t.get("claimed_by"):
        out.append(finding("warn", tid, "status is claimed but claimed_by is empty — nobody knows who holds it"))

    if kind == "decision":
        if status not in DECISION_STATUSES:
            out.append(finding("error", tid, f"decision status {status!r} not in {sorted(DECISION_STATUSES)}"))
        dtype = t.get("type")
        if dtype not in DECISION_TYPES:
            out.append(finding("error", tid, f"decision type {dtype!r} not in {sorted(DECISION_TYPES)}"))
        if not str(t.get("question", "")).strip():
            out.append(finding("error", tid, "decision ticket has no question"))
        elif not str(t["question"]).strip().endswith("?"):
            out.append(finding("warn", tid, "question is not phrased as a question — state what must be decided"))
        if not str(t.get("owner", "")).strip():
            out.append(finding("error", tid, "decision ticket has no owner — nobody can make the call"))
        options = t.get("options") or []
        if dtype in NEEDS_OPTIONS and len(options) < 2:
            out.append(finding("error", tid, f"{dtype} decision lists {len(options)} option(s); needs at least 2"))
        if status == "resolved" and not str(t.get("resolution", "")).strip():
            out.append(finding("error", tid, "resolved without a recorded resolution — the decision is lost"))
        decide_by = t.get("decide_by")
        if today and decide_by and status in {"open", "claimed"}:
            try:
                if date.fromisoformat(str(decide_by)) < today:
                    out.append(finding("warn", tid, f"decide_by {decide_by} has passed and the decision is still {status}"))
            except ValueError:
                out.append(finding("error", tid, f"decide_by {decide_by!r} is not YYYY-MM-DD"))
        return out

    if status not in IMPL_STATUSES:
        out.append(finding("error", tid, f"implementation status {status!r} not in {sorted(IMPL_STATUSES)}"))
    derived = t.get("derived_from") or []
    if not derived:
        out.append(finding("error", tid, "implementation ticket traces to no decision (orphan) — add derived_from"))
    for ref in derived:
        src = by_id.get(ref)
        if src is None:
            out.append(finding("error", tid, f"derived_from references unknown ticket {ref!r}"))
        elif src.get("kind") == "decision" and src.get("status") != "resolved":
            out.append(finding("error", tid, f"built on decision {ref} which is still {src.get('status', 'open')}"))
    for ref in t.get("blocked_by", []) or []:
        src = by_id.get(ref)
        if src and src.get("kind") == "decision" and src.get("status") != "resolved":
            out.append(finding("error", tid, f"blocked by unresolved decision {ref} — implementation is premature"))
        if src and status in {"in-progress", "done"} and src.get("status") not in CLOSED:
            out.append(finding("error", tid, f"is {status} while blocker {ref} is still {src.get('status', 'open')}"))
    return out


def find_cycles(by_id: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """Return blocking cycles found by depth-first search, each as a closed path."""
    cycles: List[List[str]] = []
    state: Dict[str, int] = {}
    stack: List[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for nxt in sorted(by_id[node].get("blocked_by", []) or []):
            if nxt not in by_id:
                continue
            if state.get(nxt) == 1:
                cycles.append(stack[stack.index(nxt):] + [nxt])
            elif nxt not in state:
                visit(nxt)
        stack.pop()
        state[node] = 2

    for tid in sorted(by_id):
        if tid not in state:
            visit(tid)
    return cycles


def topo_order(by_id: Dict[str, Dict[str, Any]]) -> List[str]:
    """Kahn's algorithm over blocking edges; ties broken by id for stable output."""
    indeg = {tid: 0 for tid in by_id}
    dependents: Dict[str, List[str]] = {tid: [] for tid in by_id}
    for tid, t in by_id.items():
        for ref in set(t.get("blocked_by", []) or []):
            if ref in by_id:
                indeg[tid] += 1
                dependents[ref].append(tid)
    heap = [tid for tid, d in indeg.items() if d == 0]
    heapq.heapify(heap)
    order: List[str] = []
    while heap:
        tid = heapq.heappop(heap)
        order.append(tid)
        for dep in dependents[tid]:
            indeg[dep] -= 1
            if indeg[dep] == 0:
                heapq.heappush(heap, dep)
    return order


def frontier(by_id: Dict[str, Dict[str, Any]]) -> List[str]:
    """Open, unclaimed tickets whose blockers are all closed. Decisions listed first."""
    ready = []
    for tid, t in by_id.items():
        if t.get("status", "open") != "open":
            continue
        refs = t.get("blocked_by", []) or []
        if any(r not in by_id for r in refs):
            continue  # an unknown blocker cannot be shown closed, so the ticket is not takeable
        if all(by_id[r].get("status") in CLOSED for r in refs):
            ready.append((0 if t.get("kind") == "decision" else 1, tid))
    return [tid for _, tid in sorted(ready)]


def analyse(data: Dict[str, Any], today: Optional[date]) -> Dict[str, Any]:
    """Run every map-level and ticket-level check and assemble the report."""
    findings: List[Dict[str, str]] = []
    if not str(data.get("destination", "")).strip():
        findings.append(finding("error", "map", "no destination — the map cannot say when it is finished"))
    by_id: Dict[str, Dict[str, Any]] = {}
    for t in data["tickets"]:
        tid = str(t.get("id", "")).strip()
        if not tid:
            findings.append(finding("error", "map", f"ticket without id: {t.get('title', '?')!r}"))
            continue
        if tid in by_id:
            findings.append(finding("error", tid, "duplicate ticket id"))
        by_id[tid] = t
    for tid in sorted(by_id):
        findings.extend(check_ticket(by_id[tid], by_id, today))
    for cyc in find_cycles(by_id):
        findings.append(finding("error", cyc[0], "blocking cycle: " + " -> ".join(cyc)))

    linked: Set[str] = set()
    for tid, t in by_id.items():
        refs = list(t.get("blocked_by", []) or []) + list(t.get("derived_from", []) or [])
        if refs:
            linked.add(tid)
            linked.update(refs)
    decisions = [tid for tid, t in by_id.items() if t.get("kind") == "decision"]
    if len(by_id) > 1:
        for tid in sorted(decisions):
            if tid not in linked:
                findings.append(finding("warn", tid, "isolated decision — no links in or out; confirm it serves the destination"))
    converted = {r for t in by_id.values() for r in t.get("derived_from", []) or []}
    for tid in sorted(decisions):
        t = by_id[tid]
        if t.get("status") == "resolved" and tid not in converted and not t.get("no_build"):
            findings.append(finding("warn", tid, "resolved decision not yet converted into a tracer-bullet ticket"))

    ready = frontier(by_id)
    open_ids = [tid for tid, t in by_id.items() if t.get("status", "open") not in CLOSED]
    if open_ids and not ready and not any(by_id[t].get("status") in {"claimed", "in-progress"} for t in open_ids):
        findings.append(finding("warn", "map", "frontier is empty but work remains — the map is stalled"))
    order = topo_order(by_id)
    findings.sort(key=lambda f: (0 if f["severity"] == "error" else 1, f["ticket"], f["message"]))
    errors = sum(1 for f in findings if f["severity"] == "error")
    return {
        "map": data.get("map", ""), "destination": data.get("destination", ""),
        "counts": {
            "tickets": len(by_id), "decisions": len(decisions),
            "decisions_resolved": sum(1 for d in decisions if by_id[d].get("status") == "resolved"),
            "implementation": len(by_id) - len(decisions),
            "fog_items": len(data.get("fog", []) or []),
            "out_of_scope": len(data.get("out_of_scope", []) or []),
        },
        "order": order, "unordered": sorted(set(by_id) - set(order)),
        "frontier": ready, "findings": findings,
        "errors": errors, "warnings": len(findings) - errors, "passed": errors == 0,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    c = report["counts"]
    print(f"Decision map: {report['map'] or '(unnamed)'}")
    print(f"Destination:  {report['destination'] or '(missing)'}")
    print(f"Tickets: {c['tickets']}  decisions {c['decisions_resolved']}/{c['decisions']} resolved, "
          f"implementation {c['implementation']}, fog {c['fog_items']}, out of scope {c['out_of_scope']}")
    print("\nDependency order: " + (" -> ".join(report["order"]) or "(none)"))
    if report["unordered"]:
        print("Cannot order (in or behind a cycle): " + ", ".join(report["unordered"]))
    print("Frontier (take next): " + (", ".join(report["frontier"]) or "(empty)"))
    print(f"\nFindings: {report['errors']} error(s), {report['warnings']} warning(s)")
    for f in report["findings"]:
        print(f"  [{f['severity']:5}] {f['ticket']:<6} {f['message']}")
    print("\nRESULT: " + ("PASS" if report["passed"] else "FAIL — fix errors before taking the next ticket"))


def main() -> None:
    """Parse arguments, validate the map, print the report, exit by contract."""
    parser = argparse.ArgumentParser(description="Validate a decision map; print dependency order and frontier.")
    parser.add_argument("--input", required=True, help="path to the decision map JSON")
    parser.add_argument("--today", help="YYYY-MM-DD; enables overdue decide_by warnings")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        today = date.fromisoformat(args.today) if args.today else None
        report = analyse(load_map(Path(args.input)), today)
    except ValueError as exc:
        print(f"error: bad --today value: {exc}", file=sys.stderr)
        sys.exit(2)
    except (InputError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
