# Development Workflow

**Repository:** claude-code-skills
**Branch Strategy:** single-trunk — short-lived type-branch → `main` via PR. There is no `dev` branch.

---

## Quick Start

```bash
# 1. Always start from an up-to-date main
git checkout main
git pull origin main

# 2. Create a type-prefixed branch
git checkout -b feat/agents-{name}

# 3. Work and commit (Conventional Commits)
git add .
git commit -m "feat(agents): implement {name}"

# 4. Push (set upstream on first push)
git push -u origin feat/agents-{name}

# 5. Open a PR against main
gh pr create --base main --head feat/agents-{name}

# 6. After review/CI, squash-merge and delete the branch
gh pr merge --squash --delete-branch
```

---

## Branch Structure

### main

- The single integration branch — all work merges here via PR.
- Protected: PR required, no direct pushes.
- Tagged for releases (`vX.Y.Z`).

### Working branches

Short-lived, branched from `main`, deleted after merge. Name them with a Conventional-Commit **type prefix**:

```bash
feat/{area}-{component}      # New features / skills / agents
fix/{issue}-{description}    # Bug fixes
docs/{component}             # Documentation
chore/{description}          # Tooling, CI, housekeeping
ci/{description}             # CI/CD workflow changes
perf/{description}           # Performance
refactor/{component}         # Refactors
test/{feature}               # Tests
hotfix/{description}         # Urgent production fixes
```

**Examples:** `feat/agents-cfo-advisor` · `fix/42-broken-relative-paths` · `docs/installation-guide` · `chore/regenerate-manifest`

---

## Daily Workflow

```bash
# Start new work
git checkout main && git pull origin main
git checkout -b feat/agents-data-scientist

# Make changes, then stage + commit with a conventional message
git add agents/engineering/cs-data-scientist.md
git commit -m "feat(agents): implement cs-data-scientist agent

- Add YAML frontmatter with required fields
- Document 4 workflows
- Integrate with data-analysis Python tools

Closes #25"

# Push and open the PR against main
git push -u origin feat/agents-data-scientist
gh pr create --base main --head feat/agents-data-scientist
```

After merge, clean up:

```bash
git checkout main && git pull origin main
git branch -d feat/agents-data-scientist
```

---

## Pull Requests

PRs target `main` directly. A good PR body states what changed and how it was verified:

```bash
gh pr create --base main --head feat/agents-data-scientist \
  --title "feat(agents): implement cs-data-scientist agent" \
  --body "Closes #25

## Summary
Implements the data-scientist agent with ML-pipeline workflows.

## Changes
- Created cs-data-scientist.md
- Added 4 workflows, integrated 3 Python tools

## Verification
- [x] YAML frontmatter valid
- [x] Relative paths resolve
- [x] Python tools run
- [x] Conventional commit format"
```

**Merge:** squash-merge is preferred for a clean history.

```bash
gh pr merge --squash --delete-branch
```

---

## Releases

There is no `dev → main` release PR. A release is simply an annotated tag on `main`:

```bash
git checkout main && git pull origin main
git tag -a v4.11.0 -m "v4.11.0 — <summary>"
git push origin v4.11.0
```

(`cli-v*` tags trigger the npm publish workflow; `vX.Y.Z` tags do not.)

---

## Quality Checks

```bash
# No secrets staged
git diff --cached | grep -iE '(api[_-]?key|secret|password|token)'

# Python compiles (stdlib-only tools)
python3 -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

# After adding/removing/renaming a skill, regenerate the catalogs
python scripts/build_manifest.py   # CI also does this on push to main
```

---

## Common Scenarios

**New skill / agent** — `feat/…` branch, add the skill folder (`SKILL.md` + `scripts/` + `references/`), run `build_manifest.py`, PR to `main`.

**Bug fix** — `fix/{issue}-…` branch, reference the issue in the commit, PR to `main`.

**Docs** — `docs/…` branch, PR to `main`.

**Hotfix** — `hotfix/…` branch from `main`, PR to `main` with a `P0`/`hotfix` label.

---

## Best Practices

**DO** ✅ — start from an up-to-date `main`; use Conventional Commits; one logical change per PR; reference issues; squash-merge; delete merged branches; regenerate manifests after skill changes.

**DON'T** ❌ — push directly to `main` (blocked by protection); commit secrets; mix unrelated changes; leave stale branches; skip the quality checks.

---

## Related Documentation

- **Git Workflow Standards:** [standards/git/git-workflow-standards.md](../standards/git/git-workflow-standards.md)
- **Quality Standards:** [standards/quality/quality-standards.md](../standards/quality/quality-standards.md)
- **Main CLAUDE.md:** [../CLAUDE.md](../CLAUDE.md)

---

## FAQ

**Q: Is there a `dev` branch?**
A: No. The repo is single-trunk — branch from `main`, PR back to `main`.

**Q: Why can't I push to `main` directly?**
A: Branch protection requires a PR. Create a type-branch and open a PR.

**Q: What if I'm the only contributor?**
A: Still use a PR — it gives a review checkpoint, runs CI, and keeps clean history.

**Q: How do I cut a release?**
A: Tag `main` with `vX.Y.Z` and push the tag (see [Releases](#releases)).
