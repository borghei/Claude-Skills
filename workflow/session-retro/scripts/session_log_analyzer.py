#!/usr/bin/env python3
"""Analyze a coding-agent session transcript (JSONL) for wasted or failed tool calls.

Reads a Claude Code session log (one JSON event per line, tool_use / tool_result
blocks) or a normalized log (one {"tool", "input", "is_error", "output"} object per
line) and reports retries, redundant re-reads, failed commands, empty searches,
permission friction, oversized outputs, slow orientation and expected skills that
never ran. Each finding maps to a retro category so it can become an action item.

Usage:
  python3 session_log_analyzer.py --input session.jsonl
  python3 session_log_analyzer.py --input session.jsonl --expected-skills tdd,code-reviewer --format json

Exit codes: 0 = no finding at or above --fail-on, 1 = at least one such finding,
2 = input could not be read or parsed. Standard library only; no network, no LLM.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}
READ_TOOLS = {"Read", "read_file", "view", "cat"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "write_file", "apply_patch"}
SEARCH_TOOLS = {"Grep", "Glob", "grep", "glob", "search", "find"}
SHELL_TOOLS = {"Bash", "shell", "run_shell_command", "exec_command"}
PERMISSION_RE = re.compile(r"permission|not allowed|denied|requires approval|user rejected|"
                           r"doesn't want to proceed|blocked by (?:policy|hook)", re.IGNORECASE)
EMPTY_SEARCH_RE = re.compile(r"^\s*(no (files|matches) found|0 matches|no results)", re.IGNORECASE)
EXIT_CODE_RE = re.compile(r"exit code[:\s]+(\d+)", re.IGNORECASE)
SHELL_READ_RE = re.compile(r"^\s*(?:cat|head|tail|less|sed -n \S+)\s+(?:-\S+\s+)*['\"]?([^\s|;'\"]+)")


def _text(content: Any) -> str:
    """Flatten a tool_result content field (string or list of blocks) to text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(_text(c.get("text", c.get("content", ""))) if isinstance(c, dict) else str(c)
                         for c in content)
    return "" if content is None else str(content)


def load_calls(path: Path) -> List[Dict[str, Any]]:
    """Return tool calls in order, each with tool, input, is_error and output."""
    calls: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {lineno}: not valid JSON ({exc.msg})") from exc
            if "tool" in event:  # normalized format
                calls.append({"tool": str(event["tool"]), "input": event.get("input") or {},
                              "is_error": bool(event.get("is_error")), "output": _text(event.get("output"))})
                continue
            message = event.get("message") or {}
            blocks = message.get("content") if isinstance(message.get("content"), list) else []
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    call = {"tool": str(block.get("name", "?")), "input": block.get("input") or {},
                            "is_error": False, "output": ""}
                    by_id[str(block.get("id"))] = call
                    calls.append(call)
                elif block.get("type") == "tool_result":
                    call = by_id.get(str(block.get("tool_use_id")))
                    if call is not None:
                        call["output"] = _text(block.get("content"))
                        call["is_error"] = bool(block.get("is_error"))
    for index, call in enumerate(calls, 1):
        call["n"] = index
        match = EXIT_CODE_RE.search(call["output"])
        if call["tool"] in SHELL_TOOLS and match and match.group(1) != "0":
            call["is_error"] = True
    return calls


def target_path(call: Dict[str, Any]) -> Optional[str]:
    """Return the file a read-like call touches, if any."""
    data = call["input"] if isinstance(call["input"], dict) else {}
    if call["tool"] in READ_TOOLS | WRITE_TOOLS:
        return data.get("file_path") or data.get("path") or data.get("notebook_path")
    if call["tool"] in SHELL_TOOLS:
        match = SHELL_READ_RE.match(str(data.get("command", "")))
        return match.group(1) if match else None
    return None


def signature(call: Dict[str, Any]) -> str:
    """Stable key for 'the same call again'."""
    return call["tool"] + ":" + json.dumps(call["input"], sort_keys=True, default=str)


def finding(category: str, severity: str, title: str, evidence: List[int], fix: str) -> Dict[str, Any]:
    """Build one finding record."""
    return {"category": category, "severity": severity, "title": title,
            "evidence_calls": evidence[:12], "suggested_fix": fix}


