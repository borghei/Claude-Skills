#!/usr/bin/env python3
"""Pre-publication review gate for authored Markdown.

Validates heading structure, frontmatter schema, and accessibility affordances, then applies a CI
severity gate. No network access, no external packages.
Usage: python3 md_review_gate.py --input article.md --config review_config.json [--format json]
Exit codes: 0 = gate passed, 1 = tool error, 2 = gate failed.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SEV = {"info": 0, "warning": 1, "error": 2}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]*)")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]*)")
TABLE_DELIM_RE = re.compile(r"^\s*\|[\s:|-]*-[\s:|-]*\|\s*$")
SMALL = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "up", "via", "with"}


@dataclass
class Finding:
    """A review finding: stable rule id, severity, source line, message carrying the fix."""
    rule: str
    severity: str
    line: int
    message: str


@dataclass
class Document:
    """A parsed Markdown document: frontmatter fields, prose lines, and the heading tree."""
    path: Path
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    has_frontmatter: bool = False
    body: List[Tuple[int, str]] = field(default_factory=list)
    headings: List[Tuple[int, int, str]] = field(default_factory=list)


def load_config(path: Optional[str]) -> Dict[str, Any]:
    """Load a review config JSON file, returning {} when none is supplied."""
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: config file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: config file is not valid JSON ({exc})")

def parse_frontmatter(lines: List[str]) -> Tuple[Dict[str, Any], bool, int]:
    """Parse a minimal YAML frontmatter block into (fields, present, end_index)."""
    if not lines or lines[0].strip() != "---":
        return {}, False, 0
    fields: Dict[str, Any] = {}
    key = ""
    for idx in range(1, len(lines)):
        raw = lines[idx]
        if raw.strip() == "---":
            return fields, True, idx + 1
        if raw.lstrip().startswith("- ") and key and isinstance(fields.setdefault(key, []), list):
            fields[key].append(raw.lstrip()[2:].strip())
        elif ":" in raw and not raw.startswith(" "):
            key, _, value = raw.partition(":")
            key, value = key.strip(), value.strip().strip("\"'")
            fields[key] = value if value else []
    return fields, False, 0

def parse_document(path: Path) -> Document:
    """Read a Markdown file into a Document, skipping fenced code blocks."""
    try:
        raw = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SystemExit(f"error: input file not found: {path}")
    except UnicodeDecodeError:
        raise SystemExit(f"error: input file is not UTF-8 text: {path}")
    fields, present, start = parse_frontmatter(raw)
    doc = Document(path=path, frontmatter=fields, has_frontmatter=present)
    fenced = False
    for offset, text in enumerate(raw[start:], start=start + 1):
        if text.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced:
            continue
        doc.body.append((offset, text))
        match = HEADING_RE.match(text)
        if match:
            doc.headings.append((offset, len(match.group(1)), match.group(2).strip()))
    return doc

def check_frontmatter(doc: Document, cfg: Dict[str, Any]) -> List[Finding]:
    """Validate frontmatter presence, required fields, declared types, and max lengths."""
    rules = cfg.get("frontmatter", {})
    required, out = rules.get("required_fields", []), []  # type: List[str], List[Finding]
    if not required:
        return out
    if not doc.has_frontmatter:
        return [Finding("frontmatter.absent", "error", 1,
                        "No YAML frontmatter block; add a --- block with: " + ", ".join(required))]
    for name in required:
        if doc.frontmatter.get(name, "") in ("", []):
            state = "absent" if name not in doc.frontmatter else "empty"
            out.append(Finding("frontmatter.missing", "error", 1,
                               f"Required field '{name}' is {state}; set it to a real value."))
    for name, expected in rules.get("field_types", {}).items():
        value = doc.frontmatter.get(name)
        if value in (None, "", []):
            continue
        if expected == "list" and not isinstance(value, list):
            out.append(Finding("frontmatter.wrong-type", "error", 1,
                               f"Field '{name}' must be a list; rewrite it as a '- item' list."))
        elif expected == "date" and isinstance(value, str) and not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            out.append(Finding("frontmatter.wrong-type", "error", 1,
                               f"Field '{name}' is not ISO-8601: {value!r}; use YYYY-MM-DD."))
    for name, limit in rules.get("max_lengths", {}).items():
        value = doc.frontmatter.get(name)
        if isinstance(value, str) and len(value) > int(limit):
            out.append(Finding("frontmatter.too-long", "warning", 1,
                               f"Field '{name}' is {len(value)} chars; trim to the {limit}-char limit."))
    return out

def classify_heading_case(text: str) -> str:
    """Return 'title' or 'sentence' for a heading string, ignoring the first and small words."""
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    tail = [w for w in words[1:] if w.lower() not in SMALL] if len(words) > 1 else []
    return "title" if tail and sum(1 for w in tail if w[0].isupper()) / len(tail) >= 0.6 else "sentence"

def check_sections(doc: Document, rules: Dict[str, Any]) -> List[Finding]:
    """Flag sections whose prose word count falls outside the configured band."""
    out: List[Finding] = []
    hi, lo = int(rules.get("max_section_words", 400)), int(rules.get("min_section_words", 0))
    by_line, bounds = dict(doc.body), [(line, text) for line, _, text in doc.headings]
    for idx, (line, title) in enumerate(bounds):
        end = bounds[idx + 1][0] if idx + 1 < len(bounds) else max(by_line or {0: 0}) + 1
        words = sum(len(by_line.get(n, "").split()) for n in range(line + 1, end))
        if words > hi:
            out.append(Finding("structure.section-too-long", "warning", line,
                               f"Section '{title}' holds {words} words (limit {hi}); split it into subsections."))
        elif lo and words < lo and idx + 1 < len(bounds):
            out.append(Finding("structure.section-too-short", "info", line,
                               f"Section '{title}' holds only {words} words; merge it upward or expand it."))
    return out

def check_structure(doc: Document, cfg: Dict[str, Any]) -> List[Finding]:
    """Validate heading hierarchy, depth, capitalization consistency, and section length."""
    rules, out = cfg.get("structure", {}), []  # type: Dict[str, Any], List[Finding]
    h1s = [h for h in doc.headings if h[1] == 1]
    if rules.get("require_single_h1", True):
        if not h1s:
            out.append(Finding("structure.no-h1", "error", 1, "Document has no H1; add one '# Title'."))
        for line, _, text in h1s[1:]:
            out.append(Finding("structure.multiple-h1", "error", line,
                               f"Second H1 '{text}'; demote it to '##' — a page gets exactly one H1."))
    if rules.get("require_h1_first", True) and doc.headings and doc.headings[0][1] != 1:
        out.append(Finding("structure.h1-not-first", "warning", doc.headings[0][0],
                           f"First heading is H{doc.headings[0][1]}, not H1; open the document with an H1."))
    depth, previous = int(rules.get("max_heading_depth", 4)), 0
    for line, level, text in doc.headings:
        if not rules.get("allow_skipped_levels", False) and previous and level > previous + 1:
            out.append(Finding("structure.skipped-level", "error", line,
                               f"Heading jumps H{previous} -> H{level} at '{text}'; use H{previous + 1}."))
        if level > depth:
            out.append(Finding("structure.too-deep", "warning", line,
                               f"'{text}' is H{level}, past the H{depth} limit; flatten or split the page."))
        previous = level
    styles = [(line, classify_heading_case(text), text) for line, _, text in doc.headings]
    if len(styles) >= 3:
        want = rules.get("heading_case")
        if want not in ("title", "sentence"):
            titles = sum(1 for _, s, _ in styles if s == "title")
            want = "title" if titles > len(styles) - titles else "sentence"
        out += [Finding("structure.heading-case-inconsistent", "error", line,
                        f"Heading '{text}' is {style} case; document uses {want} case — rewrite it.")
                for line, style, text in styles if style != want]
    return out + check_sections(doc, rules)

def check_tables(doc: Document) -> List[Finding]:
    """Flag pipe tables that lack a header delimiter row (WCAG 1.3.1)."""
    out, block = [], []  # type: List[Finding], List[Tuple[int, str]]
    for line, text in list(doc.body) + [(-1, "")]:
        if text.strip().startswith("|"):
            block.append((line, text))
            continue
        if len(block) >= 2 and not TABLE_DELIM_RE.match(block[1][1]):
            out.append(Finding("a11y.table-no-header", "error", block[0][0],
                               "Table has no header delimiter row (WCAG 1.3.1); insert '| --- | --- |'."))
        block = []
    return out

def check_accessibility(doc: Document, cfg: Dict[str, Any]) -> List[Finding]:
    """Check alt text, link text, and table headers against WCAG-derived rules."""
    rules = cfg.get("accessibility", {})
    placeholders = {p.lower() for p in rules.get("placeholder_alt_text", [])}
    weak, out = {t.lower() for t in rules.get("non_descriptive_link_text", [])}, []
    min_alt, max_alt = int(rules.get("min_alt_text_chars", 6)), int(rules.get("max_alt_text_chars", 150))
    for line, text in doc.body:
        for alt, target in IMAGE_RE.findall(text):
            label = alt.strip()
            if not label:
                out.append(Finding("a11y.missing-alt", "error", line,
                                   f"Image {target} has empty alt text (WCAG 1.1.1); describe what it conveys."))
            elif label.lower() in placeholders or len(label) < min_alt:
                out.append(Finding("a11y.placeholder-alt", "warning", line,
                                   f"Alt text {label!r} is a placeholder (WCAG 1.1.1); describe the content."))
            elif len(label) > max_alt:
                out.append(Finding("a11y.alt-too-long", "info", line,
                                   f"Alt text is {len(label)} chars (limit {max_alt}); move detail to a caption."))
        for label, _ in LINK_RE.findall(text):
            clean = label.strip().rstrip(".!?").lower()
            if clean in weak:
                out.append(Finding("a11y.non-descriptive-link", "error", line,
                                   f"Link text {label!r} is meaningless out of context (WCAG 2.4.4); name the "
                                   "destination."))
            elif rules.get("flag_bare_urls_as_link_text", True) and clean.startswith("http"):
                out.append(Finding("a11y.bare-url-link-text", "warning", line,
                                   "Link text is a raw URL (WCAG 2.4.4); use a human-readable label."))
    return out + (check_tables(doc) if rules.get("require_table_headers", True) else [])

def apply_overrides(findings: List[Finding], cfg: Dict[str, Any]) -> List[Finding]:
    """Re-map finding severities using the config's severity_overrides table, then sort."""
    overrides = cfg.get("severity_overrides", {})
    for item in findings:
        if overrides.get(item.rule) in SEV:
            item.severity = overrides[item.rule]
    return sorted(findings, key=lambda f: (-SEV[f.severity], f.line))

