# Authoring Playbook

Section-by-section guidance for writing a skill package that clears review on the
first pass. Read this while drafting; read `pattern-checklist.md` before submitting.

---

## 1. Start with the description, not the content

The description is the only part of a skill that is always resident in an
assistant's context. Everything else loads on demand. This inverts the natural
writing order: you write the smallest, cheapest artifact first, because it decides
whether the expensive artifacts are ever read.

### The drafting procedure

1. Write down, verbatim, three sentences a real user would type when they need this
   skill. Not paraphrases — the actual words, including the imprecise ones.
2. Underline every noun and verb that appears in at least two of the three.
3. Compose: `<what it does — one clause>. Use when <trigger a>, <trigger b>, <trigger c>.`
4. Count characters. Over 240 means the scope is too broad, not that the prose is
   too long. Cut a trigger and consider whether the cut trigger is a second skill.

### Worked rewrites

**Before (312 chars, score 30):**

> The comprehensive API design review skill provides world-class analysis of your
> REST and GraphQL APIs, covering naming conventions, versioning strategy, pagination,
> error formats, authentication patterns, rate limiting, documentation quality, and
> backwards compatibility. Pairs with the api-test-suite-builder skill.

Failures: filler adjectives, an exhaustive feature list that belongs in `tags`,
cross-skill routing prose, and no `Use when` clause at all. Nothing in it describes
a moment in a user's day.

**After (198 chars, score 100):**

> Review REST and GraphQL API designs for versioning, pagination, and error-contract
> problems before they ship. Use when designing a new endpoint, reviewing an API PR,
> or planning a breaking change.

The feature list moved to `tags`. The routing prose moved to a Scope section in the
body. The three triggers are now moments — "designing a new endpoint," "reviewing an
API PR," "planning a breaking change" — which is what users actually say.

**Before (89 chars, score 45):**

> Helps with database work. Use when working with databases.

Failure: no discrimination. It matches every database question in existence, so an
assistant either activates it constantly or learns to ignore it.

**After (211 chars):**

> Design relational schemas and review migrations for normalization, index coverage,
> and lock risk. Use when modelling a new table, reviewing a migration PR, or
> diagnosing a slow query's schema cause.

### Collision resolution

`description_audit.py` reports Jaccard overlap between trigger vocabularies. Read the
result this way:

| Overlap | Meaning | Action |
|---------|---------|--------|
| Under 0.30 | Cleanly separated | Ship |
| 0.30 - 0.50 | Adjacent, distinguishable | Add one discriminating trigger to each |
| 0.50 - 0.70 | An assistant is guessing | Re-cut the scope boundary between them |
| Over 0.70 | Effectively the same skill | Merge, or delete the weaker one |

Re-cutting means finding the axis that genuinely separates them — audience, artifact,
lifecycle stage — and putting that axis into both descriptions. "Spec authoring" vs
"spec coverage tracking" are the same nouns at different lifecycle stages; say so.

---

## 2. Framing paragraph

Two to three sentences immediately under the `#` title. Its job is to tell a reader
who has already activated the skill what the skill believes, not what it contains.

A good framing paragraph states the problem the skill exists to solve and names the
failure mode it prevents. A bad one restates the description in longer words.

**Weak:** "This skill helps you write specifications. It provides workflows, tools,
and templates for specification-driven development."

**Strong:** "Development from an executable specification, where the spec is precise
enough to generate from and every requirement carries an ID that survives to the test
suite. The failure this prevents is the spec that was true at kickoff and fiction by
week three, with nobody able to name which requirements shipped."

---

## 3. When to use this skill

Five to six bullets, each a **concrete situation**, not a capability. The test: can
you imagine the specific afternoon on which someone is in that situation?

- Capability (weak): "Requirement traceability analysis"
- Situation (strong): "Auditing which of last quarter's committed requirements
  actually shipped, ahead of a stakeholder review"

Bold the leading phrase so the list is scannable. Order by frequency — the most
common situation first, because readers stop after three bullets.

---

## 4. Inputs the skill expects

Four to six bullets naming what the user must supply. This section does double duty:
it tells the user what to gather, and it tells the assistant what to ask for when the
user has not supplied it.

Name the input, then parenthesise why it matters when the reason is not obvious.
"Audience (drives altitude and length of the summary)" is worth the extra six words;
"Project name" is not.

---

## 5. Clarify First (generative skills only)

Include this section if and only if the skill emits an artifact. Advisory and
reference skills must omit it — a gate before answering a question is friction with
no payoff.

Three to four checkboxes, each with an em-dash clause explaining **why it changes the
output**. That clause is the whole point: it tells the assistant which inputs are
load-bearing, so it knows what is worth interrupting the user for.

The stop rule is verbatim and non-negotiable:

> Stop rule: ask only the 2-3 that most change the output. If the user says "just
> draft it," proceed and list your assumptions at the top of the artifact.

Without the stop rule the gate degrades into an intake interview, and users learn to
route around the skill entirely.

### Choosing the right inputs to gate on

Ask: if I got this input wrong, would the artifact need rewriting or just editing?
Gate only on rewrite-level inputs. Audience is usually rewrite-level. Formatting
preference almost never is.

---

## 6. Workflows

Exactly three. Fewer suggests the skill is a single script with documentation; more
suggests two skills wearing one coat.

Each workflow gets:

