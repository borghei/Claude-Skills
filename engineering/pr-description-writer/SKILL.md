---
name: pr-description-writer
description: >
  Write PR descriptions with evidence, verification steps and a one-way/two-way
  merge-risk call. Use when opening a PR, when asked to write or fix a PR body,
  or when checking a description before requesting review.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: code-review
  updated: 2026-11-08
  tags: [pull-request, pr-description, code-review, merge-risk, rollback, evidence]
---

# PR Description Writer

A PR description exists so the reviewer can decide how hard to look, where to
look, and whether the merge can be undone. Most descriptions fail all three:
they narrate the commits, assert "tested, works", and call the change "low
risk" while it ships a `DROP COLUMN`. This skill writes the body in five
sections (summary, why, evidence, how to verify, merge risk), classifies the
change from its real file list and diff, and lints the result so an honest
classification is enforced rather than hoped for.

This skill is for the **author**. Reviewing someone else's PR (blast-radius
analysis, security scanning, coverage deltas) is a separate job covered by the
`engineering/pr-review-expert` package; this one only produces and checks the
description.

## When to use this skill

- **Opening a PR**: the branch is ready and needs a body
- **Rewriting a weak body**: "fix this PR description", "make this reviewable"
- **Before requesting review**: a mechanical check that evidence, steps and
  rollback are there
- **PRs with migrations, API or contract changes, deletions**: where getting
  the merge-risk call wrong costs an incident
- **CI gate**: fail PRs whose body claims "reversible" while touching
  migrations

## Clarify First

The merge-risk call and the evidence decide whether the description is useful,
and both depend on facts the author has but the diff may not show. Settle the
inputs below before writing. When one is missing or vague and would change the
result, ask about it; when it wouldn't, use a sensible default and say which one
you used.

- **Base branch and file list:** the classification comes from
  `git diff --name-only <base>...HEAD`. The wrong base produces the wrong door.
- **Evidence available:** whether screenshots, test output or a staging run
  exist. If none do, the agent says so and proposes the command to produce
  them, rather than writing "verified".
- **Deploy and rollback mechanics:** who deploys, whether migrations run
  automatically, whether a flag guards the change. A one-way PR's rollback plan
  is unusable without these.
- **Audience:** internal team only, or external API consumers too. This moves a
  contract change from conditional to one-way.

Ask about the two or three inputs that matter most for this request, not the
whole list. If the user wants a result straight away, draft it from the diff
and state your assumptions at the top of the body.

## Quick Start

```bash
# 1. Classify the change from its real file list and diff
T=$(mktemp -d)
git diff --name-only main...HEAD > "$T/changed.txt"
git diff main...HEAD > "$T/pr.diff"
python3 engineering/pr-description-writer/scripts/risk_classifier.py \
  --files "$T/changed.txt" --diff "$T/pr.diff" --emit-section

# 2. Write the body from assets/pr-body-template.md, then lint it against the same files
python3 engineering/pr-description-writer/scripts/pr_body_lint.py \
  --body pr.md --files "$T/changed.txt" --diff "$T/pr.diff"

# 3. Open the PR only when the lint passes
gh pr create --base main --body-file pr.md
```

## Tools Overview

| Tool | Purpose | Exit codes |
|------|---------|------------|
| `scripts/risk_classifier.py` | Classify each changed path (schema migration, public API, persisted format, data deletion, infra, auth, deps, CI, config, code, tests/docs), scan the diff for destructive SQL and removed contract fields, compute door and blast radius, and draft a Merge risk section (`--emit-section`) | `0` classified, `1` door at or above `--fail-on`, `2` usage error |
| `scripts/pr_body_lint.py` | Check the five sections exist and are filled, evidence is concrete, verification is runnable, the door is stated with a rollback for one-way, no credentials leaked, and (with `--files`) that the claimed door matches the files | `0` pass, `1` errors (or warnings with `--strict`), `2` usage error |

