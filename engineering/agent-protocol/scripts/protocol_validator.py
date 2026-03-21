#!/usr/bin/env python3
"""Validate agent protocol configurations for MCP, A2A, and OpenAI Function Calling compliance.

Reads JSON tool schema files and checks them against protocol-specific rules:
- MCP: tool name conventions, description quality, inputSchema structure, required fields
- A2A: agent card completeness, skill definitions, capability declarations
- OpenAI: function calling schema, parameter types, strict mode readiness

Usage:
    python protocol_validator.py schema.json
    python protocol_validator.py --protocol mcp tools/*.json
    python protocol_validator.py --protocol a2a agent-card.json --json
    python protocol_validator.py --strict schema.json
"""

import argparse
import json
import os
import re
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Severity levels
# ---------------------------------------------------------------------------
SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"


def _issue(severity: str, code: str, message: str, path: str = "") -> dict:
    entry = {"severity": severity, "code": code, "message": message}
    if path:
        entry["path"] = path
    return entry


# ---------------------------------------------------------------------------
# JSON Schema type helpers
# ---------------------------------------------------------------------------
VALID_JSON_TYPES = {"string", "number", "integer", "boolean", "array", "object", "null"}
VALID_STRING_FORMATS = {
    "date", "date-time", "time", "email", "uri", "uri-reference",
    "hostname", "ipv4", "ipv6", "uuid", "regex",
}


def _validate_json_schema_fragment(schema: dict, path: str) -> list[dict]:
    """Validate a JSON Schema fragment for structural correctness."""
    issues: list[dict] = []
    if not isinstance(schema, dict):
        issues.append(_issue(SEVERITY_ERROR, "SCHEMA_NOT_OBJECT",
                             f"Schema at '{path}' must be an object, got {type(schema).__name__}", path))
        return issues

    stype = schema.get("type")
    if stype and stype not in VALID_JSON_TYPES:
        issues.append(_issue(SEVERITY_ERROR, "INVALID_TYPE",
                             f"Unknown JSON Schema type '{stype}'", path))

    if stype == "array":
        items = schema.get("items")
        if items is None:
            issues.append(_issue(SEVERITY_WARNING, "ARRAY_NO_ITEMS",
                                 "Array type should declare 'items' schema", path))
        elif isinstance(items, dict):
            issues.extend(_validate_json_schema_fragment(items, f"{path}.items"))

    if stype == "object":
        props = schema.get("properties", {})
        for pname, pdef in props.items():
            issues.extend(_validate_json_schema_fragment(pdef, f"{path}.properties.{pname}"))

    fmt = schema.get("format")
    if fmt and stype == "string" and fmt not in VALID_STRING_FORMATS:
        issues.append(_issue(SEVERITY_INFO, "UNKNOWN_FORMAT",
                             f"Non-standard string format '{fmt}' — agents may ignore it", path))

    if "enum" in schema:
        if not isinstance(schema["enum"], list) or len(schema["enum"]) == 0:
            issues.append(_issue(SEVERITY_ERROR, "EMPTY_ENUM",
                                 "Enum must be a non-empty array", path))

    return issues


# ---------------------------------------------------------------------------
# MCP validation
# ---------------------------------------------------------------------------
MCP_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
DESCRIPTION_TRIGGER_PHRASES = {"use when", "use this", "returns", "use for"}


