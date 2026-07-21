# Extraction Rules and Note Conventions

The rule catalogue behind deterministic extraction of decisions, actions and
open questions from meeting artefacts — plus the note-taking conventions that
make extraction reliable in the first place. Read this when tuning the parser
for a team's house style, when extraction quality is poor, or when defining how
a team should take notes.

---

## 1. Why rules rather than a model

Pattern rules are the right tool here for four reasons, and it is worth being
explicit about them because the instinct is to reach for a model.

1. **Auditability.** When an action is missed, you can point at the rule that
   did not fire and add a cue. A model that missed it gives you nothing to fix.
2. **Determinism.** The same notes produce the same register every time, so a
   diff between two runs means the notes changed — not the extractor.
3. **The failure mode is safe.** Rules under-extract; they miss items. Models
   over-extract, inventing owners and dates that were never agreed. A fabricated
   due date is far more damaging than a missed line, because it enters the
   tracker looking legitimate.
4. **Cost and latency.** Extraction runs on every meeting, forever.

The trade is real: rules need note conventions to work well. Section 4 covers
the conventions, and they are worth adopting regardless — they make the notes
better for humans too.

---

## 2. Cue taxonomy

Cues split into **strong** and **weak**. Strong cues fire anywhere, including
mid-paragraph. Weak cues fire only inside a list item or under a matching
section heading, where the surrounding structure already signals intent. This
two-tier design is what keeps discussion prose out of the action register — the
single largest source of false positives.

### Decision cues [PROVEN]

| Pattern | Example it catches |
|---------|--------------------|
| `DECISION:` / `Decision -` label | `DECISION: we ship behind a flag` |
| `we decided to/that` | `We decided to defer the migration` |
| `agreed to/that/on` | `Agreed to hold the September date` |
| `we're going with` | `We're going with the stopgap importer` |
| `we will <commit verb>` | `We will build the importer` |
| `approved`, `signed off`, `resolved to` | `Approved by Priya` |

The commit-verb list matters: `we will use / adopt / ship / keep / build / hold
/ move / go`. A bare `we will` is too loose — "we will need to think about it"
is not a decision, and admitting it as one inflates the decision count, which is
the metric the series diagnostic runs on.

### Action cues

**Strong** — fire anywhere:

| Pattern | Example |
|---------|---------|
| `ACTION:` / `TODO:` / `Next step:` label | `ACTION: open the PR` |
| `@name to` / `@name will` | `@lena to confirm the schema` |
| `^Name will <verb>` / `^Name to <verb>` | `Sam will scope the importer` |
| `[ ]` checkbox | `- [ ] draft the contract` |
| `takes the action` | `Kai takes the action` |

**Weak** — only in list items or an actions section:

| Pattern | Why it is weak |
|---------|----------------|
| `will <verb>` | Matches narrative future tense: "the migration will take a week" |
| `to <task verb>` | Matches infinitives everywhere in prose |
| `owns this/it` | Matches ownership discussion, not assignment |
| `needs to` | Frequently describes a system, not a person |

### Open-question cues

**Strong:** `Open question:`, `^TBD`, `still unclear/unknown/open/undecided`,
`we don't know`, `no resolution`.
**Weak:** `needs investigation/research/input`, inline `TBD`, a line ending in
`?`.

The trailing-`?` rule must stay weak. Transcripts are full of conversational
questions that were answered thirty seconds later; only a question captured in
a structured position is genuinely open.

---

## 3. Field extraction

### Owner detection, in priority order

1. `@handle` — highest confidence, unambiguous.
2. `Owner: Name` — an explicit label.
3. `^Name will|to|owns|takes` — a capitalised name at the start of the item.

Extraction runs against the **cleaned** text — after list markers, checkboxes
and leading labels are stripped — so `ACTION: Sam to open the PR` still matches
the `^Name` anchor. Running it against the raw line is the most common reason
owner detection silently fails on well-labelled notes.

