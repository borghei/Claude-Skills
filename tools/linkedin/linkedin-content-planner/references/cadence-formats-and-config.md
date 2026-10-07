# Cadence, Formats and Config Reference

How often to post, in what form, how to make room for conversation, and the
full field reference for the plan config.

**A note on platform claims.** A great deal of confident advice circulates
about the best day, the best hour, the ideal length and which format the feed
favours. Most of it cannot be verified from outside, and whatever was true
changes without notice. This document therefore states planning heuristics and
labels them as such. Where it mentions a platform mechanic, treat it as current
as of writing and verify it in the product and against your own results.

## Contents

1. Choosing a cadence
2. Choosing posting days
3. Conversation days
4. Format mix and production capacity
5. Skip dates and gaps
6. Weekly versus monthly planning
7. Config field reference
8. Limits reference
9. Output reference
10. Troubleshooting

## 1. Choosing a cadence

Cadence is limited by three supplies, and the plan should be set to the
smallest of them.

| Supply | Question to ask | Sign it is the constraint |
|--------|-----------------|---------------------------|
| Material | How many ready story bank entries exist per pillar? | CP-012 flags; slots get improvised |
| Time | How many hours a week are really available for writing? | Posts slip to the evening before |
| Attention afterwards | Can the author be around to answer replies on the day? | Comments sit unanswered |

Heuristic starting points:

| Situation | Posts per week | Why |
|-----------|----------------|-----|
| First four weeks ever | 2 | The habit is the goal; each post teaches something about the next |
| Solo, established | 3 | Leaves two working days with no post, for conversation and for living |
| With production help | 4 to 5 | Only if the bank holds at least a month of entries |
| Above 5 | Not by default | The builder warns (CP-004). Raise `max_posts_per_week` if you have evidence it works for you |

The single most useful question: *what will you still be doing in week ten?*
Plan that number. Increase it after four weeks of hitting it without strain.

A missed slot costs more than an absent one. A plan of two that is kept reads
as steady; a plan of five that delivers two reads as someone who stopped.

## 2. Choosing posting days

There is no universally correct day. Choose on these grounds, in this order:

1. **When the author can be present afterwards.** A post is the start of a
   conversation. Pick days when there is time later the same day to answer.
2. **When the intended readers are plausibly at work and looking.** For most
   professional audiences that suggests working days in the readers' time
   zone. This is a reasonable assumption, not a measured fact; check your own
   numbers after a month.
3. **Spacing.** Leave at least one non-posting day between posts where the
   cadence allows, so each has room and conversation days fit between.

Keep the days fixed for a whole plan period. Consistency lets you compare
weeks. Change one day at a time and only between periods.

Time of day is not part of the config. Decide it by when the author is free to
reply for the following hour or two, and keep it steady.

## 3. Conversation days

A conversation day is a day with no post, reserved for reading and commenting
on other people's work. The config lists them under `conversation_weekdays`
and the plan prints them as conversation blocks.

Why they are in the plan at all:

- Commenting is how people outside your existing audience first see your name.
- It is where you find out what your readers are arguing about, which feeds
  the `peers` pillar and sharpens the others.
- Without a reserved day it is the first thing dropped in a busy week.

How to use the block (heuristic):

| Step | Guide |
|------|-------|
| Keep a short list of people whose posts you want to read | A dozen or so: peers, a few people ahead of you, a few likely readers or customers |
| Read first, then comment where you can add a case, a number or a disagreement | A comment that only agrees adds nothing to the thread |
| Stop at a fixed time | Half an hour is a workable default; open-ended sessions get abandoned |

If a posting weekday and a conversation weekday coincide, the post wins and no
block is printed for that day. The builder warns (CP-014) when no conversation
weekday is configured.

What to write in comments, and how to handle replies to your own posts, are
outside this skill.

## 4. Format mix and production capacity

### Declaring formats

List the formats you actually make, each with a share, and mark the ones that
need production time:

```json
"formats": [
  {"name": "text", "share": 50},
  {"name": "document", "share": 30, "produced": true},
  {"name": "video", "share": 20, "produced": true}
]
```

Names are free text. If `formats` is omitted the plan is all `text`.

### Choosing a mix

| Format | Cost to make | Good for | Watch out for |
|--------|--------------|----------|---------------|
| Text | Low | Episodes, opinions, anything where the voice matters | Walls of unbroken prose |
| Single image | Low to medium | One chart, one photo of the real thing, one annotated screenshot | Stock imagery; it signals nothing happened |
| Multi-page document | High | Methods, checklists, step-by-step cases | Slides with one slogan each |
| Short video | Medium to high | Demonstrations, a person explaining at a whiteboard | Reading a text post aloud to camera |
| Poll or question | Low | Finding out what readers think before writing about it | Using it as a shortcut to activity |

Format availability, size limits and how each is displayed change over time;
confirm in the product before committing a month to a format you have not used
recently.

A text-heavy mix is the right default for one person. Add a produced format
only when there is a specific post that needs it: a method with steps, a
before-and-after, a thing that must be shown.

### Capacity

