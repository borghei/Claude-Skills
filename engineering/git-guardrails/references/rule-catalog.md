# Git Guardrail Rule Catalog

Every rule the bundled hook enforces, why it exists, what it deliberately lets
through, the safe alternative to offer the agent, and how to recover if the
operation already happened. Rule ids are the strings you put in a policy's
`disabled_rules` list and the ids printed in the block message.

## How to read this catalog

- **Loss class** describes what is destroyed: *uncommitted* (never in git, no
  recovery), *local history* (recoverable from the reflog for ~90 days),
  *shared history* (other clones diverge, recovery needs coordination), or
  *safety net* (removes the thing that would let you recover).
- **Allowed on purpose** lists close cousins that stay allowed. A guardrail that
  blocks everyday commands gets disabled within a week; precision is what keeps
  it installed.

## Rules by loss class

### Uncommitted work (no recovery possible)

| Rule id | Blocks | Allowed on purpose | Safe alternative |
|---------|--------|--------------------|------------------|
| `reset-hard` | `git reset --hard [ref]` | `reset --soft`, `reset --mixed`, `reset <file>` | `git stash push -u -m "before reset"` then `git reset --hard` by the human, or `git switch -c rescue` first |
| `clean-force` | `git clean -f`, `-fd`, `-fdx`, `--force` | `git clean -n` / `--dry-run` (always shown first) | Show `git clean -nd` output to the user and let them run the real command |
| `checkout-discard` | `git checkout .`, `git checkout -- .`, `git checkout HEAD -- .`, `git checkout -f` | `git checkout -- path/to/one/file`, `git checkout -b new` | `git stash push -- <paths>` keeps the changes retrievable |
| `restore-discard` | `git restore .` (worktree) | `git restore --staged .`, `git restore one/file` | Same as above |
| `switch-discard` | `git switch -f`, `--discard-changes` | plain `git switch` (refuses on dirty tree, which is the point) | Commit or stash, then switch |
| `worktree-force-remove` | `git worktree remove --force` | `git worktree remove` (refuses on dirty tree) | `git -C <worktree> status` and commit first |

**Why these are the highest priority:** untracked and unstaged changes were never
written to the object store. There is no reflog entry, no dangling blob for most
cases, nothing `git fsck` can find. An agent that "cleans up" to make a failing
command pass can erase an afternoon of human work in one call.

Recovery if it happened anyway: for `reset --hard` over *staged* content,
`git fsck --lost-found` sometimes finds dangling blobs (only for content that was
`git add`-ed). IDE local history (JetBrains, VS Code Timeline) is the next best
source. For `clean -f` there is usually nothing.

### Local history (recoverable via reflog)

| Rule id | Blocks | Allowed on purpose | Safe alternative |
|---------|--------|--------------------|------------------|
| `branch-force-delete` | `git branch -D`, `branch -d -f`, `branch --delete --force`, and `... | xargs git branch -D` | `git branch -d` (refuses unmerged branches) | `git branch -d`; if it refuses, the branch has unmerged work: report that instead |
| `branch-force-move` | `git branch -f main HEAD~3` (force-moving a protected branch) | `git branch -f` on an unprotected local branch | `git switch main && git reset` only after confirming nothing is lost, or open a revert PR |
| `branch-force-rename` | `git branch -M`, `-C`, `-m -f` | `git branch -m old new` when `new` does not exist | Plain `-m`, which refuses to clobber |
| `stash-clear` | `git stash clear` | `git stash drop stash@{n}`, `git stash pop` | Drop individual entries after reading them with `git stash show -p` |
| `update-ref-delete` | `git update-ref -d <ref>` | `update-ref` writes | `git branch -d` / `git tag -d` which carry their own checks |

Recovery: `git reflog` shows the old tip; `git branch <name> <sha>` restores a
deleted branch. A dropped stash is a dangling commit:
`git fsck --unreachable | grep commit` then `git stash apply <sha>`.

### Shared history (other people's clones are affected)

| Rule id | Blocks | Allowed on purpose | Safe alternative |
|---------|--------|--------------------|------------------|
| `push-force` | `git push --force`, `-f`, `+refspec` | `--force-with-lease` on unprotected branches (see below) | `git push --force-with-lease` on the agent's own feature branch |
| `push-force-with-lease` | lease pushes to protected branches, or all lease pushes when `allow_force_with_lease` is false | lease on feature branches | Open a PR; never rewrite a protected branch |
| `push-protected` | `git push origin main`, `HEAD:main`, bare `git push` while on a protected branch, `push --all` | pushes to feature branches, `--dry-run` | Push a branch and open a pull request |
| `push-delete` | `git push --delete`, `-d`, `:branch` refspecs | none | Ask the human; remote deletion has no local undo |
| `push-mirror` | `git push --mirror` | none | Explicit refspecs |
| `rebase-shared` | `git rebase` while a protected branch is checked out, or `git rebase <upstream> <protected>` | rebasing feature branches, `--continue/--abort/--skip` on anything | `git rebase main` from the feature branch |
| `history-rewrite` | `git filter-branch`, `git filter-repo` | none | These are planned, announced, human-run operations (secret purge, repo split) |

