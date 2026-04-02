---
name: helm-chart-builder
description: >
  This skill should be used when the user asks to "analyze Helm charts",
  "validate Helm values", "review chart structure", "check Kubernetes Helm
  templates", or "audit chart dependencies and configuration".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: kubernetes
  updated: 2026-04-02
  tags: [helm, kubernetes, k8s, charts, devops]
---
# Helm Chart Builder

> **Category:** Engineering
> **Domain:** Kubernetes & Helm

## Overview

The **Helm Chart Builder** skill provides automated analysis of Helm charts including structure validation, values checking, template inspection, and dependency review. It helps teams maintain high-quality charts with correct configurations, proper security contexts, and complete documentation.

## Quick Start

```bash
# Analyze chart structure and quality
python scripts/chart_analyzer.py --path ./charts/my-app

# Validate values.yaml against chart requirements
python scripts/values_validator.py --chart ./charts/my-app --values values-prod.yaml

# JSON output for CI
python scripts/chart_analyzer.py --path ./charts/my-app --format json

# Validate multiple values files
python scripts/values_validator.py --chart ./charts/my-app --values values-dev.yaml values-prod.yaml
```

## Tools Overview

### chart_analyzer.py

Analyzes Helm chart structure, metadata, templates, and dependencies.

| Feature | Description |
|---------|-------------|
| Structure validation | Checks required files exist (Chart.yaml, values.yaml, templates/) |
| Metadata check | Validates Chart.yaml fields, version format, appVersion |
| Template review | Inspects templates for common patterns and issues |
| Dependency analysis | Reviews subchart dependencies and version constraints |
| Documentation check | Verifies NOTES.txt and README presence |

### values_validator.py

Validates values files against chart expectations and Kubernetes best practices.

| Feature | Description |
|---------|-------------|
| Resource limits | Checks for CPU/memory requests and limits |
| Security context | Validates runAsNonRoot, readOnlyRootFilesystem |
| Replica count | Checks for production-appropriate replica counts |
| Image tags | Flags use of latest or missing image tags |
| Ingress config | Validates ingress annotations and TLS settings |

## Workflows

### Chart Review Workflow

1. **Analyze structure** - Run chart_analyzer.py to check chart organization
2. **Validate defaults** - Run values_validator.py against default values.yaml
3. **Check environments** - Validate each environment's values file
4. **Review findings** - Address critical issues first, then warnings
5. **Re-check** - Confirm fixes pass validation

### Pre-Release Workflow

1. **Bump version** - Update Chart.yaml version and appVersion
2. **Lint chart** - Run chart_analyzer.py in strict mode
3. **Validate all values** - Check every environment's values file
4. **Check dependencies** - Ensure subchart versions are pinned
5. **Package** - Chart is ready for helm package

### CI Integration

```bash
# Structure check
python scripts/chart_analyzer.py --path ./charts/my-app --format json --strict

# Values validation for all environments
for env in dev staging production; do
  python scripts/values_validator.py \
    --chart ./charts/my-app \
    --values "values-${env}.yaml"
done
```

## Reference Documentation

- [Helm Best Practices](references/helm-best-practices.md) - Chart structure, templates, security, dependencies

## Common Patterns Quick Reference

### Required Chart Structure
```
my-chart/
  Chart.yaml          # Required: chart metadata
  values.yaml         # Required: default values
  templates/          # Required: template directory
    deployment.yaml
    service.yaml
    _helpers.tpl      # Recommended: template helpers
    NOTES.txt         # Recommended: post-install notes
  charts/             # Optional: subchart dependencies
```

### Values Best Practices
| Setting | Requirement | Why |
|---------|------------|-----|
| resources.limits | Required | Prevents resource exhaustion |
| resources.requests | Required | Enables proper scheduling |
| securityContext.runAsNonRoot | Required | Security baseline |
| image.tag | Required (not latest) | Reproducible deployments |
| replicaCount >= 2 | Recommended for prod | High availability |
| ingress.tls | Recommended | Encrypted traffic |

### Chart.yaml Required Fields
| Field | Description |
|-------|-------------|
| apiVersion | v2 for Helm 3 |
| name | Chart name (lowercase) |
| version | SemVer chart version |
| appVersion | Application version |
| description | Brief chart description |

### Common Issues
| Issue | Severity | Fix |
|-------|----------|-----|
| Missing Chart.yaml | Critical | Add required chart metadata |
| No resource limits | Warning | Set CPU/memory limits |
| Latest image tag | Warning | Pin specific version |
| No security context | Warning | Add runAsNonRoot: true |
| Missing NOTES.txt | Info | Add post-install notes |
| Unpinned dependencies | Warning | Pin subchart versions |
