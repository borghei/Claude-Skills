#!/usr/bin/env python3
"""Generate tool schema definitions for MCP, A2A, and OpenAI Function Calling.

Creates well-structured protocol schemas from:
- Inline parameter definitions (--param name:type:description)
- JSON config files describing tools
- Python function signatures (parsed from source files)

Usage:
    python schema_generator.py --name search_documents --desc "Search docs" --param query:string:required:"Search query"
    python schema_generator.py --from-config tools.json --protocol mcp
    python schema_generator.py --from-python module.py --function my_func --protocol openai
    python schema_generator.py --name research --protocol a2a --skill-tags research,web --json
"""

import argparse
import ast
import json
import os
import re
import sys
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Python type -> JSON Schema type mapping
# ---------------------------------------------------------------------------
PY_TYPE_MAP: dict[str, dict[str, Any]] = {
    "str": {"type": "string"},
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "bool": {"type": "boolean"},
    "list": {"type": "array"},
    "dict": {"type": "object"},
    "List": {"type": "array"},
    "Dict": {"type": "object"},
    "Optional": {},  # handled separately
    "None": {"type": "null"},
    "NoneType": {"type": "null"},
}

CLI_TYPE_MAP: dict[str, str] = {
    "string": "string",
    "str": "string",
    "int": "integer",
    "integer": "integer",
    "float": "number",
    "number": "number",
    "bool": "boolean",
    "boolean": "boolean",
    "array": "array",
    "list": "array",
    "object": "object",
    "dict": "object",
}


# ---------------------------------------------------------------------------
# Parameter parsing from CLI --param flags
# ---------------------------------------------------------------------------
def parse_param_spec(spec: str) -> dict:
    """Parse a parameter specification string.

    Format: name:type[:required|optional][:description]
    Examples:
        query:string:required:"The search query"
        limit:integer:optional:"Max results"
        tags:array:"List of tags"
    """
    # Handle quoted descriptions
    parts: list[str] = []
    current = ""
    in_quotes = False
    for ch in spec:
        if ch == '"' or ch == "'":
            in_quotes = not in_quotes
        elif ch == ':' and not in_quotes:
            parts.append(current)
            current = ""
            continue
        current += ch
    parts.append(current)

    if len(parts) < 2:
        raise ValueError(f"Parameter spec needs at least name:type — got '{spec}'")

    name = parts[0].strip()
    ptype = CLI_TYPE_MAP.get(parts[1].strip().lower(), "string")

    required = True
    description = ""

    for part in parts[2:]:
        stripped = part.strip().strip('"').strip("'")
        if stripped.lower() == "required":
            required = True
        elif stripped.lower() == "optional":
            required = False
        else:
            description = stripped

    result: dict[str, Any] = {"name": name, "type": ptype, "required": required}
    if description:
        result["description"] = description
    return result


# ---------------------------------------------------------------------------
# Python source parsing
# ---------------------------------------------------------------------------
def extract_function_schema(source_path: str, function_name: str) -> dict:
    """Extract parameter schema from a Python function's signature and docstring."""
    with open(source_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=source_path)

    func_node: Optional[ast.FunctionDef] = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                func_node = node
                break

    if func_node is None:
        raise ValueError(f"Function '{function_name}' not found in {source_path}")

    # Extract docstring
    docstring = ast.get_docstring(func_node) or ""

    # Parse docstring for parameter descriptions (Google/NumPy style)
    param_docs: dict[str, str] = {}
    doc_lines = docstring.split("\n")
    in_params = False
    current_param = ""
    for line in doc_lines:
        stripped = line.strip()
        if stripped.lower() in ("args:", "parameters:", "params:"):
            in_params = True
            continue
        if in_params:
            if stripped.lower() in ("returns:", "raises:", "yields:", "examples:", "note:", "notes:"):
                in_params = False
                continue
            # Match "param_name (type): description" or "param_name: description"
            m = re.match(r"(\w+)\s*(?:\([^)]*\))?\s*:\s*(.*)", stripped)
            if m:
                current_param = m.group(1)
                param_docs[current_param] = m.group(2).strip()
            elif current_param and stripped:
                param_docs[current_param] += " " + stripped

    # Extract parameters from function signature
    params: list[dict] = []
    args = func_node.args

    # Count defaults to determine which args are optional
    num_defaults = len(args.defaults)
    num_args = len(args.args)

    for idx, arg in enumerate(args.args):
        if arg.arg in ("self", "cls"):
            continue

        param: dict[str, Any] = {"name": arg.arg}

        # Resolve type annotation
        if arg.annotation:
            type_str = _annotation_to_string(arg.annotation)
            is_optional, base_type = _parse_type_string(type_str)
            json_type = PY_TYPE_MAP.get(base_type, {}).get("type", "string")
            param["type"] = json_type
            param["required"] = not is_optional
        else:
            param["type"] = "string"
            param["required"] = True

        # Check if it has a default value
        default_idx = idx - (num_args - num_defaults)
        if default_idx >= 0:
            param["required"] = False
            default_node = args.defaults[default_idx]
            default_val = _extract_default(default_node)
            if default_val is not None:
                param["default"] = default_val

        if arg.arg in param_docs:
            param["description"] = param_docs[arg.arg]

        params.append(param)

    # First line of docstring as function description
    func_desc = doc_lines[0].strip() if doc_lines else ""

    return {
        "name": function_name,
        "description": func_desc,
        "params": params,
    }


