# Copy: Facts, Voice and Tells

Generic copy is a symptom of missing input. With no facts, a writer (person or model) fills a
template with lines that fit any business. The fix is facts and decisions, not synonyms: a hype word
swapped for a calmer word is the next tell. Write all the copy before the layout, from a fact sheet,
in a voice chosen for this client.

## 1. The fact sheet

Fill this from the brief, the client's files or their current site, word for word where possible.
An empty field stays empty and its section shrinks or goes; the report lists what the client must
supply.

| Field | Feeds |
|---|---|
| What it is, in one plain sentence with no adjective | h1, sub-line |
| Who it is for, and who should look elsewhere | h1 or sub-line, one FAQ answer |
| What buyers do today instead | the pain line, a comparison |
| The true difference, with its proof | the claims worth a heading |
| Customer words (reviews, emails, sales calls) | headings, the pain line |
| Numbers, each with its source | sentences; a facts row only of given facts |
| Odd true details (a habit, an object, a constraint) | the texture that would otherwise be invented |
| One limit (closed Mondays, Mac only, no lift) | one admission per page |
| The offer: price, trial, booking terms, the one action | buttons, the close |

[PROVEN] Nothing is invented: no reviews, ratings, customer counts, logos, awards, testimonials or
figures that the brief does not give. A product with no price says "Price on request" or shows none.

## 2. The voice card

Pick one register per client and write it on the plan, never on the page. The default voice of
generated copy (warm, wry, modest, a little literary, ending each paragraph on a dry twist) is out
unless the client asks for it, because every generated page now sounds like that.

| Register | Sounds like | Suits |
|---|---|---|
| Technical-dry | Exact nouns, numbers with units, no adjectives that cannot be measured | Developer tools, infrastructure, B2B software |
| Plain-service | Short sentences, the customer's own words, what happens next | Clinics, trades, repair shops, public services |
| Editorial | Longer sentences, one strong opinion per section, named sources | Studios, publishers, consultancies |
| Local-direct | Street names, opening hours, prices, the owner's habits | Cafes, bakeries, guesthouses, shops |
| Confident-retail | Product first, one benefit per line, the price near the claim | Physical products, direct-to-consumer brands |
| Formal-assured | Complete sentences, no contractions, process and guarantees | Law, finance, healthcare providers |