**Reject-list.** `we`, `the`, `team`, `someone`, `everyone`, `tbd` are never
owners even when they occupy the grammatical slot. "The team will handle it"
must register as **unowned**, because that is exactly what it is. Accepting
"team" as an owner is the difference between a tracker that surfaces the
accountability gap and one that launders it.

### Date detection

| Format | Example |
|--------|---------|
| ISO | `2026-07-22` |
| Day-month | `18 Jul`, `18 July 2026` |
| Month-day | `Jul 18`, `July 18, 2026` |
| Relative anchored | `by next Tuesday`, `by EOW` |

**Vague dates are recorded as a distinct gap**, not as a date: `soon`, `next
sprint`, `ASAP`, `when I can`, `in the next few days`, `eventually`, `at some
point`. These are worse than no date, because they feel like a commitment to
the person saying them and read as nothing to everyone else. Flag them
explicitly — "Lena will produce the breakdown soon" needs a different
conversation than "Lena will produce the breakdown", and the tracker should say
which one it is.

**Relative dates are not resolved to calendar dates.** "Next Tuesday" depends
on the meeting date, which the parser may not know reliably. Recording the raw
string preserves the ambiguity honestly rather than inventing precision.

---

## 4. Line reflow

Notes are hard-wrapped. Without reflow, a wrapped decision extracts as its first
line only, which truncates exactly the clause that carries the rationale.

**Rule:** a line continues the previous one when it is not a heading, not a list
item, not a blockquote, and the previous line did not end on `.`, `!` or `?`.

A line ending in `:` **does** continue — `Approver:` on its own line followed by
the name is common, and treating `:` as a terminator splits the record from its
approver.

Line numbers are preserved from the **first** line of the joined unit, so the
register still points back to a findable location in the source.

---

## 5. Note conventions that make extraction reliable [RECOMMENDED]

Adopt these and rule-based extraction reaches roughly 90% recall. Without them
it sits closer to 60%, and the gap is entirely in the items that were sloppily
recorded — which are also the items least likely to get done.

### The five conventions

1. **Label decisions and actions with a keyword at line start.** `DECISION:`
   and `ACTION:` cost two seconds and remove all ambiguity. This one convention
   does more than the other four combined.
2. **One action per line.** "Sam will scope it and Lena will confirm the schema"
   extracts as one action with one owner. Split it.
3. **Owner first, then verb, then object, then date.** `Sam to open the importer
   PR by 2026-07-22`. This ordering is what the `^Name` anchor keys on.
4. **Always an ISO date.** "By Friday" is ambiguous across timezones and
   meaningless in a register read three weeks later.
5. **Name the approver on every decision.** `Approver: Priya`. A decision with
   no approver gets re-litigated by whoever was absent.

### The template line

```
DECISION: <what was decided, past tense>. Approver: <name>. <one-clause rationale>
ACTION: <Name> to <verb> <object> by <YYYY-MM-DD>
OPEN QUESTION: <the question>. Owner: <name>. Needs an answer by <YYYY-MM-DD>
```

An open question needs an owner and a date as much as an action does. An
unowned open question is how a known unknown becomes a surprise.

---

## 6. Known failure modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Decision counted twice | Restated in a summary section at the end | Deduplicate on normalised text before counting |
| Discussion prose in the action list | A weak cue fired inside a section heading's scope | Narrow the section heading match, or move prose out of labelled sections |
| Action missed entirely | Phrased passively: "the importer needs opening" | Convention 3; passive actions have no owner by construction, so the gap is real |
| Owner detected as a false name | Sentence starts with a capitalised non-name | Extend the reject-list with the team's recurring vocabulary |
| Question captured mid-transcript that was answered | Trailing `?` in a conversational line | Keep the `?` rule weak; rely on `OPEN QUESTION:` labels |
| Everything extracts as one giant item | File uses single line breaks between paragraphs | Ensure blank lines between paragraphs before parsing |

