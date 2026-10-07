# Cloud and Deployment Companion

Tier: focused, full.

## Select this companion when

The repository defines how the system is deployed and what it may reach:
infrastructure-as-code, IAM policies and role bindings, container and
orchestrator manifests, service-mesh or ingress configuration, serverless and
edge function definitions, event triggers, or the wiring of secrets and
runtime configuration.

This is a source audit of deployment definitions and of application code that
relies on them. It does not query a cloud account. A posture review of live
resources is a different exercise.

## Ground rules

```text
- Work only from definitions in the repository and from rendering them
  locally (template output, policy evaluation with dummy identities). Never
  call a cloud API or read live state.
- The deployed account may differ from the repository. A control you cannot
  see is unknown, not absent. If it decides the question, the lead is
  needs_validation and the owner check names the exact resource and setting.
- A broad permission is a finding only with a path: which workload holds it,
  how a lower-trust actor comes to act as that workload, and what they can
  then reach.
- Distinguish the application trusting the platform from the platform being
  misconfigured. Both matter; they have different fixes.
- Render overlays for every environment the repository defines. The
  production overlay is the one that counts, and the difference between
  overlays is often the finding.
```

## Hunting classes

### Workload identity with excess reach

A service, function, job, or pod whose role allows far more than its code
uses: wildcard actions or resources, the ability to pass or assume other
roles, write access to its own policy or deployment. Combine with any code
path that lets a caller steer the workload's requests.

### Cross-account and cross-tenant role assumption

Trust policies that let an external principal assume a role without a
condition binding it to the intended caller, missing external identifiers,
wildcard principals, and tenant-supplied role or resource names used without
validation.

### Authorization delegated to resource metadata

Application decisions based on tags, labels, names, or bucket paths that a
lower-trust actor can set. If writing the label is cheaper than gaining the
access it confers, the label is not a control.

### Unintended service or management exposure

Listeners, admin consoles, debug ports, orchestration APIs, dashboards, and
databases reachable from wider networks than intended: public load balancers,
permissive ingress rules, host networking, node ports, default-allow policies.

### Trusted proxy and mesh identity bypass

Application code that trusts an identity header or a network position because
a gateway or sidecar is expected to enforce it, while a route exists that
does not pass through that component: direct pod access, an internal service
port, a second ingress.

### Metadata service and internal endpoint reach

A workload that can be made to request instance metadata or internal control
endpoints on a caller's behalf, where the definitions do not restrict that
access. Pair with the core server-side fetch class.

### Container privilege and host access

Privileged mode, added capabilities, host namespaces, host path mounts,
writable runtime sockets, root users with a writable root filesystem, and
missing seccomp or equivalent profiles on workloads that process untrusted
input.

### Admission and policy path gaps

Policy enforced on one creation path and not another: a controller that
validates deployments but not jobs, namespaces exempt from policy, mutating
steps that run after validation, policy in audit-only mode.

### Namespace and label trust

Network policy, access rules, or scheduling that select on labels or
namespaces a tenant or low-privilege team can create or edit.

### Configuration precedence drift

Several sources set the same security-relevant value — defaults, files,
environment, flags, remote config — and the effective one is weaker than the
reviewed one. Follow precedence in code and in each overlay; look for a debug
or bypass flag reachable in production.

### Secrets crossing workload boundaries

Secrets mounted into workloads that do not need them, shared across
environments or tenants, written to logs or environment dumps, baked into
images, or readable through a broad secret-store policy.

### Credential renewal failure fallback

What the code does when a token cannot be refreshed, a certificate has
expired, or the secret store is unreachable: continue with a stale
credential, skip verification, or fall back to a static key.

### Object storage and signed URL policy

Buckets or containers with public or cross-account access, signed URLs with
long lifetimes or attacker-chosen keys and content types, upload policies that
allow overwriting other tenants' objects, and listings exposed alongside
objects.

### Event source identity

Functions and consumers triggered by queues, topics, storage events, or
webhooks that do not verify which source produced the event, so anyone able
to publish to the source — or to a look-alike — drives privileged code.

### Edge and origin disagreement

Rules at the edge (auth, path rewriting, header normalization, caching) that
the origin assumes were applied, with an origin still directly reachable or an
edge rule that normalizes differently from the application.

## Cross-cutting moves

- For each workload, write: identity, what that identity can do, who can
  influence its inputs, what it can reach on the network.
- Diff environments. A control present in staging and absent in production,
  or the reverse, deserves a unit.
- Look for the second door: a direct service address behind every gateway.
- Trace each secret from store to consumer to log.
- Check defaults: what applies to a new namespace, a new bucket, a new role
  when nobody sets anything.

## Evidence bar

- Confirmed needs the definition in the repository, the rendered effective
  configuration, and a local demonstration where one exists: a policy
  evaluation with dummy principals, a rendered manifest, a unit test of the
  application code that trusts the platform.
- Whether the live environment matches the repository is always the owner's
  to confirm. If the impact depends on that match, write the owner check and
  keep the lead as `needs_validation`.
- Permissive settings with no reachable actor or no meaningful resource are
  hardening notes.
- Severity follows reachable authority: control-plane or cross-tenant reach is
  high; a broad role on an isolated batch job is not, by itself.
