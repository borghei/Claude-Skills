#!/usr/bin/env python3
"""
Cross-Platform Skill Validator

Validates that a skill directory is compatible with both Claude Code and
Codex CLI. Checks YAML frontmatter, file structure, description format,
and agents/openai.yaml configuration.

Usage:
    python cross_platform_validator.py path/to/skill-dir
    python cross_platform_validator.py path/to/skill-dir --strict
    python cross_platform_validator.py path/to/skill-dir --json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ValidationResult:
    """Holds a single validation check result."""

    def __init__(self, check: str, platform: str, passed: bool,
                 message: str, severity: str = "error"):
        self.check = check
        self.platform = platform
        self.passed = passed
        self.message = message
        self.severity = severity  # "error", "warning", "info"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check,
            "platform": self.platform,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
        }


def parse_yaml_frontmatter_simple(content: str) -> Tuple[Dict[str, str], bool]:
    """Simple YAML frontmatter parser. Returns (dict, is_valid)."""
    result: Dict[str, str] = {}

    if not content.startswith("---"):
        return result, False

    lines = content.split("\n")
    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index == -1:
        return result, False

    fm_lines = lines[1:end_index]
    current_key = None
    current_value = ""

    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key: value
        match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', stripped)
        if match and indent == 0:
            if current_key and current_value:
                result[current_key] = current_value.strip()
            current_key = match.group(1)
            current_value = match.group(2).strip()
            # Remove quotes
            if (current_value.startswith('"') and current_value.endswith('"')) or \
               (current_value.startswith("'") and current_value.endswith("'")):
                current_value = current_value[1:-1]
            continue

        # Continuation of multi-line value
        if indent > 0 and current_key:
            if current_key in ("description",):
                current_value += " " + stripped
            elif ":" in stripped:
                # Nested key - store parent as marker
                if current_key not in result:
                    result[current_key] = "__nested__"

    if current_key and current_value:
        result[current_key] = current_value.strip()

    return result, True


def parse_openai_yaml_simple(content: str) -> Tuple[Dict[str, Any], bool]:
    """Simple parser for agents/openai.yaml. Returns (dict, is_valid)."""
    result: Dict[str, Any] = {}

    lines = content.split("\n")
    current_key = None
    current_value = ""
    tools_list: List[Dict[str, str]] = []
    in_tools = False
    current_tool: Dict[str, str] = {}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key
        top_match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', stripped)
        if top_match and indent == 0:
            # Save previous key
            if current_key and current_value and current_key != "tools":
                result[current_key] = current_value.strip()
            if in_tools and current_tool:
                tools_list.append(current_tool)
                current_tool = {}

            current_key = top_match.group(1)
            val = top_match.group(2).strip()

            if current_key == "tools":
                in_tools = True
                current_value = ""
                continue

            in_tools = False
            if val in (">", "|", "|-", ">-"):
                current_value = ""
            else:
                current_value = val
            continue

        # Inside tools section
        if in_tools:
            if stripped.startswith("- name:"):
                if current_tool:
                    tools_list.append(current_tool)
                current_tool = {"name": stripped.split(":", 1)[1].strip()}
            elif ":" in stripped and current_tool:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v in (">", "|"):
                    current_tool[k] = ""
                elif v:
                    current_tool[k] = v
                elif k in current_tool and not current_tool[k]:
                    pass  # Multi-line continuation handled below
            elif current_tool:
                # Continuation line for tool field
                for tk in ("description", "command"):
                    if tk in current_tool and not current_tool[tk]:
                        current_tool[tk] = stripped
                        break
            continue

        # Multi-line value continuation
        if indent > 0 and current_key:
            if current_value:
                current_value += " " + stripped
            else:
                current_value = stripped

    # Finalize
    if current_key and current_value and current_key != "tools":
        result[current_key] = current_value.strip()
    if in_tools and current_tool:
        tools_list.append(current_tool)
    if tools_list:
        result["tools"] = tools_list

    return result, bool(result)


def validate_skill(skill_dir: str, strict: bool = False) -> Dict[str, Any]:
    """Validate a skill directory for cross-platform compatibility.

    Returns a validation report dict.
    """
    path = Path(skill_dir).resolve()
    checks: List[ValidationResult] = []
    skill_name = path.name

    # =========================================================
    # Claude Code Compatibility Checks
    # =========================================================

    # Check 1: SKILL.md exists
    skill_md_path = path / "SKILL.md"
    if skill_md_path.is_file():
        checks.append(ValidationResult(
            "skill_md_exists", "claude-code", True,
            "SKILL.md exists"
        ))
    else:
        checks.append(ValidationResult(
            "skill_md_exists", "claude-code", False,
            "SKILL.md not found - required for Claude Code",
            "error"
        ))

    # Check 2: Valid YAML frontmatter
    frontmatter: Dict[str, str] = {}
    if skill_md_path.is_file():
        try:
            with open(skill_md_path, "r", encoding="utf-8") as f:
                content = f.read()
            frontmatter, fm_valid = parse_yaml_frontmatter_simple(content)
            if fm_valid:
                checks.append(ValidationResult(
                    "valid_frontmatter", "claude-code", True,
                    "Valid YAML frontmatter found"
                ))
            else:
                checks.append(ValidationResult(
                    "valid_frontmatter", "claude-code", False,
                    "No valid YAML frontmatter (must start with --- and end with ---)",
                    "error"
                ))
        except (OSError, UnicodeDecodeError) as e:
            checks.append(ValidationResult(
                "valid_frontmatter", "claude-code", False,
                f"Cannot read SKILL.md: {e}",
                "error"
            ))

    # Check 3: Name field present
    if frontmatter.get("name"):
        checks.append(ValidationResult(
            "name_field", "claude-code", True,
            f"Name field present: {frontmatter['name']}"
        ))
        skill_name = frontmatter["name"]
    else:
        checks.append(ValidationResult(
            "name_field", "claude-code", False,
            "Name field missing in frontmatter",
            "error"
        ))

    # Check 4: Description field present and third-person
    desc = frontmatter.get("description", "")
    if desc:
        checks.append(ValidationResult(
            "description_exists", "claude-code", True,
            "Description field present"
        ))

        # Check third-person / discovery format
        discovery_patterns = [
            r"this skill",
            r"should be used when",
            r"use for",
            r"use when",
            r"analyzes",
            r"generates",
            r"provides",
            r"automates",
        ]
        has_discovery_pattern = any(
            re.search(pat, desc, re.IGNORECASE) for pat in discovery_patterns
        )
        if has_discovery_pattern:
            checks.append(ValidationResult(
                "description_format", "claude-code", True,
                "Description uses discovery-friendly format"
            ))
        else:
            checks.append(ValidationResult(
                "description_format", "claude-code", False,
                "Description should use third-person, discovery-friendly format "
                "(e.g., 'This skill should be used when...')",
                "warning"
            ))
    else:
        checks.append(ValidationResult(
            "description_exists", "claude-code", False,
            "Description field missing in frontmatter",
            "error"
        ))

    # Check 5: License field
    if frontmatter.get("license"):
        checks.append(ValidationResult(
            "license_field", "claude-code", True,
            f"License: {frontmatter['license']}"
        ))
    else:
        checks.append(ValidationResult(
            "license_field", "claude-code", False,
            "License field missing (recommended for distribution)",
            "warning"
        ))

    # Check 6: Scripts directory
    scripts_dir = path / "scripts"
    if scripts_dir.is_dir():
        py_scripts = list(scripts_dir.glob("*.py"))
        if py_scripts:
            checks.append(ValidationResult(
                "scripts_dir", "claude-code", True,
                f"scripts/ directory found ({len(py_scripts)} Python tool(s))"
            ))
        else:
            checks.append(ValidationResult(
                "scripts_dir", "claude-code", False,
                "scripts/ directory exists but contains no Python files",
                "warning"
            ))
    else:
        checks.append(ValidationResult(
            "scripts_dir", "claude-code", False,
            "scripts/ directory not found (optional but recommended)",
            "warning"
        ))

    # Check 7: References directory
    refs_dir = path / "references"
    if refs_dir.is_dir():
        ref_files = list(refs_dir.glob("*.md"))
        checks.append(ValidationResult(
            "references_dir", "claude-code", True,
            f"references/ directory found ({len(ref_files)} file(s))"
        ))
    else:
        checks.append(ValidationResult(
            "references_dir", "claude-code", False,
            "references/ directory not found (optional)",
            "info"
        ))

    # Check 8: Assets directory
    assets_dir = path / "assets"
    if assets_dir.is_dir():
        asset_files = list(assets_dir.iterdir())
        asset_count = len([f for f in asset_files if f.is_file()])
        checks.append(ValidationResult(
            "assets_dir", "claude-code", True,
            f"assets/ directory found ({asset_count} file(s))"
        ))
    else:
        checks.append(ValidationResult(
            "assets_dir", "claude-code", False,
            "assets/ directory not found (optional)",
            "info"
        ))

    # Check 9: No requirements.txt or heavy dependencies
    req_file = path / "requirements.txt"
    if req_file.is_file():
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                deps = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            if deps:
                checks.append(ValidationResult(
                    "no_heavy_deps", "claude-code", False,
                    f"requirements.txt found with {len(deps)} dependencies "
                    f"(skills should use standard library only)",
                    "warning"
                ))
        except OSError:
            pass
    else:
        checks.append(ValidationResult(
            "no_heavy_deps", "claude-code", True,
            "No requirements.txt (standard library only - good)"
        ))

    # =========================================================
    # Codex CLI Compatibility Checks
    # =========================================================

    # Check 10: agents/openai.yaml exists
    yaml_path = path / "agents" / "openai.yaml"
    if yaml_path.is_file():
        checks.append(ValidationResult(
            "openai_yaml_exists", "codex-cli", True,
            "agents/openai.yaml exists"
        ))
    else:
        checks.append(ValidationResult(
            "openai_yaml_exists", "codex-cli", False,
            "agents/openai.yaml not found - required for Codex CLI",
            "error"
        ))

    # Check 11: Valid YAML structure
    yaml_data: Dict[str, Any] = {}
    if yaml_path.is_file():
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_content = f.read()
            yaml_data, yaml_valid = parse_openai_yaml_simple(yaml_content)
            if yaml_valid:
                checks.append(ValidationResult(
                    "openai_yaml_valid", "codex-cli", True,
                    "agents/openai.yaml has valid structure"
                ))
            else:
                checks.append(ValidationResult(
                    "openai_yaml_valid", "codex-cli", False,
                    "agents/openai.yaml appears empty or invalid",
                    "error"
                ))
        except (OSError, UnicodeDecodeError) as e:
            checks.append(ValidationResult(
                "openai_yaml_valid", "codex-cli", False,
                f"Cannot read agents/openai.yaml: {e}",
                "error"
            ))

    # Check 12: Name field in openai.yaml
    if yaml_data.get("name"):
        checks.append(ValidationResult(
            "yaml_name", "codex-cli", True,
            f"Name field present: {yaml_data['name']}"
        ))

        # Check name matches SKILL.md
        if skill_name and yaml_data["name"] != skill_name:
            checks.append(ValidationResult(
                "name_match", "cross-platform", False,
                f"Name mismatch: SKILL.md has '{skill_name}', "
                f"openai.yaml has '{yaml_data['name']}'",
                "warning"
            ))
        else:
            checks.append(ValidationResult(
                "name_match", "cross-platform", True,
                "Skill name matches across platforms"
            ))
    elif yaml_path.is_file():
        checks.append(ValidationResult(
            "yaml_name", "codex-cli", False,
            "Name field missing in agents/openai.yaml",
            "error"
        ))

    # Check 13: Description in openai.yaml
    if yaml_data.get("description"):
        checks.append(ValidationResult(
            "yaml_description", "codex-cli", True,
            "Description field present in openai.yaml"
        ))
    elif yaml_path.is_file():
        checks.append(ValidationResult(
            "yaml_description", "codex-cli", False,
            "Description field missing in agents/openai.yaml",
            "error"
        ))

    # Check 14: Instructions in openai.yaml
    if yaml_data.get("instructions"):
        inst_len = len(yaml_data["instructions"])
        if inst_len > 50:
            checks.append(ValidationResult(
                "yaml_instructions", "codex-cli", True,
                f"Instructions field present ({inst_len} chars)"
            ))
        else:
            checks.append(ValidationResult(
                "yaml_instructions", "codex-cli", False,
                f"Instructions field is very short ({inst_len} chars) - "
                "consider adding more detail",
                "warning"
            ))
    elif yaml_path.is_file():
        checks.append(ValidationResult(
            "yaml_instructions", "codex-cli", False,
            "Instructions field missing in agents/openai.yaml",
            "warning"
        ))

    # Check 15: Tools in openai.yaml reference existing scripts
    if yaml_data.get("tools") and isinstance(yaml_data["tools"], list):
        for tool in yaml_data["tools"]:
            cmd = tool.get("command", "")
            # Extract script path from command
            script_match = re.search(r'scripts/(\S+)', cmd)
            if script_match:
                script_file = path / "scripts" / script_match.group(1)
                if script_file.is_file():
                    checks.append(ValidationResult(
                        f"tool_script_{tool.get('name', 'unknown')}", "codex-cli", True,
                        f"Tool '{tool.get('name', 'unknown')}' references existing script"
                    ))
                else:
                    checks.append(ValidationResult(
                        f"tool_script_{tool.get('name', 'unknown')}", "codex-cli", False,
                        f"Tool '{tool.get('name', 'unknown')}' references "
                        f"missing script: {script_match.group(1)}",
                        "error"
                    ))

    # =========================================================
    # Cross-Platform Checks
    # =========================================================

    # Check 16: File encoding (UTF-8)
    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix in (".md", ".yaml", ".yml", ".py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError:
                checks.append(ValidationResult(
                    "utf8_encoding", "cross-platform", False,
                    f"File not UTF-8 encoded: {file_path.relative_to(path)}",
                    "error"
                ))
                break
    else:
        checks.append(ValidationResult(
            "utf8_encoding", "cross-platform", True,
            "All text files are UTF-8 encoded"
        ))

    # Check 17: Skill size
    total_size = sum(
        f.stat().st_size for f in path.rglob("*") if f.is_file()
    )
    size_kb = total_size / 1024
    if size_kb < 1024:
        checks.append(ValidationResult(
            "skill_size", "cross-platform", True,
            f"Skill size: {size_kb:.1f} KB (under 1 MB - good)"
        ))
    else:
        checks.append(ValidationResult(
            "skill_size", "cross-platform", False,
            f"Skill size: {size_kb:.1f} KB (over 1 MB - consider reducing)",
            "warning"
        ))

    # Build summary
    errors = [c for c in checks if not c.passed and c.severity == "error"]
    warnings = [c for c in checks if not c.passed and c.severity == "warning"]
    infos = [c for c in checks if not c.passed and c.severity == "info"]
    passed = [c for c in checks if c.passed]

    if strict:
        is_compatible = len(errors) == 0 and len(warnings) == 0
    else:
        is_compatible = len(errors) == 0

    report = {
        "skill_name": skill_name,
        "skill_path": str(path),
        "compatible": is_compatible,
        "summary": {
            "total_checks": len(checks),
            "passed": len(passed),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(infos),
        },
        "checks": [c.to_dict() for c in checks],
    }

    return report


def format_human_output(report: Dict[str, Any]) -> str:
    """Format validation report as human-readable text."""
    lines = []
    lines.append("Cross-Platform Skill Validator")
    lines.append("=" * 40)
    lines.append(f"Skill: {report['skill_name']}")
    lines.append(f"Path:  {report['skill_path']}")
    lines.append("")

    # Group by platform
    platforms: Dict[str, List[Dict[str, Any]]] = {}
    for check in report["checks"]:
        platform = check["platform"]
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(check)

    platform_labels = {
        "claude-code": "Claude Code Compatibility",
        "codex-cli": "Codex CLI Compatibility",
        "cross-platform": "Cross-Platform Checks",
    }

    for platform_key in ["claude-code", "codex-cli", "cross-platform"]:
        if platform_key not in platforms:
            continue
        label = platform_labels.get(platform_key, platform_key)
        lines.append(f"{label}:")

        for check in platforms[platform_key]:
            if check["passed"]:
                status = "[PASS]"
            elif check["severity"] == "warning":
                status = "[WARN]"
            elif check["severity"] == "info":
                status = "[INFO]"
            else:
                status = "[FAIL]"
            lines.append(f"  {status} {check['message']}")

        lines.append("")

    # Summary
    s = report["summary"]
    compat_str = "COMPATIBLE" if report["compatible"] else "NOT COMPATIBLE"
    detail_parts = []
    if s["errors"] > 0:
        detail_parts.append(f"{s['errors']} error(s)")
    if s["warnings"] > 0:
        detail_parts.append(f"{s['warnings']} warning(s)")
    detail = f" ({', '.join(detail_parts)})" if detail_parts else ""

    lines.append(f"Overall: {compat_str}{detail}")
    lines.append(f"Checks: {s['passed']}/{s['total_checks']} passed")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a skill directory for Claude Code and Codex CLI compatibility.",
        epilog="Example: python cross_platform_validator.py path/to/skill-dir",
    )
    parser.add_argument(
        "skill_dir",
        help="Path to the skill directory to validate",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (fail if any warnings)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    if not Path(args.skill_dir).is_dir():
        print(f"Error: '{args.skill_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    report = validate_skill(args.skill_dir, strict=args.strict)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_human_output(report))

    if not report["compatible"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
