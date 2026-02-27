---
name: devops-workflow-engineer
description: >
  Guides teams through designing, implementing, and optimizing CI/CD pipelines,
  GitHub Actions workflows, deployment automation, and agentic workflow patterns.
  Provides production-ready templates, cost optimization strategies, quality gates,
  and multi-environment deployment planning for modern DevOps practices.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: devops
  tools:
    - workflow_generator.py
    - pipeline_analyzer.py
    - deployment_planner.py
  references:
    - github-actions-patterns.md
    - deployment-strategies.md
    - agentic-workflows-guide.md
  assets:
    - ci-template.yml
    - cd-template.yml
---

# DevOps Workflow Engineer

Design, implement, and optimize CI/CD pipelines, GitHub Actions workflows, and deployment automation for production systems.

## Keywords

`ci/cd` `github-actions` `deployment` `automation` `pipelines` `devops` `continuous-integration` `continuous-delivery` `blue-green` `canary` `rolling-deploy` `feature-flags` `matrix-builds` `caching` `secrets-management` `reusable-workflows` `composite-actions` `agentic-workflows` `quality-gates` `security-scanning` `cost-optimization` `multi-environment` `infrastructure-as-code` `gitops`

## Quick Start

### 1. Generate a CI Workflow

```bash
python scripts/workflow_generator.py --type ci --language python --test-framework pytest
```

### 2. Analyze Existing Pipelines

```bash
python scripts/pipeline_analyzer.py path/to/.github/workflows/
```

### 3. Plan a Deployment Strategy

```bash
python scripts/deployment_planner.py --type webapp --environments dev,staging,prod
```

### 4. Use Production Templates

Copy templates from `assets/` into your `.github/workflows/` directory and customize.

---

## Core Workflows

### Workflow 1: GitHub Actions Design

**Goal:** Design maintainable, efficient GitHub Actions workflows from scratch.

**Process:**

1. **Identify triggers** -- Determine which events should start the pipeline (push, PR, schedule, manual dispatch).
2. **Map job dependencies** -- Draw a DAG of jobs; identify which can run in parallel vs. which must be sequential.
3. **Select runners** -- Choose between GitHub-hosted (ubuntu-latest, macos-latest, windows-latest) and self-hosted runners based on cost, performance, and security needs.
4. **Structure the workflow file** -- Use clear naming, concurrency groups, and permissions scoping.
5. **Add quality gates** -- Each job should have a clear pass/fail criterion.

**Design Principles:**

- **Fail fast:** Put the cheapest, fastest checks first (linting before integration tests).
- **Minimize blast radius:** Use `permissions` to grant least-privilege access.
- **Idempotency:** Every workflow run should produce the same result for the same inputs.
- **Observability:** Add step summaries and annotations for quick debugging.

**Trigger Selection Matrix:**

| Trigger | Use Case | Example |
|---------|----------|---------|
| `push` | Run on every commit to specific branches | `push: branches: [main, dev]` |
| `pull_request` | Validate PRs before merge | `pull_request: branches: [main]` |
| `schedule` | Nightly builds, dependency checks | `schedule: - cron: '0 2 * * *'` |
| `workflow_dispatch` | Manual deployments, ad-hoc tasks | Add `inputs:` for parameters |
| `release` | Publish artifacts on new release | `release: types: [published]` |
| `workflow_call` | Reusable workflow invocation | Define `inputs:` and `secrets:` |

### Workflow 2: CI Pipeline Creation

**Goal:** Build a continuous integration pipeline that catches issues early and runs efficiently.

**Process:**

1. **Lint and format check** (fastest gate, ~30s)
2. **Unit tests** (medium speed, ~2-5m)
3. **Build verification** (compile/bundle, ~3-8m)
4. **Integration tests** (slower, ~5-15m, run in parallel with build)
5. **Security scanning** (SAST, dependency audit, ~2-5m)
6. **Report aggregation** (combine results, post summaries)

**Optimized CI Structure:**

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linter
        run: make lint

  test:
    needs: lint
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: pip install -r requirements.txt
      - run: pytest --junitxml=results.xml
      - uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.python-version }}
          path: results.xml

  security:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency audit
        run: pip-audit -r requirements.txt