1. A named heading describing the outcome, not the tool (`Audit descriptions for
   activation`, not `Run description_audit.py`).
2. Three to four numbered steps in imperative mood.
3. One runnable ```bash block invoking a real script with real flags and a path that
   resolves from the repository root.
4. Optionally, one paragraph after the block explaining how to read the output or
   what the exit code means. This is where most of the skill's judgement lives — use it.

### Ordering

Order workflows by the sequence a new user follows: create, then inspect, then gate.
A user reading top to bottom should be walking the happy path.

### The runnable rule

Every bash block is executed verbatim before the PR opens. Path from repository root,
sample data shipped in `assets/`, flags that exist. The most common reviewer-visible
defect in this library is a workflow whose `--flag` was renamed during script
development and never updated in SKILL.md.

---

## 7. Decision frameworks

One to three tables or decision trees carrying **real thresholds**. This is the
section that separates a skill from a blog post.

A threshold is a number with a unit and a consequence: "over 0.6 trigger overlap →
extend the existing skill instead of building a new one." Not "consider whether the
skills are too similar."

If you cannot produce a number, produce a discriminating question with two named
branches and what each implies. What you may not do is write "it depends on your
context" — that sentence is the absence of a framework.

### Where thresholds come from

- Standards documents (line limits, budgets) — cite them
- Measured practice ("three or more independent sources before asserting a claim")
- Cost inflection points (the point where doing it by hand becomes cheaper)

State the source when it is not obvious. A threshold a reader cannot trace is a
threshold they will ignore the first time it is inconvenient.

---

## 8. Anti-Patterns

Minimum three, in the exact format, with a real mistake behind each one.

```markdown
### Name Of The Anti-Pattern
**Mistake:** what people actually do
**Why it happens:** the reasonable-sounding root cause
**Instead:** the specific corrective action
```

The **Why it happens** line is what makes the section useful and is the one authors
skip. An anti-pattern without a root cause reads as scolding; with one, it reads as
recognition, and readers who recognise themselves change behaviour.

Root causes worth reaching for, because they are usually true:
- The wrong behaviour is locally cheaper and the cost lands on someone else
- A generally good instinct (DRY, thoroughness, humility) applied in the wrong place
- The artifact was correct when written and nothing forced an update

Name anti-patterns memorably. "The Encyclopedia SKILL.md" gets quoted in review;
"Excessive documentation length" does not.

---

## 9. Files

A table of every shipped file with a one-line purpose. Reviewers use it to check that
nothing undocumented crept in, and users use it to decide what to read next.

Order: scripts, references, assets. One line each, no wrapping.

---

## 10. Writing the scripts

### What earns a script

A script earns its place when it performs deterministic analysis a human would
otherwise do by hand for fifteen minutes or more: parsing, cross-referencing,
counting, scoring against thresholds, diffing two representations of the same thing.

A script does not earn its place when it reformats what the user typed, wraps a
single shell command, or asks questions and echoes the answers into a template. The
assistant can already do all three, better, without a file.

### Shape

```
shebang + module docstring with usage examples
stdlib imports only
module-level constants (thresholds, vocabularies)
analysis functions — typed, docstringed, pure where possible
output(report, fmt) — text and json
main() — argparse, try/except, sys.exit
if __name__ == "__main__": main()
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Analysis ran; nothing above the failure threshold |
| 1 | Analysis ran and found failures, or the input was unusable |

Consistent exit codes are what make a skill usable in CI. Document them in the
workflow prose so readers know a non-zero exit is a finding, not a crash.

### Error messages

Every caught exception produces a message naming the file and the fix:

- Bad: `error: invalid input`
- Good: `error: spec is not valid JSON (assets/sample.json): Expecting ',' delimiter: line 8 column 3`

### Determinism

No `random`, no network, no wall-clock reads that reach the output. A script that
returns different results on two runs over the same input cannot be used as a gate,
and gating is most of the value.

---

## 11. Writing the references

References carry what would blow the SKILL.md budget: frameworks, benchmark tables,
maturity models, exhaustive checklists, methodological detail. 300-800 lines each,
one to three files.

Split by **when it is read**, not by topic size. A reference the assistant loads
during drafting and a reference it loads during review are two files even if both are
short, because they are needed at different moments.

Each reference opens with one sentence stating when to load it. SKILL.md links to it
by relative path with the same sentence. Never duplicate content between the two —
if a table appears in both, delete it from SKILL.md.

---

## 12. Writing the assets

Two kinds of file live here.

**Sample inputs** (`sample_*.json`) exist so every workflow block runs for someone
who just cloned the repository. Include realistic data, and include at least one
deliberately failing record so the tool's findings output is exercised rather than
just its happy path.

**Templates** are documents the user fills in and keeps — checklists, report
skeletons, review forms. They are written for the user, not the assistant, so they
carry no frontmatter and no skill jargon.

---

## 13. Self-review before submitting

Run in this order:

1. `skill_lint.py --skill <path> --strict` — until clean
2. Every workflow bash block, verbatim, from the repository root
3. `description_audit.py --domain <domain>` — check for new collisions
4. Copy the folder to an empty directory; confirm SKILL.md still reads and scripts
   still run (the Pattern 9 extraction test)
5. Read `assets/skill-review-checklist.md` as if you were the reviewer

Then estimate, in one sentence, how long the task takes without the skill and with
it. If the gap is under 40%, the honest move is not to publish.
