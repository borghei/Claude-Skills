#!/usr/bin/env python3
"""Validate API response samples against JSON Schema contracts.

Takes an OpenAPI/Swagger spec and a directory of response sample JSON files,
then validates each sample against its corresponding schema definition.
Reports schema violations, missing required fields, type mismatches, and
extra properties (if additionalProperties is false).

Usage:
    python contract_validator.py spec.json samples/
    python contract_validator.py spec.json samples/ --strict
    python contract_validator.py spec.json samples/ --json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------- JSON Schema Validator (standard-library only) ----------

class SchemaValidationError:
    """A single validation error."""
    def __init__(self, path: str, message: str, schema_path: str = ""):
        self.path = path
        self.message = message
        self.schema_path = schema_path

    def to_dict(self) -> dict:
        return {"path": self.path, "message": self.message, "schema_path": self.schema_path}

    def __repr__(self):
        return f"{self.path}: {self.message}"


def validate_value(value, schema: dict, root_schema: dict, path: str = "$",
                   strict: bool = False) -> list:
    """Validate a value against a JSON Schema. Returns list of SchemaValidationError."""
    errors = []

    if not schema:
        return errors

    # Resolve $ref
    if "$ref" in schema:
        schema = _resolve_ref(root_schema, schema["$ref"])
        if schema is None:
            errors.append(SchemaValidationError(path, "unresolvable $ref"))
            return errors

    # Handle allOf
    if "allOf" in schema:
        for sub in schema["allOf"]:
            errors.extend(validate_value(value, sub, root_schema, path, strict))
        return errors

    # Handle oneOf
    if "oneOf" in schema:
        matches = 0
        for sub in schema["oneOf"]:
            sub_errors = validate_value(value, sub, root_schema, path, strict)
            if not sub_errors:
                matches += 1
        if matches == 0:
            errors.append(SchemaValidationError(path, "does not match any oneOf schema"))
        elif matches > 1:
            errors.append(SchemaValidationError(path, f"matches {matches} oneOf schemas, expected exactly 1"))
        return errors

    # Handle anyOf
    if "anyOf" in schema:
        for sub in schema["anyOf"]:
            sub_errors = validate_value(value, sub, root_schema, path, strict)
            if not sub_errors:
                return []
        errors.append(SchemaValidationError(path, "does not match any anyOf schema"))
        return errors

    # Nullable
    nullable = schema.get("nullable", False)
    if value is None:
        if not nullable and "type" in schema:
            errors.append(SchemaValidationError(path, f"expected {schema['type']}, got null"))
        return errors

    # Type checking
    expected_type = schema.get("type")
    if expected_type:
        type_ok = _check_type(value, expected_type)
        if not type_ok:
            actual = type(value).__name__
            errors.append(SchemaValidationError(path, f"expected type '{expected_type}', got '{actual}'"))
            return errors  # No point checking further if type is wrong

    # Enum
    if "enum" in schema:
        if value not in schema["enum"]:
            errors.append(SchemaValidationError(
                path, f"value '{value}' not in enum {schema['enum']}"
            ))

    # String constraints
    if expected_type == "string" and isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(SchemaValidationError(
                path, f"string length {len(value)} below minLength {schema['minLength']}"
            ))
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(SchemaValidationError(
                path, f"string length {len(value)} above maxLength {schema['maxLength']}"
            ))
        if "pattern" in schema:
            if not re.search(schema["pattern"], value):
                errors.append(SchemaValidationError(
                    path, f"string does not match pattern '{schema['pattern']}'"
                ))
        if "format" in schema:
            fmt_error = _check_format(value, schema["format"])
            if fmt_error:
                errors.append(SchemaValidationError(path, fmt_error))

    # Number constraints
    if expected_type in ("integer", "number") and isinstance(value, (int, float)):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(SchemaValidationError(
                path, f"value {value} below minimum {schema['minimum']}"
            ))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(SchemaValidationError(
                path, f"value {value} above maximum {schema['maximum']}"
            ))
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            errors.append(SchemaValidationError(
                path, f"value {value} not above exclusiveMinimum {schema['exclusiveMinimum']}"
            ))
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            errors.append(SchemaValidationError(
                path, f"value {value} not below exclusiveMaximum {schema['exclusiveMaximum']}"
            ))

    # Object validation
    if expected_type == "object" and isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        # Check required fields
        for req_field in required:
            if req_field not in value:
                errors.append(SchemaValidationError(
                    f"{path}.{req_field}", f"required field '{req_field}' is missing"
                ))

        # Validate known properties
        for prop_name, prop_schema in properties.items():
            if prop_name in value:
                errors.extend(validate_value(
                    value[prop_name], prop_schema, root_schema,
                    f"{path}.{prop_name}", strict
                ))

        # Check additional properties
        additional = schema.get("additionalProperties", True)
        if strict or additional is False:
            known_props = set(properties.keys())
            extra = set(value.keys()) - known_props
            if extra and additional is False:
                for prop in sorted(extra):
                    errors.append(SchemaValidationError(
                        f"{path}.{prop}", f"additional property '{prop}' not allowed"
                    ))
            elif extra and strict and additional is not True:
                for prop in sorted(extra):
                    errors.append(SchemaValidationError(
                        f"{path}.{prop}", f"unexpected property '{prop}' (strict mode)"
                    ))

        # Validate patternProperties
        pattern_props = schema.get("patternProperties", {})
        for pattern, p_schema in pattern_props.items():
            regex = re.compile(pattern)
            for key in value:
                if regex.search(key):
                    errors.extend(validate_value(
                        value[key], p_schema, root_schema,
                        f"{path}.{key}", strict
                    ))

    # Array validation
    if expected_type == "array" and isinstance(value, list):
        items_schema = schema.get("items", {})
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(SchemaValidationError(
                path, f"array length {len(value)} below minItems {schema['minItems']}"
            ))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(SchemaValidationError(
                path, f"array length {len(value)} above maxItems {schema['maxItems']}"
            ))
        if "uniqueItems" in schema and schema["uniqueItems"]:
            seen = []
            for item in value:
                serialized = json.dumps(item, sort_keys=True)
                if serialized in seen:
                    errors.append(SchemaValidationError(path, "array contains duplicate items"))
                    break
                seen.append(serialized)

        for i, item in enumerate(value):
            errors.extend(validate_value(
                item, items_schema, root_schema,
                f"{path}[{i}]", strict
            ))

    return errors


def _check_type(value, expected: str) -> bool:
    """Check if value matches the expected JSON Schema type."""
    if expected == "string":
        return isinstance(value, str)
    elif expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    elif expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    elif expected == "boolean":
        return isinstance(value, bool)
    elif expected == "array":
        return isinstance(value, list)
    elif expected == "object":
        return isinstance(value, dict)
    elif expected == "null":
        return value is None
    return True


def _check_format(value: str, fmt: str) -> str:
    """Basic format validation for common formats. Returns error message or empty string."""
    if fmt == "email":
        if "@" not in value or "." not in value.split("@")[-1]:
            return f"'{value}' is not a valid email format"
    elif fmt == "uri" or fmt == "url":
        if not re.match(r'^https?://', value):
            return f"'{value}' is not a valid URI format"
    elif fmt == "uuid":
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value, re.I):
            return f"'{value}' is not a valid UUID format"
    elif fmt in ("date-time", "datetime"):
        if not re.match(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', value):
            return f"'{value}' is not a valid date-time format"
    elif fmt == "date":
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return f"'{value}' is not a valid date format"
    return ""


def _resolve_ref(root_schema: dict, ref: str) -> dict:
    """Resolve a $ref path within the root schema."""
    if not ref.startswith("#/"):
        return None
    parts = ref[2:].split("/")
    current = root_schema
    for part in parts:
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


# ---------- Spec + Sample Loading ----------

def load_spec(spec_path: str) -> dict:
    """Load and validate an OpenAPI/Swagger spec file."""
    path = Path(spec_path)
    if not path.exists():
        print(f"Error: spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in spec file: {e}", file=sys.stderr)
        sys.exit(1)
    if "openapi" not in spec and "swagger" not in spec:
        print("Error: not an OpenAPI/Swagger spec", file=sys.stderr)
        sys.exit(1)
    return spec


def extract_response_schemas(spec: dict) -> dict:
    """Extract response schemas keyed by 'METHOD /path STATUS'.

    Returns dict like:
        {"GET /users 200": <schema>, "POST /users 201": <schema>}
    """
    schemas = {}
    for path, path_item in spec.get("paths", {}).items():
        for method in ("get", "post", "put", "patch", "delete"):
            if method not in path_item:
                continue
            operation = path_item[method]
            for status, resp in operation.get("responses", {}).items():
                content = resp.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema")
                if schema:
                    key = f"{method.upper()} {path} {status}"
                    schemas[key] = schema
    return schemas


def load_samples(samples_dir: str) -> list:
    """Load JSON sample files from the samples directory.

    Expected naming convention:
        METHOD_path_STATUS.json  (e.g., GET_users_200.json)
        or any .json file with a _meta key inside specifying method/path/status
    """
    samples = []
    samples_path = Path(samples_dir)
    if not samples_path.exists():
        print(f"Error: samples directory not found: {samples_dir}", file=sys.stderr)
        sys.exit(1)

    for json_file in sorted(samples_path.rglob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            samples.append({
                "file": str(json_file),
                "error": f"invalid JSON: {e}",
                "data": None,
                "meta": None,
            })
            continue

        # Try to extract meta from file content
        meta = None
        body = data
        if isinstance(data, dict) and "_meta" in data:
            meta = data.pop("_meta")
            body = data

        # Try to infer from filename: GET_api_v1_users_200.json
        if meta is None:
            meta = _infer_meta_from_filename(json_file.stem)

        samples.append({
            "file": str(json_file),
            "data": body,
            "meta": meta,
            "error": None,
        })

    return samples


def _infer_meta_from_filename(stem: str) -> dict:
    """Try to parse METHOD_path_STATUS from filename stem."""
    # Pattern: GET_api_v1_users_200
    match = re.match(r'^(GET|POST|PUT|PATCH|DELETE)_(.+)_(\d{3})$', stem, re.IGNORECASE)
    if match:
        method = match.group(1).upper()
        path_raw = match.group(2)
        status = match.group(3)
        # Convert underscores back to slashes
        path = "/" + path_raw.replace("_", "/")
        return {"method": method, "path": path, "status": status}

    # Fallback: try just METHOD_path
    match = re.match(r'^(GET|POST|PUT|PATCH|DELETE)_(.+)$', stem, re.IGNORECASE)
    if match:
        method = match.group(1).upper()
        path_raw = match.group(2)
        path = "/" + path_raw.replace("_", "/")
        return {"method": method, "path": path, "status": "200"}

    return None


def validate_samples(spec: dict, samples: list, strict: bool = False) -> list:
    """Validate each sample against its matching response schema."""
    response_schemas = extract_response_schemas(spec)
    results = []

    for sample in samples:
        result = {
            "file": sample["file"],
            "status": "skip",
            "errors": [],
            "meta": sample["meta"],
        }

        if sample["error"]:
            result["status"] = "error"
            result["errors"] = [{"path": "$", "message": sample["error"]}]
            results.append(result)
            continue

        if sample["meta"] is None:
            result["status"] = "skip"
            result["errors"] = [{"path": "$", "message": "could not determine endpoint from filename or _meta"}]
            results.append(result)
            continue

        meta = sample["meta"]
        schema_key = f"{meta['method']} {meta['path']} {meta['status']}"

        # Try exact match first, then try path parameter variants
        schema = response_schemas.get(schema_key)
        if schema is None:
            # Try matching with path params
            for key, s in response_schemas.items():
                key_parts = key.split(" ")
                if len(key_parts) == 3:
                    k_method, k_path, k_status = key_parts
                    if k_method == meta["method"] and k_status == meta["status"]:
                        if _paths_match(k_path, meta["path"]):
                            schema = s
                            break

        if schema is None:
            result["status"] = "skip"
            result["errors"] = [{"path": "$", "message": f"no schema found for {schema_key}"}]
            results.append(result)
            continue

        errors = validate_value(sample["data"], schema, spec, "$", strict)
        result["status"] = "pass" if not errors else "fail"
        result["errors"] = [e.to_dict() for e in errors]
        results.append(result)

    return results


def _paths_match(spec_path: str, sample_path: str) -> bool:
    """Check if a spec path (with {params}) matches a concrete sample path."""
    spec_parts = spec_path.strip("/").split("/")
    sample_parts = sample_path.strip("/").split("/")
    if len(spec_parts) != len(sample_parts):
        return False
    for sp, sa in zip(spec_parts, sample_parts):
        if sp.startswith("{") and sp.endswith("}"):
            continue
        if sp != sa:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate API response samples against OpenAPI schema contracts.",
        epilog="Example: python contract_validator.py openapi.json samples/ --strict",
    )
    parser.add_argument("spec", help="Path to OpenAPI/Swagger JSON spec file")
    parser.add_argument("samples_dir", help="Directory containing JSON response samples")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode: reject unexpected properties even if additionalProperties is not false",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    spec = load_spec(args.spec)
    samples = load_samples(args.samples_dir)

    if not samples:
        print("Warning: no JSON sample files found.", file=sys.stderr)
        sys.exit(1)

    results = validate_samples(spec, samples, strict=args.strict)

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    errored = sum(1 for r in results if r["status"] == "error")
    skipped = sum(1 for r in results if r["status"] == "skip")

    if args.json_output:
        output = {
            "summary": {
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "errored": errored,
                "skipped": skipped,
            },
            "strict_mode": args.strict,
            "results": results,
        }
        print(json.dumps(output, indent=2))
    else:
        print("=== Contract Validation Report ===")
        print(f"Strict mode: {'ON' if args.strict else 'OFF'}")
        print()
        print(f"Total samples: {len(results)}")
        print(f"  Passed:  {passed}")
        print(f"  Failed:  {failed}")
        print(f"  Errors:  {errored}")
        print(f"  Skipped: {skipped}")
        print()

        # Show failures and errors
        for r in results:
            if r["status"] == "pass":
                symbol = "[PASS]"
            elif r["status"] == "fail":
                symbol = "[FAIL]"
            elif r["status"] == "error":
                symbol = "[ERR ]"
            else:
                symbol = "[SKIP]"

            filename = Path(r["file"]).name
            meta_str = ""
            if r["meta"]:
                meta_str = f" ({r['meta']['method']} {r['meta']['path']} {r['meta']['status']})"

            print(f"  {symbol} {filename}{meta_str}")

            if r["status"] in ("fail", "error"):
                for err in r["errors"]:
                    print(f"         {err['path']}: {err['message']}")

        print()

    if failed > 0 or errored > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
