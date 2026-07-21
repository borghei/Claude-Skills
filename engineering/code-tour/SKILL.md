---
name: code-tour
description: >
  Build ordered, annotated tours of an unfamiliar codebase and keep the anchors from
  rotting. Use when onboarding an engineer, handing off a service, or explaining a
  subsystem before a review.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: developer-experience
  updated: 2026-07-21
  tags: [onboarding, code-reading, documentation, developer-experience, handoff]
---

# Code Tour

A guided path through a codebase, ordered so each stop makes the next one legible, and
annotated with why the code is the way it is rather than what it does. The what is
already on screen; the why is what takes a new engineer three weeks to reconstruct and
what the person who knows it will lose in six months. Tours rot faster than any other
documentation because they point at line numbers, so anchoring and validation are half
this skill.

## When to use this skill

- **Onboarding an engineer** onto a service where reading order determines whether week one is productive or archaeological
- **Handing off ownership** of a system before its author changes team or leaves
- **Explaining a subsystem** ahead of a design review, so reviewers arrive with shared context
- **Documenting a surprising design** whose rationale lives only in a closed pull request
- **Auditing an existing tour** that has silently rotted as files moved and functions were renamed
- **Re-entering your own code** after six months away, which is functionally the same problem as onboarding

## Inputs the skill expects

- The repository root, and which directories are vendored or generated
- The audience and their starting knowledge — a backend engineer and a frontend engineer need different first stops
- The one question the tour must leave answered ("how does a request become a row?")
- Time budget, which sets the stop count more than anything else
- The design decisions worth explaining, especially the ones that look wrong at first glance
- An existing tour definition, when validating or updating rather than authoring

## Clarify First

Before building the tour, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The question the tour answers** — a tour of "the codebase" has no ordering principle; a tour of "how a request becomes a row" orders itself
- [ ] **Audience and their existing knowledge** — decides which stops can be skipped and which concepts need a stop of their own
- [ ] **Time budget** — 30 minutes is 5-7 stops; anything longer gets abandoned midway and never resumed
- [ ] **Which decisions are worth explaining** — the why-notes are the entire value; without them the tour is a file listing

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Propose candidate stops from the repository

1. Run the analyzer against the repo root, excluding vendored and generated directories.
2. Read the ranked candidates. Entry points come first, then config and boundaries,
   then high-fan-in internals — that ordering is the analyzer's opinion about reading order.
3. Cut ruthlessly. Any candidate you cannot write a "why it is this way" note for is a
   file, not a stop.
4. Add stops the analyzer cannot see: the surprising workaround, the module that looks
   redundant and is not, the abstraction whose absence would be worse.

```bash
python3 engineering/code-tour/scripts/tour_propose.py \
  --repo . --max-stops 7 --exclude vendor --exclude generated --format text
```

Fan-in for Python comes from the AST import graph and is reliable. For other languages
it is a filename-reference heuristic and will over-count common names — treat those
scores as a ranked shortlist to review, not a verdict.

### Workflow 2 — Write the tour and audit the notes

1. Fill in each stop's `note`, `question`, and `gotcha` in the tour JSON. The note
   explains why; the question forces the reader to look at the code before moving on.
2. Anchor every stop to a **symbol name**, not a line number. Line numbers are recorded
   for convenience but resolved from the symbol on every validation.
3. Run the renderer's audit. It flags notes that only restate what the code does, notes
   under 20 words, and notes with no causal language.
4. Render the document once the why-ratio clears 0.8.

```bash
python3 engineering/code-tour/scripts/tour_render.py \
  --input engineering/code-tour/assets/sample_tour.json \
  --audit-only --min-why-ratio 0.8 --format text
```

The shipped sample scores 83% — stop 5 fails deliberately, so you can see what a
what-only note looks like next to four that explain why.

### Workflow 3 — Validate the tour against the current tree

1. Run validation before every use of the tour, and in CI on the branch that owns the code.
2. Read the statuses: `deleted` and `moved` are broken, `drifted` means the anchor's
   body changed and the note may now be wrong, `shifted` is cosmetic line movement.
3. For moved anchors, take the suggested relocations — they come from searching the
   tree for the anchor name.
4. Re-freeze line numbers and fingerprints with `--update` once you have re-read the
   drifted notes.

```bash
python3 engineering/code-tour/scripts/tour_validate.py \
  --tour engineering/code-tour/assets/sample_tour.json \
  --repo engineering/code-tour --format text
```

Stop paths are relative to the tour's own `repo` root, so `--repo` points at the
package the tour describes — here, this skill itself. Exit code is 1 when any stop is
broken, which is what lets a tour live in CI. The shipped sample exits 1 on purpose:
stop 6 points at a `scripts/tour_export.py` that was never shipped.

## Decision frameworks

### Choosing the first stop [PROVEN]

The first stop determines whether the reader builds a mental model or a list of facts.

| Tour purpose | First stop | Why |
|--------------|-----------|-----|
| "How does the system work?" | The entry point — `main`, the router, the CLI dispatcher | Execution order is the only ordering a newcomer already trusts |
| "How do I add a feature like X?" | The most recent similar feature, end to end | Pattern-matching beats principles for a first change |
| "Why is this designed this way?" | The constraint — the schema, the external contract, the SLA | Design decisions are unreadable without the constraint that forced them |
| "How do I debug this?" | The observability seam — logging, error handler, trace entry | Debugging is navigation, and navigation starts at the signal |