`max_produced_per_week` caps how many produced-format posts land in one week.
The builder respects it while placing formats and substitutes an unproduced
format when the cap is reached. If that leaves fewer produced posts than the
mix asked for, CP-008 reports the shortfall. If a pillar allows only produced
formats, the builder must exceed capacity and CP-008 reports the week.

Set capacity from hours, not ambition. One produced post a week is realistic
for most people working alone.

## 5. Skip dates and gaps

List dates when nothing should go out under `skip_dates`: holidays, travel, a
company announcement that should stand alone, a day of bad news in the
industry. Skipped posting days are removed before quotas are calculated, so
the remaining slots still honour the shares. CP-011 reports how many were
removed; CP-015 warns if a whole week ends up empty.

A deliberate gap is fine. Say nothing about it. Posts that apologise for
absence or announce a return are about the author's schedule, which is not a
pillar.

## 6. Weekly versus monthly planning

| Plan length | Use when | Limits |
|-------------|----------|--------|
| 1 week | Trying a cadence; founders in a fast-moving period | Shares cannot be honoured in so few slots; expect CP-005 and CP-010 |
| 2 weeks | Founders; anyone around a launch | Good balance of structure and flexibility |
| 4 weeks | The default for most people | Angles for weeks three and four should stay pencilled |
| Up to 13 weeks | Checking whether a bank can sustain a cadence | Treat it as a supply forecast, not a schedule |

Whatever the length, fix the angle only for the coming week. Later slots keep
their pillar, format and ask, and get their angle when the week arrives.

## 7. Config field reference

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `owner` | string | no | Printed in the plan header |
| `start_date` | `YYYY-MM-DD` | yes | First day of the plan. A Monday keeps week numbers aligned with calendar weeks |
| `weeks` | integer 1 to 13 | no (default 1) | Plan length |
| `posting_weekdays` | array of `mon`..`sun` | yes | Days a post goes out |
| `conversation_weekdays` | array of `mon`..`sun` | no | Days reserved for commenting |
| `skip_dates` | array of `YYYY-MM-DD` | no | Dates with no post and no block |
| `pillars` | array of pillar objects | yes, unless `pillar_set` | See below |
| `pillar_set` | `general` or `founder` | no | Use a built-in set when `pillars` is absent |
| `formats` | array of format objects | no (default all text) | See section 4 |
| `limits` | object | no | Overrides for the defaults in section 8 |

### Pillar object

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `name` | string | yes | Unique. Must match the story bank's pillar name to bind entries |
| `share` | number above 0 | yes | Percentage of the plan. All shares sum to 100 |
| `ask` | string | no (default `reply`) | The reader ask: `reply`, `keep`, `pass-on`, `contact`, or your own word |
| `formats` | array of format names | no (default all) | Formats this pillar may use |
| `promotional` | boolean | no | Subject to `max_promotional_per_week` |

### Format object

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `name` | string | yes | Unique |
| `share` | number above 0 | yes | Percentage of the plan. All shares sum to 100 |
| `produced` | boolean | no | Counts against `max_produced_per_week` |

## 8. Limits reference

Every limit is a house default that can be overridden. None is a platform rule.

| Limit | Default | Controls | Flag |
|-------|---------|----------|------|
| `max_posts_per_week` | 5 | Warn when a week has more posts | CP-004 |
| `max_pillar_share` | 50 | Largest share of the plan one pillar may take, in percent | CP-002 |
| `max_promotional_per_week` | 1 | Promotional posts allowed per week | CP-003 |
| `max_produced_per_week` | 1 | Produced-format posts allowed per week | CP-008 |
| `max_ask_share` | 60 | Largest share of the plan one ask may take, in percent | CP-009 |
| `share_tolerance` | 15 | Allowed gap in points between target and planned share | CP-010 |

Run `plan_rules.py --list-rules` for the full flag catalogue.

## 9. Output reference

Text output has three parts: the calendar by week, the pillar and format mix,
and the flags sorted by severity. JSON output (`--format json`) carries the
same information:

| Key | Holds |
|-----|-------|
| `slots` | One object per post: `date`, `weekday`, `week`, `pillar`, `format`, `ask`, `promotional`, `entry_id`, `entry_title` |
| `conversation_days` | One object per reserved day |
| `pillar_mix` | Target share, planned share and post count per pillar |
| `format_mix` | Post count per format |
| `flags` | `id`, `severity`, `where`, `title`, `evidence`, `action` |
| `counts` | Number of flags per severity |

The JSON is suitable for pasting into a spreadsheet or a task tool by hand.
The skill itself sends it nowhere.

## 10. Troubleshooting

| Message | Cause | Fix |
|---------|-------|-----|
| `'pillars' shares sum to N, not 100` | Shares do not add up | Adjust them; the builder will not normalise |
| `contains unknown weekday(s)` | A day is misspelt | Use `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun` |
| `the config produces no posting slots` | Every posting day is skipped, or no days set | Check `posting_weekdays` and `skip_dates` |
| `pillar 'x' allows formats [...]` | A pillar lists a format not declared under `formats` | Add the format or correct the name |
| `is not a story bank` | The file passed to `--story-bank` has no `entries` array | Pass the bank file, not the plan config |
| Every slot says `no source entry` with a bank attached | Pillar names differ between plan and bank | Make them identical, including hyphens and case |
