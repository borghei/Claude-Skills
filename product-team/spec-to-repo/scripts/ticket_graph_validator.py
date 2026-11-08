#!/usr/bin/env python3
"""Validate a tracer-bullet ticket set: vertical slices, blocking links, and build order.

Reads a JSON ticket set (see assets/sample_tracer_tickets.json) and checks that every
ticket is a thin end-to-end slice through the feature's layers, that blocking links point
at real tickets and form no cycle, and that each ticket carries acceptance criteria. Prints
the build order as waves: wave 1 is the starting frontier (no blockers), wave N can start
once everything before it is done.

Usage:
  python3 ticket_graph_validator.py --input tickets.json
  python3 ticket_graph_validator.py --input tickets.json --max-days 2 --format json

Exit codes: 0 = no errors (warnings allowed), 1 = at least one error, 2 = input could not
be read or parsed. Standard library only; deterministic; no network.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

EXEMPT_KINDS = {"prefactor", "expand", "migrate", "contract", "spike", "integrate"}


def load(path: Path) -> Dict[str, Any]:
    """Load and shape-check the ticket set."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("tickets"), list):
        raise ValueError("expected an object with a 'tickets' list")
    return data


def find_cycle(graph: Dict[str, List[str]]) -> Optional[List[str]]:
    """Return one blocking cycle as a list of ids, or None."""
    state: Dict[str, int] = {}
    stack: List[str] = []

    def visit(node: str) -> Optional[List[str]]:
        state[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            if state.get(nxt, 0) == 0 and nxt in graph:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            found = visit(node)
            if found:
                return found
    return None


def waves(graph: Dict[str, List[str]]) -> List[List[str]]:
    """Group tickets into build waves by longest blocker chain (graph must be acyclic)."""
    depth: Dict[str, int] = {}

    def level(node: str) -> int:
        if node not in depth:
            blockers = [b for b in graph.get(node, []) if b in graph]
            depth[node] = 1 + max((level(b) for b in blockers), default=0)
        return depth[node]

    for node in graph:
        level(node)
    out: List[List[str]] = [[] for _ in range(max(depth.values(), default=0))]
    for node in sorted(depth, key=lambda n: (depth[n], n)):
        out[depth[node] - 1].append(node)
    return out


def validate(data: Dict[str, Any], max_days: float) -> Dict[str, Any]:
    """Run every check and return the report."""
    tickets = data["tickets"]
    layers = [str(x).lower() for x in data.get("layers", [])]
    findings: List[Dict[str, str]] = []

    def add(level: str, tid: str, msg: str) -> None:
        findings.append({"level": level, "ticket": tid, "message": msg})

    ids = [str(t.get("id", "")) for t in tickets]
    for tid in {i for i in ids if ids.count(i) > 1}:
        add("error", tid, "duplicate ticket id")
    graph: Dict[str, List[str]] = {}
    for t in tickets:
        tid = str(t.get("id", "")) or "?"
        kind = str(t.get("kind", "slice")).lower()
        blockers = [str(b) for b in t.get("blocked_by", [])]
        graph[tid] = blockers
        if not t.get("title"):
            add("error", tid, "no title")
        for b in blockers:
            if b not in ids:
                add("error", tid, f"blocked by unknown ticket '{b}'")
            if b == tid:
                add("error", tid, "blocks itself")
        if not t.get("acceptance"):
            add("error", tid, "no acceptance criteria — a slice must be verifiable on its own")
        touched = [str(x).lower() for x in t.get("layers", [])]
        if kind not in EXEMPT_KINDS:
            if layers and len(touched) < min(2, len(layers)):
                add("warn", tid, f"horizontal slice: touches {touched or 'no layers'} of {layers}")
            missing = [x for x in layers if x not in touched]
            if layers and touched and missing and len(touched) >= 2:
                add("info", tid, f"skips layers {missing}; fine if this path genuinely has none")
            if t.get("demoable") is False:
                add("warn", tid, "not demoable — a tracer bullet should show working behaviour end to end")
        days = t.get("estimated_days")
        if isinstance(days, (int, float)) and days > max_days:
            add("warn", tid, f"{days} days exceeds {max_days}; slice thinner")
    first = [t for t in tickets if not t.get("blocked_by")]
    if tickets and not first:
        add("error", "graph", "no ticket is free to start — every ticket has a blocker")
    cycle = find_cycle(graph)
    if cycle:
        add("error", "graph", "blocking cycle: " + " -> ".join(cycle))
    order = [] if cycle else waves(graph)
    fan_in = {tid: sum(1 for bs in graph.values() if tid in bs) for tid in graph}
    hub = max(fan_in, key=lambda k: fan_in[k]) if fan_in else None
    if hub and fan_in[hub] >= max(4, len(tickets) // 2):
        add("warn", hub, f"blocks {fan_in[hub]} tickets — a bottleneck; land it first or split it")
    errors = sum(1 for f in findings if f["level"] == "error")
    return {"feature": data.get("feature", ""), "tickets": len(tickets), "layers": layers,
            "errors": errors, "warnings": sum(1 for f in findings if f["level"] == "warn"),
            "waves": order, "critical_path": len(order), "findings": findings}


def render_text(report: Dict[str, Any]) -> str:
    """Human-readable report."""
    lines = [f"Feature: {report['feature'] or '(unnamed)'} — {report['tickets']} tickets, "
             f"layers {report['layers'] or 'not declared'}",
             f"{report['errors']} errors, {report['warnings']} warnings"]
    if report["waves"]:
        lines.append(f"Build order ({report['critical_path']} waves; wave 1 is the starting frontier):")
        lines += [f"  wave {i}: {', '.join(w)}" for i, w in enumerate(report["waves"], 1)]
    for f in report["findings"]:
        lines.append(f"  [{f['level']:5}] {f['ticket']}: {f['message']}")
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate tracer-bullet tickets and their blocking links.")
    parser.add_argument("--input", required=True, help="ticket set JSON")
    parser.add_argument("--max-days", type=float, default=3.0, help="warn when a ticket estimate exceeds this")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        data = load(Path(args.input))
    except (OSError, ValueError) as exc:
        print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
        sys.exit(2)
    report = validate(data, args.max_days)
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(report))
    sys.exit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
