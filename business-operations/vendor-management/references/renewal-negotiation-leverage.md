# Renewal and Negotiation Leverage

Where leverage comes from, when it exists, and how to use it. Risk tiering and
diligence obligations live in `vendor-risk-tiering.md`.

The core asymmetry: **the vendor knows your renewal date and has a quota tied to
it; you usually do not have it in a calendar.** Almost every recoverable point
of leverage is lost to timing rather than to negotiating skill.

---

## 1. The renewal calendar

Work backwards from the renewal date. These are the windows that matter.

| Days before renewal | Activity |
|--------------------|----------|
| 180 | Pull usage vs entitlement. Confirm the internal owner. Decide renew / renegotiate / exit. |
| 150 | If exiting or seriously renegotiating, open the alternative evaluation now — it must be real. |
| 120 | First conversation with the vendor. Signal expectations before they build the quote. |
| 90 | Notice deadline for most annual contracts. **Serve notice if there is any doubt.** |
| 60 | Negotiate on the substance: price, terms, SLAs, exit rights. |
| 30 | Close. Anything unresolved now will be resolved in the vendor's favour. |
| 0 | Renewal. |

**Serving notice is not the same as leaving.** Notice reopens the contract; it
converts an auto-renewal into a negotiation. On any contract you intend to
renegotiate, serve notice at the deadline as a matter of routine. The most common
and most expensive procurement failure is the missed notice window on an
auto-renew contract — at which point your leverage is precisely zero for another
full term, and the vendor knows it.

Track two dates per contract, never one: the renewal date and the
notice deadline. The second is the one that actually constrains you.

---

## 2. Sources of leverage, ranked

### [PROVEN] A real alternative

The only leverage that reliably moves price. "Real" means: evaluated, priced,
technically validated, and with an internal sponsor willing to switch. Vendors
distinguish a genuine alternative from a bluff almost immediately, because their
account teams see both every quarter.

Building one costs real effort — typically 3-6 weeks of evaluation. That effort
is the price of the leverage, and it is why leverage-building has to start at
day 150, not day 30.

### [PROVEN] Timing

Vendor quarter-end and fiscal year-end produce genuine discount authority that
does not exist mid-quarter. Discounts of 10-25% appear in the last two weeks of a
vendor's fiscal year that were unavailable a month earlier.

Know their fiscal calendar. Align your close to it where the timing is
compatible with your notice deadlines — never at the cost of missing a notice
window, which costs more than any quarter-end discount is worth.

### [RECOMMENDED] Multi-year commitment

Worth 10-20% off annual pricing. Trades price for flexibility, which is a bad
trade for a Tier 1 vendor you may need to exit, and a fine one for a commodity
service.

Only commit multi-year with: a price-protection clause covering renewal, an exit
clause for material SLA failure, and a cap on annual increases. Without all
three, a multi-year deal is a discount purchased with your only remaining
leverage.

### [RECOMMENDED] Volume and consolidation

Committing more spend or consolidating from a competitor buys 15-30%. Genuine
where the growth is real; be careful not to commit to seat counts you will not
reach — unused committed seats are the most expensive line item in SaaS.

### [RECOMMENDED] Reference and case-study value

Real currency for vendors selling into your segment, particularly if you are a
recognisable name or a new logo in a vertical they are targeting. Worth 5-15%,
and it costs you marketing time rather than money. Under-used because it feels
soft — but a reference commitment is a line item their marketing budget will pay
for.

### [EXPERIMENTAL] Payment terms as currency

Offering annual-upfront instead of quarterly is worth 5-10% and costs you the
cash-flow float. Occasionally the only lever available with a vendor holding firm
on list price.

Risk: prepaying a financially distressed vendor converts a service risk into a
credit risk. Check viability signals before prepaying anything material, and
never prepay more than one year to a vendor showing distress signals.

### What is not leverage

- **Complaining about price.** Every account manager hears it daily.
- **Threatening to leave without an alternative.** Transparent and it damages
  credibility for the next cycle.
- **Escalating without a specific ask.** Escalation works when it carries a
  concrete decision; without one it just annoys someone senior.
- **Loyalty.** Long tenure is a retention argument for you, not a discount
  argument. Incumbency reduces vendor risk, which is why long-tenured accounts
  are frequently priced *higher*, not lower.

---

## 3. What to negotiate beyond price

Price is the most visible term and often not the most valuable. A 5% discount on
a $200K contract is $10K; an uncapped annual increase clause can cost multiples
of that over three years.

