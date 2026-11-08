#!/usr/bin/env python3
"""Lint a GLOSSARY.md and find banned aliases used in docs or code.

Parses terms written as '### Term' headings followed by '**Definition:**',
'**Avoid:**', '**Owner:**', '**Related:**' and '**Status:**' lines. Reports
missing definitions and owners, duplicate terms, aliases that collide with a
canonical term or with another term's alias, circular and overlong definitions,
and implementation detail in definitions. With --scan it searches text and
source files for aliases the glossary says to avoid, splitting camelCase and
snake_case identifiers so 'purchaseId' counts as 'purchase'.

Usage:
  python3 glossary_lint.py --glossary GLOSSARY.md
  python3 glossary_lint.py --glossary GLOSSARY.md --scan docs/ src/ --format json

Exit codes: 0 clean, 1 errors or banned-alias usages found, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

FIELD_RE = re.compile(r"^\s*[-*]?\s*\*\*(definition|avoid|owner|related|status):\*\*\s*(.*)$", re.IGNORECASE)
IMPL_WORDS = ("table", "column", "class", "endpoint", "json", "database", "foreign key", "microservice",
              "api", "schema", "row", "boolean", "enum", "dto", "repository")
SCAN_EXTS = {".md", ".txt", ".rst", ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rb",
             ".cs", ".sql", ".yaml", ".yml", ".feature"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
STATUSES = {"agreed", "proposed", "deprecated"}


def parse_glossary(text: str) -> List[Dict[str, Any]]:
    """Return term records parsed from '### Term' blocks."""
    terms: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}
    group = ""
    for no, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            group = line[3:].strip()
            continue
        if line.startswith("### "):
            current = {"term": line[4:].strip(), "line": no, "group": group, "definition": "",
                       "avoid": [], "owner": "", "related": [], "status": "agreed"}
            terms.append(current)
            continue
        m = FIELD_RE.match(line)
        if m and current:
            key, value = m.group(1).lower(), m.group(2).strip()
            if key in ("avoid", "related"):
                current[key] = [v.strip().strip("_*`") for v in re.split(r"[,;]", value) if v.strip()]
            else:
                current[key] = value
        elif current and current["definition"] and line.strip() and not line.startswith("#"):
            if not FIELD_RE.match(line) and not line.lstrip().startswith(("-", "*", "|")):
                current["definition"] += " " + line.strip()
    return terms


def norm(text: str) -> str:
    """Lowercase and split camelCase / snake_case / kebab-case into spaced words."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    return re.sub(r"[_\-]+", " ", text).lower()


def lint(terms: List[Dict[str, Any]], max_words: int) -> List[Dict[str, Any]]:
    """Check term records and return findings."""
    out: List[Dict[str, Any]] = []

    def add(level: str, term: Dict[str, Any], msg: str) -> None:
        out.append({"level": level, "term": term["term"], "line": term["line"], "message": msg})

    canon: Dict[str, Dict[str, Any]] = {}
    for t in terms:
        key = t["term"].lower()
        if key in canon:
            add("error", t, f"duplicate term (first defined on line {canon[key]['line']})")
        canon.setdefault(key, t)
    alias_owner: Dict[str, str] = {}
    for t in terms:
        d = t["definition"].strip()
        if not d:
            add("error", t, "no definition")
        else:
            words = len(d.split())
            sentences = len([s for s in re.split(r"[.!?](?:\s|$)", d) if s.strip()])
            if words > max_words or sentences > 2:
                add("warn", t, f"definition is {words} words / {sentences} sentences; keep it to two sentences")
            if re.search(rf"\b{re.escape(t['term'].lower())}\b", d.lower()):
                add("warn", t, "definition uses the term itself (circular)")
            hits = [w for w in IMPL_WORDS if re.search(rf"\b{w}s?\b", d.lower())]
            if hits:
                add("warn", t, f"definition mentions implementation ({', '.join(hits)}); say what it is, not how it is stored")
        if not t["owner"]:
            add("warn", t, "no owner; nobody can settle disputes about this term")
        if t["status"].lower() not in STATUSES:
            add("error", t, f"status '{t['status']}' not one of {', '.join(sorted(STATUSES))}")
        for alias in t["avoid"]:
            a = alias.lower()
            if a == t["term"].lower():
                add("error", t, "term lists itself as an alias to avoid")
            elif a in canon:
                add("error", t, f"avoided alias '{alias}' is itself a canonical term; the two meanings collide")
            elif a in alias_owner and alias_owner[a] != t["term"]:
                add("error", t, f"alias '{alias}' is also avoided under '{alias_owner[a]}'; it must map to one term")
            alias_owner.setdefault(a, t["term"])
        for rel in t["related"]:
            if rel.lower() not in canon:
                add("warn", t, f"related term '{rel}' is not defined in this glossary")
    return out


