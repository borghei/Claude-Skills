---
name: docker-development
description: >
  This skill should be used when the user asks to "analyze a Dockerfile",
  "optimize Docker layers", "validate docker-compose", "check container
  best practices", or "audit Docker configurations".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: containers
  updated: 2026-04-02
  tags: [docker, containers, devops, compose, dockerfile]
---
# Docker Development

> **Category:** Engineering
> **Domain:** Container Development & Optimization

## Overview

The **Docker Development** skill provides automated analysis of Dockerfiles and docker-compose configurations. It identifies layer optimization opportunities, security issues, best practice violations, and compose service misconfigurations. Use this skill to enforce container standards across your team and catch issues before they reach production.

## Clarify First

Before running the analysis, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target file:** which Dockerfile or docker-compose.yml to analyze (sets `--file` and which tool runs).
- **Focus:** full analysis vs security-only, and whether to check port conflicts (sets `--security-only`/`--check-ports`).
- **Output mode:** human-readable vs JSON for CI (sets `--format json` and whether findings gate a pipeline).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Analyze a Dockerfile for best practices
python scripts/dockerfile_analyzer.py --file Dockerfile

# Analyze with JSON output
python scripts/dockerfile_analyzer.py --file Dockerfile --format json

# Validate a docker-compose file
python scripts/compose_validator.py --file docker-compose.yml

# Check for host port conflicts between services in one compose file
python scripts/compose_validator.py --file docker-compose.yml --check-ports
```

## Tools Overview

### dockerfile_analyzer.py

Analyzes Dockerfiles for best practices, security issues, and optimization opportunities.

| Feature | Description |
|---------|-------------|
| Layer optimization | Detects unnecessary layers, recommends combining RUN statements |
| Multi-stage analysis | Lists build stages and suggests a multi-stage build when a single stage has many RUN steps (does not measure image size) |
| Security scanning | Flags running as root, use of latest tags, exposed secrets |
| Base image checks | Recommends smaller base images (alpine, distroless, slim) |
| Cache optimization | Identifies poor layer ordering that breaks Docker cache |

```bash
# Full analysis
python scripts/dockerfile_analyzer.py --file Dockerfile

# Security-focused scan
python scripts/dockerfile_analyzer.py --file Dockerfile --security-only

# JSON output for CI integration
python scripts/dockerfile_analyzer.py --file Dockerfile --format json
```

### compose_validator.py

Validates docker-compose files for correctness, dependency issues, and port conflicts.

| Feature | Description |
|---------|-------------|
| Schema validation | Checks compose file structure and syntax |
| Dependency graph | Validates depends_on chains for circular dependencies |
| Port conflict detection | Identifies duplicate host port bindings |
| Volume mount checks | Validates volume paths and mount configurations |
| Network mode check | Flags services using `network_mode: host` (network definitions and connectivity are not checked) |

```bash
# Full validation
python scripts/compose_validator.py --file docker-compose.yml

# Check port conflicts only
python scripts/compose_validator.py --file docker-compose.yml --check-ports

# JSON output
python scripts/compose_validator.py --file docker-compose.yml --format json
```

## Workflows

### Dockerfile Review Workflow

1. **Analyze** - Run dockerfile_analyzer.py against the target Dockerfile
2. **Review findings** - Address critical security issues first (root user, secrets)
3. **Optimize layers** - Combine RUN statements, reorder for cache efficiency
4. **Validate base images** - Switch to minimal base images where possible
5. **Re-analyze** - Confirm improvements and verify no regressions

### Compose Validation Workflow

1. **Validate structure** - Run compose_validator.py for syntax and schema checks
2. **Check dependencies** - Review service dependency graph for circular refs
3. **Audit ports** - Ensure no host port conflicts across services
4. **Review volumes** - Confirm volume mounts are correct and necessary
5. **Network review** - Act on any host network mode warning, then check network definitions and service isolation by hand

### CI Integration Workflow

```yaml
# Example GitHub Actions step
- name: Docker Lint
  run: |
    python scripts/dockerfile_analyzer.py --file Dockerfile --format json > results.json
    python scripts/compose_validator.py --file docker-compose.yml --format json >> results.json
```

## Scope & Limitations

**In Scope:**
- Dockerfile analysis with `dockerfile_analyzer.py`: layer count, multi-stage use, running as root, `latest` tags, secrets in the file, base image choice and cache-breaking instruction order, with `--security-only` for a narrower report
- Compose file checks with `compose_validator.py`: file structure, circular `depends_on` chains, duplicate host port bindings, volume mounts, security settings and best practices such as restart policies and resource limits
- Text or JSON output for review and CI steps
- Dockerfile and Compose patterns from the Docker best practices reference

**Out of Scope:**
- Building images, running containers or measuring real image size
- Scanning image layers or packages for known CVEs (dependency-level scanning is in `engineering/dependency-auditor/`)
- Kubernetes manifests and Helm charts (see `engineering/kubernetes-operator/` and `engineering/helm-chart-builder/`)
- CI pipeline design around image builds (see `engineering/devops-workflow-engineer/`)

**Important Caveats:**
- Both tools read files as text. The Compose validator uses a small built-in YAML parser, so anchors, merge keys, `extends`, `include` and variable substitution may not be read correctly.
- `compose_validator.py` checks one file per run. Port conflicts or overrides spread across several Compose files are not detected.
- Base image advice is general. Whether `alpine`, `slim` or distroless suits an image depends on its libraries and needs a test build.
- A clean report means the rules found nothing. It is not a container security assessment.

## Reference Documentation

- [Docker Best Practices](references/docker-best-practices.md) - Comprehensive guide to Dockerfile and Compose patterns

## Common Patterns Quick Reference

| Pattern | Good | Bad |
|---------|------|-----|
| Base image | `FROM python:3.12-slim` | `FROM python:latest` |
| User | `USER appuser` | Running as root |
| Layer combining | `RUN apt-get update && apt-get install -y pkg` | Separate RUN for update and install |
| COPY ordering | Copy requirements first, then code | Copy everything at once |
| Multi-stage | Use builder stage + minimal runtime | Single stage with build tools |
| Secrets | Use build secrets or env at runtime | `COPY .env .` or `ENV SECRET=value` |
| Health checks | `HEALTHCHECK CMD curl -f http://localhost/` | No health check defined |
| .dockerignore | Include node_modules, .git, etc. | No .dockerignore file |

### Compose Patterns

| Pattern | Good | Bad |
|---------|------|-----|
| Restart policy | `restart: unless-stopped` | No restart policy |
| Resource limits | `deploy.resources.limits` set | Unlimited resources |
| Named volumes | `volumes: [db-data:/var/lib/postgresql]` | Anonymous volumes |
| Networks | Explicit network definitions | Default bridge only |
| Environment | `env_file: .env` | Inline secrets in compose |
