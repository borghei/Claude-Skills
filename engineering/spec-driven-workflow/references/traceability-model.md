# Traceability Model

ID schemes, annotation conventions, drift handling, and CI wiring. Load this when
setting up traceability on a repository or when a coverage report is producing
findings you did not expect.

---

## 1. The ID scheme

IDs take the form `REQ-<SECTION>-<NN>`, where `<SECTION>` is a slug of the enclosing
heading and `<NN>` is the ordinal within that section.

```
REQ-ROTATION-02
REQ-KEY-ISSUANCE-01
REQ-NON-FUNCTIONAL-01
```

### Why section-scoped ordinals

The alternative — a flat global counter — renumbers everything downstream when a
requirement is inserted early in the document, which invalidates every annotation in
the codebase for a one-line spec edit. Section scoping contains the blast radius to
one section.

### Stability properties

| Edit | ID impact |
|------|-----------|
| Add a requirement at the end of a section | None to existing IDs |
| Insert a requirement mid-section | Renumbers later IDs *in that section only* |
| Reword a requirement in place | ID stable, fingerprint changes → drift finding |
| Rename a section heading | All IDs in that section change |
| Reorder sections | No ID changes |

Section renames are the expensive edit. Name sections for stable domain concepts
(`Rotation`, `Revocation`) rather than for organisational artifacts (`Sprint 4`,
`Phase 2`), and the expensive edit never happens.

### Fingerprints

Each requirement carries an 8-character hash of its whitespace-normalized, lowercased
text. This exists to catch the one edit an ID scheme cannot: text changing while the
ID stays the same.

That state is more dangerous than a renumbering, because nothing appears broken. The
tests still reference a live ID and still pass. They are simply verifying an
obligation the specification no longer contains.

---

## 2. Annotation conventions

An annotation is the requirement ID appearing verbatim in source or test code. The
scanner matches `REQ-[A-Z0-9-]+-\d\d` anywhere in a file, so any comment style works.

### Per language

| Language | Convention |
|----------|-----------|
| Python | `def test_x():  # REQ-ROTATION-01` or in the test docstring |
| JavaScript / TypeScript | `it("marks pending revocation [REQ-ROTATION-01]", ...)` |
| Go | `// REQ-ROTATION-01` above the test function |
| Java | `@Tag("REQ-ROTATION-01")` or a Javadoc line |
| Ruby | `it "marks pending revocation (REQ-ROTATION-01)"` |
| SQL migrations | `-- REQ-SCHEMA-03` in the file header |

Putting the ID in the **test name** rather than a comment is worth the ugliness: the
ID then appears in CI output, so a failing build names the violated requirement
directly instead of a test file.

### Where to annotate in source

Annotate the narrowest construct that implements the requirement — the function, not
the module. Module-level annotations produce technically-covered requirements whose
implementation nobody can locate, which is coverage theatre.

One requirement may legitimately appear in several files. One file may implement
several requirements. Neither is a finding.

### What not to annotate

Do not annotate framework glue, generated code, or configuration that merely enables
an implementation. The annotation should mark where the obligation is *satisfied*,
not everywhere it is touched. Over-annotation degrades the report's precision until
"which file implements this" stops being answerable.

---

## 3. Reading the coverage report

### The four statuses

| Status | Source | Test | Usual cause | Action |
|--------|--------|------|-------------|--------|
| `covered` | yes | yes | Working as intended | Merge |
| `untested` | yes | no | Shipped without a test, or the test lacks an annotation | Block |
| `test-only` | no | yes | Missing source annotation, or a test asserting nothing real | Investigate |
| `unimplemented` | no | no | Not built yet, or deliberately deferred | Block if mandatory |

`untested` is the status worth the most attention. The behaviour exists, so it works
today and demos fine. Nothing prevents its regression, and nobody will notice until
the requirement matters — typically during an incident.

`test-only` is usually benign (a missing source annotation) but occasionally reveals a
test that constructs its own fixture and asserts against it, verifying nothing about
the production path.

### Orphan annotations

An orphan is an ID appearing in code that the current spec does not contain. Three
causes, all worth surfacing:

1. **Deleted requirement, surviving code** — the feature was descoped, and the
   implementation stayed. This is how dead code accumulates in specified systems.