def validate_mcp_tool(tool: dict, strict: bool = False) -> list[dict]:
    """Validate a single MCP tool definition."""
    issues: list[dict] = []

    # --- name ---
    name = tool.get("name")
    if not name:
        issues.append(_issue(SEVERITY_ERROR, "MISSING_NAME", "Tool definition missing 'name' field"))
    elif not MCP_NAME_RE.match(name):
        issues.append(_issue(SEVERITY_ERROR, "BAD_NAME_FORMAT",
                             f"Tool name '{name}' must be snake_case (lowercase alphanumeric + underscores)"))
    elif "_" not in name:
        issues.append(_issue(SEVERITY_WARNING, "NAME_NO_VERB_NOUN",
                             f"Tool name '{name}' should follow verb_noun pattern (e.g., search_documents)"))

    # --- description ---
    desc = tool.get("description", "")
    if not desc:
        issues.append(_issue(SEVERITY_ERROR, "MISSING_DESCRIPTION",
                             "Tool must have a description for LLM tool selection"))
    else:
        if len(desc) < 30:
            issues.append(_issue(SEVERITY_WARNING, "SHORT_DESCRIPTION",
                                 f"Description is only {len(desc)} chars — aim for 50+ for effective LLM guidance"))
        if len(desc) > 1024:
            issues.append(_issue(SEVERITY_WARNING, "LONG_DESCRIPTION",
                                 f"Description is {len(desc)} chars — consider shortening to under 1024"))
        desc_lower = desc.lower()
        if not any(phrase in desc_lower for phrase in DESCRIPTION_TRIGGER_PHRASES):
            issues.append(_issue(SEVERITY_WARNING, "DESCRIPTION_NO_USAGE_GUIDANCE",
                                 "Description should include usage guidance (e.g., 'Use when...', 'Returns...')"))
        if strict and not desc.rstrip().endswith("."):
            issues.append(_issue(SEVERITY_INFO, "DESCRIPTION_NO_PERIOD",
                                 "Description should end with a period for consistency"))

    # --- inputSchema ---
    schema = tool.get("inputSchema")
    if schema is None:
        issues.append(_issue(SEVERITY_WARNING, "MISSING_INPUT_SCHEMA",
                             "Tool has no inputSchema — consider adding one even if no parameters are needed"))
    elif not isinstance(schema, dict):
        issues.append(_issue(SEVERITY_ERROR, "INPUT_SCHEMA_NOT_OBJECT",
                             f"inputSchema must be an object, got {type(schema).__name__}"))
    else:
        if schema.get("type") != "object":
            issues.append(_issue(SEVERITY_ERROR, "INPUT_SCHEMA_TYPE",
                                 "inputSchema.type must be 'object'"))

        props = schema.get("properties", {})
        required = schema.get("required", [])

        if not isinstance(required, list):
            issues.append(_issue(SEVERITY_ERROR, "REQUIRED_NOT_ARRAY",
                                 "inputSchema.required must be an array"))
        else:
            for req_name in required:
                if req_name not in props:
                    issues.append(_issue(SEVERITY_ERROR, "REQUIRED_MISSING_PROP",
                                         f"Required field '{req_name}' not found in properties"))

        for pname, pdef in props.items():
            ppath = f"inputSchema.properties.{pname}"
            if not pdef.get("description"):
                issues.append(_issue(SEVERITY_WARNING, "PROP_NO_DESCRIPTION",
                                     f"Property '{pname}' missing description — LLMs need context", ppath))
            if not pdef.get("type"):
                issues.append(_issue(SEVERITY_WARNING, "PROP_NO_TYPE",
                                     f"Property '{pname}' missing type declaration", ppath))
            issues.extend(_validate_json_schema_fragment(pdef, ppath))

        if strict and not props:
            issues.append(_issue(SEVERITY_INFO, "NO_PROPERTIES",
                                 "inputSchema has no properties — is this intentional?"))

    return issues


# ---------------------------------------------------------------------------
# A2A Agent Card validation
# ---------------------------------------------------------------------------
def validate_a2a_agent_card(card: dict, strict: bool = False) -> list[dict]:
    """Validate a Google A2A agent card."""
    issues: list[dict] = []

    for field in ("name", "description", "url", "version"):
        if not card.get(field):
            issues.append(_issue(SEVERITY_ERROR, f"MISSING_{field.upper()}",
                                 f"Agent card missing required field '{field}'"))

    url = card.get("url", "")
    if url and not url.startswith(("http://", "https://")):
        issues.append(_issue(SEVERITY_ERROR, "INVALID_URL",
                             f"Agent URL '{url}' must start with http:// or https://"))

    provider = card.get("provider", {})
    if not provider.get("organization"):
        issues.append(_issue(SEVERITY_WARNING, "NO_PROVIDER_ORG",
                             "Agent card should include provider.organization"))

    caps = card.get("capabilities", {})
    if not isinstance(caps, dict):
        issues.append(_issue(SEVERITY_ERROR, "CAPABILITIES_NOT_OBJECT",
                             "capabilities must be an object"))
    else:
        for cap_key in ("streaming", "pushNotifications", "stateTransitionHistory"):
            if cap_key not in caps:
                issues.append(_issue(SEVERITY_INFO, f"NO_{cap_key.upper()}",
                                     f"capabilities.{cap_key} not declared — defaults to false"))

    auth = card.get("authentication", {})
    if not auth:
        issues.append(_issue(SEVERITY_WARNING, "NO_AUTH",
                             "Agent card has no authentication section"))
    else:
        if not auth.get("schemes"):
            issues.append(_issue(SEVERITY_WARNING, "NO_AUTH_SCHEMES",
                                 "authentication.schemes should list supported auth mechanisms"))

    skills = card.get("skills", [])
    if not skills:
        issues.append(_issue(SEVERITY_WARNING, "NO_SKILLS",
                             "Agent card should declare at least one skill"))
    for idx, skill in enumerate(skills):
        spath = f"skills[{idx}]"
        for sf in ("id", "name", "description"):
            if not skill.get(sf):
                issues.append(_issue(SEVERITY_ERROR, f"SKILL_MISSING_{sf.upper()}",
                                     f"Skill at {spath} missing '{sf}'", spath))
        if strict and not skill.get("examples"):
            issues.append(_issue(SEVERITY_INFO, "SKILL_NO_EXAMPLES",
                                 f"Skill at {spath} has no examples — adding examples improves discoverability",
                                 spath))

    input_modes = card.get("defaultInputModes", [])
    output_modes = card.get("defaultOutputModes", [])
    if not input_modes:
        issues.append(_issue(SEVERITY_INFO, "NO_INPUT_MODES",
                             "No defaultInputModes declared"))
    if not output_modes:
        issues.append(_issue(SEVERITY_INFO, "NO_OUTPUT_MODES",
                             "No defaultOutputModes declared"))

    return issues


