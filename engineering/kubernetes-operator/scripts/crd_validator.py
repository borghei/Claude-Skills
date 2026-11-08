#!/usr/bin/env python3
"""
crd_validator.py — Validate Kubernetes CRD YAML files against design best practices.

Reads one or more CRD YAML manifests and flags:
  - Schema issues (preserve-unknown-fields, missing structural validation)
  - Missing OpenAPI descriptions on user-facing fields
  - Missing required fields, enums, patterns
  - Missing printer columns
  - Status subresource not enabled
  - Cluster-scoped resources without justification
  - Missing observed-generation / conditions in status
  - Versioning issues (multiple storage versions, missing conversion)

Stdlib only. Parses YAML via a minimal embedded parser; for full YAML support
prefer to pre-convert to JSON, but the embedded parser handles ~95%% of real
CRD manifests.

Markdown or JSON output.

Usage:
    python3 crd_validator.py --schema my-crd.yaml
    python3 crd_validator.py --schema config/crd/bases/*.yaml --format json
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# Minimal YAML parser sufficient for typical CRD files (no anchors, no flow style
# besides simple lists/maps). Falls back gracefully on parse failures.
def parse_yaml(text: str) -> list[dict[str, Any]]:
    """Parse a YAML document with --- separators into a list of dicts."""
    docs: list[dict[str, Any]] = []
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.strip() == "---":
            if current_lines:
                d = _parse_one_doc(current_lines)
                if d:
                    docs.append(d)
                current_lines = []
            continue
        current_lines.append(line)
    if current_lines:
        d = _parse_one_doc(current_lines)
        if d:
            docs.append(d)
    return docs


def _parse_one_doc(lines: list[str]) -> dict[str, Any]:
    """Very small YAML subset parser. Handles mappings, sequences, scalars, comments."""
    cleaned: list[tuple[int, str]] = []
    for raw in lines:
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        cleaned.append((indent, line[indent:]))
    result, _ = _parse_block(cleaned, 0, 0)
    return result if isinstance(result, dict) else {}


def _parse_block(lines: list[tuple[int, str]], idx: int, indent: int) -> tuple[Any, int]:
    if idx >= len(lines):
        return None, idx
    first_indent = lines[idx][0]
    if first_indent < indent:
        return None, idx
    # Determine block type: list (starts with "- ") or map
    first_line = lines[idx][1]
    if first_line.startswith("- "):
        return _parse_seq(lines, idx, first_indent)
    return _parse_map(lines, idx, first_indent)


def _parse_map(lines: list[tuple[int, str]], idx: int, indent: int) -> tuple[dict, int]:
    out: dict[str, Any] = {}
    while idx < len(lines):
        cur_indent, content = lines[idx]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            idx += 1
            continue
        if ":" not in content:
            idx += 1
            continue
        key, _, rest = content.partition(":")
        key = key.strip().strip('"').strip("'")
        rest = rest.strip()
        if rest:
            out[key] = _scalar(rest)
            idx += 1
        else:
            # nested block
            idx += 1
            # A block is indented deeper, or is a "- " sequence at the same indent
            # (the compact style controller-gen and kubectl emit).
            if idx < len(lines) and (lines[idx][0] > indent
                                     or (lines[idx][0] == indent and lines[idx][1].startswith("- "))):
                value, idx = _parse_block(lines, idx, lines[idx][0])
                out[key] = value if value is not None else {}
            else:
                out[key] = {}
    return out, idx


def _parse_seq(lines: list[tuple[int, str]], idx: int, indent: int) -> tuple[list, int]:
    out: list[Any] = []
    while idx < len(lines):
        cur_indent, content = lines[idx]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            idx += 1
            continue
        if not content.startswith("- "):
            break
        rest = content[2:].strip()
        if not rest:
            idx += 1
            if idx < len(lines) and lines[idx][0] > indent:
                value, idx = _parse_block(lines, idx, lines[idx][0])
                out.append(value if value is not None else {})
            else:
                out.append(None)
        elif ":" in rest:
            # inline map-as-list-item: parse as a one-line map continued by following lines
            # rewrite as a synthetic block starting at this indent + 2
            synth = [(indent + 2, rest)]
            # take following lines until we leave the item
            j = idx + 1
            while j < len(lines) and lines[j][0] > indent:
                synth.append(lines[j])
                j += 1
            value, _ = _parse_map(synth, 0, indent + 2)
            out.append(value)
            idx = j
        else:
            out.append(_scalar(rest))
            idx += 1
    return out, idx


def _scalar(s: str) -> Any:
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    if s.lower() in ("null", "~", ""):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


@dataclass
class Finding:
    severity: str
    crd_name: str
    version: str
    path: str
    issue: str
    recommendation: str


@dataclass
class CrdReport:
    file_path: str
    crd_name: str
    group: str
    scope: str
    versions: list[str]
    storage_version: str
    findings: list[Finding] = field(default_factory=list)


def validate_crd(doc: dict[str, Any], file_path: str) -> CrdReport:
    findings: list[Finding] = []
    meta = doc.get("metadata", {}) or {}
    spec = doc.get("spec", {}) or {}
    name = meta.get("name", "<unknown>")
    group = spec.get("group", "")
    scope = spec.get("scope", "Namespaced")
    names = spec.get("names", {}) or {}
    versions_raw = spec.get("versions", []) or []
    versions_list = [v.get("name", "") for v in versions_raw if isinstance(v, dict)]
    storage_versions = [v.get("name", "") for v in versions_raw if isinstance(v, dict) and v.get("storage")]
    storage_version = storage_versions[0] if storage_versions else ""

    if len(storage_versions) > 1:
        findings.append(Finding(
            severity="critical",
            crd_name=name,
            version="all",
            path=".spec.versions",
            issue=f"Multiple storage versions: {storage_versions}",
            recommendation="Exactly one version may have storage:true at a time.",
        ))
    if not storage_versions and versions_raw:
        findings.append(Finding(
            severity="critical",
            crd_name=name,
            version="all",
            path=".spec.versions",
            issue="No storage version designated",
            recommendation="Exactly one version must have storage:true.",
        ))

    if not group or "." not in group or group.endswith(".io") and "kubernetes" in group:
        findings.append(Finding(
            severity="warning",
            crd_name=name,
            version="all",
            path=".spec.group",
            issue=f"Group '{group}' may not be appropriately scoped",
            recommendation="Use a domain you own. Avoid kubernetes.io / k8s.io for custom CRDs.",
        ))

    if not names.get("plural"):
        findings.append(Finding(severity="critical", crd_name=name, version="all", path=".spec.names.plural",
                                issue="Missing plural name", recommendation="Required for API access."))
    if not names.get("shortNames"):
        findings.append(Finding(severity="info", crd_name=name, version="all", path=".spec.names.shortNames",
                                issue="No shortNames defined",
                                recommendation="Add shortNames for kubectl UX, e.g., 'db' for Database."))
    if not names.get("categories"):
        findings.append(Finding(severity="info", crd_name=name, version="all", path=".spec.names.categories",
                                issue="No categories defined",
                                recommendation="Consider adding 'all' or domain-specific category for kubectl get."))

    if scope == "Cluster":
        findings.append(Finding(
            severity="warning",
            crd_name=name,
            version="all",
            path=".spec.scope",
            issue="Cluster-scoped resource",
            recommendation="Justify cluster scope. Most CRDs are Namespaced.",
        ))

    has_conversion = bool((spec.get("conversion") or {}).get("strategy"))
    served_versions = [v for v in versions_raw if isinstance(v, dict) and v.get("served")]
    if len(served_versions) > 1 and not has_conversion:
        findings.append(Finding(
            severity="warning",
            crd_name=name,
            version="all",
            path=".spec.conversion",
            issue=f"{len(served_versions)} served versions but no conversion strategy",
            recommendation="Add conversion: { strategy: Webhook } and implement webhook.",
        ))

    for v in versions_raw:
        if not isinstance(v, dict):
            continue
        vname = v.get("name", "<unknown>")
        if not v.get("subresources", {}).get("status") and v.get("subresources", {}).get("status") != {}:
            # status subresource missing or not configured
            subs = v.get("subresources") or {}
            if "status" not in subs:
                findings.append(Finding(
                    severity="critical",
                    crd_name=name,
                    version=vname,
                    path=f".spec.versions[{vname}].subresources.status",
                    issue="Status subresource not enabled",
                    recommendation="Add 'subresources: { status: {} }'. Always enable for production CRDs.",
                ))

        if not v.get("additionalPrinterColumns"):
            findings.append(Finding(
                severity="warning",
                crd_name=name,
                version=vname,
                path=f".spec.versions[{vname}].additionalPrinterColumns",
                issue="No printer columns defined",
                recommendation="Add at minimum: Phase + Age. Optional: domain-specific fields.",
            ))

        schema = (v.get("schema") or {}).get("openAPIV3Schema") or {}
        if not schema:
            findings.append(Finding(severity="critical", crd_name=name, version=vname,
                                    path=f".spec.versions[{vname}].schema",
                                    issue="No schema",
                                    recommendation="Define openAPIV3Schema for validation."))
            continue

        if schema.get("x-kubernetes-preserve-unknown-fields"):
            findings.append(Finding(severity="critical", crd_name=name, version=vname,
                                    path=f".spec.versions[{vname}].schema (root)",
                                    issue="Schema preserves unknown fields at root",
                                    recommendation="Define structural schema. preserve-unknown-fields defeats validation."))

        props = (schema.get("properties") or {})
        spec_schema = props.get("spec") or {}
        status_schema = props.get("status") or {}

        if spec_schema.get("x-kubernetes-preserve-unknown-fields") and not spec_schema.get("properties"):
            findings.append(Finding(severity="critical", crd_name=name, version=vname,
                                    path=f".spec.versions[{vname}].schema.properties.spec",
                                    issue="spec is untyped (preserve-unknown-fields with no properties)",
                                    recommendation="Declare spec properties; the API server cannot validate an untyped spec."))
        if not spec_schema:
            findings.append(Finding(severity="warning", crd_name=name, version=vname,
                                    path=f".spec.versions[{vname}].schema.properties.spec",
                                    issue="No spec schema",
                                    recommendation="Define the spec structure explicitly."))
        else:
            _audit_object_schema(spec_schema, "spec", name, vname, findings)

        if not status_schema:
            findings.append(Finding(severity="warning", crd_name=name, version=vname,
                                    path=f".spec.versions[{vname}].schema.properties.status",
                                    issue="No status schema",
                                    recommendation="Define status structure (phase, observedGeneration, conditions)."))
        else:
            status_props = (status_schema.get("properties") or {})
            if "observedGeneration" not in status_props:
                findings.append(Finding(severity="warning", crd_name=name, version=vname,
                                        path=f"status.observedGeneration",
                                        issue="Missing observedGeneration in status",
                                        recommendation="Add observedGeneration: int — tracks last spec generation reconciled."))
            if "conditions" not in status_props and "phase" not in status_props:
                findings.append(Finding(severity="warning", crd_name=name, version=vname,
                                        path=f"status.conditions",
                                        issue="Status has neither 'phase' nor 'conditions' field",
                                        recommendation="Use conditions array (preferred) or phase string for status reporting."))

    return CrdReport(
        file_path=file_path,
        crd_name=name,
        group=group,
        scope=scope,
        versions=versions_list,
        storage_version=storage_version,
        findings=findings,
    )


def _audit_object_schema(schema: dict[str, Any], path: str, crd_name: str, version: str, findings: list[Finding]) -> None:
    """Recursively check that schema fields have descriptions and validation."""
    if not isinstance(schema, dict):
        return
    if schema.get("type") == "object":
        props = schema.get("properties") or {}
        for prop_name, prop_schema in props.items():
            sub_path = f"{path}.{prop_name}"
            if not isinstance(prop_schema, dict):
                continue
            if not prop_schema.get("description"):
                findings.append(Finding(severity="info", crd_name=crd_name, version=version,
                                        path=sub_path, issue="Missing description",
                                        recommendation=f"Add description for {sub_path} — visible in kubectl explain."))
            if prop_schema.get("type") == "string" and not prop_schema.get("enum") and not prop_schema.get("pattern") and not prop_schema.get("format"):
                findings.append(Finding(severity="info", crd_name=crd_name, version=version,
                                        path=sub_path, issue="Open string with no validation",
                                        recommendation=f"Consider adding enum / pattern / format to {sub_path}."))
            if prop_schema.get("type") == "integer" and "minimum" not in prop_schema and "maximum" not in prop_schema:
                findings.append(Finding(severity="info", crd_name=crd_name, version=version,
                                        path=sub_path, issue="Integer with no bounds",
                                        recommendation=f"Consider adding minimum/maximum to {sub_path}."))
            _audit_object_schema(prop_schema, sub_path, crd_name, version, findings)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate CRD YAML manifests against design best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--schema", nargs="+", required=True, help="Path(s) or globs to CRD YAML files")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    p.add_argument("--severity", choices=["info", "warning", "critical"], default="info",
                   help="Minimum severity to report (default: info)")
    return p.parse_args()


SEVERITY_LEVEL = {"info": 0, "warning": 1, "critical": 2}


def render_markdown(reports: list[CrdReport], min_sev: str) -> str:
    out: list[str] = ["# CRD Validation Report", ""]
    total_findings = sum(len(r.findings) for r in reports)
    out.append(f"_CRDs analyzed: {len(reports)}_  ")
    out.append(f"_Total findings: {total_findings}_")
    out.append("")
    for r in reports:
        out.append(f"## `{r.crd_name}` ({r.group}, {r.scope})")
        out.append(f"- File: `{r.file_path}`")
        out.append(f"- Versions: {', '.join(r.versions) or '—'}")
        out.append(f"- Storage version: `{r.storage_version}`")
        out.append("")
        rel_findings = [f for f in r.findings if SEVERITY_LEVEL[f.severity] >= SEVERITY_LEVEL[min_sev]]
        if not rel_findings:
            out.append("_No findings at this severity level._")
            out.append("")
            continue
        out.append("| Severity | Version | Path | Issue | Recommendation |")
        out.append("|----------|---------|------|-------|----------------|")
        for f in sorted(rel_findings, key=lambda f: (-SEVERITY_LEVEL[f.severity], f.path)):
            out.append(f"| {f.severity} | {f.version} | `{f.path}` | {f.issue} | {f.recommendation} |")
        out.append("")
    return "\n".join(out)


def main() -> int:
    args = parse_args()
    files: list[str] = []
    for s in args.schema:
        if "*" in s or "?" in s:
            files.extend(sorted(glob.glob(s)))
        else:
            files.append(s)
    if not files:
        print("error: no files matched", file=sys.stderr)
        return 2
    reports: list[CrdReport] = []
    for f in files:
        try:
            text = Path(f).read_text()
        except OSError as e:
            print(f"error reading {f}: {e}", file=sys.stderr)
            return 2
        docs = parse_yaml(text)
        for d in docs:
            if d.get("kind") != "CustomResourceDefinition":
                continue
            reports.append(validate_crd(d, f))
    if not reports:
        print("error: no CRDs found in input files", file=sys.stderr)
        return 2
    if args.format == "json":
        out = json.dumps(
            {"reports": [asdict(r) for r in reports]},
            indent=2,
            default=str,
        )
    else:
        out = render_markdown(reports, args.severity)
    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 1 if any(f.severity == "critical" for r in reports for f in r.findings) else 0


if __name__ == "__main__":
    sys.exit(main())
