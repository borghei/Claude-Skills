# Markdown Review Rulebook and Severity Model

The complete rule catalog enforced by this skill, the severity taxonomy behind the CI gate, the
configuration schema, and the integration patterns that keep a publication gate fast and trusted.

---

## 1. Why a pre-publication gate exists

Markdown that converts cleanly to HTML is not the same as Markdown that is *publishable*. A
converter is happy to render a document with three H1s, four dead links, an image with no alt
text, and a 67-word sentence. The HTML will validate. The page will still be bad.

The review gate sits between authoring and conversion. It catches the defects that are cheap to
fix in Markdown and expensive to fix after publication:

| Defect | Cost to fix pre-publication | Cost to fix post-publication |
| --- | --- | --- |
| Broken relative link | 30 seconds, one edit | Rebuild, redeploy, cache purge, possible 404 in search index |
| Missing image alt text | 60 seconds writing a description | Accessibility complaint, remediation ticket, possible legal exposure |
| Skipped heading level | 10 seconds | Screen-reader users already navigated a broken outline |
| Wrong terminology | Seconds per instance | Inconsistent docs corpus, degraded search, brand drift |
| Missing frontmatter field | 15 seconds | Broken index page, missing card, silent CMS failure |

The economics are the entire argument. Every finding this gate produces is one that costs 10x to
100x more after the page is live.

### The zero-network rule

**This gate never makes a network request.** That is a hard design constraint, not a limitation.

Reasons, in order of importance:

1. **Determinism.** A gate that fails because a third-party server was slow is a gate engineers
   learn to ignore. Once a check is flaky, every failure gets re-run rather than read.
2. **Speed.** Offline checks on a 2,000-line document complete in well under a second. Network
   link checking on the same document takes 10-90 seconds depending on target hosts.
3. **Privacy.** Fetching every URL in a draft leaks the draft's research trail to every host
   mentioned in it. For drafts under embargo this is disqualifying.
4. **Rate limits.** Repeated CI runs against the same external hosts produce 429s and, eventually,
   blocks. The gate then fails for reasons unrelated to document quality.

External links are therefore **inventoried, never fetched**. The inventory is genuinely useful
output — it tells a reviewer exactly which hosts a document depends on — but its verification is
a separate, network-enabled, non-blocking job that runs on a schedule, not on every commit.

---

## 2. Severity taxonomy

Three levels. Resist the urge to add more; a four-level or five-level scale produces arguments
about classification rather than fixes.

### error — blocks publication

A finding is an error when **a reader will encounter a concrete defect**. Not a style preference.
Not a maintainer inconvenience. A defect the reader hits.

Qualifying tests — an error must satisfy all three:

1. **Reader-visible.** Someone reading the published page is worse off.
2. **Unambiguous.** There is no legitimate authoring reason to do this.
3. **Mechanically fixable.** The author can resolve it without a product decision.

Examples that qualify: a link that 404s, an image a screen reader cannot describe, a table with no
header row, a missing required frontmatter field that breaks the index page.

Examples that do **not** qualify: a section that runs long (a judgment call), prose that scores
below a readability band (audience-dependent), terminology drift (a house-style preference).

### warning — fix before the next review cycle

Real quality problems that are context-dependent or subjective enough that a blanket block causes
more harm than good. Warnings accumulate into technical debt and should be capped — see the
`max_warnings` gate setting — but a single warning must never stop a release.

### info — recorded, never acted on urgently

Observations that improve the document but are frequently correct as written. Passive voice is the
canonical example: it is often the right choice ("the server was compromised" when the actor is
unknown), so counting it is useful and blocking on it is not.

### Severity assignment table

| Rule ID | Default | Rationale |
| --- | --- | --- |
| `frontmatter.absent` | error | Downstream tooling cannot index the page at all |
| `frontmatter.missing` | error | A required field is absent or empty; index/card rendering breaks |
| `frontmatter.wrong-type` | error | Type mismatch breaks parsers silently (a string where a list is expected) |
| `frontmatter.too-long` | warning | Truncation is ugly but not broken |
| `structure.no-h1` | error | Document has no accessible name; breaks outline and SEO title |
| `structure.multiple-h1` | error | Ambiguous document title; violates the single-H1 document outline |
| `structure.h1-not-first` | warning | Usually a mistake, occasionally intentional in partials |
| `structure.skipped-level` | error | Breaks screen-reader outline navigation (WCAG 1.3.1) |
| `structure.too-deep` | warning | H5/H6 signals a page that should be split; not a defect per se |
| `structure.section-too-long` | warning | Judgment call; depends on content type |
| `structure.section-too-short` | info | Sometimes a deliberate signpost section |
| `structure.heading-case-inconsistent` | error → warning | Style, not defect; overridden to warning in the shipped profile |
| `a11y.missing-alt` | error | WCAG 1.1.1 Level A failure |
| `a11y.placeholder-alt` | warning | Present but useless; still better than absent |
| `a11y.alt-too-long` | info | Verbose alt is tiring, not blocking |
| `a11y.non-descriptive-link` | error | WCAG 2.4.4 Level A failure |
| `a11y.bare-url-link-text` | warning | Read character-by-character by some screen readers |
| `a11y.table-no-header` | error | WCAG 1.3.1 Level A failure; data table with no programmatic headers |
| `link.broken-relative` | error | 404 for the reader |
| `link.broken-anchor` | error | Silent scroll-to-top; reader never reaches the content |
| `link.duplicate-anchor` | warning | Anchors shift silently when headings repeat |
| `readability.very-long-sentence` | error | 45+ words is a comprehension failure at any audience level |
| `readability.long-sentence` | warning | 30-45 words is heavy but sometimes correct |
| `readability.passive-voice` | info | Frequently the right choice |
| `readability.grade-level-high` | warning | Audience-dependent |
| `terminology.disallowed-term` | warning | House style; blocking creates release friction |

