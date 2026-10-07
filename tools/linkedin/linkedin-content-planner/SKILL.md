---
name: linkedin-content-planner
description: >
  Builds a weekly or monthly LinkedIn publishing plan from content pillars, a
  posting cadence and a format mix, with a founder-oriented pillar set as an
  alternative to the general one. Use when planning a week, a month or a launch
  period of posts rather than drafting a single post.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: tools
  domain: linkedin
  updated: 2026-10-07
  tags: [linkedin, content-calendar, content-pillars, editorial-planning, founder-content]
---

# LinkedIn Content Planner

Posting without a plan produces a recognisable pattern: three posts in an
enthusiastic first week, all on the same subject, then silence, then a product
announcement to an audience that has stopped expecting anything. The individual
posts may be good. The sequence is not, because nobody decided in advance how
often each subject should come up, which posts need production time, or where
the material for week three would come from.

This skill makes those decisions once, on paper. The agent turns a small config
(pillars with target shares, posting days, a format mix, a few limits) into a
dated plan in which pillars and formats are spread evenly, each slot states the
one thing it asks of the reader, and every slot is either tied to a real piece
of material or visibly marked as lacking one. Imbalance is flagged before the
first post is written, when it is still cheap to fix.

**Offline only.** The skill produces a plan for a person to act on. It does not
post, schedule, read a feed, pull analytics or call any API. Inputs are a
config file and, optionally, a story bank file, both supplied by the user.

**Scope boundary.** This skill decides what goes on which date; it does not
write the posts. Drafting a slot is `linkedin-post-writer`; cleaning a draft's
phrasing is `linkedin-humanizer`; testing its opening line is
`linkedin-hook-analyzer`. Finding the material a slot needs is
`linkedin-story-interviewer`, which also owns the story bank format this skill
can optionally read. Adapting an existing talk or article into a slot is
`linkedin-content-repurposer`. The plan reserves conversation days but what to
say on them is `linkedin-comment-writer`, `linkedin-reply-manager` and
`linkedin-thread-tracker`. Profile copy is `linkedin-profile-optimizer`,
multi-person programmes are `linkedin-employee-advocacy`, and deciding from
past results what to change next month is `linkedin-engagement-analytics`.

## When to use this skill

- "Plan my week" or "what should I post this month"
- A person posts in bursts and wants a cadence they can keep for a quarter
- A launch, fundraise or hiring push is coming and needs to sit inside normal posting rather than replace it
- A founder is writing for investors, candidates and buyers at once and the feed has become all product
- A story bank exists and nobody has checked whether it can feed the intended cadence
- An existing calendar feels repetitive and needs an objective look at its mix

## Inputs the skill expects

- A start date and a length of one to thirteen weeks
- Posting weekdays, and the weekdays reserved for conversation on other people's posts
- Three to five pillars, each with a target share, the reader ask it usually carries, and the formats it suits
- A format mix with shares, marking which formats need production time
- Limits where the defaults do not fit: posts per week, pillar cap, promotional posts per week, produced posts per week
- Optional: dates to skip, and a story bank file whose pillar names match the plan's

## Clarify First

Before building the plan, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **General or founder pillar set** — a founder writing for investors, hires and buyers needs pillars keyed to those readers; the general set is keyed to subject matter. Choosing wrong produces a plan that is balanced on paper and aimed at nobody.
- [ ] **How many posts a week the person will still be making in week ten** — the plan is built on this number; an optimistic answer creates slots that go unfilled and a pattern of gaps.
- [ ] **How much production time exists per week** — carousels, video and designed images take hours that text does not; this caps the format mix regardless of preference.
- [ ] **Whether a story bank exists** — with one, slots are bound to entries and shortages show up as flags; without one, every slot is a topic with nothing behind it yet.

Stop rule: ask only the two or three that most change the plan. If the user says "just plan it", use the general set at three posts a week, text-heavy, and list those assumptions at the top of the plan.

## Workflows

Quick start: copy `assets/plan_config_template.json`, set the dates and
pillars, and run Workflow 1.

### Workflow 1 — Build a month plan from a config

1. Agree pillars and shares using `references/pillars-and-mix.md`. Shares must
   sum to 100; the builder refuses to guess otherwise.
