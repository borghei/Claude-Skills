#!/usr/bin/env python3
"""diff_scope_check.py - Check that a bugfix diff stayed focused.

Reads a unified diff (`git diff`, `git diff --cached`, `git show`, or a .patch
file) and reports what makes a bugfix hard to review or risky to roll back:

  - more files or changed lines than the stated budget
  - files outside the expected scope (--allow globs)
  - hunks that only change whitespace or formatting
  - dependency manifests or lockfiles changed in the same diff
  - no test file touched (a fix should ship a regression test)

Usage:
    git diff main...HEAD > fix.diff
    python3 diff_scope_check.py --diff fix.diff --allow 'src/auth/*' --max-files 3
    git diff | python3 diff_scope_check.py --diff - --format json

Exit codes: 0 diff is focused, 1 scope findings, 2 bad input (missing file,
not a unified diff).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

DEPENDENCY_FILES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "requirements.txt",
    "poetry.lock", "pyproject.toml", "Pipfile.lock", "go.mod", "go.sum", "Cargo.toml",
    "Cargo.lock", "Gemfile", "Gemfile.lock", "composer.json", "composer.lock",
}
TEST_PATTERN = re.compile(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec|_spec)\.\w+$|(^|/)test_[^/]+$")


@dataclass
class FileChange:
    path: str
    added: int = 0
    removed: int = 0
    whitespace_only_hunks: int = 0
    hunks: int = 0


@dataclass
class Report:
    files: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    total_added: int = 0
    total_removed: int = 0
    test_files: list = field(default_factory=list)


def parse_diff(text: str) -> list[FileChange]:
    """Parse a unified diff into per-file line counts and hunk details."""
    files: list[FileChange] = []
    current: FileChange | None = None
    minus: list[str] = []
    plus: list[str] = []

    def close_hunk():
        if current is not None and (minus or plus):
            current.hunks += 1
            if minus and plus and [re.sub(r"\s+", "", l) for l in minus] == [re.sub(r"\s+", "", l) for l in plus]:
                current.whitespace_only_hunks += 1
        minus.clear()
        plus.clear()

    old_path = ""
    for line in text.splitlines():
        if line.startswith("diff --git "):
            continue
        if line.startswith("--- "):
            old_path = line[4:].strip().split("\t")[0].removeprefix("a/")
            continue
        if line.startswith("+++ "):
            path = line[4:].strip().split("\t")[0].removeprefix("b/")
            if path == "/dev/null":  # deleted file: report it under its old name
                path = old_path
            close_hunk()
            current = FileChange(path=path)
            files.append(current)
            continue
        if line.startswith("@@"):
            close_hunk()
            continue
        if current is None:
            continue
        if line.startswith("+"):
            current.added += 1
            plus.append(line[1:])
        elif line.startswith("-"):
            current.removed += 1
            minus.append(line[1:])
        else:  # context line ends a change block
            close_hunk()
    close_hunk()
    return files


def check(files: list[FileChange], allow: list[str], max_files: int, max_lines: int,
          require_test: bool) -> Report:
    rep = Report(files=[asdict(f) for f in files])
    rep.total_added = sum(f.added for f in files)
    rep.total_removed = sum(f.removed for f in files)
    rep.test_files = [f.path for f in files if TEST_PATTERN.search(f.path)]
    source = [f for f in files if f.path not in rep.test_files]

    if len(source) > max_files:
        rep.findings.append(f"{len(source)} non-test files changed (budget {max_files}): "
                            + ", ".join(f.path for f in source))
    changed = sum(f.added + f.removed for f in source)
    if changed > max_lines:
        rep.findings.append(f"{changed} non-test lines changed (budget {max_lines})")
    if allow:
        outside = [f.path for f in source if not any(fnmatch.fnmatch(f.path, g) for g in allow)]
        if outside:
            rep.findings.append("outside the expected scope: " + ", ".join(outside))
    for f in files:
        if f.whitespace_only_hunks:
            rep.findings.append(f"{f.path}: {f.whitespace_only_hunks} whitespace/formatting-only hunk(s)")
    deps = [f.path for f in files if Path(f.path).name in DEPENDENCY_FILES]
    if deps and any(Path(f.path).name not in DEPENDENCY_FILES for f in source):
        rep.findings.append("dependency change bundled with code change: " + ", ".join(deps))
    if require_test and not rep.test_files:
        rep.findings.append("no test file changed: add a regression test that fails before the fix")
    return rep


def render_text(rep: Report) -> str:
    out = ["DIFF SCOPE CHECK", "=" * 40]
    for f in rep.files:
        out.append(f"  {f['path']}: +{f['added']} -{f['removed']}")
    out.append(f"Total: +{rep.total_added} -{rep.total_removed}; tests touched: {len(rep.test_files)}")
    if rep.findings:
        out.append("")
        out.append(f"FINDINGS ({len(rep.findings)}):")
        out += [f"  - {x}" for x in rep.findings]
    else:
        out.append("Focused: within budget, in scope, with a test, no formatting noise.")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description="Check that a bugfix diff stayed focused.",
                                epilog=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--diff", required=True, help="Unified diff file, or '-' for stdin")
    p.add_argument("--allow", nargs="*", default=[], help="Glob(s) of files the fix is expected to touch")
    p.add_argument("--max-files", type=int, default=3, help="Non-test file budget (default 3)")
    p.add_argument("--max-lines", type=int, default=60, help="Non-test changed-line budget (default 60)")
    p.add_argument("--no-test-required", action="store_true", help="Do not require a test file change")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    try:
        text = sys.stdin.read() if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read diff: {exc}", file=sys.stderr)
        return 2
    files = parse_diff(text)
    if not files:
        print("error: no file changes found; pass a unified diff (git diff output)", file=sys.stderr)
        return 2

    rep = check(files, args.allow, args.max_files, args.max_lines, not args.no_test_required)
    print(json.dumps(asdict(rep), indent=2) if args.format == "json" else render_text(rep))
    return 1 if rep.findings else 0


if __name__ == "__main__":
    sys.exit(main())
