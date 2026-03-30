---
name: launch-strategy
description: >
  Plan and execute product launches and feature announcements for SaaS and
  technology products. Covers phased launch plans (alpha, beta, GA), channel
  strategy (owned/rented/borrowed), Product Hunt playbooks, launch day
  execution, and post-launch momentum. Use when launching a new product, major
  feature, pricing change, or planning a Product Hunt launch.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: product-launch
  updated: 2026-03-09
  frameworks: phased-launch, orb-channels, product-hunt, launch-momentum
---
# Launch Strategy

**Category:** Marketing
**Tags:** product launch, feature release, Product Hunt, go-to-market, launch playbook, announcement strategy

## Overview

Launch Strategy provides the complete playbook for launching products and features that build momentum, capture attention, and convert interest into users. A product launch is not an event -- it is a campaign with pre-launch, launch day, and post-launch phases. Shipping without a launch plan is leaving growth on the table.

---

## Launch Tiers

Not every release deserves the same effort. Classify first.

| Tier | What It Is | Marketing Effort | Examples |
|------|-----------|-----------------|---------|
| **Tier 1: Major Launch** | New product, major pivot, rebrand | 4-8 weeks prep, all channels | New product launch, platform launch |
| **Tier 2: Feature Launch** | Significant new capability | 2-4 weeks prep, owned + select channels | Major feature, integration, new plan |
| **Tier 3: Update** | Improvement to existing feature | 1 week prep, owned channels only | Performance improvement, UI refresh |
| **Tier 4: Changelog** | Bug fix, minor improvement | Same day, changelog only | Bug fixes, minor UX tweaks |

The rest of this skill focuses on Tier 1-2 launches. Tier 3-4 follow a simplified version of the same process.

---

## Phase 1: Pre-Launch (4-8 Weeks Before)

### Week 8-6: Foundation

**Positioning & Messaging**
1. Define the one-sentence value prop for this launch
2. Identify primary audience segment (who cares most about this?)
3. Draft the headline you want to see in coverage
4. Answer the "so what?" question -- why should anyone care?

**Positioning Template:**
```
For [target audience] who [need/pain point],
[product/feature] is the [category]
that [key benefit].
Unlike [alternatives],
we [key differentiator].
```

**Asset Checklist:**
- [ ] Landing page copy and design
- [ ] Product screenshots / demo video
- [ ] Blog post (announcement)
- [ ] Email announcement draft
- [ ] Social media posts (per platform)
- [ ] Press release / media pitch (Tier 1 only)
- [ ] Internal FAQ for team
- [ ] Customer FAQ

### Week 6-4: Build Momentum

**Audience Warming**
- Tease the launch in social posts (building in public)
- Share behind-the-scenes development content
- Engage with potential users about the problem you are solving
- Collect early feedback from beta users

**Waitlist / Early Access**
For Tier 1 launches, consider a waitlist to build anticipation:
```
Waitlist Landing Page Elements:
1. Clear headline: what is coming
2. One-sentence description: why it matters
3. Email capture form
4. Social proof: "Join [X] others waiting"
5. Expected launch date
6. Share incentive: "Move up the list by sharing"
```

### Week 4-2: Prepare Channels

**The ORB Channel Framework**

Categorize every launch channel as Owned, Rented, or Borrowed:

| Channel Type | Definition | Examples | Control |
|-------------|-----------|---------|---------|
| **Owned** | You control the audience | Email list, blog, product (in-app), changelog | Full |
| **Rented** | You pay for access | Paid ads, sponsorships, promoted posts | High (while paying) |
| **Borrowed** | You earn access through others | Press, influencer mentions, community shares, Product Hunt | Low |

**Channel Strategy by Tier:**

| Channel | Tier 1 | Tier 2 | Tier 3 |
|---------|--------|--------|--------|
| Email (full list) | Yes | Yes | Segment only |
| Blog post | Long-form | Short-form | Changelog |
| Social media | Multi-post campaign | Single announcement | Brief mention |
| In-app notification | Yes | Yes | Optional |
| Product Hunt | If applicable | No | No |
| Press / media | Targeted pitches | No | No |
| Paid amplification | Budget allocated | Small budget | No |
| Partner co-marketing | If applicable | No | No |
| Community posts | HN, Reddit, Discord | HN maybe | No |

### Week 2-1: Final Prep

- [ ] All assets created and reviewed
- [ ] Landing page live (or ready to flip)
- [ ] Email sequences loaded and tested
- [ ] Social posts scheduled
- [ ] Team briefed on launch plan and talking points
- [ ] Analytics tracking configured for launch metrics
- [ ] Support team briefed on new feature / expected questions
- [ ] Rollback plan documented (if something goes wrong)

---

