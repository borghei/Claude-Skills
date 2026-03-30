---
name: monorepo-navigator
description: >
  Navigate, manage, and optimize monorepos with Turborepo, Nx, pnpm workspaces,
  and Changesets. Covers cross-package impact analysis, selective builds,
  dependency graph visualization, remote caching, migration from multi-repo, and
  coordinated publishing. Use when working in monorepos, optimizing build times,
  or managing shared packages.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: monorepo-architecture
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: turborepo, nx, pnpm-workspaces, changesets
---
# Monorepo Navigator

**Tier:** POWERFUL
**Category:** Engineering / Build Systems
**Maintainer:** Claude Skills Team

## Overview

Navigate, manage, and optimize monorepos at any scale. Covers Turborepo, Nx, pnpm workspaces, and Lerna/Changesets for cross-package impact analysis, selective builds on affected packages only, dependency graph visualization, remote caching configuration, migration from multi-repo to monorepo with preserved git history, and coordinated package publishing with automated changelogs.

## Keywords

monorepo, Turborepo, Nx, pnpm workspaces, Changesets, dependency graph, remote cache, affected packages, selective builds, cross-package impact, npm publishing, workspace protocol

## Core Capabilities

### 1. Impact Analysis
- Determine which apps break when a shared package changes
- Trace dependency chains from leaf packages to root apps
- Visualize impact as Mermaid dependency graphs
- Calculate blast radius for any file change

### 2. Selective Execution
- Run tests/builds only for affected packages (not everything)
- Filter by changed files since a git ref
- Scope commands to specific packages and their dependents
- Skip unchanged packages in CI for faster feedback

### 3. Build Optimization
- Remote caching with Turborepo (Vercel) or Nx Cloud
- Incremental builds with proper input/output configuration
- Parallel execution with dependency-aware scheduling
- Artifact sharing between CI jobs

### 4. Publishing
- Changesets for coordinated versioning across packages
- Automated changelog generation per package
- Pre-release channels (alpha, beta, rc)
- `workspace:*` protocol replacement during publish

## When to Use

- Multiple packages/apps share code (UI components, utils, types, API clients)
- Build times are slow because everything rebuilds on every change
- Migrating from multiple repos to a single monorepo
- Publishing npm packages with coordinated versioning
- Teams work across packages and need unified tooling

## Tool Selection Decision Matrix

| Requirement | Turborepo | Nx | pnpm Workspaces | Changesets |
|-------------|-----------|-----|-----------------|------------|
| Simple task runner | Best | Good | N/A | N/A |
| Remote caching | Built-in | Nx Cloud | N/A | N/A |
| Code generation | No | Best | N/A | N/A |
| Dependency management | N/A | N/A | Best | N/A |
| Package publishing | N/A | N/A | N/A | Best |
| Plugin ecosystem | Limited | Extensive | N/A | N/A |
| Config complexity | Minimal | Moderate | Minimal | Minimal |

**Recommended modern stack:** pnpm workspaces + Turborepo + Changesets

## Monorepo Structure

```
my-monorepo/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── package.json        # depends on @repo/ui, @repo/utils
│   │   └── ...
│   ├── api/                    # Express/Fastify backend
│   │   ├── package.json        # depends on @repo/db, @repo/utils
│   │   └── ...
│   └── mobile/                 # React Native app
│       ├── package.json
│       └── ...
├── packages/
│   ├── ui/                     # Shared React components
│   │   ├── package.json        # @repo/ui
│   │   └── ...
│   ├── utils/                  # Shared utilities
│   │   ├── package.json        # @repo/utils
│   │   └── ...
│   ├── db/                     # Database client + schema
│   │   ├── package.json        # @repo/db
│   │   └── ...
│   ├── types/                  # Shared TypeScript types
│   │   ├── package.json        # @repo/types (no runtime deps)
│   │   └── ...
│   └── config/                 # Shared configs (tsconfig, eslint)
│       ├── tsconfig.base.json
│       └── eslint.base.js
├── turbo.json                  # Turborepo pipeline config
├── pnpm-workspace.yaml         # Workspace package locations
├── package.json                # Root scripts, devDependencies
└── .changeset/                 # Changeset config
    └── config.json
```

