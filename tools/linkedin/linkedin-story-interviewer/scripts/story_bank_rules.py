#!/usr/bin/env python3
"""Rule data and text checks behind story_bank_audit.py.

Holds the entry kinds, the fields each kind needs before a draft can use it,
the soft-phrase vocabulary, the rule catalogue, and the follow-up questions
suggested for each kind of gap. The loading, coverage maths and CLI for a real
bank live in story_bank_audit.py.

Usage:
    python3 story_bank_rules.py --list-rules
    python3 story_bank_rules.py --list-rules --format json

Exit codes:
    0  rules printed
    2  bad arguments
"""

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SEVERITY_RANK = {"blocker": 0, "fix": 1, "note": 2}

KINDS = {
    "role": "A job or stretch of work: where, when, what you were answerable for",
    "figure": "A number you can state from memory, with what it measures",
    "build": "Something that exists because you worked on it",
    "reversal": "A belief or plan you held and then dropped",
    "cost": "Something that went wrong and what it took out of you or the team",
    "stance": "An opinion you would defend against people you respect",
    "anecdote": "A story you already tell out loud and know the ending of",
}

# Fields that must be non-empty before an entry of this kind counts as usable.
NEEDS = {
    "figure": ["figure"],
    "reversal": ["before", "after"],
    "cost": ["price"],
    "stance": ["against", "price"],
}

# Kinds that give a pillar tension. A pillar with none of these only has wins.
TENSION_KINDS = ("reversal", "cost", "stance")

SOFT_PHRASES = [
    "significantly", "a lot", "lots of", "many", "several", "numerous",
    "recently", "a while ago", "a while back", "some time ago", "last year",
    "a big client", "a major client", "a large customer", "huge", "massive",
    "dramatically", "substantially", "various", "countless", "a number of",
    "quite a few", "pretty much", "more or less", "roughly speaking",
]

RULES = {
    "SB-001": ("blocker", "Entry mentions a name on the never-name list"),
    "SB-002": ("blocker", "Entry touches a subject on the no-go list"),
    "SB-010": ("fix", "Entry id is missing or duplicated"),
    "SB-011": ("fix", "Entry kind is not one of the seven kinds"),
    "SB-012": ("fix", "Entry is filed under a pillar the bank does not declare"),
    "SB-013": ("fix", "Entry has no usable date"),
    "SB-014": ("fix", "Entry lacks a field its kind needs"),
    "SB-015": ("fix", "Figure has no stated measure or basis"),
    "SB-020": ("fix", "Entry is marked ready but reads soft"),
    "SB-021": ("note", "Entry detail is too short to draft from"),
    "SB-022": ("note", "Entry keeps none of the owner's own wording"),
    "SB-023": ("note", "Naming decision has not been made"),
    "SB-030": ("note", "Bank has not been updated for a long stretch"),
    "SB-031": ("note", "Bank file is not covered by a .gitignore"),
    "SB-032": ("note", "Entry has already been used more than once"),
}

FOLLOW_UPS = {
    "role": "Pick one job from the last ten years. What were you the person "
            "people came to when it broke?",
    "figure": "What is one number from your work you could say right now "
              "without opening a spreadsheet, and what exactly does it count?",
    "build": "What is still running, standing or in use today that would not "
             "be there if you had taken a different job?",
    "reversal": "What did you argue for two years ago that you would argue "
                "against now, and what was the day you noticed?",
    "cost": "Tell me about a week that went badly because of a call you made. "
            "What did it cost, in money, time or a person?",
    "stance": "What do most people in your field treat as settled that you "
              "think is wrong, and what has saying so cost you?",
    "anecdote": "Which story do colleagues ask you to tell again? Give me the "
                "version you tell at the table, ending included.",
    "soft": "You said '{phrase}' in {entry}. What is the actual number or the "
            "actual month?",
    "unfinished": "{entry} is still marked soft{phrase}. What is the number, the "
                  "month or the name that would make it usable?",
    "pillar": "For the pillar '{pillar}': when did this last happen to you, "
              "on a specific day, with a specific person in the room?",
}

WHEN_RE = re.compile(r"^\d{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?)?$")
WORD_RE = re.compile(r"[A-Za-z0-9']+")


