# Pattern Checklist

The 11 authoring patterns rendered as pass/fail criteria, with the failure mode each
one exists to prevent and the fix when it fires. Load this before submitting a skill
for review, or when a linter finding is unclear.

Column key: **Auto** means `skill_lint.py` proves it mechanically. **Human** means
only a reviewer can judge it.

---

## P1 — Context-First Design

**Rule:** The description tells an assistant when to activate the skill, in ≤ 240
characters, using the form `<what it does>. Use when <trigger a>, <trigger b>, <trigger c>.`

| Criterion | Auto | Fails when |
|-----------|------|-----------|
| ≤ 240 characters | Yes | Author padded with features or synonyms |
| Contains a `Use when` clause | Yes | Description describes capability, not moment |
| ≥ 6 distinctive trigger terms | Yes (audit) | Triggers are generic verbs like "help", "manage" |
| No name restatement | Yes | "The X skill is a skill that…" |
| No cross-skill routing prose | Yes | "Pairs with Y", "Distinct from Z" |
| No marketing adjectives | Yes | "comprehensive", "world-class", "robust" |
| Trigger overlap with neighbours < 0.5 | Yes (audit) | Two skills compete for the same phrasing |

**Failure mode prevented:** a well-built skill that never activates, which is
indistinguishable from a skill that does not exist.

**Fix when it fires:** rewrite from the three literal user sentences, not from the
existing description. Editing a bad description usually preserves its framing.

---

## P2 — YAML Frontmatter Schema

**Rule:** `name`, `description`, `license`, and `metadata.{version, author, category,
domain, updated, tags}` all present; `name` matches the folder exactly.

| Criterion | Auto | Notes |
|-----------|------|-------|
| All required fields present | Yes | Missing `domain` is the most common omission |
| `name` == folder name | Yes | Breaks catalog generation when they diverge |
| `category` matches a top-level directory | Human | Linter cannot see the repo layout |
| `updated` is ISO 8601 | Yes | `2026-07-21`, never `July 2026` |
| 3-8 tags, lowercase | Human | Tags carry the feature list the description must not |
| `version` is semver | Yes | New skills start at `1.0.0` |

**Failure mode prevented:** the skill is invisible to manifest generation and never
appears in the catalog, regardless of quality.

---

## P3 — Line Limits

**Rule:** SKILL.md ≤ 500 lines, `references/*.md` ≤ 800, `scripts/*.py` 150-300.

