#!/usr/bin/env python3
"""
Helm Chart Analyzer - Analyze Helm chart structure, metadata, and templates.

Checks for required files, validates Chart.yaml metadata, inspects templates
for common issues, and reviews dependency configurations.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Any


@dataclass
class Finding:
    """An analysis finding."""
    severity: str  # critical, warning, info
    category: str
    message: str
    recommendation: str


@dataclass
class ChartMetadata:
    """Parsed Chart.yaml metadata."""
    api_version: str
    name: str
    version: str
    app_version: str
    description: str
    type: str
    dependencies: List[Dict[str, str]]


class SimpleYamlParser:
    """Minimal YAML parser for Helm chart files (stdlib only)."""

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse simple YAML into a dict."""
        result: Dict[str, Any] = {}
        current_key = None
        current_list: Optional[List] = None
        current_list_item: Optional[Dict] = None

        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            # Top-level key: value
            if indent == 0 and ":" in stripped:
                if current_list_item and current_list is not None:
                    current_list.append(current_list_item)
                    current_list_item = None
                current_list = None

                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip()
                current_key = key
                if value:
                    result[key] = value.strip('"').strip("'")
                else:
                    result[key] = None

            # List item
            elif stripped.startswith("- "):
                if current_key and result.get(current_key) is None:
                    result[current_key] = []
                    current_list = result[current_key]

                if current_list_item and current_list is not None:
                    current_list.append(current_list_item)

                item_content = stripped[2:].strip()
                if ":" in item_content:
                    k, _, v = item_content.partition(":")
                    current_list_item = {k.strip(): v.strip().strip('"').strip("'")}
                elif current_list is not None:
                    current_list.append(item_content)
                    current_list_item = None

            # Continuation of list item
            elif indent >= 4 and current_list_item is not None and ":" in stripped:
                k, _, v = stripped.partition(":")
                current_list_item[k.strip()] = v.strip().strip('"').strip("'")

        if current_list_item and current_list is not None:
            current_list.append(current_list_item)

        return result


