# Conversational Ad Platform Specs (as of September 2026)

Every fact below was checked against the platform's own site in September 2026. These products change monthly — **re-verify on the linked page before committing budget.** Where a fact could not be confirmed on an official page, it is marked *unverified* or omitted.

---

## At a glance

| | ChatGPT Ads | Google ads in AI Overviews / AI Mode | Ads in Microsoft Copilot | Perplexity |
|---|---|---|---|---|
| **Buy directly?** | Yes — ChatGPT Ads Manager (self-serve beta) | No — served from existing Search/Shopping/PMax campaigns | No — served from existing campaigns | *Unverified* current availability |
| **Launched** | Test began 9 Feb 2026 (US); self-serve Ads Manager May 2026 | AI Overviews ads live; AI Mode ads in test/rollout; new AI Mode formats announced May 2026 | Live; new Copilot formats announced 2025-2026 | Ads experiment announced Nov 2024 |
| **Opt-out?** | n/a (you choose to run) | **No** — cannot opt out, cannot target the placement | **No** — eligible campaigns auto opted in | — |
| **Placement-level reporting?** | Yes (ChatGPT is the whole placement) | **No** segmented reporting; counted as Top ads | **No** Copilot-specific metrics | — |
| **Sensitive categories** | Health, mental health, politics excluded from ad adjacency; several categories disallowed or manually approved | Adult, alcohol, gambling, finance, healthcare, politics "and more" excluded from AI Overviews | Same policies as Bing; ads not shown in conversations flagged as harmful | — |

---

## ChatGPT Ads (OpenAI)

**Official sources:** https://openai.com/index/testing-ads-in-chatgpt/ · https://openai.com/index/our-approach-to-advertising-and-expanding-access/ · https://openai.com/index/new-ways-to-buy-chatgpt-ads/ · https://openai.com/policies/ad-policies/ · https://help.openai.com/en/collections/20001223-chatgpt-ads · https://developers.openai.com/ads · https://ads.openai.com/

| Topic | Fact (as of Sep 2026) | Source |
|-------|------------------------|--------|
| Launch | Testing began 9 Feb 2026 with logged-in adult users on the **Free and Go** plans in the US | openai.com/index/testing-ads-in-chatgpt |
| Ad-free plans | Plus, Pro, Business, Enterprise, Edu | help.openai.com "Ads in ChatGPT" |
| Who never sees ads | Accounts identified as under 18 (account info + age prediction); Temporary Chats | help.openai.com "Ads in ChatGPT" |
| Answer independence | Ads do not influence answers; labelled **Sponsored** and visually separated from the answer | openai.com announcements |
| Sensitive adjacency | Ads not eligible near sensitive or regulated topics such as health, mental health or politics; no political advertising | help.openai.com; openai.com |
| Privacy | Advertisers do not receive chats, chat history, memories, name, email, precise location or IP | help.openai.com "Ads in ChatGPT" |
| Categories | At launch mainly consumer verticals (lifestyle, household goods, local services, travel, digital products/education). Dating/sexual content, health claims, alcohol and drugs, gambling, political content disallowed; **financial services, healthcare and legal services** rolling out gradually with **manual, case-by-case approval** | openai.com/policies/ad-policies |
| Deceptive content | Ads that exaggerate results, use false endorsements or otherwise deceive are prohibited regardless of category | openai.com/policies/ad-policies |
| Buying | Self-serve **Ads Manager (beta)** since May 2026; CPC bidding and outcome-optimised bidding; natural-language campaign management via an Ads Manager plugin | openai.com/index/new-ways-to-buy-chatgpt-ads |
| Creative | Title + copy + landing page + image. OpenAI Help Center recommends **titles of 16-24 characters and copy of 32-48 characters**, distinct angles per variation, and a high volume of diverse variations | help.openai.com "Create Ads for ChatGPT" |
| Targeting | Contextual matching to the conversation; geographic targeting (country/region), platform (apps/web), custom audiences; product feeds and a Delta Feeds API for price/availability updates | developers.openai.com/ads |
| Measurement | **OpenAI Pixel** (browser) and **Conversions API** (server); static UTMs on landing URLs persist on click; dynamic macros `{campaign_id}`, `{ad_group_id}`, `{ad_id}`, `{ad_account_id}`; measurement-partner and mobile MMP integrations | developers.openai.com/ads; help.openai.com "Measure Results" |
| Markets | Expanded from the US during 2026; OpenAI announcements name Europe, the UK, India, Middle East and North Africa, Mexico, Brazil, Japan and South Korea. Check ads.openai.com for the current list per account | openai.com/index/chatgpt-ads-expands-across-europe; openai.com/index/expanding-access-to-ai-with-chatgpt-ads |
| Starting bid | Help Center guidance at time of writing suggested a starting CPC bid in the low single-digit USD range — check the current recommendation in Ads Manager rather than hard-coding | help.openai.com |

