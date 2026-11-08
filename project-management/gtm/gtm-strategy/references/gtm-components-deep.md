# GTM Components — Deep Reference

## 1. ICP (Ideal Customer Profile)

See `project-management/gtm/ideal-customer-profile` for depth. Summary
of what GTM strategy requires from ICP:

- Sharp definition (size, vertical, role, JTBD)
- Trigger event (why now)
- Reachable channels
- Budget authority
- Real workaround they pay for today

A vague ICP makes everything else vague.

## 2. Beachhead segment

Crossing the Chasm: don't try to win the whole market. Win one concentrated
segment, then expand.

### Beachhead criteria
- **Concentrated:** customers know each other, talk to each other
- **Reachable:** clear channel to find them
- **Underserved:** existing alternatives are weak
- **Important to them:** burning pain
- **Big enough:** can be a meaningful business
- **Small enough:** you can dominate it

### Examples
- Workday: HR for mid-market companies struggling with PeopleSoft
- Notion: small startup teams frustrated with Confluence + Trello mix
- Stripe: developers building SaaS who hated PayPal integration

Each was a sharp beachhead, not "all businesses."

### Bowling pin expansion
After winning the beachhead:
1. Adjacent verticals with similar needs
2. Adjacent personas in same verticals
3. Adjacent geographies
4. Adjacent product use cases

Each "pin" leverages references + learning from the previous.

## 3. Motion taxonomy

### PLG (Product-Led Growth)
- Product itself acquires, activates, monetizes
- Self-service signup → activation → upgrade
- Examples: Slack, Notion, Figma, Zapier
- Strong when: low friction, network effects, daily use, low ACV
- Weak when: high-touch needed, complex buying committee, infrequent use
- Investment: heavy product; light sales

### Sales-led
- AEs drive deals through formal process
- Typical SaaS enterprise model
- Examples: Salesforce, Snowflake, Datadog enterprise
- Strong when: high ACV, complex requirements, multiple stakeholders
- Weak when: low ACV, self-service possible
- Investment: heavy sales (AE + SE + CSM); marketing-supported

### Marketing-led (inbound)
- Content + paid + events drive demand → MQL → SQL → AE
- Classic SaaS funnel
- Examples: HubSpot, Pardot, Marketo
- Strong when: mid-ACV, content-rich category
- Weak when: undifferentiated category, no content angle
- Investment: marketing-heavy

### Channel-led
- Partners (resellers, MSPs, SIs) drive distribution
- Examples: Cisco, Microsoft, much of enterprise tech
- Strong when: wide geographic distribution, partner ecosystem exists
- Weak when: greenfield category, no partner motivation
- Investment: partner program, channel team

### Community-led / open-source
- Community drives adoption; commercial layer monetizes
- Examples: HashiCorp, GitLab, Confluent
- Strong when: category attracts community; founder credibility
- Weak when: niche category; high commercial complexity
- Investment: long ramp; significant ongoing

### Hybrid
- PLG for acquisition + sales for expansion (most modern SaaS)
- Examples: Figma, Notion, Zoom (Day 1 → enterprise)
- Complex to coordinate; motion conflicts common
- Investment: both PLG infrastructure + sales team

## 4. ACV vs motion fit

| ACV | Motion that works | Why |
|-----|-------------------|-----|
| < $1K | PLG / consumer | Sales unit economics fail |
| $1K-$10K | PLG-led + light assist | Sales overhead breaks margin |
| $10K-$50K | Marketing-led + inside sales | Need human touch but not field |
| $50K-$250K | Sales-led with marketing support | Complex buying; field sales |
| $250K+ | Enterprise sales | Multi-month cycles; strategic |
| $1M+ | Enterprise sales + execs | C-level relationships |

Cross these too far → unit economics break.

## 5. Channels by motion

### PLG channels
- Web direct + SEO (organic discovery)
- Viral / collaboration (built-in)
- App stores (mobile, browser extensions)
- Free tier as channel
- Community / forum
- Integrations (in marketplace = channel)
- Content (developer or operator audience)

### Sales-led channels
- Outbound SDR (cold outreach)
- AE outbound (warm relationships)
- Account-based marketing
- Events / conferences
- Customer references
- Partner referrals

### Marketing-led channels
- SEO + content marketing
- Paid (search, social, display)
- Webinars / virtual events
- Content syndication
- Email nurture
- Re-marketing

### Channel-led channels
- Partner program (recruit + enable)
- Marketplace (AWS, GCP, Salesforce AppExchange)
- Referral programs
- Reseller / MSP / SI

### Community-led channels
- Open-source repository
- Community events (meetups, conferences)
- Newsletter
- Podcast
- Integration ecosystem

## 6. Messaging + positioning

### Positioning statement (April Dunford)
```
For [target customer]
Who has [problem]
[Product name] is a [category]
That provides [key benefit]
Unlike [primary competitive alternative]
[Product] is [key differentiator]
```

### Hero message
The single thing on the homepage hero. Outcome-focused. Customer
recognizes themselves immediately.

Good: "Cut your SOC 2 audit prep from 6 months to 6 weeks."
Weak: "AI-powered compliance automation platform."

### Per-segment talk track
Same product; different framing per ICP:
- For SMB IT: "Skip the consultant; ship SOC 2 in 90 days."
- For mid-market CISO: "Auditor-ready evidence collection; cut close time in half."
- For enterprise CISO: "Continuous compliance across SOC 2 + ISO 27001 + custom controls."

## 7. Success metrics

