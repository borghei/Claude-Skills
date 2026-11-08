#!/usr/bin/env python3
"""Lint a pull request body for reviewability: sections, evidence, verification, merge risk.

Checks that the five sections a reviewer needs are present and filled in
(Summary, Why, Evidence, How to verify, Merge risk), that evidence is concrete
(screenshot, log, test output, CI link), that verification steps are runnable,
that the merge-risk section classifies the door and carries a rollback plan when
one-way, and that no credentials leaked into pasted logs. With --files (and
optionally --diff) it cross-checks the claimed classification against the
changed paths, so "two-way door" on a PR with a schema migration fails.

Usage:
  python3 pr_body_lint.py --body pr.md
  python3 pr_body_lint.py --body pr.md --files changed.txt --diff pr.diff --format json
  gh pr view 123 --json body -q .body | python3 pr_body_lint.py --body - --strict

Exit codes:
  0  no errors (and no warnings under --strict)
  1  at least one error (or warning under --strict)
  2  usage error (unreadable input)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional



def _load_classifier() -> Any:
    """Load the sibling risk_classifier.py by path so the skill folder stays self-contained."""
    path = Path(__file__).resolve().parent / "risk_classifier.py"
    spec = importlib.util.spec_from_file_location("risk_classifier", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"error: cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RC = _load_classifier()
classify_files, read_files, scan_diff, summarize = _RC.classify_files, _RC.read_files, _RC.scan_diff, _RC.summarize

SECTIONS: Dict[str, List[str]] = {
    "summary": ["summary", "what changed", "what", "overview", "changes"],
    "why": ["why", "motivation", "context", "problem", "background"],
    "evidence": ["evidence", "before/after", "before and after", "screenshots", "proof", "results", "demo"],
    "verify": ["how to verify", "verification", "how to test", "test plan", "testing", "to verify", "reviewer steps"],
    "risk": ["merge risk", "risk", "rollout", "risk and rollback", "risk & rollback", "deployment risk"],
}
PLACEHOLDER = re.compile(r"^\s*(todo|tbd|n/?a|none|-|\d+\.|\.\.\.|<[^>]*>|\[[^\]]*\]|\*\*[^*]+\*\*:?)\s*$",
                         re.IGNORECASE)
TEMPLATE_LEFTOVER = re.compile(r"<!--.*?-->|\[(fill|describe|add|exact steps)[^\]]*\]", re.IGNORECASE | re.DOTALL)
WEAK_VERIFY = re.compile(r"^\s*(tested locally|works on my machine|ci (passes|is green)|see tests|it works)\.?\s*$",
                         re.IGNORECASE)
ONE_WAY = re.compile(r"\b(one[- ]way|irreversible|not reversible|non[- ]reversible)\b", re.IGNORECASE)
TWO_WAY = re.compile(r"\b(two[- ]way|reversible|safe to revert|revert(ing)? is a full rollback)\b", re.IGNORECASE)
ROLLBACK = re.compile(r"\b(roll ?back|revert|restore|down[- ]migration|forward[- ]fix|kill switch|feature flag)\b",
                      re.IGNORECASE)
SECRETS = [
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), "GitHub token"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}\b"), "API secret key"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"), "bearer token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\b(postgres|mysql|mongodb(\+srv)?|redis)://[^\s:@/]+:[^\s@/]+@"), "database URL with password"),
]


def split_sections(body: str) -> Dict[str, str]:
    """Map each recognised section key to its text. Headings inside code fences are ignored."""
    chunks: List[List[str]] = [["", ""]]
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        heading = None if in_fence else re.match(r"^#{1,4}\s+(.+?)\s*#*\s*$", line)
        if heading:
            chunks.append([heading.group(1), ""])
        else:
            chunks[-1][1] += line + "\n"
    found: Dict[str, str] = {}
    for title, text in chunks[1:]:
        title = re.sub(r"[^\w/&\s-]", "", title.lower()).strip()
        for key, aliases in SECTIONS.items():
            if key not in found and any(title == a or title.startswith(a + " ") for a in aliases):
                found[key] = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()
                break
    return found


def is_empty(text: str) -> bool:
    """True when a section has no real content after removing comments and placeholders."""
    cleaned = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()
    lines = [ln for ln in cleaned.splitlines() if ln.strip()]
    return not lines or all(PLACEHOLDER.match(ln) for ln in lines)


def add(findings: List[Dict[str, str]], severity: str, section: str, message: str) -> None:
    """Append one finding."""
    findings.append({"severity": severity, "section": section, "message": message})


def lint(body: str, files: Optional[List[str]], diff_text: Optional[str]) -> Dict[str, Any]:
    """Run every check and return findings plus the parsed classification."""
    findings: List[Dict[str, str]] = []
    sections = split_sections(body)
    for key in SECTIONS:
        if key not in sections:
            add(findings, "error", key, f"missing section (accepted headings: {', '.join(SECTIONS[key][:3])})")
        elif is_empty(sections[key]):
            add(findings, "error", key, "section is empty or only a placeholder")

    summary = sections.get("summary", "")
    words = len(re.sub(r"```.*?```", "", summary, flags=re.DOTALL).split())
    if words > 150:
        add(findings, "warn", "summary", f"summary is {words} words; reviewers read the first 3 lines, keep prose under 150")
    why = sections.get("why", "")
    if why and re.fullmatch(r"\s*((closes|fixes|resolves|refs?)\s+)?\S+\s*", why, re.IGNORECASE):
        add(findings, "warn", "why", "why is only a ticket reference; state the problem in one or two sentences")

    evidence = sections.get("evidence", "")
    if evidence and not is_empty(evidence):
        concrete = re.search(r"!\[|<img|```|^(?: {4}|\t)\S|https?://\S*(actions/runs|buildkite|circleci|jenkins|grafana|loom|\.png|\.gif|\.mp4)",
                             evidence, re.IGNORECASE | re.MULTILINE)
        if not concrete:
            add(findings, "error", "evidence", "no concrete evidence: add a screenshot, log/test output block, or CI/run link")
        if not (re.search(r"\bbefore\b", evidence, re.I) and re.search(r"\bafter\b", evidence, re.I)):
            add(findings, "warn", "evidence", "no before/after pair; show the old behaviour next to the new one")

    verify = sections.get("verify", "")
    if verify and not is_empty(verify):
        if WEAK_VERIFY.match(verify):
            add(findings, "error", "verify", "verification is a claim, not steps a reviewer can repeat")
        elif not re.search(r"^\s*(\d+\.|[-*]\s|\- \[ \])|```", verify, re.MULTILINE):
            add(findings, "warn", "verify", "write verification as numbered steps or a command block")

    risk = sections.get("risk", "")
    claimed: Optional[str] = None
    if risk and not is_empty(risk):
        if ONE_WAY.search(risk):
            claimed = "one-way"
        elif TWO_WAY.search(risk):
            claimed = "two-way"
        if not claimed:
            add(findings, "error", "risk", "no door classification: say one-way (irreversible) or two-way (reversible)")
        if claimed == "one-way" and not ROLLBACK.search(risk):
            add(findings, "error", "risk", "one-way change with no rollback or forward-fix plan")
        if claimed == "one-way" and ROLLBACK.search(risk) and len(risk.split()) < 25:
            add(findings, "warn", "risk", "rollback plan is under 25 words; name the steps, the owner and the time it takes")
        if not re.search(r"blast radius|affects|impact|who sees", risk, re.IGNORECASE):
            add(findings, "warn", "risk", "no blast radius: say who or what is affected if this goes wrong")

    classified: Optional[Dict[str, Any]] = None
    if files:
        classified = summarize(classify_files(files), scan_diff(diff_text) if diff_text else [])
        reasons = [f"{f['path']} ({', '.join(f['categories'])})" for f in classified["files"] if f["door"] == "one-way"]
        reasons += [f"{h['file']}: {h['signal']}" for h in classified["diff_signals"]]
        if classified["door"] == "one-way" and claimed == "two-way":
            add(findings, "error", "risk", "claims two-way/reversible but the change is one-way: " + "; ".join(reasons[:4]))
        elif classified["door"] == "conditional" and claimed == "two-way":
            missing = [c for c in classified["categories"] if c not in ("application-code", "tests-docs")
                       and c.split("-")[0] not in risk.lower()]
            if missing:
                add(findings, "warn", "risk", f"reversible claim does not address: {', '.join(missing)}")

    for rx, label in SECRETS:
        if rx.search(body):
            add(findings, "error", "body", f"possible {label} in the PR body; redact it and rotate the credential")
    if TEMPLATE_LEFTOVER.search(body):
        add(findings, "warn", "body", "template comments or [fill-in] markers left in the body")
    total = len(body.split())
    if total > 900:
        add(findings, "warn", "body", f"body is {total} words; move detail into linked docs or commit messages")

    errors = sum(f["severity"] == "error" for f in findings)
    warns = sum(f["severity"] == "warn" for f in findings)
    return {"sections_found": sorted(sections), "claimed_door": claimed,
            "computed_door": classified["door"] if classified else None,
            "blast_radius": classified["blast_radius"] if classified else None,
            "errors": errors, "warnings": warns, "score": max(0, 100 - 15 * errors - 5 * warns),
            "findings": findings}


def render_text(report: Dict[str, Any], strict: bool) -> str:
    """Human-readable report."""
    lines = [f"PR body lint: score {report['score']}/100  "
             f"({report['errors']} errors, {report['warnings']} warnings)",
             f"  sections: {', '.join(report['sections_found']) or 'none recognised'}",
             f"  door claimed: {report['claimed_door'] or '-'}   door from files: {report['computed_door'] or 'not checked'}"]
    if report["blast_radius"]:
        lines.append(f"  blast radius from files: {report['blast_radius']}")
    lines.append("")
    for f in sorted(report["findings"], key=lambda x: x["severity"] != "error"):
        lines.append(f"  {f['severity'].upper():5}  [{f['section']}] {f['message']}")
    failed = report["errors"] or (strict and report["warnings"])
    lines.append("")
    lines.append("RESULT: FAIL" if failed else "RESULT: PASS")
    return "\n".join(lines)


def main() -> None:
    """Entry point."""
    p = argparse.ArgumentParser(description="Lint a pull request body for reviewability and merge-risk honesty.")
    p.add_argument("--body", required=True, help="PR body markdown file, or '-' for stdin")
    p.add_argument("--files", help="changed paths (.txt, .json, or '-') to cross-check the risk classification")
    p.add_argument("--diff", help="unified diff to scan for destructive statements (needs --files)")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = p.parse_args()
    if args.body == "-" and args.files == "-":
        print("error: only one of --body/--files can read stdin", file=sys.stderr)
        sys.exit(2)
    try:
        body = sys.stdin.read() if args.body == "-" else Path(args.body).read_text(encoding="utf-8")
        diff_text = Path(args.diff).read_text(encoding="utf-8", errors="replace") if args.diff else None
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    files = read_files(args.files) if args.files else None
    report = lint(body, files, diff_text)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(render_text(report, args.strict))
    sys.exit(1 if report["errors"] or (args.strict and report["warnings"]) else 0)


if __name__ == "__main__":
    main()
