#!/usr/bin/env python3
"""Static detector for generic and low-quality interface patterns.

Scans HTML, JSX/TSX, Vue, Svelte, Astro and CSS/SCSS/LESS files and reports
each hit with file:line, rule id, severity, evidence, the fix, and the
refinement command that owns it. Runs the declaration rules (css_checks.py),
the utility-class rules (class_checks.py) and the structural rules
(markup_checks.py), then the project-level rules (animation with no
reduced-motion path anywhere in the scan).

Inline waivers need a reason and cover the marker's own line and the next:
  /* ui-refine-ignore side-stripe-border -- severity rule on a square callout */
  <!-- ui-refine-ignore-file * -- deliberate before/after demo -->

Usage:
  python3 ui_slop_detector.py src/ --format text
  python3 ui_slop_detector.py page.html styles.css --fail-on high --format json
  python3 ui_slop_detector.py src/ --scope color,type --skip default-font-stack
  python3 ui_slop_detector.py src/ --context interface-context.md --fail-on advisory

Exit codes: 0 nothing at or above --fail-on, 1 findings at or above it,
2 bad input (missing path, nothing scannable, unreadable file, bad catalog).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _load(name: str):
    """Load a sibling module from this scripts/ folder (keeps the package self-contained)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


C = _load("css_checks")
M = _load("markup_checks")
R = _load("ui_rules")
X = _load("extra_checks")
S = _load("system_checks")
if X.check_block not in C.EXTRA:
    C.EXTRA.append(X.check_block)


MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
STYLE_EXT = {".css", ".scss", ".less"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "vendor", ".next", ".nuxt", "coverage", "out"}
PAGE_RULE = re.compile(r"(?<![\w.#-])(?:html|body|:root)(?![\w-])[^{}<>]{0,200}\{([^{}]*)\}")
PAGE_TAG = re.compile(r"<(?:html|body)\b[^>]*?\bclass(?:Name)?=[\"']([^\"']*)[\"']", re.I)
IGNORE_RE = re.compile(r"ui-refine-ignore(-file)?\s+([\w*,-]+)(?:\s*(?:--|:)\s*(\S.*?))?\s*(?:\*/|-->|\}|$)")


class InputError(Exception):
    """Raised for anything the caller must fix before a scan can run."""


def collect(paths: List[str], max_files: int) -> List[Path]:
    files: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if not p.exists():
            raise InputError(f"path not found: {raw}")
        candidates = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
        for f in candidates:
            if any(part in SKIP_DIRS for part in f.parts) or f.name.endswith(".min.css"):
                continue
            if f.suffix.lower() in MARKUP_EXT | STYLE_EXT:
                files.append(f)
    if not files:
        raise InputError("no scannable files (html, jsx, tsx, vue, svelte, astro, css, scss, less)")
    if len(files) > max_files:
        raise InputError(f"{len(files)} files exceeds --max-files {max_files}; narrow the target")
    return files


