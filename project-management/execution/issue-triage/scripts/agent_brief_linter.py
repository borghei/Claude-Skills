#!/usr/bin/env python3
"""Lint agent briefs before an issue moves to ready-for-agent or ready-for-human.

An agent brief is the contract a coding agent (or a human) works from. This
linter reads briefs as JSON ({"briefs": [...]}) or as markdown with one
"## Agent Brief" heading per brief and "**Field:**" lines, then flags missing
sections, file paths and line numbers that will go stale, vague or compound
acceptance criteria, procedural (how-to) language, a missing out-of-scope list,
a verification step that is not runnable, unfilled template placeholders,
and ready-for-human briefs that never
say why the work cannot be delegated.

Usage:
    python3 agent_brief_linter.py --input assets/sample_agent_briefs.json
    python3 agent_brief_linter.py --input assets/sample_agent_brief_clean.md --format json

Exit codes: 0 no errors, 1 at least one error finding, 2 unreadable or invalid input.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

FIELDS = {  # markdown label (lower-case) -> canonical key
    "category": "category", "target state": "target_state", "summary": "summary",
    "current behavior": "current_behavior", "current behaviour": "current_behavior",
    "desired behavior": "desired_behavior", "desired behaviour": "desired_behavior",
    "key interfaces": "key_interfaces", "acceptance criteria": "acceptance_criteria",
    "out of scope": "out_of_scope", "verification": "verification",
    "why not delegated": "human_reason",
}
REQUIRED = ["category", "summary", "current_behavior", "desired_behavior",
            "acceptance_criteria", "out_of_scope", "verification"]
LIST_KEYS = {"key_interfaces", "acceptance_criteria", "out_of_scope"}
EXT = r"(?:py|ts|tsx|js|jsx|go|rb|java|kt|rs|swift|cs|cpp|c|h|php|vue|sql|ya?ml|toml|scala|ex|exs)"
PATH_RE = re.compile(r"(?:[\w.-]+/)+[\w.-]+\.%s\b|\b[\w-]+\.%s:\d+" % (EXT, EXT))
LINE_RE = re.compile(r"\b(?:on |at |around )?line\s+\d+\b|\bL\d{1,5}\b", re.IGNORECASE)
VAGUE_RE = re.compile(r"\b(works?|working|correctly|properly|as expected|gracefully|appropriate(?:ly)?|"
                      r"user[- ]friendly|intuitive|fast(?:er)?|better|improved?|robust|seamless(?:ly)?|"
                      r"etc\.?|and so on|no bugs|bug[- ]free)\b", re.IGNORECASE)
PROCEDURAL_RE = re.compile(r"\b(open the file|go to|navigate to|scroll|add a line|insert (?:a|the) line|"
                           r"edit the|change the code|modify the function|in the handler|copy (?:the|this)|"
                           r"step \d|first,|then,? (?:add|edit|change|open))\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"<[A-Za-z#][^<>]{2,}>")
COMMAND_RE = re.compile(r"`[^`]+`|^\s*(?:\$\s*)?(?:npm|pnpm|yarn|make|pytest|python3?|go test|cargo|"
                        r"bundle|rake|mvn|gradle|dotnet|bash|sh|curl|gh)\b", re.IGNORECASE)


def parse_markdown(text: str) -> List[Dict[str, Any]]:
    """Split markdown into briefs at '## Agent Brief' headings and read '**Field:**' blocks."""
    chunks = re.split(r"^##\s+Agent Brief.*$", text, flags=re.MULTILINE | re.IGNORECASE)[1:]
    briefs: List[Dict[str, Any]] = []
    for n, chunk in enumerate(chunks, 1):
        brief: Dict[str, Any] = {"id": f"brief-{n}"}
        key = None
        for raw in chunk.splitlines():
            m = re.match(r"^\*\*([^*:]+):\*\*\s*(.*)$", raw.strip())
            if m:
                label = m.group(1).strip().lower()
                key = FIELDS.get(label)
                if label == "id":
                    brief["id"] = m.group(2).strip()
                    key = None
                elif key:
                    brief[key] = [] if key in LIST_KEYS else m.group(2).strip()
                    if key in LIST_KEYS and m.group(2).strip():
                        brief[key].append(m.group(2).strip())
                continue
            line = raw.strip()
            if not key or not line:
                continue
            if key in LIST_KEYS:
                item = re.sub(r"^[-*]\s*(\[[ xX]\]\s*)?", "", line)
                if line[:1] in "-*":
                    brief[key].append(item)
                elif brief[key]:
                    brief[key][-1] += " " + line
            else:
                brief[key] = (brief.get(key, "") + " " + line).strip()
        briefs.append(brief)
    return briefs


def load_briefs(path: Path) -> List[Dict[str, Any]]:
    """Load briefs from a .json or .md file."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".md", ".markdown"):
        briefs = parse_markdown(text)
    else:
        data = json.loads(text)
        briefs = data.get("briefs") if isinstance(data, dict) else data
    if not isinstance(briefs, list) or not briefs:
        raise ValueError("no briefs found (expected {'briefs': [...]} or '## Agent Brief' sections)")
    return briefs


