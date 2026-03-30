---
name: git-worktree-manager
description: >
  Manage parallel development with Git worktrees. Covers worktree creation with
  port allocation, environment sync, branch isolation for multi-agent workflows,
  cleanup automation, and Docker Compose integration. Use when working on
  multiple branches simultaneously, running parallel CI validations, or
  isolating agent workspaces.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: developer-tooling
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: git-worktree
---
# Git Worktree Manager

**Tier:** POWERFUL
**Category:** Engineering / Developer Tooling
**Maintainer:** Claude Skills Team

## Overview

Manage parallel development workflows using Git worktrees with deterministic naming, automatic port allocation, environment file synchronization, dependency installation, and cleanup automation. Optimized for multi-agent workflows where each agent or terminal session owns an isolated worktree with its own ports, environment, and running services.

## Keywords

git worktree, parallel development, branch isolation, port allocation, multi-agent development, worktree cleanup, Docker Compose worktree, concurrent branches

## Core Capabilities

### 1. Worktree Lifecycle Management
- Create worktrees from new or existing branches with deterministic naming
- Copy .env files from main repo to new worktrees
- Install dependencies based on lockfile detection
- List all worktrees with status (clean/dirty, ahead/behind)
- Safe cleanup with uncommitted change detection

### 2. Port Allocation
- Deterministic port assignment per worktree (base + index * stride)
- Collision detection against running processes
- Persistent port map in `.worktree-ports.json`
- Docker Compose override generation for per-worktree ports

### 3. Multi-Agent Isolation
- One branch per worktree, one agent per worktree
- No shared state between agent workspaces
- Conflict-free parallel execution
- Task ID mapping for traceability

### 4. Cleanup Automation
- Stale worktree detection by age
- Merged branch detection for safe removal
- Dirty state warnings before deletion
- Bulk cleanup with safety confirmations

## When to Use

- You need 2+ concurrent branches open with running dev servers
- You want isolated environments for feature work, hotfixes, and PR review
- Multiple AI agents need separate workspaces that do not interfere
- Your current branch is blocked but a hotfix is urgent
- You want automated cleanup instead of manual `rm -rf` operations

## Quick Start

### Create a Worktree

```bash
# Create worktree for a new feature branch
git worktree add ../wt-auth -b feature/new-auth main

# Create worktree from an existing branch
git worktree add ../wt-hotfix hotfix/fix-login

# Create worktree in a dedicated directory
git worktree add ~/worktrees/myapp-auth -b feature/auth origin/main
```

### List All Worktrees

```bash
git worktree list
# Output:
# /Users/dev/myapp              abc1234 [main]
# /Users/dev/wt-auth            def5678 [feature/new-auth]
# /Users/dev/wt-hotfix          ghi9012 [hotfix/fix-login]
```

### Remove a Worktree

```bash
# Safe removal (fails if there are uncommitted changes)
git worktree remove ../wt-auth

# Force removal (discards uncommitted changes)
git worktree remove --force ../wt-auth

# Prune stale metadata
git worktree prune
```

## Port Allocation Strategy

### Deterministic Port Assignment

Each worktree gets a block of ports based on its index:

```
Worktree Index    App Port    DB Port    Redis Port    API Port
────────────────────────────────────────────────────────────────
0 (main)          3000        5432       6379          8000
1 (wt-auth)       3010        5442       6389          8010
2 (wt-hotfix)     3020        5452       6399          8020
3 (wt-feature)    3030        5462       6409          8030
```

Formula: `port = base_port + (worktree_index * stride)`
Default stride: 10

### Port Map File

Store the allocation in `.worktree-ports.json` at the worktree root:

```json
{
  "worktree": "wt-auth",
  "branch": "feature/new-auth",
  "index": 1,
  "ports": {
    "app": 3010,
    "database": 5442,
    "redis": 6389,
    "api": 8010
  },
  "created": "2026-03-09T10:30:00Z"
}
```

### Port Collision Detection

```bash
# Check if a port is already in use
check_port() {
  local port=$1
  if lsof -i :"$port" > /dev/null 2>&1; then
    echo "PORT $port is BUSY"
    return 1
  else
    echo "PORT $port is FREE"
    return 0
  fi
}

# Check all ports for a worktree
for port in 3010 5442 6389 8010; do
  check_port $port
done
```

