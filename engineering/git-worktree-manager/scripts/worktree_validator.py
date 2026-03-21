#!/usr/bin/env python3
"""
worktree_validator.py - Validate worktree health across a git repository.

Checks for stale worktrees, missing directories, orphaned branches,
environment file parity, port map integrity, and lockfile consistency.

Usage:
    python worktree_validator.py
    python worktree_validator.py --json
    python worktree_validator.py --checks stale,env,ports
    python worktree_validator.py --stale-days 7
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

ALL_CHECKS = ["stale", "missing", "branch", "env", "ports", "lockfile"]

ENV_FILES = [".env", ".env.local", ".env.development", ".env.test"]
LOCKFILES = [
    "pnpm-lock.yaml", "package-lock.json", "yarn.lock",
    "requirements.txt", "Pipfile.lock", "go.sum", "Gemfile.lock",
]


def run_git(args, cwd=None):
    """Run a git command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=cwd, timeout=30
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_repo_root():
    """Get the main repository root."""
    root = run_git(["rev-parse", "--show-toplevel"])
    if not root:
        print("Error: not inside a git repository.", file=sys.stderr)
        sys.exit(1)
    return root


def parse_worktrees(repo_root):
    """Parse worktree list into structured records."""
    raw = run_git(["worktree", "list", "--porcelain"], cwd=repo_root)
    if not raw:
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
            current["branch"] = line[len("branch "):].replace("refs/heads/", "")
        elif line == "detached":
            current["branch"] = "(detached)"
            current["detached"] = True
        elif line == "bare":
            current["bare"] = True
    if current:
        worktrees.append(current)
    return worktrees


def get_env_keys(filepath):
    """Extract variable names from an env file, ignoring comments and blanks."""
    keys = set()
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=", 1)[0].strip()
                    if key:
                        keys.add(key)
    except (OSError, UnicodeDecodeError):
        pass
    return keys


def check_stale(worktrees, repo_root, stale_days):
    """Check for worktrees older than the stale threshold."""
    findings = []
    for wt in worktrees:
        if wt["path"] == repo_root:
            continue
        if not os.path.isdir(wt["path"]):
            continue
        try:
            mtime = os.path.getmtime(wt["path"])
            age_days = int((time.time() - mtime) / 86400)
        except OSError:
            age_days = -1

        if age_days >= stale_days:
            findings.append({
                "check": "stale",
                "severity": SEVERITY_WARNING,
                "path": wt["path"],
                "branch": wt.get("branch", "?"),
                "age_days": age_days,
                "threshold": stale_days,
                "message": f"Worktree is {age_days} days old (threshold: {stale_days})",
            })
    return findings


def check_missing(worktrees, repo_root):
    """Check for worktrees whose directories no longer exist."""
    findings = []
    for wt in worktrees:
        if wt["path"] == repo_root:
            continue
        if not os.path.isdir(wt["path"]):
            findings.append({
                "check": "missing",
                "severity": SEVERITY_ERROR,
                "path": wt["path"],
                "branch": wt.get("branch", "?"),
                "message": "Worktree directory does not exist. Run 'git worktree prune'.",
            })
    return findings


def check_branch(worktrees, repo_root):
    """Check for orphaned branches (remote deleted) and detached HEADs."""
    findings = []
    # Get list of remote branches
    remote_raw = run_git(["branch", "-r", "--format=%(refname:short)"], cwd=repo_root)
    remote_branches = set()
    if remote_raw:
        remote_branches = {b.strip() for b in remote_raw.splitlines()}

    for wt in worktrees:
        if wt["path"] == repo_root:
            continue
        branch = wt.get("branch", "")

        if wt.get("detached"):
            findings.append({
                "check": "branch",
                "severity": SEVERITY_WARNING,
                "path": wt["path"],
                "branch": branch,
                "message": "Worktree is in detached HEAD state.",
            })
            continue

        if not branch:
            continue

        # Check if the branch has a remote tracking counterpart
        tracking = run_git(
            ["rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"], cwd=repo_root
        )
        if tracking and tracking not in remote_branches:
            findings.append({
                "check": "branch",
                "severity": SEVERITY_WARNING,
                "path": wt["path"],
                "branch": branch,
                "message": f"Upstream '{tracking}' no longer exists on remote.",
            })

        # Check if the branch is merged into main
        merged_raw = run_git(["branch", "--merged", "main"], cwd=repo_root)
        if merged_raw:
            merged_list = [b.strip().lstrip("* ") for b in merged_raw.splitlines()]
            if branch in merged_list and branch != "main":
                findings.append({
                    "check": "branch",
                    "severity": SEVERITY_INFO,
                    "path": wt["path"],
                    "branch": branch,
                    "message": "Branch is already merged into main. Consider removing this worktree.",
                })

    return findings


