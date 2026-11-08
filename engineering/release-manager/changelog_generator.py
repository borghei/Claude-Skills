#!/usr/bin/env python3
"""
Changelog Generator

Parses git log output in conventional commits format and generates structured changelogs
in multiple formats (Markdown, Keep a Changelog). Groups commits by type, extracts scope,
links to PRs/issues, and highlights breaking changes.

Input: git log text (piped from git log) or JSON array of commits
Output: formatted CHANGELOG.md section + release summary stats
"""

import argparse
import json
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

ONELINE = re.compile(r'^([0-9a-f]{7,40})\s+(.+)$')
FULL_HEADER = re.compile(r'^commit\s+([0-9a-f]{7,40})\b')


class ConventionalCommit:
    """Represents a parsed conventional commit."""

    def __init__(self, raw_message: str, commit_hash: str = "", author: str = "",
                 date: str = "", merge_info: Optional[str] = None):
        self.raw_message = raw_message
        self.commit_hash = commit_hash
        self.author = author
        self.date = date
        self.merge_info = merge_info

        # Parse the commit message
        self.type = ""
        self.scope = ""
        self.description = ""
        self.body = ""
        self.footers = []
        self.is_breaking = False
        self.breaking_change_description = ""

        self._parse_commit_message()

    def _parse_commit_message(self):
        """Parse conventional commit format."""
        lines = self.raw_message.split('\n')
        header = lines[0] if lines else ""

        # Parse header: type(scope): description
        header_pattern = r'^(\w+)(\([^)]+\))?(!)?:\s*(.+)$'
        match = re.match(header_pattern, header)

        if match:
            self.type = match.group(1).lower()
            scope_match = match.group(2)
            self.scope = scope_match[1:-1] if scope_match else ""  # Remove parentheses
            self.is_breaking = bool(match.group(3))  # ! indicates breaking change
            self.description = match.group(4).strip()
        else:
            # Fallback for non-conventional commits
            self.type = "chore"
            self.description = header

        # Parse body and footers
        if len(lines) > 1:
            body_lines = []
            footer_lines = []
            in_footer = False

            for line in lines[1:]:
                if not line.strip():
                    continue

                # Footer: "Token: value", "Token #123" or "BREAKING CHANGE: ..."
                footer_pattern = r'^(BREAKING[ -]CHANGE|[A-Za-z-]+):\s*(.+)$|^([A-Za-z-]+)\s+#(\d+)$'
                if re.match(footer_pattern, line):
                    in_footer = True
                    footer_lines.append(line)
                    if re.match(r'^BREAKING[ -]CHANGE:', line):
                        self.is_breaking = True
                        self.breaking_change_description = line[16:].strip()
                else:
                    if in_footer:
                        # Continuation of footer
                        footer_lines.append(line)
                    else:
                        body_lines.append(line)

            self.body = '\n'.join(body_lines).strip()
            self.footers = footer_lines

    def extract_issue_references(self) -> List[str]:
        """Extract issue/PR references like #123, fixes #456, etc."""
        text = f"{self.description} {self.body} {' '.join(self.footers)}"

        # Common patterns for issue references
        patterns = [
            r'#(\d+)',  # Simple #123
            r'(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)',  # closes #123
            r'(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(\w+/\w+)?#(\d+)'  # fixes repo#123
        ]

        references = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle tuple results from more complex patterns
                    ref = match[-1] if match[-1] else match[0]
                else:
                    ref = match
                if ref and ref not in references:
                    references.append(ref)

        return references

    def get_changelog_category(self) -> str:
        """Map commit type to changelog category."""
        category_map = {
            'feat': 'Added',
            'add': 'Added',
            'fix': 'Fixed',
            'bugfix': 'Fixed',
            'security': 'Security',
            'perf': 'Changed',  # Keep a Changelog has no Performance section
            'refactor': 'Changed',
            'style': 'Changed',
            'docs': 'Changed',
            'test': None,  # Tests don't appear in user-facing changelog
            'ci': None,
            'build': None,
            'chore': None,
            'revert': 'Fixed',
            'remove': 'Removed',
            'deprecate': 'Deprecated'
        }

        return category_map.get(self.type, 'Changed')