```

**Key CI Metrics:**

| Metric | Target | Action if Exceeded |
|--------|--------|--------------------|
| Total CI time | < 10 minutes | Parallelize jobs, add caching |
| Lint step | < 1 minute | Use pre-commit locally |
| Unit tests | < 5 minutes | Split test suites, use matrix |
| Flaky test rate | < 1% | Quarantine flaky tests |
| Cache hit rate | > 80% | Review cache keys |

### Workflow 3: CD Pipeline Creation

**Goal:** Automate delivery from merged code to running production systems.

**Process:**

1. **Build artifacts** -- Create deployable packages (Docker images, bundles, binaries).
2. **Publish artifacts** -- Push to registry (GHCR, ECR, Docker Hub, npm).
3. **Deploy to staging** -- Automatic deployment on merge to main.
4. **Run smoke tests** -- Validate the staging deployment with lightweight checks.
5. **Promote to production** -- Manual approval gate or automated canary.
6. **Post-deploy verification** -- Health checks, synthetic monitoring.

**Environment Promotion Flow:**

```
Build -> Dev (auto) -> Staging (auto) -> Production (manual approval)
                                              |
                                        Canary (10%) -> Full rollout
```

**CD Best Practices:**

- Always deploy the same artifact across environments (build once, deploy many).
- Use immutable deployments (never modify a running instance).
- Maintain rollback capability at every stage.
- Tag artifacts with the commit SHA for traceability.
- Use environment protection rules in GitHub for production gates.

### Workflow 4: Multi-Environment Deployment

**Goal:** Manage consistent deployments across dev, staging, and production.

**Environment Configuration Matrix:**

| Aspect | Dev | Staging | Production |
|--------|-----|---------|------------|
| Deploy trigger | Every push | Merge to main | Manual approval |
| Replicas | 1 | 2 | 3+ (auto-scaled) |
| Database | Shared test DB | Isolated clone | Production DB |
| Secrets source | Repository secrets | Environment secrets | Vault/OIDC |
| Monitoring | Basic logs | Full observability | Full + alerting |
| Rollback | Redeploy | Automated | Automated + page |

**Environment Variables Strategy:**

```yaml
env:
  REGISTRY: ghcr.io/${{ github.repository_owner }}

jobs:
  deploy:
    strategy:
      matrix:
        environment: [dev, staging, production]
    environment: ${{ matrix.environment }}
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          ./deploy.sh --env ${{ matrix.environment }}
```

### Workflow 5: Workflow Optimization

**Goal:** Reduce CI/CD execution time and cost while maintaining quality.

**Optimization Checklist:**

1. **Caching** -- Cache dependencies, build outputs, Docker layers.
2. **Parallelization** -- Run independent jobs concurrently.
3. **Conditional execution** -- Skip unchanged paths with `paths` filter or `dorny/paths-filter`.
4. **Artifact reuse** -- Build once, test/deploy the artifact everywhere.
5. **Runner sizing** -- Use larger runners for CPU-bound tasks; smaller for I/O-bound.
6. **Concurrency controls** -- Cancel in-progress runs for the same branch.

**Path-Based Filtering:**

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'requirements*.txt'
    paths-ignore:
      - 'docs/**'
      - '*.md'
```

**Concurrency Groups:**

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

---

## GitHub Actions Patterns

### Matrix Builds

Use matrices to test across multiple versions, OS, or configurations:

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node-version: [18, 20, 22]
    exclude:
      - os: windows-latest
        node-version: 18
    include:
      - os: ubuntu-latest
        node-version: 22
        experimental: true
```

**Dynamic Matrices** -- generate the matrix in a prior job:

```yaml
jobs:
  prepare:
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: echo "matrix=$(jq -c . matrix.json)" >> "$GITHUB_OUTPUT"

  build:
    needs: prepare
    strategy:
      matrix: ${{ fromJson(needs.prepare.outputs.matrix) }}