### Overriding severities

Every rule ID is overridable in config. This is deliberate — a rulebook that cannot be tuned to a
team's context gets disabled wholesale.

```json
"severity_overrides": {
  "structure.heading-case-inconsistent": "warning",
  "readability.grade-level-high": "warning",
  "terminology.disallowed-term": "warning",
  "structure.section-too-long": "info"
}
```

**The one rule that should never be downgraded is `a11y.missing-alt`.** Every other check has a
defensible exception. Missing alt text does not; if an image is decorative, the fix is an explicit
empty alt with a decorative marker, not a suppressed rule.

---

## 3. Structure rules in detail

### Single H1 (`structure.no-h1`, `structure.multiple-h1`)

**Threshold: exactly one H1 per document.**

An HTML document's H1 is its accessible name in the heading outline. Two H1s means two documents
in one file. Screen-reader users navigating by heading level land on both and cannot tell which
is the page.

The common cause is an appendix or a second article pasted into the same file. The fix is always
either demote to H2 or split the file.

**Escape hatch:** documentation *fragments* — files intended for inclusion inside another page —
legitimately have no H1. Set `require_single_h1: false` and `require_h1_first: false` for a
fragments directory, and run the strict profile on the assembled output instead.

### No skipped levels (`structure.skipped-level`)

**Threshold: heading level may increase by at most 1 at a time.**

H2 → H4 is a violation. H4 → H2 is not — closing multiple levels is normal.

This maps directly onto WCAG 1.3.1 (Info and Relationships). A screen reader announces "heading
level 4" after "heading level 2" and the user infers a missing level-3 section that does not
exist. Authors do this because H3 "looks the right size" in their preview theme. The fix is CSS,
not a level skip.

### Heading depth (`structure.too-deep`)

**Threshold: H4 maximum for articles, H5 for reference documentation, never H6.**

| Document type | Max depth | Reasoning |
| --- | --- | --- |
| Blog post / article | H3 | More than two levels of nesting means the piece has two topics |
| Tutorial / how-to | H4 | Steps within phases within the guide |
| Reference documentation | H5 | Namespaces, types, methods, parameters, notes |
| Any document | never H6 | If you reach H6 the document should be several documents |

### Section length (`structure.section-too-long`, `structure.section-too-short`)

**Thresholds: 400 words maximum, 15 words minimum between headings.**

The 400-word ceiling comes from scan behavior — readers scanning a technical page look for the
next heading roughly every screen, and 400 words is about two screens at typical documentation
line lengths. Beyond that, the section becomes an unnavigable wall.

The 15-word floor catches the opposite failure: a heading with one line beneath it, usually the
residue of an outline that was never filled in, or a heading used as a bold label.

Both are warnings/info, never errors. A 600-word section with a good reason is fine.

### Heading capitalization (`structure.heading-case-inconsistent`)

**Threshold: 100% of headings match the document's dominant style, evaluated only when the
document has 3+ headings.**

Two legitimate styles:

- **Sentence case** — "Rotating service credentials". Recommended for documentation. Easier to
  write consistently, reads better with technical terms embedded, and avoids arguments about
  whether "API" and "of" are capitalized.
- **Title case** — "Rotating Service Credentials". Common in marketing and book-style content.

The detector classifies a heading as title case when 60%+ of its words after the first — excluding
articles, conjunctions, and short prepositions — begin with a capital. Below 3 headings there is
not enough signal to infer a dominant style, so the check is skipped.

`heading_case` in config pins the expected style explicitly. Leave it unset to let the document's
own majority win, which is the right behavior when auditing an inherited corpus.

---

## 4. Link rules in detail

### Resolution model

Every link target is classified into exactly one of four kinds:

