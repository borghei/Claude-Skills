---
name: ci-cd-pipeline-builder
description: >
  Design and generate CI/CD pipelines from detected project stack signals.
  Covers GitHub Actions, GitLab CI, CircleCI, and Buildkite with caching, matrix
  builds, deployment strategies (blue-green, canary, rolling), environment
  gates, and security scanning. Use when bootstrapping CI, migrating pipelines,
  or optimizing build times.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: devops
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: github-actions, gitlab-ci, circleci, buildkite
---
# CI/CD Pipeline Builder

**Tier:** POWERFUL
**Category:** Engineering / DevOps
**Maintainer:** Claude Skills Team

## Overview

Generate production-grade CI/CD pipelines from detected project stack signals. Analyzes lockfiles, manifests, and scripts to produce optimized pipelines with proper caching, matrix strategies, security scanning, and deployment gates. Supports GitHub Actions, GitLab CI, CircleCI, and Buildkite with deployment strategies including blue-green, canary, and rolling updates.

## Keywords

CI/CD, GitHub Actions, GitLab CI, pipeline, deployment, caching, matrix builds, blue-green deployment, canary deployment, security scanning, SAST, container builds, environment gates

## Core Capabilities

### 1. Stack Detection
- Language/runtime detection from lockfiles and manifests
- Package manager inference from lock file format
- Build/test/lint command extraction from scripts
- Framework detection (Next.js, FastAPI, Go modules, etc.)
- Infrastructure detection (Docker, Kubernetes, Terraform)

### 2. Pipeline Generation
- Lint, test, build, deploy stages with correct dependencies
- Caching strategies matched to package manager
- Matrix builds for multi-version support
- Artifact passing between jobs
- Conditional execution (path filters, branch rules)

### 3. Deployment Strategies
- Blue-green with instant rollback
- Canary with percentage-based traffic shifting
- Rolling updates with health checks
- Feature flags integration
- Manual approval gates for production

### 4. Security Integration
- SAST scanning (CodeQL, Semgrep, Snyk)
- Dependency vulnerability scanning
- Container image scanning (Trivy, Grype)
- Secret scanning in CI
- SBOM generation

## When to Use

- Bootstrapping CI/CD for a new repository
- Migrating between CI platforms
- Optimizing slow or flaky pipelines
- Adding deployment stages to an existing CI-only pipeline
- Implementing security scanning in the pipeline
- Setting up multi-environment deployment (staging, production)

## Stack Detection Heuristics

```
File Found                    → Inference
─────────────────────────────────────────────────
package-lock.json             → Node.js + npm
pnpm-lock.yaml                → Node.js + pnpm
yarn.lock                     → Node.js + yarn
bun.lockb                     → Bun
requirements.txt / Pipfile    → Python + pip/pipenv
pyproject.toml + uv.lock      → Python + uv
poetry.lock                   → Python + poetry
go.mod                        → Go
Cargo.lock                    → Rust
Gemfile.lock                  → Ruby
composer.lock                 → PHP
next.config.*                 → Next.js (Node.js)
nuxt.config.*                 → Nuxt (Node.js)
Dockerfile                    → Container build needed
docker-compose.yml            → Multi-service setup
terraform/*.tf                → Infrastructure as Code
k8s/ or kubernetes/           → Kubernetes deployment
```

## GitHub Actions Pipeline Templates

### Node.js (pnpm + Vitest + Next.js)

```yaml
name: CI/CD

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  NODE_VERSION: '20'
  PNPM_VERSION: '9'

jobs:
  lint-and-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck

  test:
    runs-on: ubuntu-latest
    needs: lint-and-typecheck
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm test:ci
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: .next/
          retention-days: 1

  security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript-typescript
      - uses: github/codeql-action/analyze@v3

  deploy-staging:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.myapp.com
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: .next/
      - name: Deploy to staging
        run: |
          # Replace with your deployment command
          echo "Deploying to staging..."
        env:
          DEPLOY_TOKEN: ${{ secrets.STAGING_DEPLOY_TOKEN }}

  deploy-production:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: .next/
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
        env:
          DEPLOY_TOKEN: ${{ secrets.PROD_DEPLOY_TOKEN }}
```

