# Review Order and Chart Choice

How to use the UX rule base in a review, and how to pick a chart from a data question.

## Review in severity order, then by product priority

Review a design or build in this order. Stop and fix critical findings before looking
at medium ones: polishing type scales on a screen keyboard users cannot reach wastes the
review.

| Pass | What | Rules |
|------|------|-------|
| 1 | Can everyone perceive and operate it? | Every `critical` rule: text contrast, text on fills, focus ring, colour-only meaning, icon names, input labels, flashing, touch size |
| 2 | The product type's priority categories | `high` and `medium` rules in the four categories listed for the product type (for example banking: trust, forms, accessibility, feedback) |
| 3 | Everything else that applies to the platform | Remaining `high`, then `medium` |
| 4 | Polish | `low` rules: tabular figures, all-caps, icon set consistency, halation |

The recommender's `ux_rules` list is passes 1 and 2, already filtered by platform. Use
`ux_rules_search.py --min-severity high --platform mobile` for pass 3.

### Automated versus manual

Rules with an `auto` value are tested by `design_spec_checker.py` against the token file:
contrast pairs, focus width, touch target, base size, line height, scale ratios, spacing
grid, radius count, family count, durations, reduced motion, dark mode presence and
halation. Everything else needs a person with the product open. A clean checker run
means the *tokens* are sound; it says nothing about whether a component uses them.

### Writing a finding

A finding a team can act on names four things: the rule id, the screen or component, the
measured value against the threshold, and the fix. "Muted text fails" is not a finding.
"A11Y-02, invoice list timestamps: #9CA3AF on #FFFFFF is 2.5:1, needs 4.5:1; use the
`muted_fg` token (#4B5563)" is.

## Choosing a chart

Start from the question the reader is asking, not from the data shape. The bundled
`charts.json` maps 22 questions to a chart, its alternatives, when it breaks, and the
accessible fallback. `ux_rules_search.py --domain charts --query "<question>"` finds the
entry.

**[PROVEN] Bars and lines answer most questions.** Compare categories with sorted bars;
show change over time with lines. Reach for anything else only when the question is about
share, spread, flow, place or relationship.

**[PROVEN] Pie and donut charts only for one share or at most five parts.** People
compare lengths far better than angles. A 100% stacked bar does the same job with less
error.

**[RECOMMENDED] Stat tiles carry a comparison.** A number without a period and a change
cannot be judged. "1,240 orders, up 4% vs last month" beats "1,240".

**[RECOMMENDED] Every chart has a text or table alternative.** Screen-reader users and
anyone checking an exact value need it. A summary sentence counts when the table would be
long.

**[EXPERIMENTAL] Sonified or haptic charts** for blind users are promising but tooling is
thin; ship the table first.

### Colour in charts

- Categorical: about six distinguishable hues at most; beyond that use direct labels or
  small multiples.
- Sequential (heatmaps, choropleths): one hue from light to dark, so it survives
  greyscale.
- Diverging (change, sentiment): two hues around a neutral midpoint that means something
  (zero, target, average).
- Never green/red as the only signal. Add sign, shape or a word.

### Volume limits

Each chart entry has a `max`. Past it the chart misleads more than it informs: a 20-line
chart is a texture, a 40-slice pie is a colour wheel. Switch to the listed alternative
or to a searchable table.
