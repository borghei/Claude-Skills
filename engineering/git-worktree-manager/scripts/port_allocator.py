#!/usr/bin/env python3
"""
port_allocator.py - Manage port allocation across git worktrees.

Assigns deterministic port blocks to worktrees, detects conflicts with
running processes, and maintains a central port registry to prevent collisions.

Usage:
    python port_allocator.py status
    python port_allocator.py assign wt-auth --index 1
    python port_allocator.py release wt-auth
    python port_allocator.py check --port 3010
    python port_allocator.py status --json
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_BASE_PORTS = {
    "app": 3000,
    "database": 5432,
    "redis": 6379,
    "api": 8000,
}
DEFAULT_STRIDE = 10
REGISTRY_FILE = ".worktree-ports-registry.json"


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


def registry_path(repo_root):
    """Path to the central port registry file."""
    return os.path.join(repo_root, REGISTRY_FILE)


def load_registry(repo_root):
    """Load the port registry from disk."""
    path = registry_path(repo_root)
    if not os.path.isfile(path):
        return {"version": 1, "stride": DEFAULT_STRIDE, "base_ports": DEFAULT_BASE_PORTS, "allocations": {}}
    try:
        with open(path, "r") as f:
            data = json.load(f)
        # Ensure required keys
        data.setdefault("version", 1)
        data.setdefault("stride", DEFAULT_STRIDE)
        data.setdefault("base_ports", DEFAULT_BASE_PORTS)
        data.setdefault("allocations", {})
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: could not read registry ({e}), starting fresh.", file=sys.stderr)
        return {"version": 1, "stride": DEFAULT_STRIDE, "base_ports": DEFAULT_BASE_PORTS, "allocations": {}}


def save_registry(repo_root, registry):
    """Persist the port registry to disk."""
    path = registry_path(repo_root)
    try:
        with open(path, "w") as f:
            json.dump(registry, f, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"Error: could not write registry: {e}", file=sys.stderr)
        sys.exit(1)


def is_port_in_use(port):
    """Check if a TCP port is currently in use by attempting to bind."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            return result == 0
    except OSError:
        return False


def compute_ports(index, base_ports, stride):
    """Compute the port block for a given worktree index."""
    return {
        service: base + (index * stride)
        for service, base in base_ports.items()
    }


def find_next_index(registry):
    """Find the lowest available index not in use."""
    used_indices = set()
    for alloc in registry["allocations"].values():
        used_indices.add(alloc.get("index", 0))
    idx = 0
    while idx in used_indices:
        idx += 1
    return idx


def get_active_worktrees(repo_root):
    """Get set of worktree directory names from git."""
    raw = run_git(["worktree", "list", "--porcelain"], cwd=repo_root)
    if not raw:
        return set()
    names = set()
    for line in raw.splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree "):]
            names.add(os.path.basename(path))
    return names


def cmd_status(args):
    """Show current port allocations and their status."""
    repo_root = get_repo_root()
    registry = load_registry(repo_root)
    allocations = registry["allocations"]
    active_wts = get_active_worktrees(repo_root)

    entries = []
    for name, alloc in sorted(allocations.items()):
        ports = alloc.get("ports", {})
        port_status = {}
        for service, port in ports.items():
            port_status[service] = {
                "port": port,
                "in_use": is_port_in_use(port),
            }
        entries.append({
            "worktree": name,
            "index": alloc.get("index", "?"),
            "branch": alloc.get("branch", "?"),
            "ports": port_status,
            "active": name in active_wts or os.path.basename(repo_root) == name,
            "created": alloc.get("created", "?"),
        })

    if args.json:
        output = {
            "repo_root": repo_root,
            "stride": registry["stride"],
            "base_ports": registry["base_ports"],
            "allocation_count": len(entries),
            "allocations": entries,
        }
        print(json.dumps(output, indent=2))
        return

    print(f"Port Allocation Status")
    print(f"Repository: {repo_root}")
    print(f"Stride: {registry['stride']}  |  Base ports: {', '.join(f'{s}={p}' for s, p in registry['base_ports'].items())}")
    print("=" * 90)

    if not entries:
        print("\nNo port allocations registered.")
        print("Use 'assign <worktree-name>' to allocate ports.")
        return

    print(f"\n{'Worktree':<25} {'Idx':<5} {'Branch':<25} {'Ports':<30} {'Status'}")
    print("-" * 90)

    for e in entries:
        ports_str = ", ".join(
            f"{s}:{p['port']}" for s, p in e["ports"].items()
        )
        busy = [s for s, p in e["ports"].items() if p["in_use"]]
        if not e["active"]:
            status = "ORPHANED"
        elif busy:
            status = f"BUSY({','.join(busy)})"
        else:
            status = "free"

        wt_display = e["worktree"] if len(e["worktree"]) <= 24 else e["worktree"][:21] + "..."
        br_display = e["branch"] if len(e["branch"]) <= 24 else e["branch"][:21] + "..."
        print(f"{wt_display:<25} {e['index']:<5} {br_display:<25} {ports_str:<30} {status}")

    total_ports = sum(len(e["ports"]) for e in entries)
    busy_total = sum(1 for e in entries for p in e["ports"].values() if p["in_use"])
    orphaned = sum(1 for e in entries if not e["active"])
    print(f"\nTotal: {len(entries)} allocation(s), {total_ports} port(s), {busy_total} in use, {orphaned} orphaned")


