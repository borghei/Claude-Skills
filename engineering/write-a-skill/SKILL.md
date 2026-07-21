---
name: write-a-skill
description: >
  Author, lint, and publish skill packages that satisfy the library authoring
  standard. Use when creating a new skill, reviewing a skill PR, or fixing one
  that never activates.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: meta-skills
  updated: 2026-07-21
  tags: [authoring, meta-skill, linting, standards, packaging]
---

# Write A Skill

The meta-skill for building skill packages. It turns `standards/skill-authoring-standard.md`
from a document you agree with into a gate you can run: scaffold the package, write a
description that actually activates, place content in the right file, and lint against all
11 patterns before anyone reviews it. Most rejected skills fail on two things — a
description nothing matches, and a SKILL.md carrying content that belonged in `references/`.

## When to use this skill

- **Creating a new skill** from a one-line idea and needing the package structure right the first time
- **Reviewing a skill PR** and wanting a mechanical pass before spending attention on judgement
- **Fixing a skill that never activates** despite being well written — almost always a description problem
- **Splitting an oversized SKILL.md** that has crept past 500 lines
- **Auditing a whole domain** for description collisions after adding several neighbouring skills
- **Onboarding a new author** who needs the standard operationalised rather than explained

## Inputs the skill expects

- The skill's one-sentence purpose and the domain directory it belongs in
- The three to five user sentences that should activate it (these become the description)
- Which existing skills sit closest to it in trigger space
- Whether it emits a deliverable (drives the Pattern 11 Clarify First gate) or only advises
- The analysis each script will perform, and the sample input each will run against
- Any deep knowledge that will exceed the SKILL.md budget and belongs in `references/`

Under Pattern 9 this skill is self-contained except for one permitted outbound
reference: `standards/skill-authoring-standard.md`. Standards apply library-wide, so
citing them does not create a cross-skill dependency. Nothing here may point at
another skill's files.

## Clarify First

Before scaffolding, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Trigger sentences** — the literal phrases a user would type; they set the description, which decides whether the skill ever activates
- [ ] **Nearest existing skills** — determines whether this should be a new package or an extension of one that already owns the trigger space
- [ ] **Generative or advisory** — generative skills require the Clarify First gate; advisory ones must omit it
- [ ] **What the scripts compute** — a skill whose scripts only reformat user input will not clear the 40% time-saving bar

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Scaffold a new package

1. Write the description first, before any other content. If you cannot express the
   trigger set in 240 characters, the skill's scope is still too broad — narrow it.
2. Fill in a spec JSON: name, title, description, category, domain, script names,
   and whether the skill is generative.
3. Run the scaffolder with `--dry-run` to inspect the file plan, then again to write it.
4. Fill every `TODO` marker. The scaffold is deliberately unshippable until you do.

```bash
python3 engineering/write-a-skill/scripts/skill_scaffold.py \
  --input engineering/write-a-skill/assets/sample_skill_spec.json \
  --out engineering --dry-run --format text
```

The scaffolder refuses specs whose description exceeds 240 characters or lacks a
`Use when` clause. That refusal is the point — it stops you building 4,000 lines of
package around a skill that will never activate.

### Workflow 2 — Audit descriptions for activation and collision

1. Run the auditor across the target domain, or against a JSON list while drafting.
2. Fix anything scoring under 70: budget overruns, missing `Use when`, filler adjectives.
3. Read the collision report. Any pair above 0.50 overlap means an assistant is
   guessing between them — either merge the skills or re-cut their triggers so each
   owns distinct vocabulary.

```bash
python3 engineering/write-a-skill/scripts/description_audit.py \
  --input engineering/write-a-skill/assets/sample_descriptions.json \
  --min-score 70 --collision-threshold 0.5 --format text
```

Exit code is 1 when any description scores below `--min-score`, which makes this
usable as a CI gate. Point `--domain engineering` at a whole directory to audit
every shipped description at once.

### Workflow 3 — Lint before review

1. Run the linter in `--strict` mode so warnings fail too.
2. Fix errors in pattern order — P2 and P1 findings first, since frontmatter and
   description problems invalidate everything downstream.
3. Re-run until clean, then run each workflow's bash block verbatim and paste the
   output into the PR. A skill whose own examples were never executed is not done.
4. Hand the reviewer `assets/skill-review-checklist.md` for the judgement half.

```bash
python3 engineering/write-a-skill/scripts/skill_lint.py \
  --skill engineering/write-a-skill \
  --rules engineering/write-a-skill/assets/sample_lint_rules.json \
  --strict --format json
```

The linter distinguishes **tools** from **helper modules**. A `scripts/*.py` file that
a sibling script imports and that has no `__main__` guard is a library, so the argparse
/ `--format` / guard requirements are not applied to it; it is still checked for
stdlib-only imports and the line-count budget. Imports that resolve to a
`.py` file in the same `scripts/` directory are permitted under Pattern 9 — reaching
into a *different* skill's directory stays an error. Verify both behaviours with the
built-in fixtures before shipping a linter change:

```bash
python3 engineering/write-a-skill/scripts/skill_lint.py --selftest
```

## Decision frameworks

### Where does this content go?

The single most common authoring mistake is putting everything in SKILL.md. Route
content by asking what reads it and when.

| Content | Destination | Test |
|---------|-------------|------|
| Workflows, decision tables, activation context | `SKILL.md` | An assistant needs it on *every* invocation |
| Frameworks, benchmark tables, maturity models, regulatory detail | `references/*.md` | Needed on *some* invocations; would blow the 500-line budget |
| Deterministic analysis over user data | `scripts/*.py` | A human would otherwise do it by hand for 15+ minutes |
| Anything the user fills in and keeps | `assets/*` | The output belongs to the user, not the skill |

