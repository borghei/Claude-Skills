---
name: helm-chart-builder
description: >
  Review an existing Helm chart and its values files: metadata, structure,
  dependency pinning, resources, security context, image tags, probes and plaintext
  secrets. Use when auditing a chart before release or adding chart checks to CI.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: kubernetes
  updated: 2026-11-08
  tags: [helm, kubernetes, k8s, charts, devops]
---
# Helm Chart Builder

The agent reviews Helm charts that already exist: is the chart well-formed, are its dependencies pinned, and are its values safe to run in production. Despite the name, the tools analyse rather than generate; when a new chart is needed, start from `helm create`, then run this review.

## When to Use

- Reviewing a chart or its per-environment values files before a release.
- Adding chart checks to CI.
- Auditing third-party charts and values overrides for security defaults.

## Clarify First

Before analyzing the chart, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Chart path:** which chart directory to analyze (sets `--path`/`--chart`).
- **Values files:** which environment values files to validate (sets `--values` and what gets checked against best practices).
- **Strictness:** strict/lint mode and JSON for CI (sets `--strict --format json` and whether findings gate the pipeline).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Analyse the chart** with `chart_analyzer.py --path <chart>`: required files, `apiVersion: v2`, SemVer version, appVersion, dependency pinning and `Chart.lock`, NOTES.txt, `_helpers.tpl`, README.
2. **Validate every values file** with `values_validator.py`: resources, security context, image tag, replicas, service type, ingress TLS, probes, autoscaling and plaintext secrets.
3. **Fix critical findings first** (missing required files, plaintext secrets), then warnings.
4. **Render and dry-run** with `helm lint`, `helm template` and `helm install --dry-run` (or `helm upgrade --install --dry-run=server` against a cluster). The analysers read text; only rendering proves the manifests.
5. **Verify** that both tools report no critical findings for every environment's values file and that the rendered manifests pass your policy checks.

Helm 4 (released late 2025) keeps chart `apiVersion: v2`, so v2 charts work with both Helm 3 and Helm 4. Check the Helm 4 release notes for changed CLI flags and plugin behaviour before upgrading CI.

## Quick Start

```bash
python3 scripts/chart_analyzer.py --path examples                                  # apiVersion v1, loose dependency range, missing files
python3 scripts/values_validator.py --values examples/values.yaml                  # latest tag, plaintext passwords, no resources (exit 1)
python3 scripts/values_validator.py --values examples/values-production.yaml       # passes (exit 0)
```

For CI, write one JSON report per tool:

```bash
python3 scripts/chart_analyzer.py --path ./charts/my-app --format json --strict > chart-report.json
python3 scripts/values_validator.py --chart ./charts/my-app --values values-dev.yaml values-prod.yaml --format json > values-report.json
```

## Tools Overview

| Tool | What it checks | Key flags | Exit codes |
|------|----------------|-----------|------------|
| `chart_analyzer.py` | Required files and dirs, Chart.yaml fields, `apiVersion: v2`, SemVer, appVersion, dependency version ranges and `Chart.lock`, template helpers, NOTES.txt, README | `--path`, `--strict` (warnings fail), `--format text|json` | 0, 1 critical (or warning with `--strict`), 2 not a chart directory |
| `values_validator.py` | Resources, security context, image tag (`latest` or empty), pull policy, replicaCount, service type, ingress TLS/class, probes, autoscaling, plaintext passwords/secrets/tokens and credentialed URLs | `--values <files...>`, `--chart` (only to locate relative paths), `--format text|json` | 0, 1 critical finding, 2 a values file not found |

## Anti-Patterns

**Mistake:** Passwords and API keys in `values.yaml`.
**Why it happens:** It is the quickest way to make a chart install.
**Instead:** Values end up in git and in the release history Helm stores in the cluster. Reference an existing Secret (`existingSecret`), or use External Secrets or SOPS.

**Mistake:** Broad dependency ranges such as `12.x.x` without a committed `Chart.lock`.
**Why it happens:** Ranges feel like they keep the chart current.
**Instead:** Pin dependency versions, commit `Chart.lock`, and update deliberately.

**Mistake:** Treating a clean analyser run as a working chart.
**Why it happens:** No findings looks like a pass.
**Instead:** Template logic and `--set` overrides are not evaluated. Render with `helm template` and dry-run the install.

## Files

- `scripts/chart_analyzer.py`, `scripts/values_validator.py` — the tools above.
- `examples/Chart.yaml`, `examples/values.yaml` — deliberately flawed chart metadata and values; `examples/values-production.yaml` — values that pass.

## Scope & Limitations

**In Scope:**
- Static review of a Helm chart directory with `chart_analyzer.py`: required files, Chart.yaml fields and version format, template file checks, subchart dependency pinning, and NOTES.txt and README presence.
- Best-practice checks on one or more values files with `values_validator.py`: resource requests and limits, security context, image tags, replica count, service, ingress TLS, probes and autoscaling.
- Text or JSON output, with `--strict` on the analyzer to treat warnings as errors in CI.
- The chart review and pre-release workflows, backed by `references/helm-best-practices.md`.

**Out of Scope:**
- Rendering, linting, installing or upgrading charts. The scripts do not call `helm` or a cluster.
- Generating new charts or templates. The scripts review existing files.
- Kubernetes operators and custom controllers (see `engineering/kubernetes-operator/`).
- Building container images (see `engineering/docker-development/`) and designing CI pipelines (see `engineering/ci-cd-pipeline-builder/`).

**Important Caveats:**
- Both scripts read YAML with a small stdlib parser and inspect templates with regular expressions. Template logic, `--set` overrides and values merged at install time are not evaluated, so a clean report does not mean the rendered manifests are correct.
- `values_validator.py` checks each values file against fixed best-practice rules. The `--chart` flag only locates the files; values are not compared with what the chart's templates actually use.
- Findings are review prompts, not proof that a chart is secure or production ready. The reference lists `helm lint`, `helm template` and a dry-run install as the checks that cover rendering.

## Reference Documentation

- [references/helm-best-practices.md](references/helm-best-practices.md) — chart structure, template patterns, security defaults, values design and dependency management. Read when restructuring a chart or writing templates.