def evaluate_gate(findings: List[Finding], cfg: Dict[str, Any],
                  fail_on: Optional[str]) -> Tuple[bool, Dict[str, int], str]:
    """Return (passed, counts, reason) after applying the configured gate thresholds."""
    gate = cfg.get("gate", {})
    level, counts = (fail_on or gate.get("fail_on", "error")), \
        {sev: sum(1 for f in findings if f.severity == sev) for sev in SEV}
    if level == "never":
        return True, counts, "gate disabled (fail_on=never)"
    blocking = sum(c for sev, c in counts.items() if SEV[sev] >= SEV.get(level, 2))
    cap = int(gate.get("max_warnings", 10 ** 6))
    if blocking:
        return False, counts, f"{blocking} finding(s) at or above '{level}'"
    if counts["warning"] > cap:
        return False, counts, f"{counts['warning']} warnings exceed max_warnings={cap}"
    return True, counts, "no blocking findings"

def output(doc: Document, findings: List[Finding], passed: bool, counts: Dict[str, int],
           reason: str, fmt: str) -> None:
    """Emit the review result as human-readable text or JSON."""
    if fmt == "json":
        print(json.dumps({"file": str(doc.path), "passed": passed, "reason": reason, "counts": counts,
                          "heading_count": len(doc.headings), "findings": [f.__dict__ for f in findings]}, indent=2))
        return
    print(f"Markdown review gate — {doc.path}\n  headings: {len(doc.headings)}   "
          f"errors: {counts['error']}  warnings: {counts['warning']}  info: {counts['info']}\n" + "-" * 72)
    if not findings:
        print("  no findings")
    for item in findings:
        print(f"  [{item.severity.upper():7}] line {item.line:>4}  {item.rule}\n            {item.message}")
    print("-" * 72 + f"\n  GATE: {'PASS' if passed else 'FAIL'} — {reason}")