```

### Caching Strategies

**Dependency Caching:**

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.npm
      ~/.cargo/registry
    key: ${{ runner.os }}-deps-${{ hashFiles('**/requirements.txt', '**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

**Docker Layer Caching:**

```yaml
- uses: docker/build-push-action@v5
  with:
    context: .
    cache-from: type=gha
    cache-to: type=gha,mode=max
    push: true
    tags: ${{ env.IMAGE }}:${{ github.sha }}
```

### Artifacts

Upload and share artifacts between jobs:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 5

# In downstream job
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: dist/
```

### Secrets Management

**Hierarchy:** Organization > Repository > Environment secrets.

**Best Practices:**

- Never echo secrets; use `add-mask` for dynamic values.
- Prefer OIDC for cloud authentication (no long-lived credentials).
- Rotate secrets on a schedule; use expiration alerts.
- Use environment protection rules for production secrets.

**OIDC Example (AWS):**

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-actions
      aws-region: us-east-1
```

### Reusable Workflows

Define a workflow that other workflows can call:

```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image_tag:
        required: true
        type: string
    secrets:
      DEPLOY_KEY:
        required: true

jobs:
  deploy:
    environment: ${{ inputs.environment }}
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: ./deploy.sh ${{ inputs.environment }} ${{ inputs.image_tag }}
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

**Calling a reusable workflow:**

```yaml
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
      image_tag: ${{ github.sha }}
    secrets:
      DEPLOY_KEY: ${{ secrets.STAGING_DEPLOY_KEY }}
```

### Composite Actions

Bundle multiple steps into a reusable action:

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Install dependencies and configure the environment

inputs:
  node-version:
    description: Node.js version
    default: '20'

runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - run: npm ci
      shell: bash
    - run: npm run build
      shell: bash
```

---

## GitHub Agentic Workflows (2026)

GitHub's agentic workflow system enables AI-driven automation using markdown-based definitions.

### Markdown-Based Workflow Authoring

Agentic workflows are defined in `.github/agents/` as markdown files:

```markdown
---
name: code-review-agent
description: Automated code review with context-aware feedback
triggers:
  - pull_request
tools:
  - code-search
  - file-read
  - comment-create
permissions:
  pull-requests: write
  contents: read
safe-outputs: true
---

# Code Review Agent

Review pull requests for:
1. Code quality and adherence to project conventions
2. Security vulnerabilities
3. Performance regressions
4. Test coverage gaps

## Instructions
- Read the diff and related files for context
- Post inline comments for specific issues
- Summarize findings as a PR comment
```

### Safe-Outputs

The `safe-outputs: true` flag ensures that agent-generated outputs are:

- Clearly labeled as AI-generated.
- Not automatically merged or deployed without human review.
- Logged with full provenance for auditing.

### Tool Permissions

Agentic workflows declare which tools they can access:

| Tool | Capability | Permission Scope |
|------|-----------|-----------------|
| `code-search` | Search repository code | `contents: read` |
| `file-read` | Read file contents | `contents: read` |
| `file-write` | Modify files | `contents: write` |
| `comment-create` | Post PR/issue comments | `pull-requests: write` |
| `issue-create` | Create issues | `issues: write` |
| `workflow-trigger` | Trigger other workflows | `actions: write` |

### Continuous Automation Categories

| Category | Examples | Trigger Pattern |
|----------|----------|-----------------|
| Code Quality | Auto-review, style fixes | `pull_request` |
| Documentation | Doc generation, changelog | `push` to main |
| Security | Dependency alerts, secret detection | `schedule`, `push` |
| Release | Versioning, release notes | `release`, `workflow_dispatch` |
| Triage | Issue labeling, assignment | `issues`, `pull_request` |

---

## Quality Gates

### Linting

Enforce code style before any other check:

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Python lint
      run: |
        pip install ruff
        ruff check .
        ruff format --check .
    - name: YAML lint
      run: |
        pip install yamllint
        yamllint .github/workflows/
```

### Testing

Structure tests by speed tier:

| Tier | Type | Max Duration | Runs On |
|------|------|-------------|---------|
| 1 | Unit tests | 5 minutes | Every push |
| 2 | Integration tests | 15 minutes | Every PR |
| 3 | E2E tests | 30 minutes | Pre-deploy |
| 4 | Load tests | 60 minutes | Weekly schedule |

