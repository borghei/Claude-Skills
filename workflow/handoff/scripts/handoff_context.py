#!/usr/bin/env python3
"""Capture objective repo state to seed a handoff document.

Gathers the git branch, recent commits, and changed/untracked files so the
in-progress state of the work is recorded factually rather than from memory.
Standard library only; no network or LLM calls.
"""
from __future__ import annotations

import argparse
import json
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Seed a handoff with objective repo state.")
    p.add_argument("--repo", default=".", help="Path to the git repository (default: .)")
    p.add_argument("--commits", type=int, default=5, help="How many recent commits to include")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = p.parse_args(argv)

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
