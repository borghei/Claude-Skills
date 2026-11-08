# Merge Risk Classification

How to classify a pull request as a two-way door (reversible by revert) or a
one-way door (a revert does not restore the previous state), estimate its blast
radius, and write a rollback plan that works under pressure.

## The test

> After this merges and deploys, if I revert the commit and redeploy, is the
> world exactly as it was before?

- **Yes** → two-way door. "Revert the PR" is the whole rollback plan.
- **No** → one-way door. Something persisted, was published, or was deleted,
  and the revert only removes the code that did it.
- **Yes, unless...** → conditional. Reversible in the normal case, one-way in a
  specific failure mode that the body must name.

## One-way categories

| Category | Why a revert does not undo it | Typical paths |
|----------|-------------------------------|---------------|
| Schema migration | The schema change stays; reverted code may not run against it (dropped column, renamed table, new NOT NULL) | `migrations/`, `db/migrate/`, `alembic/versions/`, `V12__*.sql` |
| Public API / contract | External clients may already have shipped code against the new shape; removing a field again breaks them a second time | `openapi.yaml`, `*.proto`, `*.graphql`, `api/v2/`, published SDKs |
| Persisted format | Data written in the new format stays in databases, caches, queues and files after the revert; old readers choke on it | event schemas, `.avsc`, cache key formats, file formats |
| Data deletion | Deleted rows, objects or files do not come back with a revert | purge/retention jobs, backfills that overwrite, `DELETE`, `TRUNCATE` |
| External side effects | Emails sent, payments captured, webhooks fired, third-party state created | notification campaigns, billing changes, partner integrations |

## Conditional categories

| Category | Normally | One-way when |
|----------|----------|-------------|
| Infrastructure (Terraform, Helm, k8s) | Re-apply the previous version | The plan destroys or replaces a stateful resource (DB, volume, bucket, DNS zone) |
| Auth and security | Revert restores the old checks | A weaker check was live long enough to be exploited; tokens were issued under new rules |
| Dependencies | Revert the lockfile | A major bump ran a data migration on startup (ORMs, search engines, queues) |
| CI / deploy pipeline | Revert the workflow | The broken pipeline is the one that would deploy the revert |
| Config and feature flags | Flip the flag or config back | The flag default changed for everyone at merge, or the flag gates a one-way action |

The body must say which condition applies and why it does not here (or that it
does, in which case the PR is one-way).

## Signals in the diff, not just the paths

Paths tell you a migration exists; the diff tells you what it does. Treat
these added lines as one-way regardless of where they live:

| Signal | Why |
|--------|-----|
| `DROP TABLE` / `DROP COLUMN` / `drop_column(...)` | Data is gone |
| `TRUNCATE`, `DELETE FROM x;` with no `WHERE` | Data is gone |
| `ALTER TABLE ... RENAME` | Old code reading the old name breaks during a rolling deploy |
| `ALTER COLUMN ... TYPE`, `SET NOT NULL` | Can rewrite or lock a large table; old writers fail |
| Removed field in a `.proto` / OpenAPI / GraphQL schema | Every client using it breaks |

Destructive statements inside a migration's `downgrade()` / `down` block are
expected and not flagged: they only run during a rollback.

## Making one-way changes safer [PROVEN]

### Expand / contract (parallel change)

Split a breaking change into reversible steps, each its own PR:

1. **Expand:** add the new column/field/endpoint alongside the old one. Additive,
   nullable, unused. Reversible in practice (leave it in place).
2. **Migrate:** backfill and dual-write. Reads still use the old path.
3. **Switch:** reads move to the new path, behind a flag if possible. Reversible
   by flag.
4. **Contract:** remove the old column/field once nothing reads it, after a
   deprecation window for external clients. This is the only one-way step, and
   by now it is boring.

A PR that does expand and contract in one go turns four two-way doors into one
one-way door.

### Other techniques

- **Feature flag the behaviour, not just the UI.** The off switch is the rollback.
- **Soft delete first.** Mark rows deleted, purge in a later job with its own review.
- **Version the endpoint** instead of changing the existing one.
- **Dry-run counts.** Destructive jobs print "would delete N rows" in staging and
  the PR quotes N.
- **Backups with a tested restore.** "We have backups" is not a plan; "restore of
  table X from the 02:00 snapshot takes ~12 minutes, last tested 2026-10-14" is.

## Blast radius

State who or what is affected if the change is wrong, in user terms:

| Level | Meaning | Example |
|-------|---------|---------|
| Contained | One code path, one screen, or internal-only | Admin report formatting |
| Module | One service or feature area | Invoice rendering |
| Cross-cutting | Several services or every request of one kind | All authenticated API calls |
| Platform-wide | Every user, every request, or the deploy pipeline itself | Base image, auth middleware, CI |

`risk_classifier.py` estimates the level from the number of top-level
directories touched (tests and docs excluded) and bumps it for contract and
pipeline changes. Treat the estimate as a floor; you know your coupling better
than path counting does.

## Writing the rollback plan

A rollback plan is read by someone stressed, possibly not the author, possibly
at night. It needs:

1. **Trigger:** what signal says roll back (error rate, failed check, a named alert).
2. **Steps:** exact commands or clicks, in order.
3. **Owner:** who is allowed and able to run them.
4. **Duration:** roughly how long, and whether there is downtime.
5. **End state:** what data or clients are left in which state afterwards.

Weak: "Can be rolled back if needed."

Strong: "If invoice errors exceed 1% for 5 minutes, revert the PR (the columns
stay, nothing reads them). If the backfill itself fails, on-call runs
`manage.py migrate customers 0047`, which drops both new columns in about 2 s;
`full_name` is never modified, so no data is lost."

## Classification mistakes that recur

- **"Low risk" as a classification.** Risk is likelihood times impact; door is
  reversibility. A low-likelihood one-way change still needs a plan.
- **Counting only the code.** A two-line change that flips a flag default for
  every tenant is platform-wide.
- **Forgetting the rolling deploy.** During a deploy old and new code run
  together against one schema. A rename is breaking for that window even if
  both versions are individually correct.
- **Trusting the down-migration.** Down-migrations are rarely tested and often
  lossy (drop the column that held the new data). Say whether yours was run.
