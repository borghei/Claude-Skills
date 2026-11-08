# Demand Evidence Ladder

The viability verdict separates numbers that work on paper from demand that has
been shown. This reference explains what each kind of evidence proves, how to
run the cheapest test that would change the decision, and why simulated buyers
never confirm demand on their own.

## The ladder, weakest to strongest

| Rung | Evidence kind | What it proves | What it does not prove |
|------|---------------|----------------|------------------------|
| 1 | `simulated_panel` | Which objections, segments and phrases to test | That anyone will pay |
| 2 | `interviews` | The problem is real and how people describe it | Willingness to pay |
| 3 | `waitlist` (no price) | Curiosity and reach of the channel | That the price works |
| 4 | `landing_page` with price | People click through at a known price | That they complete payment |
| 5 | `presale` / deposit | People part with money at the real price | Repeat behaviour |
| 6 | `pilot` / pop-up | People buy the real product, in the real setting | Steady-state volume |

The verdict counts only rungs 4-6 with `price_shown: true` and at least the
minimum sample (default 30 people reached) as confirmed demand.

## Why a simulated panel cannot confirm demand

Language-model personas are useful for surfacing objections and wording quickly,
but they have systematic biases:

- **Agreeableness.** Generated personas tend to say yes more than real buyers.
  A panel buy rate is a ceiling, not a forecast.
- **No cost of saying yes.** Nothing leaves a simulated wallet. Real conversion
  is limited by friction, timing and competing priorities.
- **Shared priors.** Every persona comes from the same model, so their errors are
  correlated. One hundred personas are not one hundred independent samples.

A low panel buy rate is still informative: if simulated buyers who lean
agreeable still pass, real buyers will pass harder. The verdict treats a panel
below its threshold as a failed signal.

## Choosing the cheapest test that would change the decision

Start from the most sensitive driver in the economics report.

| Most sensitive driver | Test to run first | Signal to record |
|-----------------------|-------------------|------------------|
| Volume -20% | Pre-sale or pop-up at the real price | Converted / reached, first-month repeat |
| Price -10% | Two-price landing page or two pop-up days at different prices | Conversion at each price |
| Unit costs +15% | Supplier quotes with price locks | Quoted cost per unit |
| Fixed costs +10% | Lease and wage quotes in writing | Quoted monthly fixed cost |

Run the test, add it to the evidence file, and re-run the verdict. A verdict is
a snapshot of the evidence on that day, not a judgement on the founder.

## Setting thresholds

Default thresholds are deliberately conservative:

- `min_real_conversion` 5%: the share of people reached by a priced test who
  committed money. Cold traffic to a landing page converts lower than a warm
  pop-up crowd; adjust and say why.
- `min_panel_buy_rate` 25%: below this, even agreeable simulated buyers pass.
- `min_real_sample` 30: below this, one or two buyers swing the rate.
- `funding_buffer` 1.2: funding should cover the cash trough plus 20%, because
  pre-launch plans run late and over budget.

Change a threshold only with a written reason in the plan; never change one to
turn a failing check into a passing one.

## Recording evidence honestly

- Count everyone reached, not only the interested ones.
- Record `price_shown: false` for any test where the buyer did not see the real
  price at the moment of commitment.
- Keep refunds: a pre-sale with heavy refunds is weaker evidence than its raw
  conversion suggests. Subtract refunded orders from `converted`.
- Never present simulated panel answers as testimonials or customer quotes.
