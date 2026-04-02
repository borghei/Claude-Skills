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
