#!/usr/bin/env python3
"""
Prompt Catalog Manager - Manage a catalog of approved prompts with versioning.

Provides a local file-based prompt catalog with versioning, metadata tracking,
diff comparison, and search capabilities.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional
import difflib


CATALOG_FILE = "catalog.json"
PROMPTS_DIR = "versions"


@dataclass
class PromptEntry:
    """A single prompt entry in the catalog."""
    name: str
    version: str
    status: str  # draft, review, approved, deployed, retired
    author: str
    created: str
    updated: str
    description: str
    tags: List[str]
    model_targets: List[str]
    content_hash: str
    content_file: str
    audit_status: str  # pending, passed, failed
    token_estimate: int


@dataclass
class Catalog:
    """The prompt catalog."""
    created: str
    updated: str
    total_prompts: int = 0
    entries: Dict[str, List[PromptEntry]] = field(default_factory=dict)  # name -> versions


def _hash_content(content: str) -> str:
    """SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _estimate_tokens(text: str) -> int:
    """Quick token estimate."""
    return max(1, int(len(text) / 4.0 * 0.5 + len(text.split()) / 0.75 * 0.5))


def _next_version(versions: List[str]) -> str:
    """Calculate next semantic version."""
    if not versions:
        return "1.0.0"
    latest = sorted(versions, key=lambda v: [int(x) for x in v.split(".")])[-1]
    parts = latest.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def load_catalog(catalog_dir: Path) -> Catalog:
    """Load catalog from disk."""
    catalog_path = catalog_dir / CATALOG_FILE
    if not catalog_path.exists():
        return Catalog(
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
        )

    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog = Catalog(
        created=data.get("created", ""),
        updated=data.get("updated", ""),
        total_prompts=data.get("total_prompts", 0),
    )
    for name, versions in data.get("entries", {}).items():
        catalog.entries[name] = [
            PromptEntry(**v) for v in versions
        ]
    return catalog


def save_catalog(catalog: Catalog, catalog_dir: Path):
    """Save catalog to disk."""
    catalog.updated = datetime.now().isoformat()
    catalog.total_prompts = sum(len(v) for v in catalog.entries.values())

    data = {
        "created": catalog.created,
        "updated": catalog.updated,
        "total_prompts": catalog.total_prompts,
        "entries": {
            name: [asdict(e) for e in versions]
            for name, versions in catalog.entries.items()
        },
    }

    catalog_path = catalog_dir / CATALOG_FILE
    catalog_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def init_catalog(catalog_dir: Path) -> str:
    """Initialize a new prompt catalog."""
    catalog_dir.mkdir(parents=True, exist_ok=True)
    (catalog_dir / PROMPTS_DIR).mkdir(exist_ok=True)

    catalog = Catalog(
        created=datetime.now().isoformat(),
        updated=datetime.now().isoformat(),
    )
    save_catalog(catalog, catalog_dir)
    return f"Catalog initialized at {catalog_dir}"


def add_prompt(catalog_dir: Path, name: str, content: str,
               author: str = "unknown", description: str = "",
               tags: Optional[List[str]] = None,
               model_targets: Optional[List[str]] = None,
               status: str = "draft") -> str:
    """Add or update a prompt in the catalog."""
    catalog = load_catalog(catalog_dir)
    versions_dir = catalog_dir / PROMPTS_DIR
    versions_dir.mkdir(exist_ok=True)

    # Determine version
    existing_versions = [e.version for e in catalog.entries.get(name, [])]
    version = _next_version(existing_versions)

    # Save content file
    content_hash = _hash_content(content)
    content_file = f"{name}_v{version.replace('.', '_')}.txt"
    (versions_dir / content_file).write_text(content, encoding="utf-8")

    # Check for duplicate content
    for existing in catalog.entries.get(name, []):
        if existing.content_hash == content_hash:
            return f"Duplicate: Content identical to {name} v{existing.version}. No new version created."

    entry = PromptEntry(
        name=name,
        version=version,
        status=status,
        author=author,
        created=datetime.now().isoformat(),
        updated=datetime.now().isoformat(),
        description=description,
        tags=tags or [],
        model_targets=model_targets or [],
        content_hash=content_hash,
        content_file=content_file,
        audit_status="pending",
        token_estimate=_estimate_tokens(content),
    )

    if name not in catalog.entries:
        catalog.entries[name] = []
    catalog.entries[name].append(entry)

    save_catalog(catalog, catalog_dir)
    return f"Added {name} v{version} ({entry.token_estimate} tokens, hash: {content_hash})"


