---
name: spec-driven-workflow
description: >
  Run development from an executable specification with traceable requirement IDs
  and merge-time coverage gates. Use when starting a greenfield feature, reviving a
  stale spec, or gating merges on requirement coverage.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: software-process
  updated: 2026-07-21
  tags: [specification, requirements, traceability, acceptance-criteria, process]
---

# Spec-Driven Workflow

Development where the specification is the source of truth and the code is its
implementation, rather than a document that was true at kickoff and fiction by week
three. The mechanism is unglamorous: every normative statement gets a stable ID, every
ID appears in a test, and the merge gate fails when the two drift apart. Without that
mechanical link a spec is a memo, and memos do not survive contact with a sprint.

## When to use this skill

- **Starting a greenfield feature** where the interface is contested and the cost of building the wrong thing is high
- **Reviving a stale spec** that no longer matches shipped behaviour and needs reconciling before the next change
- **Gating merges on coverage** so a PR that implements two of five committed requirements cannot silently land
- **Auditing what actually shipped** ahead of a stakeholder review or a compliance obligation
- **Handing a feature to another team** who need the intent, not just the code
- **Generating an implementation** from a spec — which only works if the spec is precise enough that two engineers would build the same thing

## Inputs the skill expects

- A specification document in markdown, with normative statements using must/shall/should/may
- Acceptance criteria per requirement, ideally in given/when/then form
- The source tree and test suite where implementations will be annotated
- The coverage bar the merge gate enforces (mandatory-requirement coverage, typically 1.0)
- The previous requirements snapshot, when checking for drift against a baseline
- Which requirements are explicitly out of scope for the current milestone

## Clarify First

Before writing or auditing a spec, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **What must be true for this to be "done"** — becomes the acceptance criteria; without it the spec is a wish list and nothing is verifiable
- [ ] **Which constraints are hard vs preferences** — decides must/shall versus should, which in turn decides what the merge gate blocks on
- [ ] **Who consumes the spec** — an implementing engineer, a generating model, and an auditor need different precision; the generating case needs the most
- [ ] **Scope boundary for this milestone** — requirements outside it must be marked, or coverage reports will show permanent false gaps

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Write the spec, then prove it is precise

1. Draft requirements one statement at a time, each with exactly one obligation and a
   modality keyword. Two obligations in one sentence become two requirements.
2. Attach given/when/then acceptance criteria directly beneath each requirement.
3. Run the ambiguity linter. Fix every error before circulating the draft; errors are
   statements no engineer could implement without guessing.
4. Re-run until the precision ratio clears 0.85. Below that, review meetings will be
   spent discovering ambiguity rather than discussing design.

```bash
python3 engineering/spec-driven-workflow/scripts/spec_lint.py \
  --spec engineering/spec-driven-workflow/assets/sample_spec.md \
  --max-findings 0 --min-precision 0.85 --format text
```

The shipped sample scores 0.46 on purpose — it contains the exact failures the linter
is built to catch, so you can see each rule fire before pointing it at real work.

### Workflow 2 — Extract requirement IDs and freeze the baseline

1. Parse the spec into requirements. IDs are derived from section and ordinal
   (`REQ-ROTATION-02`), so they are stable across unrelated edits elsewhere in the file.
2. Commit the emitted JSON alongside the spec. This is the baseline.
3. On every subsequent parse, diff against the baseline. A `DRIFT` line means a
   requirement's text changed while its ID stayed the same — its tests now verify
   something the spec no longer says, which is the most dangerous state in the workflow.

```bash
python3 engineering/spec-driven-workflow/scripts/spec_parse.py \
  --spec engineering/spec-driven-workflow/assets/sample_spec.md \
  --baseline engineering/spec-driven-workflow/assets/sample_requirements.json \
  --require-acceptance --format text
```

Exit code is 1 when a mandatory requirement lacks acceptance criteria or when any
requirement has drifted, which makes this the first half of the CI gate.

### Workflow 3 — Gate the merge on bidirectional coverage

1. Annotate implementations and tests with their requirement IDs in comments or test
   names (`def test_rotation_marks_pending_revocation():  # REQ-ROTATION-01`).
2. Run coverage against the source tree. Read both directions: requirements with no
   implementation, and annotations naming IDs the spec no longer contains.
3. Fail the build below the mandatory coverage floor, or on any orphan annotation.

```bash
python3 engineering/spec-driven-workflow/scripts/trace_coverage.py \
  --requirements engineering/spec-driven-workflow/assets/sample_requirements.json \
  --index engineering/spec-driven-workflow/assets/sample_trace_index.json \
  --min-coverage 1.0 --format text
```

Swap `--index` for `--code <path>` to scan a real tree. The index form exists so the
gate can run against a trace index built by another tool, and so this workflow is
runnable straight from a fresh clone.

## Decision frameworks

### How precise does the spec need to be? [PROVEN]

Precision is a cost, and the right amount depends entirely on who reads the spec next.

| Consumer | Required precision | Test |
|----------|-------------------|------|
| Engineer on the team who wrote it | Moderate | Shared context fills gaps; acceptance criteria on mandatory requirements only |
| Engineer on another team | High | Every requirement has criteria; no undefined domain terms |
| A model generating the implementation | Very high | Every requirement quantified; no adjective without a number |
| An auditor or regulator | Very high, plus provenance | Every requirement traced to a test result and a decision record |

