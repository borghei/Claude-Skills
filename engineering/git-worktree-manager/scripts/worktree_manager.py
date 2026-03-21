#!/usr/bin/env python3
"""
worktree_manager.py - List, create, and clean up git worktrees with status information.

Reports branch, dirty state, age, and merge status for each worktree.
Supports creating new worktrees with deterministic naming and cleaning up
stale or merged-branch worktrees safely.

Usage:
    python worktree_manager.py list
    python worktree_manager.py list --json
    python worktree_manager.py create feature/auth --base main
    python worktree_manager.py remove ../wt-auth
    python worktree_manager.py cleanup --stale-days 14 --dry-run
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def run_git(args, cwd=None):
    """Run a git command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=cwd, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_repo_root():
    """Get the top-level directory of the main git repository."""
    root = run_git(["rev-parse", "--show-toplevel"])
    if not root:
        print("Error: not inside a git repository.", file=sys.stderr)
        sys.exit(1)
    return root


def parse_worktree_list_porcelain(repo_root):
    """Parse 'git worktree list --porcelain' into structured data."""
    raw = run_git(["worktree", "list", "--porcelain"], cwd=repo_root)
    if raw is None:
        return []

    worktrees = []
    current = {}
    for line in raw.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[len("worktree "):]}
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):]
        elif line.startswith("branch "):
            ref = line[len("branch "):]
            current["branch"] = ref.replace("refs/heads/", "")
        elif line == "detached":
            current["branch"] = "(detached HEAD)"
            current["detached"] = True
        elif line == "bare":
            current["bare"] = True

    if current:
        worktrees.append(current)
    return worktrees


def get_worktree_status(wt_path):
    """Check dirty state of a worktree."""
    porcelain = run_git(["status", "--porcelain"], cwd=wt_path)
    if porcelain is None:
        return "unknown"
    return "dirty" if porcelain else "clean"


def get_worktree_age_days(wt_path):
    """Get the age of a worktree directory in days."""
    try:
        mtime = os.path.getmtime(wt_path)
        age_seconds = time.time() - mtime
        return max(0, int(age_seconds / 86400))
    except OSError:
        return -1


def is_branch_merged(branch, target="main", cwd=None):
    """Check whether a branch has been merged into target."""
    merged = run_git(["branch", "--merged", target], cwd=cwd)
    if merged is None:
        return False
    merged_branches = [b.strip().lstrip("* ") for b in merged.splitlines()]
    return branch in merged_branches


def get_ahead_behind(branch, cwd=None):
    """Get ahead/behind counts relative to the upstream or origin/main."""
    upstream = run_git(["rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"], cwd=cwd)
    if not upstream:
        upstream = "origin/main"
    counts = run_git(["rev-list", "--left-right", "--count", f"{branch}...{upstream}"], cwd=cwd)
    if counts:
        parts = counts.split()
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    return 0, 0


def enrich_worktree(wt, repo_root):
    """Add status, age, merge info, and ahead/behind to a worktree dict."""
    path = wt.get("path", "")
    is_main = (path == repo_root)
    wt["is_main"] = is_main
    wt["exists"] = os.path.isdir(path)

    if wt["exists"]:
        wt["status"] = get_worktree_status(path)
        wt["age_days"] = get_worktree_age_days(path)
    else:
        wt["status"] = "missing"
        wt["age_days"] = -1

    branch = wt.get("branch", "")
    if branch and branch != "(detached HEAD)" and not is_main:
        wt["merged"] = is_branch_merged(branch, cwd=repo_root)
        ahead, behind = get_ahead_behind(branch, cwd=repo_root)
        wt["ahead"] = ahead
        wt["behind"] = behind
    else:
        wt["merged"] = False
        wt["ahead"] = 0
        wt["behind"] = 0

    return wt


