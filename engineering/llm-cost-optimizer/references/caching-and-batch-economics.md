# Caching & Batch Economics

Token counts and static per-token prices (see [llm-pricing-guide.md](llm-pricing-guide.md))
tell you the cost of a single naive request. They do **not** capture the four levers that
dominate real production bills: prompt caching, batch processing, reasoning effort, and
structured-output overhead. This guide is model-agnostic and principle-focused — plug your
own provider's published multipliers and prices into the math below.

> All numbers in examples are placeholders. Use **your** measured token counts and **your**
> provider's published rates. Vendor pricing and feature names change; treat the *shape* of
> the math as the durable part.

---

## 1. Prompt / Context Caching

Many providers let you cache a stable prefix of a prompt server-side so that repeated
requests sharing that prefix skip re-processing it. There are two distinct prices:

- **Cache write** — storing the prefix the first time. Usually charged at a **premium**
  over the normal input rate (a multiplier > 1, e.g. ~1.25x as a common order of magnitude).
- **Cache read** — reusing the stored prefix on later requests. Charged at a steep
  **discount** to the normal input rate (a multiplier < 1, e.g. ~0.1x as a common order of
  magnitude).

### Effective cost model

For a prefix of `P` input tokens at base input price `b` (per token), reused across `N`
requests:

```
naive_cost   = N * P * b                       # no caching: pay full price every time
cached_cost  = (P * b * write_mult)            # one cache write
             + (N - 1) * (P * b * read_mult)   # N-1 cache reads
```

The dynamic (uncached) part of each request — the user turn, retrieved chunks that change,
the model's output — is priced normally and is the same in both worlds, so it cancels out
when you compare. Focus the math on the **cacheable prefix only**.

### Break-even reuse count

Caching only pays once the discounted reads recover the write premium. Solve
`cached_cost < naive_cost` for `N`:

```
break_even_N = (write_mult - 1) / (1 - read_mult) + 1
```

With write_mult = 1.25 and read_mult = 0.1, break-even ≈ **1.28**, i.e. the prefix must be
reused at least **twice** (the write plus one more hit) before caching is net-positive. The
larger the prefix and the more reuse, the more dramatic the win — savings asymptotically
approach `(1 - read_mult)` (e.g. ~90%) of the prefix cost as `N` grows.

### Cache-hit ratio math

In real traffic not every request hits the cache (TTL expiry, prefix drift, cold start). If
a fraction `h` of requests are cache hits and `(1 - h)` pay full input price for the prefix:

```
effective_prefix_price_per_token = b * [ h * read_mult + (1 - h) * 1.0 ]
```

A 70% hit ratio with read_mult = 0.1 gives an effective prefix price of
`b * (0.7*0.1 + 0.3*1.0) = b * 0.37` — a 63% discount on the prefix. Track hit ratio as a
first-class metric; a cache that never hits is pure overhead.

### What belongs in the cached prefix

Order the prompt **most-stable first, most-volatile last** so the longest possible prefix is
identical across requests:

- ✅ System prompt / role instructions, tool and schema definitions, long static policy or
  style guides, few-shot exemplars, large reference documents reused across many calls.
- ❌ The user's current message, freshly retrieved RAG chunks, timestamps, per-request IDs,
  anything that changes the prefix and silently invalidates the cache.

A single volatile token near the top of the prompt can wipe out the entire downstream cache,
so keep the boundary clean and put variability at the tail.

### When reuse pays off

- **Strong fit:** chatbots/agents with a big fixed system prompt, document-Q&A over the same
  document, batch classification sharing one instruction block, multi-turn sessions.
- **Weak fit:** one-shot prompts, prefixes shorter than the provider's minimum cacheable
  size, traffic so spread out that entries expire before reuse.

---

## 2. Batch Processing

Many providers offer an asynchronous **batch** tier: submit a large set of independent
requests and receive results within a longer window (often hours) in exchange for a large
discount — commonly on the order of **~50% off** synchronous pricing.

