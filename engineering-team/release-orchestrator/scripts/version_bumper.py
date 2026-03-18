#!/usr/bin/env python3
"""
Semantic Version Bumper for Release Orchestration.

Reads current version from multiple sources, auto-determines bump level
from conventional commits, and updates version across all discovered files.

Supported version sources:
- package.json
- pyproject.toml
- setup.py / setup.cfg
- Cargo.toml
- VERSION file

Usage:
    python version_bumper.py --repo . --dry-run
    python version_bumper.py --repo . --bump minor
    python version_bumper.py --repo . --bump major --pre rc
    python version_bumper.py --repo . --json
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# SemVer
# ---------------------------------------------------------------------------

SEMVER_RE = re.compile(
    r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<pre>[0-9A-Za-z\-.]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z\-.]+))?"
)

CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\([^)]+\))?"
    r"(?P<breaking>!)?"
    r":\s+"
)

BREAKING_CHANGE_FOOTER_RE = re.compile(r"^BREAKING[ -]CHANGE:", re.MULTILINE)


@dataclass
class SemVer:
    """Semantic version representation."""
    major: int
    minor: int
    patch: int
    pre: Optional[str] = None
    build: Optional[str] = None

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre:
            version += f"-{self.pre}"
        if self.build:
            version += f"+{self.build}"
        return version

    @classmethod
    def parse(cls, version_str: str) -> Optional["SemVer"]:
        match = SEMVER_RE.search(version_str)
        if not match:
            return None
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            pre=match.group("pre"),
            build=match.group("build"),
        )

    def bump_major(self) -> "SemVer":
        return SemVer(self.major + 1, 0, 0)

    def bump_minor(self) -> "SemVer":
        return SemVer(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "SemVer":
        return SemVer(self.major, self.minor, self.patch + 1)

    def with_pre(self, pre_tag: str, pre_number: int = 1) -> "SemVer":
        return SemVer(self.major, self.minor, self.patch, pre=f"{pre_tag}.{pre_number}")

    def increment_pre(self) -> "SemVer":
        """Increment pre-release number."""
        if not self.pre:
            return self
        parts = self.pre.rsplit(".", 1)
        if len(parts) == 2:
            try:
                num = int(parts[1])
                return SemVer(self.major, self.minor, self.patch, pre=f"{parts[0]}.{num + 1}")
            except ValueError:
                pass
        return SemVer(self.major, self.minor, self.patch, pre=f"{self.pre}.1")


@dataclass
class VersionSource:
    """A file that contains a version string."""
    filepath: str
    current_version: str
    line_number: int
    pattern: str  # For display


@dataclass
class BumpResult:
    """Result of a version bump operation."""
    current: str
    next: str
    bump_type: str
    sources_found: List[VersionSource]
    sources_updated: List[str]
    dry_run: bool
    auto_detected: bool
    commit_analysis: Dict[str, int]

    def to_dict(self) -> Dict:
        return {
            "current_version": self.current,
            "next_version": self.next,
            "bump_type": self.bump_type,
            "dry_run": self.dry_run,
            "auto_detected": self.auto_detected,
            "commit_analysis": self.commit_analysis,
            "sources": [
                {"file": s.filepath, "version": s.current_version, "line": s.line_number}
                for s in self.sources_found
            ],
            "updated_files": self.sources_updated,
        }


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def run_git(args: List[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True
    )


def get_latest_tag(repo: str) -> Optional[str]:
    result = run_git(["describe", "--tags", "--abbrev=0"], cwd=repo)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def get_commits_since_tag(repo: str, tag: Optional[str]) -> List[Tuple[str, str]]:
    """Return (subject, body) tuples for commits since tag."""
    if tag:
        args = ["log", f"{tag}..HEAD", "--pretty=format:%s|||%b---END---"]
    else:
        args = ["log", "--pretty=format:%s|||%b---END---"]

    result = run_git(args, cwd=repo)
    if result.returncode != 0:
        return []

    commits = []
    for block in result.stdout.split("---END---"):
        block = block.strip()
        if not block:
            continue
        parts = block.split("|||", 1)
        subject = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""
        commits.append((subject, body))
    return commits


def detect_bump_from_commits(repo: str) -> Tuple[str, Dict[str, int]]:
    """Analyze commits since last tag to determine bump level."""
    tag = get_latest_tag(repo)
    commits = get_commits_since_tag(repo, tag)

    analysis = {
        "total": len(commits),
        "feat": 0,
        "fix": 0,
        "breaking": 0,
        "docs": 0,
        "chore": 0,
        "refactor": 0,
        "perf": 0,
        "test": 0,
        "other": 0,
    }

    has_breaking = False
    has_feat = False
    has_fix = False

    for subject, body in commits:
        match = CONVENTIONAL_COMMIT_RE.match(subject)
        if match:
            commit_type = match.group("type")
            is_breaking = match.group("breaking") is not None

            if commit_type in analysis:
                analysis[commit_type] += 1
            else:
                analysis["other"] += 1

            if is_breaking:
                has_breaking = True
                analysis["breaking"] += 1
            if commit_type == "feat":
                has_feat = True
            if commit_type == "fix":
                has_fix = True
        else:
            analysis["other"] += 1

        # Check body for BREAKING CHANGE footer
        if BREAKING_CHANGE_FOOTER_RE.search(body):
            has_breaking = True
            analysis["breaking"] += 1

    if has_breaking:
        return "major", analysis
    elif has_feat:
        return "minor", analysis
    elif has_fix:
        return "patch", analysis
    else:
        return "patch", analysis


# ---------------------------------------------------------------------------
# Version source discovery
# ---------------------------------------------------------------------------

def find_version_sources(repo: str) -> List[VersionSource]:
    """Discover all files containing version strings."""
    sources: List[VersionSource] = []

    # package.json
    pkg_json = os.path.join(repo, "package.json")
    if os.path.isfile(pkg_json):
        try:
            with open(pkg_json, "r") as f:
                data = json.load(f)
            if "version" in data:
                # Find line number
                with open(pkg_json, "r") as f:
                    for i, line in enumerate(f, 1):
                        if '"version"' in line:
                            sources.append(VersionSource(
                                filepath=pkg_json,
                                current_version=data["version"],
                                line_number=i,
                                pattern="package.json",
                            ))
                            break
        except (json.JSONDecodeError, OSError):
            pass

    # pyproject.toml
    pyproject = os.path.join(repo, "pyproject.toml")
    if os.path.isfile(pyproject):
        try:
            with open(pyproject, "r") as f:
                for i, line in enumerate(f, 1):
                    # Match version = "x.y.z" in [project] or [tool.poetry] section
                    match = re.match(r'^version\s*=\s*["\'](.+?)["\']', line)
                    if match:
                        sources.append(VersionSource(
                            filepath=pyproject,
                            current_version=match.group(1),
                            line_number=i,
                            pattern="pyproject.toml",
                        ))
                        break
        except OSError:
            pass

    # setup.py
    setup_py = os.path.join(repo, "setup.py")
    if os.path.isfile(setup_py):
        try:
            with open(setup_py, "r") as f:
                content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                # Find line number
                line_num = content[:match.start()].count("\n") + 1
                sources.append(VersionSource(
                    filepath=setup_py,
                    current_version=match.group(1),
                    line_number=line_num,
                    pattern="setup.py",
                ))
        except OSError:
            pass

    # setup.cfg
    setup_cfg = os.path.join(repo, "setup.cfg")
    if os.path.isfile(setup_cfg):
        try:
            with open(setup_cfg, "r") as f:
                for i, line in enumerate(f, 1):
                    match = re.match(r'^version\s*=\s*(.+)', line)
                    if match:
                        sources.append(VersionSource(
                            filepath=setup_cfg,
                            current_version=match.group(1).strip(),
                            line_number=i,
                            pattern="setup.cfg",
                        ))
                        break
        except OSError:
            pass

    # Cargo.toml
    cargo_toml = os.path.join(repo, "Cargo.toml")
    if os.path.isfile(cargo_toml):
        try:
            in_package = False
            with open(cargo_toml, "r") as f:
                for i, line in enumerate(f, 1):
                    if line.strip() == "[package]":
                        in_package = True
                        continue
                    if line.strip().startswith("[") and in_package:
                        break
                    if in_package:
                        match = re.match(r'^version\s*=\s*"(.+?)"', line)
                        if match:
                            sources.append(VersionSource(
                                filepath=cargo_toml,
                                current_version=match.group(1),
                                line_number=i,
                                pattern="Cargo.toml",
                            ))
                            break
        except OSError:
            pass

    # VERSION file
    version_file = os.path.join(repo, "VERSION")
    if os.path.isfile(version_file):
        try:
            with open(version_file, "r") as f:
                ver = f.read().strip()
            if SEMVER_RE.match(ver):
                sources.append(VersionSource(
                    filepath=version_file,
                    current_version=ver,
                    line_number=1,
                    pattern="VERSION",
                ))
        except OSError:
            pass

    return sources


def update_version_in_file(filepath: str, old_version: str, new_version: str) -> bool:
    """Replace old_version with new_version in the given file."""
    try:
        with open(filepath, "r") as f:
            content = f.read()

        if old_version not in content:
            return False

        # For JSON files, be more precise
        if filepath.endswith(".json"):
            # Replace only in "version": "x.y.z" pattern
            pattern = f'"version"\\s*:\\s*"{re.escape(old_version)}"'
            replacement = f'"version": "{new_version}"'
            new_content, count = re.subn(pattern, replacement, content)
            if count == 0:
                return False
            content = new_content
        else:
            content = content.replace(old_version, new_version, 1)

        with open(filepath, "w") as f:
            f.write(content)
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def bump_version(
    repo: str,
    bump_type: Optional[str] = None,
    pre_tag: Optional[str] = None,
    dry_run: bool = False,
) -> BumpResult:
    """Execute the version bump."""
    sources = find_version_sources(repo)

    if not sources:
        # Try to get version from git tag
        tag = get_latest_tag(repo)
        if tag:
            ver = tag.lstrip("v")
            sources = [VersionSource(
                filepath="(git tag)",
                current_version=ver,
                line_number=0,
                pattern="git tag",
            )]

    if not sources:
        return BumpResult(
            current="0.0.0",
            next="0.1.0",
            bump_type=bump_type or "minor",
            sources_found=[],
            sources_updated=[],
            dry_run=dry_run,
            auto_detected=False,
            commit_analysis={},
        )

    # Use first source as canonical version
    current_version_str = sources[0].current_version
    current = SemVer.parse(current_version_str)
    if current is None:
        print(f"Error: Could not parse version '{current_version_str}'", file=sys.stderr)
        sys.exit(1)

    # Auto-detect bump type from commits if not specified
    auto_detected = bump_type is None
    commit_analysis: Dict[str, int] = {}
    if bump_type is None:
        bump_type, commit_analysis = detect_bump_from_commits(repo)
    else:
        _, commit_analysis = detect_bump_from_commits(repo)

    # Calculate next version
    if bump_type == "major":
        next_ver = current.bump_major()
    elif bump_type == "minor":
        next_ver = current.bump_minor()
    else:
        next_ver = current.bump_patch()

    # Apply pre-release tag
    if pre_tag:
        # Check if current is already a pre-release of the same base version
        if (current.pre and current.pre.startswith(pre_tag)
                and current.major == next_ver.major
                and current.minor == next_ver.minor
                and current.patch == next_ver.patch):
            next_ver = current.increment_pre()
        else:
            next_ver = next_ver.with_pre(pre_tag)

    # Update files
    updated_files: List[str] = []
    if not dry_run:
        for source in sources:
            if source.filepath == "(git tag)":
                continue
            if update_version_in_file(source.filepath, source.current_version, str(next_ver)):
                updated_files.append(source.filepath)

    return BumpResult(
        current=str(current),
        next=str(next_ver),
        bump_type=bump_type,
        sources_found=sources,
        sources_updated=updated_files,
        dry_run=dry_run,
        auto_detected=auto_detected,
        commit_analysis=commit_analysis,
    )


def render_text(result: BumpResult) -> str:
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("  SEMANTIC VERSION BUMP")
    lines.append("=" * 60)

    if result.dry_run:
        lines.append("  Mode: DRY RUN (no files modified)")
    else:
        lines.append("  Mode: LIVE")

    lines.append("")
    lines.append(f"  Current Version: {result.current}")
    lines.append(f"  Next Version:    {result.next}")
    lines.append(f"  Bump Type:       {result.bump_type.upper()}")
    lines.append(f"  Auto-Detected:   {'Yes' if result.auto_detected else 'No'}")
    lines.append("")

    if result.commit_analysis:
        lines.append("  Commit Analysis:")
        for key, count in sorted(result.commit_analysis.items()):
            if count > 0:
                lines.append(f"    {key:12s}: {count}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("  Version Sources Found:")
    for source in result.sources_found:
        lines.append(f"    {source.pattern:20s} {source.filepath}")
        lines.append(f"    {'':20s} version={source.current_version} (line {source.line_number})")
    lines.append("")

    if not result.dry_run and result.sources_updated:
        lines.append("  Files Updated:")
        for f in result.sources_updated:
            lines.append(f"    - {f}")
    elif result.dry_run:
        lines.append("  Files that would be updated:")
        for source in result.sources_found:
            if source.filepath != "(git tag)":
                lines.append(f"    - {source.filepath}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Semantic version bumper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo . --dry-run
  %(prog)s --repo . --bump minor
  %(prog)s --repo . --bump major --pre rc
  %(prog)s --repo . --json
        """,
    )
    parser.add_argument("--repo", default=".", help="Path to repository")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump type (auto-detected if omitted)")
    parser.add_argument("--pre", help="Pre-release tag (alpha, beta, rc)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying files")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()
    repo = os.path.abspath(args.repo)

    if not os.path.isdir(repo):
        print(f"Error: {repo} is not a directory", file=sys.stderr)
        sys.exit(2)

    result = bump_version(
        repo=repo,
        bump_type=args.bump,
        pre_tag=args.pre,
        dry_run=args.dry_run,
    )

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(render_text(result))


if __name__ == "__main__":
    main()
