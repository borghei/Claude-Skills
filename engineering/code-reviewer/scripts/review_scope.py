#!/usr/bin/env python3
"""Pin the scope of a two-axis review: base commit, diff, spec sources, standards sources.

Resolves a fixed base ref, confirms the diff against its merge-base is non-empty, lists
the commits and changed files, pulls issue references out of commit messages, finds
candidate spec files and the repo's documented standards, and prints the two briefs
(standards pass, spec pass) to hand to independent reviewers.

Usage:
  python3 review_scope.py --repo . --base main
  python3 review_scope.py --repo . --base v2.3.0 --spec docs/specs/export.md --format json

Exit codes: 0 = scope pinned, 1 = diff is empty (nothing to review), 2 = not a git
repository or the base ref does not resolve. Standard library only; read-only git calls.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ISSUE_RE = re.compile(r"(?:(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+)?(#\d+|\b[A-Z][A-Z0-9]+-\d+\b|!\d+)",
                      re.IGNORECASE)
STANDARDS_NAMES = ["CODING_STANDARDS.md", "CONTRIBUTING.md", "STYLEGUIDE.md", "STYLE.md", "docs/standards.md",
                   "AGENTS.md", "CLAUDE.md", ".editorconfig", "pyproject.toml", "ruff.toml", ".eslintrc.json",
                   "eslint.config.js", ".golangci.yml", ".swiftlint.yml", "detekt.yml"]
SPEC_DIRS = ["docs/specs", "specs", "docs/spec", "docs/rfcs", "rfcs", "docs/prd", "docs", ".scratch"]


def git(repo: str, *args: str) -> Optional[str]:
    """Run a read-only git command; return stdout or None on failure."""
    try:
        done = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return done.stdout.strip()


def find_specs(repo: Path, branch: str, explicit: Optional[str]) -> List[str]:
    """Return spec candidates: the explicit path, else files whose name shares a branch token."""
    if explicit:
        return [explicit]
    tokens = {t for t in re.split(r"[^a-z0-9]+", branch.lower()) if len(t) > 3}
    tokens -= {"feat", "feature", "main", "master", "release", "hotfix", "chore", "refactor"}
    hits: List[str] = []
    for folder in SPEC_DIRS:
        base = repo / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if any(tok in path.stem.lower() for tok in tokens):
                rel = str(path.relative_to(repo))
                if rel not in hits:
                    hits.append(rel)
    return hits[:10]


def collect(repo: str, base: str, head: str, spec: Optional[str]) -> Dict[str, Any]:
    """Gather everything both review passes need, or raise SystemExit(2) on a bad ref."""
    if git(repo, "rev-parse", "--git-dir") is None:
        print(f"error: {repo} is not a git repository", file=sys.stderr)
        sys.exit(2)
    base_sha = git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
    head_sha = git(repo, "rev-parse", "--verify", f"{head}^{{commit}}")
    if not base_sha or not head_sha:
        print(f"error: cannot resolve {'base ' + base if not base_sha else 'head ' + head}", file=sys.stderr)
        sys.exit(2)
    merge_base = git(repo, "merge-base", base_sha, head_sha) or base_sha
    commits = [c for c in (git(repo, "log", "--format=%h %s", f"{merge_base}..{head_sha}") or "").splitlines() if c]
    bodies = git(repo, "log", "--format=%B", f"{merge_base}..{head_sha}") or ""
    stat = git(repo, "diff", "--numstat", f"{merge_base}..{head_sha}") or ""
    files: List[Dict[str, Any]] = []
    for line in stat.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            added, removed, path = parts
            files.append({"path": path, "added": int(added) if added.isdigit() else 0,
                          "removed": int(removed) if removed.isdigit() else 0})
    issues = sorted({m.group(1).upper() if "-" in m.group(1) else m.group(1) for m in ISSUE_RE.finditer(bodies)})
    root = Path(git(repo, "rev-parse", "--show-toplevel") or repo)
    branch = git(repo, "rev-parse", "--abbrev-ref", head) or head
    standards = [n for n in STANDARDS_NAMES if (root / n).is_file()]
    return {
        "base": base, "base_sha": base_sha[:12], "head": head, "head_sha": head_sha[:12],
        "merge_base": merge_base[:12], "diff_command": f"git diff {base}...{head}",
        "commits": commits, "files": files,
        "lines_changed": sum(f["added"] + f["removed"] for f in files),
        "issue_refs": issues, "spec_candidates": find_specs(root, branch, spec),
        "standards_sources": standards,
    }


def briefs(scope: Dict[str, Any]) -> Dict[str, str]:
    """Write the two reviewer briefs. Each is meant for a reviewer with no other context."""
    common = (f"Review the diff `{scope['diff_command']}` ({len(scope['commits'])} commits, "
              f"{len(scope['files'])} files, {scope['lines_changed']} lines). Read only what the diff touches.")
    standards = scope["standards_sources"] or ["(none found: apply the language checklist in references/)"]
    spec_src = scope["spec_candidates"] + scope["issue_refs"]
    standards_brief = (common + " Axis: STANDARDS. Sources: " + ", ".join(standards) + ". For each finding give "
                       "file:line, the rule broken (source file and rule), and whether it is a hard violation or "
                       "a judgement call. Skip anything a linter in the repo already enforces. Do not judge "
                       "whether the change does what was asked; that is the other pass.")
    if spec_src:
        spec_brief = (common + " Axis: SPEC. Sources: " + ", ".join(spec_src) + ". Report (a) requirements "
                      "missing or only partly built, (b) behaviour nobody asked for, (c) requirements built "
                      "wrongly. Quote the spec line for each. Do not comment on style; that is the other pass.")
    else:
        spec_brief = "SKIPPED: no spec or issue found. Ask the author where the requirement lives before merging."
    return {"standards": standards_brief, "spec": spec_brief}


def render_text(scope: Dict[str, Any], b: Dict[str, str]) -> str:
    """Human-readable scope sheet."""
    lines = [f"Base {scope['base']} ({scope['base_sha']}) -> head {scope['head']} ({scope['head_sha']}), "
             f"merge-base {scope['merge_base']}",
             f"Diff: {scope['diff_command']}  |  {len(scope['files'])} files, {scope['lines_changed']} lines",
             "Commits:"] + [f"  {c}" for c in scope["commits"][:20]]
    lines.append("Issue refs: " + (", ".join(scope["issue_refs"]) or "none"))
    lines.append("Spec candidates: " + (", ".join(scope["spec_candidates"]) or "none"))
    lines.append("Standards sources: " + (", ".join(scope["standards_sources"]) or "none"))
    lines += ["", "Brief - standards pass:", "  " + b["standards"], "", "Brief - spec pass:", "  " + b["spec"]]
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Pin the base, diff and sources for a two-axis code review.")
    parser.add_argument("--repo", default=".", help="path to the git repository")
    parser.add_argument("--base", required=True, help="fixed base: branch, tag, SHA or HEAD~N")
    parser.add_argument("--head", default="HEAD", help="head ref (default HEAD)")
    parser.add_argument("--spec", help="path or URL of the spec/issue, if known")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    scope = collect(args.repo, args.base, args.head, args.spec)
    if not scope["files"]:
        print(f"error: no changes between {args.base} and {args.head}; nothing to review", file=sys.stderr)
        sys.exit(1)
    b = briefs(scope)
    if args.format == "json":
        print(json.dumps({**scope, "briefs": b}, indent=2))
    else:
        print(render_text(scope, b))
    sys.exit(0)


if __name__ == "__main__":
    main()