---

## Google — ads in AI Overviews and AI Mode

**Official sources:** https://support.google.com/google-ads/answer/16297775 · https://support.google.com/google-ads/answer/15910366 (AI Max for Search) · https://blog.google/products/ads-commerce/google-marketing-live-search-ads/ · https://support.google.com/google-ads/answer/7684791 (RSA limits)

| Topic | Fact (as of Sep 2026) | Source |
|-------|------------------------|--------|
| Eligible campaigns | Text and Shopping ads from existing **Search, Shopping and Performance Max** campaigns; matching requires AI-powered targeting — broad match, AI Max for Search keywordless matching, PMax, Shopping, or Dynamic Search Ads | support.google.com/google-ads/answer/16297775 |
| Matching | Both the user query **and the content of the AI Overview** are considered; the ad must be relevant to both | same |
| Opt-out / targeting | **You can't opt out** and **can't directly target** AI Overviews placements | same |
| Reporting | **No segmented reporting** for AI Overviews; ads are reported as **Top ads** | same |
| Excluded verticals | Adult, alcohol, gambling, finance, healthcare, politics "and more" | same |
| Availability | **English**, mobile and desktop, in Australia, Canada, India, Indonesia, Kenya, Malaysia, New Zealand, Nigeria, Pakistan, Philippines, Singapore and the US | same |
| AI Mode | Advertisers on PMax, Shopping and Search with broad match (incl. AI Max) are eligible for AI Mode; ads may appear below and integrated into AI Mode responses. In May 2026 Google announced tests of new AI Mode formats (conversational discovery ads, highlighted answers) and expanded Direct Offers; dates and markets "coming soon" | blog.google GML 2026 post |
| Copy limits | RSA headlines up to **30** characters, descriptions up to **90**, paths up to **15** (double-width characters count as 2) | support.google.com/google-ads/answer/7684791 |

---

## Microsoft — ads in Copilot

**Official sources:** https://learn.microsoft.com/en-us/advertising/msa-help/hlp_ba_conc_adsforcopilot · https://about.ads.microsoft.com/en/blog/post/april-2026/win-across-all-three-eras-of-the-web

| Topic | Fact (as of Sep 2026) | Source |
|-------|------------------------|--------|
| Eligible types | Multimedia ads; Product ads (Shopping and PMax); Search ads **with logo extensions or business-logo automated extensions** (incl. DSA, RSA and PMax in search placements); Property promotion ads; Tours and Activities ads | learn.microsoft.com |
| Creation | Ads are **automatically created from existing assets** (text, images) | same |
| Opt-out | All eligible campaigns are **automatically opted in; advertisers cannot opt out**; no guarantee of serving | same |
| Negatives | Negative keywords apply in Copilot exactly as on search | same |
| Reporting | **No Copilot-specific metrics** at present; search term and asset reporting available | same |
| Matching | Considers the context of the **entire conversation**, not only the last prompt; ads surface after Copilot has resolved the initial query | same |
| Brand safety | Ads not shown in conversations flagged as potentially harmful | same |
| Regulated categories | If an ad can serve on Bing it can serve in Copilot; copy is not truncated; prescription ads require specific disclaimers | same |
| Best lever | Microsoft recommends **Performance Max** to maximise Copilot exposure; add logo and image extensions | same |
| New formats | **Offer Highlights** available for retail in English-speaking markets on Copilot, Edge and Bing product pages (Apr 2026); Showroom ads and Brand Agents announced; Copilot Checkout live in the US | about.ads.microsoft.com blog, Apr 2026 |

---

## Perplexity

Perplexity announced an advertising experiment in November 2024 (sponsored follow-up questions and side-of-answer paid media, US first, answers not written or edited by sponsors): https://www.perplexity.ai/hub/blog/why-we-re-experimenting-with-advertising. No current official self-serve documentation, specs or availability were found in September 2026. **Treat as unverified; contact Perplexity directly before planning spend.** The planner excludes it.

---

## Analytics — GA4 "AI Assistant" channel

**Source:** https://support.google.com/analytics/answer/9756891

GA4's default channel group includes an **AI Assistant** channel: medium exactly matches `ai-assistant`; GA4 sets medium `ai-assistant` and campaign `(ai-assistant)` when the referrer matches its list of AI assistants (examples given: ChatGPT, Gemini, DeepSeek, Copilot, Grok). **Paid clicks tagged `utm_medium=cpc` do not match this rule**, so tagging your ChatGPT Ads with `utm_medium=cpc` keeps paid traffic out of the organic AI Assistant channel — which is what you want for clean incrementality reads.