def _annotation_to_string(node: ast.expr) -> str:
    """Convert an AST annotation node to a string representation."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Attribute):
        return f"{_annotation_to_string(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        base = _annotation_to_string(node.value)
        sl = _annotation_to_string(node.slice)
        return f"{base}[{sl}]"
    if isinstance(node, ast.Tuple):
        return ", ".join(_annotation_to_string(e) for e in node.elts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left = _annotation_to_string(node.left)
        right = _annotation_to_string(node.right)
        return f"{left} | {right}"
    return "Any"


def _parse_type_string(type_str: str) -> tuple[bool, str]:
    """Parse a type string and return (is_optional, base_type)."""
    is_optional = False
    # Handle Optional[X] and X | None
    m = re.match(r"Optional\[(\w+)]", type_str)
    if m:
        return True, m.group(1)
    if "| None" in type_str or "None |" in type_str:
        base = type_str.replace("| None", "").replace("None |", "").strip()
        return True, base
    return is_optional, type_str.split("[")[0]


def _extract_default(node: ast.expr) -> Any:
    """Extract a default value from an AST node."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return []
    if isinstance(node, ast.Dict):
        return {}
    if isinstance(node, ast.Name) and node.id == "None":
        return None
    return None


# ---------------------------------------------------------------------------
# Schema generation for each protocol
# ---------------------------------------------------------------------------
def generate_mcp_schema(name: str, description: str, params: list[dict]) -> dict:
    """Generate an MCP tool schema."""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for p in params:
        prop: dict[str, Any] = {"type": p["type"]}
        if p.get("description"):
            prop["description"] = p["description"]
        if "default" in p:
            prop["default"] = p["default"]
        if "enum" in p:
            prop["enum"] = p["enum"]
        properties[p["name"]] = prop
        if p.get("required", True):
            required.append(p["name"])

    schema: dict[str, Any] = {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
        },
    }
    if required:
        schema["inputSchema"]["required"] = required

    return schema


def generate_openai_schema(name: str, description: str, params: list[dict],
                           strict: bool = False) -> dict:
    """Generate an OpenAI function calling schema."""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for p in params:
        prop: dict[str, Any] = {"type": p["type"]}
        if p.get("description"):
            prop["description"] = p["description"]
        if "enum" in p:
            prop["enum"] = p["enum"]
        properties[p["name"]] = prop
        if p.get("required", True) or strict:
            required.append(p["name"])

    func_def: dict[str, Any] = {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
        },
    }
    if required:
        func_def["parameters"]["required"] = required
    if strict:
        func_def["parameters"]["additionalProperties"] = False
        func_def["strict"] = True

    return {"type": "function", "function": func_def}