### North star per motion
- PLG: weekly active companies × activation rate
- Sales-led: pipeline coverage × win rate × ACV
- Marketing-led: MQL → SQL → opportunity conversion
- Channel-led: partner-sourced revenue %

### Input metrics
For each motion, 3-5 input metrics drive the NS.

### Guardrails
- Customer satisfaction (NPS, CSAT)
- Quality of acquired customers (churn within 90 days)
- Unit economics (CAC payback)
- Brand sentiment

## 8. Launch sequence

### T-90 (3 months before launch)
- ICP locked
- Positioning v1
- Channel strategy
- Team aligned (PM + marketing + sales + CS + CEO)
- Lighthouse customer commitments started
- Press / analyst briefings scheduled

### T-60
- Sales + marketing collateral ready (deck, one-pagers, demo)
- Lighthouse customer pilot results
- Sales playbook drafted
- Pricing finalized
- Channel partners (if applicable) trained

### T-30
- Internal training (sales kickoff, all-hands)
- Lighthouse customers ready to be public
- Press kits ready
- Launch comms drafted (blog, email, social)
- Analyst pre-briefings done

### T-7
- Final comms reviewed
- PR / analyst embargoes
- Launch dashboards configured
- Customer success ready for inquiries
- Support ready for questions

### T-0 (Launch)
- Comms executed
- Sales / CS ready
- Real-time monitoring of demand

### T+7
- Demand triage (which channels are working?)
- Quick collateral fixes based on early questions
- First lighthouse customer story
- Sales coaching as cycles begin

### T+30
- First wave of customer feedback
- Iterate messaging
- Adjust channel investment

### T+90
- GTM v2 incorporating learnings
- Beachhead success metrics
- Expansion criteria for next bowling pin

## 9. Common cross-functional misalignments

### Product vs sales
- Sales pitches features not in roadmap
- Product builds features sales never sells
- Resolution: shared GTM scorecard; weekly sync

### Marketing vs sales
- Marketing generates volume; sales says quality is low
- Sales follows up randomly; marketing can't measure
- Resolution: shared MQL/SQL definition; closed-loop reporting

### CS vs sales
- Sales over-promises; CS deals with disappointed customers
- Resolution: shared deal-room reviews; CS in late-stage cycle

### Finance vs everyone
- Aggressive bookings forecasts; finance can't predict cash
- Resolution: GTM dashboard finance helps build

## 10. GTM refresh triggers

Refresh GTM when:
- Win rate dropping (positioning issue)
- CAC rising (channel issue)
- ACV stagnating (segment / motion issue)
- Churn rising (ICP fit issue)
- Competitor takes share (positioning / product issue)
- Major regulatory shift
- Major tech shift

Don't refresh:
- Just because it's been a year
- Without diagnostic of what's broken

## Appendix: motion, channel and metric tables

_Moved from SKILL.md. Rules of thumb, not standards; the ACV bands in particular vary by market._

### Motion by context

| Motion | When | Cost structure |
|--------|------|----------------|
| **PLG (product-led)** | Self-serve product; low ACV ($0-$5K); strong activation | Low CAC; high product investment |
| **Sales-led** | High ACV ($25K+); complex buying committees | High CAC; sales team needed |
| **Marketing-led / inbound** | Mid-ACV ($5K-$25K); content-driven | Medium CAC; content + ops team |
| **Channel-led** | Wide distribution via partners | Medium CAC; partner program needed |
| **Community-led** | Strong category with passionate users | Long ramp; high ongoing investment |
| **Hybrid (PLG + sales)** | PLG to capture; sales to expand | Most modern SaaS; complex to coordinate |

Don't try to run all motions Day 1.

### Channels per motion

| Motion | Primary channels |
|--------|------------------|
| PLG | Web direct, SEO, viral, content, app stores |
| Sales-led | Outbound SDR, AE outbound, events, account-based |
| Marketing-led | SEO, paid, content syndication, webinar |
| Channel-led | Partner program, marketplace |
| Community-led | Open source, community events, integrations |

### KPI focus by motion

| Motion | KPI focus |
|--------|-----------|
| PLG | Signups, activation, free-to-paid conversion, NRR |
| Sales-led | Pipeline coverage, win rate, ACV, cycle time, NRR |
| Marketing-led | MQL → SQL conversion, CPA, content engagement |
| Channel-led | Partner-sourced revenue, partner activity |

Set targets; track weekly; tune.


### Motion fit by ACV

| ACV | Likely motion |
|-----|---------------|
| < $1K | PLG; consumer-style |
| $1K-$10K | PLG-led; light sales-assist |
| $10K-$50K | Marketing-led + inside sales |
| $50K-$250K | Sales-led with marketing support |
| $250K+ | Enterprise sales-led; long cycle |

Cross these and economics break.

### Beachhead vs broad

Going broad Day 1:
- Diluted messaging
- No reference customers
- Sales motion thinly stretched
- No moat in any segment

Beachhead first:
- Win the segment
- Build reference customers
- Develop battle-tested motion
- Then expand adjacent

Geoffrey Moore: cross the chasm one bowling pin at a time.

### Channel-product fit

Each channel has product-fit assumptions:
- SEO: long content; SERP-able problem
- Paid: clear high-intent keywords; LTV > 2-3x CAC
- Outbound: defined ICP; AE can articulate value in 30 seconds
- Channel: partners economically incentivized; product fits their offering
- Community: passionate users + room to participate
- Viral: collaboration / sharing built into product

If channel-product fit is off, channel won't deliver regardless of effort.
