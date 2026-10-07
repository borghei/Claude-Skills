#!/usr/bin/env python3
"""Gate a LinkedIn post draft before the author pastes it into the composer.

Checks the things that are cheap to verify mechanically and expensive to get
wrong: an opening that fits before the feed truncates it, total length,
leftover placeholders and markup, paragraph density, hashtags, links, the
close, and whether the draft contains anything only its author could know.
Offline only; the tool reads a text file and prints a verdict.

Usage:
    python3 post_gate.py --input draft.txt
    python3 post_gate.py --input draft.txt --fold-chars 200 --format json
    python3 post_gate.py --input draft.txt --allow-links --max-warnings 2

Exit codes:
    0  gate passed
    1  gate failed (any blocker, or more warnings than --max-warnings)
    2  bad input (missing, empty or unreadable file; invalid option value)

Platform numbers (--max-chars, --fold-chars) are defaults current as of
writing; verify them in the product and override when they change.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

STOCK_OPENER = re.compile(
    r"in today's|in a world|in the (?:age|era) of|i(?:'m| am) (?:thrilled|excited|humbled|"
    r"delighted|proud|pleased|happy) to|let's (?:talk about|dive)|have you ever|ever wonder|"
    r"picture this|imagine this|unpopular opinion", re.IGNORECASE)
STOCK_CLOSER = re.compile(
    r"what do you think\?|^thoughts\?|\bagree\?|tag someone|repost if|share (?:this )?if you|"
    r"follow (?:me )?for more|let that sink in|read that again|comment .{1,25} (?:below|and i'll)",
    re.IGNORECASE | re.MULTILINE)
PLACEHOLDER = re.compile(
    r"\[(?:your|insert|company|name|topic|link|number|role|x)\b[^\]]*\]|\{\{?\s*[a-z_ ]+\s*\}?\}|"
    r"\bX{2,}\b|\bTK\b|\*\*[^*\n]+\*\*|^#{1,6}\s+\S", re.IGNORECASE | re.MULTILINE)
HABITS = {
    "contrast frame": re.compile(
        r"\b(?:isn't|is not|aren't|not) (?:just |only |about )?[^.,;\n]{2,40}[.,;—-]+\s*"
        r"(?:it's|it is|they're)\b", re.IGNORECASE),
    "question-and-answer bridge": re.compile(
        r"\bthe (?:result|truth|catch|kicker|lesson|secret)\?|here's the (?:thing|kicker)|"
        r"plot twist", re.IGNORECASE),
    "announced candor": re.compile(
        r"let me be honest|i'll be honest|to be honest|real talk|hard truth", re.IGNORECASE),
    "stock vocabulary": re.compile(
        r"\b(?:leverag\w*|unlock\w*|seamless\w*|game-chang\w*|holistic|synerg\w*|"
        r"transformative|cutting-edge|impactful|streamlin\w*)\b", re.IGNORECASE),
}
HASHTAG = re.compile(r"(?<!\w)#[A-Za-z][\w]*")
PROPER = re.compile(r"(?<=[a-z0-9,;:] )(?!LinkedIn)[A-Z][A-Za-z]{2,}")
FIRST_PERSON = re.compile(r"\b(?:I|[Ww]e|[Mm]y|[Oo]ur)\b")


def fail(message: str) -> None:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def read_draft(path_arg: str) -> str:
    """Read the draft from a file or stdin ('-'); exit 2 with guidance on failure."""
    try:
        text = sys.stdin.read() if path_arg == "-" else Path(path_arg).read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        fail(f"no readable file at {path_arg}. Pass a plain-text draft or '-' for stdin.")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path_arg} as UTF-8 text ({exc.__class__.__name__}). "
             "Save the draft as a plain .txt file and retry.")
    if not text.strip():
        fail(f"{path_arg} is empty. Paste the draft text into the file first.")
    return text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').strip()


def item(check: str, level: str, title: str, detail: str, fix: str) -> Dict[str, str]:
    """Build one finding record."""
    return {"id": check, "level": level, "title": title, "detail": detail, "fix": fix}


def check_opening(first: str, fold: int) -> List[Dict[str, str]]:
    """Check the opening line: fit before truncation, stock phrasing, case, teasing."""
    out: List[Dict[str, str]] = []
    letters = [c for c in first if c.isalpha()]
    if len(first) > fold:
        out.append(item("PG-01", "warn", "Opening runs past the fold",
                        f"{len(first)} characters; the feed cuts near {fold}",
                        "Move the figure, name or claim into the first clause, or shorten."))
    if STOCK_OPENER.search(first):
        out.append(item("PG-02", "block", "Stock opening phrase", first[:70],
                        "Open with the most specific true thing in the draft."))
    if len(letters) >= 8 and sum(c.isupper() for c in letters) / len(letters) > 0.7:
        out.append(item("PG-03", "block", "Opening line in capitals", first[:70],
                        "Write it in sentence case; let the content carry the weight."))
    if first.rstrip().endswith("?"):
        out.append(item("PG-04", "warn", "Opens on a question to the reader", first[:70],
                        "Open on a statement; a real question belongs at the close."))
    if len(first.split()) <= 6 and not re.search(r"\d", first) and not PROPER.search(first):
        out.append(item("PG-05", "warn", "Opening teases without content", first[:70],
                        "Say what happened. A short line needs a figure or a name in it."))
    return out


def check_body(text: str, rows: List[str], allow_links: bool, max_chars: int,
               min_chars: int) -> List[Dict[str, str]]:
    """Check length, leftovers, density, hashtags, links and specificity."""
    out: List[Dict[str, str]] = []
    if len(text) > max_chars:
        out.append(item("PG-06", "block", "Over the character limit",
                        f"{len(text)} characters against a limit of {max_chars}",
                        f"Cut {len(text) - max_chars} characters; start with the setup."))
    elif len(text) < min_chars:
        out.append(item("PG-07", "note", "Very short", f"{len(text)} characters",
                        "Fine for an announcement; otherwise add the evidence."))
    left = PLACEHOLDER.findall(text)
    if left:
        out.append(item("PG-08", "block", "Placeholder or markup left in",
                        "; ".join(sorted(set(m.strip() for m in left)))[:90],
                        "Fill every slot with the real value and strip asterisks and pound signs."))
    dense = [p for p in re.split(r"\n\s*\n", text) if len(p.split()) > 70]
    if dense:
        out.append(item("PG-09", "warn", "Dense paragraph",
                        f"{len(dense)} paragraph(s) over 70 words, e.g. '{dense[0][:50]}...'",
                        "Break at the point where the subject changes."))
    tags = HASHTAG.findall(text)
    if len(tags) > 3:
        out.append(item("PG-10", "warn", "Too many hashtags", f"{len(tags)}: {' '.join(tags)}",
                        "Keep up to three that name the subject; put them on the last line."))
    if not allow_links and re.search(r"https?://|www\.", text):
        out.append(item("PG-11", "warn", "Link in the body", "a URL appears in the post text",
                        "Heuristic: many authors put the link in the first comment. Pass "
                        "--allow-links if the link is the point of the post."))
    lacking = [name for name, found in (
        ("a figure", re.search(r"\d", text)), ("a named person, company or place",
                                                PROPER.search(text)),
        ("a first-person statement", FIRST_PERSON.search(text))) if not found]
    if len(lacking) >= 2:
        out.append(item("PG-12", "block", "Nothing only the author could know",
                        "missing: " + ", ".join(lacking),
                        "Ask the author for one real number and one name. Do not invent them."))
    elif lacking:
        out.append(item("PG-12", "note", "Thin on specifics", "missing: " + lacking[0],
                        "Add it if it exists; leave it if it does not."))
    fired = [name for name, pattern in HABITS.items() if pattern.search(text)]
    if len(fired) >= 2:
        out.append(item("PG-13", "warn", "Machine-sounding habits", ", ".join(fired),
                        "Rewrite the flagged lines; a full audit is the humanizer skill's job."))
    if text.count("!") > 2:
        out.append(item("PG-14", "note", "Exclamation marks", f"{text.count('!')} in the draft",
                        "Keep one at most."))
    prose = [r for r in rows if not HASHTAG.fullmatch(r.split()[0])] or rows
    closing = "\n".join(prose[-2:])
    if STOCK_CLOSER.search(closing):
        out.append(item("PG-15", "block", "Stock closing line", prose[-1][:70],
                        "Ask one question only someone with experience could answer, or stop."))
    return out


def gate(text: str, fold: int, max_chars: int, min_chars: int, allow_links: bool,
         max_warnings: int) -> Dict[str, Any]:
    """Run all checks and return the verdict with counts and findings."""
    rows = [ln.strip() for ln in text.splitlines() if ln.strip()]
    findings = check_opening(rows[0], fold) + check_body(
        text, rows, allow_links, max_chars, min_chars)
    order = {"block": 0, "warn": 1, "note": 2}
    findings.sort(key=lambda f: (order[f["level"]], f["id"]))
    counts = {lvl: sum(1 for f in findings if f["level"] == lvl) for lvl in order}
    passed = counts["block"] == 0 and counts["warn"] <= max_warnings
    return {"characters": len(text), "words": len(text.split()), "paragraphs": len(
        [p for p in re.split(r"\n\s*\n", text) if p.strip()]), "opening": rows[0],
        "opening_chars": len(rows[0]), "fold_chars": fold, "max_chars": max_chars,
        "counts": counts, "max_warnings": max_warnings, "passed": passed, "findings": findings}


def output(report: Dict[str, Any], fmt: str, source: str) -> None:
    """Print the gate report as JSON or readable text."""
    if fmt == "json":
        print(json.dumps({**report, "source": source}, indent=2, ensure_ascii=False))
        return
    counts = report["counts"]
    print(f"Post gate: {source}")
    print(f"{report['characters']} characters (limit {report['max_chars']}) | "
          f"{report['words']} words | {report['paragraphs']} paragraphs")
    print(f"Opening: {report['opening_chars']} characters (fold near {report['fold_chars']})")
    print(f"Verdict: {'PASS' if report['passed'] else 'FAIL'} - {counts['block']} blocker(s), "
          f"{counts['warn']} warning(s) (limit {report['max_warnings']}), {counts['note']} note(s)")
    print("=" * 72)
    for found in report["findings"]:
        print(f"[{found['level'].upper():<5}] {found['id']} {found['title']}")
        print(f"        seen: {found['detail']}")
        print(f"        fix : {found['fix']}")
    if not report["findings"]:
        print("Nothing flagged. Read it aloud once, then paste.")


def main() -> None:
    """Parse arguments, run the gate, print the report and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Gate a LinkedIn post draft before pasting it (offline).",
        epilog="Exit codes: 0 passed, 1 failed (a blocker, or warnings above "
               "--max-warnings), 2 bad input. Platform numbers are current as of "
               "writing; verify in the product and override as needed.")
    parser.add_argument("--input", required=True,
                        help="Plain-text draft, or '-' to read stdin.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--fold-chars", type=int, default=140,
                        help="Characters shown before the feed truncates (default: 140, "
                             "a conservative mobile estimate; desktop shows more).")
    parser.add_argument("--max-chars", type=int, default=3000,
                        help="Post character limit (default: 3000 as of writing).")
    parser.add_argument("--min-chars", type=int, default=250,
                        help="Below this the draft is noted as very short (default: 250).")
    parser.add_argument("--max-warnings", type=int, default=3,
                        help="Warnings tolerated before the gate fails (default: 3).")
    parser.add_argument("--allow-links", action="store_true",
                        help="Do not warn about a URL in the post body.")
    args = parser.parse_args()
    if min(args.fold_chars, args.max_chars) < 1 or min(args.min_chars, args.max_warnings) < 0:
        fail("--fold-chars and --max-chars must be positive; --min-chars and "
             "--max-warnings cannot be negative.")
    report = gate(read_draft(args.input), args.fold_chars, args.max_chars, args.min_chars,
                  args.allow_links, args.max_warnings)
    output(report, args.format, "stdin" if args.input == "-" else args.input)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
