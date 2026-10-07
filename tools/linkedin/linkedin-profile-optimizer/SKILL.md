---
name: linkedin-profile-optimizer
description: >
  Audits and rewrites a LinkedIn profile from pasted text: headline, About,
  experience, skills, Featured, banner and photo. Use when reviewing a profile,
  fixing a headline or About, or preparing a profile before posting more.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: tools
  domain: linkedin
  updated: 2026-10-07
  tags: [linkedin, profile, headline, personal-branding, career]
---

# LinkedIn Profile Optimizer

Most profiles are a CV pasted into a different box. The headline is a job title
and an employer, the About is a third-person paragraph of adjectives, the
experience entries list duties, Featured is empty and the banner is the
default. None of that is wrong, exactly. It simply gives a visitor nothing to
act on, and the headline, which travels beside every comment the person
writes, says nothing to the people who will never open the profile.

This skill treats the profile as one argument aimed at one reader. It fixes
the goal first, inventories the evidence, scores each section against a rule
catalogue, and rewrites in priority order so the hour available goes to the
sections that matter for that goal. It works **offline**: it reads profile
text the user pastes and answers the user gives about the visuals. It does not
fetch profiles, log in, post, or call any service.

**Scope boundary.** This skill covers the standing profile only. It does
**not** write feed posts (`linkedin-post-writer`), strip machine-sounding
phrasing from drafts (`linkedin-humanizer`), or test opening lines
(`linkedin-hook-analyzer`). It does **not** write comments or handle replies
and threads (`linkedin-comment-writer`, `linkedin-reply-manager`,
`linkedin-thread-tracker`), plan or recycle content (`linkedin-content-planner`,
`linkedin-content-repurposer`), or draw stories out of a person
(`linkedin-story-interviewer`). Rolling profile standards out across a team is
`linkedin-employee-advocacy`; working out who a post reached is
`linkedin-engagement-analytics`. Each of those stands alone, as this one does.

## When to use this skill

- Someone asks for a profile review, a headline rewrite or a better About
- A person is about to post regularly and the profile those posts lead to is CV-shaped
- A job search, a move to independent work or a new role changes what the profile is for
- A founder or hiring manager wants the profile to attract candidates or customers
- A profile was rewritten once and needs a quarterly check
- A draft headline or About exists and needs a second opinion before it goes live

## Inputs the skill expects

- The profile **as text**: headline, About, each experience entry, skills (and which are in the top slots), Featured items, recommendations, public URL. A link is not enough; nothing here opens it
- Answers about the photo and banner, given while looking at the live profile on a phone (`references/featured-and-visuals.md` §8 lists the questions)
- The goal: clients, job search, authority or hiring
- Two to four search terms the target reader would type, and how that reader describes themselves
- Evidence the person can stand behind and is allowed to publish

## Clarify First

Before auditing or rewriting, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The single goal** (clients, job search, authority, hiring) — sets the section weights, the Featured slots and the closing action; a profile aimed at two goals argues for neither
- [ ] **Who the reader is and what they would search for** — without it the headline and skills checks have nothing to test against, and the rewrite defaults to generic wording
- [ ] **What evidence exists and what may be published** — decides whether the rewrite can use figures, must fall back to scope, or has to stop and collect proof first
- [ ] **Whether the pasted text is the whole profile** — never score a section that was not supplied, and never infer content from a URL or a name

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Quick start: audit a profile

1. Copy `assets/profile_template.json` and paste the profile text into it.
   Fill in `goal`, `target_keywords` and `audience_terms`; the keyword and
   audience checks are skipped when those are empty.
2. Answer the photo and banner fields by looking at the live profile on a
   phone. The tool cannot see images.
3. Run the auditor. Read the scorecard for where the weight is, then the fix
   list from the top.
4. The agent reports the scorecard, the five highest-priority fixes with their
   evidence, and any section it could not assess because the text was missing.

```bash
python3 tools/linkedin/linkedin-profile-optimizer/scripts/profile_auditor.py \
  --input tools/linkedin/linkedin-profile-optimizer/assets/sample_profile.json
```