def generate_a2a_agent_card(name: str, description: str, url: str = "https://agent.example.com",
                            org: str = "Organization", skill_tags: list[str] | None = None,
                            streaming: bool = False) -> dict:
    """Generate an A2A agent card."""
    card: dict[str, Any] = {
        "name": name,
        "description": description,
        "url": url,
        "provider": {
            "organization": org,
            "url": f"https://{org.lower().replace(' ', '-')}.example.com",
        },
        "version": "1.0.0",
        "capabilities": {
            "streaming": streaming,
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "authentication": {
            "schemes": ["Bearer"],
            "credentials": "oauth2",
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain", "application/json"],
        "skills": [
            {
                "id": name.lower().replace(" ", "-"),
                "name": name,
                "description": description,
                "tags": skill_tags or [],
                "examples": [],
            }
        ],
    }
    return card


# ---------------------------------------------------------------------------
# Config file parsing
# ---------------------------------------------------------------------------
def load_config(filepath: str) -> list[dict]:
    """Load tool definitions from a JSON config file.

    Expected format:
    {
      "tools": [
        {
          "name": "tool_name",
          "description": "...",
          "params": [
            {"name": "query", "type": "string", "required": true, "description": "..."}
          ]
        }
      ]
    }
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if "tools" in data:
        return data["tools"]
    # Single tool
    return [data]


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------
def format_human_schema(schema: dict, protocol: str) -> str:
    """Format a schema for human-readable output."""
    lines: list[str] = []
    lines.append(f"Protocol: {protocol.upper()}")
    lines.append(f"{'='*50}")

    if protocol == "mcp":
        lines.append(f"Tool:        {schema.get('name', 'N/A')}")
        lines.append(f"Description: {schema.get('description', 'N/A')}")
        isc = schema.get("inputSchema", {})
        props = isc.get("properties", {})
        required = set(isc.get("required", []))
        if props:
            lines.append(f"\nParameters ({len(props)}):")
            for pname, pdef in props.items():
                req_marker = "*" if pname in required else " "
                ptype = pdef.get("type", "any")
                pdesc = pdef.get("description", "")
                default = f" [default: {pdef['default']}]" if "default" in pdef else ""
                lines.append(f"  {req_marker} {pname}: {ptype}{default}")
                if pdesc:
                    lines.append(f"      {pdesc}")
            lines.append("\n  * = required")

    elif protocol == "openai":
        func = schema.get("function", schema)
        lines.append(f"Function:    {func.get('name', 'N/A')}")
        lines.append(f"Description: {func.get('description', 'N/A')}")
        params = func.get("parameters", {})
        props = params.get("properties", {})
        required = set(params.get("required", []))
        if props:
            lines.append(f"\nParameters ({len(props)}):")
            for pname, pdef in props.items():
                req_marker = "*" if pname in required else " "
                ptype = pdef.get("type", "any")
                pdesc = pdef.get("description", "")
                lines.append(f"  {req_marker} {pname}: {ptype}")
                if pdesc:
                    lines.append(f"      {pdesc}")
            lines.append("\n  * = required")
        if func.get("strict"):
            lines.append("\n  [STRICT MODE enabled]")

    elif protocol == "a2a":
        lines.append(f"Agent:       {schema.get('name', 'N/A')}")
        lines.append(f"Description: {schema.get('description', 'N/A')}")
        lines.append(f"URL:         {schema.get('url', 'N/A')}")
        lines.append(f"Version:     {schema.get('version', 'N/A')}")
        caps = schema.get("capabilities", {})
        lines.append(f"\nCapabilities:")
        for k, v in caps.items():
            lines.append(f"  {k}: {v}")
        skills = schema.get("skills", [])
        if skills:
            lines.append(f"\nSkills ({len(skills)}):")
            for s in skills:
                lines.append(f"  - {s.get('name', 'N/A')}: {s.get('description', '')}")
                if s.get("tags"):
                    lines.append(f"    Tags: {', '.join(s['tags'])}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate tool schema definitions for MCP, A2A, and OpenAI protocols.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  %(prog)s --name search_docs --desc "Search documents." '
            '--param query:string:required:"Search query" --param limit:int:optional:"Max results"\n'
            "  %(prog)s --from-python api.py --function search_docs --protocol openai\n"
            "  %(prog)s --from-config tools.json --protocol mcp --json\n"
            '  %(prog)s --name "Research Agent" --protocol a2a --skill-tags research,web\n'
        ),
    )

    source_group = parser.add_argument_group("input source (pick one)")
    source_group.add_argument("--name", help="Tool/agent name")
    source_group.add_argument("--desc", "--description", dest="description", default="",
                              help="Tool/agent description")
    source_group.add_argument("--param", action="append", dest="params", metavar="SPEC",
                              help="Parameter spec: name:type[:required|optional][:description]")
    source_group.add_argument("--from-python", metavar="FILE",
                              help="Extract schema from a Python function signature")
    source_group.add_argument("--function", help="Function name to extract (with --from-python)")
    source_group.add_argument("--from-config", metavar="FILE",
                              help="Load tool definitions from a JSON config file")

    output_group = parser.add_argument_group("output options")
    output_group.add_argument("--protocol", choices=["mcp", "a2a", "openai"], default="mcp",
                              help="Target protocol (default: mcp)")
    output_group.add_argument("--strict", action="store_true",
                              help="Enable strict mode (OpenAI: all required + no additionalProperties)")
    output_group.add_argument("--json", dest="json_output", action="store_true",
                              help="Output as JSON (default for piping)")
    output_group.add_argument("--output", "-o", metavar="FILE",
                              help="Write output to file instead of stdout")

    # A2A-specific options
    a2a_group = parser.add_argument_group("A2A options")
    a2a_group.add_argument("--url", default="https://agent.example.com",
                           help="Agent URL for A2A agent card")
    a2a_group.add_argument("--org", default="Organization",
                           help="Provider organization name")
    a2a_group.add_argument("--skill-tags", default="",
                           help="Comma-separated skill tags for A2A agent card")
    a2a_group.add_argument("--streaming", action="store_true",
                           help="Enable streaming capability in A2A agent card")

    args = parser.parse_args()

    schemas: list[dict] = []

    # Source: config file
    if args.from_config:
        if not os.path.isfile(args.from_config):
            print(f"Error: Config file not found: {args.from_config}", file=sys.stderr)
            return 1
        tools = load_config(args.from_config)
        for tool in tools:
            name = tool.get("name", "unnamed_tool")
            desc = tool.get("description", "")
            params = tool.get("params", [])
            if args.protocol == "mcp":
                schemas.append(generate_mcp_schema(name, desc, params))
            elif args.protocol == "openai":
                schemas.append(generate_openai_schema(name, desc, params, args.strict))
            elif args.protocol == "a2a":
                tags = [t.strip() for t in args.skill_tags.split(",") if t.strip()]
                schemas.append(generate_a2a_agent_card(name, desc, args.url, args.org, tags, args.streaming))

    # Source: Python function
    elif args.from_python:
        if not os.path.isfile(args.from_python):
            print(f"Error: Python file not found: {args.from_python}", file=sys.stderr)
            return 1
        if not args.function:
            print("Error: --function is required with --from-python", file=sys.stderr)
            return 1
        try:
            extracted = extract_function_schema(args.from_python, args.function)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        name = extracted["name"]
        desc = extracted["description"]
        params = extracted["params"]
        if args.protocol == "mcp":
            schemas.append(generate_mcp_schema(name, desc, params))
        elif args.protocol == "openai":
            schemas.append(generate_openai_schema(name, desc, params, args.strict))
        elif args.protocol == "a2a":
            tags = [t.strip() for t in args.skill_tags.split(",") if t.strip()]
            schemas.append(generate_a2a_agent_card(name, desc, args.url, args.org, tags, args.streaming))

    # Source: inline params
    elif args.name:
        params = []
        for spec in (args.params or []):
            try:
                params.append(parse_param_spec(spec))
            except ValueError as exc:
                print(f"Error parsing param: {exc}", file=sys.stderr)
                return 1

        if args.protocol == "mcp":
            schemas.append(generate_mcp_schema(args.name, args.description, params))
        elif args.protocol == "openai":
            schemas.append(generate_openai_schema(args.name, args.description, params, args.strict))
        elif args.protocol == "a2a":
            tags = [t.strip() for t in args.skill_tags.split(",") if t.strip()]
            schemas.append(generate_a2a_agent_card(
                args.name, args.description, args.url, args.org, tags, args.streaming))
    else:
        parser.print_help()
        return 1

    # Output
    if len(schemas) == 1:
        output_data = schemas[0]
    else:
        output_data = {"tools": schemas}

    if args.json_output or args.output:
        output_text = json.dumps(output_data, indent=2)
    else:
        parts = []
        for s in schemas:
            parts.append(format_human_schema(s, args.protocol))
        output_text = "\n\n".join(parts)
        output_text += "\n\n--- JSON ---\n" + json.dumps(output_data, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
        print(f"Schema written to {args.output}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
