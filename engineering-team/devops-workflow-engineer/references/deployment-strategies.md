# Deployment Strategies

Comprehensive guide to deployment strategies for production systems. Covers blue-green, canary, rolling, A/B testing, feature flags, and database migration handling during deployments.

---

## Table of Contents

1. [Strategy Comparison](#strategy-comparison)
2. [Blue-Green Deployment](#blue-green-deployment)
3. [Canary Deployment](#canary-deployment)
4. [Rolling Deployment](#rolling-deployment)
5. [A/B Testing Deployments](#ab-testing-deployments)
6. [Feature Flags](#feature-flags)
7. [Database Migrations During Deploy](#database-migrations-during-deploy)
8. [Choosing the Right Strategy](#choosing-the-right-strategy)

---

## Strategy Comparison

| Aspect | Blue-Green | Canary | Rolling | A/B Testing |
|--------|-----------|--------|---------|-------------|
| Zero downtime | Yes | Yes | Yes | Yes |
| Rollback speed | Instant | Instant | Minutes | Instant |
| Infrastructure cost | 2x during deploy | 1.1-1.5x | 1x | 1.1-1.5x |
| Complexity | Low | High | Low | High |
| Production testing | Full env before switch | Gradual real traffic | Mixed versions | Segment-based |
| Best for | Critical apps | High-traffic services | Stateless services | UX experiments |
| Risk level | Low | Very low | Medium | Very low |

---

## Blue-Green Deployment

### Overview

Blue-green deployment maintains two identical production environments. At any time, only one (say "blue") serves live traffic. New versions are deployed to the inactive environment ("green"), validated, and then traffic is switched.

### Architecture

```
                    Load Balancer
                    /           \
                   /             \
            [Blue - v1.2]    [Green - v1.3]
            (ACTIVE)         (STAGING)
                   \             /
                    \           /
                  Shared Database
```

### Implementation Steps

1. **Deploy to green environment**
   ```bash
   # Deploy new version to green
   kubectl apply -f deployment-green.yaml
   kubectl rollout status deployment/app-green --timeout=300s
   ```

2. **Run validation on green**
   ```bash
   # Health checks
   curl -sf https://green.internal.example.com/health || exit 1

   # Smoke tests against green
   SMOKE_URL=https://green.internal.example.com pytest tests/smoke/
   ```

3. **Switch traffic**
   ```bash
   # Update load balancer to point to green
   # AWS ALB example:
   aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
     --default-actions Type=forward,TargetGroupArn=$GREEN_TG_ARN

   # Or Kubernetes service selector:
   kubectl patch service app-service -p '{"spec":{"selector":{"version":"green"}}}'
   ```

4. **Monitor**
   - Watch error rates for 15-30 minutes.
   - Compare latency baselines.
   - Verify business metrics (conversion, API success rate).

5. **Finalize or rollback**
   ```bash
   # If healthy: decommission blue (or keep as rollback)
   # If unhealthy: switch back to blue
   kubectl patch service app-service -p '{"spec":{"selector":{"version":"blue"}}}'
   ```

### GitHub Actions Integration

```yaml
jobs:
  deploy-green:
    environment: production-green
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to green
        run: ./scripts/deploy.sh green ${{ github.sha }}
      - name: Validate green
        run: ./scripts/validate.sh green

  switch-traffic:
    needs: deploy-green
    environment: production
    runs-on: ubuntu-latest
    steps:
      - name: Switch traffic to green
        run: ./scripts/switch-traffic.sh green
      - name: Monitor (5 min)
        run: ./scripts/monitor.sh --duration 300 --threshold 0.01
```

### When to Use

- Applications where instant rollback is critical.
- Systems that can afford 2x infrastructure during deployments.
- When you need to validate the full environment before exposing to users.

### When to Avoid

- Very large infrastructure (cost doubles during deploy).
- Stateful services with data that diverges between environments.
- When database schema changes require both versions to coexist.

---

## Canary Deployment

### Overview

Canary deployment routes a small fraction of traffic to the new version while the majority continues on the stable version. Traffic percentage increases gradually based on success metrics.

### Architecture

```
            Load Balancer / Service Mesh
              /        |         \
            95%        |         5%
           /           |           \
    [Stable v1.2]     |     [Canary v1.3]
    (10 replicas)     |     (1 replica)
                       |
               Metric Collection
               (errors, latency)
```

### Traffic Split Schedule

| Phase | Canary % | Duration | Promotion Gate |
|-------|---------|----------|----------------|
| Deploy | 0% | 5 min | Canary pods healthy |
| Phase 1 | 5% | 15 min | Error rate < 0.1%, P99 < 200ms |
| Phase 2 | 25% | 30 min | Error rate < 0.1%, P99 < 200ms |
| Phase 3 | 50% | 60 min | All metrics within baseline |
| Phase 4 | 100% | -- | Full promotion |

### Implementation with Kubernetes

Using Argo Rollouts:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 15m }
        - setWeight: 25
        - pause: { duration: 30m }
        - setWeight: 50
        - pause: { duration: 60m }
        - setWeight: 100
      canaryMetadata:
        labels:
          role: canary
      stableMetadata:
        labels:
          role: stable
      analysis:
        templates:
          - templateName: success-rate
        startingStep: 1
        args:
          - name: service-name
            value: my-app
```

### Analysis Template

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result[0] >= 0.99
      failureCondition: result[0] < 0.95
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

### Implementation with Istio

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
    - my-app
  http:
    - route:
        - destination:
            host: my-app
            subset: stable
          weight: 95
        - destination:
            host: my-app
            subset: canary
          weight: 5
```

### When to Use

- High-traffic services where a bad deploy affects many users.
- When you have good observability and can detect issues at low traffic percentages.
- Services where you want real production validation before full rollout.

### When to Avoid

- Low-traffic services (not enough signal at 5%).
- Services without good metrics/monitoring.
- When speed of deployment is more important than safety.

---

## Rolling Deployment

### Overview

Rolling deployment replaces instances of the old version with the new version one at a time (or in configured batch sizes). At least some instances are always available.

### Architecture

```
Time T0: [v1] [v1] [v1] [v1]  (all old)
Time T1: [v2] [v1] [v1] [v1]  (1 updated)
Time T2: [v2] [v2] [v1] [v1]  (2 updated)
Time T3: [v2] [v2] [v2] [v1]  (3 updated)
Time T4: [v2] [v2] [v2] [v2]  (all new)
```

### Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # Max extra pods during update
      maxUnavailable: 0     # Always maintain full capacity
  template:
    spec:
      containers:
        - name: app
          image: my-app:v2
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 10
```

### Key Parameters

| Parameter | Description | Recommended Default |
|-----------|-------------|-------------------|
| `maxSurge` | Extra pods allowed during update | 25% or 1 |
| `maxUnavailable` | Pods that can be unavailable | 0 (safest) or 25% |
| `minReadySeconds` | Wait after ready before next | 10-30 seconds |
| `progressDeadlineSeconds` | Timeout for rollout | 600 seconds |

### Rollback

```bash
# Automatic rollback on failure
kubectl rollout undo deployment/my-app

# Rollback to specific revision
kubectl rollout undo deployment/my-app --to-revision=3

# Check rollout history
kubectl rollout history deployment/my-app
```

### When to Use

- Stateless services with multiple replicas.
- Kubernetes-native deployments.
- When infrastructure cost must stay flat (no extra environment).

### When to Avoid

- When both versions cannot serve traffic simultaneously (breaking API changes).
- Single-instance deployments (no redundancy during update).
- When instant rollback is required (rolling back is another rolling update).

---

## A/B Testing Deployments

### Overview

A/B testing deployments route traffic to different versions based on user attributes (not random traffic splitting). This enables data-driven decisions about which version performs better.

### Difference from Canary

| Aspect | Canary | A/B Test |
|--------|--------|----------|
| Goal | Risk mitigation | Feature validation |
| Routing | Random percentage | User attributes |
| Duration | Hours | Days to weeks |
| Metrics | Error rate, latency | Business KPIs |
| Rollback trigger | Technical failure | Experiment conclusion |

### Routing Strategies

**Header-based:**
```yaml
# Istio VirtualService
http:
  - match:
      - headers:
          x-experiment-group:
            exact: "variant-b"
    route:
      - destination:
          host: my-app
          subset: variant-b
  - route:
      - destination:
          host: my-app
          subset: variant-a
```

**Cookie-based:**
```yaml
http:
  - match:
      - headers:
          cookie:
            regex: ".*ab_group=B.*"
    route:
      - destination:
          host: my-app
          subset: variant-b
```

**User-segment based (application level):**
```python
def get_variant(user):
    """Determine which variant to show based on user attributes."""
    if user.id % 100 < 50:
        return "A"
    return "B"
```

### Metrics to Track

- **Primary metric:** Conversion rate, revenue per user, engagement time.
- **Guardrail metrics:** Error rate, latency, bounce rate (must not degrade).
- **Statistical significance:** Typically need p < 0.05 with adequate sample size.

### When to Use

- Validating new UI/UX against existing.
- Testing pricing changes.
- Comparing different recommendation algorithms.

---

## Feature Flags

### Overview

Feature flags decouple deployment from release. Code is deployed but features are toggled on/off independently, enabling gradual rollout, instant kill switches, and A/B testing without redeployment.

### Flag Types

| Type | Lifespan | Example |
|------|----------|---------|
| Release flag | Days to weeks | New checkout flow |
| Experiment flag | Weeks to months | Pricing experiment |
| Ops flag | Permanent | Maintenance mode, rate limits |
| Permission flag | Permanent | Premium features, beta access |

### Implementation Patterns

**Simple boolean flag:**
```python
def checkout(request):
    if flags.is_enabled("new-checkout-v2"):
        return new_checkout(request)
    return legacy_checkout(request)
```

**Percentage rollout:**
```python
def checkout(request):
    if flags.is_enabled("new-checkout-v2", percentage=10):
        return new_checkout(request)
    return legacy_checkout(request)
```

**User-targeted flag:**
```python
def checkout(request):
    if flags.is_enabled("new-checkout-v2", user=request.user,
                         rules={"plan": "premium", "country": "US"}):
        return new_checkout(request)
    return legacy_checkout(request)
```

### Flag Lifecycle

```
1. Create flag (disabled) -----> Code deploys with flag check
2. Enable for internal users --> Test in production
3. Enable for 5% of users ----> Monitor metrics
4. Increase to 25%, 50% ------> Gradual rollout
5. Enable for 100% -----------> Full release
6. Remove flag from code ------> Clean up (critical step!)
```

### Best Practices

- **Name flags clearly:** `enable-new-checkout-flow` not `flag-123`.
- **Set expiration dates:** Stale flags are tech debt.
- **Log flag evaluations:** Know which users see which variant.
- **Have a kill switch process:** Document how to disable a flag in an emergency.
- **Clean up after rollout:** Remove flag code once fully launched.
- **Limit active flags:** More than 10-15 active flags creates combinatorial complexity.

### Feature Flag in GitHub Actions

```yaml
jobs:
  deploy:
    steps:
      - name: Set feature flags for environment
        run: |
          # Using a hypothetical flag management CLI
          flag-ctl set new-checkout-v2 \
            --env ${{ inputs.environment }} \
            --percentage 5 \
            --description "Gradual rollout of new checkout"
```

### Services

| Service | Type | Key Feature |
|---------|------|-------------|
| LaunchDarkly | SaaS | Real-time flag evaluation, experimentation |
| Unleash | Open source | Self-hosted, Kubernetes-native |
| Flagsmith | Open source + SaaS | Remote config + flags |
| Split.io | SaaS | Feature flags + experimentation platform |
| Custom | DIY | Simple JSON/YAML config file |

---

## Database Migrations During Deploy

### The Challenge

Database schema changes during deployment create risk because:
- Old code may not work with new schema.
- New code may not work with old schema.
- Both versions run simultaneously during rolling/canary/blue-green deployments.

### Golden Rule: Backward-Compatible Migrations

Every migration must be compatible with **both** the current and previous version of the application code.

### Safe Migration Patterns

**1. Add a column (safe)**
```sql
-- Migration: Add column with default
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
-- Old code ignores the new column. New code uses it.
```

**2. Remove a column (two-phase)**
```
Phase 1 (deploy v2): Stop reading the column in code. Deploy.
Phase 2 (deploy v3): Drop the column in migration. Deploy.
```

**3. Rename a column (three-phase)**
```
Phase 1: Add new column, write to both old and new.
Phase 2: Migrate data, read from new column.
Phase 3: Drop old column.
```

**4. Add an index (safe, but watch performance)**
```sql
-- Use CONCURRENTLY to avoid locking the table
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

**5. Change column type (two-phase)**
```
Phase 1: Add new column with new type, dual-write.
Phase 2: Migrate data, switch reads to new column.
Phase 3: Drop old column.
```

### Unsafe Migration Patterns (Avoid)

| Migration | Risk | Safe Alternative |
|-----------|------|-----------------|
| DROP COLUMN | Old code breaks | Two-phase: stop using, then drop |
| RENAME COLUMN | Both versions break | Three-phase: add, migrate, drop |
| ALTER TYPE (in-place) | Table lock, old code breaks | Add new column, migrate |
| NOT NULL without default | INSERT fails for old code | Add with DEFAULT first |
| DROP TABLE | Everything breaks | Deprecate, stop references, then drop |

### Migration Execution in CI/CD

```yaml
jobs:
  migrate:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4

      - name: Backup database
        run: ./scripts/db-backup.sh ${{ inputs.environment }}

      - name: Run migration (dry run)
        run: ./scripts/db-migrate.sh --dry-run --env ${{ inputs.environment }}

      - name: Run migration
        run: ./scripts/db-migrate.sh --env ${{ inputs.environment }}

      - name: Verify migration
        run: ./scripts/db-verify.sh --env ${{ inputs.environment }}

  deploy:
    needs: migrate
    # ... deploy application code
```

### Migration Rollback

- Always write a corresponding `down` migration.
- Test rollback in staging before deploying to production.
- If a migration is not reversible, document it and plan accordingly.

```python
# Example: Django migration with reverse
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]

    # Django auto-generates reverse: RemoveField
```

---

## Choosing the Right Strategy

### Decision Tree

```
Start
  |
  v
Is zero-downtime required?
  |
  No --> Simple deployment (stop old, start new)
  |
  Yes
  |
  v
Is instant rollback critical?
  |
  No --> Rolling deployment
  |
  Yes
  |
  v
Can you afford 2x infrastructure?
  |
  Yes --> Blue-green deployment
  |
  No
  |
  v
Do you have good observability (metrics, alerting)?
  |
  No --> Blue-green (simpler to manage)
  |
  Yes
  |
  v
Is traffic high enough for meaningful canary signal?
  |
  No --> Blue-green
  |
  Yes --> Canary deployment
```

### Strategy Selection by Service Type

| Service Type | Recommended Primary | Recommended Secondary |
|-------------|--------------------|-----------------------|
| User-facing web app | Blue-green | Canary |
| API service | Canary | Rolling |
| Background worker | Rolling | Blue-green |
| Stateful service | Blue-green | Rolling (careful) |
| Database | Rolling (with migrations) | N/A |
| Shared library | Version publish | N/A |
| Mobile app | Staged rollout (canary) | Feature flags |
| Infrastructure | Rolling (Terraform) | Blue-green |

### Combining Strategies

Production deployments often combine multiple strategies:

1. **Feature flags + Canary:** Deploy with feature hidden behind flag, canary the deployment, then gradually enable the flag.
2. **Blue-green + Database migration:** Run backward-compatible migration first, then blue-green switch the application.
3. **Rolling + Health checks:** Standard Kubernetes rolling update with readiness probes acting as automatic gates.
4. **Canary + A/B test:** Use canary for risk mitigation during deploy, then A/B test the feature over days.
