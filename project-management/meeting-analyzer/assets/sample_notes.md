# Payments Platform — Weekly Working Session

**Date:** 2026-07-14 · **Attendees:** Priya S. (EM), Amara O. (staff eng), Kai T. (PM), Lena K. (data), Sam W. (eng)
**Absent:** Dev R. (PTO)

---

## Multi-currency settlement

Kai walked through the September cutover plan. Treasury still has not delivered
the reconciliation export, which is the second slip. Amara pointed out that the
ledger abstraction is now behind a flag and 3 of 11 currencies are migrated, so
the remaining risk is concentrated in reconciliation rather than in the
migration itself.

Discussion on whether to keep waiting on Treasury or build a stopgap importer.
Sam estimated the stopgap at 4-5 days. Priya pushed back on spending a week on
throwaway code; Lena noted we would need the importer anyway for the historical
backfill, so it is not throwaway.

DECISION: We will build the stopgap importer rather than continue waiting on
Treasury. Approver: Priya. It doubles as the historical backfill tool, so the
work is not wasted if the Treasury export arrives.

- Sam will scope the stopgap importer and post the estimate by 2026-07-17
- @lena to confirm the backfill schema matches the importer output by 18 Jul
- Someone should tell Treasury we are unblocking ourselves

We agreed to hold the September cutover date for now and revisit at the 28 July
session with the importer estimate in hand.

## Payout latency

p95 came down from 840ms to 610ms after the connection-pool change landed. Lena
showed the breakdown: most of the remaining tail is a single downstream
provider.

Open question: is the 610ms number stable, or is it an artefact of lower weekend
volume? Lena does not have a weekday-only cut yet.

- Lena will produce a weekday-only p95 breakdown soon
- Amara to open a ticket with the downstream provider about their timeout
  behaviour — no date agreed

Still unclear whether we need a provider-level SLA before the cutover or after.
Kai will take that to the vendor conversation next month.

## Fraud-scoring ownership

Long discussion, no resolution. Payments and Risk both believe they own the
scoring service. Priya and the Risk EM will meet separately.

TBD: whether the service moves to Risk entirely or stays shared with a defined
interface contract.

## Wrap-up

Decided to move this session from 60 to 50 minutes starting next week — the last
ten minutes have been consistently unused.

Next session: 2026-07-21.
