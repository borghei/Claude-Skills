# Customer Feedback Triage — Workflow Guide

A practical guide to running the triage workflow week over week, with channel-by-channel guidance, common edge cases, and the discipline required to make request management work without consuming a PM's calendar.

## The cadence

| Frequency | What | Who | Time |
|---|---|---|---|
| **Continuously** | Intake records created as feedback arrives | Support, Sales, CSMs, in-app widget | ~1 min per item |
| **Weekly** | Triage queue review: dedup, score, route, draft responses | PM (owner) + CSM + Engineering rep | 60 min |
| **Weekly** | Acknowledgments sent to customers from previous week's triage | Originating channel (support agent, AE) | 15 min |
| **Monthly** | Triage retrospective: channel mix, conversion rates, themes | PM + leadership | 30 min |
| **Quarterly** | Adjust segment weights and Kano category assignments based on observed patterns | PM | 60 min |

Teams that batch triage less frequently than weekly tend to accumulate acknowledgment debt and miss recurring patterns. Teams that triage daily tend to over-react to single signals.

## Channel-by-channel intake

Each channel has different signal characteristics and different intake norms.

### Support tickets

- **Signal characteristics**: rich, problem-anchored (the customer is having an active issue), often a mix of bugs and feature requests.
- **Intake norm**: the support agent tags the ticket with a "feature-feedback" label at close. A nightly job pulls those tickets into the triage queue.
- **Common trap**: support agents paraphrase the request to fit a known template; raw verbatim is lost. Mitigation: capture the customer's exact words in a dedicated field, not just the agent's summary.

### Sales call notes

- **Signal characteristics**: aspirational (the customer is buying or considering buying), often filtered through what Sales thinks will close the deal.
- **Intake norm**: AEs tag CRM notes with "feature-asked" or use a dedicated "feature requests" field. Weekly sync exports to the triage queue.
- **Common trap**: every feature ask from sales is framed as "blocker for renewal" or "blocker for closing". Mitigation: require a verifiable tie-back ("would the customer state this in writing as a renewal condition?") to apply the segment weight uplift.

### CSAT and NPS verbatims

- **Signal characteristics**: short, post-experience, often pain-anchored. NPS detractors give the most actionable feedback; promoters give the least.
- **Intake norm**: weekly export from the survey tool. Filter to verbatims of >= 10 characters that contain a request or pain signal.
- **Common trap**: averaging the numerical score and ignoring the verbatim. The verbatim is the signal; the number is a heuristic.

### In-app feedback widget

- **Signal characteristics**: contextual (the customer was on a specific screen when they submitted), often terse, often anonymous.
- **Intake norm**: each submission is a triage queue item. Include the URL / screen as part of the raw_text.
- **Common trap**: low-effort submissions overwhelm the queue. Mitigation: require a minimum-length submission (40+ characters) on the widget, or have the widget ask a follow-up question.

### Executive ask ("HiPPO")

- **Signal characteristics**: high social weight, low information density (often a one-liner from a customer dinner), high political cost to ignore.
- **Intake norm**: any exec-channel ask goes through the same intake form as any other channel. The exec doesn't get to bypass the queue.
- **Common trap**: PM acts on the exec ask first because of the social signal, displacing higher-priority work. Mitigation: report exec-channel-to-roadmap conversion rate monthly to leadership. If the rate is much higher than other channels, the data itself becomes the conversation.

### Social listening

- **Signal characteristics**: noisy, often emotional, occasionally contains genuine product insight.
- **Intake norm**: filter to mentions of your product name with a verb ("can't", "wish", "would love", "broken"). Skim weekly, log promising ones manually.
- **Common trap**: triaging every tweet. The signal-to-noise ratio is low. A 15-minute weekly scan is enough.

### Partner / integration requests

- **Signal characteristics**: structured, often have a specific use case behind them, sometimes come with commercial pressure (partner says "ship this or we'll integrate with your competitor").
- **Intake norm**: same triage queue, but flag with `channel=partner` so the segment weight and strategic-alignment calculation can boost.

