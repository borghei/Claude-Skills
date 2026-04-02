#!/usr/bin/env python3
"""
Skill Scaffolder - Generate new skill skeletons for the Claude Skills Library

Creates a complete skill directory structure with pre-filled SKILL.md template,
empty subdirectories, and correct YAML frontmatter following repository standards.

Usage:
    python scripts/create_skill.py engineering/my-new-skill
    python scripts/create_skill.py engineering/my-new-skill --author borghei
    python scripts/create_skill.py marketing/my-skill --domain seo --tags "seo,content"
    python scripts/create_skill.py finance/budget-planner --description "Budget planning toolkit"
"""

import argparse
import os
import sys
import textwrap
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_DOMAINS = [
    "business-growth",
    "c-level-advisor",
    "data-analytics",
    "engineering",
    "finance",
    "hr-operations",
    "marketing",
    "product-team",
    "project-management",
    "ra-qm-team",
    "sales-success",
]

DOMAIN_CATEGORIES = {
    "business-growth": "business-growth",
    "c-level-advisor": "leadership",
    "data-analytics": "data",
    "engineering": "engineering",
    "finance": "finance",
    "hr-operations": "hr",
    "marketing": "marketing",
    "product-team": "product",
    "project-management": "project-management",
    "ra-qm-team": "compliance",
    "sales-success": "sales",
}

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

USE_COLOR = True


