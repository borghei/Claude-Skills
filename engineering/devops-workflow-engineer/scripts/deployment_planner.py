#!/usr/bin/env python3
"""
Deployment Planner

Generates a deployment plan document based on project type, target environments,
and deployment strategy. Includes environment matrix, rollback strategy, health
checks, and monitoring configuration.

Usage:
    python deployment_planner.py --type webapp --environments dev,staging,prod
    python deployment_planner.py --type microservice --environments dev,staging,prod --strategy canary
    python deployment_planner.py --type library --environments staging,prod
    python deployment_planner.py --type webapp --environments dev,staging,prod --format json
"""

import argparse
import json
import sys
import textwrap
from datetime import datetime


# ---------------------------------------------------------------------------
# Project type configurations
# ---------------------------------------------------------------------------

PROJECT_TYPES = {
    "webapp": {
        "label": "Web Application",
        "description": "Full-stack web application with frontend and backend components.",
        "default_strategy": "blue-green",
        "recommended_strategies": ["blue-green", "canary", "rolling"],
        "artifacts": ["Docker image", "Static assets (CDN)", "Database migrations"],
        "health_checks": [
            {"endpoint": "/health", "method": "GET", "expected_status": 200, "timeout_seconds": 5},
            {"endpoint": "/api/health", "method": "GET", "expected_status": 200, "timeout_seconds": 10},
            {"endpoint": "/", "method": "GET", "expected_status": 200, "timeout_seconds": 5},
        ],
        "monitoring_metrics": [
            "HTTP error rate (5xx)",
            "P50/P95/P99 response latency",
            "Request throughput (req/s)",
            "CPU and memory utilization",
            "Active database connections",
            "Cache hit rate",
        ],
        "rollback_steps": [
            "Redirect traffic to previous deployment",
            "Verify previous version health checks pass",
            "Roll back database migrations if needed (backward-compatible only)",
            "Invalidate CDN cache for reverted static assets",
            "Notify on-call team via PagerDuty/Slack",
        ],
        "pre_deploy_checks": [
            "All CI checks pass (lint, test, build, security scan)",
            "Database migration is backward-compatible",
            "Feature flags configured for new features",
            "Rollback procedure tested in staging",
            "Monitoring dashboards reviewed",
        ],
        "post_deploy_checks": [
            "Health endpoints return 200",
            "Error rate below threshold (< 0.1%)",
            "Latency within SLA bounds",
            "Key user journeys verified (smoke tests)",
            "No increase in error log volume",
        ],
    },
    "microservice": {
        "label": "Microservice",
        "description": "Individual microservice deployed as a container, communicating via API or message queue.",
        "default_strategy": "canary",
        "recommended_strategies": ["canary", "rolling", "blue-green"],
        "artifacts": ["Docker image", "API schema (OpenAPI)", "Service mesh config"],
        "health_checks": [
            {"endpoint": "/health", "method": "GET", "expected_status": 200, "timeout_seconds": 5},
            {"endpoint": "/ready", "method": "GET", "expected_status": 200, "timeout_seconds": 5},
        ],
        "monitoring_metrics": [
            "gRPC/HTTP error rate",
            "Request latency by endpoint",
            "Message queue depth/lag",
            "Circuit breaker state",
            "Pod restart count",
            "Memory and CPU per pod",
        ],
        "rollback_steps": [
            "Scale down new version pods",
            "Scale up previous version pods",
            "Verify service mesh routing restored",
            "Check upstream/downstream service health",
            "Review distributed traces for cascading failures",
        ],
        "pre_deploy_checks": [
            "Contract tests pass with upstream and downstream services",
            "API schema backward-compatible (no breaking changes)",
            "Resource limits configured (CPU, memory)",
            "Horizontal pod autoscaler tested",
            "Circuit breaker thresholds configured",
        ],
        "post_deploy_checks": [
            "Readiness probe passes",
            "Liveness probe passes",
            "No increase in upstream error rates",
            "Message queue consumers healthy",
            "Distributed traces show normal latency",
        ],
    },
    "library": {
        "label": "Library / Package",
        "description": "Shared library or package published to a registry (npm, PyPI, crates.io, etc.).",
        "default_strategy": "rolling",
        "recommended_strategies": ["rolling"],
        "artifacts": ["Package archive", "Documentation site", "Changelog"],
        "health_checks": [
            {"endpoint": "Registry package page", "method": "GET", "expected_status": 200, "timeout_seconds": 10},
        ],
        "monitoring_metrics": [
            "Download count (post-release)",
            "Issue/bug report rate",
            "Dependency compatibility (CI matrix)",
            "Documentation site uptime",
        ],
        "rollback_steps": [
            "Yank/unpublish the broken version from registry",
            "Publish a patch version with the fix",
            "Notify consumers via changelog and GitHub advisory",
            "Update dependent projects pinned to the broken version",
        ],
        "pre_deploy_checks": [
            "All tests pass across supported platform matrix",
            "Changelog updated with release notes",
            "Version bumped according to semver",
            "No breaking changes without major version bump",
            "Documentation updated for new APIs",
        ],
        "post_deploy_checks": [
            "Package installable from registry",
            "Basic usage example works with new version",
            "Documentation site reflects new version",
            "No compatibility issues reported in first 24 hours",
        ],
    },
    "mobile": {
        "label": "Mobile Application",
        "description": "iOS/Android mobile application distributed via app stores.",
        "default_strategy": "canary",
        "recommended_strategies": ["canary", "rolling"],
        "artifacts": ["iOS .ipa / Android .aab", "App store metadata", "Release notes"],
        "health_checks": [
            {"endpoint": "App store listing", "method": "GET", "expected_status": 200, "timeout_seconds": 30},
            {"endpoint": "/api/mobile/health", "method": "GET", "expected_status": 200, "timeout_seconds": 10},
        ],
        "monitoring_metrics": [
            "Crash-free session rate",
            "App Not Responding (ANR) rate",
            "API error rate from mobile clients",
            "App launch time",
            "User retention (day 1, day 7)",
            "Store rating changes",
        ],
        "rollback_steps": [
            "Submit expedited review for hotfix build",
            "Enable server-side kill switch for broken features",
            "Roll back backend API to support previous app version",
            "Communicate via in-app messaging about known issues",
        ],
        "pre_deploy_checks": [
            "UI tests pass on target device matrix",
            "Backend APIs backward-compatible with previous app version",
            "App size within acceptable limits",
            "Staged rollout percentage configured (5% initially)",
            "Crash reporting SDK configured",
        ],
        "post_deploy_checks": [
            "Crash-free rate above 99.5%",
            "No spike in ANR reports",
            "App store review approved",
            "Staged rollout metrics healthy before increasing percentage",
        ],
    },
    "infrastructure": {
        "label": "Infrastructure (IaC)",
        "description": "Infrastructure as Code changes (Terraform, Pulumi, CloudFormation).",
        "default_strategy": "rolling",
        "recommended_strategies": ["rolling", "blue-green"],
        "artifacts": ["Terraform plan", "State file backup", "Drift report"],
        "health_checks": [
            {"endpoint": "Cloud provider health API", "method": "GET", "expected_status": 200, "timeout_seconds": 15},
        ],
        "monitoring_metrics": [
            "Resource provisioning success rate",
            "Infrastructure drift count",
            "Cloud spend delta (pre/post deploy)",
            "Service availability during change",
            "DNS propagation status",
        ],
        "rollback_steps": [
            "Apply previous Terraform state (terraform apply -target)",
            "Restore from state file backup",
            "Verify all dependent services reconnect",
            "Check DNS and load balancer routing",
            "Review cloud audit logs for partial changes",
        ],
        "pre_deploy_checks": [
            "Terraform plan reviewed and approved",
            "No destructive changes without explicit confirmation",
            "State file backed up",
            "Blast radius assessed (how many services affected)",
            "Maintenance window scheduled if needed",
        ],
        "post_deploy_checks": [
            "All resources in desired state (no drift)",
            "Dependent services healthy",
            "Network connectivity verified",
            "Cloud costs within expected range",
            "Security group rules correct",
        ],
    },
}