A voice card has four lines: the register, two "X, not Y" pairs that fence it ("exact, not cold"),
who "we" and "you" are, and a sentence-length habit ("mostly 8 to 16 words; one long one per
section").

### Shape the page from the reader's questions

A reader asks, roughly in order: what is this, is it for me, why believe you, how does it work, what
does it cost, what if it goes wrong, what do I do now. How much they already know sets the opening:

| The reader... | Open with |
|---|---|
| does not know they have the problem | a moment they recognise, in the sub-line |
| knows the problem | the problem in the customer's own words, then the product |
| is comparing options | the mechanism: what this does differently |
| already knows the client | the product, the offer, the price, the action |

A section exists only when the fact sheet has true material for it. Five full sections beat eight
padded ones. When the brief has an organising idea (the menu as the page, a timetable, a founder's
letter), let it break the template once.

### Voice checks before drafting

- **Copy the client's own voice first:** a writing sample, the old site or the brief's wording
  overrides the register table (never the rules in section 3).
- **The nine-trades test:** imagine the voice card on nine businesses in nine other trades. If it
  fits any of them, push it further toward this client.
- **Voice holds, tone moves:** the hero and story carry the most voice; prices, the FAQ, booking and
  forms go plain, because readers there are anxious.
- When this session already built another page, pick the register least like that one.

## 3. Rules every page keeps

1. **The h1 names the category,** plus the buyer or the place for an unknown brand, in 2 to 8
   words: "Payroll app for restaurant teams", "Bike repair workshop on Kastanienallee".
2. **The first screen holds one hard fact:** a price, a number, a place or a date.
3. **Every heading has a noun** that names a thing: the product, a part of it, prices, rooms, hours,
   questions. No bare commands ("Get started"), no question headlines, no lines that only make sense
   after reading the page.
4. **Buttons are a verb plus what the visitor gets,** 1 to 5 words: "Book a table", "Start a free
   trial", "See the price list". Never "Learn more", "Read more", "Discover", "Explore", "Click here"
   or "Submit".
5. **Few actions, one wording each.** At most two in the hero. The main action reads the same in the
   nav, the hero and the close.

Plain versions, when a line is vague: put the category noun first, then one count, place or price,
and drop the figure of speech. "Every shift, sorted" becomes "Shift planning for restaurant teams".

## 4. The tells

Severity: **ban** means one hit fails; **budget** means fine once or twice, a tic beyond that;
**warn** means worth a look, often fine in context. The ids are the ones `copy_lint.py` prints; the
lists live in `assets/copy_tells.json` and can be extended per client.

### Older tells (still common, easy to catch)

| id | Severity | Example | Fix |
|---|---|---|---|
| `hype-word` | ban | seamless, cutting-edge, unlock, empower, robust, world-class | Replace with the fact it stands for: the setup steps, the failure case, the figure |
| `stock-phrase` | ban | "In today's fast-paced world", "Say goodbye to", "at your fingertips" | Delete; start with the category noun |
| `residue` | ban | lorem ipsum, `{{token}}`, "[Company Name]", "Certainly!", `**bold**` on a rendered page | Write the real words or leave the element out |
| `vague-cta` | ban | Learn more, Explore, Click here | Verb plus object |
| `reveal` | warn | "The result?", "Here's how", "this section shows" | Make the point directly; the page never talks about itself |
| `puffery` | warn | "serves as", "in the heart of", "where design meets data", ecosystem, journey | Plain "is" and "has"; name the street or the thing |
| `exclamation` | budget 0 | "Join us today!" | A full stop. Excitement comes from the fact |
| `em-dash` | budget 2 | Three dashes in one paragraph | Comma, colon, brackets or a full stop where each is natural |
| `emoji` | budget 1 | Emoji as bullets or in buttons | Real icons, or nothing |

### Newer tells (they look like good copy, so they survive review)

| id | Severity | Example | Fix |
|---|---|---|---|
| `fragment-heading` | budget 1 | "Twelve rooms. Three ways to stay." on every section | Spend it once; give other headings a plain label or a claim |
| `contrast-frame` | budget 2 | "Freshness isn't a slogan here", "rather than", "instead of", "without the" | State the positive fact on its own; all forms count together |
| `virtue-word` | budget 2 | honest, genuinely, simply, thoughtful, passionate, dedicated | Show it with a fact or an admission |
| `ing-rider` | budget 1 | "..., ensuring a smooth start" | End the sentence at the claim |
| `proof-figure` | warn | 10,000+ teams, 3x faster, 99% satisfaction | Only the brief's figures, in a sentence, with unit and source |
| `default-cast` | warn | Acme, Nimbus, Zenith, Jane Doe, "Sarah J., CEO" | Names come from the brief; a coined brand is checked against the trade first |
| `footer-signoff` | warn | "Made with love in Brooklyn" | The footer holds the brand, the year, Privacy, Terms, credits |
| `stale-year` | warn | © 2023 on a page shipped in 2026 | The current year |
| `question-heading`, `h1-length` | warn | "Ready to grow?" as the h1; a 14-word h1 | Name the category in 2 to 8 words |

Tells the linter cannot count, found by reading aloud:

- **Invented specifics.** "Batch No. 047", "6:12 a.m. from Room 9": detail produced as decoration.
- **The strip of figures** under the hero: three numbers over one-word labels, none from the brief.
- **The section template:** eyebrow label, claim heading, short lede, three cards, in every section.
- **Perfect evenness:** every card the same length, every paragraph the same arc.
- **The name's metaphor run into the ground:** a brand called Forge that "forges" every section.
- **The origin template:** "In [year], [two first names] found [an old building]..."
- **The dry closer:** a deadpan quip ending most paragraphs.

### Device budgets counted by `copy_devices.py`

| id | Severity | Example | Fix |
|---|---|---|---|
| `number-pair` | budget 1 | "Four projects, four very different problems" | Say what the section holds; the claim goes in the line under it |
| `negation-run` | budget 1 | "No forms, no back-and-forth." | Keep one, and only when each item is a refusal the buyer can check |
| `colon-heading`, `run-on` | warn | "Our process: simple"; a grey half that runs on from the first | Name the thing; end the first sentence with a full stop before the muted span |
| `caps-label` | budget 1 | "OUR PROCESS" over every section | Sentence case |
| `stat-strip` | warn | 10,000+ / 3x / 99% over one-word labels | Each number in the sentence it proves, from the brief; a menu or price list is not a strip |
| `step-numbers` | warn | 01, 02, 03 on features that read in any order | Number only steps that happen in order |
| `eyebrows` | over 2 | a small label above every heading | One or two a page; a heading that names the thing needs none |
| `testimonials` | 3 or more | three polished quotes, each with a number and a punchline | Only quotes the brief gives, word for word, with name and role; none is normal |
| `coming-soon` | warn | "Online booking coming soon" with nothing in the brief | Only what the brief says is coming, with its date if given; otherwise leave it out |
| `response-time`, `since-year` | warn | "within 24 hours" here, "within one working day" there | One promise from the brief, the same words wherever it repeats |
| `apology-note` | ban | "Names and figures on this page are examples", "Representative image" | Real material, or leave the element out |
| `cast-brand` | ban | a page whose own name is Nimbus or Kestrel | The brand comes from the brief, or a coinage searched against the trade first |
| `even-rhythm`, `fragment-drumbeat` | warn | every sentence 9 words; a third of them fragments | Let length follow meaning; one sentence a section may run long |
| `shared-phrase` | warn | the same heading phrase on two pages of this session | Break the shared cadence; pass all pages in one run to see it |

## 5. Moves for each part of the page

- **Hero forms that keep the category:** category and buyer ("Payroll app for restaurant teams"),
  category and place ("Bakery on Mill Street"), category and a true, unexpected promise ("Tax return
  app that asks eleven questions"), category and scope ("Card payments for market stalls"), a narrow
  superlative the brief proves. Greetings, questions and enemies may take the sub-line, never the h1.
- **About and story:** start in a moment the brief gives (the day the oven arrived), not a thesis;
  values as behaviours with numbers ("we pay growers twice the market price"), never a list of
  adjectives; end in a modest present tense, then say how to reach them.
- **Features:** the mechanism in verb-led steps ("Forward the invoice. The app reads the total. It
  pays on the day you choose."); the outcome first, the feature as its proof; real values in examples.
- **Proof:** only what the brief gives, attributed in full; a rule instead of a claim ("every frame
  is brazed by the person who measured you"). None is fine.
- **The plain zone (prices, FAQ, booking):** facts only, perks priced, a risk reversal only when it
  is true, a limit admitted plainly ("Android comes next year; today it is iPhone only").
- **Microcopy:** write the form errors, the sent line, empty states, the 404 page and the newsletter
  confirmation in the register. A stock form error under a hand-tuned hero gives the page away.
  This is where a dry line is welcome.
- **Repeat the product's name** rather than cycling through "the platform, the tool, the solution".

## 6. Over-correction

Every ban breeds a substitute. Watch for these after a cleanup pass:

| Rule applied | Habit it breeds | Counter |
|---|---|---|
| No em dashes | Comma splices, or only full stops | Use colons and brackets where they are natural |
| No "not X but Y" | "rather than", "instead of", "without the" | The linter counts them together; state the positive |
| No hype words | Calm hype: quietly, steady, simply, thoughtfully | A fact in place of any adjective |
| Be specific | Invented numbers and anecdotes | The fact sheet, or a plainer line |
| Short punchy sentences | A drumbeat of fragments | One longer sentence per section |
| Add personality | A joke in every section | Humour goes in the microcopy, once |

## 7. Not tells

Leave these alone: correct grammar; plain "is" and "has"; a list of three when there are three
things; a superlative the brief can prove ("the only climbing gym in the district open at 6:00");
title case when it is the client's house style; one honest "no card needed" when it is true; a word
that is literal for the trade (a climbing harness, bespoke tailoring, a seamless knit). For a literal
use, pass `--allow <word>` to `copy_lint.py` and say why in the report.

## 8. The read-aloud check and the outside reads

After the linter is clean, read every line aloud as if to a customer at the counter. Ask of each
line: would a stranger know what is sold after five seconds? Is this line true of this client and
false of its nearest rival? If a rival could paste the line onto their own page, rewrite it.

Then three more reads:

1. **A rival's name:** put a rival's name, or the same trade in another town, into the h1, the
   sub-line and each heading. A line that still reads true says nothing about this client.
2. **As the client:** cut every sentence the owner would not say about their own business.
3. **A fresh reader:** when a subagent is available, hand it only the page text and ask what this is,
   who it is for, why this over the alternative, what it costs, what would make it hesitate, and
   which three lines sound like any other website. Fix what it finds. Never iterate to beat a
   detector; iterate toward facts.
