---
name: linkedin-engagement-analytics
description: >
  Segments who reacted to and commented on a post from a CSV or JSON export,
  and says whether it reached the intended audience. Use when reviewing a
  post's engagers, checking audience fit, or building a baseline.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: tools
  domain: linkedin
  updated: 2026-10-07
  tags: [linkedin, analytics, audience-segmentation, engagement, privacy]
---

# LinkedIn Engagement Analytics

A post gets two hundred reactions and the author concludes it worked. Nobody
checks who the two hundred were. Often a third are colleagues, a third are
recruiters and vendors, and the people the post was written for are a handful.
The next post is modelled on the "successful" one, and the account drifts
toward whatever earns the most reactions from the widest crowd, away from the
readers it was meant to reach.

This skill answers a narrower question than "how did it do": of the people who
responded, what share were the people it was for, and is that better or worse
than this author's own recent posts? It classifies each engager's headline
into a seniority band and a function, sets aside colleagues, compares the mix
with a target audience written beforehand, and states the result with an
interval so that noise is not reported as a change. It works **offline**, from
an export the user supplies. It does not collect engagement data, log in to
anything, or call any service.

**Personal data.** An export contains real people's names, job titles and
employers. Keep it local, remove columns the analysis does not need, report
segments and never individuals, add nothing about anyone from another source,
and delete the file once the readout is written. The scripts print aggregates
only. The agent does not produce contact lists, per-person notes or lookups
from an export, whoever asks. Full rules: `references/data-handling.md`.

**Scope boundary.** This skill describes the audience of a post after the
fact. It does **not** write or polish posts (`linkedin-post-writer`,
`linkedin-humanizer`), assess opening lines (`linkedin-hook-analyzer`), or
write comments and replies (`linkedin-comment-writer`,
`linkedin-reply-manager`). It does **not** follow conversations over time
(`linkedin-thread-tracker`), plan or reuse content (`linkedin-content-planner`,
`linkedin-content-repurposer`), or interview for stories
(`linkedin-story-interviewer`). Profiles are `linkedin-profile-optimizer`;
team programmes and their measurement are `linkedin-employee-advocacy`. Each
is independent of this one.

## When to use this skill

- A post drew a response and the author wants to know whether it reached the intended readers
- Reactions are rising and inbound from the right people is not
- An author wants a baseline of their own audience mix before changing what they write
- Two subjects or framings need comparing on who they attract, not how many
- A sponsor asks whether content is reaching a named segment and the answer so far is a reaction count
- An export exists and someone is about to turn it into a contact list (use this instead, and say why)

## Inputs the skill expects

- One export per post, CSV or JSON, with at least a headline column (`references/segmentation-method.md` §2 lists accepted column names)
- How and when each export was produced; it must be the user's own post and a permitted method
- A target audience file written **before** the export is read: seniority bands, functions, title keywords, optionally named organisations
- Every name the user's own employer goes by, so colleagues can be set aside
- Optionally, the user's own goal for core share and a trailing baseline from earlier posts

## Clarify First

Before analysing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Who the post was written for** — the whole verdict is measured against it; a target invented after reading the export describes whoever turned up
- [ ] **Where the export came from and whose post it is** — decides whether the analysis should run at all, and which limits go in the readout
- [ ] **The user's own-company names** — without them colleagues count as audience and the fit figure is inflated
- [ ] **Whether a baseline exists** — with one, the readout can say above, in line or below; without one, this run becomes the first baseline point and no verdict is given

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Quick start: read one post's audience

1. Remove unneeded columns from the export (links, locations, identifiers)
   and save it locally.
2. Copy `assets/target_audience_template.json` and describe the intended
   reader. Check the band and function names with `--list-rules`.
3. Run the segmenter.
4. The agent reports coverage, the core share with its interval, the largest
   segments and the limits, using the script output only. It does not open
   the raw rows or name anyone.

```bash
python3 tools/linkedin/linkedin-engagement-analytics/scripts/engager_segmenter.py \
  --input tools/linkedin/linkedin-engagement-analytics/assets/sample_engagers.csv \
  --target tools/linkedin/linkedin-engagement-analytics/assets/sample_target_audience.json
```

