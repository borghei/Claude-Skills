#!/usr/bin/env python3
"""
Markdown Link Checker

Scans markdown files for links and validates them:
- Local file references (does the file exist?)
- Anchor references within documents (does the heading exist?)
- Cross-document anchors (does the file and heading exist?)
- Relative path correctness
- Case sensitivity issues
- Image references
- Duplicate anchors

Usage:
    python link_checker.py /path/to/repo
    python link_checker.py /path/to/repo/README.md
    python link_checker.py /path/to/repo --json
    python link_checker.py /path/to/repo --broken-only
    python link_checker.py /path/to/repo --check-external
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# --- Constants ---

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", "dist", "build"}
MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp"}


# --- Link Extraction ---

class LinkInfo:
    """Represents a link found in a markdown file."""

    def __init__(
        self,
        source_file: str,
        line_number: int,
        link_text: str,
        link_target: str,
        link_type: str,  # "local_file", "anchor", "cross_doc_anchor", "external", "image"
    ):
        self.source_file = source_file
        self.line_number = line_number
        self.link_text = link_text
        self.link_target = link_target
        self.link_type = link_type
        self.is_valid: Optional[bool] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_file": self.source_file,
            "line": self.line_number,
            "text": self.link_text,
            "target": self.link_target,
            "type": self.link_type,
            "valid": self.is_valid,
            "error": self.error,
        }


def classify_link(target: str) -> str:
    """Classify a link target by type."""
    if target.startswith(("http://", "https://", "ftp://", "mailto:")):
        return "external"
    if target.startswith("#"):
        return "anchor"

    # Check if it has an anchor
    file_part = target.split("#")[0] if "#" in target else target

    # Check for image
    ext = Path(file_part).suffix.lower() if file_part else ""
    if ext in IMAGE_EXTENSIONS:
        return "image"

    if "#" in target:
        return "cross_doc_anchor"

    return "local_file"


def extract_links(file_path: str, rel_path: str) -> List[LinkInfo]:
    """Extract all links from a markdown file."""
    links = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except (OSError, IOError):
        return links

    # Patterns
    # Standard markdown links: [text](target)
    md_link = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    # Reference-style links: [text][ref] and [ref]: url
    ref_def = re.compile(r'^\[([^\]]+)\]:\s+(.+)$')
    # HTML links: <a href="target">
    html_link = re.compile(r'<a\s+[^>]*href=["\']([^"\']+)["\']', re.IGNORECASE)
    # Image links: ![alt](src)
    img_link = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    # HTML images: <img src="target">
    html_img = re.compile(r'<img\s+[^>]*src=["\']([^"\']+)["\']', re.IGNORECASE)

    in_code_block = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Image links (check before regular links to avoid double-counting)
        for match in img_link.finditer(line):
            alt_text = match.group(1)
            target = match.group(2).strip()
            link_type = classify_link(target)
            if link_type == "external":
                links.append(LinkInfo(rel_path, i, alt_text, target, "external"))
            else:
                links.append(LinkInfo(rel_path, i, alt_text, target, "image"))

        # Standard markdown links (exclude images already captured)
        for match in md_link.finditer(line):
            # Skip if this is part of an image link
            start = match.start()
            if start > 0 and line[start - 1] == "!":
                continue
            text = match.group(1)
            target = match.group(2).strip()
            link_type = classify_link(target)
            links.append(LinkInfo(rel_path, i, text, target, link_type))

        # Reference-style link definitions
        ref_match = ref_def.match(stripped)
        if ref_match:
            ref_name = ref_match.group(1)
            target = ref_match.group(2).strip()
            link_type = classify_link(target)
            links.append(LinkInfo(rel_path, i, ref_name, target, link_type))

        # HTML links
        for match in html_link.finditer(line):
            target = match.group(1).strip()
            link_type = classify_link(target)
            links.append(LinkInfo(rel_path, i, "", target, link_type))

        # HTML images
        for match in html_img.finditer(line):
            target = match.group(1).strip()
            if not target.startswith(("http://", "https://")):
                links.append(LinkInfo(rel_path, i, "", target, "image"))

    return links


# --- Heading / Anchor Extraction ---

def extract_headings(file_path: str) -> Set[str]:
    """Extract all heading anchors from a markdown file."""
    headings = set()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return headings

    for line in content.splitlines():
        match = re.match(r'^#{1,6}\s+(.+)', line)
        if match:
            heading_text = match.group(1).strip()
            slug = slugify_heading(heading_text)
            headings.add(slug)

    return headings


def slugify_heading(text: str) -> str:
    """Convert heading text to GitHub-style anchor slug."""
    text = text.lower()
    # Remove inline code backticks
    text = text.replace("`", "")
    # Remove special characters except hyphens and spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'[\s]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text


def find_duplicate_anchors(file_path: str) -> List[Tuple[str, int]]:
    """Find headings that produce duplicate anchors."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except (OSError, IOError):
        return []

    seen: Dict[str, int] = {}
    duplicates = []

    for i, line in enumerate(lines, 1):
        match = re.match(r'^#{1,6}\s+(.+)', line)
        if match:
            slug = slugify_heading(match.group(1).strip())
            if slug in seen:
                duplicates.append((slug, i))
            else:
                seen[slug] = i

    return duplicates


