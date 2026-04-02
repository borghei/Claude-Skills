#!/usr/bin/env python3
"""
Helm Values Validator - Validate values.yaml against chart requirements.

Checks for missing resource limits, security contexts, image tag best practices,
and other Kubernetes configuration requirements.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Finding:
    """A validation finding."""
    severity: str
    category: str
    path: str  # YAML path like "resources.limits.memory"
    message: str
    recommendation: str


class ValuesParser:
    """Parse values.yaml with stdlib only."""

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse YAML-like content into nested dict."""
        result: Dict[str, Any] = {}
        stack: List[tuple] = []  # (indent, dict_ref)
        current = result

        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            # Pop stack to find parent at this indent level
            while stack and stack[-1][0] >= indent:
                stack.pop()
            if stack:
                current = stack[-1][1]
            else:
                current = result

            # Handle list items
            if stripped.startswith("- "):
                continue  # Skip list items for this validation

            if ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip()

                if value:
                    # Strip quotes
                    value = value.strip('"').strip("'")
                    # Try to parse booleans and numbers
                    if value.lower() == "true":
                        current[key] = True
                    elif value.lower() == "false":
                        current[key] = False
                    elif value.lower() in ("null", "~"):
                        current[key] = None
                    else:
                        try:
                            current[key] = int(value)
                        except ValueError:
                            try:
                                current[key] = float(value)
                            except ValueError:
                                current[key] = value
                else:
                    # Nested dict
                    current[key] = {}
                    stack.append((indent, current))
                    current = current[key]
                    stack.append((indent + 2, current))

        return result

    def get_nested(self, data: Dict, path: str, default=None):
        """Get a nested value by dot-separated path."""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current