class ChartAnalyzer:
    """Analyzes Helm chart structure and quality."""

    REQUIRED_FILES = ["Chart.yaml", "values.yaml"]
    REQUIRED_DIRS = ["templates"]
    RECOMMENDED_FILES = ["templates/NOTES.txt", "templates/_helpers.tpl"]
    CHART_REQUIRED_FIELDS = ["apiVersion", "name", "version"]
    SEMVER_PATTERN = re.compile(r'^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$')

    def __init__(self, chart_path: Path, strict: bool = False):
        self.chart_path = chart_path
        self.strict = strict
        self.findings: List[Finding] = []
        self.metadata: Optional[ChartMetadata] = None

    def analyze(self) -> List[Finding]:
        """Run full chart analysis."""
        self._check_structure()
        self._check_chart_yaml()
        self._check_templates()
        self._check_dependencies()
        self._check_documentation()
        return self.findings

    def _check_structure(self):
        """Check required files and directories exist."""
        for req_file in self.REQUIRED_FILES:
            if not (self.chart_path / req_file).exists():
                self.findings.append(Finding(
                    severity="critical",
                    category="structure",
                    message=f"Required file missing: {req_file}",
                    recommendation=f"Create {req_file} in the chart root directory.",
                ))

        for req_dir in self.REQUIRED_DIRS:
            if not (self.chart_path / req_dir).is_dir():
                self.findings.append(Finding(
                    severity="critical",
                    category="structure",
                    message=f"Required directory missing: {req_dir}/",
                    recommendation=f"Create {req_dir}/ directory with template files.",
                ))

        for rec_file in self.RECOMMENDED_FILES:
            if not (self.chart_path / rec_file).exists():
                self.findings.append(Finding(
                    severity="info",
                    category="structure",
                    message=f"Recommended file missing: {rec_file}",
                    recommendation=f"Add {rec_file} for better chart usability.",
                ))

        # Check for Chart.lock if dependencies exist
        if (self.chart_path / "Chart.yaml").exists():
            chart_content = (self.chart_path / "Chart.yaml").read_text()
            if "dependencies:" in chart_content and not (self.chart_path / "Chart.lock").exists():
                self.findings.append(Finding(
                    severity="warning",
                    category="dependencies",
                    message="Chart has dependencies but no Chart.lock file.",
                    recommendation="Run 'helm dependency update' to generate Chart.lock.",
                ))

    def _check_chart_yaml(self):
        """Validate Chart.yaml metadata."""
        chart_file = self.chart_path / "Chart.yaml"
        if not chart_file.exists():
            return

        content = chart_file.read_text()
        parser = SimpleYamlParser()
        data = parser.parse(content)

        # Check required fields
        for field_name in self.CHART_REQUIRED_FIELDS:
            if field_name not in data or not data[field_name]:
                self.findings.append(Finding(
                    severity="critical",
                    category="metadata",
                    message=f"Required field missing in Chart.yaml: {field_name}",
                    recommendation=f"Add '{field_name}' to Chart.yaml.",
                ))

        # Check apiVersion
        api_version = data.get("apiVersion", "")
        if api_version and api_version != "v2":
            self.findings.append(Finding(
                severity="warning",
                category="metadata",
                message=f"Chart uses apiVersion '{api_version}'. Helm 3 expects 'v2'.",
                recommendation="Set apiVersion to 'v2' for Helm 3 compatibility.",
            ))

        # Check version format
        version = data.get("version", "")
        if version and not self.SEMVER_PATTERN.match(version):
            self.findings.append(Finding(
                severity="warning",
                category="metadata",
                message=f"Chart version '{version}' is not valid SemVer.",
                recommendation="Use semantic versioning format: MAJOR.MINOR.PATCH",
            ))

        # Check description
        if not data.get("description"):
            self.findings.append(Finding(
                severity="info",
                category="metadata",
                message="Chart.yaml missing 'description' field.",
                recommendation="Add a brief description of the chart's purpose.",
            ))

        # Check appVersion
        if not data.get("appVersion"):
            self.findings.append(Finding(
                severity="info",
                category="metadata",
                message="Chart.yaml missing 'appVersion' field.",
                recommendation="Add appVersion to track the application version deployed.",
            ))

        # Store metadata
        deps = data.get("dependencies", [])
        if not isinstance(deps, list):
            deps = []
        self.metadata = ChartMetadata(
            api_version=data.get("apiVersion", ""),
            name=data.get("name", ""),
            version=data.get("version", ""),
            app_version=data.get("appVersion", ""),
            description=data.get("description", ""),
            type=data.get("type", "application"),
            dependencies=[d for d in deps if isinstance(d, dict)],
        )

    def _check_templates(self):
        """Inspect template files for common issues."""
        templates_dir = self.chart_path / "templates"
        if not templates_dir.is_dir():
            return

        template_files = list(templates_dir.glob("*.yaml")) + list(templates_dir.glob("*.yml"))
        tpl_files = list(templates_dir.glob("*.tpl"))

        if not template_files and not tpl_files:
            self.findings.append(Finding(
                severity="warning",
                category="templates",
                message="No template files found in templates/ directory.",
                recommendation="Add Kubernetes manifest templates (deployment.yaml, service.yaml, etc.).",
            ))
            return

        for tpl in template_files:
            content = tpl.read_text()

            # Check for hardcoded namespace
            if re.search(r'namespace:\s*["\']?\w+["\']?\s*$', content, re.MULTILINE):
                if "{{ " not in content.split("namespace:")[0].split("\n")[-1]:
                    nearby = [l for l in content.split("\n") if "namespace:" in l]
                    for ns_line in nearby:
                        if "{{" not in ns_line:
                            self.findings.append(Finding(
                                severity="warning",
                                category="templates",
                                message=f"Hardcoded namespace in {tpl.name}.",
                                recommendation="Use {{ .Release.Namespace }} for namespace references.",
                            ))
                            break

            # Check for hardcoded image tags
            if re.search(r'image:\s*["\']?[\w/.-]+:\w+', content):
                img_lines = [l for l in content.split("\n") if "image:" in l]
                for img_line in img_lines:
                    if "{{" not in img_line:
                        self.findings.append(Finding(
                            severity="warning",
                            category="templates",
                            message=f"Hardcoded image reference in {tpl.name}.",
                            recommendation="Use templated image: {{ .Values.image.repository }}:{{ .Values.image.tag }}",
                        ))
                        break

    def _check_dependencies(self):
        """Check subchart dependency configurations."""
        if not self.metadata or not self.metadata.dependencies:
            return

        for dep in self.metadata.dependencies:
            name = dep.get("name", "unknown")
            version = dep.get("version", "")

            if not version:
                self.findings.append(Finding(
                    severity="warning",
                    category="dependencies",
                    message=f"Dependency '{name}' has no version constraint.",
                    recommendation=f"Pin dependency '{name}' to a version range.",
                ))
            elif version == "*":
                self.findings.append(Finding(
                    severity="warning",
                    category="dependencies",
                    message=f"Dependency '{name}' uses wildcard version '*'.",
                    recommendation=f"Pin to a specific version range like '~1.2.0' or '>=1.0.0 <2.0.0'.",
                ))

            if not dep.get("repository"):
                self.findings.append(Finding(
                    severity="warning",
                    category="dependencies",
                    message=f"Dependency '{name}' has no repository specified.",
                    recommendation="Add repository URL for the dependency.",
                ))

    def _check_documentation(self):
        """Check for chart documentation."""
        readme = self.chart_path / "README.md"
        if not readme.exists():
            self.findings.append(Finding(
                severity="info",
                category="documentation",
                message="No README.md found in chart directory.",
                recommendation="Add README.md documenting chart usage, values, and examples.",
            ))