**Why force-with-lease is allowed on feature branches [RECOMMENDED]:** agents
legitimately rebase their own branch after review and must update the PR.
`--force-with-lease` refuses if the remote moved since the last fetch, which is
exactly the failure mode a plain `--force` hides. Blocking it too pushes agents
toward `--force` workarounds or toward stacking merge commits. Set
`allow_force_with_lease: false` if your team forbids rewriting any pushed branch.

Recovery after a bad force push: anyone with the old tip in their reflog can
restore it (`git push origin <old-sha>:refs/heads/<branch> --force-with-lease`).
GitHub keeps the old head in the PR timeline and in the branch's activity view.

### Safety net (removes the ability to recover)

| Rule id | Blocks | Allowed on purpose |
|---------|--------|--------------------|
| `reflog-destroy` | `git reflog expire --expire=now`, `--expire-unreachable=now`, `git reflog delete` | `git reflog` (read) |
| `gc-prune-now` | `git gc --prune=now` / `--prune=all` | plain `git gc` (keeps two weeks of unreachable objects) |
| `no-verify` | `git commit --no-verify` / `-n`, `git push --no-verify` | normal commits |

These are rarely destructive by themselves. They are blocked because they are
the second half of a destructive pair: rewrite history, then prune so nobody can
undo it. `--no-verify` is here because skipping a repository's own hooks is how
an agent routes around every other guardrail the team installed.

## Command-shape coverage

The hook parses the command rather than grepping it, so these all resolve to the
same git invocation:

| Shape | Example |
|-------|---------|
| Chained | `npm test && git push --force` |
| Directory hop | `cd services/api && git reset --hard` |
| Git global options | `git -C ../repo -c core.pager=cat push -f` |
| Env prefix / wrappers | `GIT_TRACE=1 sudo git reset --hard`, `sudo -u deploy git ...`, `nice -n 10 git ...`, `env -u X git ...`, `timeout 30 git ...` |
| Subshells | `echo $(git branch -D old)`, backticks, `( ... )` |
| Nested shells | `bash -c "git clean -fdx"`, `bash -lc '...'`, `sh -xc '...'`, `eval "..."` (3 levels) |
| Pipelines into xargs | `git branch --merged \| xargs git branch -D` |
| Combined short flags | `-fdx`, `-nm`, `-fu` |
| Abbreviated long options | `git reset --har`, `git push origin x --del` (git accepts any unambiguous prefix) |

And these stay allowed, because text is not a command: `echo 'git push --force'`,
`grep -r "reset --hard" docs/`, and a commit message containing
`; git push -f`.

## Known gaps [RECOMMENDED: accept them, document them]

- **Git aliases.** `git nuke` defined as `reset --hard` is not expanded. Agents
  rarely use aliases; if your team does, add their names to `extra_block_regex`.
- **Scripts.** `./scripts/release.sh` that force-pushes internally is invisible
  to a command-level hook. The plain git `pre-push` hook covers this for pushes.
- **Other tools.** `gh repo delete`, `rm -rf .git`, IDE integrations and MCP
  servers that call git directly are out of scope. Add regexes for the ones you
  care about.
- **Variable indirection.** `g=git; $g reset --hard` and `$(echo git) reset --hard`
  are not resolved; the hook reads text, it does not evaluate the shell.
- **Heredoc bodies.** A heredoc whose body contains `git reset --hard` is blocked
  even when it is only written to a file. This fails safe; write the file with
  the editor tool instead.
- **Uninspected options.** Rules only look at the options listed in this catalog.
  `push --force-with-lease` to an unprotected branch is allowed by design.
- **Obfuscation.** A determined adversary can build a command string at runtime.
  The hook is a seatbelt against honest mistakes, not a sandbox. Pair it with
  branch protection on the server, which no client-side hook can bypass.

## Writing extra rules

`extra_block_regex` is matched against the full raw command with Python `re`.
Keep each pattern anchored on the verb so it does not fire on documentation:

```json
{"extra_block_regex": ["\\bgit\\s+push\\s+\\S+\\s+--tags\\b", "\\bgh\\s+repo\\s+delete\\b"]}
```

Add a corpus case for every new pattern, both a block case and the closest
allow case, and re-run `guardrail_test.py`.
