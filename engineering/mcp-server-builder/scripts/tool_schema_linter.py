#!/usr/bin/env python3
"""Flag interaction-design smells in MCP tool definitions.

Complements tool_linter.py (which checks naming, description quality, and schema
completeness). This linter focuses on how a tool behaves in a conversation:
chatty single-item tools that should accept batches, list/read tools missing
pagination, destructive tools lacking a confirmation or dry-run gate, and overly
broad inputs. Heuristics are name/description/schema based — treat findings as
prompts to review intent, not hard failures.

Usage:
    python tool_schema_linter.py tools.json
    python tool_schema_linter.py server_config.json --path tools --json
    python tool_schema_linter.py tools.json --strict
"""

import argparse
import json
import re
import sys

SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

# Verbs whose plural-noun form implies the caller may act on many items.
BATCHABLE_VERBS = {
    "delete", "remove", "update", "create", "add", "fetch", "get", "send",
    "process", "import", "export", "sync", "tag", "label", "archive", "move",
}

# Verbs that return collections and therefore should paginate.
LIST_VERBS = {"list", "search", "query", "find", "scan"}

# Verbs that change or destroy state and should be gated.
DESTRUCTIVE_VERBS = {
    "delete", "remove", "drop", "destroy", "purge", "wipe", "truncate",
    "deploy", "send", "publish", "execute", "run", "restart", "stop",
    "terminate", "revoke", "reset", "overwrite", "merge", "cancel",
}

DESTRUCTIVE_DESC_RE = re.compile(
    r"\b(delete|remove|destroy|purge|wipe|drop|truncate|irreversibl|permanent|"
    r"cannot be undone|overwrit|send(s)? (an? )?(email|message|notification)|"
    r"charge|payment|deploy|terminate|revoke)\w*", re.IGNORECASE)

# Schema keys that suggest a confirmation / dry-run gate is present.
GATE_KEYS = {"confirm", "confirmation", "dry_run", "dryrun", "force",
             "acknowledge", "i_understand", "yes_really"}

# Schema keys that suggest pagination is present.
PAGE_KEYS = {"limit", "page", "page_size", "per_page", "cursor", "offset",
             "next_cursor", "page_token", "max_results", "top", "count"}

# Schema keys that suggest the input already accepts many items.
BATCH_KEYS = {"ids", "items", "records", "batch", "entries", "objects",
              "rows", "documents", "files", "keys", "targets"}

SINGULAR_ID_RE = re.compile(r"^[a-z]+_?id$|^id$|^[a-z]+_?name$")


def _verb(name: str) -> str:
    return name.split("_")[0] if name else ""


def _schema(tool: dict) -> dict:
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    return schema if isinstance(schema, dict) else {}


def _properties(tool: dict) -> dict:
    props = _schema(tool).get("properties", {})
    return props if isinstance(props, dict) else {}


def _has_array_input(tool: dict) -> bool:
    props = _properties(tool)
    if any(k.lower() in BATCH_KEYS for k in props):
        return True
    for prop_def in props.values():
        if isinstance(prop_def, dict) and prop_def.get("type") == "array":
            return True
    return False


def lint_batch(tool: dict) -> list[dict]:
    """Flag single-item tools whose operation is naturally repeated."""
    name = tool.get("name", "<unnamed>")
    verb = _verb(name)
    if verb not in BATCHABLE_VERBS:
        return []
    if _has_array_input(tool):
        return []
    props = _properties(tool)
    singular_id_props = [k for k in props if SINGULAR_ID_RE.match(k.lower())]
    if not singular_id_props:
        return []
    return [{
        "rule": "batch-friendly",
        "severity": SEVERITY_WARNING,
        "message": (f"Tool '{name}' takes a single '{singular_id_props[0]}' — agents must call it "
                    f"once per item. Consider accepting an array (e.g. '{singular_id_props[0]}s') "
                    f"with per-item partial-failure results."),
    }]


def lint_pagination(tool: dict) -> list[dict]:
    """Flag list/search tools that return collections without pagination."""
    name = tool.get("name", "<unnamed>")
    if _verb(name) not in LIST_VERBS:
        return []
    props = _properties(tool)
    if any(k.lower() in PAGE_KEYS for k in props):
        return []
    return [{
        "rule": "list-pagination",
        "severity": SEVERITY_WARNING,
        "message": (f"Tool '{name}' returns a collection but exposes no pagination/limit param "
                    f"(limit, cursor, page_size...). Unbounded lists flood the context and risk "
                    f"truncation — add a capped page size and a cursor."),
    }]


def lint_destructive_gate(tool: dict) -> list[dict]:
    """Flag destructive/irreversible tools lacking a confirm or dry-run param."""
    name = tool.get("name", "<unnamed>")
    desc = tool.get("description", "") or ""
    verb = _verb(name)
    is_destructive = verb in DESTRUCTIVE_VERBS or bool(DESTRUCTIVE_DESC_RE.search(desc))
    if not is_destructive:
        return []
    props = _properties(tool)
    if any(k.lower() in GATE_KEYS for k in props):
        return []
    return [{
        "rule": "destructive-gate",
        "severity": SEVERITY_WARNING,
        "message": (f"Tool '{name}' appears destructive/irreversible but has no confirmation or "
                    f"dry-run param (confirm, dry_run...). Add an explicit gate so the action is "
                    f"committed deliberately, and default to the safe path."),
    }]


