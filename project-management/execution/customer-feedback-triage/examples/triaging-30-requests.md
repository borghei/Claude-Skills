# Example: Triaging 30 Inbound Feature Requests at Pylon

> Real-world scenario showing how to apply the feedback triage workflow end-to-end.

## Context

Pylon is a Series-A vertical SaaS for industrial-equipment service teams (~120 customers, $4M ARR). The PM (Hugo Aalto) inherited a chaotic feedback stream: support tickets, sales-call notes from a recent SKO push, NPS verbatims from a quarterly survey, in-app feedback widget submissions. The team is 8 engineers; nothing is being prioritized; an exec one-liner from the CEO last week ("can we just build the workflow Acme has?") is starting to bend the roadmap.

Hugo has 4 hours blocked to run a feedback triage sweep over 30 inbound items collected in the last 6 weeks. The goal: convert raw requests into opportunities, categorize against Kano, dedupe, score, and produce a routing decision per item plus acknowledgment responses to customers.

## Inputs

- 30 raw feedback items in `inbox.json` across 4 channels (support 11, sales 8, NPS 6, in-app 5)
- Pylon's current Kano snapshot (in `references/kano-baseline.md`)
- The `feedback_triage.py` tool
- Quarterly roadmap context: focus area is "self-serve workflows for technicians"

## Applying the skill

1. **Normalized intake** by piping all 30 items through `feedback_triage.py --normalize` to standardize fields (channel, severity, customer-tier, ARR).
2. **Cagan separation**: every item rewritten from Request -> Opportunity. Several requests collapsed into the same opportunity (4 separate "PDF export" requests = one opportunity "share status with stakeholders who don't use Pylon").
3. **Kano category** assigned by Hugo + a CSM, 5 min per item.
4. **RICE scored** at the opportunity level (not request level) -- this is the key Cagan move.
5. **Routed each item** to one of: backlog (build), discovery (investigate), watch (track signal), decline (politely).
6. **Drafted acknowledgment responses** for all 30 customers, per the request-management principle of "always acknowledge".

Key decision quoted: *"The CEO's 'just build what Acme has' request becomes opportunity OP-7 -- routed to discovery, not to build. Sponsorship is not prioritization."*

## The artifact

````markdown
# Pylon Feedback Triage Sweep -- 2026-05-22

**PM:** Hugo Aalto
**Window covered:** 2026-04-08 to 2026-05-20 (6 weeks)
**Items in:** 30
**Items out:** 12 opportunities (after dedup), 14 backlog candidates, 8 declines, 8 watch

## Channel mix

| Channel | Count | % |
|---|---|---|
| Support tickets | 11 | 37% |
| Sales SKO notes | 8 | 27% |
| NPS verbatims | 6 | 20% |
| In-app feedback widget | 5 | 16% |

## Deduplicated opportunities

| OP | Opportunity (Cagan) | Source requests | Kano | RICE | Route |
|---|---|---|---|---|---|
| OP-1 | Share work-order status with stakeholders who don't use Pylon | 4 ("PDF export" x3, "email link to my client") | Performance | 380 | Backlog (build) |
| OP-2 | See which technician closed a job from a list view | 3 ("show tech name in queue", "filter by tech") | Basic | 220 | Backlog (build) |
| OP-3 | Re-assign a job in <3 clicks | 3 | Basic | 200 | Backlog (build) |
| OP-4 | Bulk-edit job priorities | 2 | Performance | 110 | Backlog (build) |
| OP-5 | Use Pylon offline at customer site | 5 | Delight | 320 | Discovery (deep investigate) |
| OP-6 | Slack notifications for job updates | 2 | Performance | 80 | Backlog (build) |
| OP-7 | "What Acme has" -- per CEO request | 1 (CEO + AE inference) | Unknown | n/a | Discovery (interview 6 customers; do NOT build blind) |
| OP-8 | Custom job-status taxonomy per workspace | 1 (1 enterprise, $80k ARR) | Performance | 140 | Backlog (build) |
| OP-9 | Two-way calendar sync (Google + Outlook) | 2 | Performance | 90 | Backlog (build) |
| OP-10 | Native mobile app instead of mobile web | 3 | Delight | 200 | Watch (signal only; build after offline) |
| OP-11 | White-label customer portal | 1 (highest-ARR customer, $180k) | Delight | 60 | Decline politely; suggest workaround |
| OP-12 | Voice-control job updates ("Hey Siri, mark job 14 done") | 1 | Indifferent | 12 | Decline politely |

