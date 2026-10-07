# Segmentation Method

How an export becomes segments: the file format, how headlines are parsed,
how fit is decided, and where the method is weak. Read this before editing
the patterns in `scripts/segment_rules.py`.

## Contents

1. Producing an export
2. File format
3. Cleaning: blanks and duplicates
4. Parsing a headline
5. Seniority bands
6. Functions
7. Writing the target audience
8. Fit: core, adjacent, off
9. Internal engagers and named accounts
10. Unclassified headlines
11. Extending the patterns
12. Known weaknesses
13. Method checklist

## 1. Producing an export

This skill starts from a file the user already has. It does not collect data.

Acceptable sources:

- the engagement list the product shows the author for their own post, copied
  by hand into a spreadsheet;
- an export from an analytics or scheduling tool the user's organisation
  already licenses and is permitted to use for this purpose;
- for a company page, the page administrators' own analytics.

Not acceptable: automated collection that breaches the platform's terms,
exports of other people's posts gathered to study their audiences, and any
file whose origin the user cannot explain. If the user has no export, the
answer is to make one by hand from their own post, not to find a way around.

Record, for every export, the post, the date it was taken and the method. An
export taken an hour after posting and one taken a week later describe
different audiences.

## 2. File format

CSV (UTF-8, with a header row) or JSON (an array of objects, or an object
with an `engagers` array). Column names are matched case-insensitively and
several aliases are accepted.

| Standard field | Accepted column names | Required | Notes |
|----------------|-----------------------|----------|-------|
| `headline` | headline, title, job_title, occupation, subtitle | Yes | The professional headline as shown beside the name |
| `name` | name, full_name, member, person | No | Used only to merge duplicate rows |
| `company` | company, organisation, organization, employer | No | Overrides any company found in the headline |
| `engagement` | engagement, type, action, interaction | No | Any value containing "comment" is a comment; everything else is a reaction |
| `comment` | comment, comment_text, text | No | Non-empty text marks the row as a comment; the content is not analysed |

A minimal file:

```
name,headline,company,engagement
Example Person,Director of Engineering,Example Freight,reaction
Another Person,Staff SRE at Example Bank,,comment
```

Columns the tool does not know are ignored. Remove them anyway before saving
the file (profile links, locations, connection degree, photographs); see
`data-handling.md`.

## 3. Cleaning: blanks and duplicates

- Rows with an empty headline are skipped and counted in the output.
- A person who both reacted and commented appears twice in most exports. Rows
  with the same name and headline are merged, and the comment wins.
- Without a name column no merging is possible, and people who did both are
  counted twice. The effect is to overweight commenters slightly.
- Two different people with the same name and the same headline would be
  merged. This is rare enough to accept.

## 4. Parsing a headline

A headline is free text. The parser does three things in order.

1. **Split off the company.** If a company column is present it is used. If
   not, the text after the last " at " or " @ " is taken as the company, up to
   the next separator. "Head of Platform at Example Retail | Speaker" yields
   the company "Example Retail".
2. **Find the seniority band** by testing the title text against an ordered
   list of patterns. The first match wins.
3. **Find the function** the same way, with its own ordered list.

Test any headline from the command line:

```bash
python3 scripts/segment_rules.py --classify "VP Platform Engineering at Example Co"
```

Only the title part is tested, so a company called "Data Harbour" does not
make its accountant a data person.

## 5. Seniority bands

| Band | Typical cues | Notes |
|------|--------------|-------|
| `founder_owner` | founder, co-founder, owner | Tested before executive, so "Founder & CEO" is a founder |
| `vp` | VP, SVP, vice president | Tested before executive, so "Vice President" is not read as "President" |
| `executive` | chief, CEO, CTO, president, managing director, general manager | "Partner" counts only when it is the whole title |
| `director` | director, head of | |
| `manager_lead` | manager, lead, supervisor | "Lead generation" is excluded |
| `early_career` | student, intern, trainee, graduate | |
| `individual_contributor` | engineer, analyst, designer, consultant, specialist and similar | Also assigned when a function is found and no seniority cue is present |
| `unknown` | none of the above | |

Bands describe a title, not a person's influence. A staff engineer at a large
company may matter more to your goal than a director at a small one. If that
is your audience, express it with `title_keywords`, not by redefining bands.

Assistants to senior people are tested first and placed with individual
contributors, so "Executive Assistant to the CEO" is not counted as a chief
executive.

## 6. Functions

Order matters because titles overlap. The list runs from specific to general:
people, data, engineering, design, marketing, product, sales, customer
success, finance, legal, operations, consulting, education, general
management.

Consequences worth knowing:

- "Technical Recruiter" is people, not engineering.
- "Data Engineer" is data, not engineering. If your target is engineering
  broadly, list both functions.
