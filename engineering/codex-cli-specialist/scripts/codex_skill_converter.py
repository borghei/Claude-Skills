#!/usr/bin/env python3
"""
Codex Skill Converter

Converts a Claude Code SKILL.md into Codex-compatible format by generating
an agents/openai.yaml configuration file alongside the existing skill.

Usage:
    python codex_skill_converter.py path/to/SKILL.md
    python codex_skill_converter.py path/to/SKILL.md --output-dir ./converted
    python codex_skill_converter.py path/to/SKILL.md --json
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_yaml_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Returns a tuple of (frontmatter_dict, body_content).
    Uses a simple parser to avoid external dependencies.
    """
    frontmatter: Dict[str, Any] = {}
    body = content

    if not content.startswith("---"):
        return frontmatter, body

    lines = content.split("\n")
    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index == -1:
        return frontmatter, body

    fm_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1:]).lstrip("\n")

    # Simple YAML key-value parser (handles flat keys and nested metadata)
    current_key = None
    current_indent = 0

    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key: value
        match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', stripped)
        if match and indent == 0:
            key = match.group(1)
            value = match.group(2).strip()
            if value:
                # Remove surrounding quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                frontmatter[key] = value
            else:
                frontmatter[key] = {}
            current_key = key
            current_indent = indent
            continue

        # Nested key: value (under metadata, codex, etc.)
        if indent > 0 and current_key and isinstance(frontmatter.get(current_key), dict):
            nested_match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', stripped)
            if nested_match:
                nkey = nested_match.group(1)
                nval = nested_match.group(2).strip()
                if (nval.startswith('"') and nval.endswith('"')) or \
                   (nval.startswith("'") and nval.endswith("'")):
                    nval = nval[1:-1]
                frontmatter[current_key][nkey] = nval
                continue

        # Multi-line description continuation
        if current_key == "description" and indent > 0 and isinstance(frontmatter.get("description"), str):
            frontmatter["description"] += " " + stripped

    return frontmatter, body


def extract_title(body: str) -> str:
    """Extract the first H1 title from markdown body."""
    for line in body.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_scripts(skill_dir: Path) -> List[Dict[str, str]]:
    """Find Python scripts in the skill's scripts/ directory."""
    scripts_dir = skill_dir / "scripts"
    tools = []

    if not scripts_dir.is_dir():
        return tools

    for script_path in sorted(scripts_dir.glob("*.py")):
        name = script_path.stem
        # Read first docstring for description
        description = f"Runs {script_path.name}"
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Extract module docstring
            doc_match = re.search(r'^"""(.*?)"""', content, re.DOTALL)
            if not doc_match:
                doc_match = re.search(r"^'''(.*?)'''", content, re.DOTALL)
            if doc_match:
                doc_text = doc_match.group(1).strip()
                # Take just the first line or sentence
                first_line = doc_text.split("\n")[0].strip()
                if first_line:
                    description = first_line
        except (OSError, UnicodeDecodeError):
            pass

        tools.append({
            "name": name,
            "description": description,
            "command": f"python scripts/{script_path.name}",
        })

    return tools


def build_instructions(frontmatter: Dict[str, Any], body: str, title: str) -> str:
    """Build Codex instructions from the skill's content."""
    lines = []

    lines.append(f"You are an expert {title.lower()} specialist.")
    lines.append("")

    # Extract description for context
    desc = frontmatter.get("description", "")
    if desc:
        lines.append(f"## Purpose")
        lines.append(desc)
        lines.append("")

    # Extract key sections from the body for instructions
    sections = extract_key_sections(body)
    if sections.get("workflows"):
        lines.append("## Key Workflows")
        for wf in sections["workflows"][:5]:  # Limit to 5 workflows
            lines.append(f"- {wf}")
        lines.append("")

    if sections.get("best_practices"):
        lines.append("## Best Practices")
        for bp in sections["best_practices"][:8]:
            lines.append(f"- {bp}")
        lines.append("")

    lines.append("## Output Standards")
    lines.append("- Provide clear, actionable guidance")
    lines.append("- Show concrete examples when possible")
    lines.append("- Reference available tools when relevant")
    lines.append("- Use the scripts in the scripts/ directory for automation")

    return "\n".join(lines)