## Full Worktree Setup Script

```bash
#!/bin/bash
# setup-worktree.sh — Create a fully prepared worktree
set -euo pipefail

BRANCH="${1:?Usage: setup-worktree.sh <branch-name> [base-branch]}"
BASE="${2:-main}"
WT_NAME="wt-$(echo "$BRANCH" | sed 's|.*/||' | tr '[:upper:]' '[:lower:]')"
WT_PATH="../$WT_NAME"
MAIN_REPO="$(git rev-parse --show-toplevel)"

echo "Creating worktree: $WT_PATH from $BASE..."

# 1. Create worktree
if git rev-parse --verify "$BRANCH" > /dev/null 2>&1; then
  git worktree add "$WT_PATH" "$BRANCH"
else
  git worktree add "$WT_PATH" -b "$BRANCH" "$BASE"
fi

# 2. Copy environment files
for envfile in .env .env.local .env.development; do
  if [ -f "$MAIN_REPO/$envfile" ]; then
    cp "$MAIN_REPO/$envfile" "$WT_PATH/$envfile"
    echo "Copied $envfile"
  fi
done

# 3. Allocate ports
WT_INDEX=$(git worktree list | grep -n "$WT_PATH" | cut -d: -f1)
WT_INDEX=$((WT_INDEX - 1))
STRIDE=10

cat > "$WT_PATH/.worktree-ports.json" << EOF
{
  "worktree": "$WT_NAME",
  "branch": "$BRANCH",
  "index": $WT_INDEX,
  "ports": {
    "app": $((3000 + WT_INDEX * STRIDE)),
    "database": $((5432 + WT_INDEX * STRIDE)),
    "redis": $((6379 + WT_INDEX * STRIDE)),
    "api": $((8000 + WT_INDEX * STRIDE))
  }
}
EOF
echo "Ports allocated (index $WT_INDEX)"

# 4. Update .env with allocated ports
if [ -f "$WT_PATH/.env" ]; then
  APP_PORT=$((3000 + WT_INDEX * STRIDE))
  DB_PORT=$((5432 + WT_INDEX * STRIDE))
  sed -i.bak "s/APP_PORT=.*/APP_PORT=$APP_PORT/" "$WT_PATH/.env"
  sed -i.bak "s/:5432/:$DB_PORT/g" "$WT_PATH/.env"
  rm -f "$WT_PATH/.env.bak"
  echo "Updated .env with worktree ports"
fi

# 5. Install dependencies
cd "$WT_PATH"
if [ -f "pnpm-lock.yaml" ]; then
  pnpm install --frozen-lockfile
elif [ -f "package-lock.json" ]; then
  npm ci
elif [ -f "yarn.lock" ]; then
  yarn install --frozen-lockfile
elif [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
elif [ -f "go.mod" ]; then
  go mod download
fi

echo ""
echo "Worktree ready: $WT_PATH"
echo "Branch: $BRANCH"
echo "App port: $((3000 + WT_INDEX * STRIDE))"
echo ""
echo "Next: cd $WT_PATH && pnpm dev"
```

## Docker Compose Per-Worktree

```yaml
# docker-compose.worktree.yml — override for worktree-specific ports
# Usage: docker compose -f docker-compose.yml -f docker-compose.worktree.yml up

services:
  postgres:
    ports:
      - "${DB_PORT:-5432}:5432"
    environment:
      POSTGRES_DB: "myapp_${WT_NAME:-main}"

  redis:
    ports:
      - "${REDIS_PORT:-6379}:6379"

  app:
    ports:
      - "${APP_PORT:-3000}:3000"
    environment:
      DATABASE_URL: "postgresql://dev:dev@postgres:5432/myapp_${WT_NAME:-main}"
```

Launch with worktree-specific ports:

```bash
DB_PORT=5442 REDIS_PORT=6389 APP_PORT=3010 WT_NAME=auth \
  docker compose -f docker-compose.yml -f docker-compose.worktree.yml up -d
```

## Cleanup Automation