2. Set posting and conversation weekdays, skip dates, and the format mix.
   Mark formats that need production with `"produced": true`.
3. Run the builder. Read the flags before the calendar.
4. Resolve every `error` flag by changing the config, not by hand-editing the
   output. Decide deliberately about each `warn`.
5. Copy the result into `assets/weekly_plan_template.md` and add a one-line
   angle per slot.

```bash
python3 tools/linkedin/linkedin-content-planner/scripts/plan_builder.py \
  --input tools/linkedin/linkedin-content-planner/assets/sample_plan_config.json
```

### Workflow 2 — Bind the plan to a story bank and find the shortfall

1. Check that the bank's pillar names match the plan's exactly.
2. Run the builder with `--story-bank`. Each slot takes the next ready entry
   filed under its pillar, unused entries first.
3. Read every CP-012 flag: those are slots with no material behind them.
4. For each short pillar, either lower its share or schedule an interview
   session before the plan starts. Do not leave the slot to be improvised.
5. Validate the final version with `--fail-on error` so a broken mix cannot
   be handed on.

```bash
python3 tools/linkedin/linkedin-content-planner/scripts/plan_builder.py \
  --input tools/linkedin/linkedin-content-planner/assets/sample_plan_config.json \
  --story-bank tools/linkedin/linkedin-content-planner/assets/sample_story_bank.json \
  --fail-on error
```

On the sample this exits 0 with four warnings: the bank cannot cover the
`offer` pillar at all, and the format mix asks for more produced posts than
one a week allows.

### Workflow 3 — Plan a founder fortnight

1. Read `references/founder-pillar-set.md` and confirm the three readers
   (investors, candidates, buyers) are the ones the founder actually wants.
2. Start from `assets/sample_founder_config.json` or set
   `"pillar_set": "founder"` in a config with no `pillars` key.
3. Build a two-week plan first. Founders' weeks change too fast for a month
   to survive contact.
4. For each slot pick an angle from the founder reference and name the real
   event behind it. A slot with no event is cut, not padded.

```bash
python3 tools/linkedin/linkedin-content-planner/scripts/plan_builder.py \
  --input tools/linkedin/linkedin-content-planner/assets/sample_founder_config.json \
  --format json
```

**Exit-code contract.** `0` plan built; `1` a flag reached the `--fail-on`
level; `2` the config or bank is missing, not JSON, or invalid (shares not
summing to 100, unknown weekday, bad date, no slots).

## Decision frameworks

### Which pillar set

| Situation | Set | Why |
|-----------|-----|-----|
| Employee, consultant, freelancer, job-seeker | [RECOMMENDED] General: craft, field-notes, peers, offer | Readers come for a subject; pillars keyed to subject keep it recognisable |
| Founder with a product in market | [RECOMMENDED] Founder: market-view, build-log, customer-desk, ledger | Three distinct readers decide the company's future; each needs a regular reason to keep reading |
| Founder before any product exists | [EXPERIMENTAL] Founder set with customer-desk replaced by a research pillar | There are no customers to report on yet; risk is a feed of opinions with no evidence |
| Anyone whose pillars already work | Keep them | A plan is for spreading pillars, not replacing ones that readers respond to |

### Cadence

All figures here are planning heuristics, not platform rules. Platform
behaviour changes; treat anything about reach as current as of writing and
verify it against your own results.

| Capacity | Cadence | Tag |
|----------|---------|-----|
| First month of posting | Two posts a week, two conversation days | [RECOMMENDED] Builds the habit before the volume |
| Established, writing alone | Three posts a week | [PROVEN] as a sustainable solo editorial rhythm; the limit is the supply of material, not the calendar |
| Has help with production | Four to five a week | [RECOMMENDED] only when a story bank can supply it |
| More than five a week | Not planned by default | [EXPERIMENTAL] The builder warns (CP-004); quality and material run out first |

### Reading the flags

| Flag level | Meaning | Action |
|------------|---------|--------|
| `error` | The plan breaks one of its own limits: a pillar over the cap, promotion stacked in a week | Change the config and rebuild |
| `warn` | A judgement call: runs of one pillar or format, an ask that dominates, slots without material | Decide and note the decision in the plan |
| `info` | Context: skip dates applied, no bank supplied | None |

### One ask per post

