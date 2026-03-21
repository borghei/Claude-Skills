#!/usr/bin/env python3
"""Format parsed commits into Keep a Changelog markdown.

Accepts JSON from commit_parser.py (via stdin or --file) and renders a
complete changelog entry in Keep a Changelog format. Supports version
headers, comparison links, breaking change sections, and the Unreleased
section pattern.

Usage:
    python commit_parser.py --json | python changelog_formatter.py --version 1.4.0
    python changelog_formatter.py --file parsed.json --version 2.0.0 --repo-url https://github.com/org/repo
    python changelog_formatter.py --file parsed.json --version 2.0.0 --json
    python changelog_formatter.py --file parsed.json --unreleased
"""

import argparse
import json
import sys
from collections import OrderedDict
from datetime import date

SECTION_ORDER = [
    "BREAKING CHANGES",
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Performance",
    "Security",
]

TYPE_TO_SECTION = OrderedDict([
    ("feat", "Added"),
    ("fix", "Fixed"),
    ("perf", "Performance"),
    ("security", "Security"),
    ("deprecated", "Deprecated"),
    ("remove", "Removed"),
    ("refactor", "Changed"),
])

CHANGELOG_HEADER = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
"""


def read_input(args):
    """Read parsed commit JSON from file or stdin."""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return json.load(f)
    if not sys.stdin.isatty():
        return json.load(sys.stdin)
    print("Error: No input provided. Pipe commit_parser.py --json output or use --file.",
          file=sys.stderr)
    sys.exit(1)


def extract_commits(data):
    """Extract the flat list of commits from parser output."""
    if "commits" in data:
        return data["commits"]
    if "groups" in data:
        commits = []
        for group in data["groups"].values():
            if isinstance(group, dict) and "commits" in group:
                commits.extend(group["commits"])
        return commits
    if isinstance(data, list):
        return data
    return []


def build_sections(commits, repo_url=None, link_style="commit"):
    """Group commits into changelog sections."""
    sections = OrderedDict()

    # Collect breaking changes into their own section first
    breaking_commits = [c for c in commits if c.get("breaking")]
    if breaking_commits:
        entries = []
        for c in breaking_commits:
            desc = c.get("breaking_description") or c["description"]
            scope_prefix = f"**{c['scope']}**: " if c.get("scope") else ""
            entries.append(f"- {scope_prefix}{desc}")
        sections["BREAKING CHANGES"] = entries

    # Group remaining commits by section
    for commit in commits:
        section_name = TYPE_TO_SECTION.get(commit.get("type"))
        if not section_name:
            continue

        if section_name not in sections:
            sections[section_name] = []

        scope_prefix = f"**{commit['scope']}**: " if commit.get("scope") else ""
        description = commit["description"]

        # Build link suffix
        link = ""
        if repo_url and commit.get("hash"):
            short = commit.get("short_hash", commit["hash"][:7])
            if link_style == "commit":
                link = f" ([{short}]({repo_url}/commit/{commit['hash']}))"
            elif link_style == "none":
                link = ""

        sections[section_name].append(f"- {scope_prefix}{description}{link}")

    return sections


def render_keep_a_changelog(version, release_date, sections, repo_url=None,
                            previous_version=None, include_header=False):
    """Render sections in Keep a Changelog markdown format."""
    lines = []

    if include_header:
        lines.append(CHANGELOG_HEADER.strip())
        lines.append("")

    # Version heading
    if version.lower() == "unreleased":
        if repo_url and previous_version:
            lines.append(f"## [Unreleased]")
        else:
            lines.append("## [Unreleased]")
    else:
        lines.append(f"## [{version}] - {release_date}")

    lines.append("")

    # Render sections in defined order
    rendered_any = False
    for section_name in SECTION_ORDER:
        if section_name in sections:
            lines.append(f"### {section_name}")
            lines.append("")
            for entry in sections[section_name]:
                lines.append(entry)
            lines.append("")
            rendered_any = True

    # Handle any custom sections not in the standard order
    for section_name, entries in sections.items():
        if section_name not in SECTION_ORDER:
            lines.append(f"### {section_name}")
            lines.append("")
            for entry in entries:
                lines.append(entry)
            lines.append("")
            rendered_any = True

    if not rendered_any:
        lines.append("No notable changes in this release.")
        lines.append("")

    # Comparison link footer
    if repo_url and version.lower() != "unreleased" and previous_version:
        lines.append(
            f"[{version}]: {repo_url}/compare/v{previous_version}...v{version}"
        )
        lines.append("")

    return "\n".join(lines)


def render_github_release(version, sections, repo_url=None, previous_version=None):
    """Render sections in GitHub Release Notes format."""
    github_section_names = {
        "BREAKING CHANGES": "Breaking Changes",
        "Added": "What's New",
        "Changed": "Changes",
        "Deprecated": "Deprecations",
        "Removed": "Removals",
        "Fixed": "Bug Fixes",
        "Performance": "Performance",
        "Security": "Security",
    }

    lines = []
    for section_name in SECTION_ORDER:
        if section_name in sections:
            heading = github_section_names.get(section_name, section_name)
            lines.append(f"## {heading}")
            lines.append("")
            for entry in sections[section_name]:
                lines.append(entry)
            lines.append("")

    if repo_url and previous_version:
        lines.append(
            f"**Full Changelog**: {repo_url}/compare/v{previous_version}...v{version}"
        )
        lines.append("")

    return "\n".join(lines)


def build_json_output(version, release_date, sections, stats=None):
    """Build structured JSON output for automation pipelines."""
    return {
        "version": version,
        "date": release_date,
        "sections": dict(sections),
        "section_count": len(sections),
        "entry_count": sum(len(v) for v in sections.values()),
        "has_breaking_changes": "BREAKING CHANGES" in sections,
        "stats": stats,
    }


def determine_bump(commits):
    """Determine the semver bump level from commits."""
    if any(c.get("breaking") for c in commits):
        return "major"
    if any(c.get("type") == "feat" for c in commits):
        return "minor"
    if any(c.get("type") in ("fix", "perf", "security", "refactor") for c in commits):
        return "patch"
    return "none"


def bump_version(current, bump_level):
    """Apply a semver bump to a version string."""
    clean = current.lstrip("v")
    parts = clean.split(".")
    if len(parts) != 3:
        return current
    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return current

    if bump_level == "major":
        return f"{major + 1}.0.0"
    elif bump_level == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_level == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return current


def main():
    parser = argparse.ArgumentParser(
        description="Format parsed conventional commits into Keep a Changelog markdown.",
        epilog="Reads JSON output from commit_parser.py via stdin or --file.",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to JSON file from commit_parser.py (default: read from stdin)",
    )
    parser.add_argument(
        "--version", "-v",
        help="Version number for the release header (e.g. 1.4.0)",
    )
    parser.add_argument(
        "--date", "-d",
        default=None,
        help="Release date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--previous-version", "-p",
        help="Previous version for comparison link (e.g. 1.3.2)",
    )
    parser.add_argument(
        "--repo-url", "-r",
        help="Repository URL for commit/comparison links (e.g. https://github.com/org/repo)",
    )
    parser.add_argument(
        "--format",
        choices=["keepachangelog", "github"],
        default="keepachangelog",
        help="Output format (default: keepachangelog)",
    )
    parser.add_argument(
        "--unreleased",
        action="store_true",
        help="Use [Unreleased] as the version header",
    )
    parser.add_argument(
        "--include-header",
        action="store_true",
        help="Include the full Keep a Changelog file header",
    )
    parser.add_argument(
        "--link-style",
        choices=["commit", "none"],
        default="commit",
        help="Style for commit links in entries (default: commit)",
    )
    parser.add_argument(
        "--auto-version",
        help="Auto-determine next version from BASE version (e.g. 1.3.2 -> computed bump)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of markdown",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)",
    )

    args = parser.parse_args()

    data = read_input(args)
    commits = extract_commits(data)

    if not commits:
        print("Warning: No commits found in input.", file=sys.stderr)

    # Determine version
    release_date = args.date or date.today().isoformat()

    if args.unreleased:
        version = "Unreleased"
    elif args.auto_version:
        bump_level = determine_bump(commits)
        version = bump_version(args.auto_version, bump_level)
        if not args.previous_version:
            args.previous_version = args.auto_version.lstrip("v")
    elif args.version:
        version = args.version
    else:
        version = "Unreleased"

    repo_url = args.repo_url.rstrip("/") if args.repo_url else None

    # Build sections
    sections = build_sections(commits, repo_url=repo_url, link_style=args.link_style)

    stats = data.get("stats") if isinstance(data, dict) else None

    if args.json_output:
        output = build_json_output(version, release_date, sections, stats)
        if args.auto_version:
            output["bump_level"] = determine_bump(commits)
            output["previous_version"] = args.auto_version
        print(json.dumps(output, indent=args.indent, default=str))
    elif args.format == "github":
        print(render_github_release(
            version, sections,
            repo_url=repo_url,
            previous_version=args.previous_version,
        ))
    else:
        print(render_keep_a_changelog(
            version, release_date, sections,
            repo_url=repo_url,
            previous_version=args.previous_version,
            include_header=args.include_header,
        ))


if __name__ == "__main__":
    main()
