# Research note: does the payments API allow idempotent retries on refunds?

**Status:** answered · **Date:** 2026-11-08 · **Question owner:** payments team
**Informs:** `docs/specs/refund-retries.md`

## Question

Can our refund worker safely retry a refund call after a timeout without risking a double
refund, and for how long does the provider remember an idempotency key?

## Answer

Yes, if every refund request carries an `Idempotency-Key` header; the provider returns the
original response for a repeated key instead of creating a second refund [1]. Keys are kept
for 24 hours, so a retry must happen inside that window or be reconciled by hand [1].

## Findings

- The refund endpoint accepts the `Idempotency-Key` header on POST requests [1].
- A repeated key with a different request body is rejected with HTTP 409 rather than processed [1][2].
- Our current client library sets the header only for charges, not for refunds [3].
- The client library added refund support for idempotency keys in its 4.2 release [4].
- A widely shared blog post claims keys last seven days, which contradicts the provider docs [5].

## Inference

The worker should generate one key per refund intent and persist it before the first call,
because a key generated per attempt defeats the protection. This follows from [1] and [3]
but is our design conclusion, not a provider statement.

## Open questions

- Does the 24-hour window restart on each retry, or run from the first request? The docs do not say; ask provider support.

## Sources

[1] https://docs.example-payments.com/api/idempotency (accessed 2026-11-08)
[2] https://docs.example-payments.com/api/errors#409 (accessed 2026-11-08)
[3] src/payments/client.py at commit 4f9e2c1, function `post_refund`
[4] https://github.com/example-payments/client-python/releases/tag/v4.2.0 (v4.2.0)
[5] https://medium.com/@someone/idempotency-keys-explained (accessed 2026-11-08) — secondary, contradicted by [1]