- "Product Marketing Manager" is marketing.
- "Founder" and "CEO" with no other cue fall to general management.
- A headline that is a slogan ("Helping teams ship faster") has no function.

Print the full patterns with `--list-rules`.

## 7. Writing the target audience

Write the target **before** reading the export. A target written afterwards
will describe whoever turned up.

| Key | Meaning | Guidance |
|-----|---------|----------|
| `seniority` | Bands that count | List every band you would be glad to reach, not only the ideal one |
| `functions` | Functions that count | Use the names from `--list-rules` |
| `title_keywords` | Words in the title that count regardless of function | For niches the function list is too coarse for: "platform", "procurement", "clinical" |
| `companies` | Named organisations you hoped to reach | Optional; reported as a count only |

An empty list leaves that dimension unconstrained. A target with seniority
only means "anyone at these levels". A target with nothing is rejected.

Keep the target narrow enough to be wrong. If nine in ten working adults
would qualify, the core share will always look good and tell you nothing.

Record the intent in one sentence in `post.intent`. It is not used in the
calculation; it stops the target drifting between posts.

## 8. Fit: core, adjacent, off

Two conditions are tested for each classified external engager.

- **Seniority condition:** the band is in the target's list (or the list is
  empty).
- **Role condition:** the function is in the target's list, or a title
  keyword appears in the title (or both lists are empty).

| Seniority | Role | Fit |
|-----------|------|-----|
| Met | Met | Core |
| Met | Not met | Adjacent |
| Not met | Met | Adjacent |
| Not met | Not met | Off |

Adjacent is worth reading closely. A large adjacent group of the right
function at a lower level usually means the post is reaching practitioners,
who may be exactly who forwards it to the target. A large adjacent group of
the right level in the wrong function suggests the subject is general
leadership, not your subject.

## 9. Internal engagers and named accounts

**Internal.** Colleagues respond to colleagues. On a small account they can
be most of the list. Put every name your employer goes by in `own_companies`;
matching ignores case, punctuation and common legal suffixes. Internal
engagers are counted, reported as a share and removed before fit is
calculated. When the internal share is high the readout says so, because the
post mostly reached people who already work with you.

Internal matching needs a company. An employee whose headline is a slogan
with no company cannot be recognised and will sit among the external or
unclassified engagers.

**Named accounts.** If `target.companies` is set, the readout reports how many
external engagers came from those organisations. It is a count. It does not
list who they were, and it is not a list of leads.

Company names appear in the output only when two or more engagers share the
company. A company with a single engager, combined with a seniority band,
would identify a person.

## 10. Unclassified headlines

Some headlines carry no role: slogans, "Open to work", a string of nouns. The
segmenter counts these separately and leaves them out of the fit calculation.
It does not guess.

Watch coverage. When more than two in five external headlines are
unclassified, the readout warns that the mix describes a minority. Options,
in order of preference:

1. Add a company column if the source has one; it does not classify people
   but it improves the internal split.
2. Look at the titles that failed with `--classify` and add patterns for
   recurring roles in your sector.
3. Accept the low coverage and say so.

Do not look people up elsewhere to fill in their roles. See
`data-handling.md`.

## 11. Extending the patterns

The patterns live in two ordered lists in `scripts/segment_rules.py`. To add
a sector's vocabulary:

1. Collect ten to twenty real headlines from your exports that classified
   wrongly or not at all.
2. Decide the band or function each should have.
3. Add the narrowest pattern that catches them. Prefer two-word phrases to
   single common words; "people" and "support" as bare words match slogans.
4. Place the pattern above any more general rule it should beat.
5. Run `--classify` on the collected headlines and on a handful that already
   worked, to check nothing else moved.
6. Re-run earlier exports so the baseline uses the same rules.

## 12. Known weaknesses

- English-language titles only. Other languages need their own patterns.
- Abbreviations collide. Two-letter cues are kept to those that are rarely
  ordinary words.
- Portfolio headlines ("Founder | Investor | Adviser") take the first
  matching band, which may not be the person's main role.
- Seniority is not comparable across company sizes.
- The split on " at " fails on headlines such as "Looking at new
  opportunities", which produce a nonsense company. A company column avoids
  this.
- People who engage are not a random sample of people who saw the post.

None of these is fatal for a comparison of one author's posts against that
author's own baseline, because the errors are roughly the same on both sides.
They matter a great deal if the output is read as a census.

## 13. Method checklist

- [ ] Export source and date recorded; the method is one the user is permitted to use
- [ ] Unneeded columns removed before analysis
- [ ] Target written before the export was read
- [ ] `own_companies` lists every form of the employer's name
- [ ] Coverage checked; low coverage stated in the readout
- [ ] Pattern changes tested with `--classify` and old exports re-run
- [ ] Company names shown only where two or more engagers share them