def waivers(text: str, path: str) -> Tuple[Dict[int, set], set, List[dict]]:
    """Inline waivers: line -> rule ids, file-wide ids, and markers rejected for having no reason."""
    by_line: Dict[int, set] = {}
    whole: set = set()
    rejected: List[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        for m in IGNORE_RE.finditer(line):
            ids = {x for x in m.group(2).split(",") if x}
            if not (m.group(3) or "").strip():
                rejected.append({"file": path, "line": number, "marker": m.group(0).strip()[:80],
                                 "reason": "waiver has no reason after '--'"})
                continue
            if m.group(1):
                whole |= ids
            else:
                by_line.setdefault(number, set()).update(ids)
                by_line.setdefault(number + 1, set()).update(ids)
    return by_line, whole, rejected


def page_ground(texts: List[str]) -> Optional[str]:
    """The page ground set in the scan (body/html rule, @apply, or <html>/<body> classes), so a component
    scanned with its global stylesheet or layout is judged on the right ground. None when grounds disagree."""
    found = set()
    for text in texts:
        for m in PAGE_RULE.finditer(text):
            applied = re.search(r"@apply\s+([^;}]+)", m.group(1))
            value = re.search(r"background(?:-color)?\s*:\s*([^;}]+)", m.group(1))
            colors = R.find_colors(value.group(1)) if value and "gradient(" not in value.group(1) else []
            found.add(M.K.ground(applied.group(1).split()) if applied else
                      ("dark" if R.luminance(colors[0]) < 0.2 else "light") if colors else None)
        for m in PAGE_TAG.finditer(text):
            dark = re.search(r"(?<![\w:-])dark(?![\w-])", m.group(1))
            found.add("dark" if dark else M.K.ground(m.group(1).split()))
    found.discard(None)
    return found.pop() if len(found) == 1 else None


def waived(f: dict, by_line: Dict[int, set], whole: set) -> bool:
    ids = by_line.get(f["line"], set()) | whole
    return "*" in ids or f["rule"] in ids


def scan(files: List[Path], cat: dict, system: Optional[dict] = None) -> dict:
    texts: Dict[Path, str] = {}
    unreadable: List[str] = []
    for f in files:
        try:
            texts[f] = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            unreadable.append(f"{f}: {exc.__class__.__name__}")
    if not texts:
        raise InputError("no file could be read as UTF-8: " + "; ".join(unreadable))
    joined = "\n".join(texts.values())
    focus_visible = ":focus-visible" in joined or "focus-visible:" in joined
    ground = page_ground(list(texts.values()))
    findings: List[dict] = []
    ignored, rejected = 0, []
    animated, reduced, anywhere = None, False, set()
    shared: Dict[str, tuple] = {}
    for f, text in texts.items():
        path = str(f)
        ctx = C.new_context(text)
        ctx["focus_visible"] = focus_visible
        ctx["shared"] = shared
        ctx["page_ground"] = ground
        if f.suffix.lower() in STYLE_EXT:
            found, ctx = C.scan_text(text, path, cat, ctx=ctx)
        else:
            found = M.scan_markup(text, path, cat, ctx) + X.scan_markup(text, path, cat)
        if system:
            found += S.drift_file(text, path, system, cat)
        found += R.file_level(ctx, path, cat)
        animated = animated or ctx["animated"]
        reduced = reduced or ctx["reduced_motion"]
        by_line, whole, bad = waivers(text, path)
        rejected += bad
        anywhere |= whole
        for x in found:
            if waived(x, by_line, whole):
                ignored += 1
            else:
                findings.append(x)
    if animated and not reduced:
        if "missing-reduced-motion" in anywhere:
            ignored += 1
        else:
            findings.append(R.make_finding(cat, "missing-reduced-motion", animated[0], animated[1],
                                           "animation found; no prefers-reduced-motion or motion-reduce anywhere in scan"))
    for x in X.project_level(shared, cat):
        if "flat-type-hierarchy" in anywhere:
            ignored += 1
        else:
            findings.append(x)
    if system:
        findings = S.honour(findings, system)
        S.escalate(findings, system["refusals"])
    findings.sort(key=lambda x: (x["file"], x["line"], -R.SEVERITY_RANK[x["severity"]]))
    return {"files_scanned": len(texts), "findings": findings, "ignored": ignored, "rejected_waivers": rejected,
            "unreadable": unreadable}


def summarise(report: dict, fail_on: str) -> dict:
    sev = Counter(f["severity"] for f in report["findings"])
    cmd = Counter(f["command"] for f in report["findings"])
    floor = R.SEVERITY_RANK[fail_on]
    blocking = sum(1 for f in report["findings"] if R.SEVERITY_RANK[f["severity"]] >= floor)
    return {"files_scanned": report["files_scanned"], "findings": len(report["findings"]),
            "by_severity": {k: sev.get(k, 0) for k in ("high", "medium", "advisory")},
            "by_command": dict(cmd.most_common()), "fail_on": fail_on, "blocking": blocking,
            "ignored": report["ignored"], "rejected_waivers": len(report["rejected_waivers"]),
            "verdict": "FAIL" if blocking else "PASS"}


def render_text(report: dict, summary: dict) -> str:
    out: List[str] = []
    current = None
    for f in report["findings"]:
        if f["file"] != current:
            current = f["file"]
            out.append(f"\n{current}")
        out.append(f"  {f['line']:>5}  {f['severity']:<8} {f['rule']:<24} {f['evidence']}")
        out.append(f"         fix: {f['fix']}  [run: {f['command']}]")
    for u in report["unreadable"]:
        out.append(f"\n  skipped unreadable file {u}")
    for r in report["rejected_waivers"]:
        out.append(f"\n  waiver rejected {r['file']}:{r['line']}  {r['reason']}")
    s = summary
    out.append(f"\n{s['verdict']}  {s['findings']} finding(s) in {s['files_scanned']} file(s): "
               f"{s['by_severity']['high']} high, {s['by_severity']['medium']} medium, "
               f"{s['by_severity']['advisory']} advisory; {s['blocking']} at or above '{s['fail_on']}'; "
               f"{s['ignored']} waived")
    if s["by_command"]:
        out.append("Commands by finding count: " + ", ".join(f"{k} {v}" for k, v in s["by_command"].items()))
    return "\n".join(out).lstrip("\n")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Detect generic and low-quality interface patterns in markup and styles.")
    p.add_argument("paths", nargs="+", help="Files or directories to scan")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    p.add_argument("--fail-on", choices=("high", "medium", "advisory"), default="medium",
                   help="Lowest severity that makes the run exit 1 (default medium)")
    p.add_argument("--rules", help="Comma-separated rule ids to keep (default all)")
    p.add_argument("--skip", help="Comma-separated rule ids to drop")
    p.add_argument("--scope", help="Comma-separated scopes to keep: color,type,layout,motion,surface,structure,copy,interaction")
    p.add_argument("--context", help="interface-context.md: report values outside its visual system "
                   "(off-system-* rules) and fail on any rule it lists under Refusals")
    p.add_argument("--max-files", type=int, default=2000, help="Refuse scans larger than this (default 2000)")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cat = R.load_catalog()
        for flag in (args.rules, args.skip):
            unknown = [x for x in (flag or "").split(",") if x and x not in cat]
            if unknown:
                raise InputError(f"unknown rule id(s): {', '.join(unknown)}")
        scopes = {x for x in (args.scope or "").split(",") if x}
        if scopes - {r["scope"] for r in cat.values()}:
            raise InputError(f"unknown scope(s): {', '.join(sorted(scopes - {r['scope'] for r in cat.values()}))}")
        system = S.load_context(args.context) if args.context else None
        report = scan(collect(args.paths, args.max_files), cat, system)
    except (InputError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    keep = set((args.rules or "").split(",")) - {""}
    drop = set((args.skip or "").split(",")) - {""}
    report["findings"] = [f for f in report["findings"] if (not keep or f["rule"] in keep)
                          and f["rule"] not in drop and (not scopes or f["scope"] in scopes)]
    summary = summarise(report, args.fail_on)
    if args.format == "json":
        print(json.dumps({"summary": summary, **report}, indent=2))
    else:
        print(render_text(report, summary))
    return 1 if summary["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main())