## Phase 2: Launch Day Execution

### Launch Day Checklist (Time-Boxed)

**T-2 hours:**
- [ ] Final check: landing page, links, tracking all working
- [ ] Team Slack channel open for coordination
- [ ] Support team ready

**T-0 (Launch):**
- [ ] Flip landing page / feature gate live
- [ ] Send email announcement (Segment 1: most engaged users)
- [ ] Publish blog post
- [ ] Post on social media (all platforms, staggered by 30 min)
- [ ] Submit to Product Hunt (if planned -- see PH section)
- [ ] Post in relevant communities (HN, Reddit, Discord)
- [ ] Notify partners for co-promotion

**T+2 hours:**
- [ ] Check analytics: traffic, signups, errors
- [ ] Respond to all social media comments/questions
- [ ] Send email announcement (Segment 2: broader list)
- [ ] Monitor Product Hunt ranking (if applicable)

**T+6 hours:**
- [ ] Share early results with team
- [ ] Address any support issues
- [ ] Engage with community discussion threads
- [ ] Schedule next-day follow-up content

**End of Day:**
- [ ] Document day-one metrics
- [ ] Thank early adopters publicly
- [ ] Note any issues for immediate fix
- [ ] Confirm next-day plan

### Launch Day Communication Rules

1. **Respond to everything** -- launch day is not the day to ignore comments
2. **Founder engagement** -- CEO/founders should personally reply on HN, Reddit, PH
3. **Celebrate wins publicly** -- share milestones as they happen ("500 signups in first 3 hours!")
4. **Address issues immediately** -- if something breaks, communicate before people complain
5. **Never argue** -- if someone criticizes, thank them and learn

---

## Phase 3: Product Hunt Playbook

Product Hunt is a launch channel, not a launch strategy. It works best when combined with the full ORB approach.

### PH Timeline

**Week -4: Preparation**
- Create / update Maker profile
- Engage genuinely in PH community (comment on other products)
- Build relationships with active PH hunters
- Draft listing: tagline, description, first comment, media

**Week -1: Pre-Launch**
- Confirm launch date (Tuesday, Wednesday, or Thursday -- avoid Monday/Friday)
- Prepare all PH assets:
  - Thumbnail (240x240, clean, recognizable)
  - Gallery images (1270x760, show the product, not marketing fluff)
  - Demo video or GIF (under 60s)
  - First comment (personal, story-driven, not corporate)
- Notify your network: "We are launching on PH on [date]"
- Do NOT ask for upvotes (against PH guidelines and counterproductive)

**Launch Day (12:01 AM PT)**
- Submit immediately after midnight PT (products are ranked by votes within a 24h window starting at midnight PT)
- Post first comment within 5 minutes (this is your pitch)
- Share across channels: "We launched on Product Hunt today" with direct link
- Respond to EVERY comment on PH within 30 minutes
- Engage authentically -- answer questions, thank feedback, acknowledge criticism

**First Comment Template:**
```
Hey PH! [Name] here, [role] at [Company].

We built [product] because [personal story about the problem].

[1-2 sentences about what it does and why it's different]

Here's what you get:
- [Key feature 1]
- [Key feature 2]
- [Key feature 3]

Special for PH: [offer -- extended trial, discount, early access to feature]

Would love your honest feedback. Happy to answer any questions!
```

### PH Success Metrics

| Outcome | What It Means |
|---------|---------------|
| Top 5 of the day | Strong launch, badge, homepage visibility |
| Top 10 of the day | Good launch, still gets homepage traffic for 24h |
| Below top 10 | Minimal PH-specific value, but launch content still works elsewhere |
| Product of the week/month | Significant ongoing PH traffic |

---

## Phase 4: Post-Launch Momentum (30 Days)

The launch is not over on day one. Most of the value comes from sustained post-launch activity.

### Week 1 (Days 2-7)

- [ ] Publish follow-up content: "What we learned from launching"
- [ ] Share metrics publicly if impressive: "1,000 signups in 48 hours"
- [ ] Create comparison pages: [Product] vs [Competitor A], vs [Competitor B]
- [ ] Reach out to people who engaged on launch day for testimonials
- [ ] Fix any issues reported on launch day

### Week 2 (Days 8-14)

- [ ] Publish case study or early user story
- [ ] Create interactive demo or product tour
- [ ] Submit to relevant directories and lists (G2, Capterra, AlternativeTo)
- [ ] Pitch guest posts to relevant blogs / newsletters
- [ ] Run retargeting ads to launch day visitors who did not convert

### Week 3-4 (Days 15-30)