| Kind | Example | Resolution |
| --- | --- | --- |
| `anchor` | `#installation` | Slugified headings of the same file |
| `relative` | `./guide.md`, `../img/a.png`, `guide.md#setup` | Filesystem path relative to the source file's directory |
| `absolute` | `/docs/guide.md` | Filesystem path relative to `--root`; unchecked without it |
| `external` | `https://…`, `mailto:…`, `//cdn…` | Inventoried only, never fetched |

### Slug generation

Anchor resolution requires reproducing the converter's slug algorithm. The implementation here
matches the widely-used GitHub-flavored behavior:

1. Strip inline link syntax, keeping the link text.
2. Strip backticks, asterisks, underscores, and tildes.
3. Lowercase.
4. Remove every character that is not a word character, whitespace, or hyphen.
5. Replace runs of whitespace and underscores with a single hyphen.
6. Trim leading and trailing hyphens.
7. On a repeat slug, append `-1`, `-2`, … in document order.

`## Rotate the credential` → `rotate-the-credential`
`## Step 2: Verify (optional)` → `step-2-verify-optional`
`## API: \`GET /users\`` → `api-get-users`

**If your converter uses a different algorithm, the anchor check will produce false positives.**
Verify against one known-good anchor before trusting the results at scale. Python-Markdown's
`toc` extension and most static site generators match this algorithm; a few CMSes do not.

### Duplicate anchors (`link.duplicate-anchor`)

Two headings that slugify identically produce `#setup` and `#setup-1`. The second is invisible to
an author who wrote `#setup` intending the later section. Nothing errors — the reader simply lands
in the wrong place. Reported as a warning with the collision count.

### External link inventory

The inventory groups by host and counts occurrences. Use it for three things:

1. **Dependency review** — a documentation page depending on 14 distinct third-party hosts is a
   link-rot liability.
2. **Policy enforcement** — competitor domains, staging hosts, or `localhost` URLs left in a draft
   show up immediately.
3. **Scheduled verification** — feed the host list to a separate weekly network job.

`localhost`, `127.0.0.1`, and internal-only hostnames appearing in a public document are the most
common real finding here, and no network check would catch them anyway.

---

## 5. Frontmatter validation

### Schema definition

```json
"frontmatter": {
  "required_fields": ["title", "description", "author", "date", "tags"],
  "field_types": { "title": "string", "date": "date", "tags": "list" },
  "max_lengths": { "title": 60, "description": 160 }
}
```

| Setting | Effect | Failure severity |
| --- | --- | --- |
| `required_fields` | Field must be present and non-empty | error |
| `field_types` | `string`, `list`, or `date` (ISO-8601 `YYYY-MM-DD`) | error |
| `max_lengths` | Character ceiling for string fields | warning |

### Recommended length limits

| Field | Limit | Why |
| --- | --- | --- |
| `title` | 60 chars | Search result titles truncate around 55-60 characters |
| `description` | 160 chars | Meta description truncation point in major search engines |
| `slug` | 75 chars | URL readability; longer slugs get truncated in shares |

These are warning-level because truncation degrades a preview, it does not break a page.

### The parser's deliberate limits

The frontmatter parser handles the subset of YAML that documentation frontmatter actually uses:
top-level `key: value` pairs and top-level `- item` lists. It does **not** handle nested mappings,
multi-line scalars (`|`, `>`), anchors, or flow-style collections.

This is a feature. Frontmatter that needs full YAML is frontmatter that has become a configuration
file, and it belongs in a configuration file. If your frontmatter genuinely requires nesting, the
right move is to validate it with your site generator's own schema tooling and set
`required_fields: []` here to disable the check.

---

## 6. Configuration reference

### Full schema

```json
{
  "profile_name": "string — identifies the profile in reports",
  "frontmatter": {
    "required_fields": ["array of field names"],
    "field_types": { "field": "string | list | date" },
    "max_lengths": { "field": 60 }
  },
  "structure": {
    "require_single_h1": true,
    "require_h1_first": true,
    "allow_skipped_levels": false,
    "max_heading_depth": 4,
    "max_section_words": 400,
    "min_section_words": 15,
    "heading_case": "sentence | title | unset"
  },
  "accessibility": {
    "min_alt_text_chars": 10,
    "max_alt_text_chars": 150,
    "placeholder_alt_text": ["image", "screenshot", "..."],
    "non_descriptive_link_text": ["click here", "read more", "..."],
    "require_table_headers": true,
    "flag_bare_urls_as_link_text": true
  },
  "readability": {
    "audience": "string label",
    "target_flesch_min": 50.0,
    "target_flesch_max": 70.0,
    "max_grade_level": 12.0,
    "long_sentence_words": 30,
    "very_long_sentence_words": 45,
    "max_long_sentence_pct": 10.0,
    "max_passive_pct": 15.0
  },
  "terminology": { "preferred term": ["disallowed", "variants"] },
  "severity_overrides": { "rule.id": "error | warning | info" },
  "gate": { "fail_on": "error", "max_errors": 0, "max_warnings": 25 }
}
```

