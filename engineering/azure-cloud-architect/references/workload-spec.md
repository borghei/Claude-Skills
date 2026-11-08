# Workload Spec (YAML) Reference

All three scripts read the same YAML file. Unknown keys are ignored; a missing boolean counts as
`false`, so a sparse spec scores low rather than failing. Full example:
`assets/sample_workload.yaml` (a sound tier-1 workload) and `assets/sample_workload_flawed.yaml`.

The scripts use a small built-in YAML parser: plain mappings, lists of mappings, scalars. Anchors,
multi-line strings and flow style (`[a, b]`) are not supported.

## Top level

| Key | Type | Read by | Meaning |
|-----|------|---------|---------|
| `name` | string | all | Workload name in reports |
| `tier` | 1/2/3 | WAF, validator | 1 = business-critical: zone redundancy and multi-region become critical checks |

## compute

| Key | Read by | Notes |
|-----|---------|-------|
| `type` | cost | `app-service`, `aks` or `vmss` (others are not priced) |
| `sku`, `instances` | cost | App Service SKU (`P1v3`…) and count; for `vmss`, `sku` + `count` |
| `sku_tier`, `node_pool.{sku,count,reserved}` | cost | AKS control-plane tier (`free`/`standard`/`premium`) and node pool |
| `zone_redundant`, `multi_region`, `autoscale` | WAF, validator | booleans |

## data (list)

Each item: `service` = `sql-db` (`tier`, `vcores`, `dtu_model`), `cosmos` (`mode` manual/autoscale/serverless,
`max_ru_per_sec`, `avg_utilization`, `monthly_ru_millions`, `storage_gb`), `storage` (`tier`, `size_gb`,
`avg_access_days`), `pg-flex` (`tier`), `redis` (`sku`). Every item may set `zone_redundant`, `ha`,
`backup_tested` and `public_access` (booleans read by the WAF scorer and validator).

## network

`vnet`, `private_endpoints`, `nsg_least_privilege` (booleans); `front_door.request_millions_per_month`,
`app_gateway.capacity_units`, `egress_gb_per_month` (priced by the cost estimator).

## identity, security, observability

- `identity.managed_identity` (bool), `identity.rbac_scope` (`resource`, `resource_group`, `subscription`, `management_group`)
- `security.key_vault`, `mfa_enforced`, `defender_for_cloud`, `encryption_at_rest` (default true), `min_tls_1_2` (default true)
- `observability.log_analytics` (bool), `ingest_gb_per_day` (priced), `alerts`, `slo_alerts`

## reliability, operations, cost, performance (WAF checklist booleans)

- `reliability.rpo_minutes`, `reliability.rto_minutes`
- `operations.`: `iac`, `ci_cd`, `staging_env`, `runbooks`, `gradual_rollout`, `deployment_slots`, `on_call_defined`, `health_probes`, `retry_policies`, `azure_policy`, `blameless_pir`, `chaos_last_run`
- `cost.`: `right_sized`, `reservations_purchased`, `spot_used`, `storage_tiered`, `devtest_schedule`, `orphans_cleaned`, `db_throughput_right_sized`, `log_retention_tuned`, `budgets_configured`
- `performance.`: `caching`, `cdn_assets`, `load_tested`, `slos_defined`, `async_io`, `db_optimized`, `data_partitioned`, `payload_reviewed`, `profiled`

Each boolean is a claim about the workload. The WAF score is only as true as these claims; ask for
evidence (a dashboard, a runbook link, a restore-test date) before marking one `true`.
