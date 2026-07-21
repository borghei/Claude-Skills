# Cloud Posture Review — <account / subscription / project>

**Provider:** AWS / Azure / GCP
**Scope:** <accounts, regions, environments reviewed>
**Inventory export date:** YYYY-MM-DD
**Reviewer:** <name>
**Decision requested:** <e.g. approve production launch / accept residual risk / block>

---

## Executive summary

<Three sentences maximum. Lead with whether the environment is safe to run
production data in, then the single largest exposure, then what it takes to
close it.>

| Signal | Value |
|--------|-------|
| Posture score / grade | |
| Critical findings | |
| High findings | |
| Resources audited | |
| Principals reviewed | |
| Delta vs last review | |

---

## Critical findings — block until closed

| # | Resource / principal | Finding | Exposure if exploited | Owner | Due |
|---|----------------------|---------|-----------------------|-------|-----|
| 1 | | | | | |

For each critical, answer explicitly: **is it exploitable from the internet
right now, and what data is behind it?** A public bucket of marketing images
and a public bucket of customer exports are the same finding ID and completely
different incidents.

---

## Identity findings

| Principal | Tier | Finding | Escalation path? | Owner | Due |
|-----------|------|---------|------------------|-------|-----|
| | | | | | |

**Privilege-escalation paths found:** <list, or "none">

**Stale credentials to disable:** <list with last-used dates>

---

## Exposure and encryption findings

| Resource | Finding | Classification | Owner | Due |
|----------|---------|----------------|-------|-----|
| | | | | |

---

## Detection coverage gaps

| Layer | Status | Gap | Consequence in an investigation |
|-------|--------|-----|---------------------------------|
| Control-plane audit log | | | |
| Data-plane access log | | | |
| Network flow log | | | |
| Managed detection | | | |
| Log archive isolation | | | |

---

## Finding classes → preventive controls

> The point of the review. Group findings and name the guardrail that
> eliminates each class permanently, instead of listing the instances.

| Finding class | Instances | Preventive control | Where it applies | Owner |
|---------------|-----------|--------------------|------------------|-------|
| | | | | |

---

## Accepted risk

| Finding | Why accepted | Compensating control | Approver | Expires |
|---------|--------------|----------------------|----------|---------|
| | | | | |

An acceptance with no expiry date is a silent policy change. Every row needs a date.

---

## Follow-ups

- [ ] Critical findings assigned as incidents with owners
- [ ] Guardrails from the finding-class table scheduled
- [ ] Re-scan booked for +30 days; report the delta, not the absolute count
- [ ] Exceptions entered in the risk register with expiry dates
