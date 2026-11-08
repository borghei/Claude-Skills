---
name: git-guardrails
description: >
  Install a hook that blocks destructive git commands before an AI agent runs them.
  Use when an agent force-pushed or ran reset --hard, when adding git safety hooks,
  or when protecting main from agent pushes.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: developer-tooling
  updated: 2026-11-08
  tags: [git, hooks, claude-code, safety, pretooluse, branch-protection]
---

# Git Guardrails

An agent with shell access can run `git reset --hard`, `git clean -fdx` or
`git push --force` as casually as `ls`, usually while trying to make a failing
command pass. This skill installs a **PreToolUse hook** that reads every Bash
call before it runs, parses the git invocations inside it (chains, subshells,
`bash -c`, `xargs`, `git -C`), and blocks the destructive ones with exit code 2
and a reason the agent can act on. It ships the hook, an installer that merges
into `.claude/settings.json` without overwriting anything, plain git `pre-push`
and `pre-rebase` hooks for non-agent callers, and a corpus tester that proves
which commands are allowed and which are blocked.

## When to use this skill

- **After an incident**: an agent discarded uncommitted work, deleted a branch,
  or force-pushed over a teammate's commits
- **Before giving an agent autonomy**: auto-accept mode, background agents,
  long unattended runs, or several agents in parallel worktrees
- **Protecting shared branches**: no direct pushes or rebases on `main`,
  `release/*`, `production`
- **Auditing an existing guardrail**: run its hook against the corpus to see what
  it actually catches
- **Rolling guardrails out to a team**: one committed project-scope hook plus a
  CI-runnable test

Not for server-side branch protection (configure that in your Git host) or for
general command sandboxing; this guards git specifically.

## Clarify First

The install scope and the protected-branch list decide what gets blocked, so
settle them before installing. When one is missing or vague and would change
the result, ask about it; when it wouldn't, use the default and say so.

- **Scope:** project scope (`<repo>/.claude/settings.json`, committed, applies to
  every contributor's agent) or user scope (`~/.claude/settings.json`, every repo
  on this machine). The default is project scope, because team rules belong in
  version control.
- **Protected branches:** the default list is `main, master, develop, trunk,
  production, prod, release/*`. Repos with `stable`, `staging` or `deploy/*`
  need a policy file, or pushes to those branches pass.
- **Force-with-lease on feature branches:** allowed by default so an agent can
  update its own rebased PR. Teams that forbid any history rewrite after push
  should turn it off.
- **Non-agent callers:** if release scripts, IDEs or humans also need the push
  rules, add the plain git hooks (`--git-hooks`).

Ask about the two or three inputs that matter most for this request, not the
whole list. If the user wants a result straight away, install at project scope
with defaults and state your assumptions at the top.

## Quick Start

```bash
# 1. See exactly what would change (writes nothing)
python3 engineering/git-guardrails/scripts/install_guardrails.py --project . --dry-run

# 2. Install hook + policy file + plain git hooks
python3 engineering/git-guardrails/scripts/install_guardrails.py --project . --policy --git-hooks

# 3. Prove it: run the corpus through the installed hook
python3 engineering/git-guardrails/scripts/guardrail_test.py --hook .claude/hooks/git_guardrails_hook.py
```

Restart the Claude Code session afterwards; settings are read at session start.

## Tools Overview

| Tool | Purpose | Exit codes |
|------|---------|------------|
| `scripts/install_guardrails.py` | Copy the hook into `.claude/hooks/`, merge one PreToolUse entry into `settings.json`, optionally add policy and git hooks. `--dry-run` prints a unified diff | `0` installed or already installed, `1` a conflict was left untouched, `2` usage error or invalid settings (nothing written) |
| `scripts/guardrail_test.py` | Pipe each corpus command to a hook as a real PreToolUse payload; report allow/block and rule id per case. `--command` tests one command | `0` all cases matched, `1` any mismatch or reasonless block, `2` usage error |
| `assets/git_guardrails_hook.py` | The hook itself. Stdin JSON in; exit `0` allow or exit `2` + stderr reason. `--check "<cmd>"` for manual use | `0` allow, `2` block |
| `assets/pre-push`, `assets/pre-rebase` | Plain git hooks: force/non-fast-forward pushes, protected deletes, rebases of protected branches | `0` continue, `1` abort |

All tools take `--format text|json` (except the hooks, whose output format is
fixed by their callers).

## Workflows

### Workflow 1: Install at project scope [RECOMMENDED]

