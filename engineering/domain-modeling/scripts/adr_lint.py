#!/usr/bin/env python3
"""Lint a directory of decision records (ADRs) and suggest the next number.

Expects files named NNNN-kebab-slug.md whose first heading is '# NNNN. Title'
followed by '**Status:**' and '**Date:**' lines and '## Context', '## Decision'
and '## Consequences' sections. Checks numbering (duplicates, gaps, title
mismatch), status values, supersession links in both directions, required
sections, decisive wording, and whether accepted records name an alternative.

Usage:
  python3 adr_lint.py --dir docs/adr
  python3 adr_lint.py --input adr_set.json --next-title "Publish events for billing" --format json

Exit codes: 0 clean, 1 errors found, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

NAME_RE = re.compile(r"^(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
TITLE_RE = re.compile(r"^#\s+(\d{4})\.\s+(.+)$")
FIELD_RE = re.compile(r"^\s*[-*]?\s*\*\*(status|date|deciders|supersedes):\*\*\s*(.*)$", re.IGNORECASE)
STATUSES = ("proposed", "accepted", "rejected", "deprecated", "superseded")
DECISIVE = re.compile(r"\b(we will|we use|we choose|we chose|we adopt|we keep|we do not|we won't|"
                      r"is chosen|will be|must|decided)\b", re.IGNORECASE)
STOPWORDS = {"a", "an", "the", "of", "for", "to", "and", "in", "on", "with", "use", "by"}


def parse(name: str, text: str) -> Dict[str, Any]:
    """Extract number, title, fields and sections from one record."""
    rec: Dict[str, Any] = {"file": name, "number": None, "slug": "", "title": "", "title_number": None,
                           "status": "", "superseded_by": None, "supersedes": [], "date": "", "sections": {}}
    m = NAME_RE.match(Path(name).name)
    if m:
        rec["number"], rec["slug"] = int(m.group(1)), m.group(2)
    section = None
    for line in text.splitlines():
        t = TITLE_RE.match(line)
        if t and not rec["title"]:
            rec["title_number"], rec["title"] = int(t.group(1)), t.group(2).strip()
            continue
        f = FIELD_RE.match(line)
        if f and section is None:
            key, value = f.group(1).lower(), f.group(2).strip()
            if key == "status":
                rec["status"] = value
                s = re.search(r"superseded by\s+(?:adr-|dr-)?(\d{1,4})", value, re.IGNORECASE)
                rec["superseded_by"] = int(s.group(1)) if s else None
            elif key == "supersedes":
                rec["supersedes"] = [int(n) for n in re.findall(r"\d{1,4}", value)]
            else:
                rec[key] = value
            continue
        if line.startswith("## "):
            section = line[3:].strip().lower()
            rec["sections"][section] = ""
        elif section is not None:
            rec["sections"][section] += line.strip() + " "
    return rec


def lint(recs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Check every record and the set as a whole."""
    out: List[Dict[str, str]] = []

    def add(level: str, where: str, msg: str) -> None:
        out.append({"level": level, "file": where, "message": msg})

    by_num: Dict[int, List[str]] = {}
    for r in recs:
        if r["number"] is None:
            add("error", r["file"], "filename is not NNNN-kebab-slug.md")
            continue
        by_num.setdefault(r["number"], []).append(r["file"])
    for n, files in sorted(by_num.items()):
        if len(files) > 1:
            add("error", files[1], f"number {n:04d} is also used by {files[0]}")
    nums = sorted(by_num)
    for missing in sorted(set(range(nums[0], nums[-1] + 1)) - set(nums)) if nums else []:
        add("warn", f"{missing:04d}", "gap in numbering; records are never deleted, mark them rejected or deprecated")
    known = {r["number"]: r for r in recs if r["number"] is not None}
    for r in recs:
        f = r["file"]
        if not r["title"]:
            add("error", f, "first heading must be '# NNNN. Title'")
        elif r["number"] is not None and r["title_number"] != r["number"]:
            add("error", f, f"title number {r['title_number']:04d} does not match filename {r['number']:04d}")
        if r["title"] and len(r["title"]) > 80:
            add("warn", f, "title over 80 characters; state the decision, not the discussion")
        if r["title"] and r["slug"]:
            words = {w for w in re.findall(r"[a-z0-9]+", r["title"].lower()) if w not in STOPWORDS}
            if words and not words & set(r["slug"].split("-")):
                add("warn", f, "slug shares no words with the title")
        status = r["status"].lower()
        if not status:
            add("error", f, "missing **Status:** line")
        elif not status.startswith(STATUSES):
            add("error", f, f"status '{r['status']}' is not one of {', '.join(STATUSES)}")
        if status.startswith("superseded"):
            target = r["superseded_by"]
            if target is None:
                add("error", f, "superseded without naming the record that replaces it")
            elif target not in known:
                add("error", f, f"superseded by {target:04d}, which does not exist")
            elif r["number"] not in known[target]["supersedes"]:
                add("warn", f, f"{target:04d} does not list '**Supersedes:** {r['number']:04d}'")
        for old in r["supersedes"]:
            if old in known and not known[old]["status"].lower().startswith("superseded"):
                add("error", f, f"supersedes {old:04d}, but {old:04d} is not marked superseded")
            elif old in known and known[old]["superseded_by"] not in (None, r["number"]):
                add("error", f, f"supersedes {old:04d}, but {old:04d} names {known[old]['superseded_by']:04d} "
                                f"as its replacement")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", r["date"] or ""):
            add("warn", f, "missing or non-ISO **Date:** (YYYY-MM-DD)")
        for needed in ("context", "decision"):
            if not r["sections"].get(needed, "").strip():
                add("error", f, f"missing or empty '## {needed.title()}' section")
        decision = r["sections"].get("decision", "")
        if decision.strip() and not DECISIVE.search(decision):
            add("warn", f, "decision section has no decisive statement ('We will ...', 'We do not ...')")
        if "consequences" not in r["sections"]:
            add("warn", f, "no '## Consequences' section")
        has_alt = any(k.startswith(("alternatives", "options", "considered")) for k in r["sections"])
        if status.startswith("accepted") and not has_alt:
            add("warn", f, "accepted with no alternatives recorded; if there was no real trade-off it may not need a record")
    return out