Never open on the data model. It is where authors want to start, because it is where
the domain lives, and it is where readers stall — a schema without a flow through it is
a vocabulary list.

### Stop count by time budget [RECOMMENDED]

| Budget | Stops | Words per note |
|--------|-------|----------------|
| 15 min | 3-4 | 40-60 |
| 30 min | 5-7 | 50-80 |
| 60 min | 8-10 | 60-100 |
| Over 60 min | Split into two tours | — |

Beyond ten stops readers stop retaining and start skimming, and a skimmed tour teaches
less than a well-chosen five-stop one. If the system genuinely needs fifteen stops,
that is two tours with different questions, not one long one.

### Anchoring strategy — what rots and what does not

| Anchor type | Rot rate | Use when |
|-------------|----------|----------|
| Symbol name (function, class) | Low | Default — survives every edit except a rename |
| File path only | Low | The stop is about a file's existence or shape |
| Distinctive string in a comment | Medium | Non-Python code with no stable symbol |
| Line number | Very high | Never as the anchor; record it as a convenience only |
| Line range | Very high | Never |

The tour format records `line` but resolves from `anchor`. A tour anchored on line
numbers is broken by the next unrelated edit above it, which is why most tours in the
wild are broken within a month of being written.

### When a stop is drifted, what actually changed?

| Signal | Likely cause | Action |
|--------|-------------|--------|
| Fingerprint changed, name and shape same | Refactor inside the body | Re-read the note; usually still true |
| Fingerprint changed, function much longer | Feature added inside the stop | Note is now incomplete — extend it or split the stop |
| Anchor missing, found elsewhere in tree | Moved or extracted | Re-point the stop; check the ordering still holds |
| Anchor missing everywhere | Renamed or deleted | Decide whether the concept still exists; delete the stop if not |

## Anti-Patterns

### The Line-Number Tour
**Mistake:** Anchoring stops to file paths and line numbers, so the tour points at `parser.py:142`.
**Why it happens:** Line numbers are what the editor shows and what a link needs, so they are the obvious thing to record. They are also correct at the moment of writing, which makes the problem invisible until later.
**Instead:** Anchor on the symbol name and resolve the line at validation time. Record the line as a convenience so readers can jump, but never let it be the identity of the stop. A tour that survives six months of refactoring is worth more than one that was slightly easier to write.

### The What-Not-Why Tour
**Mistake:** Notes that describe what the code does — "this function validates the input and returns a normalized record."
**Why it happens:** Describing behaviour is easy, feels informative, and can be done without remembering any history. Explaining why requires reconstructing a decision, which is genuinely harder.
**Instead:** For every stop, answer one of: why is it here, why is it this way and not the obvious alternative, and what breaks if you change it. If none of the three has an interesting answer, the file does not need a stop. Run the renderer's audit — it catches notes that open by restating behaviour.

### The Complete Tour
**Mistake:** Trying to cover every module so the reader is not left with gaps.
**Why it happens:** Omitting things feels like negligence, especially for the author who knows what is being left out. The reader does not know, and would not have retained it anyway.
**Instead:** Pick one question the tour answers and include only what serves it. Five stops that build one accurate mental model beat twenty that build a shallow index. Gaps get filled by the reader's first real task, which teaches better than any tour.

### The Orphaned Tour
**Mistake:** Writing the tour in a wiki, a doc site, or an onboarding deck, separate from the repository.
**Why it happens:** That is where onboarding material lives, and the tour is onboarding material. It also gets the tour in front of readers who never clone the repo.
**Instead:** Keep the tour definition in the repository it describes, and validate it in CI on that repository. A tour that cannot be broken by a code change will not be updated by one either. Publish a rendered copy wherever readers look, generated from the definition rather than maintained separately.

### Author-Order Stops
**Mistake:** Ordering stops the way the author thinks about the system — usually data model, then services, then interface.
**Why it happens:** That is the order the system was built in and the order it lives in the author's head. It feels like the logical decomposition, and for someone who already understands it, it is.
**Instead:** Order by what a newcomer can verify at each step. Start where execution starts, follow one real request or command through, and introduce each abstraction at the moment it first blocks understanding. The test: could the reader, after each stop, predict what the next file does? If not, a stop is missing before it.

## Files

| File | Purpose |
|------|---------|
| `scripts/tour_propose.py` | Rank candidate stops by entry-point, fan-in, and boundary signals using AST and file analysis |
| `scripts/tour_validate.py` | Resolve every anchor against the current tree; report deleted, moved, drifted, and shifted stops |
| `scripts/tour_render.py` | Render a tour into an onboarding document and audit notes for why-not-what quality |
| `references/tour-construction.md` | Stop selection, ordering models, note-writing patterns, and audience variants |
| `references/tour-maintenance.md` | Anchoring strategies, rot mechanics, CI wiring, and the rules for updating a drifted tour |
| `assets/sample_tour.json` | Runnable tour of this skill's own scripts, with a deliberately broken stop and a weak note |
| `assets/tour-template.json` | Empty tour definition with every supported field documented |
