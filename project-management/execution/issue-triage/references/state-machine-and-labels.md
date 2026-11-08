# Triage State Machine and Label Scheme

Triage is the act of deciding, for every inbound issue or external pull
request, what it is, whether it is real, whether the project wants it, and who
does the next thing. Treating it as a state machine instead of a pile of
labels gives three properties that ad-hoc triage never has:

1. **Every item has exactly one owner of the next move.** A state names who is
   expected to act: the triager, the reporter, an agent, or a maintainer.
2. **Illegal shortcuts are visible.** A bug that jumps from `new` to
   `accepted` without anyone reproducing it is a detectable defect, not a
   judgment call buried in a comment.
3. **The queue can be read at a glance.** Counting items per state tells you
   where the bottleneck is (reporters slow to answer, triagers behind, briefs
   not written, agents idle).

## States

| State | Open/closed | Meaning | Next move owned by |
|---|---|---|---|
| `new` | open | Arrived or re-entered; not yet evaluated | Triager |
| `needs-info` | open | A specific question is waiting on the reporter | Reporter |
| `reproduced` | open | Bug confirmed from the report's steps; for a PR, the diff verified to do what it claims | Triager |
| `accepted` | open | The project wants this; it is not yet specified for hand-off | Triager |
| `ready-for-agent` | open | A brief is posted; a coding agent may pick it up unattended | Agent |
| `ready-for-human` | open | A brief is posted; a person must do it, and the brief says why | Maintainer |
| `duplicate` | closed | Same root cause or concept as a canonical item, which is linked | — |
| `out-of-scope` | closed | Deliberately rejected; recorded in the out-of-scope register | — |
| `already-implemented` | closed | The request already exists; the closing note says where | — |
| `stale-closed` | closed | Sat in `needs-info` past the close window | Reporter may reopen |
| `resolved` | closed | Fixed, built, or merged | — |

`reproduced` is the state most teams skip, and skipping it is where most
wasted engineering time comes from: a bug that was never reproduced gets a
brief, an agent "fixes" something, and the original symptom remains.

### Why `accepted` and `ready-for-*` are separate

`accepted` answers "do we want this?". `ready-for-agent` and
`ready-for-human` answer "is it specified well enough that someone can start
without asking a question?". Collapsing them produces the most common failure
in agent-assisted teams: items labelled for an agent that carry only the
reporter's original text. The brief is the gate between the two.

## Legal transitions

| From | Allowed to | Notes |
|---|---|---|
| (none) | `new` | Every history starts here |
| `new` | `needs-info`, `reproduced`, `accepted`*, `duplicate`, `out-of-scope`, `already-implemented` | *`accepted` directly only for non-bugs |
| `needs-info` | `new`, `reproduced`, `stale-closed`, `duplicate`, `out-of-scope`, `already-implemented` | `new` when the reporter replies |
| `reproduced` | `accepted`, `needs-info`, `duplicate`, `already-implemented` | `needs-info` if reproduction raised a new question |
| `accepted` | `ready-for-agent`, `ready-for-human`, `out-of-scope` | `out-of-scope` only for a genuine re-scope, with a register entry |
| `ready-for-agent` | `ready-for-human`, `accepted`, `resolved` | Back to `accepted` when the brief is withdrawn for rework |
| `ready-for-human` | `ready-for-agent`, `accepted`, `resolved` | To agent once the human-only part is done |
| any closed state | `new` | Reopening always re-enters triage; it never resumes mid-flow |

Two transitions deserve explanation.

**`needs-info → new` on reply.** When the reporter answers, the item does not
jump straight to `reproduced` or `accepted`. It returns to `new` so it is
re-evaluated with the new information, and it reappears in the triager's
queue. The validator warns when someone other than the reporter performs this
move, because that usually means a maintainer cleared the state without an
answer.

**Reopen goes to `new`.** A reopened `out-of-scope` item means the decision
is being reconsidered; a reopened `duplicate` means the link was wrong; a
reopened `stale-closed` means the reporter came back. In every case the item
needs fresh evaluation, so it re-enters at the top.

### Bug versus enhancement paths

- **Bug:** `new → (needs-info ↔ new)* → reproduced → accepted → ready-for-*`.
  A bug may not reach `accepted` without passing `reproduced`.
- **Enhancement / chore / docs:** `new → accepted → ready-for-*` is fine,
  because there is nothing to reproduce. The redundancy and prior-rejection
  checks replace reproduction as the evidence step.
- **Question:** usually `new → resolved` (answered) or converted into a bug
  or enhancement by changing the type label and continuing.

## External pull requests

A pull request from outside the core team is an issue that arrives with code
attached. It moves through the same states with these readings:

