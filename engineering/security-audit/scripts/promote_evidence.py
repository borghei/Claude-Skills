#!/usr/bin/env python3
"""Promote sandbox output into an agent's retained evidence directory.

Files a hunter or verifier produces inside agents/<id>/scratch/ stay
target-controlled even after the sandbox exits: a build or test can leave
symlinks, hard links, FIFOs, or huge files behind. This tool is the only path
from scratch/ to evidence/. It copies named files one at a time through
directory descriptors that never follow links, accepts only single-link
regular files within the byte limits, re-checks the file after reading, and
creates each destination exclusively.

Run it only after the sandbox and every process it started have exited. A
rejected file is not evidence: keep the lead as needs_validation and record
the rejection as its blocker.

Exit codes: 0 every file promoted, 1 at least one file rejected, 2 usage
error or unsupported platform.

Usage:
    python3 promote_evidence.py --run-dir ~/security-audits/app/run-1 \
        --agent-id hunter-03 --file out/result.txt --file out/trace.log
    python3 promote_evidence.py --run-dir . --agent-id verifier-07 \
        --file result.json --max-bytes 65536 --format json
"""

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import is_agent_id, is_repo_path  # noqa: E402

DIR_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
CHUNK = 64 * 1024


class Rejected(Exception):
    """Raised when a file fails a promotion check."""


def supported() -> bool:
    """Descriptor-relative, no-follow file access is required."""
    return (hasattr(os, "O_NOFOLLOW") and os.open in os.supports_dir_fd
            and os.mkdir in os.supports_dir_fd)


def open_dir(parent_fd: int, name: str, create: bool) -> int:
    """Open one directory component without following a link."""
    if create:
        try:
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
    try:
        return os.open(name, DIR_FLAGS, dir_fd=parent_fd)
    except OSError as exc:
        raise Rejected(f"directory component {name!r} is not a real directory "
                       f"({exc.strerror})") from exc


def walk(root_fd: int, parts: List[str], create: bool) -> int:
    """Descend through directory components, returning the last descriptor."""
    current = os.dup(root_fd)
    for name in parts:
        try:
            following = open_dir(current, name, create)
        finally:
            os.close(current)
        current = following
    return current


def read_checked(parent_fd: int, name: str, limit: int) -> bytes:
    """Read a single-link regular file, rejecting anything that changes."""
    flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        raise Rejected(f"cannot open without following links ({exc.strerror})") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise Rejected("not a regular file")
        if before.st_nlink != 1:
            raise Rejected("file has more than one hard link")
        if before.st_size > limit:
            raise Rejected(f"{before.st_size} bytes exceeds the limit of {limit}")
        data = bytearray()
        while len(data) <= limit:
            chunk = os.read(fd, CHUNK)
            if not chunk:
                break
            data += chunk
        after = os.fstat(fd)
        same = (before.st_ino, before.st_dev, before.st_size, before.st_mtime_ns,
                before.st_nlink) == (after.st_ino, after.st_dev, after.st_size,
                                     after.st_mtime_ns, after.st_nlink)
        if len(data) != before.st_size or not same:
            raise Rejected("file changed while it was being read")
        return bytes(data)
    finally:
        os.close(fd)


def write_exclusive(parent_fd: int, name: str, data: bytes) -> None:
    """Create the destination file; refuse to reuse an existing name."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    try:
        fd = os.open(name, flags, 0o600, dir_fd=parent_fd)
    except OSError as exc:
        raise Rejected(f"destination cannot be created exclusively ({exc.strerror})") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise Rejected("destination is not a fresh regular file")
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
    finally:
        os.close(fd)


def promote(agent_dir: Path, relative: str, limit: int) -> Dict[str, Any]:
    """Copy one scratch file into evidence/ under the same relative path."""
    parts = relative.split("/")
    root_fd = os.open(str(agent_dir), DIR_FLAGS)
    scratch_fd = evidence_fd = source_dir = dest_dir = -1
    try:
        scratch_fd = open_dir(root_fd, "scratch", create=False)
        evidence_fd = open_dir(root_fd, "evidence", create=True)
        source_dir = walk(scratch_fd, parts[:-1], create=False)
        data = read_checked(source_dir, parts[-1], limit)
        dest_dir = walk(evidence_fd, parts[:-1], create=True)
        write_exclusive(dest_dir, parts[-1], data)
    finally:
        for fd in (source_dir, dest_dir, scratch_fd, evidence_fd, root_fd):
            if fd >= 0:
                os.close(fd)
    return {"file": relative, "promoted": True, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "evidence_file": f"agents/{agent_dir.name}/evidence/{relative}"}


def run(args: argparse.Namespace) -> Dict[str, Any]:
    """Promote each requested file inside the per-file and total limits."""
    agent_dir = args.run_dir.expanduser().resolve() / "agents" / args.agent_id
    results: List[Dict[str, Any]] = []
    total = 0
    for relative in args.file:
        try:
            if not is_repo_path(relative):
                raise Rejected("path must be relative, with no '..', '.', or "
                               "empty components")
            remaining = args.max_total_bytes - total
            if remaining <= 0:
                raise Rejected("cumulative byte limit already reached")
            outcome = promote(agent_dir, relative, min(args.max_bytes, remaining))
            total += outcome["bytes"]
        except (Rejected, OSError) as exc:
            outcome = {"file": relative, "promoted": False, "reason": str(exc)}
        results.append(outcome)
    return {"agent_id": args.agent_id, "total_bytes": total, "results": results,
            "all_promoted": all(item["promoted"] for item in results)}


def main() -> None:
    """Parse arguments, promote the files, and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Safely copy named files from an agent's scratch/ to its "
                    "evidence/ directory.")
    parser.add_argument("--run-dir", type=Path, required=True, help="audit run directory")
    parser.add_argument("--agent-id", required=True, help="owner of the scratch directory")
    parser.add_argument("--file", action="append", required=True, metavar="REL",
                        help="scratch-relative file to promote (repeatable); "
                             "name files explicitly, never a directory or glob")
    parser.add_argument("--max-bytes", type=int, default=1024 * 1024,
                        help="per-file byte limit (default: 1 MiB)")
    parser.add_argument("--max-total-bytes", type=int, default=8 * 1024 * 1024,
                        help="cumulative byte limit for this call (default: 8 MiB)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args()
    if not is_agent_id(args.agent_id):
        print("ERROR: --agent-id must match ^[a-z0-9][a-z0-9_-]{0,63}$",
              file=sys.stderr)
        sys.exit(2)
    if not supported():
        print("ERROR: this platform lacks no-follow descriptor-relative file "
              "access; treat sandbox output as unavailable evidence",
              file=sys.stderr)
        sys.exit(2)
    report = run(args)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for item in report["results"]:
            if item["promoted"]:
                print(f"PROMOTED {item['evidence_file']} "
                      f"({item['bytes']} bytes, sha256 {item['sha256'][:16]})")
            else:
                print(f"REJECTED {item['file']}: {item['reason']}")
    sys.exit(0 if report["all_promoted"] else 1)


if __name__ == "__main__":
    main()
