---
name: linkedin-employee-advocacy
description: >
  Designs and runs an employee advocacy programme: who posts what and how
  often, review rules, and what is never scripted. Use when getting a team
  posting, writing an advocacy policy, or fixing a programme that has stalled.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: tools
  domain: linkedin
  updated: 2026-10-07
  tags: [linkedin, employee-advocacy, governance, team-cadence, social-policy]
---

# LinkedIn Employee Advocacy

Advocacy programmes usually fail the same way. Marketing writes a post, sends
it to thirty people with "please share", and eight of them paste it on the
same morning. Colleagues like each other's copies for a week. A manager starts
asking who has posted. By the second month the willing have gone quiet and the
unwilling are resentful, and the company has taught its own staff that their
personal accounts are a distribution list.

The cause is treating employees' accounts as a channel the company owns. This
skill designs the programme the other way round: people opt in individually,
write in their own words about subjects they know first-hand, at a cadence
sized to the time they have actually agreed to, with review limited to a short
list of risk triggers. It works **offline**. It plans from a roster file the
user supplies; it does not post, schedule, log in to anything, or collect data
from the network.

**Scope boundary.** This skill designs and governs the team programme. It does
**not** write anyone's posts or comments (`linkedin-post-writer`,
`linkedin-comment-writer`), clean up drafting-tool phrasing
(`linkedin-humanizer`), or test opening lines (`linkedin-hook-analyzer`). It
does **not** manage replies or follow threads (`linkedin-reply-manager`,
`linkedin-thread-tracker`), build an individual's content calendar or recycle
material (`linkedin-content-planner`, `linkedin-content-repurposer`), or
interview a person to find their stories (`linkedin-story-interviewer`).
Individual profiles are `linkedin-profile-optimizer`; working out who a post
reached is `linkedin-engagement-analytics`. None of those is required to use
this one.

## When to use this skill

- A leader wants "the team posting" and there is no charter, roster or cadence yet
- A programme exists but output is identical, sporadic or has stopped
- HR, legal or a works council asks what the rules are and none are written down
- People are being nominated by managers instead of asked
- A review queue has become the reason nothing gets published
- The sponsor wants to know whether the programme is working, and the only numbers are a leaderboard

## Inputs the skill expects

- The programme goal: pipeline, hiring, reputation or category
- A roster of people who have been asked: role family, seniority, how often they post today, hours a week they have agreed to, their own topics, and whether they said yes
- Honest answers to the governance questions in `assets/roster_template.json`
- Who the owner and the checkers are, and how much time the checkers have
- Any regulated or restricted roles on the team
- The countries the team works in, for the legal review of disclosure and employment wording

## Clarify First

Before producing a plan or charter, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Whether each person has opted in themselves** — the planner schedules only people with a recorded yes; a manager's list is not consent and changes the roster entirely
- [ ] **The programme goal** — decides which role families the plan depends on and what the outcome log counts
- [ ] **Hours each person has really agreed to** — every cadence is capped by it; an optimistic figure produces a plan nobody keeps
- [ ] **Regulated roles and jurisdictions** — decides who needs a pre-publication check and which sections of the charter need counsel

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Quick start: plan a roster

1. Copy `assets/roster_template.json`. Add one entry per person who has been
   asked, and set `opted_in` to true only for those who said yes.
2. Answer every governance key. An unanswered key is reported as a gap.
3. Run the planner and read the findings before the matrix; blockers come
   first.
4. The agent reports the weekly matrix, the topic coverage map, each blocker
   with its fix, and the assumptions used (time model, review share).

```bash
python3 tools/linkedin/linkedin-employee-advocacy/scripts/advocacy_planner.py \
  --input tools/linkedin/linkedin-employee-advocacy/assets/sample_roster.json
```

### Workflow 2 — Write the charter and clear the gate

1. Fill in `assets/advocacy_charter_template.md` using
   `references/governance-and-consent.md`: consent, never-scripted list,
   disclosure, triggers and checkers, incident pause, leavers.
2. Send sections 4, 5 and 8 for legal review in each jurisdiction.
3. Update the roster's governance answers to match what the charter now says.
4. Re-run the planner as a quality gate. It must pass with no blockers before
   anyone is invited to post.
5. Share each member their own row and record their acceptance in charter
   section 12.

```bash
python3 tools/linkedin/linkedin-employee-advocacy/scripts/advocacy_planner.py \
  --input tools/linkedin/linkedin-employee-advocacy/assets/sample_roster.json \
  --fail-on blocker

python3 tools/linkedin/linkedin-employee-advocacy/scripts/advocacy_rules.py --list-rules
```

### Workflow 3 — Four-week review and recalibration

1. Collect plan versus actual at team level and each member's honest estimate
   of minutes spent. Do not collect individual reach figures unless offered.
2. Calibrate the time model with the team median
   (`references/programme-design.md` §10) and re-run for the current week.
3. Resolve crowded topics by vantage point and agree changes with the members
   concerned.
4. Update the baseline sheet and the outcome log
   (`references/measuring-the-programme.md` §3 and §5).
5. Verify that nobody has been moved up a stage without asking for it.

```bash
python3 tools/linkedin/linkedin-employee-advocacy/scripts/advocacy_planner.py \
  --input tools/linkedin/linkedin-employee-advocacy/assets/sample_roster.json \
  --week 8 --minutes-per-post 55 --format json
```

## Decision frameworks

### What the company may supply