### Workflow 2 — Rewrite in priority order

1. Complete sections 1 and 2 of `assets/profile_rewrite_worksheet.md` (goal and
   evidence inventory) before writing a sentence.
2. Headline: draft the blocks, assemble three candidates, run the three tests
   in `references/headline-and-about.md` §4, choose one.
3. About: write the five moves, then read only the preview on a phone.
4. Experience: convert each duty line with the four questions in
   `references/experience-skills-and-credibility.md` §3. Verify that every
   figure is accurate and cleared for publication.
5. Skills, Featured, visuals and credibility: work the remaining worksheet
   sections in the order the fix list ranks them.
6. Deliver before and after for each rewritten section, with the assumptions
   and any evidence still to be confirmed listed at the top.

```bash
python3 tools/linkedin/linkedin-profile-optimizer/scripts/profile_auditor.py \
  --input tools/linkedin/linkedin-profile-optimizer/assets/sample_profile.json \
  --goal job_search --top 8
```

### Workflow 3 — Re-audit and hold the line

1. Put the rewritten text into a second JSON file and run the auditor again.
2. Compare scores section by section. For every finding left open on purpose,
   record the reason in worksheet section 10.
3. Use `--fail-under` as a quality gate when a team wants a floor before
   profiles are linked from a campaign.
4. Validate the platform limits in the product on the day of publishing and
   pass any change with `--headline-limit` or `--about-preview`.
5. Set a review date: quarterly, and after any change of role or goal.

```bash
python3 tools/linkedin/linkedin-profile-optimizer/scripts/profile_auditor.py \
  --input tools/linkedin/linkedin-profile-optimizer/assets/sample_profile_rewritten.json \
  --fail-under 75 --format json

python3 tools/linkedin/linkedin-profile-optimizer/scripts/profile_rules.py --list-rules
```

## Decision frameworks

### Where the hour goes, by goal

The auditor weights sections by goal. These are editorial weights, not
platform facts; change them in `scripts/profile_rules.py` if your situation
differs.

| Goal | Rewrite first | Then | Leave for last | Why |
|------|---------------|------|----------------|-----|
| Clients | [RECOMMENDED] Headline, About, Featured | Visuals | Skills | A prospect decides from the top of the page; Featured carries the proof and the door |
| Job search | [RECOMMENDED] Experience, then headline and skills | About | Featured | Recruiters and hiring managers read the work history and search by role terms |
| Authority | [RECOMMENDED] Featured, headline, About | Credibility | Skills | The reader wants to know what you have said and where to follow it |
| Hiring | [RECOMMENDED] About, headline | Featured, experience | Skills | Candidates read the manager's profile to judge the team |

### Headline decisions

| Situation | Recommendation | Reason |
|-----------|----------------|--------|
| Headline is a title and an employer | [PROVEN] Keep the title as the anchor and add audience plus one proof block | The title is what people search; alone it gives no reason to click |
| Tempted to replace the title with a benefit statement | [RECOMMENDED] Do not drop the anchor | A headline nobody can classify or find is worse than a plain one |
| Unsure whether to fill the character limit | [RECOMMENDED] Use what the blocks need, front-load the first line | Most surfaces truncate; the opening words are the headline for most readers |
| Considering emoji, capitals or decorative separators | [RECOMMENDED] One separator style, no capitals for emphasis | Decoration costs characters and reads as noise at thumbnail size |
| Want to signal availability | [EXPERIMENTAL] Put it in the About's closing action, test the headline without it | The product has its own availability signals; a headline spent on status says nothing about the work |

### Evidence decisions

| Evidence available | What the rewrite uses |
|--------------------|-----------------------|
| Figures that are yours and public | The figures, with the base they were measured on |
| Figures that belong to an employer or client | Scope and before-and-after in words, until permission is given |
| No figures | Scope, frequency, firsts, named artefacts, adoption |
| Nothing the person can point to yet | Stop. Collect evidence before rewriting; adjectives are not a substitute |

### Reading the score

