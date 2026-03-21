#!/usr/bin/env python3
"""
Skills Index Builder

Builds a skills-index.json manifest from a directory of skills. Scans for
skill directories containing SKILL.md files, extracts metadata, and produces
a structured index for skill registries and discovery systems.

Usage:
    python skills_index_builder.py /path/to/skills
    python skills_index_builder.py /path/to/skills --output skills-index.json
    python skills_index_builder.py /path/to/skills --format human
    python skills_index_builder.py /path/to/skills --category engineering
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


INDEX_VERSION = "1.0.0"


def parse_yaml_frontmatter(content: str) -> Dict[str, Any]:
    """Parse YAML frontmatter from markdown content.

    Returns a flat-ish dict of frontmatter fields.
    """
    result: Dict[str, Any] = {}

    if not content.startswith("---"):
        return result

    lines = content.split("\n")
    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index == -1:
        return result

    fm_lines = lines[1:end_index]
    current_key: Optional[str] = None
    current_value = ""
    nested_dict: Dict[str, str] = {}
    nested_key: Optional[str] = None

    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key
        match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', stripped)
        if match and indent == 0:
            # Save previous
            if current_key:
                if nested_key and nested_dict:
                    result[current_key] = dict(nested_dict)
                    nested_dict = {}
                    nested_key = None
                elif current_value:
                    result[current_key] = current_value.strip()

            current_key = match.group(1)
            val = match.group(2).strip()

            # Remove YAML flow indicators
            if val in (">", "|", "|-", ">-"):
                current_value = ""
            elif val:
                if (val.startswith('"') and val.endswith('"')) or \
                   (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                current_value = val
            else:
                current_value = ""
                nested_key = current_key
            continue

        # Nested key: value
        if indent > 0 and nested_key:
            nested_match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', stripped)
            if nested_match:
                nkey = nested_match.group(1)
                nval = nested_match.group(2).strip()
                if (nval.startswith('"') and nval.endswith('"')) or \
                   (nval.startswith("'") and nval.endswith("'")):
                    nval = nval[1:-1]
                nested_dict[nkey] = nval
                continue

        # Multi-line continuation
        if indent > 0 and current_key:
            if current_value:
                current_value += " " + stripped
            else:
                current_value = stripped

    # Final key
    if current_key:
        if nested_key and nested_dict:
            result[current_key] = dict(nested_dict)
        elif current_value:
            result[current_key] = current_value.strip()

    return result


def detect_platforms(skill_dir: Path) -> List[str]:
    """Detect which platforms a skill supports."""
    platforms = []

    if (skill_dir / "SKILL.md").is_file():
        platforms.append("claude-code")

    if (skill_dir / "agents" / "openai.yaml").is_file():
        platforms.append("codex-cli")

    # Check for other platform markers
    if (skill_dir / ".cursorrules").is_file():
        platforms.append("cursor")

    if (skill_dir / ".github" / "copilot-instructions.md").is_file():
        platforms.append("github-copilot")

    return platforms


def get_directory_size(dir_path: Path) -> int:
    """Calculate total size of all files in a directory."""
    total = 0
    for f in dir_path.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except OSError:
                pass
    return total


def count_files_by_type(dir_path: Path) -> Dict[str, int]:
    """Count files grouped by extension."""
    counts: Dict[str, int] = {}
    for f in dir_path.rglob("*"):
        if f.is_file():
            ext = f.suffix.lower() or "(no extension)"
            counts[ext] = counts.get(ext, 0) + 1
    return counts


def scan_skill(skill_dir: Path) -> Optional[Dict[str, Any]]:
    """Scan a single skill directory and extract metadata.

    Returns None if the directory is not a valid skill.
    """
    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.is_file():
        return None

    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return None

    frontmatter = parse_yaml_frontmatter(content)

    name = frontmatter.get("name", skill_dir.name)
    description = frontmatter.get("description", "")
    license_val = frontmatter.get("license", "")

    # Extract metadata
    metadata = frontmatter.get("metadata", {})
    version = "0.0.0"
    category = ""
    domain = ""
    if isinstance(metadata, dict):
        version = metadata.get("version", "0.0.0")
        category = metadata.get("category", "")
        domain = metadata.get("domain", "")

    # Find scripts
    scripts_dir = skill_dir / "scripts"
    tools: List[str] = []
    if scripts_dir.is_dir():
        tools = sorted([f.name for f in scripts_dir.glob("*.py")])

    # Find references
    refs_dir = skill_dir / "references"
    references: List[str] = []
    if refs_dir.is_dir():
        references = sorted([f.name for f in refs_dir.glob("*.md")])

    # Find assets
    assets_dir = skill_dir / "assets"
    assets: List[str] = []
    if assets_dir.is_dir():
        assets = sorted([f.name for f in assets_dir.iterdir() if f.is_file()])

    # Detect platforms
    platforms = detect_platforms(skill_dir)

    # Calculate size
    total_size = get_directory_size(skill_dir)

    # Extract title from markdown body
    title = ""
    body_start = content.find("\n---\n")
    if body_start >= 0:
        body = content[body_start + 5:]
    else:
        body = content
    for line in body.split("\n"):
        if line.strip().startswith("# "):
            title = line.strip()[2:].strip()
            break

    # Extract keywords if present
    keywords: List[str] = []
    kw_match = re.search(
        r'##\s+Keywords\s*\n+(.+?)(?:\n\n|\n##)',
        content,
        re.DOTALL
    )
    if kw_match:
        kw_text = kw_match.group(1).strip()
        keywords = [k.strip() for k in kw_text.split(",") if k.strip()]

    return {
        "name": name,
        "title": title or name,
        "description": description,
        "version": version,
        "license": license_val,
        "category": category,
        "domain": domain,
        "keywords": keywords,
        "tools": tools,
        "tools_count": len(tools),
        "references": references,
        "references_count": len(references),
        "assets": assets,
        "assets_count": len(assets),
        "platforms": platforms,
        "size_bytes": total_size,
        "size_human": format_size(total_size),
        "path": str(skill_dir.relative_to(skill_dir.parent)),
    }


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def build_index(
    skills_dir: str,
    category_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a skills index from a directory of skill subdirectories.

    Returns the complete index dict.
    """
    path = Path(skills_dir).resolve()

    if not path.is_dir():
        return {
            "error": f"Directory not found: {skills_dir}",
            "version": INDEX_VERSION,
            "skills": [],
            "skills_count": 0,
        }

    skills: List[Dict[str, Any]] = []

    # Scan all subdirectories for SKILL.md
    for item in sorted(path.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue

        skill_data = scan_skill(item)
        if skill_data is None:
            continue

        # Apply category filter
        if category_filter:
            if skill_data.get("category", "").lower() != category_filter.lower():
                continue

        skills.append(skill_data)

    # Build summary stats
    total_tools = sum(s["tools_count"] for s in skills)
    total_refs = sum(s["references_count"] for s in skills)
    total_size = sum(s["size_bytes"] for s in skills)

    categories: Dict[str, int] = {}
    domains: Dict[str, int] = {}
    platform_counts: Dict[str, int] = {}

    for s in skills:
        cat = s.get("category") or "uncategorized"
        categories[cat] = categories.get(cat, 0) + 1

        dom = s.get("domain") or "unspecified"
        domains[dom] = domains.get(dom, 0) + 1

        for p in s.get("platforms", []):
            platform_counts[p] = platform_counts.get(p, 0) + 1

    index = {
        "version": INDEX_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_directory": str(path),
        "skills_count": len(skills),
        "summary": {
            "total_tools": total_tools,
            "total_references": total_refs,
            "total_size": format_size(total_size),
            "total_size_bytes": total_size,
            "categories": categories,
            "domains": domains,
            "platforms": platform_counts,
        },
        "skills": skills,
    }

    return index


def format_human_output(index: Dict[str, Any]) -> str:
    """Format index as human-readable text."""
    lines = []
    lines.append("Skills Index")
    lines.append("=" * 60)
    lines.append(f"Source:     {index.get('source_directory', 'N/A')}")
    lines.append(f"Generated: {index.get('generated_at', 'N/A')}")
    lines.append(f"Skills:    {index.get('skills_count', 0)}")
    lines.append("")

    summary = index.get("summary", {})
    lines.append(f"Total Tools:      {summary.get('total_tools', 0)}")
    lines.append(f"Total References: {summary.get('total_references', 0)}")
    lines.append(f"Total Size:       {summary.get('total_size', '0 B')}")
    lines.append("")

    cats = summary.get("categories", {})
    if cats:
        lines.append("Categories:")
        for cat, count in sorted(cats.items()):
            lines.append(f"  {cat}: {count}")
        lines.append("")

    platforms = summary.get("platforms", {})
    if platforms:
        lines.append("Platform Support:")
        for plat, count in sorted(platforms.items()):
            lines.append(f"  {plat}: {count} skill(s)")
        lines.append("")

    lines.append("-" * 60)
    lines.append(f"{'Name':<30} {'Version':<10} {'Tools':<8} {'Platforms'}")
    lines.append("-" * 60)

    for skill in index.get("skills", []):
        name = skill.get("name", "unknown")
        version = skill.get("version", "?")
        tools = str(skill.get("tools_count", 0))
        platforms_str = ", ".join(skill.get("platforms", []))

        # Truncate name if too long
        if len(name) > 28:
            name = name[:25] + "..."

        lines.append(f"{name:<30} {version:<10} {tools:<8} {platforms_str}")

    lines.append("-" * 60)
    lines.append(f"Total: {index.get('skills_count', 0)} skills")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a skills-index.json manifest from a directory of skills.",
        epilog="Example: python skills_index_builder.py /path/to/skills --output skills-index.json",
    )
    parser.add_argument(
        "skills_dir",
        help="Path to the directory containing skill subdirectories",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: print to stdout)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "human"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--category", "-c",
        default=None,
        help="Filter skills by category",
    )

    args = parser.parse_args()

    if not Path(args.skills_dir).is_dir():
        print(f"Error: '{args.skills_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    index = build_index(args.skills_dir, category_filter=args.category)

    if "error" in index and index["skills_count"] == 0:
        print(f"Error: {index['error']}", file=sys.stderr)
        sys.exit(1)

    if args.format == "human":
        output_text = format_human_output(index)
    else:
        output_text = json.dumps(index, indent=2)

    if args.output:
        output_path = Path(args.output)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_text)
                f.write("\n")
            if args.format == "human":
                print(f"Index written to {output_path}")
            else:
                print(f"Index written to {output_path} ({index['skills_count']} skills)")
        except OSError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
