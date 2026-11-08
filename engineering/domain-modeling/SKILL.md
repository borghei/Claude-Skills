---
name: domain-modeling
description: >
  Keep a project glossary of domain terms and lightweight decision records, and
  catch banned synonyms in docs and code. Use when terms are used inconsistently,
  writing a GLOSSARY.md, or recording a design decision.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: domain-design
  updated: 2026-11-08
  tags: [domain-modeling, glossary, ubiquitous-language, adr, decision-records, naming]
---

# Domain Modeling

Shared language is the cheapest defect prevention there is. This skill keeps two
small artefacts: a `GLOSSARY.md` where every domain term has one name, one
definition in business language, the synonyms to avoid and an owner who settles
disputes; and a folder of short decision records for choices that are costly to
reverse, surprising later and the result of a real trade-off. Its tools pull
candidate terms out of conversations and code, lint the glossary, find banned
synonyms in docs and identifiers, and keep decision records numbered and linked.

## When to use this skill

- **The same thing has three names** across code, docs, tickets and support macros
- **A design conversation keeps stalling** on what a word means ("account" — the payer or the login?)
- **Starting a GLOSSARY.md** for a project or a bounded part of a system
- **A decision was just made** that a newcomer would otherwise undo
- **Onboarding** — new people need the vocabulary before the code makes sense
- **Before naming a new module, table or API resource**, to use the agreed term

## Inputs the skill expects

- Material that carries the language: meeting transcripts, design notes, tickets, code paths
- The existing `GLOSSARY.md` and `docs/adr/` if present
- Who owns which terms (roles that can settle a meaning)
- Whether the system has one context or several where the same word means different things

## Clarify First

What most shapes the output is whether the language is being created, repaired or checked, and who has authority over it. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **One context or several:** if a word legitimately means two things in two parts of the system, forcing one definition causes the bugs this skill exists to prevent.
- **Term owners:** a proposed term without an owner stays proposed forever; the owner decides synonym fights.
- **Source material:** transcripts and support tickets surface customer language and aliases; code surfaces engineering names — the extraction differs.
- **Decision threshold:** which choices the team wants recorded; default is the three-part test (costly to reverse, surprising, real trade-off).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Lint the sample glossary and find banned aliases in a feature note
python3 engineering/domain-modeling/scripts/glossary_lint.py \
  --glossary engineering/domain-modeling/assets/sample_GLOSSARY.md \
  --scan engineering/domain-modeling/assets/sample_feature_notes.md

# Lint the sample decision records and get the next file name
python3 engineering/domain-modeling/scripts/adr_lint.py \
  --input engineering/domain-modeling/assets/sample_adr_set.json \
  --next-title "Publish events for billing"
```

## Workflows

### Workflow 1 — Extract terms from conversations and code [RECOMMENDED]

1. Gather material: a design-session transcript, recent tickets, and the code paths for the area.
2. Run the extractor against the current glossary (or none, for a first pass):

   ```bash
   python3 engineering/domain-modeling/scripts/term_extract.py \
     --paths engineering/domain-modeling/assets/sample_conversation.txt \
     --glossary engineering/domain-modeling/assets/sample_GLOSSARY.md --format text
   ```

3. Triage each new candidate: add as a term, add as an alias of an existing term, split (one word, two concepts), or ignore. In the sample, `pause` and `suspension` are two concepts that need two entries; `membership` is an alias of Subscription.
4. Read the "never used" list: those terms are stale or called something else in practice.
5. Draft new entries with status `proposed` and ask each owner to confirm.

Exit code 1 means new candidates exist and need a decision — useful as a periodic review prompt, not a merge gate.

### Workflow 2 — Write and lint the glossary [PROVEN]

1. Start from `assets/GLOSSARY-template.md`: one `### Term` block per concept with Definition, Avoid, Owner, Related, Status.
2. Definitions say what the thing is in at most two sentences. No tables, columns, classes or endpoints.
3. Each alias appears under exactly one term, and never matches another canonical term.
4. Lint it, then scan docs and code for the aliases you just banned:

   ```bash
   python3 engineering/domain-modeling/scripts/glossary_lint.py \
     --glossary engineering/domain-modeling/assets/sample_GLOSSARY.md \
     --scan engineering/domain-modeling/assets/sample_feature_notes.md --format json
   ```

