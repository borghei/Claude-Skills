# Assumption Map Template

## Context

| Field | Value |
|-------|-------|
| **Product / Feature** | |
| **Date** | YYYY-MM-DD |
| **Facilitator** | |
| **Participants** | PM: / Designer: / Engineer: |
| **Product Type** | New Product / Existing Product |
| **Categories Used** | 4 (existing) / 8 (new product) |

---

## Assumption Registry

| # | Assumption | Category | Confidence | Impact (1-10) | Risk Score | Quadrant |
|---|-----------|----------|-----------|:---:|:---:|----------|
| 1 | | Value | Low / Med / High | | | |
| 2 | | Usability | Low / Med / High | | | |
| 3 | | Viability | Low / Med / High | | | |
| 4 | | Feasibility | Low / Med / High | | | |
| 5 | | Ethics | Low / Med / High | | | |
| 6 | | Go-to-Market | Low / Med / High | | | |
| 7 | | Strategy | Low / Med / High | | | |
| 8 | | Team | Low / Med / High | | | |

**Risk Score Formula:** Impact x (1 - Confidence), where High=0.8, Medium=0.5, Low=0.2

**Quadrant Assignment:**
- **Test Now:** Impact >= 7 AND Confidence = Low or Medium
- **Proceed:** Impact >= 7 AND Confidence = High
- **Investigate:** Impact < 7 AND Confidence = Low
- **Defer:** Impact < 7 AND Confidence = Medium or High

---

## Risk Category Quick Reference

### Core 4 (All Products)

| Category | Key Question | Devil's Advocate Prompt |
|----------|-------------|------------------------|
| **Value** | Will customers want this? | "What if nobody actually has this problem?" |
| **Usability** | Can they figure it out? | "What if users cannot complete the task without help?" |
| **Viability** | Does the business case work? | "What if this costs more to maintain than it generates?" |
| **Feasibility** | Can we build it? | "What if the technical complexity is 3x our estimate?" |

### Extended 4 (New Products Only)

| Category | Key Question | Devil's Advocate Prompt |
|----------|-------------|------------------------|
| **Ethics** | Should we build this? | "What if this harms users we did not consider?" |
| **Go-to-Market** | Can we reach customers? | "What if our target segment is unreachable at viable CAC?" |
| **Strategy** | Does this align with our direction? | "What if leadership changes priorities next quarter?" |
| **Team** | Do we have the right people? | "What if the key skill gap takes 6 months to fill?" |

---

## Prioritization Matrix (Impact vs. Risk)

```
     10 ┌─────────────────┬─────────────────┐
        │                 │                 │
        │    PROCEED      │    TEST NOW     │
  I     │  (move forward  │  (experiment    │
  M     │   with tripwire)│   immediately)  │
  P   7 ├─────────────────┼─────────────────┤
  A     │                 │                 │
  C     │    DEFER        │   INVESTIGATE   │
  T     │  (accept risk)  │  (gather data)  │
        │                 │                 │
      1 └─────────────────┴─────────────────┘
        HIGH confidence    LOW confidence
        (low risk)         (high risk)
```

Place each assumption's number on the matrix above.

---

## Action Plan: Test Now Assumptions

| # | Assumption | Why High Risk | Validation Method | Owner | Timeline | Status |
|---|-----------|--------------|-------------------|-------|----------|--------|
| | | | | | | Not Started |
| | | | | | | Not Started |
| | | | | | | Not Started |

---

## Tripwires: Proceed Assumptions

| # | Assumption | Monitoring Metric | Tripwire Threshold | Review Date |
|---|-----------|-------------------|-------------------|-------------|
| | | | | |
| | | | | |

---

## Notes

*Capture reasoning, debates, and additional context from the mapping session.*