def cmd_list(args):
    """List all worktrees with enriched status."""
    repo_root = get_repo_root()
    worktrees = parse_worktree_list_porcelain(repo_root)
    enriched = [enrich_worktree(wt, repo_root) for wt in worktrees]

    if args.json:
        print(json.dumps(enriched, indent=2))
        return

    if not enriched:
        print("No worktrees found.")
        return

    print(f"{'Path':<45} {'Branch':<30} {'Status':<10} {'Age':<8} {'Flags'}")
    print("-" * 110)
    for wt in enriched:
        path = wt.get("path", "?")
        branch = wt.get("branch", "?")
        status = wt.get("status", "?")
        age = f"{wt['age_days']}d" if wt["age_days"] >= 0 else "?"

        flags = []
        if wt.get("is_main"):
            flags.append("MAIN")
        if wt.get("merged"):
            flags.append("MERGED")
        if wt.get("detached"):
            flags.append("DETACHED")
        if not wt.get("exists"):
            flags.append("MISSING")
        ahead, behind = wt.get("ahead", 0), wt.get("behind", 0)
        if ahead:
            flags.append(f"+{ahead}")
        if behind:
            flags.append(f"-{behind}")

        flag_str = ", ".join(flags) if flags else ""
        # Truncate long paths/branches for display
        display_path = path if len(path) <= 44 else "..." + path[-41:]
        display_branch = branch if len(branch) <= 29 else branch[:26] + "..."
        print(f"{display_path:<45} {display_branch:<30} {status:<10} {age:<8} {flag_str}")

    total = len(enriched)
    dirty = sum(1 for w in enriched if w.get("status") == "dirty")
    merged = sum(1 for w in enriched if w.get("merged"))
    print(f"\nTotal: {total} | Dirty: {dirty} | Merged: {merged}")


def cmd_create(args):
    """Create a new worktree with deterministic naming."""
    repo_root = get_repo_root()
    branch = args.branch
    base = args.base

    # Derive worktree name from branch
    short_name = re.sub(r".*/", "", branch).lower()
    short_name = re.sub(r"[^a-z0-9-]", "-", short_name)
    wt_name = f"wt-{short_name}"
    parent_dir = Path(repo_root).parent
    wt_path = str(parent_dir / wt_name)

    if os.path.exists(wt_path):
        msg = f"Error: path already exists: {wt_path}"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    # Check if branch already exists
    branch_exists = run_git(["rev-parse", "--verify", branch], cwd=repo_root) is not None

    if branch_exists:
        result = run_git(["worktree", "add", wt_path, branch], cwd=repo_root)
    else:
        result = run_git(["worktree", "add", wt_path, "-b", branch, base], cwd=repo_root)

    if result is None:
        msg = f"Error: failed to create worktree at {wt_path}"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    info = {
        "action": "created",
        "path": wt_path,
        "branch": branch,
        "base": base,
        "name": wt_name,
    }

    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print(f"Worktree created: {wt_path}")
        print(f"  Branch: {branch}")
        print(f"  Base:   {base}")
        print(f"  Name:   {wt_name}")
        print(f"\nNext: cd {wt_path}")


def cmd_remove(args):
    """Remove a worktree safely."""
    repo_root = get_repo_root()
    wt_path = os.path.abspath(args.path)

    if wt_path == repo_root:
        msg = "Error: cannot remove the main worktree."
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    # Check dirty state unless --force
    if not args.force and os.path.isdir(wt_path):
        status = get_worktree_status(wt_path)
        if status == "dirty":
            msg = f"Worktree at {wt_path} has uncommitted changes. Use --force to remove."
            if args.json:
                print(json.dumps({"error": msg, "status": "dirty"}))
            else:
                print(msg, file=sys.stderr)
            sys.exit(1)

    git_args = ["worktree", "remove", wt_path]
    if args.force:
        git_args.insert(2, "--force")

    result = run_git(git_args, cwd=repo_root)
    if result is None:
        msg = f"Error: failed to remove worktree at {wt_path}"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    info = {"action": "removed", "path": wt_path, "forced": args.force}
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print(f"Worktree removed: {wt_path}")