def extract_key_sections(body: str) -> Dict[str, List[str]]:
    """Extract workflow names and best practices from markdown body."""
    result: Dict[str, List[str]] = {"workflows": [], "best_practices": []}

    lines = body.split("\n")
    in_best_practices = False

    for line in lines:
        stripped = line.strip()

        # Find workflow section headers (### Workflow N: Title)
        wf_match = re.match(r'^###\s+(?:Workflow\s+\d+[:.]\s*)?(.+)', stripped)
        if wf_match and "workflow" in stripped.lower():
            result["workflows"].append(wf_match.group(1).strip())

        # Detect best practices sections
        if re.match(r'^#{1,3}\s+[Bb]est\s+[Pp]ractices', stripped):
            in_best_practices = True
            continue

        # Next heading exits best practices
        if in_best_practices and re.match(r'^#{1,3}\s+', stripped):
            in_best_practices = False
            continue

        # Collect numbered or bulleted items in best practices
        if in_best_practices:
            bp_match = re.match(r'^[\d]+[.)]\s+\*\*(.+?)\*\*', stripped)
            if bp_match:
                result["best_practices"].append(bp_match.group(1).strip())
            elif stripped.startswith("- ") or stripped.startswith("* "):
                text = stripped.lstrip("-* ").strip()
                if text and not text.startswith("```"):
                    result["best_practices"].append(text)

    return result


def generate_openai_yaml(
    name: str,
    description: str,
    instructions: str,
    tools: List[Dict[str, str]],
    version: str = "1.0.0",
    model: Optional[str] = None,
) -> str:
    """Generate the agents/openai.yaml content."""
    lines = []

    lines.append(f"name: {name}")
    lines.append("description: >")
    # Wrap description at ~78 chars
    desc_words = description.split()
    current_line = "  "
    for word in desc_words:
        if len(current_line) + len(word) + 1 > 78:
            lines.append(current_line.rstrip())
            current_line = "  " + word
        else:
            current_line += (" " if len(current_line.strip()) > 0 else "") + word
    if current_line.strip():
        lines.append(current_line.rstrip())

    lines.append("instructions: |")
    for inst_line in instructions.split("\n"):
        if inst_line:
            lines.append(f"  {inst_line}")
        else:
            lines.append("")

    if tools:
        lines.append("tools:")
        for tool in tools:
            lines.append(f"  - name: {tool['name']}")
            lines.append(f"    description: >")
            lines.append(f"      {tool['description']}")
            lines.append(f"    command: {tool['command']}")

    if model:
        lines.append(f"model: {model}")

    lines.append(f"version: {version}")

    return "\n".join(lines) + "\n"