class ValuesValidator:
    """Validates Helm chart values files."""

    def __init__(self, values: Dict[str, Any], values_file: str):
        self.values = values
        self.values_file = values_file
        self.findings: List[Finding] = []
        self.parser = ValuesParser()

    def validate(self) -> List[Finding]:
        """Run all validation checks."""
        self._check_resources()
        self._check_security_context()
        self._check_image()
        self._check_replicas()
        self._check_service()
        self._check_ingress()
        self._check_probes()
        self._check_autoscaling()
        return self.findings

    def _get(self, path: str, default=None):
        """Helper to get nested values."""
        return self.parser.get_nested(self.values, path, default)

    def _check_resources(self):
        """Check for resource limits and requests."""
        resources = self._get("resources", {})

        if not resources or not isinstance(resources, dict):
            self.findings.append(Finding(
                severity="warning",
                category="resources",
                path="resources",
                message="No resource limits or requests defined.",
                recommendation="Add resources.limits and resources.requests for CPU and memory.",
            ))
            return

        limits = resources.get("limits", {})
        requests = resources.get("requests", {})

        if not limits or not isinstance(limits, dict):
            self.findings.append(Finding(
                severity="warning",
                category="resources",
                path="resources.limits",
                message="No resource limits defined.",
                recommendation="Add resources.limits.cpu and resources.limits.memory.",
            ))
        else:
            if "cpu" not in limits:
                self.findings.append(Finding(
                    severity="warning",
                    category="resources",
                    path="resources.limits.cpu",
                    message="CPU limit not set.",
                    recommendation="Set resources.limits.cpu (e.g., '500m').",
                ))
            if "memory" not in limits:
                self.findings.append(Finding(
                    severity="warning",
                    category="resources",
                    path="resources.limits.memory",
                    message="Memory limit not set.",
                    recommendation="Set resources.limits.memory (e.g., '256Mi').",
                ))

        if not requests or not isinstance(requests, dict):
            self.findings.append(Finding(
                severity="info",
                category="resources",
                path="resources.requests",
                message="No resource requests defined.",
                recommendation="Add resources.requests for proper scheduling.",
            ))

    def _check_security_context(self):
        """Check security context settings."""
        sec_ctx = self._get("securityContext", {})
        pod_sec = self._get("podSecurityContext", {})

        if not sec_ctx and not pod_sec:
            self.findings.append(Finding(
                severity="warning",
                category="security",
                path="securityContext",
                message="No security context defined.",
                recommendation="Add securityContext with runAsNonRoot, readOnlyRootFilesystem, allowPrivilegeEscalation.",
            ))
            return

        if isinstance(sec_ctx, dict):
            if sec_ctx.get("runAsNonRoot") is not True:
                self.findings.append(Finding(
                    severity="warning",
                    category="security",
                    path="securityContext.runAsNonRoot",
                    message="runAsNonRoot is not set to true.",
                    recommendation="Set securityContext.runAsNonRoot: true.",
                ))

            if sec_ctx.get("readOnlyRootFilesystem") is not True:
                self.findings.append(Finding(
                    severity="info",
                    category="security",
                    path="securityContext.readOnlyRootFilesystem",
                    message="readOnlyRootFilesystem is not enabled.",
                    recommendation="Set securityContext.readOnlyRootFilesystem: true where possible.",
                ))

            if sec_ctx.get("allowPrivilegeEscalation") is not False:
                self.findings.append(Finding(
                    severity="warning",
                    category="security",
                    path="securityContext.allowPrivilegeEscalation",
                    message="allowPrivilegeEscalation is not explicitly set to false.",
                    recommendation="Set securityContext.allowPrivilegeEscalation: false.",
                ))

    def _check_image(self):
        """Check image configuration."""
        image = self._get("image", {})
        if not image or not isinstance(image, dict):
            return

        tag = image.get("tag", "")
        if not tag:
            self.findings.append(Finding(
                severity="warning",
                category="image",
                path="image.tag",
                message="Image tag is empty or not set.",
                recommendation="Set image.tag to a specific version (not 'latest').",
            ))
        elif str(tag).lower() == "latest":
            self.findings.append(Finding(
                severity="warning",
                category="image",
                path="image.tag",
                message="Image tag is 'latest', which is non-deterministic.",
                recommendation="Pin image.tag to a specific version for reproducible deployments.",
            ))

        pull_policy = image.get("pullPolicy", "")
        if pull_policy == "Always" and tag and str(tag).lower() != "latest":
            self.findings.append(Finding(
                severity="info",
                category="image",
                path="image.pullPolicy",
                message="pullPolicy is 'Always' with a pinned tag.",
                recommendation="Consider 'IfNotPresent' for pinned tags to reduce pull overhead.",
            ))

    def _check_replicas(self):
        """Check replica count."""
        replicas = self._get("replicaCount")
        autoscaling = self._get("autoscaling", {})

        if isinstance(autoscaling, dict) and autoscaling.get("enabled") is True:
            return  # Autoscaling handles replicas

        if replicas is not None and isinstance(replicas, (int, float)):
            if replicas < 2:
                self.findings.append(Finding(
                    severity="info",
                    category="availability",
                    path="replicaCount",
                    message=f"replicaCount is {replicas}. Single replica has no redundancy.",
                    recommendation="Set replicaCount >= 2 for production environments.",
                ))

    def _check_service(self):
        """Check service configuration."""
        service = self._get("service", {})
        if not service or not isinstance(service, dict):
            return

        svc_type = service.get("type", "ClusterIP")
        if svc_type == "NodePort":
            self.findings.append(Finding(
                severity="info",
                category="networking",
                path="service.type",
                message="Service type is NodePort.",
                recommendation="Consider ClusterIP with Ingress for production. NodePort exposes ports on all nodes.",
            ))
        elif svc_type == "LoadBalancer":
            self.findings.append(Finding(
                severity="info",
                category="networking",
                path="service.type",
                message="Service type is LoadBalancer (creates cloud LB per service).",
                recommendation="Consider using Ingress to consolidate multiple services behind one LB.",
            ))

    def _check_ingress(self):
        """Check ingress configuration."""
        ingress = self._get("ingress", {})
        if not ingress or not isinstance(ingress, dict):
            return

        if ingress.get("enabled") is not True:
            return

        if not ingress.get("tls"):
            self.findings.append(Finding(
                severity="warning",
                category="networking",
                path="ingress.tls",
                message="Ingress is enabled but TLS is not configured.",
                recommendation="Configure ingress.tls for encrypted traffic.",
            ))

        if not ingress.get("className") and not ingress.get("ingressClassName"):
            self.findings.append(Finding(
                severity="info",
                category="networking",
                path="ingress.className",
                message="No ingress class specified.",
                recommendation="Set ingress.className to specify the ingress controller.",
            ))

    def _check_probes(self):
        """Check liveness and readiness probes."""
        liveness = self._get("livenessProbe", {})
        readiness = self._get("readinessProbe", {})

        if not liveness:
            self.findings.append(Finding(
                severity="info",
                category="reliability",
                path="livenessProbe",
                message="No liveness probe configured.",
                recommendation="Add livenessProbe to enable automatic restart on failure.",
            ))

        if not readiness:
            self.findings.append(Finding(
                severity="info",
                category="reliability",
                path="readinessProbe",
                message="No readiness probe configured.",
                recommendation="Add readinessProbe to prevent traffic to unready pods.",
            ))

    def _check_autoscaling(self):
        """Check autoscaling configuration."""
        autoscaling = self._get("autoscaling", {})
        if not isinstance(autoscaling, dict) or autoscaling.get("enabled") is not True:
            return

        if not autoscaling.get("minReplicas"):
            self.findings.append(Finding(
                severity="info",
                category="scaling",
                path="autoscaling.minReplicas",
                message="Autoscaling minReplicas not set.",
                recommendation="Set minReplicas >= 2 for production availability.",
            ))


