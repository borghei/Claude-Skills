#!/usr/bin/env python3
"""Compare two prompt versions and highlight structural changes.

Detects added/removed sections, instruction changes, layer modifications,
token count deltas, and flags potential regressions aligned with the
Prompt Diff Analysis checklist from the Prompt Engineer Toolkit.

No external dependencies -- uses Python standard library only.
"""

import argparse
import difflib
import json
import os
import re
import sys
from collections import OrderedDict


# Section header patterns (markdown-style and separator-based).
SECTION_PATTERNS = [
    re.compile(r"^(#{1,6})\s+(.+)$"),           # Markdown headers
    re.compile(r"^([A-Z][A-Za-z\s]{2,50}):$"),   # "Section Name:"
    re.compile(r"^-{3,}$"),                       # Horizontal rules
    re.compile(r"^={3,}$"),                       # Double rules
]

# Risk checklist from the SKILL.md Prompt Diff Analysis section.
RISK_CHECKS = [
    {
        "id": "constraints_removed",
        "label": "Constraints removed",
        "risk": "Safety regression",
        "patterns_old": [r"(?i)\bmust\b", r"(?i)\bnever\b", r"(?i)\bdo not\b", r"(?i)\bdon't\b",
                         r"(?i)\bshall not\b", r"(?i)\bprohibit", r"(?i)\bforbid"],
    },
    {
        "id": "examples_changed",
        "label": "Examples changed",
        "risk": "Calibration shift",
        "patterns_old": [r"(?i)\bexample\b", r"(?i)\bfor instance\b", r"(?i)\bsample\b"],
    },
    {
        "id": "output_format_changed",
        "label": "Output format changed",
        "risk": "Downstream parser breakage",
        "patterns_old": [r"(?i)\bjson\b", r"(?i)\bschema\b", r"(?i)\bformat\b",
                         r"(?i)\brespond with\b", r"(?i)\bstructure\b"],
    },
    {
        "id": "anti_patterns_removed",
        "label": "Anti-patterns removed",
        "risk": "Known failure modes may return",
        "patterns_old": [r"(?i)\bavoid\b", r"(?i)\bnever\b", r"(?i)\bdo not\b",
                         r"(?i)\bdon't\b", r"(?i)\bforbid"],
    },
]

TOKEN_RATIO = 1.3


def estimate_tokens(text: str) -> int:
    words = text.split()
    return max(1, int(len(words) * TOKEN_RATIO + 0.5))


def extract_sections(text: str) -> OrderedDict:
    """Split text into named sections based on header patterns."""
    sections = OrderedDict()
    current_name = "__preamble__"
    current_lines = []

    for line in text.splitlines():
        matched = False
        for pattern in SECTION_PATTERNS[:2]:  # Only named headers
            m = pattern.match(line.strip())
            if m:
                if current_lines or current_name != "__preamble__":
                    sections[current_name] = "\n".join(current_lines)
                current_name = m.group(2) if m.lastindex >= 2 else m.group(1)
                current_name = current_name.strip()
                current_lines = []
                matched = True
                break
        if not matched:
            current_lines.append(line)

    sections[current_name] = "\n".join(current_lines)
    return sections


def compute_line_diff(old_text: str, new_text: str) -> dict:
    """Compute unified diff statistics."""
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="old", tofile="new", n=3))
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))

    similarity = difflib.SequenceMatcher(None, old_text, new_text).ratio()

    return {
        "added_lines": added,
        "removed_lines": removed,
        "similarity": round(similarity, 3),
        "diff_text": "".join(diff),
    }


def compare_sections(old_sections: OrderedDict, new_sections: OrderedDict) -> dict:
    """Compare sections between old and new prompts."""
    old_names = set(old_sections.keys())
    new_names = set(new_sections.keys())

    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)
    common = sorted(old_names & new_names)

    modified = []
    unchanged = []
    for name in common:
        if old_sections[name].strip() != new_sections[name].strip():
            sim = difflib.SequenceMatcher(None, old_sections[name], new_sections[name]).ratio()
            modified.append({"section": name, "similarity": round(sim, 3)})
        else:
            unchanged.append(name)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def check_risks(old_text: str, new_text: str, line_diff: dict) -> list:
    """Run the risk checklist from the Prompt Diff Analysis."""
    findings = []

    for check in RISK_CHECKS:
        old_hits = 0
        new_hits = 0
        for pat in check["patterns_old"]:
            old_hits += len(re.findall(pat, old_text))
            new_hits += len(re.findall(pat, new_text))

        if old_hits > new_hits:
            findings.append({
                "check": check["id"],
                "label": check["label"],
                "risk": check["risk"],
                "severity": "high" if (old_hits - new_hits) > 2 else "medium",
                "detail": f"Signal count dropped from {old_hits} to {new_hits}",
            })
        elif new_hits > old_hits and check["id"] in ("output_format_changed",):
            findings.append({
                "check": check["id"],
                "label": check["label"],
                "risk": check["risk"],
                "severity": "medium",
                "detail": f"Signal count changed from {old_hits} to {new_hits}",
            })

    # Check if prompt got significantly longer (context budget risk).
    old_tokens = estimate_tokens(old_text)
    new_tokens = estimate_tokens(new_text)
    if new_tokens > old_tokens * 1.25:
        findings.append({
            "check": "prompt_length_increase",
            "label": "Prompt significantly longer",
            "risk": "Context budget impact",
            "severity": "low",
            "detail": f"Token estimate grew from {old_tokens} to {new_tokens} (+{new_tokens - old_tokens})",
        })

    return findings


