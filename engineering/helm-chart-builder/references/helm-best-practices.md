# Helm Best Practices Reference

## Chart Structure

### Minimum Required Files
```
my-chart/
  Chart.yaml       # Required: metadata
  values.yaml      # Required: defaults
  templates/       # Required: manifests
```

### Recommended Structure
```
my-chart/
  Chart.yaml
  Chart.lock
  values.yaml
  values-dev.yaml
  values-staging.yaml
  values-production.yaml
  templates/
    deployment.yaml
    service.yaml
    ingress.yaml
    serviceaccount.yaml
    hpa.yaml
    pdb.yaml
    configmap.yaml
    secret.yaml
    _helpers.tpl
    NOTES.txt
    tests/
      test-connection.yaml
  charts/           # Subcharts
  crds/             # CRDs
  README.md
```

## Chart.yaml Best Practices

```yaml
apiVersion: v2
name: my-app
description: A Helm chart for my application
type: application
version: 1.2.3          # Chart version (SemVer)
appVersion: "2.0.0"     # Application version
maintainers:
  - name: team
    email: team@example.com
dependencies:
  - name: postgresql
    version: "~12.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
```

## Values Best Practices

### Security Defaults
```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL

podSecurityContext:
  fsGroup: 1000
  runAsUser: 1000
  runAsGroup: 1000
```

### Resource Management
```yaml
resources:
  limits:
    cpu: 500m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

### Health Probes
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Template Patterns

### _helpers.tpl Standard Labels
```yaml
{{- define "my-chart.labels" -}}
helm.sh/chart: {{ include "my-chart.chart" . }}
app.kubernetes.io/name: {{ include "my-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

### Conditional Resources
```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
...
{{- end }}
```

## Dependency Management

- Always pin dependency versions with range operators: `~1.2.0` or `>=1.0.0 <2.0.0`
- Use `condition` fields to make dependencies optional
- Run `helm dependency update` after modifying Chart.yaml
- Commit Chart.lock for reproducible builds

## Testing

```bash
# Lint chart
helm lint ./my-chart

# Template rendering
helm template my-release ./my-chart --values values-prod.yaml

# Dry run install
helm install my-release ./my-chart --dry-run --debug

# Run chart tests
helm test my-release
```
