# Retrospective Facilitation Guide

Expert knowledge base for running effective sprint retrospectives — formats, facilitation techniques, anti-patterns, and psychological safety frameworks.

## Retrospective Formats

### 1. Start / Stop / Continue

**Best for:** Teams new to retros, quick sessions (<30 min)

| Column | Prompt |
|--------|--------|
| Start | What should we begin doing next sprint? |
| Stop | What should we stop doing? |
| Continue | What is working well and should continue? |

**Facilitation tip:** Time-box each column to 5 minutes of silent writing, then 5 minutes of discussion.

### 2. 4Ls (Liked, Learned, Lacked, Longed For)

**Best for:** Teams that want both emotional and practical reflection

- **Liked:** What went well? What did you enjoy?
- **Learned:** What new knowledge or skills did you gain?
- **Lacked:** What was missing? What resources or support were needed?
- **Longed For:** What do you wish had happened?

### 3. Sailboat

**Best for:** Visual thinkers, longer retros (45-60 min)

- **Wind (propellers):** What pushed us forward?
- **Anchor (drag):** What slowed us down?
- **Rocks (risks):** What risks lie ahead?
- **Island (goal):** Where are we trying to go?
- **Sun (appreciation):** What made this sprint bright?

### 4. DAKI (Drop, Add, Keep, Improve)

**Best for:** Action-oriented teams, process improvement focus

- **Drop:** What should we stop doing entirely?
- **Add:** What new practice should we adopt?
- **Keep:** What practices are working and should stay?
- **Improve:** What existing practices need adjustment?

### 5. Mad / Sad / Glad

**Best for:** Teams needing to surface emotions, after difficult sprints

- **Mad:** What frustrated you?
- **Sad:** What disappointed you?
- **Glad:** What made you happy?

**Facilitation tip:** This format works best when followed by a root-cause discussion on the top "Mad" items.

### 6. Starfish

**Best for:** Nuanced feedback, teams beyond basic Start/Stop/Continue

Five categories on a starfish diagram:
1. Keep Doing
2. More Of
3. Less Of
4. Stop Doing
5. Start Doing

### 7. Timeline Retrospective

**Best for:** Long sprints (3-4 weeks), sprints with significant events

Draw the sprint timeline on a board. Team members place events (positive and negative) along the timeline. Discuss patterns, clusters, and cause-effect relationships.

### 8. Lean Coffee Retrospective

**Best for:** Self-organizing teams, when facilitator wants minimal structure

1. Team members write topics on sticky notes (2 min)
2. Brief explanation of each topic (30 sec each)
3. Dot-vote to prioritize (2 votes per person)
4. Discuss top-voted topics (5 min each, extend by vote)

## Facilitation Techniques

### Setting the Stage (5 minutes)

- **Check-in round:** One word describing your sprint experience
- **Prime directive:** "Regardless of what we discover, we understand and truly believe that everyone did the best job they could, given what they knew at the time."
- **Working agreements:** Remind the team of retro ground rules

### Gathering Data (15 minutes)

- Silent brainstorming first (prevents anchoring bias)
- Use timers to keep writing phases focused
- Encourage specific examples over vague observations
- Dot-voting to surface top themes (2-3 votes per person)

### Generating Insights (15 minutes)

- "Five Whys" on top-voted items to find root causes
- Affinity mapping to group related observations
- Focus on systems and processes, never individuals
- Ask "What conditions led to this?" rather than "Who caused this?"

### Deciding Actions (10 minutes)

- Limit to 2-3 action items per retro (more leads to dilution)
- Every action item needs an owner and a deadline
- Actions should be SMART: Specific, Measurable, Achievable, Relevant, Time-bound
- Review previous action items before creating new ones

### Closing (5 minutes)

- Appreciation round: each person thanks one teammate
- Return on Time Invested (ROTI) vote: 1-5 scale
- Confirm action item owners and review date

## Anti-Patterns to Avoid

### 1. The Blame Game

**Symptom:** Discussion devolves into finger-pointing at individuals.
**Fix:** Enforce the prime directive. Redirect to systemic causes. Use "What conditions..." framing.

