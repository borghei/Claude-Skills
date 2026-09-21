# Platform AI-Label Policies (as of September 2026)

Platforms enforce their own AI-disclosure rules independently of the law. A platform label does **not** by itself satisfy a legal duty (Google says so explicitly), and a legal disclosure does not replace a platform's required toggle. Do both. Every row links the platform's own help or policy page — re-read it before each campaign; these pages change without notice.

## Summary table

| Platform | Organic content rule | Paid ads rule | Mechanism | Consequence of non-disclosure | Source |
|----------|---------------------|---------------|-----------|-------------------------------|--------|
| **YouTube** | Creators must disclose realistic altered or synthetic content: a real person appearing to say/do something they didn't, altered footage of a real event or place, or a realistic scene that didn't occur | Election ads follow the Google Ads political content policy (below) | "Altered or synthetic content" setting in YouTube Studio at upload; label in the expanded description; for photorealistic content a label may also appear in the player | YouTube may apply a label itself; persistent non-disclosure can lead to content removal or YouTube Partner Program suspension | https://support.google.com/youtube/answer/14328491 |
| **TikTok** | AI-generated content that is realistic must be labelled | Mandatory disclosure for ads with AI-generated or significantly AI-modified image, video or audio; misuse of a public figure's likeness without permission is restricted | AIGC label / self-disclosure toggle in Ads Manager, **or** your own clear disclaimer, caption, watermark or sticker | Undisclosed AIGC ads are **rejected or restricted** | https://ads.tiktok.com/help/article/tiktok-ads-policy-misleading-and-false-content ; https://newsroom.tiktok.com/en-us/new-labels-for-disclosing-ai-generated-content |
| **Meta** (Facebook, Instagram, Threads) | "AI info" label shown on content Meta detects as AI-generated (industry signals or self-disclosure) | Social issue, electoral or political ads: advertiser must disclose AI-created or altered media in certain cases. From 1 June 2026 Meta also uses automated detection to add information to ads created with third-party AI tools, shown under "About this ad" | Self-disclosure in Ads Manager (political); automated "AI info" on other ads | Treated as a policy violation of the political ads standard; Meta may also add labels itself | https://transparency.meta.com/policies/ad-standards/SIEP-advertising/SIEP ; https://about.fb.com/news/2026/02/meta-prepares-for-2026-us-midterms/ ; https://transparency.meta.com/governance/tracking-impact/labeling-ai-content/ |
| **Google Ads** (Search, YouTube, Display, DV360) | — | (a) **Election ads**: verified election advertisers must disclose synthetic or digitally altered content that inauthentically depicts real or realistic-looking people or events; checkbox auto-generates a disclosure on some YouTube/feed formats, otherwise add your own. (b) **All image/video ads** (from July 2026): advertisers **may** add AI labels in the creative or via the AI label setting; Google says regulations in the **EU, India and New York** require labels on certain AI-generated or edited ads | Election: "Altered or synthetic content" checkbox. General: AI label setting in Google Ads, DV360, CM360, Merchant Center, Ads Editor; in-creative labels exempt from overlay/watermark rules | Election ads without disclosure violate the political content policy; using the AI label setting does **not** guarantee legal compliance | https://support.google.com/adspolicy/answer/6014595 ; https://support.google.com/adspolicy/answer/17257106 |

Inconsequential edits (resize, crop, colour/brightness correction, red-eye removal, background edits that do not create realistic depictions of actual events) are outside Google's election-ad synthetic content rule. YouTube similarly excludes beauty filters, colour/lighting adjustments and cloning your own voice for voice-over.

## Practical rules

1. **Toggle + on-asset label for EU audiences.** Platform labels may sit in a description or an "About this ad" panel — that may not meet the EU AI Act's "clear and distinguishable at first exposure" standard for deepfakes. Put the label on the asset too.
2. **TikTok ads fail closed.** Undisclosed AIGC ads are rejected. Tick the toggle for any realistic AI footage or AI voice-over, even if you think it is minor.
3. **Political = strictest path.** Any AI-touched social-issue, electoral or political creative gets the platform checkbox on Meta and Google, plus a visible label.
4. **Do not rely on detection.** Meta and TikTok read C2PA/IPTC metadata and apply labels, but stripping metadata in your edit pipeline removes that signal, and a missing platform label is not evidence of compliance.
5. **Log the disclosure.** Keep a screenshot of the toggle and the rendered label per asset; platform audits and regulators both ask for it.

## Not covered here (verify separately)

- LinkedIn, X, Snapchat, Pinterest and Amazon Ads AI-content rules — check each platform's current help centre; this skill does not encode them.
- Microsoft Advertising — follows its own editorial policies; no AI-label rule was verified for this reference.
