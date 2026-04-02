#!/usr/bin/env python3
"""Check memory system health: line counts, stale entries, contradictions.

Scans MEMORY.md and related files for health issues including line limit
violations, stale references, duplicate entries, and promotion candidates.
Produces an actionable health report.

Usage:
    python memory_health_checker.py --memory ./MEMORY.md
    python memory_health_checker.py --memory ./MEMORY.md --rules ./.claude/rules/
    python memory_health_checker.py --memory ./MEMORY.md --json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


MEMORY_LINE_LIMIT = 200
TOPIC_FILE_LINE_LIMIT = 100
STALE_AGE_DAYS = 90
PROMOTION_THRESHOLD = 3


def load_memory_file(path):
    """Load and parse a memory file into structured entries."""
    if not os.path.exists(path):
        return {"path": path, "exists": False, "lines": 0, "entries": []}

    content = Path(path).read_text(encoding="utf-8")
    lines = content.split("\n")
    entries = []
    current_entry = None

    for i, line in enumerate(lines, 1):
        # Detect entry headers (## Learning: or ## heading)
        if line.startswith("## "):
            if current_entry:
                current_entry["end_line"] = i - 1
                entries.append(current_entry)
            current_entry = {
                "title": line.lstrip("# ").strip(),
                "start_line": i,
                "end_line": None,
                "content_lines": [],
                "metadata": {},
            }
        elif current_entry:
            current_entry["content_lines"].append(line)
            # Extract metadata from key-value lines
            kv_match = re.match(r"\*\*(\w[\w\s]*)\*\*:\s*(.+)", line)
            if kv_match:
                key = kv_match.group(1).strip().lower()
                value = kv_match.group(2).strip()
                current_entry["metadata"][key] = value

    if current_entry:
        current_entry["end_line"] = len(lines)
        entries.append(current_entry)

    return {
        "path": str(path),
        "exists": True,
        "lines": len(lines),
        "entries": entries,
    }


def load_rules(rules_dir):
    """Load existing promoted rules for comparison."""
    rules = []
    rules_path = Path(rules_dir)
    if not rules_path.exists():
        return rules

    for rule_file in rules_path.glob("*.md"):
        content = rule_file.read_text(encoding="utf-8")
        rules.append({
            "file": str(rule_file),
            "content": content,
            "tokens": set(re.findall(r"[a-zA-Z_]{3,}", content.lower())),
        })

    return rules


def classify_entry(entry, existing_rules, all_entries):
    """Classify a memory entry into PROMOTE, CONSOLIDATE, STALE, KEEP, or EXTRACT."""
    title = entry["title"].lower()
    metadata = entry["metadata"]
    content_text = " ".join(entry["content_lines"]).lower()
    entry_tokens = set(re.findall(r"[a-zA-Z_]{3,}", content_text))

    issues = []
    classification = "KEEP"

    # Check recurrence for promotion
    recurrence_str = metadata.get("recurrence", "")
    recurrence_count = 0
    match = re.search(r"(\d+)", recurrence_str)
    if match:
        recurrence_count = int(match.group(1))

    if recurrence_count >= PROMOTION_THRESHOLD:
        classification = "PROMOTE"
        issues.append(f"Recurrence {recurrence_count} meets promotion threshold ({PROMOTION_THRESHOLD})")

    # Check for explicit action metadata
    action = metadata.get("action", "").upper()
    if action == "PROMOTE":
        classification = "PROMOTE"
    elif action == "EXTRACT":
        classification = "EXTRACT"

    # Check for stale entries (references to deleted files, old dates)
    confidence = metadata.get("confidence", "").lower()
    if confidence == "low":
        issues.append("Low confidence entry")
        if classification == "KEEP":
            classification = "STALE"

    # Check for duplicates / consolidation candidates
    for other in all_entries:
        if other is entry:
            continue
        other_tokens = set(re.findall(r"[a-zA-Z_]{3,}", " ".join(other["content_lines"]).lower()))
        if entry_tokens and other_tokens:
            overlap = len(entry_tokens & other_tokens) / max(len(entry_tokens | other_tokens), 1)
            if overlap > 0.6:
                if classification in ("KEEP", "STALE"):
                    classification = "CONSOLIDATE"
                issues.append(f"Similar to entry: {other['title'][:40]}")
                break

    # Check if already promoted (redundant in memory)
    for rule in existing_rules:
        overlap = len(entry_tokens & rule["tokens"]) / max(len(entry_tokens | rule["tokens"]), 1)
        if overlap > 0.5:
            classification = "STALE"
            issues.append(f"Already promoted to: {rule['file']}")
            break

    return {
        "title": entry["title"],
        "start_line": entry["start_line"],
        "classification": classification,
        "recurrence": recurrence_count,
        "issues": issues,
    }


def check_constraints(memory_data, topic_files):
    """Check system-wide constraints."""
    violations = []

    if memory_data["lines"] > MEMORY_LINE_LIMIT:
        violations.append({
            "type": "line_limit",
            "file": memory_data["path"],
            "current": memory_data["lines"],
            "limit": MEMORY_LINE_LIMIT,
            "severity": "high",
        })

    for tf in topic_files:
        if tf["lines"] > TOPIC_FILE_LINE_LIMIT:
            violations.append({
                "type": "line_limit",
                "file": tf["path"],
                "current": tf["lines"],
                "limit": TOPIC_FILE_LINE_LIMIT,
                "severity": "medium",
            })

    return violations


def run_health_check(memory_path, rules_dir, topic_dir):
    """Run complete health check."""
    memory_data = load_memory_file(memory_path)
    if not memory_data["exists"]:
        return {
            "status": "NO_MEMORY",
            "message": f"No memory file found at {memory_path}",
            "maturity_level": 0,
        }

    # Load topic files
    topic_files = []
    if topic_dir and os.path.isdir(topic_dir):
        for tf in Path(topic_dir).glob("*.md"):
            topic_files.append(load_memory_file(tf))

    # Load rules
    existing_rules = load_rules(rules_dir) if rules_dir else []

    # Classify entries
    classifications = []
    for entry in memory_data["entries"]:
        cls = classify_entry(entry, existing_rules, memory_data["entries"])
        classifications.append(cls)

    # Count by classification
    counts = defaultdict(int)
    for c in classifications:
        counts[c["classification"]] += 1

    # Check constraints
    violations = check_constraints(memory_data, topic_files)

    # Determine health status
    if violations and any(v["severity"] == "high" for v in violations):
        health_status = "CRITICAL"
    elif counts["STALE"] > 5 or counts["CONSOLIDATE"] > 5:
        health_status = "NEEDS_ATTENTION"
    elif counts["PROMOTE"] > 0:
        health_status = "GOOD_WITH_ACTIONS"
    else:
        health_status = "HEALTHY"

    # Determine maturity level
    if not memory_data["entries"]:
        maturity = 1  # Recording (file exists but empty-ish)
    elif counts["PROMOTE"] > 0 or len(existing_rules) > 0:
        maturity = 3  # Promoting
    elif counts["CONSOLIDATE"] > 0 or counts["STALE"] > 0:
        maturity = 2  # Curating
    else:
        maturity = 1  # Recording

    return {
        "status": health_status,
        "maturity_level": maturity,
        "memory_file": {
            "path": memory_data["path"],
            "lines": memory_data["lines"],
            "line_limit": MEMORY_LINE_LIMIT,
            "entry_count": len(memory_data["entries"]),
        },
        "topic_files": [{"path": tf["path"], "lines": tf["lines"]} for tf in topic_files],
        "classifications": classifications,
        "counts": dict(counts),
        "constraint_violations": violations,
        "existing_rules": len(existing_rules),
    }


def format_human(result):
    """Format health check result for human output."""
    output = []
    output.append("=" * 60)
    output.append("MEMORY HEALTH CHECK")
    output.append("=" * 60)

    if result["status"] == "NO_MEMORY":
        output.append(f"  {result['message']}")
        output.append(f"  Maturity Level: 0 (Stateless)")
        return "\n".join(output)

    mf = result["memory_file"]
    maturity_names = {0: "Stateless", 1: "Recording", 2: "Curating", 3: "Promoting", 4: "Extracting", 5: "Meta-Learning"}
    output.append(f"  Status:         {result['status']}")
    output.append(f"  Maturity Level: {result['maturity_level']} ({maturity_names.get(result['maturity_level'], '?')})")
    output.append(f"  Memory file:    {mf['path']}")
    output.append(f"  Lines:          {mf['lines']}/{mf['line_limit']}")
    output.append(f"  Entries:        {mf['entry_count']}")
    output.append(f"  Existing rules: {result['existing_rules']}")
    output.append("")

    # Classification summary
    output.append("ENTRY CLASSIFICATIONS")
    output.append("-" * 60)
    counts = result["counts"]
    order = ["PROMOTE", "CONSOLIDATE", "STALE", "KEEP", "EXTRACT", "CONTRADICTION"]
    for cls in order:
        count = counts.get(cls, 0)
        if count > 0:
            marker = {"PROMOTE": ">>", "STALE": "xx", "CONSOLIDATE": "==", "EXTRACT": "->", "KEEP": "  "}.get(cls, "  ")
            output.append(f"  {marker} {cls:<15} {count}")
    output.append("")

    # Detailed classifications
    actionable = [c for c in result["classifications"] if c["classification"] != "KEEP"]
    if actionable:
        output.append("ACTIONABLE ENTRIES")
        output.append("-" * 60)
        for c in actionable:
            output.append(f"  [{c['classification']}] Line {c['start_line']}: {c['title'][:50]}")
            for issue in c["issues"]:
                output.append(f"    - {issue}")
        output.append("")

    # Constraint violations
    if result["constraint_violations"]:
        output.append("CONSTRAINT VIOLATIONS")
        output.append("-" * 60)
        for v in result["constraint_violations"]:
            output.append(f"  [{v['severity'].upper()}] {v['file']}: {v['current']} lines (limit: {v['limit']})")
        output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Check memory system health: line counts, stale entries, contradictions.",
        epilog="Example: python memory_health_checker.py --memory ./MEMORY.md --rules ./.claude/rules/",
    )
    parser.add_argument("--memory", required=True, help="Path to MEMORY.md file")
    parser.add_argument("--rules", default=None, help="Path to rules directory (.claude/rules/)")
    parser.add_argument("--topics", default=None, help="Path to topic memory files directory")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    result = run_health_check(args.memory, args.rules, args.topics)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