# --- Validation ---

def validate_link(
    link: LinkInfo,
    repo_path: str,
    heading_cache: Dict[str, Set[str]],
    check_external: bool = False,
) -> None:
    """Validate a single link and set is_valid and error."""

    if link.link_type == "external":
        if check_external:
            link.is_valid, link.error = validate_external_url(link.link_target)
        else:
            link.is_valid = True  # Skip external by default
        return

    if link.link_type == "anchor":
        # Anchor within same document
        anchor = link.link_target.lstrip("#")
        source_full = os.path.join(repo_path, link.source_file)
        headings = _get_headings(source_full, heading_cache)
        slug = slugify_heading(anchor)
        if slug in headings:
            link.is_valid = True
        else:
            link.is_valid = False
            link.error = f"Anchor '#{anchor}' not found in {link.source_file}"
        return

    # For local_file, image, cross_doc_anchor
    target = link.link_target
    anchor = None
    if "#" in target:
        file_part, anchor = target.split("#", 1)
    else:
        file_part = target

    if not file_part and anchor:
        # This is actually just an anchor link
        source_full = os.path.join(repo_path, link.source_file)
        headings = _get_headings(source_full, heading_cache)
        slug = slugify_heading(anchor)
        if slug in headings:
            link.is_valid = True
        else:
            link.is_valid = False
            link.error = f"Anchor '#{anchor}' not found"
        return

    # Resolve file path
    source_dir = os.path.dirname(link.source_file)
    resolved = os.path.normpath(os.path.join(repo_path, source_dir, file_part))

    if not os.path.exists(resolved):
        # Try from repo root
        resolved_root = os.path.normpath(os.path.join(repo_path, file_part))
        if os.path.exists(resolved_root):
            resolved = resolved_root
        else:
            # Case sensitivity check
            case_match = _check_case_insensitive(resolved)
            if case_match:
                link.is_valid = False
                link.error = (
                    f"File not found at '{file_part}' (case mismatch? "
                    f"found '{os.path.relpath(case_match, repo_path)}')"
                )
            else:
                link.is_valid = False
                link.error = f"File not found: '{file_part}'"
            return

    # File exists
    if anchor:
        # Validate anchor in target file
        if resolved.endswith(tuple(MARKDOWN_EXTENSIONS)):
            headings = _get_headings(resolved, heading_cache)
            slug = slugify_heading(anchor)
            if slug in headings:
                link.is_valid = True
            else:
                link.is_valid = False
                link.error = f"File exists but anchor '#{anchor}' not found in '{file_part}'"
        else:
            # Non-markdown file with anchor -- can't validate anchor
            link.is_valid = True
    else:
        link.is_valid = True


def _get_headings(file_path: str, cache: Dict[str, Set[str]]) -> Set[str]:
    """Get headings for a file, using cache."""
    if file_path not in cache:
        cache[file_path] = extract_headings(file_path)
    return cache[file_path]


def _check_case_insensitive(path: str) -> Optional[str]:
    """Check if a file exists with different case. Returns the actual path if found."""
    directory = os.path.dirname(path)
    filename = os.path.basename(path)

    if not os.path.isdir(directory):
        return None

    try:
        for entry in os.listdir(directory):
            if entry.lower() == filename.lower() and entry != filename:
                return os.path.join(directory, entry)
    except (OSError, PermissionError):
        pass

    return None


def validate_external_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate an external URL with a HEAD request."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "doc-drift-detector/2.0")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status < 400:
                return True, None
            return False, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        # Some servers don't support HEAD
        if e.code == 405:
            try:
                req = urllib.request.Request(url, method="GET")
                req.add_header("User-Agent", "doc-drift-detector/2.0")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.status < 400, None if resp.status < 400 else f"HTTP {resp.status}"
            except Exception:
                return False, f"HTTP {e.code}"
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)


# --- File Discovery ---

def find_markdown_files(path: str) -> List[str]:
    """Find all markdown files under a path."""
    files = []

    if os.path.isfile(path):
        if Path(path).suffix.lower() in MARKDOWN_EXTENSIONS:
            return [path]
        return []

    for root, dirs, filenames in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in filenames:
            if Path(f).suffix.lower() in MARKDOWN_EXTENSIONS:
                files.append(os.path.join(root, f))

    return sorted(files)


# --- Report ---

