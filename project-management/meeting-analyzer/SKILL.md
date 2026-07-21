---
name: meeting-analyzer
description: >
  Turn meeting notes into an accountable register — extract decisions, actions
  and open questions, flag ownerless items, track follow-through. Use when
  commitments get dropped or a recurring meeting decides nothing.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-07-21
  tags: [meeting-notes, action-items, accountability, decision-log, meeting-health]
---

# Meeting Analyzer

Meetings fail at the seam between talking and tracking. The decision gets made
and nobody records who approved it; the action gets stated and nobody's name
lands on it; the same topic returns for the seventh week because discussing it
feels productive and deciding it feels risky. This skill closes that seam with
deterministic extraction — pattern rules, no model calls — and then follows the
commitments across meetings to see which ones actually close.

## Scope note

This is the **accountability** lens on meetings, not the summary lens. It
extracts and tracks; it does not write the polished recap. Use it on notes that
already exist, across a series, when the question is "did anything we said we
would do actually happen?"

## When to use this skill

- **Actions keep getting dropped** — items agreed in one meeting quietly
  reappear three weeks later, or never do
- **A recurring meeting feels pointless** — you need decision density and topic
  churn measured before proposing to cancel it
- **Notes exist but no register does** — months of markdown notes with decisions
  buried in prose that nobody can find or count
- **The same topic returns every week** — you need evidence of churn to force a
  decision owner and a deadline
- **Preparing a retro or a meeting audit** — completion rates and ageing per
  meeting show which rituals produce work that gets done
- **Onboarding onto an existing project** — extracting the decision log from
  past notes reconstructs why the system looks the way it does

## Inputs the skill expects

- Meeting notes or transcripts as markdown or plain text, one file per meeting
- Ideally several meetings from the same series, so trends are visible
- An action-item register with created date, due date, owner, status and
  carry-over count (the parser bootstraps this from notes)
- Per-occurrence series data: attendance, duration, decisions, actions, whether
  an agenda was posted and notes published, and the topics covered
- The reference date for ageing calculations, if not "the newest date in the data"
- Which meeting types to exclude from decision-density scoring (retros,
  brainstorms, incident reviews legitimately decide little)

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Whether owners and dates may be inferred** — the answer is no by default; a fabricated due date enters the tracker looking legitimate and is far more damaging than a flagged gap
- [ ] **Meeting type** — a retro or brainstorm scored on decision density will look broken when it is working exactly as intended
- [ ] **The reference date for ageing** — "overdue" is meaningless without it, and pulling from the system clock makes yesterday's report irreproducible
- [ ] **Who sees the per-owner output** — aggregate for the team, per-person only in a 1:1; low follow-through is usually over-assignment, not under-delivery

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Extract an accountable register from raw notes

1. Point the parser at the notes file. It buckets every item into decisions,
   actions and open questions, and pulls owner and due date from each action.
2. Read the completeness rate first. Anything under 60% means the meeting
   produced intentions, not commitments.
3. Work the flagged gaps **in the room or in the thread the same day**. Asking
   "who owns this?" a week later means reconstructing a conversation nobody
   remembers, and the answer becomes whoever feels most guilty.
4. Never infer a missing owner or date. A flagged gap is the deliverable — it is
   the thing that gets fixed.
5. Add `--strict` in CI over a notes directory to fail the build when a meeting
   lands actions with no owner or date.

```bash
python3 project-management/meeting-analyzer/scripts/meeting_notes_parser.py \
  --input project-management/meeting-analyzer/assets/sample_notes.md \
  --format text --strict
```

### Workflow 2 — Track follow-through across a series

1. Append each meeting's extracted actions to a register in
   `assets/sample_commitments.json` shape, keeping `created`, `due`, `owner`,
   `status` and `carried_over`.
2. Run the tracker with an explicit `--as-of` so the report is reproducible.
3. Read in this order: completion rate, the ageing distribution, then per
   meeting. Per-owner comes last and never first.
4. Act on the 30+ day band — close, reassign, or explicitly drop. An action
   auto-closed at 30 days that genuinely mattered gets re-opened within a week;
   one that nobody notices did not matter.
5. Apply the three-strike rule to anything with `carried_over >= 3`: re-commit
   with a date the owner states out loud, or drop it. There is no fourth carry.

```bash
python3 project-management/meeting-analyzer/scripts/commitment_tracker.py \
  --input project-management/meeting-analyzer/assets/sample_commitments.json \
  --as-of 2026-07-21 --format text
```

### Workflow 3 — Diagnose a recurring meeting that decides nothing

1. Assemble 8-12 occurrences with attendance, decisions, actions, agenda and
   notes compliance, and the topics covered.
2. Run the diagnostic. It returns decision density, churning topics, attendance
   trend, and a KEEP / RESTRUCTURE / ASYNC / KILL verdict with a prescription.
3. Check the exclusions before acting — retros and brainstorms score badly by
   design and should be removed from the input, not accommodated by lowering
   the floor.
4. Take the churning topics to the room with the one diagnostic question: *who
   can actually decide this?* The answer picks the fix.
5. Fix hygiene before cancelling. A series at 30% agenda compliance has not yet
   been tried as a well-run meeting.

```bash
python3 project-management/meeting-analyzer/scripts/meeting_series_diagnostic.py \
  --input project-management/meeting-analyzer/assets/sample_series.json \
  --churn-threshold 3 --format text
```

## Decision frameworks

### The action-item completeness gate [PROVEN]

| Has owner | Has date | Verdict |
|-----------|----------|---------|
| Yes | Yes (ISO) | Tracked |
| Yes | Vague ("soon", "next sprint") | **Gap** — the owner believes they committed; nobody else does |
| Yes | None | **Gap** — reads as "someday" |
| No | Either | **Gap** — an action owned by "the team" is owned by nobody |