### Workflow 2 — Build or roll a trailing baseline

1. Gather exports for the last five to eight comparable posts, produced the
   same way.
2. Pass them all in one command. The pooled core share is the baseline; the
   per-export table shows the spread.
3. Record the pooled share and counts under `baseline` in the target file
   and in the baseline log of `assets/post_readout_template.md`.
4. Delete the raw exports; keep the counts.
5. When a new post is judged, add it to the window and drop the oldest.

```bash
python3 tools/linkedin/linkedin-engagement-analytics/scripts/engager_segmenter.py \
  --input tools/linkedin/linkedin-engagement-analytics/assets/sample_engagers_earlier_post.json \
          tools/linkedin/linkedin-engagement-analytics/assets/sample_engagers.csv \
  --target tools/linkedin/linkedin-engagement-analytics/assets/sample_target_audience.json \
  --format json
```

### Workflow 3 — Tune the classification, then write the readout

1. If coverage is low, test the headlines that are typical of the user's
   sector one at a time and extend the patterns
   (`references/segmentation-method.md` §11).
2. Re-run earlier exports so both sides of any comparison use the same rules.
3. Fill in `assets/post_readout_template.md`. Verify that no cell describes a
   single person and that the wording of the verdict matches where the
   baseline sits relative to the interval.
4. Optionally use `--fail-on-miss` as a quality gate in a content review:
   it exits 1 only when the sample is adequate and the core share is below
   the goal (or the baseline if no goal is set).

```bash
python3 tools/linkedin/linkedin-engagement-analytics/scripts/segment_rules.py \
  --classify "Head of Developer Experience at Example Energy"

python3 tools/linkedin/linkedin-engagement-analytics/scripts/engager_segmenter.py \
  --input tools/linkedin/linkedin-engagement-analytics/assets/sample_engagers.csv \
  --target tools/linkedin/linkedin-engagement-analytics/assets/sample_target_audience.json \
  --min-sample 40 --fail-on-miss
```

## Decision frameworks

### Reading the verdict

| Where your baseline or goal sits | Say | Do |
|----------------------------------|-----|-----|
| Below the whole interval | [RECOMMENDED] "Above our baseline" | Note the subject and framing; repeat once before concluding |
| Inside the interval | [RECOMMENDED] "In line with our baseline" | Report no change, in either direction |
| Above the whole interval | [RECOMMENDED] "Below our baseline" | Look at the adjacent and off groups to see who came instead |
| Sample under the minimum | "Too few to judge" | Describe counts; pool with other posts on the subject |
| No baseline or goal | "First baseline point" | Record it; judge nothing yet |

### What the mix is telling you

| Pattern | Likely reading | Next post |
|---------|----------------|-----------|
| High volume, low core share, many off | The subject is broad; it travelled beyond the intended reader | Narrow the subject to a problem only the target has |
| Large adjacent group: right function, lower seniority | Practitioners found it useful | Decide whether they are in fact the audience; they often forward upward |
| Large adjacent group: right seniority, other functions | It read as general leadership content | Add the specifics of your field |
| Internal share above a third | The post mostly reached colleagues | Fewer company announcements; more that stands alone for an outsider |
| Core share higher among commenters than reaction-only | The target had something to say | [EXPERIMENTAL] Try ending on a question for that reader and compare over several posts |
| Many sales and recruiting titles | Vendors treat the comment section as a lead source | Expect it; exclude nothing, but do not count it as reach |

### What to compare with

| Comparison | Verdict |
|------------|---------|
| This post against your own trailing baseline | [PROVEN] The only comparison that controls for your audience, sector and account size |
| This post against a goal you set from your baseline | [RECOMMENDED] |
| Subject A against subject B, several posts each | [RECOMMENDED] |
| Your figures against published industry benchmarks | No. Different accounts, sectors and definitions; not comparable |
| One colleague's figures against another's | No. Audience differences swamp everything else |

### What may be done with an export