| Overall score | Meaning | Action |
|---------------|---------|--------|
| Under 50 | Several sections are in their default state | Workflow 2 in full |
| 50 to 79 | Structure is there; proof or visuals are thin | Work the top eight fixes |
| 80 and over | No obvious rule failures | Human read for tone and truth; the tool cannot judge either |

A clean report means no rule fired. It does not mean the profile is good. The
sample rewrite scores 100 and still needs a person to confirm every figure in
it.

## Anti-Patterns

### Rewriting before choosing a goal
**Mistake:** The headline is polished to attract clients while the About and Featured still argue for a job search, because each section was rewritten on its own.
**Why it happens:** The request arrives as "fix my headline", and a headline can be improved in isolation in five minutes.
**Instead:** Fix the goal and the reader first (worksheet section 1). Every later choice, including the section weights the auditor applies, follows from that. If the person has two goals, pick the one with a deadline.

### Deleting the job title to make room for a promise
**Mistake:** The headline becomes "Helping ambitious teams unlock sustainable growth" and the role disappears.
**Why it happens:** Common advice says to lead with value, and the title feels like the dull part.
**Instead:** Keep a searchable anchor and add to it. The title-only headline fails because it stops too early, not because it names the job. Rule HL-02 flags the bare title; the fix is more blocks, not fewer.

### Manufacturing numbers
**Mistake:** Duty lines are converted to results by attaching plausible percentages nobody measured.
**Why it happens:** "Add metrics" is the best-known profile advice, and a rewrite with figures looks finished.
**Instead:** Inventory real evidence before writing. Where no figure exists or the figure is not the person's to publish, use scope, frequency or a named artefact (`references/experience-skills-and-credibility.md` §4). Never invent or round up a figure on someone's behalf; a former colleague can check it in seconds.

### Scoring what was not shown
**Mistake:** The audit rates the banner, the photo or a missing section from a profile link or from assumptions.
**Why it happens:** A complete-looking scorecard feels more helpful than one with gaps.
**Instead:** Score only supplied text and the user's own answers about the visuals. Say which sections were not assessed and what is needed to assess them.

### Treating the score as the deliverable
**Mistake:** The profile is edited until every rule passes, including keyword terms forced into the headline, and the result reads like a checklist.
**Why it happens:** A number that goes up is satisfying, and the rules are easy to satisfy mechanically.
**Instead:** Use the fix list to find problems and the references to solve them. Leave a finding open when fixing it would make the profile worse, and record why. The rules detect absence; they cannot detect quality.

### Appending a keyword list
**Mistake:** The About ends with a "Specialties" line of twenty comma-separated terms.
**Why it happens:** It is the fastest way to make the keyword check pass, and the effect on search cannot be seen from outside.
**Instead:** Use two to four terms inside ordinary sentences, and put the full vocabulary in the skills section where a list is expected.

## Files

Tools overview and reference documentation for this skill:

| File | Purpose |
|------|---------|
| `scripts/profile_auditor.py` | Scores a profile JSON across seven sections, weights them by goal, and prints fixes in priority order; `--fail-under` turns it into a gate |
| `scripts/profile_rules.py` | Rule catalogue, goal weights, platform limits, filler and duty-language vocabularies, the visuals check and shared text helpers; `--list-rules` prints them |
| `references/headline-and-about.md` | Headline block model, patterns by goal, three pre-publish tests, the five-move About, preview writing, a worked example |
| `references/experience-skills-and-credibility.md` | Duty-to-result conversion, what to do without numbers, publication checks, skills selection, recommendation requests, public URL |
| `references/featured-and-visuals.md` | Featured slot model by goal, titles and thumbnails, rotation triggers, banner and photo guidance, the self-assessment questions |
| `assets/sample_profile.json` | Invented CV-shaped profile that triggers most rules |
| `assets/sample_profile_rewritten.json` | The same invented profile after a rewrite, for the re-audit workflow |
| `assets/profile_template.json` | Blank profile to fill in with pasted text and visual answers |
| `assets/profile_rewrite_worksheet.md` | Fill-in worksheet: goal, evidence inventory, section rewrites, re-audit record |
