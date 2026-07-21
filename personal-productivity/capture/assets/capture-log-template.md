# Capture Log

One line per capture. Do not organise, prioritise, or edit while capturing —
that happens at the weekly processing pass.

**Format:** `- [YYYY-MM-DD] [source] <noun + verb>`

The date drives staleness detection. The source reveals which inbox leaks.
Both should be automated if your tool allows it; if not, the date matters more
than the source.

---

## Inbox

- [2026-07-21] [inbox] Reply to Dana about the contract redline
- [2026-07-21] [voice] Call the dentist to move Thursday's appointment
- [2026-07-20] [browser] https://example.org/attention-residue — method for measuring switch cost, cite in the focus doc
- [2026-07-20] [meeting] Ask Priya whether she wants to own the migration doc

---

## Capture quality reminder

Minimum viable capture = **the thing + what you intend to do to it**.

| Instead of | Write |
|---|---|
| `taxes` | `Gather 2026 receipts for the accountant — needed before Aug 15` |
| `pricing` | `Draft three pricing-page headline options` |
| `follow up with landlord` | `Email the landlord asking when the boiler inspection is scheduled` |
| a bare URL | the URL plus one clause saying why you saved it |

Ten extra characters now saves two minutes of reconstruction later. You do not
need a perfect phrase — you need a noun and a verb.

---

## Converting to JSON for the scripts

The scripts read either this markdown (bullet lines) or JSON. For the full
feature set — staleness, source breakdown — use JSON:

```json
{
  "items": [
    {"id": "C1", "text": "Reply to Dana about the contract redline",
     "captured_at": "2026-07-21", "source": "inbox"}
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | No | Auto-assigned from line number if absent |
| `text` | Yes | The capture itself |
| `captured_at` | No | `YYYY-MM-DD`; without it, ageing analysis is skipped |
| `source` | No | Free text; drives the source-leak breakdown |

Never record priority or a self-assigned due date at capture time. Priority is
relative to a list you cannot see in the moment, and invented due dates create
false urgency that erodes trust in every real deadline on the list.
