---
name: video-content-strategist
description: >
  This skill should be used when the user asks to "plan video content", "create a video
  calendar", "optimize video SEO", "analyze thumbnail performance", "improve video titles",
  "schedule video production", or "build a YouTube strategy".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: video
  updated: 2026-04-02
  tags: [video, youtube, content-calendar, thumbnail, seo, video-strategy]
---
# Video Content Strategist Skill

## Overview

Production-ready video content strategy toolkit for planning content calendars, analyzing thumbnail effectiveness, and optimizing video metadata for platform SEO. Designed for content creators, marketing teams, and video producers managing consistent video output across YouTube, TikTok, LinkedIn, and other platforms.

## Clarify First

Before planning, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Platform(s):** YouTube, TikTok, LinkedIn, or Instagram — sets optimal video length and SEO approach.
- **Deliverable:** content calendar, thumbnail analysis, or SEO metadata optimization — selects the tool and workflow.
- **Audience & content pillars:** who it's for and the pillar mix/ratios — drives calendar topics and formats.
- **Posting frequency:** videos per week and planning horizon — sets the production schedule.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Plan a video content calendar from topics and audience data
python scripts/video_content_planner.py topics.json --weeks 8 --frequency 3

# Analyze thumbnail text and composition patterns
python scripts/thumbnail_analyzer.py thumbnails.csv

# Optimize video titles, descriptions, and tags for SEO
python scripts/video_seo_optimizer.py video_data.json --platform youtube
```

## Tools Overview

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `video_content_planner.py` | Content calendar generation | JSON with topics/audience | Weekly calendar + production schedule |
| `thumbnail_analyzer.py` | Thumbnail pattern analysis | CSV with thumbnail data | Optimization recommendations |
| `video_seo_optimizer.py` | Video metadata SEO | JSON with video details | Optimized titles, descriptions, tags |

## Workflows

### Workflow 1: Monthly Video Strategy

1. Define audience personas and content pillars in topics JSON
2. Run `video_content_planner.py` to generate 4-week calendar
3. For each planned video, run `video_seo_optimizer.py` for metadata
4. After publishing, collect thumbnail data and run `thumbnail_analyzer.py`
5. Feed learnings back into next month's planning cycle

### Workflow 2: YouTube Channel Optimization

1. Export existing video data (titles, descriptions, tags, performance)
2. Run `video_seo_optimizer.py` on underperforming videos to identify metadata gaps
3. Run `thumbnail_analyzer.py` on top vs bottom performers
4. Apply optimizations to existing videos and use patterns for new content

### Workflow 3: Multi-Platform Video Strategy

1. Create topics JSON with platform-specific audience data
2. Run `video_content_planner.py` with `--platforms youtube,tiktok,linkedin`
3. Get platform-adapted content recommendations
4. Optimize each platform's metadata with `video_seo_optimizer.py`

## Reference Documentation

See `references/video-strategy-guide.md` for comprehensive frameworks covering:
- Content pillar strategy
- Platform-specific best practices
- Thumbnail design principles
- Video SEO fundamentals
- Production workflow optimization

## Common Patterns

### Pattern: Topics JSON Format
```json
{
  "channel": "TechStartupTV",
  "audience": {
    "primary": "SaaS founders, 25-45",
    "interests": ["startup growth", "fundraising", "product development"],
    "pain_points": ["scaling teams", "finding product-market fit", "managing burn rate"]
  },
  "content_pillars": [
    {"name": "Founder Stories", "ratio": 0.3, "format": "interview", "avg_length_min": 25},
    {"name": "Tactical Guides", "ratio": 0.4, "format": "tutorial", "avg_length_min": 12},
    {"name": "Industry Analysis", "ratio": 0.2, "format": "commentary", "avg_length_min": 8},
    {"name": "Behind the Scenes", "ratio": 0.1, "format": "vlog", "avg_length_min": 5}
  ],
  "topics": [
    {"title": "How We Hit $1M ARR", "pillar": "Founder Stories", "priority": "high"},
    {"title": "5 Pricing Strategies That Work", "pillar": "Tactical Guides", "priority": "high"},
    {"title": "AI in SaaS: 2026 Trends", "pillar": "Industry Analysis", "priority": "medium"}
  ]
}
```

### Pattern: Thumbnail CSV Format
```csv
video_id,title,views,ctr_pct,has_face,has_text,text_words,colors_dominant,emotion
V001,How to Scale,15000,8.2,yes,yes,3,red-yellow,surprise
V002,Tech Review,8500,4.1,no,yes,5,blue-white,neutral
```

### Platform Video Length Guidelines

| Platform | Optimal Length | Max Recommended |
|----------|---------------|-----------------|
| YouTube (standard) | 8-15 min | 25 min |
| YouTube Shorts | 30-60 sec | 60 sec |
| TikTok | 30-90 sec | 3 min |
| LinkedIn | 1-3 min | 10 min |
| Instagram Reels | 15-60 sec | 90 sec |

## Scope & Limitations

**In Scope:**
- Content calendar and production schedule from a topics JSON with content pillars and ratios, with `video_content_planner.py` (weeks, videos per week, target platforms, start date)
- Thumbnail pattern analysis from a CSV of thumbnail attributes and performance (face, text, word count, colours, emotion, views, CTR) with `thumbnail_analyzer.py`
- Title, description and tag recommendations for YouTube, TikTok or LinkedIn with `video_seo_optimizer.py`, singly or in batch
- A strategy guide covering content pillars, platform practices, thumbnail design principles, video SEO and production checklists

**Out of Scope:**
- Scripting, filming or editing video, and designing thumbnail images
- Uploading, scheduling or publishing videos; the tools have no platform API access
- Social media strategy beyond video, such as platform selection and community management (see `marketing/social-media-manager/`)
- Paid video ad campaigns (see `marketing/paid-ads/`)

**Important Caveats:**
- The thumbnail analyzer does not look at images. It works only from attributes you tag by hand in the CSV, so results depend on consistent tagging.
- Performance data such as views and CTR must be exported from each platform and entered manually.
- SEO recommendations and the platform length guidelines are rule-based heuristics, not platform-published rules. Platform ranking and format limits change, so check current platform guidance before relying on them.