```
batch_cost = sync_cost * batch_discount_mult     # e.g. batch_discount_mult ≈ 0.5
```

### The tradeoff is latency, not quality

You get the same model and outputs; you give up interactivity and immediate completion. Route
work by latency tolerance:

- **Batch it:** offline evals, bulk summarization/classification/extraction, embeddings
  backfills, dataset labeling, nightly report generation, content pre-generation — anything
  no human is blocking on.
- **Keep it synchronous:** anything in an interactive request path where a user is waiting.

For orchestrating large asynchronous jobs (chunking, submission, polling, retries,
reassembly), see the **batch-api-orchestrator** skill — this skill scopes only the cost
decision.

### Stacking with caching

Batch discounts and caching discounts generally compose multiplicatively on their respective
token classes. A bulk job that *also* shares a large fixed instruction prefix can apply the
cache-read discount to the prefix **and** the batch discount on top — model the two effects
separately, then combine.

---

## 3. Reasoning Effort / Extended Thinking

Reasoning-style models can spend additional **internal reasoning tokens** before producing a
final answer. These intermediate tokens are typically billed like output tokens, so a "higher
effort" setting raises cost roughly in proportion to the extra reasoning tokens generated —
the visible answer length barely moves while the bill does.

```
cost ≈ input_cost + (visible_output + reasoning_tokens) * output_price
```

Key implications:

- More reasoning effort ⇒ more reasoning tokens ⇒ higher cost **and** higher latency. The
  relationship is roughly linear in tokens spent, not free.
- **Worth it** for genuinely hard multi-step problems (complex math/logic, tricky debugging,
  planning) where the extra reasoning measurably lifts accuracy and a wrong answer is costly.
- **Wasteful** for simple extraction, formatting, classification, or lookups — high effort
  buys little accuracy and inflates both cost and latency. Use the lowest effort that hits
  your quality bar, and reserve high effort for the queries that actually need it.
- Treat reasoning effort as a per-route knob, not a global default; pair it with model
  tiering (cheap model + low effort for easy traffic).
- Don't assume vendor parameter names — consult the provider's current API docs for how
  effort is configured and how the reasoning tokens are reported and billed.

---

## 4. Structured Output / JSON-Schema Overhead

Forcing the model to emit JSON (or conform to a schema/grammar) trades parsing reliability
for extra tokens. Two cost surfaces:

1. **Schema in the prompt.** A large schema, function/tool definition, or format spec sent on
   every request is input tokens you pay for repeatedly. This is a prime candidate for the
   **cached prefix** (Section 1) — a stable schema reused across calls should almost never be
   re-billed at full price.
2. **Structural tokens in the output.** Keys, braces, brackets, quotes, and commas are all
   output tokens. Verbose or deeply nested schemas, long descriptive key names, and repeated
   wrapper objects inflate output cost — the most expensive token class — on every response.

### Reducing the overhead

- Keep key names short but clear; avoid redundant nesting and wrapper envelopes.
- Return only the fields you actually consume; drop "nice to have" fields from the schema.
- Prefer flat arrays of records over deeply nested objects when the data allows.
- For very high-volume extraction, weigh a terse delimited format against JSON — but only if
  parsing stays reliable; the whole point of structured output is to avoid retries, and a
  re-run is far more expensive than a few extra structural tokens.
- Cache the schema/format block; vary only the per-request data.

---

## Putting It Together — Decision Order

1. **Measure** the real token split: stable prefix vs. volatile body vs. output (incl.
   reasoning tokens). Use `token_counter.py` for the prefix and body.
2. **Cache** the stable prefix if it clears the break-even reuse count
   (`cache_savings_calculator.py`).
3. **Batch** any traffic with no human waiting on it (~half cost for added latency).
4. **Right-size reasoning effort** per route — high only where accuracy demands it.
5. **Trim structured-output overhead** — short schema, only-needed fields, cache the schema.

These levers are independent and compound. Always run the numbers with **your** measured
tokens and **your** provider's current published rates — never hardcode vendor prices.
