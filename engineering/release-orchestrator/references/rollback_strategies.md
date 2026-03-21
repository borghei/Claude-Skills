# Rollback Strategies

## Database Migration Rollbacks

### Reversible Migrations

Every `up()` migration must have a corresponding `down()` migration. Test both directions before release.

**Safe operations (easily reversible):**
- Add column (rollback: drop column)
- Add index (rollback: drop index)
- Add table (rollback: drop table)
- Add constraint with default (rollback: drop constraint)

**Dangerous operations (require careful planning):**
- Drop column - data loss, must backup first
- Rename column - both old and new code must work during transition
- Change column type - may lose precision or fail for existing data
- Drop table - irreversible without backup

### Expand-Contract Pattern

For schema changes that cannot be reversed atomically:

1. **Expand:** Add the new column/table alongside the old one
2. **Migrate:** Backfill data from old to new
3. **Transition:** Application reads from new, writes to both
4. **Contract:** Remove the old column/table after verification

This allows rollback at any stage without data loss.

### Migration Rollback Checklist

- [ ] Every migration has a tested `down()` function
- [ ] Data backups taken before destructive migrations
- [ ] Expand-contract pattern used for column renames/type changes
- [ ] Migration tested against production-sized dataset
- [ ] Rollback tested in staging environment
- [ ] Migration timeout configured (kill long-running migrations)

---

## Feature Flag Rollbacks

### Instant Disable

The simplest rollback: flip the flag to OFF. No deployment, no code change.

```yaml
# Before rollback
new_checkout_flow: true

# After rollback
new_checkout_flow: false
```

### Gradual Rollback

If issues appear at high percentages, reduce gradually:

1. Reduce from 100% to 50%
2. Monitor for 10 minutes
3. Reduce to 10%
4. Monitor for 10 minutes
5. Disable completely
6. Investigate root cause

### Flag Rollback Considerations

- Ensure flag evaluation is cached appropriately (avoid thundering herd on disable)
- Log flag state changes with timestamps for debugging
- Have a "kill all flags" emergency procedure
- Test the OFF path regularly (it may have rotted)

---

## Git Revert Strategies

### Single Commit Revert

```bash
git revert <commit-hash>
git push origin main
```

Creates a new commit that undoes the specified commit. Safe and traceable.

### Range Revert

```bash
# Revert commits C, D, E (from oldest to newest)
git revert --no-commit C^..E
git commit -m "revert: undo commits C through E due to regression"
```

Use `--no-commit` to combine multiple reverts into a single commit.

### Merge Commit Revert

```bash
# -m 1 means keep the first parent (usually main)
git revert -m 1 <merge-commit-hash>
```

Reverting a merge commit requires specifying which parent to keep.

### Revert Best Practices

- Always revert in production branch first, then propagate
- Write descriptive revert messages explaining WHY
- After reverting, create a fix branch from the reverted code
- Never force-push to shared branches as a rollback mechanism

---

## Infrastructure Rollback

### Container/Kubernetes Rollback

```bash
# Kubernetes: roll back to previous revision
kubectl rollout undo deployment/my-app

# Roll back to specific revision
kubectl rollout undo deployment/my-app --to-revision=3

# Check rollout history
kubectl rollout history deployment/my-app
```

### Serverless Rollback

```bash
# AWS Lambda: point alias to previous version
aws lambda update-alias \
  --function-name my-function \
  --name production \
  --function-version 42

# Revert to previous traffic split
aws lambda update-alias \
  --function-name my-function \
  --name production \
  --routing-config '{"AdditionalVersionWeights":{}}'
```

### Load Balancer Rollback

Switch target group to point at the old deployment:

1. Keep the old target group registered for 30 minutes post-deploy
2. If rollback needed, update listener rules to old target group
3. Drain connections gracefully (deregistration delay)

---

## Communication Templates

### Rollback Initiated

```
Subject: [ROLLBACK] v{version} rollback initiated

Team,

We are rolling back release v{version} due to:
- Issue: {brief description}
- Impact: {affected users/services}
- Detection: {how it was detected}

Current status:
- Rollback started at {time}
- Expected completion: {time}
- Incident commander: {name}

We will send an update when rollback is complete.
```

### Rollback Complete

```
Subject: [RESOLVED] v{version} rollback complete

Team,

Rollback of v{version} is complete.

Timeline:
- {time}: Issue detected
- {time}: Rollback initiated
- {time}: Rollback verified
- {time}: Services restored to v{previous_version}

Next steps:
- Root cause analysis in progress
- Fix branch: {branch name}
- Expected re-release: {date/time}

Post-incident review scheduled for {date/time}.
```

### Customer-Facing Communication

```
Subject: Service Update - {date}

We identified an issue with a recent update that affected {service}.
The issue has been resolved and all systems are operating normally.

What happened: {user-friendly description}
Impact: {what users experienced}
Duration: {start time} to {end time}
Resolution: We reverted the update and restored service.

We apologize for any inconvenience and are taking steps to prevent
similar issues in the future.
```