### 2. The Echo Chamber

**Symptom:** Same feedback every sprint, no new insights surface.
**Fix:** Rotate retro formats. Invite guest facilitators. Use data (from velocity_analyzer.py) to surface non-obvious patterns.

### 3. No Follow-Through

**Symptom:** Action items from last retro are forgotten or incomplete.
**Fix:** Start every retro by reviewing previous action items. Use retro_report_generator.py with `--previous-retro` to track completion.

### 4. The Monologue

**Symptom:** One person dominates discussion; others disengage.
**Fix:** Use silent writing phases. Round-robin sharing. Anonymous submission tools.

### 5. Scope Creep

**Symptom:** Retro turns into a planning meeting or architecture discussion.
**Fix:** Park off-topic items in a "parking lot." Strict time-boxing. Facilitator redirects.

### 6. Skipping the Retro

**Symptom:** Team cancels retros when "nothing went wrong" or they're "too busy."
**Fix:** Retros are for amplifying what works, not just fixing problems. Schedule as recurring, non-negotiable.

### 7. Metrics Without Context

**Symptom:** Velocity numbers used to judge or pressure the team.
**Fix:** Velocity is a planning tool, not a performance metric. Always pair numbers with qualitative discussion.

### 8. Superficial Action Items

**Symptom:** Actions like "communicate better" or "be more careful."
**Fix:** Demand specificity. "Communicate better" becomes "Add a 5-minute async standup post in Slack by 10am daily."

## Remote Retrospective Best Practices

### Tooling

- Use collaborative boards (Miro, FigJam, Retrium) for visual exercises
- Video on during discussion phases for non-verbal cues
- Anonymous input options for sensitive topics
- Timer visible to all participants

### Engagement Techniques

- Smaller breakout groups (3-4 people) for initial discussion, then regroup
- Asynchronous pre-work: gather observations before the meeting
- Use reactions/emojis for quick agreement signals
- Rotate facilitator role to maintain engagement

### Time Adjustments

- Remote retros need 10-15% more time than in-person
- Add explicit transition moments between phases
- Build in 2-minute breaks for sessions over 45 minutes
- Use countdown timers for writing phases

### Inclusion

- Record the session for absent team members (with consent)
- Share the retro report (via retro_report_generator.py) within 24 hours
- Allow async additions for 24 hours after the retro
- Accommodate time zones — rotate meeting times if needed

## Psychological Safety in Retrospectives

### The Foundation

Psychological safety (Edmondson, 1999) is the belief that one will not be punished or humiliated for speaking up with ideas, questions, concerns, or mistakes. It is the single strongest predictor of effective retrospectives.

### Building Safety

1. **Model vulnerability:** Facilitator shares their own mistakes first
2. **Normalize disagreement:** "It's okay to see this differently"
3. **Separate observation from judgment:** Describe what happened before evaluating it
4. **Celebrate learning from failure:** "What did this teach us?"
5. **Confidentiality agreement:** What's said in retro stays in retro (except action items)

### Safety Signals to Watch

| Signal | Healthy | Concerning |
|--------|---------|------------|
| Participation | Everyone contributes | 1-2 people silent |
| Feedback type | Mix of positive and negative | Only positive or only negative |
| Specificity | Concrete examples shared | Vague, hedged statements |
| Risk-taking | Novel ideas proposed | Only "safe" suggestions |
| Body language | Relaxed, engaged | Crossed arms, cameras off |

### When Safety Is Low

- Switch to anonymous input methods
- Use 1-on-1 pre-retro conversations to surface concerns
- Address the safety issue directly (meta-retro)
- Consider bringing in an external facilitator
- Start with appreciations to build positive atmosphere

### Measuring Safety Over Time

Track these proxy metrics across retros:
- Number of unique contributors to discussion
- Ratio of improvement items to appreciation items
- Action item completion rate (indicates trust in the process)
- ROTI scores trend (indicates perceived value)

---

**Last Updated:** 2026-03-18
