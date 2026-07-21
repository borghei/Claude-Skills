# Interview Craft and Synthesis

Reference for constructing discovery interview guides, moderating without
contaminating the data, and converting sessions into insights that survive
scrutiny.

## 1. The guide is a structure, not a script


A semi-structured guide fixes the **topics and their order**, not the wording.
Fixing the wording produces a survey administered aloud, which wastes the one
thing an interview offers: the ability to follow a surprise.

What the guide must fix:

- The opening and consent language, verbatim
- The topic sequence
- The one or two must-ask questions per topic
- The probes available under each topic
- The closing

What the guide must leave free: everything else. Moderators should feel licensed
to spend ten minutes on an unplanned thread if it is producing new information.

## 2. Guide structure


### Warm-up (3-5 minutes)

Establish role, tenure, and daily shape of the work. Purpose is twofold: get the
participant talking in specifics, and capture the context needed to interpret
everything that follows.

- "Walk me through what a normal Tuesday looks like for you."
- "How long have you been doing this, and what did you do before?"

Never open with the topic under study. A cold open on "so, tell me about ticket
triage" produces a rehearsed summary rather than a real account.

### Context (5-8 minutes)

Establish the problem space in the participant's own terms, before you introduce
any of your vocabulary.

- "Where does the work come from, and who hands it to you?"
- "What has changed about that in the last year?"

**Record their vocabulary verbatim.** If they say "the pile" and you say "the
inbound queue," adopt their word for the rest of the session. Their language is
also the language your product and marketing should use.

### The specific-instance core (20-30 minutes)

This is the load-bearing section. Everything valuable in a discovery interview
comes from concrete past occurrences, not from generalisations.

The move that makes the difference:

> "Tell me about the last time that happened."

Then walk the timeline: what triggered it, what they did first, what they tried,
what they did when that failed, who else got involved, how it ended, and what it
cost them.

| Ask this | Not this |
|----------|----------|
| "Walk me through the last time a ticket got misrouted." | "How often do tickets get misrouted?" |
| "What did you do when you noticed?" | "What would you normally do?" |
| "How long did that take you?" | "Is it time-consuming?" |
| "Who else got pulled in?" | "Is it a team problem?" |
| "What happened to the customer?" | "Does it affect customers?" |

The left column produces data. The right column produces the participant's
theory about themselves, which is a different and much weaker artefact.

### Workaround excavation (5-10 minutes)

Workarounds are the highest-value signal in discovery: they are places where
someone cared enough about a problem to build an unsupported solution.

- "Is there anything you do outside the system to make this work?"
- "Do you keep anything in a spreadsheet, notes app, or on paper?"
- "Has anyone on the team built something for this themselves?"
- "What do you check before you trust what the system tells you?"

That last one is particularly productive. Every verification ritual marks a
trust failure.

### Prioritisation (5 minutes)

Force a trade-off. Unranked problem lists come back with everything important.

- "Of the things we've discussed, which one, if it disappeared tomorrow, would
  change your week the most?"
- "If you could fix exactly one and the others stayed as they are, which?"

### Close (2-3 minutes)

- "What should I have asked you that I didn't?"
- "Who else should I talk to about this?"

The first question is consistently one of the most productive in the whole
guide, and it costs nothing.

## 3. Probing


The core probes, in order of usefulness:

| Probe | Use |
|-------|-----|
| **Silence** | Wait. Three to five seconds. The most underused probe there is — participants fill it with the thing they were deciding whether to say. |
| **"Tell me more about that."** | Neutral expansion with no direction attached. |
| **"What happened next?"** | Keeps a timeline moving without steering it. |
| **"What did you do then?"** | Behaviour, not opinion. |
| **"Why does that matter to you?"** | Ladders from behaviour to motivation. |
| **"You mentioned X — say more?"** | Signals you were listening and lets them choose the direction. |
| **"How did you learn to do it that way?"** | Surfaces institutional history and prior failures. |
| **"What would you have done if that hadn't worked?"** | Reveals the fallback hierarchy. |

### Moderator failure modes

| Failure | What it sounds like | Fix |
|---------|--------------------|-----|
| **Leading** | "So that's frustrating, right?" | Ask "how did that feel" or nothing at all. |
| **Feature pitching** | "What if we built X?" | Never. If you must test a concept, do it in the last five minutes, after all generative content is captured. |
| **Filling silence** | Rephrasing your own question after two seconds | Count to five. Let them work. |
| **Accepting generalities** | Participant says "usually we..." and you move on | "Tell me about the most recent time." |
| **Talking past 20% of airtime** | Long moderator turns | Track it. If you are talking more than a fifth of the session, you are interviewing yourself. |
| **Defending the product** | "Actually you can do that in settings" | Note it, say nothing, follow up after the session. Correcting a participant mid-session ends the honest reporting. |
| **Note-taking instead of listening** | Missed follow-ups | Record with consent and bring a second person to take notes. |