def list_prompts(catalog_dir: Path, show_all_versions: bool = False) -> str:
    """List all prompts in the catalog."""
    catalog = load_catalog(catalog_dir)

    if not catalog.entries:
        return "Catalog is empty."

    lines = []
    lines.append(f"Prompt Catalog ({catalog.total_prompts} total entries)")
    lines.append(f"Last updated: {catalog.updated}")
    lines.append("=" * 70)

    for name in sorted(catalog.entries.keys()):
        versions = catalog.entries[name]
        latest = versions[-1]

        lines.append(f"\n  {name}")
        lines.append(f"    Latest: v{latest.version} ({latest.status})")
        lines.append(f"    Author: {latest.author}")
        lines.append(f"    Tokens: ~{latest.token_estimate}")
        lines.append(f"    Audit: {latest.audit_status}")
        lines.append(f"    Tags: {', '.join(latest.tags) if latest.tags else 'none'}")
        lines.append(f"    Versions: {len(versions)}")

        if show_all_versions and len(versions) > 1:
            for v in versions:
                lines.append(f"      v{v.version} ({v.status}) - {v.created[:10]} [{v.audit_status}]")

    return "\n".join(lines)


def diff_versions(catalog_dir: Path, name: str,
                  version_a: Optional[str] = None,
                  version_b: Optional[str] = None) -> str:
    """Show diff between two versions of a prompt."""
    catalog = load_catalog(catalog_dir)
    versions_dir = catalog_dir / PROMPTS_DIR

    if name not in catalog.entries:
        return f"Prompt '{name}' not found in catalog."

    versions = catalog.entries[name]
    if len(versions) < 2 and not (version_a and version_b):
        return f"Only one version of '{name}' exists. Nothing to diff."

    # Default to last two versions
    if not version_a:
        entry_a = versions[-2]
    else:
        entry_a = next((v for v in versions if v.version == version_a), None)
        if not entry_a:
            return f"Version {version_a} not found for '{name}'."

    if not version_b:
        entry_b = versions[-1]
    else:
        entry_b = next((v for v in versions if v.version == version_b), None)
        if not entry_b:
            return f"Version {version_b} not found for '{name}'."

    file_a = versions_dir / entry_a.content_file
    file_b = versions_dir / entry_b.content_file

    if not file_a.exists() or not file_b.exists():
        return "Content files not found on disk."

    text_a = file_a.read_text(encoding="utf-8").splitlines(keepends=True)
    text_b = file_b.read_text(encoding="utf-8").splitlines(keepends=True)

    diff = difflib.unified_diff(
        text_a, text_b,
        fromfile=f"{name} v{entry_a.version}",
        tofile=f"{name} v{entry_b.version}",
    )
    diff_text = "".join(diff)

    if not diff_text:
        return f"No differences between v{entry_a.version} and v{entry_b.version}."

    lines = []
    lines.append(f"Diff: {name} v{entry_a.version} -> v{entry_b.version}")
    lines.append(f"Tokens: {entry_a.token_estimate} -> {entry_b.token_estimate} "
                 f"({entry_b.token_estimate - entry_a.token_estimate:+d})")
    lines.append("-" * 50)
    lines.append(diff_text)
    return "\n".join(lines)


