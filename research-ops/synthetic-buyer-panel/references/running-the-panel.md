# Running the Panel

Operational guide for the moderator: dealing cards, dispatching one buyer agent
per brief, collecting answers, re-running failures and producing the tally.
The moderator runs the process and never answers for a buyer.

## 1. Layout on disk

Keep a flat working folder per panel run, for example `panel-2026-11-08/`:

```
panel-2026-11-08/
├── profile.json        # the customer profile used
├── cards.json          # written by panel_deal.py
├── brief_B001.md ...   # one brief per buyer
└── answers/
    ├── B001.json ...   # one answer per buyer, written by that buyer's agent
```

Record the seed and the profile version in the readout. The same profile, size
and seed always deal the same cards, so any run can be reproduced.

## 2. Dealing

```bash
python3 scripts/panel_deal.py --profile profile.json --n 40 --seed 7 --out-dir panel-2026-11-08
```

If the deal tool reports a FAIL, nothing is dealt. Fix the profile; do not work
around the check by editing cards by hand.

## 3. Dispatching buyer agents

Each buyer is one isolated agent run with only its brief. Isolation matters:
an agent that can see the conversation, other briefs or other answers will be
anchored by them.

In an assistant that supports sub-agents, dispatch in waves of about ten, one
agent per brief, all in one message:

- Prompt: "Read `<folder>/brief_B001.md` and follow it exactly. Write your JSON
  answer to `<folder>/answers/B001.json` and nothing else."
- Wait for the whole wave before starting the next one.
- 40 buyers is four waves; 100 buyers is ten.

Before a large run, tell the user how many agent runs it will take and suggest
a 20-buyer first look. In permission-gated environments each answer file may
need approval; suggest a mode that allows file writes for the run.

In an assistant without sub-agents, run each brief in a fresh conversation and
save the answer by hand. Never answer several briefs in one conversation: the
answers converge.

## 4. Collecting and checking answers

Run the tally as soon as a wave lands; it reports invalid and missing answers:

```bash
python3 scripts/panel_tally.py --cards panel-2026-11-08/cards.json --answers panel-2026-11-08/answers/
```

When an agent prints its JSON in its reply instead of writing the file, save
that reply verbatim as the answer file. Do not edit it except to strip text
around the JSON object.

Re-run each invalid or missing buyer once with the same brief. A buyer that
fails twice stays missing and counts against coverage. Never write, complete or
"tidy" an answer for a buyer; the tally cannot tell moderator text from buyer
text, and one filled-in answer contaminates the whole readout.

## 5. Moderator checks before reading results

Use this checklist:

- [ ] Coverage at or above 90% (the tally fails below it)
- [ ] At least 20 valid answers
- [ ] No answer cites facts that are not in the pitch (spot-check five)
- [ ] Duplicate-reason share under 30%; if higher, contexts are too thin
- [ ] Buy rate under 60%; if higher, re-read the pitch for hype or leading lines

## 6. Comparing two variants

To test a change (a lower price, a delivery option, a different headline):

1. Keep the profile and seed fixed; change only the pitch lines.
2. Deal into a second folder; the cards are identical to the first run.
3. Run both panels and compare buy rate by segment and the pass-reason mix.
4. A change that moves the top pass reason is more informative than one that
   moves the overall rate by a few points.

## 7. Writing the readout

Fill `assets/panel-readout-template.md`:

1. Headline: buy and pass counts and the buy rate, labelled as a ceiling.
2. The segment and behaviour rows that differ most from the average.
3. Top three pass reasons with one example each, labelled as simulated.
4. The most repeated flips, mapped to an offer, channel or price change.
5. The price corridor as a range to test, not a price to charge.
6. One recommended real-world test, with what result would change the plan.

## 8. Cost and time

Each buyer is one short agent run. A 40-buyer panel in waves of ten usually
takes a few minutes of wall time. The expensive part is not the run but a wrong
profile, so time spent grounding the profile in real evidence is the best
investment in the whole process.
