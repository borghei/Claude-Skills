# Architecture Review Playbook

How to run a codebase-level review that finds where modules should be deeper,
ranks the opportunities, writes them up, and then works through the chosen one
until there is an interface worth building. This is module-level work inside one
codebase; decisions about service boundaries, data stores and deployment
topology are system architecture and out of scope.

## Contents

- [Phase 1 — Choose where to look](#phase-1--choose-where-to-look)
- [Phase 2 — Scan](#phase-2--scan)
- [Phase 3 — Rank](#phase-3--rank)
- [Phase 4 — Write the report](#phase-4--write-the-report)
- [Phase 5 — Interrogate the chosen candidate](#phase-5--interrogate-the-chosen-candidate)
- [Phase 6 — Design the interface twice](#phase-6--design-the-interface-twice)
- [Phase 7 — Migrate](#phase-7--migrate)
- [Question bank](#question-bank)

## Phase 1 — Choose where to look

Deepening pays back through future changes, so look where change happens.

1. If the requester named an area or a pain point, start there and skip the rest of this phase.
2. Otherwise build a change-frequency map for the last six months:

   ```bash
   git log --since="6 months ago" --name-only --format= \
     | grep -E '\.(py|js|ts|tsx|jsx|mjs|cjs)$' | sort | uniq -c \
     | awk '{printf "%s\"%s\": %s", (NR>1?",":"{"), $2, $1} END {print "}"}' > churn.json
   ```

3. Read the top 20 paths. Clusters (several hot files in one directory) are stronger signals than a single hot file.
4. Read the project's glossary and decision records for those areas before scanning, so findings use the project's names and do not re-propose a decision already recorded.

## Phase 2 — Scan

Run the analyser from the repository root so its module names match the churn keys:

```bash
python3 path/to/module_depth.py --path . --churn churn.json --format json > depth.json
```

Then read, because the tool only sees shape. For each flagged module and its
immediate callers, note:

- Where understanding one concept means opening several small files in turn.
- Where the same preparation code appears before every call to a module.
- Where a pure function was extracted for testing, but the bugs live in how it is called.
- Where tests reach past an interface (patching internals, asserting private state).
- Where a rule (rounding, permissions, retry policy) is implemented in more than one place.

Apply the deletion test to each suspect: would deleting it concentrate
complexity in one place, or spread it across callers? Concentrate is the signal.

## Phase 3 — Rank

Combine the tool's opportunity score with judgement. Score each candidate 1–3 on:

| Factor | 3 | 1 |
|--------|---|---|
| Change frequency | Changed most months | Untouched for a year |
| Pain evidence | Recent bugs or slow changes traced here | Theoretical only |
| Locality gain | A rule now in N places would live in one | Mostly cosmetic |
| Test gain | Behaviour becomes testable through one interface | Already well tested |
| Migration risk (inverted) | Few callers, good test coverage | Many callers, no tests |

Total out of 15. Present the top 3–5; more than that is a backlog, not a review.
Label each **Strong** (12+), **Worth exploring** (9–11) or **Speculative** (under 9).

If a candidate contradicts a recorded decision, include it only when the pain is
strong enough to reopen that decision, and say so explicitly in the card.

## Phase 4 — Write the report

Use `assets/architecture-review-template.md`. Every candidate card has:

- **Modules involved** — paths, using the glossary's names for the concept
- **Friction** — what is hard today, with evidence (churn count, bug, duplicated rule)
- **Proposed deepening** — in plain language: what merges, what becomes hidden
- **Gains** — in leverage (what callers stop needing to know) and locality (what stops being spread)
- **Test impact** — which tests move to the new interface and which get deleted
- **Before / after sketch** — a small diagram or two lists of call sites
- **Strength** — Strong / Worth exploring / Speculative

End with one top recommendation and the reason. Do not propose interface
signatures yet — that comes after the requester picks a candidate.

## Phase 5 — Interrogate the chosen candidate

Walk the decision tree with the requester, one question at a time, recording
answers as they settle. Typical order:

1. What is the one domain concept this module will own? (If it needs "and", it is two modules.)
2. Who are the callers today and what does the most common one need?
3. Which dependencies does it have, and which category is each (see the depth-principles reference)?
4. Where does the seam go, and what are the two adapters that justify it?
5. Which error modes do callers genuinely need to distinguish?
6. What existing tests survive, move or get deleted?
7. What is the migration path for callers — all at once or behind a compatibility shim?

Side effects while interrogating: when a new or sharpened term appears, add it to
the project glossary; when the requester rejects a candidate for a lasting reason,
offer to record that as a decision so future reviews do not suggest it again.

## Phase 6 — Design the interface twice

Never ship the first interface. Produce at least two, ideally three, designed
under deliberately different constraints:

| Constraint | Aims for |
|------------|----------|
| Smallest surface | 1–3 entry points; everything else hidden |
| Common caller first | The dominant use is one call with defaults |
| Flexible | Supports rarer callers without new entry points later |
| Port-based | Remote or third-party dependencies behind ports with two adapters each |

For each design capture: entry points with parameters, error modes and ordering
rules; configuration knobs; what it hides; what it leaves to callers; the
common caller's code; seams with their adapters. Put them in a JSON file shaped
like `assets/sample_designs.json` and run:

```bash
python3 path/to/interface_compare.py --input designs.json
```

Read the scores as a prompt for discussion, then give your own recommendation.
If two designs are within a point, propose a hybrid: the winner's surface with
the runner-up's hidden behaviour.

## Phase 7 — Migrate

1. Write tests at the new interface first, using the most common caller's scenarios.
2. Build the deep module behind the new interface, reusing the old code internally.
3. Move callers over one at a time; keep the build green after each.
4. Delete the shallow modules and their now-redundant tests.
5. Re-run `module_depth.py` on the area; the candidate should drop out of the flagged list.

## Question bank

Use these to probe a candidate or a proposed design:

- If I delete this module, where does its code go, and how many copies appear?
- What does a caller have to remember that the code could remember for them?
- Which parameter is passed through here without being used?
- Which errors reach callers that only the storage layer understands?
- What changes when the business rule changes — one file or five?
- Which tests break if I rename a private function? (They are testing past the interface.)
- What is the second adapter for this seam? If there is none, why is there a seam?
- Could the common case be a single call?
- What does this module know that nothing else should?