## Item-by-item routing (selected)

### Support ticket #4471 (customer: Northwind Industrial, $32k ARR)

- **Request:** "Add a PDF export button."
- **Opportunity:** OP-1 -- share status with stakeholders who don't use Pylon
- **Kano:** Performance
- **Route:** Backlog (build)
- **Acknowledgment:**

```
Hi Maya,

Thanks for the request to add a PDF export. The underlying need you described
("send a snapshot to my customer who doesn't log into Pylon") is one we are
actively working on. The solution we're scoping is a sharable read-only link
rather than a PDF -- it stays live as the job progresses, which we think
solves the actual problem better.

We're targeting this for the Q3 release. I'll follow up when it lands.

If you'd rather have PDF specifically (not a share link), please let me know
the reason -- it'll help us scope right.

Hugo
PM, Pylon
```

### Sales SKO note #SKO-12 (prospect: Helix Field Services)

- **Request:** "We need offline mode for our technicians."
- **Opportunity:** OP-5 -- offline use at customer site
- **Kano:** Delight
- **Route:** Discovery (6 customer interviews + assumption-mapping; see `../../discovery/identify-assumptions/`)
- **Acknowledgment (to AE forwarding the deal):**

```
Hey Pat,

Offline mode came up in 5 separate notes this quarter; it's a real opportunity.
Before we commit a roadmap slot we need to understand which 'offline' --
the field tech may need read-only (just the job sheet), read-write (with
sync conflicts), or selective (downloads jobs for the route, pushes on
reconnect). These three are three different builds.

I'm interviewing 6 field-tech customers in the next 2 weeks to nail this
down. Can we set Helix expectations to 'on the roadmap, in active discovery,
no committed date'? I'd love a call with their head of ops as one of the 6.

Hugo
```

### CEO one-liner (in #product Slack)

- **Request:** "Why don't we just build what Acme has?"
- **Opportunity:** OP-7 -- unknown; needs decomposition
- **Kano:** Unknown
- **Route:** Discovery
- **Acknowledgment (1:1 with CEO):**

```
Sami,

Treating "what Acme has" as one feature would cost the team 8 weeks for
something we're not sure customers want here -- Acme's customer mix is
different from ours.

I want to do this right: in the next two weeks I'll interview 6 customers
who'd plausibly buy that workflow and come back with a 1-pager: yes / no /
deferred, with data. If yes, we plan it for Q3.

Is that timing OK?

Hugo
```

### NPS verbatim #NPS-22 ("dropped to 7 from 9 because of slow page loads")

- **Request:** "Slow page loads."
- **Opportunity:** not a feature -- a performance defect
- **Route:** Engineering (bug triage, not this workflow)
- **Acknowledgment:** auto-reply via NPS thank-you flow; CSM follow-up on the account.

### In-app feedback widget #IAF-9 (free-tier user)

- **Request:** "Add voice control."
- **Opportunity:** OP-12 -- voice-control job updates
- **Kano:** Indifferent
- **Route:** Decline politely
- **Acknowledgment:**

```
Hi Theo,

Thanks for taking the time to suggest voice control. We considered it and
decided it's not a fit for our roadmap -- the field environments most of
our customers work in are too loud for voice to reliably work, and the
keyboard / touch flow already lands jobs in under 6 seconds.

If you've got a specific situation in mind where voice would solve something
the touch flow can't, I'd love to hear it -- reply and I'll read.

Hugo
PM, Pylon
```

