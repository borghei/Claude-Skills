#!/usr/bin/env python3
"""Extract candidate domain terms from conversations, docs and code.

Splits identifiers (camelCase, snake_case, kebab-case), removes English stop
words and generic programming vocabulary, then counts single words and two-word
phrases. Each candidate is classified against an optional GLOSSARY.md as
defined, an avoided alias (with the canonical term to use), or new. It also
lists glossary terms that never appear in the material, which are either stale
or named differently in practice.

Usage:
  python3 term_extract.py --paths meeting.txt src/billing --glossary GLOSSARY.md
  python3 term_extract.py --paths notes/ --min-count 3 --top 30 --format json

Exit codes: 0 no new candidate terms, 1 new candidates need a glossary decision, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

STOP = set("""a about above after again against all also am an and any are as at be because been before being
below between both but by can could did do does doing down during each either else even ever every few for
from further get gets got had has have having he her here hers him his how i if in into is it its itself just
keep let lets like make makes may me might more most much must my need needs no nor not now of off on once
one only or other our ours out over own per please probably really same says say see she should so some still
such sure than that thats the their them then there these they thing things think this those though through
to too two under until up us use used using very want wants was way we well were what when where which while
who whom why will with would yeah yes you your yours ok okay right actually basically just guess mean kind
sort lot lots maybe already always never first last next new old same different another today tomorrow week
month months year years day days time times end start back something anything nothing everything
someone anyone thing stay stays shift shifts ask asks asked write written""".split())
CODE = set("""abstract args async await bool boolean break case catch class const constructor continue def
default del dict elif else enum except export extends false final finally float for from func function get
id ids if impl import in int interface is isinstance kwargs lambda len let list map new none null num number
obj object package pass print private protected public raise readonly record return self set static str
string struct super switch this throw true try type typeof undefined var void while with yield data value
values item items result results response request req res err error errors config util utils helper helpers
manager handler service impl test tests mock fixture json http https api url uri tmp temp foo bar baz key
keys val idx index count size length name names info init args param params opts options callback cb fn""".split())
EXTS = {".md", ".txt", ".rst", ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rb", ".cs",
        ".sql", ".yaml", ".yml", ".feature", ".vtt", ".srt"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
WORD = re.compile(r"[a-z][a-z]+")
SPEAKER = re.compile(r"^\s*[A-Z][\w.' -]{0,30}:\s")
PROSE_EXTS = {".md", ".txt", ".rst", ".vtt", ".srt", ".feature"}


def norm(text: str) -> str:
    """Lowercase and split camelCase / snake_case / kebab-case into spaced words."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    return re.sub(r"[_\-]+", " ", text).lower()


def singular(word: str) -> str:
    """Crude plural folding so 'invoices' and 'invoice' count together."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def load_glossary(path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Return (canonical term -> display name, alias -> canonical display name)."""
    canon: Dict[str, str] = {}
    alias: Dict[str, str] = {}
    current = ""
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            canon[" ".join(singular(w) for w in norm(current).split())] = current
        m = re.match(r"^\s*[-*]?\s*\*\*avoid:\*\*\s*(.*)$", line, re.IGNORECASE)
        if m and current:
            for a in re.split(r"[,;]", m.group(1)):
                if a.strip():
                    alias[" ".join(singular(w) for w in norm(a.strip()).split())] = current
    return canon, alias


def collect(paths: List[str]) -> List[Path]:
    """Expand files and directories into readable text files."""
    files: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files += [f for f in sorted(p.rglob("*")) if f.is_file() and f.suffix in EXTS
                      and not SKIP_DIRS & set(f.parts)]
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(raw)
    return files


def count_terms(files: List[Path], skip: Path | None) -> Tuple[Counter, Dict[str, str]]:
    """Count content words and adjacent content-word pairs; keep one example location each."""
    counts: Counter = Counter()
    where: Dict[str, str] = {}
    for f in files:
        if skip is not None and f.resolve() == skip.resolve():
            continue
        prose = f.suffix in PROSE_EXTS
        for no, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if prose:
                line = SPEAKER.sub("", line)
            words = [singular(w) for w in WORD.findall(norm(line))]
            content = [w if w not in STOP and w not in CODE and len(w) > 2 else "" for w in words]
            grams = [w for w in content if w]
            grams += [f"{a} {b}" for a, b in zip(content, content[1:]) if a and b and a != b]
            for g in grams:
                counts[g] += 1
                where.setdefault(g, f"{f}:{no}")
    return counts, where


def classify(counts: Counter, where: Dict[str, str], canon: Dict[str, str], alias: Dict[str, str],
             min_count: int, top: int) -> Dict[str, Any]:
    """Split candidates into defined, aliased and new, and list unused glossary terms."""
    defined, aliased, new = [], [], []
    for term, n in counts.most_common():
        if n < min_count:
            break
        row = {"term": term, "count": n, "example": where[term]}
        if term in canon:
            defined.append({**row, "glossary_term": canon[term]})
        elif term in alias:
            aliased.append({**row, "use_instead": alias[term]})
        elif " " in term and all(part in canon or part in alias for part in term.split()):
            continue
        else:
            new.append(row)
    unigram_new = {r["term"] for r in new if " " not in r["term"]}
    new = [r for r in new if " " in r["term"] or not any(
        r["term"] in b["term"].split() and b["count"] >= r["count"] for b in new if " " in b["term"])]
    unused = sorted(v for k, v in canon.items() if counts.get(k, 0) == 0)
    return {"defined": defined, "aliased": aliased, "new": new[:top], "new_total": len(new),
            "unused_glossary_terms": unused, "new_single_words": len(unigram_new)}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Scanned {report['files']} file(s); glossary: {report['glossary'] or 'none'}")
    if report["aliased"]:
        print("\nAvoided aliases in use (replace them):")
        for r in report["aliased"]:
            print(f"  {r['count']:>4}  {r['term']:<24} -> {r['use_instead']:<16} e.g. {r['example']}")
    print(f"\nNew candidate terms ({report['new_total']}, showing {len(report['new'])}) — decide: add, alias, or ignore:")
    for r in report["new"]:
        print(f"  {r['count']:>4}  {r['term']:<28} e.g. {r['example']}")
    if report["defined"]:
        print("\nDefined terms seen: " + ", ".join(f"{r['glossary_term']} ({r['count']})" for r in report["defined"]))
    if report["unused_glossary_terms"]:
        print("Glossary terms never used here: " + ", ".join(report["unused_glossary_terms"]))


def main() -> None:
    """Parse arguments, extract candidates, and exit with the review signal."""
    p = argparse.ArgumentParser(description="Extract candidate domain terms from conversations, docs and code.")
    p.add_argument("--paths", nargs="+", required=True, help="files or directories to read")
    p.add_argument("--glossary", help="GLOSSARY.md to classify candidates against")
    p.add_argument("--min-count", type=int, default=2, help="minimum occurrences to report (default 2)")
    p.add_argument("--top", type=int, default=25, help="maximum new candidates to list (default 25)")
    p.add_argument("--format", choices=("text", "json"), default="text", help="output format (default text)")
    args = p.parse_args()
    try:
        canon, alias = load_glossary(args.glossary) if args.glossary else ({}, {})
        files = collect(args.paths)
        counts, where = count_terms(files, Path(args.glossary) if args.glossary else None)
    except (OSError, FileNotFoundError) as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        sys.exit(2)
    report = classify(counts, where, canon, alias, args.min_count, args.top)
    report.update({"files": len(files), "glossary": args.glossary or ""})
    output(report, args.format)
    sys.exit(1 if report["new_total"] else 0)


if __name__ == "__main__":
    main()
