#!/usr/bin/env python3
"""
Skill Relationship Graph Generator

Analyzes skills in the Claude Skills Library and generates relationship data
based on tag overlap, domain proximity, reference cross-links, and script
similarity.

Usage:
    python scripts/skill_graph.py                              # Full graph (human)
    python scripts/skill_graph.py --format json > skill-graph.json
    python scripts/skill_graph.py --skill engineering/senior-backend
    python scripts/skill_graph.py --format mermaid > docs/skill-graph.mmd
    python scripts/skill_graph.py --top 20
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_DOMAINS = [
    "business-growth", "c-level-advisor", "data-analytics", "engineering",
    "finance", "hr-operations", "marketing", "product-team",
    "project-management", "ra-qm-team", "sales-success",
]

# Minimum shared tags to create a tag-based edge
MIN_TAG_OVERLAP = 2

# Edge weights
WEIGHT_TAG_OVERLAP = 3       # Per shared tag beyond the minimum
WEIGHT_DOMAIN = 1            # Same domain = weak relation
WEIGHT_CROSS_LINK = 5        # Explicit mention of another skill
WEIGHT_SCRIPT_SIMILARITY = 2 # Similar script names

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

USE_COLOR = True


def _c(code: str, text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str: return _c("32", t)
def yellow(t: str) -> str: return _c("33", t)
def cyan(t: str) -> str: return _c("36", t)
def bold(t: str) -> str: return _c("1", t)
def dim(t: str) -> str: return _c("2", t)


# ---------------------------------------------------------------------------
# Skill discovery and parsing
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    """Walk up from this script to find the repo root."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "skills.json").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter fields from SKILL.md content."""
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return meta

    block = match.group(1)

    # name
    m = re.search(r"^name:\s*(.+)", block, re.MULTILINE)
    if m:
        meta["name"] = m.group(1).strip()

    # tags — supports [a, b, c] or multiline list
    m = re.search(r"tags:\s*\[([^\]]*)\]", block)
    if m:
        raw = m.group(1)
        meta["tags"] = [t.strip().strip("'\"") for t in raw.split(",") if t.strip()]
    else:
        # Try multiline YAML list
        m = re.search(r"tags:\s*\n((?:\s+-\s+.+\n?)+)", block)
        if m:
            meta["tags"] = [
                line.strip().lstrip("- ").strip("'\"")
                for line in m.group(1).strip().split("\n")
                if line.strip()
            ]

    # domain
    m = re.search(r"domain:\s*(.+)", block, re.MULTILINE)
    if m:
        meta["domain"] = m.group(1).strip()

    # category
    m = re.search(r"category:\s*(.+)", block, re.MULTILINE)
    if m:
        meta["category"] = m.group(1).strip()

    return meta