def update_status(catalog_dir: Path, name: str, status: str,
                  version: Optional[str] = None) -> str:
    """Update the status of a prompt."""
    catalog = load_catalog(catalog_dir)

    if name not in catalog.entries:
        return f"Prompt '{name}' not found."

    valid_statuses = {"draft", "review", "approved", "deployed", "retired"}
    if status not in valid_statuses:
        return f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"

    versions = catalog.entries[name]
    if version:
        entry = next((v for v in versions if v.version == version), None)
        if not entry:
            return f"Version {version} not found."
    else:
        entry = versions[-1]

    old_status = entry.status
    entry.status = status
    entry.updated = datetime.now().isoformat()
    save_catalog(catalog, catalog_dir)

    return f"Updated {name} v{entry.version}: {old_status} -> {status}"


def search_prompts(catalog_dir: Path, query: str) -> str:
    """Search prompts by name, tags, or description."""
    catalog = load_catalog(catalog_dir)
    query_lower = query.lower()
    results = []

    for name, versions in catalog.entries.items():
        latest = versions[-1]
        searchable = f"{name} {latest.description} {' '.join(latest.tags)}".lower()
        if query_lower in searchable:
            results.append((name, latest))

    if not results:
        return f"No prompts matching '{query}'."

    lines = [f"Search results for '{query}' ({len(results)} found):"]
    for name, entry in results:
        lines.append(f"  {name} v{entry.version} ({entry.status}) - {entry.description[:60]}")
    return "\n".join(lines)


def format_json_output(data: str) -> str:
    """Wrap string output as JSON."""
    return json.dumps({"result": data}, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Catalog Manager - Manage versioned prompt catalog"
    )
    parser.add_argument("--catalog-dir", required=True, help="Path to catalog directory")

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--init", action="store_true", help="Initialize new catalog")
    action.add_argument("--add", action="store_true", help="Add prompt to catalog")
    action.add_argument("--list", action="store_true", help="List all prompts")
    action.add_argument("--diff", action="store_true", help="Diff prompt versions")
    action.add_argument("--status", help="Update prompt status (draft/review/approved/deployed/retired)")
    action.add_argument("--search", help="Search prompts by query")

    parser.add_argument("--name", help="Prompt name (for --add, --diff, --status)")
    parser.add_argument("--file", help="Path to prompt content file (for --add)")
    parser.add_argument("--text", help="Prompt text (for --add)")
    parser.add_argument("--author", default="unknown", help="Author name")
    parser.add_argument("--description", default="", help="Prompt description")
    parser.add_argument("--tags", nargs="+", help="Tags for the prompt")
    parser.add_argument("--models", nargs="+", help="Target models")
    parser.add_argument("--version-a", help="First version for diff")
    parser.add_argument("--version-b", help="Second version for diff")
    parser.add_argument("--all-versions", action="store_true", help="Show all versions in list")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format")

    args = parser.parse_args()
    catalog_dir = Path(args.catalog_dir)

    if args.init:
        result = init_catalog(catalog_dir)
    elif args.add:
        if not args.name:
            print("Error: --name required for --add", file=sys.stderr)
            sys.exit(1)
        if args.file:
            content = Path(args.file).read_text(encoding="utf-8")
        elif args.text:
            content = args.text
        else:
            print("Error: --file or --text required for --add", file=sys.stderr)
            sys.exit(1)
        result = add_prompt(catalog_dir, args.name, content,
                           author=args.author, description=args.description,
                           tags=args.tags, model_targets=args.models)
    elif args.list:
        result = list_prompts(catalog_dir, show_all_versions=args.all_versions)
    elif args.diff:
        if not args.name:
            print("Error: --name required for --diff", file=sys.stderr)
            sys.exit(1)
        result = diff_versions(catalog_dir, args.name, args.version_a, args.version_b)
    elif args.status:
        if not args.name:
            print("Error: --name required for --status", file=sys.stderr)
            sys.exit(1)
        result = update_status(catalog_dir, args.name, args.status)
    elif args.search:
        result = search_prompts(catalog_dir, args.search)
    else:
        parser.print_help()
        sys.exit(1)

    if args.format == "json":
        print(format_json_output(result))
    else:
        print(result)


if __name__ == "__main__":
    main()