def cmd_cleanup(args):
    """Clean up stale and merged-branch worktrees."""
    repo_root = get_repo_root()
    worktrees = parse_worktree_list_porcelain(repo_root)
    enriched = [enrich_worktree(wt, repo_root) for wt in worktrees]

    candidates = []
    for wt in enriched:
        if wt.get("is_main"):
            continue
        reasons = []
        if wt.get("merged"):
            reasons.append("merged")
        if wt.get("age_days", 0) >= args.stale_days:
            reasons.append(f"stale ({wt['age_days']}d)")
        if not wt.get("exists"):
            reasons.append("missing")
        if reasons:
            wt["cleanup_reasons"] = reasons
            wt["safe_to_remove"] = wt.get("status") != "dirty"
            candidates.append(wt)

    if args.json:
        output = {
            "dry_run": args.dry_run,
            "stale_threshold_days": args.stale_days,
            "candidates": candidates,
        }
        if not args.dry_run:
            removed = []
            skipped = []
            for c in candidates:
                if c["safe_to_remove"]:
                    run_git(["worktree", "remove", c["path"]], cwd=repo_root)
                    removed.append(c["path"])
                else:
                    skipped.append(c["path"])
            run_git(["worktree", "prune"], cwd=repo_root)
            output["removed"] = removed
            output["skipped_dirty"] = skipped
        print(json.dumps(output, indent=2))
        return

    if not candidates:
        print(f"No cleanup candidates (threshold: {args.stale_days} days).")
        run_git(["worktree", "prune"], cwd=repo_root)
        return

    print(f"Cleanup candidates (threshold: {args.stale_days} days):\n")
    for c in candidates:
        reasons = ", ".join(c["cleanup_reasons"])
        safe = "safe" if c["safe_to_remove"] else "DIRTY - skip"
        print(f"  {c['path']}")
        print(f"    Branch:  {c.get('branch', '?')}")
        print(f"    Reasons: {reasons}")
        print(f"    Status:  {safe}")
        print()

    if args.dry_run:
        print(f"Dry run: {len(candidates)} candidate(s). Re-run without --dry-run to remove.")
    else:
        removed = 0
        for c in candidates:
            if c["safe_to_remove"]:
                run_git(["worktree", "remove", c["path"]], cwd=repo_root)
                print(f"  Removed: {c['path']}")
                removed += 1
            else:
                print(f"  Skipped (dirty): {c['path']}")
        run_git(["worktree", "prune"], cwd=repo_root)
        print(f"\nRemoved {removed} worktree(s). Pruned stale metadata.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage git worktrees: list, create, remove, and cleanup."
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    sp_list = subparsers.add_parser("list", help="List all worktrees with status")
    sp_list.add_argument("--json", action="store_true", help="Output in JSON format")

    # create
    sp_create = subparsers.add_parser("create", help="Create a new worktree")
    sp_create.add_argument("branch", help="Branch name for the worktree")
    sp_create.add_argument("--base", default="main", help="Base branch (default: main)")
    sp_create.add_argument("--json", action="store_true", help="Output in JSON format")

    # remove
    sp_remove = subparsers.add_parser("remove", help="Remove a worktree")
    sp_remove.add_argument("path", help="Path to the worktree to remove")
    sp_remove.add_argument("--force", action="store_true", help="Force removal even if dirty")
    sp_remove.add_argument("--json", action="store_true", help="Output in JSON format")

    # cleanup
    sp_cleanup = subparsers.add_parser("cleanup", help="Clean up stale/merged worktrees")
    sp_cleanup.add_argument(
        "--stale-days", type=int, default=14,
        help="Consider worktrees older than N days stale (default: 14)"
    )
    sp_cleanup.add_argument(
        "--dry-run", action="store_true",
        help="Show candidates without removing"
    )
    sp_cleanup.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "list": cmd_list,
        "create": cmd_create,
        "remove": cmd_remove,
        "cleanup": cmd_cleanup,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
