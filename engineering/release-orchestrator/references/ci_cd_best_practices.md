# CI/CD Best Practices

## Pipeline Design Patterns

### Stage-Gate Pipeline

Organize the pipeline into sequential stages. Each stage must pass before the next begins.

```
Build -> Unit Tests -> Integration Tests -> Security Scan -> Deploy Staging -> E2E Tests -> Deploy Production
```

**Rules:**
- Fast stages first (lint, compile, unit tests)
- Expensive stages later (E2E, load tests)
- Every stage must be independently retriable
- Fail fast: stop the pipeline on first failure

### Fan-Out / Fan-In

Run independent jobs in parallel, then converge for dependent stages.

```
                +--> Unit Tests ----+
Build --> Lint -+--> Type Check ----+--> Integration Tests --> Deploy
                +--> Security Scan -+
```

This reduces total pipeline time by running independent checks concurrently.

### Pipeline as Code

Define pipelines in version-controlled files alongside the application code.

- GitHub Actions: `.github/workflows/*.yml`
- GitLab CI: `.gitlab-ci.yml`
- Jenkins: `Jenkinsfile`

**Benefits:** Review pipeline changes in PRs, audit history, branch-specific pipelines.

### Environment Promotion

```
Build Artifact --> Dev --> Staging --> Production
```

- Build the artifact ONCE
- Promote the same artifact through environments
- Never rebuild for production (eliminates "works on my machine" issues)
- Use environment-specific configuration, not environment-specific builds

---

## Parallel Test Execution

### Test Splitting Strategies

**By file:** Distribute test files evenly across runners. Simple but may produce uneven load.

**By timing:** Use historical test durations to split evenly. Produces the most balanced distribution.

**By test suite:** Run unit, integration, and E2E in parallel pipelines.

### Parallelization Patterns

```yaml
# GitHub Actions: Matrix strategy
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

**Guidelines:**
- Start with 4 shards, increase if pipeline > 10 minutes
- Monitor for flaky tests that appear only in parallel (shared state issues)
- Use separate databases per shard for integration tests
- Report aggregated coverage from all shards

### Test Ordering

1. **Lint and type check** (seconds) - catches syntax and type errors immediately
2. **Unit tests** (seconds to minutes) - fast feedback on logic
3. **Integration tests** (minutes) - API contracts, database interactions
4. **E2E tests** (minutes to tens of minutes) - user workflows
5. **Performance tests** (minutes) - regression detection

---

## Caching Strategies

### Dependency Caching

Cache package manager downloads to avoid re-fetching on every build.

```yaml
# GitHub Actions
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('package-lock.json') }}
    restore-keys: npm-
```

**Cache keys:** Always include the lock file hash. Use restore-keys for partial matches.

### Build Caching

- **Docker layer caching:** Order Dockerfile instructions from least to most frequently changing
- **Compilation caching:** Use ccache (C/C++), sccache (Rust), or Turborepo (JavaScript)
- **Test result caching:** Skip tests for unchanged modules

### Cache Invalidation

- Lock file change = full dependency cache invalidation
- Source file change = incremental build cache invalidation
- CI config change = consider full cache invalidation
- Set maximum cache age (7-14 days) to prevent stale caches

### What NOT to Cache

- Security scan databases (must be current)
- Secrets or credentials
- Build artifacts intended for deployment (build fresh for reproducibility)
- Test fixtures that must reflect current data

---

## Artifact Management

### Build Artifacts

- Tag artifacts with commit SHA and build number
- Store in a registry (Docker Hub, ECR, GCR, Artifactory)
- Retain production artifacts for at least 30 days (rollback window)
- Sign artifacts for integrity verification

### Artifact Naming Convention

```
{project}-{version}-{commit_sha_short}-{timestamp}
```

Example: `my-app-1.3.0-a1b2c3d-20260318T1423`

### Artifact Lifecycle

| Stage | Retention | Example |
|---|---|---|
| Feature branch | 7 days | Auto-delete after branch merge |
| Staging | 14 days | Keep for debugging |
| Production | 90 days | Rollback window |
| Release tags | Permanent | Audit trail |

### Container Image Best Practices

- Use multi-stage builds to minimize image size
- Pin base image versions (not `latest`)
- Scan images for vulnerabilities before pushing
- Use immutable tags (SHA-based) for production deployments
- Never run containers as root

---

## Environment Promotion

### Promotion Flow

```
Developer -> Feature Branch CI -> Dev Environment -> QA/Staging -> Production
```

### Environment Parity

Keep environments as similar as possible:
- Same OS, runtime versions, and configurations
- Same infrastructure (containers, orchestration)
- Same monitoring and logging
- Different only in: scale, data, secrets, external integrations

### Promotion Gates

| Gate | Checks | Auto/Manual |
|---|---|---|
| Dev -> Staging | All tests pass, no critical vulnerabilities | Automatic |
| Staging -> Production | E2E tests pass, performance baseline met, approval | Manual approval |
| Production canary -> Full | Error rate < 0.1%, latency within baseline | Automatic with manual override |

### Environment-Specific Configuration

Use environment variables or config services, never bake configuration into artifacts:

```bash
# Good: runtime configuration
DATABASE_URL=${ENV_DATABASE_URL}

# Bad: build-time configuration
DATABASE_URL=postgres://prod-server:5432/mydb
```

### Secrets Management

- Never store secrets in code, environment files, or CI configuration
- Use a secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager)
- Rotate secrets regularly
- Audit secret access
- Different secrets per environment (never share production secrets with staging)
