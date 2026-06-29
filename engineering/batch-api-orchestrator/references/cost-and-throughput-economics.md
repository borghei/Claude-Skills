# Cost and Throughput Economics

How to reason about the money and time tradeoff when choosing between a realtime/streaming
LLM path and an asynchronous batch path. This is principle-focused and vendor-neutral —
plug your own prices into `scripts/batch_cost_estimator.py`; the defaults are placeholders.

## The ~half-cost rule of thumb

Batch APIs are typically priced at a discount to realtime — a common, rough heuristic is
about **half the per-token cost** — in exchange for asynchronous, delayed delivery. Treat
this as a starting assumption only:

- Confirm the *actual* discount your provider offers and pass it as `--batch-discount`.
- The discount usually applies to both input and output tokens, but verify.
- Some providers price prompt caching, long context, or specific models differently in
  batch vs realtime — check before extrapolating.

## What you pay for

Total cost is driven by token volume, not request count alone:

```
total_input_tokens  = requests x avg_input_tokens
total_output_tokens = requests x avg_output_tokens
realtime_cost = (total_input_tokens / 1e6) * realtime_input_price
             + (total_output_tokens / 1e6) * realtime_output_price
batch_cost    = realtime_cost * (1 - batch_discount)
savings       = realtime_cost - batch_cost
```

Implications:

- **Output tokens usually dominate** — they are priced higher and you control them less
  precisely. Tightening output length (concise schemas, max-token caps) often saves more
  than trimming the prompt.
- **Shared/system prompts** repeated across thousands of items are pure multiplied cost;
  prompt caching (where available) attacks this in both lanes.
- The batch discount scales linearly with volume, so the bigger the job, the bigger the
  absolute savings — which is exactly why large offline workloads are the prime candidates.

## Throughput vs. latency

These are different axes; don't conflate them:

- **Latency** = time until *a* result is ready. Realtime ~ sub-second to seconds; batch ~
  minutes to hours (often a completion window, not a guarantee).
- **Throughput** = items processed per unit time across the whole job. Batch lanes often
  carry separate, higher rate limits, so a million-item job can finish without exhausting
  your realtime quota or tripping rate limiting.

A job can be *high throughput* and *high latency* at once — that is the batch sweet spot:
everything finishes efficiently, just not instantly.

## Queueing and rate limits

- Realtime at scale forces you to manage concurrency, backoff, and rate-limit retries
  yourself — engineering cost that rarely shows up in the per-token price.
- Batch shifts that queueing burden to the provider: you submit, they schedule. Your job
  is chunking, idempotency, and reconciliation rather than fine-grained throttling.
- If you find yourself building a large internal queue + worker pool to push volume
  through the realtime API cheaply, that is a strong signal the work belongs in batch.

## Chunk sizing economics

- Smaller chunks = smaller blast radius, but more orchestration overhead and more
  completion events to track.
- Larger chunks = fewer moving parts, but a wholesale retry of a big chunk is expensive
  and slow.
- Size chunks so a worst-case full re-run is *affordable in both dollars and time*. Let
  the vendor's max-batch limit be the ceiling, and your retry-cost tolerance the floor.

## The break-even question

Sometimes the choice isn't obvious — a faster realtime path may be worth paying more for.
Frame it as a break-even between **cost saved** and **value of speed**:

- If results unlock revenue or a decision *now* (e.g. a launch-blocking eval), the time
  value can exceed the batch savings — pay for realtime.
- If results feed an offline index, warehouse, or report consumed later, the latency is
  free and you should bank the discount.
- For recurring large jobs, even a modest per-run saving compounds; default to batch and
  only override when a specific run is time-critical.

Rule: **let latency tolerance pick the lane, then let volume size the savings.** The
estimator encodes exactly this — an interactive `--latency-tolerance` forces a realtime
recommendation regardless of how large the savings would be.

## Worked intuition (illustrative, placeholder prices)

For 50,000 requests at 800 input / 200 output tokens each, with realtime priced at $3/1M
input and $15/1M output and a 0.5 batch discount:

- Input: 40M tokens -> $120 realtime.
- Output: 10M tokens -> $150 realtime.
- Realtime total ~ $270; batch ~ $135; savings ~ $135 (50%).

(Use your own vendor prices — these numbers exist only to show the shape of the math.)
