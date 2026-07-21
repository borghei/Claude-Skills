#!/usr/bin/env python3
"""
Cross-reference Auditor — audit the labelling and referencing discipline of an
authored markdown document before it is converted to HTML.

Reports unresolved references, duplicate labels, unlabelled figures and tables,
labels nobody references, forward references, and figures missing alt text.
Exits non-zero when blocking findings exist, so it drops straight into CI.

Usage:
    python3 crossref_auditor.py --input report.md
    python3 crossref_auditor.py --input report.md --format json
    python3 crossref_auditor.py --input report.md --max-severity warning
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

LABEL_RE = re.compile(r"\{#(fig|tbl|sec):([A-Za-z0-9_-]+)\}")
XREF_RE = re.compile(r"\[@(fig|tbl|sec):([A-Za-z0-9_-]+)\]")
IMAGE_LINE_RE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)\)")
TABLE_CAPTION_RE = re.compile(r"^Table:\s*(?P<caption>.+?)(\s*\{#tbl:[^}]+\})?\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
PLACEHOLDER_ALT = {"", "image", "img", "figure", "chart", "graph", "screenshot",
                   "diagram", "picture", "photo", "todo", "tbd"}


def read_lines(path: Path) -> List[str]:
    """Read a markdown file into a list of lines."""
    try:
        return path.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    except FileNotFoundError:
        raise SystemExit(f"error: input file not found: {path}")
    except UnicodeDecodeError:
        raise SystemExit(f"error: {path} is not valid UTF-8 text")


def scan(lines: List[str]) -> Dict[str, Any]:
    """Inventory every label, reference, figure, and table with line numbers."""
    labels: Dict[str, List[int]] = {}
    refs: Dict[str, List[int]] = {}
    figures: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []
    in_code = False
    for number, line in enumerate(lines, start=1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        stripped = line.strip()
        for kind, name in LABEL_RE.findall(stripped):
            labels.setdefault(f"{kind}:{name}", []).append(number)
        for kind, name in XREF_RE.findall(stripped):
            refs.setdefault(f"{kind}:{name}", []).append(number)
        image = IMAGE_LINE_RE.match(stripped)
        if image:
            label = LABEL_RE.search(stripped)
            figures.append({
                "line": number,
                "alt": image.group("alt").strip(),
                "src": image.group("src"),
                "label": f"fig:{label.group(2)}" if label else None,
            })
        caption = TABLE_CAPTION_RE.match(stripped)
        if caption:
            label = LABEL_RE.search(stripped)
            tables.append({
                "line": number,
                "caption": caption.group("caption").strip(),
                "label": f"tbl:{label.group(2)}" if label else None,
            })
    return {"labels": labels, "refs": refs, "figures": figures, "tables": tables,
            "headings": [(len(m.group(1)), m.group(2), i)
                         for i, line in enumerate(lines, start=1)
                         if (m := HEADING_RE.match(line.strip()))]}


def finding(severity: str, code: str, line: int, message: str, fix: str) -> Dict[str, Any]:
    """Build a single audit finding record."""
    return {"severity": severity, "code": code, "line": line,
            "message": message, "fix": fix}


def audit(scanned: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply every cross-reference rule and return the findings."""
    out: List[Dict[str, Any]] = []
    labels, refs = scanned["labels"], scanned["refs"]

    for key, lines in refs.items():
        if key not in labels:
            for line in lines:
                out.append(finding("error", "XREF_UNRESOLVED", line,
                                   f"[@{key}] has no matching label",
                                   f"add {{#{key}}} to the target, or fix the reference"))
    for key, lines in labels.items():
        if len(lines) > 1:
            out.append(finding("error", "LABEL_DUPLICATE", lines[1],
                               f"label {{#{key}}} is defined {len(lines)} times "
                               f"(lines {', '.join(str(n) for n in lines)})",
                               "labels must be unique; the second definition wins silently"))
        elif key not in refs:
            out.append(finding("info", "LABEL_UNREFERENCED", lines[0],
                               f"label {{#{key}}} is never referenced",
                               "remove the label, or reference it with [@" + key + "]"))
    for key, ref_lines in refs.items():
        if key in labels and min(ref_lines) < labels[key][0]:
            out.append(finding("info", "XREF_FORWARD", min(ref_lines),
                               f"[@{key}] is referenced before it is defined",
                               "expected in reports; numbering still resolves correctly"))
    for fig in scanned["figures"]:
        if fig["alt"].lower() in PLACEHOLDER_ALT:
            out.append(finding("error", "FIG_ALT_MISSING", fig["line"],
                               f"figure has empty or placeholder alt text: '{fig['alt']}'",
                               "describe what the figure shows, not that it is a figure"))
        elif len(fig["alt"]) < 15:
            out.append(finding("warning", "FIG_ALT_THIN", fig["line"],
                               f"alt text is {len(fig['alt'])} characters: '{fig['alt']}'",
                               "aim for 15-125 characters describing the finding"))
        elif len(fig["alt"]) > 125:
            out.append(finding("warning", "FIG_ALT_LONG", fig["line"],
                               f"alt text is {len(fig['alt'])} characters",
                               "keep alt under 125 chars; move detail into the caption"))
        if not fig["label"]:
            out.append(finding("warning", "FIG_UNLABELLED", fig["line"],
                               "figure has no {#fig:name} label",
                               "label it so prose can reference it instead of saying 'below'"))
    for table in scanned["tables"]:
        if not table["label"]:
            out.append(finding("warning", "TBL_UNLABELLED", table["line"],
                               "table caption has no {#tbl:name} label",
                               "label it so prose can reference the table by number"))
    for i in range(1, len(scanned["headings"])):
        prev, current = scanned["headings"][i - 1], scanned["headings"][i]
        if current[0] - prev[0] > 1:
            out.append(finding("error", "HEADING_SKIP", current[2],
                               f"heading jumps from h{prev[0]} to h{current[0]}",
                               "never skip a level; screen-reader outlines depend on it"))
    return sorted(out, key=lambda f: (f["line"], f["code"]))


