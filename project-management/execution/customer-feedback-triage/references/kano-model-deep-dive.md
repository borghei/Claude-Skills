# Kano Model — Deep Dive for Customer-Feedback Triage

The Kano Model, developed by Noriaki Kano and his collaborators in the early 1980s and published in 1984, classifies product features by how their presence or absence affects customer satisfaction. It is one of the most useful frameworks for triaging customer feedback because it answers a question the volume metric cannot: not "how many people asked", but "what kind of effect would building this have on satisfaction?"

## The five categories

### Must-be (Basic) quality

- **Effect of having it**: customers do not notice; satisfaction does not increase. This is the cost of entry.
- **Effect of missing it**: severe dissatisfaction; the customer may abandon the product.
- **Examples for a SaaS analytics tool**: login works; charts render; data export exists; basic permissions work.
- **Triage implication**: any cluster classified as basic with even a small customer count is a P0/P1 candidate. Basic gaps are existential.
- **Common verbatim signals**: "broken", "doesn't work", "can't", "blocker", "missing", "404", "error", "crashed".

### One-dimensional (Performance) quality

- **Effect of having it**: more is linearly better — more satisfaction with more of it.
- **Effect of missing it**: linearly worse — proportional dissatisfaction.
- **Examples**: query speed, dashboard load time, number of supported integrations, storage limit, API rate limit.
- **Triage implication**: scoring should weight performance items by how much the team is willing to invest. The marginal return diminishes — going from 5s to 2s page load matters more than going from 2s to 1.5s, even though both are "performance".
- **Common verbatim signals**: "faster", "slower", "more", "increase", "bulk", "batch", "scale", "limit", "throughput", "performance".

### Attractive (Delight) quality

- **Effect of having it**: disproportionate satisfaction; the customer is delighted and tells other customers about it.
- **Effect of missing it**: no effect; the customer does not miss what they did not expect.
- **Examples**: natural-language query, collaborative cursors, AI-generated dashboard suggestions, an unexpectedly fast feature.
- **Triage implication**: delighters score moderately in the priority formula (kano_weight = 3) but warrant qualitative attention because they are the basis of competitive differentiation. Build a few delighters per quarter, not 30.
- **Common verbatim signals**: "would love", "wish", "dream", "magic", "ai", "smart", "automatic", "predict", "suggest", "delight".

### Indifferent quality

- **Effect of having it**: no effect on satisfaction.
- **Effect of missing it**: no effect on satisfaction.
- **Examples**: theme color picker (for most users), splash-screen animation, vanity metrics dashboard.
- **Triage implication**: build only when there's a near-zero engineering cost or it's a precondition for another feature. Indifferent features consume roadmap space without moving any metric.
- **Common verbatim signals**: "color", "theme", "icon", "rename", "label", aesthetic-only asks.

### Reverse quality

- **Effect of having it**: causes dissatisfaction (the more, the worse).
- **Effect of missing it**: improves satisfaction (the less, the better).
- **Examples**: an overly chatty AI assistant; intrusive popups; aggressive upgrade nags; too many email notifications.
- **Triage implication**: a reverse cluster is a signal to *remove* something, not to *add* something. The priority formula gives reverse a negative weight (-3) intentionally — building more would actively damage satisfaction.
- **Common verbatim signals**: "too chatty", "annoying", "intrusive", "popup", "spam", "noise", "remove", "disable", "turn off".

## The two-dimensional model

Kano's original formulation plots two dimensions:

- Horizontal axis: degree to which the feature is implemented (none ↔ fully implemented).
- Vertical axis: customer satisfaction (dissatisfied ↔ delighted).

The five categories correspond to five different curves:

| Category | Curve shape |
|---|---|
| Must-be | Asymptotes upward; dropping toward dissatisfied if missing; flat at the top |
| Performance | Linear, passes through origin |
| Attractive | Asymptotes downward; high payoff when present, no penalty if absent |
| Indifferent | Flat — no slope |
| Reverse | Inverted — the more you build, the lower the satisfaction |

The visual is useful when explaining to non-PM stakeholders why building more of a performance feature has diminishing returns and why one delighter is worth more than three indifferents.

## Time dynamics: features migrate

Kano's most important practical insight is that **category assignment changes over time**:

