# Utilisation Benchmarks and Measurement

The benchmarks are only as good as the measurement. Most portfolio analyses fail before they
reach a benchmark, because they measure the wrong thing.

---

## The three seat counts

| Count | Definition | What it tells you |
|-------|-----------|-------------------|
| **Purchased** | Seats on the contract | What you pay for |
| **Assigned** | Seats allocated to a named user | What your admin has provisioned |
| **Active (30-day)** | Seats with a meaningful action in 30 days | What you actually use |

The gap between purchased and assigned is **procurement slack** — bought and never handed out.
It is politically free to cut and usually the first 5-10%.

The gap between assigned and active is **adoption failure** — handed out and never used. It is
politically expensive to cut, because every one of those seats has a name attached and that
person will object to losing it. It is also where the large money is.

### Defining "active"

"Logged in" is too weak a definition. A user who opens the app once because a notification
linked them there is not a user. Define active as a **meaningful action**: created, edited,
commented, ran a query, resolved a ticket. Most vendor admin consoles can export this; if
yours cannot, that is itself a negotiating point.

Use a 30-day window as standard. Use 90 days for genuinely episodic tools (legal, LMS,
performance-review systems) and state which window you used — comparing a 30-day figure for
one tool against a 90-day figure for another produces a conclusion that is simply wrong.

---

## Benchmarks by category

Active seats ÷ purchased seats. Below the benchmark means over-licensed.

| Category | Benchmark | Notes |
|----------|-----------|-------|
| Security / identity / secrets | 90% | Should approach universal deployment. Unused seats here are pure waste with no usage-pattern excuse |
| CRM | 85% | Defined user population. Below 80% usually means seats assigned to non-selling roles |
| Chat / messaging | 85% | If below 75%, you have leavers still provisioned — check joiner-mover-leaver hygiene |
| Support desk | 85% | Agent seats are expensive and closely tracked; low utilisation here is unusual and worth investigating |
| Developer tools / CI | 80% | Contractor churn creates genuine slack. 70-80% is acceptable in agency-heavy orgs |
| Finance systems | 80% | Small, well-defined user set. Low utilisation means over-buying at signature |
| Design tools | 70% | Editor vs viewer split matters. Check whether viewers are on full-price seats — a very common and expensive misconfiguration |
| Product analytics | 60% | Real long tail of occasional queriers. Below 40% means the tool has not landed |
| Legal / CLM | 55% | Episodic use by a small team |
| Knowledge base / wiki | 50% | Read-heavy; many readers never take a seat-consuming action. Check whether read-only access needs a seat at all |
| Whiteboard | 40% | Bursty, workshop-driven. Company-wide deployment at full seat price is almost always wrong here |
| LMS / training | 40% | Quarterly or annual cadence by design. Do not treat as waste without checking the compliance-training calendar |

### Using the benchmarks correctly

A tool below its benchmark is a **candidate**, not a verdict. Check three things before acting:

1. **Seasonality.** A performance-review tool measured in July looks abandoned and is not.
2. **Deployment stage.** A tool six weeks into rollout has not reached steady state.
3. **Licence model.** Some tools charge per editor with free viewers; the seat count you are
   measuring may already exclude the majority of users.

---

## Spend-per-head orientation

Total software spend ÷ headcount. Wide variance by sector; use as a smell test, not a target.

| Company type | Typical annual software spend per employee |
|-------------|-------------------------------------------|
| Services / consulting | $1,500 - $3,000 |
| General B2B, non-technical | $2,000 - $4,000 |
| Software company, mid-size | $3,500 - $7,000 |
| Software company, engineering-heavy | $6,000 - $12,000 |
| Regulated (financial, healthcare) | add 20-40% for compliance tooling |

Being above the range is not automatically a problem — an engineering-heavy company genuinely
buys more software per head. Being above the range **while portfolio utilisation is below
benchmark** is the combination that indicates real waste, and it is the pair worth reporting
rather than either number alone.

---

## Portfolio-level indicators

| Indicator | Healthy | Investigate |
|-----------|---------|-------------|
| Reclaimable share of total spend | Under 10% | Over 20% |
| Tools with no named owner | 0 | Any |
| Contracts auto-renewing without review | Under 20% | Over 50% |
| Categories holding 3+ tools | 0-1 | 3+ |
| Contracts with an uplift cap | Over 60% | Under 30% |
| Tools added in the last year vs removed | Roughly balanced | Added far exceeds removed |