If SKILL.md exceeds 500 lines, the split is almost never "trim prose." It is one
whole section that should have been a reference from the start.

### Description budget allocation [PROVEN]

240 characters, spent in this order:

| Segment | Budget | Contains |
|---------|--------|----------|
| What it does | ~80 chars | One clause, concrete verb, the artifact produced |
| `Use when` triggers | ~140 chars | 3 trigger phrases in the user's own words |
| Slack | ~20 chars | Leave it — descriptions grow at every revision |

Never spend budget on: the skill's own name, feature enumerations (those are `tags`),
"pairs with X" routing prose (that goes in the body), or adjectives. The description
is resident in context for every session in which the skill is installed — it is the
most expensive text in the package per byte.

### Does this deserve to be a skill? [RECOMMENDED]

| Signal | Build it | Do not build it |
|--------|----------|-----------------|
| Time saved per use | 15+ minutes | Under 5 minutes |
| Repeat frequency | Monthly or more | Once ever |
| Judgement encoded | Real thresholds, named methods | Generic process everyone knows |
| Nearest skill's trigger overlap | Under 0.4 | Over 0.6 — extend that skill instead |
| Scripts | Compute something non-obvious | Reformat what the user typed |

Two "do not build it" columns is a rejection. One is a warning worth arguing about.

### Script count and shape [PROVEN]

Two to three scripts, 150-300 lines each. Under 150 lines means the tool does not
justify a file; over 300 means it is two tools. Every script takes `--format
{text,json}` with text as the default, exits 1 on findings so CI can gate on it, and
ships a `sample_*.json` in `assets/` so the workflow block in SKILL.md is runnable by
someone who just cloned the repo.

## Anti-Patterns

### The Keyword-Stuffed Description
**Mistake:** Padding the description with every synonym the author can think of, on the theory that more words means more matches.
**Why it happens:** Discovery feels like search, and search rewards keywords. It also feels free, because the cost is paid in someone else's context window.
**Instead:** Write the three sentences a user would actually type, and lift the distinctive nouns and verbs from those. Then run `description_audit.py` — if it reports a collision above 0.5 with a neighbouring skill, the fix is sharper scope, not more words.

### The Encyclopedia SKILL.md
**Mistake:** Writing an 900-line SKILL.md that covers the domain exhaustively, with `references/` left empty.
**Why it happens:** The author knows the domain deeply and everything genuinely feels important. Splitting also feels like admitting the content is second-tier.
**Instead:** Keep in SKILL.md only what an assistant needs on every single invocation — workflows, decision tables, activation context. Move frameworks and exhaustive detail to `references/` and link them by relative path. `references/` is not the demotion bin; it is where deep content is actually usable, because it gets loaded on demand instead of never.

### The Untested Workflow
**Mistake:** Shipping bash blocks in Workflows that were written by hand and never executed, often with flags the script does not implement.
**Why it happens:** The workflow is written before the script is finished, and nobody goes back once the flags settle.
**Instead:** Run every bash block verbatim against the shipped sample data as the last step before opening the PR, and paste the real output into the PR description. A script that crashes on its own sample input is the single loudest quality signal a reviewer can get.

### The Menu Skill
**Mistake:** Presenting five approaches with balanced pros and cons and letting the reader choose.
**Why it happens:** It feels more honest and less presumptuous than picking one, especially when the author has seen all five work.
**Instead:** State the recommendation, give the reason, then give the escape hatch — the specific condition under which the recommendation stops applying. Users invoke a skill for a position, not a survey; anything less than a recommendation they could have found themselves in thirty seconds.

### The Cross-Skill Dependency
**Mistake:** Writing "see the X skill for the scoring model" or importing a helper from `../other-skill/scripts/`.
**Why it happens:** Duplication feels wrong to engineers, and DRY is a deeply trained instinct.
**Instead:** Copy the helper. Skills are distributed as individual folders, so a cross-skill import is a broken package the moment someone extracts one directory. A helper module inside the skill's *own* `scripts/` directory is fine — that ships with the folder. `standards/` is the only permitted outbound reference, because it applies to every skill everywhere.

## Files

| File | Purpose |
|------|---------|
| `scripts/skill_lint.py` | Lint a skill folder against all 11 patterns; per-pattern findings, exit 1 on error. `--selftest` runs the built-in helper/dependency fixtures |
| `scripts/lint_checks.py` | Helper library for `skill_lint.py` — rule set, frontmatter parser, SKILL.md and structure checks. No CLI by design |
| `scripts/skill_scaffold.py` | Generate a compliant package skeleton from a JSON spec, with every required section stubbed |
| `scripts/description_audit.py` | Score descriptions on budget and trigger quality; flag colliding skill pairs |
| `references/authoring-playbook.md` | Section-by-section guidance, worked description rewrites, and the content-routing rules |
| `references/pattern-checklist.md` | The 11 patterns as concrete pass/fail criteria with common failure modes and fixes |
| `assets/sample_skill_spec.json` | Runnable scaffold input for Workflow 1 |
| `assets/sample_descriptions.json` | Runnable audit input for Workflow 2, including deliberately failing examples |
| `assets/sample_lint_rules.json` | Threshold overrides for Workflow 3 |
| `assets/skill-review-checklist.md` | Reviewer checklist covering the judgement half the linter cannot check |
