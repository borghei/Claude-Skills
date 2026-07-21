---
title: Storage Tiering Review
author: Platform Engineering
date: 2026-07-21
status: draft
---

# Storage Tiering Review

This memo evaluates whether moving cold object storage to an infrequent-access
tier is worth the retrieval-latency cost. It covers the current spend profile,
three candidate policies, and a recommendation.

[TOC]

## Current state {#sec:current}

Object storage is 41% of the platform bill and grows about 6% month over month.
Roughly **72%** of stored bytes have not been read in the last 90 days, but that
cold set still sits on the standard tier at the full rate.

Access is heavily skewed. The top 3% of objects absorb most reads, and the tail
is effectively archival. See [@fig:access] for the distribution.

![Read frequency by object age, 90-day window](figures/access-distribution.png){#fig:access}

> The tail is not uniform. A small set of compliance exports is read rarely but
> under a hard deadline when it is read at all.

## Candidate policies {#sec:policies}

Three policies were modelled against 12 months of access logs.

| Policy | Trigger | Monthly saving | First-byte latency |
|--------|---------|----------------|--------------------|
| A: conservative | No read in 180 days | $8,400 | 15-40 ms |
| B: balanced | No read in 90 days | $19,100 | 15-40 ms |
| C: aggressive | No read in 30 days | $27,600 | 3-5 hours |

Table: Modelled outcomes per tiering policy {#tbl:policies}

Policy C moves objects to the archive class, which is why its latency figure is
in hours rather than milliseconds.[^retrieval] The saving is real but it changes
the failure mode from *slow* to *unavailable for the length of a restore*.

### Cost model assumptions

1. Storage rates held flat for the projection window.
2. Retrieval volume grows in line with the trailing six-month average.
3. Early-deletion charges apply to anything re-tiered within 30 days.

The third assumption matters more than it looks: a policy that flaps objects
between tiers pays the minimum-duration charge twice.[^flap]

## Recommendation {#sec:recommendation}

**Adopt Policy B.** It captures 69% of the theoretical saving from [@tbl:policies]
while keeping first-byte latency inside the range the API gateway already
tolerates, so no caller changes.

Policy C is the tempting number and the wrong choice. Compliance exports live in
the cold tail described in [@sec:current], and a multi-hour restore against a
regulator deadline is not a tradeoff worth $8,500 a month.

Implementation is a lifecycle rule plus a `retain-standard` tag for the
compliance prefix:

```yaml
lifecycle:
  - id: cold-to-ia
    filter: { tagMissing: retain-standard }
    transition: { days: 90, class: INFREQUENT_ACCESS }
```

---

[^retrieval]: Archive-class retrieval is billed per request *and* per gigabyte;
    the bulk restore tier is cheapest but has the longest window.
[^flap]: Minimum storage duration is 30 days on the infrequent-access class.
    An object moved out and back within that window is charged for the full
    30 days twice.