### Calibrating on a team's own notes

Run the parser over four past meetings, then have the note-taker mark what it
missed and what it invented. Two rounds of cue additions typically close most of
the gap. Track recall (found / actually present) rather than raw counts —
a parser that finds 20 items when 30 exist looks productive and is not.

**Never tune toward higher extraction counts.** The metric is agreement with a
human reading of the same notes. A parser tuned to maximise items found becomes
a parser that reports discussion as commitment, and the register stops being
trustworthy — which is the only property it has.

---

## 7. Source-format handling

Different artefacts fail differently. Know which one you have before judging
the output.

| Source | Extraction quality | Characteristic problem | Preparation |
|--------|-------------------|------------------------|-------------|
| **Structured markdown notes** | Best | Wrapped lines truncating items | Ensure blank lines between paragraphs |
| **Labelled transcript** | Good | Conversational noise, filler questions | Keep the `DECISION:` / `ACTION:` blocks the note-taker added |
| **Raw auto-transcript** | Poor | No labels, no structure, decisions phrased conversationally | Have a human insert labels first; accept low recall otherwise |
| **Chat log** | Poor to fair | Decisions split across many short messages | Extract the summary message, not the whole thread |
| **Slide deck** | Very poor | Content is fragmentary and context-free | Do not parse; use the notes taken alongside it |

**Raw auto-transcripts are the hard case.** A decision in speech rarely looks
like one in text — "yeah, let's just do the six then" is a real decision that no
defensible rule set will catch without also catching a great deal of noise.
Ten seconds of a note-taker typing `DECISION:` at the moment it happens is worth
more than any amount of rule tuning after the fact.

### Handling a backlog of unlabelled notes

When extracting from months of past notes with no conventions:

1. Run the parser and expect roughly 50-60% recall. Treat it as a shortlist.
2. Focus on the decisions, not the actions. Old actions are stale; old decisions
   are still load-bearing and are what you actually need reconstructed.
3. Read the source around each hit — the parser points at a location, and the
   surrounding paragraph carries the rationale that makes the decision usable.
4. Write the recovered decisions into a proper log going forward. Do not attempt
   to retro-fix the source notes; that work is never finished and never used.

---

## 8. Deduplication

Meetings restate. A decision made mid-meeting and repeated in a closing summary
extracts twice, which inflates decision counts and corrupts the density metric
the series diagnostic runs on.

**Normalise before counting:** lowercase, strip punctuation, collapse
whitespace, drop leading labels, then compare. Items sharing a normalised prefix
of 60+ characters are near-certainly the same item.

Prefer the **later** occurrence when deduplicating decisions — a closing summary
usually states the final form, after amendments. Prefer the **earlier**
occurrence for actions, since that is where the owner and date were negotiated.

Do not deduplicate across meetings. The same action appearing in three
consecutive meetings is not a duplicate; it is a **carry-over**, and it is one
of the most valuable signals in the register. Collapsing carry-overs into one
item destroys exactly the data that predicts abandonment.

---

## 9. Quick reference — the conventions card

Give this to whoever takes notes. It is the whole intervention.

```
DECISION: <what was decided, past tense>. Approver: <one name>. <why, one clause>
ACTION:   <Name> to <verb> <object> by <YYYY-MM-DD>
OPEN QUESTION: <the question>. Owner: <name>. Answer needed by <YYYY-MM-DD>

Never write:  "the team will", "we should", "someone needs to"
Never write:  "soon", "ASAP", "next sprint", "when I get a chance"
One action per line. One owner per action. ISO dates only.
```

Five lines, adopted consistently, move rule-based extraction from roughly 60%
recall to roughly 90% — and they improve the notes for human readers by exactly
the same mechanism, because everything that makes an item machine-extractable
also makes it unambiguous to a person reading it three weeks later.
