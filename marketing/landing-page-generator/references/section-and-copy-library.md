# Section and Copy Library

Section-by-section patterns and how each copy framework maps onto the page. Loaded from SKILL.md when writing a section.

## Page Section Library

### Hero Section

The most important section. Must communicate value in 5 seconds.

**Components:**
- Headline (primary value proposition)
- Subheadline (expand on headline, add specificity)
- Primary CTA button
- Secondary CTA (optional, lower commitment)
- Supporting visual (product screenshot, illustration, or video)
- Trust signal, only when it can be sourced (a named customer logo with permission, a rating the platform shows, one hard fact such as the price or the trial length)

**Hero Variants:**

| Variant | Layout | Best For |
|---------|--------|----------|
| Centered | Text centered, CTA below, visual below | Simple offers, clear value props |
| Split | Text left, visual right (or vice versa) | Product with strong visual/screenshot |
| Video background | Text over a muted, poster-first video with a pause control | Software or hardware with real footage; never mood footage standing in for the product |
| Minimal | Headline + CTA only, no visual | High-intent traffic, direct offers |
| Social proof hero | A real, attributed quote beside an h1 that still names the category | A named customer story the client may show |

**Hero Copy Guidelines:**
- Headline: 6-12 words, names the category and the primary benefit; never a slogan or a question
- Subheadline: 1-2 sentences, adds specificity or addresses the "how"
- CTA: Action verb + what they get ("Start my free trial")
- Supporting text below CTA: reduce friction ("No credit card required")

### Problem Section

Make the reader feel understood before pitching anything.

**Structure:**
- 2-3 pain points in the reader's language
- Each pain point is specific and recognizable
- Optional: quantify the cost of the problem ("This costs teams an average of $X per month")

### Solution / Benefits Section

Connect your product to the outcomes they want.

**Structure:**
- 3-5 key benefits (not features)
- Each benefit follows the pattern: [What it does] > [Why that matters] > [Specific outcome]
- Visual support for each benefit (icon, screenshot, or illustration)

### How It Works Section

Reduce perceived complexity to 3-4 simple steps.

**Structure:**
- Step 1: [Action] (with brief description)
- Step 2: [Action] (with brief description)
- Step 3: [Action] (with brief description)
- Optional Step 4: [Outcome] ("See results within [timeframe]")

**Rules:**
- Never exceed 4 steps (complexity kills conversion)
- Each step starts with an action verb
- Each step can be understood independently

### Social Proof Section

**Rule:** only proof you can source. Never invent a testimonial, a customer count, a logo or a rating; without real proof, show a line of plain facts (price, trial length, a count you can verify) or nothing.

**Types ranked by conversion impact:**

| Type | Impact | Example |
|------|--------|---------|
| Named testimonial with metrics | Highest | A customer quote with a measured result, the person's name and role, used with permission |
| Customer logos | High | Row of recognizable brand logos |
| Aggregate metrics | High | Real counts from your own data, uneven where real (2,847, not 3,000+) |
| Star ratings / review scores | Medium | "4.8 out of 5 on G2 (500+ reviews)" |
| Case study link | Medium | "See how [Company] achieved [result]" |
| Generic testimonial | Low | "Great product!" — John D. |

### Pricing Section

**Guidelines:**
- 2-4 tiers maximum (3 is optimal)
- Highlight the recommended tier visually
- Feature comparison shows what is included in each tier
- Enterprise tier with "Contact us" for custom needs
- Annual vs. monthly toggle if offering both
- Trust signals near pricing (guarantee, cancel anytime)

### FAQ Section

**Guidelines:**
- 5-8 questions maximum
- Questions should address real buying objections
- Answers should be direct (1-3 sentences)
- Include FAQPage schema markup for SEO

**Common FAQ questions to include:**
- How does pricing work?
- Can I cancel anytime?
- How long does setup take?
- Do you offer a free trial?
- Is my data secure?
- What integrations do you support?
- How is this different from [competitor]?

### Final CTA Section

**Structure:**
- Headline restating the core value
- 1 sentence of supporting copy
- Primary CTA button (same as hero)
- Risk reversal statement (guarantee, no CC, cancel anytime)
- Optional: one real, attributed quote or a count the client can source; nothing invented

---

## Copy Framework Application

### PAS Application to Landing Page

| Section | PAS Element | Copy Approach |
|---------|------------|---------------|
| Hero headline | Problem | Name the pain directly |
| Problem section | Agitate | Show consequences of inaction |
| Solution section | Solve | Introduce product as the answer |
| CTA | Solve | Clear action to access the solution |

**Example:**
- Hero: "Your team wastes 4 hours every week on manual reporting"
- Problem: "That is 200 hours a year — the equivalent of losing a full-time employee to spreadsheets. Meanwhile, your competitors are shipping features."
- Solution: "[Product] automates your reporting. Set it once, get reports every Monday morning."
- CTA: "Automate my reports — start free trial"

### AIDA Application to Landing Page

| Section | AIDA Element | Copy Approach |
|---------|-------------|---------------|
| Hero headline | Attention | The category and the buyer, plus the one fact that surprises; attention comes from the fact, not from a slogan |
| Benefits section | Interest | Expand with relevant details and benefits |
| Social proof | Desire | Show proof and paint the transformation |
| CTA | Action | Clear, compelling call to action |

### BAB Application to Landing Page

| Section | BAB Element | Copy Approach |
|---------|------------|---------------|
| Hero + Problem | Before | Current painful state |
| Solution + Benefits | After | Desired future state |
| How it works | Bridge | How the product gets them there |

## A/B Testing Framework

### What to Test (Highest to Lowest Impact)

1. **Headline** — The single highest-impact element. Test 2-3 variants.
2. **CTA copy and color** — Test action text and visual prominence.
3. **Hero image/visual** — Product screenshot vs. illustration vs. video.
4. **Social proof placement** — Above fold vs. below benefits.
5. **Form length** — Fewer fields vs. more qualified leads.
6. **Price display** — Annual vs. monthly default, pricing anchor.

### Testing Rules

- Test one variable at a time
- Run tests for minimum 14 days or 1,000 visitors per variant
- Calculate statistical significance (95% confidence) before declaring winner
- Document hypothesis, variants, and results for every test
- Never end a test early based on early results

### Test Documentation

```markdown
## A/B Test: [Name]
- Page: [URL]
- Hypothesis: [If we change X, then Y improves because Z]
- Control: [Current version]
- Variant: [Changed version]
- Primary metric: [Conversion rate / Click rate / Signup rate]
- Duration: [Start - End]
- Traffic per variant: [Number]
- Result: [Winner + lift + confidence]
- Learning: [What we apply going forward]
```
