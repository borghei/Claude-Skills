#!/usr/bin/env python3
"""
Skill Validator - Validates skill directories against quality standards

This script validates a skill directory structure, documentation, and Python scripts
against the claude-skills ecosystem standards. It checks for required files, proper
formatting, and compliance with tier-specific requirements.

Usage:
    python skill_validator.py <skill_path> [--tier TIER] [--json] [--verbose]

Author: Claude Skills Engineering Team
Version: 1.0.0
Dependencies: Python Standard Library Only
"""

import argparse
import ast
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


# ---------------------------------------------------------------------------
# Minimal YAML reader (stdlib only)
#
# Covers the block-style subset used by SKILL.md frontmatter and pipeline
# configs: nested maps, lists (of scalars or maps), `>` / `|` block scalars,
# quoted strings, inline `[a, b]` lists, and bool / null / number scalars.
# Anchors, tags, multi-document streams and flow maps are not supported.
# ---------------------------------------------------------------------------

class YamlLiteError(ValueError):
    """Raised when the text falls outside the supported YAML subset."""


def _yaml_split_outside_quotes(text: str, sep: str) -> list:
    """Split on `sep` wherever it falls outside single or double quotes."""
    parts, buf, quote = [], '', None
    for ch in text:
        if quote:
            quote = None if ch == quote else quote
        elif ch in ('"', "'") and not buf.strip():
            quote = ch
        elif ch == sep:
            parts.append(buf)
            buf = ''
            continue
        buf += ch
    parts.append(buf)
    return parts


def _yaml_strip_comment(value: str) -> str:
    quote = value[:1] if value[:1] in ('"', "'") else None
    start = value.find(quote, 1) + 1 if quote else 0
    if quote and start == 0:
        return value
    cut = value.find(' #', start)
    return value[:cut].rstrip() if cut != -1 else value


def _yaml_scalar(text: str):
    s = text.strip()
    if len(s) >= 2 and s[0] == s[-1] == '"':
        try:
            return json.loads(s)
        except ValueError:
            return s[1:-1]
    if len(s) >= 2 and s[0] == s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if s.startswith('[') and s.endswith(']'):
        inner = s[1:-1].strip()
        return [_yaml_scalar(x) for x in _yaml_split_outside_quotes(inner, ',')] if inner else []
    if s == '{}':
        return {}
    low = s.lower()
    if low == 'true':
        return True
    if low == 'false':
        return False
    if low in ('null', '~', ''):
        return None
    for cast in (int, float):
        try:
            return cast(s)
        except ValueError:
            pass
    return s