### Customer interview notes (from discovery)

- **Signal characteristics**: high-quality, opportunity-anchored (the interviewer is probing for jobs, not capturing requests).
- **Intake norm**: only file an item if the customer said something that maps to a specific request. Most of an interview produces opportunity signal that should flow into `discovery/interview-synthesis/`, not the triage queue.

## The weekly triage meeting (60 minutes)

| Time | Activity |
|---|---|
| 0-10 min | Review queue size and channel mix; flag anomalies (e.g. sudden support-ticket spike) |
| 10-25 min | Run the Python tool (or manual triage worksheet); review clusters and Kano guesses; PM overrides where the heuristic is wrong |
| 25-40 min | Route to destinations: prioritization, bug tracker, docs, strategy, archive |
| 40-50 min | Draft and send acknowledgments (or assign to channel originators) |
| 50-60 min | Note recurring themes for monthly retrospective |

The meeting has a fixed cadence and a fixed time box. If the queue is too big to triage in the time, the right move is to raise the threshold for the next week (auto-archive more low-signal items) rather than extend the meeting.

## When to override the Kano guess

The keyword heuristic gets the category right roughly 60-70% of the time on common requests. Override when:

- The request is **basic** but the keywords didn't include the obvious bug-indicators ("the report shows the wrong number" — basic, but no "broken" keyword).
- The request is **delight** but masquerades as performance ("make search faster" — but in context, the customer wants natural-language search, not literally faster).
- The request is **reverse** but the keywords missed it ("can you add more notifications?" — for some customer segments this is a reverse feature; the team should reduce, not add).
- The customer segment changes the category. A delighter for SMB ("ai assistant") is often a basic for enterprise ("must have an audit log of every AI action").

Document overrides in the cluster notes. Over time, override patterns inform heuristic tuning.

## Responding to customers

The single biggest impact you can have on customer trust at low cost is consistent acknowledgment. Three response templates exist (in `assets/response_templates.md`); the discipline is:

| Template | When | What to avoid |
|---|---|---|
| **Will-build** | The cluster is funded, scoped, and on the next 1-2 quarters of roadmap. | Specific commitments to dates the team will not hit. Use "an upcoming release" if a date is not locked. |
| **Exploring** | The cluster has signal but is not yet scoped. | "We'll probably build that". Acknowledge interest, do not commit. |
| **Won't-build** | The cluster is out of scope, low-signal, or strategically off-direction. | Boilerplate that does not address the customer's underlying need. Always explain. |

The response is sent **by the originating channel owner**, not by the PM directly. The support agent, AE, or CSM keeps the relationship. The PM provides the message and the routing rationale.

## Common edge cases

### A single enterprise customer asks for something nobody else wants

- This is the most contentious triage case. The volume signal says "no" (1 customer). The segment signal says "yes" (enterprise). The strategic signal depends on the deal size and the company's segment strategy.
- The disciplined answer: if the request is a renewal-blocker for a top-decile customer AND the work is small AND it doesn't drag the product in a direction misaligned with strategy, build it. Otherwise, decline gracefully and explain the rationale.

### Sales promises a feature in a deal

- Damage control: bring the request through normal triage but flag it as "sales-promised" so it shows up in the monthly delta report.
- Process fix: train sales to use the "exploring" framing in customer conversations. "We've heard this from other customers and are looking into it" is a defensible statement; "we'll have that in Q3" is a commitment.

### A request looks like a feature but is actually a strategy question

- "Can we get a free tier?" "Can we integrate with Salesforce?" "Can we expand into European data residency?" These are not features; they are strategy questions.
- Route to `strategy` category; do not score with feature heuristics; surface to leadership via `senior-pm/` or `c-level-advisor/`.

### A request looks like a feature but is actually a documentation gap

- "How do I export to CSV?" If the feature exists but the customer couldn't find it, the request is a doc gap, not a feature.
- Route to `question` category; flag to support and docs teams. Recurring "how do I X" questions about existing features are gold for product-marketing and onboarding teams.