def discover_skills(repo_root: Path) -> list[dict]:
    """Scan all domains for skills with SKILL.md files."""
    skills = []

    for domain in VALID_DOMAINS:
        domain_path = repo_root / domain
        if not domain_path.is_dir():
            continue
        for entry in sorted(domain_path.iterdir()):
            skill_md = entry / "SKILL.md"
            if not entry.is_dir() or not skill_md.exists():
                continue

            skill_id = f"{domain}/{entry.name}"
            content = skill_md.read_text(errors="replace")
            meta = parse_frontmatter(content)

            # Collect script names
            scripts_dir = entry / "scripts"
            script_names = []
            if scripts_dir.is_dir():
                script_names = [
                    f.stem for f in scripts_dir.iterdir()
                    if f.suffix == ".py" and f.stem != "__init__"
                ]

            # Find cross-references to other skills (domain/skill-name patterns)
            cross_refs = set()
            for d in VALID_DOMAINS:
                for m in re.finditer(rf"\b{re.escape(d)}/([a-z0-9_-]+)", content):
                    ref_id = f"{d}/{m.group(1)}"
                    if ref_id != skill_id:
                        cross_refs.add(ref_id)

            skills.append({
                "id": skill_id,
                "domain": domain,
                "name": entry.name,
                "tags": meta.get("tags", []),
                "script_names": script_names,
                "cross_refs": list(cross_refs),
                "body": content,
            })

    return skills


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph(skills: list[dict]) -> dict:
    """Build a weighted relationship graph from discovered skills."""
    skill_map = {s["id"]: s for s in skills}
    edges: dict[tuple[str, str], dict] = {}

    def add_edge(a: str, b: str, weight: int, reason: str):
        key = tuple(sorted([a, b]))
        if key not in edges:
            edges[key] = {"weight": 0, "reasons": []}
        edges[key]["weight"] += weight
        if reason not in edges[key]["reasons"]:
            edges[key]["reasons"].append(reason)

    # 1. Tag overlap
    for i, s1 in enumerate(skills):
        tags1 = set(s1["tags"])
        if not tags1:
            continue
        for s2 in skills[i + 1:]:
            tags2 = set(s2["tags"])
            overlap = tags1 & tags2
            if len(overlap) >= MIN_TAG_OVERLAP:
                w = WEIGHT_TAG_OVERLAP * len(overlap)
                add_edge(s1["id"], s2["id"], w, f"tags: {', '.join(sorted(overlap))}")

    # 2. Domain proximity
    domain_groups = defaultdict(list)
    for s in skills:
        domain_groups[s["domain"]].append(s["id"])
    for domain, members in domain_groups.items():
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                add_edge(a, b, WEIGHT_DOMAIN, f"domain: {domain}")

    # 3. Cross-references
    skill_ids = set(skill_map.keys())
    for s in skills:
        for ref in s["cross_refs"]:
            if ref in skill_ids:
                add_edge(s["id"], ref, WEIGHT_CROSS_LINK, "cross-reference")

    # 4. Script name similarity
    for i, s1 in enumerate(skills):
        names1 = set(s1["script_names"])
        if not names1:
            continue
        for s2 in skills[i + 1:]:
            names2 = set(s2["script_names"])
            common = names1 & names2
            if common:
                add_edge(
                    s1["id"], s2["id"],
                    WEIGHT_SCRIPT_SIMILARITY * len(common),
                    f"scripts: {', '.join(sorted(common))}",
                )

    # Build final structure
    nodes = [{"id": s["id"], "domain": s["domain"], "tags": s["tags"]} for s in skills]
    edge_list = []
    for (a, b), data in edges.items():
        if data["weight"] > WEIGHT_DOMAIN:  # Skip domain-only edges to reduce noise
            edge_list.append({
                "source": a,
                "target": b,
                "weight": data["weight"],
                "reasons": data["reasons"],
            })

    edge_list.sort(key=lambda e: e["weight"], reverse=True)

    return {"nodes": nodes, "edges": edge_list}


def get_connections(graph: dict) -> dict[str, list[tuple[str, int]]]:
    """Build adjacency list with weights from graph."""
    adj: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for edge in graph["edges"]:
        adj[edge["source"]].append((edge["target"], edge["weight"]))
        adj[edge["target"]].append((edge["source"], edge["weight"]))
    # Sort each by weight descending
    for k in adj:
        adj[k].sort(key=lambda x: x[1], reverse=True)
    return adj


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def output_json(graph: dict, skill_filter: str | None, top_n: int | None):
    """Print graph as JSON."""
    if skill_filter:
        adj = get_connections(graph)
        related = adj.get(skill_filter, [])
        result = {
            "skill": skill_filter,
            "related": [{"skill": s, "weight": w} for s, w in related],
        }
        print(json.dumps(result, indent=2))
    elif top_n:
        print(json.dumps(format_top(graph, top_n), indent=2))
    else:
        print(json.dumps(graph, indent=2))


def output_mermaid(graph: dict, skill_filter: str | None, top_n: int | None):
    """Print graph as Mermaid diagram syntax."""
    print("graph LR")

    # Determine which edges to include
    if skill_filter:
        adj = get_connections(graph)
        related = adj.get(skill_filter, [])
        edges_to_show = []
        for target, weight in related[:15]:
            edges_to_show.append((skill_filter, target, weight))
    elif top_n:
        # Get top N nodes by connection count
        top_data = format_top(graph, top_n)
        top_ids = {entry["skill"] for entry in top_data}
        edges_to_show = [
            (e["source"], e["target"], e["weight"])
            for e in graph["edges"]
            if e["source"] in top_ids and e["target"] in top_ids
        ][:60]
    else:
        edges_to_show = [
            (e["source"], e["target"], e["weight"])
            for e in graph["edges"][:80]
        ]

    # Node ID sanitizer for Mermaid
    def mid(skill_id: str) -> str:
        return skill_id.replace("/", "_").replace("-", "_")

    seen_nodes = set()
    for src, tgt, weight in edges_to_show:
        for sid in (src, tgt):
            if sid not in seen_nodes:
                label = sid.split("/")[1]
                print(f"    {mid(sid)}[\"{label}\"]")
                seen_nodes.add(sid)
        thickness = "---" if weight < 5 else "===" if weight < 10 else "==="
        print(f"    {mid(src)} {thickness} {mid(tgt)}")

    # Style by domain
    domains_seen = defaultdict(list)
    for sid in seen_nodes:
        d = sid.split("/")[0]
        domains_seen[d].append(mid(sid))

    colors = [
        "#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336",
        "#00BCD4", "#795548", "#607D8B", "#E91E63", "#3F51B5", "#CDDC39",
    ]
    for i, (domain, node_ids) in enumerate(sorted(domains_seen.items())):
        color = colors[i % len(colors)]
        ids = ",".join(node_ids)
        print(f"    style {ids} fill:{color},color:#fff")