## 4. Running the session


- **Two people per session** where possible: one moderates, one takes notes and
  tracks which guide topics remain uncovered.
- **Record with explicit consent**, and say what will happen to the recording,
  who will see it, and when it will be deleted.
- **Debrief within 15 minutes of the session ending**, before the next one. Five
  minutes: top three things heard, anything that contradicted an earlier
  session, anything to change in the guide. Memory of the session degrades
  faster than anyone expects.
- **Update the guide between sessions.** A guide that has not changed by session
  four means you are not learning from your own study.
- **Log new themes per session** so you can see saturation arriving rather than
  guessing at it.

## 5. Synthesis


### Sequence

1. **Extract observations.** One atomic observation per note: what the
   participant did or said, with participant ID and timestamp. No
   interpretation at this stage.
2. **Tag by kind.** Observed behaviour, artefact, reported statement, or your
   inference. This distinction determines everything downstream.
3. **Cluster into themes.** Group observations that describe the same underlying
   behaviour — not the same topic. "Slow" and "I check it twice" belong to the
   same theme if the second is caused by the first.
4. **Count before you interpret.** How many distinct participants exhibited each
   theme? This number is the finding; the quote is the illustration.
5. **Write claims.** A claim states what is happening and why, in one sentence,
   falsifiably.
6. **Score confidence.** Weighted by evidence kind, participant spread, and
   source diversity.
7. **Attach the decision.** What should change as a result? An insight with no
   implied action is trivia.

### Evidence kinds and their weight

| Kind | Definition | Weight |
|------|------------|--------|
| **Observed** | You watched them do it | Highest |
| **Artefact** | A log, ticket, recording, or document shows it | High |
| **Reported** | They told you they do it | Moderate — subject to recall error and self-presentation |
| **Inferred** | You concluded it from other evidence | Low — must be labelled as your inference, never as a finding |

A claim resting entirely on reported evidence is capped in confidence no matter
how many people said it. Consistent self-report across a dozen people is still
self-report; it establishes that a belief is widespread, not that the behaviour
is.

### Writing a good claim

| Weak claim | Strong claim |
|------------|-------------|
| "Users are frustrated by triage." | "Agents re-triage manually because auto-assignment ignores account tier, so enterprise tickets land in the general queue." |
| "Onboarding is confusing." | "Users abandon at the workspace-naming step because they cannot tell whether the name is permanent or visible to their customers." |
| "People want more integrations." | "Teams using an external scheduler export a CSV weekly because there is no sync, costing about 40 minutes each week." |

A strong claim names the actor, the behaviour, the mechanism, and where possible
the cost. It is specific enough that a single counter-observation would
challenge it — which is exactly the property that makes it useful.

### Confidence bands and how to use them

| Band | Meaning | Use |
|------|---------|-----|
| **High** | Multiple participants, observed or artefact evidence, 2+ channels | Decision input. Cite it directly. |
| **Moderate** | Several participants, mixed evidence kinds | Decision input with the caveat stated. |
| **Low** | Thin participant spread or single channel | Hypothesis. Name it as one. |
| **Speculative** | One participant, or entirely inferred | Do not put it in a readout as a finding. It is a research question for next round. |

The discipline that matters: **label the bands in the readout.** A deck where
every insight is presented with equal weight teaches the audience to discount
all of them equally, including the well-evidenced ones.

## 6. The readout


Structure that survives an executive audience:

1. **The decision this informs** — one line, at the top
2. **What we did** — method, n per segment, dates, recruiting source
3. **The three things that matter** — highest-confidence insights only
4. **Evidence per insight** — participant count, evidence kinds, one illustrating quote
5. **What we recommend** — the action each insight implies
6. **What we still do not know** — the hypotheses that did not clear the bar
7. **Method limitations** — who was not in the sample and what that means

Section 7 is the one most often cut and the one that most protects the work. If
your sample was all power users, saying so explicitly prevents the finding from
being over-applied six months later by someone who never read the method.

## 7. Remote and in-person sessions


| Factor | Remote | In-person |
|--------|--------|-----------|
| Recruiting reach | Wide — geography is not a constraint | Narrow |
| Cost per session | Low | High once travel is counted |
| Observing the environment | Poor — you see what the camera shows | Excellent |
| Artefact discovery | Weak; you must ask | Strong; you notice |
| Rapport | Adequate; slower to build | Stronger |
| Scheduling | Easy | Hard |

**[RECOMMENDED]** Default to remote for interviews and in-person for contextual
inquiry. Remote is good enough for narrative and cheap enough to do more of;
contextual inquiry loses its central advantage — seeing the environment and the
artefacts people never mention — when mediated by a webcam.

For remote sessions specifically:

- Ask participants to share their screen and walk through the real thing rather
  than describing it. A screen share recovers much of what remote loses.
- Send the consent form in advance and confirm verbally at the start.
- Budget five minutes for setup problems in every session, and have a phone
  fallback ready.