### Security Scanning

Integrate security at multiple levels:

```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: SAST - Static analysis
      uses: github/codeql-action/analyze@v3

    - name: Dependency audit
      run: |
        pip-audit -r requirements.txt
        npm audit --audit-level=high

    - name: Container scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.IMAGE }}:${{ github.sha }}
        severity: CRITICAL,HIGH
```

### Performance Benchmarks

Gate deployments on performance regression:

```yaml
benchmark:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run benchmarks
      run: python -m pytest benchmarks/ --benchmark-json=output.json
    - name: Compare with baseline
      run: python scripts/compare_benchmarks.py output.json baseline.json --threshold 10
```

---

## Deployment Strategies

### Blue-Green Deployment

Maintain two identical environments; switch traffic after verification.

**Flow:**

```
1. Deploy new version to "green" environment
2. Run health checks on green
3. Switch load balancer to green
4. Monitor for errors (5-15 minutes)
5. If healthy: decommission old "blue"
   If unhealthy: switch back to blue (instant rollback)
```

**Best for:** Zero-downtime deployments, applications needing instant rollback.

### Canary Deployment

Route a small percentage of traffic to the new version.

**Flow:**

```
1. Deploy canary (new version) alongside stable
2. Route 5% traffic to canary
3. Monitor error rates, latency, business metrics
4. If healthy: increase to 25% -> 50% -> 100%
   If unhealthy: route 100% back to stable
```

**Traffic Split Schedule:**

| Phase | Canary % | Duration | Gate |
|-------|---------|----------|------|
| 1 | 5% | 15 min | Error rate < 0.1% |
| 2 | 25% | 30 min | P99 latency < 200ms |
| 3 | 50% | 60 min | Business metrics stable |
| 4 | 100% | -- | Full promotion |

### Rolling Deployment

Update instances incrementally, maintaining availability.

**Best for:** Stateless services, Kubernetes deployments with multiple replicas.

```yaml
# Kubernetes rolling update
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
```

### Feature Flags

Decouple deployment from release using feature flags:

```python
# Feature flag check (simplified)
if feature_flags.is_enabled("new-checkout-flow", user_id=user.id):
    return new_checkout(request)
else:
    return legacy_checkout(request)
```

**Benefits:**

- Deploy code without exposing it to users.
- Gradual rollout by user segment (internal, beta, percentage).
- Instant kill switch without redeployment.
- A/B testing capability.

---

## Monitoring and Alerting Integration

### Deploy-Time Monitoring Checklist

After every deployment, verify:

1. **Health endpoints** respond with 200 status.
2. **Error rate** has not increased (compare 5-minute window pre/post).
3. **Latency** P50/P95/P99 within acceptable bounds.
4. **CPU/Memory** usage is not spiking.
5. **Business metrics** (conversion rate, API calls) are stable.

### Alert Configuration

```yaml
# Example alert rules (Prometheus-compatible)
groups:
  - name: deployment-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate exceeds 5% after deployment"

      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency exceeds 500ms"
```

### Deployment Annotations

Mark deployments in your monitoring system for correlation:

```bash
# Grafana annotation
curl -X POST "$GRAFANA_URL/api/annotations" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"Deploy $VERSION to $ENVIRONMENT\",
    \"tags\": [\"deployment\", \"$ENVIRONMENT\"]
  }"
```

---

## Cost Optimization for CI/CD

### Runner Cost Comparison

| Runner | vCPU | RAM | Cost/min | Best For |
|--------|------|-----|----------|----------|
| ubuntu-latest (2-core) | 2 | 7 GB | $0.008 | Standard tasks |
| ubuntu-latest (4-core) | 4 | 16 GB | $0.016 | Build-heavy tasks |
| ubuntu-latest (8-core) | 8 | 32 GB | $0.032 | Large compilations |
| ubuntu-latest (16-core) | 16 | 64 GB | $0.064 | Parallel test suites |
| Self-hosted | Variable | Variable | Infra cost | Specialized needs |

### Cost Reduction Strategies

