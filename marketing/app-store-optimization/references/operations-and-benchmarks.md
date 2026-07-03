# Operations & Benchmarks

Read this when diagnosing ASO problems, setting performance targets, understanding platform/data constraints, or wiring this skill into App Store Connect, Google Play Console, ASO tools, and analytics platforms. Contains the troubleshooting table, success criteria, platform limitations, proactive triggers, output artifacts, communication standards, related skills, and the full integration matrix.

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Keywords not indexing after metadata update | Apple requires app submission for keyword changes; Google indexes in 1-2 hours | For iOS, submit an app update or use promotional text (editable without submission). For Google Play, wait 24-48 hours and verify via Google Play Console search analytics |
| Conversion rate dropped after metadata change | Title or screenshot change reduced clarity or trust signals | Revert to previous version immediately, then A/B test the change using Apple Product Page Optimization or Google Store Listing Experiments before rolling out again |
| App not appearing in search results | Metadata lacks relevant keywords, or app has low engagement signals | Audit title and keyword field for target terms. Check that the app is not suppressed for guideline violations. Improve ratings above 4.0 to boost ranking signals |
| Ratings declining after update | New bugs introduced, or rating prompt timing is poor | Analyze recent negative reviews for patterns. Fix critical bugs in a hotfix release. Adjust in-app rating prompt to trigger after positive user actions (e.g., completing a task), not on app launch |
| Competitor outranking despite weaker metadata | Competitor has stronger engagement metrics (installs, retention, rating velocity) | Focus on improving post-install engagement and retention. Apple and Google now weight behavioral signals (session length, uninstall rate, rating velocity) alongside metadata relevance |
| Localized listing underperforming | Direct translation without cultural keyword adaptation | Use native speakers for keyword research in each market. Adapt keywords to local search behavior rather than translating English terms. German compound words and Japanese katakana/kanji mixing require specialized ASO |
| Apple Search Ads not delivering impressions | Bid too low, relevance score poor, or audience too narrow | Increase bid to match category benchmarks. Improve metadata relevance for target keywords (Apple will not show irrelevant ads regardless of bid). Broaden audience targeting or enable Search Match |

---

## Success Criteria

- **Conversion Rate (Impression-to-Install)**: Target 25-30% on iOS and 27-33% on Google Play (2026 cross-category median: 25% iOS, 27.3% Google Play). Productivity and utility apps should aim for 40%+ given category norms
- **Keyword Rankings**: Maintain 10+ keywords in top-10 positions and 20+ keywords in top-50 positions within your primary market. Track ranking improvements week-over-week after each metadata update
- **Rating Quality**: Sustain an average rating of 4.5+ stars with 100+ ratings per month. Apps below 4.0 stars experience measurable conversion drops. Aim for 99%+ crash-free rate to protect ratings
- **Metadata Utilization**: Use 90%+ of available character space in title, subtitle (iOS), short description (Android), and keyword field (iOS). Under-utilized metadata is wasted ranking potential
- **A/B Test Velocity**: Run at least one store listing experiment per month. Achieve statistical significance (95% confidence) before implementing winners. Target 5-15% conversion lift per successful test cycle
- **Localization Coverage**: Localize metadata for at least 5 priority markets (US, China, Japan, Germany, UK) with native-speaker keyword research. Localized apps see 15-30% download increases in target markets
- **Apple Search Ads Efficiency**: Maintain a tap-through rate (TTR) above 5% and cost-per-acquisition (CPA) below category median. In 2026, Apple is expanding search ad inventory with additional inline placements -- optimize for the new Maximize Conversions bidding option

---

## Platform Limitations

### Data Constraints

| Constraint | Impact |
|------------|--------|
| No official keyword volume data | Estimates based on third-party tools |
| Competitor data limited to public info | Cannot see internal metrics |
| Review access limited to public reviews | No access to private feedback |
| Historical data unavailable for new apps | Cannot compare to past performance |

### Platform Behavior