def analyze(calls: List[Dict[str, Any]], args: argparse.Namespace) -> Dict[str, Any]:
    """Run every detector over the ordered call list and return the report."""
    out: List[Dict[str, Any]] = []
    tools = Counter(c["tool"] for c in calls)
    failed = [c for c in calls if c["is_error"]]

    last_failed: Dict[str, int] = {}
    retries: List[int] = []
    for c in calls:
        if c["tool"] in WRITE_TOOLS:  # an edit in between makes a re-run legitimate
            last_failed.clear()
        key = signature(c)
        if key in last_failed:
            retries.append(c["n"])
        if c["is_error"]:
            last_failed[key] = c["n"]
        else:
            last_failed.pop(key, None)
    if retries:
        sev = "high" if len(retries) >= 3 else "medium"
        out.append(finding("tool-economy", sev, f"{len(retries)} identical retries after a failure", retries,
                           "Fix the cause the retry ignored: add a check, a usage note, or a wrapper script."))

    reads: Dict[str, List[int]] = defaultdict(list)
    redundant: Dict[str, List[int]] = defaultdict(list)
    for c in calls:
        path = target_path(c)
        if not path:
            continue
        if c["tool"] in WRITE_TOOLS:
            reads.pop(path, None)
            continue
        if reads.get(path):
            redundant[path].append(c["n"])
        reads[path].append(c["n"])
    if redundant:
        evidence = sorted(n for ns in redundant.values() for n in ns)
        worst = max(redundant, key=lambda p: len(redundant[p]))
        sev = "high" if len(evidence) >= 5 else "medium" if len(evidence) >= 2 else "low"
        out.append(finding("navigation", sev, f"{len(evidence)} re-reads of unchanged files (worst: {worst})",
                           evidence, "Add a navigation pointer or summary so the file is read once."))

    shell_failed = [c["n"] for c in failed if c["tool"] in SHELL_TOOLS and not PERMISSION_RE.search(c["output"])]
    if shell_failed:
        sev = "high" if len(shell_failed) >= 4 else "medium"
        out.append(finding("missing-check", sev, f"{len(shell_failed)} failed shell commands", shell_failed,
                           "Document the right command in the steering file or wrap it in a script with --help."))

    denied = [c["n"] for c in calls if c["is_error"] and PERMISSION_RE.search(c["output"])]
    if denied:
        sev = "high" if len(denied) >= 3 else "medium"
        out.append(finding("permission-friction", sev, f"{len(denied)} calls blocked by permissions", denied,
                           "Allowlist the safe read-only commands, or state the approved alternative."))

    empty, streak, worst_streak = [], 0, 0
    for c in calls:
        if c["tool"] in SEARCH_TOOLS:
            if EMPTY_SEARCH_RE.search(c["output"]) or (not c["output"].strip() and not c["is_error"]):
                empty.append(c["n"])
                streak += 1
                worst_streak = max(worst_streak, streak)
                continue
            streak = 0
    if len(empty) >= 2:
        sev = "high" if worst_streak >= 3 else "medium"
        out.append(finding("navigation", sev, f"{len(empty)} empty searches (longest run {worst_streak})", empty,
                           "Add a 'where things live' pointer to CLAUDE.md/AGENTS.md for the searched area."))

    big = [c["n"] for c in calls if len(c["output"]) > args.large_output]
    if big:
        out.append(finding("tool-economy", "medium" if len(big) >= 2 else "low",
                           f"{len(big)} outputs over {args.large_output} chars", big,
                           "Narrow the command (limit, filter, --format json) or add a summary flag to the tool."))

    first_write = next((c["n"] for c in calls if c["tool"] in WRITE_TOOLS), None)
    if first_write and first_write - 1 > args.orientation_budget:
        out.append(finding("navigation", "medium", f"{first_write - 1} calls before the first edit",
                           list(range(1, min(first_write, 13))),
                           "Add the entry points for this kind of change to the steering file."))

    ran_skills = {str((c["input"] or {}).get("skill", "")) for c in calls if c["tool"] == "Skill"}
    expected = [s.strip() for s in (args.expected_skills or "").split(",") if s.strip()]
    missed = [s for s in expected if s not in ran_skills]
    if missed:
        out.append(finding("skill-miss", "medium", f"expected skills never invoked: {', '.join(missed)}", [],
                           "Sharpen each missed skill's description triggers or add a pointer in the steering file."))

    out.sort(key=lambda f: (-SEVERITY_RANK[f["severity"]], -len(f["evidence_calls"])))
    return {"calls": len(calls), "failed": len(failed), "tools": dict(tools.most_common()),
            "skills_invoked": sorted(s for s in ran_skills if s), "findings": out}


def render_text(report: Dict[str, Any]) -> str:
    """Human-readable report."""
    lines = [f"Session: {report['calls']} tool calls, {report['failed']} failed",
             "Tools: " + ", ".join(f"{k}={v}" for k, v in report["tools"].items())]
    if report["skills_invoked"]:
        lines.append("Skills invoked: " + ", ".join(report["skills_invoked"]))
    lines.append("")
    if not report["findings"]:
        lines.append("No findings. The session was clean on every detector.")
    for i, f in enumerate(report["findings"], 1):
        ev = ", ".join(f"#{n}" for n in f["evidence_calls"]) or "n/a"
        lines += [f"{i}. [{f['severity'].upper()}] {f['category']}: {f['title']}",
                  f"   evidence: calls {ev}", f"   fix: {f['suggested_fix']}"]
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Find retries, re-reads, failures and friction in a session log.")
    parser.add_argument("--input", required=True, help="session transcript (.jsonl)")
    parser.add_argument("--expected-skills", default="", help="comma-separated skills that should have run")
    parser.add_argument("--large-output", type=int, default=20000, help="chars above which an output is oversized")
    parser.add_argument("--orientation-budget", type=int, default=25, help="max calls before the first edit")
    parser.add_argument("--fail-on", choices=["low", "medium", "high"], default="medium",
                        help="lowest severity that makes the exit code 1")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        calls = load_calls(Path(args.input))
    except (OSError, ValueError) as exc:
        print(f"error: cannot analyze {args.input}: {exc}", file=sys.stderr)
        sys.exit(2)
    report = analyze(calls, args)
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(report))
    floor = SEVERITY_RANK[args.fail_on]
    sys.exit(1 if any(SEVERITY_RANK[f["severity"]] >= floor for f in report["findings"]) else 0)


if __name__ == "__main__":
    main()