| File | Limit | What over-limit usually means |
|------|-------|-------------------------------|
| SKILL.md | 500 | One section should have been a reference |
| references/*.md | 800 | Two references split by read-moment |
| scripts/*.py | 300 | Two tools sharing a file |
| scripts/*.py | 150 min | The tool does not justify a file |
| assets/* | none | — |

**Failure mode prevented:** context exhaustion. A 900-line SKILL.md consumes budget
that the actual task needs, on every invocation, forever.

**Fix when it fires:** do not trim prose. Find the section that is only needed on
some invocations and move it wholesale to `references/`, leaving a one-line link.

---

## P4 — Opinionated Recommendations

**Rule:** every recommendation states a position, its reason, and its escape hatch.

| Criterion | Auto | Notes |
|-----------|------|-------|
| No "you could use X or Y" constructions | Human | Search the draft for "options", "depends", "consider" |
| Alternatives get one sentence maximum | Human | Longer means the author has not decided |
| Escape hatch is a named condition | Human | "unless traffic exceeds 100K rps", not "unless it doesn't fit" |

**Failure mode prevented:** the skill delivers what a thirty-second search delivers,
which is why the user did not search.

**Fix when it fires:** for each menu, pick the option you would actually choose on a
Monday, say so, and write the one condition under which you would choose differently.

---

## P5 — Anti-Patterns Section

**Rule:** minimum three entries, each with `**Mistake:**`, `**Why it happens:**`, and
`**Instead:**`.

| Criterion | Auto | Notes |
|-----------|------|-------|
| ≥ 3 entries | Yes | Counts `**Mistake:**` occurrences |
| All three fields per entry | Human | `Why it happens` is the one authors skip |
| Root cause sounds reasonable | Human | If it sounds stupid, it is not the real cause |
| Drawn from experience | Human | Theoretical anti-patterns read as filler |
| Memorable names | Human | Named patterns get quoted in review |

**Failure mode prevented:** users repeat the domain's known mistakes because the
skill only described the happy path.

---

## P6 — Confidence Tagging

**Rule:** key recommendations carry `[PROVEN]`, `[RECOMMENDED]`, or `[EXPERIMENTAL]`.

| Tag | Bar | Obligation |
|-----|-----|-----------|
| `[PROVEN]` | Author has seen it work in 3+ real projects | None |
| `[RECOMMENDED]` | Strong evidence, not universal | Default when unsure |
| `[EXPERIMENTAL]` | Promising, thinly validated | Must include a risk note naming what breaks |

Tag at section or recommendation level. Tagging every sentence is noise; tagging
nothing leaves the reader unable to calibrate how hard to push back.

**Failure mode prevented:** a reader treats a speculative suggestion with the same
weight as an industry-standard practice, and finds out in production.

---

## P7 — Tool Design Standards

**Rule:** stdlib only, argparse, `--format {text,json}`, 150-300 lines, type hints,
docstrings, caught exceptions, deterministic.

| Criterion | Auto | Notes |
|-----------|------|-------|
| Stdlib-only imports | Yes | Checked by AST against `sys.stdlib_module_names` |
| argparse present | Yes | `--help` must document every option |
| `--format` supported | Yes | Text default, JSON for pipelines |
| `__main__` guard | Yes | Required for importability |
| 150-300 lines | Yes | See P3 |
| Type hints on every signature | Human | Linter does not enforce completeness |
| Docstrings on public functions | Human | One line is enough if it says what, not how |
| Actionable error messages | Human | Must name the file and the fix |
| Deterministic | Human | No `random`, no network, no clock in output |
| Exit 1 on findings | Human | What makes the tool usable as a CI gate |

**Failure mode prevented:** the skill stops working the moment it leaves the author's
machine, because it needed a package nobody else installed.

---

## P8 — Reference Architecture

**Rule:** `SKILL.md` + flat `scripts/`, `references/`, `assets/`. Required body
sections in order.

Required section order:

1. Title + framing paragraph
2. `## When to use this skill`
3. `## Inputs the skill expects`
4. `## Clarify First` (generative only)
5. `## Workflows` — exactly three
6. `## Decision frameworks`
7. `## Anti-Patterns`
8. `## Files`

| Criterion | Auto | Notes |
|-----------|------|-------|
| Required sections present | Yes | Matched case-insensitively on heading text |
| No nested subdirectories | Yes | `scripts/utils/` is a violation |
| At least one `sample_*.json` in assets | Yes | Makes workflow blocks runnable |
| ≥ 1 runnable bash block | Yes | Workflows without commands are documentation |
| Exactly three workflows | Human | Count them |

**Failure mode prevented:** every skill reads differently, so users have to relearn
navigation per package and assistants cannot rely on structure.

---

## P9 — Self-Contained Packaging

**Rule:** the folder is deployable alone. No cross-skill imports, no cross-skill
prose dependencies. Duplicate rather than depend.

| Criterion | Auto | Notes |
|-----------|------|-------|
| No `../other-skill/` imports | Yes | AST import check plus path scan |
| No "see the X skill" prose | Yes | Regex over the body |
| All relative paths resolve | Human | Run the extraction test |
| `standards/` is the only outbound reference | Human | Permitted because standards are universal |

**The extraction test:** copy the folder to an empty directory. SKILL.md must read
coherently, every script must run, every relative path must resolve. If anything
breaks, the package is not self-contained regardless of what the linter said.

A "Related skills" list at the end of SKILL.md is acceptable — it is navigation, not
dependency — provided nothing in the skill's actual operation requires reading them.

---

## P10 — Quality Threshold

**Rule:** 40%+ time saving, 30%+ consistency improvement. Human judgement only.

Three rejection categories:

| Category | Symptom | Test |
|----------|---------|------|
| Information-only | Facts with no workflow or tool | Could this have been a wiki page? |
| Thin wrapper | Generic process plus bullet points | Remove the domain nouns — is anything left? |
| Copy-paste | Repackaged public documentation | Does it add structure, thresholds, or judgement? |

State the estimate explicitly in the PR: "manually, this is a 90-minute task; with
the skill it is 30." If you cannot write that sentence honestly, do not publish.

---

## P11 — Clarify-First Gate

**Rule:** generative skills carry a `## Clarify First` section with 2-4 checkboxes
and the verbatim stop rule. Advisory skills omit it.

| Criterion | Auto | Notes |
|-----------|------|-------|
| Section present for generative skills | Human | Linter cannot tell generative from advisory |
| Stop rule present when section is | Yes | Fires if the section exists without it |
| 2-4 checkboxes, not more | Human | Longer is an intake form, and users route around it |
| Each has a "why it changes the output" clause | Human | The clause is the payload |
| Gate lives in the body, not the description | Yes | It must not consume the P1 budget |

**Failure mode prevented:** a polished artifact built on misunderstood intent, which
costs more to discover late than the question would have cost early.

**Choosing gate inputs:** gate only on inputs where a wrong answer forces a rewrite,
not an edit. Audience and purpose usually qualify. Format preferences rarely do.

---

## Pre-submission run order

```bash
python3 engineering/write-a-skill/scripts/skill_lint.py --skill <path> --strict
python3 engineering/write-a-skill/scripts/description_audit.py --domain <domain>
# then every workflow bash block, verbatim, from the repository root
# then the extraction test into an empty directory
```

Fix findings in pattern order. P1 and P2 problems invalidate everything downstream —
there is no point polishing workflows in a skill that will never activate.