# ---------------------------------------------------------------------------
# OpenAI Function Calling validation
# ---------------------------------------------------------------------------
def validate_openai_function(func: dict, strict: bool = False) -> list[dict]:
    """Validate an OpenAI function calling definition."""
    issues: list[dict] = []

    name = func.get("name")
    if not name:
        issues.append(_issue(SEVERITY_ERROR, "MISSING_NAME",
                             "Function definition missing 'name' field"))
    elif not re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*$", name):
        issues.append(_issue(SEVERITY_ERROR, "BAD_FUNCTION_NAME",
                             f"Function name '{name}' contains invalid characters"))
    if name and len(name) > 64:
        issues.append(_issue(SEVERITY_ERROR, "NAME_TOO_LONG",
                             f"Function name '{name}' exceeds 64-character limit"))

    desc = func.get("description", "")
    if not desc:
        issues.append(_issue(SEVERITY_ERROR, "MISSING_DESCRIPTION",
                             "Function must have a description"))
    elif len(desc) > 1024:
        issues.append(_issue(SEVERITY_WARNING, "LONG_DESCRIPTION",
                             f"Description is {len(desc)} chars — OpenAI recommends under 1024"))

    params = func.get("parameters")
    if params is not None:
        if params.get("type") != "object":
            issues.append(_issue(SEVERITY_ERROR, "PARAMS_TYPE",
                                 "parameters.type must be 'object'"))
        props = params.get("properties", {})
        for pname, pdef in props.items():
            ppath = f"parameters.properties.{pname}"
            issues.extend(_validate_json_schema_fragment(pdef, ppath))
            if not pdef.get("description"):
                issues.append(_issue(SEVERITY_WARNING, "PROP_NO_DESCRIPTION",
                                     f"Property '{pname}' missing description", ppath))

        if strict:
            required = params.get("required", [])
            additional = params.get("additionalProperties")
            if additional is not False:
                issues.append(_issue(SEVERITY_INFO, "STRICT_ADDITIONAL_PROPS",
                                     "For OpenAI strict mode, set additionalProperties: false"))
            for pname in props:
                if pname not in required:
                    issues.append(_issue(SEVERITY_INFO, "STRICT_ALL_REQUIRED",
                                         f"Strict mode requires all properties in 'required' — '{pname}' is optional"))

    return issues


# ---------------------------------------------------------------------------
# Auto-detect protocol
# ---------------------------------------------------------------------------
def detect_protocol(data: dict) -> str:
    """Heuristically detect which protocol a schema belongs to."""
    if "inputSchema" in data:
        return "mcp"
    if "skills" in data or "defaultInputModes" in data or "defaultOutputModes" in data:
        return "a2a"
    if "parameters" in data and "name" in data:
        return "openai"
    # Check if it wraps a list of tools
    if "tools" in data and isinstance(data["tools"], list):
        first = data["tools"][0] if data["tools"] else {}
        if "inputSchema" in first:
            return "mcp"
        if "function" in first:
            return "openai"
    return "unknown"


