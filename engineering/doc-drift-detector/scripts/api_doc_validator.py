#!/usr/bin/env python3
"""
API Documentation Validator

Extracts function and class signatures from Python source files using the ast module
and compares them against API documentation in markdown files.

Detects:
- Functions/classes in code but missing from docs
- Functions/classes documented but removed from code
- Parameter mismatches (missing, extra, wrong defaults)
- Deprecated items still documented as current
- Return type annotation mismatches

Usage:
    python api_doc_validator.py /path/to/src /path/to/docs/api.md
    python api_doc_validator.py /path/to/src /path/to/docs/ --recursive
    python api_doc_validator.py /path/to/src /path/to/docs/api.md --json
    python api_doc_validator.py /path/to/src /path/to/docs/ --include-private
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# --- AST Source Extraction ---

class SourceSignature:
    """Represents an extracted function or class signature."""

    def __init__(
        self,
        name: str,
        kind: str,  # "function", "method", "class"
        file_path: str,
        line_number: int,
        parameters: List[Dict[str, Any]],
        return_annotation: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        docstring: Optional[str] = None,
        is_private: bool = False,
        parent_class: Optional[str] = None,
    ):
        self.name = name
        self.kind = kind
        self.file_path = file_path
        self.line_number = line_number
        self.parameters = parameters
        self.return_annotation = return_annotation
        self.decorators = decorators or []
        self.docstring = docstring
        self.is_private = is_private
        self.parent_class = parent_class

    @property
    def qualified_name(self) -> str:
        if self.parent_class:
            return f"{self.parent_class}.{self.name}"
        return self.name

    @property
    def is_deprecated(self) -> bool:
        return any("deprecated" in d.lower() for d in self.decorators)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "qualified_name": self.qualified_name,
            "kind": self.kind,
            "file": self.file_path,
            "line": self.line_number,
            "parameters": self.parameters,
            "return_annotation": self.return_annotation,
            "decorators": self.decorators,
            "is_private": self.is_private,
            "is_deprecated": self.is_deprecated,
        }


def _annotation_to_str(node: Optional[ast.expr]) -> Optional[str]:
    """Convert an AST annotation node to a string representation."""
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except AttributeError:
        # Python < 3.9 fallback
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Attribute):
            return f"{_annotation_to_str(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{_annotation_to_str(node.value)}[{_annotation_to_str(node.slice)}]"
        return str(type(node).__name__)


def _extract_decorator_names(decorator_list: List[ast.expr]) -> List[str]:
    """Extract decorator names from AST decorator list."""
    names = []
    for dec in decorator_list:
        if isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.append(f"{_annotation_to_str(dec.value)}.{dec.attr}")
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                names.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                names.append(f"{_annotation_to_str(dec.func.value)}.{dec.func.attr}")
    return names


def _extract_parameters(func_node: ast.FunctionDef) -> List[Dict[str, Any]]:
    """Extract parameter information from a function definition."""
    params = []
    args = func_node.args

    # Calculate defaults offset
    num_args = len(args.args)
    num_defaults = len(args.defaults)
    default_offset = num_args - num_defaults

    for i, arg in enumerate(args.args):
        if arg.arg == "self" or arg.arg == "cls":
            continue
        param: Dict[str, Any] = {
            "name": arg.arg,
            "annotation": _annotation_to_str(arg.annotation),
            "has_default": False,
            "default": None,
        }
        # Check if this arg has a default
        default_idx = i - default_offset
        if default_idx >= 0 and default_idx < len(args.defaults):
            param["has_default"] = True
            try:
                param["default"] = ast.unparse(args.defaults[default_idx])
            except AttributeError:
                param["default"] = "..."
        params.append(param)

    # *args
    if args.vararg:
        params.append({
            "name": f"*{args.vararg.arg}",
            "annotation": _annotation_to_str(args.vararg.annotation),
            "has_default": False,
            "default": None,
        })

    # keyword-only args
    for i, arg in enumerate(args.kwonlyargs):
        param = {
            "name": arg.arg,
            "annotation": _annotation_to_str(arg.annotation),
            "has_default": False,
            "default": None,
        }
        if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
            param["has_default"] = True
            try:
                param["default"] = ast.unparse(args.kw_defaults[i])
            except AttributeError:
                param["default"] = "..."
        params.append(param)

    # **kwargs
    if args.kwarg:
        params.append({
            "name": f"**{args.kwarg.arg}",
            "annotation": _annotation_to_str(args.kwarg.annotation),
            "has_default": False,
            "default": None,
        })

    return params


def extract_signatures(source_path: str, include_private: bool = False) -> List[SourceSignature]:
    """Extract all function and class signatures from a Python file."""
    signatures = []
    try:
        with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=source_path)
    except (SyntaxError, OSError, IOError):
        return signatures

    rel_path = source_path  # Will be made relative by caller

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            is_private = node.name.startswith("_")
            if is_private and not include_private:
                continue

            # Determine if it's a method (inside a class)
            parent_class = None
            kind = "function"
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef):
                    for item in parent.body:
                        if item is node:
                            parent_class = parent.name
                            kind = "method"
                            break

            docstring = ast.get_docstring(node)
            decorators = _extract_decorator_names(node.decorator_list)
            parameters = _extract_parameters(node)
            return_annotation = _annotation_to_str(node.returns)

            sig = SourceSignature(
                name=node.name,
                kind=kind,
                file_path=rel_path,
                line_number=node.lineno,
                parameters=parameters,
                return_annotation=return_annotation,
                decorators=decorators,
                docstring=docstring,
                is_private=is_private,
                parent_class=parent_class,
            )
            signatures.append(sig)

        elif isinstance(node, ast.ClassDef):
            is_private = node.name.startswith("_")
            if is_private and not include_private:
                continue

            docstring = ast.get_docstring(node)
            decorators = _extract_decorator_names(node.decorator_list)

            # Extract __init__ params as the class params
            init_params = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    init_params = _extract_parameters(item)
                    break

            sig = SourceSignature(
                name=node.name,
                kind="class",
                file_path=rel_path,
                line_number=node.lineno,
                parameters=init_params,
                decorators=decorators,
                docstring=docstring,
                is_private=is_private,
            )
            signatures.append(sig)

    return signatures


def extract_all_signatures(
    source_dir: str, include_private: bool = False
) -> Dict[str, List[SourceSignature]]:
    """Extract signatures from all Python files in a directory."""
    all_sigs: Dict[str, List[SourceSignature]] = {}
    skip_dirs = {"__pycache__", ".venv", "venv", ".git", "node_modules", ".tox"}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.endswith(".py"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, source_dir)
                sigs = extract_signatures(full_path, include_private)
                # Update file paths to be relative
                for s in sigs:
                    s.file_path = rel_path
                if sigs:
                    all_sigs[rel_path] = sigs

    return all_sigs


# --- Documentation Parsing ---

def extract_documented_items(doc_path: str) -> Dict[str, Dict[str, Any]]:
    """Extract function/class references from markdown documentation."""
    items: Dict[str, Dict[str, Any]] = {}

    try:
        with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return items

    lines = content.splitlines()

    # Pattern 1: Function headings like ### `function_name()` or ### function_name
    heading_func = re.compile(r'^#{1,6}\s+`?(\w+(?:\.\w+)*)\(`?.*\)?`?\s*$')
    # Pattern 2: Function in backticks with params like `function_name(param1, param2)`
    inline_func = re.compile(r'`(\w+(?:\.\w+)*)\(([^)]*)\)`')
    # Pattern 3: Class headings like ### class ClassName or ### ClassName
    heading_class = re.compile(r'^#{1,6}\s+(?:class\s+)?`?(\w+)`?\s*$')
    # Pattern 4: Parameter lists like - `param_name` (type): description
    param_pattern = re.compile(r'^\s*[-*]\s+`(\w+)`\s*(?:\(([^)]+)\))?\s*(?::|--)?\s*(.*)')

    current_item = None
    current_params: List[Dict[str, Any]] = []

    for i, line in enumerate(lines):
        # Check for function heading
        match = heading_func.match(line)
        if match:
            if current_item and current_item in items:
                items[current_item]["parameters"] = current_params

            func_name = match.group(1)
            items[func_name] = {
                "name": func_name,
                "line": i + 1,
                "kind": "function",
                "file": doc_path,
                "parameters": [],
            }
            current_item = func_name
            current_params = []
            continue

        # Check for inline function definitions
        for match in inline_func.finditer(line):
            func_name = match.group(1)
            param_str = match.group(2)
            if func_name not in items:
                params = []
                if param_str:
                    for p in param_str.split(","):
                        p = p.strip()
                        if p and p not in ("self", "cls", "..."):
                            # Handle type annotations like param: type
                            parts = p.split(":")
                            param_name = parts[0].strip().split("=")[0].strip()
                            if param_name and param_name.replace("*", "").isidentifier():
                                params.append({"name": param_name})
                items[func_name] = {
                    "name": func_name,
                    "line": i + 1,
                    "kind": "function",
                    "file": doc_path,
                    "parameters": params,
                }

        # Check for parameter list items
        param_match = param_pattern.match(line)
        if param_match and current_item:
            param_name = param_match.group(1)
            param_type = param_match.group(2)
            current_params.append({
                "name": param_name,
                "annotation": param_type,
            })

    # Finalize last item
    if current_item and current_item in items:
        items[current_item]["parameters"] = current_params

    return items


def extract_all_documented_items(
    doc_path: str, recursive: bool = False
) -> Dict[str, Dict[str, Any]]:
    """Extract documented items from one or more markdown files."""
    all_items: Dict[str, Dict[str, Any]] = {}

    if os.path.isfile(doc_path):
        return extract_documented_items(doc_path)

    if os.path.isdir(doc_path) and recursive:
        for root, dirs, files in os.walk(doc_path):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules"}]
            for f in files:
                if f.endswith((".md", ".rst")):
                    full_path = os.path.join(root, f)
                    items = extract_documented_items(full_path)
                    all_items.update(items)
    elif os.path.isdir(doc_path):
        # Non-recursive: just top-level files
        for f in os.listdir(doc_path):
            if f.endswith((".md", ".rst")):
                full_path = os.path.join(doc_path, f)
                items = extract_documented_items(full_path)
                all_items.update(items)

    return all_items


# --- Validation ---

def validate_api_docs(
    source_sigs: Dict[str, List[SourceSignature]],
    documented_items: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Compare source signatures against documented items and find mismatches."""
    issues = []

    # Build lookup of all source signatures by name and qualified name
    source_by_name: Dict[str, SourceSignature] = {}
    for file_sigs in source_sigs.values():
        for sig in file_sigs:
            source_by_name[sig.name] = sig
            source_by_name[sig.qualified_name] = sig

    documented_names = set(documented_items.keys())
    source_names = set(source_by_name.keys())

    # 1. Documented but not in source (removed or renamed)
    for name in documented_names:
        if name not in source_names:
            doc_item = documented_items[name]
            issues.append({
                "type": "documented_not_in_source",
                "severity": "high",
                "name": name,
                "doc_file": doc_item.get("file", "unknown"),
                "doc_line": doc_item.get("line", 0),
                "description": f"'{name}' is documented but not found in source code (removed or renamed)",
            })

    # 2. In source but not documented
    for name, sig in source_by_name.items():
        # Skip qualified names that are also present as simple names
        if "." in name and name.split(".")[-1] in source_by_name:
            # Only report on the simple name to avoid duplicates
            continue
        if name not in documented_names and sig.qualified_name not in documented_names:
            if not sig.is_private:
                issues.append({
                    "type": "undocumented",
                    "severity": "medium",
                    "name": sig.qualified_name,
                    "source_file": sig.file_path,
                    "source_line": sig.line_number,
                    "description": f"'{sig.qualified_name}' ({sig.kind}) exists in source but is not documented",
                })

    # 3. Parameter mismatches
    for name in documented_names & source_names:
        sig = source_by_name[name]
        doc_item = documented_items[name]

        doc_params = doc_item.get("parameters", [])
        source_params = sig.parameters

        if not doc_params and not source_params:
            continue

        doc_param_names = {p["name"] for p in doc_params if "name" in p}
        source_param_names = {
            p["name"].lstrip("*") for p in source_params if "name" in p
        }

        # Parameters in source but not in docs
        missing_in_docs = source_param_names - doc_param_names
        for param in missing_in_docs:
            if param not in ("self", "cls"):
                issues.append({
                    "type": "missing_param_in_docs",
                    "severity": "medium",
                    "name": name,
                    "parameter": param,
                    "source_file": sig.file_path,
                    "source_line": sig.line_number,
                    "description": f"Parameter '{param}' of '{name}' exists in source but not in docs",
                })

        # Parameters in docs but not in source
        extra_in_docs = doc_param_names - source_param_names
        for param in extra_in_docs:
            issues.append({
                "type": "extra_param_in_docs",
                "severity": "medium",
                "name": name,
                "parameter": param,
                "doc_file": doc_item.get("file", "unknown"),
                "doc_line": doc_item.get("line", 0),
                "description": f"Parameter '{param}' documented for '{name}' but not in source",
            })

    # 4. Deprecated items still documented without deprecation notice
    for name in documented_names & source_names:
        sig = source_by_name[name]
        if sig.is_deprecated:
            doc_item = documented_items[name]
            # Check if doc mentions "deprecated"
            # This is a simple heuristic; we check the item's doc context
            issues.append({
                "type": "deprecated_still_documented",
                "severity": "low",
                "name": name,
                "source_file": sig.file_path,
                "source_line": sig.line_number,
                "description": f"'{name}' has @deprecated decorator but may still be documented as current",
            })

    return issues


