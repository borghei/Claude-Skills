# Workspace File Formats

Every file in a learning workspace, what belongs in it, what does not, and the exact
schema the tools read. Read this when scaffolding a workspace by hand, when editing
`learning-record.json`, or when a tool rejects a file.

## Layout

```
<workspace>/
├── MISSION.md              # why the learner is doing this; success criteria
├── CURRICULUM.md           # modules in dependency order with observable outcomes
├── RESOURCES.md            # vetted sources with a trust tier
├── GLOSSARY.md             # one meaning per term, used in every lesson
├── NOTES.md                # teaching preferences and working notes
├── learning-record.json    # machine-readable state: sessions, items, misconceptions
└── lessons/
    ├── 0001-<slug>.md      # one file per lesson, numbered in order taught
    └── 0002-<slug>.md
```

`workspace_scaffolder.py` creates all of it from a spec. The workspace is plain files on
purpose: it survives tool changes, can live in a git repo, and any assistant can resume
from it with no memory of earlier sessions.

## Spec (input to the scaffolder)

```json
{
  "topic": "string — the subject",
  "why": "string — the concrete outcome that changes when the skill exists",
  "success": ["observable thing the learner can do", "..."],
  "constraints": {"minutes_per_session": 30, "sessions_per_week": 3, "deadline": "YYYY-MM-DD"},
  "prior_knowledge": ["claimed prior knowledge, to verify in lesson 1"],
  "modules": [{"id": "M1", "title": "...", "outcome": "observable", "depends_on": []}],
  "resources": [{"title": "...", "kind": "book|course|doc|video|community|tool",
                 "trust": "primary|secondary|unvetted", "url": "", "use_for": "..."}]
}
```

### Gate rules

| Field | Error when | Why |
|---|---|---|
| `why` | Missing, or a short restatement like "to understand X" | Without a real outcome there is no way to choose the next lesson |
| `success` | Empty, or any item uses understand/know/familiar/grasp/learn | Unobservable criteria cannot be checked, so the mission never ends |
| `modules` | Empty, duplicate ids, missing outcome, unknown dependency, cycle | The curriculum cannot be ordered |

Warnings: more than 12 modules, no resources, no primary source, no community, no session
length.

### Writing an observable success criterion

| Unobservable | Observable |
|---|---|
| Understand p-values | Explain in two sentences what p = 0.03 means for a named test, without the "97% chance" error |
| Know Spanish | Hold a 10-minute unscripted conversation about work with a native speaker |
| Be comfortable with SQL | Write a query with two joins and a window function from a plain-English request in under 15 minutes |
| Learn yoga | Hold the standing sequence for 20 minutes with form a teacher signs off |

Test: could someone watch the learner and say yes or no?

## MISSION.md

Sections: **Why** (1–3 sentences, the real outcome), **Success looks like** (checkbox list
of observable criteria), **Constraints** (session length, frequency, target date), **Prior
knowledge (claimed)**, **Mission changes** (dated table).

Rules:

- The mission grounds every lesson choice. If a lesson cannot be tied to a line in it,
  question the lesson.
- Missions change as the learner discovers what they actually care about. That is normal.
  Confirm with the learner, update the file, add a row to **Mission changes** with the
  reason, and record it in the learning record's session notes.
- Prior knowledge is a claim until a lesson verifies it.

## CURRICULUM.md

One table: Module, Title, Outcome (observable), Needs (prerequisite ids), Status
(`todo|active|done`).

- A module spans several lessons. It is `done` when its outcome has been demonstrated,
  not when its material has been covered.
- Keep one module `active` at a time. Two at once splits attention and doubles warm-up load.
- Re-order freely as the learner's real needs emerge; keep the dependency column honest.

## RESOURCES.md

Columns: Title, Kind, Trust, Link, Use for.

| Trust tier | Meaning | Use |
|---|---|---|
| `primary` | Authoritative source: standard text, official documentation, the original paper or spec | Ground every factual claim in a lesson |
| `secondary` | Reputable explainer, course, experienced practitioner | Alternative explanations, practice material |
| `unvetted` | Found but not checked | Do not teach from it until promoted |

