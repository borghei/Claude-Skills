# Prototype Brief: <hypothesis ID and name>

<!-- A prototype brief is the prompt/spec you hand to an AI app builder, AI design tool or
     AI coding assistant. Write it BEFORE generating anything. One brief per variant. -->

## 1. What we are trying to learn
- **Hypothesis:** We believe <target user> will <behavior> because <reason>.
- **Uncertainty type:** <desirability | usability | feasibility | viability>
- **Pre-set threshold:** <e.g. at least 5 of 6 participants complete task 2 unassisted>
- **Kill criterion:** <what result makes us stop or pivot>

## 2. Fidelity rung
- <F1 prompted mock | F2 clickable | F3 working, synthetic data | F4 working, real data (approval ref)>
- **Why this rung and not a cheaper one:** <one sentence>

## 3. Generation prompt (paste into the tool)

```text
Role: You are building a throwaway prototype to test one hypothesis. It will not ship.

Users: <persona, context of use, device, accessibility needs>
Job: <the job the user is trying to get done, in their words>

Build exactly these screens / states:
1. <screen> - <what must be on it> - <the one action that matters>
2. <screen> - ...
3. Error / empty state for <case> (needed because task <n> exercises it)

Data: use only the synthetic data below. Do not invent real company names, people or
payment details. <paste or describe the synthetic dataset>

Constraints:
- Platform: <mobile web | desktop web | native-like>
- Visual style: <existing design system tokens or "plain, neutral, unbranded">
- Accessibility baseline: labelled controls, visible focus, text contrast that meets WCAG 2.2 AA
- Do not add features not listed above. Do not add login.

Out of scope: <the things that would tempt the tool to over-build>
```

## 4. Variants
| Variant | What differs | Which solution it represents |
|---------|--------------|------------------------------|
| A | <...> | <...> |
| B | <...> | <...> |

## 5. Test script
- **Participants:** <n> from <segment>, recruited via <channel>; not colleagues, not friends
- **Framing line (read aloud):** "This is an early prototype. Some things will not work. We are testing the design, not you."
- **Tasks (goal-based, no UI words):**
  1. <"You have three expenses waiting. Deal with the one that breaks policy.">
  2. <...>
- **Measures per task:** unassisted success (y/n), time, errors, where they hesitated
- **Commitment ask (desirability only):** <waitlist, pilot sign-up, calendar slot, pre-order>

## 6. Guardrails checklist
- [ ] No real customer or employee data in the tool (or approval ref: <...>)
- [ ] No production secrets, API keys or internal URLs in prompts or code
- [ ] Tool terms (data retention, training on inputs, output ownership) checked
- [ ] Prototype labelled "PROTOTYPE - NOT FOR PRODUCTION" in the UI and repo README
