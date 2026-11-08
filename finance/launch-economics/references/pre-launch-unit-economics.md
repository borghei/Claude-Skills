# Pre-Launch Unit Economics

How to build the numbers for a business that has no history yet: what goes in
each cost bucket, where each number should come from, how to set a ramp you can
defend, and how to read the outputs.

## 1. Pick the unit before anything else

The unit is one sale as the customer experiences it. Everything else is priced
per unit or per month, so a vague unit poisons every downstream number.

| Business shape | Good unit | Bad unit |
|----------------|-----------|----------|
| Counter service (café, repair shop, salon) | One ticket or one service | "A customer" (one customer buys many times) |
| Delivery kitchen | One order | One menu item |
| Subscription box | One box shipped | One subscriber (mixes churn into price) |
| Service business | One billable client-month or one project | One hour, unless billed hourly |
| Product sold online | One order, average basket | One SKU, unless single-SKU |

If the average ticket varies widely, use the average ticket as the price and say
how it was estimated. A model built on the most popular item rather than the
average ticket overstates contribution by the margin difference.

## 2. The three cost buckets

**Variable cost per unit.** Anything that would not be spent if this one sale did
not happen: ingredients or parts, packaging, card processing, platform
commission, per-order courier fees, per-sale commissions. Card and platform fees
are percentages of price; convert them to money per unit at the planned price,
and remember to recompute when the price changes.

**Fixed cost per month.** Spent whether you sell one unit or a thousand within
the capacity of the setup: rent, base wages, insurance, software, loan service,
accounting. Staff who are scheduled regardless of demand are fixed, even if paid
hourly. Staff added per unit of volume (piece-rate, per-delivery couriers) are
variable.

**Startup cost.** One-off spend before the first sale: deposits, fit-out,
equipment, opening inventory, licences, launch marketing. Deposits come back
eventually, but they are cash out at the start and belong in the cash model.

Misfiling is the most common error. Putting a courier fee in fixed costs makes
break-even look better at low volume and worse at high volume. Putting base wages
in variable costs hides the fact that a slow month still pays everyone.

## 3. Source every number

Each cost line carries a `source` tag:

| Source | Meaning | Confidence |
|--------|---------|------------|
| `quote` | A written quote, lease, invoice or signed offer | Highest |
| `public` | A published price list or fee schedule anyone can check | High |
| `estimate` | Reasoned guess with the reasoning written down | Low |

The tool warns when more than half of the cost base by value is `estimate`.
Converting the three largest estimates into quotes usually moves the model more
than any other hour of work. Ask for the rent quote, the wage the founder will
actually pay, and the main supplier's price list first.

## 4. Setting a defensible ramp

The ramp is the twelve-month volume curve from opening day. It is where most
pre-launch plans quietly break, because the plan volume is copied into month 1.

Practical anchors:

- **Walk-in retail and food:** month 1 commonly lands at 30-50% of the steady
  state, reaching steady state between month 6 and month 12.
- **Delivery-only:** month 1 depends almost entirely on platform placement and
  paid promotion; model a lower start and a launch-spend line.
- **Service businesses:** volume follows the founder's existing network first,
  then referrals; month 1 is often a handful of clients.
- **Evidence beats anchors:** a pre-sale, a pop-up or a pilot gives a measured
  first-month number. Use it and record where it came from.

The tool warns when month 1 is at or above 80% of plan. That warning is not a
rule violation; it is a request for the evidence behind the number.

## 5. Reading the outputs

| Output | Question it answers | Healthy signal |
|--------|---------------------|----------------|
| Contribution per unit | Does each sale pay for itself? | Positive, and large enough that fixed costs need a realistic volume |
| Contribution margin | How much of each sale is left for fixed costs? | Depends on model: services 60%+, food 55-70%, delivery 20-40% |
| Break-even per day | How many sales a day keep the lights on? | Well below capacity, ideally under 60% of it |
| Margin at plan | What does a normal month look like at steady state? | Positive with room for the what-ifs |
| Cash needed | How deep is the hole before the business funds itself? | Covered by available funding plus a buffer |
| Payback month | When is the startup spend earned back? | Inside 12 months for most small businesses; longer needs a reason |
| Most sensitive driver | Which assumption to test first | The test plan should target this driver |

**Cash needed is the trough, not the startup cost.** Startup spend plus the
operating losses of the early months is what the founder must fund. A plan that
raises only the startup budget runs out of money in month two or three.

## 6. What-ifs and what they tell you

The tool runs four fixed stress cases on every model:

- **Price -10%:** the effect of discounting, a weaker market, or a competitor
  forcing a lower price. Hits contribution directly.
- **Volume -20%:** a slower ramp or a smaller audience than planned. Usually the
  most damaging case for high fixed-cost businesses.
- **Unit costs +15%:** supplier inflation, waste, or underestimated packaging.
  Most damaging for thin-margin businesses such as delivery.
- **Fixed costs +10%:** a higher rent or wage than expected.

If one case flips year one from profit to loss, that driver is the plan's single
point of failure. Test it before spending money: get the quote, run the pre-sale,
or sign a supplier price lock.

## 7. Improving a thin margin

Run each lever as a what-if rather than guessing its effect:

1. **Raise price** with `--price`. A small price rise often beats a large cost cut
   because the whole increase lands in contribution.
2. **Cut the largest variable cost line.** Platform commissions are the usual
   culprit in delivery models; a direct ordering channel changes the economics.
3. **Raise ticket size.** Add-ons and bundles raise the average price per unit
   without raising fixed costs.
4. **Reduce fixed costs before opening.** Smaller premises, shared kitchen,
   part-time staff until volume arrives.
5. **Shorten the ramp** with real pre-launch demand: a pre-sale moves month 1
   volume with evidence, not hope.

## 8. Tax and structure

Prices in the model are before sales tax or VAT. Where the market quotes prices
with tax included, strip the tax before entering the price, or the model counts
tax as revenue. Owner pay, payroll taxes, corporate tax and depreciation are not
modelled; the operating profit is before tax and before any owner draw beyond
the wages listed. An accountant should confirm structure, payroll costs and tax
before money moves.