Each lesson should point to one primary source for the learner to read or watch next.
List at least one **community** — a forum, class, study group or colleague circle — where
the learner can test judgment against people who do the thing for real.

## GLOSSARY.md

Columns: Term, Meaning in this workspace, First lesson. One meaning per term. Once a term
is defined, every later lesson uses it with exactly that meaning; drifting vocabulary is a
reliable source of confusion. Add terms when a lesson introduces them, not in bulk.

## NOTES.md

Free-form. Record teaching preferences the learner states ("prefers code over diagrams",
"no lessons after 21:00", "already uses R at work"), working notes, and anything the next
session needs that does not fit elsewhere. Read it at the start of every session.

## lessons/NNNN-slug.md

Numbered sequentially (`0001`, `0002`, …), slug from the lesson's core idea. Sections:

1. **Win for this lesson** — the one thing the learner will be able to do at the end.
2. **Warm-up** — the due items from the scheduler, as retrieval questions.
3. **Core idea** — the minimum knowledge for the win, with a citation to a resource.
4. **Worked example** — fully worked, each step's reason stated.
5. **Practice** — 3–5 tasks, faded from the example, with immediate feedback.
6. **Exit check** — explain-back plus one transfer question.
7. **Primary source** — what to read or watch next.
8. **Record after the lesson** — items introduced, misconceptions surfaced.

Lessons are rarely re-read; durable reference material belongs in the glossary or in a
cheat sheet the learner keeps.

## learning-record.json

The single source of truth for what the learner knows. `review_scheduler.py` reads it.

```json
{
  "topic": "string",
  "mission": "string",
  "modules": [{"id": "M1", "title": "...", "status": "todo|active|done", "depends_on": []}],
  "sessions": [{"n": 1, "date": "YYYY-MM-DD", "module": "M1", "lesson": "lessons/0001-x.md",
                "notes": "optional"}],
  "items": [{
    "id": "C1",
    "concept": "one testable idea, phrased as a claim",
    "module": "M1",
    "state": "new|learning|secure",
    "introduced": "YYYY-MM-DD",
    "evidence": "what the learner did that shows understanding",
    "reviews": [{"date": "YYYY-MM-DD", "result": "recalled|partial|failed"}]
  }],
  "misconceptions": [{
    "id": "X1",
    "belief": "the wrong model, in the learner's words",
    "correction": "the replacement model",
    "status": "open|corrected",
    "found": "YYYY-MM-DD",
    "recheck": "YYYY-MM-DD",
    "item": "C3"
  }]
}
```

### Item states

| State | Meaning | Required |
|---|---|---|
| `new` | Introduced, not yet shown | `introduced` date |
| `learning` | Shown at least once in the lesson | `evidence` text |
| `secure` | Survived spaced retrieval | `evidence` plus a streak of 3 including a 5+ day gap |

### What counts as evidence

Evidence names an action, not an exposure: "rewrote the dashboard caption correctly",
"predicted the spread before running the simulation", "held the pose 60 s with neutral
spine (teacher check)". Not evidence: "covered in lesson 3", "watched the video", "said it
made sense".

### Grading a review

| Result | When |
|---|---|
| `recalled` | Correct from memory without hints, at normal speed |
| `partial` | Correct with a hint, or the core right and a detail wrong |
| `failed` | Could not produce it, or produced the wrong model |

Grade honestly and immediately after the attempt. Inflated grades push the next review
out too far and the item is lost.

### What not to put in the record

- Activity logs ("did 40 minutes on intervals") — that is session notes, not learning.
- Material covered but not demonstrated.
- Glossary definitions — keep them in GLOSSARY.md.

## Gate reference for review_scheduler.py

| Finding | Severity |
|---|---|
| Item `secure` without 3 spaced recalls including a 5+ day gap | error |
| Item `learning` or `secure` with empty evidence | error |
| Review dated after `--today` | error |
| Open misconception with no recheck date | error |
| Module depends on unknown module | error |
| Item more than 14 days overdue | warn |
| Misconception recheck date has passed | warn |
| Module started before a prerequisite | warn |
| More than one module active | warn |