def next_name(recs: List[Dict[str, Any]], title: str) -> str:
    """Return the next filename for a new record with the given title."""
    n = max([r["number"] for r in recs if r["number"] is not None] or [0]) + 1
    words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOPWORDS][:6]
    return f"{n:04d}-{'-'.join(words) or 'decision'}.md"


def load(args: argparse.Namespace) -> List[Dict[str, Any]]:
    """Load records from a directory or a JSON bundle of {filename: text}."""
    if args.input:
        files = json.loads(Path(args.input).read_text(encoding="utf-8")).get("files", {})
        return [parse(n, t) for n, t in sorted(files.items())]
    d = Path(args.dir)
    if not d.is_dir():
        raise FileNotFoundError(f"not a directory: {d}")
    return [parse(p.name, p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.md"))
            if p.name.lower() not in ("readme.md", "index.md", "template.md")]


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Decision records: {report['records']}")
    for f in report["findings"]:
        print(f"  [{f['level'].upper():5}] {f['file']}: {f['message']}")
    if report.get("next_file"):
        print(f"\nNext record: {report['next_file']}")
    print(f"Verdict: {report['verdict']}  ({report['errors']} error(s), {report['warnings']} warning(s))")


def main() -> None:
    """Parse arguments, lint the records, and exit with the gate result."""
    p = argparse.ArgumentParser(description="Lint decision records and suggest the next number.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--dir", help="directory of NNNN-slug.md records")
    src.add_argument("--input", help='JSON bundle: {"files": {"0001-slug.md": "text"}}')
    p.add_argument("--next-title", help="print the filename the next record with this title should use")
    p.add_argument("--format", choices=("text", "json"), default="text", help="output format (default text)")
    args = p.parse_args()
    try:
        recs = load(args)
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(f"error: cannot read records: {exc}", file=sys.stderr)
        sys.exit(2)
    findings = lint(recs)
    errors = sum(f["level"] == "error" for f in findings)
    report = {"records": len(recs), "findings": findings, "errors": errors,
              "warnings": sum(f["level"] == "warn" for f in findings),
              "next_file": next_name(recs, args.next_title) if args.next_title else None,
              "verdict": "FAIL" if errors else "PASS"}
    output(report, args.format)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
