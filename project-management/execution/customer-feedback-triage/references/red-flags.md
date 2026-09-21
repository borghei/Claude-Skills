# Red Flags: Customer Feedback Triage

> Common ways this skill's output goes wrong — concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan the triage queue, the `feedback_triage.py` output, and the response distribution before the weekly triage meeting. Each red flag shows the *bad* version next to the *good* version, anchored to Marty Cagan's Request/Opportunity/Solution separation, Noriaki Kano's model, and the acknowledge/commit/promise request-management discipline.

---

## Red Flag 1: Squeaky-wheel bias

**Symptom.** The triage queue elevates whoever submitted the most messages. One angry enterprise account submits 8 tickets and gets prioritized over 30 SMBs asking for the same thing.

**Why it's bad.** Volume of submissions does not equal volume of demand. One customer submitting 8 messages is volume 1 in the model, not volume 8. Treating it as 8 conflates frequency-of-submission with population-of-need.

**Bad example:**
> "Cluster C-014 priority score 18.7 (5 submissions from Acme Corp last week, all about CSV export). Routed to top of prioritization queue."

**Good example:**
> "Cluster C-014 priority score 4.2. After deduplication: 1 distinct customer (Acme Corp), 5 messages from the same account. Volume=1, segment_weight=4 (enterprise). Cluster C-021 priority score 8.9. After dedup: 14 distinct customers across segments — actually represents broader demand. C-021 routes ahead of C-014."

**How to catch it.** Compare `distinct_customers` to `request_count` per cluster. Ratio < 0.3 means the cluster is one shouter, not a population.

---

## Red Flag 2: Sales-driven roadmap

**Symptom.** Every closed-won deal arrives with a "promised list". The roadmap fills with one-off enterprise asks. Engineering ships features that benefit single customers.

**Why it's bad.** Sales-promised features are a contract problem dressed as a product problem. The roadmap stops representing market demand and starts representing the last sales conversation. PMs lose strategic control.

**Bad example:**
> "Q3 roadmap: 6 items. 5 are sales-channel asks. 'Acme Corp custom report builder', 'BigCo SAML claim mapping', 'Mega Inc audit log retention 7y'. Each from one customer."

**Good example:**
> "Q3 roadmap: 6 items. Each scored against >= 4 distinct customers (excluding Friends-cohort). Sales-channel asks tracked separately in a 'sales commitments' register; monthly review of gap between PM-prioritized and sales-promised. Top sales ask 'Acme custom report builder' rejected this quarter — Acme is the only customer with this need; declined in writing with workaround offered."