## Turborepo Configuration

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "globalEnv": ["NODE_ENV", "CI"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json", "package.json"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_*"]
    },
    "test": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tests/**", "vitest.config.*"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", ".eslintrc.*", "tsconfig.json"]
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### Key Turborepo Commands

```bash
# Run all tasks
turbo run build

# Run only affected packages (compared to main)
turbo run build test --filter='...[origin/main]'

# Run for a specific package and its dependencies
turbo run build --filter=@repo/web...

# Run for a specific package only (no deps)
turbo run test --filter=@repo/ui

# Dry run to see what would execute
turbo run build --dry=json

# View dependency graph
turbo run build --graph=graph.html

# Summarize cache usage
turbo run build --summarize
```

## pnpm Workspace Configuration

### pnpm-workspace.yaml

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### Cross-Package References

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "dependencies": {
    "@repo/types": "workspace:*"
  }
}

// apps/web/package.json
{
  "name": "@repo/web",
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/utils": "workspace:*"
  }
}
```

### Workspace Commands

```bash
# Install all workspace dependencies
pnpm install

# Add a dependency to a specific package
pnpm add zod --filter @repo/api

# Add a workspace package as dependency
pnpm add @repo/utils --filter @repo/web --workspace

# Run a script in a specific package
pnpm --filter @repo/web dev

# Run a script in all packages that have it
pnpm -r run build

# List all packages
pnpm -r ls --depth -1
```

## Impact Analysis

### Find All Dependents of a Changed Package

```bash
# Using turbo to see what depends on @repo/ui
turbo run build --filter='...@repo/ui' --dry=json | \
  jq '.tasks[].package' -r | sort -u

# Manual: search for imports of a package
grep -r "from '@repo/ui'" apps/ packages/ --include="*.ts" --include="*.tsx" -l
```

### Dependency Graph Visualization

```bash
# Generate HTML visualization
turbo run build --graph=dependency-graph.html

# Generate DOT format for custom rendering
turbo run build --graph=deps.dot

# Quick Mermaid diagram from package.json files
echo "graph TD"
for pkg in packages/*/package.json apps/*/package.json; do
  name=$(jq -r '.name' "$pkg")
  jq -r '.dependencies // {} | keys[] | select(startswith("@repo/"))' "$pkg" | while read dep; do
    echo "  $name --> $dep"
  done
done
```

## Remote Caching

### Turborepo Remote Cache (Vercel)

```bash
# Login to Vercel (one-time)
turbo login

# Link repo to Vercel team
turbo link

# CI: set environment variables
# TURBO_TOKEN=<vercel-token>
# TURBO_TEAM=<team-slug>

# Verify remote cache works
turbo run build --summarize
# Look for "Remote cache: hit" entries
```

### Self-Hosted Remote Cache

```bash
# Using ducktape/turborepo-remote-cache
docker run -p 3000:3000 \
  -e STORAGE_PROVIDER=local \
  -e STORAGE_PATH=/cache \
  ducktape/turborepo-remote-cache

# Configure turbo to use it
# turbo.json:
# { "remoteCache": { "apiUrl": "http://cache-server:3000" } }
```

## CI/CD with Affected Packages Only

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # needed for --filter comparisons

      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - run: pnpm install --frozen-lockfile

      # Only lint/test/build affected packages
      - run: turbo run lint test build --filter='...[origin/main]'
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

## Publishing with Changesets

### Setup

```bash
# Install changesets
pnpm add -D -w @changesets/cli @changesets/changelog-github

# Initialize
pnpm changeset init
```

### .changeset/config.json

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": ["@changesets/changelog-github", { "repo": "org/repo" }],
  "commit": false,
  "fixed": [],
  "linked": [["@repo/ui", "@repo/utils"]],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch"
}
```

### Publishing Workflow

```bash
# 1. Developer adds a changeset for their changes
pnpm changeset
# Interactive: select packages, bump type (patch/minor/major), summary

# 2. Before release: consume changesets and bump versions
pnpm changeset version
# Updates package.json versions and CHANGELOG.md files

# 3. Publish to npm
pnpm changeset publish
# Replaces workspace:* with real versions and publishes
```

## Migration: Multi-Repo to Monorepo

```bash
# 1. Preserve git history using filter-repo
# In each source repo:
git filter-repo --to-subdirectory-filter packages/ui
git filter-repo --to-subdirectory-filter apps/api

# 2. Create monorepo and merge histories
mkdir monorepo && cd monorepo && git init
git remote add ui ../old-ui-repo
git fetch ui --no-tags
git merge ui/main --allow-unrelated-histories

git remote add api ../old-api-repo
git fetch api --no-tags
git merge api/main --allow-unrelated-histories

# 3. Set up workspace configuration
# Add pnpm-workspace.yaml, turbo.json, root package.json

# 4. Update internal imports
# Change "ui-package" imports to "@repo/ui"
# Change npm versions to "workspace:*"

# 5. Verify
pnpm install
turbo run build test
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Running `turbo run build` without `--filter` on every PR | Always use `--filter='...[origin/main]'` in CI |
| `workspace:*` breaks npm publish | Use `pnpm changeset publish` which replaces automatically |
| All packages rebuild when unrelated file changes | Tune `inputs` in turbo.json to exclude docs, config files |
| Shared tsconfig breaks type-checks across packages | Each package extends root but overrides `rootDir`/`outDir` |
| Git history lost during migration | Use `git filter-repo --to-subdirectory-filter` before merging |
| Remote cache misses in CI | Verify TURBO_TOKEN and TURBO_TEAM; check with `--summarize` |
| Import cycles between packages | Use `madge --circular` to detect; refactor shared code to a new package |

## Best Practices

1. **Root package.json has no runtime dependencies** — only devDependencies and scripts
2. **Always scope commands with --filter in CI** — running everything defeats the monorepo purpose
3. **Remote cache is not optional** — without it, monorepo CI is slower than multi-repo
4. **Shared configs extend from root** — tsconfig.base.json, eslint.base.js, vitest shared config
5. **`packages/types` is pure TypeScript** — no runtime code, no dependencies, fastest to build
6. **Changesets over manual versioning** — never hand-edit package.json versions in a monorepo
7. **Impact analysis before merging shared package changes** — check affected packages, communicate blast radius
8. **Keep workspace:* for internal deps** — real version ranges are for external npm packages only

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `turbo run build` rebuilds everything despite no changes | Inputs glob is too broad or `globalDependencies` includes volatile files | Narrow `inputs` in turbo.json; exclude `.env`, docs, and test fixtures from build inputs |
| `ERR_PNPM_PEER_DEP_ISSUES` on install | Peer dependency mismatches across workspace packages | Add `peerDependencyRules.ignoreMissing` or `peerDependencyRules.allowAny` in root `.npmrc` or `package.json` |
| Remote cache reports 0% hit rate in CI | TURBO_TOKEN or TURBO_TEAM not set, or `inputs`/`outputs` changed between runs | Verify env vars with `turbo run build --summarize`; ensure inputs/outputs are stable across branches |
| `workspace:*` version appears in published package | Published with `npm publish` or `pnpm publish` instead of Changesets | Always use `pnpm changeset publish` which replaces `workspace:*` with resolved versions automatically |
| Circular dependency detected between packages | Two packages import from each other directly | Run `madge --circular` to identify the cycle; extract shared code into a new leaf package with no internal deps |
| TypeScript `Cannot find module '@repo/ui'` in IDE | IDE TypeScript server not resolving workspace paths | Add `paths` mapping in root `tsconfig.json` or use TypeScript project references; restart TS server after changes |
| CI takes longer after monorepo migration than multi-repo | Missing remote cache, no `--filter`, or `fetch-depth: 1` preventing git comparisons | Enable remote caching, use `--filter='...[origin/main]'`, and set `fetch-depth: 0` in checkout action |

## Success Criteria

- **Build time reduction**: CI pipeline completes affected-only builds in under 50% of full-build time within 2 weeks of adoption
- **Cache hit rate**: Remote cache achieves 70%+ hit rate on PR builds after initial warm-up period
- **Impact visibility**: Every PR includes an affected-packages summary showing blast radius of changes
- **Zero full rebuilds in CI**: No CI workflow runs all packages unconditionally; every pipeline uses `--filter` or equivalent
- **Publishing reliability**: Changesets workflow produces correct versions and changelogs with zero manual `package.json` edits per release cycle
- **Migration completeness**: Multi-repo to monorepo migration preserves 100% of git history for all migrated packages
- **Developer onboarding**: New team members can run, build, and test any package locally within 15 minutes using documented workspace commands

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
