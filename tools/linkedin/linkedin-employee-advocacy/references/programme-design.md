# Programme Design

How to size, staff and sequence an employee advocacy programme so that it is
still running in six months. The cadence numbers in this file and in
`scripts/advocacy_rules.py` are planning defaults. They are starting points to
be tuned against your own team's history, not industry statistics.

## Contents

1. What an advocacy programme is and is not
2. Five design principles
3. Who to invite
4. Cadence: how the planner sizes a week
5. Stages: entering by habit, not by calendar
6. Topics: one person, a few subjects, first-hand
7. What the company supplies each week
8. Launch sequence
9. Running it: events, absences, quiet members
10. Calibrating the time model
11. Design checklist

## 1. What an advocacy programme is and is not

An advocacy programme is an arrangement in which a company makes it easier for
employees who want to write publicly about their work to do so, on their own
accounts, in their own words.

It is not a distribution channel the company owns. The accounts belong to the
people. The audiences followed a person, not an employer. A programme that
forgets this produces the familiar result: eight identical posts on the same
morning, a week of awkward mutual likes, and silence by the second month.

The useful test for any design choice is: would this still be acceptable if
the employee described it accurately to their own followers? "My employer
gives me time and source material and I write what I think" passes. "My
employer writes these and I paste them" does not.

## 2. Five design principles

**Their account, their words.** The company may supply facts, links, images
and angles. It does not supply sentences to paste. The reason is practical as
well as ethical: readers recognise duplicated copy, and people stop posting
things that do not sound like them.

**Supply material, not scripts.** The hard part of posting is knowing what is
worth saying and whether you are allowed to say it. A weekly note that answers
both removes most of the friction. A script removes the person.

**Size to time, not ambition.** Every cadence is capped by the hours a person
has actually agreed to. A plan that needs three hours from someone with thirty
free minutes is a plan for guilt.

**Comments before posts.** Commenting on other people's posts is cheaper,
lower-stakes and teaches voice. New members start there. Some members should
stay there permanently, by choice.

**Measure the programme, not the people.** Report at team level. The moment
individuals are ranked, the programme becomes a performance obligation, and
the behaviour that follows (padding, pods, pasted copy) damages the thing
being measured.

## 3. Who to invite

Invite people who have first-hand knowledge an outside reader would value, and
who have shown some inclination to explain things. Seniority is not the test.

| Role family | What only they can say | Typical shape |
|-------------|------------------------|---------------|
| Founder | Why the company exists, what it got wrong, where it is going | Posts and comments; the highest sustainable cadence |
| Executive | How a function is run, decisions and their reasons | Occasional posts; often a restricted role needing a check |
| Marketing | Customer stories, what the market is saying | Posts and curation; often runs the programme |
| Sales | What buyers ask, what makes a purchase stall | Comment-led; a post when there is a real story |
| Customer success | What adoption looks like in practice | Short, concrete posts; strong on detail |
| People | What working here is like, how hiring works | Posts tied to real openings and real practices |
| Product, engineering, design | How things are built and why | Infrequent, substantial posts; time budget is the limit |

Match the invitations to the programme goal. A pipeline goal with no sales or
customer voice, or a hiring goal with no engineers, is mismatched; the planner
flags this as RS-08.

Ask individually, explain the charter, and accept "no" and "not now" without
follow-up. A person appears on the roster with `opted_in: true` only after
they have said yes. The planner excludes everyone else and reports them as
RS-01 so that a roster drawn up by a manager is not mistaken for consent.

## 4. Cadence: how the planner sizes a week

The planner builds each person's week in four steps.

1. **Start from the role family.** Each family has a steady-state weekly
   starting point for a senior member: original posts, comments on other
   people's posts, and reshares with a comment of their own.
2. **Scale by seniority.** Junior and mid-level members start lower. This is
   about how much standing material a person has, not their worth.
3. **Scale by stage** (see section 5).
4. **Cap by time.** The result is costed with the time model and trimmed until
   it fits the hours the person agreed to. Reshares are cut first, then posts
   in half steps, then comments.

A value of 0.5 posts means one post a fortnight. That is a legitimate steady
state for many roles, engineering especially.

Run `python3 scripts/advocacy_rules.py --list-rules` to see the current
tables. Edit them when your own history says otherwise; they are deliberately
in one file.

Two limits worth keeping whatever the tables say:

- **A ceiling.** Outside founders and people whose job is content, more than
  two original posts a week is usually taking time from the work that makes
  the posts worth reading.
- **A floor that is allowed to be zero.** Comment-only members are part of the
  programme. Do not push them to post to make a chart look fuller.

## 5. Stages: entering by habit, not by calendar

People join with different habits, so a single team-wide ramp either bores the
regular posters or overwhelms the new ones. The planner assigns a stage per
person from their prior habit and the weeks they have been in.

| Prior habit | Weeks 0 to 1 | Weeks 2 to 5 | Week 6 on |
|-------------|--------------|--------------|-----------|
| New (has rarely or never posted) | Listen | Starter | Steady |
| Occasional (posts a few times a year) | Starter | Starter until week 3, then steady | Steady |
| Regular (already posts most weeks) | Steady | Steady | Steady |

