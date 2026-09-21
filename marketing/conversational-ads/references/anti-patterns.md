# Conversational Ads Anti-Patterns

Extended catalogue. The five most common are summarised in SKILL.md.

### Search Copy Pasted Into Chat
**Mistake:** Reusing keyword-stuffed RSA headlines ("Hiking Boots | Buy Hiking Boots Online") in ChatGPT creative.
**Why it happens:** It is the copy that already exists and passed review.
**Instead:** Answer-adjacent copy adds a fact the answer lacks. Rewrite per prompt cluster: "Wide waterproof boots" / "2E and 4E widths, 540 g per boot".

### Borrowing The Assistant's Voice
**Mistake:** "ChatGPT's top pick", "Copilot recommends", or formatting the ad to look like part of the answer.
**Why it happens:** Teams chase the trust the answer carries.
**Instead:** Ads are labelled Sponsored and separated from answers by design; OpenAI's ad policies prohibit false endorsements. Earn trust with specifics, not borrowed authority.

### Reading Platform ROAS As Incrementality
**Mistake:** Scaling because platform-reported ROAS looks strong in week 3.
**Why it happens:** It is the only number on the dashboard, and Google/Microsoft do not break out AI placements at all.
**Instead:** Hold out regions or time blocks from day one and decide on incremental CPA.

### Chasing A Placement You Cannot Buy
**Mistake:** Creating a separate "AI Overviews campaign" with its own budget line.
**Why it happens:** Media plans expect one line per placement.
**Instead:** On Google and Microsoft the placement is an outcome of broad match / AI Max / Shopping / PMax eligibility. Budget the underlying campaign and test the change that made you eligible.

### Feed Neglect
**Mistake:** Spending on creative while product titles lack the attributes people ask about (width, material, compatibility) and prices lag the site.
**Why it happens:** Feeds belong to e-commerce ops, ads belong to marketing.
**Instead:** Treat the feed as creative. Audit the top 50 SKUs against real prompts before launch; use delta feeds for price and availability.

### Spreading A Small Budget Across Every Assistant
**Mistake:** $3,000 split across three platforms for a four-week test.
**Why it happens:** Fear of missing the "next channel".
**Instead:** Concentrate until each arm can reach ~50 conversions. The planner flags underpowered arms and exits 2.

### Targeting Sensitive Prompts
**Mistake:** Writing copy for "symptoms", "debt help" or "lawyer near me" prompts in ChatGPT.
**Why it happens:** Those prompts have high commercial intent.
**Instead:** OpenAI does not place ads near health, mental health or political conversations, and regulated categories need manual approval. Route those to channels with explicit policies for the category.

### Changing Everything Mid-Test
**Mistake:** Swapping creatives, bids and landing pages in week 3 because early CPA looks high.
**Why it happens:** Learning-period CPAs are volatile.
**Instead:** Set a learning ceiling (target × 1.3) and a freeze window. Change inputs only between tests.

### No Paid/Organic Separation In Analytics
**Mistake:** Leaving ChatGPT Ads clicks untagged, so they mix with organic ChatGPT referrals in GA4's AI Assistant channel.
**Why it happens:** Organic referrals from ChatGPT already carry `utm_source=chatgpt.com`, which looks similar.
**Instead:** Tag paid clicks `utm_medium=cpc` with campaign macros; keep organic and paid AI traffic in separate channel rows.
