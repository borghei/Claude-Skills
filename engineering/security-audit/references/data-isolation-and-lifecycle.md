# Data Isolation and Lifecycle Companion

Tier: full.

## Select this companion when

The system keeps data for more than one tenant, team, or user in shared
infrastructure, or data moves through copies with their own lifetimes: caches,
search indexes, object storage, analytics pipelines, exports, backups,
replicas, migrations, soft deletion, retention, restore.

The core `Access control` class asks whether the primary read and write paths
check the right thing. This file follows the data after that: every other
reader, every derived copy, and every point in the record's life where the
rule can lapse.

## Ground rules

```text
- State the isolation rule in one sentence: which principal may see which
  record, keyed on what. Then find each place the code must apply it.
- Enforcement lives in the query, the key, or the storage policy. A tenant
  column that the query does not filter on is documentation.
- Follow copies. For every record type, list where it is duplicated or
  derived: cache, index, queue, log, analytics event, export file, backup,
  replica. Each copy needs the rule or needs to be unreachable.
- Follow time. Check the rule at creation, update, share, unshare, role
  change, deletion, retention expiry, and restore.
- Demonstrate with two dummy tenants in a local store. Never read real
  customer data or a shared environment.
```

## Hunting classes

### Missing tenant or owner scope

A query, lookup, or update that selects by record identifier alone where the
rule requires tenant or owner as well. Check single reads, lists, counts,
joins, bulk operations, background jobs, and admin or support tools.

### Composite key and namespace collision

Keys built by joining parts without an unambiguous separator, truncation or
case-folding that makes two tenants' keys equal, slugs or usernames reusable
after deletion, and identifiers unique per tenant used in a global namespace.

### Policy and query disagreement

The authorization layer decides on one representation and the data layer
fetches by another: a policy evaluated on the parent while the query returns
children, a filter applied after pagination, row-level rules bypassed by a
raw query or a privileged connection.

### Access by possession of a link or key

Object keys, file URLs, or signed links that grant access by possession:
predictable or enumerable paths, links that outlive the permission, a
signature covering a prefix instead of an object, and a shared bucket with no
per-tenant policy.

### Search, cache, and index drift

A derived store returns records the primary store would refuse: indexes built
without access fields, cache keys missing the principal or tenant, results
filtered in the application after ranking, permissions changed in the source
and never propagated.

### Logs, analytics, and traces as readers

Sensitive fields copied into logs, events, traces, error reports, or support
dashboards that a wider audience can read, or that a tenant can query through
an analytics feature.

### Enumeration and aggregate oracles

Counts, totals, autocomplete, uniqueness errors, and sequential identifiers
that reveal the existence or size of another tenant's data without returning
the records.

### Export and backup scope

Export, report, and backup jobs that run with a privileged connection and
select more than the requester may see, or whose output lands somewhere with
weaker access than the source.

### Import and restore authority

An import, sync, or restore that writes records with identifiers, owners, or
tenants taken from the file, letting the caller place or overwrite data
outside their scope.

### Migration defaults and ownership

A schema or data migration that assigns a default owner, tenant, or
visibility to existing rows, backfills permissions too broadly, or leaves a
window in which the new column is unset and the check passes.

### Replica and backup boundary drift

Read replicas, warehouses, staging copies, and backups that hold production
data under different access rules, encryption, or retention than the primary.

### Soft delete bypass

Records marked deleted that remain reachable by direct identifier, through a
relationship, in search, in exports, or by an endpoint that forgets the
filter.

### Stale authorization in derived copies

Access removed at the source — unshare, role change, membership removal,
tenant offboarding — while tokens, cached decisions, materialized views, or
queued jobs continue to act on the old grant.

### Retention and queued work overrun

Data that outlives its promised lifetime in queues, dead-letter stores,
temporary files, or scheduled jobs, and work queued before a deletion that
recreates or re-exposes the record afterwards.

### Restore of invalid state

Undelete, version rollback, or backup restore that brings back a record with
its old owner, sharing, or validation state without applying current rules.

## Cross-cutting moves

- Build the copy map for each sensitive record type, and check each copy's
  key and its reader.
- Run every list and search path as tenant B looking for tenant A's fixture.
- Change a permission, then exercise each derived store before any refresh.
- Delete a record, then look for it by identifier, by relation, in search, in
  export, and after restore.
- Find the privileged connection and list every code path that uses it.

## Evidence bar

- Confirmed needs a local two-tenant reproduction: tenant B's request and
  tenant A's fixture record, field, or existence returned or changed.
- Where isolation depends on storage policy, database roles, or
  infrastructure not in the repository, record `needs_validation` and name
  the policy the owner should check.
- Exposure of a principal's own data to themselves, or of non-sensitive
  metadata, is not an isolation failure.
- Severity follows what crosses the boundary and how far: arbitrary
  cross-tenant read or write is high; existence of a record is usually low.
