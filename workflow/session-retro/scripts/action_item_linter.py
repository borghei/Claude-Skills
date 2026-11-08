#!/usr/bin/env python3
"""Lint a session-retro action list so every item is a concrete environment change.

An action item passes when it names a known retro category, a target file to edit,
an imperative change (not advice to "be careful"), evidence from the session, and a
severity; when steering-file edits stay short; and when mechanical rules go to a
check rather than to prose. Accepts JSON ({"items": [...]}) or the markdown table
from assets/retro_template.md.

Usage:
  python3 action_item_linter.py --input action_items.json
  python3 action_item_linter.py --input retro.md --strict --format json

Exit codes: 0 = clean (warnings allowed unless --strict), 1 = errors (or warnings
with --strict), 2 = input could not be read or parsed. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

CATEGORIES = {"navigation", "missing-check", "standards", "steering-file", "tool-economy",
              "permission-friction", "skill-miss", "information-access"}
SEVERITIES = {"high": 3, "medium": 2, "low": 1}
STEERING_FILES = ("claude.md", "agents.md", "gemini.md", ".cursorrules", ".windsurfrules",
                  ".clinerules", ".goosehints", "copilot-instructions.md")
VERBS = {"add", "remove", "replace", "move", "wire", "allowlist", "allow", "rename", "split", "delete",
         "create", "document", "sharpen", "rewrite", "shorten", "pin", "cache", "point", "register",
         "enable", "disable", "install", "merge", "extract", "fix", "tighten", "narrow", "expose", "tee"}
ADVICE_RE = re.compile(r"\b(be careful|remember to|try to|make sure|more careful(ly)?|pay attention|"
                       r"be mindful|keep in mind|should consider|consider|better|improve)\b", re.IGNORECASE)
MECHANICAL_RE = re.compile(r"\b(never|always|do not|don't|must not|forbid|banned?)\b", re.IGNORECASE)
PATH_RE = re.compile(r"[\w.\-/~]+\.(md|py|json|ya?ml|toml|js|ts|sh|cfg|ini|txt|mdc)$|^\.?[\w\-]+rules$|"
                     r"(^|/)(Makefile|Justfile|Dockerfile)$|\.git/hooks/[\w\-]+$|/$")
COLUMNS = ["rank", "category", "change", "file", "evidence", "severity"]


def parse_markdown(text: str) -> List[Dict[str, Any]]:
    """Read rows of the action-item table (header must contain the six columns)."""
    items: List[Dict[str, Any]] = []
    header: List[str] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            header = [] if not items else header
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if all(col in lowered for col in COLUMNS):
            header = lowered
            continue
        if not header or all(set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(header, cells))
        if any(row.get(col) for col in COLUMNS[1:]):
            items.append({col: row.get(col, "") for col in COLUMNS})
    return items


def load_items(path: Path) -> List[Dict[str, Any]]:
    """Load items from JSON or a markdown table."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        items = data.get("items") if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValueError("JSON must be a list or an object with an 'items' list")
        return [i for i in items if isinstance(i, dict)]
    items = parse_markdown(text)
    if not items:
        raise ValueError("no action-item table found (need columns: " + ", ".join(COLUMNS) + ")")
    return items


def lint_item(index: int, item: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return findings for one action item."""
    out: List[Dict[str, str]] = []
    label = f"item {item.get('rank') or index}"

    def add(level: str, msg: str) -> None:
        out.append({"item": label, "level": level, "message": msg})

    category = str(item.get("category", "")).strip().lower()
    change = str(item.get("change", "")).strip()
    target = str(item.get("file", "")).strip()
    evidence = str(item.get("evidence", "")).strip()
    severity = str(item.get("severity", "")).strip().lower()

    if category not in CATEGORIES:
        add("error", f"category '{category or '-'}' is not one of: {', '.join(sorted(CATEGORIES))}")
    if not change:
        add("error", "no change described")
    else:
        first = re.sub(r"[^a-z]", "", change.split()[0].lower())
        if first not in VERBS:
            add("warn", f"change should start with an imperative verb (got '{change.split()[0]}')")
        if ADVICE_RE.search(change):
            add("warn", f"'{ADVICE_RE.search(change).group(0)}' is advice to the agent, not a change to its environment")
    if not target:
        add("error", "no target file — every item must name the file to edit")
    elif not PATH_RE.search(target) and target.lower() not in STEERING_FILES:
        add("warn", f"target '{target}' does not look like a file path")
    if not evidence or evidence.lower() in {"-", "n/a", "none"}:
        add("error", "no evidence — cite the call numbers or transcript moment that motivated it")
    if severity not in SEVERITIES:
        add("warn", f"severity '{severity or '-'}' should be high, medium or low")

    is_steering = target.lower().endswith(STEERING_FILES)
    if is_steering and len(change) > 220:
        add("warn", f"steering-file edit is {len(change)} chars; keep it to one short imperative line or a pointer")
    if is_steering and category in {"missing-check", "standards"} and MECHANICAL_RE.search(change):
        add("warn", "mechanical rule routed to a steering file — prefer a lint rule, hook or CI check")
    return out


def lint(items: List[Dict[str, Any]], max_items: int) -> Dict[str, Any]:
    """Lint the whole list, including cross-item checks."""
    findings: List[Dict[str, str]] = []
    for i, item in enumerate(items, 1):
        findings += lint_item(i, item)
    if len(items) > max_items:
        findings.append({"item": "list", "level": "warn",
                         "message": f"{len(items)} items; ship the top {max_items} and park the rest"})
    seen: Dict[tuple, int] = {}
    for i, item in enumerate(items, 1):
        key = (str(item.get("file", "")).lower(), str(item.get("category", "")).lower())
        if key[0] and key in seen:
            findings.append({"item": f"item {i}", "level": "warn",
                             "message": f"same file and category as item {seen[key]}; merge them"})
        seen.setdefault(key, i)
    ranks = [SEVERITIES.get(str(it.get("severity", "")).lower(), 0) for it in items]
    if any(b > a for a, b in zip(ranks, ranks[1:]) if a and b):
        findings.append({"item": "list", "level": "warn", "message": "items are not ranked by severity (high first)"})
    errors = sum(1 for f in findings if f["level"] == "error")
    return {"items": len(items), "errors": errors, "warnings": len(findings) - errors, "findings": findings}


def render_text(report: Dict[str, Any], source: str) -> str:
    """Human-readable output."""
    head = f"{source}: {report['items']} items, {report['errors']} errors, {report['warnings']} warnings"
    if not report["findings"]:
        return head + "\nclean — every item is a concrete, evidenced environment change"
    rows = [f"  [{f['level']:5}] {f['item']}: {f['message']}" for f in report["findings"]]
    return "\n".join([head] + rows)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Lint a session-retro action list.")
    parser.add_argument("--input", required=True, help="action items (.json or markdown with the template table)")
    parser.add_argument("--max-items", type=int, default=7, help="warn above this many items")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        items = load_items(Path(args.input))
    except (OSError, ValueError) as exc:
        print(f"error: cannot lint {args.input}: {exc}", file=sys.stderr)
        sys.exit(2)
    report = lint(items, args.max_items)
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(report, args.input))
    failed = report["errors"] > 0 or (args.strict and report["warnings"] > 0)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