def scan(paths: List[str], terms: List[Dict[str, Any]], glossary: Path) -> List[Dict[str, Any]]:
    """Find avoided aliases in files, matching whole words on normalised text."""
    aliases = [(norm(a), a, t["term"]) for t in terms if t["status"].lower() != "deprecated" for a in t["avoid"]]
    patterns = [(re.compile(rf"(?<![a-z0-9]){re.escape(n)}s?(?![a-z0-9])"), a, term) for n, a, term in aliases]
    files: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files += [f for f in sorted(p.rglob("*")) if f.is_file() and f.suffix in SCAN_EXTS
                      and not SKIP_DIRS & set(f.parts)]
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(raw)
    hits: List[Dict[str, Any]] = []
    for f in files:
        if f.resolve() == glossary.resolve():
            continue
        for no, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            low = norm(line)
            for pat, alias, term in patterns:
                if pat.search(low):
                    hits.append({"file": str(f), "line": no, "alias": alias, "use_instead": term,
                                 "text": line.strip()[:100]})
    return hits


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Glossary: {report['glossary']}  ({report['terms']} terms)")
    for f in report["findings"]:
        print(f"  [{f['level'].upper():5}] line {f['line']:<4} {f['term']}: {f['message']}")
    if report["scanned"]:
        print(f"\nBanned aliases in scanned files: {len(report['alias_hits'])}")
        for h in report["alias_hits"]:
            print(f"  {h['file']}:{h['line']}  '{h['alias']}' -> use '{h['use_instead']}'  | {h['text']}")
    print(f"\nVerdict: {report['verdict']}  ({report['errors']} error(s), {report['warnings']} warning(s))")


def main() -> None:
    """Parse arguments, lint the glossary, scan files, and exit with the gate result."""
    p = argparse.ArgumentParser(description="Lint a GLOSSARY.md and find banned aliases in docs or code.")
    p.add_argument("--glossary", required=True, help="path to GLOSSARY.md")
    p.add_argument("--scan", nargs="*", default=[], help="files or directories to search for avoided aliases")
    p.add_argument("--max-words", type=int, default=45, help="definition word budget (default 45)")
    p.add_argument("--format", choices=("text", "json"), default="text", help="output format (default text)")
    args = p.parse_args()
    gpath = Path(args.glossary)
    try:
        terms = parse_glossary(gpath.read_text(encoding="utf-8"))
        findings = lint(terms, args.max_words)
        hits = scan(args.scan, terms, gpath) if args.scan else []
    except (OSError, FileNotFoundError) as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        sys.exit(2)
    if not terms:
        print(f"error: no '### Term' entries found in {gpath}", file=sys.stderr)
        sys.exit(2)
    errors = sum(f["level"] == "error" for f in findings)
    report = {"glossary": str(gpath), "terms": len(terms), "findings": findings, "errors": errors,
              "warnings": sum(f["level"] == "warn" for f in findings), "scanned": bool(args.scan),
              "alias_hits": hits, "verdict": "FAIL" if errors or hits else "PASS"}
    output(report, args.format)
    sys.exit(1 if errors or hits else 0)


if __name__ == "__main__":
    main()