def format_text(findings: List[Finding], chart_path: str, metadata: Optional[ChartMetadata]) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("HELM CHART ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"\nChart: {chart_path}")

    if metadata:
        lines.append(f"  Name: {metadata.name}")
        lines.append(f"  Version: {metadata.version}")
        lines.append(f"  App Version: {metadata.app_version}")
        lines.append(f"  Dependencies: {len(metadata.dependencies)}")

    critical = [f for f in findings if f.severity == "critical"]
    warnings = [f for f in findings if f.severity == "warning"]
    info = [f for f in findings if f.severity == "info"]

    lines.append(f"\nFindings: {len(critical)} critical, {len(warnings)} warnings, {len(info)} info")
    lines.append("-" * 60)

    for severity, group in [("CRITICAL", critical), ("WARNING", warnings), ("INFO", info)]:
        if not group:
            continue
        lines.append(f"\n[{severity}]")
        for f in group:
            lines.append(f"  [{f.category}] {f.message}")
            lines.append(f"    Fix: {f.recommendation}")
            lines.append("")

    if not findings:
        lines.append("\nNo issues found. Chart follows best practices.")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(findings: List[Finding], chart_path: str, metadata: Optional[ChartMetadata]) -> str:
    """Format as JSON."""
    return json.dumps({
        "chart_path": chart_path,
        "metadata": asdict(metadata) if metadata else None,
        "findings": [asdict(f) for f in findings],
        "summary": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f.severity == "critical"),
            "warnings": sum(1 for f in findings if f.severity == "warning"),
            "info": sum(1 for f in findings if f.severity == "info"),
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Helm chart structure, metadata, and templates."
    )
    parser.add_argument("--path", "-p", required=True, help="Path to Helm chart directory")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    chart_path = Path(args.path)
    if not chart_path.is_dir():
        print(f"Error: Not a directory: {args.path}", file=sys.stderr)
        sys.exit(2)

    analyzer = ChartAnalyzer(chart_path, strict=args.strict)
    findings = analyzer.analyze()

    if args.format == "json":
        print(format_json(findings, str(chart_path), analyzer.metadata))
    else:
        print(format_text(findings, str(chart_path), analyzer.metadata))

    has_critical = any(f.severity == "critical" for f in findings)
    has_warning = any(f.severity == "warning" for f in findings)
    if has_critical or (args.strict and has_warning):
        sys.exit(1)


if __name__ == "__main__":
    main()