def main() -> None:
    """Parse arguments, run the selected checks, print the report, and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Pre-publication review gate for authored Markdown: heading structure, "
                    "frontmatter schema, accessibility, and a CI-ready severity gate.",
        epilog="Exit codes: 0 pass, 1 tool error, 2 gate failure.")
    parser.add_argument("--input", required=True, help="Markdown file to review.")
    parser.add_argument("--config", default=None,
                        help="Review config JSON: frontmatter schema, thresholds, severity overrides, gate.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text).")
    parser.add_argument("--fail-on", choices=["error", "warning", "info", "never"], default=None,
                        help="Minimum severity that fails the gate; overrides the config value.")
    parser.add_argument("--only", choices=["frontmatter", "structure", "accessibility"],
                        default=None, help="Run a single check family instead of all three.")
    args = parser.parse_args()
    try:
        cfg, doc, findings = load_config(args.config), parse_document(Path(args.input)), []
        if args.only in (None, "frontmatter"):
            findings += check_frontmatter(doc, cfg)
        if args.only in (None, "structure"):
            findings += check_structure(doc, cfg)
        if args.only in (None, "accessibility"):
            findings += check_accessibility(doc, cfg)
        findings = apply_overrides(findings, cfg)
        passed, counts, reason = evaluate_gate(findings, cfg, args.fail_on)
        output(doc, findings, passed, counts, reason, args.format)
        sys.exit(0 if passed else 2)
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        print(f"error: review gate failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