| Request | Answer |
|---------|--------|
| Segment the audience and compare with a target | Yes |
| Count engagers from named organisations | Yes, as a count |
| List the directors who reacted | No. Per-person output is outside this skill |
| Look up the people with unclear headlines | No. No enrichment |
| Draft messages to the engagers | No. Different purpose from the one the data serves here |
| Analyse a competitor's post | No. Own posts only |

## Anti-Patterns

### Counting reactions as reach to the target
**Mistake:** A post with the highest reaction count of the quarter is declared the model for future posts.
**Why it happens:** The count is on the post, costs nothing to read, and bigger feels better.
**Instead:** Segment the engagers. In the sample export an eighth of engagers are colleagues and about a quarter of the classified outsiders are off target; the figure that matters is the core share and its interval, read against the author's own baseline.

### Writing the target after reading the list
**Mistake:** The author looks through who engaged, then defines the target audience as roughly those people.
**Why it happens:** The target file is filled in at analysis time, when the names are already on screen.
**Instead:** Write the target when the post is drafted, or at the latest before the export is opened. Record the intent in one sentence. A target that cannot be missed measures nothing.

### Turning the export into a prospect list
**Mistake:** The spreadsheet gains columns for "fit score", "contacted" and "notes", and gets shared with sales.
**Why it happens:** The names are right there, each one looks like an opportunity, and the step from analysis to outreach feels small.
**Instead:** Keep the purpose to audience analysis. The scripts print no names for this reason. Answer people who comment or message, as anyone would; do not build a file on people who clicked a reaction. `references/data-handling.md` §3 sets the line.

### Enriching to fix low coverage
**Mistake:** Half the headlines are slogans, so someone looks each person up to fill in their role and company.
**Why it happens:** Low coverage looks like a data-quality problem with an obvious manual fix.
**Instead:** Report coverage as it is. Extend the patterns for recurring titles, add a company column if the source already has one, and otherwise accept that the mix describes the classifiable part.

### Reporting noise as a trend
**Mistake:** "Core share rose from 21% to 28%" goes into a monthly update on the strength of one post with thirty-five engagers.
**Why it happens:** Two numbers invite a subtraction, and a rise is welcome news.
**Instead:** Read the interval. If the baseline sits inside it, the correct statement is "in line with our baseline". Wait for a second post in the same direction, or pool posts on the subject.

### Borrowing a benchmark
**Mistake:** The readout says the post was "above the industry average engagement rate".
**Why it happens:** A sponsor asks whether the result is good, and a published figure offers an easy answer.
**Instead:** Compare with the author's own trailing history, and say so. Published figures blend accounts unlike yours and rarely define their terms; this skill ships none.

## Files

Tools overview and reference documentation for this skill:

| File | Purpose |
|------|---------|
| `scripts/engager_segmenter.py` | Reads one or more CSV or JSON exports, merges duplicates, sets aside colleagues, segments by seniority, function and company, and judges core share against the user's goal and baseline with a Wilson interval; aggregate output only; `--fail-on-miss` turns it into a gate |
| `scripts/segment_rules.py` | Ordered seniority and function patterns, headline splitting, the fit rule, target validation and the interval calculation; `--list-rules` prints the patterns, `--classify` tests one headline |
| `references/metrics-layers.md` | The four measurement layers, what an export can and cannot show, definitions and formulas, building a trailing baseline, reading intervals, small samples |
| `references/segmentation-method.md` | Export sources and format, cleaning, headline parsing, bands and functions, writing a target, fit levels, extending patterns, known weaknesses |
| `references/data-handling.md` | Purpose limits, minimisation, local storage, segments-not-dossiers, no enrichment, retention, sharing, untrusted text, rules for an agent |
| `assets/sample_engagers.csv` | Invented export of 58 rows with duplicates, colleagues, slogans and a blank headline |
| `assets/sample_engagers_earlier_post.json` | Smaller invented export in JSON form, for pooling into a baseline |
| `assets/sample_target_audience.json` | Target audience, own-company names, goal and baseline for the sample |
| `assets/target_audience_template.json` | Blank target audience file |
| `assets/post_readout_template.md` | One-page readout and baseline log that identifies no one |