# ---------------------------------------------------------------------------
# Deployment strategy details
# ---------------------------------------------------------------------------

STRATEGIES = {
    "blue-green": {
        "label": "Blue-Green",
        "description": "Maintain two identical environments. Deploy to the inactive one, then switch traffic.",
        "pros": [
            "Zero-downtime deployment",
            "Instant rollback (switch back to old environment)",
            "Full production testing before traffic switch",
        ],
        "cons": [
            "Requires 2x infrastructure during deployment",
            "Database migrations need careful handling",
            "Stateful services complicate the switch",
        ],
        "phases": [
            {"name": "Prepare green", "duration": "5-10 min", "action": "Deploy new version to inactive environment"},
            {"name": "Validate green", "duration": "5-15 min", "action": "Run health checks and smoke tests on green"},
            {"name": "Switch traffic", "duration": "< 1 min", "action": "Update load balancer to point to green"},
            {"name": "Monitor", "duration": "15-30 min", "action": "Watch error rates and latency on green"},
            {"name": "Decommission blue", "duration": "5 min", "action": "Tear down old environment (or keep as rollback)"},
        ],
        "rollback_time": "< 1 minute (traffic switch)",
    },
    "canary": {
        "label": "Canary",
        "description": "Route a small percentage of traffic to the new version; increase gradually.",
        "pros": [
            "Low risk -- only a fraction of users see the new version initially",
            "Real production traffic validates the release",
            "Gradual rollout allows early detection of issues",
        ],
        "cons": [
            "Complex traffic routing configuration",
            "Requires good observability to detect issues at low traffic percentages",
            "Longer total deployment time",
        ],
        "phases": [
            {"name": "Deploy canary", "duration": "5 min", "action": "Deploy new version alongside stable"},
            {"name": "Route 5%", "duration": "15 min", "action": "Send 5% traffic to canary, monitor"},
            {"name": "Route 25%", "duration": "30 min", "action": "Increase to 25% if metrics healthy"},
            {"name": "Route 50%", "duration": "60 min", "action": "Increase to 50% if metrics healthy"},
            {"name": "Route 100%", "duration": "ongoing", "action": "Promote canary to stable, remove old version"},
        ],
        "rollback_time": "< 1 minute (route 100% back to stable)",
    },
    "rolling": {
        "label": "Rolling Update",
        "description": "Replace instances one at a time (or in batches), maintaining availability throughout.",
        "pros": [
            "No additional infrastructure required",
            "Built into Kubernetes and most orchestrators",
            "Simple to configure and understand",
        ],
        "cons": [
            "Mixed versions running during deployment",
            "Rollback requires another rolling update",
            "Harder to test with full production traffic before commit",
        ],
        "phases": [
            {"name": "Start rollout", "duration": "1 min", "action": "Begin replacing instances (maxSurge/maxUnavailable)"},
            {"name": "Rolling replace", "duration": "5-20 min", "action": "Instances replaced incrementally with health checks"},
            {"name": "Verify", "duration": "5 min", "action": "Confirm all instances on new version and healthy"},
            {"name": "Monitor", "duration": "15 min", "action": "Watch metrics for regression"},
        ],
        "rollback_time": "5-20 minutes (rolling back to previous version)",
    },
}

