#!/usr/bin/env python3
"""Parse git log output (conventional commits) into structured changelog entries.

Reads git log output from stdin or a file and extracts structured data from
Conventional Commit messages. Groups commits by type (feat, fix, docs, etc.)
and detects breaking changes from both the ! suffix and BREAKING CHANGE footer.

Usage:
    git log v1.0.0..HEAD --pretty=format:'%H%n%s%n%b%n---COMMIT_END---' --no-merges | python commit_parser.py
    python commit_parser.py --file git-log-output.txt
    python commit_parser.py --file git-log-output.txt --json
    python commit_parser.py --file git-log-output.txt --scope api
    python commit_parser.py --file git-log-output.txt --types feat,fix
"""

import argparse
import json
import re
import sys
from collections import OrderedDict

COMMIT_DELIMITER = "---COMMIT_END---"

COMMIT_PATTERN = re.compile(
    r"^(?P<type>feat|fix|perf|refactor|docs|test|build|ci|chore|security|deprecated|remove)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?"
    r":\s*(?P<description>.+)$"
)

BREAKING_CHANGE_PATTERN = re.compile(
    r"BREAKING CHANGE:\s*(.+)", re.DOTALL
)

TYPE_LABELS = OrderedDict([
    ("feat", "Features"),
    ("fix", "Bug Fixes"),
    ("perf", "Performance Improvements"),
    ("security", "Security"),
    ("deprecated", "Deprecations"),
    ("remove", "Removals"),
    ("refactor", "Refactoring"),
    ("docs", "Documentation"),
    ("test", "Tests"),
    ("build", "Build System"),
    ("ci", "Continuous Integration"),
    ("chore", "Chores"),
])

USER_FACING_TYPES = {"feat", "fix", "perf", "security", "deprecated", "remove", "refactor"}


def parse_raw_log(text):
    """Split raw git log text into individual commit blocks."""
    blocks = text.split(COMMIT_DELIMITER)
    commits_raw = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        if len(lines) < 2:
            continue
        commit_hash = lines[0].strip()
        subject = lines[1].strip()
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        if commit_hash and subject:
            commits_raw.append({
                "hash": commit_hash,
                "subject": subject,
                "body": body,
            })
    return commits_raw


def parse_commit(raw):
    """Parse a single raw commit dict into a structured commit entry.

    Returns None if the subject does not match conventional commit format.
    """
    subject = raw["subject"]
    body = raw["body"]
    commit_hash = raw["hash"]

    match = COMMIT_PATTERN.match(subject)
    if not match:
        return None

    commit_type = match.group("type")
    scope = match.group("scope")
    is_breaking = bool(match.group("breaking"))
    description = match.group("description").strip()

    breaking_description = None
    if body:
        bc_match = BREAKING_CHANGE_PATTERN.search(body)
        if bc_match:
            is_breaking = True
            breaking_description = bc_match.group(1).strip()

    # Extract co-authors from trailers
    co_authors = []
    if body:
        for line in body.split("\n"):
            line = line.strip()
            if line.lower().startswith("co-authored-by:"):
                co_authors.append(line.split(":", 1)[1].strip())

    return {
        "hash": commit_hash,
        "short_hash": commit_hash[:7],
        "type": commit_type,
        "scope": scope,
        "description": description,
        "body": body if body else None,
        "breaking": is_breaking,
        "breaking_description": breaking_description,
        "co_authors": co_authors if co_authors else None,
    }


def group_by_type(commits):
    """Group parsed commits by their type, maintaining defined order."""
    groups = OrderedDict()
    for type_key in TYPE_LABELS:
        matching = [c for c in commits if c["type"] == type_key]
        if matching:
            groups[type_key] = {
                "label": TYPE_LABELS[type_key],
                "count": len(matching),
                "commits": matching,
            }
    return groups


