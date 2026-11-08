---
name: monorepo-navigator
description: >
  Manage and optimize monorepos with Turborepo, Nx, pnpm workspaces, and Changesets. Use when
  working in monorepos, running impact analysis, optimizing build times with remote caching,
  migrating from multi-repo, or coordinating publishing.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: monorepo-architecture
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: turborepo, nx, pnpm-workspaces, changesets
  tags:
    - monorepo
    - turborepo
    - nx
    - pnpm
    - changesets
---
# Monorepo Navigator

Navigate, manage, and optimize monorepos at any scale. Covers Turborepo, Nx, pnpm workspaces, and Lerna/Changesets for cross-package impact analysis, selective builds on affected packages only, dependency graph visualization, remote caching configuration, migration from multi-repo to monorepo with preserved git history, and coordinated package publishing with automated changelogs.

**Keywords:** monorepo, Turborepo, Nx, pnpm workspaces, Changesets, dependency graph, remote cache, affected packages, selective builds, cross-package impact, npm publishing, workspace protocol

## Core Capabilities

- **Impact analysis** — determine which apps break when a shared package changes, trace dependency chains, visualize Mermaid graphs, and calculate blast radius.
- **Selective execution** — run tests/builds only for affected packages, filter by changed files since a git ref, and skip unchanged packages in CI.
- **Build optimization** — remote caching (Turborepo/Vercel, Nx Cloud), incremental builds with input/output config, dependency-aware parallel scheduling, and artifact sharing.
- **Publishing** — Changesets for coordinated versioning, automated per-package changelogs, pre-release channels, and `workspace:*` replacement during publish.

## When to Use

- Multiple packages/apps share code (UI components, utils, types, API clients)
- Build times are slow because everything rebuilds on every change
- Migrating from multiple repos to a single monorepo
- Publishing npm packages with coordinated versioning
- Teams work across packages and need unified tooling

## Clarify First

Before analyzing or configuring, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Tooling:** Turborepo, Nx, pnpm workspaces, or Changesets (drives the config and commands generated).
- **Task:** impact/dependency analysis, build optimization, or publishing setup (selects `dependency_graph.py` vs `impact_detector.py` vs `package_analyzer.py`).
- **Repo root & git ref:** the monorepo path and the baseline ref for "affected" detection (sets `--ref` and what counts as changed).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Command |
|------|---------|---------|
| `dependency_graph.py` | Mermaid dependency graph of internal packages, optionally focused on one package | `python3 scripts/dependency_graph.py <root> --focus @repo/ui --direction dependents` |
| `impact_detector.py` | Packages affected (directly and transitively) by changed files | `python3 scripts/impact_detector.py <root> --ref origin/main --affected-only` |
| `package_analyzer.py` | Package inventory, internal and shared external dependencies, version drift, orphans | `python3 scripts/package_analyzer.py <root> --only-shared` |

Workspace detection order: `pnpm-workspace.yaml`, then the root `package.json` `workspaces` field (npm, Yarn), then `lerna.json`. **Exit codes:** 0 report; 2 no packages found or bad input (a directory that is not a workspace root must not look like an empty monorepo).

## Quick Start

```bash
# from engineering/monorepo-navigator/ (a four-package pnpm workspace)
python3 scripts/package_analyzer.py assets/sample_monorepo                    # 4 packages, 3 internal deps, date-fns drift
python3 scripts/impact_detector.py assets/sample_monorepo --files packages/utils/src/index.ts --affected-only
python3 scripts/dependency_graph.py assets/sample_monorepo --focus @acme/utils --direction dependents --mermaid-only
```

A change in `packages/utils` affects `@acme/ui`, `@acme/utils` and `@acme/web` (through `ui`), but not `@acme/docs`.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tooling-and-configuration.md](references/tooling-and-configuration.md)** — tool selection decision matrix, recommended repo structure, full turbo.json and pnpm-workspace config, key Turborepo/pnpm commands, impact-analysis commands, remote-caching setup, affected-only CI workflow, Changesets publishing, and multi-repo→monorepo migration steps. Read when configuring or operating a monorepo.
- **[references/operations-and-best-practices.md](references/operations-and-best-practices.md)** — common pitfalls, best practices, troubleshooting table, and success criteria. Read when something misbehaves or when validating a setup.

## Anti-Patterns

**Mistake:** Running every test and build on every change.
**Why it matters:** CI time grows with the repo, not with the change, and teams start skipping checks.
**Instead:** Use the affected set from `impact_detector.py` (or the build tool's filter) and run the full suite on a schedule.

**Mistake:** Letting shared dependencies drift between packages.
**Why it matters:** Two versions of the same library ship twice, and bugs reproduce in one app but not another.
**Instead:** Check `package_analyzer.py --only-shared` and pin shared versions in one place (catalog or root constraints).

**Mistake:** Deep imports across package boundaries (`../../packages/ui/src/...`).
**Why it matters:** The dependency never appears in `package.json`, so impact analysis and the build cache miss it.
**Instead:** Import through the package name and declare it with `workspace:*`.

## Files

| File | Purpose |
|------|---------|
| `scripts/package_analyzer.py`, `scripts/impact_detector.py`, `scripts/dependency_graph.py` | Stdlib CLIs |
| `assets/sample_monorepo/` | pnpm workspace: `apps/web`, `apps/docs`, `packages/ui`, `packages/utils` |

## Scope & Limitations

**This skill covers:**
- Turborepo, Nx, and pnpm workspace configuration and optimization
- Cross-package dependency analysis and impact visualization
- Remote caching setup (Vercel, Nx Cloud, self-hosted)
- Changesets-based coordinated versioning and npm publishing

**This skill does NOT cover:**
- Application-level build configuration (webpack, Vite, esbuild internals) — see `performance-profiler`
- CI/CD pipeline design beyond monorepo-specific filters — see `ci-cd-pipeline-builder`
- Git branching strategies and release flow — see `release-manager`
- Dependency vulnerability scanning and license auditing — see `dependency-auditor`