1. Confirm the protected-branch list with the user. If it differs from the
   defaults, the installer's `--policy` copies `assets/sample_guardrail_policy.json`
   to `.claude/git-guardrails.json`; edit that file.
2. Dry-run the installer and read the diff. Verify that the only change to
   `settings.json` is one appended `PreToolUse` entry.
3. Install for real. A pre-existing `settings.json` is backed up to
   `settings.json.bak`.
4. Run the tester against the installed copy. It must pass every case before
   you call the install done.
5. Commit `.claude/settings.json`, `.claude/hooks/git_guardrails_hook.py` and
   the policy file so every contributor's agent gets the same rules.

```bash
python3 engineering/git-guardrails/scripts/install_guardrails.py --project . --policy --format json
python3 engineering/git-guardrails/scripts/guardrail_test.py \
  --hook .claude/hooks/git_guardrails_hook.py --policy .claude/git-guardrails.json
```

The installer never edits an existing hook entry. A `settings.json` that is not
valid JSON stops the run with exit 2 and nothing written: fix the JSON by hand
first. Re-running is safe: the second run reports `unchanged`.

### Workflow 2: Add the plain git layer

1. Run the installer with `--git-hooks`. It installs `pre-push` and
   `pre-rebase` into `.git/hooks/` only where no hook exists.
2. If it reports `conflict-foreign`, a hook from another tool (husky,
   pre-commit, lefthook) is already there. Chain ours from it instead of
   replacing it; `references/hook-mechanics.md` has the snippet.
3. Set protected branches in git config so the shell hooks share the policy:

```bash
git config --add guardrails.protected main
git config --add guardrails.protected 'release/*'
git config guardrails.blockDirectPush true
```

Git has no hook for `reset`, `clean` or `branch -D`. The git layer covers
pushes and rebases from any caller; the Claude Code hook covers everything the
agent types. Use both.

### Workflow 3: Validate or extend the rules

1. Reproduce the command the agent actually ran (or the one that was wrongly
   blocked) with `--command` and `--branch`.
2. Add it to a corpus copy as a case with `expect` and, for blocks, the `rule`
   id. Add the closest harmless neighbour as an `allow` case too.
3. Change the policy (`disabled_rules`, `protected_branches`,
   `extra_block_regex`) or the hook, then re-run the full corpus. The
   corpus is the regression suite: no rule change ships with a failing case.

```bash
python3 engineering/git-guardrails/scripts/guardrail_test.py \
  --command "git push origin HEAD" --branch main
python3 engineering/git-guardrails/scripts/guardrail_test.py \
  --corpus engineering/git-guardrails/assets/sample_command_corpus.json --format json
```

### Workflow 4: Audit somebody else's guardrail

1. Point `--hook` at their script. It must speak the same contract (stdin JSON,
   exit 2 to block).
2. Run the bundled 79-case corpus. Mismatches show which shapes it misses,
   typically `cd x && git reset --hard`, `bash -c "..."`, `-fdx` flag clusters,
   or `git -C`.
3. Check for exit-1 blocks: the tester reports any exit code other than 0 or 2
   as an error, because Claude Code treats exit 1 as "warn and run anyway".

## What gets blocked

Defaults below; `references/rule-catalog.md` has every rule with the allowed
cousins, safe alternatives and recovery steps.

| Loss class | Rules |
|------------|-------|
| Uncommitted work (no recovery) | `reset --hard`, `clean -f*`, `checkout .` / `checkout -f`, `restore .`, `switch --discard-changes`, `worktree remove --force` |
| Local history (reflog recovers) | `branch -D`, `branch -M/-C`, `stash clear`, `update-ref -d` |
| Shared history | `push --force` / `+ref`, lease pushes to protected branches, push to protected, `push --delete` / `:ref`, `push --mirror`, rebase of a protected branch, `filter-branch`, `filter-repo` |
| Safety net | `reflog expire --expire=now`, `gc --prune=now`, `--no-verify` |

### Design decisions

- **[PROVEN] Parse, don't grep.** `grep "push --force"` both misses
  `push -f origin x` and blocks `echo "never push --force"`. The hook tokenises
  with `shlex`, splits on shell operators, unwraps `sudo`/`env`/`xargs`/`bash -c`,
  and reads git's own global options before the subcommand.
- **[PROVEN] Exit 2, never exit 1.** Exit 1 is a non-blocking error in Claude
  Code: the command still runs. The hook has no path that raises.
- **[RECOMMENDED] Allow `--force-with-lease` on feature branches.** Blocking it
  pushes agents toward worse workarounds; the lease already refuses when
  someone else pushed.