1. **Path filters** -- Do not run full CI for docs-only changes.
2. **Concurrency cancellation** -- Cancel superseded runs.
3. **Cache aggressively** -- Save 30-60% of dependency install time.
4. **Right-size runners** -- Use larger runners only for jobs that benefit.
5. **Schedule expensive jobs** -- Run full matrix nightly, not on every push.
6. **Timeout limits** -- Prevent runaway jobs from burning minutes.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15  # Hard limit
```

### Monthly Budget Estimation

```
Formula:
  Monthly minutes = (runs/day) x (avg minutes/run) x 30
  Monthly cost = Monthly minutes x (cost/minute)

Example:
  50 pushes/day x 8 min/run x 30 days = 12,000 minutes
  12,000 x $0.008 = $96/month (2-core Linux)
```

**Use `scripts/pipeline_analyzer.py`** to estimate costs for your specific workflows.

---

## Tools Reference

### workflow_generator.py

Generate GitHub Actions workflow YAML from templates.

```bash
# Generate CI workflow for Python + pytest
python scripts/workflow_generator.py --type ci --language python --test-framework pytest

# Generate CD workflow for Node.js webapp
python scripts/workflow_generator.py --type cd --language node --deploy-target kubernetes

# Generate security scan workflow
python scripts/workflow_generator.py --type security-scan --language python

# Generate release workflow
python scripts/workflow_generator.py --type release --language python

# Generate docs-check workflow
python scripts/workflow_generator.py --type docs-check

# Output as JSON
python scripts/workflow_generator.py --type ci --language python --format json
```

### pipeline_analyzer.py

Analyze existing workflows for optimization opportunities.

```bash
# Analyze all workflows in a directory
python scripts/pipeline_analyzer.py path/to/.github/workflows/

# Analyze a single workflow file
python scripts/pipeline_analyzer.py path/to/workflow.yml

# Output as JSON
python scripts/pipeline_analyzer.py path/to/.github/workflows/ --format json
```

### deployment_planner.py

Generate deployment plans based on project type.

```bash
# Plan for a web application
python scripts/deployment_planner.py --type webapp --environments dev,staging,prod

# Plan for a microservice
python scripts/deployment_planner.py --type microservice --environments dev,staging,prod --strategy canary

# Plan for a library/package
python scripts/deployment_planner.py --type library --environments staging,prod

# Output as JSON
python scripts/deployment_planner.py --type webapp --environments dev,staging,prod --format json
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| Monolithic workflow | Single 45-minute workflow | Split into parallel jobs |
| No caching | Reinstall deps every run | Cache dependencies and build outputs |
| Secrets in logs | Leaked credentials | Use `add-mask`, avoid `echo` |
| No timeout | Stuck jobs burn budget | Set `timeout-minutes` on every job |
| Always full matrix | 30-minute matrix on every push | Full matrix nightly; reduced on push |
| Manual deployments | Error-prone, slow | Automate with approval gates |
| No rollback plan | Stuck with broken deploy | Automate rollback in CD pipeline |
| Shared mutable state | Flaky tests, race conditions | Isolate environments per job |

---

## Decision Framework

### Choosing a Deployment Strategy

```
Is zero-downtime required?
  No  -> Rolling deployment
  Yes ->
    Need instant rollback?
      No  -> Rolling with health checks
      Yes ->
        Budget for 2x infrastructure?
          Yes -> Blue-green
          No  ->
            Can handle complexity of traffic splitting?
              Yes -> Canary
              No  -> Blue-green with smaller footprint
```

### Choosing CI Runner Size

```
Job duration > 20 minutes on 2-core?
  No  -> Use 2-core (cheapest)
  Yes ->
    CPU-bound (compilation, tests)?
      Yes -> 4-core or 8-core (cut time in half)
      No  ->
        I/O bound (downloads, Docker)?
          Yes -> 2-core is fine, optimize caching
          No  -> Profile the job to find the bottleneck
```

---

## Further Reading

- `references/github-actions-patterns.md` -- 30+ production patterns
- `references/deployment-strategies.md` -- Deep dive on each strategy
- `references/agentic-workflows-guide.md` -- GitHub agentic workflows (2026)
- `assets/ci-template.yml` -- Production CI template
- `assets/cd-template.yml` -- Production CD template
