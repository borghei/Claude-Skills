# Label Scheme Template

Copy into the repository's contributing docs and create the labels once.
The prefixes are what `triage_state_validator.py` reads; the tracker column
shows how to express each one where labels are not the native mechanism.

## Invariants

- Exactly one `type:` label on every triaged item.
- Exactly one `state:` label on every item, matching its last transition.
- At most one `priority:` label; required from `state:accepted` onward.
- Area/component labels are free-form and unlimited.

## Type labels

| Label | Meaning |
|---|---|
| `type:bug` | Existing behaviour is wrong. Must pass through `reproduced` before `accepted`. |
| `type:enhancement` | New capability or a change to intended behaviour. |
| `type:chore` | Maintenance with no user-visible change (deps, CI, refactor). |
| `type:docs` | Documentation only. |
| `type:question` | Usage question; usually answered and closed, or converted. |

## State labels

| Label | Meaning | Owner of next move |
|---|---|---|
| `state:new` | Not yet evaluated | Triager |
| `state:needs-info` | Waiting on the reporter | Reporter |
| `state:reproduced` | Bug confirmed / PR diff verified | Triager |
| `state:accepted` | We want it; not yet specified for hand-off | Triager |
| `state:ready-for-agent` | Brief posted; a coding agent may take it | Agent |
| `state:ready-for-human` | Brief posted; needs a person (reason stated) | Maintainer |
| `state:duplicate` | Closed; points at the canonical issue | — |
| `state:out-of-scope` | Closed; recorded in the out-of-scope register | — |
| `state:already-implemented` | Closed; points at where it already exists | — |
| `state:stale-closed` | Closed after the needs-info close window | Reporter can reopen |
| `state:resolved` | Fixed or merged | — |

## Priority labels

| Label | Rule of thumb |
|---|---|
| `priority:p0` | Data loss, security, or outage. Interrupts current work. |
| `priority:p1` | Broken core path for many users; next in line. |
| `priority:p2` | Real but contained; scheduled normally. |
| `priority:p3` | Nice to have; taken when convenient. |

## Tracker mapping

| Concept | GitHub | GitLab | Linear | Jira |
|---|---|---|---|---|
| type | label `type:*` or issue type | scoped label `type::*` | label group "Type" | Issue type |
| state | label `state:*` | scoped label `state::*` (enforces one) | workflow status | workflow status |
| priority | label `priority:*` | scoped label `priority::*` | native priority | Priority field |
| duplicate link | "Duplicate of #n" comment / close reason | "Duplicate of" link | Mark as duplicate | "duplicates" link |
| PR in triage | PR with the same labels | MR with the same labels | linked PR on the issue | linked PR / dev panel |