def yaml_lite_load(text: str):
    """Parse a block-style YAML document into dicts, lists and scalars."""
    lines = text.expandtabs(2).splitlines()
    pos = 0

    def indent(line):
        return len(line) - len(line.lstrip(' '))

    def is_item(stripped):
        return stripped == '-' or stripped.startswith('- ')

    def skip_blank():
        nonlocal pos
        while pos < len(lines) and (not lines[pos].strip() or lines[pos].lstrip().startswith('#')):
            pos += 1

    def parse_block(ind):
        skip_blank()
        if pos >= len(lines):
            return None
        return parse_list(ind) if is_item(lines[pos].strip()) else parse_map(ind)

    def parse_value(rest, ind):
        if rest[:1] in ('>', '|'):
            return parse_block_scalar(rest, ind)
        if rest:
            if rest[0] in '"\'[{':
                return _yaml_scalar(rest)
            return _yaml_scalar(plain_continuation(rest, ind))
        skip_blank()
        if pos < len(lines):
            child = indent(lines[pos])
            if child > ind:
                return parse_block(child)
            if child == ind and is_item(lines[pos].strip()):
                return parse_list(ind)
        return None

    def plain_continuation(first, ind):
        # A plain scalar may continue on more-indented lines; YAML folds them with spaces
        nonlocal pos
        words = [first]
        while pos < len(lines):
            line = lines[pos]
            if line.strip() and indent(line) <= ind:
                break
            if line.strip() and not line.lstrip().startswith('#'):
                words.append(line.strip())
            pos += 1
        return ' '.join(words)

    def parse_map(ind):
        nonlocal pos
        out = {}
        while True:
            skip_blank()
            if pos >= len(lines) or indent(lines[pos]) < ind:
                return out
            line = lines[pos].strip()
            if indent(lines[pos]) > ind:
                raise YamlLiteError(f"line {pos + 1}: unexpected indentation")
            if is_item(line):
                return out
            key, sep, rest = line.partition(':')
            if not sep or (rest and not rest.startswith(' ')):
                raise YamlLiteError(f"line {pos + 1}: expected 'key: value'")
            pos += 1
            out[key.strip().strip('"\'')] = parse_value(_yaml_strip_comment(rest.strip()), ind)

    def parse_list(ind):
        nonlocal pos
        out = []
        while True:
            skip_blank()
            if pos >= len(lines) or indent(lines[pos]) != ind or not is_item(lines[pos].strip()):
                return out
            after_dash = lines[pos].strip()[1:]
            item = after_dash.strip()
            child = ind + 1 + len(after_dash) - len(after_dash.lstrip(' '))
            key, sep, rest = item.partition(':')
            if not item:
                pos += 1
                out.append(parse_value('', ind))
            elif sep and item[0] not in '"\'[{' and (not rest or rest.startswith(' ')):
                lines[pos] = ' ' * child + item
                out.append(parse_map(child))
            else:
                pos += 1
                out.append(_yaml_scalar(_yaml_strip_comment(item)))

    def parse_block_scalar(header, ind):
        nonlocal pos
        body, body_ind = [], None
        while pos < len(lines):
            line = lines[pos]
            if line.strip():
                if indent(line) <= ind or (body_ind is not None and indent(line) < body_ind):
                    break
                if body_ind is None:
                    body_ind = indent(line)
                body.append(line[body_ind:])
            else:
                body.append('')
            pos += 1
        while body and body[-1] == '':
            body.pop()
        if header[0] == '|':
            value = '\n'.join(body)
        else:
            value, prev_blank = '', True
            for part in body:
                if part == '':
                    value += '\n'
                    prev_blank = True
                else:
                    value += ('' if prev_blank else ' ') + part
                    prev_blank = False
        if not body:
            return ''
        return value if '-' in header else value + '\n'

    return parse_block(0)


# ---------------------------------------------------------------------------
# SKILL.md section concepts
#
# Skills in this library name their sections in different words, so sections
# are checked as concepts, each matched by the headings that express it.
# Requirements follow standards/skill-authoring-standard.md (P5, P11).
# ---------------------------------------------------------------------------

# Structural concepts must match the whole heading ("Tools", not "Tool Selection
# Criteria"); topical ones may appear anywhere in it ("Query Anti-Patterns").
_TOOLS = r"(python |automation )*(tools?|scripts|tooling)( overview| reference| & scripts)?"
SECTION_CONCEPTS = {
    "purpose": (r"when to use( this skill)?|use when|overview|purpose|(core )?capabilities"
                r"|what (this|the) skill does", "full"),
    "usage": (r"quick ?start|((core|end-to-end|common) )?workflows?|usage|how to use|getting started"
              r"|operating modes|common engagements|" + _TOOLS, "full"),
    "clarify_first": (r"clarify[- ]first", "anywhere"),
    "anti_patterns": (r"anti[- ]?patterns?|mistakes|pitfalls|red flags", "anywhere"),
    "scope": (r"scope|limitations|out[- ]of[- ]scope", "anywhere"),
    "tools": (_TOOLS, "full"),
    "references": (r"references?|reference (guides|documentation|materials)|knowledge base", "full"),
}

SECTION_LABELS = {
    "purpose": "what the skill is for (When to Use, Overview, Core Capabilities)",
    "usage": "how to use it (Quick Start, Workflows, Tools)",
    "clarify_first": "Clarify First",
    "anti_patterns": "Anti-Patterns",
    "scope": "Scope & Limitations",
    "tools": "Tools",
    "references": "References",
}