# ---------------------------------------------------------------------------
# Environment templates
# ---------------------------------------------------------------------------

ENVIRONMENT_DEFAULTS = {
    "dev": {
        "label": "Development",
        "deploy_trigger": "Every push to feature branch",
        "approval_required": False,
        "replicas": 1,
        "auto_scale": False,
        "monitoring_level": "Basic (logs only)",
        "alerting": False,
        "data": "Seed/fixture data",
        "secrets_source": "Repository secrets",
        "retention_days": 7,
    },
    "staging": {
        "label": "Staging",
        "deploy_trigger": "Merge to main branch",
        "approval_required": False,
        "replicas": 2,
        "auto_scale": False,
        "monitoring_level": "Full observability",
        "alerting": False,
        "data": "Anonymized production clone",
        "secrets_source": "Environment secrets",
        "retention_days": 30,
    },
    "prod": {
        "label": "Production",
        "deploy_trigger": "Manual approval after staging validation",
        "approval_required": True,
        "replicas": 3,
        "auto_scale": True,
        "monitoring_level": "Full observability + tracing",
        "alerting": True,
        "data": "Production data",
        "secrets_source": "Vault / OIDC",
        "retention_days": 90,
    },
    "qa": {
        "label": "QA / Testing",
        "deploy_trigger": "On-demand or PR-based",
        "approval_required": False,
        "replicas": 1,
        "auto_scale": False,
        "monitoring_level": "Full observability",
        "alerting": False,
        "data": "Test data set",
        "secrets_source": "Environment secrets",
        "retention_days": 14,
    },
    "uat": {
        "label": "User Acceptance Testing",
        "deploy_trigger": "Manual promotion from staging",
        "approval_required": True,
        "replicas": 2,
        "auto_scale": False,
        "monitoring_level": "Full observability",
        "alerting": False,
        "data": "Anonymized production clone",
        "secrets_source": "Environment secrets",
        "retention_days": 30,
    },
}


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------


