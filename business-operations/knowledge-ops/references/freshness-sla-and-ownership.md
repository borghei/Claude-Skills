# Freshness SLAs and Document Ownership

Content decays. The question is not whether to let it decay but which decay you can tolerate,
and the answer differs by two orders of magnitude between an on-call runbook and a 2021 retro.
Uniform review policies fail because they generate more review work than any organisation will
actually do, so nothing gets reviewed and the policy becomes decorative.

---

## Tiering

### Tier definitions

| Tier | Test | Review SLA | Stale at | Share of a typical KB |
|------|------|-----------|----------|----------------------|
| **Critical** | Someone acts on it under time pressure, and being wrong causes harm | 90 days | 120 days | 5-10% |
| **Core** | People rely on it to do their job correctly, but not urgently | 180 days | 270 days | 20-30% |
| **Reference** | Consulted occasionally; wrong content causes annoyance, not damage | 365 days | 540 days | 30-40% |
| **Archive** | Historical record only; nobody acts on it | Never | Never | 25-40% |

### The tiering test

Ask one question: **"If this page were wrong for six months, what would happen?"**

- Someone would take a harmful action → Critical
- Someone would do their job badly and not know → Core
- Someone would be mildly inconvenienced → Reference
- Nothing → Archive

Note what this test does not use: traffic. A high-traffic FAQ is Reference. A rarely-read
incident runbook is Critical. Tiering by popularity is the most common tiering mistake, and
it systematically under-protects exactly the pages whose failure is expensive.

### Canonical Critical-tier content

On-call and escalation runbooks; incident severity definitions; security incident procedure;
access provisioning and revocation; payroll and benefits processes; regulated procedures under
audit scope; anything with a legal retention obligation; disaster recovery. If your Critical
tier is more than about 10% of the KB, the tier has been diluted and the 90-day SLA will not
be met.

---

## Ownership

### The one non-negotiable rule

**An owner is a named person.** Not a team, not an alias, not a distribution list, not a
rotating role without a current occupant.

Review notifications sent to a group are read by nobody — every member assumes another member
will handle it, and the mail is filtered within a month. This is the most reliable finding in
knowledge-base operations, and it is why the auditor flags alias-shaped owner values as
findings rather than treating them as owned.

Record the team as a secondary field for routing when the person leaves. But the notification
goes to a human.

### What an owner is accountable for

1. **Accuracy** at the review interval for their tier
2. **Deciding the page's fate** at review time: keep, update, merge, or archive. "Keep as-is"
   is a valid, common outcome and should take under ten minutes
3. **Answering questions** the page generates, or routing them
4. **Handing over explicitly** when they change role — an unhanded-over page is unowned

What an owner is **not** accountable for: writing all the content, being the subject expert,
or fielding every question personally.

### Ownership assignment sprint

For an unowned KB, this is the highest-value week of work available and it precedes all
content work.

1. Run the auditor and export unowned pages with traffic.
2. Sort by traffic descending. Take the top 50.
3. Propose an owner for each from the page's git or edit history — the last substantive editor
   is right about 70% of the time.
4. Send each proposed owner their list with an opt-out: "you are now the owner of these three
   pages; reply if that is wrong." Opt-out gets 5-10× the acceptance of opt-in.
5. Anything nobody accepts after two rounds is a deletion candidate. That non-acceptance is
   real information about whether the page matters.

### Coverage targets

| Tier | Named-owner coverage target |
|------|----------------------------|
| Critical | 100%. A Critical page without an owner is an open risk item |
| Core | 90% |
| Reference | 60% — the tail here is genuinely low-value |
| Archive | 0% required |

---

## Review workflow

A review that requires an hour will not happen. Design it to take ten minutes.

### The ten-minute review

The owner receives a notification with the page, its tier, and its age, and answers three
questions:

1. **Is anything on this page now wrong?** If no → re-date, done.
2. **Is anything missing that readers keep asking about?** If yes → add it or note it.
3. **Does this page still deserve to exist?** If no → merge or archive.

Roughly 60% of reviews end at question 1. Designing for that case is what makes the SLA
achievable; designing every review as a rewrite is what makes review policies collapse.

### Batching

Batch Reference-tier reviews annually by domain rather than trickling them individually — one
scheduled afternoon per domain per year, with the owner group in a room. Batching produces
review rates several times higher than per-page notifications, because the work is scheduled
rather than interrupting.

Never batch Critical-tier reviews. Those are individual, notified, and tracked.

### Escalation

| Overdue by | Action |
|-----------|--------|
| 0-30 days | Reminder to owner |
| 30-60 days | Reminder to owner's manager |
| 60-90 days (Critical only) | Raise as a risk item; the page carries a visible "unverified" banner |
| 90+ days | Reassign ownership, or archive the page |

