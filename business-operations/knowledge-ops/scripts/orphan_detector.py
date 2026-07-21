#!/usr/bin/env python3
"""Detect orphan pages, dead links, and hub pages in a knowledge base link graph.

Usage:
    python3 orphan_detector.py --input kb.json [--hub-threshold 3] [--format text|json]

Input JSON shape:
    {"docs": [{"path": "...", "title": "...", "tier": "core",
               "views_90d": 320, "links_to": ["other/path.md"]}]}
"""

import argparse
import json
import sys
from collections import defaultdict
from typing import Any, Dict, List, Set

# Traffic band that separates a findability bug from dead weight.
HIGH_TRAFFIC = 50
LOW_TRAFFIC = 1


def build_graph(docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build inbound and outbound adjacency maps plus the set of known paths."""
    known: Set[str] = {str(d.get("path", "")) for d in docs if d.get("path")}
    outbound: Dict[str, List[str]] = {}
    inbound: Dict[str, List[str]] = defaultdict(list)
    dead: List[Dict[str, str]] = []

    for doc in docs:
        path = str(doc.get("path", ""))
        if not path:
            continue
        targets = doc.get("links_to") or []
        if not isinstance(targets, list):
            raise ValueError(f"{path}: 'links_to' must be an array of paths")
        outbound[path] = [str(t) for t in targets]
        for target in outbound[path]:
            if target == path:
                continue
            if target in known:
                inbound[target].append(path)
            else:
                dead.append({"from": path, "to": target})

    return {"known": known, "outbound": outbound, "inbound": dict(inbound), "dead": dead}


def triage_orphan(views: int) -> Dict[str, str]:
    """Classify an orphan page by traffic and return diagnosis plus action."""
    if views >= HIGH_TRAFFIC:
        return {
            "diagnosis": "findability bug",
            "action": "link from the correct hub urgently - people rely on a page the IA hides",
            "priority": "high",
        }
    if views >= LOW_TRAFFIC:
        return {
            "diagnosis": "bookmark-only survivor",
            "action": "fold into a parent page, or link it from a hub",
            "priority": "medium",
        }
    return {
        "diagnosis": "dead weight",
        "action": "delete - version history already preserves it",
        "priority": "low",
    }


def analyse(docs: List[Dict[str, Any]], hub_threshold: int) -> Dict[str, Any]:
    """Analyse the link graph for orphans, dead links, hubs, and isolated clusters."""
    if not docs:
        raise ValueError("inventory contains no documents")
    graph = build_graph(docs)
    by_path = {str(d.get("path", "")): d for d in docs if d.get("path")}

    orphans: List[Dict[str, Any]] = []
    hubs: List[Dict[str, Any]] = []
    leaves: List[str] = []

    for path, doc in sorted(by_path.items()):
        tier = str(doc.get("tier", "reference")).lower()
        views = int(doc.get("views_90d", 0) or 0)
        in_count = len(graph["inbound"].get(path, []))
        out_count = len(graph["outbound"].get(path, []))

        if in_count == 0 and tier != "archive":
            entry = {"path": path, "title": doc.get("title", ""), "tier": tier,
                     "views_90d": views, "outbound_links": out_count}
            entry.update(triage_orphan(views))
            orphans.append(entry)

        if in_count >= hub_threshold:
            hubs.append({"path": path, "title": doc.get("title", ""), "tier": tier,
                         "inbound_links": in_count, "views_90d": views,
                         "note": "protect: assign a named owner and the Critical SLA"})

        if out_count == 0 and tier != "archive":
            leaves.append(path)

    orphans.sort(key=lambda o: ({"high": 0, "medium": 1, "low": 2}[o["priority"]],
                                -o["views_90d"], o["path"]))
    hubs.sort(key=lambda h: (-h["inbound_links"], h["path"]))

    delete_candidates = [o["path"] for o in orphans if o["priority"] == "low"]
    connectivity = round(
        100.0 * sum(1 for p in by_path if graph["inbound"].get(p)) / len(by_path), 1)

    return {
        "total_docs": len(by_path),
        "total_links": sum(len(v) for v in graph["outbound"].values()),
        "connectivity_pct": connectivity,
        "orphan_count": len(orphans),
        "dead_link_count": len(graph["dead"]),
        "hub_count": len(hubs),
        "leaf_count": len(leaves),
        "orphans": orphans,
        "dead_links": sorted(graph["dead"], key=lambda d: (d["from"], d["to"])),
        "hubs": hubs,
        "leaf_pages": sorted(leaves),
        "delete_candidates": delete_candidates,
        "estimated_page_reduction_pct": round(
            100.0 * len(delete_candidates) / len(by_path), 1),
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the link-graph analysis as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print("Link graph analysis")
    print(f"  {result['total_docs']} docs, {result['total_links']} links, "
          f"connectivity {result['connectivity_pct']}%")
    print(f"  orphans={result['orphan_count']}  dead_links={result['dead_link_count']}  "
          f"hubs={result['hub_count']}  leaf_pages={result['leaf_count']}")

    if result["dead_links"]:
        print("\nDead links (fix these first - cheapest, most visible):")
        for link in result["dead_links"]:
            print(f"  {link['from']} -> {link['to']} (target does not exist)")

    if result["orphans"]:
        print("\nOrphans (nothing links to these):")
        for orphan in result["orphans"]:
            print(f"  [{orphan['priority'].upper():>6}] {orphan['path']} "
                  f"({orphan['tier']}, {orphan['views_90d']} views)")
            print(f"           {orphan['diagnosis']}: {orphan['action']}")

    if result["hubs"]:
        print("\nHub pages:")
        for hub in result["hubs"]:
            print(f"  {hub['inbound_links']} inbound  {hub['path']} - {hub['note']}")

    print(f"\nDeletion candidates: {len(result['delete_candidates'])} pages "
          f"({result['estimated_page_reduction_pct']}% of the KB)")
    for path in result["delete_candidates"]:
        print(f"  {path}")


def main() -> None:
    """Parse arguments, analyse the graph, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Detect orphan pages, dead links, and hubs in a knowledge base.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON inventory with a 'docs' array including 'links_to'")
    parser.add_argument("--hub-threshold", type=int, default=3,
                        help="Inbound-link count at which a page counts as a hub (default: 3)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)

    try:
        docs = payload.get("docs")
        if not isinstance(docs, list):
            raise ValueError("input JSON must contain a 'docs' array")
        result = analyse(docs, args.hub_threshold)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