`we`, `the team`, `someone`, `everyone` and `TBD` are never owners, even when
they occupy the grammatical slot. Accepting them launders the gap instead of
surfacing it.

### Follow-through benchmarks [RECOMMENDED]

| Metric | Healthy | Warning | Broken |
|--------|---------|---------|--------|
| Completion rate | 75%+ | 50-75% | under 50% |
| Owner **and** date present | 90%+ | 70-90% | under 70% |
| On-time closure | 70%+ | 50-70% | under 50% |
| Open beyond 30 days | 0-1 | 2-4 | 5+ |
| Average carry-over | under 1 | 1-2 | 3+ |

Carry-over predicts abandonment better than age. An item carried three times has
usually been silently deprioritised by its owner but never formally dropped.

### Decision density verdicts [PROVEN]

Density = decisions produced / person-hours consumed.

| Density | Verdict | Action |
|---------|---------|--------|
| 0.35+ | KEEP | Healthy: a 60-min meeting of 5 produces 2+ decisions |
| 0.15-0.35 | RESTRUCTURE | Cut duration 25%; trim to the people who hold the decision |
| under 0.15 | ASYNC | Move standing content to a written update |
| under 0.15 **and** 40%+ empty occurrences | KILL | Cancel; replace with a written update and a comment window |

Exclude retros, brainstorms, incident reviews and onboarding — they decide
little by design. Exclude them explicitly rather than lowering the floor, or the
floor stops catching the status meetings it exists to catch.

### Reading low follow-through

Low follow-through has four common causes and only one of them is the person:
over-assignment (one owner holding 40%+ of open actions), deadlines set by
someone other than the owner, an unclearable blocking dependency, or a meeting
generating more actions than the team has capacity for. **When every owner looks
bad, the meeting is the problem** — see the diagnostic table and per-owner
interpretation guidance in `references/accountability-and-series-health.md`.

## Anti-Patterns

### Inferring the Missing Owner
**Mistake:** Filling in a plausible owner or date for an action the notes left blank, so the register looks complete.
**Why it happens:** An incomplete register feels like a failure of the extraction, and a model will happily supply a name. Completeness is mistaken for quality.
**Instead:** Leave it flagged. The gap **is** the finding — an unowned action is genuinely unowned, and surfacing it is the entire value. Rules under-extract and models over-extract; a fabricated due date enters the tracker looking legitimate and nobody ever questions it again.

### The Decorative Register
**Mistake:** Maintaining a meticulous action list that is reviewed by reading every row aloud at the next meeting, and never acted on.
**Why it happens:** The register becomes a performance of diligence. Reading it all feels thorough, and cutting the review feels like letting standards slip.
**Instead:** Review overdue items and third carry-overs only — under five minutes. Everything on track needs no airtime. A register that consumes twenty minutes a week to change nothing is more expensive than having no register.

### Weaponising Per-Owner Data
**Mistake:** Opening a team meeting with the per-owner follow-through table and asking the bottom name to explain themselves.
**Why it happens:** The data looks like performance data, and it is right there, ranked.
**Instead:** Share follow-through in aggregate with the team and per-person only in a 1:1, as a question rather than a verdict. When every owner looks bad, the meeting is over-generating actions — treating that as several simultaneous performance problems is both wrong and expensive, and it teaches people to accept fewer actions rather than to close more.

### Scoring Every Meeting on Decision Density
**Mistake:** Running the series diagnostic across the whole calendar and proposing to cancel the retro because it produced two decisions in ten weeks.
**Why it happens:** The metric is clean and comparable, which makes it tempting to apply universally.
**Instead:** Exclude retros, brainstorms, incident reviews and onboarding before scoring. Their output is shared understanding, not convergence. Excluding them keeps the floor sharp enough to catch the status meeting it was built for.

### Cancelling Before Fixing Hygiene
**Mistake:** Killing a low-density meeting that never had an agenda or published notes.
**Why it happens:** The density number is damning and cancellation is a satisfying, visible action.
**Instead:** Fix hygiene first — agenda-or-cancel plus published notes — and re-measure over four occurrences. A series at 30% agenda compliance has not been tried as a well-run meeting yet, and cancelling it moves the same unresolved topics somewhere less visible.

## Files

| File | Purpose |
|------|---------|
| `scripts/meeting_notes_parser.py` | Extracts decisions, actions and questions from notes; detects owners and dates; flags gaps; `--strict` exits 1 |
| `scripts/commitment_tracker.py` | Ageing, completion and on-time rates, carry-over, per-owner and per-meeting breakdowns, deterministic `--as-of` |
| `scripts/meeting_series_diagnostic.py` | Decision density, churning topics, attendance decay, hygiene compliance, KEEP/RESTRUCTURE/ASYNC/KILL verdict |
| `references/extraction-rules-and-note-conventions.md` | Cue catalogue, owner/date detection, reflow, source-format handling, deduplication, note conventions, failure modes |
| `references/accountability-and-series-health.md` | Commitment lifecycle, benchmarks, per-owner interpretation, decision density, topic churn, action caps, escalation ladder |
| `assets/action_register_template.md` | Register: open actions, third-carry-over gate, decision log, open questions, health snapshot |
| `assets/sample_notes.md` | Wrapped markdown notes, mixed-quality actions (extracts at 33% completeness) |
| `assets/sample_notes_transcript.txt` | Labelled transcript (extracts at 100%) — the contrast shows what note conventions buy |
| `assets/sample_commitments.json` | 18-action register across 5 meetings and 7 weeks |
| `assets/sample_series.json` | 10 occurrences of a weekly alignment meeting |