def output(findings: List[Dict[str, Any]], scanned: Dict[str, Any],
           threshold: str, fmt: str) -> int:
    """Print findings and return the count at or above the gate threshold."""
    limit = SEVERITY_ORDER[threshold]
    blocking = [f for f in findings if SEVERITY_ORDER[f["severity"]] >= limit]
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    summary = {
        "figures": len(scanned["figures"]), "tables": len(scanned["tables"]),
        "labels": len(scanned["labels"]),
        "references": sum(len(v) for v in scanned["refs"].values()),
    }
    if fmt == "json":
        print(json.dumps({"gate": "fail" if blocking else "pass", "threshold": threshold,
                          "summary": summary, "counts": counts,
                          "findings": findings}, indent=2))
        return len(blocking)
    print(f"Cross-reference audit - {summary['figures']} figures, "
          f"{summary['tables']} tables, {summary['labels']} labels, "
          f"{summary['references']} references\n")
    if not findings:
        print("  no findings - labelling and references are clean")
    for sev in ("error", "warning", "info"):
        for f in [x for x in findings if x["severity"] == sev]:
            print(f"  [{sev.upper():<7}] line {f['line']:>4}  {f['code']}: {f['message']}")
            print(f"                       fix: {f['fix']}")
    print(f"\n{counts['error']} error, {counts['warning']} warning, {counts['info']} info")
    print(f"GATE ({threshold}+): {'FAIL' if blocking else 'PASS'}")
    return len(blocking)


def main() -> None:
    """Parse arguments, audit the document, and exit non-zero on blocking findings."""
    parser = argparse.ArgumentParser(
        description="Audit figure/table/section labels and cross-references in markdown.")
    parser.add_argument("--input", required=True, help="path to the markdown source file")
    parser.add_argument("--max-severity", choices=["info", "warning", "error"],
                        default="error", dest="threshold",
                        help="lowest severity that fails the gate (default: error)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--no-gate", action="store_true",
                        help="always exit 0, even when findings block (report-only mode)")
    args = parser.parse_args()

    try:
        scanned = scan(read_lines(Path(args.input)))
        blocking = output(audit(scanned), scanned, args.threshold, args.format)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: audit failed ({type(exc).__name__}: {exc})", file=sys.stderr)
        sys.exit(1)
    if blocking and not args.no_gate:
        sys.exit(2)  # 2 = gate failed (1 is reserved for tool errors)


if __name__ == "__main__":
    main()
