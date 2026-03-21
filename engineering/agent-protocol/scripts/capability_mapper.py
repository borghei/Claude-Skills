#!/usr/bin/env python3
"""Map and analyze agent capabilities across protocol definitions.

Scans tool schemas, agent cards, and function definitions to produce:
- Capability inventory across agents and protocols
- Conflict detection (duplicate tool names, overlapping capabilities)
- Protocol compatibility matrix
- Gap analysis (missing descriptions, auth, error handling)

Usage:
    python capability_mapper.py *.json
    python capability_mapper.py --scan-dir ./agents/ --json
    python capability_mapper.py agent-card.json mcp-tools.json --detect-conflicts
    python capability_mapper.py --scan-dir ./protocols/ --compatibility-matrix
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Any

# ---------------------------------------------------------------------------
# Protocol detection (same heuristics as protocol_validator)
# ---------------------------------------------------------------------------

def detect_protocol(data: dict) -> str:
    """Detect which agent protocol a JSON document belongs to."""
    if "inputSchema" in data:
        return "mcp"
    if "skills" in data and ("defaultInputModes" in data or "url" in data):
        return "a2a"
    if "parameters" in data and "name" in data and "inputSchema" not in data:
        return "openai"
    if "tools" in data and isinstance(data["tools"], list):
        sample = data["tools"][0] if data["tools"] else {}
        if "inputSchema" in sample:
            return "mcp"
        if "function" in sample:
            return "openai"
    if "functions" in data:
        return "openai"
    return "unknown"


# ---------------------------------------------------------------------------
# Capability extraction
# ---------------------------------------------------------------------------

def extract_capabilities(filepath: str) -> list[dict]:
    """Extract capability entries from a protocol file.

    Returns a list of capability dicts with normalized fields:
    - source_file, protocol, name, description, parameters (list of param names),
      required_params, has_auth, transport
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return [{"source_file": filepath, "error": str(exc)}]

    protocol = detect_protocol(data)
    caps: list[dict] = []

    if protocol == "mcp":
        tools = [data] if "name" in data and "inputSchema" in data else data.get("tools", [data])
        for tool in tools:
            if not isinstance(tool, dict) or "name" not in tool:
                continue
            schema = tool.get("inputSchema", {})
            props = list(schema.get("properties", {}).keys())
            required = schema.get("required", [])
            caps.append({
                "source_file": filepath,
                "protocol": "mcp",
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "parameters": props,
                "required_params": required,
                "has_auth": False,
                "transport": "stdio/sse",
            })

    elif protocol == "a2a":
        card_name = data.get("name", "")
        auth = data.get("authentication", {})
        has_auth = bool(auth.get("schemes"))
        caps_section = data.get("capabilities", {})
        streaming = caps_section.get("streaming", False)

        for skill in data.get("skills", []):
            caps.append({
                "source_file": filepath,
                "protocol": "a2a",
                "name": f"{card_name}/{skill.get('id', skill.get('name', ''))}",
                "description": skill.get("description", ""),
                "parameters": [],
                "required_params": [],
                "has_auth": has_auth,
                "transport": "http+json-rpc",
                "tags": skill.get("tags", []),
                "streaming": streaming,
                "agent_name": card_name,
                "agent_url": data.get("url", ""),
            })

        # If no skills declared, still register the agent
        if not data.get("skills"):
            caps.append({
                "source_file": filepath,
                "protocol": "a2a",
                "name": card_name,
                "description": data.get("description", ""),
                "parameters": [],
                "required_params": [],
                "has_auth": has_auth,
                "transport": "http+json-rpc",
                "tags": [],
                "streaming": streaming,
                "agent_name": card_name,
                "agent_url": data.get("url", ""),
            })

    elif protocol == "openai":
        funcs: list[dict] = []
        if "function" in data:
            funcs = [data["function"]]
        elif "functions" in data:
            funcs = data["functions"]
        elif "tools" in data:
            funcs = [t.get("function", t) for t in data["tools"]]
        elif "name" in data:
            funcs = [data]

        for func in funcs:
            params = func.get("parameters", {})
            props = list(params.get("properties", {}).keys())
            required = params.get("required", [])
            caps.append({
                "source_file": filepath,
                "protocol": "openai",
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "parameters": props,
                "required_params": required,
                "has_auth": False,
                "transport": "http-rest",
                "strict": func.get("strict", False),
            })

    else:
        caps.append({"source_file": filepath, "error": f"Unknown protocol format"})

    return caps


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def detect_conflicts(capabilities: list[dict]) -> list[dict]:
    """Find duplicate or overlapping tool names across files."""
    conflicts: list[dict] = []
    name_map: dict[str, list[dict]] = defaultdict(list)

    for cap in capabilities:
        if "error" in cap:
            continue
        base_name = cap["name"].split("/")[-1]  # strip agent prefix for A2A
        name_map[base_name].append(cap)

    for name, entries in name_map.items():
        if len(entries) > 1:
            sources = [{"file": e["source_file"], "protocol": e["protocol"]} for e in entries]
            # Check if descriptions are semantically similar (simple word overlap)
            descs = [set(e.get("description", "").lower().split()) for e in entries]
            overlap_scores = []
            for i in range(len(descs)):
                for j in range(i + 1, len(descs)):
                    if descs[i] and descs[j]:
                        intersection = descs[i] & descs[j]
                        union = descs[i] | descs[j]
                        score = len(intersection) / len(union) if union else 0
                        overlap_scores.append(score)

            avg_overlap = sum(overlap_scores) / len(overlap_scores) if overlap_scores else 0

            conflicts.append({
                "name": name,
                "count": len(entries),
                "sources": sources,
                "description_similarity": round(avg_overlap, 2),
                "likely_duplicate": avg_overlap > 0.5,
                "protocols": list(set(e["protocol"] for e in entries)),
            })

    return conflicts