2. **Typo in the annotation** — `REQ-ROTATON-01`. Silently uncovers the real
   requirement while looking fully covered by eye.
3. **Section renamed** — every ID in that section became an orphan simultaneously.
   The tell is a cluster of orphans sharing a prefix.

Cause 3 is why the tool reports orphans grouped and with locations: a single rename
produces a distinctive shape in the report, and the fix is a bulk rename rather than
an investigation.

---

## 4. Drift handling

When the parser reports `DRIFT REQ-X-NN`, the requirement's text changed while its ID
stayed the same. Exactly one of two things is true:

**The change was a clarification.** The obligation is the same; the wording improved.
Re-read the tests referencing that ID, confirm they still verify the obligation, and
commit the new baseline.

**The change was a new obligation.** Someone edited an existing requirement instead of
adding one. The tests now verify something that is no longer required, and the actual
new requirement is untested. Split it: restore the original text, add the new
obligation as a new requirement with a new ID.

The distinction cannot be automated, which is why drift exits non-zero and demands a
human decision rather than auto-updating the baseline. A tool that silently rebaselines
on drift provides no value over having no baseline at all.

### Baseline hygiene

- Commit `requirements.json` next to the spec, in the same PR.
- Never edit it by hand. It is generated output.
- Regenerate it in the same commit that changes the spec, so the diff shows both.
- Review the diff. A spec PR whose requirements diff is larger than expected is the
  cheapest place to catch scope creep.

---

## 5. CI wiring

Three gates, in order. Each is cheap and fails fast.

```bash
# Gate 1 — the spec is precise enough to implement against
python3 scripts/spec_lint.py --spec docs/spec.md --max-findings 0 --min-precision 0.85

# Gate 2 — every mandatory requirement is verifiable, and nothing drifted silently
python3 scripts/spec_parse.py --spec docs/spec.md \
  --baseline docs/requirements.json --require-acceptance --format json > /tmp/current.json

# Gate 3 — bidirectional coverage clears the floor and no orphans exist
python3 scripts/trace_coverage.py --requirements /tmp/current.json \
  --code . --min-coverage 1.0
```

### Exit codes

| Script | Exits 1 when |
|--------|-------------|
| `spec_lint.py` | Error findings exceed `--max-findings`, or precision below `--min-precision` |
| `spec_parse.py` | `--require-acceptance` and a mandatory requirement lacks criteria, or any drift |
| `trace_coverage.py` | Mandatory coverage below `--min-coverage`, or any orphan annotation |

### Rollout sequence for an existing codebase

Turning all three gates on at once against a mature repository produces hundreds of
findings and gets the whole thing reverted within a week. Sequence instead:

1. **Week 1 — report only.** Run all three in CI with `|| true`. Publish the numbers.
   Do not gate.
2. **Week 2-3 — ratchet the lint.** Set `--min-precision` to the current measured
   value. Raise it by 0.05 per week. New ambiguity cannot be added; existing ambiguity
   drains.
3. **Week 4 — gate new requirements only.** Coverage floor applies to requirements
   added after the baseline commit. Legacy requirements report without blocking.
4. **Week 6+ — full gate.** Mandatory coverage at 1.0, orphans as errors, drift as
   an error.

The ratchet in step 2 is the mechanism that matters. A quality bar that only forbids
getting worse is politically survivable in a way that a bar demanding immediate
improvement is not.

---

## 6. Scaling limits

| Spec size | Viable | Notes |
|-----------|--------|-------|
| Under 50 requirements | Yes | Single document, single baseline |
| 50-200 | Yes | Split into per-area documents, one baseline each |
| 200-500 | With discipline | Section slugs must be globally unique across documents |
| Over 500 | Reconsider | Usually several systems' specs in one file; split by service boundary |

Above roughly 200 requirements in one document, section-slug collisions across files
become the dominant failure mode: two documents both containing a `## Rotation`
section produce colliding IDs. Prefix section slugs per document, or split by service
and keep one baseline per service.

Scan cost is not the constraint — `trace_coverage.py` caps at 5,000 files by default
and scans a large monorepo in seconds. The constraint is human: a coverage report
with 400 rows does not get read, and an unread gate is an unenforced one.
