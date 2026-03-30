---
name: social-media-analyzer
description: >
  Social media campaign analysis and performance tracking. Calculates engagement
  rates, ROI, and benchmarks across platforms. Use for analyzing social media
  performance, calculating engagement rate, measuring campaign ROI, comparing
  platform metrics, or benchmarking against industry standards.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: social-media
  updated: 2026-03-31
  tags: [social-media, analytics, sentiment-analysis, engagement]
---
# Social Media Analyzer

Campaign performance analysis with engagement metrics, ROI calculations, and platform benchmarks.

---

## Table of Contents

- [Analysis Workflow](#analysis-workflow)
- [Engagement Metrics](#engagement-metrics)
- [ROI Calculation](#roi-calculation)
- [Platform Benchmarks](#platform-benchmarks)
- [Tools](#tools)
- [Examples](#examples)

---

## Analysis Workflow

Analyze social media campaign performance:

1. Validate input data completeness (reach > 0, dates valid)
2. Calculate engagement metrics per post
3. Aggregate campaign-level metrics
4. Calculate ROI if ad spend provided
5. Compare against platform benchmarks
6. Identify top and bottom performers
7. Generate recommendations
8. **Validation:** Engagement rate < 100%, ROI matches spend data

### Input Requirements

| Field | Required | Description |
|-------|----------|-------------|
| platform | Yes | instagram, facebook, twitter, linkedin, tiktok |
| posts[] | Yes | Array of post data |
| posts[].likes | Yes | Like/reaction count |
| posts[].comments | Yes | Comment count |
| posts[].reach | Yes | Unique users reached |
| posts[].impressions | No | Total views |
| posts[].shares | No | Share/retweet count |
| posts[].saves | No | Save/bookmark count |
| posts[].clicks | No | Link clicks |
| total_spend | No | Ad spend (for ROI) |

### Data Validation Checks

Before analysis, verify:

- [ ] Reach > 0 for all posts (avoid division by zero)
- [ ] Engagement counts are non-negative
- [ ] Date range is valid (start < end)
- [ ] Platform is recognized
- [ ] Spend > 0 if ROI requested

---

## Engagement Metrics

### Engagement Rate Calculation

```
Engagement Rate = (Likes + Comments + Shares + Saves) / Reach × 100
```

### Metric Definitions

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Engagement Rate | Engagements / Reach × 100 | Audience interaction level |
| CTR | Clicks / Impressions × 100 | Content click appeal |
| Reach Rate | Reach / Followers × 100 | Content distribution |
| Virality Rate | Shares / Impressions × 100 | Share-worthiness |
| Save Rate | Saves / Reach × 100 | Content value |

### Performance Categories

| Rating | Engagement Rate | Action |
|--------|-----------------|--------|
| Excellent | > 6% | Scale and replicate |
| Good | 3-6% | Optimize and expand |
| Average | 1-3% | Test improvements |
| Poor | < 1% | Analyze and pivot |

---

## ROI Calculation

Calculate return on ad spend:

1. Sum total engagements across posts
2. Calculate cost per engagement (CPE)
3. Calculate cost per click (CPC) if clicks available
4. Estimate engagement value using benchmark rates
5. Calculate ROI percentage
6. **Validation:** ROI = (Value - Spend) / Spend × 100

### ROI Formulas

| Metric | Formula |
|--------|---------|
| Cost Per Engagement (CPE) | Total Spend / Total Engagements |
| Cost Per Click (CPC) | Total Spend / Total Clicks |
| Cost Per Thousand (CPM) | (Spend / Impressions) × 1000 |
| Return on Ad Spend (ROAS) | Revenue / Ad Spend |

### Engagement Value Estimates

| Action | Value | Rationale |
|--------|-------|-----------|
| Like | $0.50 | Brand awareness |
| Comment | $2.00 | Active engagement |
| Share | $5.00 | Amplification |
| Save | $3.00 | Intent signal |
| Click | $1.50 | Traffic value |

### ROI Interpretation

| ROI % | Rating | Recommendation |
|-------|--------|----------------|
| > 500% | Excellent | Scale budget significantly |
| 200-500% | Good | Increase budget moderately |
| 100-200% | Acceptable | Optimize before scaling |
| 0-100% | Break-even | Review targeting and creative |
| < 0% | Negative | Pause and restructure |

---

## Platform Benchmarks

### Engagement Rate by Platform

| Platform | Average | Good | Excellent |
|----------|---------|------|-----------|
| Instagram | 1.22% | 3-6% | >6% |
| Facebook | 0.07% | 0.5-1% | >1% |
| Twitter/X | 0.05% | 0.1-0.5% | >0.5% |
| LinkedIn | 2.0% | 3-5% | >5% |
| TikTok | 5.96% | 8-15% | >15% |

### CTR by Platform

| Platform | Average | Good | Excellent |
|----------|---------|------|-----------|
| Instagram | 0.22% | 0.5-1% | >1% |
| Facebook | 0.90% | 1.5-2.5% | >2.5% |
| LinkedIn | 0.44% | 1-2% | >2% |
| TikTok | 0.30% | 0.5-1% | >1% |

### CPC by Platform

| Platform | Average | Good |
|----------|---------|------|
| Facebook | $0.97 | <$0.50 |
| Instagram | $1.20 | <$0.70 |
| LinkedIn | $5.26 | <$3.00 |
| TikTok | $1.00 | <$0.50 |

See `references/platform-benchmarks.md` for complete benchmark data.

---

## Tools

### Calculate Metrics

```bash
python scripts/calculate_metrics.py assets/sample_input.json
```

Calculates engagement rate, CTR, reach rate for each post and campaign totals.

### Analyze Performance

```bash
python scripts/analyze_performance.py assets/sample_input.json
```

Generates full performance analysis with ROI, benchmarks, and recommendations.

**Output includes:**
- Campaign-level metrics
- Post-by-post breakdown
- Benchmark comparisons
- Top performers ranked
- Actionable recommendations

---

## Examples

### Sample Input

See `assets/sample_input.json`:

```json
{
  "platform": "instagram",
  "total_spend": 500,
  "posts": [
    {
      "post_id": "post_001",
      "content_type": "image",
      "likes": 342,
      "comments": 28,
      "shares": 15,
      "saves": 45,
      "reach": 5200,
      "impressions": 8500,
      "clicks": 120
    }
  ]
}
```

### Sample Output

See `assets/expected_output.json`:

```json
{
  "campaign_metrics": {
    "total_engagements": 1521,
    "avg_engagement_rate": 8.36,
    "ctr": 1.55
  },
  "roi_metrics": {
    "total_spend": 500.0,
    "cost_per_engagement": 0.33,
    "roi_percentage": 660.5
  },
  "insights": {
    "overall_health": "excellent",
    "benchmark_comparison": {
      "engagement_status": "excellent",
      "engagement_benchmark": "1.22%",
      "engagement_actual": "8.36%"
    }
  }
}
```

### Interpretation

The sample campaign shows:
- **Engagement rate 8.36%** vs 1.22% benchmark = Excellent (6.8x above average)
- **CTR 1.55%** vs 0.22% benchmark = Excellent (7x above average)
- **ROI 660%** = Outstanding return on $500 spend
- **Recommendation:** Scale budget, replicate successful elements

---

## Reference Documentation

### Platform Benchmarks

`references/platform-benchmarks.md` contains:

- Engagement rate benchmarks by platform and industry
- CTR benchmarks for organic and paid content
- Cost benchmarks (CPC, CPM, CPE)
- Content type performance by platform
- Optimal posting times and frequency
- ROI calculation formulas

## Proactive Triggers

- **Engagement rate below platform average** -- Content isn't resonating. Analyze top performers for patterns to replicate.
- **Follower growth stalled** -- Content distribution or frequency issue. Audit posting patterns and content mix.
- **High impressions, low engagement** -- Reach without resonance. Content quality or relevance issue needs addressing.
- **Competitor outperforming significantly** -- Content gap detected. Analyze their successful posts for format and topic insights.

## Output Artifacts

| When you ask for... | You get... |
|---------------------|------------|
| "Social media audit" | Performance analysis across platforms with benchmarks |
| "What's performing?" | Top content analysis with patterns and recommendations |
| "Competitor social analysis" | Competitive social media comparison with gaps |
| "Campaign ROI" | Full ROI calculation with engagement value estimates |

## Communication

All output passes quality verification:
- Self-verify: source attribution, assumption audit, confidence scoring
- Output format: Bottom Line first, then What (with confidence), Why, How to Act
- Every finding tagged with confidence level: verified, medium confidence, or assumed

## Related Skills

- **campaign-analytics**: For cross-channel analytics including social alongside other channels.
- **content-creator**: For creating social media content optimized by analysis findings.
- **marketing-demand-acquisition**: For integrating social media into broader demand gen strategy.
- **marketing-strategy-pmm**: For aligning social content with product marketing positioning.

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Engagement rate appears unrealistically high (>50%) | Reach value is too low relative to engagements, or reach/impressions data is swapped | Verify that `reach` represents unique users reached (not impressions). Engagement rate = (likes + comments + shares + saves) / reach. If using Instagram data from 2025+, note that Instagram shifted from "impressions" to "views" as primary metric -- ensure you are using the correct field |
| Benchmark comparison shows "no_benchmark_available" | Platform name in input JSON does not match expected values | Use exact lowercase platform names: `instagram`, `facebook`, `twitter`, `linkedin`, `tiktok`. The analyzer matches against these exact strings |
| ROI calculation shows negative despite good engagement | Engagement value estimates are too conservative for your industry | The default engagement value model uses $0.50/like, $2.00/comment, $5.00/share, $3.00/save, $1.50/click. Adjust these values in `calculate_metrics.py` for your specific vertical. B2B companies typically have higher per-engagement values than B2C |
| TikTok metrics show low engagement compared to benchmarks | Using reach-based calculation on a platform where view-based metrics are standard | TikTok's 2026 benchmark engagement rate of 2.50-3.70% is calculated against views, not reach. Ensure your TikTok data uses video views in the `reach` field for accurate comparison. TikTok engagement rates rose 49% YoY in 2025 |
| LinkedIn engagement appears lower than expected | Comparing against outdated benchmarks | LinkedIn's 2026 median engagement rate is approximately 3.85-6.1%, significantly higher than other platforms. Carousel/document posts earn the highest engagement (up to 21.77% median). If your rate is below 2%, focus on conversation-starting content rather than corporate announcements |
| Instagram metrics declining despite consistent content quality | Algorithm and metric definition changes in 2025-2026 | Instagram shifted to "Views" as its primary metric across all formats (Reels, Stories, posts), replacing "Impressions" and "Plays." Carousel posts now earn the most engagement. Meta plans to replace reach with "Viewers" metric in Graph API by June 2026. Adapt your data collection accordingly |
| Campaign analysis has too few posts for reliable insights | Small sample size produces unreliable averages | Minimum 10 posts recommended for meaningful analysis. The `analyze_performance.py` script flags campaigns with fewer than 10 posts. For statistical reliability, aim for 30+ posts per analysis period |

---

## Success Criteria

- **Engagement Rate by Platform (2026 benchmarks)**: Instagram 0.50-0.70% (average), 3-6% (good), >6% (excellent). Facebook 0.06-0.09% (average), 0.5-1% (good). LinkedIn 3.85-6.1% (average), >6% (good). TikTok 2.50-3.70% (average), 8-15% (good), >15% (excellent). Twitter/X 0.03-0.05% (average), 0.1-0.5% (good)
- **Click-Through Rate**: Instagram >0.5% (good), Facebook >1.5% (good), LinkedIn >1.0% (good), TikTok >0.5% (good). Featured snippets and carousels drive highest CTR across platforms
- **Cost Per Click**: Facebook <$0.50 (good), Instagram <$0.70 (good), LinkedIn <$3.00 (good, but averages $4-5+ for B2B), TikTok <$0.50 (good). LinkedIn CPC has risen 89% since 2023
- **ROI Threshold**: Target minimum 200% ROI on paid social. Campaigns above 500% are excellent and should be scaled. Campaigns below 100% need immediate creative or targeting revision
- **Content Format Performance**: Prioritize high-engagement formats per platform -- carousel/document posts on LinkedIn (21.77% median engagement), Reels on Instagram, short-form video on TikTok. Test at least 3 content formats per month
- **Posting Frequency**: Maintain consistent posting cadence: LinkedIn 3-5x/week, Instagram 4-7x/week, TikTok 3-5x/week. The LinkedIn algorithm favors content that generates meaningful engagement in the first 90 minutes
- **Analysis Cadence**: Run full performance analysis weekly for active campaigns. Compare month-over-month trends to identify growth or decline patterns. Update benchmark baselines quarterly as platform norms shift rapidly

---

## Scope & Limitations

**In Scope:**
- Post-level and campaign-level engagement metrics (engagement rate, CTR, reach rate, virality rate, save rate)
- ROI calculation with engagement value estimates and cost efficiency metrics (CPE, CPC, CPM, ROAS)
- Platform benchmark comparison for Instagram, Facebook, Twitter/X, LinkedIn, and TikTok
- Top/bottom performer identification and ranking
- Actionable recommendations based on benchmark assessment

**Out of Scope:**
- Real-time API connections to social media platforms (scripts analyze static JSON data you export)
- Social media scheduling, publishing, or content creation
- Follower growth tracking or audience demographics analysis
- Competitor social media monitoring (use dedicated social listening tools)
- Influencer identification or collaboration management
- Social commerce and shopping metrics
- Video-specific analytics (watch time, completion rate, drop-off points)
- Sentiment analysis on comments or mentions (use the app-store-optimization skill's review_analyzer for text sentiment)
- Cross-platform identity resolution or deduplication

**Platform API Changes (2025-2026):**
- Meta/Instagram is replacing "reach" with "Viewers" metric in Graph API by June 2026
- Instagram shifted to "Views" as primary metric across all formats, replacing "Impressions" and "Plays"
- TikTok tightened API access approval process in 2025
- LinkedIn added AI-powered conversational search; algorithm now favors people-first content over polished corporate updates

---

## Integration Points

| Integration | Purpose | How to Connect |
|-------------|---------|----------------|
| **Meta Business Suite** | Export Instagram and Facebook campaign data | Export post-level metrics (likes, comments, shares, reach, impressions, clicks) as JSON for `calculate_metrics.py` and `analyze_performance.py`. Note: "Views" is replacing "Impressions" in 2026 |
| **LinkedIn Campaign Manager** | Export LinkedIn ad and organic performance data | Export engagement metrics per post. LinkedIn's native analytics now includes "Viewer" demographics and AI search visibility data |
| **TikTok Business Center** | Export TikTok campaign performance data | Export video-level metrics. Use video views as the reach equivalent for engagement rate calculation |
| **Google Analytics 4 (GA4)** | Track social traffic and conversions on your website | Connect social campaign UTM parameters to GA4 to measure downstream conversions. Use `campaign-analytics` skill for full attribution |
| **campaign-analytics skill** | Cross-channel ROI comparison | Feed social media ROI data into `campaign_roi_calculator.py` alongside other channels for unified portfolio analysis |
| **content-creator skill** | Content optimization based on performance data | Use top-performing post analysis to inform content strategy. Apply `brand_voice_analyzer.py` to ensure social content matches brand voice |
| **marketing-demand-acquisition skill** | Social as demand gen channel | Integrate social performance data into demand gen channel mix evaluation. Use CAC data from social alongside other acquisition channels |

---

## Tool Reference

### calculate_metrics.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `SocialMediaMetricsCalculator(campaign_data: Dict)`

**Constructor Input:** `{"platform": "instagram", "total_spend": 500, "posts": [{"post_id": "str", "content_type": "str", "likes": int, "comments": int, "shares": int, "saves": int, "reach": int, "impressions": int, "clicks": int}]}`

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `calculate_engagement_rate()` | `post: Dict` (likes, comments, shares, saves, reach) | Engagement rate as percentage (float). Formula: (likes + comments + shares + saves) / reach * 100 |
| `calculate_ctr()` | `clicks: int`, `impressions: int` | CTR as percentage (float) |
| `calculate_campaign_metrics()` | None (uses constructor data) | Dict with platform, total_posts, total_engagements, total_reach, total_impressions, total_clicks, avg_engagement_rate, ctr |
| `calculate_roi_metrics()` | None (uses constructor data) | Dict with total_spend, cost_per_engagement, cost_per_click, estimated_value (at $2.50/engagement default), roi_percentage |
| `identify_top_posts()` | `metric: str = 'engagement_rate'`, `limit: int = 5` | Sorted list of top posts by specified metric. Supported metrics: `engagement_rate`, `likes`, `comments`, `shares`, `clicks` |
| `analyze_all()` | None | Combined dict of campaign_metrics, roi_metrics, and top_posts |

### analyze_performance.py

**Type:** Python library (imported, not CLI)

**Classes:**
- `PerformanceAnalyzer(campaign_metrics: Dict, roi_metrics: Dict)`

**Built-in Benchmarks:** Engagement rate and CTR benchmarks for `facebook`, `instagram`, `twitter`, `linkedin`, `tiktok`.

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `benchmark_performance()` | None | Dict with engagement_status, engagement_benchmark, engagement_actual, ctr_status, ctr_benchmark, ctr_actual. Status values: `excellent` (>=1.5x benchmark), `good` (>=benchmark), `below_average` |
| `generate_recommendations()` | None | List of actionable recommendation strings based on engagement rate, CTR, CPC, ROI, and post volume thresholds |
| `generate_insights()` | None | Dict with overall_health (`excellent`/`good`/`needs_improvement`), benchmark_comparison, recommendations, key_strengths, areas_for_improvement |