- Today's delighter becomes tomorrow's basic. The iPhone's touchscreen was a delighter in 2007; in 2026 it is basic.
- A performance feature can degrade into a basic if competitors all match it. Page load time used to be performance; "the page loading at all" is now basic.
- Sometimes the migration is faster than expected. AI features (autocomplete, summarization) moved from delight in 2023 to performance in 2025 and arguably basic in some categories by 2026.

**Triage implication**: re-categorize quarterly. A cluster classified as "delight" 6 months ago may be "performance" today, which changes the priority and the response template.

## Edge cases and traps

### Segment-dependent categories

A feature can be basic for one segment and indifferent for another. SSO is basic for enterprise, indifferent for prosumer. The Python tool's keyword heuristic doesn't account for segment; the PM should re-categorize when a cluster is segment-skewed.

### Same word, different category

"Faster" usually means performance. But "I wish reports loaded faster" in a context where the report literally times out is basic (the feature is broken). Always read the verbatim, not just the keyword.

### Reverse features hidden inside delighters

A delighter can include a reverse element. "AI assistant" is a delighter if it's invoked deliberately, reverse if it nags. The triage cluster should split if both signals exist.

### Indifferent in aggregate, performance in segments

A feature can be indifferent across all customers but high-performance in one segment. Niche performance features can be valuable if the segment is high-margin and you're committed to serving it.

### The "I want what they have" request

Sometimes customers ask for a feature because a competitor has it. This is a strategic signal, not necessarily a Kano category. Resist mapping competitor parity directly to Kano; route to strategy and ask whether parity is the right move at all.

## Methodology: the Kano questionnaire

The original Kano method asks customers two questions per feature:

1. **Functional question**: "How do you feel if this feature is *present*?" (1 = I like it; 2 = I expect it; 3 = I'm neutral; 4 = I can live with it; 5 = I dislike it)
2. **Dysfunctional question**: "How do you feel if this feature is *absent*?" (same scale)

The pair of answers maps to a category via Kano's evaluation table:

| Functional answer | Dysfunctional answer | Category |
|---|---|---|
| Like | Dislike | Performance |
| Like | Live with | Attractive |
| Expect | Dislike | Must-be |
| Live with | Live with | Indifferent |
| Like | Like | Reverse |

The PM rarely has the budget for a full Kano survey on every feature, but for high-stakes decisions (pricing changes, major product additions), running a Kano survey with 50-100 customers can definitively resolve a category question. See the formal Kano method papers in references below.

## Heuristic versus methodology

The Python tool's keyword heuristic is a triage-grade approximation, not the formal Kano method. It exists because:

- The PM cannot run a Kano survey on every feedback item.
- Most categorization is "good enough" with a heuristic plus PM judgment.
- The heuristic is transparent: a PM can audit why a category was assigned and override.

For genuinely strategic features (the kind that show up in `create-prd/` and `business-growth/pricing-strategy/`), run a proper Kano survey or at least structured customer-interview Kano questions. For everyday triage, the heuristic plus override is sufficient.

## Worked example: AI assistant request

Suppose 12 customers in the queue have requested an AI assistant. Verbatim signals:

- "Would love an AI that auto-builds dashboards" → attractive (delight keywords)
- "AI assistant is essential, every competitor has it" → migrating toward performance
- "Need natural-language query as table stakes for our team" → basic (table stakes)
- "Curious about AI features" → indifferent (no strong signal)
- "An AI assistant would be nice but we're not pushing for it" → attractive

The cluster's majority category is attractive (delight). But the segment matters: if 8 of the 12 are enterprise prospects who are saying "table stakes", the cluster is actually performance or basic for that segment. Re-cluster by segment; route the enterprise sub-cluster as performance with priority uplift; route the rest as delight.

## References

- Kano, N., Seraku, N., Takahashi, F., & Tsuji, S. (1984). "Attractive Quality and Must-Be Quality". *Journal of the Japanese Society for Quality Control*, 14(2), 39-48.
- Berger, C., Blauth, R., Boger, D., et al. (1993). "Kano's Methods for Understanding Customer-defined Quality". *Center for Quality Management Journal*, 2(4).
- Folmer, E., & Bosch, J. (2004). "Architecting for Usability: A Survey". *Journal of Systems and Software*, 70(1-2).
- Marty Cagan, *Inspired*, chapter on prioritization techniques — Kano framing applied to product
