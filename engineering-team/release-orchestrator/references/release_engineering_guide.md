# Release Engineering Guide

## Release Strategies

### Rolling Deployment

Deploy new versions incrementally across server instances. At any point, both old and new versions serve traffic. No downtime.

**When to use:** Stateless services, horizontally scaled applications.

**Process:**
1. Deploy to 1 instance, monitor for errors
2. If healthy after 5 minutes, deploy to 25% of fleet
3. Monitor key metrics (error rate, latency p99, CPU)
4. Continue rolling at 25% increments
5. Full rollout after all cohorts are stable

**Rollback:** Stop the roll and redeploy the previous version to affected instances.

### Blue-Green Deployment

Maintain two identical environments. Route all traffic from blue (current) to green (new) in a single switch.

**When to use:** Zero-downtime requirements, database schema compatibility between versions.

**Process:**
1. Deploy new version to the idle (green) environment
2. Run smoke tests against green
3. Switch load balancer / DNS to green
4. Monitor for 15-30 minutes
5. Decommission blue or keep as rollback target

**Rollback:** Switch traffic back to blue. Instant, sub-second recovery.

### Canary Deployment

Route a small percentage of traffic to the new version. Compare metrics against the baseline before expanding.

**When to use:** High-risk changes, user-facing features, performance-sensitive paths.

**Process:**
1. Deploy canary alongside production
2. Route 1-5% of traffic to canary
3. Compare error rates, latencies, business metrics
4. If canary is healthy for 30+ minutes, expand to 25%, then 50%, then 100%
5. Kill canary infrastructure after full rollout

**Metrics to compare:** Error rate, p50/p95/p99 latency, CPU/memory, business KPIs.

### Feature Flag Deployment

Deploy code to production with features behind flags. Enable features independently of deployment.

**When to use:** Long-lived feature branches, A/B testing, progressive rollouts, kill switches.

**Process:**
1. Merge feature behind a flag (default: OFF)
2. Deploy to production (no user impact)
3. Enable flag for internal users / beta testers
4. Gradually roll out: 1% -> 10% -> 50% -> 100%
5. Remove flag and dead code after full rollout

**Rollback:** Disable the flag. Instant, no deployment required.

---

## Semantic Versioning Deep Dive

Semantic Versioning (SemVer) uses the format `MAJOR.MINOR.PATCH`:

| Component | When to Increment | Example |
|---|---|---|
| MAJOR | Incompatible API changes | Removing an endpoint, changing auth flow |
| MINOR | Backward-compatible new functionality | New endpoint, new optional parameter |
| PATCH | Backward-compatible bug fixes | Fix null pointer, correct calculation |

### Pre-release Versions

Pre-release identifiers follow the patch: `1.2.0-alpha.1`, `1.2.0-beta.3`, `1.2.0-rc.1`.

**Precedence:** `1.0.0-alpha.1` < `1.0.0-alpha.2` < `1.0.0-beta.1` < `1.0.0-rc.1` < `1.0.0`

### Build Metadata

Build metadata follows `+`: `1.2.0+build.42`. Build metadata does NOT affect version precedence.

### Version Zero

`0.x.y` is for initial development. Anything may change at any time. The public API is not stable.

### Rules

- Once a versioned package is released, that version MUST NOT be modified
- MAJOR version zero is for rapid iteration; treat every minor bump as potentially breaking
- Deprecate before removing: announce deprecation in MINOR, remove in next MAJOR

---

## Conventional Commits Specification

Format: `<type>[optional scope][!]: <description>`

### Types

| Type | Purpose | SemVer Impact |
|---|---|---|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | None |
| `style` | Formatting, missing semicolons | None |
| `refactor` | Code change that neither fixes a bug nor adds a feature | None |
| `perf` | Performance improvement | PATCH |
| `test` | Adding or correcting tests | None |
| `build` | Build system or external dependencies | None |
| `ci` | CI configuration | None |
| `chore` | Other changes that don't modify src or test files | None |
| `revert` | Reverts a previous commit | Depends on reverted commit |

### Breaking Changes

Two ways to indicate breaking changes:

1. **Exclamation mark:** `feat!: redesign authentication` or `feat(auth)!: require API keys`
2. **Footer:** Include `BREAKING CHANGE: description` in the commit body

Both result in a MAJOR version bump.

### Scope

Optional, in parentheses: `feat(parser): add support for arrays`. Use module names, component names, or feature areas.

---

## Release Branch Management

### Git Flow

- `main` - production-ready code, tagged with versions
- `develop` - integration branch for features
- `feature/*` - individual feature branches
- `release/*` - release preparation
- `hotfix/*` - production fixes

### Trunk-Based Development

- `main` - single source of truth, always deployable
- Short-lived feature branches (< 2 days)
- Feature flags for incomplete work
- Release branches cut from main for stabilization

### Release Branch Workflow

1. Cut `release/1.3.0` from `develop` (or `main` in trunk-based)
2. Only bug fixes and release prep on the branch
3. No new features after cut
4. Bump version, generate changelog
5. Merge to `main`, tag, deploy
6. Back-merge to `develop`

---

## Hotfix Workflows

### Standard Hotfix

1. Branch from latest release tag: `git checkout -b hotfix/1.2.1 v1.2.0`
2. Apply the minimal fix (smallest possible change)
3. Bump PATCH version
4. Generate changelog entry
5. Run full test suite
6. Merge to `main`, tag `v1.2.1`
7. Back-merge to `develop` / current release branch

### Emergency Hotfix

Same as standard but with abbreviated testing:
1. Run only affected test suites
2. Deploy to canary (1% traffic) for 15 minutes
3. If stable, roll to 100%
4. Post-deploy: run full regression suite
5. If regression found, revert and apply proper fix

### Hotfix Rules

- Never include unrelated changes in a hotfix
- Always branch from the release tag, not from HEAD
- Hotfixes bypass feature freeze windows
- Document the incident that triggered the hotfix
