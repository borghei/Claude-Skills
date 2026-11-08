---
name: git-worktree-manager
description: >
  Run parallel Git worktrees without collisions: a port block per worktree, .env sync,
  health checks for stale or dirty trees, and safe cleanup of merged ones. Use when several
  branches or agents need running dev servers at once.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: developer-tooling
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: git-worktree
  tags:
    - git
    - worktrees
    - parallel-development
    - branching
    - developer-tooling
---
# Git Worktree Manager

Plain `git worktree add/remove` is the easy part. The agent uses this skill for what git does not do: give every worktree its own port block so dev servers and Docker services do not collide, carry `.env` files across, spot worktrees that are stale, dirty or tracking deleted branches, and remove merged ones without losing uncommitted work. It suits multi-agent setups where each agent or terminal owns one worktree.

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

Before managing worktrees, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Operation:** create, list, remove, or clean up worktrees (selects the `worktree_manager.py` action vs `port_allocator.py` vs `worktree_validator.py`).
- **Branch & base:** which branch(es) the worktree(s) track and from what base (drives worktree naming and isolation).
- **Port/service needs:** whether dev servers or Docker need allocated ports (drives the deterministic port block and the Docker Compose override generated).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Create** the worktree with `worktree_manager.py create <branch> --base main`; it names the directory deterministically, copies `.env` files and installs dependencies from the lockfile it finds.
2. **Assign ports** with `port_allocator.py assign <worktree-name>`: a block at `base + index * stride`, checked against listening processes and recorded in `.worktree-ports.json`. Use the Docker Compose override in [references/setup-and-ports.md](references/setup-and-ports.md) to apply it.
3. **Work**: one branch and one agent per worktree, no shared mutable state.
4. **Check health** with `worktree_validator.py` (stale trees, missing directories, deleted branches, `.env` parity, port conflicts, lockfile drift).
5. **Clean up** with `worktree_manager.py cleanup --dry-run` first, then without `--dry-run`; dirty worktrees are reported, not deleted. Run `port_allocator.py sync` afterwards to free released blocks.
6. **Verify** that `worktree_validator.py` reports no issues and `git worktree list` matches the port registry.

## Quick Start

Run inside any git repository:

```bash
python3 scripts/worktree_manager.py list                          # worktrees with clean/dirty and ahead/behind
python3 scripts/port_allocator.py status                          # current port blocks
python3 scripts/worktree_validator.py --stale-days 14 --json      # health report
python3 scripts/worktree_manager.py cleanup --stale-days 30 --dry-run
```

## Tools Overview

| Tool | Subcommands and flags | Exit codes |
|------|-----------------------|------------|
| `worktree_manager.py` | `list`, `create <branch> [--base]`, `remove <name>`, `cleanup [--stale-days N] [--dry-run]`; `--json` | 0, 1 git operation failed, 2 no subcommand or not inside a repository |
| `port_allocator.py` | `status`, `assign <name> [--index] [--branch]`, `release <name>`, `check`, `sync`; `--json` | 0, 1 operation failed, 2 no subcommand or not inside a repository |
| `worktree_validator.py` | `--checks stale,missing,branch,env,ports,lockfile`, `--stale-days`, `--json` | 0 no errors (warnings allowed), 1 errors found, 2 unknown check or not inside a repository |

## Anti-Patterns

**Mistake:** Deleting worktree directories with `rm -rf`.
**Why it happens:** It looks like any other folder.
**Instead:** Use `worktree_manager.py remove` (or `git worktree remove`); a raw delete leaves stale metadata and loses uncommitted work without warning.

**Mistake:** Two worktrees on the same dev-server ports.
**Why it happens:** Every checkout reads the same default `.env`.
**Instead:** Assign a port block per worktree and generate the Compose override from it.

**Mistake:** Two agents sharing one worktree.
**Why it happens:** It saves a checkout.
**Instead:** One agent per worktree and branch; shared working trees produce interleaved, unreviewable changes.

## Files

- `scripts/worktree_manager.py`, `scripts/port_allocator.py`, `scripts/worktree_validator.py` — the tools above. They read the current repository; there is no sample data.

## Reference Documentation

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

Related skills: `engineering/env-secrets-manager` (the `.env` files copied into worktrees), `engineering/monorepo-navigator` (package boundaries inside a worktree).
