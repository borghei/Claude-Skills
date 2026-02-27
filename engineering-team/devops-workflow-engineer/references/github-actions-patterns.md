# GitHub Actions Patterns

30+ proven patterns for production GitHub Actions workflows. Each pattern includes a working example and guidance on when to apply it.

---

## Table of Contents

1. [Trigger Patterns](#trigger-patterns)
2. [Job Structure Patterns](#job-structure-patterns)
3. [Matrix Patterns](#matrix-patterns)
4. [Caching Patterns](#caching-patterns)
5. [Artifact Patterns](#artifact-patterns)
6. [Security Patterns](#security-patterns)
7. [Reusable Workflow Patterns](#reusable-workflow-patterns)
8. [Composite Action Patterns](#composite-action-patterns)
9. [Environment Patterns](#environment-patterns)
10. [Advanced Patterns](#advanced-patterns)

---

## Trigger Patterns

### Pattern 1: Path-Filtered Push

Run the workflow only when relevant files change.

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'Dockerfile'
      - 'requirements*.txt'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

**When to use:** Reduce unnecessary CI runs on documentation-only or config-only changes.

### Pattern 2: Manual Dispatch with Inputs

Allow manual triggering with parameters.

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [dev, staging, production]
      dry_run:
        description: 'Dry run (no actual deploy)'
        required: false
        type: boolean
        default: true
      version:
        description: 'Version to deploy (leave empty for latest)'
        required: false
        type: string
```

**When to use:** On-demand deployments, maintenance tasks, or any workflow that needs human-supplied parameters.

### Pattern 3: Scheduled with Conditional Skip

Run on schedule but skip if there are no new changes.

```yaml
on:
  schedule:
    - cron: '0 6 * * 1-5'  # Weekdays at 6 AM UTC

jobs:
  check:
    runs-on: ubuntu-latest
    outputs:
      should_run: ${{ steps.check.outputs.should_run }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      - id: check
        run: |
          if git diff --quiet HEAD~1; then
            echo "should_run=false" >> "$GITHUB_OUTPUT"
          else
            echo "should_run=true" >> "$GITHUB_OUTPUT"
          fi

  build:
    needs: check
    if: needs.check.outputs.should_run == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building..."
```

**When to use:** Nightly dependency checks or security scans that should skip if nothing changed.

### Pattern 4: PR Target Branch Filter

Run different checks depending on the target branch of a PR.

```yaml
on:
  pull_request:
    branches:
      - main
      - 'release/**'

jobs:
  basic-checks:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Run on all PRs"

  release-checks:
    if: startsWith(github.base_ref, 'release/')
    runs-on: ubuntu-latest
    steps:
      - run: echo "Extra checks for release branches"
```

**When to use:** Enforce stricter validation for release branch PRs.

### Pattern 5: Multi-Event Trigger with Conditional Logic

Handle multiple triggers with event-specific behavior.

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build

      - name: Publish (release only)
        if: github.event_name == 'release'
        run: make publish
```

---

## Job Structure Patterns

### Pattern 6: Fan-Out / Fan-In

Run independent checks in parallel, then merge results.

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make security-scan

  gate:
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    steps:
      - run: echo "All checks passed"
```

**When to use:** Always. This is the default pattern for CI pipelines.

### Pattern 7: Conditional Job Execution

Skip jobs based on commit message or labels.

```yaml
jobs:
  test:
    if: "!contains(github.event.head_commit.message, '[skip ci]')"
    runs-on: ubuntu-latest
    steps:
      - run: make test

  deploy:
    if: contains(github.event.pull_request.labels.*.name, 'deploy-preview')
    runs-on: ubuntu-latest
    steps:
      - run: make deploy-preview
```

### Pattern 8: Job Output Passing

Pass data from one job to another.

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
      sha_short: ${{ steps.sha.outputs.sha_short }}
    steps:
      - uses: actions/checkout@v4
      - id: version
        run: echo "version=$(cat VERSION)" >> "$GITHUB_OUTPUT"
      - id: sha
        run: echo "sha_short=$(git rev-parse --short HEAD)" >> "$GITHUB_OUTPUT"

  build:
    needs: prepare
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building version ${{ needs.prepare.outputs.version }}"
```

### Pattern 9: Timeout and Retry

Protect against hung processes and handle transient failures.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Run flaky integration test (with retry)
        uses: nick-fields/retry@v3
        with:
          timeout_minutes: 5
          max_attempts: 3
          command: make integration-test
```

---

## Matrix Patterns

### Pattern 10: Basic Cross-Platform Matrix

Test across operating systems and language versions.

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pytest
```

### Pattern 11: Matrix with Include/Exclude

Fine-tune matrix combinations.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    node: [18, 20, 22]
    exclude:
      - os: macos-latest
        node: 18
    include:
      - os: ubuntu-latest
        node: 22
        coverage: true
```

**When to use:** Skip combinations that are not supported or add extra configuration to specific combinations.

### Pattern 12: Dynamic Matrix from JSON

Generate matrix values dynamically.

```yaml
jobs:
  generate-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - id: set
        run: |
          # Read from file, API, or compute dynamically
          MATRIX=$(python generate_matrix.py)
          echo "matrix=$MATRIX" >> "$GITHUB_OUTPUT"

  build:
    needs: generate-matrix
    strategy:
      matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.runner }}
    steps:
      - run: echo "Building ${{ matrix.name }}"
```

### Pattern 13: Matrix with Shared Setup

Factor out common setup into a composite action or reusable step.

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-project
      - name: Run test shard
        run: pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

---

## Caching Patterns

### Pattern 14: Language-Native Cache

Use built-in cache support in setup actions.

```yaml
# Python
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip

# Node.js
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm

# Go
- uses: actions/setup-go@v5
  with:
    go-version: '1.22'
    cache: true
```

### Pattern 15: Multi-Path Cache

Cache multiple directories with a composite key.

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.local/share/virtualenvs
      .mypy_cache
      .pytest_cache
    key: ${{ runner.os }}-full-${{ hashFiles('**/requirements*.txt', 'setup.cfg') }}
    restore-keys: |
      ${{ runner.os }}-full-
      ${{ runner.os }}-
```

### Pattern 16: Docker Layer Cache with BuildKit

Cache Docker build layers using GitHub Actions cache backend.

```yaml
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Pattern 17: Turbo/Nx Build Cache

Cache build outputs for monorepo build systems.

```yaml
- uses: actions/cache@v4
  with:
    path: node_modules/.cache/turbo
    key: turbo-${{ runner.os }}-${{ hashFiles('**/turbo.json', '**/package-lock.json') }}
    restore-keys: turbo-${{ runner.os }}-
```

---

## Artifact Patterns

### Pattern 18: Build Once, Deploy Everywhere

Build an artifact in one job, use it across deployment jobs.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 1

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - run: ./deploy.sh staging dist/

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - run: ./deploy.sh production dist/
```

### Pattern 19: Test Report Artifacts

Aggregate test results across matrix jobs.

```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results-${{ matrix.os }}-${{ matrix.version }}
    path: |
      **/junit-*.xml
      **/coverage-*.xml
    retention-days: 7
```

---

## Security Patterns

### Pattern 20: OIDC Authentication (AWS)

Use short-lived tokens instead of stored credentials.

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions
      aws-region: us-east-1
```

### Pattern 21: OIDC Authentication (GCP)

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: projects/123456/locations/global/workloadIdentityPools/github/providers/my-repo
      service_account: github-actions@my-project.iam.gserviceaccount.com
```

### Pattern 22: Minimal Permissions

Always declare the minimum permissions needed.

```yaml
# Top-level: restrict all
permissions:
  contents: read

jobs:
  deploy:
    permissions:
      contents: read
      packages: write      # Only this job needs package write
      id-token: write      # Only this job needs OIDC
```

### Pattern 23: Secret Masking for Dynamic Values

Mask dynamically generated sensitive values.

```yaml
steps:
  - name: Generate token
    id: token
    run: |
      TOKEN=$(curl -s https://auth.example.com/token)
      echo "::add-mask::$TOKEN"
      echo "token=$TOKEN" >> "$GITHUB_OUTPUT"
```

### Pattern 24: Dependency Review on PRs

Block PRs that introduce vulnerable dependencies.

```yaml
on:
  pull_request:

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high
          deny-licenses: GPL-3.0, AGPL-3.0
```

---

## Reusable Workflow Patterns

### Pattern 25: Parameterized Reusable Workflow

Define a workflow that can be called with different parameters.

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: '3.12'
      test-command:
        type: string
        default: 'pytest'
    secrets:
      CODECOV_TOKEN:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
      - run: pip install -r requirements.txt
      - run: ${{ inputs.test-command }}
```

### Pattern 26: Chained Reusable Workflows

Call reusable workflows in sequence.

```yaml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.12'

  build:
    needs: test
    uses: ./.github/workflows/reusable-build.yml
    with:
      push_image: true
    secrets: inherit

  deploy:
    needs: build
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
    secrets: inherit
```

### Pattern 27: Cross-Repository Reusable Workflow

Call a workflow from another repository.

```yaml
jobs:
  deploy:
    uses: my-org/shared-workflows/.github/workflows/deploy.yml@v2
    with:
      environment: production
    secrets:
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

---

## Composite Action Patterns

### Pattern 28: Project Setup Composite

Bundle common setup steps.

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Install all dependencies and configure environment

inputs:
  python-version:
    default: '3.12'

runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
    - run: pip install -r requirements.txt -r requirements-dev.txt
      shell: bash
    - run: pre-commit install
      shell: bash
```

### Pattern 29: Deploy Composite with Outputs

A composite action that deploys and returns the deployment URL.

```yaml
# .github/actions/deploy/action.yml
name: Deploy
description: Deploy to environment and return URL

inputs:
  environment:
    required: true
  image_tag:
    required: true

outputs:
  url:
    description: Deployment URL
    value: ${{ steps.deploy.outputs.url }}

runs:
  using: composite
  steps:
    - id: deploy
      run: |
        URL=$(./deploy.sh ${{ inputs.environment }} ${{ inputs.image_tag }})
        echo "url=$URL" >> "$GITHUB_OUTPUT"
      shell: bash
```

---

## Environment Patterns

### Pattern 30: Environment Protection Rules

Use GitHub environments with required reviewers and wait timers.

```yaml
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://myapp.example.com
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh production
```

Configure in **Settings > Environments > production:**
- Required reviewers: team leads
- Wait timer: 5 minutes
- Deployment branches: only `main`

### Pattern 31: Environment-Specific Secrets and Variables

Use environment-scoped configuration.

```yaml
jobs:
  deploy:
    environment: ${{ inputs.environment }}
    runs-on: ubuntu-latest
    steps:
      - run: |
          curl -X POST ${{ vars.DEPLOY_URL }} \
            -H "Authorization: Bearer ${{ secrets.DEPLOY_TOKEN }}" \
            -d '{"version": "${{ github.sha }}"}'
```

Each environment (dev, staging, production) has its own `DEPLOY_URL` variable and `DEPLOY_TOKEN` secret.

---

## Advanced Patterns

### Pattern 32: Concurrency Groups

Prevent concurrent runs and cancel outdated ones.

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
```

For production deployments, do NOT cancel in progress:

```yaml
concurrency:
  group: deploy-production
  cancel-in-progress: false
```

### Pattern 33: Step Summary

Write rich markdown summaries visible in the Actions UI.

```yaml
- name: Generate summary
  run: |
    echo "## Build Results" >> "$GITHUB_STEP_SUMMARY"
    echo "| Metric | Value |" >> "$GITHUB_STEP_SUMMARY"
    echo "|--------|-------|" >> "$GITHUB_STEP_SUMMARY"
    echo "| Tests | 142 passed |" >> "$GITHUB_STEP_SUMMARY"
    echo "| Coverage | 87.3% |" >> "$GITHUB_STEP_SUMMARY"
    echo "| Build time | 3m 12s |" >> "$GITHUB_STEP_SUMMARY"
```

### Pattern 34: PR Comment with Results

Post CI results as a PR comment.

```yaml
- uses: marocchino/sticky-pull-request-comment@v2
  with:
    header: ci-results
    message: |
      ## CI Results
      - Tests: ${{ steps.test.outputs.result }}
      - Coverage: ${{ steps.coverage.outputs.percentage }}%
      - Build: ${{ steps.build.outputs.status }}
```

### Pattern 35: Monorepo Path-Based Jobs

Run only the jobs relevant to changed packages.

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.filter.outputs.frontend }}
      backend: ${{ steps.filter.outputs.backend }}
      infra: ${{ steps.filter.outputs.infra }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            frontend:
              - 'packages/frontend/**'
            backend:
              - 'packages/backend/**'
            infra:
              - 'terraform/**'

  test-frontend:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: cd packages/frontend && npm test

  test-backend:
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: cd packages/backend && pytest
```

### Pattern 36: Automatic PR Labeling

Label PRs based on changed files.

```yaml
on:
  pull_request:

jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/labeler@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

With `.github/labeler.yml`:

```yaml
frontend:
  - changed-files:
    - any-glob-to-any-file: 'src/frontend/**'
backend:
  - changed-files:
    - any-glob-to-any-file: 'src/backend/**'
documentation:
  - changed-files:
    - any-glob-to-any-file: '**/*.md'
```

### Pattern 37: Release Drafter

Automatically draft release notes from PR titles.

```yaml
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