def finding(rule_id: str, where: str, evidence: str, action: str) -> Dict[str, Any]:
    """Build one finding record, taking severity and title from RULES."""
    severity, title = RULES[rule_id]
    return {"id": rule_id, "severity": severity, "entry": where,
            "title": title, "evidence": evidence, "action": action}


def valid_when(value: Any) -> bool:
    """Return True for a YYYY, YYYY-MM or YYYY-MM-DD string."""
    return isinstance(value, str) and bool(WHEN_RE.match(value.strip()))


def entry_text(entry: Dict[str, Any]) -> str:
    """Join every free-text field of an entry into one searchable string."""
    parts: List[str] = []
    for key in ("title", "detail", "words", "before", "after", "price", "against"):
        value = entry.get(key)
        if isinstance(value, str):
            parts.append(value)
    figure = entry.get("figure")
    if isinstance(figure, dict):
        parts.extend(str(v) for v in figure.values())
    return " ".join(parts)


def soft_hits(text: str) -> List[str]:
    """List the soft phrases that appear in a piece of text."""
    lowered = f" {text.lower()} "
    return [p for p in SOFT_PHRASES
            if re.search(r"(?<![a-z])" + re.escape(p) + r"(?![a-z])", lowered)]


def has_anchor(text: str) -> bool:
    """Return True when the text carries at least one digit."""
    return any(ch.isdigit() for ch in text)


def word_count(text: str) -> int:
    """Count word-like tokens in a piece of text."""
    return len(WORD_RE.findall(text))


def mentions(text: str, terms: List[Any]) -> List[str]:
    """Return the terms that occur in the text, compared case-insensitively."""
    lowered = text.lower()
    return [str(t) for t in terms
            if isinstance(t, str) and t.strip() and t.strip().lower() in lowered]


def missing_fields(entry: Dict[str, Any]) -> List[str]:
    """List the kind-specific fields an entry has left empty."""
    absent: List[str] = []
    for key in NEEDS.get(str(entry.get("kind")), []):
        value = entry.get(key)
        if not value or (isinstance(value, str) and not value.strip()):
            absent.append(key)
    return absent


def is_ignored(path: Path) -> Optional[bool]:
    """Report whether a .gitignore in a parent directory covers the bank file.

    Returns None when the file is not inside a git working tree.
    """
    resolved = path.resolve()
    for folder in resolved.parents:
        ignore = folder / ".gitignore"
        if ignore.is_file():
            relative = resolved.relative_to(folder).as_posix()
            covered = False
            for raw in ignore.read_text(encoding="utf-8", errors="replace").splitlines():
                rule = raw.strip()
                negated = rule.startswith("!")
                rule = rule.lstrip("!").lstrip("/")
                if not rule or rule.startswith("#"):
                    continue
                if (fnmatch.fnmatch(relative, rule) or fnmatch.fnmatch(resolved.name, rule)
                        or relative.startswith(rule.rstrip("/") + "/")):
                    covered = not negated
            if covered:
                return True
        if (folder / ".git").exists():
            return False
    return None


def main() -> None:
    """Print the rule catalogue, entry kinds and soft-phrase list."""
    parser = argparse.ArgumentParser(
        description="Show the rules, entry kinds and soft phrases used by "
                    "story_bank_audit.py.",
        epilog="Exit codes: 0 rules printed, 2 bad arguments.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print the catalogue (required; the module has "
                             "no other action).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if not args.list_rules:
        print("ERROR: nothing to do. Pass --list-rules, or run "
              "story_bank_audit.py --input <bank.json> to audit a bank.",
              file=sys.stderr)
        sys.exit(2)
    if args.format == "json":
        print(json.dumps({
            "rules": {k: {"severity": v[0], "title": v[1]} for k, v in RULES.items()},
            "kinds": KINDS, "needs": NEEDS, "soft_phrases": SOFT_PHRASES,
        }, indent=2))
        return
    print("Story bank rules")
    print("=" * 72)
    for rule_id, (severity, title) in RULES.items():
        print(f"{rule_id}  [{severity:<7}] {title}")
    print("\nEntry kinds")
    for kind, text in KINDS.items():
        needs = ", ".join(NEEDS.get(kind, [])) or "no extra fields"
        print(f"  {kind:<9} {text} (needs: {needs})")
    print(f"\nSoft phrases checked: {', '.join(SOFT_PHRASES)}")


if __name__ == "__main__":
    main()