- Watch for the participant reading their own notes. Prepared answers are a sign
  the invitation revealed too much about what you wanted to hear.

## 8. Ethics and participant care


Discovery research puts you in contact with people's working lives and sometimes
their difficulties. Three obligations:

1. **Informed consent that is actually informed.** Say what the session is for,
   who will see the recording, how long it is kept, and that they may stop at any
   time. Consent obtained by reading a paragraph quickly is not consent.
2. **Data minimisation.** Do not collect personal data you do not need. If you
   need it for scheduling only, delete it after the session. Store recordings
   with access limited to the people who need them.
3. **Do no harm in the writeup.** Participants can be identifiable from role
   plus company plus a distinctive quote even without a name. Aggregate, and
   check with fresh eyes whether any single participant is identifiable.

If a participant discloses distress, harassment, or wrongdoing, stop the research
frame. Do not probe it for insight. Acknowledge it, offer to pause or end, and
follow whatever escalation path your organisation has.

## 9. Building a continuous cadence


Project-based research produces bursts of insight separated by long silences.
Continuous discovery produces a steady flow that keeps decisions evidenced.

A workable weekly rhythm:

| Cadence | Activity | Owner |
|---------|----------|-------|
| Weekly | 2-3 participant conversations | Rotating: PM, designer, engineer |
| Weekly | 30-minute synthesis session | Whole trio |
| Fortnightly | Update the opportunity map | PM |
| Monthly | Review which decisions used evidence | PM + lead |
| Quarterly | Retire stale insights | Whole team |

Four things make it survive contact with a real roadmap:

- **A standing recruiting pipeline.** The reason continuous discovery stops is
  always recruiting. Keep a rolling pool with participants scheduled two weeks
  ahead so a busy week does not break the chain.
- **Engineers in sessions.** An engineer who has watched three users struggle
  needs no persuading later. This is the highest-return habit available and the
  first one dropped under delivery pressure.
- **A shared repository.** Insights that live in one person's notes are lost when
  they change team. Tag by theme and by decision so they are findable later.
- **A staleness policy.** Insights decay. Anything older than about 12 months
  should be re-validated before it is cited, and anything about a flow that has
  since changed should be retired outright.

## 10. Handling difficult sessions


| Situation | Response |
|-----------|----------|
| **Participant gives one-word answers** | Slow down. Go back to a concrete past event and walk the timeline step by step. Silence helps more than another question. |
| **Participant wants to give feedback on your product** | Note it, thank them, redirect: "That's useful — before we get there, can you tell me how you handle it today?" |
| **Participant is clearly the wrong fit** | Continue politely and briefly, pay the incentive, exclude from analysis, and fix the screener. Never make them feel they failed a test. |
| **Participant is a colleague's contact and is performing** | Acknowledge the relationship openly and say that critical feedback is the useful kind. |
| **A senior stakeholder joins and starts pitching** | Agree the rules before the session: observers stay muted and ask questions only at the end. Enforce it. |
| **Participant becomes upset about a work situation** | Stop the research frame. Offer to pause or stop. Do not mine it. |
| **You realise mid-session the question is wrong** | Change it. That is what semi-structured means. Note the change for the next session. |

## 11. Common synthesis errors


| Error | Why it happens | Correction |
|-------|---------------|------------|
| **Counting statements rather than participants** | One talkative participant produces many quotes | Count distinct participants per theme |
| **Theming by topic rather than by behaviour** | Topics are easier to name | Group by underlying behaviour and cause |
| **Losing the negative cases** | They complicate a clean story | Report them; a theme with three exceptions out of eight is not a pattern |
| **Promoting an inference to a finding** | The inference feels obvious after ten sessions | Keep the evidence-kind tag through to the readout |
| **Synthesising too early** | Pressure to report after session three | Do not synthesise before four sessions in a segment |
| **Anchoring on the first session** | It was the most surprising | Re-read the first session's notes last, after the themes are set |

That final trick is worth adopting as habit. The first session disproportionately
shapes how every later one is heard; re-reading it at the end, against themes
built from the others, reliably surfaces where you over-fitted to it.

## 12. Session checklist


**Before**
- [ ] Guide has topics and probes, not a fixed script
- [ ] The result that would change our course is written down
- [ ] Consent language drafted; recording permission plan clear
- [ ] Second person assigned to notes
- [ ] Participant's segment and how they were recruited logged

**During**
- [ ] Warm-up before topic
- [ ] Their vocabulary captured and adopted
- [ ] Every generality converted to a specific past instance
- [ ] Workaround excavation run
- [ ] Forced trade-off asked
- [ ] "What should I have asked?" asked
- [ ] Moderator airtime under 20%

**After**
- [ ] Debriefed within 15 minutes
- [ ] New themes logged for saturation tracking
- [ ] Guide updated if anything surprised you
- [ ] Observations extracted atomically, tagged by evidence kind
- [ ] Themes counted by distinct participant before any quote was selected
