# Evidence Checks, Needs-Info Craft, and the Out-of-Scope Register

Before an item earns `accepted`, triage has to establish three things: that
the request is not already satisfied, that the project has not already said
no to it, and — for bugs and PRs — that the claim holds up. This file covers
how to run each check, how to ask the reporter for what is missing, and how
to keep the out-of-scope register useful for years.

## 1. Redundancy check: is it already implemented?

A surprising share of enhancement requests describe something the product
already does, reached through a path the reporter did not find. Closing those
quickly, with directions, is the cheapest win in triage.

**Search by concept, not by the reporter's words.** "Export to spreadsheet",
"download as CSV" and "save table to Excel" are one concept. Search the code,
docs and changelog for:

- the domain noun (export, report, table),
- the user-facing verb (download, save, export),
- the format or channel (CSV, XLSX, clipboard),
- the CLI flag or settings key a feature like this would have.

**Report where you looked.** The triage comment should list the places
searched, even when nothing is found. "Searched the export module, CLI help,
settings reference and the last three changelogs: no CSV path exists" lets
the maintainer trust the conclusion without redoing the search.

**Outcomes:**

| Finding | Action |
|---|---|
| Fully exists | Close as `already-implemented`; say where it lives in user terms |
| Exists but hard to find | Close as `already-implemented` and open a `type:docs` item for discoverability |
| Partly exists | Keep open; rewrite the request as the missing delta |
| Does not exist | Continue to the prior-rejection check |

Never add already-implemented items to the out-of-scope register. The
register answers "did we decide not to do this?"; an implemented feature is
the opposite answer, and mixing them makes future matches lie.

## 2. Prior-rejection check: did we already say no?

Read the out-of-scope register before evaluating any enhancement. Match by
concept similarity, not keyword: "night theme" matches `per-user-themes`;
"let me write extensions in Lua" matches `plugin-runtime`.

When a match is found, surface it to the maintainer with the recorded
reason and ask whether it still holds. Three outcomes:

| Maintainer says | Action |
|---|---|
| Still holds | Append the issue to the entry's prior requests; close as `out-of-scope` with a link to the entry |
| Changed our mind | Update or delete the entry; the new item proceeds through normal triage |
| Related but different | Proceed with normal triage; optionally note the distinction in the entry |

The count of prior requests is product signal. An entry with twelve prior
requests in a year is a decision worth revisiting on purpose, at a planning
review — not one to overturn inside a single triage comment.

## 3. Verifying the claim

### Bugs: reproduce before accepting

Reproduction is the evidence that turns a report into a fact. Work from the
reporter's steps on the reported version first; only then try the latest.

| Result | Next state | Note to post |
|---|---|---|
| Reproduced as described | `reproduced` | Version, environment, minimal steps, observed vs expected |
| Reproduced on reported version, not on latest | `already-implemented` or `resolved` | Which release fixed it |
| Could not reproduce, steps complete | `needs-info` | What you ran and what happened instead; ask for the difference |
| Could not reproduce, steps incomplete | `needs-info` | The specific missing detail |

A reproduction note is the single most valuable input to a later brief. The
"current behavior" section of the brief is usually the reproduction note,
tightened.