Both take `--format text|json`. Both read `-` as stdin, so they chain with
`git diff --name-only` and `gh pr view --json body`.

## Workflows

### Workflow 1: Write a new PR body [RECOMMENDED]

1. Get the file list and diff against the real base branch.
2. Run `risk_classifier.py --emit-section`. Read the per-file categories; if a
   path is misclassified, the body must say why (e.g. a `migrations/` folder
   holding fixtures).
3. Draft the body from `assets/pr-body-template.md`:
   - **Summary:** behaviour change in one or two sentences, plus at most one
     small picture (structure diff, call tree, file tree, or mermaid sequence).
   - **Why:** the problem in user terms, plus the ticket link.
   - **Evidence:** before and after, strongest tier available (screenshot >
     test output > command output > CI link). Redact tokens and customer data.
   - **How to verify:** numbered steps with exact commands and expected results.
   - **Merge risk:** classification, blast radius, rollback plan. Paste the
     classifier's draft and replace its bracketed placeholder.
4. Validate with the linter, using `--files` and `--diff`. Fix every error; a warning needs a reason
   to stay.
5. Delete template comments and open the PR.

```bash
python3 engineering/pr-description-writer/scripts/pr_body_lint.py \
  --body engineering/pr-description-writer/assets/sample_pr_body_good.md \
  --files engineering/pr-description-writer/assets/sample_changed_files.json \
  --diff engineering/pr-description-writer/assets/sample_migration.diff
```

### Workflow 2: Fix an existing body

1. Pull the current body and file list:
   `gh pr view 123 --json body -q .body > pr.md` and
   `gh pr diff 123 --name-only > changed.txt`.
2. Lint it. The findings are the edit list.
3. Rewrite only the failing sections; keep the author's wording where it passes.
4. Re-lint, then update with `gh pr edit 123 --body-file pr.md`.

```bash
python3 engineering/pr-description-writer/scripts/pr_body_lint.py \
  --body engineering/pr-description-writer/assets/sample_pr_body_flawed.md \
  --files engineering/pr-description-writer/assets/sample_changed_files.json --format json
```

The flawed sample fails on purpose (exit 1): it claims "fully reversible" on a
PR with a migration and an OpenAPI change, has "Tested locally" as its
verification, and pastes a bearer token into the evidence.

### Workflow 3: Gate PR bodies in CI (quality gate)

1. In the PR workflow, write the body and the changed-file list to files.
2. Run the linter. Exit 1 fails the job.
3. Optionally require a label for one-way PRs:
   `risk_classifier.py --files changed.txt --fail-on one-way` exits 1, so the
   job can demand a `one-way-reviewed` label before merge.

Pass the body through a file, never by interpolating `${{ github.event.pull_request.body }}`
into a shell line: PR bodies are attacker-controlled text.

## Decision Rules

### Door classification [PROVEN]

| If the PR... | Door |
|--------------|------|
| Only changes code, tests, docs | two-way |
| Touches infra, auth, dependencies, CI or config defaults | conditional: name the condition and why it does not apply |
| Adds or changes a migration, public API/contract, persisted format, or deletes data | one-way |
| Contains `DROP`, `TRUNCATE`, unscoped `DELETE`, renames, or removes a contract field | one-way, whatever the paths |

Over-classifying is cheap. Under-classifying is the expensive mistake.

### Rollback plan depth [RECOMMENDED]

- **Two-way:** "Revert this PR" plus anything that must happen with it (flag off, cache flush).
- **Conditional:** the condition that would make it one-way, and why it does not hold here.
- **One-way:** trigger, exact steps, owner, duration, and the end state of data and clients.
  If you cannot write those, split the PR with expand/contract until you can.

### Evidence by change type [RECOMMENDED]

| Change | Minimum evidence |
|--------|------------------|
| UI | Before/after screenshot or a short recording |
| Bug fix | The test that failed before and passes now, with both outputs |
| Backend behaviour | Command output (curl, CLI) from a real run |
| Migration | Migration plan output, row counts, staging timing and lock waits |
| Performance | Before/after numbers with the measurement method |
| Pure refactor | Identical output before and after for the same input |

