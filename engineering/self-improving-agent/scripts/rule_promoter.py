#!/usr/bin/env python3
"""Analyze pattern frequency and promote memory entries to permanent rules.

Validates promotion criteria for memory entries and generates rule text
suitable for CLAUDE.md or .claude/rules/ files. Supports dry-run mode
to preview changes before applying.

Usage:
    python rule_promoter.py --memory ./MEMORY.md --entry-title "Use pnpm" --target claude-md --dry-run
    python rule_promoter.py --memory ./MEMORY.md --entry-title "Use pnpm" --target rules-dir --apply
    python rule_promoter.py --memory ./MEMORY.md --list-candidates
    python rule_promoter.py --memory ./MEMORY.md --list-candidates --json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


PROMOTION_CRITERIA = {
    "min_recurrence": 3,
    "required_confidence": ["high", "medium"],
    "forbidden_actions": ["EXTRACT"],
}

RULE_TEMPLATES = {
    "coding-convention": "**{rule}** -- {reason}",
    "tool-preference": "**{rule}** -- {reason}",
    "project-architecture": "- {rule} ({reason})",
    "debugging-pattern": "When debugging: {rule} ({reason})",
    "style-guide": "- {rule}",
    "default": "- {rule} -- {reason}",
}


def load_memory(path):
    """Load memory file and parse entries."""
    if not os.path.exists(path):
        print(f"Error: Memory file '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    content = Path(path).read_text(encoding="utf-8")
    lines = content.split("\n")
    entries = []
    current = None

    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            if current:
                current["end_line"] = i - 1
                current["content"] = "\n".join(current["raw_lines"])
                entries.append(current)
            current = {
                "title": line.lstrip("# ").strip(),
                "start_line": i,
                "end_line": None,
                "raw_lines": [],
                "metadata": {},
            }
        elif current:
            current["raw_lines"].append(line)
            kv = re.match(r"\*\*(\w[\w\s]*)\*\*:\s*(.+)", line)
            if kv:
                current["metadata"][kv.group(1).strip().lower()] = kv.group(2).strip()

    if current:
        current["end_line"] = len(lines)
        current["content"] = "\n".join(current["raw_lines"])
        entries.append(current)

    return content, lines, entries


def get_recurrence(entry):
    """Extract recurrence count from entry metadata."""
    rec_str = entry["metadata"].get("recurrence", "")
    match = re.search(r"(\d+)", rec_str)
    return int(match.group(1)) if match else 1


def validate_promotion(entry):
    """Check if an entry meets all promotion criteria."""
    reasons = []
    passes = True

    recurrence = get_recurrence(entry)
    if recurrence < PROMOTION_CRITERIA["min_recurrence"]:
        passes = False
        reasons.append(f"Recurrence {recurrence} < minimum {PROMOTION_CRITERIA['min_recurrence']}")

    confidence = entry["metadata"].get("confidence", "").lower()
    if confidence and confidence not in PROMOTION_CRITERIA["required_confidence"]:
        passes = False
        reasons.append(f"Confidence '{confidence}' not in required: {PROMOTION_CRITERIA['required_confidence']}")

    action = entry["metadata"].get("action", "").upper()
    if action in PROMOTION_CRITERIA["forbidden_actions"]:
        passes = False
        reasons.append(f"Action '{action}' is marked for extraction, not promotion")

    # Check clarity: title should be concise
    if len(entry["title"]) > 100:
        reasons.append("Title is over 100 characters -- consider making it more concise")

    return {
        "valid": passes,
        "reasons": reasons,
        "recurrence": recurrence,
        "confidence": confidence,
    }


def generate_rule_text(entry, category="default"):
    """Generate formatted rule text from a memory entry."""
    title = entry["title"]
    # Extract the core rule from the title
    # Remove "Learning: " prefix if present
    rule = re.sub(r"^Learning:\s*", "", title, flags=re.IGNORECASE).strip()

    reason = entry["metadata"].get("root cause", "")
    if not reason:
        reason = entry["metadata"].get("correct approach", "")
    if not reason:
        # Try to extract from content
        for line in entry["raw_lines"]:
            if "because" in line.lower() or "reason" in line.lower():
                reason = line.strip().lstrip("- ").strip()
                break

    template = RULE_TEMPLATES.get(category, RULE_TEMPLATES["default"])
    return template.format(rule=rule, reason=reason or "proven pattern")


def find_candidates(entries):
    """Find all entries that meet promotion criteria."""
    candidates = []
    for entry in entries:
        validation = validate_promotion(entry)
        if validation["valid"]:
            candidates.append({
                "title": entry["title"],
                "start_line": entry["start_line"],
                "recurrence": validation["recurrence"],
                "confidence": validation["confidence"],
                "suggested_rule": generate_rule_text(entry),
            })
        elif validation["recurrence"] >= 2:
            # Near-ready candidates
            candidates.append({
                "title": entry["title"],
                "start_line": entry["start_line"],
                "recurrence": validation["recurrence"],
                "confidence": validation["confidence"],
                "suggested_rule": generate_rule_text(entry),
                "blockers": validation["reasons"],
            })

    candidates.sort(key=lambda c: -c["recurrence"])
    return candidates


def remove_entry_from_memory(content, lines, entry):
    """Remove a promoted entry from memory content."""
    start = entry["start_line"] - 1  # 0-indexed
    end = entry["end_line"]  # already past-the-end
    new_lines = lines[:start] + lines[end:]
    # Clean up double blank lines
    cleaned = []
    prev_blank = False
    for line in new_lines:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank
    return "\n".join(cleaned)


def apply_promotion(memory_path, entry, target, target_path):
    """Apply the promotion: add rule to target, remove from memory."""
    rule_text = generate_rule_text(entry)
    now = datetime.now().strftime("%Y-%m-%d")

    if target == "claude-md":
        # Append to CLAUDE.md
        if os.path.exists(target_path):
            existing = Path(target_path).read_text(encoding="utf-8")
        else:
            existing = ""
        addition = f"\n{rule_text}  <!-- promoted {now} -->\n"
        Path(target_path).write_text(existing + addition, encoding="utf-8")
    elif target == "rules-dir":
        # Create or append to rules file
        rules_dir = Path(target_path)
        rules_dir.mkdir(parents=True, exist_ok=True)
        rule_file = rules_dir / "promoted-rules.md"
        existing = rule_file.read_text(encoding="utf-8") if rule_file.exists() else "# Promoted Rules\n\n"
        existing += f"\n{rule_text}  <!-- promoted {now} -->\n"
        rule_file.write_text(existing, encoding="utf-8")

    # Remove from memory
    content, lines, entries = load_memory(memory_path)
    new_content = remove_entry_from_memory(content, lines, entry)
    # Add promotion note
    note = f"\n<!-- Promoted to {target} on {now}: {entry['title'][:50]} -->\n"
    Path(memory_path).write_text(new_content + note, encoding="utf-8")

    return {
        "promoted": True,
        "rule_text": rule_text,
        "target": target,
        "target_path": target_path,
        "removed_from_memory": True,
    }


def format_human(result):
    """Format result for human output."""
    lines = []

    if "candidates" in result:
        lines.append("=" * 60)
        lines.append("PROMOTION CANDIDATES")
        lines.append("=" * 60)
        ready = [c for c in result["candidates"] if "blockers" not in c]
        near_ready = [c for c in result["candidates"] if "blockers" in c]

        if ready:
            lines.append(f"\nREADY FOR PROMOTION ({len(ready)})")
            lines.append("-" * 60)
            for c in ready:
                lines.append(f"  >> Line {c['start_line']}: {c['title'][:50]}")
                lines.append(f"     Recurrence: {c['recurrence']} | Confidence: {c['confidence']}")
                lines.append(f"     Rule: {c['suggested_rule'][:60]}")
                lines.append("")

        if near_ready:
            lines.append(f"\nNEAR-READY ({len(near_ready)})")
            lines.append("-" * 60)
            for c in near_ready:
                lines.append(f"  .. Line {c['start_line']}: {c['title'][:50]}")
                lines.append(f"     Recurrence: {c['recurrence']} | Blockers: {'; '.join(c['blockers'][:2])}")
                lines.append("")

    elif "validation" in result:
        v = result["validation"]
        status = "READY" if v["valid"] else "NOT READY"
        lines.append(f"Promotion Validation: {status}")
        lines.append(f"  Entry: {result['entry_title']}")
        lines.append(f"  Recurrence: {v['recurrence']}")
        if v["reasons"]:
            lines.append(f"  Issues: {'; '.join(v['reasons'])}")
        if "rule_text" in result:
            lines.append(f"  Generated rule: {result['rule_text']}")

    elif "promoted" in result:
        lines.append(f"Promotion Applied")
        lines.append(f"  Rule: {result['rule_text']}")
        lines.append(f"  Target: {result['target']} ({result['target_path']})")
        lines.append(f"  Removed from memory: {result['removed_from_memory']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze pattern frequency and promote memory entries to permanent rules.",
    )
    parser.add_argument("--memory", required=True, help="Path to MEMORY.md")
    parser.add_argument("--list-candidates", action="store_true", help="List all promotion candidates")
    parser.add_argument("--entry-title", help="Title of specific entry to promote")
    parser.add_argument("--target", choices=["claude-md", "rules-dir"], help="Promotion target")
    parser.add_argument("--target-path", help="Path to target file/directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview without applying")
    parser.add_argument("--apply", action="store_true", help="Apply the promotion")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()
    content, file_lines, entries = load_memory(args.memory)

    if args.list_candidates:
        candidates = find_candidates(entries)
        result = {"candidates": candidates, "total_entries": len(entries)}
    elif args.entry_title:
        # Find the specific entry
        target_entry = None
        for e in entries:
            if args.entry_title.lower() in e["title"].lower():
                target_entry = e
                break
        if not target_entry:
            print(f"Error: Entry matching '{args.entry_title}' not found.", file=sys.stderr)
            sys.exit(1)

        validation = validate_promotion(target_entry)
        rule_text = generate_rule_text(target_entry)

        if args.apply and validation["valid"] and args.target and args.target_path:
            result = apply_promotion(args.memory, target_entry, args.target, args.target_path)
        else:
            result = {
                "entry_title": target_entry["title"],
                "validation": validation,
                "rule_text": rule_text,
                "dry_run": True,
            }
    else:
        parser.print_help()
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
