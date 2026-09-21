# Disclosure Decision Tree

Walk every asset through these gates in order. Stop at the first "REMOVE". Otherwise collect every "DISCLOSE" and apply all of them — they stack (legal + platform + endorsement).

```
START: one asset
│
├─ Q1. Is it a review, testimonial or endorsement?
│   ├─ Was it written by AI, a vendor, or anyone other than a real person
│   │  describing their own real experience, and shown as a customer review?
│   │     └─ YES → REMOVE (FTC 465.2, EU UCPD Annex I 23c, UK DMCC). No label cures this.
│   ├─ Was an incentive conditioned on positive (or negative) sentiment?
│   │     └─ YES → REMOVE affected reviews; fix the programme (FTC 465.4)
│   ├─ Insider (employee, officer, agent, their family)?  → DISCLOSE relationship in the review (FTC 465.5)
│   ├─ Any material connection (payment, free product, discount, affiliate)?
│   │     └─ YES → DISCLOSE in the endorsement itself, clear and conspicuous (FTC 255; UK DMCC; EU UCPD)
│   └─ Endorser is a virtual influencer? → DISCLOSE brand relationship ("#ad") and that the persona is virtual
│
├─ Q2. How much did AI contribute?
│   ├─ none / assistive (spelling, colour, crop, background clean-up) → no AI label; go to Q6
│   └─ partial / generated → continue
│
├─ Q3. Is it image, audio or video that a viewer could take as real (a "deep fake" of a
│       person, object, place, entity or event)?
│   ├─ EU audience → DISCLOSE on the asset at first exposure (AI Act Art. 50(4))
│   │     └─ Evidently artistic/satirical/fictional? → DISCLOSE in a non-disruptive way (end card, caption)
│   ├─ New York audience + paid ad + synthetic performer → DISCLOSE synthetic performer (NY law)
│   └─ India audience → expect platform label; add visible "AI-generated" label
│
├─ Q4. Is it text published to inform the public on matters of public interest
│       (news-like, policy, health, safety, finance, elections)?
│   ├─ EU audience, no documented human review + editorial responsibility → DISCLOSE (Art. 50(4))
│   └─ Human review + editorial responsibility → no label required; KEEP review evidence
│
├─ Q5. Is it an AI system people interact with (chatbot, voice agent)?
│   └─ EU → DISCLOSE "you're talking to an AI" from the first interaction unless obvious (Art. 50(1))
│
├─ Q6. Platform rules (apply regardless of Q2-Q5 legal outcome)
│   ├─ YouTube + realistic AI → tick "altered or synthetic content"
│   ├─ TikTok + realistic AI (esp. ads) → AIGC toggle or own clear disclaimer
│   ├─ Meta / Google + political/social issue/election + AI → platform AI checkbox
│   └─ Google Ads image/video + EU/India/NY audience + AI → AI label setting or in-creative label
│
└─ Q7. Are you the PROVIDER of the generator (you offer an AI creation tool to others)?
    └─ EU → machine-readable marking of outputs (Art. 50(2)); legacy systems from 2 Dec 2026
```

## Risk levels used by `disclosure_checker.py`

| Level | Meaning | Default gate |
|-------|---------|--------------|
| **high** | Statutory duty or prohibition with fines/civil penalties, or a platform rule that rejects the ad | Fails (exit 2) when unresolved |
| **medium** | Platform labelling expectation, provider-side duty, or artistic-work disclosure | Passes by default; fail with `--fail-on medium` |
| **low** | Exception claimed — evidence must be kept | Informational |

## Tie-breakers

- **Unsure whether it is "realistic"?** Label it. Over-labelling costs a little trust; under-labelling costs fines and ad rejection.
- **Unsure whether text is "public interest"?** Put it under documented editorial review — that both improves quality and removes the text duty.
- **Multiple regions?** Apply the strictest disclosure everywhere unless you run region-specific creative.