### Python (uv + pytest + FastAPI)

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src/

  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync --frozen
      - run: uv run pytest --cov --cov-report=xml -v
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb
      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          file: coverage.xml

  build-container:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  container-scan:
    needs: build-container
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
```

## Deployment Strategy Decision Framework

```
How critical is zero-downtime?
│
├─ Critical (payment processing, real-time systems)
│  └─ BLUE-GREEN DEPLOYMENT
│     Pro: Instant rollback, zero-downtime guaranteed
│     Con: Requires 2x infrastructure during deployment
│
├─ Important but can tolerate brief errors
│  ├─ Need to validate with real traffic first?
│  │  └─ CANARY DEPLOYMENT
│  │     Pro: Test with small % of traffic before full rollout
│  │     Con: Complex routing, need observability for canary metrics
│  │
│  └─ Standard web app with health checks
│     └─ ROLLING UPDATE
│        Pro: Simple, built into K8s/ECS, gradual rollout
│        Con: Both versions serve traffic during rollout
│
└─ Development/staging environment
   └─ RECREATE (stop old, start new)
      Pro: Simplest, cleanest
      Con: Brief downtime during deployment
```

## Caching Strategy Reference

| Package Manager | Cache Path | Key Pattern |
|----------------|-----------|-------------|
| npm | `~/.npm` | `${{ runner.os }}-npm-${{ hashFiles('package-lock.json') }}` |
| pnpm | Detected by setup-node | `cache: 'pnpm'` in setup-node |
| yarn | `~/.cache/yarn` | `${{ runner.os }}-yarn-${{ hashFiles('yarn.lock') }}` |
| pip | `~/.cache/pip` | `${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}` |
| uv | `~/.cache/uv` | Handled by setup-uv |
| Go | `~/go/pkg/mod` | `${{ runner.os }}-go-${{ hashFiles('go.sum') }}` |
| Cargo | `~/.cargo/registry` | `${{ runner.os }}-cargo-${{ hashFiles('Cargo.lock') }}` |
| Docker | GHA cache | `cache-from: type=gha` in build-push-action |

## Pipeline Optimization Techniques

### 1. Path Filtering (Skip Unnecessary Runs)
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'package.json'
      - 'pnpm-lock.yaml'
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/ISSUE_TEMPLATE/**'
```

### 2. Job Dependency Graph
```
lint ──────┐
           ├──→ test ──→ build ──→ deploy-staging ──→ deploy-production
typecheck ─┘                │
                            └──→ security-scan
```

### 3. Matrix Strategy with Fail-Fast
```yaml
strategy:
  fail-fast: true  # cancel all if one fails
  matrix:
    node-version: [18, 20, 22]
    os: [ubuntu-latest]
    include:
      - node-version: 20
        os: macos-latest  # test one combo on macOS
```

## GitLab CI Equivalent

```yaml
stages:
  - validate
  - test
  - build
  - deploy

variables:
  NODE_VERSION: "20"

.node-setup: &node-setup
  image: node:${NODE_VERSION}
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
      - .pnpm-store/
  before_script:
    - corepack enable
    - pnpm install --frozen-lockfile

lint:
  stage: validate
  <<: *node-setup
  script:
    - pnpm lint
    - pnpm typecheck

test:
  stage: test
  <<: *node-setup
  services:
    - postgres:16
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
    DATABASE_URL: postgresql://test:test@postgres:5432/testdb
  script:
    - pnpm test:ci
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'

build:
  stage: build
  <<: *node-setup
  script:
    - pnpm build
  artifacts:
    paths:
      - .next/
    expire_in: 1 hour

deploy_staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.myapp.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  script:
    - echo "Deploy to staging"

deploy_production:
  stage: deploy
  environment:
    name: production
    url: https://myapp.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
  needs: [deploy_staging]
  script:
    - echo "Deploy to production"
```

## Validation Checklist

Before merging a generated pipeline:

1. YAML parses without syntax errors
2. All referenced commands exist in the repository (`test`, `lint`, `build`)
3. Cache strategy matches the detected package manager
4. Required secrets are documented (not embedded in YAML)
5. Branch protection rules match organization policy
6. Deployment jobs are gated by protected environments
7. Security scanning runs on the appropriate code paths
8. Artifact retention is set (do not keep build artifacts indefinitely)
9. Concurrency group prevents duplicate runs on the same branch
10. Path filters exclude documentation-only changes from full CI runs

## Common Pitfalls

