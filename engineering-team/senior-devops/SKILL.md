---
name: senior-devops
description: Senior DevOps engineering skill covering CI/CD pipeline design, infrastructure as code with Terraform, container orchestration with Kubernetes, cloud platform architecture (AWS, GCP, Azure), deployment strategies, monitoring and observability, and security hardening. Provides pipeline generation, Terraform scaffolding, and deployment management automation. Use when the user needs to build CI/CD pipelines, containerize applications, manage Kubernetes clusters, provision cloud infrastructure, implement deployment strategies, set up monitoring, optimize cloud costs, or handle incident response.
license: MIT
metadata:
  version: 2.0.0
  category: engineering
  domain: infrastructure
---

# Senior DevOps Engineer

Production-grade DevOps engineering toolkit covering the full infrastructure lifecycle: CI/CD pipeline design, container orchestration, infrastructure as code, cloud platform architecture, deployment strategies, observability, security hardening, cost optimization, and incident response.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Docker and Containerization](#docker-and-containerization)
- [Kubernetes](#kubernetes)
- [CI/CD Pipelines](#cicd-pipelines)
- [Infrastructure as Code](#infrastructure-as-code)
- [Monitoring and Observability](#monitoring-and-observability)
- [Cloud Platforms](#cloud-platforms)
- [Deployment Strategies](#deployment-strategies)
- [Security](#security)
- [Cost Optimization](#cost-optimization)
- [Incident Response](#incident-response)
- [Reference Documentation](#reference-documentation)
- [Integration Points](#integration-points)

---

## Keywords

Use this skill when you encounter:

| Category | Terms |
|----------|-------|
| **CI/CD** | pipeline, GitHub Actions, GitLab CI, Jenkins, CircleCI, build automation, artifact registry, continuous integration, continuous delivery, continuous deployment |
| **Containers** | Docker, Dockerfile, docker-compose, container image, multi-stage build, OCI, container registry, ECR, GCR, ACR |
| **Orchestration** | Kubernetes, k8s, kubectl, Helm, pod, deployment, service, ingress, HPA, VPA, StatefulSet, DaemonSet, CronJob |
| **IaC** | Terraform, OpenTofu, CloudFormation, Pulumi, Ansible, state management, tfstate, modules, workspaces, drift detection |
| **Cloud** | AWS, GCP, Azure, EC2, EKS, GKE, AKS, Lambda, Cloud Functions, S3, VPC, IAM, load balancer, auto-scaling |
| **Monitoring** | Prometheus, Grafana, Datadog, ELK, Loki, Jaeger, OpenTelemetry, alerting, SLO, SLI, SLA, dashboards |
| **Deployment** | blue-green, canary, rolling update, feature flags, rollback, zero-downtime, A/B deployment, progressive delivery |
| **Security** | Vault, secrets management, RBAC, network policy, supply chain security, SBOM, image scanning, Trivy, Falco |
| **Reliability** | incident response, runbook, postmortem, SRE, error budget, chaos engineering, disaster recovery, RTO, RPO |
| **Cost** | FinOps, right-sizing, spot instances, reserved capacity, cost allocation, tagging strategy, savings plans |

---

## Quick Start

This skill provides three core automation tools:

```bash
# Generate CI/CD pipelines for any platform (GitHub Actions, GitLab CI, Jenkins, CircleCI)
python scripts/pipeline_generator.py <project-path> --platform github-actions --verbose

# Scaffold Terraform infrastructure with modules, state config, and environment separation
python scripts/terraform_scaffolder.py <target-path> --provider aws --env production --verbose

# Manage deployments with strategy selection, health checks, and rollback support
python scripts/deployment_manager.py <target-path> --strategy canary --verbose
```

### Tool Details

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `pipeline_generator.py` | Generates CI/CD pipeline configurations from project analysis | `--platform`, `--stages`, `--json` |
| `terraform_scaffolder.py` | Creates Terraform module structure with best-practice patterns | `--provider`, `--env`, `--modules` |
| `deployment_manager.py` | Orchestrates deployments with strategy selection and rollback | `--strategy`, `--target`, `--dry-run` |

---

## Docker and Containerization

### Dockerfile Best Practices

Every production Dockerfile should follow this layered pattern:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependency manifests first (cache layer)
COPY package.json package-lock.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app

# Run as non-root
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

# Copy only production artifacts
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/healthz || exit 1

CMD ["node", "dist/server.js"]
```

**Critical rules:**
- Always use specific image tags, never `latest` in production
- Order COPY instructions from least to most frequently changed (maximizes layer cache)
- Use `.dockerignore` to exclude `.git`, `node_modules`, test files, docs
- Never store secrets in images -- use runtime injection via environment or mounted secrets
- Pin package manager versions: `npm ci` not `npm install`, lock files always copied
- Multi-stage builds reduce final image size by 60-80%

### Docker Compose Patterns

Production-ready compose for a typical microservice stack:

```yaml
version: "3.9"

x-common: &common
  restart: unless-stopped
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

services:
  app:
    <<: *common
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://app:${DB_PASSWORD}@db:5432/appdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/healthz"]
      interval: 15s
      timeout: 5s
      retries: 3

  db:
    <<: *common
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    <<: *common
    image: redis:7-alpine
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  pgdata:
  redisdata:
```

### Container Security Checklist

- [ ] Base images from trusted registries only (Docker Official, Chainguard, Distroless)
- [ ] Images scanned with Trivy or Grype before push: `trivy image --severity HIGH,CRITICAL myapp:latest`
- [ ] No root processes inside containers -- always use `USER` directive
- [ ] Read-only root filesystem where possible: `--read-only --tmpfs /tmp`
- [ ] Resource limits enforced (CPU, memory) to prevent noisy-neighbor attacks
- [ ] No secrets baked into image layers -- verify with `docker history --no-trunc`
- [ ] Minimal base images (Alpine, Distroless) to reduce attack surface

---

## Kubernetes

### Pod Design Patterns

**Sidecar pattern** -- add capabilities without modifying the main container:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
      serviceAccountName: app-sa
      securityContext:
        runAsNonRoot: true
        fsGroup: 1001
      containers:
        - name: app
          image: myapp:1.2.3
          ports:
            - containerPort: 3000
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: "1"
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /healthz
              port: 3000
            initialDelaySeconds: 15
            periodSeconds: 20
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          startupProbe:
            httpGet:
              path: /healthz
              port: 3000
            failureThreshold: 30
            periodSeconds: 10
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: db-password
        - name: log-shipper
          image: fluent/fluent-bit:2.2
          volumeMounts:
            - name: app-logs
              mountPath: /var/log/app
      volumes:
        - name: app-logs
          emptyDir: {}
```

**Probe decision framework:**
- **startupProbe**: Use for slow-starting apps (JVM, large model loading). Prevents liveness from killing a container that has not finished starting.
- **livenessProbe**: Detects deadlocks and hangs. Keep it simple (check process health, not downstream dependencies).
- **readinessProbe**: Controls traffic routing. Include dependency checks here (database reachable, cache warm).

### Helm Chart Structure

```
charts/myapp/
  Chart.yaml
  values.yaml
  values-staging.yaml
  values-production.yaml
  templates/
    deployment.yaml
    service.yaml
    ingress.yaml
    hpa.yaml
    networkpolicy.yaml
    serviceaccount.yaml
    _helpers.tpl
```

Key `values.yaml` patterns:

```yaml
replicaCount: 3

image:
  repository: myapp
  tag: "1.2.3"
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.example.com
```

### Resource Management and Auto-Scaling

**HPA (Horizontal Pod Autoscaler):**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 25
          periodSeconds: 120
```

**Decision: HPA vs VPA vs KEDA**

| Scaler | Use When | Avoid When |
|--------|----------|------------|
| **HPA** | Stateless services, predictable CPU/memory patterns | Stateful workloads, bursty event-driven loads |
| **VPA** | Right-sizing requests/limits, batch jobs, single-replica workloads | Used alone for latency-sensitive services |
| **KEDA** | Event-driven scaling (queue depth, HTTP rate, cron) | Simple CPU-based scaling (HPA is simpler) |

---

## CI/CD Pipelines

### GitHub Actions

Production pipeline with caching, matrix testing, and deployment gates:

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write
  id-token: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        if: matrix.node-version == 20
        with:
          name: coverage
          path: coverage/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
          exit-code: 1

  build:
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: |
          helm upgrade --install app charts/myapp \
            --namespace staging \
            --values charts/myapp/values-staging.yaml \
            --set image.tag=${{ github.sha }} \
            --wait --timeout 300s

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production (canary)
        run: |
          helm upgrade --install app charts/myapp \
            --namespace production \
            --values charts/myapp/values-production.yaml \
            --set image.tag=${{ github.sha }} \
            --set canary.enabled=true \
            --set canary.weight=10 \
            --wait --timeout 300s
```

### GitLab CI

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_BUILDKIT: 1

test:
  stage: test
  image: node:20-alpine
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
  script:
    - npm ci
    - npm run lint
    - npm test -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  only:
    - main
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy_staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main
  script:
    - helm upgrade --install app charts/myapp
        --namespace staging
        --set image.tag=$CI_COMMIT_SHA
        --wait

deploy_production:
  stage: deploy
  environment:
    name: production
    url: https://app.example.com
  only:
    - main
  when: manual
  script:
    - helm upgrade --install app charts/myapp
        --namespace production
        --set image.tag=$CI_COMMIT_SHA
        --wait
```

### Pipeline Design Principles

1. **Fail fast**: Run linting and unit tests before expensive integration tests
2. **Cache aggressively**: Node modules, Docker layers, Go modules, pip packages
3. **Immutable artifacts**: Build once, deploy the same artifact to every environment
4. **Gate promotions**: Require manual approval or automated smoke tests before production
5. **Parallel where possible**: Run independent test suites and security scans concurrently
6. **Reproduce locally**: Every CI step should be runnable on a developer machine

---

## Infrastructure as Code

### Terraform Module Structure

```
infrastructure/
  modules/
    vpc/
      main.tf
      variables.tf
      outputs.tf
    eks/
      main.tf
      variables.tf
      outputs.tf
    rds/
      main.tf
      variables.tf
      outputs.tf
  environments/
    staging/
      main.tf          # Calls modules with staging values
      terraform.tfvars
      backend.tf        # S3 + DynamoDB state backend
    production/
      main.tf
      terraform.tfvars
      backend.tf
```

### State Management

Remote state with locking (AWS):

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "production/infrastructure.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

**State management rules:**
- One state file per environment per component (blast radius control)
- Never store state locally or in git
- Enable encryption at rest and in transit
- Use DynamoDB (AWS) or Cloud Storage (GCP) for state locking
- Run `terraform plan` in CI, `terraform apply` only after approval
- Use `terraform state list` and `terraform state show` for debugging, never edit state manually

### Workspace vs Directory Pattern

| Pattern | Use When | Trade-offs |
|---------|----------|------------|
| **Workspaces** | Same config, different scale (dev/staging/prod with identical topology) | Shared state backend, easy switching, but harder to diverge configs |
| **Directories** | Different environments need different resources or topology | Full isolation, clear boundaries, but duplicated boilerplate |

**Recommendation**: Use directories for environment separation. Use modules for shared logic. Workspaces are better suited for ephemeral environments (PR previews, load test environments).

### Drift Detection

Integrate drift detection into CI:

```bash
# Run in CI on a schedule (daily)
terraform plan -detailed-exitcode -out=plan.tfplan

# Exit code 0 = no changes (clean)
# Exit code 1 = error
# Exit code 2 = changes detected (drift)

# Alert on exit code 2
if [ $? -eq 2 ]; then
  # Send alert to Slack/PagerDuty
  curl -X POST "$SLACK_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d '{"text":"Terraform drift detected in production. Review required."}'
fi
```

### Terraform Anti-Patterns

- **Monolithic state**: One state file for the entire infrastructure. Split by component and environment.
- **Hardcoded values**: Use variables and tfvars. Never hardcode AMI IDs, instance types, or CIDR blocks.
- **No lifecycle rules**: Use `prevent_destroy` on critical resources (databases, S3 buckets with data).
- **Ignoring plan output**: Always review plan diffs before apply, especially `destroy` and `replace` actions.

---

## Monitoring and Observability

### The Three Pillars

| Pillar | Tool | Purpose |
|--------|------|---------|
| **Metrics** | Prometheus + Grafana | Numeric time-series data (CPU, latency, error rates) |
| **Logs** | Loki / ELK (Elasticsearch, Logstash, Kibana) | Structured event records for debugging |
| **Traces** | Jaeger / Tempo + OpenTelemetry | Request flow across services for latency analysis |

### Prometheus Alerting Rules

```yaml
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate exceeds 5% for 5 minutes"
          runbook: "https://wiki.example.com/runbooks/high-error-rate"

      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
          > 2.0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency exceeds 2s for 10 minutes"

      - alert: PodCrashLooping
        expr: |
          increase(kube_pod_container_status_restarts_total[1h]) > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} restarting frequently"

      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.15
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Disk space below 15% on {{ $labels.instance }}"
```

### SLO/SLI Definitions

**Define SLIs first, then set SLOs:**

| Service | SLI (what you measure) | SLO (target) | Error Budget |
|---------|------------------------|---------------|--------------|
| API Gateway | Successful requests / Total requests | 99.9% availability (43.8 min/month downtime) | 0.1% |
| API Latency | Requests under 500ms / Total requests | 99th percentile < 500ms | 1% |
| Data Pipeline | Successful pipeline runs / Total runs | 99.5% success rate | 0.5% |
| Deployment | Successful deploys / Total deploys | 99% success rate | 1% |

**Error budget policy**: When the error budget is exhausted, freeze feature deployments and prioritize reliability work until the budget recovers.

### Grafana Dashboard Essentials

Every service dashboard should include these panels (the "Four Golden Signals"):

1. **Latency**: P50, P90, P99 response times (histogram)
2. **Traffic**: Requests per second by endpoint and status code
3. **Errors**: 5xx rate, 4xx rate, application-specific error codes
4. **Saturation**: CPU usage, memory usage, connection pool utilization, queue depth

---

## Cloud Platforms

### Service Comparison Matrix

| Capability | AWS | GCP | Azure |
|------------|-----|-----|-------|
| **Managed Kubernetes** | EKS | GKE | AKS |
| **Serverless Compute** | Lambda | Cloud Functions / Cloud Run | Azure Functions |
| **Container Service** | ECS/Fargate | Cloud Run | Container Apps |
| **Object Storage** | S3 | Cloud Storage | Blob Storage |
| **Managed Database** | RDS / Aurora | Cloud SQL / AlloyDB | Azure SQL / Cosmos DB |
| **Message Queue** | SQS / SNS | Pub/Sub | Service Bus |
| **CDN** | CloudFront | Cloud CDN | Azure CDN / Front Door |
| **DNS** | Route 53 | Cloud DNS | Azure DNS |
| **Secrets** | Secrets Manager | Secret Manager | Key Vault |
| **IAM** | IAM + STS | IAM + Workload Identity | Entra ID + RBAC |
| **IaC** | CloudFormation / CDK | Deployment Manager | Bicep / ARM |

### Multi-Cloud Strategy Decision Framework

**When multi-cloud makes sense:**
- Regulatory requirements mandate geographic or vendor diversity
- Acquisition brings in workloads on a different cloud
- Specific best-of-breed services (e.g., GCP for ML, AWS for breadth)

**When it does not:**
- Avoiding vendor lock-in as the sole motivation (the operational tax exceeds the savings)
- Small teams that cannot afford the complexity overhead
- Workloads with no regulatory driver for distribution

**If you go multi-cloud:**
- Use Terraform (not provider-specific IaC) for the abstraction layer
- Standardize on Kubernetes as the compute plane across clouds
- Centralize observability (Datadog, Grafana Cloud) to avoid fragmented visibility
- Invest in a platform engineering team to manage the abstraction

---

## Deployment Strategies

### Strategy Selection Framework

| Strategy | Risk | Rollback Speed | Infrastructure Cost | Best For |
|----------|------|----------------|---------------------|----------|
| **Rolling Update** | Medium | Minutes | 1x | Stateless services, internal APIs |
| **Blue-Green** | Low | Seconds (DNS/LB switch) | 2x during deploy | Mission-critical, zero-downtime required |
| **Canary** | Low | Seconds (shift traffic back) | 1.1x | User-facing services, gradual validation |
| **Feature Flags** | Lowest | Instant (toggle) | 1x | Granular control, A/B testing, trunk-based dev |

### Blue-Green Implementation

```yaml
# Blue (current production)
apiVersion: v1
kind: Service
metadata:
  name: app-production
spec:
  selector:
    app: myapp
    version: blue     # Points to current version
  ports:
    - port: 80
      targetPort: 3000

---
# Green (new version) -- deploy alongside blue
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
        - name: app
          image: myapp:2.0.0
```

**Cutover steps:**
1. Deploy green alongside blue (both running, only blue serves traffic)
2. Run smoke tests against green via internal service or port-forward
3. Switch the service selector from `version: blue` to `version: green`
4. Monitor for 15 minutes
5. If healthy, scale down blue. If not, switch selector back to blue.

### Canary with Istio/Nginx

```yaml
# Istio VirtualService for canary routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-canary
spec:
  hosts:
    - app.example.com
  http:
    - route:
        - destination:
            host: app-stable
            port:
              number: 80
          weight: 90
        - destination:
            host: app-canary
            port:
              number: 80
          weight: 10
```

**Canary promotion ladder:**
1. Deploy canary with 5% traffic
2. Monitor error rate and latency for 10 minutes
3. Promote to 25%, monitor 10 minutes
4. Promote to 50%, monitor 15 minutes
5. Promote to 100% (canary becomes stable)
6. Automated rollback if error rate exceeds baseline by 2x at any step

### Feature Flags

Use feature flags for decoupling deployment from release:

```python
# Example with LaunchDarkly / Unleash / simple config
if feature_flags.is_enabled("new-checkout-flow", user_context):
    return new_checkout_handler(request)
else:
    return legacy_checkout_handler(request)
```

**Flag lifecycle:**
1. Create flag (default: off)
2. Enable for internal users / beta testers
3. Gradual rollout: 5% -> 25% -> 50% -> 100%
4. Remove flag and dead code path within 2 sprints of full rollout

---

## Security

### Secret Management

**Decision matrix:**

| Tool | Best For | Avoid When |
|------|----------|------------|
| **HashiCorp Vault** | Dynamic secrets, PKI, encryption as a service, multi-cloud | Small teams, simple applications |
| **AWS Secrets Manager** | AWS-native workloads, automatic rotation | Multi-cloud or hybrid requirements |
| **AWS SSM Parameter Store** | Non-sensitive config, low-cost secret storage | Rotation or audit requirements at scale |
| **Kubernetes Secrets** | Pod-level injection (with encryption at rest enabled) | Storing secrets long-term or sharing across clusters |
| **SOPS / age** | Encrypted secrets in git (gitops workflows) | Teams unfamiliar with key management |

**Vault integration pattern for Kubernetes:**

```yaml
# Using Vault Agent Injector
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "app-role"
        vault.hashicorp.com/agent-inject-secret-db: "secret/data/app/db"
        vault.hashicorp.com/agent-inject-template-db: |
          {{- with secret "secret/data/app/db" -}}
          export DB_HOST={{ .Data.data.host }}
          export DB_PASSWORD={{ .Data.data.password }}
          {{- end -}}
    spec:
      serviceAccountName: app-sa
      containers:
        - name: app
          image: myapp:1.2.3
          command: ["/bin/sh", "-c", "source /vault/secrets/db && node server.js"]
```

### Network Policies

Default-deny with explicit allow:

```yaml
# Default deny all ingress and egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress

---
# Allow app to receive traffic from ingress controller and talk to database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 3000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:  # Allow DNS resolution
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
```

### RBAC Best Practices

- Follow the principle of least privilege: grant minimum permissions needed
- Use ClusterRoles for cluster-wide resources, Roles for namespace-scoped
- Bind service accounts to roles, not users (service accounts are auditable and rotatable)
- Audit RBAC with: `kubectl auth can-i --list --as=system:serviceaccount:production:app-sa`
- Never grant `cluster-admin` to application service accounts

### Supply Chain Security

```bash
# Sign container images with cosign
cosign sign --key cosign.key ghcr.io/myorg/myapp:1.2.3

# Verify before deployment
cosign verify --key cosign.pub ghcr.io/myorg/myapp:1.2.3

# Generate SBOM
syft ghcr.io/myorg/myapp:1.2.3 -o spdx-json > sbom.json

# Scan SBOM for vulnerabilities
grype sbom:sbom.json --fail-on high
```

**Admission control**: Use Kyverno or OPA Gatekeeper to enforce policies:
- Only allow images from trusted registries
- Require image signatures
- Block containers running as root
- Enforce resource limits on all pods

---

## Cost Optimization

### Right-Sizing Methodology

1. **Collect**: Gather 2-4 weeks of CPU and memory utilization data from Prometheus/CloudWatch
2. **Analyze**: Identify instances running below 40% average CPU utilization
3. **Recommend**: Suggest one size down (e.g., m5.xlarge -> m5.large)
4. **Validate**: Apply in staging, load test, confirm no performance regression
5. **Apply**: Resize in production during maintenance window
6. **Monitor**: Track for 1 week post-change to confirm stability

### Spot/Preemptible Instance Strategy

| Workload Type | Spot Suitable? | Pattern |
|---------------|----------------|---------|
| Stateless web servers (behind LB) | Yes | Mix 70% spot + 30% on-demand |
| CI/CD runners | Yes | 100% spot with retry logic |
| Batch processing / ETL | Yes | Spot fleet with checkpointing |
| Databases / stateful | No | Use reserved instances |
| Kubernetes control plane | No | On-demand or reserved |
| Dev/test environments | Yes | 100% spot, accept interruptions |

### FinOps Practices

- **Tagging strategy**: Enforce tags for `team`, `environment`, `service`, `cost-center` on all resources
- **Budget alerts**: Set CloudWatch/GCP Budget alerts at 50%, 80%, 100% of monthly budget
- **Reserved capacity**: Purchase 1-year reservations for baseline workloads (30-40% savings)
- **Savings Plans**: Use Compute Savings Plans (AWS) for flexible commitment discounts
- **Scheduled scaling**: Scale down non-production environments outside business hours
- **Storage lifecycle**: S3 lifecycle policies to move old data to Glacier/Archive tiers
- **Unused resource cleanup**: Weekly scan for unattached EBS volumes, idle load balancers, stale snapshots

---

## Incident Response

### Severity Classification

| Severity | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| **SEV-1** | Complete service outage, data loss risk | 15 minutes | Production database down, payment system failure |
| **SEV-2** | Significant degradation, partial outage | 30 minutes | High error rate, API latency > 10x normal |
| **SEV-3** | Minor degradation, workaround available | 4 hours | Non-critical feature broken, elevated error rate < 1% |
| **SEV-4** | Cosmetic / informational | Next business day | Dashboard rendering issue, log verbosity spike |

### Runbook Template

```markdown
# Runbook: [Service Name] - [Issue Type]

## Symptoms
- What alerts fire
- What users report
- What dashboards show

## Impact
- Which users/services affected
- Revenue impact estimate

## Diagnosis Steps
1. Check service health: `kubectl get pods -n production -l app=myapp`
2. Review recent deployments: `helm history myapp -n production`
3. Check error logs: `kubectl logs -l app=myapp -n production --tail=100`
4. Verify database connectivity: `kubectl exec -it app-pod -- pg_isready -h db-host`
5. Check resource utilization: Review Grafana dashboard [link]

## Remediation
### Quick Fix (< 5 min)
- Restart pods: `kubectl rollout restart deployment/myapp -n production`
- Scale up: `kubectl scale deployment/myapp --replicas=10 -n production`

### Rollback (< 10 min)
- `helm rollback myapp [previous-revision] -n production`

### Root Cause Fix
- [Document fix steps specific to this issue]

## Escalation
- L1: On-call engineer (PagerDuty)
- L2: Team lead / service owner
- L3: VP Engineering (SEV-1 only)

## Communication
- Statuspage update within 15 min of SEV-1/SEV-2
- Slack channel: #incidents
```

### Postmortem Process

Every SEV-1 and SEV-2 incident requires a blameless postmortem within 3 business days:

1. **Timeline**: Minute-by-minute reconstruction of what happened
2. **Root cause**: Use the "5 Whys" technique to identify the underlying cause
3. **Impact**: Users affected, duration, revenue impact
4. **What went well**: Detection, communication, and resolution that worked
5. **What went poorly**: Gaps in monitoring, slow response, unclear ownership
6. **Action items**: Concrete tasks with owners and due dates, prioritized by impact
7. **Lessons learned**: Patterns to adopt or avoid going forward

**Template**: Store postmortems in a shared wiki. Link them from the incident channel for team visibility.

---

## Reference Documentation

This skill includes three reference guides for deep-dive topics:

| Reference | Path | Covers |
|-----------|------|--------|
| **CI/CD Pipeline Guide** | `references/cicd_pipeline_guide.md` | Pipeline patterns, platform comparisons, optimization techniques, testing strategies |
| **Infrastructure as Code** | `references/infrastructure_as_code.md` | Terraform patterns, module design, state management, provider configuration |
| **Deployment Strategies** | `references/deployment_strategies.md` | Strategy comparison, implementation details, rollback procedures, traffic management |

Use the reference files for extended examples and edge-case handling beyond what this skill file covers.

---

## Integration Points

This skill works alongside other skills in the library:

| Skill | Integration |
|-------|-------------|
| **senior-secops** | Security scanning in CI/CD pipelines, container image scanning, compliance checks |
| **senior-architect** | Infrastructure design decisions, service topology, dependency analysis |
| **senior-backend** | Application containerization, health check endpoints, config management |
| **senior-cloud-architect** | Cloud platform selection, multi-region architecture, disaster recovery planning |
| **incident-commander** | Incident escalation procedures, communication protocols, postmortem facilitation |
| **code-reviewer** | Infrastructure-as-code review standards, Terraform plan review, pipeline config review |
| **aws-solution-architect** | AWS-specific infrastructure patterns, service selection, cost optimization |

---

**Last Updated:** February 2026
**Version:** 2.0.0
**Tools:** 3 Python automation scripts
**References:** 3 deep-dive guides
