# Metrics Layers

Which numbers answer which question, what an engager export can and cannot
tell you, and how to judge a post against your own history. This file gives no
industry benchmark figures. Published engagement benchmarks mix account sizes,
sectors and formats that are not yours, and claims about how the feed ranks
content cannot be verified from outside. The only comparison this skill
endorses is with your own trailing posts.

## Contents

1. Four layers, four questions
2. What an engager export contains
3. What it cannot tell you
4. Definitions used by the segmenter
5. Why audience fit and not volume
6. Building a trailing baseline
7. Reading a result with an interval
8. Small samples
9. Comparing posts fairly
10. What to put in a readout
11. Review checklist

## 1. Four layers, four questions

| Layer | Question | Where the numbers come from | Decision it informs |
|-------|----------|-----------------------------|---------------------|
| Post reach | How many people saw it? | The product's own post analytics (impressions, views) | Format and timing experiments |
| Post response | How many acted, and how? | Counts of reactions, comments and reposts | What subjects earn a response |
| Audience fit | Were the people who acted the people it was for? | An export of who reacted and commented, segmented | Whether the subject and framing reach the intended reader |
| Outcome | Did anything follow? | Your own log of messages, meetings, applications | Whether to keep investing |

This skill works on the third layer. It is the layer most people skip, because
the first two are shown on the post and the third needs work.

Keep the layers apart in any report. A post can do well on response and badly
on fit, and that combination is the one worth knowing about.

## 2. What an engager export contains

A list of people who reacted to or commented on one post, each with the short
professional headline shown beside their name, sometimes a company, and for
commenters the comment text. That is all the segmenter needs:

| Field | Used for |
|-------|----------|
| Headline | Seniority band, function, and company when written as "Title at Company" |
| Company (optional) | Company grouping, own-company exclusion, named-account matching |
| Engagement type | Splitting commenters from people who only reacted |
| Name | Merging duplicate rows only; never printed |
| Comment text | Marking the row as a comment; the text is not analysed |

## 3. What it cannot tell you

Be explicit about these limits in every readout.

- **Not reach.** The export lists people who acted. Most people who see a
  post do nothing visible. A healthy mix among engagers does not prove the
  same mix among viewers.
- **Not intent.** A reaction from a director at a target company is a
  reaction. It is not interest in buying, and the readout must not present it
  as a lead.
- **Not accuracy.** Headlines are self-written. Some are slogans, some are
  out of date, some name a role the person no longer holds.
- **Not completeness.** The product may not show every reaction, and a
  manual export may stop early. Record how the export was produced.
- **Not causation.** A better mix on one post may be the subject, the day,
  one well-connected commenter, or chance.

## 4. Definitions used by the segmenter

| Term | Definition |
|------|------------|
| Engager | One person who reacted or commented, counted once per post. A person who did both is counted as a commenter |
| Internal | An engager whose company matches `own_companies`. Reported, then excluded from the fit calculation |
| External | Every other engager |
| Classified | An external engager whose headline yielded a seniority band or a function |
| Unclassified | An external engager whose headline yielded neither. Counted, not guessed |
| Core | Classified engager whose seniority matches the target and whose function or title keyword matches the target |
| Adjacent | Exactly one of those two conditions held |
| Off | Neither held |
| Core share | Core divided by classified external engagers |
| Coverage | Classified divided by external engagers |
| Named-account engagers | External engagers whose company is in the target's company list |

Formulas:

```
core share      = core / classified
coverage        = classified / external
internal share  = internal / all engagers
```

The denominator for core share is **classified** engagers, not all engagers.
Putting unclassified people in the denominator silently treats them as off
target, which is a guess. Coverage is reported beside the share so the reader
can see how much of the audience the share describes.

## 5. Why audience fit and not volume

A raw count rewards whatever travels. Posts about general career feelings
collect reactions from everyone; a post about a narrow professional problem
collects fewer, from the people who have that problem. If the goal is to be
known by a particular kind of reader, the second post may be the better one,
and the count will say the opposite.

Core share corrects for that. It asks one question of every post: of the
people who responded and whose role we could read, what proportion were the
ones this was written for?

