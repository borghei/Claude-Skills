---
description: Generate a SaaS health dashboard with key business metrics.
---

Build a SaaS metrics dashboard:

1. **Gather inputs** — ask for monthly data (or point to a CSV/JSON):
   - MRR per month (last 6-12 months)
   - New, expansion, contraction, and churned MRR
   - Customer counts (new, active, churned)
   - Sales and marketing spend
2. **Calculate and display:**
   - **MRR/ARR**: current and trend line
   - **MRR Growth Rate**: month-over-month and 3-month rolling average
   - **Gross Churn**: lost MRR / starting MRR
   - **Net Revenue Retention (NRR)**: (starting + expansion - contraction - churn) / starting
   - **Logo Churn**: lost customers / starting customers
   - **Expansion Revenue %**: expansion MRR as % of total new MRR
   - **LTV**: average revenue per account / monthly churn rate
   - **CAC**: total S&M spend / new customers acquired
   - **LTV:CAC Ratio**
   - **CAC Payback**: months to recover acquisition cost
   - **Magic Number**: net new ARR / prior quarter S&M spend
   - **Rule of 40**: revenue growth rate % + profit margin %
3. **Benchmark each metric** against SaaS industry standards (Bessemer, OpenView data).
4. **Traffic-light status**: green (above median), yellow (near median), red (below 25th percentile).
5. **Output** a formatted dashboard with all metrics, benchmarks, and 3 action items to improve weakest areas.