def build_compatibility_matrix(capabilities: list[dict]) -> dict:
    """Build a protocol compatibility analysis."""
    protocols: dict[str, list[dict]] = defaultdict(list)
    for cap in capabilities:
        if "error" not in cap:
            protocols[cap["protocol"]].append(cap)

    matrix: dict[str, Any] = {
        "protocols_found": list(protocols.keys()),
        "tool_counts": {p: len(caps) for p, caps in protocols.items()},
        "total_capabilities": sum(len(caps) for caps in protocols.values()),
    }

    # Cross-protocol bridging analysis
    bridge_candidates: list[dict] = []
    all_names: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for cap in capabilities:
        if "error" in cap:
            continue
        base_name = cap["name"].split("/")[-1]
        all_names[base_name][cap["protocol"]].append(cap["source_file"])

    for name, proto_map in all_names.items():
        if len(proto_map) > 1:
            bridge_candidates.append({
                "capability": name,
                "available_in": {p: files for p, files in proto_map.items()},
                "bridge_needed": False,
            })
        elif len(proto_map) == 1:
            proto = list(proto_map.keys())[0]
            missing = [p for p in protocols.keys() if p != proto]
            if missing:
                bridge_candidates.append({
                    "capability": name,
                    "available_in": {proto: proto_map[proto]},
                    "bridge_needed": True,
                    "missing_protocols": missing,
                })

    matrix["bridge_analysis"] = bridge_candidates

    # Feature comparison
    features: dict[str, dict[str, Any]] = {}
    for proto, caps in protocols.items():
        has_auth = any(c.get("has_auth") for c in caps)
        has_streaming = any(c.get("streaming") for c in caps)
        avg_params = sum(len(c.get("parameters", [])) for c in caps) / len(caps) if caps else 0
        desc_coverage = sum(1 for c in caps if c.get("description")) / len(caps) if caps else 0

        features[proto] = {
            "tool_count": len(caps),
            "has_authentication": has_auth,
            "has_streaming": has_streaming,
            "avg_parameters_per_tool": round(avg_params, 1),
            "description_coverage": f"{desc_coverage:.0%}",
        }
    matrix["protocol_features"] = features

    return matrix


def run_gap_analysis(capabilities: list[dict]) -> dict:
    """Identify quality gaps across all capabilities."""
    gaps: dict[str, list[dict]] = {
        "missing_description": [],
        "no_parameters": [],
        "no_required_params": [],
        "short_description": [],
        "no_auth": [],
    }

    for cap in capabilities:
        if "error" in cap:
            continue

        ref = {"name": cap["name"], "file": cap["source_file"], "protocol": cap["protocol"]}

        if not cap.get("description"):
            gaps["missing_description"].append(ref)
        elif len(cap.get("description", "")) < 30:
            gaps["short_description"].append(ref)

        if not cap.get("parameters"):
            gaps["no_parameters"].append(ref)
        elif not cap.get("required_params"):
            gaps["no_required_params"].append(ref)

        if cap["protocol"] in ("a2a",) and not cap.get("has_auth"):
            gaps["no_auth"].append(ref)

    summary: dict[str, Any] = {}
    for gap_type, entries in gaps.items():
        summary[gap_type] = {
            "count": len(entries),
            "items": entries,
        }

    total_caps = sum(1 for c in capabilities if "error" not in c)
    total_issues = sum(len(v) for v in gaps.values())
    summary["quality_score"] = round(
        max(0, (1 - total_issues / max(total_caps * 5, 1))) * 100, 1
    )

    return summary


