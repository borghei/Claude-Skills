#!/usr/bin/env python3
"""Install the git-guardrails hook into Claude Code settings, merging, never overwriting.

What it does, in order:
  1. Copies assets/git_guardrails_hook.py to <base>/.claude/hooks/ (unchanged copies are skipped;
     a different file already there is left alone and reported as a conflict).
  2. Adds one PreToolUse entry (matcher "Bash") to <base>/.claude/settings.json. Every existing
     key, hook and entry is preserved; if any entry already runs the guardrail, nothing changes.
  3. Optionally (--policy) copies the sample policy to <base>/.claude/git-guardrails.json if absent.
  4. Optionally (--git-hooks) installs the plain git pre-push and pre-rebase hooks into
     <repo>/.git/hooks, never replacing a hook that is not ours.

<base> is --project (project scope) or --home (user scope, default ~). A settings file that is
not valid JSON is never touched. Before a real write the old settings are saved to settings.json.bak.

Usage:
  python3 install_guardrails.py --project . --dry-run
  python3 install_guardrails.py --project . --policy --git-hooks
  python3 install_guardrails.py --scope user --home ~ --format json

Exit codes:
  0  installed, or already installed (idempotent re-run)
  1  finished, but a conflict was left untouched (different hook file or foreign git hook)
  2  usage error or unreadable / invalid settings.json (nothing written)
"""

from __future__ import annotations

import argparse
import difflib
import filecmp
import json
import shutil
import stat
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ASSETS = Path(__file__).resolve().parent.parent / "assets"
HOOK_NAME = "git_guardrails_hook.py"
MARKER = "git-guardrails"
GIT_HOOKS = ("pre-push", "pre-rebase")
COMMANDS = {
    "project": 'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/git_guardrails_hook.py"',
    "user": 'python3 "$HOME/.claude/hooks/git_guardrails_hook.py"',
}


class InstallError(Exception):
    """A condition that must stop the installer before anything is written."""


def load_settings(path: Path) -> Dict[str, Any]:
    """Read settings.json, refusing anything that is not a JSON object."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise InstallError(f"{path} is not valid JSON ({exc}); fix it by hand, nothing was changed")
    if not isinstance(data, dict):
        raise InstallError(f"{path} must contain a JSON object")
    return data


def already_installed(settings: Dict[str, Any]) -> bool:
    """True when any PreToolUse hook command already references the guardrail script."""
    hooks = settings.get("hooks")
    entries = hooks.get("PreToolUse") if isinstance(hooks, dict) else None
    for entry in entries if isinstance(entries, list) else []:
        inner = entry.get("hooks") if isinstance(entry, dict) else None
        for hook in inner if isinstance(inner, list) else []:
            if isinstance(hook, dict) and HOOK_NAME in str(hook.get("command", "")):
                return True
    return False


def merge_settings(settings: Dict[str, Any], command: str) -> Tuple[Dict[str, Any], bool]:
    """Return (merged copy, changed). Appends a new entry; existing entries are never edited."""
    merged = json.loads(json.dumps(settings))
    hooks = merged.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError("settings 'hooks' is not an object; refusing to guess how to merge")
    pre = hooks.setdefault("PreToolUse", [])
    if not isinstance(pre, list):
        raise InstallError("settings 'hooks.PreToolUse' is not a list; refusing to guess how to merge")
    if already_installed(merged):
        return merged, False
    pre.append({"matcher": "Bash", "hooks": [{"type": "command", "command": command, "timeout": 10}]})
    return merged, True


def plan_copy(src: Path, dest: Path, executable: bool) -> Dict[str, Any]:
    """Decide what to do with one file copy without touching disk."""
    if not dest.exists():
        action = "create"
    elif filecmp.cmp(src, dest, shallow=False):
        action = "unchanged"
    elif MARKER in dest.read_text(encoding="utf-8", errors="replace"):
        action = "conflict-outdated"
    else:
        action = "conflict-foreign"
    return {"src": str(src), "dest": str(dest), "action": action, "executable": executable}


def apply_copy(step: Dict[str, Any]) -> None:
    """Perform a planned 'create' copy."""
    dest = Path(step["dest"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(step["src"], dest)
    if step["executable"]:
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def build_plan(args: argparse.Namespace) -> Dict[str, Any]:
    """Work out every change, read-only."""
    base = (args.project if args.scope == "project" else args.home).expanduser().resolve()
    if not base.is_dir():
        raise InstallError(f"target directory does not exist: {base}")
    claude_dir = base / ".claude"
    settings_path = claude_dir / "settings.json"
    current = load_settings(settings_path)
    merged, changed = merge_settings(current, COMMANDS[args.scope])
    files: List[Dict[str, Any]] = [plan_copy(ASSETS / HOOK_NAME, claude_dir / "hooks" / HOOK_NAME, True)]
    if args.policy:
        step = plan_copy(ASSETS / "sample_guardrail_policy.json", claude_dir / "git-guardrails.json", False)
        if step["action"].startswith("conflict"):
            step["action"] = "keep-existing"
        files.append(step)
    notes: List[str] = []
    if args.git_hooks:
        git_dir = base / ".git"
        if git_dir.is_dir():
            files += [plan_copy(ASSETS / name, git_dir / "hooks" / name, True) for name in GIT_HOOKS]
        else:
            notes.append(f"--git-hooks skipped: {git_dir} is not a directory (not a repo root, or a worktree)")
    before = json.dumps(current, indent=2).splitlines() if settings_path.exists() else []
    diff = list(difflib.unified_diff(before, json.dumps(merged, indent=2).splitlines(),
                                     str(settings_path), str(settings_path) + " (merged)", lineterm=""))
    return {"scope": args.scope, "base": str(base), "settings": str(settings_path),
            "settings_action": "merge" if changed else "unchanged", "settings_diff": diff,
            "merged": merged, "files": files, "notes": notes, "dry_run": args.dry_run}


def apply_plan(plan: Dict[str, Any]) -> None:
    """Write the planned changes. Conflicts are never overwritten."""
    for step in plan["files"]:
        if step["action"] == "create":
            apply_copy(step)
    if plan["settings_action"] == "merge":
        path = Path(plan["settings"])
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            shutil.copyfile(path, path.with_name(path.name + ".bak"))
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(plan["merged"], indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)


def conflicts(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return file steps left untouched because something different is already there."""
    return [s for s in plan["files"] if s["action"].startswith("conflict")]