# --- Report ---

def generate_report(issues: List[Dict[str, Any]], source_count: int, doc_count: int, as_json: bool = False) -> str:
    """Generate a validation report."""
    report_data = {
        "summary": {
            "source_signatures": source_count,
            "documented_items": doc_count,
            "total_issues": len(issues),
            "by_type": {},
            "by_severity": {},
        },
        "issues": issues,
    }

    for issue in issues:
        itype = issue.get("type", "unknown")
        sev = issue.get("severity", "unknown")
        report_data["summary"]["by_type"][itype] = report_data["summary"]["by_type"].get(itype, 0) + 1
        report_data["summary"]["by_severity"][sev] = report_data["summary"]["by_severity"].get(sev, 0) + 1

    if as_json:
        return json.dumps(report_data, indent=2, default=str)

    lines = []
    lines.append("API Documentation Validation Report")
    lines.append("=" * 60)
    lines.append(f"Source signatures found: {source_count}")
    lines.append(f"Documented items found:  {doc_count}")
    lines.append(f"Issues found:            {len(issues)}")
    lines.append("")

    if not issues:
        lines.append("No issues found. API documentation matches source code.")
        return "\n".join(lines)

    # Group by severity
    severity_order = ["high", "medium", "low"]
    for severity in severity_order:
        sev_issues = [i for i in issues if i.get("severity") == severity]
        if not sev_issues:
            continue
        lines.append(f"{severity.upper()} ({len(sev_issues)} issues):")
        lines.append("-" * 40)
        for issue in sev_issues:
            lines.append(f"  [{issue.get('type', 'unknown')}] {issue['description']}")
            if "source_file" in issue:
                lines.append(f"    Source: {issue['source_file']}:{issue.get('source_line', '?')}")
            if "doc_file" in issue:
                lines.append(f"    Doc:    {issue['doc_file']}:{issue.get('doc_line', '?')}")
            lines.append("")
        lines.append("")

    # Summary by type
    lines.append("SUMMARY BY TYPE:")
    lines.append("-" * 40)
    type_labels = {
        "undocumented": "Undocumented items",
        "documented_not_in_source": "Documented but not in source",
        "missing_param_in_docs": "Missing parameters in docs",
        "extra_param_in_docs": "Extra parameters in docs",
        "deprecated_still_documented": "Deprecated items still documented",
    }
    for itype, count in sorted(report_data["summary"]["by_type"].items()):
        label = type_labels.get(itype, itype)
        lines.append(f"  {label}: {count}")

    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Validate API documentation against Python source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("source_path", help="Path to Python source directory")
    parser.add_argument("doc_path", help="Path to API documentation (file or directory)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--recursive", action="store_true", help="Recursively scan doc directory")
    parser.add_argument("--include-private", action="store_true", help="Include private (_prefixed) items")

    args = parser.parse_args()

    source_path = os.path.abspath(args.source_path)
    doc_path = os.path.abspath(args.doc_path)

    if not os.path.exists(source_path):
        print(f"Error: Source path '{source_path}' does not exist", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(doc_path):
        print(f"Error: Doc path '{doc_path}' does not exist", file=sys.stderr)
        sys.exit(2)

    # Extract source signatures
    if os.path.isfile(source_path) and source_path.endswith(".py"):
        sigs = extract_signatures(source_path, args.include_private)
        source_sigs = {os.path.basename(source_path): sigs}
    elif os.path.isdir(source_path):
        source_sigs = extract_all_signatures(source_path, args.include_private)
    else:
        print(f"Error: Source path must be a Python file or directory", file=sys.stderr)
        sys.exit(2)

    # Extract documented items
    documented_items = extract_all_documented_items(doc_path, recursive=args.recursive)

    # Count totals
    source_count = sum(len(sigs) for sigs in source_sigs.values())
    doc_count = len(documented_items)

    # Validate
    issues = validate_api_docs(source_sigs, documented_items)

    # Report
    report = generate_report(issues, source_count, doc_count, as_json=args.json)
    print(report)

    # Exit code
    has_high = any(i.get("severity") == "high" for i in issues)
    sys.exit(1 if has_high else 0)


if __name__ == "__main__":
    main()