- [ ] Publish "roundup" email to full list with launch highlights + social proof
- [ ] Create SEO-optimized content around launch keywords
- [ ] Analyze full launch funnel: what worked, what did not, what to repeat
- [ ] Document launch playbook for next time (what you would do differently)
- [ ] Plan next feature launch using learnings

---

## Launch Metrics

### Pre-Launch Metrics

| Metric | Target | Source |
|--------|--------|--------|
| Waitlist signups | 500+ for Tier 1 | Landing page |
| Email list growth | 10%+ increase | Email platform |
| Social engagement on teaser content | 2x normal | Platform analytics |

### Launch Day Metrics

| Metric | Target | Source |
|--------|--------|--------|
| Landing page visitors | 5x normal daily | GA4 |
| Signup/conversion rate | 5-15% of visitors | Product analytics |
| Social shares/mentions | 50+ | Social monitoring |
| Product Hunt rank | Top 5 | Product Hunt |

### Post-Launch Metrics (30 day)

| Metric | Target | Source |
|--------|--------|--------|
| Total signups attributed to launch | 2-5x monthly average | Attribution |
| Activation rate of launch signups | Match or exceed normal cohort | Product analytics |
| Press/blog mentions | 3+ organic mentions | Google Alerts |
| SEO keyword rankings | Ranking for launch keywords | Search console |

---

## Proactive Triggers

- Feature ship date mentioned with no marketing plan: immediately ask about launch strategy
- Waitlist or early access mentioned: design the full phased funnel, not just a landing page
- Product Hunt considered: trigger the full PH playbook with the 4-week timeline
- Post-launch silence: suggest momentum content if nothing published after day 3
- Pricing change planned: treat it as a Tier 2 launch opportunity

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **email-sequence** | Building launch announcement and post-launch onboarding sequences |
| **social-media-manager** | Coordinating social strategy around the launch |
| **content-creator** | Writing blog posts and landing page copy for the launch |
| **analytics-tracking** | Setting up tracking for launch conversion metrics |
| **ab-test-setup** | Testing launch page variants |

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Launch day traffic spike but near-zero signups | Landing page value proposition unclear or CTA buried | Audit landing page: headline must answer "what is this and why should I care" in 5 seconds |
| Product Hunt submission gets below 50 upvotes | No community warm-up, poor listing assets, or launched on wrong day | Follow 4-week PH playbook; launch Tue-Thu; ensure gallery images show product, not marketing graphics |
| Post-launch momentum dies by day 3 | No post-launch content plan; team assumes launch day is the end | Execute 30-day post-launch plan with follow-up content, testimonials, and retargeting |
| Email open rate below 15% on launch announcement | Subject line not compelling or list not segmented by engagement | A/B test subject lines; segment by engagement (send to most engaged first, then broader list) |
| Support team overwhelmed on launch day | Not briefed on new feature or FAQ not prepared | Include support briefing and FAQ creation in pre-launch checklist, minimum 1 week before launch |
| Metrics dashboard shows no data on launch day | Tracking not configured or UTMs not applied to launch URLs | Include tracking verification in final QA checklist, test all conversion events in staging first |

---

## Success Criteria

- Launch readiness score above 80% on readiness checker before go-live decision
- Launch day traffic at least 5x normal daily traffic
- Signup/conversion rate between 5-15% of launch day visitors
- 50+ social shares/mentions on launch day
- Product Hunt top 5 finish (for Tier 1 launches using PH channel)
- Post-launch 30-day signups at 2-5x monthly average
- Activation rate of launch cohort matches or exceeds normal cohort within 10%

---

## Scope & Limitations

**In Scope:** Phased launch planning (Tier 1-4), ORB channel strategy, Product Hunt playbook, launch day execution checklists, post-launch momentum campaigns, waitlist management, launch metrics tracking, launch readiness assessment.

**Out of Scope:** Product development and feature readiness (engineering responsibility), pricing strategy (see marketing-strategy-pmm skill), ongoing marketing operations (see marketing-ops skill), press and media relationship building (PR function).

**Limitations:** Launch success depends on product-market fit — no launch strategy compensates for a product that does not solve a real problem. Product Hunt effectiveness varies by product category; B2C and developer tools typically perform better than enterprise B2B. Post-launch metrics require 30 days minimum for meaningful assessment.

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/launch_readiness_checker.py` | Assess go/no-go readiness across positioning, assets, channels, team, tracking | `python scripts/launch_readiness_checker.py checklist.json --tier 1` |
| `scripts/launch_timeline_generator.py` | Generate week-by-week launch timeline with tasks and owners | `python scripts/launch_timeline_generator.py --date 2026-04-15 --tier 1` |
| `scripts/launch_metrics_tracker.py` | Track actual vs target metrics across pre-launch, launch day, and post-launch | `python scripts/launch_metrics_tracker.py metrics.json --demo` |
