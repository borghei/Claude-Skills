#!/usr/bin/env python3
"""Generate API test skeletons from OpenAPI/Swagger spec files.

Parses OpenAPI 3.x or Swagger 2.0 JSON spec files and generates test
code scaffolds covering auth, validation, happy path, and error cases
for each endpoint. Outputs pytest+httpx (Python) or vitest+supertest
(TypeScript) test files.

Usage:
    python test_generator.py spec.json --framework pytest
    python test_generator.py spec.json --framework vitest --output tests/
    python test_generator.py spec.json --json
"""

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path


def load_spec(spec_path: str) -> dict:
    """Load and validate an OpenAPI/Swagger spec file."""
    path = Path(spec_path)
    if not path.exists():
        print(f"Error: spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    if not path.suffix.lower() == ".json":
        print("Error: only JSON spec files are supported", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in spec file: {e}", file=sys.stderr)
        sys.exit(1)
    # Basic validation
    if "openapi" not in spec and "swagger" not in spec:
        print("Error: file does not appear to be an OpenAPI or Swagger spec", file=sys.stderr)
        sys.exit(1)
    return spec


def extract_endpoints(spec: dict) -> list:
    """Extract endpoint definitions from spec paths."""
    endpoints = []
    paths = spec.get("paths", {})
    for path, path_item in paths.items():
        for method in ("get", "post", "put", "patch", "delete"):
            if method not in path_item:
                continue
            operation = path_item[method]
            endpoint = {
                "path": path,
                "method": method.upper(),
                "operation_id": operation.get("operationId", ""),
                "summary": operation.get("summary", ""),
                "tags": operation.get("tags", []),
                "parameters": operation.get("parameters", []),
                "request_body": None,
                "responses": {},
                "security": operation.get("security", path_item.get("security", spec.get("security", []))),
            }
            # Extract request body schema
            req_body = operation.get("requestBody", {})
            if req_body:
                content = req_body.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema", {})
                endpoint["request_body"] = _resolve_schema(spec, schema)
            # Extract response status codes
            for status, resp in operation.get("responses", {}).items():
                endpoint["responses"][status] = resp.get("description", "")
            endpoints.append(endpoint)
    return endpoints


def _resolve_schema(spec: dict, schema: dict) -> dict:
    """Resolve a $ref in a schema to its definition."""
    if "$ref" in schema:
        ref_path = schema["$ref"]
        parts = ref_path.lstrip("#/").split("/")
        resolved = spec
        for part in parts:
            resolved = resolved.get(part, {})
        return resolved
    return schema


def _extract_required_fields(schema: dict) -> list:
    """Get required field names from a schema."""
    return schema.get("required", [])


def _extract_properties(schema: dict) -> dict:
    """Get properties with their types from a schema."""
    props = {}
    for name, prop in schema.get("properties", {}).items():
        props[name] = {
            "type": prop.get("type", "string"),
            "format": prop.get("format"),
            "enum": prop.get("enum"),
            "max_length": prop.get("maxLength"),
            "min_length": prop.get("minLength"),
            "minimum": prop.get("minimum"),
            "maximum": prop.get("maximum"),
        }
    return props


def _has_auth(endpoint: dict) -> bool:
    """Check if endpoint requires authentication."""
    return bool(endpoint.get("security"))


def _make_test_name(endpoint: dict) -> str:
    """Create a descriptive test function/describe name."""
    op_id = endpoint.get("operation_id")
    if op_id:
        return op_id
    method = endpoint["method"].lower()
    path_slug = endpoint["path"].strip("/").replace("/", "_").replace("{", "").replace("}", "")
    return f"{method}_{path_slug}"


# --- Pytest (Python) Generator ---

def generate_pytest(endpoints: list, spec: dict) -> dict:
    """Generate pytest+httpx test files. Returns {filename: content}."""
    files = {}
    # Group endpoints by first tag or path segment
    groups = {}
    for ep in endpoints:
        tag = ep["tags"][0] if ep["tags"] else ep["path"].strip("/").split("/")[0]
        tag = tag.lower().replace(" ", "_").replace("-", "_")
        groups.setdefault(tag, []).append(ep)

    for group_name, group_eps in groups.items():
        lines = [
            '"""Auto-generated API tests for {group}."""'.format(group=group_name),
            "import httpx",
            "import pytest",
            "",
            "",
            'BASE_URL = "http://localhost:8000"',
            "",
            "",
            "def auth_headers(token: str = \"test-token\") -> dict:",
            '    return {"Authorization": f"Bearer {token}"}',
            "",
        ]
        for ep in group_eps:
            test_name = _make_test_name(ep)
            method_lower = ep["method"].lower()
            path = ep["path"]
            summary = ep["summary"] or f'{ep["method"]} {ep["path"]}'

            # Happy path test
            lines.append("")
            lines.append(f"class Test{test_name.title().replace('_', '')}:")
            lines.append(f'    """{summary}"""')
            lines.append("")

            # Auth tests
            if _has_auth(ep):
                lines.append(f"    def test_returns_401_without_auth(self):")
                lines.append(f'        """Missing Authorization header returns 401."""')
                lines.append(f"        response = httpx.{method_lower}(")
                lines.append(f'            f"{{BASE_URL}}{path}"')
                lines.append(f"        )")
                lines.append(f"        assert response.status_code == 401")
                lines.append("")
                lines.append(f"    def test_returns_401_with_expired_token(self):")
                lines.append(f'        """Expired token returns 401."""')
                lines.append(f"        response = httpx.{method_lower}(")
                lines.append(f'            f"{{BASE_URL}}{path}",')
                lines.append(f'            headers=auth_headers("expired-token")')
                lines.append(f"        )")
                lines.append(f"        assert response.status_code == 401")
                lines.append("")

            # Validation tests for POST/PUT/PATCH with request body
            if ep["request_body"] and ep["method"] in ("POST", "PUT", "PATCH"):
                schema = ep["request_body"]
                required = _extract_required_fields(schema)
                properties = _extract_properties(schema)

                if required:
                    lines.append(f"    def test_returns_422_with_empty_body(self):")
                    lines.append(f'        """Empty request body returns 422."""')
                    lines.append(f"        response = httpx.{method_lower}(")
                    lines.append(f'            f"{{BASE_URL}}{path}",')
                    lines.append(f"            json={{}},")
                    if _has_auth(ep):
                        lines.append(f"            headers=auth_headers()")
                    lines.append(f"        )")
                    lines.append(f"        assert response.status_code == 422")
                    lines.append("")

                for field_name in required:
                    lines.append(f"    def test_returns_422_when_{field_name}_missing(self):")
                    lines.append(f'        """Missing required field {field_name} returns 422."""')
                    sample = _build_sample_payload(properties, required, exclude=field_name)
                    lines.append(f"        payload = {json.dumps(sample, indent=8)}")
                    lines.append(f"        response = httpx.{method_lower}(")
                    lines.append(f'            f"{{BASE_URL}}{path}",')
                    lines.append(f"            json=payload,")
                    if _has_auth(ep):
                        lines.append(f"            headers=auth_headers()")
                    lines.append(f"        )")
                    lines.append(f"        assert response.status_code == 422")
                    lines.append("")

                # Type mismatch tests
                for field_name, field_info in properties.items():
                    if field_info["type"] == "string":
                        lines.append(f"    def test_returns_422_when_{field_name}_wrong_type(self):")
                        lines.append(f'        """Wrong type for {field_name} returns 422."""')
                        sample = _build_sample_payload(properties, required)
                        sample[field_name] = 99999
                        lines.append(f"        payload = {json.dumps(sample, indent=8)}")
                        lines.append(f"        response = httpx.{method_lower}(")
                        lines.append(f'            f"{{BASE_URL}}{path}",')
                        lines.append(f"            json=payload,")
                        if _has_auth(ep):
                            lines.append(f"            headers=auth_headers()")
                        lines.append(f"        )")
                        lines.append(f"        assert response.status_code == 422")
                        lines.append("")

            # Happy path
            happy_status = "200"
            if ep["method"] == "POST":
                happy_status = "201" if "201" in ep["responses"] else "200"
            elif ep["method"] == "DELETE":
                happy_status = "204" if "204" in ep["responses"] else "200"

            lines.append(f"    def test_success(self):")
            lines.append(f'        """Successful {ep["method"]} returns {happy_status}."""')
            if ep["request_body"] and ep["method"] in ("POST", "PUT", "PATCH"):
                schema = ep["request_body"]
                properties = _extract_properties(schema)
                required = _extract_required_fields(schema)
                sample = _build_sample_payload(properties, required)
                lines.append(f"        payload = {json.dumps(sample, indent=8)}")
                lines.append(f"        response = httpx.{method_lower}(")
                lines.append(f'            f"{{BASE_URL}}{path}",')
                lines.append(f"            json=payload,")
            else:
                lines.append(f"        response = httpx.{method_lower}(")
                lines.append(f'            f"{{BASE_URL}}{path}",')
            if _has_auth(ep):
                lines.append(f"            headers=auth_headers()")
            lines.append(f"        )")
            lines.append(f"        assert response.status_code == {happy_status}")
            lines.append("")

            # Error code tests from responses
            for status_code, desc in ep["responses"].items():
                if status_code in ("200", "201", "204", "default"):
                    continue
                lines.append(f"    def test_returns_{status_code}(self):")
                lines.append(f'        """Trigger {status_code}: {desc}"""')
                lines.append(f"        # TODO: set up conditions to trigger {status_code}")
                lines.append(f"        pass")
                lines.append("")

        filename = f"test_{group_name}.py"
        files[filename] = "\n".join(lines) + "\n"
    return files


# --- Vitest (TypeScript) Generator ---

def generate_vitest(endpoints: list, spec: dict) -> dict:
    """Generate vitest+supertest test files. Returns {filename: content}."""
    files = {}
    groups = {}
    for ep in endpoints:
        tag = ep["tags"][0] if ep["tags"] else ep["path"].strip("/").split("/")[0]
        tag = tag.lower().replace(" ", "-")
        groups.setdefault(tag, []).append(ep)

    for group_name, group_eps in groups.items():
        lines = [
            "import { describe, it, expect } from 'vitest'",
            "import request from 'supertest'",
            "",
            "const BASE_URL = process.env.API_URL || 'http://localhost:3000'",
            "const AUTH_TOKEN = process.env.AUTH_TOKEN || 'test-token'",
            "",
            "function authHeaders() {",
            "  return { Authorization: `Bearer ${AUTH_TOKEN}` }",
            "}",
            "",
        ]
        for ep in group_eps:
            summary = ep["summary"] or f'{ep["method"]} {ep["path"]}'
            method_lower = ep["method"].lower()
            path = ep["path"]

            lines.append(f"describe('{ep['method']} {path}', () => {{")

            if _has_auth(ep):
                lines.append(f"  it('returns 401 without auth header', async () => {{")
                lines.append(f"    const res = await request(BASE_URL).{method_lower}('{path}')")
                lines.append(f"    expect(res.status).toBe(401)")
                lines.append(f"  }})")
                lines.append("")

            if ep["request_body"] and ep["method"] in ("POST", "PUT", "PATCH"):
                schema = ep["request_body"]
                required = _extract_required_fields(schema)
                if required:
                    lines.append(f"  it('returns 422 with empty body', async () => {{")
                    lines.append(f"    const res = await request(BASE_URL)")
                    lines.append(f"      .{method_lower}('{path}')")
                    lines.append(f"      .set(authHeaders())")
                    lines.append(f"      .send({{}})")
                    lines.append(f"    expect(res.status).toBe(422)")
                    lines.append(f"  }})")
                    lines.append("")

            happy_status = "200"
            if ep["method"] == "POST":
                happy_status = "201" if "201" in ep["responses"] else "200"

            lines.append(f"  it('returns {happy_status} on success', async () => {{")
            if ep["request_body"] and ep["method"] in ("POST", "PUT", "PATCH"):
                schema = ep["request_body"]
                properties = _extract_properties(schema)
                required = _extract_required_fields(schema)
                sample = _build_sample_payload(properties, required)
                payload_str = json.dumps(sample, indent=4)
                lines.append(f"    const payload = {payload_str}")
                lines.append(f"    const res = await request(BASE_URL)")
                lines.append(f"      .{method_lower}('{path}')")
                lines.append(f"      .set(authHeaders())")
                lines.append(f"      .send(payload)")
            else:
                lines.append(f"    const res = await request(BASE_URL)")
                lines.append(f"      .{method_lower}('{path}')")
                lines.append(f"      .set(authHeaders())")
            lines.append(f"    expect(res.status).toBe({happy_status})")
            lines.append(f"  }})")

            lines.append(f"}})")
            lines.append("")

        filename = f"{group_name}.test.ts"
        files[filename] = "\n".join(lines) + "\n"
    return files


def _build_sample_payload(properties: dict, required: list, exclude: str = None) -> dict:
    """Build a sample JSON payload from schema properties."""
    payload = {}
    for name, info in properties.items():
        if name == exclude:
            continue
        if info.get("enum"):
            payload[name] = info["enum"][0]
        elif info["type"] == "string":
            payload[name] = f"test-{name}"
        elif info["type"] == "integer":
            payload[name] = 1
        elif info["type"] == "number":
            payload[name] = 1.0
        elif info["type"] == "boolean":
            payload[name] = True
        elif info["type"] == "array":
            payload[name] = []
        elif info["type"] == "object":
            payload[name] = {}
        else:
            payload[name] = f"test-{name}"
    return payload


def generate_report(endpoints: list, files: dict, framework: str) -> dict:
    """Build a summary report of generated tests."""
    total_tests = 0
    for content in files.values():
        if framework == "pytest":
            total_tests += content.count("    def test_")
        else:
            total_tests += content.count("  it(")

    auth_endpoints = sum(1 for ep in endpoints if _has_auth(ep))
    mutation_endpoints = sum(1 for ep in endpoints if ep["method"] in ("POST", "PUT", "PATCH"))

    return {
        "total_endpoints": len(endpoints),
        "auth_endpoints": auth_endpoints,
        "mutation_endpoints": mutation_endpoints,
        "files_generated": len(files),
        "total_test_cases": total_tests,
        "framework": framework,
        "filenames": sorted(files.keys()),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate API test skeletons from OpenAPI/Swagger spec files.",
        epilog="Example: python test_generator.py openapi.json --framework pytest --output tests/",
    )
    parser.add_argument("spec", help="Path to OpenAPI/Swagger JSON spec file")
    parser.add_argument(
        "--framework",
        choices=["pytest", "vitest"],
        default="pytest",
        help="Test framework to generate for (default: pytest)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory for generated test files (default: stdout preview)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output generation report as JSON",
    )
    args = parser.parse_args()

    spec = load_spec(args.spec)
    endpoints = extract_endpoints(spec)

    if not endpoints:
        print("Warning: no endpoints found in spec.", file=sys.stderr)
        sys.exit(1)

    if args.framework == "pytest":
        files = generate_pytest(endpoints, spec)
    else:
        files = generate_vitest(endpoints, spec)

    report = generate_report(endpoints, files, args.framework)

    # Write files or preview
    if args.output:
        out_dir = Path(args.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in files.items():
            filepath = out_dir / filename
            filepath.write_text(content, encoding="utf-8")

    if args.json_output:
        print(json.dumps(report, indent=2))
    else:
        print(f"=== API Test Generator Report ===")
        print(f"Spec:               {args.spec}")
        print(f"Framework:          {args.framework}")
        print(f"Endpoints found:    {report['total_endpoints']}")
        print(f"  Authenticated:    {report['auth_endpoints']}")
        print(f"  Mutation (POST+): {report['mutation_endpoints']}")
        print(f"Files generated:    {report['files_generated']}")
        print(f"Total test cases:   {report['total_test_cases']}")
        print()
        if args.output:
            print(f"Output directory: {args.output}")
            for fn in report["filenames"]:
                print(f"  {fn}")
        else:
            print("--- Preview (use --output to write files) ---")
            for filename, content in files.items():
                print(f"\n{'='*60}")
                print(f"FILE: {filename}")
                print(f"{'='*60}")
                print(content)


if __name__ == "__main__":
    main()
