#!/usr/bin/env python3
"""Capture objective repo state to seed a handoff document.

Gathers the git branch, recent commits, and changed/untracked files so the
in-progress state of the work is recorded factually rather than from memory.

With --check FILE it instead checks a finished handoff doc is ready to be the prompt
of a background agent: required sections present, no unfilled <placeholders>, no
secret-looking strings, a bounded size. It then prints a launch command.

Usage:
  python3 handoff_context.py --repo . --format markdown
  python3 handoff_context.py --check handoff.md --name "Finish export flag"

Exit codes: 0 = ok / ready, 1 = handoff not ready (--check only), 2 = file unreadable.
Standard library only; no network or LLM calls; never launches anything itself.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys


def _git(repo: str, *args: str) -> str:
    """Run a git command in *repo*; return stdout (stripped) or '' on failure."""
    try:
        out = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def collect(repo: str, commits: int) -> dict:
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "(unknown)"
    log = _git(repo, "log", f"-{commits}", "--pretty=format:%h %s")
    status = _git(repo, "status", "--porcelain")

    changed, untracked = [], []
    for line in status.splitlines():
        if not line:
            continue
        code, path = line[:2], line[3:]
        (untracked if code.strip() == "??" else changed).append(path)

    return {
        "branch": branch,
        "recent_commits": [c for c in log.splitlines() if c],
        "changed_files": changed,
        "untracked_files": untracked,
    }


def to_markdown(ctx: dict) -> str:
    lines = ["## Key locations (auto-captured)", ""]
    lines.append(f"- **Branch:** `{ctx['branch']}`")
    if ctx["recent_commits"]:
        lines.append("- **Recent commits:**")
        lines += [f"  - `{c}`" for c in ctx["recent_commits"]]
    if ctx["changed_files"]:
        lines.append("- **Changed (uncommitted):**")
        lines += [f"  - `{f}`" for f in ctx["changed_files"]]
    if ctx["untracked_files"]:
        lines.append("- **Untracked:**")
        lines += [f"  - `{f}`" for f in ctx["untracked_files"]]
    if not (ctx["changed_files"] or ctx["untracked_files"]):
        lines.append("- Working tree clean.")
    return "\n".join(lines) + "\n"


REQUIRED_SECTIONS = ("goal", "current state", "next steps", "start here", "stop and report", "suggested skills")
SECRET_PATTERNS = {
    "private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
    "API key (sk-)": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "Slack token": r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b",
    "inline credential": r"(?i)\b(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"]?[^\s'\"<>]{8,}",
}


def check_handoff(path: str, max_chars: int) -> dict:
    """Check a handoff doc is fit to be a background agent's whole prompt."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    lowered = text.lower()
    problems: list[str] = []
    headings = " ".join(line.lower() for line in text.splitlines() if line.startswith("#") or "**" in line)
    for section in REQUIRED_SECTIONS:
        if section not in headings:
            problems.append(f"missing section: {section}")
    placeholders = sorted(set(re.findall(r"<[a-z][^<>\n]{1,60}>", text)))
    if placeholders:
        problems.append(f"{len(placeholders)} unfilled placeholder(s), e.g. {placeholders[0]}")
    for label, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, text):
            problems.append(f"possible secret: {label} — redact before using as a prompt")
    if len(text) > max_chars:
        problems.append(f"{len(text)} chars (limit {max_chars}); point at files instead of pasting them")
    if "```diff" in lowered or lowered.count("\n+") > 40:
        problems.append("looks like it pastes a diff; reference the branch or commit instead")
    return {"file": path, "chars": len(text), "ready": not problems, "problems": problems}


def launch_hint(path: str, name: str) -> list[str]:
    """Suggested commands; the user runs one, this script never does."""
    quoted, title = shlex.quote(path), shlex.quote(name)
    return [
        f'claude --bg --name {title} -- "$(cat {quoted})"   # if your Claude Code version has --bg',
        f"nohup claude -p < {quoted} > handoff-run.log 2>&1 &   # headless fallback",
        f'codex exec "$(cat {quoted})"   # Codex CLI equivalent',
    ]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Seed a handoff with objective repo state.")
    p.add_argument("--repo", default=".", help="Path to the git repository (default: .)")
    p.add_argument("--commits", type=int, default=5, help="How many recent commits to include")
    p.add_argument("--format", choices=["markdown", "json", "text"], default="markdown",
                   help="markdown (default) or json; text is accepted as an alias of markdown")
    p.add_argument("--check", metavar="FILE", help="check a handoff doc is ready to seed a background agent")
    p.add_argument("--name", default="Continue handoff", help="display name for the background session")
    p.add_argument("--max-chars", type=int, default=12000, help="size limit for a background prompt")
    args = p.parse_args(argv)

    if args.check:
        try:
            result = check_handoff(args.check, args.max_chars)
        except OSError as exc:
            print(f"error: cannot read {args.check}: {exc}", file=sys.stderr)
            return 2
        result["launch"] = launch_hint(args.check, args.name) if result["ready"] else []
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"{args.check}: {'READY' if result['ready'] else 'NOT READY'} ({result['chars']} chars)")
            for problem in result["problems"]:
                print(f"  - {problem}")
            if result["ready"]:
                print("Launch one of (check `--help` on your CLI first):")
                print("\n".join(f"  {cmd}" for cmd in result["launch"]))
        return 0 if result["ready"] else 1

    ctx = collect(args.repo, args.commits)
    if ctx["branch"] == "(unknown)" and not ctx["recent_commits"]:
        print(f"warning: '{args.repo}' is not a git repo or git is unavailable.", file=sys.stderr)

    if args.format == "json":
        print(json.dumps(ctx, indent=2))
    else:
        print(to_markdown(ctx))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