Read it alongside volume, not instead of it. A core share of four in five on
five engagers is not a success; neither is one in twenty on five hundred.

## 6. Building a trailing baseline

A baseline is your own recent normal. Build it once, then roll it forward.

1. Choose the window: the last five to eight posts of the kind you want to
   judge, excluding obvious one-offs (a job announcement, a viral outlier).
2. Produce an export for each, the same way each time.
3. Write the target audience file as it would have been written **before**
   those posts went out. Do not tune the target to flatter the history.
4. Run the segmenter with all exports in one command. The pooled core share
   is the baseline.
5. Record it in the target file under `baseline`: the share, the number of
   posts and the number of classified engagers behind it.
6. Roll forward: when a new post is judged, add it to the window and drop the
   oldest. Rebuild the pooled figure every few posts.

Pooling counts each engagement once per post. A regular reader who engages
with every post counts each time, which is what you want: the baseline
describes the audience your posts typically draw, weighted by how often they
show up. The segmenter also reports how many people appear in more than one
export, as a count only.

If different kinds of post have different targets (hiring posts versus
product posts), keep a baseline for each. A single blended baseline describes
neither.

## 7. Reading a result with an interval

A share from forty people is an estimate. The segmenter prints a 95% Wilson
interval around the core share: a range of values consistent with what was
observed. Use it like this.

| Where the reference sits | What to say |
|--------------------------|-------------|
| Baseline below the whole interval | "Above our baseline." The difference is larger than the noise for a sample this size |
| Baseline inside the interval | "In line with our baseline." Do not report the difference as a change, in either direction |
| Baseline above the whole interval | "Below our baseline." |

The same three readings apply to a goal you set yourself (`goal_core_share`).
A goal is your own number: the share you decided in advance would count as
reaching the intended audience. There is no correct value to borrow; start
from your baseline and set the goal a little above it.

The interval treats engagers as independent observations. They are not
entirely: one prominent commenter brings their colleagues. Treat the interval
as optimistic, and treat "within" as the common, honest answer.

## 8. Small samples

- Below the minimum sample (thirty classified external engagers by default;
  change it with `--min-sample` or in the target file), the segmenter still
  prints the mix but says a verdict does not count. Thirty is a working
  convention for this tool, not a property of the platform.
- With a small sample, describe: "eleven of twenty-four were core". Do not
  convert to a percentage in the headline of a readout.
- Pool posts on the same subject before concluding anything about the subject.
- One post never establishes a trend. Two in the same direction is the
  earliest point at which to change what you write.

## 9. Comparing posts fairly

| Comparison | Fair when | Unfair when |
|------------|-----------|-------------|
| Post against baseline | Same author, same target, similar format | The target was rewritten after seeing the result |
| Subject A against subject B | Each has several posts pooled | One post each |
| Commenters against reaction-only | Enough commenters to mean something | Six comments, four from colleagues |
| This quarter against last | Same export method, same target file | The classification patterns were edited in between without re-running the old exports |
| One author against another | Almost never | Audiences differ in size and make-up for reasons unrelated to the posts |

When the patterns or the target change, re-run the old exports so both sides
of a comparison use the same rules.

## 10. What to put in a readout

One page, in this order (`assets/post_readout_template.md` has the layout):

1. The post, its intended reader, and the target as written beforehand.
2. Volume: engagers, internal share, coverage.
3. Fit: core, adjacent and off counts; core share with its interval.
4. Against the baseline and the goal, in the three-way wording of section 7.
5. The largest segments by seniority and function.
6. What surprised you, as a hypothesis for the next post.
7. Limits: how the export was made, sample size, anything unusual that week.

Leave out names, individual headlines, and any list of people to contact.
The readout describes an audience.

## 11. Review checklist

Validate a readout before sharing it.

- [ ] Target audience written before the export was read
- [ ] Internal engagers reported and excluded from fit
- [ ] Coverage stated next to the core share
- [ ] Interval shown, and the wording matches where the reference sits
- [ ] Sample size checked against the minimum
- [ ] Compared only with the author's own baseline
- [ ] No benchmark figure from outside the team's own history
- [ ] No individual identified
- [ ] Limits section filled in
