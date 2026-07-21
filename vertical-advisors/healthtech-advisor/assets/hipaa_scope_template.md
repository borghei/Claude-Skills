# HIPAA Scope and BAA Inventory — [Company Name]

Living document. Capture HIPAA scope decisions, BAA inventory, and operational compliance commitments. Revisit annually and on material product changes.

---

## Document Info

- **Owner:** [name, role]
- **Counsel (HIPAA-specialist):** [law firm + lead partner]
- **Last reviewed:** [YYYY-MM-DD]
- **Next review:** [YYYY-MM-DD]

---

## Product / Business Description

[1 paragraph: what the product does, what data it touches, who the users are, who the customers are]

---

## HIPAA Scope Determination

**Date of determination:** [YYYY-MM-DD]
**Counsel-confirmed (Y/N):** [Y]

| Question | Answer | Notes |
|----------|--------|-------|
| Does the product handle PHI? | [Y/N] | [If Y, summarize categories] |
| Are we a Covered Entity? | [Y/N] | [Why or why not] |
| Are we a Business Associate? | [Y/N] | [If Y, on behalf of which CEs] |
| Is data consumer wellness only? | [Y/N] | [If Y, document why HIPAA does not apply] |
| State laws that may apply | [list] | [California CMIA, Washington MHMD, etc.] |

---

## PHI Inventory

For each PHI flow:

| Flow | Source | Destination | PHI categories | Legal basis | Encryption (transit / rest) | Audit logging |
|------|--------|-------------|----------------|--------------|------------------------------|---------------|
| [name] | [...] | [...] | [demographics / clinical / etc.] | [TPO / authorization] | [Y/Y or details] | [Y/N] |

---

## BAA Inventory

### As Business Associate (signed with Covered Entities)

| CE | Date signed | Renewal | Special terms |
|----|-------------|---------|---------------|
| [...] | [...] | [...] | [...] |

### As Covered Entity / BA-of-BA (signed with our subcontractors)

| Subcontractor | Service | Date signed | Renewal | Special terms |
|---------------|---------|-------------|---------|---------------|
| [Cloud host, e.g., AWS] | [Hosting under BAA program] | [...] | [...] | [Covered services list] |
| [...] | [...] | [...] | [...] | [...] |

---

## Security Rule Compliance

| Safeguard | Status | Last reviewed | Notes |
|-----------|--------|---------------|-------|
| Risk analysis | [Done / In progress / Overdue] | [date] | [link to doc] |
| Workforce training | [%] complete | [date] | [vendor / internal] |
| Access controls (least privilege) | [Y/N] | [date] | [details] |
| Audit logging of PHI access | [Y/N] | [date] | [retention period] |
| Encryption in transit | [Y/N] | [date] | [TLS version] |
| Encryption at rest | [Y/N] | [date] | [key management] |
| Backup and disaster recovery | [Y/N] | [date] | [RTO / RPO] |
| Workstation security policies | [Y/N] | [date] | [details] |
| Mobile device policy | [Y/N] | [date] | [details] |
| Sub-contractor BAA flow-down | [Y/N] | [date] | [details] |
| Breach notification process | [Y/N] | [date] | [SLA per BAA] |

---

## Notable Risk Decisions

| Risk / decision | Rationale | Owner | Date | Counsel review |
|-----------------|-----------|-------|------|----------------|
| [...] | [...] | [...] | [...] | [Y/N] |

---

## Open Items

| Item | Owner | Due date |
|------|-------|----------|
| [...] | [...] | [...] |

---

## Sign-off

- [ ] Founder / CEO: [Name, date]
- [ ] Privacy / Security Officer: [Name, date]
- [ ] Counsel: [Firm, date]