The visible unverified banner is the mechanism that matters. It converts a hidden risk into a
reader-visible one, which both protects the reader and creates the social pressure that
notification alone does not.

---

## Health metrics

Track four numbers quarterly. More than four and nobody looks.

| Metric | Definition | Target |
|--------|------------|--------|
| **Freshness rate** | Non-archive pages within their tier SLA | 80%+ |
| **Ownership coverage** | Non-archive pages with a named human owner | 90%+ |
| **Critical compliance** | Critical-tier pages within 90 days | 100% |
| **Page count trend** | Total live pages quarter over quarter | Flat or falling |

### Why page count should not grow

A knowledge base that grows monotonically is one where nothing is ever merged or retired, and
its search quality degrades on a predictable curve regardless of how good the new content is.
Healthy KBs add and remove at similar rates. A quarter where page count fell and freshness rose
is the best possible quarter, and it should be reported as a win rather than apologised for.

### The metric to distrust

**Total page count and total word count as achievement metrics.** They are the easiest numbers
to produce and they are inversely correlated with KB quality past a fairly low threshold. If a
documentation programme reports growth as its headline result, it is optimising the thing that
causes the failure it was chartered to fix.

---

## Decay rates by content type

Not all content decays at the same speed, and tiering by consequence (above) should be adjusted
by how fast the underlying reality moves.

| Content type | Half-life | Driver of decay | Implication |
|-------------|-----------|-----------------|-------------|
| Tool-specific how-tos with screenshots | 6-9 months | Vendor UI changes | Screenshots are the most expensive content to maintain. Prefer described steps |
| API and integration docs | 3-6 months | Release cadence | Generate from source where possible; hand-written API docs are a losing battle |
| Org and process docs | 12-18 months | Reorgs, role changes | Avoid naming individuals; name roles and link to a single source-of-truth directory |
| Runbooks | 6-12 months | Infrastructure change | Tie review to the change that invalidates them, not only to the calendar |
| Architecture overviews | 18-24 months | Slow structural change | Cheap to maintain, high value. Under-invested in most KBs |
| Policy and compliance | 12 months, or on regulation change | External change | Review trigger is regulatory, not calendar-based |
| Onboarding | 6 months | Everything above, compounded | Onboarding aggregates every other doc's decay. Review after every cohort |

**Screenshots deserve a specific policy.** They decay fastest, are the most work to update, and
their absence rarely harms comprehension for described steps. Restrict them to genuinely
ambiguous UI, and never screenshot a full page when a cropped detail will do.

**Onboarding is the canary.** It touches the most other documents, and a new joiner following
it hits every broken link and stale step in one pass. The cheapest KB health signal available
is asking each new cohort to log every point where the onboarding path failed them — this
consistently surfaces problems the tooling does not, and it costs nothing.

---

## The 90-day rescue plan

For a KB scoring under 40 — distrusted, unowned, people asking in chat. The instinct is to
start writing. Do not; you will be adding to the denominator of a search-quality problem.

### Days 1-15: measure and stop the bleeding

1. Run the auditor and the orphan detector. Record the baseline with an explicit `--as-of`.
2. Fix every dead link. Cheap, fast, and the most visible signal that someone is home.
3. Move everything that meets the Archive test out of the search index. In a neglected KB this
   is typically 30-40% of pages and it is the single largest search improvement available.

### Days 16-45: ownership

4. Take the top 50 pages by traffic. Propose owners from edit history.
5. Assign on an **opt-out** basis: "you own these three pages unless you reply." Opt-out
   achieves several times the coverage of opt-in.
6. Anything unclaimed after two rounds goes on the deletion list. Non-acceptance is real data.
7. Publish the ownership list openly. Visible ownership is what makes the next step socially
   possible.

### Days 46-70: consolidate

8. Merge duplicate-title clusters into the most-linked path. Redirect, never delete silently.
9. Delete zero-link, zero-traffic orphans outright.
10. Build or repair the hub layer: 5-12 spokes per hub, each hub owned by a named person.

### Days 71-90: verify and hand over

11. Run the first review cycle on Critical-tier pages only. Ten minutes each.
12. Re-run the auditor with the same convention. Report the delta, not the absolute.
13. Hand over the recurring cadence: monthly Critical reviews, quarterly audit, annual batched
    Reference reviews.

**Expected outcome:** page count down 25-40%, health score up 20-30 points, and — the only
result that matters — people starting to search before they ask. Note that no step in the
first 70 days involves writing new content. That is deliberate, and it is the part teams
most want to skip.