def format_text(findings: List[Finding], values_file: str) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("HELM VALUES VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"\nValues file: {values_file}")

    critical = [f for f in findings if f.severity == "critical"]
    warnings = [f for f in findings if f.severity == "warning"]
    info = [f for f in findings if f.severity == "info"]

    lines.append(f"Findings: {len(critical)} critical, {len(warnings)} warnings, {len(info)} info")
    lines.append("-" * 60)

    for severity, group in [("CRITICAL", critical), ("WARNING", warnings), ("INFO", info)]:
        if not group:
            continue
        lines.append(f"\n[{severity}]")
        for f in group:
            lines.append(f"  [{f.category}] {f.path}: {f.message}")
            lines.append(f"    Fix: {f.recommendation}")
            lines.append("")

    if not findings:
        lines.append("\nNo issues found. Values follow best practices.")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(findings: List[Finding], values_file: str) -> str:
    """Format as JSON."""
    return json.dumps({
        "values_file": values_file,
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
        description="Validate Helm values files against best practices."
    )
    parser.add_argument("--chart", "-c", help="Path to Helm chart directory (for context)")
    parser.add_argument("--values", "-v", nargs="+", required=True, help="Path(s) to values file(s)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    exit_code = 0
    all_results = []

    for values_file in args.values:
        path = Path(values_file)
        if not path.exists():
            # Try relative to chart directory
            if args.chart:
                path = Path(args.chart) / values_file
            if not path.exists():
                print(f"Error: Values file not found: {values_file}", file=sys.stderr)
                exit_code = 2
                continue

        content = path.read_text()
        vp = ValuesParser()
        values = vp.parse(content)

        validator = ValuesValidator(values, str(path))
        findings = validator.validate()

        if args.format == "json":
            all_results.append({
                "file": str(path),
                "findings": [asdict(f) for f in findings],
            })
        else:
            print(format_text(findings, str(path)))

        if any(f.severity == "critical" for f in findings):
            exit_code = 1

    if args.format == "json":
        print(json.dumps({"results": all_results}, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