def _c(code: str, text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str:
    return _c("32", t)


def yellow(t: str) -> str:
    return _c("33", t)


def red(t: str) -> str:
    return _c("31", t)


def bold(t: str) -> str:
    return _c("1", t)


def dim(t: str) -> str:
    return _c("2", t)


# ---------------------------------------------------------------------------
# SKILL.md template
# ---------------------------------------------------------------------------

def generate_skill_md(
    name: str,
    description: str,
    author: str,
    domain_dir: str,
    subdomain: str,
    tags: list[str],
    category: str,
) -> str:
    """Generate a complete SKILL.md with YAML frontmatter and section templates."""

    today = date.today().isoformat()
    title = name.replace("-", " ").title()
    tag_list = ", ".join(tags) if tags else "TODO"

    return textwrap.dedent(f"""\
        ---
        name: {name}
        description: >
          TODO: Write a 1-3 sentence description of when this skill should be used.
          Include specific trigger phrases like "design X", "review Y", "optimize Z".
        license: MIT + Commons Clause
        metadata:
          version: 1.0.0
          author: {author}
          category: {category}
          domain: {subdomain or 'TODO'}
          updated: {today}
          tags: [{tag_list}]
        ---
        # {title}

        {description}

        ## Table of Contents

        - [Quick Start](#quick-start)
        - [Tools Overview](#tools-overview)
        - [Workflows](#workflows)
        - [Anti-Patterns](#anti-patterns)
        - [Reference Documentation](#reference-documentation)

        ---

        ## Quick Start

        <!-- TODO: Add 2-3 example commands showing the most common uses -->

        ```bash
        # Example: Run the primary tool
        python scripts/TODO_tool_name.py --help
        ```

        ---

        ## Tools Overview

        <!-- TODO: Document each script in scripts/ directory -->
        <!-- Each tool should have: description, input, output, example usage -->

        ### 1. TODO: First Tool Name

        **Description:** TODO: What this tool does
        **Input:** TODO: Expected input format
        **Output:** TODO: What it produces

        ```bash
        python scripts/TODO_tool_name.py --example
        ```

        ---

        ## Workflows

        <!-- TODO: Define step-by-step workflows that combine tools and references -->
        <!-- Each workflow should solve a specific problem end-to-end -->

        ### TODO: Primary Workflow Name

        1. **Step 1** - TODO: First step description
        2. **Step 2** - TODO: Second step description
        3. **Step 3** - TODO: Third step description

        ---

        ## Anti-Patterns

        <!-- TODO: Document common mistakes and what to do instead -->

        | Anti-Pattern | Why It Fails | Do This Instead |
        |---|---|---|
        | TODO: Bad practice | TODO: Explanation | TODO: Better approach |

        ---

        ## Reference Documentation

        <!-- TODO: List reference files in references/ directory -->
        <!-- Each reference should be a focused knowledge base on a specific topic -->

        - `references/TODO.md` - TODO: Description of reference content

        ---

        **Last Updated:** {today}
    """)


# ---------------------------------------------------------------------------
# Scaffolding logic
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    """Walk up from this script to find the repo root (contains skills.json)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "skills.json").exists():
            return current
        current = current.parent
    # Fallback: assume script is in scripts/ at repo root
    return Path(__file__).resolve().parent.parent


def create_skill(
    skill_path: str,
    author: str,
    domain: str | None,
    tags: list[str],
    description: str | None,
    dry_run: bool,
    format_json: bool,
) -> int:
    """Create a new skill skeleton at the given path."""

    repo_root = find_repo_root()

    # Parse domain/skill-name from path
    parts = skill_path.strip("/").split("/")
    if len(parts) < 2:
        print(red("Error: Path must be domain/skill-name (e.g. engineering/my-skill)"))
        return 1

    domain_dir = parts[0]
    skill_name = parts[1]

    # Validate domain
    if domain_dir not in VALID_DOMAINS:
        print(red(f"Error: Unknown domain '{domain_dir}'"))
        print(f"Valid domains: {', '.join(VALID_DOMAINS)}")
        return 1

    # Validate skill name
    if not all(c.isalnum() or c in "-_" for c in skill_name):
        print(red("Error: Skill name must contain only alphanumeric characters, hyphens, or underscores"))
        return 1

    target_dir = repo_root / domain_dir / skill_name

    # Check if skill already exists
    if target_dir.exists():
        print(red(f"Error: Skill already exists at {target_dir}"))
        return 1

    subdomain = domain or ""
    category = DOMAIN_CATEGORIES.get(domain_dir, domain_dir)
    desc = description or f"TODO: Describe what the {skill_name.replace('-', ' ')} skill does."

    if dry_run:
        if format_json:
            import json
            print(json.dumps({
                "action": "dry_run",
                "target": str(target_dir),
                "files": [
                    str(target_dir / "SKILL.md"),
                    str(target_dir / "scripts" / ".gitkeep"),
                    str(target_dir / "references" / ".gitkeep"),
                    str(target_dir / "examples" / ".gitkeep"),
                ],
                "domain": domain_dir,
                "skill_name": skill_name,
                "author": author,
                "tags": tags,
            }, indent=2))
        else:
            print(bold("Dry run — would create:"))
            print(f"  {target_dir}/")
            print(f"  ├── SKILL.md")
            print(f"  ├── scripts/           {dim('.gitkeep')}")
            print(f"  ├── references/        {dim('.gitkeep')}")
            print(f"  └── examples/          {dim('.gitkeep')}")
        return 0

    # Create directories
    for subdir in ["scripts", "references", "examples"]:
        (target_dir / subdir).mkdir(parents=True, exist_ok=True)
        (target_dir / subdir / ".gitkeep").touch()

    # Generate SKILL.md
    skill_md = generate_skill_md(
        name=skill_name,
        description=desc,
        author=author,
        domain_dir=domain_dir,
        subdomain=subdomain,
        tags=tags,
        category=category,
    )
    (target_dir / "SKILL.md").write_text(skill_md)

    # Output
    if format_json:
        import json
        print(json.dumps({
            "action": "created",
            "target": str(target_dir),
            "files": [
                str(target_dir / "SKILL.md"),
                str(target_dir / "scripts" / ".gitkeep"),
                str(target_dir / "references" / ".gitkeep"),
                str(target_dir / "examples" / ".gitkeep"),
            ],
            "domain": domain_dir,
            "skill_name": skill_name,
        }, indent=2))
    else:
        print(green("✓") + f" Created skill: {bold(skill_name)}")
        print(f"  Location: {target_dir}")
        print()
        print(f"  {target_dir}/")
        print(f"  ├── SKILL.md           {dim('← Edit this first')}")
        print(f"  ├── scripts/           {dim('← Add Python CLI tools')}")
        print(f"  ├── references/        {dim('← Add knowledge bases')}")
        print(f"  └── examples/          {dim('← Add usage examples')}")
        print()
        print(dim("Next steps:"))
        print(f"  1. Edit {target_dir / 'SKILL.md'} — fill in TODO placeholders")
        print(f"  2. Add scripts to {target_dir / 'scripts/'}")
        print(f"  3. Add reference docs to {target_dir / 'references/'}")

    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new skill for the Claude Skills Library",
        epilog="Example: python scripts/create_skill.py engineering/my-skill --author borghei",
    )
    parser.add_argument(
        "path",
        help="Skill path as domain/skill-name (e.g. engineering/my-new-skill)",
    )
    parser.add_argument(
        "--author",
        default="borghei",
        help="Skill author (default: borghei)",
    )
    parser.add_argument(
        "--domain",
        default=None,
        help="Subdomain within the category (e.g. seo, backend, devops)",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags (e.g. 'seo,content,strategy')",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Short description for the skill",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing files",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colorized output",
    )

    args = parser.parse_args()

    global USE_COLOR
    if args.no_color or not sys.stdout.isatty():
        USE_COLOR = False

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    return create_skill(
        skill_path=args.path,
        author=args.author,
        domain=args.domain,
        tags=tags,
        description=args.description,
        dry_run=args.dry_run,
        format_json=(args.format == "json"),
    )


if __name__ == "__main__":
    sys.exit(main())
