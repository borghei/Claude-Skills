# Pipeline Templates, Stack Detection, Caching & Deployment Strategies

Read this when generating a pipeline: detecting the stack, picking GitHub Actions or GitLab CI templates, configuring caching/matrix/path-filtering, or choosing a deployment strategy.

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
  NODE_VERSION: '24'
  PNPM_VERSION: '9'

jobs:
  lint-and-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
      - uses: actions/setup-node@v7
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
      - uses: actions/checkout@v7
      - uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
      - uses: actions/setup-node@v7
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
      - uses: actions/checkout@v7
      - uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}
      - uses: actions/setup-node@v7
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - uses: actions/upload-artifact@v7
        with:
          name: build-output
          path: .next/
          retention-days: 1

  security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v7
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
      - uses: actions/checkout@v7
      - uses: actions/download-artifact@v8
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
      - uses: actions/checkout@v7
      - uses: actions/download-artifact@v8
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
      - uses: actions/checkout@v7
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
      - uses: actions/checkout@v7
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
      - uses: actions/checkout@v7
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
  NODE_VERSION: '24'

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