def build_inventory(capabilities: list[dict]) -> dict:
    """Build a structured inventory of all capabilities."""
    by_protocol: dict[str, list[dict]] = defaultdict(list)
    by_file: dict[str, list[dict]] = defaultdict(list)

    errors: list[dict] = []

    for cap in capabilities:
        if "error" in cap:
            errors.append(cap)
            continue
        entry = {
            "name": cap["name"],
            "description": cap.get("description", "")[:120],
            "protocol": cap["protocol"],
            "parameter_count": len(cap.get("parameters", [])),
            "required_params": len(cap.get("required_params", [])),
            "has_auth": cap.get("has_auth", False),
            "transport": cap.get("transport", "unknown"),
        }
        by_protocol[cap["protocol"]].append(entry)
        by_file[cap["source_file"]].append(entry)

    return {
        "total_capabilities": sum(len(v) for v in by_protocol.values()),
        "by_protocol": dict(by_protocol),
        "by_file": dict(by_file),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_human_inventory(inventory: dict) -> str:
    """Format the capability inventory for human reading."""
    lines: list[str] = []
    lines.append("AGENT CAPABILITY INVENTORY")
    lines.append("=" * 60)
    lines.append(f"Total capabilities: {inventory['total_capabilities']}")
    lines.append("")

    for proto, caps in inventory["by_protocol"].items():
        lines.append(f"--- {proto.upper()} ({len(caps)} tool(s)) ---")
        for cap in caps:
            auth_flag = " [AUTH]" if cap["has_auth"] else ""
            lines.append(f"  {cap['name']}{auth_flag}")
            if cap["description"]:
                lines.append(f"    {cap['description']}")
            lines.append(f"    Params: {cap['parameter_count']} ({cap['required_params']} required) | Transport: {cap['transport']}")
        lines.append("")

    if inventory["errors"]:
        lines.append(f"--- ERRORS ({len(inventory['errors'])}) ---")
        for err in inventory["errors"]:
            lines.append(f"  {err.get('source_file', 'unknown')}: {err.get('error', 'unknown error')}")

    return "\n".join(lines)


def format_human_conflicts(conflicts: list[dict]) -> str:
    """Format conflict detection results."""
    lines: list[str] = []
    lines.append("CONFLICT DETECTION REPORT")
    lines.append("=" * 60)

    if not conflicts:
        lines.append("No conflicts detected.")
        return "\n".join(lines)

    lines.append(f"Found {len(conflicts)} potential conflict(s):\n")

    for conf in conflicts:
        dup_flag = " ** LIKELY DUPLICATE **" if conf["likely_duplicate"] else ""
        lines.append(f"  Name: {conf['name']}{dup_flag}")
        lines.append(f"  Occurrences: {conf['count']} across protocols: {', '.join(conf['protocols'])}")
        lines.append(f"  Description similarity: {conf['description_similarity']:.0%}")
        for src in conf["sources"]:
            lines.append(f"    - {src['file']} ({src['protocol']})")
        lines.append("")

    return "\n".join(lines)


def format_human_matrix(matrix: dict) -> str:
    """Format the compatibility matrix."""
    lines: list[str] = []
    lines.append("PROTOCOL COMPATIBILITY MATRIX")
    lines.append("=" * 60)
    lines.append(f"Protocols: {', '.join(matrix['protocols_found'])}")
    lines.append(f"Total capabilities: {matrix['total_capabilities']}")
    lines.append("")

    # Feature comparison table
    features = matrix.get("protocol_features", {})
    if features:
        lines.append("Feature Comparison:")
        lines.append(f"  {'Feature':<30} " + " ".join(f"{p:<12}" for p in features.keys()))
        lines.append("  " + "-" * (30 + 13 * len(features)))

        rows = ["tool_count", "has_authentication", "has_streaming",
                "avg_parameters_per_tool", "description_coverage"]
        for row in rows:
            label = row.replace("_", " ").title()
            vals = []
            for proto in features:
                v = features[proto].get(row, "N/A")
                if isinstance(v, bool):
                    v = "Yes" if v else "No"
                vals.append(str(v))
            lines.append(f"  {label:<30} " + " ".join(f"{v:<12}" for v in vals))
        lines.append("")

    # Bridge analysis
    bridges = matrix.get("bridge_analysis", [])
    needs_bridge = [b for b in bridges if b.get("bridge_needed")]
    if needs_bridge:
        lines.append(f"Bridge Candidates ({len(needs_bridge)} capabilities need cross-protocol bridges):")
        for b in needs_bridge[:20]:  # limit output
            available = ", ".join(b["available_in"].keys())
            missing = ", ".join(b.get("missing_protocols", []))
            lines.append(f"  {b['capability']}: available in [{available}], missing in [{missing}]")
        if len(needs_bridge) > 20:
            lines.append(f"  ... and {len(needs_bridge) - 20} more")
    else:
        lines.append("No protocol bridges needed — all capabilities have cross-protocol coverage.")

    return "\n".join(lines)


def format_human_gaps(gaps: dict) -> str:
    """Format gap analysis results."""
    lines: list[str] = []
    lines.append("GAP ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"Quality Score: {gaps.get('quality_score', 0)}%\n")

    gap_labels = {
        "missing_description": "Missing Description (critical for LLM tool selection)",
        "short_description": "Short Description (< 30 chars)",
        "no_parameters": "No Parameters Defined",
        "no_required_params": "No Required Parameters",
        "no_auth": "No Authentication (A2A agents)",
    }

    for gap_key, label in gap_labels.items():
        info = gaps.get(gap_key, {"count": 0, "items": []})
        count = info["count"]
        status = "PASS" if count == 0 else "FAIL"
        lines.append(f"  [{status}] {label}: {count}")
        if count > 0:
            for item in info["items"][:5]:
                lines.append(f"        - {item['name']} ({item['protocol']}) in {item['file']}")
            if count > 5:
                lines.append(f"        ... and {count - 5} more")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def find_json_files(directory: str) -> list[str]:
    """Recursively find JSON files in a directory."""
    files: list[str] = []
    for root, _dirs, filenames in os.walk(directory):
        for fn in sorted(filenames):
            if fn.endswith(".json"):
                files.append(os.path.join(root, fn))
    return files


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Map and analyze agent capabilities across protocol definitions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s tools.json agent-card.json\n"
            "  %(prog)s --scan-dir ./agents/\n"
            "  %(prog)s --detect-conflicts mcp-tools.json openai-funcs.json\n"
            "  %(prog)s --compatibility-matrix --scan-dir ./protocols/ --json\n"
            "  %(prog)s --gap-analysis *.json\n"
        ),
    )
    parser.add_argument("files", nargs="*", metavar="FILE",
                        help="JSON protocol files to analyze")
    parser.add_argument("--scan-dir", metavar="DIR",
                        help="Recursively scan directory for JSON protocol files")
    parser.add_argument("--detect-conflicts", action="store_true",
                        help="Detect duplicate or overlapping tool names")
    parser.add_argument("--compatibility-matrix", action="store_true",
                        help="Generate cross-protocol compatibility matrix")
    parser.add_argument("--gap-analysis", action="store_true",
                        help="Run quality gap analysis across all capabilities")
    parser.add_argument("--json", dest="json_output", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    # Collect files
    all_files: list[str] = list(args.files)
    if args.scan_dir:
        if not os.path.isdir(args.scan_dir):
            print(f"Error: Directory not found: {args.scan_dir}", file=sys.stderr)
            return 1
        all_files.extend(find_json_files(args.scan_dir))

    if not all_files:
        parser.print_help()
        print("\nError: No input files specified. Provide files or use --scan-dir.", file=sys.stderr)
        return 1

    # Extract capabilities from all files
    all_capabilities: list[dict] = []
    for filepath in all_files:
        if not os.path.isfile(filepath):
            all_capabilities.append({"source_file": filepath, "error": "File not found"})
            continue
        all_capabilities.extend(extract_capabilities(filepath))

    valid_caps = [c for c in all_capabilities if "error" not in c]

    if not valid_caps and not any("error" in c for c in all_capabilities):
        print("No capabilities found in the provided files.", file=sys.stderr)
        return 1

    # Determine which analyses to run
    run_conflicts = args.detect_conflicts
    run_matrix = args.compatibility_matrix
    run_gaps = args.gap_analysis

    # If no specific analysis requested, run inventory + all analyses
    if not (run_conflicts or run_matrix or run_gaps):
        run_conflicts = True
        run_matrix = True
        run_gaps = True

    # Build results
    results: dict[str, Any] = {}
    results["inventory"] = build_inventory(all_capabilities)

    if run_conflicts:
        results["conflicts"] = detect_conflicts(valid_caps)
    if run_matrix:
        results["compatibility_matrix"] = build_compatibility_matrix(valid_caps)
    if run_gaps:
        results["gap_analysis"] = run_gap_analysis(valid_caps)

    # Output
    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_human_inventory(results["inventory"]))
        if run_conflicts:
            print("\n")
            print(format_human_conflicts(results["conflicts"]))
        if run_matrix:
            print("\n")
            print(format_human_matrix(results["compatibility_matrix"]))
        if run_gaps:
            print("\n")
            print(format_human_gaps(results["gap_analysis"]))

    # Exit code: 1 if there are errors or likely duplicates
    has_errors = bool(results["inventory"].get("errors"))
    has_dupes = any(c.get("likely_duplicate") for c in results.get("conflicts", []))
    return 1 if (has_errors or has_dupes) else 0


if __name__ == "__main__":
    sys.exit(main())
