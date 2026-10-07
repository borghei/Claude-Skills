# Story Bank File Format

The story bank is one JSON file that holds what a person can truthfully say
about their own working life. This document is the specification. The format is
owned by `linkedin-story-interviewer`; other skills may read a bank as optional
input but must keep working when none is supplied, and must parse the file
themselves rather than depend on this skill's scripts.

Schema version described here: **1**.

## Contents

1. Design decisions
2. Top-level fields
3. Entry fields
4. The seven entry kinds
5. Readiness: `ready` versus `soft`
6. Naming and no-go handling
7. Voice notes
8. Rules for anything that reads a bank
9. Where the file lives
10. Changing the format

## 1. Design decisions

**One flat list of entries, not sections.** An outage is at once a thing that
went wrong, a figure and a story told at dinner. Forcing it into a single
section loses two of the three uses. Each entry has one `kind` (its strongest
use) and any number of `pillars`.

**JSON, not prose.** The bank is read by tools as well as people. A plan
builder needs to count ready entries per pillar; an audit needs to match names
against a list. Both are trivial on JSON and unreliable on free text.

**Facts and wording kept apart.** `detail` holds what happened. `words` holds
how the owner phrased it. Drafts need both and should never have to guess which
is which.

**Status is explicit.** An entry that has not been pressed for a date or a
number is marked `soft`. Nothing downstream should have to infer whether a
sentence is firm enough to publish.

## 2. Top-level fields

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `schema_version` | integer | yes | `1` for this specification |
| `owner` | string | yes | Whose material this is |
| `updated` | string `YYYY-MM-DD` | yes | Date of the last session that changed the file |
| `sessions` | integer | yes | How many interview sessions have contributed |
| `pillars` | array of strings | yes | Two to five pillar names; entries are filed under these |
| `entries` | array of objects | yes | The material; see section 3 |
| `naming` | object | yes | Three lists: `free`, `ask_first`, `never` |
| `no_go` | array of strings | yes | Subjects that stay out of posts entirely |
| `voice_notes` | object | no | `says`, `never_says`, `sample_lines` |

Pillar names are free text, but keep them short and lowercase with hyphens
(`ops-craft`, `field-notes`). They must match the names used in a publishing
plan exactly if the plan is to draw on the bank.

## 3. Entry fields

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `id` | string | yes | Unique within the file. Convention: `S-001`, `S-002`, ... Never reuse an id after deleting an entry |
| `kind` | string | yes | One of the seven kinds in section 4 |
| `title` | string | yes | A label the owner will recognise months later |
| `detail` | string | yes | What happened, in facts. Aim for two or three sentences and at least a dozen words |
| `when` | string | yes | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. "Recently" is not a date |
| `pillars` | array of strings | yes | One or more names from the top-level `pillars` |
| `status` | string | yes | `ready` or `soft`; see section 5 |
| `naming` | string | yes | `clear`, `ask` or `anonymise`; see section 6 |
| `used_in` | array of strings | yes | One line per post that drew on the entry; empty when unused |
| `words` | string | no | Verbatim phrasing worth keeping |
| `figure` | object | kind-dependent | `value`, `measures`, `basis` |
| `before` / `after` | string | kind-dependent | The old belief and the new one |
| `price` | string | kind-dependent | What it cost |
| `against` | string | kind-dependent | Who disagrees |

### The `figure` object

| Key | Meaning | Example |
|-----|---------|---------|
| `value` | The number as the owner would say it | `37 claims down to 11` |
| `measures` | Exactly what is being counted | `customer spoilage claims per half-year across three depots` |
| `basis` | Where it comes from and how it was measured | `claims ledger kept by finance, same customers both halves` |

A figure with a `value` and no `measures` or `basis` cannot be defended if a
reader asks, and is reported by the audit as SB-015. Any entry may carry a
figure; an entry of kind `figure` must.

## 4. The seven entry kinds

| Kind | What it holds | Extra fields required | Typical use in a post |
|------|---------------|-----------------------|-----------------------|
| `role` | A job or stretch of work: where, when, what the owner answered for | none | Establishes standing in one line |
| `figure` | A number the owner can state from memory | `figure` | The concrete anchor a claim rests on |
| `build` | Something that exists because the owner worked on it | none | Evidence that advice was earned |
| `reversal` | A belief or plan held and then dropped | `before`, `after` | The turn in the middle of a post |
| `cost` | Something that went wrong and what it took | `price` | Stakes; the reason a lesson is believable |
| `stance` | An opinion the owner would defend against peers | `against`, `price` | The argument a post makes |
| `anecdote` | A story already told aloud, ending known | none | A scene to open on |