### A feature request appears that you've already shipped

- The customer asked for a feature that already exists. Two possibilities: they didn't know it existed (doc/onboarding gap), or what they're asking for is subtly different from what you shipped (opportunity).
- Default to assuming opportunity. Route a clarifying question back through the originating channel before archiving.

### A negative feedback verbatim ("the product is terrible")

- Vague negative feedback is not a request. It's a satisfaction signal.
- File the customer's pattern of complaints with CSM for relationship-level follow-up. Do not score in the triage queue.

## What "good" looks like

A triage program is working when:

- Every customer who submitted a request has been acknowledged within 14 days.
- The PM can answer "why is X on the roadmap?" with a cluster ID, a customer count, and a Kano category.
- Sales reports decreasing frustration with "we feel ignored" sentiment because there is now a defensible answer to every ask.
- Leadership sees a monthly report of feedback volume by channel, Kano breakdown, and roadmap conversion rate.
- Discovery interviews are sourced from triage clusters at least once a quarter — closing the loop from request signal to discovery insight.

## References in this skill

- `assets/triage_template.md` — manual triage worksheet for teams not using the Python tool.
- `assets/response_templates.md` — three response templates, three variants each.
- `assets/kano_quick_reference.md` — one-page Kano category reference.
- `references/kano-model-deep-dive.md` — deeper Kano theory and edge cases.

## External references

- Marty Cagan, *Inspired: How to Create Tech Products Customers Love* (2nd ed., 2017)
- Marty Cagan, *Empowered* (2020)
- Noriaki Kano et al., "Attractive Quality and Must-Be Quality," *Journal of the Japanese Society for Quality Control*, 14(2), 1984

---

## Frameworks

### Marty Cagan: Request → Opportunity → Solution

Cagan separates three things customers and the inbound stream conflate:

| Layer | What it is | Example |
|---|---|---|
| **Request** | What the customer literally asked for | "Add an export to PDF button" |
| **Opportunity** | The underlying job or problem | "I need to share results with my CFO who doesn't have a login" |
| **Solution** | The chosen response | "Shareable read-only link" or "PDF export" or "CSV + email digest" |

The triage workflow's job is to convert each Request into an Opportunity and route the Opportunity to the appropriate discovery / prioritization process. The literal Request is rarely the right thing to build.

### Kano Model (Noriaki Kano, 1984)

Kano classifies features by how their presence or absence affects customer satisfaction. The five categories:

| Category | Effect of having it | Effect of missing it | Example (SaaS analytics tool) |
|---|---|---|---|
| **Basic / Must-be** | Expected; satisfaction does not increase | Severe dissatisfaction | Login works; data export exists |
| **Performance / One-dimensional** | More is linearly better | Less is linearly worse | Query speed; dashboard load time |
| **Delight / Attractive** | Disproportionate satisfaction | Customer does not miss it | Natural-language query; collaborative cursors |
| **Indifferent** | No effect | No effect | Theme color picker (for most users) |
| **Reverse** | Causes dissatisfaction | Improves satisfaction | An overly chatty AI assistant |

Kano categories shift over time: today's delighter becomes tomorrow's basic. The categorization in this triage workflow is the team's current snapshot.

### Layered customer development

Customer development can be framed as concentric rings: stated needs → revealed jobs → underlying motivations. The triage workflow operates at the first ring (stated needs, captured in the request text). It explicitly routes high-signal items into deeper discovery work to surface the second and third rings.

### Request management

Three principles of request management, adopted here:

1. **Always acknowledge.** Every request, even ones that get a "no", gets a response. Customer silence is the fastest path to lost trust.
2. **Sometimes commit.** Commit only when the item is scored, prioritized, and on the roadmap with a date the team will actually hit.
3. **Rarely promise.** Avoid "we'll definitely build that" in any external channel until the item is funded, scoped, and started.

## Workflow

### Phase 1: Intake & normalization