def render_text(plan: Dict[str, Any]) -> str:
    """Human-readable summary of the plan or the applied result."""
    verb = "Would" if plan["dry_run"] else "Did"
    lines = [f"git-guardrails installer ({plan['scope']} scope){'  [dry run]' if plan['dry_run'] else ''}",
             f"  base:     {plan['base']}",
             f"  settings: {plan['settings']} -> {plan['settings_action']}"]
    for step in plan["files"]:
        lines.append(f"  file:     {step['dest']} -> {step['action']}")
    if plan["settings_diff"] and plan["dry_run"]:
        lines.append("")
        lines.extend("    " + line for line in plan["settings_diff"])
    for step in conflicts(plan):
        if step["action"] == "conflict-outdated":
            lines.append(f"  ! {step['dest']} is an older guardrail copy; diff it against {step['src']} and update by hand")
        else:
            lines.append(f"  ! {step['dest']} belongs to another tool; chain it manually (call ours from yours)")
    lines.extend(f"  note: {n}" for n in plan["notes"])
    lines.append("")
    if conflicts(plan):
        lines.append(f"{verb} install with {len(conflicts(plan))} conflict(s) left untouched.")
    elif plan["settings_action"] == "unchanged" and all(s["action"] != "create" for s in plan["files"]):
        lines.append("Already installed; nothing to change.")
    else:
        lines.append(f"{verb} install. Verify with: python3 scripts/guardrail_test.py --hook "
                     f"{plan['files'][0]['dest']}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Command-line interface."""
    p = argparse.ArgumentParser(description="Merge the git-guardrails PreToolUse hook into Claude Code settings.")
    p.add_argument("--scope", choices=["project", "user"], default="project",
                   help="project: <project>/.claude/settings.json; user: <home>/.claude/settings.json")
    p.add_argument("--project", type=Path, default=Path("."), help="project root for project scope (default .)")
    p.add_argument("--home", type=Path, default=Path("~"), help="home directory for user scope (default ~)")
    p.add_argument("--policy", action="store_true", help="also copy the sample policy if none exists")
    p.add_argument("--git-hooks", action="store_true", help="also install plain git pre-push/pre-rebase hooks")
    p.add_argument("--dry-run", action="store_true", help="show the plan and settings diff, write nothing")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    return p


def main() -> None:
    """Entry point."""
    args = build_parser().parse_args()
    try:
        plan = build_plan(args)
        if not args.dry_run:
            apply_plan(plan)
    except InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"error: could not write: {exc}", file=sys.stderr)
        sys.exit(2)
    if args.format == "json":
        out = {k: v for k, v in plan.items() if k != "merged"}
        out["conflicts"] = len(conflicts(plan))
        print(json.dumps(out, indent=2))
    else:
        print(render_text(plan))
    sys.exit(1 if conflicts(plan) else 0)


if __name__ == "__main__":
    main()
