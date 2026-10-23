# Deployment Strategies

Read this when choosing how to release a service, setting rollback thresholds, or reviewing a plan from `scripts/deployment_manager.py`.

## Choosing a Strategy

`deployment_manager.py` applies these rules in order. The first that matches wins; `--strategy` overrides it and the plan records that the inputs pointed elsewhere.

| # | Condition | Strategy | Why |
|---|-----------|----------|-----|
| 1 | `stateful: true` | Rolling, one pod at a time | Two fleets would share or duplicate state; a StatefulSet partition replaces pods in order |
| 2 | Rollback tolerance 2 min or less and capacity can double | Blue-green | Rollback is one traffic switch back to an untouched fleet |
| 3 | User-facing, medium or high risk, 20 rps or more | Canary | Enough traffic to judge a small slice before everyone sees it |
| 4 | High risk, low traffic, capacity can double | Blue-green | Too few requests for a canary signal; test a full green stack instead |
| 5 | Everything else | Rolling | Cheapest; readiness gates and surge capacity are enough for low-risk or internal changes |

A breaking schema change does not change the pick. It produces a warning, because every strategy runs old and new code against the same database for some time.

| Strategy | Extra capacity | Rollback time | Main risk |
|----------|----------------|---------------|-----------|
| Rolling | 25% surge | Minutes (pods roll back one by one) | Mixed versions serve traffic during the roll |
| Blue-green | 100% for the bake window | Seconds | Cost, and both stacks share the database |
| Canary | One extra ReplicaSet | Seconds (weight to 0) | Needs per-version metrics and a traffic router |
| Feature flag | None | Instant | Flag debt; code for both paths ships together |

Feature flags complement any of the three: deploy dark with a rolling update, then release by flag.

## Canary Ladder and Bake Time

| Risk | Traffic steps | Minimum bake per step |
|------|---------------|-----------------------|
| High | 1%, 5%, 25%, 50%, 100% | 15 min |
| Medium | 5%, 25%, 50%, 100% | 10 min |
| Low | 10%, 50%, 100% | 5 min |

Bake time is a statistical floor, not a ritual. Each step needs enough canary requests to tell a 1% error rate from noise; the tool targets 2,000 requests per step:

```
bake_minutes = max(minimum, ceil(2000 / (traffic_rps * pct / 100) / 60)), capped at 60
```

At 400 rps a 5% step needs under 2 minutes of traffic, so the 10-minute floor applies. At 30 rps a 1% step would need about 111 minutes; the tool caps it at 60 and warns that early steps only work as smoke tests. Below 20 rps a canary says little, which is why rule 3 requires that much traffic.

Compare the canary against the stable version over the same window, not against last week. Label metrics by version or ReplicaSet; fleet-wide averages hide a bad 5% slice.

## Spec Validation

`deployment_manager.py` rejects a spec, with a one-line error, unless it is a JSON object whose `service` is a Kubernetes name (RFC 1123: lowercase letters, digits and `-`, at most 63 characters, alphanumeric at both ends), whose `version` and `previous_version` are image tags (`[A-Za-z0-9_+][A-Za-z0-9._+-]{0,127}`), whose numbers are finite and non-negative, and whose health paths are plain URL paths. These values end up in copy-paste runbook commands, so nothing else is allowed through. A `previous_version` equal to `version` produces a warning.

## Health Checks

| Probe | Path | Settings the tool emits | Purpose |
|-------|------|-------------------------|---------|
| Startup | liveness path | period 5 s, failure threshold sized to 1.5x `startup_seconds` | Keeps liveness from killing slow starters |
| Liveness | liveness path | period 10 s, timeout 2 s, 3 failures | Restarts a deadlocked process. Never check downstream dependencies here |
| Readiness | readiness path | period 5 s, timeout 2 s, 3 failures, 1 success | Removes a pod from load balancing; may check critical dependencies |
| Smoke test | readiness plus one read-only business call | before traffic | Proves the new version does real work |

Set `minReadySeconds` (the tool uses 30) so a pod that passes readiness once and then crashes does not count as available.

## Automatic Rollback Triggers

Thresholds come from the spec's `baseline` and `slo`:

| Signal | Threshold | Window |
|--------|-----------|--------|
| Error rate (5xx / total) | the larger of 2x baseline and baseline + 0.5 points, capped at the SLO | 2 consecutive 1-min windows |
| p99 latency | 1.5x baseline, capped at the SLO | 3 consecutive 1-min windows |
| New pod readiness | not ready 5 min after start | any pod |
| Container restarts | 2 or more on a new pod | 10 min |

Consecutive windows prevent a single spike from rolling back a good release. Capping at the SLO stops a noisy baseline from allowing an SLO breach. Without a `baseline` and `slo` in the spec the tool uses example values and says so; real numbers matter.

Wire these into the rollout controller (Argo Rollouts `AnalysisTemplate`, Flagger metric checks, or a pipeline step that queries Prometheus) so rollback does not wait for a human.

## Rollback Runbooks

**Canary:** set the canary weight to 0 (`kubectl argo rollouts abort <service>`). Stable never stopped serving.

**Blue-green:** point the router or Service selector back at blue. Keep blue running for at least 30 minutes, or six times the rollback tolerance, after the switch.

**Rolling:** `kubectl rollout undo deployment/<service>` and watch `kubectl rollout status`. This takes as long as the roll forward did, which is why it does not suit a tolerance under a few minutes.

After any rollback: confirm error rate and latency are back at baseline within 5 minutes, freeze further deploys of the service, record trigger, time and version, and keep the failed version's logs.

## Database Changes

Use expand and contract so both versions work against the schema at every point:

1. **Expand:** add columns or tables, nullable or with defaults. Deploy code that writes both shapes.
2. **Migrate:** backfill in batches.
3. **Contract:** in a later release, once no running version reads the old shape, drop it.

Never roll a schema back by hand during an incident. Roll the code back to a version that works with the current schema.

## Anti-Patterns

- Canary on a service with 2 requests a minute: the signal never arrives, so the canary is a slow rolling update.
- Rollback thresholds set from memory rather than the service's baseline.
- Deleting blue as soon as green passes its smoke test.
- A liveness probe that calls the database, so a database blip restarts every pod at once.
- Shipping a breaking migration and code change in the same release.