def validate_file(filepath: str, protocol: str, strict: bool) -> dict:
    """Validate a single file and return results."""
    result: dict[str, Any] = {"file": filepath, "protocol": protocol, "issues": []}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        result["issues"].append(_issue(SEVERITY_ERROR, "INVALID_JSON",
                                       f"Failed to parse JSON: {exc}"))
        return result
    except OSError as exc:
        result["issues"].append(_issue(SEVERITY_ERROR, "FILE_READ_ERROR", str(exc)))
        return result

    detected = protocol if protocol != "auto" else detect_protocol(data)
    result["protocol"] = detected

    if detected == "mcp":
        # Could be a single tool or a list
        tools = [data] if "name" in data else data.get("tools", [data])
        for idx, tool in enumerate(tools):
            tool_issues = validate_mcp_tool(tool, strict)
            for iss in tool_issues:
                iss["tool_index"] = idx
                iss.setdefault("path", "")
            result["issues"].extend(tool_issues)

    elif detected == "a2a":
        result["issues"].extend(validate_a2a_agent_card(data, strict))

    elif detected == "openai":
        funcs = [data] if "name" in data else [f.get("function", f) for f in data.get("tools", data.get("functions", [data]))]
        for idx, func in enumerate(funcs):
            func_issues = validate_openai_function(func, strict)
            for iss in func_issues:
                iss["function_index"] = idx
            result["issues"].extend(func_issues)

    else:
        result["issues"].append(_issue(SEVERITY_ERROR, "UNKNOWN_PROTOCOL",
                                       "Could not detect protocol — use --protocol to specify"))

    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------
SEVERITY_SYMBOLS = {
    SEVERITY_ERROR: "[ERROR]  ",
    SEVERITY_WARNING: "[WARN]   ",
    SEVERITY_INFO: "[INFO]   ",
}


def format_human(results: list[dict]) -> str:
    """Format validation results for human consumption."""
    lines: list[str] = []
    total_errors = 0
    total_warnings = 0

    for res in results:
        lines.append(f"\n{'='*60}")
        lines.append(f"File:     {res['file']}")
        lines.append(f"Protocol: {res['protocol']}")

        if not res["issues"]:
            lines.append("Status:   PASS — no issues found")
            continue

        errors = [i for i in res["issues"] if i["severity"] == SEVERITY_ERROR]
        warnings = [i for i in res["issues"] if i["severity"] == SEVERITY_WARNING]
        infos = [i for i in res["issues"] if i["severity"] == SEVERITY_INFO]
        total_errors += len(errors)
        total_warnings += len(warnings)

        lines.append(f"Status:   {len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info(s)")
        lines.append("-" * 60)

        for iss in res["issues"]:
            prefix = SEVERITY_SYMBOLS.get(iss["severity"], "         ")
            loc = ""
            if "tool_index" in iss:
                loc = f"[tool {iss['tool_index']}] "
            elif "function_index" in iss:
                loc = f"[func {iss['function_index']}] "
            if iss.get("path"):
                loc += f"({iss['path']}) "
            lines.append(f"  {prefix}{loc}{iss['code']}: {iss['message']}")

    lines.append(f"\n{'='*60}")
    lines.append(f"Total: {len(results)} file(s), {total_errors} error(s), {total_warnings} warning(s)")

    if total_errors > 0:
        lines.append("Result: FAIL")
    elif total_warnings > 0:
        lines.append("Result: PASS with warnings")
    else:
        lines.append("Result: PASS")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate agent protocol configurations (MCP, A2A, OpenAI Function Calling).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s tool.json\n"
            "  %(prog)s --protocol mcp tools/*.json\n"
            "  %(prog)s --protocol a2a agent-card.json --json\n"
            "  %(prog)s --strict --protocol openai functions.json\n"
        ),
    )
    parser.add_argument("files", nargs="+", metavar="FILE",
                        help="JSON schema file(s) to validate")
    parser.add_argument("--protocol", choices=["mcp", "a2a", "openai", "auto"],
                        default="auto",
                        help="Protocol to validate against (default: auto-detect)")
    parser.add_argument("--strict", action="store_true",
                        help="Enable strict validation with additional checks")
    parser.add_argument("--json", dest="json_output", action="store_true",
                        help="Output results as JSON")
    args = parser.parse_args()

    results: list[dict] = []
    for filepath in args.files:
        if not os.path.isfile(filepath):
            results.append({
                "file": filepath,
                "protocol": args.protocol,
                "issues": [_issue(SEVERITY_ERROR, "FILE_NOT_FOUND",
                                  f"File not found: {filepath}")]
            })
            continue
        results.append(validate_file(filepath, args.protocol, args.strict))

    if args.json_output:
        print(json.dumps({"results": results, "file_count": len(results)}, indent=2))
    else:
        print(format_human(results))

    has_errors = any(
        iss["severity"] == SEVERITY_ERROR
        for res in results
        for iss in res["issues"]
    )
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
