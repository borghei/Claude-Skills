# Tour Maintenance

Anchoring strategies, rot mechanics, CI wiring, and the decision rules for updating a
drifted tour. Load this when a tour has broken, or when setting one up to survive.

---

## 1. Why tours rot faster than other documentation

Most documentation degrades gradually: a README describing a system at the wrong level
of detail is still 70% useful a year later. A tour degrades discontinuously. One
rename breaks one stop completely, and a reader who hits a broken stop stops trusting
the remaining ones — including the correct ones.

Three properties cause this:

1. **Tours point at specific code.** Precision is the value and the fragility.
2. **Nothing breaks when a tour goes stale.** No test fails, no build turns red.
3. **The author has already left the context.** Tours are written at handoff, and the
   person best placed to update them is the one who moved on.

The fix is not discipline. It is making the tour breakable by a code change and
validated by the same CI that runs the tests.

---

## 2. Anchoring strategies

| Anchor | Survives | Breaks on | Verdict |
|--------|----------|-----------|---------|
| Symbol name | Edits above, reformatting, file growth, moves within file | Rename, extraction to another file | **Default** |
| File path | Everything inside the file | File move, rename | Good for shape-of-file stops |
| Distinctive comment string | Most edits | Comment rewrite | Fallback for non-Python |
| Line number | Nothing meaningful | Any edit above it | Never |
| Line range | Nothing | Any edit | Never |

### How resolution works

The tour records `path`, `anchor`, `line`, and `fingerprint`. Only `path` and `anchor`
are identity; `line` and `fingerprint` are derived and refreshed by `--update`.

For Python, the anchor resolves through the AST — a function, async function, or class
whose name matches. This means the anchor survives the whole file being reformatted or
doubling in length. For other languages, resolution falls back to the first line
containing the anchor string, which is weaker but still survives edits above it.

### Choosing anchors that last

- Anchor on the **public** symbol, not a private helper. Helpers get inlined and renamed
  far more often.
- Prefer the class over the method when the method is likely to be split.
- Avoid anchoring on names that appear in many files (`handler`, `run`, `main`) if the
  tour will ever need relocation suggestions — the search will return noise.
- If a stop is about a whole file's shape rather than a specific construct, omit the
  anchor. The validator will report that drift cannot be detected, which is honest.

---

## 3. Reading the validation report

| Status | Meaning | Urgency |
|--------|---------|---------|
| `ok` | Path, anchor, and fingerprint all match | None |
| `shifted` | Anchor moved to a different line, content unchanged | Cosmetic — refresh with `--update` |
| `drifted` | Anchor body changed since the tour was written | Re-read the note; it may now be wrong |
| `moved` | Anchor is gone from this file but exists elsewhere | Re-point the stop |
| `missing-anchor` | Anchor not found anywhere in the tree | Decide whether the concept still exists |
| `deleted` | File does not exist at the recorded path | Re-point or delete the stop |

`shifted` is deliberately not counted as broken. Treating line movement as a failure
trains people to ignore the report, which is worse than the noise it prevents.

### The drift decision

A `drifted` stop means the code under a note changed. Three outcomes, and the choice
cannot be automated:

1. **The note is still true.** Refactoring inside the body, same decision, same
   rationale. Refresh the fingerprint with `--update` and move on.
2. **The note is now incomplete.** The function grew a new responsibility. Extend the
   note, or split the stop in two if the new responsibility deserves its own why.
3. **The note is now wrong.** The decision the note explains was reversed. Rewrite it,
   and consider whether the reversal itself is the more interesting stop.

Case 3 is rare and expensive to miss, which is why `--update` refreshes fingerprints
only when you run it explicitly, rather than the validator silently rebaselining. A
tool that auto-heals drift provides no more value than having no fingerprints at all.

### Relocation suggestions

For `moved` and `deleted` stops, the validator searches the tree for files containing
the anchor name and for files sharing the original basename, returning up to five
candidates. Read them with judgement: a common anchor name will return unrelated hits.
A cluster of stops all relocating to the same new directory means a module was moved
wholesale, and the fix is a bulk path edit rather than five investigations.

---

## 4. CI wiring

Put the tour in the repository it describes and validate it on every change to that
repository.

```bash
python3 scripts/tour_validate.py --tour docs/tours/request-lifecycle.json --repo .
```

Exit code 1 on any broken stop. Wire it as a non-blocking check first, then promote it
once the tour is clean.

### What to gate and what to report

| Check | Gate or report | Why |
|-------|---------------|-----|
| `deleted`, `moved`, `missing-anchor` | Gate | The tour is actively wrong; fixing is a two-minute edit |
| `drifted` | Report on the PR | Needs a human decision, and blocking on it teaches people to skip tours |
| `shifted` | Silent | Cosmetic |
| Why-ratio below 0.8 | Gate on new tours only | Retrofitting existing tours all at once never happens |

### Reviewer prompt

The highest-leverage practice is not automation. It is one line in the PR template:

> Does this change touch a file named in a tour? If so, does the tour's note still
> hold?

The validator catches structural breakage. Only a human catches a note that is
structurally fine and semantically obsolete.

---

## 5. Ownership

A tour without an owner is a tour that will be deleted in a year, after everyone agrees
it is out of date and nobody wants to be the one to fix it.

| Model | How it works | Holds up |
|-------|-------------|----------|
| Author owns forever | The person who wrote it maintains it | No — they change teams |
| Service team owns | The team owning the code owns its tours | Yes — the best default |
| Onboarding buddy updates | Each new hire fixes what they find broken | Yes, and it doubles as a first contribution |
| Nobody | Validation in CI catches breakage; whoever broke it fixes it | Partially — catches structure, not semantics |

The onboarding-buddy model is worth adopting deliberately. A new engineer walking a
tour is the only person who reliably notices its gaps, and a tour fix is a genuinely
useful first PR: small, reviewable, and it forces them to read the code twice.

---

## 6. Lifecycle

Tours have a lifespan, and pretending otherwise produces a directory of documents
nobody trusts.

| Age | Expected state | Action |
|-----|---------------|--------|
| 0-3 months | Accurate | Use it |
| 3-12 months | 1-2 drifted stops per quarter | Refresh during validation runs |
| 12-24 months | Ordering may no longer match the system | Re-walk it cold; re-order if needed |
| Over 24 months | Usually describes a system that no longer exists | Rewrite from scratch or delete |

### When to delete rather than fix

Delete when:

- More than half the stops are broken — the system was restructured, and patching
  produces a tour that reflects neither the old design nor the new one
- The tour's question is no longer one anyone asks
- The subsystem it covers is deprecated
- Nobody has walked it in a year and nobody can name who it was for

A deleted tour is honest. A tour with six broken stops is worse than nothing, because
it costs a new engineer an hour before they conclude it cannot be trusted — and by
then they have also stopped trusting the tours that were fine.

---

## 7. Scaling to many tours

| Tours per repo | Structure |
|----------------|-----------|
| 1-3 | `docs/tours/*.json`, validated together |
| 4-8 | Group by audience or subsystem; one index document listing question and audience |
| Over 8 | Usually a sign of over-documentation; check which have been walked in the last six months and delete the rest |

Each tour must state its question and audience in its title and metadata. Two tours
whose questions overlap will both go stale, because neither is clearly the one to
update when the code changes.

Validation cost is negligible — a tour of ten stops validates in well under a second,
and the relocation search only runs for stops that are already broken. There is no
performance reason to validate tours less often than tests.
