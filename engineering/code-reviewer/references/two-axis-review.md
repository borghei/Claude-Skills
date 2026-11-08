# Two-Axis Review

A single reviewer reading a diff tends to answer one question well and the other badly.
Reviewers who start with style rarely notice that a requirement was never built; reviewers
who start from the ticket rarely notice that the code breaks three repo conventions. The
two-axis review separates those questions into independent passes and only combines the
results at the end.

- **Axis A — Standards.** Does the change follow this repository's documented rules for how code is written?
- **Axis B — Spec fidelity.** Does the change do what the originating spec, issue or ticket asked, no less and no more?

## Why the passes must be independent

Each pass runs with fresh context: a new reviewer, a new agent session, or a sub-agent that
receives only its brief. The reasons are practical.

- **Anchoring.** A reviewer who has just listed twelve naming problems has spent their attention. The missing requirement gets a skim.
- **Context load.** The standards pass needs the standards files; the spec pass needs the spec and the issue thread. Loading both into one context halves the room for the diff.
- **Different failure modes.** Standards findings are mostly local (a line, a file). Spec findings are mostly global (a behaviour that should exist somewhere and does not). One reading order cannot serve both.
- **Honest ranking.** A missing requirement and an awkward variable name should not compete for the top slot in one merged list. Keeping the axes apart makes each axis's worst issue visible.

When the work is done by one human with no second reviewer, run the passes sequentially
with a clear break: finish and write down the standards pass, then start the spec pass from
the spec, not from the diff.

## Step 1 — Pin a fixed base

The review covers the diff between a fixed base and the head. The base is something the
author names: a branch (`main`), a tag (`v2.3.0`), a commit SHA, or `HEAD~N`. Pinning it
first stops the scope from drifting while the review runs.

- Use the three-dot form, `git diff <base>...HEAD`, so the diff is taken against the merge-base and excludes changes that landed on the base branch after the work branched.
- Record the base SHA in the review output. "Reviewed against `main`" is ambiguous a day later; "reviewed against `53c5999`" is not.
- Fail early on a bad ref or an empty diff. `scripts/review_scope.py` exits 2 on an unresolvable ref and 1 on an empty diff, so neither problem surfaces halfway through two parallel passes.

## Step 2 — Find the spec source

Look in this order and stop at the first hit:

1. A spec path or issue link the author gave.
2. Issue references in the commit messages (`#123`, `Closes #45`, `PROJ-88`, `!67`). `review_scope.py` extracts these.
3. A spec file whose name matches the branch, under `docs/specs/`, `specs/`, `docs/rfcs/`, `docs/prd/` or similar.
4. Ask the author.

If there is no spec, say so in the report and skip Axis B rather than inventing a spec from
the code. "No spec found" is itself a finding worth raising before merge on anything larger
than a small fix.

## Step 3 — Find the standards sources

Collect every file that documents how code should be written: `CODING_STANDARDS.md`,
`CONTRIBUTING.md`, style guides, steering files (`AGENTS.md`, `CLAUDE.md`), and linter
configuration. The linter configuration matters for a negative reason: anything a linter in
the repo already enforces is out of scope for the human pass. Reviewing what a machine
checks wastes the reviewer's attention.

Where the repo documents nothing, fall back to `coding_standards.md` and
`common_antipatterns.md` in this skill, and label every finding from them as a judgement
call. A documented repo rule always overrides the fallback: if the repo explicitly allows
something the fallback would flag, do not flag it.

## Step 4 — Brief each pass

Each brief is everything that reviewer gets. Keep it short and complete.

**Standards brief contains:** the diff command and commit list, the standards source files,
and the instruction to report per finding the location, the rule (file plus rule text), and
whether it is a hard violation of a documented rule or a judgement call. It explicitly
excludes spec questions.

**Spec brief contains:** the diff command and commit list, the spec text or path and the
issue thread, and the instruction to report three lists — requirements missing or partly
built, behaviour that was not asked for, and requirements that look built but built wrongly
— each quoting the spec line. It explicitly excludes style.

`review_scope.py` prints both briefs ready to paste. Cap each report at roughly 400 words so
the passes stay focused on what matters.

## Step 5 — Merge the results

Present the two reports under separate headings, Standards and Spec, without re-ranking
findings across axes. Then add:

- A one-line summary per axis: number of findings and the most serious one.
- **Overlaps.** A finding both passes raised from different angles (for example, an unrequested feature that also breaks a convention) is listed once under Spec with a note.
- **Verdict.** Approve, request changes, or block. Any missing mandatory requirement or wrongly built requirement is at least request-changes, regardless of how clean Axis A is. A hard violation of a documented standard is request-changes. Judgement calls alone never block.

Use `assets/two-axis-review-template.md` for the layout.

## Scope creep: what counts

Behaviour in the diff that the spec did not ask for falls into three buckets.

| Bucket | Example | Action |
|--------|---------|--------|
| Enabling work | A small refactor that makes the requirement possible | Accept; mention it so the reviewer of record knows |
| Unrequested behaviour | A new flag, endpoint or setting nobody asked for | Request removal or a spec update before merge |
| Speculative generality | Hooks, parameters or abstractions for needs the spec does not have | Request removal; inline until a real need appears |

The spec pass flags all three; only the second and third need action.

## When to use a lighter review

The two-axis review costs two passes. Skip it for a typo fix, a dependency bump with a green
build, or a revert. Use it for anything that implements a ticket or a spec, anything touching
money, auth or data, and any change produced mainly by an AI agent, where scope creep and
silently skipped requirements are the most common failure.