def convert_skill(
    skill_md_path: str,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert a Claude Code SKILL.md to Codex-compatible format.

    Returns a result dict with status, warnings, and generated files.
    """
    result: Dict[str, Any] = {
        "status": "success",
        "source": str(skill_md_path),
        "output_dir": "",
        "files_generated": [],
        "files_copied": [],
        "warnings": [],
        "errors": [],
    }

    skill_md = Path(skill_md_path).resolve()

    if not skill_md.is_file():
        result["status"] = "error"
        result["errors"].append(f"File not found: {skill_md}")
        return result

    if skill_md.name != "SKILL.md":
        result["warnings"].append(
            f"Expected filename 'SKILL.md', got '{skill_md.name}'. Proceeding anyway."
        )

    skill_dir = skill_md.parent

    # Determine output directory
    if output_dir:
        out_path = Path(output_dir).resolve()
    else:
        out_path = skill_dir

    result["output_dir"] = str(out_path)

    # Read and parse SKILL.md
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        result["status"] = "error"
        result["errors"].append(f"Cannot read {skill_md}: {e}")
        return result

    frontmatter, body = parse_yaml_frontmatter(content)

    if not frontmatter:
        result["warnings"].append("No YAML frontmatter found. Using defaults.")

    # Extract key fields
    name = frontmatter.get("name", skill_dir.name)
    description = frontmatter.get("description", "")
    title = extract_title(body) or name

    if not description:
        description = f"Expert guidance for {title}."
        result["warnings"].append("No description in frontmatter. Generated a default.")

    # Extract metadata
    metadata = frontmatter.get("metadata", {})
    version = "1.0.0"
    if isinstance(metadata, dict):
        version = metadata.get("version", "1.0.0")

    # Check for Codex-specific hints
    codex_hints = frontmatter.get("codex", {})
    model = None
    if isinstance(codex_hints, dict):
        model = codex_hints.get("model")

    # Find scripts
    tools = extract_scripts(skill_dir)

    # Build instructions
    instructions = build_instructions(frontmatter, body, title)

    # Generate openai.yaml
    yaml_content = generate_openai_yaml(
        name=name,
        description=description,
        instructions=instructions,
        tools=tools,
        version=version,
        model=model,
    )

    # Create output directory structure
    try:
        agents_dir = out_path / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        yaml_path = agents_dir / "openai.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        result["files_generated"].append(str(yaml_path))

    except OSError as e:
        result["status"] = "error"
        result["errors"].append(f"Cannot write output: {e}")
        return result

    # If output dir differs from source, copy other files
    if out_path != skill_dir:
        for subdir in ["scripts", "references", "assets"]:
            src = skill_dir / subdir
            dst = out_path / subdir
            if src.is_dir():
                try:
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    result["files_copied"].append(str(dst))
                except OSError as e:
                    result["warnings"].append(f"Could not copy {subdir}/: {e}")

        # Copy SKILL.md
        dst_skill = out_path / "SKILL.md"
        try:
            shutil.copy2(skill_md, dst_skill)
            result["files_copied"].append(str(dst_skill))
        except OSError as e:
            result["warnings"].append(f"Could not copy SKILL.md: {e}")

    # Check for existing openai.yaml that was overwritten
    if (skill_dir / "agents" / "openai.yaml").is_file() and out_path == skill_dir:
        result["warnings"].append(
            "Overwrote existing agents/openai.yaml. Previous version not backed up."
        )

    return result


def format_human_output(result: Dict[str, Any]) -> str:
    """Format result as human-readable text."""
    lines = []
    lines.append("Codex Skill Converter")
    lines.append("=" * 40)
    lines.append("")
    lines.append(f"Source:     {result['source']}")
    lines.append(f"Output:    {result['output_dir']}")
    lines.append(f"Status:    {result['status'].upper()}")
    lines.append("")

    if result["files_generated"]:
        lines.append("Files Generated:")
        for f in result["files_generated"]:
            lines.append(f"  + {f}")
        lines.append("")

    if result["files_copied"]:
        lines.append("Files Copied:")
        for f in result["files_copied"]:
            lines.append(f"  > {f}")
        lines.append("")

    if result["warnings"]:
        lines.append("Warnings:")
        for w in result["warnings"]:
            lines.append(f"  ! {w}")
        lines.append("")

    if result["errors"]:
        lines.append("Errors:")
        for e in result["errors"]:
            lines.append(f"  X {e}")
        lines.append("")

    if result["status"] == "success":
        lines.append("Conversion complete. Review agents/openai.yaml before deploying.")
    else:
        lines.append("Conversion failed. See errors above.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a Claude Code SKILL.md into Codex-compatible format.",
        epilog="Example: python codex_skill_converter.py path/to/SKILL.md --output-dir ./converted",
    )
    parser.add_argument(
        "skill_md",
        help="Path to the Claude Code SKILL.md file to convert",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for the converted skill (default: same as source)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    result = convert_skill(args.skill_md, args.output_dir)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_human_output(result))

    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
