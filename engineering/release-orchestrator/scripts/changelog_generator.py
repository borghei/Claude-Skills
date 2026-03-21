#!/usr/bin/env python3
"""
Changelog Generator for Release Orchestration.

Parses git log for conventional commits, groups by type, detects breaking
changes, and generates Keep a Changelog formatted output.

Usage:
    python changelog_generator.py --repo . --from v1.0.0 --to HEAD
    python changelog_generator.py --repo . --from latest --to HEAD
    python changelog_generator.py --repo . --since 2026-01-01 --until 2026-03-18
    python changelog_generator.py --repo . --from v1.0.0 --to v1.1.0 --output CHANGELOG.md
    python changelog_generator.py --repo . --from v1.0.0 --to HEAD --json
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Conventional commit parsing
# ---------------------------------------------------------------------------

CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?"
    r":\s+"
    r"(?P<description>.+)"
)

BREAKING_CHANGE_FOOTER_RE = re.compile(
    r"^BREAKING[ -]CHANGE:\s*(?P<description>.+)", re.MULTILINE
)

# Map conventional commit types to Keep a Changelog sections
TYPE_TO_SECTION: Dict[str, str] = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": "Documentation",
    "style": "Changed",
    "refactor": "Changed",
    "perf": "Performance",
    "test": "Testing",
    "build": "Build",
    "ci": "CI/CD",
    "chore": "Maintenance",
    "revert": "Reverted",
}

# Primary sections in display order
SECTION_ORDER = [
    "Breaking Changes",
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Security",
    "Performance",
    "Documentation",
    "Testing",
    "Build",
    "CI/CD",
    "Maintenance",
    "Reverted",
    "Other",
]


@dataclass
class CommitEntry:
    """Parsed conventional commit."""
    hash: str
    short_hash: str
    type: str
    scope: Optional[str]
    description: str
    body: str
    author: str
    author_email: str
    date: str
    is_breaking: bool
    breaking_description: Optional[str]
    raw_subject: str

    @property
    def section(self) -> str:
        return TYPE_TO_SECTION.get(self.type, "Other")

    @property
    def scope_prefix(self) -> str:
        if self.scope:
            return f"**{self.scope}:** "
        return ""

    def to_dict(self) -> Dict:
        return {
            "hash": self.hash,
            "short_hash": self.short_hash,
            "type": self.type,
            "scope": self.scope,
            "description": self.description,
            "author": self.author,
            "date": self.date,
            "is_breaking": self.is_breaking,
            "breaking_description": self.breaking_description,
        }


@dataclass
class ChangelogRelease:
    """A single release entry in the changelog."""
    version: Optional[str]
    date: str
    entries: List[CommitEntry] = field(default_factory=list)
    sections: Dict[str, List[CommitEntry]] = field(default_factory=lambda: defaultdict(list))
    breaking_changes: List[CommitEntry] = field(default_factory=list)

    def add_entry(self, entry: CommitEntry) -> None:
        self.entries.append(entry)
        self.sections[entry.section].append(entry)
        if entry.is_breaking:
            self.breaking_changes.append(entry)

    @property
    def contributors(self) -> List[str]:
        seen = set()
        result = []
        for e in self.entries:
            if e.author not in seen:
                seen.add(e.author)
                result.append(e.author)
        return result

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "date": self.date,
            "total_commits": len(self.entries),
            "breaking_changes": len(self.breaking_changes),
            "contributors": self.contributors,
            "sections": {
                section: [e.to_dict() for e in entries]
                for section, entries in self.sections.items()
            },
        }


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def run_git(args: List[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True
    )


def get_latest_tag(repo: str) -> Optional[str]:
    """Return the most recent tag or None."""
    result = run_git(["describe", "--tags", "--abbrev=0"], cwd=repo)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def get_all_tags(repo: str) -> List[str]:
    """Return list of tags sorted by date (newest first)."""
    result = run_git(
        ["tag", "--sort=-creatordate", "--format=%(refname:short)"],
        cwd=repo,
    )
    if result.returncode != 0:
        return []
    return [t for t in result.stdout.strip().split("\n") if t]


def resolve_ref(repo: str, ref: str) -> Optional[str]:
    """Resolve a ref to its full hash."""
    if ref == "latest":
        tag = get_latest_tag(repo)
        if tag is None:
            return None
        ref = tag
    result = run_git(["rev-parse", ref], cwd=repo)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def get_version_from_tag(tag: Optional[str]) -> Optional[str]:
    """Extract version number from a tag like v1.2.3."""
    if tag is None:
        return None
    if tag.startswith("v"):
        return tag[1:]
    return tag


def get_commits_between(
    repo: str,
    from_ref: Optional[str],
    to_ref: str,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> List[CommitEntry]:
    """Get commits between two refs or within a date range."""
    # Build git log command
    # Format: hash|short_hash|author|email|date|subject
    separator = "---COMMIT_END---"
    log_format = f"%H|%h|%an|%ae|%Y-%m-%d|%s%n%b{separator}"

    args = ["log", f"--pretty=format:{log_format}"]

    if since:
        args.append(f"--since={since}")
    if until:
        args.append(f"--until={until}")

    if from_ref and to_ref:
        from_resolved = from_ref
        if from_ref == "latest":
            tag = get_latest_tag(repo)
            if tag:
                from_resolved = tag
            else:
                # No tags, get all commits
                from_resolved = None

        if from_resolved:
            args.append(f"{from_resolved}..{to_ref}")
        else:
            args.append(to_ref)
    elif to_ref:
        args.append(to_ref)

    args.append("--no-merges")

    result = run_git(args, cwd=repo)
    if result.returncode != 0:
        return []

    entries: List[CommitEntry] = []
    raw_commits = result.stdout.split(separator)

    for raw in raw_commits:
        raw = raw.strip()
        if not raw:
            continue

        lines = raw.split("\n")
        if not lines:
            continue

        header = lines[0]
        body = "\n".join(lines[1:]).strip()

        parts = header.split("|", 5)
        if len(parts) < 6:
            continue

        full_hash, short_hash, author, email, date, subject = parts

        # Parse conventional commit
        match = CONVENTIONAL_COMMIT_RE.match(subject)
        if match:
            commit_type = match.group("type")
            scope = match.group("scope")
            is_breaking = match.group("breaking") is not None
            description = match.group("description")
        else:
            commit_type = "other"
            scope = None
            is_breaking = False
            description = subject

        # Check for BREAKING CHANGE in body
        breaking_desc = None
        if body:
            bc_match = BREAKING_CHANGE_FOOTER_RE.search(body)
            if bc_match:
                is_breaking = True
                breaking_desc = bc_match.group("description")

        if is_breaking and not breaking_desc:
            breaking_desc = description

        entries.append(CommitEntry(
            hash=full_hash,
            short_hash=short_hash,
            type=commit_type,
            scope=scope,
            description=description,
            body=body,
            author=author,
            author_email=email,
            date=date,
            is_breaking=is_breaking,
            breaking_description=breaking_desc,
            raw_subject=subject,
        ))

    return entries


# ---------------------------------------------------------------------------
# Changelog rendering
# ---------------------------------------------------------------------------

def render_markdown(release: ChangelogRelease) -> str:
    """Render a release as Keep a Changelog markdown."""
    lines: List[str] = []

    # Header
    version_str = release.version or "Unreleased"
    lines.append(f"## [{version_str}] - {release.date}")
    lines.append("")

    # Breaking changes first (always)
    if release.breaking_changes:
        lines.append("### Breaking Changes")
        lines.append("")
        for entry in release.breaking_changes:
            desc = entry.breaking_description or entry.description
            lines.append(f"- {entry.scope_prefix}{desc} ({entry.short_hash}) - @{entry.author}")
        lines.append("")

    # Remaining sections in order
    for section in SECTION_ORDER:
        if section == "Breaking Changes":
            continue  # Already rendered
        if section not in release.sections:
            continue
        section_entries = release.sections[section]
        if not section_entries:
            continue

        lines.append(f"### {section}")
        lines.append("")
        for entry in section_entries:
            lines.append(f"- {entry.scope_prefix}{entry.description} ({entry.short_hash}) - @{entry.author}")
        lines.append("")

    # Contributors
    if release.contributors:
        lines.append("### Contributors")
        lines.append("")
        for contrib in release.contributors:
            lines.append(f"- @{contrib}")
        lines.append("")

    # Stats
    lines.append(f"**Total commits:** {len(release.entries)} | "
                 f"**Breaking changes:** {len(release.breaking_changes)} | "
                 f"**Contributors:** {len(release.contributors)}")
    lines.append("")

    return "\n".join(lines)


def render_full_changelog(releases: List[ChangelogRelease], repo_name: str = "") -> str:
    """Render a full changelog document."""
    lines: List[str] = []
    lines.append("# Changelog")
    lines.append("")
    lines.append("All notable changes to this project will be documented in this file.")
    lines.append("")
    lines.append("The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),")
    lines.append("and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).")
    lines.append("")

    for release in releases:
        lines.append(render_markdown(release))

    return "\n".join(lines)


def render_text_summary(release: ChangelogRelease) -> str:
    """Render a compact text summary."""
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("  CHANGELOG")
    lines.append("=" * 60)
    version_str = release.version or "Unreleased"
    lines.append(f"  Version: {version_str}")
    lines.append(f"  Date: {release.date}")
    lines.append(f"  Commits: {len(release.entries)}")
    lines.append(f"  Breaking Changes: {len(release.breaking_changes)}")
    lines.append(f"  Contributors: {', '.join(release.contributors)}")
    lines.append("-" * 60)

    for section in SECTION_ORDER:
        if section not in release.sections or not release.sections[section]:
            continue
        lines.append(f"\n  {section}:")
        for entry in release.sections[section]:
            lines.append(f"    - {entry.scope_prefix}{entry.description} ({entry.short_hash})")

    if release.breaking_changes:
        lines.append(f"\n  Breaking Changes:")
        for entry in release.breaking_changes:
            desc = entry.breaking_description or entry.description
            lines.append(f"    - {entry.scope_prefix}{desc}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Detect version for upcoming release
# ---------------------------------------------------------------------------

def detect_next_version(entries: List[CommitEntry], current_version: Optional[str]) -> Optional[str]:
    """Detect the next version based on commit types."""
    if current_version is None:
        return None

    parts = current_version.split(".")
    if len(parts) < 3:
        return None

    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2].split("-")[0])
    except ValueError:
        return None

    has_breaking = any(e.is_breaking for e in entries)
    has_feat = any(e.type == "feat" for e in entries)
    has_fix = any(e.type == "fix" for e in entries)

    if has_breaking:
        return f"{major + 1}.0.0"
    elif has_feat:
        return f"{major}.{minor + 1}.0"
    elif has_fix:
        return f"{major}.{minor}.{patch + 1}"
    else:
        return f"{major}.{minor}.{patch + 1}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate changelog from conventional commits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo . --from v1.0.0 --to HEAD
  %(prog)s --repo . --from latest --to HEAD
  %(prog)s --repo . --since 2026-01-01 --until 2026-03-18
  %(prog)s --repo . --from v1.0.0 --to v1.1.0 --output CHANGELOG.md
        """,
    )
    parser.add_argument("--repo", default=".", help="Path to git repository")
    parser.add_argument("--from", dest="from_ref", help="Start ref (tag, commit, or 'latest')")
    parser.add_argument("--to", dest="to_ref", default="HEAD", help="End ref (default: HEAD)")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", "-o", help="Write changelog to file")
    parser.add_argument("--version", help="Override version label for this release")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument("--format", choices=["markdown", "text"], default="markdown", dest="fmt", help="Output format")
    parser.add_argument("--full", action="store_true", help="Generate full changelog document with header")

    args = parser.parse_args()
    repo = os.path.abspath(args.repo)

    if not os.path.isdir(repo):
        print(f"Error: {repo} is not a directory", file=sys.stderr)
        sys.exit(2)

    # Get commits
    entries = get_commits_between(
        repo,
        from_ref=args.from_ref,
        to_ref=args.to_ref,
        since=args.since,
        until=args.until,
    )

    if not entries:
        print("No commits found in the specified range.", file=sys.stderr)
        sys.exit(1)

    # Determine version
    version = args.version
    if version is None and args.from_ref:
        from_tag = args.from_ref
        if from_tag == "latest":
            from_tag = get_latest_tag(repo)
        if from_tag:
            current_ver = get_version_from_tag(from_tag)
            version = detect_next_version(entries, current_ver)

    # Build release
    release = ChangelogRelease(
        version=version,
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    for entry in entries:
        release.add_entry(entry)

    # Output
    if args.json_output:
        output = json.dumps(release.to_dict(), indent=2)
    elif args.fmt == "text":
        output = render_text_summary(release)
    else:
        if args.full:
            output = render_full_changelog([release])
        else:
            output = render_markdown(release)

    if args.output:
        output_path = args.output
        if not os.path.isabs(output_path):
            output_path = os.path.join(repo, output_path)

        # If file exists and we're appending, insert after header
        if os.path.isfile(output_path) and not args.full:
            with open(output_path, "r") as f:
                existing = f.read()

            # Insert new release after the header lines
            header_end = "adheres to [Semantic Versioning]"
            if header_end in existing:
                idx = existing.index(header_end)
                idx = existing.index("\n", idx) + 1
                # Skip blank lines
                while idx < len(existing) and existing[idx] == "\n":
                    idx += 1
                new_content = existing[:idx] + "\n" + render_markdown(release) + "\n" + existing[idx:]
            else:
                new_content = existing + "\n" + render_markdown(release)

            with open(output_path, "w") as f:
                f.write(new_content)
            print(f"Updated {output_path}")
        else:
            content = render_full_changelog([release]) if not args.full else output
            with open(output_path, "w") as f:
                f.write(content)
            print(f"Written to {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
