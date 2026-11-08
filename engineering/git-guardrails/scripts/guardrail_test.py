#!/usr/bin/env python3
"""Run a corpus of shell commands through the git-guardrails hook and report allow/block.

Each command is wrapped in the same JSON payload Claude Code sends to a
PreToolUse hook and piped to the hook as a real subprocess, so the test covers
the exact contract that runs in production: stdin JSON in, exit 0 (allow) or
exit 2 plus a stderr reason (block) out.

Usage:
  python3 guardrail_test.py                                   # bundled hook + corpus
  python3 guardrail_test.py --corpus my_corpus.json --format json
  python3 guardrail_test.py --hook .claude/hooks/git_guardrails_hook.py
  python3 guardrail_test.py --command "git push -f origin main" --branch feature/x

Exit codes:
  0  every case matched its expectation
  1  at least one case mismatched, errored, or blocked without a reason
  2  usage error (missing hook or corpus, invalid corpus JSON)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_HOOK = SKILL_DIR / "assets" / "git_guardrails_hook.py"
DEFAULT_CORPUS = SKILL_DIR / "assets" / "sample_command_corpus.json"
EXIT_TO_DECISION = {0: "allow", 2: "block"}


class UsageError(Exception):
    """Raised for problems the caller must fix before a run is meaningful."""


def load_corpus(path: Path) -> Dict[str, Any]:
    """Load and validate a corpus file: {"default_branch": str, "cases": [...]}."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise UsageError(f"corpus not found: {path}")
    except json.JSONDecodeError as exc:
        raise UsageError(f"corpus is not valid JSON ({path}): {exc}")
    if isinstance(data, list):
        data = {"cases": data}
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or not cases:
        raise UsageError("corpus needs a non-empty 'cases' list")
    for idx, case in enumerate(cases, 1):
        if not isinstance(case, dict) or not isinstance(case.get("command"), str):
            raise UsageError(f"case {idx}: needs a string 'command'")
        if case.get("expect") not in ("allow", "block"):
            raise UsageError(f"case {idx}: 'expect' must be 'allow' or 'block'")
    return data


def run_hook(hook: Path, command: str, branch: str, policy: Optional[Path],
             timeout: float) -> Dict[str, Any]:
    """Pipe one Bash tool call to the hook and capture its decision."""
    payload = {
        "session_id": "guardrail-test",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command, "description": "guardrail corpus case"},
        "cwd": os.getcwd(),
    }
    env = dict(os.environ)
    env.pop("GIT_GUARDRAILS_DISABLE", None)
    env["GIT_GUARDRAILS_CURRENT_BRANCH"] = branch
    env["GIT_GUARDRAILS_POLICY"] = str(policy) if policy else os.devnull
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        proc = subprocess.run([sys.executable, str(hook)], input=json.dumps(payload),
                              capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"decision": "error", "exit_code": None, "stderr": f"hook timed out after {timeout}s"}
    decision = EXIT_TO_DECISION.get(proc.returncode, "error")
    return {"decision": decision, "exit_code": proc.returncode, "stderr": proc.stderr.strip()}


def rule_from_stderr(stderr: str) -> Optional[str]:
    """Extract the [rule-id] the hook printed, if any."""
    start, end = stderr.find("["), stderr.find("]")
    return stderr[start + 1:end] if 0 <= start < end else None