def check_env(worktrees, repo_root):
    """Validate env file parity between main repo and worktrees."""
    findings = []

    # Collect main repo env keys per file
    main_env = {}
    for env_file in ENV_FILES:
        main_path = os.path.join(repo_root, env_file)
        if os.path.isfile(main_path):
            main_env[env_file] = get_env_keys(main_path)

    if not main_env:
        findings.append({
            "check": "env",
            "severity": SEVERITY_INFO,
            "path": repo_root,
            "message": "No .env files found in main repo. Skipping parity check.",
        })
        return findings

    for wt in worktrees:
        if wt["path"] == repo_root:
            continue
        if not os.path.isdir(wt["path"]):
            continue

        for env_file, main_keys in main_env.items():
            wt_env_path = os.path.join(wt["path"], env_file)
            if not os.path.isfile(wt_env_path):
                findings.append({
                    "check": "env",
                    "severity": SEVERITY_WARNING,
                    "path": wt["path"],
                    "file": env_file,
                    "message": f"Missing {env_file} (present in main repo).",
                })
                continue

            wt_keys = get_env_keys(wt_env_path)
            missing_in_wt = main_keys - wt_keys
            extra_in_wt = wt_keys - main_keys

            if missing_in_wt:
                findings.append({
                    "check": "env",
                    "severity": SEVERITY_WARNING,
                    "path": wt["path"],
                    "file": env_file,
                    "missing_keys": sorted(missing_in_wt),
                    "message": f"{env_file} is missing {len(missing_in_wt)} key(s) present in main: {', '.join(sorted(missing_in_wt))}",
                })
            if extra_in_wt:
                findings.append({
                    "check": "env",
                    "severity": SEVERITY_INFO,
                    "path": wt["path"],
                    "file": env_file,
                    "extra_keys": sorted(extra_in_wt),
                    "message": f"{env_file} has {len(extra_in_wt)} extra key(s) not in main: {', '.join(sorted(extra_in_wt))}",
                })

    return findings