def skill_md_section_concepts(content: str) -> set:
    """Return the section concepts present in a SKILL.md, ignoring fenced code."""
    prose = re.sub(r"^```.*?^```", "", content, flags=re.MULTILINE | re.DOTALL)
    headings = [re.sub(r"[^\w &/-]", "", h).strip().lower()
                for h in re.findall(r"^#{2,3}\s+(.+?)\s*$", prose, re.MULTILINE)]
    found = set()
    for name, (pattern, mode) in SECTION_CONCEPTS.items():
        regex = re.compile(rf"(?:{pattern})" if mode == "full" else rf"\b(?:{pattern})\b")
        match = regex.fullmatch if mode == "full" else regex.search
        if any(match(h) for h in headings):
            found.add(name)
    return found


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class ValidationReport:
    """Container for validation results"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.checks = {}
        self.warnings = []
        self.errors = []
        self.suggestions = []
        self.overall_score = 0.0
        self.compliance_level = "FAIL"
        
    def add_check(self, check_name: str, passed: bool, message: str = "", score: float = 0.0):
        """Add a validation check result"""
        self.checks[check_name] = {
            "passed": passed,
            "message": message,
            "score": score
        }
        
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
        
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        
    def add_suggestion(self, message: str):
        """Add an improvement suggestion"""
        self.suggestions.append(message)
        
    def calculate_overall_score(self):
        """Calculate overall compliance score"""
        if not self.checks:
            self.overall_score = 0.0
            return
            
        total_score = sum(check["score"] for check in self.checks.values())
        max_score = len(self.checks) * 1.0
        self.overall_score = (total_score / max_score) * 100 if max_score > 0 else 0.0
        
        # Determine compliance level
        if self.overall_score >= 90:
            self.compliance_level = "EXCELLENT"
        elif self.overall_score >= 75:
            self.compliance_level = "GOOD"
        elif self.overall_score >= 60:
            self.compliance_level = "ACCEPTABLE"
        elif self.overall_score >= 40:
            self.compliance_level = "NEEDS_IMPROVEMENT"
        else:
            self.compliance_level = "POOR"


class SkillValidator:
    """Main skill validation engine"""
    
    # Tier requirements
    TIER_REQUIREMENTS = {
        "BASIC": {
            "min_skill_md_lines": 100,
            "min_scripts": 1,
            "script_size_range": (100, 300),
            "required_dirs": ["scripts"],
            "optional_dirs": ["assets", "references", "expected_outputs"],
            "features_required": ["argparse", "main_guard"]
        },
        "STANDARD": {
            "min_skill_md_lines": 200,
            "min_scripts": 1,
            "script_size_range": (300, 500),
            "required_dirs": ["scripts", "assets", "references"],
            "optional_dirs": ["expected_outputs"],
            "features_required": ["argparse", "main_guard", "json_output", "help_text"]
        },
        "POWERFUL": {
            "min_skill_md_lines": 300,
            "min_scripts": 2,
            "script_size_range": (500, 800),
            "required_dirs": ["scripts", "assets", "references", "expected_outputs"],
            "optional_dirs": [],
            "features_required": ["argparse", "main_guard", "json_output", "help_text", "error_handling"]
        }
    }
    
    # Section concepts (see SECTION_CONCEPTS): missing required ones are errors,
    # missing recommended ones are warnings
    REQUIRED_SECTION_CONCEPTS = ["purpose", "usage"]
    RECOMMENDED_SECTION_CONCEPTS = ["clarify_first", "anti_patterns", "scope"]
    
    # Schema from standards/skill-authoring-standard.md (Pattern 2)
    FRONTMATTER_REQUIRED_FIELDS = ["name", "description", "license"]
    FRONTMATTER_REQUIRED_METADATA = ["version", "author", "category", "updated"]
    FRONTMATTER_RECOMMENDED_METADATA = ["domain", "tags"]
    
    def __init__(self, skill_path: str, target_tier: Optional[str] = None, verbose: bool = False):
        self.skill_path = Path(skill_path).resolve()
        self.target_tier = target_tier
        self.verbose = verbose
        self.report = ValidationReport(str(self.skill_path))
        
    def log_verbose(self, message: str):
        """Log verbose message if verbose mode enabled"""
        if self.verbose:
            print(f"[VERBOSE] {message}", file=sys.stderr)
            
    def validate_skill_structure(self) -> ValidationReport:
        """Main validation entry point"""
        try:
            self.log_verbose(f"Starting validation of {self.skill_path}")
            
            # Check if path exists
            if not self.skill_path.exists():
                self.report.add_error(f"Skill path does not exist: {self.skill_path}")
                return self.report
                
            if not self.skill_path.is_dir():
                self.report.add_error(f"Skill path is not a directory: {self.skill_path}")
                return self.report
                
            # Run all validation checks
            self._validate_required_files()
            self._validate_skill_md()
            self._validate_readme()
            self._validate_directory_structure()
            self._validate_python_scripts()
            self._validate_tier_compliance()
            
            # Calculate overall score
            self.report.calculate_overall_score()
            
            self.log_verbose(f"Validation completed. Score: {self.report.overall_score:.1f}")
            
        except Exception as e:
            self.report.add_error(f"Validation failed with exception: {str(e)}")
            
        return self.report
        
    def _validate_required_files(self):
        """Validate presence of required files"""
        self.log_verbose("Checking required files...")
        
        # Check SKILL.md
        skill_md_path = self.skill_path / "SKILL.md"
        if skill_md_path.exists():
            self.report.add_check("skill_md_exists", True, "SKILL.md found", 1.0)
        else:
            self.report.add_check("skill_md_exists", False, "SKILL.md missing", 0.0)
            self.report.add_error("SKILL.md is required but missing")
            
        # Check README.md
        readme_path = self.skill_path / "README.md"
        if readme_path.exists():
            self.report.add_check("readme_exists", True, "README.md found", 1.0)
        else:
            self.report.add_check("readme_exists", False, "README.md missing", 0.0)
            self.report.add_warning("README.md is recommended but missing")
            self.report.add_suggestion("Add README.md with usage instructions and examples")
            
    def _validate_skill_md(self):
        """Validate SKILL.md content and format"""
        self.log_verbose("Validating SKILL.md...")
        
        skill_md_path = self.skill_path / "SKILL.md"
        if not skill_md_path.exists():
            return
            
        try:
            content = skill_md_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            line_count = len([line for line in lines if line.strip()])
            
            # Check line count
            min_lines = self._get_tier_requirement("min_skill_md_lines", 100)
            if line_count >= min_lines:
                self.report.add_check("skill_md_length", True, 
                                     f"SKILL.md has {line_count} lines (≥{min_lines})", 1.0)
            else:
                self.report.add_check("skill_md_length", False,
                                     f"SKILL.md has {line_count} lines (<{min_lines})", 0.0)
                self.report.add_error(f"SKILL.md too short: {line_count} lines, minimum {min_lines}")
                
            # Validate frontmatter
            self._validate_frontmatter(content)
            
            # Check required sections
            self._validate_required_sections(content)
            
        except Exception as e:
            self.report.add_check("skill_md_readable", False, f"Error reading SKILL.md: {str(e)}", 0.0)
            self.report.add_error(f"Cannot read SKILL.md: {str(e)}")
            
    def _validate_frontmatter(self, content: str):
        """Validate SKILL.md frontmatter"""
        self.log_verbose("Validating frontmatter...")
        
        # Extract frontmatter
        if content.startswith('---'):
            try:
                end_marker = content.find('---', 3)
                if end_marker == -1:
                    self.report.add_check("frontmatter_format", False, 
                                         "Frontmatter closing marker not found", 0.0)
                    return
                    
                frontmatter_text = content[3:end_marker].strip()
                frontmatter = yaml_lite_load(frontmatter_text)
                
                if not isinstance(frontmatter, dict):
                    self.report.add_check("frontmatter_format", False, 
                                         "Frontmatter is not a valid dictionary", 0.0)
                    return
                    
                # Check required fields
                metadata = frontmatter.get("metadata")
                metadata = metadata if isinstance(metadata, dict) else {}
                missing_fields = [f for f in self.FRONTMATTER_REQUIRED_FIELDS if not frontmatter.get(f)]
                missing_fields += [f"metadata.{f}" for f in self.FRONTMATTER_REQUIRED_METADATA
                                   if not metadata.get(f)]
                missing_recommended = [f"metadata.{f}" for f in self.FRONTMATTER_RECOMMENDED_METADATA
                                       if not metadata.get(f)]
                if missing_recommended:
                    self.report.add_warning(
                        f"Recommended frontmatter fields missing: {', '.join(missing_recommended)}")
                if frontmatter.get("name") and frontmatter["name"] != self.skill_path.name:
                    self.report.add_warning(
                        f"Frontmatter name '{frontmatter['name']}' does not match folder '{self.skill_path.name}'")

                if not missing_fields:
                    self.report.add_check("frontmatter_complete", True, 
                                         "All required frontmatter fields present", 1.0)
                else:
                    self.report.add_check("frontmatter_complete", False,
                                         f"Missing fields: {', '.join(missing_fields)}", 0.0)
                    self.report.add_error(f"Missing frontmatter fields: {', '.join(missing_fields)}")
                    
            except YamlLiteError as e:
                self.report.add_check("frontmatter_format", False, 
                                     f"Invalid YAML frontmatter: {str(e)}", 0.0)
                self.report.add_error(f"Invalid YAML frontmatter: {str(e)}")
                
        else:
            self.report.add_check("frontmatter_exists", False, 
                                 "No frontmatter found", 0.0)
            self.report.add_error("SKILL.md must start with YAML frontmatter")
            
    def _validate_required_sections(self, content: str):
        """Validate SKILL.md section concepts against the authoring standard"""
        self.log_verbose("Checking required sections...")

        present = skill_md_section_concepts(content)
        # A skill passes "purpose or usage" with either; slim skills route to references/
        if not present & set(self.REQUIRED_SECTION_CONCEPTS):
            missing = " or ".join(SECTION_LABELS[c] for c in self.REQUIRED_SECTION_CONCEPTS)
            self.report.add_check("required_sections", False, f"Missing a section on {missing}", 0.0)
            self.report.add_error(f"SKILL.md needs a section on {missing}")
        else:
            self.report.add_check("required_sections", True, "Required sections present", 1.0)

        for concept in self.RECOMMENDED_SECTION_CONCEPTS:
            if concept not in present:
                self.report.add_warning(f"Recommended section missing: {SECTION_LABELS[concept]}")

        scripts = [s for s in (self.skill_path / "scripts").glob("*.py") if s.name != "__init__.py"]
        if scripts and "tools" not in present:
            self.report.add_warning("scripts/ has Python tools but SKILL.md has no Tools section")
        unmentioned = sorted(s.name for s in scripts if s.name not in content)
        if unmentioned:
            self.report.add_warning(f"Tools not mentioned in SKILL.md: {', '.join(unmentioned)}")
        if (self.skill_path / "references").is_dir() and "references/" not in content \
                and "references" not in present:
            self.report.add_warning("references/ exists but SKILL.md never points to it")

    def _validate_readme(self):
        """Validate README.md content"""
        self.log_verbose("Validating README.md...")
        
        readme_path = self.skill_path / "README.md"
        if not readme_path.exists():
            return
            
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            # Check minimum content length
            if len(content.strip()) >= 200:
                self.report.add_check("readme_substantial", True,
                                     "README.md has substantial content", 1.0)
            else:
                self.report.add_check("readme_substantial", False,
                                     "README.md content is too brief", 0.5)
                self.report.add_suggestion("Expand README.md with more detailed usage instructions")
                
        except Exception as e:
            self.report.add_check("readme_readable", False,
                                 f"Error reading README.md: {str(e)}", 0.0)
            
    def _validate_directory_structure(self):
        """Validate directory structure against tier requirements"""
        self.log_verbose("Validating directory structure...")
        
        required_dirs = self._get_tier_requirement("required_dirs", ["scripts"])
        optional_dirs = self._get_tier_requirement("optional_dirs", [])
        
        # Check required directories
        missing_required = []
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.report.add_check(f"dir_{dir_name}_exists", True,
                                     f"{dir_name}/ directory found", 1.0)
            else:
                missing_required.append(dir_name)
                self.report.add_check(f"dir_{dir_name}_exists", False,
                                     f"{dir_name}/ directory missing", 0.0)
                
        if missing_required:
            self.report.add_error(f"Missing required directories: {', '.join(missing_required)}")
            
        # Check optional directories and provide suggestions
        missing_optional = []
        for dir_name in optional_dirs:
            dir_path = self.skill_path / dir_name
            if not (dir_path.exists() and dir_path.is_dir()):
                missing_optional.append(dir_name)
                
        if missing_optional:
            self.report.add_suggestion(f"Consider adding optional directories: {', '.join(missing_optional)}")
            
    def _validate_python_scripts(self):
        """Validate Python scripts in the scripts directory"""
        self.log_verbose("Validating Python scripts...")
        
        scripts_dir = self.skill_path / "scripts"
        if not scripts_dir.exists():
            return
            
        python_files = list(scripts_dir.glob("*.py"))
        min_scripts = self._get_tier_requirement("min_scripts", 1)
        
        # Check minimum number of scripts
        if len(python_files) >= min_scripts:
            self.report.add_check("min_scripts_count", True,
                                 f"Found {len(python_files)} Python scripts (≥{min_scripts})", 1.0)
        else:
            self.report.add_check("min_scripts_count", False,
                                 f"Found {len(python_files)} Python scripts (<{min_scripts})", 0.0)
            self.report.add_error(f"Insufficient scripts: {len(python_files)}, minimum {min_scripts}")
            
        # Validate each script
        for script_path in python_files:
            self._validate_single_script(script_path)
            
    def _validate_single_script(self, script_path: Path):
        """Validate a single Python script"""
        script_name = script_path.name
        self.log_verbose(f"Validating script: {script_name}")
        
        try:
            content = script_path.read_text(encoding='utf-8')
            
            # Count lines of code (excluding empty lines and comments)
            lines = content.split('\n')
            loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Check script size against tier requirements
            size_range = self._get_tier_requirement("script_size_range", (100, 1000))
            min_size, max_size = size_range
            
            if min_size <= loc <= max_size:
                self.report.add_check(f"script_size_{script_name}", True,
                                     f"{script_name} has {loc} LOC (within {min_size}-{max_size})", 1.0)
            else:
                self.report.add_check(f"script_size_{script_name}", False,
                                     f"{script_name} has {loc} LOC (outside {min_size}-{max_size})", 0.5)
                if loc < min_size:
                    self.report.add_suggestion(f"Consider expanding {script_name} (currently {loc} LOC)")
                else:
                    self.report.add_suggestion(f"Consider refactoring {script_name} (currently {loc} LOC)")
                    
            # Parse and validate Python syntax
            try:
                tree = ast.parse(content)
                self.report.add_check(f"script_syntax_{script_name}", True,
                                     f"{script_name} has valid Python syntax", 1.0)
                                     
                # Check for required features
                self._validate_script_features(tree, script_name, content)
                
            except SyntaxError as e:
                self.report.add_check(f"script_syntax_{script_name}", False,
                                     f"{script_name} has syntax error: {str(e)}", 0.0)
                self.report.add_error(f"Syntax error in {script_name}: {str(e)}")
                
        except Exception as e:
            self.report.add_check(f"script_readable_{script_name}", False,
                                 f"Cannot read {script_name}: {str(e)}", 0.0)
            self.report.add_error(f"Cannot read {script_name}: {str(e)}")
            
    def _validate_script_features(self, tree: ast.AST, script_name: str, content: str):
        """Validate required script features"""
        required_features = self._get_tier_requirement("features_required", ["argparse", "main_guard"])
        
        # Check for argparse usage
        if "argparse" in required_features:
            has_argparse = self._check_argparse_usage(tree)
            self.report.add_check(f"script_argparse_{script_name}", has_argparse,
                                 f"{'Uses' if has_argparse else 'Missing'} argparse in {script_name}", 1.0 if has_argparse else 0.0)
            if not has_argparse:
                self.report.add_error(f"{script_name} must use argparse for command-line arguments")
                
        # Check for main guard
        if "main_guard" in required_features:
            has_main_guard = 'if __name__ == "__main__"' in content
            self.report.add_check(f"script_main_guard_{script_name}", has_main_guard,
                                 f"{'Has' if has_main_guard else 'Missing'} main guard in {script_name}", 1.0 if has_main_guard else 0.0)
            if not has_main_guard:
                self.report.add_error(f"{script_name} must have 'if __name__ == \"__main__\"' guard")
                
        # Check for external imports (should only use stdlib)
        external_imports = self._check_external_imports(tree)
        if not external_imports:
            self.report.add_check(f"script_imports_{script_name}", True,
                                 f"{script_name} uses only standard library", 1.0)
        else:
            self.report.add_check(f"script_imports_{script_name}", False,
                                 f"{script_name} uses external imports: {', '.join(external_imports)}", 0.0)
            self.report.add_error(f"{script_name} uses external imports: {', '.join(external_imports)}")
            
    def _check_argparse_usage(self, tree: ast.AST) -> bool:
        """Check if the script uses argparse"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == 'argparse':
                        return True
            elif isinstance(node, ast.ImportFrom):
                if node.module == 'argparse':
                    return True
        return False
        
    def _check_external_imports(self, tree: ast.AST) -> List[str]:
        """Check for external (non-stdlib) imports"""
        # Simplified check - a more comprehensive solution would use a stdlib module list
        stdlib_modules = {
            'argparse', 'ast', 'json', 'os', 'sys', 'pathlib', 'datetime', 'typing',
            'collections', 're', 'math', 'random', 'itertools', 'functools', 'operator',
            'csv', 'sqlite3', 'urllib', 'http', 'html', 'xml', 'email', 'base64',
            'hashlib', 'hmac', 'secrets', 'tempfile', 'shutil', 'glob', 'fnmatch',
            'subprocess', 'threading', 'multiprocessing', 'queue', 'time', 'calendar',
            'zoneinfo', 'locale', 'gettext', 'logging', 'warnings', 'unittest',
            'doctest', 'pickle', 'copy', 'pprint', 'reprlib', 'enum', 'dataclasses',
            'contextlib', 'abc', 'atexit', 'traceback', 'gc', 'weakref', 'types',
            'copy', 'pprint', 'reprlib', 'enum', 'decimal', 'fractions', 'statistics',
            'cmath', 'platform', 'errno', 'io', 'codecs', 'unicodedata', 'stringprep',
            'textwrap', 'string', 'struct', 'difflib', 'heapq', 'bisect', 'array',
            'weakref', 'types', 'copyreg', 'uuid', 'mmap', 'ctypes'
        }
        
        external_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name not in stdlib_modules:
                        external_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module.split('.')[0]
                if module_name not in stdlib_modules:
                    external_imports.append(node.module)
                    
        return list(set(external_imports))
        
    def _validate_tier_compliance(self):
        """Validate overall tier compliance"""
        if not self.target_tier:
            return
            
        self.log_verbose(f"Validating {self.target_tier} tier compliance...")
        
        # This is a summary check - individual checks are done in other methods
        critical_checks = ["skill_md_exists", "min_scripts_count", "skill_md_length"]
        failed_critical = [check for check in critical_checks 
                          if check in self.report.checks and not self.report.checks[check]["passed"]]
                          
        if not failed_critical:
            self.report.add_check("tier_compliance", True,
                                 f"Meets {self.target_tier} tier requirements", 1.0)
        else:
            self.report.add_check("tier_compliance", False,
                                 f"Does not meet {self.target_tier} tier requirements", 0.0)
            self.report.add_error(f"Failed critical checks for {self.target_tier} tier: {', '.join(failed_critical)}")
            
    def _get_tier_requirement(self, requirement: str, default: Any) -> Any:
        """Get tier-specific requirement value"""
        if self.target_tier and self.target_tier in self.TIER_REQUIREMENTS:
            return self.TIER_REQUIREMENTS[self.target_tier].get(requirement, default)
        return default