| State | Reading for a PR |
|---|---|
| `reproduced` | The diff was checked out and does what it claims; relevant tests run |
| `accepted` | The project wants the change, independent of diff quality |
| `ready-for-agent` | A brief says what is left to do *to this diff* (finish, test, address review) |
| `ready-for-human` | A person must review, approve a contract, or merge |
| `out-of-scope` | The change is rejected; record it in the register so the same code does not return |

Two PR-specific rules:

1. Accept the *change* before judging the *code*. A clean diff for an
   unwanted feature is still out of scope; a rough diff for a wanted fix is
   an opportunity for a brief.
2. Only external PRs enter the triage queue by default. A collaborator's
   in-flight PR is not triage work unless someone names it explicitly.

## Stale `needs-info` policy

An item waiting on its reporter is the cheapest thing in the queue to forget
and the most expensive to leave open, because it pollutes every queue count.

| Window | Default | Action |
|---|---|---|
| Nudge | 7 days | One reminder comment that restates the specific questions |
| Close | 21 days | Close as `stale-closed` with a note that replying reopens it |

Rules:

- The clock starts at the transition into `needs-info`, not at issue creation.
- A reporter's reply resets the cycle by moving the item to `new`.
- Never auto-close `type:bug` items with `priority:p0` or `priority:p1`; a
  severe bug with a silent reporter becomes the triager's job to reproduce.
- Tune the windows to the project's rhythm: a weekly-release product can use
  5/14, a slow-moving library 14/45. Pass them to the validator with
  `--nudge-days` and `--stale-days`.

## Label scheme

Three label families carry the state machine. Everything else (area,
component, platform) is free-form.

| Family | Cardinality | Rule |
|---|---|---|
| `type:` | exactly one | Set at first evaluation; may change if a question becomes a bug |
| `state:` | exactly one | Must equal the destination of the last transition |
| `priority:` | at most one | Required from `accepted` onward |

The "exactly one" rules are the most valuable thing in the scheme. Two state
labels means two people disagree about who owns the item, and nobody does.
When a conflict is found, stop and ask the maintainer before applying any
change; do not pick one.

### Mapping to trackers

| Concept | GitHub | GitLab | Linear | Jira |
|---|---|---|---|---|
| type | `type:*` label or native issue type | scoped `type::*` label | "Type" label group | Issue type |
| state | `state:*` label (or project status field) | scoped `state::*` label, which enforces one | Workflow status | Workflow status |
| priority | `priority:*` label | scoped `priority::*` | Native priority | Priority field |
| duplicate | close reason "duplicate" + link | "duplicate of" relation | "Mark as duplicate" | "duplicates" link |

Where the tracker has native workflow statuses (Linear, Jira), map the states
onto statuses and keep the labels only for type; the invariant "one state per
item" is then enforced by the tool itself. GitLab scoped labels enforce
mutual exclusivity within a scope, which makes them the closest native match
to this scheme.

## Queue views

Three queries give a triager everything needing attention, oldest first:

1. Items with no `state:` label at all (never triaged).
2. `state:new` (evaluation pending, including reporter replies).
3. `state:needs-info` past the nudge window.

And two views for the people downstream:

- `state:ready-for-agent` sorted by priority — the agent's work queue.
- `state:ready-for-human` sorted by priority — the maintainer's queue.

Run `triage_state_validator.py` on a weekly export; the `state_counts` block
in its output is the queue health snapshot. A growing `needs-info` count means
questions are too vague; a growing `accepted` count means briefs are not
being written; a growing `ready-for-agent` count with few `resolved` means
agents are failing on the briefs and they need tightening.

## Validator rule reference

| Rule | Severity | Trigger |
|---|---|---|
| `entry-state` | error | History does not start with a transition into `new` |
| `broken-chain` | error | A transition's `from` differs from the previous `to` |
| `illegal-transition` | error | Move not in the legal transitions table |
| `unknown-state` | error | Transition targets a state outside the machine |
| `date-order` | error | Transition dated before its predecessor |
| `type-label` | error | Zero or several `type:` labels |
| `state-label` | error | Zero or several `state:` labels |
| `state-drift` | error | `state:` label differs from the last transition |
| `priority-label` | error / warn | Several priorities (error); none from `accepted` on (warn) |
| `skipped-repro` | error | `type:bug` reached `accepted` without `reproduced` |
| `missing-brief` | error | `ready-for-*` with no brief reference |
| `human-reason` | error | `ready-for-human` with no reason it cannot be delegated |
| `duplicate-link` | error | `duplicate` with no or a self-referencing canonical link |
| `register-missing` | error | `out-of-scope` item absent from the register |
| `register-misuse` | error | Already-implemented work recorded in the register |
| `register-reason` | error | Register entry without a reason |
| `stale-needs-info` | error | `needs-info` longer than the close window |
| `nudge-needs-info` | warn | `needs-info` longer than the nudge window |
| `reply-actor` | warn | `needs-info → new` performed by someone other than the reporter |
| `closing-note` | warn | Closed (other than resolved) with no explanatory note |