def compute_instruction_delta(old_text: str, new_text: str) -> dict:
    """Compare instruction-bearing lines between versions."""
    instruction_pat = re.compile(
        r"(?i)\b(must|should|shall|always|never|do not|don't|avoid|ensure|require|critical|important)\b"
    )
    old_instructions = [l.strip() for l in old_text.splitlines() if instruction_pat.search(l)]
    new_instructions = [l.strip() for l in new_text.splitlines() if instruction_pat.search(l)]

    old_set = set(old_instructions)
    new_set = set(new_instructions)

    return {
        "old_count": len(old_instructions),
        "new_count": len(new_instructions),
        "added_instructions": sorted(new_set - old_set)[:15],
        "removed_instructions": sorted(old_set - new_set)[:15],
    }


def diff_prompts(old_path: str, new_path: str) -> dict:
    """Run full diff analysis between two prompt files."""
    with open(old_path, "r", encoding="utf-8") as f:
        old_text = f.read()
    with open(new_path, "r", encoding="utf-8") as f:
        new_text = f.read()

    old_sections = extract_sections(old_text)
    new_sections = extract_sections(new_text)

    line_diff = compute_line_diff(old_text, new_text)
    section_diff = compare_sections(old_sections, new_sections)
    risks = check_risks(old_text, new_text, line_diff)
    instruction_delta = compute_instruction_delta(old_text, new_text)

    old_tokens = estimate_tokens(old_text)
    new_tokens = estimate_tokens(new_text)

    return {
        "old_file": old_path,
        "new_file": new_path,
        "summary": {
            "old_tokens": old_tokens,
            "new_tokens": new_tokens,
            "token_delta": new_tokens - old_tokens,
            "similarity": line_diff["similarity"],
            "lines_added": line_diff["added_lines"],
            "lines_removed": line_diff["removed_lines"],
        },
        "sections": section_diff,
        "instructions": instruction_delta,
        "risks": risks,
        "risk_count": len(risks),
        "diff_text": line_diff["diff_text"],
    }


def format_human(result: dict, show_diff: bool = False) -> str:
    """Format diff result for human-readable console output."""
    lines = []
    lines.append(f"Prompt Diff: {result['old_file']} -> {result['new_file']}")
    lines.append("=" * 64)

    s = result["summary"]
    lines.append(f"  Similarity:    {s['similarity']:.1%}")
    lines.append(f"  Tokens:        {s['old_tokens']} -> {s['new_tokens']} ({'+' if s['token_delta'] >= 0 else ''}{s['token_delta']})")
    lines.append(f"  Lines added:   {s['lines_added']}")
    lines.append(f"  Lines removed: {s['lines_removed']}")
    lines.append("")

    # Sections
    sec = result["sections"]
    if sec["added"]:
        lines.append("  Sections ADDED:")
        for name in sec["added"]:
            lines.append(f"    + {name}")
    if sec["removed"]:
        lines.append("  Sections REMOVED:")
        for name in sec["removed"]:
            lines.append(f"    - {name}")
    if sec["modified"]:
        lines.append("  Sections MODIFIED:")
        for m in sec["modified"]:
            lines.append(f"    ~ {m['section']} (similarity: {m['similarity']:.1%})")
    if sec["unchanged"]:
        lines.append(f"  Sections unchanged: {len(sec['unchanged'])}")
    lines.append("")

    # Instructions
    inst = result["instructions"]
    lines.append(f"  Instructions: {inst['old_count']} -> {inst['new_count']}")
    if inst["removed_instructions"]:
        lines.append("  REMOVED instructions:")
        for i in inst["removed_instructions"][:8]:
            lines.append(f"    - {i[:80]}")
    if inst["added_instructions"]:
        lines.append("  ADDED instructions:")
        for i in inst["added_instructions"][:8]:
            lines.append(f"    + {i[:80]}")
    lines.append("")

    # Risks
    if result["risks"]:
        lines.append(f"  RISK FINDINGS ({result['risk_count']}):")
        for r in result["risks"]:
            sev_marker = "!!!" if r["severity"] == "high" else "! " if r["severity"] == "medium" else "  "
            lines.append(f"    [{sev_marker}] {r['label']}: {r['risk']}")
            lines.append(f"         {r['detail']}")
    else:
        lines.append("  No risk findings detected.")
    lines.append("")

    if show_diff and result["diff_text"]:
        lines.append("  Unified Diff:")
        lines.append("  " + "-" * 40)
        for dl in result["diff_text"].splitlines()[:60]:
            lines.append(f"  {dl}")
        if result["diff_text"].count("\n") > 60:
            lines.append("  ... (truncated)")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare two prompt versions and highlight structural changes, instruction deltas, and risk findings.",
        epilog="Example: python prompt_diff.py prompt_v1.txt prompt_v2.txt --show-diff",
    )
    parser.add_argument("old_file", help="Path to the old/baseline prompt file")
    parser.add_argument("new_file", help="Path to the new/candidate prompt file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--show-diff", action="store_true", help="Include unified diff text in output")
    args = parser.parse_args()

    for path in (args.old_file, args.new_file):
        if not os.path.isfile(path):
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    result = diff_prompts(args.old_file, args.new_file)

    if args.json:
        output = result
        if not args.show_diff:
            output = {k: v for k, v in result.items() if k != "diff_text"}
        print(json.dumps(output, indent=2))
    else:
        print(format_human(result, show_diff=args.show_diff))


if __name__ == "__main__":
    main()
