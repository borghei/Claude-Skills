---
name: docker-development
description: >
  Analyse Dockerfiles and Compose files for security, image size, cache and config problems,
  with CI-ready exit codes. Use when reviewing or optimising a Dockerfile, validating
  docker-compose, or adding a container lint step.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: containers
  updated: 2026-11-08
  tags: [docker, containers, devops, compose, dockerfile]
---
# Docker Development

The agent reviews Dockerfiles and Compose files the way a careful platform engineer would: security first (root user, secrets, privileged containers, floating tags), then image size and build-cache order, then operability (health checks, restart policies, resource limits). The two analyzers catch the mechanical issues so the review can focus on the design.

## When to Use

- Reviewing or optimising a Dockerfile (size, cache hits, security).
- Validating a docker-compose file before it is shared or deployed.
- Adding a container lint step to CI.

## Clarify First

Before running the analysis, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target file:** which Dockerfile or docker-compose.yml to analyze (sets `--file` and which tool runs).
- **Focus:** full analysis vs security-only, and whether to check port conflicts (sets `--security-only`/`--check-ports`).
- **Output mode:** human-readable vs JSON for CI (sets `--format json` and whether findings gate a pipeline).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Analyse** the Dockerfile with `dockerfile_analyzer.py` and the Compose file with `compose_validator.py`.
2. **Fix critical findings first**: secrets in `ENV`/environment, root user, privileged mode, host port conflicts. Then floating tags, then layer and cache order, then health checks and limits.
3. **Change the design where the findings point to it**: a multi-stage build when build tools ship in the runtime image, a non-root `USER`, dependency files copied before source.
4. **Verify** by rerunning both tools (critical count must be 0), then a real `docker build` and `docker compose config` to confirm the files still work. The analyzers read text; only a build proves the image.

## Quick Start

```bash
python3 scripts/dockerfile_analyzer.py --file examples/Dockerfile.sample                 # latest tag, ENV secret, root (exit 1)
python3 scripts/compose_validator.py --file examples/docker-compose.sample.yml          # port clash, privileged, literal passwords (exit 1)
python3 scripts/compose_validator.py --file examples/docker-compose.sound.yml           # clean (exit 0)
python3 scripts/compose_validator.py --file examples/docker-compose.sample.yml --check-ports   # port check only
```

In CI, write one report per tool (two JSON documents in one file is not valid JSON) and gate on the exit codes:

```bash
python3 scripts/dockerfile_analyzer.py --file Dockerfile --format json > dockerfile-report.json
python3 scripts/compose_validator.py --file docker-compose.yml --format json > compose-report.json
```

## Tools Overview

| Tool | Checks | Key flags | Exit codes |
|------|--------|-----------|------------|
| `dockerfile_analyzer.py` | Root user, `latest`/untagged base, secrets in `ENV`/`ARG`, oversized base images, runs of consecutive `RUN` layers, missing `--no-install-recommends`, cache-breaking `COPY .` before installs, single-stage builds with many steps, missing `HEALTHCHECK`, missing `.dockerignore` next to the Dockerfile | `--file`, `--security-only`, `--format text|json` | 0 no critical, 1 critical finding, 2 file not found |
| `compose_validator.py` | Structure, circular `depends_on`, host port conflicts, Docker socket and sensitive mounts, privileged and host network mode, floating image tags, literal passwords/secrets/tokens in `environment`, restart policy, resource limits | `--file`, `--check-ports` (runs only the port check), `--format text|json` | 0 no critical, 1 critical finding, 2 file not found |

## Anti-Patterns

**Mistake:** Treating a clean analyzer run as a container security review.
**Why it happens:** Zero findings looks like approval.
**Instead:** The rules are text checks. Scan the built image for CVEs (Trivy, Grype or the registry's scanner) and review runtime privileges separately.

**Mistake:** "Fixing" a secret finding by moving the value to a build `ARG`.
**Why it happens:** The warning disappears from `ENV`.
**Instead:** Build args are stored in image history. Use BuildKit secrets (`RUN --mount=type=secret`) for build-time secrets and runtime environment or secret stores for the rest.

**Mistake:** Switching every base image to Alpine for size.
**Why it happens:** Smaller looks strictly better.
**Instead:** musl breaks some native wheels and binaries. Prefer `-slim` or distroless when Alpine causes rebuilds from source, and confirm with a test build.

## Files

- `scripts/dockerfile_analyzer.py`, `scripts/compose_validator.py` — the analyzers.
- `examples/Dockerfile.sample`, `examples/docker-compose.sample.yml` (deliberately flawed), `examples/docker-compose.sound.yml` (passes).

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

- [references/docker-best-practices.md](references/docker-best-practices.md) — Dockerfile and Compose patterns (multi-stage builds, layer order, non-root users, health checks, secrets) with examples. Read when rewriting a Dockerfile or Compose file.