`reversal`, `cost` and `stance` are the **tension kinds**. A pillar with ready
entries but none of these three holds only successes, and the audit puts it on
the agenda.

Choosing between kinds when an event fits several: pick the kind whose extra
fields you can fill. If the owner can say what they believed before and after,
it is a `reversal`. If they can only say what it cost, it is a `cost`.

## 5. Readiness: `ready` versus `soft`

An entry is `ready` when all of the following hold:

- `when` is a real date at year precision or better
- `detail` contains at least one concrete thing: a number, a named place, a named artefact
- every field its kind requires is filled
- the owner has been asked about naming and the answer is recorded

Everything else is `soft`. Soft entries are worth keeping: they are the agenda
for the next session. They are not material for a draft.

The audit catches two kinds of drift. SB-020 fires when an entry is marked
`ready` but its text contains soft wording ("significantly", "a lot",
"recently") and no digit. SB-014 fires when a kind-specific field is empty.

## 6. Naming and no-go handling

### Per-entry `naming`

| Value | Meaning for a draft |
|-------|---------------------|
| `clear` | People and organisations in this entry may be named |
| `ask` | The owner must check with someone before this is published; a draft may be written but must be flagged |
| `anonymise` | Use the event, remove the identities ("a dairy customer", "a supervisor") |

### Bank-level `naming` lists

- `free`: names that may always appear
- `ask_first`: names that need consent each time
- `never`: names that must not appear in any post, comment or reply

The `never` list is checked against the text of every entry. An entry that
contains a never-name is a **blocker** (SB-001) even when its own `naming` is
`anonymise`, because the name is sitting in the file where a draft can copy it.
Rewrite the entry without the name.

### `no_go`

A list of short phrases for subjects that are out of bounds regardless of how
well they would perform. Write each one as the shortest phrase that would
actually appear in a sentence about it (`depot sale`, `union negotiation`),
because matching is literal and case-insensitive. An entry containing a no-go
phrase is a blocker (SB-002).

When a person declines to discuss something during an interview, add it here in
the same session and tell them it has been added.

## 7. Voice notes

`voice_notes` is optional and deliberately small. It exists because a person
who has never posted has no writing to analyse, but does have a way of talking
that surfaces during an interview.

| Key | Holds |
|-----|-------|
| `says` | Phrases the owner reaches for unprompted |
| `never_says` | Words the owner dislikes or would not use about their own work |
| `sample_lines` | Two to five sentences of theirs, verbatim, that sound most like them |

This is a starting point, not a style guide. Checking a finished draft for
machine-sounding phrasing is a separate job done on the draft itself.

## 8. Rules for anything that reads a bank

1. **Work without it.** A missing bank is normal. Fall back to asking the user.
2. **Use `ready` entries only.** A `soft` entry may be shown to the user as a
   question, never used as a fact.
3. **No figure from outside the bank.** If a draft needs a number and no entry
   supplies one, the draft goes without or the user is asked. Derived
   arithmetic on bank figures (percentages, differences) must be shown to the
   user before use.
4. **Honour `naming` and `no_go` literally.** Do not rephrase around them.
5. **Prefer unused entries.** Check `used_in` and reach for empty ones first.
6. **Append to `used_in` only on the user's say-so.** The bank records what was
   published, not what was drafted.
7. **Never write to the bank silently.** Any tool or session that changes the
   file says what it added.
8. **Parse it yourself.** Do not import code from this skill.

## 9. Where the file lives

The bank contains named colleagues, customer events and figures that were never
meant for public view. Treat it like a private notebook.

- Preferred: a folder outside any git repository.
- Acceptable: inside a repository, with the filename in `.gitignore` before the
  first entry is written.
- Not acceptable: committed, synced to a shared drive the owner does not
  control, or pasted into a ticket.

The audit walks up from the file looking for a `.gitignore` that covers it and
reports SB-031 when the file sits inside a working tree with no matching rule.
The check is a plain filename and path match and does not implement every
ignore-pattern feature, so read the note as a prompt to look, not as proof
either way.

## 10. Changing the format

Add fields freely; readers must ignore keys they do not recognise. Renaming or
removing a field, or changing the meaning of a status, requires bumping
`schema_version` and updating this document, the template and the sample in the
same change.