| Stage | What the person does | Why |
|-------|----------------------|-----|
| Listen | Comments only, at a reduced count | Finds their subjects and their voice with nothing at stake |
| Starter | A post a fortnight or half the steady rate, most of the comment habit | First posts without a weekly deadline |
| Steady | The full, time-capped cadence | Sustainable rhythm |

Set `weeks_in_programme` on a member who joined later than the rest; otherwise
the programme week is used. Hold someone at a stage longer if they ask. Nobody
is moved up without wanting to be.

## 6. Topics: one person, a few subjects, first-hand

Each member has two or three subjects they know from doing the work. Topics
are chosen by the person, with help, and are not assigned from a campaign
plan.

Good topics are narrow and experiential: "what breaks when a dashboard gets
its hundredth user", not "data". A useful prompt is: what do you explain to
new colleagues or customers every month?

**Crowding.** When three or more people hold the same topic, their posts
converge and readers who follow several of them see repetition. The planner
flags this as RS-02. Resolve it by splitting the topic by vantage point:

| Shared topic | Split by vantage point |
|--------------|------------------------|
| Customer stories | Marketing: the outcome. Sales: what made the customer start looking. Customer success: what the first ninety days were like |
| The product launch | Product: the decision behind it. Engineering: the hardest part to build. Sales: the question it finally answers |
| Hiring | People team: how the process works. Hiring manager: what the team does. A recent joiner: what the first month was like |

**Gaps.** Read the topic coverage map for what nobody covers. A subject that
matters to the goal and has no owner is either an invitation to make or a
subject to leave alone, not something to hand to whoever has spare time.

## 7. What the company supplies each week

One short internal note, sent on the same day each week, containing:

- **What happened** that people may want to talk about: a release, a customer
  milestone, an event, a hire.
- **What is cleared**: the specific facts, figures, names and images that may
  be used publicly, and anything that is explicitly not yet public.
- **Source material**: links, screenshots, a photo from the event.
- **Angles, not copy**: "engineers might talk about the migration; sales might
  talk about the question customers kept asking". One line each.
- **Who to ask** if a draft trips a review trigger.

The note never contains a ready-to-paste post. If someone asks for one, offer
a conversation about what they would say instead.

Help that keeps the person in the loop is fine: a colleague reading a draft, a
drafting tool used by the author, an interview that turns into the author's
own post. The author decides what is published and can explain every line.

## 8. Launch sequence

Four steps. Each has an exit condition; move on when it is met, not on a date.

| Step | Work | Exit condition |
|------|------|----------------|
| Charter | Fill in `assets/advocacy_charter_template.md`; answer every governance key; run the planner with `--fail-on blocker` | No blockers; the charter has an owner and a reviewer |
| Invite | Ask people one at a time; share the charter; record consent | A roster of people who each said yes |
| Stage | Agree topics and hours with each person; run the planner; share each person their own row | Every member has seen and accepted their row |
| Review | After four weeks, compare the plan with what happened and adjust tables, hours and topics | Changes agreed with the members, not announced to them |

Small is better at launch. Five willing people who keep going teach you more
than twenty who were enrolled.

## 9. Running it: events, absences, quiet members

| Situation | What to do |
|-----------|------------|
| Someone is on leave, at a conference or in a crunch | Their cadence is zero for the period. Nothing is "owed" on return |
| Someone has gone quiet | Ask once, privately, whether they want to pause, change topics or stop. Accept the answer |
| Someone wants to do much more | Check it fits their job and their manager's expectations; raise their hours, do not just raise the target |
| A company incident (outage, press issue, legal matter) | The owner calls a pause under the charter; see `governance-and-consent.md` |
| A launch week | Supply more material. Do not raise cadences or coordinate timing; let people post when they have something to say |
| A member leaves the company | Remove them from the roster. Their account and audience remain theirs |

## 10. Calibrating the time model

The planner assumes minutes per post, per comment and per reshare. The defaults
are guesses that suit nobody exactly. Calibrate after the first month:

1. Ask each member for an honest estimate of minutes spent in a typical week.
2. Divide by what they actually published to get their real minutes per post.
3. Take the median across the team and pass it with `--minutes-per-post`.
4. Re-run the planner and see whose rows are now trimmed to budget.

If the median is far above the default, the bottleneck is usually deciding
what to say, which the weekly note should fix, not typing speed.

## 11. Design checklist

Validate the design before launch.

- [ ] Charter completed and shared with every invitee
- [ ] Planner run with `--fail-on blocker` exits 0
- [ ] Every member on the plan has said yes themselves
- [ ] Every member has two or three topics of their own
- [ ] No topic held by three or more people without an agreed split
- [ ] Every row fits the hours that person agreed to
- [ ] The goal has at least one voice from the roles it depends on
- [ ] A weekly note exists, with an owner, and contains no paste-ready posts
- [ ] A four-week review is in the calendar
