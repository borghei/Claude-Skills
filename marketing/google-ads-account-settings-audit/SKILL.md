---
name: google-ads-account-settings-audit
description: Audits Google Ads account and campaign settings to uncover hidden spend leaks from search partners, Display expansion, broad location intent, auto-apply recommendations, and mismatched bid strategies. Use when auditing a Google Ads account, reviewing campaign settings, onboarding a new client account, or troubleshooting wasted spend and out-of-area traffic.
version: 2.0.0
updated: 2026-11-22
domain: marketing
tags: [google-ads, ppc, paid-search, account-audit, marketing-analytics]
---

# Google Ads Account Settings Audit

Identifies silent configuration defects in Google Ads accounts—such as Search Partners, Display expansion, presence-or-interest location targeting, and auto-apply recommendations—and prices each defect by the actual ad spend flowing through it.

## Audit Workflow

### Step 1: Verify Data Sources and Coverage
The agent checks available structural and performance datasets (from live connectors such as Coupler.io MCP or exported Google Ads structural/performance tables).
- Structural tables required: `campaigns`, `campaign_criteria`, `bidding_strategies`, `campaign_budgets`, and `accounts`.
- Performance tables required: 30 to 90 complete days of campaign and network-level performance ending on the last complete day.
- The agent explicitly states the coverage verdict before running analysis, noting which checks cannot be executed if specific structural tables (such as `campaign_criteria` or `bidding_strategies`) are missing.

**Validate:** Confirm the structural snapshot date, performance window dates, account currency, and explicit list of available vs. missing tables before proceeding.

### Step 2: Join Structural Settings with Performance Spend
The agent filters out paused and removed campaigns that recorded zero impressions during the performance window, then joins active campaign configurations to the 30–90 day spend data.
- Rebuilds all conversion rates, CTRs, and CPAs from raw totals rather than averaging pre-calculated rate columns.
- Isolates direct network spend (e.g., Search Partners vs. Google Search) where network-split data exists, rather than attributing 100% of campaign spend to a single toggle.
- Ranks every configuration defect strictly by the total spend exposed to it.

**Validate:** Confirm every flagged defect is paired with an exact spend figure and percentage share of total account spend, with zero unverified estimates.

### Step 3: Evaluate Core Configuration Defects (Cheapest-Fix-First)
The agent inspects the account across seven configuration areas in priority order:
1. **Network and Expansion Settings:** Checks if Search Partners, Display Network expansion on Search campaigns, or automatic placement expansion are enabled, comparing partner conversion rates against core Google Search inventory.
2. **Location Targeting Intent:** Checks whether location targeting is set to *Presence or interest* rather than *Presence: People in or regularly in your targeted locations*, corroborating with user-location spend reports where available.
3. **Bid Strategy Alignment:** Verifies that target-based Smart Bidding strategies (Target CPA, Target ROAS) have targets set and meet minimum conversion thresholds (at least 15 conversions in 30 days for Target CPA; 30+ for Target ROAS). Notes that changing a bid strategy resets the learning phase.
4. **Budget Structure and Pacing:** Identifies shared budgets masking constrained high-performing campaigns and campaigns capped by budget while beating CPA/ROAS targets.
5. **Ad Rotation and Delivery Schedule:** Flags indefinite ad rotation paired with Smart Bidding and ad schedules restricting delivery during high-converting hours.
6. **Conversion Windows and Counting:** Compares click-through conversion windows against actual conversion lag to detect premature undercounting.
7. **Automated Changes:** Checks whether auto-apply recommendations are active and quantifies the spend governed by automated changes.

**Validate:** Confirm all seven areas are categorized into either the Defect List, Passed List, or Not-Checked List so no setting is left ambiguous.

### Step 4: Deliver the Structured Audit Report
The agent compiles the findings into a clear diagnostic report containing:
- **TL;DR:** Total defect count, total spend exposed to defects, and the single highest-spend configuration fix.
- **Defect Table:** Ranked by spend exposed, showing Campaign/Scope, Setting Name, Current Value, Recommended Value, Exposed Spend, and Evidence.
- **Passed List:** Settings explicitly verified as properly configured.
- **Not-Checked List:** Settings unreadable from the provided tables or API limitations.
- **Actionable Recommendations:** Exact location in Google Ads UI to apply each fix, flagging any change that triggers a Smart Bidding learning reset.

**Validate:** Confirm the report includes the structural snapshot date, performance window dates, currency, and at least one concrete next-step question tailored to the highest-spend finding.

## Concrete Example

**Scenario:** Onboarding audit for *Apex Plumbing Leeds* (local B2B/B2C service provider), analyzing a 60-day window (Sept 1 – Oct 30, 2026) with £14,200 total spend.

- **Finding #1 (Highest Spend Exposure — £10,082 / 71% of spend):** Three core Search campaigns (`Search - Emergency Plumber`, `Search - Boiler Repair`, `Search - Leak Detection`) have Location Intent set to *Presence or interest*. User-location data shows £2,410 (23.9%) was spent on clicks from users physically outside West Yorkshire. **Fix:** Switch location option to *Presence* in Campaign Settings > Locations > Location options.
- **Finding #2 (£3,900 exposed spend):** Search Partners is enabled across all active Search campaigns. Network segmentation shows Search Partners converting at 1.8% (£112 CPA) versus 5.9% (£34 CPA) on Google Search. **Fix:** Uncheck *Include Google search partners* in Campaign Settings > Networks.
- **Passed:** Auto-tagging is enabled; Target CPA bid strategy on `Search - Emergency Plumber` has 48 conversions in 30 days (above the 15-conversion learning threshold).
- **Not Checked:** Auto-apply recommendation history (not exposed in the provided campaign export).

## Anti-Patterns

- **Never present exposed spend as guaranteed recoverable savings:** Spend flowing through a setting (e.g., £3,900 on Search Partners) represents total exposure, not pure waste. The agent must distinguish between exposed spend and projected net savings.
- **Never audit paused or zero-impression campaigns as active defects:** Paused legacy campaigns often retain outdated defaults; including them clutters the report and distorts priority ranking.
- **Never mark unreadable settings as "Passed":** If `campaign_criteria` or auto-apply logs are unavailable, the agent must place those checks in the **Not-Checked List** rather than assuming compliance.
- **Never recommend bid strategy changes without warning about learning resets:** Switching from Maximize Clicks to Target CPA or altering targets significantly resets algorithmic learning; this operational cost must be stated alongside the recommendation.
- **Never average pre-calculated rate columns:** The agent must always compute CTR, conversion rate, and CPA from summed clicks, conversions, and cost totals.