- **[RECOMMENDED] Block on the current branch, not just explicit refspecs.**
  A bare `git push` on `main` is the most common accidental protected push.
- **[RECOMMENDED] Fail open on unparseable input, fail closed on a broken
  policy.** Non-Bash payloads exit 0 so the hook never wedges the session; an
  unreadable policy file falls back to the strict defaults.

## Anti-Patterns

### The Grep Guardrail
**Mistake:** Blocking on `grep -E "push.*--force|reset --hard"` over the raw command.
**Why it happens:** It is a one-liner and catches the exact command from the incident.
**Instead:** Parse the command. Run the corpus against the grep version: it misses `-f`, `-fdx` clusters and `git -C`, and blocks `grep`/`echo` lines that only mention the words. A guardrail with false positives gets disabled within a week.

### The Exit-1 Block
**Mistake:** Writing the hook to `exit 1` (or letting it crash) when it means to block.
**Why it happens:** Exit 1 means failure everywhere else, and a traceback feels like a refusal.
**Instead:** Block with exit 2 and a stderr reason. Exit 1 only warns the user and the command runs anyway. The tester flags any exit code other than 0 or 2.

### The Overwritten Settings File
**Mistake:** Writing a fresh `.claude/settings.json` that contains only the guardrail hook.
**Why it happens:** Examples show a complete file, and copying it is faster than merging.
**Instead:** Merge. The installer appends one entry, keeps permissions, env and every other hook, backs up the old file, and refuses to touch invalid JSON. Always dry-run first and read the diff.

### The Workaround Invitation
**Mistake:** A block message that only says "command not allowed".
**Why it happens:** The author thinks of the hook as a filter, not as a message to the model.
**Instead:** Say why it is dangerous and what to do next: stop, explain, hand it to the human. Without that line, models reach for the next closest destructive command.

### The Hook-Only Strategy
**Mistake:** Treating the client hook as the protection for `main`.
**Why it happens:** It visibly blocks the agent, so it feels complete.
**Instead:** Keep server-side branch protection on (no force push, no deletion, required reviews). Client hooks catch mistakes early; only server rules cannot be skipped with `--no-verify`, an alias or a script.

## Verification Checklist

- [ ] Dry-run diff shows one appended `PreToolUse` entry and nothing else changed
- [ ] `guardrail_test.py` passes against the **installed** copy, with the project policy
- [ ] A session restart shows the hook in `/hooks`
- [ ] `git status`, `git log`, `git diff`, `git commit`, feature-branch pushes still run
- [ ] Server-side branch protection is on for every protected branch

## Reference Documentation

| File | Contents |
|------|----------|
| `references/rule-catalog.md` | Every rule by loss class: what it blocks, what it allows on purpose, safe alternative, recovery after the fact; command shapes covered; known gaps; writing extra rules |
| `references/hook-mechanics.md` | PreToolUse contract and exit codes, settings layering, escape hatches, plain git hook coverage, installer guarantees, chaining with existing hooks, debugging |

## Files

| File | Purpose |
|------|---------|
| `scripts/install_guardrails.py` | Idempotent merge installer with `--dry-run`, `--policy`, `--git-hooks` |
| `scripts/guardrail_test.py` | Corpus tester for any hook that speaks the PreToolUse contract |
| `assets/git_guardrails_hook.py` | The PreToolUse hook (stdlib only) |
| `assets/pre-push` | Plain git hook: force, delete and protected-branch pushes |
| `assets/pre-rebase` | Plain git hook: rebase of protected branches |
| `assets/sample_guardrail_policy.json` | Policy template: protected branches, lease toggle, disabled rules, extra regexes |
| `assets/sample_command_corpus.json` | 79-case regression corpus (53 block, 26 allow) |

## Scope & Limitations

**In Scope:**
- Blocking destructive git commands typed by an agent through the Bash tool.
- Plain git push/rebase protection for any caller.
- Safe, idempotent installation and corpus-based verification.

**Out of Scope:**
- Server-side branch protection rules and repository permissions.
- Non-git destruction (`rm -rf`, `gh repo delete`, database commands) unless
  you add `extra_block_regex` entries.
- Sandboxing a hostile agent; this is a seatbelt against honest mistakes.

**Important Caveats:**
- Git aliases and scripts that call git internally are not seen by the
  Claude Code hook; the `pre-push` hook covers pushes from scripts.
- The hook resolves the current branch with a local `git symbolic-ref`; in a
  detached HEAD, bare-push protection relies on explicit refspecs.
- Hook settings are read at session start; restart after installing.