def check_ports(worktrees, repo_root):
    """Validate .worktree-ports.json integrity and uniqueness."""
    findings = []
    all_ports = {}  # port -> worktree path

    for wt in worktrees:
        if not os.path.isdir(wt["path"]):
            continue
        port_file = os.path.join(wt["path"], ".worktree-ports.json")
        if wt["path"] == repo_root:
            if not os.path.isfile(port_file):
                continue  # main repo may not have a port file
        if not os.path.isfile(port_file):
            if wt["path"] != repo_root:
                findings.append({
                    "check": "ports",
                    "severity": SEVERITY_WARNING,
                    "path": wt["path"],
                    "message": "Missing .worktree-ports.json file.",
                })
            continue

        try:
            with open(port_file, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            findings.append({
                "check": "ports",
                "severity": SEVERITY_ERROR,
                "path": wt["path"],
                "message": f"Invalid .worktree-ports.json: {e}",
            })
            continue

        ports = data.get("ports", {})
        if not isinstance(ports, dict) or not ports:
            findings.append({
                "check": "ports",
                "severity": SEVERITY_ERROR,
                "path": wt["path"],
                "message": "Port map is empty or malformed in .worktree-ports.json.",
            })
            continue

        # Check for collisions with other worktrees
        for service, port in ports.items():
            if not isinstance(port, int):
                findings.append({
                    "check": "ports",
                    "severity": SEVERITY_ERROR,
                    "path": wt["path"],
                    "message": f"Port for '{service}' is not an integer: {port}",
                })
                continue
            key = f"{service}:{port}"
            if port in all_ports and all_ports[port] != wt["path"]:
                findings.append({
                    "check": "ports",
                    "severity": SEVERITY_ERROR,
                    "path": wt["path"],
                    "message": f"Port {port} ({service}) conflicts with {all_ports[port]}.",
                })
            all_ports[port] = wt["path"]

        # Validate branch matches
        recorded_branch = data.get("branch", "")
        actual_branch = wt.get("branch", "")
        if recorded_branch and actual_branch and recorded_branch != actual_branch:
            findings.append({
                "check": "ports",
                "severity": SEVERITY_WARNING,
                "path": wt["path"],
                "message": f"Branch mismatch: ports.json says '{recorded_branch}', git says '{actual_branch}'.",
            })

    return findings


def check_lockfile(worktrees, repo_root):
    """Check that lockfiles in worktrees match the main repo."""
    findings = []

    main_locks = {}
    for lf in LOCKFILES:
        main_path = os.path.join(repo_root, lf)
        if os.path.isfile(main_path):
            try:
                main_locks[lf] = os.path.getmtime(main_path)
            except OSError:
                pass

    for wt in worktrees:
        if wt["path"] == repo_root:
            continue
        if not os.path.isdir(wt["path"]):
            continue

        for lf, main_mtime in main_locks.items():
            wt_lf = os.path.join(wt["path"], lf)
            if not os.path.isfile(wt_lf):
                findings.append({
                    "check": "lockfile",
                    "severity": SEVERITY_INFO,
                    "path": wt["path"],
                    "file": lf,
                    "message": f"Lockfile {lf} not found (present in main repo).",
                })
                continue

            try:
                wt_mtime = os.path.getmtime(wt_lf)
            except OSError:
                continue

            # Lockfile in worktree is older than main
            if wt_mtime < main_mtime:
                findings.append({
                    "check": "lockfile",
                    "severity": SEVERITY_WARNING,
                    "path": wt["path"],
                    "file": lf,
                    "message": f"{lf} is older than main repo copy. Dependencies may be out of sync.",
                })

    return findings


def run_checks(checks, worktrees, repo_root, stale_days):
    """Run the requested checks and return all findings."""
    findings = []
    dispatch = {
        "stale": lambda: check_stale(worktrees, repo_root, stale_days),
        "missing": lambda: check_missing(worktrees, repo_root),
        "branch": lambda: check_branch(worktrees, repo_root),
        "env": lambda: check_env(worktrees, repo_root),
        "ports": lambda: check_ports(worktrees, repo_root),
        "lockfile": lambda: check_lockfile(worktrees, repo_root),
    }
    for check in checks:
        if check in dispatch:
            findings.extend(dispatch[check]())
    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Validate worktree health: stale trees, missing branches, env parity, port conflicts."
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    parser.add_argument(
        "--checks", type=str, default=",".join(ALL_CHECKS),
        help=f"Comma-separated checks to run (default: {','.join(ALL_CHECKS)})"
    )
    parser.add_argument(
        "--stale-days", type=int, default=14,
        help="Stale threshold in days (default: 14)"
    )

    args = parser.parse_args()
    requested = [c.strip() for c in args.checks.split(",") if c.strip()]

    invalid = [c for c in requested if c not in ALL_CHECKS]
    if invalid:
        print(f"Error: unknown check(s): {', '.join(invalid)}", file=sys.stderr)
        print(f"Available: {', '.join(ALL_CHECKS)}", file=sys.stderr)
        sys.exit(1)

    repo_root = get_repo_root()
    worktrees = parse_worktrees(repo_root)

    findings = run_checks(requested, worktrees, repo_root, args.stale_days)

    if args.json:
        output = {
            "repo_root": repo_root,
            "worktree_count": len(worktrees),
            "checks_run": requested,
            "finding_count": len(findings),
            "errors": sum(1 for f in findings if f["severity"] == SEVERITY_ERROR),
            "warnings": sum(1 for f in findings if f["severity"] == SEVERITY_WARNING),
            "info": sum(1 for f in findings if f["severity"] == SEVERITY_INFO),
            "findings": findings,
        }
        print(json.dumps(output, indent=2))
        return

    print(f"Worktree Health Report")
    print(f"Repository: {repo_root}")
    print(f"Worktrees:  {len(worktrees)}")
    print(f"Checks:     {', '.join(requested)}")
    print("=" * 70)

    if not findings:
        print("\nAll checks passed. No issues found.")
        return

    errors = [f for f in findings if f["severity"] == SEVERITY_ERROR]
    warnings = [f for f in findings if f["severity"] == SEVERITY_WARNING]
    infos = [f for f in findings if f["severity"] == SEVERITY_INFO]

    for label, group, marker in [
        ("ERRORS", errors, "X"),
        ("WARNINGS", warnings, "!"),
        ("INFO", infos, "~"),
    ]:
        if not group:
            continue
        print(f"\n  {label} ({len(group)})")
        print(f"  {'-' * 40}")
        for f in group:
            print(f"  [{marker}] {f['message']}")
            print(f"      Path: {f['path']}")
            if "branch" in f:
                print(f"      Branch: {f['branch']}")
            print()

    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
