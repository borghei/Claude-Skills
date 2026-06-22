---
name: monorepo-navigator
description: >
  Manage and optimize monorepos with Turborepo, Nx, pnpm workspaces, and Changesets. Use when
  working in monorepos, running impact analysis, optimizing build times with remote caching,
  migrating from multi-repo, or coordinating publishing.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: monorepo-architecture
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: turborepo, nx, pnpm-workspaces, changesets
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

Before analyzing or configuring, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Tooling** — Turborepo, Nx, pnpm workspaces, or Changesets (drives the config and commands generated)
- [ ] **Task** — impact/dependency analysis, build optimization, or publishing setup (selects `dependency_graph.py` vs `impact_detector.py` vs `package_analyzer.py`)
- [ ] **Repo root & git ref** — the monorepo path and the baseline ref for "affected" detection (sets `--ref` and what counts as changed)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `dependency_graph.py` | Generate a Mermaid dependency graph of internal packages | `python scripts/dependency_graph.py . --focus @repo/ui --direction dependents` |
| `impact_detector.py` | Detect which packages are affected by file changes | `python scripts/impact_detector.py . --ref origin/main --affected-only` |
| `package_analyzer.py` | Analyze package structure, dependencies, and health | `python scripts/package_analyzer.py . --only-shared` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tooling-and-configuration.md](references/tooling-and-configuration.md)** — tool selection decision matrix, recommended repo structure, full turbo.json and pnpm-workspace config, key Turborepo/pnpm commands, impact-analysis commands, remote-caching setup, affected-only CI workflow, Changesets publishing, and multi-repo→monorepo migration steps. Read when configuring or operating a monorepo.
- **[references/operations-and-best-practices.md](references/operations-and-best-practices.md)** — common pitfalls, best practices, troubleshooting table, and success criteria. Read when something misbehaves or when validating a setup.

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|------------|-----------|
| `ci-cd-pipeline-builder` | Monorepo-aware CI workflows use `--filter` flags and remote caching tokens | Monorepo Navigator defines filter patterns and cache config that CI pipelines consume |
| `release-manager` | Changesets versioning feeds into release orchestration and tag management | Release Manager triggers `changeset version` and `changeset publish` as part of release flow |
| `dependency-auditor` | Workspace dependency graph informs vulnerability and license scanning scope | Monorepo Navigator exports the package dependency tree that Dependency Auditor analyzes |
| `performance-profiler` | Build profiling data identifies slow packages for optimization | Performance Profiler measures per-package build times surfaced by Turborepo `--summarize` |
| `changelog-generator` | Changesets produce per-package changelogs consumed by release notes | Changeset summaries flow into Changelog Generator for formatted release documentation |
| `tech-debt-tracker` | Cross-package coupling and circular dependencies surface as tracked tech debt items | Monorepo Navigator's impact analysis identifies coupling hotspots that Tech Debt Tracker records |
