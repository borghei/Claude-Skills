---
name: app-store-optimization
description: >
  App Store Optimization toolkit for researching keywords, optimizing metadata,
  and tracking mobile app performance on Apple App Store and Google Play Store.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: marketing
  domain: aso
  updated: 2026-06-15
  tags: [aso, app-store, google-play, keywords, ratings]
---
# App Store Optimization (ASO)

ASO tools for researching keywords, optimizing metadata, analyzing competitors, and improving app store visibility on Apple App Store and Google Play Store. This file is a lean map — execute a task by loading the matching reference below.

## Core Capabilities

- **Keyword research** — seed/expand/score keywords by relevance, volume, competition, and conversion intent; map to metadata placements
- **Metadata optimization** — title, subtitle/short description, iOS keyword field, and full description against platform character limits and density targets
- **Competitor analysis** — keyword matrices, gap analysis, visual and ratings benchmarking across the top 10 competitors
- **Launch & A/B testing** — structured launch checklists, timing, and conversion experiments with sample-size and significance math
- **Reviews & localization** — sentiment/theme/issue extraction and multi-market metadata adaptation
- **8 Python tools** — `keyword_analyzer`, `metadata_optimizer`, `competitor_analyzer`, `aso_scorer`, `ab_test_planner`, `review_analyzer`, `launch_checklist`, `localization_helper` (stdlib only, analyze data you provide)

## When to Use

- Researching or scoring keywords for an app store listing
- Optimizing a title/subtitle/description/keyword field for ranking and conversion
- Auditing competitors for keyword gaps and positioning opportunities
- Planning an app launch or running a store-listing A/B test
- Analyzing reviews or planning multi-market localization

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Platform** — Apple App Store vs Google Play (different character limits, keyword field vs description indexing, ranking factors)
- [ ] **App category + seed keywords** — the app's space and starting terms (drives keyword research + scoring)
- [ ] **Primary goal** — ranking visibility vs conversion rate (shapes metadata, title/subtitle, and screenshot priorities)
- [ ] **Target market/locale** — which storefronts (drives localization + keyword volume estimates)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/keyword_analyzer.py --keywords "todo,task,planner"
python scripts/metadata_optimizer.py --platform ios --title "App Title"
python scripts/aso_scorer.py --app-id com.example.app
```

Note: the scripts are importable Python libraries — see the Tool Reference for classes, methods, and convenience functions.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/aso-workflows.md](references/aso-workflows.md)** — step-by-step procedures, scoring criteria, placement tables, structure diagrams, templates, and before/after examples for all five workflows. Read when executing keyword research, metadata optimization, competitor analysis, launch, or A/B testing.
- **[references/tool-reference.md](references/tool-reference.md)** — full usage for the 8 Python scripts: classes, methods, parameters, returns, convenience functions, plus the scripts and assets tables. Read before invoking a tool.
- **[references/operations-and-benchmarks.md](references/operations-and-benchmarks.md)** — troubleshooting table, success criteria/targets, platform limitations, proactive triggers, output artifacts, communication standards, related skills, and the full integration matrix. Read when diagnosing issues, setting targets, or wiring into other tools.
- **[references/keyword-research-guide.md](references/keyword-research-guide.md)** — research methodology, evaluation framework, and tracking. Read for deep keyword discovery and selection.
- **[references/platform-requirements.md](references/platform-requirements.md)** — iOS and Android metadata specs and visual asset requirements. Read when validating fields against platform rules.
- **[references/aso-best-practices.md](references/aso-best-practices.md)** — optimization strategies, rating management, and launch tactics. Read for proven tactics and playbooks.

## Scope & Limitations

**In scope:** keyword research, metadata optimization and character-limit validation, competitor ASO analysis (public data), A/B test planning with significance math, launch/seasonal/localization planning, and review sentiment analysis for Apple App Store and Google Play Store.

**Out of scope:** real-time store data fetching (scripts analyze static data you provide), Apple Search Ads / Google Ads campaign management, creative asset design, cross-device attribution (use an MMP), in-app analytics/retention, and revenue/subscription pricing.

**Data constraints:** no official search-volume API exists for either store (estimates use third-party tools or heuristics); competitor and review data are limited to public info; historical ranking data needs external tools (AppTweak, Sensor Tower, data.ai); Apple's June 2025 update indexes screenshot text, which these scripts do not yet analyze. See [references/operations-and-benchmarks.md](references/operations-and-benchmarks.md) for details.

## Integration Points

Connects to **Apple App Store Connect** and **Google Play Console** (metadata submission, Product Page Optimization / Store Listing Experiments), **Apple Search Ads** (keyword discovery), **ASO tools** (AppTweak, Sensor Tower, data.ai for volume/ranking data), **analytics** (Firebase/Mixpanel/Amplitude for engagement signals), and the **campaign-analytics** and **content-creator** skills. Full connection details and data flows: [references/operations-and-benchmarks.md](references/operations-and-benchmarks.md).
