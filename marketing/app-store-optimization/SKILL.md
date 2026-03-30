---
name: app-store-optimization
description: >
  App Store Optimization toolkit for researching keywords, optimizing metadata,
  and tracking mobile app performance on Apple App Store and Google Play Store.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: aso
  updated: 2026-03-31
  tags: [aso, app-store, google-play, keywords, ratings]
---
# App Store Optimization (ASO)

ASO tools for researching keywords, optimizing metadata, analyzing competitors, and improving app store visibility on Apple App Store and Google Play Store.

---

## Table of Contents

- [Keyword Research Workflow](#keyword-research-workflow)
- [Metadata Optimization Workflow](#metadata-optimization-workflow)
- [Competitor Analysis Workflow](#competitor-analysis-workflow)
- [App Launch Workflow](#app-launch-workflow)
- [A/B Testing Workflow](#ab-testing-workflow)
- [Before/After Examples](#beforeafter-examples)
- [Tools and References](#tools-and-references)

---

## Keyword Research Workflow

Discover and evaluate keywords that drive app store visibility.

### Workflow: Conduct Keyword Research

1. Define target audience and core app functions:
   - Primary use case (what problem does the app solve)
   - Target user demographics
   - Competitive category
2. Generate seed keywords from:
   - App features and benefits
   - User language (not developer terminology)
   - App store autocomplete suggestions
3. Expand keyword list using:
   - Modifiers (free, best, simple)
   - Actions (create, track, organize)
   - Audiences (for students, for teams, for business)
4. Evaluate each keyword:
   - Search volume (estimated monthly searches)
   - Competition (number and quality of ranking apps)
   - Relevance (alignment with app function)
5. Score and prioritize keywords:
   - Primary: Title and keyword field (iOS)
   - Secondary: Subtitle and short description
   - Tertiary: Full description only
6. Map keywords to metadata locations
7. Document keyword strategy for tracking
8. **Validation:** Keywords scored; placement mapped; no competitor brand names included; no plurals in iOS keyword field

### Keyword Evaluation Criteria

| Factor | Weight | High Score Indicators |
|--------|--------|----------------------|
| Relevance | 35% | Describes core app function |
| Volume | 25% | 10,000+ monthly searches |
| Competition | 25% | Top 10 apps have <4.5 avg rating |
| Conversion | 15% | Transactional intent ("best X app") |

### Keyword Placement Priority

| Location | Search Weight | Character Limit |
|----------|---------------|-----------------|
| App Title | Highest | 30 (iOS) / 50 (Android) |
| Subtitle (iOS) | High | 30 |
| Keyword Field (iOS) | High | 100 |
| Short Description (Android) | High | 80 |
| Full Description | Medium | 4,000 |

See: [references/keyword-research-guide.md](references/keyword-research-guide.md)

---

## Metadata Optimization Workflow

Optimize app store listing elements for search ranking and conversion.

### Workflow: Optimize App Metadata

1. Audit current metadata against platform limits:
   - Title character count and keyword presence
   - Subtitle/short description usage
   - Keyword field efficiency (iOS)
   - Description keyword density
2. Optimize title following formula:
   ```
   [Brand Name] - [Primary Keyword] [Secondary Keyword]
   ```
3. Write subtitle (iOS) or short description (Android):
   - Focus on primary benefit
   - Include secondary keyword
   - Use action verbs
4. Optimize keyword field (iOS only):
   - Remove duplicates from title
   - Remove plurals (Apple indexes both forms)
   - No spaces after commas
   - Prioritize by score
5. Rewrite full description:
   - Hook paragraph with value proposition
   - Feature bullets with keywords
   - Social proof section
   - Call to action
6. Validate character counts for each field
7. Calculate keyword density (target 2-3% primary)
8. **Validation:** All fields within character limits; primary keyword in title; no keyword stuffing (>5%); natural language preserved

### Platform Character Limits

| Field | Apple App Store | Google Play Store |
|-------|-----------------|-------------------|
| Title | 30 characters | 50 characters |
| Subtitle | 30 characters | N/A |
| Short Description | N/A | 80 characters |
| Keywords | 100 characters | N/A |
| Promotional Text | 170 characters | N/A |
| Full Description | 4,000 characters | 4,000 characters |
| What's New | 4,000 characters | 500 characters |

### Description Structure

```
PARAGRAPH 1: Hook (50-100 words)
├── Address user pain point
├── State main value proposition
└── Include primary keyword

PARAGRAPH 2-3: Features (100-150 words)
├── Top 5 features with benefits
├── Bullet points for scanability
└── Secondary keywords naturally integrated

PARAGRAPH 4: Social Proof (50-75 words)
├── Download count or rating
├── Press mentions or awards
└── Summary of user testimonials

PARAGRAPH 5: Call to Action (25-50 words)
├── Clear next step
└── Reassurance (free trial, no signup)
```

See: [references/platform-requirements.md](references/platform-requirements.md)

---

## Competitor Analysis Workflow

Analyze top competitors to identify keyword gaps and positioning opportunities.

### Workflow: Analyze Competitor ASO Strategy

1. Identify top 10 competitors:
   - Direct competitors (same core function)
   - Indirect competitors (overlapping audience)
   - Category leaders (top downloads)
2. Extract competitor keywords from:
   - App titles and subtitles
   - First 100 words of descriptions
   - Visible metadata patterns
3. Build competitor keyword matrix:
   - Map which keywords each competitor targets
   - Calculate coverage percentage per keyword
4. Identify keyword gaps:
   - Keywords with <40% competitor coverage
   - High volume terms competitors miss
   - Long-tail opportunities
5. Analyze competitor visual assets:
   - Icon design patterns
   - Screenshot messaging and style
   - Video presence and quality
6. Compare ratings and review patterns:
   - Average rating by competitor
   - Common praise themes
   - Common complaint themes
7. Document positioning opportunities
8. **Validation:** 10+ competitors analyzed; keyword matrix complete; gaps identified with volume estimates; visual audit documented

### Competitor Analysis Matrix

| Analysis Area | Data Points |
|---------------|-------------|
| Keywords | Title keywords, description frequency |
| Metadata | Character utilization, keyword density |
| Visuals | Icon style, screenshot count/style |
| Ratings | Average rating, total count, velocity |
| Reviews | Top praise, top complaints |

### Gap Analysis Template

| Opportunity Type | Example | Action |
|------------------|---------|--------|
| Keyword gap | "habit tracker" (40% coverage) | Add to keyword field |
| Feature gap | Competitor lacks widget | Highlight in screenshots |
| Visual gap | No videos in top 5 | Create app preview |
| Messaging gap | None mention "free" | Test free positioning |

---

## App Launch Workflow

Execute a structured launch for maximum initial visibility.

### Workflow: Launch App to Stores

1. Complete pre-launch preparation (4 weeks before):
   - Finalize keywords and metadata
   - Prepare all visual assets
   - Set up analytics (Firebase, Mixpanel)
   - Build press kit and media list
2. Submit for review (2 weeks before):
   - Complete all store requirements
   - Verify compliance with guidelines
   - Prepare launch communications
3. Configure post-launch systems:
   - Set up review monitoring
   - Prepare response templates
   - Configure rating prompt timing
4. Execute launch day:
   - Verify app is live in both stores
   - Announce across all channels
   - Begin review response cycle
5. Monitor initial performance (days 1-7):
   - Track download velocity hourly
   - Monitor reviews and respond within 24 hours
   - Document any issues for quick fixes
6. Conduct 7-day retrospective:
   - Compare performance to projections
   - Identify quick optimization wins
   - Plan first metadata update
7. Schedule first update (2 weeks post-launch)
8. **Validation:** App live in stores; analytics tracking; review responses within 24h; download velocity documented; first update scheduled

### Pre-Launch Checklist

| Category | Items |
|----------|-------|
| Metadata | Title, subtitle, description, keywords |
| Visual Assets | Icon, screenshots (all sizes), video |
| Compliance | Age rating, privacy policy, content rights |
| Technical | App binary, signing certificates |
| Analytics | SDK integration, event tracking |
| Marketing | Press kit, social content, email ready |

### Launch Timing Considerations

| Factor | Recommendation |
|--------|----------------|
| Day of week | Tuesday-Wednesday (avoid weekends) |
| Time of day | Morning in target market timezone |
| Seasonal | Align with relevant category seasons |
| Competition | Avoid major competitor launch dates |

See: [references/aso-best-practices.md](references/aso-best-practices.md)

---

## A/B Testing Workflow

Test metadata and visual elements to improve conversion rates.

### Workflow: Run A/B Test

1. Select test element (prioritize by impact):
   - Icon (highest impact)
   - Screenshot 1 (high impact)
   - Title (high impact)
   - Short description (medium impact)
2. Form hypothesis:
   ```
   If we [change], then [metric] will [improve/increase] by [amount]
   because [rationale].
   ```
3. Create variants:
   - Control: Current version
   - Treatment: Single variable change
4. Calculate required sample size:
   - Baseline conversion rate
   - Minimum detectable effect (usually 5%)
   - Statistical significance (95%)
5. Launch test:
   - Apple: Use Product Page Optimization
   - Android: Use Store Listing Experiments
6. Run test for minimum duration:
   - At least 7 days
   - Until statistical significance reached
7. Analyze results:
   - Compare conversion rates
   - Check statistical significance
   - Document learnings
8. **Validation:** Single variable tested; sample size sufficient; significance reached (95%); results documented; winner implemented

### A/B Test Prioritization

| Element | Conversion Impact | Test Complexity |
|---------|-------------------|-----------------|
| App Icon | 10-25% lift possible | Medium (design needed) |
| Screenshot 1 | 15-35% lift possible | Medium |
| Title | 5-15% lift possible | Low |
| Short Description | 5-10% lift possible | Low |
| Video | 10-20% lift possible | High |

### Sample Size Quick Reference

| Baseline CVR | Impressions Needed (per variant) |
|--------------|----------------------------------|
| 1% | 31,000 |
| 2% | 15,500 |
| 5% | 6,200 |
| 10% | 3,100 |

### Test Documentation Template

```
TEST ID: ASO-2025-001
ELEMENT: App Icon
HYPOTHESIS: A bolder color icon will increase conversion by 10%
START DATE: [Date]
END DATE: [Date]

RESULTS:
├── Control CVR: 4.2%
├── Treatment CVR: 4.8%
├── Lift: +14.3%
├── Significance: 97%
└── Decision: Implement treatment

LEARNINGS:
- Bold colors outperform muted tones in this category
- Apply to screenshot backgrounds for next test
```

---

## Before/After Examples

### Title Optimization

**Productivity App:**

| Version | Title | Analysis |
|---------|-------|----------|
| Before | "MyTasks" | No keywords, brand only (8 chars) |
| After | "MyTasks - Todo List & Planner" | Primary + secondary keywords (29 chars) |

**Fitness App:**

| Version | Title | Analysis |
|---------|-------|----------|
| Before | "FitTrack Pro" | Generic modifier (12 chars) |
| After | "FitTrack: Workout Log & Gym" | Category keywords (27 chars) |

### Subtitle Optimization (iOS)

| Version | Subtitle | Analysis |
|---------|----------|----------|
| Before | "Get Things Done" | Vague, no keywords |
| After | "Daily Task Manager & Planner" | Two keywords, benefit clear |

### Keyword Field Optimization (iOS)

**Before (Inefficient - 89 chars, 8 keywords):**
```
task manager, todo list, productivity app, daily planner, reminder app
```

**After (Optimized - 97 chars, 14 keywords):**
```
task,todo,checklist,reminder,organize,daily,planner,schedule,deadline,goals,habit,widget,sync,team
```

**Improvements:**
- Removed spaces after commas (+8 chars)
- Removed duplicates (task manager → task)
- Removed plurals (reminders → reminder)
- Removed words in title
- Added more relevant keywords

### Description Opening

**Before:**
```
MyTasks is a comprehensive task management solution designed
to help busy professionals organize their daily activities
and boost productivity.
```

**After:**
```
Forget missed deadlines. MyTasks keeps every task, reminder,
and project in one place—so you focus on doing, not remembering.
Trusted by 500,000+ professionals.
```

**Improvements:**
- Leads with user pain point
- Specific benefit (not generic "boost productivity")
- Social proof included
- Keywords natural, not stuffed

### Screenshot Caption Evolution

| Version | Caption | Issue |
|---------|---------|-------|
| Before | "Task List Feature" | Feature-focused, passive |
| Better | "Create Task Lists" | Action verb, but still feature |
| Best | "Never Miss a Deadline" | Benefit-focused, emotional |

---

## Tools and References

### Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| [keyword_analyzer.py](scripts/keyword_analyzer.py) | Analyze keywords for volume and competition | `python keyword_analyzer.py --keywords "todo,task,planner"` |
| [metadata_optimizer.py](scripts/metadata_optimizer.py) | Validate metadata character limits and density | `python metadata_optimizer.py --platform ios --title "App Title"` |
| [competitor_analyzer.py](scripts/competitor_analyzer.py) | Extract and compare competitor keywords | `python competitor_analyzer.py --competitors "App1,App2,App3"` |
| [aso_scorer.py](scripts/aso_scorer.py) | Calculate overall ASO health score | `python aso_scorer.py --app-id com.example.app` |
| [ab_test_planner.py](scripts/ab_test_planner.py) | Plan tests and calculate sample sizes | `python ab_test_planner.py --cvr 0.05 --lift 0.10` |
| [review_analyzer.py](scripts/review_analyzer.py) | Analyze review sentiment and themes | `python review_analyzer.py --app-id com.example.app` |
| [launch_checklist.py](scripts/launch_checklist.py) | Generate platform-specific launch checklists | `python launch_checklist.py --platform ios` |
| [localization_helper.py](scripts/localization_helper.py) | Manage multi-language metadata | `python localization_helper.py --locales "en,es,de,ja"` |

### References

| Document | Content |
|----------|---------|
| [platform-requirements.md](references/platform-requirements.md) | iOS and Android metadata specs, visual asset requirements |
| [aso-best-practices.md](references/aso-best-practices.md) | Optimization strategies, rating management, launch tactics |
| [keyword-research-guide.md](references/keyword-research-guide.md) | Research methodology, evaluation framework, tracking |

### Assets

| Template | Purpose |
|----------|---------|
| [aso-audit-template.md](assets/aso-audit-template.md) | Structured audit checklist for app store listings |

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

## Related Skills

| Skill | Integration Point |
|-------|-------------------|
| [content-creator](../content-creator/) | App description copywriting |
| [marketing-demand-acquisition](../marketing-demand-acquisition/) | Launch promotion campaigns |
| [marketing-strategy-pmm](../marketing-strategy-pmm/) | Go-to-market planning |

## Proactive Triggers

- **No keyword optimization in title** -- App title is the #1 ranking factor. Include top keyword in title.
- **Screenshots don't show value** -- Screenshots should tell a benefit story, not just show UI.
- **No ratings strategy** -- Below 4.0 stars kills conversion. Implement in-app rating prompts at positive moments.
- **Description keyword-stuffed** -- Natural language with keywords beats keyword stuffing. Target 2-3% density.

## Output Artifacts

| When you ask for... | You get... |
|---------------------|------------|
| "ASO audit" | Full app store listing audit with prioritized fixes |
| "Keyword research" | Keyword list with search volume and difficulty scores |
| "Optimize my listing" | Rewritten title, subtitle, description, keyword field |
| "Competitor analysis" | Competitive keyword matrix with gap opportunities |

## Communication

All output passes quality verification:
- Self-verify: source attribution, assumption audit, confidence scoring
- Output format: Bottom Line first, then What (with confidence), Why, How to Act
- Every finding tagged with confidence level: verified, medium confidence, or assumed

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

## Scope & Limitations

**In Scope:**
- Keyword research, metadata optimization, and character limit validation for Apple App Store and Google Play Store
- Competitor ASO analysis using publicly available metadata, ratings, and reviews
- A/B test planning with sample size calculations and statistical significance testing
- Launch checklist generation, seasonal campaign planning, and localization strategy
- Review sentiment analysis and feature request extraction

**Out of Scope:**
- Real-time app store data fetching (scripts analyze static data you provide)
- Apple Search Ads or Google Ads campaign management (use platform dashboards)
- Creative asset design (icon, screenshots, video production)
- Cross-device attribution and install tracking (requires MMP integration such as AppsFlyer, Adjust, or Branch)
- In-app analytics and retention optimization (use Firebase, Mixpanel, or Amplitude)
- Revenue or subscription optimization (pricing strategy is a separate discipline)

**Data Constraints:**
- No official search volume API exists for either app store; volume estimates rely on third-party tools or heuristic scoring
- Competitor data is limited to publicly visible metadata, ratings, and reviews
- Historical ranking data requires external ASO tools (AppTweak, Sensor Tower, data.ai)
- Apple's June 2025 algorithm update now indexes screenshot text as a ranking factor -- this skill's scripts do not yet analyze visual text content

---

## Integration Points

| Integration | Purpose | How to Connect |
|-------------|---------|----------------|
| **Apple App Store Connect** | Metadata submission, Product Page Optimization A/B tests, analytics | Upload optimized metadata from this skill's output directly into App Store Connect. Use Product Page Optimization for A/B tests planned by `ab_test_planner.py` |
| **Google Play Console** | Metadata submission, Store Listing Experiments, performance reports | Apply metadata recommendations in Play Console. Use Store Listing Experiments for A/B tests. Export conversion data for `aso_scorer.py` input |
| **Apple Search Ads** | Paid keyword discovery, Search Match insights | Use keyword data from `keyword_analyzer.py` to build Search Ads campaigns. Import Search Ads search term reports back into keyword research workflow. In 2026, leverage new inline ad placements and Maximize Conversions bidding |
| **ASO Tools (AppTweak, Sensor Tower, data.ai)** | Search volume data, ranking tracking, competitor intelligence | Export keyword volume and competitor data from ASO tools as input for `keyword_analyzer.py` and `competitor_analyzer.py`. Feed ranking history into `aso_scorer.py` |
| **Firebase / Mixpanel / Amplitude** | Post-install analytics, retention metrics | Use retention and engagement data to inform ASO scoring (engagement signals affect store rankings). Feed conversion funnel data into `aso_scorer.py` conversion metrics |
| **campaign-analytics skill** | Attribution modeling for app install campaigns | Combine ASO organic data with paid campaign attribution from `attribution_analyzer.py` to understand full acquisition picture |
| **content-creator skill** | App description copywriting and SEO optimization | Use `seo_optimizer.py` principles for app description writing. Apply brand voice consistency from `brand_voice_analyzer.py` across store listings |

---

## Tool Reference

### keyword_analyzer.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `KeywordAnalyzer` -- Core analysis class

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `analyze_keyword()` | `keyword: str`, `search_volume: int = 0`, `competing_apps: int = 0`, `relevance_score: float = 0.0` | Dict with keyword analysis (potential score 0-100, difficulty score 0-100, recommendation) |
| `compare_keywords()` | `keywords_data: List[Dict]` (each dict: keyword, search_volume, competing_apps, relevance_score) | Ranked keywords with primary/secondary/long-tail categorization |
| `find_long_tail_opportunities()` | `base_keyword: str`, `modifiers: List[str]` | Long-tail keyword variations with competition estimates |
| `extract_keywords_from_text()` | `text: str`, `min_word_length: int = 3` | Top 50 keywords/phrases by frequency |
| `calculate_keyword_density()` | `text: str`, `target_keywords: List[str]` | Dict of keyword: density percentage |

**Convenience Function:** `analyze_keyword_set(keywords_data)` -- Analyzes and ranks a full keyword set in one call.

### metadata_optimizer.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `MetadataOptimizer(platform: str = 'apple')` -- Platform must be `'apple'` or `'google'`

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `optimize_title()` | `app_name: str`, `target_keywords: List[str]`, `include_brand: bool = True` | Title options with length, keywords included, pros/cons, recommendation |
| `optimize_description()` | `app_info: Dict` (name, key_features, unique_value, target_audience), `target_keywords: List[str]`, `description_type: str = 'full'` | Optimized description with keyword density analysis. Types: `'full'`, `'short'` (Google), `'subtitle'` (Apple) |
| `optimize_keyword_field()` | `target_keywords: List[str]`, `app_title: str = ""`, `app_description: str = ""` | Apple-only. Optimized 100-char keyword field (no spaces, no plurals, no title duplicates) |
| `validate_character_limits()` | `metadata: Dict[str, str]` | Validation report with errors, warnings, usage percentages |
| `calculate_keyword_density()` | `text: str`, `target_keywords: List[str]` | Per-keyword density with status (too_low / optimal / too_high) |

**Convenience Function:** `optimize_app_metadata(platform, app_info, target_keywords)` -- Optimizes title, description, and keyword field in one call.

### competitor_analyzer.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `CompetitorAnalyzer(category: str, platform: str = 'apple')`

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `analyze_competitor()` | `app_data: Dict` (app_name, title, description, rating, ratings_count, keywords) | Title analysis, description analysis, keyword strategy, competitive strength score (0-100) |
| `compare_competitors()` | `competitors_data: List[Dict]` | Ranked competitors, common keywords, keyword gaps, best practices, opportunities |
| `identify_gaps()` | `your_app_data: Dict`, `competitors_data: List[Dict]` | Keyword gaps, rating gaps, content gaps, competitive positioning assessment |

**Convenience Function:** `analyze_competitor_set(category, competitors_data, platform='apple')` -- Full competitive analysis in one call.

### aso_scorer.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `ASOScorer` -- Calculates weighted ASO health score (0-100)

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `calculate_overall_score()` | `metadata: Dict`, `ratings: Dict`, `keyword_performance: Dict`, `conversion: Dict` | Overall score, health status, breakdown by component, prioritized recommendations, strengths, weaknesses |
| `score_metadata_quality()` | `metadata: Dict` (title_keyword_count, title_length, description_length, description_quality, keyword_density) | Score 0-100 |
| `score_ratings_reviews()` | `ratings: Dict` (average_rating, total_ratings, recent_ratings_30d) | Score 0-100 |
| `score_keyword_performance()` | `keyword_performance: Dict` (top_10, top_50, top_100, improving_keywords) | Score 0-100 |
| `score_conversion_metrics()` | `conversion: Dict` (impression_to_install, downloads_last_30_days, downloads_trend) | Score 0-100 |

**Weights:** metadata_quality 25%, ratings_reviews 25%, keyword_performance 25%, conversion_metrics 25%.

**Convenience Function:** `calculate_aso_score(metadata, ratings, keyword_performance, conversion)`

### ab_test_planner.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `ABTestPlanner`

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `design_test()` | `test_type: str` (`'icon'`, `'screenshot'`, `'title'`, `'description'`), `variant_a: Dict`, `variant_b: Dict`, `hypothesis: str`, `success_metric: str = 'conversion_rate'` | Test design with ID, variants, secondary metrics, best practices |
| `calculate_sample_size()` | `baseline_conversion: float`, `minimum_detectable_effect: float`, `confidence_level: str = 'standard'` (`'high'`/`'standard'`/`'exploratory'`), `power: float = 0.80` | Sample size per variant, duration estimates for low/medium/high traffic |
| `calculate_significance()` | `variant_a_conversions: int`, `variant_a_visitors: int`, `variant_b_conversions: int`, `variant_b_visitors: int` | Z-score, p-value, significance at 90%/95%, decision recommendation |
| `track_test_results()` | `test_id: str`, `results_data: Dict` | Progress tracking, current significance, next steps |
| `generate_test_report()` | `test_id: str`, `final_results: Dict` | Complete report with insights, implementation plan, learnings |

**Convenience Function:** `plan_ab_test(test_type, variant_a, variant_b, hypothesis, baseline_conversion)`

### review_analyzer.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `ReviewAnalyzer(app_name: str)`

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `analyze_sentiment()` | `reviews: List[Dict]` (each: text, rating, date) | Sentiment distribution (positive/neutral/negative %), average rating, detailed sentiments |
| `extract_common_themes()` | `reviews: List[Dict]`, `min_mentions: int = 3` | Common words, phrases, categorized themes (features, performance, usability, support, pricing) |
| `identify_issues()` | `reviews: List[Dict]`, `rating_threshold: int = 3` | Categorized issues (crashes, bugs, performance, compatibility) with severity scores and priority |
| `find_feature_requests()` | `reviews: List[Dict]` | Clustered and prioritized feature requests |
| `track_sentiment_trends()` | `reviews_by_period: Dict[str, List[Dict]]` | Trend direction (improving/declining/stable), period-over-period comparison |
| `generate_response_templates()` | `issue_category: str` (`'crash'`, `'bug'`, `'feature_request'`, `'positive'`, `'negative_general'`) | Response templates for review management |

**Convenience Function:** `analyze_reviews(app_name, reviews)` -- Runs sentiment, themes, issues, and feature requests in one call.

### launch_checklist.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `LaunchChecklistGenerator(platform: str = 'both')` -- Platform: `'apple'`, `'google'`, or `'both'`

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `generate_prelaunch_checklist()` | `app_info: Dict` (name, category, target_audience), `launch_date: Optional[str]` (YYYY-MM-DD) | Platform-specific checklists, universal checklist, timeline with milestones, completion summary |
| `validate_app_store_compliance()` | `app_data: Dict`, `platform: str = 'apple'` | Compliance validation with errors, warnings, recommendations |
| `create_update_plan()` | `current_version: str`, `planned_features: List[str]`, `update_frequency: str = 'monthly'` | Version schedule, feature distribution, What's New templates |
| `optimize_launch_timing()` | `app_category: str`, `target_audience: str`, `current_date: Optional[str]` | Optimal dates, day-of-week recommendation, seasonal considerations |
| `plan_seasonal_campaigns()` | `app_category: str`, `current_month: int = None` | Seasonal opportunities, campaign ideas, implementation timeline |

**Convenience Function:** `generate_launch_checklist(platform, app_info, launch_date)`

### localization_helper.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `LocalizationHelper(app_category: str = 'general')`

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `identify_target_markets()` | `current_market: str = 'en-US'`, `budget_level: str = 'medium'` (`'low'`/`'medium'`/`'high'`), `target_market_count: int = 5` | Prioritized markets (tier 1/2/3), estimated costs, phased implementation plan |
| `translate_metadata()` | `source_metadata: Dict[str, str]`, `source_language: str`, `target_language: str`, `platform: str = 'apple'` | Character limit validation per field with language-specific multipliers, translation notes |
| `adapt_keywords()` | `source_keywords: List[str]`, `source_language: str`, `target_language: str`, `target_market: str` | Adaptation strategy per keyword (full_localization / adapt_and_translate / direct_translation), cultural considerations |
| `validate_translations()` | `translated_metadata: Dict[str, str]`, `target_language: str`, `platform: str = 'apple'` | Character limit validation, quality checks (placeholders, excessive punctuation) |
| `calculate_localization_roi()` | `target_markets: List[str]`, `current_monthly_downloads: int`, `localization_cost: float`, `expected_lift_percentage: float = 0.15` | Market breakdown, expected monthly lift, payback period, annual ROI |

**Convenience Function:** `plan_localization_strategy(current_market, budget_level, monthly_downloads)`