def as_list(value: Any) -> List[str]:
    """Normalise a field to a list of non-empty strings."""
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [value.strip()] if isinstance(value, str) and value.strip() else []


def lint_brief(brief: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return the findings for one brief."""
    bid = str(brief.get("id") or "?")
    out: List[Dict[str, str]] = []

    def add(sev: str, rule: str, msg: str) -> None:
        out.append({"severity": sev, "brief": bid, "rule": rule, "message": msg})

    for key in REQUIRED:
        if not as_list(brief.get(key)):
            add("error", "missing-section", f"missing {key.replace('_', ' ')}")
    if not as_list(brief.get("key_interfaces")):
        add("warn", "missing-interfaces", "no key interfaces or contracts named")
    if str(brief.get("target_state", "ready-for-agent")) == "ready-for-human" and not as_list(brief.get("human_reason")):
        add("error", "human-reason", "ready-for-human brief must say why it cannot be delegated")
    summary = " ".join(as_list(brief.get("summary")))
    if len(summary) > 120:
        add("warn", "long-summary", f"summary is {len(summary)} chars; keep it to one line under 120")

    texts = {k: " ".join(as_list(brief.get(k))) for k in FIELDS.values()}
    for key, text in texts.items():
        for m in PATH_RE.finditer(text):
            add("error", "file-path", f"{key}: '{m.group(0)}' is a file path that will go stale; name the behaviour or interface")
        for m in LINE_RE.finditer(text):
            add("error", "line-number", f"{key}: '{m.group(0)}' references a line number")
        if PLACEHOLDER_RE.search(text):
            add("error", "placeholder", f"{key}: unfilled template placeholder '{PLACEHOLDER_RE.search(text).group(0)[:40]}'")
    for key in ("desired_behavior", "summary"):
        m = PROCEDURAL_RE.search(texts.get(key, ""))
        if m:
            add("warn", "procedural", f"{key}: '{m.group(0)}' describes how, not what; state the behaviour")

    criteria = as_list(brief.get("acceptance_criteria"))
    if 0 < len(criteria) < 2:
        add("warn", "thin-criteria", "only one acceptance criterion; most changes need an edge case too")
    for n, crit in enumerate(criteria, 1):
        vague = VAGUE_RE.search(crit)
        if vague:
            add("error", "vague-criterion", f"criterion {n} uses '{vague.group(0)}', which no test can check")
        if ";" in crit or (re.search(r"\band\b|\balso\b", crit, re.IGNORECASE) and len(crit) > 70):
            add("warn", "compound-criterion", f"criterion {n} bundles several checks; split it so each passes or fails alone")
    verify = " ".join(as_list(brief.get("verification")))
    if verify and not COMMAND_RE.search(verify):
        add("warn", "verification", "verification is not a runnable command; give the exact command or check")
    return out


def lint(briefs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Lint every brief and build the report."""
    findings: List[Dict[str, str]] = []
    rows = []
    for brief in briefs:
        if not isinstance(brief, dict):
            raise ValueError("each brief must be a JSON object")
        items = lint_brief(brief)
        findings += items
        errs = sum(1 for f in items if f["severity"] == "error")
        rows.append({"brief": str(brief.get("id") or "?"), "errors": errs,
                     "warnings": len(items) - errs, "ready": errs == 0})
    errors = sum(1 for f in findings if f["severity"] == "error")
    return {"briefs": len(briefs), "ready": sum(1 for r in rows if r["ready"]), "errors": errors,
            "warnings": len(findings) - errors, "passed": errors == 0, "per_brief": rows, "findings": findings}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    status = "PASS" if report["passed"] else "FAIL"
    print(f"Agent brief lint: {status}  ({report['ready']}/{report['briefs']} briefs ready to hand off)")
    for row in report["per_brief"]:
        mark = "ready" if row["ready"] else "BLOCKED"
        print(f"  {row['brief']:<14} {mark:<8} errors={row['errors']} warnings={row['warnings']}")
    for f in sorted(report["findings"], key=lambda x: (x["brief"], x["severity"] != "error")):
        print(f"  [{f['severity']:5}] {f['brief']:<14} {f['rule']:<19} {f['message']}")


def main() -> None:
    """Parse arguments, lint the briefs, and exit with the gate code."""
    parser = argparse.ArgumentParser(description="Lint agent briefs for completeness, durability and testability.")
    parser.add_argument("--input", required=True, help="briefs as JSON ({'briefs': [...]}) or markdown")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        report = lint(load_briefs(Path(args.input)))
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    except (json.JSONDecodeError, ValueError, AttributeError, TypeError) as exc:
        print(f"error: invalid brief input: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
