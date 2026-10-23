# Azure Workflows, WAF, Cost, and Anti-patterns

Read this when running an end-to-end design or review workflow, applying the Well-Architected Framework pillars, optimizing cost, or checking for Azure-specific anti-patterns. For deep dives see `azure-well-architected.md` and `azure-cost-optimization.md`.

## Azure Well-Architected Framework (WAF)

Microsoft's WAF has five pillars. Every architecture should be assessed against all five.

| Pillar | Core question |
|--------|---------------|
| **Reliability** | Will it stay up under expected and unexpected load? |
| **Security** | Can it defend against threats, contain breaches, recover from compromise? |
| **Cost Optimization** | Is it spending only what's needed for the value delivered? |
| **Operational Excellence** | Can the team deploy, observe, and recover changes safely? |
| **Performance Efficiency** | Does it meet performance needs without over-provisioning? |

Use `scripts/azure_waf_scorer.py --workload-config workload.yaml` to score a workload against each pillar with concrete questions and recommendations.

See `azure-well-architected.md` for the per-pillar deep dive: 10-question checklist per pillar, common findings, remediation patterns.

## Cost optimization

### Cost levers from biggest to smallest

| Lever | Typical savings | Effort |
|-------|----------------|--------|
| **Right-sizing** (matching SKU to load) | 30-50% | Low |
| **Reserved Instances / Savings Plans** | 20-72% | Low (commitment) |
| **Autoscaling** (compute + DB) | 20-40% | Medium |
| **Spot Instances** (for batch / tolerant workloads) | up to 90% | Medium |
| **Storage tiering** (Hot/Cool/Cold/Archive) | 30-70% on storage | Low |
| **Egress reduction** (Front Door caching; CDN; private peering) | Variable, can be huge | Medium-High |
| **Decommission unused** (orphan disks, idle resources) | Variable | Low |
| **Region choice** (cheaper regions for non-latency-sensitive) | 10-25% | High (move) |

### Cost anti-patterns

- **Premium tier by default.** Premium App Service / Cosmos throughput / SQL DTUs that the workload doesn't need.
- **No autoscaling.** Always provisioned at peak. Easy 30-40% savings if added.
- **Egress through public internet.** Cross-region traffic via public endpoints is expensive; use VNet peering or Private Link.
- **Unused Log Analytics retention.** Keeping 730 days of debug logs at default rate.
- **Cosmos DB autoscale ceiling too high.** Pays for unused capacity.
- **Premium-tier Managed Disks for non-critical workloads.** Standard SSD is usually enough.

See `azure-cost-optimization.md` for the full lever catalog and detection patterns.

## End-to-end workflows

### Workflow: Design a new workload

1. **Understand requirements** — traffic, data scale, latency, region requirements, compliance.
2. **Pick compute** using the decision tree.
3. **Pick data stores** using the decision tree.
4. **Design networking** — VNet topology, Private Endpoints, gateway pattern.
5. **Design identity** — Managed Identities, RBAC scopes.
6. **Plan observability** — Log Analytics workspace, Application Insights, metrics.
7. **Estimate cost** with `scripts/azure_cost_estimator.py`.
8. **Validate against WAF** with `scripts/azure_waf_scorer.py`.
9. **Document** the architecture; share for review.

### Workflow: Review an existing Azure architecture

1. **Gather artifacts** — ARM/Bicep/Terraform code, network diagrams, service inventory.
2. **Run the validator** — `scripts/azure_architecture_validator.py --bicep ./infra/*.bicep` flags structural issues.
3. **Run WAF scorer** with the workload's actual config.
4. **Identify high-cost components** with the cost estimator.
5. **Produce findings** by pillar with severity and recommendation.

### Workflow: Migrate from AWS / GCP to Azure

1. **Map services** — most have equivalents but not 1:1 (e.g., SQS → Service Bus or Storage Queue depending on use; SNS → Event Grid; Lambda → Functions; DynamoDB → Cosmos DB).
2. **Re-evaluate the architecture** in Azure-native terms before lift-and-shift; some patterns work better here, others worse.
3. **Network parity** — VPC equivalent (VNet); IAM equivalent (Entra + RBAC); private connectivity (Private Endpoint).
4. **Data migration** — Azure Database Migration Service for many SQL/PG scenarios; Storage Migration Service for files.
5. **Cost re-estimate** — Azure pricing differs from AWS / GCP per-service; don't assume parity.

## Anti-patterns (Azure-specific)

- **Storing secrets in App Settings / env vars instead of Key Vault.** Use Key Vault references in App Settings.
- **Single-region production** for a tier-1 workload. Use paired regions + Traffic Manager / Front Door.
- **No Resource Locks on critical resources.** A single `az group delete` away from disaster.
- **Public storage account access enabled** ("AllowBlobPublicAccess"). Disable at storage-account level unless explicitly needed.
- **Premium SKU for everything.** Premium SQL / Premium App Service / Premium Cosmos used by default without need.
- **Shared keys / connection strings** for service-to-service auth instead of Managed Identity.
- **No diagnostic settings** sending logs to Log Analytics → no audit trail.
- **Hub-and-spoke without UDRs to force egress through firewall.** Defeats the firewall's purpose.
- **AKS without managed identities, RBAC, or network policies** — provisioning Kubernetes the easy way leaves obvious gaps.
- **Functions on Consumption plan for VNet integration.** Consumption can't do VNet; need Premium or Dedicated.
- **Mixing Cosmos consistency levels** without understanding the trade-off; Session is the right default for most.

## Tooling outputs

| Script | Input | Output |
|--------|-------|--------|
| `scripts/azure_architecture_validator.py` | Bicep file or YAML workload spec | Structural issues, anti-pattern findings, missing best-practice settings |
| `scripts/azure_cost_estimator.py` | YAML workload spec (services + tiers + scale) | Per-service monthly cost estimate, total, optimization opportunities |
| `scripts/azure_waf_scorer.py` | YAML workload spec | Score per WAF pillar, gap analysis, recommendations |

All scripts: stdlib only, argparse CLI, JSON or markdown output.