def filter_commits(commits, scope_filter=None, type_filter=None, user_facing_only=False):
    """Apply optional filters to the parsed commit list."""
    result = commits

    if scope_filter:
        scopes = {s.strip().lower() for s in scope_filter.split(",")}
        result = [c for c in result if c["scope"] and c["scope"].lower() in scopes]

    if type_filter:
        types = {t.strip().lower() for t in type_filter.split(",")}
        result = [c for c in result if c["type"] in types]

    if user_facing_only:
        result = [c for c in result if c["type"] in USER_FACING_TYPES]

    return result


def format_human_readable(grouped, stats):
    """Render grouped commits as human-readable text output."""
    lines = []
    lines.append("=" * 60)
    lines.append("PARSED COMMITS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Total parsed:      {stats['parsed']}")
    lines.append(f"Skipped (invalid): {stats['skipped']}")
    lines.append(f"Breaking changes:  {stats['breaking']}")
    lines.append(f"User-facing:       {stats['user_facing']}")
    lines.append("")

    if not grouped:
        lines.append("No commits matched the given filters.")
        return "\n".join(lines)

    for type_key, group in grouped.items():
        lines.append("-" * 60)
        lines.append(f"{group['label']} ({group['count']})")
        lines.append("-" * 60)

        for commit in group["commits"]:
            scope_prefix = f"({commit['scope']}) " if commit["scope"] else ""
            breaking_marker = " [BREAKING]" if commit["breaking"] else ""
            lines.append(f"  {commit['short_hash']}  {scope_prefix}{commit['description']}{breaking_marker}")

            if commit["breaking_description"]:
                # Indent breaking change description
                for bd_line in commit["breaking_description"].split("\n"):
                    lines.append(f"             BREAKING: {bd_line}")

        lines.append("")

    return "\n".join(lines)


def build_output(grouped, stats, all_commits):
    """Build the JSON-serializable output structure."""
    return {
        "stats": stats,
        "groups": grouped,
        "commits": all_commits,
    }


def read_input(args):
    """Read git log text from file or stdin."""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Error: No input provided. Pipe git log output or use --file.", file=sys.stderr)
    print("Example: git log v1.0.0..HEAD --pretty=format:'%H%n%s%n%b%n---COMMIT_END---' "
          "--no-merges | python commit_parser.py", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Parse git log output with conventional commits into structured changelog entries.",
        epilog="Reads git log output formatted with ---COMMIT_END--- delimiters. "
               "Use: git log --pretty=format:'%%H%%n%%s%%n%%b%%n---COMMIT_END---' --no-merges",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to a file containing git log output (default: read from stdin)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of human-readable text",
    )
    parser.add_argument(
        "--scope", "-s",
        help="Filter commits by scope (comma-separated, e.g. 'api,ui')",
    )
    parser.add_argument(
        "--types", "-t",
        help="Filter commits by type (comma-separated, e.g. 'feat,fix')",
    )
    parser.add_argument(
        "--user-facing", "-u",
        action="store_true",
        help="Show only user-facing commit types (feat, fix, perf, security, deprecated, remove, refactor)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)",
    )

    args = parser.parse_args()

    raw_text = read_input(args)
    raw_commits = parse_raw_log(raw_text)

    parsed = []
    skipped = 0
    for raw in raw_commits:
        result = parse_commit(raw)
        if result:
            parsed.append(result)
        else:
            skipped += 1

    filtered = filter_commits(
        parsed,
        scope_filter=args.scope,
        type_filter=args.types,
        user_facing_only=args.user_facing,
    )

    grouped = group_by_type(filtered)

    stats = {
        "total_raw": len(raw_commits),
        "parsed": len(parsed),
        "skipped": skipped,
        "filtered": len(filtered),
        "breaking": sum(1 for c in filtered if c["breaking"]),
        "user_facing": sum(1 for c in filtered if c["type"] in USER_FACING_TYPES),
        "types_found": list(grouped.keys()),
        "scopes_found": sorted(set(
            c["scope"] for c in filtered if c["scope"]
        )),
    }

    if args.json_output:
        output = build_output(grouped, stats, filtered)
        print(json.dumps(output, indent=args.indent, default=str))
    else:
        print(format_human_readable(grouped, stats))


if __name__ == "__main__":
    main()