def generate_plan(project_type_key, environment_names, strategy_key, output_format):
    """Generate a deployment plan."""
    project_type = PROJECT_TYPES.get(project_type_key)
    if not project_type:
        return {"error": f"Unsupported project type: {project_type_key}. Supported: {', '.join(PROJECT_TYPES)}"}

    strategy_key = strategy_key or project_type["default_strategy"]
    strategy = STRATEGIES.get(strategy_key)
    if not strategy:
        return {"error": f"Unsupported strategy: {strategy_key}. Supported: {', '.join(STRATEGIES)}"}

    env_names = [e.strip() for e in environment_names.split(",")]
    environments = {}
    for name in env_names:
        if name in ENVIRONMENT_DEFAULTS:
            environments[name] = ENVIRONMENT_DEFAULTS[name].copy()
        else:
            # Custom environment with sensible defaults
            environments[name] = {
                "label": name.capitalize(),
                "deploy_trigger": "Manual",
                "approval_required": False,
                "replicas": 1,
                "auto_scale": False,
                "monitoring_level": "Basic",
                "alerting": False,
                "data": "Custom data",
                "secrets_source": "Environment secrets",
                "retention_days": 14,
            }

    plan = {
        "project_type": project_type_key,
        "project_label": project_type["label"],
        "description": project_type["description"],
        "strategy": strategy_key,
        "strategy_label": strategy["label"],
        "strategy_description": strategy["description"],
        "environments": environments,
        "artifacts": project_type["artifacts"],
        "health_checks": project_type["health_checks"],
        "monitoring_metrics": project_type["monitoring_metrics"],
        "pre_deploy_checks": project_type["pre_deploy_checks"],
        "post_deploy_checks": project_type["post_deploy_checks"],
        "rollback_steps": project_type["rollback_steps"],
        "strategy_details": {
            "pros": strategy["pros"],
            "cons": strategy["cons"],
            "phases": strategy["phases"],
            "rollback_time": strategy["rollback_time"],
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    if output_format == "json":
        return plan

    return _format_plan_markdown(plan)


def _format_plan_markdown(plan):
    """Format the deployment plan as a readable markdown document."""
    lines = []

    lines.append(f"# Deployment Plan: {plan['project_label']}")
    lines.append("")
    lines.append(f"**Generated:** {plan['generated_at']}")
    lines.append(f"**Project Type:** {plan['project_label']}")
    lines.append(f"**Strategy:** {plan['strategy_label']}")
    lines.append(f"**Environments:** {', '.join(plan['environments'].keys())}")
    lines.append("")
    lines.append(f"> {plan['description']}")
    lines.append("")

    # Strategy overview
    lines.append("## Deployment Strategy")
    lines.append("")
    lines.append(f"### {plan['strategy_label']}")
    lines.append("")
    lines.append(plan["strategy_description"])
    lines.append("")

    lines.append("**Advantages:**")
    for pro in plan["strategy_details"]["pros"]:
        lines.append(f"- {pro}")
    lines.append("")

    lines.append("**Trade-offs:**")
    for con in plan["strategy_details"]["cons"]:
        lines.append(f"- {con}")
    lines.append("")

    lines.append(f"**Estimated rollback time:** {plan['strategy_details']['rollback_time']}")
    lines.append("")

    lines.append("### Deployment Phases")
    lines.append("")
    lines.append("| Phase | Duration | Action |")
    lines.append("|-------|----------|--------|")
    for phase in plan["strategy_details"]["phases"]:
        lines.append(f"| {phase['name']} | {phase['duration']} | {phase['action']} |")
    lines.append("")

    # Environment matrix
    lines.append("## Environment Matrix")
    lines.append("")

    env_keys = list(plan["environments"].keys())
    header_row = "| Aspect | " + " | ".join(plan["environments"][e]["label"] for e in env_keys) + " |"
    separator = "|--------|" + "|".join("------" for _ in env_keys) + "|"

    aspects = [
        ("Deploy trigger", "deploy_trigger"),
        ("Approval required", "approval_required"),
        ("Replicas", "replicas"),
        ("Auto-scale", "auto_scale"),
        ("Monitoring", "monitoring_level"),
        ("Alerting", "alerting"),
        ("Data source", "data"),
        ("Secrets source", "secrets_source"),
        ("Log retention", "retention_days"),
    ]

    lines.append(header_row)
    lines.append(separator)
    for label, key in aspects:
        values = []
        for e in env_keys:
            val = plan["environments"][e].get(key, "N/A")
            if isinstance(val, bool):
                val = "Yes" if val else "No"
            elif key == "retention_days":
                val = f"{val} days"
            values.append(str(val))
        lines.append(f"| {label} | " + " | ".join(values) + " |")
    lines.append("")

    # Artifacts
    lines.append("## Build Artifacts")
    lines.append("")
    for artifact in plan["artifacts"]:
        lines.append(f"- {artifact}")
    lines.append("")

    # Pre-deploy checks
    lines.append("## Pre-Deployment Checklist")
    lines.append("")
    for i, check in enumerate(plan["pre_deploy_checks"], 1):
        lines.append(f"- [ ] {check}")
    lines.append("")

    # Health checks
    lines.append("## Health Checks")
    lines.append("")
    lines.append("| Endpoint | Method | Expected Status | Timeout |")
    lines.append("|----------|--------|----------------|---------|")
    for hc in plan["health_checks"]:
        lines.append(f"| `{hc['endpoint']}` | {hc['method']} | {hc['expected_status']} | {hc['timeout_seconds']}s |")
    lines.append("")

    lines.append("**Health check verification script:**")
    lines.append("")
    lines.append("```bash")
    lines.append("#!/bin/bash")
    lines.append('HEALTH_URL="${1:?Usage: health-check.sh <base-url>}"')
    lines.append("")
    for hc in plan["health_checks"]:
        lines.append(f'echo "Checking {hc["endpoint"]}..."')
        lines.append(f'STATUS=$(curl -s -o /dev/null -w "%{{http_code}}" --max-time {hc["timeout_seconds"]} "$HEALTH_URL{hc["endpoint"]}")')
        lines.append(f'if [ "$STATUS" -ne {hc["expected_status"]} ]; then')
        lines.append(f'  echo "FAIL: {hc["endpoint"]} returned $STATUS (expected {hc["expected_status"]})"')
        lines.append(f'  exit 1')
        lines.append(f'fi')
        lines.append(f'echo "OK: {hc["endpoint"]} returned $STATUS"')
        lines.append("")
    lines.append('echo "All health checks passed."')
    lines.append("```")
    lines.append("")

    # Post-deploy checks
    lines.append("## Post-Deployment Verification")
    lines.append("")
    for check in plan["post_deploy_checks"]:
        lines.append(f"- [ ] {check}")
    lines.append("")

    # Monitoring
    lines.append("## Monitoring Metrics")
    lines.append("")
    lines.append("Track these metrics before, during, and after deployment:")
    lines.append("")
    for metric in plan["monitoring_metrics"]:
        lines.append(f"- {metric}")
    lines.append("")

    # Rollback
    lines.append("## Rollback Procedure")
    lines.append("")
    lines.append(f"**Estimated rollback time:** {plan['strategy_details']['rollback_time']}")
    lines.append("")
    lines.append("**Steps:**")
    lines.append("")
    for i, step in enumerate(plan["rollback_steps"], 1):
        lines.append(f"{i}. {step}")
    lines.append("")

    lines.append("**Rollback triggers (auto-rollback if any are met):**")
    lines.append("")
    lines.append("- Error rate exceeds 1% for 2+ minutes")
    lines.append("- P99 latency exceeds 2x baseline for 5+ minutes")
    lines.append("- Health check failures on 2+ consecutive checks")
    lines.append("- Critical alert fires within 15 minutes of deployment")
    lines.append("")

    # Promotion flow
    lines.append("## Environment Promotion Flow")
    lines.append("")
    env_labels = [plan["environments"][e]["label"] for e in env_keys]
    flow_parts = []
    for i, label in enumerate(env_labels):
        if plan["environments"][env_keys[i]].get("approval_required"):
            flow_parts.append(f"[Approval Gate] -> {label}")
        else:
            flow_parts.append(label)
    lines.append("```")
    lines.append(" -> ".join(flow_parts))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate a deployment plan based on project type and target environments.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Project types: webapp, microservice, library, mobile, infrastructure

            Strategies: blue-green, canary, rolling

            Environment names: dev, staging, prod, qa, uat (or any custom name)

            Examples:
              %(prog)s --type webapp --environments dev,staging,prod
              %(prog)s --type microservice --environments dev,staging,prod --strategy canary
              %(prog)s --type library --environments staging,prod
              %(prog)s --type mobile --environments dev,qa,staging,prod --strategy canary
              %(prog)s --type infrastructure --environments staging,prod --strategy rolling
              %(prog)s --type webapp --environments dev,staging,prod --format json
        """),
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=list(PROJECT_TYPES.keys()),
        help="Project type.",
    )
    parser.add_argument(
        "--environments",
        required=True,
        help="Comma-separated list of environment names (e.g., dev,staging,prod).",
    )
    parser.add_argument(
        "--strategy",
        choices=list(STRATEGIES.keys()),
        help="Deployment strategy (default depends on project type).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text/markdown).",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write plan to file instead of stdout.",
    )

    args = parser.parse_args()

    result = generate_plan(args.type, args.environments, args.strategy, args.format)

    # Handle errors
    if isinstance(result, dict) and "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Output
    if isinstance(result, dict):
        output_text = json.dumps(result, indent=2)
    else:
        output_text = result

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Deployment plan written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