### Profile strategy

Run **two or three profiles**, not one, and not one per directory.

| Profile | `fail_on` | `max_warnings` | Applies to |
| --- | --- | --- | --- |
| `strict` | error | 10 | Published docs, public API reference, marketing pages |
| `default` | error | 25 | Internal documentation, guides, runbooks |
| `draft` | never | unlimited | Work in progress; report-only, no blocking |

Resist per-directory profiles. Every additional profile is a place where a rule silently does not
apply, and the corpus drifts apart along profile boundaries.

---

## 7. Gate design

### Exit code contract

| Code | Meaning | CI behavior |
| --- | --- | --- |
| 0 | Gate passed | Continue to conversion/publish |
| 1 | Tool error — bad path, malformed config, unreadable file | **Fail the build**; this is a broken setup, not a document problem |
| 2 | Gate failed — blocking findings present | Fail the build; print findings |

Separating 1 from 2 matters. A build that fails with code 1 needs a repository fix; a build that
fails with code 2 needs an author fix. Collapsing both into 1 sends every failure to the wrong
person first.

### The warning budget

`max_warnings` exists to stop the slow death of a gate. Without it, warnings accumulate until
nobody reads the output, at which point the errors hide in the noise too.

Set the budget at roughly the current warning count when you adopt the gate, then ratchet it down
by 10-20% per quarter. A budget that starts at zero on a legacy corpus produces one enormous
cleanup PR that nobody reviews properly.

### Rollout sequence

Adopting a gate on an existing corpus in one step fails. Use four phases:

| Phase | Duration | `fail_on` | Goal |
| --- | --- | --- | --- |
| 1. Observe | 2 weeks | `never` | Collect the real finding distribution; tune the term map |
| 2. New content only | 4 weeks | `error` on changed files | Stop the bleeding without a backlog cleanup |
| 3. Ratchet | 1-2 quarters | `error`, descending `max_warnings` | Burn down the legacy backlog |
| 4. Steady state | ongoing | `error`, fixed budget | Maintain |

Phase 2 is the critical one. Gating only files touched by the current change makes the gate
immediately valuable and never blocking on unrelated debt.

---

## 8. CI integration patterns

### Changed-files-only gate

The highest-value pattern. Run the gate against the Markdown files in the diff, not the corpus.

```bash
git diff --name-only origin/main...HEAD -- '*.md' | while read -r file; do
  python3 scripts/md_review_gate.py --input "$file" --config profiles/default.json || status=2
  python3 scripts/link_checker.py --input "$file" --root "$PWD" || status=2
done
exit "${status:-0}"
```

### Full-corpus scheduled audit

Weekly, non-blocking, reported as a trend. This is where corpus-wide regressions surface —
terminology drift, growing warning counts, readability creep.

```bash
find docs -name '*.md' -print0 | xargs -0 -I{} \
  python3 scripts/readability_scorer.py --input {} --config profiles/default.json \
    --format json --fail-on never >> audit.jsonl
```

### Report artifact

Emit JSON from all three scripts, merge, and attach to the build. JSON output is stable and keyed
by rule ID, so dashboards built on it survive message rewording.

---

## 9. Rule tuning workflow

When a rule produces false positives, the response order matters:

1. **Fix the config first.** Most false positives are a term map entry that is too broad or a
   threshold set for the wrong audience.
2. **Downgrade the severity second.** A rule that is right 70% of the time belongs at warning.
3. **Disable the rule last, and record why.** An undocumented disabled rule gets re-enabled by the
   next maintainer and the same argument happens again.

Never suppress findings inline in the document. Inline suppression comments spread, are never
reviewed, and turn into permanent exemptions. If a rule needs an exception often enough to want
inline suppression, the rule is wrong.

---

## 10. What this gate deliberately does not check

Knowing the boundaries prevents false confidence:

- **Factual accuracy.** No tool checks whether the instructions work.
- **External link liveness.** By design; see the zero-network rule.
- **Rendered visual output.** Layout, spacing, and code-block highlighting are conversion concerns.
- **Color contrast.** Requires rendered CSS; belongs in an HTML-stage audit.
- **Keyboard navigation and focus order.** Requires a rendered DOM.
- **Reading order of complex layouts.** Markdown has one reading order by construction.
- **Spelling.** Use a dedicated spell checker with a project dictionary; overlapping the two makes
  both noisier.
- **Semantic correctness of code samples.** Run the samples; do not lint them here.

The gate covers the defects that are visible in the source text. Everything else needs a rendered
page, and belongs to the stage after conversion.