def lint_broad_input(tool: dict) -> list[dict]:
    """Flag overly broad / underspecified inputs that invite misuse."""
    issues = []
    name = tool.get("name", "<unnamed>")
    schema = _schema(tool)
    props = _properties(tool)

    # Free-form object/string passthroughs with no constraints.
    for prop_name, prop_def in props.items():
        if not isinstance(prop_def, dict):
            continue
        ptype = prop_def.get("type")
        constrained = any(k in prop_def for k in
                          ("enum", "pattern", "format", "properties", "items", "maxLength"))
        if ptype in ("object", None) and not constrained and "$ref" not in prop_def:
            issues.append({
                "rule": "broad-input",
                "severity": SEVERITY_INFO,
                "message": (f"Tool '{name}' property '{prop_name}' is an unconstrained "
                            f"object/any — narrow it with properties, enum, or pattern so the "
                            f"agent knows what is valid."),
            })

    # additionalProperties left open on the root schema.
    if schema.get("additionalProperties") is True:
        issues.append({
            "rule": "broad-input",
            "severity": SEVERITY_INFO,
            "message": (f"Tool '{name}' sets additionalProperties: true — the input is open-ended. "
                        f"Close it to keep calls predictable."),
        })

    # Everything optional on a tool that clearly needs an argument.
    if props and not schema.get("required"):
        issues.append({
            "rule": "broad-input",
            "severity": SEVERITY_INFO,
            "message": (f"Tool '{name}' marks no property as required — if the action needs an "
                        f"input, mark it required so the agent supplies it."),
        })

    return issues


def lint_tool(tool: dict) -> list[dict]:
    issues = []
    issues.extend(lint_batch(tool))
    issues.extend(lint_pagination(tool))
    issues.extend(lint_destructive_gate(tool))
    issues.extend(lint_broad_input(tool))
    return issues


def load_tools(file_path: str, json_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if json_path:
        for key in json_path.split("."):
            if isinstance(data, dict) and key in data:
                data = data[key]
            elif isinstance(data, list):
                try:
                    data = data[int(key)]
                except (ValueError, IndexError):
                    raise ValueError(f"Cannot traverse path '{json_path}' — key '{key}' not found")
            else:
                raise ValueError(f"Cannot traverse path '{json_path}' — key '{key}' not found")

    if isinstance(data, dict) and "name" in data:
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError(f"Expected a tool object or array of tools, got {type(data).__name__}")


def main():
    parser = argparse.ArgumentParser(
        description="Flag interaction-design smells (batch, pagination, destructive gate, "
                    "broad input) in MCP tool definitions.",
        epilog="Example: %(prog)s tools.json --strict",
    )
    parser.add_argument("file", help="JSON file containing MCP tool definitions")
    parser.add_argument("--path", default=None,
                        help="Dot-separated path to the tools array within the JSON (e.g. 'tools')")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any warnings are found (not just on hard failures)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON instead of human-readable text")
    args = parser.parse_args()

    try:
        tools = load_tools(args.file, args.path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        if args.json:
            json.dump({"error": str(e)}, sys.stdout, indent=2)
            print()
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    all_results = []
    total_warnings = 0
    total_info = 0

    for tool in tools:
        issues = lint_tool(tool)
        warnings = [i for i in issues if i["severity"] == SEVERITY_WARNING]
        infos = [i for i in issues if i["severity"] == SEVERITY_INFO]
        total_warnings += len(warnings)
        total_info += len(infos)
        all_results.append({
            "tool": tool.get("name", "<unnamed>"),
            "issues": issues,
            "counts": {"warnings": len(warnings), "info": len(infos)},
        })

    clean = total_warnings == 0 and (not args.strict or total_info == 0)
    output = {
        "tools_checked": len(tools),
        "total_warnings": total_warnings,
        "total_info": total_info,
        "clean": clean,
        "results": all_results,
    }

    if args.json:
        json.dump(output, sys.stdout, indent=2)
        print()
    else:
        for result in all_results:
            print(f"\n{result['tool']}")
            if not result["issues"]:
                print("  No design smells found.")
            for issue in result["issues"]:
                prefix = {"warning": "W", "info": "I"}.get(issue["severity"], "?")
                print(f"  {prefix} [{issue['rule']}] {issue['message']}")
        print(f"\n{'=' * 60}")
        print(f"Tools checked: {len(tools)}")
        print(f"Warnings: {total_warnings}  Info: {total_info}")
        print("Result: CLEAN" if clean else "Result: SMELLS FOUND")

    # Warnings drive the exit code; --strict also fails on info.
    failed = total_warnings > 0 or (args.strict and total_info > 0)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
