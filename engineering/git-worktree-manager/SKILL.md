---
name: git-worktree-manager
description: >
  Manage parallel development with Git worktrees: creation with port allocation, environment
  sync, branch isolation, and cleanup. Use when working multiple branches at once, running
  parallel CI validations, or isolating agent workspaces.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: developer-tooling
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: git-worktree
---
# Git Worktree Manager

Manage parallel development workflows using Git worktrees with deterministic naming, automatic port allocation, environment file synchronization, dependency installation, and cleanup automation. Optimized for multi-agent workflows where each agent or terminal session owns an isolated worktree with its own ports, environment, and running services.

## Core Capabilities

- **Worktree lifecycle** — create worktrees from new or existing branches with deterministic naming, copy `.env` files, install dependencies by lockfile detection, list with clean/dirty + ahead/behind status, and safely remove with uncommitted-change detection.
- **Port allocation** — deterministic per-worktree assignment (`base + index * stride`), collision detection against running processes, persistent map in `.worktree-ports.json`, and Docker Compose override generation.
- **Multi-agent isolation** — one branch per worktree, one agent per worktree, no shared state, conflict-free parallel execution, task-ID mapping for traceability.
- **Cleanup automation** — stale detection by age, merged-branch detection for safe removal, dirty-state warnings, and bulk cleanup with safety confirmations.

## When to Use

- You need 2+ concurrent branches open with running dev servers.
- You want isolated environments for feature work, hotfixes, and PR review.
- Multiple AI agents need separate workspaces that do not interfere.
- Your current branch is blocked but a hotfix is urgent.
- You want automated cleanup instead of manual `rm -rf` operations.

## Clarify First

Before managing worktrees, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Operation** — create, list, remove, or clean up worktrees (selects the `worktree_manager.py` action vs `port_allocator.py` vs `worktree_validator.py`)
- [ ] **Branch & base** — which branch(es) the worktree(s) track and from what base (drives worktree naming and isolation)
- [ ] **Port/service needs** — whether dev servers or Docker need allocated ports (drives the deterministic port block and the Docker Compose override generated)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `worktree_manager.py` | List, create, remove, and clean up worktrees | `python scripts/worktree_manager.py list` |
| `port_allocator.py` | Assign/check/release deterministic port blocks; sync registry | `python scripts/port_allocator.py status` |
| `worktree_validator.py` | Validate worktree health (stale, missing branch, env parity, port conflicts, lockfile) | `python scripts/worktree_validator.py --stale-days 14` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/setup-and-ports.md](references/setup-and-ports.md)** — quick-start `git worktree` commands, the deterministic port-allocation strategy and `.worktree-ports.json` format, collision-detection snippet, the full `setup-worktree.sh` script, and the Docker Compose per-worktree override. Read when creating a worktree or wiring up ports/services.
- **[references/cleanup-and-workflows.md](references/cleanup-and-workflows.md)** — the `cleanup-worktrees.sh` safe-cleanup script, the multi-agent assignment pattern and rules, the scenario→action decision matrix, and the post-creation validation checklist. Read when automating cleanup or coordinating agents.
- **[references/operations-playbook.md](references/operations-playbook.md)** — common pitfalls, best practices, the troubleshooting table, and the success-criteria bar. Read before shipping a workflow or when diagnosing problems.

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
