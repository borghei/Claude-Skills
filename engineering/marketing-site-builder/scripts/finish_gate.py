#!/usr/bin/env python3
"""Run every static check on a page, apply written waivers, count fix rounds,
and end on one verdict line.

The six checkers in this folder each report on their own. This gate runs them
all in-process (copy_lint, copy_devices, consistency_check, page_gate,
access_links_check, style_rules), applies a waiver file in which each waiver
names one finding and gives its reason, and, with --state, counts a round each
time the page or the waivers change. Its last line is one of:

  GATE: PASS
  GATE: FAIL <n> (round <k> of <max>)
  GATE: OPEN <n> (rounds used up)        stop fixing; report what is open
  GATE: DONE (<the user's words>)       the user ended the build

Usage:
  python3 finish_gate.py index.html --kind place
  python3 finish_gate.py index.html --waivers site-waivers.json --state .site-gate.json
  python3 finish_gate.py index.html --state .site-gate.json --done "client said ship it as it is"

Waiver file: a JSON list of {"check": "<finding id>", "target": "<text from the finding>",
"reason": "<12+ characters>"}. A waiver that matches more than one finding is ignored.
More than five waivers is itself a FAIL. checker-gaming cannot be waived.

Exit codes: 0 PASS or DONE, 1 FAIL or OPEN, 2 bad input.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
UNWAIVABLE = {"checker-gaming", "too-many-waivers"}
MAX_WAIVERS = 5


def _sibling(name: str):
    """Load a sibling script as a module without a package import."""
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CL, CD, CC, PG, AL, SR = (_sibling(n) for n in ("copy_lint", "copy_devices", "consistency_check",
                                                 "page_gate", "access_links_check", "style_rules"))
ERRORS = (CL.InputError, CC.InputError, AL.InputError, ValueError, OSError, KeyError, TypeError, re.error)


def norm(script: str, f: Dict) -> Dict:
    """One finding shape for every checker."""
    where = f.get("where") or (f"L{f['line']}" if f.get("line") else "page")
    text = f.get("match") or ""
    return {"script": script, "severity": f["severity"], "id": f["id"], "where": where,
            "text": text, "message": f.get("message", ""), "key": f"{script} {f['id']} {where} {text} {f.get('message', '')}"}


def run_all(page: Path, a: argparse.Namespace, budget: Dict) -> tuple:
    """Run each checker; return its normalised findings and the CSS text read (for the round signature)."""
    segs, lex, is_html = CL.load(page, Path(a.lexicon))
    res = {"copy_lint": [norm("copy_lint", f) for f in CL.lint(segs, lex, is_html, a.allow, a.year)],
           "copy_devices": [norm("copy_devices", f) for f in CD.analyse(page, Path(a.lexicon))["findings"]]}
    if not is_html:
        return res, []
    try:
        sources, buttons = CC.gather(page, a.css)
    except CC.InputError as exc:  # a page with no readable CSS still gets every other check
        if "no CSS found" not in str(exc):
            raise
        sources = None
    res["page_gate"] = [norm("page_gate", f) for f in PG.gate(page, a.kind, budget["page"])["findings"]]
    res["access_links_check"] = [norm("access_links_check", f) for f in AL.check(page)["findings"]]
    if sources is None:
        res["consistency_check"] = [norm("consistency_check", {"severity": "FAIL", "id": "no-css", "where": "css", "message":
                                    "no stylesheet read (remote or not built yet): pass the built CSS with --css"})]
        return res, []
    cons = CC.analyse(sources, buttons, budget["system"])
    res["consistency_check"] = [norm("consistency_check", {"severity": "FAIL", "id": cat, "where": "css",
                                                           "message": f"{r['distinct']} distinct, budget {r['budget']}"})
                                for cat, r in cons["categories"].items() if r["over"]] + \
                               [norm("consistency_check", {"severity": "WARN", "id": w["id"], "where": w["where"],
                                                           "match": w["value"], "message": w["message"]}) for w in cons["warnings"]]
    res["style_rules"] = [norm("style_rules", f) for f in SR.check(page, a.css)["findings"]]
    return res, [src for src, _, _ in sources]


def load_waivers(path: Optional[Path]) -> tuple:
    """Return (valid waivers, notes about ignored ones); raise ValueError on a malformed file."""
    if path is None or not path.is_file():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"waiver file is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("waiver file must be a JSON list of {check, target, reason}")
    valid, notes = [], []
    for i, w in enumerate(data):
        if not isinstance(w, dict) or not all(isinstance(w.get(k), str) for k in ("check", "target", "reason")):
            notes.append(f"waiver {i + 1} ignored: needs check, target and reason as text")
        elif len(w["reason"].strip()) < 12:
            notes.append(f"waiver {i + 1} ({w['check']}) ignored: the reason is under 12 characters")
        elif len(w["target"].strip()) < 3:
            notes.append(f"waiver {i + 1} ({w['check']}) ignored: the target is under 3 characters")
        else:
            valid.append(w)
    return valid, notes


def apply_waivers(findings: List[Dict], waivers: List[Dict], notes: List[str]) -> None:
    """Mark the one FAIL each waiver names as WAIVED; note waivers that match none or several."""
    for w in waivers:
        hits = [f for f in findings if f["severity"] == "FAIL" and f["id"] == w["check"] and w["target"].lower() in f["key"].lower()]
        if len(hits) == 1 and hits[0]["id"] not in UNWAIVABLE:
            hits[0]["severity"], hits[0]["reason"] = "WAIVED", w["reason"]
        elif len(hits) > 1:
            notes.append(f"waiver for {w['check']} '{w['target']}' matches {len(hits)} findings: name one")
        elif hits:
            notes.append(f"{w['check']} cannot be waived")
        else:
            notes.append(f"waiver for {w['check']} '{w['target']}' matches no FAIL")


def signature(files: List[Path], css: List[str]) -> str:
    """Hash of the page, waivers, budget, lexicon and every stylesheet read, so an unchanged rerun is not a round."""
    h = hashlib.sha256()
    for p in files:
        h.update(p.read_bytes() if p.is_file() else b"-")
    for text in css:
        h.update(text.encode("utf-8", "replace"))
    return h.hexdigest()


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Run every static check, apply waivers, count rounds, print one GATE line.")
    ap.add_argument("path", help="HTML page (a .md/.txt draft runs the two copy checks only)")
    ap.add_argument("--kind", choices=PG.KINDS, help="business kind (default: <html data-kind>)")
    ap.add_argument("--css", action="append", default=[], help="extra built stylesheet (repeatable)")
    ap.add_argument("--budget", default=str(PG.DEFAULT_BUDGET), help="budget JSON (default: assets/site_budget.json)")
    ap.add_argument("--lexicon", default=str(CL.DEFAULT_LEXICON), help="copy lexicon JSON (default: assets/copy_tells.json)")
    ap.add_argument("--allow", action="append", default=[], help="a word literal for the trade (repeatable)")
    ap.add_argument("--year", type=int, default=dt.date.today().year, help="current year for the copyright check")
    ap.add_argument("--waivers", help="waiver JSON (default: site-waivers.json beside the page, if present)")
    ap.add_argument("--state", help="round counter JSON; without it rounds are not tracked")
    ap.add_argument("--max-rounds", type=int, default=3, help="fix rounds before the gate reports OPEN (default 3)")
    ap.add_argument("--done", help="the user's own words ending the build (12+ characters); needs --state")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    page = Path(args.path)
    wpath = Path(args.waivers) if args.waivers else page.parent / "site-waivers.json"
    try:
        if args.done is not None and (len(args.done.strip()) < 12 or not args.state):
            raise ValueError("--done takes the user's words (12+ characters) and needs --state")
        if args.max_rounds < 1:
            raise ValueError("--max-rounds must be 1 or more")
        budget = CC.validate_budget(json.loads(CC.read(Path(args.budget))))
        waivers, notes = load_waivers(wpath)
        results, css_read = run_all(page, args, budget)
        state_path = Path(args.state) if args.state else None
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path and state_path.is_file() else {}
        if not isinstance(state, dict) or not isinstance(state.get("rounds", 0), int):
            raise ValueError(f"state file is not a gate state object (delete it to start over): {state_path}")
        if state.get("page") not in (None, str(page)):  # a state file left by another page starts fresh
            state = {}
    except json.JSONDecodeError as exc:
        print(f"error: bad JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    except ERRORS as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    findings = [f for fs in results.values() for f in fs]
    apply_waivers(findings, waivers, notes)
    if len(waivers) > MAX_WAIVERS:
        findings.append(norm("finish_gate", {"severity": "FAIL", "id": "too-many-waivers", "where": str(wpath),
                                             "message": f"{len(waivers)} waivers: fix instead; more than {MAX_WAIVERS} means the page or the budget is wrong"}))
    fails = [f for f in findings if f["severity"] == "FAIL"]
    waived = [f for f in findings if f["severity"] == "WAIVED"]
    sig = signature([page, wpath, Path(args.budget), Path(args.lexicon)], css_read)
    rounds = int(state.get("rounds", 0))
    if state_path and state.get("sig") != sig and state.get("status") not in ("done",):
        rounds += 1
    if args.done:
        state.update(status="done", done=args.done.strip())
    if state.get("status") == "done":
        verdict, code = f"GATE: DONE ({state.get('done', '')}) with {len(fails)} FAIL open", 0
    elif not fails:
        verdict, code = "GATE: PASS", 0
        state["status"] = "passed"
    elif state_path and rounds >= args.max_rounds:
        verdict, code = f"GATE: OPEN {len(fails)} (rounds used up)", 1
        state["status"] = "open"
    else:
        where = f"round {max(rounds, 1)} of {args.max_rounds}" if state_path else "rounds not tracked; pass --state"
        verdict, code = f"GATE: FAIL {len(fails)} ({where})", 1
        state["status"] = "fixing"
    if state_path:
        state.update(rounds=rounds, sig=sig, page=str(page), max_rounds=args.max_rounds)
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps({"page": str(page), "verdict": verdict, "rounds": rounds, "fail": len(fails),
                          "waived": waived, "notes": notes, "findings": findings}, indent=2))
    else:
        print(f"finish_gate: {page}")
        for script, fs in results.items():
            nf = sum(f["severity"] == "FAIL" for f in fs)
            print(f"  {script:<19} {nf} FAIL, {sum(f['severity'] == 'WARN' for f in fs)} WARN, "
                  f"{sum(f['severity'] == 'WAIVED' for f in fs)} waived")
        for f in fails[:40]:
            print(f"  FAIL   {f['script']:<19} {f['id']:<17} {f['where']:<16} {f['text'] or f['message']}")
        if len(fails) > 40:
            print(f"  ... {len(fails) - 40} more FAIL; run the single checkers for the full list")
        for f in waived:
            print(f"  WAIVED {f['script']:<19} {f['id']:<17} {f['where']:<16} reason: {f['reason']}")
        for n in notes:
            print(f"  NOTE   {n}")
        print(verdict)
    sys.exit(code)


if __name__ == "__main__":
    main()