| Ask | The reader is invited to | Suits |
|-----|--------------------------|-------|
| `reply` | Answer, disagree, add their case | Episodes and opinions |
| `keep` | Save it for later use | Methods, checklists, worked examples |
| `pass-on` | Send it to a colleague or reshare | Credit to others, decisions with wider relevance |
| `contact` | Message or visit the profile | Offers, customer stories, hiring |

A plan in which one ask covers more than about three posts in five reads as
engineered; the builder raises CP-009.

## Anti-Patterns

### Planning topics instead of slots with material
**Mistake:** The calendar says "Thursday: leadership lessons" for six weeks.
**Why it happens:** A topic fills a cell and feels like a decision, and the material question can be postponed to the day of writing.
**Instead:** Bind slots to story bank entries with `--story-bank` and treat every CP-012 flag as work to do now. A slot with no entry is either an interview to schedule or a slot to remove.

### Letting the offer pillar grow during a launch
**Mistake:** Launch month arrives and four posts in five are about the product.
**Why it happens:** The launch is the most important thing happening to the author, so it feels like the most important thing to the reader.
**Instead:** Keep `max_promotional_per_week` at one and tell the launch through the other pillars: the build decision in craft or build-log, the customer problem in field-notes or customer-desk. The builder raises CP-003 as an error when promotion stacks.

### Planning a cadence for the best week
**Mistake:** Five posts a week, set on a quiet Sunday, abandoned by the third week.
**Why it happens:** The plan is written when energy is highest and nothing else is competing for the time.
**Instead:** Ask what the person will still be doing in week ten and plan that. Raise it after a month of hitting it. A steady two beats an abandoned five.

### Hitting the shares exactly in a single week
**Mistake:** Reworking a three-post week over and over because 35/30/20/15 cannot be reached.
**Why it happens:** The shares look like targets for every week, and a week is the unit people look at.
**Instead:** Shares are judged over the whole plan. Three slots cannot represent four pillars. The builder reports CP-010 only when the whole plan drifts beyond the tolerance, and CP-005 when a pillar gets nothing at all.

### Scheduling posts and no conversation
**Mistake:** Every working day has a post; no day is reserved for other people's.
**Why it happens:** Posts are visible output and commenting feels like a distraction from producing them.
**Instead:** Reserve conversation days in the config. A profile that only broadcasts is talking to a room it never listens to. The builder raises CP-014 when `conversation_weekdays` is empty.

### Treating heuristics as platform law
**Mistake:** Refusing to post on a Friday, or forcing every post into one format, because of a rule read somewhere.
**Why it happens:** Confident claims about what the feed rewards circulate widely and are hard to check.
**Instead:** Every limit in this skill is a labelled default that can be overridden under `limits`. Change one thing for a month and judge it against your own numbers.

## Files

Tools overview and reference documentation for this skill:

| File | Purpose |
|------|---------|
| `scripts/plan_builder.py` | Reads a plan config, lays posts onto dates with pillars and formats spread evenly, optionally binds slots to ready story bank entries, prints the calendar, the mix table and the flags; optional gate via `--fail-on` |
| `scripts/plan_rules.py` | Rule data and primitives behind the builder: default limits, the fifteen-flag catalogue, both built-in pillar sets, the largest-remainder and deficit allocation routines, and the plan checker; `--list-rules` prints them |
| `references/pillars-and-mix.md` | How to choose and word pillars, set shares, pair pillars with asks, and rebalance a plan that has drifted |
| `references/founder-pillar-set.md` | The reader-keyed founder pillar set, with angles per pillar, stage adjustments and launch-period handling |
| `references/cadence-formats-and-config.md` | Cadence and format guidance with platform caveats, conversation days, and the full config field reference |
| `assets/sample_plan_config.json` | Four-week general plan for a fictional payroll consultant; triggers capacity and skip-date flags |
| `assets/sample_founder_config.json` | Two-week founder plan for a fictional software founder |
| `assets/sample_story_bank.json` | Eight-entry bank matching the general sample, deliberately short on two pillars |
| `assets/plan_config_template.json` | Minimal valid config to copy and edit |
| `assets/weekly_plan_template.md` | Fill-in sheet for one week: slot, pillar, format, ask, source entry, angle, status |