Writing at "very high" for an internal one-week feature is waste. Writing at "moderate"
for a generated implementation produces confidently wrong code, because ambiguity gets
resolved silently rather than escalated.

### Requirement status ladder

Every requirement sits in one of four states. Only one is acceptable at merge.

| Status | Meaning | Action |
|--------|---------|--------|
| `covered` | Implementation and test both annotated | Merge |
| `untested` | Code exists, no test references the ID | Block — this is the state that regresses silently |
| `test-only` | Test exists, no implementation annotated | Usually a missing annotation, occasionally a test asserting nothing |
| `unimplemented` | Neither exists | Block if mandatory; acceptable if explicitly deferred |

### Coverage floors by requirement modality [RECOMMENDED]

| Modality | Keyword | Coverage floor at merge |
|----------|---------|------------------------|
| Mandatory | must, shall | 1.0 — no exceptions; a mandatory requirement without a test is not implemented |
| Recommended | should | 0.8 — deviations recorded in the PR with a reason |
| Optional | may, can | No floor — tracked, not gated |

The floors matter less than their being non-negotiable once set. A coverage gate that
gets waived twice stops being read.

### Ambiguity rules and what each one prevents

| Rule | Fires on | Prevents |
|------|----------|----------|
| `unquantified-adjective` | fast, scalable, secure, intuitive | Requirements nobody can fail |
| `passive-no-actor` | "notifications should be delivered" | Obligations with no owning component |
| `no-acceptance-criteria` | Normative statement with no given/when/then | Requirements that cannot be verified |
| `placeholder` | TBD, TODO, ??? | Specs that gate merges while still undecided |
| `compound-requirement` | "and/or", two obligations in one sentence | Partial implementations that still pass |
| `undefined-antecedent` | Opens with it/this/they | Requirements that break when reordered |
| `vague-quantifier` | some, several, most | Disagreement discovered at review time |

## Anti-Patterns

### The Write-Once Spec
**Mistake:** Writing a thorough specification at kickoff, then implementing against reality for six weeks without touching it.
**Why it happens:** Updating the spec has no forcing function. Nothing breaks when it goes stale, so it loses every contest for attention against shipping code.
**Instead:** Put the spec in the same repository, in the same PR, behind the same merge gate as the code. A requirement change and its implementation land together or neither lands. The gate is what converts "we should keep it updated" into a thing that actually happens.

### Adjective-Driven Requirements
**Mistake:** "The API must be fast and the interface must be intuitive."
**Why it happens:** These feel like requirements and are easy to agree on precisely because nobody can disagree. Everyone leaves the meeting satisfied and holding different pictures.
**Instead:** Every adjective becomes a number with a unit and a measurement method: "p95 latency under 200ms measured at the load balancer over a 5-minute window." If you cannot produce the number, the requirement is not ready and should be marked as such rather than shipped vague.

### ID Drift
**Mistake:** Editing a requirement's text in place while keeping its ID, so tests that reference the ID now verify something the spec no longer says.
**Why it happens:** Renumbering feels disruptive, and editing text feels smaller than adding a requirement. Both are true; the consequence is still a silent divergence.
**Instead:** Fingerprint requirement text and diff against a committed baseline on every parse. A drift finding forces a decision: either the tests get updated, or the edit was actually a new requirement and needs a new ID.

### One-Way Traceability
**Mistake:** Checking that every requirement has code, but never checking that every annotated code path has a requirement.
**Why it happens:** The forward direction answers "did we build what we promised," which is the question stakeholders ask. Nobody asks the reverse question, so nobody builds the report.
**Instead:** Run coverage in both directions and treat orphan annotations as errors. Orphans mark dead features whose requirement was deleted, typos in IDs, and scope that entered the codebase without ever entering the spec — all three are worth knowing.

### The Merge Gate Nobody Believes
**Mistake:** Setting a 100% coverage gate, waiving it under deadline, and waiving it again the following week.
**Why it happens:** The gate was set at an aspirational number rather than the number the team will actually hold, so the first real deadline breaks it.
**Instead:** Gate only on mandatory requirements, at 1.0, and let `should` requirements report without blocking. A narrow gate that never gets waived changes behaviour; a broad gate that gets waived teaches everyone that red builds are advisory.

## Files

| File | Purpose |
|------|---------|
| `scripts/spec_parse.py` | Parse a markdown spec into requirements with stable IDs and content fingerprints; diff against a baseline |
| `scripts/spec_lint.py` | Flag ambiguity — unquantified adjectives, passive requirements, missing criteria, placeholders |
| `scripts/trace_coverage.py` | Bidirectional spec-to-code coverage with orphan-annotation detection and a merge gate exit code |
| `references/spec-writing-guide.md` | Requirement grammar, acceptance-criteria patterns, and worked ambiguous-to-precise rewrites |
| `references/traceability-model.md` | ID schemes, annotation conventions per language, CI wiring, and drift handling |
| `assets/sample_spec.md` | Runnable sample spec containing both precise and deliberately ambiguous requirements |
| `assets/sample_requirements.json` | Parsed baseline for the drift and coverage workflows |
| `assets/sample_trace_index.json` | Prebuilt trace index exercising covered, untested, test-only, and orphan states |
| `assets/spec-template.md` | Skeleton for a new specification with the required structure |