- **Copying pipelines between projects** without adapting to the actual stack
- **No concurrency control** leading to redundant parallel runs on rapid pushes
- **Missing cache keys** causing cache misses on every run (slow builds)
- **Running full matrix on every PR** when only main needs multi-version testing
- **Hardcoding secrets in YAML** instead of using CI secret stores
- **No path filtering** so documentation changes trigger full build+test+deploy
- **Deploy jobs without environment gates** allowing accidental production deployments
- **No artifact retention policy** causing storage costs to grow indefinitely

## Best Practices

1. **Detect stack first, then generate pipeline** — never guess at build commands
2. **Keep the generated baseline under version control** and customize incrementally
3. **One optimization at a time** — add caching, then matrix, then split jobs
4. **Require green CI before any deployment job** can execute
5. **Use protected environments** for production credentials and manual approval gates
6. **Track pipeline duration and flakiness** as first-class engineering metrics
7. **Separate deploy jobs from CI jobs** to keep feedback fast for developers
8. **Regenerate the pipeline when the stack changes significantly** (new language, new framework)

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Pipeline YAML fails validation | Indentation errors or invalid key names | Run `yamllint` locally before committing; use the CI platform's built-in linter (e.g., `act` for GitHub Actions, `gitlab-ci-lint` for GitLab) |
| Cache misses on every run | Cache key does not include the correct lockfile hash | Verify the `hashFiles()` path matches the actual lockfile location; check the Caching Strategy Reference table above |
| Matrix build times explode | Running full OS + version matrix on every PR | Restrict the full matrix to `main` branch pushes; run a single representative version on PRs |
| Deployment job triggers on PRs | Missing branch/event guard on deploy jobs | Add `if: github.ref == 'refs/heads/main' && github.event_name == 'push'` or equivalent platform condition |
| Service containers fail to start | Health check misconfigured or image not found | Pin the service image to a specific major version; confirm health check command exists in the image |
| Secret not available in workflow | Secret not added to the repository or environment settings | Add the secret via the CI platform's secrets UI; ensure the job references the correct `environment` name |
| Build artifact missing in deploy job | Artifact name mismatch or retention expired | Ensure `upload-artifact` and `download-artifact` use the same `name` value; set `retention-days` high enough to survive the full pipeline |

## Success Criteria

- Pipeline generates valid YAML that passes platform-native linting on first attempt for detected stacks
- Build times stay under 10 minutes for lint + test + build stages combined (excluding deploy)
- Cache hit rate exceeds 90% on repeat runs with unchanged lockfiles
- Security scanning (SAST + dependency + container) executes on every push to `main` without manual triggers
- Deployment to staging is fully automated; production requires exactly one manual approval gate
- Pipeline flakiness rate remains below 2% over a rolling 30-day window
- Zero hardcoded secrets in generated pipeline YAML; all sensitive values reference platform secret stores

## Scope & Limitations

**This skill covers:**
- Generating CI/CD pipelines for GitHub Actions, GitLab CI, CircleCI, and Buildkite
- Stack detection from lockfiles, manifests, Dockerfiles, and infrastructure-as-code definitions
- Deployment strategy selection (blue-green, canary, rolling, recreate) with decision framework
- Pipeline optimization including caching, matrix builds, path filtering, and concurrency control

**This skill does NOT cover:**
- Runtime infrastructure provisioning or cloud resource management (see `engineering/saas-scaffolder`)
- Application-level security hardening beyond CI-integrated scanning (see `engineering/skill-security-auditor`)
- Monitoring, alerting, and observability configuration after deployment (see `engineering/observability-designer`)
- Database migration orchestration during deployments (see `engineering/migration-architect`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/dependency-auditor` | Feeds vulnerability scan results into pipeline security gates | Auditor findings trigger pipeline failure or warning annotations |
| `engineering/release-manager` | Coordinates versioning and changelog with deploy stages | Release tags drive conditional deployment job execution |
| `engineering/observability-designer` | Post-deploy health checks and alerting complement pipeline gates | Pipeline triggers smoke tests; observability confirms deployment health |
| `engineering/env-secrets-manager` | Manages secrets referenced by pipeline environment variables | Secret rotation policies feed into pipeline secret store configuration |
| `engineering/migration-architect` | Database migrations run as a pre-deploy step in the pipeline | Migration status gates the application deployment job |
| `engineering/runbook-generator` | Generates rollback runbooks aligned with deployment strategy | Pipeline failure triggers link to the relevant rollback runbook |