5. The scan splits identifiers, so `clientId` and `memberships.renew` count as uses of "client" and "membership". Fix docs now; rename identifiers when the files are next touched.

Validation checkpoint: the lint reports no errors, every term has an owner, and the scan over changed docs is clean before the glossary change merges.

The sample glossary is deliberately flawed and exits 1: a duplicate `Plan`, the alias `Account` colliding with the canonical term `Account`, `Churn` mapped to two terms, an invalid status, and an implementation-heavy definition of `Charge`.

### Workflow 3 — Resolve a synonym conflict [PROVEN]

1. Write a one-sentence definition for each competing word.
2. Invent a scenario where one applies and the other does not. If one exists, they are two concepts: create two terms.
3. If it is one concept, pick the name by: external (customer, contract) usage first, least overloaded internally second, most present in code third.
4. Put the losing words under Avoid, run the `--scan`, and if the choice was contested, record it as a decision so it is not reopened.

### Workflow 4 — Record a decision [RECOMMENDED]

The agent offers a record only when a choice passes all three tests: costly to reverse, surprising without context, and a real trade-off.

1. Get the next file name: `adr_lint.py --dir docs/adr --next-title "<decision>"`.
2. Fill `assets/adr-template.md`: decisive title, Context with glossary terms, "We will…" Decision, alternatives with reasons, consequences.
3. Start as `proposed`; set `accepted` once deciders agree. Never edit an accepted record's decision — supersede it and add `**Supersedes:** NNNN` to the new one.
4. Validate the folder before merging:

   ```bash
   python3 engineering/domain-modeling/scripts/adr_lint.py \
     --input engineering/domain-modeling/assets/sample_adr_set.json --format text
   ```

The sample set exits 1: number 0004 is used twice, 0002 points at a missing replacement, 0005 claims to supersede 0002 while 0002 names another record, and one record has no Decision section.

### Workflow 5 — Keep the model honest during design work [RECOMMENDED]

1. When someone uses a term against its glossary meaning, the agent points it out at once and asks which meaning they intend.
2. When code contradicts a stated rule ("partial cancellation is possible" but the code cancels whole Subscriptions), the agent surfaces the contradiction instead of picking a side.
3. Update the glossary in the same change that introduces or renames a concept.
4. Validate that every new identifier in the change uses the canonical term (`--scan` on the changed paths).

## Decision frameworks

### Does this word belong in the glossary?

| Question | Yes → | No → |
|----------|-------|------|
| Would two people here plausibly mean different things by it? | Add it | Next question |
| Does a new hire need it explained to read tickets or code? | Add it | Next question |
| Is it generic engineering vocabulary (cache, retry, queue)? | Leave it out | — |

### One context or two? [RECOMMENDED]

Split into per-context glossaries when a term keeps two definitions that both survive the scenario test, or when two teams keep correcting each other's usage. Keep a root `GLOSSARY.md` that lists contexts and translations, and translate explicitly at the code seam between them.

### Record it or not? [PROVEN]

| Costly to reverse | Surprising later | Real alternative | Record? |
|-------------------|------------------|------------------|---------|
| Yes | Yes | Yes | Yes |
| Yes | No | Yes | No — the code explains it |
| No | Any | Any | No — just change it later |
| Yes | Yes | No | Usually no; a code comment suffices |

## Anti-Patterns

### The Glossary as a Spec
**Mistake:** Definitions that describe tables, flags, endpoints and retry counts ("a row in the charges table with a captured boolean").
**Why it happens:** Engineers write the glossary and describe what they know best — storage.
**Instead:** Define what the thing is in business language. Storage changes every quarter; the concept does not. `glossary_lint.py` warns on implementation words.

### Every Synonym Is Fine
**Mistake:** Listing synonyms as "also known as" and accepting all of them.
**Why it happens:** Picking one word feels like overruling colleagues.
**Instead:** Choose one canonical term and list the rest under Avoid. A glossary that blesses three names has not removed any ambiguity. Let the term's owner make the call.

