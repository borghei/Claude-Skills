#!/usr/bin/env python3
"""Export a bundle directory with symlinks resolved to real files.

Usage:
    python3 scripts/export_bundle.py <bundle-name> [output-dir]

The bundle directories under bundles/ use symlinks into the canonical
skill folders (engineering/, marketing/, etc.) so the single source of
truth stays in the domain directories. When submitting a bundle to an
external registry like anthropics/claude-plugins-official, the plugin
must be self-contained with real files. This script produces that
self-contained copy.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_DIR = REPO_ROOT / "bundles"

VALID_BUNDLES = [
    "engineering-skills",
    "compliance-skills",
    "c-level-skills",
    "marketing-skills",
    "product-skills",
]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Copy a skill bundle out of the repo as a standalone folder.")
    parser.add_argument("bundle", choices=VALID_BUNDLES, help="Bundle to export")
    parser.add_argument("output_dir", nargs="?", help="Destination folder (default: /tmp/<bundle>)")
    args = parser.parse_args(argv)

    name = args.bundle

    src = BUNDLES_DIR / name
    if not src.is_dir():
        print(f"error: {src} does not exist", file=sys.stderr)
        return 1

    if args.output_dir:
        dst = Path(args.output_dir).resolve()
    else:
        dst = Path(f"/tmp/{name}").resolve()

    if dst.exists():
        print(f"error: {dst} already exists. Remove it first.", file=sys.stderr)
        return 1

    shutil.copytree(src, dst, symlinks=False, ignore=_ignore)

    file_count = sum(1 for _ in dst.rglob("*") if _.is_file())
    total_bytes = sum(p.stat().st_size for p in dst.rglob("*") if p.is_file())

    print(f"Exported {name} -> {dst}")
    print(f"  files: {file_count}")
    print(f"  size:  {total_bytes / 1024:.1f} KB")
    print()
    print("Next: copy this directory into external_plugins/ of the")
    print("Anthropic plugins repo fork, then submit the PR.")
    return 0


def _ignore(dirname: str, contents: list[str]) -> list[str]:
    skip = []
    for name in contents:
        if name in {"__pycache__", ".pytest_cache", ".DS_Store", "node_modules"}:
            skip.append(name)
        elif name.endswith((".pyc", ".pyo")):
            skip.append(name)
    return skip


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