```bash
#!/bin/bash
# cleanup-worktrees.sh — Safe worktree cleanup
set -euo pipefail

STALE_DAYS="${1:-14}"
DRY_RUN="${2:-true}"

echo "Scanning worktrees (stale threshold: ${STALE_DAYS} days)..."
echo ""

git worktree list --porcelain | while read -r line; do
  case "$line" in
    worktree\ *)
      WT_PATH="${line#worktree }"
      ;;
    branch\ *)
      BRANCH="${line#branch refs/heads/}"
      # Skip main worktree
      if [ "$WT_PATH" = "$(git rev-parse --show-toplevel)" ]; then
        continue
      fi

      # Check if branch is merged
      MERGED=""
      if git branch --merged main | grep -q "$BRANCH" 2>/dev/null; then
        MERGED=" [MERGED]"
      fi

      # Check for uncommitted changes
      DIRTY=""
      if [ -d "$WT_PATH" ]; then
        cd "$WT_PATH"
        if [ -n "$(git status --porcelain)" ]; then
          DIRTY=" [DIRTY - has uncommitted changes]"
        fi
        cd - > /dev/null
      fi

      # Check age
      if [ -d "$WT_PATH" ]; then
        AGE_DAYS=$(( ($(date +%s) - $(stat -f %m "$WT_PATH" 2>/dev/null || stat -c %Y "$WT_PATH" 2>/dev/null)) / 86400 ))
        STALE=""
        if [ "$AGE_DAYS" -gt "$STALE_DAYS" ]; then
          STALE=" [STALE: ${AGE_DAYS} days old]"
        fi
      fi

      echo "$WT_PATH ($BRANCH)$MERGED$DIRTY$STALE"

      if [ -n "$MERGED" ] && [ -z "$DIRTY" ] && [ "$DRY_RUN" = "false" ]; then
        echo "  -> Removing merged clean worktree..."
        git worktree remove "$WT_PATH"
      fi
      ;;
  esac
done

echo ""
git worktree prune
echo "Done. Run with 'false' as second arg to actually remove."
```

## Multi-Agent Workflow Pattern

When running multiple AI agents (Claude Code, Cursor, Copilot) on the same repo:

```
Agent Assignment:
───────────────────────────────────────────────────
Agent 1 (Claude Code)  → wt-feature-auth   (port 3010)
Agent 2 (Cursor)       → wt-feature-billing (port 3020)
Agent 3 (Copilot)      → wt-bugfix-login   (port 3030)
Main repo              → integration (main) (port 3000)
───────────────────────────────────────────────────

Rules:
- Each agent works ONLY in its assigned worktree
- No agent modifies another agent's worktree
- Integration happens via PRs to main, not direct merges
- Port conflicts are impossible due to deterministic allocation
```

## Decision Matrix

| Scenario | Action |
|----------|--------|
| Need isolated dev server for a feature | Create a new worktree |
| Quick diff review of a branch | `git diff` in current tree (no worktree needed) |
| Hotfix while feature branch is dirty | Create dedicated hotfix worktree |
| Bug triage with reproduction branch | Temporary worktree, cleanup same day |
| PR review with running code | Worktree at PR branch, run tests |
| Multiple agents on same repo | One worktree per agent |

## Validation Checklist

After creating a worktree, verify:

1. `git worktree list` shows the expected path and branch
2. `.worktree-ports.json` exists with unique port assignments
3. `.env` files are present and contain worktree-specific ports
4. `pnpm install` (or equivalent) completed without errors
5. Dev server starts on the allocated port
6. Database connects on the allocated DB port
7. No port conflicts with other worktrees or services

## Common Pitfalls

- **Creating worktrees inside the main repo directory** — always use `../wt-name` to keep them alongside
- **Reusing localhost:3000 across all branches** — causes port conflicts; use deterministic allocation
- **Sharing one DATABASE_URL across worktrees** — each needs its own database or schema
- **Removing a worktree with uncommitted changes** — always check dirty state before removal
- **Forgetting to prune after branch deletion** — run `git worktree prune` to clean metadata
- **Not updating .env ports after worktree creation** — the setup script should handle this automatically

## Best Practices

