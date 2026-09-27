# Failure Modes, Workflows & Quality

Read this when debugging a prompt or running a lifecycle workflow — common failure modes, the three core workflows, a quick-view integration table, troubleshooting matrix, and success criteria.

## Common Prompt Failure Modes

| Failure Mode | Symptom | Fix |
|-------------|---------|-----|
| Instruction override | Model ignores constraints | Move constraints earlier and state the reason beside each one; add emphasis only to the single instruction a test shows is underweighted (blanket "CRITICAL:" prefixes cause over-triggering on current models) |
| Format drift | Output structure varies between calls | Use structured outputs (JSON schema); on Claude Opus 4.7+ / Sonnet 5, non-default temperature is rejected |
| Sycophancy | Model agrees with wrong premise | Add "Challenge assumptions" instruction |
| Verbosity bloat | Output too long, buries the answer | Add word/token limits, "be concise" |
| Hallucination | Fabricated facts, citations, or code | Add "Only reference provided context" |
| Anchoring | First example dominates output style | Diversify examples, add "each input is independent" |
| Lost in the middle | Middle instructions get ignored | Front-load and back-load critical instructions |

## Workflows

### Workflow 1: Design a Production Prompt

```
1. Define the task precisely (input type, output type, quality criteria)
2. Write the system prompt using the 6-layer architecture
3. Create 10+ test cases (40% happy, 30% edge, 15% adversarial, 15% regression)
4. Run test suite, score results
5. Iterate until passing threshold (0.80+)
6. Version as v1, record baseline scores
7. Deploy with monitoring
```

### Workflow 2: Debug a Degraded Prompt

```
1. Identify which test cases are failing
2. Categorize failures (format? accuracy? safety? relevance?)
3. Check: did the model change? (API version, model update)
4. Check: did the input distribution change? (new edge cases)
5. Check: was the prompt modified? (diff against last known good)
6. Fix the root cause (not the symptom)
7. Run full regression suite before deploying fix
```

### Workflow 3: Migrate Prompt to New Model

```
1. Run full test suite on current model (baseline)
2. Run same suite on new model (no prompt changes)
3. Compare: if scores are equivalent, done
4. If scores drop: identify which dimensions degraded
5. Adjust prompt for new model's behavior patterns
6. Re-run suite until scores meet or exceed baseline
7. Document model-specific adjustments in changelog
```

## Integration Points (quick view)

| Skill | Integration |
|-------|-------------|
| **self-improving-agent** | Prompts that degrade are a regression signal; test them |
| **agent-designer** | Agent system prompts are the highest-stakes prompts to test |
| **context-engine** | Context retrieval quality directly affects prompt effectiveness |
| **ab-test-setup** | A/B test prompt variants in production with statistical rigor |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Model ignores critical instructions | Instructions buried in the middle of a long prompt | Front-load critical constraints and give the reason for each; reserve emphasis for the one instruction a test shows is underweighted |
| Output format randomly breaks | Format spec is ambiguous | Use structured outputs with an exact JSON schema rather than prose descriptions (temperature is not settable on Claude Opus 4.7+ / Sonnet 5) |
| Few-shot examples cause repetitive output | Examples are too similar, anchoring the model on a single pattern | Diversify examples across input types, lengths, and complexity levels; add "each input is independent" instruction |
| Prompt works on one model but fails on another | Model-specific instruction-following differences | Run full test suite on the target model; adjust layer ordering and verbosity for that model |
| Test scores drop after a minor prompt edit | Removed a constraint or anti-pattern that was load-bearing | Always diff before deploying; check if constraints, examples, or anti-patterns were removed; use the Prompt Diff Analysis checklist |
| Confidence scores cluster at extremes (all 0.9+ or all 0.1) | Calibration instructions missing or poorly defined | Add explicit confidence-level definitions (VERIFIED / LIKELY / UNCERTAIN / SPECULATIVE) with concrete criteria for each level |
| Prompt exceeds context window budget | Accumulated examples and instructions over multiple iterations | Audit token usage per layer; trim redundant examples; switch to dynamic few-shot selection to include only the most relevant shots |

## Success Criteria

- **Test suite pass rate >= 80%** across all prompt versions before production deployment, with zero safety-dimension failures.
- **Format compliance >= 95%** on structured output prompts, measured by schema validation against the declared JSON schema.
- **Regression delta <= 5%** on average score when migrating prompts between model versions, with no individual test case dropping by more than 10%.
- **Prompt version turnaround < 48 hours** from identifying a quality degradation to deploying a tested fix with full regression results recorded.
- **Few-shot example coverage >= 3 diversity categories** (simple, typical, edge) in every production prompt, validated during prompt review.
- **Changelog completeness: 100%** of prompt version changes documented with author, rationale, test results, and rollback plan.
- **Downstream parser breakage rate: 0** after any prompt format change, verified by integration tests against consuming systems.
