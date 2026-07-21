#!/usr/bin/env python3
"""Offline link and anchor checker for Markdown.

Resolves relative file targets and in-document anchor targets against the local
filesystem. External http(s) links are inventoried and reported but never
fetched -- this tool makes zero network requests by design.

Usage:
    python3 link_checker.py --input article.md
    python3 link_checker.py --input article.md --format json --fail-on broken

Exit codes: 0 = all internal targets resolve, 1 = tool error, 2 = broken targets.
"""

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_ID_RE = re.compile(r"<a[^>]+(?:name|id)=[\"']([^\"']+)[\"']", re.IGNORECASE)
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp://", "//")


@dataclass
class LinkRef:
    """One link or image reference extracted from a Markdown source file."""

    line: int
    text: str
    target: str
    is_image: bool
    kind: str = "unknown"
    status: str = "unchecked"
    detail: str = ""


def read_lines(path: Path) -> List[str]:
    """Read a UTF-8 text file into a list of lines, exiting cleanly on failure."""
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SystemExit(f"error: file not found: {path}")
    except UnicodeDecodeError:
        raise SystemExit(f"error: file is not UTF-8 text: {path}")


def slugify(text: str) -> str:
    """Convert heading text to a GitHub-style anchor slug."""
    stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    stripped = re.sub(r"[`*_~]", "", stripped)
    lowered = re.sub(r"[^\w\s-]", "", stripped.strip().lower())
    return re.sub(r"[\s_]+", "-", lowered).strip("-")


def collect_anchors(path: Path) -> Set[str]:
    """Return every anchor slug a Markdown file exposes (headings + HTML ids)."""
    anchors: Set[str] = set()
    fenced = False
    seen: Counter = Counter()
    for raw in read_lines(path):
        if raw.lstrip().startswith("```") or raw.lstrip().startswith("~~~"):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = HEADING_RE.match(raw)
        if match:
            slug = slugify(match.group(2))
            seen[slug] += 1
            anchors.add(slug if seen[slug] == 1 else f"{slug}-{seen[slug] - 1}")
        for found in HTML_ID_RE.findall(raw):
            anchors.add(found.strip().lower())
    return anchors


def find_duplicate_anchors(path: Path) -> List[Dict[str, Any]]:
    """Report heading slugs that occur more than once, since duplicates silently shift anchors."""
    counts: Counter = Counter()
    fenced = False
    for raw in read_lines(path):
        if raw.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        match = None if fenced else HEADING_RE.match(raw)
        if match:
            counts[slugify(match.group(2))] += 1
    return [{"slug": slug, "occurrences": n} for slug, n in sorted(counts.items()) if n > 1]

def extract_links(path: Path) -> List[LinkRef]:
    """Extract every inline link and image reference outside fenced code blocks."""
    refs: List[LinkRef] = []
    fenced = False
    for number, raw in enumerate(read_lines(path), start=1):
        if raw.lstrip().startswith("```") or raw.lstrip().startswith("~~~"):
            fenced = not fenced
            continue
        if fenced:
            continue
        for bang, text, target in LINK_RE.findall(raw):
            refs.append(LinkRef(line=number, text=text.strip(),
                                target=target.strip(), is_image=bang == "!"))
    return refs


def classify(target: str) -> str:
    """Classify a link target as external, anchor, absolute, or relative."""
    lowered = target.lower()
    if lowered.startswith(EXTERNAL_SCHEMES):
        return "external"
    if target.startswith("#"):
        return "anchor"
    if target.startswith("/"):
        return "absolute"
    return "relative"


def resolve_relative(ref: LinkRef, source: Path,
                     anchor_cache: Dict[Path, Set[str]]) -> None:
    """Resolve a relative target on disk, including its optional #anchor fragment."""
    raw_path, _, fragment = ref.target.partition("#")
    if not raw_path:
        ref.kind = "anchor"
        return
    candidate = (source.parent / raw_path).resolve()
    if not candidate.exists():
        ref.status = "broken"
        ref.detail = f"no file at {candidate}"
        return
    if not fragment:
        ref.status = "ok"
        ref.detail = str(candidate)
        return
    if candidate.suffix.lower() not in (".md", ".markdown"):
        ref.status = "unchecked"
        ref.detail = "fragment on a non-Markdown target; not resolvable offline"
        return
    if candidate not in anchor_cache:
        anchor_cache[candidate] = collect_anchors(candidate)
    if fragment.lower() in anchor_cache[candidate]:
        ref.status = "ok"
        ref.detail = f"{candidate}#{fragment}"
    else:
        ref.status = "broken"
        ref.detail = f"{candidate} has no anchor '{fragment}'"