## Anti-Patterns

### The Commit Narration
**Mistake:** A summary that lists what the author did ("refactored X, updated Y, cleaned up Z").
**Why it happens:** It is the easiest thing to write: the commit log is right there.
**Instead:** Write the behaviour change for the person who will be paged if it breaks. The diff already shows what files changed; the summary says what is different for users or operators.

### The Assertion Evidence
**Mistake:** "Tested and works" or "CI is green" as the evidence and verification.
**Why it happens:** The author did test it and assumes the reviewer trusts that.
**Instead:** Paste what you saw: the failing-then-passing test, the curl output, the screenshot. Give numbered steps the reviewer can repeat. The linter rejects claim-only verification.

### The Optimistic Door
**Mistake:** Calling a PR "low risk, reversible" when it contains a migration, a contract change or a deletion.
**Why it happens:** The code change is small, and "risk" gets confused with "size".
**Instead:** Classify by reversibility, not by size. Run the classifier with `--files` and `--diff`; the linter fails any body whose claimed door is less severe than the files say.

### The Leaky Log
**Mistake:** Pasting curl commands or logs that carry bearer tokens, cookies, connection strings or customer data.
**Why it happens:** Evidence is copied straight from the terminal at the end of a long session.
**Instead:** Redact before pasting. If the linter finds a credential, rotate it; deleting it from the body is not enough because bodies are emailed, cached and indexed by integrations.

### The Monster Body
**Mistake:** A 1,500-word description covering design history, every file, and future plans.
**Why it happens:** The author wants to pre-empt every question.
**Instead:** Keep 150-400 words and link to the design doc. If the summary needs more than two sentences, split the PR.

## Verification Checklist

- [ ] Classifier run against the real base branch, with `--diff` for migrations and contracts
- [ ] Lint passes with `--files` (and `--strict` for one-way PRs)
- [ ] Evidence was captured from a real run, not described
- [ ] Rollback plan names trigger, steps, owner, duration and end state (one-way only)
- [ ] No template comments, tokens, cookies or customer identifiers in the body

## Reference Documentation

| File | Contents |
|------|----------|
| `references/pr-body-anatomy.md` | Each section's job and failure mode, picking the smallest visual, evidence tiers, verification step format, length and tone, when to split the PR instead |
| `references/merge-risk-classification.md` | One-way and conditional categories, diff signals, expand/contract and other ways to make one-way changes safer, blast-radius levels, writing a rollback plan, recurring classification mistakes |

## Files

| File | Purpose |
|------|---------|
| `scripts/risk_classifier.py` | Door, blast radius and rollback guidance from changed paths and diff |
| `scripts/pr_body_lint.py` | Section, evidence, verification, risk-consistency and secret checks |
| `assets/pr-body-template.md` | Five-section template with inline guidance comments |
| `assets/sample_pr_body_good.md` | Passing one-way example (expand-phase migration) |
| `assets/sample_pr_body_flawed.md` | Deliberately failing example (exit 1) |
| `assets/sample_changed_files.json` | File list for the sample PR |
| `assets/sample_migration.diff` | Diff for the sample PR (migration with a downgrade, removed OpenAPI field) |

## Scope & Limitations

**In Scope:**
- Writing, rewriting and linting PR descriptions.
- Merge-risk classification from file paths and diff content.
- Gating PR bodies in CI.

**Out of Scope:**
- Reviewing the code itself (correctness, security, test coverage).
- Producing the evidence: the agent proposes the commands, a human or CI runs them.
- Changelog or release-note generation.

**Important Caveats:**
- Path categories are heuristics. A `migrations/` folder holding fixtures will
  be called one-way; say so in the body rather than weakening the rules.
- Diff scanning covers common SQL and migration-helper shapes, not every ORM.
- The secret scan catches common credential formats only; it is a backstop,
  not a redaction tool.