def cmd_assign(args):
    """Assign a port block to a worktree."""
    repo_root = get_repo_root()
    registry = load_registry(repo_root)
    name = args.name

    if name in registry["allocations"]:
        existing = registry["allocations"][name]
        if args.json:
            print(json.dumps({"error": f"'{name}' already allocated", "existing": existing}))
        else:
            print(f"Error: '{name}' already has an allocation (index {existing.get('index')}).", file=sys.stderr)
            print("Use 'release' first, then re-assign.", file=sys.stderr)
        sys.exit(1)

    index = args.index if args.index is not None else find_next_index(registry)
    base_ports = registry["base_ports"]
    stride = registry["stride"]
    ports = compute_ports(index, base_ports, stride)

    # Check for index collision
    for existing_name, alloc in registry["allocations"].items():
        if alloc.get("index") == index:
            msg = f"Index {index} is already assigned to '{existing_name}'."
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"Error: {msg}", file=sys.stderr)
            sys.exit(1)

    # Check for port conflicts with running processes
    conflicts = []
    for service, port in ports.items():
        if is_port_in_use(port):
            conflicts.append({"service": service, "port": port})

    allocation = {
        "index": index,
        "branch": args.branch or "",
        "ports": ports,
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    registry["allocations"][name] = allocation
    save_registry(repo_root, registry)

    # Also write per-worktree port file if worktree exists
    parent_dir = Path(repo_root).parent
    wt_path = parent_dir / name
    if wt_path.is_dir():
        wt_port_file = wt_path / ".worktree-ports.json"
        try:
            with open(wt_port_file, "w") as f:
                json.dump({
                    "worktree": name,
                    "branch": args.branch or "",
                    "index": index,
                    "ports": ports,
                    "created": allocation["created"],
                }, f, indent=2)
                f.write("\n")
        except OSError:
            pass  # Non-fatal: registry is the source of truth

    if args.json:
        output = {
            "action": "assigned",
            "worktree": name,
            "index": index,
            "ports": ports,
            "conflicts": conflicts,
        }
        print(json.dumps(output, indent=2))
        return

    print(f"Port block assigned to '{name}' (index {index}):\n")
    for service, port in sorted(ports.items()):
        busy = " (IN USE)" if any(c["port"] == port for c in conflicts) else ""
        print(f"  {service:<12} {port}{busy}")

    if conflicts:
        print(f"\nWarning: {len(conflicts)} port(s) currently in use by other processes.")

    print(f"\nRegistry saved to {registry_path(repo_root)}")


def cmd_release(args):
    """Release a port allocation for a worktree."""
    repo_root = get_repo_root()
    registry = load_registry(repo_root)
    name = args.name

    if name not in registry["allocations"]:
        msg = f"No allocation found for '{name}'."
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    released = registry["allocations"].pop(name)
    save_registry(repo_root, registry)

    if args.json:
        print(json.dumps({"action": "released", "worktree": name, "released": released}))
    else:
        print(f"Released port allocation for '{name}' (index {released.get('index')}).")
        print(f"Freed ports: {', '.join(f'{s}={p}' for s, p in released.get('ports', {}).items())}")


def cmd_check(args):
    """Check if specific ports are available."""
    ports_to_check = [int(p.strip()) for p in args.port.split(",")]
    repo_root = get_repo_root()
    registry = load_registry(repo_root)

    # Build reverse map: port -> (worktree, service)
    port_owners = {}
    for name, alloc in registry["allocations"].items():
        for service, port in alloc.get("ports", {}).items():
            port_owners[port] = {"worktree": name, "service": service}

    results = []
    for port in ports_to_check:
        in_use = is_port_in_use(port)
        owner = port_owners.get(port)
        results.append({
            "port": port,
            "in_use": in_use,
            "allocated_to": owner,
            "available": not in_use and owner is None,
        })

    if args.json:
        print(json.dumps({"ports": results}, indent=2))
        return

    print(f"{'Port':<8} {'Process':<12} {'Allocated To':<30} {'Available'}")
    print("-" * 60)
    for r in results:
        proc = "BUSY" if r["in_use"] else "free"
        owner = ""
        if r["allocated_to"]:
            owner = f"{r['allocated_to']['worktree']} ({r['allocated_to']['service']})"
        avail = "yes" if r["available"] else "NO"
        print(f"{r['port']:<8} {proc:<12} {owner:<30} {avail}")


def cmd_sync(args):
    """Sync registry with actual git worktrees, removing orphaned entries."""
    repo_root = get_repo_root()
    registry = load_registry(repo_root)
    active_wts = get_active_worktrees(repo_root)

    orphaned = []
    for name in list(registry["allocations"].keys()):
        if name not in active_wts and os.path.basename(repo_root) != name:
            orphaned.append(name)

    if not orphaned:
        if args.json:
            print(json.dumps({"action": "sync", "removed": [], "message": "Registry is in sync."}))
        else:
            print("Registry is in sync with active worktrees. Nothing to clean.")
        return

    if args.dry_run:
        if args.json:
            print(json.dumps({"action": "sync_preview", "orphaned": orphaned}))
        else:
            print(f"Orphaned allocations ({len(orphaned)}):")
            for name in orphaned:
                idx = registry["allocations"][name].get("index", "?")
                print(f"  {name} (index {idx})")
            print("\nRe-run without --dry-run to remove these entries.")
        return

    removed = []
    for name in orphaned:
        registry["allocations"].pop(name)
        removed.append(name)

    save_registry(repo_root, registry)

    if args.json:
        print(json.dumps({"action": "sync", "removed": removed}))
    else:
        print(f"Removed {len(removed)} orphaned allocation(s):")
        for name in removed:
            print(f"  {name}")
        print(f"\nRegistry saved to {registry_path(repo_root)}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage port allocation across git worktrees to prevent conflicts."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    sp_status = subparsers.add_parser("status", help="Show all port allocations and their status")
    sp_status.add_argument("--json", action="store_true", help="Output in JSON format")

    # assign
    sp_assign = subparsers.add_parser("assign", help="Assign a port block to a worktree")
    sp_assign.add_argument("name", help="Worktree name (e.g., wt-auth)")
    sp_assign.add_argument("--index", type=int, default=None, help="Worktree index (auto-assigned if omitted)")
    sp_assign.add_argument("--branch", type=str, default="", help="Branch name for metadata")
    sp_assign.add_argument("--json", action="store_true", help="Output in JSON format")

    # release
    sp_release = subparsers.add_parser("release", help="Release a port allocation")
    sp_release.add_argument("name", help="Worktree name to release")
    sp_release.add_argument("--json", action="store_true", help="Output in JSON format")

    # check
    sp_check = subparsers.add_parser("check", help="Check if ports are available")
    sp_check.add_argument("--port", required=True, help="Comma-separated port(s) to check")
    sp_check.add_argument("--json", action="store_true", help="Output in JSON format")

    # sync
    sp_sync = subparsers.add_parser("sync", help="Sync registry with active worktrees")
    sp_sync.add_argument("--dry-run", action="store_true", help="Preview without removing")
    sp_sync.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "status": cmd_status,
        "assign": cmd_assign,
        "release": cmd_release,
        "check": cmd_check,
        "sync": cmd_sync,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