| Term | Why it matters | Target |
|------|---------------|--------|
| Annual increase cap | Uncapped uplift is the most common hidden cost | CPI, or 3-5% maximum |
| Price protection at renewal | Prevents the year-2 correction | Locked, or capped |
| SLA credits | Makes the SLA mean something | Meaningful tiers, not 2% gestures |
| Termination for convenience | Converts a term contract into optionality | 30-90 day notice |
| Termination for SLA failure | Exit without penalty when service degrades | Defined breach threshold |
| Data export format | Determines whether exit is possible at all | Open, documented, tested |
| Subprocessor change notice | Your data moving without your knowledge | 30 days, with objection right |
| Seat true-down rights | Lets you reduce, not just add | At renewal, without penalty |
| Support response commitments | Support quality is what you actually consume | Tiered by severity, with credits |
| Assignment on acquisition | Your terms surviving their sale | Consent required, or exit right |

**Seat true-down is the most valuable and least-requested term.** Almost every
SaaS contract permits adding seats mid-term and forbids reducing them. Negotiating
a true-down right at renewal costs the vendor little at signature and saves
10-20% at every subsequent renewal.

---

## 4. Making SLAs mean something

Most SLAs are decorative. A 99.9% uptime commitment with a 2% service credit
means the vendor pays $400 on a $20,000 quarter for an outage that cost you far
more. The credit is not a remedy; it is a rounding error priced into their model.

Structural fixes:

| Problem | Fix |
|---------|-----|
| Credits too small to matter | Tier them: 5% / 10% / 25% by severity |
| Credits capped too low | Negotiate the cap up; below 20% of period fees it is theatre |
| Credits require you to claim | Make them automatic, or diarise the claim — unclaimed credits are the norm |
| Only uptime is measured | Add response time, resolution time, and support quality |
| No consequence for repeat failure | Add a termination right after N breaches in M periods |
| Measurement is the vendor's | Agree the measurement method and get the raw data |

**The termination-on-repeat-breach right is the term that changes vendor
behaviour.** Credits are a cost of doing business; losing the account is not.
Three severe breaches in four quarters granting a no-penalty exit converts the
SLA from decoration into an actual control.

### Reading SLA performance

- **Trend beats incident.** One bad quarter is noise; three declining quarters is
  a pattern and belongs in the business review with the full series shown.
- **A permanently green SLA is measuring the wrong thing.** If every metric has
  been met for two years, the targets are below what the vendor delivers
  anyway — renegotiate the targets, not the credits.
- **Measure availability on the error budget, not the percentage.** Missing 99.9%
  by half a point sounds trivial and is nearly six times the permitted downtime.

---

## 5. Negotiation sequence

1. **Know your position first.** Usage vs entitlement, actual value delivered,
   switching cost, and your genuine walk-away point. Enter without these and you
   are negotiating against yourself.
2. **Decide the outcome you want** before the first conversation: renew as-is,
   renew cheaper, restructure terms, consolidate, or exit.
3. **Signal early.** At day 120, tell them what you expect. A vendor who learns
   at day 30 that you want 20% off has already booked the renewal at list.
4. **Ask for everything at once.** Sequential asks train the vendor to hold
   concessions back. One prioritised list, once.
5. **Trade, do not concede.** Every give gets a get — multi-year for price
   protection, reference for discount, prepay for true-down rights.
6. **Get the paper early.** Verbal agreement at day 40 with redlines starting at
   day 20 means signing whatever is on the table at day 5.
7. **Record what you learned** for next cycle: what worked, their fiscal
   calendar, who had authority, what they conceded last.

---

## 6. Exit execution

When the decision is to leave, sequence matters more than speed.

| Step | Detail |
|------|--------|
| 1. Confirm the exit clause | Notice period, format, recipient. Serve it correctly — informal notice is frequently disputed. |
| 2. Export and verify data | Before announcing. Verify it opens and is complete; history and attachments are the usual casualties. |
| 3. Map the integrations | Every downstream system consuming this vendor's data. This list is always longer than expected. |
| 4. Run parallel | Overlap the old and new for at least one full business cycle. |
| 5. Confirm deletion | Written confirmation of data destruction, including from subprocessors. |
| 6. Close the commercials | Final invoice, unused prepay, and credits owed. |

**Export and verify before announcing the exit.** Cooperation declines sharply
once a vendor knows they have lost the account, and a support queue you are no
longer a priority in is a bad place to discover the export is incomplete.

Budget 2-3x the estimated time for a Tier 1 exit. The estimate is always built on
the data you know about, and the overrun always comes from the integrations and
history nobody documented.
