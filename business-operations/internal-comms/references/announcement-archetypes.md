# Announcement Archetypes

Eight archetypes cover roughly 90% of internal announcements. Each has a structure that
works, a length band, and a characteristic failure. Pick the archetype first — the tone
questions people agonise over mostly resolve themselves once the structure is right.

Every archetype still owes the reader the five required elements: what changed, why,
who is affected, what to do, where to ask.

---

## 1. Organisational change (reorg, team merge, reporting line change)

**Length:** 300-500 words. **Feedback window:** none. **Delivery:** manager cascade, then written.

### Structure

1. **The change, in one sentence, with the date.** "From 1 September, Platform and
   Infrastructure become a single team of 45, reporting to Dana."
2. **The problem it solves.** Name the actual operational failure — duplicated on-call,
   two roadmaps competing for the same capacity, whatever it was. Vagueness here is what
   generates the rumour that the real reason is cost.
3. **Who moves and who does not.** Named groups. Include the sentence "if you are not
   listed here, your reporting line does not change."
4. **What happens to work in flight.** The first practical question everyone has.
5. **Sequence and dates.** When new lines take effect, when 1:1s get scheduled.
6. **Where to ask**, with a named person and a response commitment.

### Worked opening

> From 1 September, Platform and Infrastructure merge into a single Infrastructure
> Platform team of 45, reporting to Dana Whitfield. We are doing this because the two
> teams have been carrying separate on-call rotations for one shared production estate,
> and neither rotation has been sustainable for the last two quarters.

### Characteristic failure

Leading with strategy language ("to better align our operating model") instead of the
operational problem. Readers reliably interpret unexplained reorgs as pre-layoff staging.

---

## 2. Workforce reduction

**Length:** 250-400 words to the whole org; separate, longer material for affected people.
**Feedback window:** none. **Delivery:** affected individuals in person first, always.

### Structure

1. **What happened, in plain words.** "We are eliminating 60 roles, about 8% of the company."
   Never "we are saying goodbye to some of our family."
2. **Why, including the number that forced it.** Runway, revenue miss, market shift.
3. **How people were selected.** Criteria, not names.
4. **What affected people receive.** Severance, healthcare continuation, notice period,
   references, equipment.
5. **What happens to everyone else today.** Meetings cancelled, systems access, the schedule
   for the rest of the day.
6. **When leadership will take questions.** Same day if possible.

### Sequencing rule

Nobody learns they are affected from an all-staff email. Individual conversations happen
first, in a compressed window, and the all-staff message goes out after the last one ends.
If the window cannot be compressed enough, brief managers, run the conversations in parallel,
and accept a two-hour window rather than a two-day one.

### Characteristic failure

Euphemism. "Restructuring for efficiency," "role eliminations as part of a strategic
realignment." The auditor flags these as jargon, and readers read them as evasion — which
makes the subsequent reassurances about severance less believable, not more.

---

## 3. Policy change (RTO, expenses, security, performance process)

**Length:** 400-700 words. **Feedback window:** 5-10 business days if genuinely reversible.
**Delivery:** email, with an intranet page as the record.

### Structure

1. **The new rule, stated as a rule.** Not the philosophy behind it.
2. **The old rule, for contrast.** People calibrate on the delta.
3. **Why now.** The triggering event or constraint.
4. **Who it applies to, and the exceptions.** Exceptions listed explicitly, because
   unlisted exceptions become a queue of individual negotiations.
5. **What to do and by when.**
6. **How it will be enforced.** Omitting this signals the policy is decorative.
7. **Where to ask.**

### Characteristic failure

Announcing a policy without an enforcement mechanism or an exceptions process. Both gaps
get filled informally within a fortnight, and the informal version is the one that sticks.

---

## 4. System or product migration

**Length:** 200-350 words. **Feedback window:** questions only. **Delivery:** email plus
in-product notice, repeated on a decay schedule.

### Structure

1. **The action and the deadline, in the subject line and the first sentence.**
2. **What breaks if they miss the deadline.** Concretely.
3. **How long the action takes.** "Two minutes" materially raises completion rates
   against an unspecified duration.
4. **Link to the step-by-step.**
5. **Who to ask when it fails.**

### Reinforcement schedule

T-14 announce, T-7 reminder to non-completers only, T-2 reminder to non-completers,
T-0 final notice, T+1 what changed for stragglers. Never send reminders to people who
already complied — that is the fastest way to train the org to ignore your sends.

### Characteristic failure

Explaining the strategic rationale for the migration. For an instructional message, rationale
is noise; readers want the action and the deadline.

---

## 5. Leadership change (arrival, departure, promotion)

**Length:** 200-350 words. **Feedback window:** none.

### Structure

1. **Who, what role, effective when.**
2. **For departures: whether it was their decision.** If you do not say, everyone assumes
   it was not. One clause suffices.
3. **What they will own**, in terms of the work rather than the title.
4. **Interim arrangements**, if there is a gap.
5. **How to meet them / how to say goodbye.**

### Characteristic failure

Effusive praise for a departing executive whose exit was involuntary. It reads as dishonest
and devalues genuine praise elsewhere. A neutral, factual departure note is more respectful
than an implausible tribute.

---

## 6. Bad news (incident, missed target, cancelled project)

**Length:** 250-400 words. **Feedback window:** post-mortem participation.

### Structure

1. **What happened.** Plainly, first sentence, no preamble.
2. **The impact.** Numbers where you have them, "we do not yet know" where you do not.
3. **What we did.** Past tense, specific.
4. **What we are changing.** With owners.
5. **What we do not know yet**, and when you will know.

Leading with "we take this seriously" before stating what happened reads as a legal posture.
State the facts first; the seriousness is demonstrated by the specificity.

### Characteristic failure

Waiting for complete information before communicating. A message that says "here is what we
know at 14:00, here is what we do not, next update at 17:00" beats a complete message
six hours later, because the gap is filled by speculation.

---

## 7. Recurring exec update

**Length:** 300-600 words, same shape every time. **Cadence:** weekly or fortnightly, never
both. Skipping is worse than shortening.

### Structure

1. **One-line state of play.** The single thing that changed since last time.
2. **Decisions made** — with the decision, not the discussion.
3. **Decisions pending**, with who decides and by when.
4. **Numbers**, the same three to five every time, with the delta.
5. **What I need from you.**
6. **What I got wrong last time.** Optional, but the single highest-trust element available
   in this format.

### Characteristic failure

The status dump: a list of what every team did, with no through-line. If a reader cannot say
what changed after reading it, it was a log, not an update.

---

## 8. All-hands agenda

**Length:** 45-60 minutes, at most four topics. **Cadence:** monthly beats weekly.

### Structure

| Segment | Minutes | Purpose |
|---------|---------|---------|
| State of play | 5 | One narrative, not a tour of departments |
| Numbers | 5 | Same metrics every time, with trend |
| Deep dive | 15 | One topic, owned by whoever did the work, not the exec |
| Recognition | 5 | Specific, tied to the work, not a raffle |
| Q&A | 20 | Pre-submitted and upvoted, live questions taken second |

### Rules that hold

- Answer the top-voted question first, even if it is uncomfortable. Skipping it once teaches
  people the channel is decorative and submissions collapse.
- "I do not know" plus "I will find out by Thursday" is a complete and acceptable answer.
- Never announce a reorg or a workforce reduction in an all-hands as the first delivery.
  A room is the wrong place to learn your job changed.