class ReportFormatter:
    """Formats validation reports for output"""
    
    @staticmethod
    def format_json(report: ValidationReport) -> str:
        """Format report as JSON"""
        return json.dumps({
            "skill_path": report.skill_path,
            "timestamp": report.timestamp,
            "overall_score": round(report.overall_score, 1),
            "compliance_level": report.compliance_level,
            "checks": report.checks,
            "warnings": report.warnings,
            "errors": report.errors,
            "suggestions": report.suggestions
        }, indent=2)
        
    @staticmethod
    def format_human_readable(report: ValidationReport) -> str:
        """Format report as human-readable text"""
        lines = []
        lines.append("=" * 60)
        lines.append("SKILL VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Skill: {report.skill_path}")
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append(f"Overall Score: {report.overall_score:.1f}/100 ({report.compliance_level})")
        lines.append("")
        
        # Group checks by category
        structure_checks = {k: v for k, v in report.checks.items() if k.startswith(('skill_md', 'readme', 'dir_'))}
        script_checks = {k: v for k, v in report.checks.items() if k.startswith('script_')}
        other_checks = {k: v for k, v in report.checks.items() if k not in structure_checks and k not in script_checks}
        
        if structure_checks:
            lines.append("STRUCTURE VALIDATION:")
            for check_name, result in structure_checks.items():
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                lines.append(f"  {status}: {result['message']}")
            lines.append("")
            
        if script_checks:
            lines.append("SCRIPT VALIDATION:")
            for check_name, result in script_checks.items():
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                lines.append(f"  {status}: {result['message']}")
            lines.append("")
            
        if other_checks:
            lines.append("OTHER CHECKS:")
            for check_name, result in other_checks.items():
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                lines.append(f"  {status}: {result['message']}")
            lines.append("")
            
        if report.errors:
            lines.append("ERRORS:")
            for error in report.errors:
                lines.append(f"  • {error}")
            lines.append("")
            
        if report.warnings:
            lines.append("WARNINGS:")
            for warning in report.warnings:
                lines.append(f"  • {warning}")
            lines.append("")
            
        if report.suggestions:
            lines.append("SUGGESTIONS:")
            for suggestion in report.suggestions:
                lines.append(f"  • {suggestion}")
            lines.append("")
            
        return "\n".join(lines)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate skill directories against quality standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python skill_validator.py engineering/my-skill
  python skill_validator.py engineering/my-skill --tier POWERFUL --json
  python skill_validator.py engineering/my-skill --verbose

Tier Options:
  BASIC     - Basic skill requirements (100+ lines SKILL.md, 1+ script)
  STANDARD  - Standard skill requirements (200+ lines, advanced features)
  POWERFUL  - Powerful skill requirements (300+ lines, comprehensive features)
        """
    )
    
    parser.add_argument("skill_path", 
                       help="Path to the skill directory to validate")
    parser.add_argument("--tier", 
                       choices=["BASIC", "STANDARD", "POWERFUL"],
                       help="Target tier for validation (optional)")
    parser.add_argument("--json", 
                       action="store_true",
                       help="Output results in JSON format")
    parser.add_argument("--verbose", 
                       action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        # Create validator and run validation
        validator = SkillValidator(args.skill_path, args.tier, args.verbose)
        report = validator.validate_skill_structure()
        
        # Format and output report
        if args.json:
            print(ReportFormatter.format_json(report))
        else:
            print(ReportFormatter.format_human_readable(report))
            
        # Exit with error code if validation failed
        if report.errors or report.overall_score < 60:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nValidation interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Validation failed: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()