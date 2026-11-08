#!/usr/bin/env python3
"""Check a repo research note: every claim cited, citations resolve, sources mostly primary.

A repo research note is a markdown file that answers one technical question from primary
sources (official docs, specs, source code, changelogs, first-party APIs) and lives in the
repository next to the work it informs. This checker reads such a note and reports:
claim lines with no citation, citation markers that point at no listed source, listed
sources never cited, sources with no access date or version, a source list dominated by
secondary sources, and missing Question / Answer / Sources sections.

Usage:
  python3 research_note_checker.py --input docs/research/rate-limits.md
  python3 research_note_checker.py --input note.md --max-uncited 0.1 --format json

Exit codes: 0 = note passes, 1 = at least one error, 2 = file unreadable.
Standard library only; no network: links are checked for form, never fetched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

CITE_RE = re.compile(r"\[(\d+)\](?!\()")
SOURCE_LINE_RE = re.compile(r"^\s*(?:[-*]\s*)?\[(\d+)\]:?\s*(.+)$")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
DATE_RE = re.compile(r"\b(20\d\d-\d\d(?:-\d\d)?|accessed|retrieved|v\d+(?:\.\d+)+|version \S+|commit [0-9a-f]{7,})",
                     re.IGNORECASE)
SECONDARY_HOSTS = ("medium.com", "dev.to", "stackoverflow.com", "reddit.com", "quora.com", "hashnode",
                   "substack.com", "towardsdatascience.com", "geeksforgeeks.org", "w3schools.com",
                   "youtube.com", "twitter.com", "x.com", "linkedin.com")
REQUIRED = ("question", "answer", "sources")
SKIP_LINE_RE = re.compile(r"^\s*(#|>|\||```|---|\*\*(status|date|author|question)\b)", re.IGNORECASE)


def split_sections(text: str) -> Dict[str, List[str]]:
    """Map lowercase heading text to the lines beneath it."""
    sections: Dict[str, List[str]] = {"_preamble": []}
    current = "_preamble"
    for line in text.splitlines():
        heading = re.match(r"^#{1,6}\s+(.*)$", line)
        if heading:
            current = heading.group(1).strip().lower()
            sections.setdefault(current, [])
        else:
            sections[current].append(line)
    return sections


def claim_units(lines: List[str]) -> List[str]:
    """Group lines into claim units: each bullet, or each paragraph of wrapped prose."""
    units: List[str] = []
    buf: List[str] = []
    in_code = False

    def flush() -> None:
        if buf:
            units.append(" ".join(buf))
            buf.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if not stripped or SKIP_LINE_RE.match(stripped):
            flush()
            continue
        if re.match(r"^([-*]|\d+\.)\s+", stripped):
            flush()
        buf.append(stripped)
    flush()
    return units


def is_claim(line: str) -> bool:
    """A claim unit is substantive prose or a bullet (at least six words)."""
    stripped = line.strip()
    if not stripped or SKIP_LINE_RE.match(stripped):
        return False
    words = re.sub(r"[`*_\[\]()]", " ", stripped).split()
    return len(words) >= 6


def check(text: str, max_uncited: float) -> Dict[str, Any]:
    """Run all checks on the note text."""
    findings: List[Dict[str, str]] = []

    def add(level: str, msg: str) -> None:
        findings.append({"level": level, "message": msg})

    sections = split_sections(text)
    names = list(sections)
    for req in REQUIRED:
        if not any(req in n for n in names):
            add("error", f"missing a '{req.title()}' section")
    source_key = next((n for n in names if "sources" in n or "references" in n), None)

    sources: Dict[str, str] = {}
    for line in sections.get(source_key, []) if source_key else []:
        match = SOURCE_LINE_RE.match(line)
        if match:
            sources[match.group(1)] = match.group(2).strip()

    claims, uncited = 0, []
    cited: set = set()
    for name, lines in sections.items():
        if name == source_key:
            continue
        exempt = name == "_preamble" or any(k in name for k in ("question", "inference"))
        for unit in claim_units(lines):
            refs = CITE_RE.findall(unit)
            cited.update(refs)
            if exempt or not is_claim(unit):
                continue
            claims += 1
            if not refs and not URL_RE.search(unit):
                uncited.append(unit[:80])

    for ref in sorted(cited - set(sources), key=int):
        add("error", f"citation [{ref}] has no entry in the sources list")
    for ref in sorted(set(sources) - cited, key=int):
        add("warn", f"source [{ref}] is listed but never cited")
    ratio = len(uncited) / claims if claims else 0.0
    if ratio > max_uncited:
        add("error", f"{len(uncited)}/{claims} claims uncited ({ratio:.0%} > {max_uncited:.0%})")
    for line in uncited[:5]:
        add("info", f"uncited: {line}")

    secondary = 0
    for ref, entry in sources.items():
        url = URL_RE.search(entry)
        host = urlparse(url.group(0)).netloc.lower() if url else ""
        if not url and "/" not in entry:
            add("warn", f"source [{ref}] has no URL or file path")
        if any(h in host for h in SECONDARY_HOSTS):
            secondary += 1
        if not DATE_RE.search(entry):
            add("warn", f"source [{ref}] has no access date, version or commit")
    if sources and secondary / len(sources) > 0.34:
        add("error", f"{secondary}/{len(sources)} sources are secondary; trace claims to the owning docs or code")
    if not sources:
        add("error", "no numbered sources found (expected lines like '[1] https://… (accessed 2026-11-08)')")

    errors = sum(1 for f in findings if f["level"] == "error")
    return {"claims": claims, "uncited": len(uncited), "sources": len(sources), "secondary_sources": secondary,
            "errors": errors, "warnings": sum(1 for f in findings if f["level"] == "warn"), "findings": findings}


def render_text(path: str, report: Dict[str, Any]) -> str:
    """Human-readable output."""
    head = (f"{path}: {report['claims']} claims, {report['uncited']} uncited, {report['sources']} sources "
            f"({report['secondary_sources']} secondary) — {report['errors']} errors, {report['warnings']} warnings")
    body = [f"  [{f['level']:5}] {f['message']}" for f in report["findings"]]
    return "\n".join([head] + (body or ["  clean — every claim traces to a listed source"]))


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Check citations and source quality in a repo research note.")
    parser.add_argument("--input", required=True, help="markdown research note")
    parser.add_argument("--max-uncited", type=float, default=0.15, help="max share of claims (bullets/paragraphs) without a citation")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        text = Path(args.input).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
        sys.exit(2)
    report = check(text, args.max_uncited)
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(args.input, report))
    sys.exit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
