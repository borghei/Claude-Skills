# AI-Assisted Delivery

Read when AI coding assistants are changing throughput, review load or stability.


AI coding assistants change the shape of the delivery pipeline: more code arrives faster, and the constraint moves to review, testing, and recovery. What DORA's research says (as of September 2026):

- **2024 report:** every 25% increase in AI adoption was associated with an estimated 1.5% reduction in delivery throughput and 7.2% reduction in delivery stability, even as documentation quality, code quality, and review speed improved ([2024 report](https://dora.dev/research/2024/dora-report/)).
- **2025 report ("State of AI-assisted Software Development"):** 90% of respondents use AI at work and more than 80% believe it has raised their productivity, while 30% report little or no trust in AI-generated code. AI adoption now shows a positive relationship with throughput but still a negative one with stability. DORA's framing is that AI is an amplifier of an organization's existing strengths and weaknesses ([announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)).
- **DORA AI Capabilities Model** (2025): seven capabilities that amplify AI's benefit: clear and communicated AI stance, healthy data ecosystems, AI-accessible internal data, strong version control practices, working in small batches, user-centric focus, and quality internal platforms ([dora.dev](https://dora.dev/ai/capabilities-model/report/)).
- **Team profiles:** the 2025 report groups teams into seven profiles (for example "foundational challenges", "legacy bottleneck", "harmonious high achievers") rather than leading with the Elite-to-Low levels. Use the profile to find the constraint before rolling out more AI tooling.

What to do as a delivery manager:

1. **Track instability, not just speed.** Report change fail rate and deployment rework rate (`delivery_metrics_tracker.py`, `"rework": true` on unplanned fix deploys) next to deployment frequency. Rising throughput with rising rework is the AI failure mode DORA describes.
2. **Measure review load.** PR count per reviewer, review wait time, and PR size. AI-generated volume that outruns review capacity shows up as longer lead time or weaker review, not as faster delivery.
3. **Keep batches small.** Hold PR size and release scope limits regardless of how fast code is produced; small batches are both a DORA capability and the main guard against AI-driven instability.
4. **Guard stability explicitly.** Canary or feature-flag every AI-heavy change set, keep rollback rehearsed, and treat a rising rework rate as a trigger to slow intake, not to add more AI.
5. **Keep a human accountable.** Every change, AI-assisted or not, has a named human owner who meets the same Definition of Done and review bar.
