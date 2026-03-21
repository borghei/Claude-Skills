#!/usr/bin/env python3
"""
Skill Scaffolder - Generate a complete skill package directory

Creates a new skill directory with SKILL.md template, scripts/, references/,
assets/ directories, and properly formatted YAML frontmatter.

Usage:
    python skill_scaffolder.py my-skill --domain engineering --description "Brief desc"
    python skill_scaffolder.py my-skill --domain marketing --description "Campaign tools" --json
    python skill_scaffolder.py my-skill -d product --description "User research" -o /path/to/skills/
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Valid domains for categorization
VALID_DOMAINS = [
    "engineering",
    "marketing",
    "product",
    "project-management",
    "c-level",
    "ra-qm",
    "business-growth",
    "finance",
    "standards",
    "development-tools",
]

# Template for the SKILL.md file
SKILL_MD_TEMPLATE = textwrap.dedent('''\
---
name: {name}
description: >-
  {description}
license: {license}
metadata:
  version: {version}
  category: {category}
  domain: {domain}
---

# {title}

{summary}

## Keywords

{keywords}

---

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
- [Workflows](#workflows)
- [Reference Documentation](#reference-documentation)

---

## Quick Start

```bash
# TODO: Add quick start commands
python scripts/example_tool.py --help
```

---

## Tools Overview

### 1. Example Tool

Description of what this tool does.

```bash
python scripts/example_tool.py input --option value
python scripts/example_tool.py input --json
```

| Parameter | Description |
|-----------|-------------|
| `input` | Description of input parameter |
| `--option` | Description of option |
| `--json` | Output in JSON format |

---

## Workflows

### Workflow 1: Primary Workflow

**Step 1: Description**

```bash
# Command
```

**Step 2: Description**

```bash
# Command
```

---

## Reference Documentation

| Document | Path | Description |
|----------|------|-------------|
| Guide Name | [references/guide.md](references/guide.md) | Description |

---

**Last Updated:** {date}
**Version:** {version}
''')

# Template for a starter Python script
SCRIPT_TEMPLATE = textwrap.dedent('''\
#!/usr/bin/env python3
"""
{title} - {description}