def evaluate(hook: Path, corpus: Dict[str, Any], policy: Optional[Path],
             timeout: float) -> Dict[str, Any]:
    """Run every case and compare the hook's decision with the expectation."""
    default_branch = str(corpus.get("default_branch") or "feature/work")
    results: List[Dict[str, Any]] = []
    for case in corpus["cases"]:
        branch = str(case.get("branch") or default_branch)
        got = run_hook(hook, case["command"], branch, policy, timeout)
        rule = rule_from_stderr(got["stderr"]) if got["decision"] == "block" else None
        problems: List[str] = []
        if got["decision"] == "error":
            problems.append(f"hook exited {got['exit_code']} (only 0 and 2 are valid)")
        elif got["decision"] != case["expect"]:
            problems.append(f"expected {case['expect']}, hook said {got['decision']}")
        if got["decision"] == "block" and not got["stderr"]:
            problems.append("blocked with an empty stderr reason; the agent cannot tell why")
        if case.get("rule") and got["decision"] == "block" and rule != case["rule"]:
            problems.append(f"expected rule {case['rule']}, hook reported {rule}")
        results.append({"command": case["command"], "branch": branch, "expect": case["expect"],
                        "decision": got["decision"], "rule": rule, "ok": not problems,
                        "problems": problems, "stderr": got["stderr"]})
    counts = {
        "total": len(results),
        "passed": sum(r["ok"] for r in results),
        "failed": sum(not r["ok"] for r in results),
        "blocked": sum(r["decision"] == "block" for r in results),
        "allowed": sum(r["decision"] == "allow" for r in results),
    }
    return {"hook": str(hook), "policy": str(policy) if policy else None,
            "summary": counts, "results": results}


def render_text(report: Dict[str, Any], verbose: bool) -> str:
    """Human-readable table: one line per case, failures expanded."""
    lines = [f"git-guardrails corpus run  hook={report['hook']}"]
    if report["policy"]:
        lines.append(f"policy={report['policy']}")
    lines.append("")
    for r in report["results"]:
        mark = "PASS" if r["ok"] else "FAIL"
        tag = f"{r['decision'].upper():5}" + (f" [{r['rule']}]" if r["rule"] else "")
        if r["ok"] and not verbose:
            lines.append(f"  {mark}  {tag:32} {r['command'][:70]}")
            continue
        lines.append(f"  {mark}  {tag:32} {r['command'][:70]}  (branch {r['branch']})")
        lines.extend(f"        - {p}" for p in r["problems"])
        if verbose and r["stderr"]:
            lines.append("        stderr: " + r["stderr"].splitlines()[0][:110])
    s = report["summary"]
    lines.append("")
    lines.append(f"{s['passed']}/{s['total']} cases passed  "
                 f"({s['blocked']} blocked, {s['allowed']} allowed, {s['failed']} failed)")
    lines.append("RESULT: PASS" if s["failed"] == 0 else "RESULT: FAIL - fix the hook or the corpus expectation")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Command-line interface."""
    p = argparse.ArgumentParser(description="Test the git-guardrails PreToolUse hook against a command corpus.")
    p.add_argument("--hook", type=Path, default=DEFAULT_HOOK, help="hook script to test (default: bundled hook)")
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS, help="corpus JSON (default: bundled sample)")
    p.add_argument("--policy", type=Path, help="policy JSON passed to the hook (default: built-in policy)")
    p.add_argument("--command", help="test one ad-hoc command instead of a corpus")
    p.add_argument("--expect", choices=["allow", "block"], help="expectation for --command")
    p.add_argument("--branch", default="feature/work", help="checked-out branch to simulate for --command")
    p.add_argument("--timeout", type=float, default=10.0, help="seconds per hook call (default 10)")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    p.add_argument("--verbose", action="store_true", help="show branch and stderr for every case")
    return p


def main() -> None:
    """Entry point."""
    args = build_parser().parse_args()
    try:
        if not args.hook.is_file():
            raise UsageError(f"hook not found: {args.hook}")
        if args.policy and not args.policy.is_file():
            raise UsageError(f"policy not found: {args.policy}")
        if args.command:
            corpus = {"default_branch": args.branch,
                      "cases": [{"command": args.command, "expect": args.expect or "block"}]}
        else:
            corpus = load_corpus(args.corpus)
        report = evaluate(args.hook, corpus, args.policy, args.timeout)
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    if args.command and not args.expect:
        report["summary"].update(failed=0, passed=1)
        report["results"][0]["ok"] = True
        report["results"][0]["problems"] = []
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(render_text(report, args.verbose or bool(args.command)))
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