**How to catch it.** Per roadmap item, count distinct customers behind it. If any item has only 1 customer (and isn't strategic Anchor logo work), the roadmap is sales-driven.

---

## Red Flag 3: HiPPO override (exec-channel item jumps the queue)

**Symptom.** A VP forwards an email: "saw this from a customer, please prioritize". Within a week, it's on the roadmap, ahead of higher-scored items.

**Why it's bad.** HiPPO = Highest-Paid Person's Opinion. Exec channel is a real channel — execs do have customer context — but unilateral jumps undermine the triage discipline. Other channels' submitters learn that the legitimate process is theater.

**Bad example:**
> "VP Sales forwarded a customer feature request on Monday. PM moves it to top of Q3 roadmap on Tuesday. No volume, no scoring, no segment analysis."

**Good example:**
> "Exec-channel item logged in the intake queue as channel=`exec_ask`. Runs through the same triage as everything else. Triage shows it has 2 distinct customers (Acme + the one the VP heard from). Score 5.1 — below the median in the queue. PM responds to the VP: 'logged and triaged; not in top-10 this cycle. Here's the data; if you'd like to discuss whether to override, here's the queue.' Monthly report to leadership: exec-channel intake volume + conversion rate to roadmap."

**How to catch it.** Look at the past 6 months of roadmap adds. How many came from exec channel? If > 30% of the roadmap is exec-sourced, HiPPO is dominant.

---

## Red Flag 4: Treating Request literally

**Symptom.** A customer asks for "an export to PDF button". Engineering builds an export to PDF button. Six weeks later, customers ask for "Excel export". Then "CSV". Then "Google Sheets".

**Why it's bad.** Cagan's Request/Opportunity/Solution separation: the literal Request is rarely the right thing to build. The Opportunity is "I need to share results with people who don't have a login". The Solution might be a shareable read-only link — one build that serves all the export variants.

**Bad example:**
> "FB-2026-1042: 'Need PDF export.' Built PDF export. FB-2026-1187: 'Need Excel export.' Built Excel. FB-2026-1240: 'Need CSV.' Built CSV. FB-2026-1305: 'Need Google Sheets.' Now considering."

**Good example:**
> "FB-2026-1042 'Need PDF export' clustered with FB-2026-1187, 1240, 1305. Opportunity: 'share results with non-licensed stakeholders'. Solution options: (a) shareable read-only link; (b) email digest; (c) export library. Discovery interview with 5 customers (`discovery/interview-synthesis/`): 4 of 5 prefer shareable link over export. Built shareable link in 2 weeks; closed all 4 export requests with the same solution."

**How to catch it.** For each top cluster, read the `opportunity_label`. If it is a verb + filetype ("export to PDF"), the team is treating Request as truth. Rewrite as a job statement.

---

## Red Flag 5: No acknowledgment (the silent submitter)

**Symptom.** A customer submits feedback via the in-app widget. They never receive a response. Six months later, they don't bother submitting again.

**Why it's bad.** Acknowledgment debt is the fastest path to lost signal volume. The request-management discipline: "always acknowledge, sometimes commit, rarely promise". A non-acknowledgment teaches customers that feedback is futile. The cost compounds — next quarter, fewer customers submit.

**Bad example:**
> "Last quarter: 340 inbound feedback items. Items with acknowledgment: 120 (35%). The other 220 were logged and triaged but no customer-facing response."

**Good example:**
> "100% of inbound items acknowledged within 14 days. Distribution: 12% will-build, 28% exploring, 60% won't-build. Each customer received the appropriate template; channel originator (Support agent, AE, CSM) sent the response so the customer relationship stays with the existing owner. Quarterly acknowledgment-rate metric reported to leadership."

**How to catch it.** Acknowledgment rate. < 90% is a red flag. < 50% is a credibility crisis.

---

## Red Flag 6: Won't-build response that sounds dismissive

**Symptom.** Customer receives a one-line "thanks, not on our roadmap" reply. They post on Twitter: "Asked Company for X, got blown off."

**Why it's bad.** The customer ran a workflow imagining the company would help. Receiving a one-liner feels like rejection. The relationship loses trust at the moment the team was relying on goodwill.

**Bad example:**
> "Thanks for your feedback. This isn't on our roadmap. — The Team"

**Good example:**
> "Hi [name], thanks for taking the time to write this. I understand you're trying to [acknowledge the underlying job, in the customer's words]. We've evaluated this against our Q3 plan and decided not to build it — here's the tradeoff: [one paragraph honest explanation, e.g. 'we're focused on enterprise scale this quarter and PDF export would require backend changes that compete with that work']. In the meantime, [workaround if any, or 'we don't have a great workaround — that's a real limitation']. We may revisit in Q1 2027 based on the volume of similar requests. If there's a specific deadline this blocks you on, please reply and we'll discuss."

**How to catch it.** Read 10 random won't-build responses. If any are < 3 sentences, they read dismissive.

---

## Red Flag 7: Kano category never overridden

**Symptom.** Every cluster's Kano category is whatever the heuristic produced. PM has never overridden the tool.

**Why it's bad.** The Kano heuristic is a keyword classifier — coarse by design. Treating it as truth produces miscategorization (a Delight gets classified as Performance because the words overlap). The PM's domain judgment is what makes Kano useful; without overrides, the model degrades.

**Bad example:**
> "PM workflow: run `feedback_triage.py`; copy Kano column verbatim into the triage doc; route accordingly. No overrides recorded in 6 months."

**Good example:**
> "PM workflow: run `feedback_triage.py`; for each cluster, read the raw text and the heuristic Kano; override when judgment differs. Override log: maintained in `kano_overrides.md` with reasoning. Pattern review quarterly: 'collaborative cursors' consistently misclassified as Performance — propose heuristic tuning. Override rate: ~25% (sign of healthy domain judgment)."

**How to catch it.** Count Kano overrides per quarter. 0 = PM is rubber-stamping the heuristic.

---

## Red Flag 8: Tool output above threshold treated as final priority

**Symptom.** The Python tool flags 12 clusters above threshold 4.0. PM commits them to the roadmap directly without a downstream RICE/ICE pass.

**Why it's bad.** The triage scoring is intentionally coarse — Kano × volume × segment-weight × strategic-alignment is a *router*, not a *prioritizer*. Items above threshold need proper scoring against effort, confidence, and competing initiatives.

**Bad example:**
> "Above-threshold clusters: C-001 (12.4), C-007 (10.1), C-014 (8.9), ... 12 items. All committed to Q3 roadmap."

**Good example:**
> "Above-threshold clusters routed to `prioritization-frameworks/` for RICE scoring with effort estimates. Of 12 candidates: 5 RICE-scored above competing items, committed to Q3. 4 deferred (low effort but lower customer value than other roadmap items). 3 sent to `discovery/identify-assumptions/` — high-signal but unvalidated assumptions about feasibility."

**How to catch it.** Open the Q3 roadmap. Are items effort-estimated? If no, the triage output went straight in without prioritization.

---

## Red Flag 9: Bugs in the feature-request queue

**Symptom.** Triage scores include bug clusters; bugs compete with feature requests; engineering bug queue is separately full.

**Why it's bad.** Bugs follow a different lifecycle (triage > prioritize > fix) than feature requests. Mixing them dilutes both. The triage queue's scoring formula is not designed for bugs.

**Bad example:**
> "Triage queue includes C-008 'Login button broken on Safari' alongside C-001 'Need shareable link'. Both scored, both routed to roadmap."

**Good example:**
> "Phase 3 categorization splits Bug / Feature / Question / Strategy. Bug clusters route to engineering bug queue with severity scoring (Sev0/1/2/3); feature clusters continue to RICE scoring. C-008 routed to bug tracker with Sev 2 (Safari segment, 8% of traffic affected). C-001 routed to prioritization."

**How to catch it.** Filter the triage queue by `category`. If `bug` items have a `priority_score` and are competing with `feature_request` items, the categorization step is being skipped.

---

## Red Flag 10: Won't-build distribution under 50%

**Symptom.** Triage outputs: 50% will-build, 35% exploring, 15% won't-build.

**Why it's bad.** A healthy product roadmap is mostly "no". The cited target distribution is 10-20% will-build, 20-30% exploring, 50-70% won't-build. A 50% will-build rate means the team is committing to too much; v1.1, v1.2, v1.3 will overflow; trust erodes when promised features slip.

**Bad example:**
> "Q2 triage: 280 items. Will-build 140 (50%), Exploring 100 (35%), Won't-build 40 (15%). 'We try to say yes whenever we can.'"

**Good example:**
> "Q2 triage: 280 items. Will-build 42 (15%), Exploring 70 (25%), Won't-build 168 (60%). PM standard: 'A roadmap is what we said no to.' Each won't-build response acknowledges the underlying job and explains the tradeoff. Engineering capacity matches will-build volume."

**How to catch it.** Compute the will-build percentage. > 30% sustained = the team is over-committing.

---

## Red Flag 11: Strategy items routed back to backlog

**Symptom.** A customer suggests "you should expand to APAC" or "consider a freemium tier". Triage routes these to the feature backlog. Eight months later, an exec rediscovers it from a board memo.

**Why it's bad.** Strategy items are not features. Routing them to the backlog buries the signal. The right destination is the exec channel or `c-level-advisor/`, where they receive strategic consideration, not engineering effort estimates.

**Bad example:**
> "Cluster C-018 'expand to APAC' scored 6.2, routed to roadmap. PM: 'we can't really estimate APAC expansion in story points but we'll keep it on the list.'"

**Good example:**
> "Cluster C-018 categorized as `strategy` in Phase 3. Routed to: leadership channel + `c-level-advisor/`. Not on the feature roadmap; tracked separately as a strategic option for FY27 planning. Customer who submitted received an exploring response acknowledging the input and noting it's a strategic consideration above the PM team's scope."

**How to catch it.** Read the `category` field per cluster. If items like "expand to new market", "change pricing model", "acquire competitor" appear as `feature_request`, the strategy bucket is being skipped.

---

## Red Flag 12: Triage queue grows faster than throughput

**Symptom.** Queue has 800 items. Weekly triage processes 60. New intake is 100/week. The queue is permanently growing.

**Why it's bad.** Intake wider than throughput means most submitted feedback is never seen. Customers get auto-acknowledgments but no human attention. The team is doing intake theater. Eventually intake will collapse because customers learn the channel is silent.

**Bad example:**
> "Queue: 814 items. Last triage session processed 58. Backlog age: median 11 weeks; oldest item 14 months. No SLA on triage."

**Good example:**
> "Queue cap at 14 days' worth of intake. SLA: every item acknowledged within 14 days (auto-acknowledge at intake; human triage within 14 days). Throughput limit set: PM commits 4 hours/week to triage. If intake exceeds capacity, Support/CSM pre-categorize obvious bugs and questions before the queue hits PM. Quarterly review: intake volume vs throughput vs acknowledgment rate."

**How to catch it.** Queue age. If oldest unacknowledged item > 30 days, intake exceeds throughput.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Squeaky-wheel bias | Ratio of `distinct_customers` to `request_count` per cluster? |
| 2 | Sales-driven roadmap | How many roadmap items have only 1 distinct customer? |
| 3 | HiPPO override | What share of roadmap adds came from exec channel? |
| 4 | Treating Request literally | Does `opportunity_label` describe a job or a verb+filetype? |
| 5 | No acknowledgment | What is the 14-day acknowledgment rate? |
| 6 | Dismissive won't-build response | Are any won't-build replies < 3 sentences? |
| 7 | Kano category never overridden | How many overrides in the last quarter? |
| 8 | Above-threshold = roadmap | Are above-threshold items effort-scored or admitted as-is? |
| 9 | Bugs in feature queue | Do `bug`-categorized items have a `priority_score`? |
| 10 | Won't-build distribution under 50% | What is the will-build / won't-build ratio? |
| 11 | Strategy items in backlog | Do "expand to" / "change pricing" items appear as `feature_request`? |
| 12 | Queue grows faster than throughput | Age of oldest unacknowledged item? |

## Related Reading

- SKILL.md Troubleshooting
- references/customer-feedback-triage-guide.md
- references/kano-model-deep-dive.md
- `prioritization-frameworks/` (for proper RICE/ICE scoring downstream)
- `discovery/interview-synthesis/` (for follow-up interviews with top clusters)
- `c-level-advisor/` (for strategy-routed items)

---

## Common Traps

### Squeaky-wheel bias

The loudest customer is rarely the average customer. One enterprise account screaming for a feature does not equal demand. The volume score (count of distinct customers requesting) is the antidote; segment weight prevents under-counting enterprise asks, but does not let one enterprise ask dominate alone.

### Sales-driven roadmap

A common pattern: every closed-won deal comes with a list of "promised" features. The roadmap fills with one-off enterprise asks that benefit single customers. Mitigations:

- Sales-channel requests count toward volume only if the customer is willing to be quoted as wanting it (filters tire-kickers).
- A request with a single customer behind it scores low even with high segment weight.
- Track sales-promised features separately from PM-prioritized features; report monthly on the gap.

### HiPPO override

Highest-Paid Person's Opinion. An exec sends a one-liner request and it jumps the queue. The `exec_ask` channel is a real channel — execs do have customer context — but the request should run through the same triage as everything else. Use the response policy: acknowledge, sometimes commit, rarely promise.

### Confusing requests with discovery

A high-volume request for "X" does not mean X is the right solution. It is signal that an opportunity exists in the area of X. Discovery (interviews, prototypes, experiments) determines the actual solution. The triage routes signal into discovery — it does not replace discovery.

### Acknowledgment debt

Failing to respond to inbound requests teaches customers that submitting feedback is futile. The compounding cost is loss of signal volume — fewer customers bother submitting next quarter. Acknowledgment is non-negotiable, even for items the team will not build.

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---|---|---|
| Same customer appears in multiple clusters with different requests | Customer submitted multiple distinct opportunities; correct behavior | Confirm one record per ask is the intake rule; review whether the asks are genuinely distinct or whether the customer is fishing |
| Kano heuristic mis-categorizes a delighter as performance | The keyword heuristic is intentionally coarse | The Kano column is a starting guess; PM should override during review. Document overrides for future heuristic tuning |
| Volume score dominates over enterprise signal | Single enterprise asks have volume = 1 and lose to consumer-volume asks | Raise the segment weight for enterprise (default 4); if a single enterprise ask is strategically critical, route it via the `strategic_alignment` boost rather than overriding volume |
| Exec asks bypass triage | Cultural pattern; not a tool problem | Route every exec ask through the same intake form; report monthly on exec-channel volume and conversion to roadmap; surface the cost of HiPPO override quantitatively |
| Won't-build responses get hostile customer pushback | Tone too dismissive, or the response failed to explain the rationale | Use the Won't-build template's explanation pattern: acknowledge the underlying job, explain the tradeoff, offer the closest workaround |
| Triage queue grows faster than throughput | Intake is wider than triage capacity; PM is the bottleneck | Cap triage to a weekly batch; auto-acknowledge at intake with a 2-week response SLA; train Support/CSM to pre-categorize obvious bugs |
| Tool exits with input validation error | Required fields (`id`, `channel`, `customer_id`, `raw_text`, `received_at`) missing in JSON input | Confirm input matches the schema in Tool Reference; run `--demo` to see a valid example |

## Success Criteria

- 100% of inbound feedback items receive an acknowledgment within 14 days
- Feature-request response distribution roughly: 10-20% will-build, 20-30% exploring, 50-70% won't-build (a roadmap is mostly "no")
- Deduplication reduces raw request volume by 30-60% (varies by channel mix and product maturity)
- Sales-promised feature delta from PM-prioritized list is reported monthly to leadership
- HiPPO exec-channel items are processed through triage at the same rate as other channels; exec-channel conversion rate to roadmap is tracked
- At least one customer interview per quarter is sourced from triage clusters (closing the loop from triage to discovery)
- Triage cadence is regular: at minimum monthly, ideally weekly for active products