The last row is the leading indicator. Portfolios that only ever grow accumulate exactly the
overlap and slack this skill exists to remove, and the growth rate predicts next year's audit
result better than any current-state metric.

---

## Data collection

### Minimum viable dataset

Per tool: name, category (**by the job it does**, not by department), annual cost, seats
purchased, seats assigned, seats active 30d, renewal date, notice period, auto-renew flag,
term months, owner, criticality, whether a capability alternative exists.

### Category tagging is a substitution claim

This is the most consequential and most casually made decision in the dataset. Tagging two
tools with the same category asserts that they do the same job and one could replace the other.
"Collaboration" containing a chat tool, a wiki, and a whiteboard produces a consolidation
recommendation that would migrate wiki users into a chat app — a nonsense result that follows
correctly from a nonsense tag.

Tag by job: `chat`, `knowledge-base`, `whiteboard`, `project-tracking`, `product-analytics`,
`bi`. Not by owning department and not by procurement's ledger category.

### Where the data comes from

| Field | Source | Difficulty |
|-------|--------|-----------|
| Annual cost | Finance / AP ledger | Easy |
| Renewal date, notice period, term | Contract repository | Medium — often the real blocker |
| Seats purchased | Contract or vendor admin console | Easy |
| Seats assigned | Vendor admin console | Easy |
| **Seats active 30d** | Vendor admin export or API | **Hard, and non-negotiable** |
| Criticality | Ask the owning team | Easy |

If active seat data is genuinely unavailable for a tool, SSO login logs are an acceptable
proxy — weaker, because login is not use, but far better than assigned counts. Record which
tools used the proxy so the next audit can compare like with like.

### Refresh cadence

Full portfolio audit twice a year. Renewal calendar reviewed monthly — its whole value is
catching contracts before they enter their notice window, and a quarterly review will miss
30-day notice periods routinely.

---

## Utilisation versus adoption

These are different failures with different fixes, and conflating them produces the wrong
action in one of the two cases.

| | Definition | Diagnosis | Fix |
|---|-----------|-----------|-----|
| **Utilisation** | active ÷ purchased | You bought more than you handed out | Cut seats. Purely commercial, low friction |
| **Adoption** | active ÷ assigned | You handed out seats to people who do not use it | Cutting seats does not fix this |

### Reading the pair

| Utilisation | Adoption | Diagnosis | Action |
|------------|----------|-----------|--------|
| Low | High | Over-purchased. The people with seats do use it | Cut seats to match assigned. The easiest money in the portfolio |
| Low | Low | Over-purchased *and* the tool has not landed | Question whether it should survive at all |
| High | Low | Nearly everyone has a seat, few use it | Company-wide deployment of a tool with a narrow real audience. Cut deep |
| High | High | Healthy | Negotiate on price, not volume |

The "high utilisation, low adoption" quadrant is the most commonly missed, because the headline
utilisation number looks fine. It typically indicates a tool bought for everyone that only one
department ever needed — whiteboards, LMS platforms, and note-taking tools are the repeat
offenders.

---

## Shelfware detection

Shelfware is spend on capability that is never used at all, as opposed to under-used. It hides
in places seat counts do not reach.

| Signal | What it usually means |
|--------|----------------------|
| A tool with no named internal owner | Nobody has looked at it since purchase. Check whether it is still deployed at all |
| Contract auto-renewed 3+ times with no negotiation | Renewal is running on rails; nobody has tested whether it is needed |
| Premium tier with zero use of premium-only features | Downgrade. Frequently 30-50% of the line item |
| Modules bundled "free" in year one now on the invoice | Bundle inflation converted into billed line items |
| Seats provisioned to leavers | Joiner-mover-leaver process failure. Check the whole portfolio, not just this tool |
| Tool with an active contract but no SSO traffic in 90 days | Genuinely abandoned. Verify, then terminate at notice |

**The leaver check is worth running across the whole portfolio once.** Compare provisioned
users against the current employee directory. In organisations without automated deprovisioning
this routinely finds 3-8% of all seats assigned to people who have left, and it is both a cost
finding and a security finding — which makes it far easier to get prioritised than a pure cost
finding.

### Feature-tier audit

Premium tiers are bought during the initial sale for features that were compelling in a demo
and never configured afterwards. For every tool on a premium tier, list the premium-only
features and check usage of each. If none is in use, the downgrade is available at renewal at
no operational cost, and it is usually a larger saving than any discount you would have
negotiated on the premium tier.

Vendors will warn that downgrading is hard to reverse. Ask for a written re-upgrade path at
the same rate; it is a reasonable request and it is generally granted.