For every inbound feedback item, capture a normalized record with these fields:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Internal ID |
| `channel` | yes | One of: support, sales, social, nps, in_app, exec_ask, partner, customer_interview |
| `customer_id` | yes | Anonymous OK; needed for dedup and segment analysis |
| `segment` | recommended | e.g. SMB, mid-market, enterprise, prosumer |
| `raw_text` | yes | The verbatim ask — do not paraphrase at intake |
| `received_at` | yes | ISO-8601 |
| `submitter` | yes | The internal person who logged it (Support agent, AE, PM) |
| `opportunity_area` | optional | Coarse area, populated at triage (e.g. onboarding, reporting, integrations) |

Normalization rules:

- Capture the verbatim. Paraphrasing at intake loses signal. The PM can paraphrase at triage.
- One request per record. If a customer email contains 3 asks, create 3 records.
- Do not pre-judge at intake. Even off-topic items get logged and triaged later (they are signal about channel hygiene).

### Phase 2: Triage (run `feedback_triage.py`)

The Python tool ingests the normalized intake JSON and produces:

1. **Deduplicated clusters** — items grouped by similar opportunity, even if the literal requests differ.
2. **Kano category guess** — heuristic based on keyword signals (transparent and documented; the PM should override).
3. **Categorization** — Bug / Feature / Question / Strategy.
4. **Priority score** — combined Kano weight × volume × segment × strategic-alignment.
5. **Suggested response template** — Will-build / Won't-build / Exploring, parameterized by request and customer name.

### Phase 3: Categorization

For each clustered item, categorize:

| Category | Definition | Action |
|---|---|---|
| **Bug** | Existing functionality is broken | Route to engineering bug queue, not PM backlog |
| **Feature request** | New functionality | Continue to scoring |
| **Question** | Customer needs help, not a product change | Route to support / docs; flag if recurring (it's a doc gap) |
| **Strategy** | Item implies a strategic direction (new market, new pricing model) | Route to leadership, not the backlog |

### Phase 4: Scoring

Each Feature request gets three scores:

| Dimension | Range | Source |
|---|---|---|
| **Kano category** | basic / performance / delight / indifferent / reverse | Heuristic + PM override |
| **Volume** | count of customer requests | Tool aggregates after dedup |
| **Segment weight** | enterprise=4, mid-market=2, SMB=1 (configurable) | From customer record |
| **Strategic alignment** | 0-2 | Manual; does it advance current strategic theme? |

The composite priority is:

```
priority = (kano_weight × log10(volume + 1) × max_segment_weight × (1 + strategic_alignment))
```

Where Kano weights default to:
- Basic = 4 (gaps here are existential)
- Performance = 2
- Delight = 3
- Indifferent = 0
- Reverse = -3 (negative — actively avoid building)

This is a coarse score for triage routing, not a final RICE/ICE. Items above a threshold get routed to `prioritization-frameworks/` for proper scoring.

### Phase 5: Response

Every customer who submitted a request gets a response, even for "won't build". Three response templates (in `assets/response_templates.md`):

| Template | When | Tone |
|---|---|---|
| **Will-build** | Item is scored, prioritized, on roadmap with date | Specific, dated, conservative |
| **Exploring** | Item is interesting, not yet scoped | Acknowledge, do not commit, invite follow-up |
| **Won't-build** | Item is out of scope or low-signal | Respectful, explanation, sometimes offer workaround |

The response is sent by the channel originator (support agent, AE, CSM) — not the PM directly — so the customer relationship stays with the existing owner.

### Phase 6: Feed forward

| Output | Destination |
|---|---|
| High-priority Feature requests | `prioritization-frameworks/` for RICE/ICE scoring |
| Recurring opportunity themes | `discovery/identify-assumptions/` to surface implicit assumptions |
| Top customer voices for an opportunity | `discovery/interview-synthesis/` (target list for follow-up interviews) |
| Backlog-ready items | `wwas/` or `job-stories/` for backlog format |
| Bugs | engineering bug tracker |
| Strategic items | exec channel or `c-level-advisor/` |