1. **One branch per worktree, one agent per worktree** — never share
2. **Keep worktrees short-lived** — remove after the branch is merged
3. **Deterministic naming** — use `wt-<topic>` pattern for easy identification
4. **Persist port mappings** — store in `.worktree-ports.json`, not in memory
5. **Run cleanup weekly** — scan for stale and merged-branch worktrees
6. **Include worktree path in terminal title** — prevents wrong-window commits
7. **Never force-remove dirty worktrees** — unless changes are intentionally discarded

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `fatal: '<path>' is already checked out` | Branch is already active in another worktree | Use `git worktree list` to find where the branch is checked out, then switch to a different branch or remove the existing worktree first |
| Port conflict despite deterministic allocation | A non-worktree process is occupying the assigned port | Run `lsof -i :<port>` to identify the process, terminate it or adjust the stride/base in the port allocation formula |
| `.env` file missing after worktree creation | Setup script was not run or `.env` does not exist in the main repo | Copy `.env` manually from the main repo root, or re-run `setup-worktree.sh` which handles env file copying |
| `git worktree prune` reports nothing but stale paths remain | Worktree directory was deleted manually without `git worktree remove` | Run `git worktree prune` to clean orphaned metadata, then verify with `git worktree list` |
| Dependencies fail to install in new worktree | Lockfile references a private registry or cache not available in the worktree path | Ensure `.npmrc`, `.yarnrc.yml`, or pip config files are copied alongside `.env` during setup |
| Docker Compose services start on wrong ports | The `docker-compose.worktree.yml` override was not included in the compose command | Always pass both files: `docker compose -f docker-compose.yml -f docker-compose.worktree.yml up` |
| Worktree shows as dirty immediately after creation | Untracked files from `.env` copy or generated `.worktree-ports.json` | Add `.worktree-ports.json` and copied env files to `.gitignore` in the project |

## Success Criteria

- **Zero port conflicts** across all active worktrees measured by `lsof` checks returning no collisions after setup
- **Worktree creation under 60 seconds** including dependency installation for projects with warm package caches
- **100% env parity** between main repo and worktrees verified by diffing `.env` keys (values may differ for ports)
- **Stale worktree count stays at zero** when cleanup automation runs on a weekly schedule with a 14-day threshold
- **No cross-worktree interference** validated by running concurrent dev servers in 3+ worktrees simultaneously without failures
- **Branch-to-worktree traceability** maintained via `.worktree-ports.json` present in every active worktree with correct metadata
- **Cleanup safety rate of 100%** meaning no worktree with uncommitted changes is ever removed without explicit `--force` confirmation

## Scope & Limitations

**This skill covers:**
- Git worktree lifecycle: creation, listing, status inspection, and removal
- Deterministic port allocation and collision avoidance for parallel dev servers
- Environment file synchronization and Docker Compose override patterns
- Multi-agent workspace isolation strategies and cleanup automation

**This skill does NOT cover:**
- Git branching strategies or merge conflict resolution (see `pr-review-expert` and `release-manager`)
- Secret rotation, vault integration, or credential management (see `env-secrets-manager`)
- CI/CD pipeline configuration or automated test orchestration (see `ci-cd-pipeline-builder`)
- Monorepo package management, workspace linking, or cross-package dependency resolution (see `monorepo-navigator`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `env-secrets-manager` | Worktree setup copies `.env` files that contain secrets managed by this skill | `.env` files flow from main repo to each worktree; secret references remain consistent across all copies |
| `ci-cd-pipeline-builder` | CI pipelines can spin up worktrees for parallel test matrix execution | Pipeline config triggers `setup-worktree.sh` per matrix job; port allocation prevents service collisions |
| `release-manager` | Release branches get dedicated worktrees for stabilization while feature work continues | Release worktree is created from the release branch; merged status drives cleanup automation |
| `monorepo-navigator` | In monorepo setups, worktrees must respect package boundaries and shared dependencies | Worktree creation inherits the monorepo root lockfile; package-level dev servers use allocated port blocks |
| `pr-review-expert` | PR reviews can be performed in isolated worktrees with running code for manual validation | Reviewer creates a worktree at the PR branch, runs the dev server on allocated ports, and removes after review |
| `tech-debt-tracker` | Stale worktrees and abandoned branches surface as tech debt indicators | Cleanup script output feeds into debt tracking; worktree age and merge status inform priority scores |