def check_links(source: Path, root: Optional[Path]) -> List[LinkRef]:
    """Resolve every extracted reference; external links are inventoried only."""
    refs = extract_links(source)
    own_anchors = collect_anchors(source)
    anchor_cache: Dict[Path, Set[str]] = {source.resolve(): own_anchors}
    for ref in refs:
        ref.kind = classify(ref.target)
        if ref.kind == "external":
            ref.status = "not-checked"
            ref.detail = "external link inventoried, never fetched"
        elif ref.kind == "anchor":
            fragment = ref.target.lstrip("#").lower()
            if fragment in own_anchors:
                ref.status = "ok"
                ref.detail = f"#{fragment}"
            else:
                ref.status = "broken"
                ref.detail = f"document has no anchor '{fragment}'"
        elif ref.kind == "absolute":
            if root is None:
                ref.status = "unchecked"
                ref.detail = "root-relative target; pass --root to resolve"
            else:
                candidate = (root / ref.target.lstrip("/").split("#")[0]).resolve()
                ref.status = "ok" if candidate.exists() else "broken"
                ref.detail = str(candidate) if candidate.exists() else f"no file at {candidate}"
        else:
            resolve_relative(ref, source, anchor_cache)
    return refs


def inventory_external(refs: List[LinkRef]) -> List[Dict[str, Any]]:
    """Group external targets by host with occurrence counts, without fetching."""
    hosts: Dict[str, Counter] = {}
    for ref in refs:
        if ref.kind != "external":
            continue
        remainder = ref.target.split("://", 1)[-1]
        host = remainder.split("/", 1)[0].split("?")[0] or "(none)"
        hosts.setdefault(host, Counter())[ref.target] += 1
    rows: List[Dict[str, Any]] = []
    for host in sorted(hosts):
        for url, count in sorted(hosts[host].items()):
            rows.append({"host": host, "url": url, "occurrences": count})
    return rows


def summarize(refs: List[LinkRef]) -> Dict[str, int]:
    """Count references by resolution status."""
    counts = Counter(ref.status for ref in refs)
    return {
        "total": len(refs),
        "ok": counts.get("ok", 0),
        "broken": counts.get("broken", 0),
        "external": counts.get("not-checked", 0),
        "unchecked": counts.get("unchecked", 0),
    }


def output(source: Path, refs: List[LinkRef], external: List[Dict[str, Any]], summary: Dict[str, int],
           duplicates: List[Dict[str, Any]], passed: bool, fmt: str) -> None:
    """Emit the link report as text or JSON."""
    if fmt == "json":
        print(json.dumps({"file": str(source), "passed": passed, "summary": summary,
                          "network_requests_made": 0, "duplicate_anchors": duplicates,
                          "links": [ref.__dict__ for ref in refs],
                          "external_inventory": external}, indent=2))
        return
    print(f"Link check (offline) — {source}")
    print(f"  {summary['total']} refs: {summary['ok']} ok, {summary['broken']} broken, "
          f"{summary['external']} external (not fetched), "
          f"{summary['unchecked']} unchecked")
    print("-" * 72)
    broken = [r for r in refs if r.status == "broken"]
    if broken:
        print("  BROKEN INTERNAL TARGETS")
        for ref in broken:
            kind = "image" if ref.is_image else "link"
            print(f"    line {ref.line:>4}  {kind} [{ref.text}] -> {ref.target}")
            print(f"              {ref.detail}")
    else:
        print("  no broken internal targets")
    unchecked = [r for r in refs if r.status == "unchecked"]
    if unchecked:
        print("\n  UNCHECKED")
        for ref in unchecked:
            print(f"    line {ref.line:>4}  {ref.target} — {ref.detail}")
    if duplicates:
        print("\n  DUPLICATE HEADING ANCHORS (later headings get -1, -2 suffixes)")
        for row in duplicates:
            print(f"    #{row['slug']} x{row['occurrences']}")
    if external:
        print(f"\n  EXTERNAL INVENTORY ({len(external)} unique urls, none fetched)")
        for row in external:
            print(f"    {row['occurrences']}x  {row['url']}  [{row['host']}]")
    print("-" * 72)
    print(f"  RESULT: {'PASS' if passed else 'FAIL'}")


def main() -> None:
    """Parse arguments, resolve links offline, print the report, set exit code."""
    parser = argparse.ArgumentParser(
        description="Offline Markdown link checker: resolves relative file targets "
                    "and anchor fragments on disk; inventories external links "
                    "without ever making a network request.",
        epilog="Exit codes: 0 ok, 1 tool error, 2 broken internal targets.")
    parser.add_argument("--input", required=True,
                        help="Path to the Markdown file to check.")
    parser.add_argument("--root", default=None,
                        help="Project root used to resolve root-relative (/path) "
                             "targets. Without it those are reported as unchecked.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--fail-on", choices=["broken", "unchecked", "never"],
                        default="broken",
                        help="What fails the run: 'broken' (default), 'unchecked' "
                             "(also fail on unresolvable targets), or 'never'.")
    parser.add_argument("--no-external", action="store_true",
                        help="Omit the external link inventory from the report.")
    args = parser.parse_args()
    try:
        source = Path(args.input)
        root = Path(args.root).resolve() if args.root else None
        refs = check_links(source, root)
        summary = summarize(refs)
        external = [] if args.no_external else inventory_external(refs)
        if args.fail_on == "never":
            passed = True
        elif args.fail_on == "unchecked":
            passed = summary["broken"] == 0 and summary["unchecked"] == 0
        else:
            passed = summary["broken"] == 0
        output(source, refs, external, summary, find_duplicate_anchors(source), passed, args.format)
        sys.exit(0 if passed else 2)
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        print(f"error: link check failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
