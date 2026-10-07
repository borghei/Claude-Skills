---
title: Tools — LinkedIn Suite
description: Platform toolkits. The LinkedIn suite covers finding what to say, planning, writing, humanizing, commenting, replying, profile, team advocacy and engagement analysis. Offline, stdlib-only tools.
---

# Tools

**12 skills** with **27 stdlib-only Python tools**. Platform toolkits live here; the first is the **LinkedIn suite**.

Where [Marketing](marketing.md) covers channel strategy, these skills do the hands-on work on one platform: decide what to say, write it, check it, publish it yourself, and learn from who responded.

!!! info "New domain (October 2026)"
    **Offline by design.** No skill here posts, schedules, or scrapes. Each produces drafts and plans you paste into LinkedIn yourself, and analyses text or exports you provide. Scripts use the standard library only and make no network calls. Several tools are gates that exit non-zero on their flawed sample input; each `SKILL.md` documents its exit codes.

## LinkedIn suite

### linkedin-story-interviewer

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-story-interviewer){ .md-button }

Interviews a person to surface what they actually have to say, and keeps the answers in a local story bank file that later LinkedIn drafts draw on. Use when someone has never posted, when drafts keep coming out generic, or when the story bank is thin or stale.

**Tools:** `story_bank_audit.py`, `story_bank_rules.py`

### linkedin-content-planner

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-content-planner){ .md-button }

Builds a weekly or monthly LinkedIn publishing plan from content pillars, a posting cadence and a format mix, with a founder-oriented pillar set as an alternative to the general one. Use when planning a week, a month or a launch period of posts rather than drafting a single post.

**Tools:** `plan_builder.py`, `plan_rules.py`

### linkedin-post-writer

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-post-writer){ .md-button }

Drafts LinkedIn posts from a brief: picks an angle and opening pattern the author's real material supports, structures the body, and gates the draft before it is pasted. Use when writing a post, choosing a hook, or checking a draft before publishing.

**Tools:** `angle_picker.py`, `post_gate.py`

### linkedin-hook-analyzer

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-hook-analyzer){ .md-button }

Extracts and classifies the opening-line pattern of LinkedIn posts the user pastes or saves, and turns each into a reusable slot template with cautions. Use when studying why an opening works, building a swipe file, or adapting a hook pattern without copying it.

**Tools:** `hook_classifier.py`, `hook_patterns.py`

### linkedin-humanizer

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-humanizer){ .md-button }

Audits and rewrites LinkedIn drafts to remove machine-sounding patterns: tiered tell catalogue, emoji-pattern scoring, rule explanations, and a voice fingerprint built from the author's own posts. Use when a draft reads generated, before publishing, or when an edit flattened someone's voice.

**Tools:** `emoji_audit.py`, `tell_audit.py`, `tell_rules.py`, `voice_fingerprint.py`

### linkedin-content-repurposer

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-content-repurposer){ .md-button }

Turns something made for another channel (a thread, a video or talk transcript, a blog post, a newsletter) into a post that reads as native to LinkedIn, without changing what the source says. Use when existing material should become a LinkedIn post rather than writing one from a blank page.

**Tools:** `draft_fidelity_check.py`, `repurpose_analyzer.py`, `repurpose_rules.py`

### linkedin-comment-writer

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-comment-writer){ .md-button }

Drafts comments on other people's LinkedIn posts that add a specific the post lacked, then gates them offline. Use when commenting on a post, engaging with a prospect or peer, or checking a comment before pasting it.

**Tools:** `comment_linter.py`, `comment_rules.py`

### linkedin-reply-manager

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-reply-manager){ .md-button }

Triages a pasted LinkedIn comment section and drafts replies: which comments to answer, in what order, which to ignore. Use when answering comments on your own post, replying inside a thread, or clearing a backlog.

**Tools:** `comment_triage.py`, `reply_linter.py`

### linkedin-thread-tracker

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-thread-tracker){ .md-button }

Keeps a local log of LinkedIn comments you left, records who replied, and reports follow-ups due, overdue, or dead. Use when logging a comment, checking which threads need an answer, or reviewing reply rates.

**Tools:** `thread_log.py`, `thread_tracker.py`

### linkedin-profile-optimizer

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-profile-optimizer){ .md-button }

Audits and rewrites a LinkedIn profile from pasted text: headline, About, experience, skills, Featured, banner and photo. Use when reviewing a profile, fixing a headline or About, or preparing a profile before posting more.

**Tools:** `profile_auditor.py`, `profile_rules.py`

### linkedin-employee-advocacy

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-employee-advocacy){ .md-button }

Designs and runs an employee advocacy programme: who posts what and how often, review rules, and what is never scripted. Use when getting a team posting, writing an advocacy policy, or fixing a programme that has stalled.

**Tools:** `advocacy_planner.py`, `advocacy_rules.py`

### linkedin-engagement-analytics

[:material-folder-open: Browse on GitHub](https://github.com/borghei/Claude-Skills/tree/main/tools/linkedin/linkedin-engagement-analytics){ .md-button }

Segments who reacted to and commented on a post from a CSV or JSON export, and says whether it reached the intended audience. Use when reviewing a post's engagers, checking audience fit, or building a baseline.

**Tools:** `engager_segmenter.py`, `segment_rules.py`

## How the suite fits together

| Stage | Skill |
|---|---|
| Find material | `linkedin-story-interviewer` |
| Plan | `linkedin-content-planner` |
| Write | `linkedin-post-writer`, `linkedin-hook-analyzer`, `linkedin-content-repurposer` |
| Check | `linkedin-humanizer` |
| Converse | `linkedin-comment-writer`, `linkedin-reply-manager`, `linkedin-thread-tracker` |
| Presence | `linkedin-profile-optimizer`, `linkedin-employee-advocacy` |
| Learn | `linkedin-engagement-analytics` |

Each skill is self-contained and installs alone. Where one accepts another's output (the story bank file), that input is optional.