## RICE re-cap (opportunities scored, not requests)

| OP | Reach (monthly users affected) | Impact (1-3) | Confidence (%) | Effort (weeks) | RICE |
|---|---|---|---|---|---|
| OP-1 | 1900 | 2 | 80 | 8 | 380 |
| OP-5 | 1200 | 3 | 60 | 7 | 308 |
| OP-2 | 1100 | 2 | 100 | 10 | 220 |
| OP-10 | 800 | 2 | 50 | 4 | 200 |
| OP-3 | 1000 | 1 | 100 | 5 | 200 |
| OP-8 | 200 | 3 | 70 | 3 | 140 |
| OP-4 | 700 | 1 | 80 | 5 | 112 |
| OP-9 | 600 | 1 | 60 | 4 | 90 |
| OP-6 | 400 | 1 | 80 | 4 | 80 |
| OP-11 | 50 | 2 | 50 | 8 | 6 (decline) |
| OP-12 | 100 | 1 | 30 | 2 | 15 (decline) |

(OP-7 not scored; pending discovery.)

## Decisions for the next planning cycle

- **Build (Q3 candidates):** OP-1, OP-2, OP-3, OP-8 (= 950 RICE total)
- **Build (Q4 candidates):** OP-4, OP-9, OP-6 (= 282 RICE)
- **Discovery (in flight):** OP-5, OP-7
- **Watch:** OP-10 (revisit after OP-5 lands)
- **Declined:** OP-11, OP-12 (acknowledgments sent)

## "We heard you but said no" audit trail

Stored in Notion at `Triage Decisions` DB:

| Date | Customer | Request | Decision | Reason | Notified |
|---|---|---|---|---|---|
| 2026-05-22 | Northwind Industrial | PDF export | Build (as share link, not PDF) | Better solves underlying job | Yes |
| 2026-05-22 | Theo (free) | Voice control | Decline | Kano-indifferent; field environment poor fit | Yes |
| 2026-05-22 | $180k ARR co | White-label portal | Decline | Effort 8 weeks; small reach; workaround exists | Yes -- escalated via CSM |
| ... | ... | ... | ... | ... | ... |

## Cadence going forward

- **Daily (5 min):** Hugo skims new inbound and tags channel + ICP-fit.
- **Weekly (45 min):** Run `feedback_triage.py` on the week's items; convert to opportunities; acknowledge customers.
- **Monthly (90 min):** Re-score opportunities; update RICE; review decline audit trail.
- **Quarterly (half day):** Re-Kano the categorization; what was a Delighter last quarter may be Basic this quarter.
````

## Why this works

- Every item gets an acknowledgment -- the "always acknowledge" rule, applied uniformly across channels including the CEO.
- Cagan's separation (Request -> Opportunity) collapsed 4 PDF-export requests into one opportunity, exposing the real job.
- Kano labeling caught two items (voice control, white-label portal) that would have eaten roadmap slots if scored at the request level.
- The CEO request was routed to discovery with a 2-week timebox -- treats sponsorship as input, not a prioritization override.
- The "we heard you but said no" audit trail makes future "but I asked for X" conversations defensible.

## What's next

- Feed the build queue into [../prioritization-frameworks/](../prioritization-frameworks/) for the formal RICE re-score against existing backlog.
- Send OP-5 and OP-7 into [../../discovery/interview-synthesis/](../../discovery/interview-synthesis/) for the 6-interview deep dives.
- Pair with [../../discovery/identify-assumptions/](../../discovery/identify-assumptions/) before committing OP-5 to build.
- Use [../create-prd/](../create-prd/) to scope OP-1 (the highest-RICE item) into a v1 PRD.
- Surface the triage cadence in [../status-update-generator/](../status-update-generator/) so stakeholders see the funnel.
