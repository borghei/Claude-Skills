# Expense Categorization Guide

A short, practical guide to categorizing receipts so a tax filing or board-meeting expense report doesn't fall apart at the last minute. Defaults map to **US Schedule C** buckets — adapt for your jurisdiction.

> **Disclaimer:** This skill helps you organize receipts. It is not tax, accounting, or legal advice. Confirm bucket assignments with a licensed accountant in your jurisdiction before filing.

---

## Standard Expense Categories

| Category | Typical vendors | Tax bucket (US Schedule C line) |
|----------|----------------|----------------------------------|
| Software / SaaS | GitHub, Vercel, Slack, Notion, AWS | Office expense (line 18) or Other expenses (line 27a) |
| Advertising & Marketing | Google Ads, Facebook Ads, mailing tools | Advertising (line 8) |
| Travel | Airlines, hotels, Uber, train | Travel (line 24a) |
| Meals & Entertainment | Restaurants, food delivery | Deductible meals (line 24b) — typically 50% |
| Office & Supplies | Paper, ink, office furniture | Office expense (line 18) |
| Equipment | Laptops, monitors, phones (capitalizable) | Depreciation (line 13) — see Section 179 |
| Professional Services | Lawyers, accountants, agencies | Legal & professional services (line 17) |
| Banking & Fees | Wire fees, FX fees, processor fees | Other expenses (line 27a) |
| Contract Labor | Freelancers, contractors (1099) | Contract labor (line 11) |
| Utilities | Internet, phone, business utilities | Utilities (line 25) |
| Rent | Office rent, coworking | Rent or lease (line 20b) |

---

## Mapping a New Vendor

When a vendor shows up that isn't in `category_rules.json`:

1. **What does the vendor sell?** Use the dominant offering, not a corner-case use.
2. **Is it a one-time or recurring charge?** Recurring SaaS is "Software". One-off equipment under your capitalization threshold is "Office & Supplies", above is "Equipment".
3. **Personal-use mix?** If a card processed both personal and business charges, only categorize the business portion. Keep evidence (receipts) — the categorization is not the proof.
4. **Add a rule for next time.** Open `assets/category_rules.json`, add the vendor name keyword to the right rule's `match` list, save. Next month's run picks it up automatically.

---

## Recurring Confusion Points

### Subscriptions used personally and professionally
Examples: Spotify, Netflix, ChatGPT Plus.
- If the subscription was opened on the business and serves business use (e.g., research, demos), it can be a business expense.
- If it's a hybrid (you also use it personally), most jurisdictions require an apportionment.
- When in doubt: don't categorize as business; ask your accountant.

### Capital expenditure vs. expense
Equipment over a threshold (often $2,500 in the US under de minimis safe harbor, but check current limits) typically must be **depreciated**, not expensed in full year-of-purchase.
- Laptop for $1,200: usually expensed.
- Server rack for $20,000: usually depreciated.
- Section 179 election may allow full expensing for small businesses — confirm with an accountant.

### Refunds and chargebacks
Treat as **negative expenses in the original category**, not as income. The script reads any negative-amount row as a refund.

### FX fees
On foreign-currency cards, the FX fee line is often a separate transaction.
- Categorize FX fees under "Banking & Fees".
- Keep them out of the underlying transaction's bucket.

### Mixed receipts (e.g., business meal that included gifts)
Split into separate rows in your CSV before processing — the script can't split a single row.

---

## Writing Good Rule Keywords

The script does case-insensitive substring match. Tips:

- Use the **shortest unique substring** of the vendor name. "github" matches "GitHub Inc.", "GitHub Sponsors", "github.com" all at once.
- **Avoid generic words** that match many vendors. A keyword like "card" will catch credit card fees and gift cards alike.
- **Order matters within a rule's match list** — first match wins, but order across *rules* is the bigger lever. Put more specific rules higher.

---

## When to Stop Tuning

Once you're under 5% uncategorized per month, stop adding rules and just override the long-tail manually. Rule maintenance has diminishing returns.

---

## Common Mistakes

- **Annual catch-up.** Doing a year of bookkeeping in March is how categorization mistakes get baked in.
- **No evidence kept.** Categorization without receipts won't survive an audit. Keep PDFs / photos in a separate folder organized by month.
- **Mixing currencies.** Convert to your home currency at month-end FX *before* running the categorizer.
- **Trusting the bucket label.** "Meals" in this guide assumes US 50% deduction; other jurisdictions differ. Double-check your country.
- **Forgetting personal-card business expenses.** If you paid for a business expense on a personal card, it still counts — track separately and reimburse yourself or expense via owner's draw.
