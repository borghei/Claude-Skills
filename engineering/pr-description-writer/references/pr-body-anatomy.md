# PR Body Anatomy

Section-by-section guidance for a pull request description a reviewer can act
on without opening the diff first. The body has one job: let the reviewer
decide **how carefully** to review, **what** to look at, and **whether** the
merge can be undone.

## The five sections and the question each answers

| Section | Reviewer's question | Fails when |
|---------|--------------------|-----------|
| Summary | What changes, for whom? | It narrates the commits ("refactored X, updated Y, also cleaned Z") |
| Why | Why now, why this way? | It is only a ticket key, or restates the summary |
| Evidence | How do I know it works? | It is an assertion ("tested, works") with nothing to look at |
| How to verify | How do I see it myself? | It says "tested locally" or "CI is green" |
| Merge risk | What happens if this is wrong, and can we undo it? | It says "low risk" with no classification or rollback |

Order matters. Reviewers read top-down and stop early; put the decision-making
content (summary, risk) where it is read, and the verification detail where it
is used.

## Summary

**Rule [PROVEN]:** one or two sentences, written for the person who will be
paged if it breaks, not for the person who wrote it. Lead with the behaviour
change, not the code change.

| Weak | Strong |
|------|--------|
| Refactor `InvoiceRenderer` and update tests | Invoices now print names in the customer's stored order instead of guessing at render time |
| Add caching layer | `GET /reports/:id` serves from a 5-minute cache; first load unchanged, repeat loads drop from ~1.8 s to ~40 ms |

### When to add a picture

Add **one** small visual only when it is faster to read than the prose. Pick
the smallest form that shows the point:

| Change shape | Best visual | Example |
|--------------|-------------|---------|
| Data shape / schema / payload | `diff` block of the structure | `+ given_name` under `Customer` |
| Control flow / new step in a pipeline | call tree, indented | `submit -> validate -> +enrich -> persist` |
| Component or module boundaries | file tree, two levels deep max | `src/billing/{render,tax}` |
| Interaction between services | `mermaid` sequence diagram, 3-5 participants | client, API, queue, worker |
| State machine change | `mermaid` stateDiagram with only the changed edges highlighted | |
| Algorithm change | 5-10 lines of pseudocode | |

Do not paste the code diff into the summary; the reviewer has the diff tab.
Do not draw everything; a diagram with twelve boxes is a second diff.

## Why

One short paragraph: the problem as the user or operator experiences it,
the constraint that shaped the solution, and the ticket link. If you rejected an
obvious alternative, one sentence on why saves a review round-trip:
"Not done in the renderer because the PDF service caches rendered templates
for 24 h."

## Evidence

Evidence is something the reviewer can **look at**, captured from a real run.
Strongest first:

| Tier | Form | Use for |
|------|------|---------|
| 1 | Screenshot or short recording, before and after side by side | Any visible UI change. Nothing else is as fast to review |
| 2 | Test output: the specific test that failed before and passes now | Bug fixes, behaviour changes |
| 3 | Command or log output from a real run (CLI, curl, migration plan, `EXPLAIN`) | Backend, data, infra |
| 4 | CI or staging run link | Supplement to 1-3, never alone: links rot and require a click |
| 5 | Metrics (latency, error rate, bundle size) with the measurement method | Performance work |

**Before and after.** For a fix, show the failure first. A passing test proves
nothing if the reader cannot see it failed without the change. For a refactor
with no behaviour change, the evidence is "same output before and after":
show both.

**Redact before pasting.** Logs and curl commands carry bearer tokens, cookies,
session IDs, customer emails and internal hostnames. `pr_body_lint.py` scans
for the common credential shapes and fails the body; anything it finds must be
treated as leaked and rotated, not just deleted, because PR bodies are
indexed, emailed and cached by integrations.

## How to verify

Numbered steps that a reviewer can repeat in under ten minutes, each with the
exact command and the expected result:

```markdown
1. `make seed && make run`
2. `curl -s localhost:8000/api/customers/c_8812 | jq .given_name` prints `"Yuki"`.
3. Open /invoices/INV-1001/preview: the name reads "Tanaka Yuki".
```

If verification needs credentials, a feature flag or a specific dataset, say so
in step one. If verification is genuinely impossible outside production (third-
party webhook, hardware), say that and describe the post-merge check instead.

## Merge risk

See `merge-risk-classification.md` for the full taxonomy. The section needs
three statements:

1. **Classification:** one-way or two-way door, in those words.
2. **Blast radius:** who or what breaks if this is wrong (a page, an endpoint,
   one tenant, every write path).
3. **Rollback plan:** for two-way, "revert this PR" is enough. For one-way,
   the exact steps, who runs them, how long they take, and what data or
   clients are left in which state afterwards.

Over-classifying is fine; under-classifying is the failure that hurts. A PR
that says "fully reversible" and ships a `DROP COLUMN` is the one that pages
someone at 2 a.m. with no plan.

## Length and tone

- **Target 150-400 words.** Over ~900, move detail to a design doc or the commit
  messages and link it.
- **No preamble.** Skip "This PR...", "In this pull request I have...".
- **Use the codebase's names.** Write `InvoiceRenderer`, not "the rendering component".
- **Delete template comments.** Leftover `<!-- -->` hints tell the reviewer the
  author did not reread the body.
- **Update the body when the PR changes.** A body that describes revision 1 of a
  PR on revision 4 is worse than no body.

## Size signals that should change the PR, not the body

If writing the summary needs more than two sentences or the picture needs more
than one diagram, the PR is probably two PRs. Common splits:

- Mechanical refactor (rename, move) in one PR, behaviour change in the next.
- Expand migration in one PR, code switch in the next, contract migration last.
- Dependency upgrade alone, then the code that uses the new version.

A reviewer approves a 200-line single-purpose PR in minutes and skims a
2,000-line mixed one; the second gets a worse review, not a slower one.