### The One Alias, Two Meanings
**Mistake:** Banning "churn" under both Cancellation and Downgrade, or banning a word that is itself a canonical term elsewhere.
**Why it happens:** Terms are added one at a time without checking the rest of the file.
**Instead:** Each alias maps to exactly one term. If a word genuinely covers two concepts, it is a split, not an alias — say so in both definitions. The linter rejects both collisions.

### Recording Everything
**Mistake:** A decision record for every library choice and folder rename, until nobody reads the folder.
**Why it happens:** Records feel like diligence, and writing one is easy.
**Instead:** Apply the three-part test. A record that fails it is noise that hides the records that matter.

### Editing History
**Mistake:** Rewriting an accepted record when the decision changes, or deleting a record that turned out wrong.
**Why it happens:** It keeps the folder tidy.
**Instead:** Supersede: write a new record, mark the old one `superseded by NNNN`, and add `**Supersedes:**` to the new one. The reasoning that was overturned is exactly what the next person needs to see.

## Files

### Tools Overview

| Script | Purpose | Exit codes |
|--------|---------|------------|
| `scripts/glossary_lint.py` | Lint `### Term` entries (missing definition/owner, duplicates, alias collisions, circular, overlong or implementation-heavy definitions, invalid status, dangling Related); `--scan` finds avoided aliases in docs and code with identifier splitting | 0 clean, 1 errors or alias usages, 2 input error |
| `scripts/term_extract.py` | Count content words and two-word phrases in transcripts, docs and code; classify as defined, avoided alias or new; list glossary terms never used | 0 no new candidates, 1 candidates need a decision, 2 input error |
| `scripts/adr_lint.py` | Check numbering, title/file match, status values, two-way supersession links, required sections, decisive wording, recorded alternatives; `--next-title` prints the next file name | 0 clean, 1 errors, 2 input error |

All take `--format text|json`. `adr_lint.py` reads `--dir docs/adr` or a JSON bundle via `--input`.

### Reference Documentation

| File | Purpose |
|------|---------|
| `references/glossary-practice.md` | What belongs, entry rules, extraction triage, synonym resolution order, scenario probing, multi-context glossaries, upkeep |
| `references/decision-records.md` | Three-part test, what qualifies, layout and numbering, writing rules, lifecycle and supersession, worked examples |
| `assets/GLOSSARY-template.md` | Starting glossary with editing rules and a worked entry |
| `assets/adr-template.md` | Decision record template with the qualification test inline |
| `assets/sample_GLOSSARY.md` | Billing glossary with deliberate defects — linter exits 1 |
| `assets/sample_feature_notes.md` | Feature note and code using banned aliases — `--scan` reports 14 uses |
| `assets/sample_conversation.txt` | Design-session transcript for term extraction |
| `assets/sample_adr_set.json` | Five decision records with numbering and supersession defects — linter exits 1 |

## Scope & Limitations

**In Scope:**
- Building, linting and enforcing a project glossary, including per-context glossaries and translations.
- Extracting candidate terms from transcripts, docs and code, and resolving synonym conflicts.
- Lightweight decision records for domain and design decisions: when to write them, format, numbering and supersession.

**Out of Scope:**
- System-level architecture decisions and their evaluation — the senior-architect skill owns those; this skill supplies the record format and the language.
- Module interface design and refactoring (this skill names the concepts; it does not reshape the code).
- Automated renaming of identifiers across a codebase.
- Full domain-driven design facilitation such as event-storming workshops.

**Important Caveats:**
- Extraction is frequency-based with stop-word lists; it surfaces candidates, it does not understand meaning. Person names and everyday verbs can slip through — triage is a human decision.
- The alias scan matches whole words after splitting identifiers; a banned word inside an unrelated compound (e.g. "billboard" is safe, "billFor" is not) is handled, but quoted text that mentions a banned word on purpose will still be reported.
- The linters check structure and consistency, not whether a definition is correct.