class ChangelogGenerator:
    """Main changelog generator class."""

    def __init__(self):
        self.commits: List[ConventionalCommit] = []
        self.version = "Unreleased"
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.base_url = ""

    def parse_git_log_output(self, git_log_text: str):
        """Parse `git log --oneline` or default `git log` output.

        Lines that fit neither shape are counted in ``self.skipped`` so the CLI
        can warn instead of silently dropping commits.
        """
        self.skipped = 0
        lines = git_log_text.strip('\n').split('\n')
        if any(FULL_HEADER.match(line) for line in lines):
            self._parse_full_log(lines)
            return
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = ONELINE.match(line)
            if match:
                self.commits.append(ConventionalCommit(match.group(2), match.group(1)))
            else:
                self.skipped += 1

    def _parse_full_log(self, lines: List[str]):
        """Parse default `git log` output: header lines, then a 4-space indented message."""
        current: Optional[Dict[str, str]] = None
        buffer: List[str] = []

        def flush():
            if current is not None:
                self.commits.append(ConventionalCommit(
                    '\n'.join(buffer).strip(), current['hash'], current.get('author', ''),
                    current.get('date', ''), current.get('merge')))

        for line in lines:
            match = FULL_HEADER.match(line)
            if match:
                flush()
                current, buffer = {'hash': match.group(1)}, []
            elif current is None:
                self.skipped += 1 if line.strip() else 0
            elif line.startswith(('Author:', 'Date:', 'Merge:')) and not buffer:
                key, _, value = line.partition(':')
                current[key.lower()] = value.strip()
            else:
                buffer.append(line[4:] if line.startswith('    ') else line.strip())
        flush()

    def parse_json_commits(self, json_data: Union[str, List[Dict]]):
        """Parse commits from JSON format."""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        for commit_data in data:
            commit = ConventionalCommit(
                raw_message=commit_data.get('message', ''),
                commit_hash=commit_data.get('hash', ''),
                author=commit_data.get('author', ''),
                date=commit_data.get('date', '')
            )
            self.commits.append(commit)

    def group_commits_by_category(self) -> Dict[str, List[ConventionalCommit]]:
        """Group commits by changelog category."""
        categories = defaultdict(list)

        for commit in self.commits:
            category = commit.get_changelog_category()
            if category:  # Skip None categories (internal changes)
                categories[category].append(commit)

        return dict(categories)

    def generate_markdown_changelog(self, include_unreleased: bool = True) -> str:
        """Generate Keep a Changelog format markdown."""
        grouped_commits = self.group_commits_by_category()

        if not grouped_commits:
            return "No notable changes.\n"

        # Start with header
        changelog = []
        if include_unreleased and self.version == "Unreleased":
            changelog.append(f"## [{self.version}]")
        else:
            changelog.append(f"## [{self.version}] - {self.date}")

        changelog.append("")

        # Order categories logically
        category_order = ['Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security']

        # Separate breaking changes
        breaking_changes = [commit for commit in self.commits if commit.is_breaking]

        # Add breaking changes section first if any exist
        if breaking_changes:
            changelog.append("### Breaking Changes")
            for commit in breaking_changes:
                line = self._format_commit_line(commit, show_breaking=True)
                changelog.append(f"- {line}")
            changelog.append("")

        # Add regular categories
        for category in category_order:
            # Breaking commits are listed once, under Breaking Changes
            commits = [c for c in grouped_commits.get(category, []) if not c.is_breaking]
            if not commits:
                continue

            changelog.append(f"### {category}")

            # Sort by scope (unscoped last); the scope is shown once, as a line prefix
            for commit in sorted(commits, key=lambda c: (not c.scope, c.scope)):
                changelog.append(f"- {self._format_commit_line(commit)}")

            changelog.append("")

        return '\n'.join(changelog)

    def _format_commit_line(self, commit: ConventionalCommit, show_breaking: bool = False) -> str:
        """Format a single commit line for the changelog."""
        # Start with description
        # Upper-case only the first letter so OAuth2, WebP and GitHub survive
        line = commit.description[:1].upper() + commit.description[1:]

        # Add scope if present and not already in description
        if commit.scope and commit.scope.lower() not in line.lower():
            line = f"**{commit.scope}:** {line}"

        # Add issue references
        issue_refs = commit.extract_issue_references()
        if issue_refs:
            refs_str = ', '.join(f"#{ref}" for ref in issue_refs)
            line += f" ({refs_str})"

        # Add commit hash if available
        if commit.commit_hash:
            short_hash = commit.commit_hash[:7]
            line += f" [{short_hash}]"

            if self.base_url:
                line += f"({self.base_url}/commit/{commit.commit_hash})"

        # Add breaking change indicator
        if show_breaking and commit.breaking_change_description:
            line += f" - {commit.breaking_change_description}"
        elif commit.is_breaking and not show_breaking:
            line += " ⚠️ BREAKING"

        return line

    def generate_release_summary(self) -> Dict:
        """Generate summary statistics for the release."""
        if not self.commits:
            return {
                'version': self.version,
                'date': self.date,
                'total_commits': 0,
                'by_type': {},
                'by_author': {},
                'breaking_changes': 0,
                'notable_changes': 0
            }

        # Count by type
        type_counts = Counter(commit.type for commit in self.commits)

        # Count by author
        author_counts = Counter(commit.author for commit in self.commits if commit.author)

        # Count breaking changes
        breaking_count = sum(1 for commit in self.commits if commit.is_breaking)

        # Count notable changes (excluding chore, ci, build, test)
        notable_types = {'feat', 'fix', 'security', 'perf', 'refactor', 'remove', 'deprecate'}
        notable_count = sum(1 for commit in self.commits if commit.type in notable_types)

        return {
            'version': self.version,
            'date': self.date,
            'total_commits': len(self.commits),
            'by_type': dict(type_counts.most_common()),
            'by_author': dict(author_counts.most_common(10)),  # Top 10 contributors
            'breaking_changes': breaking_count,
            'notable_changes': notable_count,
            'scopes': list(set(commit.scope for commit in self.commits if commit.scope)),
            'issue_references': len(set().union(*(commit.extract_issue_references() for commit in self.commits)))
        }

    def generate_json_output(self) -> str:
        """Generate JSON representation of the changelog data."""
        grouped_commits = self.group_commits_by_category()

        # Convert commits to serializable format
        json_data = {
            'version': self.version,
            'date': self.date,
            'summary': self.generate_release_summary(),
            'categories': {}
        }

        for category, commits in grouped_commits.items():
            json_data['categories'][category] = []
            for commit in commits:
                commit_data = {
                    'type': commit.type,
                    'scope': commit.scope,
                    'description': commit.description,
                    'hash': commit.commit_hash,
                    'author': commit.author,
                    'date': commit.date,
                    'breaking': commit.is_breaking,
                    'breaking_description': commit.breaking_change_description,
                    'issue_references': commit.extract_issue_references()
                }
                json_data['categories'][category].append(commit_data)

        return json.dumps(json_data, indent=2)


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(description="Generate changelog from conventional commits")
    parser.add_argument('--input', '-i', type=str, help='Input file (default: stdin)')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'both'],
                       default='markdown', help='Output format')
    parser.add_argument('--version', '-v', type=str, default='Unreleased',
                       help='Version for this release')
    parser.add_argument('--date', '-d', type=str,
                       default=datetime.now().strftime("%Y-%m-%d"),
                       help='Release date (YYYY-MM-DD format)')
    parser.add_argument('--base-url', '-u', type=str, default='',
                       help='Base URL for commit links')
    parser.add_argument('--input-format', choices=['git-log', 'json'],
                       default='git-log', help='Input format')
    parser.add_argument('--output', '-o', type=str, help='Output file (default: stdout)')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Include release summary statistics')

    args = parser.parse_args()

    # Read input; exit 2 means the input could not be used
    try:
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            input_data = sys.stdin.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        sys.exit(2)

    if not input_data.strip():
        print("error: no input data provided", file=sys.stderr)
        sys.exit(2)

    # Initialize generator
    generator = ChangelogGenerator()
    generator.version = args.version
    generator.date = args.date
    generator.base_url = args.base_url

    # Parse input
    try:
        if args.input_format == 'json':
            generator.parse_json_commits(input_data)
        else:
            generator.parse_git_log_output(input_data)
    except Exception as e:
        print(f"error: cannot parse input: {e}", file=sys.stderr)
        sys.exit(2)

    if not generator.commits:
        print("error: no commits found (expected `git log` or `git log --oneline` output)", file=sys.stderr)
        sys.exit(2)
    if getattr(generator, 'skipped', 0):
        print(f"warning: skipped {generator.skipped} line(s) that are not git log commit lines", file=sys.stderr)

    # Generate output
    output_lines = []

    if args.format in ['markdown', 'both']:
        changelog_md = generator.generate_markdown_changelog()
        if args.format == 'both':
            output_lines.append("# Markdown Changelog\n")
        output_lines.append(changelog_md)

    if args.format in ['json', 'both']:
        changelog_json = generator.generate_json_output()
        if args.format == 'both':
            output_lines.append("\n# JSON Output\n")
        output_lines.append(changelog_json)

    if args.summary:
        summary = generator.generate_release_summary()
        output_lines.append(f"\n# Release Summary")
        output_lines.append(f"- **Version:** {summary['version']}")
        output_lines.append(f"- **Total Commits:** {summary['total_commits']}")
        output_lines.append(f"- **Notable Changes:** {summary['notable_changes']}")
        output_lines.append(f"- **Breaking Changes:** {summary['breaking_changes']}")
        output_lines.append(f"- **Issue References:** {summary['issue_references']}")

        if summary['by_type']:
            output_lines.append("- **By Type:**")
            for commit_type, count in summary['by_type'].items():
                output_lines.append(f"  - {commit_type}: {count}")

    # Write output
    final_output = '\n'.join(output_lines)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(final_output)
    else:
        print(final_output)


if __name__ == '__main__':
    main()