Usage:
    python {filename} --help
    python {filename} input_arg
    python {filename} input_arg --json
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="{description}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python {filename} example_input
    python {filename} example_input --json
        """,
    )
    parser.add_argument("input", help="Input to process")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    result = {{"input": args.input, "status": "success", "message": "TODO: Implement"}}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Input: {{result['input']}}")
        print(f"Status: {{result['status']}}")
        print(f"Message: {{result['message']}}")


if __name__ == "__main__":
    main()
''')

# Template for a starter reference document
REFERENCE_TEMPLATE = textwrap.dedent('''\
# {title}

## Overview

This reference guide covers {topic}.

## Key Concepts

### Concept 1

Description and details.

### Concept 2

Description and details.

## Best Practices

1. **Practice 1** -- Explanation
2. **Practice 2** -- Explanation
3. **Practice 3** -- Explanation

## Examples

### Example 1

```
Example content
```

## Additional Resources

- Resource 1
- Resource 2

---

**Last Updated:** {date}
''')


def to_title_case(name: str) -> str:
    """Convert kebab-case to Title Case."""
    return " ".join(word.capitalize() for word in name.split("-"))


def validate_skill_name(name: str) -> Optional[str]:
    """Validate skill name format. Returns error message or None."""
    if not name:
        return "Skill name cannot be empty"
    if not all(c.isalnum() or c == "-" for c in name):
        return "Skill name must contain only alphanumeric characters and hyphens"
    if name.startswith("-") or name.endswith("-"):
        return "Skill name must not start or end with a hyphen"
    if "--" in name:
        return "Skill name must not contain consecutive hyphens"
    return None


def create_skill_directory(
    skill_name: str,
    domain: str,
    description: str,
    version: str = "1.0.0",
    license_type: str = "MIT",
    category: str = "",
    output_dir: str = ".",
) -> Dict:
    """Create the complete skill directory structure.

    Returns a dict with creation results.
    """
    skill_path = Path(output_dir) / skill_name
    title = to_title_case(skill_name)
    today = datetime.now().strftime("%B %Y")

    if not category:
        category = domain

    # Define directory structure
    directories = [
        skill_path / "scripts",
        skill_path / "references",
        skill_path / "assets",
    ]

    # Check if skill already exists
    if skill_path.exists():
        return {
            "success": False,
            "error": f"Directory already exists: {skill_path}",
            "path": str(skill_path),
        }

    # Create directories
    created_dirs = []
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(d))

    # Generate keywords from name and domain
    keywords = ", ".join(skill_name.split("-") + [domain, category])

    # Create SKILL.md
    skill_md_content = SKILL_MD_TEMPLATE.format(
        name=skill_name,
        description=description,
        license=license_type,
        version=version,
        category=category,
        domain=domain,
        title=title,
        summary=f"{title} skill with automation tools and reference guides.",
        keywords=keywords,
        date=today,
    )
    skill_md_path = skill_path / "SKILL.md"
    skill_md_path.write_text(skill_md_content)

    # Create starter script
    script_name = skill_name.replace("-", "_") + "_tool.py"
    script_content = SCRIPT_TEMPLATE.format(
        title=title + " Tool",
        description=f"Automation tool for {title.lower()}",
        filename=script_name,
    )
    script_path = skill_path / "scripts" / script_name
    script_path.write_text(script_content)
    os.chmod(script_path, 0o755)

    # Create starter reference
    ref_content = REFERENCE_TEMPLATE.format(
        title=f"{title} Guide",
        topic=title.lower(),
        date=today,
    )
    ref_path = skill_path / "references" / "guide.md"
    ref_path.write_text(ref_content)

    # Create .gitkeep in assets (empty directory placeholder)
    gitkeep_path = skill_path / "assets" / ".gitkeep"
    gitkeep_path.write_text("")

    created_files = [
        str(skill_md_path),
        str(script_path),
        str(ref_path),
        str(gitkeep_path),
    ]

    return {
        "success": True,
        "path": str(skill_path.resolve()),
        "name": skill_name,
        "domain": domain,
        "version": version,
        "directories_created": created_dirs,
        "files_created": created_files,
    }


def print_human_readable(result: Dict) -> None:
    """Print results in human-readable format."""
    if not result["success"]:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    print(f"Skill scaffolded successfully!")
    print(f"")
    print(f"  Name:      {result['name']}")
    print(f"  Domain:    {result['domain']}")
    print(f"  Version:   {result['version']}")
    print(f"  Location:  {result['path']}")
    print(f"")
    print(f"Directory structure:")
    print(f"  {result['name']}/")
    print(f"  ├── SKILL.md")
    print(f"  ├── scripts/")
    print(f"  │   └── {result['name'].replace('-', '_')}_tool.py")
    print(f"  ├── references/")
    print(f"  │   └── guide.md")
    print(f"  └── assets/")
    print(f"      └── .gitkeep")
    print(f"")
    print(f"Next steps:")
    print(f"  1. Edit SKILL.md with your skill's workflows and documentation")
    print(f"  2. Implement your Python tools in scripts/")
    print(f"  3. Add deep-dive guides to references/")
    print(f"  4. Add user-facing templates to assets/")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Claude Code skill package with proper structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
Examples:
    python skill_scaffolder.py my-skill --domain engineering --description "Brief desc"
    python skill_scaffolder.py api-analyzer -d engineering --description "API analysis" --json
    python skill_scaffolder.py campaign-planner -d marketing --description "Campaign planning" -o /skills/
        """),
    )
    parser.add_argument(
        "skill_name",
        help="Name for the skill (kebab-case recommended, e.g., my-new-skill)",
    )
    parser.add_argument(
        "--domain",
        "-d",
        default="engineering",
        help=f"Domain category (default: engineering). Options: {', '.join(VALID_DOMAINS)}",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Brief description for YAML frontmatter (optimized for auto-discovery)",
    )
    parser.add_argument(
        "--version",
        default="1.0.0",
        help="Semantic version (default: 1.0.0)",
    )
    parser.add_argument(
        "--license",
        dest="license_type",
        default="MIT",
        help="License type (default: MIT)",
    )
    parser.add_argument(
        "--category",
        default="",
        help="Skill category for metadata (default: same as domain)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Parent directory for the skill folder (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    # Validate skill name
    error = validate_skill_name(args.skill_name)
    if error:
        if args.json:
            print(json.dumps({"success": False, "error": error}))
        else:
            print(f"ERROR: {error}")
        sys.exit(1)

    # Validate domain
    if args.domain not in VALID_DOMAINS:
        warning = f"Warning: '{args.domain}' is not a standard domain. Standard domains: {', '.join(VALID_DOMAINS)}"
        if not args.json:
            print(warning)

    # Generate default description if not provided
    description = args.description
    if not description:
        title = to_title_case(args.skill_name)
        description = (
            f'This skill should be used when the user asks about {title.lower()}. '
            f'Use for {title.lower()} workflows, analysis, and automation.'
        )

    # Validate output directory
    output_path = Path(args.output)
    if not output_path.exists():
        if args.json:
            print(json.dumps({"success": False, "error": f"Output directory does not exist: {args.output}"}))
        else:
            print(f"ERROR: Output directory does not exist: {args.output}")
        sys.exit(1)

    # Create the skill
    result = create_skill_directory(
        skill_name=args.skill_name,
        domain=args.domain,
        description=description,
        version=args.version,
        license_type=args.license_type,
        category=args.category,
        output_dir=args.output,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_readable(result)

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