When reproduction requires access the triager lacks (production data, a
customer's tenant, hardware), say so explicitly and decide whether the item
is still worth accepting on the strength of the report. High-severity reports
with credible evidence (logs, traces) can be accepted with a recorded
justification; the validator will still flag the missing `reproduced` step,
which is the point: the exception is visible.

### Pull requests: verify the diff

For an external PR, `reproduced` means the diff was checked out and does what
it claims:

- the relevant tests pass, and new behaviour has at least one test;
- the claimed bug fix actually changes the reproduced behaviour;
- the diff does not quietly change unrelated behaviour.

Record what was run. A PR that fails verification goes to `needs-info` with
the failing output, not straight to rejection.

## 4. Writing needs-info notes

A `needs-info` comment has two jobs: preserve everything already established
so nobody re-asks it, and ask only the questions whose answers change the
decision.

**Structure:**

1. *Established so far* — facts confirmed, things tried, what happened.
2. *What we need from you* — numbered, specific, answerable in a sentence or
   a paste.
3. *What happens next* — the reply returns the item to triage; the close
   date if there is no reply.

**Good and bad questions:**

| Bad | Why | Good |
|---|---|---|
| "Can you provide more info?" | The reporter cannot guess what is missing | "What does `app --version` print?" |
| "Can you share your setup?" | Unbounded | "Does it happen with the default config file, or only with yours? If only yours, please paste it with secrets removed." |
| "Is this still an issue?" | Invites a yes without evidence | "Does it still happen on 4.3.0, released last week?" |
| Five questions at once | Reporter answers the easy two | Ask the one or two that decide the next state |

**Resuming:** when a triage session picks up an item with earlier notes, read
them first, check which questions the reporter answered, and present an
updated picture before asking anything new. Re-asking an answered question
is the fastest way to lose a reporter.

## 5. Duplicates

Mark a duplicate only when both items share a root cause or a concept, not
just a symptom. Two crash reports with different stack traces are two
issues even if the crash dialog looks the same.

- Pick the **canonical** item: the one with the best reproduction or the most
  discussion, not necessarily the oldest.
- Copy anything new from the duplicate (an extra environment, a workaround)
  into the canonical item before closing.
- Link explicitly. A duplicate with no canonical link is a dead end, and the
  validator treats it as an error.

## 6. The out-of-scope register

### Purpose

The register is the project's memory of what it decided **not** to build,
and why. It prevents two failure modes: re-litigating the same request every
few months, and a decision silently reversing because nobody remembered it
was made.

### Format

One entry per **concept**, named in kebab-case so a newcomer can scan the
list: `per-user-themes`, `plugin-runtime`, `graphql-api`, `offline-mode`.
Each entry carries:

| Field | Content |
|---|---|
| `concept` | The kebab-case name |
| `decision` | `rejected` (the only valid value; see below) |
| `reason` | A durable reason a newcomer can understand without the threads |
| `revisit_if` | The concrete change that would reopen the question |
| `prior_requests` | Every issue or PR that asked for it |

It can live as one markdown file per concept in a repository folder, as a
wiki page, or as JSON for the validator. The validator only needs `concept`,
`decision`, `reason` and `prior_requests`.

### What makes a reason durable

| Not durable | Durable |
|---|---|
| "No capacity this quarter" | "Runtime theming needs a provider around every view; the rendering pipeline resolves one palette at build time, and embedders already theme downstream" |
| "Maybe later" | "The project targets single-tenant self-hosting; multi-tenant isolation would change the security model for every user" |
| "Too hard" | "A plugin runtime means a stable internal API; the project's value is changing internals freely between minor versions" |

A capacity or timing reason is a **deferral**, not a rejection. Deferred
items stay open with a low priority; they do not go in the register.

### What never goes in the register

- Bugs. A bug the project will not fix is closed with an explanation of why
  (by design, unsupported environment), not recorded as a rejected concept.
- Already-implemented requests.
- Duplicates of open work.

### Reconsidering

When a decision changes, delete or rewrite the entry and let the triggering
item proceed through triage. Old closed items stay closed; they are history.
The validator's `register-missing` check means any later `out-of-scope`
closure for the same concept will need a fresh entry, which forces the new
reason to be written down.

## 7. Recommending an outcome

After the checks, the triager posts a recommendation to the maintainer before
changing any label: category, proposed state, the reasoning, what was
searched, and what was run. The maintainer confirms or overrides. A direct
instruction from the maintainer ("move it to ready-for-agent") is applied as
given; the triager confirms the exact label changes and comments first, and
asks whether a brief should be written if one does not exist.

Unusual transitions — a closed item reopened straight into `ready-for-agent`,
two state labels on one item, a bug accepted without reproduction — are
flagged and confirmed before acting, never silently corrected.