def format_top(graph: dict, n: int) -> list[dict]:
    """Return top N most connected skills."""
    counts: dict[str, int] = defaultdict(int)
    total_weight: dict[str, int] = defaultdict(int)
    for edge in graph["edges"]:
        counts[edge["source"]] += 1
        counts[edge["target"]] += 1
        total_weight[edge["source"]] += edge["weight"]
        total_weight[edge["target"]] += edge["weight"]

    ranked = sorted(counts.keys(), key=lambda s: (counts[s], total_weight[s]), reverse=True)
    return [
        {"skill": s, "connections": counts[s], "total_weight": total_weight[s]}
        for s in ranked[:n]
    ]


def output_human(graph: dict, skill_filter: str | None, top_n: int | None):
    """Print human-readable output."""
    if skill_filter:
        adj = get_connections(graph)
        related = adj.get(skill_filter, [])
        if not related:
            print(f"No relationships found for {bold(skill_filter)}")
            return
        print(f"\n{bold(skill_filter)} is related to:\n")
        for target, weight in related:
            # Find reasons
            for edge in graph["edges"]:
                pair = {edge["source"], edge["target"]}
                if pair == {skill_filter, target}:
                    reasons = ", ".join(edge["reasons"])
                    break
            else:
                reasons = ""
            bar = green("█" * min(weight, 20))
            print(f"  {bar} {cyan(target)}  {dim(f'(w={weight}) {reasons}')}")
        print()

    elif top_n:
        top_data = format_top(graph, top_n)
        print(f"\n{bold(f'Top {len(top_data)} Most Connected Skills')}\n")
        for i, entry in enumerate(top_data, 1):
            conn = entry["connections"]
            tw = entry["total_weight"]
            bar = green("█" * min(conn, 30))
            detail = dim(f"{conn} connections, weight {tw}")
            print(f"  {i:>3}. {bar} {cyan(entry['skill'])}  {detail}")
        print()

    else:
        node_count = len(graph["nodes"])
        edge_count = len(graph["edges"])
        print(f"\n{bold('Skill Relationship Graph')}")
        print(f"  Nodes: {node_count}  Edges: {edge_count}\n")

        # Show top 20 edges
        print(bold("  Strongest relationships:\n"))
        for edge in graph["edges"][:20]:
            reasons = ", ".join(edge["reasons"])
            w = edge["weight"]
            detail = dim(f"w={w}  ({reasons})")
            print(f"    {cyan(edge['source'])} <-> {cyan(edge['target'])}  {detail}")
        if edge_count > 20:
            print(f"\n  {dim(f'... and {edge_count - 20} more edges')}")
            print(f"  {dim('Use --format json for full output')}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze and visualize skill relationships in the Claude Skills Library",
        epilog="Example: python scripts/skill_graph.py --skill engineering/senior-backend",
    )
    parser.add_argument(
        "--skill",
        default=None,
        help="Show relationships for a specific skill (domain/name)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="Show top N most connected skills",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json", "mermaid"],
        default="human",
        help="Output format (default: human)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colorized output",
    )

    args = parser.parse_args()

    global USE_COLOR
    if args.no_color or not sys.stdout.isatty():
        USE_COLOR = False

    repo_root = find_repo_root()

    # Discover all skills
    skills = discover_skills(repo_root)
    if not skills:
        print("No skills found. Are you running from the repository root?", file=sys.stderr)
        return 1

    # Validate --skill filter
    if args.skill:
        skill_ids = {s["id"] for s in skills}
        if args.skill not in skill_ids:
            print(f"Skill '{args.skill}' not found.", file=sys.stderr)
            # Suggest close matches
            name_part = args.skill.split("/")[-1] if "/" in args.skill else args.skill
            matches = [s for s in skill_ids if name_part in s]
            if matches:
                print(f"Did you mean: {', '.join(sorted(matches)[:5])}", file=sys.stderr)
            return 1

    # Build graph
    graph = build_graph(skills)

    # Output
    if args.format == "json":
        output_json(graph, args.skill, args.top)
    elif args.format == "mermaid":
        output_mermaid(graph, args.skill, args.top)
    else:
        output_human(graph, args.skill, args.top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