def generate_report(
    all_links: List[LinkInfo],
    duplicate_anchors: Dict[str, List[Tuple[str, int]]],
    broken_only: bool = False,
    as_json: bool = False,
) -> str:
    """Generate a link check report."""
    broken = [l for l in all_links if l.is_valid is False]
    valid = [l for l in all_links if l.is_valid is True]
    skipped = [l for l in all_links if l.is_valid is None]

    report_data = {
        "summary": {
            "total_links": len(all_links),
            "valid": len(valid),
            "broken": len(broken),
            "skipped": len(skipped),
            "duplicate_anchors": sum(len(v) for v in duplicate_anchors.values()),
        },
        "broken_links": [l.to_dict() for l in broken],
        "duplicate_anchors": {
            file: [{"anchor": anchor, "line": line} for anchor, line in dups]
            for file, dups in duplicate_anchors.items()
        },
    }

    if not broken_only:
        report_data["all_links"] = [l.to_dict() for l in all_links]

    if as_json:
        return json.dumps(report_data, indent=2, default=str)

    # Human-readable
    lines = []
    lines.append("Link Check Report")
    lines.append("=" * 60)
    lines.append(f"Total links:      {len(all_links)}")
    lines.append(f"Valid:            {len(valid)}")
    lines.append(f"Broken:           {len(broken)}")
    lines.append(f"Skipped:          {len(skipped)}")
    lines.append(f"Duplicate anchors: {sum(len(v) for v in duplicate_anchors.values())}")
    lines.append("")

    if broken:
        lines.append("BROKEN LINKS:")
        lines.append("-" * 60)

        # Group by source file
        by_file: Dict[str, List[LinkInfo]] = {}
        for link in broken:
            by_file.setdefault(link.source_file, []).append(link)

        for source_file, file_links in sorted(by_file.items()):
            lines.append(f"\n  {source_file}:")
            for link in sorted(file_links, key=lambda l: l.line_number):
                lines.append(f"    Line {link.line_number}: [{link.link_text}]({link.link_target})")
                lines.append(f"      Error: {link.error}")
        lines.append("")

    if duplicate_anchors:
        lines.append("DUPLICATE ANCHORS:")
        lines.append("-" * 60)
        for file, dups in sorted(duplicate_anchors.items()):
            lines.append(f"\n  {file}:")
            for anchor, line_num in dups:
                lines.append(f"    Line {line_num}: duplicate anchor '#{anchor}'")
        lines.append("")

    if not broken and not duplicate_anchors:
        lines.append("No issues found. All links are valid.")

    # Type breakdown
    type_counts: Dict[str, int] = {}
    broken_type_counts: Dict[str, int] = {}
    for link in all_links:
        type_counts[link.link_type] = type_counts.get(link.link_type, 0) + 1
    for link in broken:
        broken_type_counts[link.link_type] = broken_type_counts.get(link.link_type, 0) + 1

    lines.append("LINK TYPE BREAKDOWN:")
    lines.append("-" * 40)
    for ltype in sorted(type_counts.keys()):
        broken_count = broken_type_counts.get(ltype, 0)
        total = type_counts[ltype]
        lines.append(f"  {ltype:<25} {total:>4} total, {broken_count:>4} broken")

    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Check markdown links for validity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="File or directory to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--broken-only", action="store_true", help="Only show broken links")
    parser.add_argument("--check-external", action="store_true", help="Also validate external URLs (slower)")

    args = parser.parse_args()

    target_path = os.path.abspath(args.path)
    if not os.path.exists(target_path):
        print(f"Error: '{target_path}' does not exist", file=sys.stderr)
        sys.exit(2)

    # Determine repo root (for resolving paths)
    if os.path.isfile(target_path):
        repo_path = os.path.dirname(target_path)
        # Try to find git root
        current = repo_path
        while current != os.path.dirname(current):
            if os.path.isdir(os.path.join(current, ".git")):
                repo_path = current
                break
            current = os.path.dirname(current)
    else:
        repo_path = target_path

    # Find markdown files
    md_files = find_markdown_files(target_path)
    if not md_files:
        if args.json:
            print(json.dumps({"error": "No markdown files found"}, indent=2))
        else:
            print("No markdown files found.")
        sys.exit(0)

    # Extract and validate links
    all_links: List[LinkInfo] = []
    heading_cache: Dict[str, Set[str]] = {}
    duplicate_anchors: Dict[str, List[Tuple[str, int]]] = {}

    for md_file in md_files:
        rel_path = os.path.relpath(md_file, repo_path)
        links = extract_links(md_file, rel_path)
        all_links.extend(links)

        # Check for duplicate anchors
        dups = find_duplicate_anchors(md_file)
        if dups:
            duplicate_anchors[rel_path] = dups

    # Validate all links
    for link in all_links:
        validate_link(link, repo_path, heading_cache, check_external=args.check_external)

    # Report
    report = generate_report(all_links, duplicate_anchors, broken_only=args.broken_only, as_json=args.json)
    print(report)

    # Exit code
    broken_count = sum(1 for l in all_links if l.is_valid is False)
    dup_count = sum(len(v) for v in duplicate_anchors.values())
    sys.exit(1 if (broken_count > 0 or dup_count > 0) else 0)


if __name__ == "__main__":
    main()