| Supplied by the company | Verdict | Reason |
|-------------------------|---------|--------|
| Facts, figures and names cleared for public use | [PROVEN] Yes | Removes the "am I allowed to say this" delay, which is the real blocker |
| Links, images, event details | [PROVEN] Yes | Source material, not speech |
| A list of possible angles by role | [RECOMMENDED] Yes | Prompts thinking without writing it |
| A conversation or interview that becomes the person's own post | [RECOMMENDED] Yes | The words and opinions remain theirs |
| A finished post to paste | No | Duplicate copy is recognisable and it puts words in people's mouths |
| Opinions, praise, testimonials, personal stories | Never | These are only true when the person originates them |
| A rota for liking and commenting on colleagues' posts | Never | Manufactured engagement misleads readers |

### Review design

| Choice | Recommendation | Reason |
|--------|----------------|--------|
| Review everything or review by trigger | [RECOMMENDED] By trigger | Most posts carry no risk; a universal queue slows all of them and teaches people their voice needs permission |
| What a checker may change | [RECOMMENDED] Facts and timing only | Style edits push people into the company voice, then out of the programme |
| Missed review deadline | [RECOMMENDED] Escalate to the owner; silence is not approval | A post that tripped a trigger should not publish because someone was busy |
| Restricted roles | [PROVEN] Named specialist check before anything about the business | The exposure is real and specific to the role |
| Automated pre-screening of drafts for trigger words | [EXPERIMENTAL] Only as a prompt to the author | Helpful as a reminder; harmful if it becomes a gate people cannot argue with |

### Cadence decisions

| Situation | Recommendation |
|-----------|----------------|
| New to posting | [RECOMMENDED] Start with comments only, then a post a fortnight |
| Engineer or designer with thirty minutes a week | [RECOMMENDED] Plan as comment-only or a post a fortnight, on purpose |
| Someone wants to post daily | Check it fits the job; raise agreed hours before raising the plan |
| Launch week | Supply more material; do not coordinate timing or raise targets |
| One person produces most of the team's posts | Spread the load and protect that person's time; do not present the programme as broader than it is |

### Blocker or warning

| Finding class | Severity | Why |
|---------------|----------|-----|
| Not voluntary, tied to pay or review, company holds logins | Blocker | Removes the employee's free choice or control of their own account |
| No disclosure guidance, verbatim shared copy, engagement rota | Blocker | Misleads readers |
| No trigger list, restricted role without a check | Blocker | Leaves the company's real risks uncaught |
| No pause rule, no leaver rule, slow review, no owner | Warning | The programme can start, but will fail at the first hard week |
| Crowded topic, thin time budget, review overload | Warning | Sustainability problems the plan can fix |

## Anti-Patterns

### The "please share" email
**Mistake:** Marketing sends a finished post to the team and asks everyone to publish it.
**Why it happens:** It is the fastest way to produce visible activity, and it guarantees the message is on-brand.
**Instead:** Send the facts, the link and one line of possible angles per role. Anyone who wants to mention it writes their own post or reshares with a comment of their own. Rule GV-05 blocks verbatim copy for this reason.

### Enrolment by org chart
**Mistake:** The roster is "everyone in sales and marketing", announced at an all-hands.
**Why it happens:** Asking people one at a time is slow, and a large roster looks like commitment.
**Instead:** Invite individually, share the charter first, and record each yes. Start with the five who want to. The planner excludes anyone without `opted_in: true` and reports them (RS-01) so the gap is visible.

### The leaderboard
**Mistake:** A weekly ranking of who posted most or reached furthest is shared in a team channel.
**Why it happens:** It feels like recognition, and it is the easiest thing to build from the available numbers.
**Instead:** Report team totals and thank people for specific posts. Ranking individuals makes participation a performance matter, rewards whoever already had the largest audience, and reliably produces padding and pasted copy.

### Reviewing voice instead of risk
**Mistake:** Every post goes through a queue, and comes back with a new opening and brand vocabulary.
**Why it happens:** The reviewer is a writer and wants to help, and nobody defined what the review is for.
**Instead:** Review only posts that trip a written trigger, and limit the checker to one question about a fact or a date (`references/governance-and-consent.md` §6 and §7).

### Uniform cadence
**Mistake:** Everyone is asked for three posts a week.
**Why it happens:** One number is easy to communicate and easy to track.
**Instead:** Size each row to the person's role, habit and agreed hours. A founder and an engineer with thirty minutes do not share a cadence, and a comment-only member is a full member.

### Asking staff to defend the company
**Mistake:** During criticism or an incident, employees are encouraged to post supportive messages or reply to critics.
**Why it happens:** It looks like a show of strength, and people offer.
**Instead:** Call the pause in the charter, give people one agreed line that points to the official statement, and leave it there. Staged support is recognisable and extends the story.

## Files

Tools overview and reference documentation for this skill:

| File | Purpose |
|------|---------|
| `scripts/advocacy_planner.py` | Builds a per-person weekly cadence matrix from a roster, capped by each person's time; maps topic coverage, estimates review load, and reports governance and roster findings; `--fail-on` turns it into a gate |
| `scripts/advocacy_rules.py` | Cadence starting points by role family, seniority and stage factors, the time model, goal emphasis, and the governance rule catalogue; `--list-rules` prints them |
| `references/programme-design.md` | Design principles, who to invite, how cadence is sized, stages, topic allocation, the weekly note, launch sequence, calibration |
| `references/governance-and-consent.md` | Consent, account ownership, the never-scripted list, disclosure, review by trigger, escalation, restricted roles, incident pause, leavers, audit |
| `references/measuring-the-programme.md` | Three measurement levels, what not to measure, building a baseline from your own history, honest attribution, health indicators, review rhythm |
| `assets/sample_roster.json` | Invented nine-person roster with deliberate governance and roster gaps |
| `assets/roster_template.json` | Blank roster with every governance key and member field |
| `assets/advocacy_charter_template.md` | Fill-in charter covering consent, never-scripted list, disclosure, triggers, pause, leavers and agreed plans |
