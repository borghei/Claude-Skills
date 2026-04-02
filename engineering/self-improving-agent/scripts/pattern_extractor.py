#!/usr/bin/env python3
"""Extract reusable patterns from agent session logs.

Analyzes JSONL session logs to identify recurring approaches, error resolutions,
and workflow patterns. Scores each pattern by frequency, consistency, and impact
to recommend which patterns should be promoted to rules.

Expected log entry format (JSONL):
{"session_id": "s1", "task_type": "code-review", "outcome": "SUCCESS",
 "approach": "used page objects", "corrections": 0, "error_resolved": "",
 "tools_used": ["Read", "Edit"], "notes": ""}

Usage:
    python pattern_extractor.py --input sessions.jsonl --min-occurrences 2
    python pattern_extractor.py --input sessions.jsonl --min-occurrences 3 --json
    python pattern_extractor.py --input sessions.jsonl --days 30
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def load_sessions(path, max_days=None):
    """Load session log entries from JSONL file."""
    entries = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if "timestamp" in entry:
                    entry["_dt"] = datetime.fromisoformat(entry["timestamp"])
                entries.append(entry)
            except json.JSONDecodeError:
                continue

    if max_days and entries:
        cutoff = datetime.now() - timedelta(days=max_days)
        entries = [e for e in entries if e.get("_dt", datetime.max) >= cutoff]

    return entries


def tokenize(text):
    """Extract meaningful tokens from text for similarity matching."""
    if not text:
        return set()
    words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", text.lower())
    stop_words = {"the", "and", "for", "with", "from", "that", "this", "was", "used", "using"}
    return set(words) - stop_words


def compute_similarity(tokens_a, tokens_b):
    """Jaccard similarity between two token sets."""
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def cluster_approaches(entries, similarity_threshold=0.4):
    """Cluster similar approaches into pattern groups."""
    # Extract approach descriptions
    approaches = []
    for e in entries:
        approach_text = e.get("approach", "") or e.get("notes", "")
        if approach_text:
            approaches.append({
                "text": approach_text,
                "tokens": tokenize(approach_text),
                "entry": e,
            })

    if not approaches:
        return []

    # Simple greedy clustering
    clusters = []
    assigned = set()

    for i, a in enumerate(approaches):
        if i in assigned:
            continue
        cluster = [a]
        assigned.add(i)

        for j, b in enumerate(approaches):
            if j in assigned:
                continue
            sim = compute_similarity(a["tokens"], b["tokens"])
            if sim >= similarity_threshold:
                cluster.append(b)
                assigned.add(j)

        if len(cluster) >= 1:
            clusters.append(cluster)

    return clusters


def extract_error_patterns(entries, min_count=2):
    """Extract recurring error resolution patterns."""
    error_resolutions = defaultdict(list)

    for e in entries:
        error = e.get("error_resolved", "")
        if error:
            error_tokens = frozenset(tokenize(error))
            if error_tokens:
                error_resolutions[error_tokens].append({
                    "error": error,
                    "task_type": e.get("task_type", "unknown"),
                    "outcome": e.get("outcome", "unknown"),
                    "session_id": e.get("session_id", ""),
                })

    # Filter by minimum count
    recurring = {}
    for tokens, resolutions in error_resolutions.items():
        if len(resolutions) >= min_count:
            # Use the first error text as representative
            recurring[resolutions[0]["error"]] = {
                "count": len(resolutions),
                "task_types": list(set(r["task_type"] for r in resolutions)),
                "success_rate": sum(1 for r in resolutions if r["outcome"] == "SUCCESS") / len(resolutions),
            }

    return recurring


def extract_tool_patterns(entries, min_count=2):
    """Extract recurring tool usage sequences."""
    tool_sequences = Counter()

    for e in entries:
        tools = e.get("tools_used", [])
        if len(tools) >= 2:
            # Use ordered pairs as a simple sequence fingerprint
            for i in range(len(tools) - 1):
                pair = f"{tools[i]} -> {tools[i + 1]}"
                tool_sequences[pair] += 1

    return {seq: count for seq, count in tool_sequences.items() if count >= min_count}


def score_pattern(cluster):
    """Score a pattern cluster on frequency, consistency, and impact."""
    entries = [item["entry"] for item in cluster]
    count = len(entries)

    # Frequency score (0-1)
    if count >= 7:
        frequency = 1.0
    elif count >= 4:
        frequency = 0.7
    elif count >= 2:
        frequency = 0.4
    else:
        frequency = 0.1

    # Consistency score: what fraction had the same outcome
    outcomes = [e.get("outcome", "unknown") for e in entries]
    most_common_outcome = Counter(outcomes).most_common(1)[0]
    consistency = most_common_outcome[1] / len(outcomes) if outcomes else 0

    # Impact score: based on outcome quality
    successes = sum(1 for e in entries if e.get("outcome") == "SUCCESS")
    zero_corrections = sum(1 for e in entries if e.get("corrections", 0) == 0 and e.get("outcome") == "SUCCESS")
    impact = zero_corrections / count if count > 0 else 0

    composite = round(frequency * 0.3 + consistency * 0.4 + impact * 0.3, 3)

    return {
        "frequency": round(frequency, 3),
        "consistency": round(consistency, 3),
        "impact": round(impact, 3),
        "composite": composite,
    }


def determine_recommendation(score, count):
    """Determine recommended action based on score."""
    if score["composite"] >= 0.7 and count >= 3:
        return "PROMOTE"
    elif score["composite"] >= 0.5 and count >= 5:
        return "PROMOTE"
    elif score["composite"] >= 0.4:
        return "KEEP"
    else:
        return "MONITOR"


def extract_patterns(entries, min_occurrences):
    """Main pattern extraction pipeline."""
    clusters = cluster_approaches(entries, similarity_threshold=0.35)
    error_patterns = extract_error_patterns(entries, min_occurrences)
    tool_patterns = extract_tool_patterns(entries, min_occurrences)

    # Score and rank approach patterns
    approach_patterns = []
    for cluster in clusters:
        if len(cluster) < min_occurrences:
            continue
        score = score_pattern(cluster)
        representative = cluster[0]["text"]
        recommendation = determine_recommendation(score, len(cluster))
        task_types = list(set(item["entry"].get("task_type", "unknown") for item in cluster))

        approach_patterns.append({
            "pattern": representative,
            "occurrences": len(cluster),
            "task_types": task_types,
            "scores": score,
            "recommendation": recommendation,
        })

    approach_patterns.sort(key=lambda p: -p["scores"]["composite"])

    return {
        "approach_patterns": approach_patterns,
        "error_patterns": error_patterns,
        "tool_patterns": tool_patterns,
    }


def format_human(results, total_entries):
    """Format results for human-readable output."""
    output = []
    output.append("=" * 60)
    output.append("PATTERN EXTRACTOR")
    output.append("=" * 60)
    output.append(f"  Sessions analyzed: {total_entries}")
    output.append(f"  Approach patterns: {len(results['approach_patterns'])}")
    output.append(f"  Error patterns:    {len(results['error_patterns'])}")
    output.append(f"  Tool patterns:     {len(results['tool_patterns'])}")
    output.append("")

    if results["approach_patterns"]:
        output.append("APPROACH PATTERNS (ranked by composite score)")
        output.append("-" * 60)
        for i, p in enumerate(results["approach_patterns"], 1):
            rec_marker = {"PROMOTE": ">>", "KEEP": "  ", "MONITOR": ".."}
            marker = rec_marker.get(p["recommendation"], "  ")
            output.append(f"  {marker} {i}. [{p['recommendation']}] (score={p['scores']['composite']:.2f}, n={p['occurrences']})")
            output.append(f"     {p['pattern'][:70]}")
            output.append(f"     Tasks: {', '.join(p['task_types'][:4])}")
            output.append("")

    if results["error_patterns"]:
        output.append("ERROR RESOLUTION PATTERNS")
        output.append("-" * 60)
        for error, data in sorted(results["error_patterns"].items(), key=lambda x: -x[1]["count"]):
            output.append(f"  [{data['count']}x] {error[:60]}")
            output.append(f"    Success rate: {data['success_rate']:.0%} | Tasks: {', '.join(data['task_types'][:3])}")
        output.append("")

    if results["tool_patterns"]:
        output.append("TOOL SEQUENCE PATTERNS")
        output.append("-" * 60)
        for seq, count in sorted(results["tool_patterns"].items(), key=lambda x: -x[1]):
            output.append(f"  [{count}x] {seq}")
        output.append("")

    promote_count = sum(1 for p in results["approach_patterns"] if p["recommendation"] == "PROMOTE")
    if promote_count:
        output.append(f"ACTION: {promote_count} patterns ready for promotion review")
    else:
        output.append("ACTION: No patterns ready for promotion yet -- continue monitoring")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Extract reusable patterns from agent session logs.",
        epilog="Example: python pattern_extractor.py --input sessions.jsonl --min-occurrences 3",
    )
    parser.add_argument("--input", required=True, help="Path to JSONL session log file")
    parser.add_argument("--min-occurrences", type=int, default=2, help="Minimum pattern frequency (default: 2)")
    parser.add_argument("--days", type=int, default=None, help="Only analyze sessions within N days")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    entries = load_sessions(args.input, max_days=args.days)
    if not entries:
        print("No session entries found.", file=sys.stderr)
        sys.exit(1)

    results = extract_patterns(entries, args.min_occurrences)

    if args.json_output:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_human(results, len(entries)))


if __name__ == "__main__":
    main()