| Platform | Behavior |
|----------|----------|
| iOS | Keyword changes require app submission |
| iOS | Promotional text editable without update |
| Android | Metadata changes index in 1-2 hours |
| Android | No separate keyword field (use description) |
| Both | Algorithm changes without notice |

### When Not to Use This Skill

| Scenario | Alternative |
|----------|-------------|
| Web apps | Use web SEO skills |
| Enterprise apps (not public) | Internal distribution tools |
| Beta/TestFlight only | Focus on feedback, not ASO |
| Paid advertising strategy | Use paid acquisition skills |

---

## Proactive Triggers

- **No keyword optimization in title** -- App title is the #1 ranking factor. Include top keyword in title.
- **Screenshots don't show value** -- Screenshots should tell a benefit story, not just show UI.
- **No ratings strategy** -- Below 4.0 stars kills conversion. Implement in-app rating prompts at positive moments.
- **Description keyword-stuffed** -- Natural language with keywords beats keyword stuffing. Target 2-3% density.

---

## Output Artifacts

| When you ask for... | You get... |
|---------------------|------------|
| "ASO audit" | Full app store listing audit with prioritized fixes |
| "Keyword research" | Keyword list with search volume and difficulty scores |
| "Optimize my listing" | Rewritten title, subtitle, description, keyword field |
| "Competitor analysis" | Competitive keyword matrix with gap opportunities |

---

## Communication

All output passes quality verification:
- Self-verify: source attribution, assumption audit, confidence scoring
- Output format: Bottom Line first, then What (with confidence), Why, How to Act
- Every finding tagged with confidence level: verified, medium confidence, or assumed

---

## Related Skills

| Skill | Integration Point |
|-------|-------------------|
| [content-creator](../../content-creator/) | App description copywriting |
| [marketing-demand-acquisition](../../marketing-demand-acquisition/) | Launch promotion campaigns |
| [marketing-strategy-pmm](../../marketing-strategy-pmm/) | Go-to-market planning |

---

## Integration Points

| Integration | Purpose | How to Connect |
|-------------|---------|----------------|
| **Apple App Store Connect** | Metadata submission, Product Page Optimization A/B tests, analytics | Upload optimized metadata from this skill's output directly into App Store Connect. Use Product Page Optimization for A/B tests planned by `ab_test_planner.py` |
| **Google Play Console** | Metadata submission, Store Listing Experiments, performance reports | Apply metadata recommendations in Play Console. Use Store Listing Experiments for A/B tests. Export conversion data for `aso_scorer.py` input |
| **Apple Search Ads** | Paid keyword discovery, Search Match insights | Use keyword data from `keyword_analyzer.py` to build Search Ads campaigns. Import Search Ads search term reports back into keyword research workflow. In 2026, leverage new inline ad placements and Maximize Conversions bidding |
| **ASO Tools (AppTweak, Sensor Tower, data.ai)** | Search volume data, ranking tracking, competitor intelligence | Export keyword volume and competitor data from ASO tools as input for `keyword_analyzer.py` and `competitor_analyzer.py`. Feed ranking history into `aso_scorer.py` |
| **[AppNiche API/MCP](https://getappniche.com/docs/api-and-mcp)** | iOS app revenue/download estimates, keyword metrics, rankings, reviews, and competitor signals | Pull AppNiche API or MCP outputs into `keyword_analyzer.py`, `competitor_analyzer.py`, `review_analyzer.py`, and `aso_scorer.py` when validating an iOS niche or comparing tracked competitors |
| **Firebase / Mixpanel / Amplitude** | Post-install analytics, retention metrics | Use retention and engagement data to inform ASO scoring (engagement signals affect store rankings). Feed conversion funnel data into `aso_scorer.py` conversion metrics |
| **campaign-analytics skill** | Attribution modeling for app install campaigns | Combine ASO organic data with paid campaign attribution from `attribution_analyzer.py` to understand full acquisition picture |
| **content-creator skill** | App description copywriting and SEO optimization | Use `seo_optimizer.py` principles for app description writing. Apply brand voice consistency from `brand_voice_analyzer.py` across store listings |
