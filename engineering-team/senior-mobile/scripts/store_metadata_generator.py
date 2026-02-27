#!/usr/bin/env python3
"""
App Store / Play Store Metadata Generator
==========================================

CLI tool that generates structured metadata for App Store (iOS) and
Google Play Store (Android) submissions.

Given an app name, category, description, and feature list, this tool
produces:
  - App title variants (short, long, localized-friendly)
  - Keyword suggestions derived from features and category
  - Category recommendations for both stores
  - Privacy label / Data Safety framework guidance
  - Age rating guidance (ESRB / IARC questionnaire prep)

Usage:
  python store_metadata_generator.py --app-name "My App" --category productivity --features "offline,sync,biometric"
  python store_metadata_generator.py --app-name "FitTrack" --category health --features "workout,tracking,social" --description "Track workouts" --json

Dependencies: Python 3.8+ standard library only.
"""

import argparse
import json
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants - Store categories
# ---------------------------------------------------------------------------

APP_STORE_CATEGORIES = {
    "business": {"ios": "Business", "android": "Business", "ios_id": 6000},
    "education": {"ios": "Education", "android": "Education", "ios_id": 6017},
    "entertainment": {"ios": "Entertainment", "android": "Entertainment", "ios_id": 6016},
    "finance": {"ios": "Finance", "android": "Finance", "ios_id": 6015},
    "food": {"ios": "Food & Drink", "android": "Food & Drink", "ios_id": 6023},
    "games": {"ios": "Games", "android": "Games", "ios_id": 6014},
    "health": {"ios": "Health & Fitness", "android": "Health & Fitness", "ios_id": 6013},
    "lifestyle": {"ios": "Lifestyle", "android": "Lifestyle", "ios_id": 6012},
    "music": {"ios": "Music", "android": "Music & Audio", "ios_id": 6011},
    "navigation": {"ios": "Navigation", "android": "Maps & Navigation", "ios_id": 6010},
    "news": {"ios": "News", "android": "News & Magazines", "ios_id": 6009},
    "photo": {"ios": "Photo & Video", "android": "Photography", "ios_id": 6008},
    "productivity": {"ios": "Productivity", "android": "Productivity", "ios_id": 6007},
    "shopping": {"ios": "Shopping", "android": "Shopping", "ios_id": 6024},
    "social": {"ios": "Social Networking", "android": "Social", "ios_id": 6005},
    "sports": {"ios": "Sports", "android": "Sports", "ios_id": 6004},
    "travel": {"ios": "Travel", "android": "Travel & Local", "ios_id": 6003},
    "utilities": {"ios": "Utilities", "android": "Tools", "ios_id": 6002},
    "weather": {"ios": "Weather", "android": "Weather", "ios_id": 6001},
}

# ---------------------------------------------------------------------------
# Feature-to-keyword expansion mapping
# ---------------------------------------------------------------------------

FEATURE_KEYWORDS = {
    "offline": ["offline mode", "no internet", "works offline", "offline access", "local storage"],
    "sync": ["cloud sync", "data sync", "real-time sync", "multi-device", "cross-device"],
    "biometric": ["face id", "touch id", "fingerprint", "biometric login", "secure login"],
    "push": ["push notifications", "alerts", "reminders", "real-time updates"],
    "dark": ["dark mode", "dark theme", "night mode", "appearance"],
    "widget": ["home screen widget", "widgets", "quick access"],
    "ai": ["ai powered", "smart", "intelligent", "machine learning", "ai assistant"],
    "chat": ["messaging", "chat", "instant messaging", "real-time chat", "conversations"],
    "payment": ["in-app purchase", "payments", "subscription", "checkout", "billing"],
    "social": ["social sharing", "community", "profiles", "social network", "friends"],
    "tracking": ["tracking", "analytics", "progress", "statistics", "monitoring"],
    "workout": ["exercise", "fitness", "training", "workout plans", "gym"],
    "map": ["maps", "location", "gps", "navigation", "nearby"],
    "camera": ["camera", "photo", "scanner", "augmented reality", "ar"],
    "voice": ["voice control", "speech", "voice assistant", "dictation"],
    "calendar": ["calendar", "scheduling", "events", "appointments", "planner"],
    "notes": ["notes", "notebook", "journaling", "writing", "editor"],
    "search": ["search", "discover", "explore", "find", "browse"],
    "share": ["sharing", "export", "collaborate", "send", "invite"],
    "video": ["video", "streaming", "recording", "playback", "live"],
    "security": ["encryption", "secure", "privacy", "protected", "vault"],
    "accessibility": ["accessibility", "voiceover", "talkback", "inclusive", "a11y"],
    "multilingual": ["multilingual", "localization", "translation", "multi-language"],
}

# Category-specific keyword pools
CATEGORY_KEYWORDS = {
    "productivity": ["productivity", "organizer", "planner", "task", "todo", "notes", "workflow", "efficiency", "time management", "calendar"],
    "health": ["fitness", "health", "workout", "exercise", "training", "wellness", "nutrition", "tracker", "gym", "lifestyle"],
    "social": ["social", "connect", "chat", "messaging", "community", "friends", "network", "share", "post", "stories"],
    "finance": ["finance", "money", "budget", "expense", "banking", "investment", "savings", "wallet", "payment", "tracking"],
    "education": ["education", "learning", "courses", "study", "knowledge", "tutorial", "skills", "training", "quiz", "classroom"],
    "entertainment": ["entertainment", "fun", "media", "streaming", "video", "content", "watch", "discover", "explore"],
    "shopping": ["shopping", "deals", "store", "buy", "sale", "marketplace", "ecommerce", "order", "delivery"],
    "travel": ["travel", "trip", "booking", "hotel", "flight", "vacation", "explore", "guide", "map"],
    "food": ["food", "recipe", "restaurant", "delivery", "cooking", "menu", "dining", "order", "meals"],
    "games": ["game", "play", "fun", "adventure", "puzzle", "strategy", "arcade", "action", "multiplayer"],
    "business": ["business", "enterprise", "team", "collaboration", "project", "management", "CRM", "workflow"],
    "utilities": ["utility", "tool", "converter", "calculator", "scanner", "cleaner", "manager", "helper"],
    "photo": ["photo", "camera", "editor", "filter", "video", "selfie", "collage", "retouch", "gallery"],
    "music": ["music", "player", "playlist", "audio", "radio", "podcast", "streaming", "songs"],
    "news": ["news", "headlines", "breaking", "articles", "journalism", "updates", "magazine"],
    "sports": ["sports", "scores", "live", "stats", "team", "match", "league", "fantasy"],
    "navigation": ["navigation", "maps", "directions", "GPS", "routes", "traffic", "driving"],
    "weather": ["weather", "forecast", "radar", "temperature", "alerts", "climate", "storm"],
    "lifestyle": ["lifestyle", "daily", "habits", "routine", "personal", "home", "style", "fashion"],
}

# ---------------------------------------------------------------------------
# Privacy label data types by feature
# ---------------------------------------------------------------------------

PRIVACY_DATA_TYPES = {
    "biometric": {
        "data_types": ["Biometric Data"],
        "purpose": "App Functionality",
        "linked_to_identity": True,
    },
    "tracking": {
        "data_types": ["Usage Data", "Analytics"],
        "purpose": "Analytics",
        "linked_to_identity": False,
    },
    "social": {
        "data_types": ["Contact Info", "User Content", "Identifiers"],
        "purpose": "App Functionality",
        "linked_to_identity": True,
    },
    "payment": {
        "data_types": ["Financial Info", "Purchase History"],
        "purpose": "App Functionality",
        "linked_to_identity": True,
    },
    "push": {
        "data_types": ["Device ID", "Identifiers"],
        "purpose": "App Functionality",
        "linked_to_identity": False,
    },
    "map": {
        "data_types": ["Precise Location", "Coarse Location"],
        "purpose": "App Functionality",
        "linked_to_identity": True,
    },
    "camera": {
        "data_types": ["Photos or Videos"],
        "purpose": "App Functionality",
        "linked_to_identity": False,
    },
    "chat": {
        "data_types": ["User Content", "Contact Info", "Identifiers"],
        "purpose": "App Functionality",
        "linked_to_identity": True,
    },
    "workout": {
        "data_types": ["Health & Fitness Data", "Usage Data"],
        "purpose": "App Functionality",
        "linked_to_identity": True,
    },
    "ai": {
        "data_types": ["Usage Data", "User Content"],
        "purpose": "App Functionality, Analytics",
        "linked_to_identity": False,
    },
    "voice": {
        "data_types": ["Audio Data"],
        "purpose": "App Functionality",
        "linked_to_identity": False,
    },
    "search": {
        "data_types": ["Search History"],
        "purpose": "App Functionality",
        "linked_to_identity": False,
    },
    "video": {
        "data_types": ["Photos or Videos", "Usage Data"],
        "purpose": "App Functionality",
        "linked_to_identity": False,
    },
    "calendar": {
        "data_types": ["Calendar Events"],
        "purpose": "App Functionality",
        "linked_to_identity": True,
    },
    "notes": {
        "data_types": ["User Content"],
        "purpose": "App Functionality",
        "linked_to_identity": False,
    },
}

# ---------------------------------------------------------------------------
# Age rating guidance by content flag
# ---------------------------------------------------------------------------

AGE_RATING_FLAGS = {
    "social": {
        "flag": "Unrestricted Web Access / User-Generated Content",
        "ios_rating": "12+",
        "android_rating": "Teen",
        "notes": "Social features with UGC typically require 12+ (iOS) or Teen (Android). Implement content moderation.",
    },
    "chat": {
        "flag": "Unrestricted Web Access / User-Generated Content",
        "ios_rating": "12+",
        "android_rating": "Teen",
        "notes": "Real-time messaging requires higher age ratings due to UGC exposure.",
    },
    "payment": {
        "flag": "In-App Purchases",
        "ios_rating": "4+",
        "android_rating": "Everyone",
        "notes": "Must disclose in-app purchases. Subscriptions require clear pricing display.",
    },
    "games": {
        "flag": "Simulated Gambling / Frequent Intense Content",
        "ios_rating": "12+",
        "android_rating": "Teen",
        "notes": "Rating depends on game content. Simulated gambling requires 17+ on iOS.",
    },
    "health": {
        "flag": "Medical / Health Information",
        "ios_rating": "4+",
        "android_rating": "Everyone",
        "notes": "Health apps should include medical disclaimer. HealthKit integration has specific review requirements.",
    },
    "camera": {
        "flag": "Camera / Microphone Access",
        "ios_rating": "4+",
        "android_rating": "Everyone",
        "notes": "Camera access alone does not raise rating. Combined with sharing to social may increase it.",
    },
    "ai": {
        "flag": "AI-Generated Content",
        "ios_rating": "12+",
        "android_rating": "Teen",
        "notes": "AI content generation may produce unexpected outputs. Consider content filtering and moderation.",
    },
}

IOS_RATING_ORDER = ["4+", "9+", "12+", "17+"]
ANDROID_RATING_ORDER = ["Everyone", "Everyone 10+", "Teen", "Mature 17+"]

# ---------------------------------------------------------------------------
# Screenshot specifications
# ---------------------------------------------------------------------------

IOS_SCREENSHOT_SPECS = [
    {"device": "iPhone 6.7\"", "display": "iPhone 15 Pro Max / 16 Pro Max", "resolution": "1290x2796", "required": True},
    {"device": "iPhone 6.5\"", "display": "iPhone 14 Plus / 15 Plus", "resolution": "1284x2778", "required": True},
    {"device": "iPhone 5.5\"", "display": "iPhone 8 Plus (legacy)", "resolution": "1242x2208", "required": False},
    {"device": "iPad 12.9\"", "display": "iPad Pro 12.9\" (6th gen)", "resolution": "2048x2732", "required": False},
]

ANDROID_SCREENSHOT_SPECS = [
    {"type": "Phone", "recommended_resolution": "1080x1920", "min_count": 2, "max_count": 8},
    {"type": "7-inch Tablet", "recommended_resolution": "1200x1920", "min_count": 0, "max_count": 8},
    {"type": "10-inch Tablet", "recommended_resolution": "1600x2560", "min_count": 0, "max_count": 8},
]

# ---------------------------------------------------------------------------
# Title generation
# ---------------------------------------------------------------------------

CATEGORY_TAGLINES = {
    "productivity": "Get More Done",
    "health": "Your Health Companion",
    "finance": "Manage Your Money",
    "education": "Learn Anywhere",
    "social": "Connect & Share",
    "business": "Work Smarter",
    "shopping": "Shop Smarter",
    "travel": "Explore the World",
    "entertainment": "Fun Awaits",
    "food": "Discover Flavors",
    "music": "Your Music, Your Way",
    "news": "Stay Informed",
    "games": "Play Now",
    "photo": "Capture Moments",
    "utilities": "Simplify Your Life",
    "weather": "Always Prepared",
    "navigation": "Find Your Way",
    "sports": "Game On",
    "lifestyle": "Live Better",
}

FEATURE_PHRASES = {
    "offline": "Works Offline",
    "sync": "Syncs Everywhere",
    "biometric": "Secure Access",
    "push": "Smart Alerts",
    "dark": "Dark Mode",
    "ai": "AI-Powered",
    "chat": "Real-Time Chat",
    "payment": "Easy Payments",
    "social": "Social Features",
    "tracking": "Smart Tracking",
    "workout": "Workout Tracking",
    "map": "Location Services",
    "camera": "Camera Ready",
    "voice": "Voice Enabled",
    "calendar": "Smart Scheduling",
    "notes": "Note Taking",
    "search": "Quick Search",
    "share": "Easy Sharing",
    "video": "Video Support",
    "security": "Bank-Level Security",
    "widget": "Home Screen Widgets",
    "accessibility": "Fully Accessible",
    "multilingual": "Multi-Language",
}


def generate_titles(app_name: str, category: str, features: list) -> dict:
    """Generate title variants for store listings."""
    clean_name = app_name.strip()
    tagline = CATEGORY_TAGLINES.get(category, "Simplify Your Life")

    feature_phrases = []
    for f in features[:3]:
        f_lower = f.lower().strip()
        if f_lower in FEATURE_PHRASES:
            feature_phrases.append(FEATURE_PHRASES[f_lower])

    subtitle = " | ".join(feature_phrases[:3]) if feature_phrases else tagline

    return {
        "primary_title": clean_name,
        "title_with_tagline": f"{clean_name} - {tagline}",
        "title_with_features": f"{clean_name}: {subtitle}",
        "ios_subtitle": tagline[:30],
        "play_store_short_description": _truncate(
            f"{clean_name} helps you {tagline.lower()}. {subtitle}.", 80
        ),
        "guidelines": {
            "ios_title_max": "30 characters",
            "ios_subtitle_max": "30 characters",
            "play_store_title_max": "30 characters",
            "play_store_short_desc_max": "80 characters",
        },
    }


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


# ---------------------------------------------------------------------------
# Keyword generation
# ---------------------------------------------------------------------------

def generate_keywords(app_name: str, category: str, features: list) -> dict:
    """Generate keyword suggestions from features and category."""
    keywords = set()

    # Add app name words (skip common words)
    stop_words = {"the", "a", "an", "and", "or", "for", "to", "in", "of", "my", "app"}
    name_words = re.split(r"[\s\-_]+", app_name.lower())
    for word in name_words:
        if word not in stop_words and len(word) > 1:
            keywords.add(word)

    # Add category-level keywords
    keywords.add(category)
    for kw in CATEGORY_KEYWORDS.get(category, []):
        keywords.add(kw.lower())

    # Expand features into keywords
    primary_keywords = []
    secondary_keywords = []
    for feature in features:
        f_lower = feature.lower().strip()
        keywords.add(f_lower)
        if f_lower in FEATURE_KEYWORDS:
            expanded = FEATURE_KEYWORDS[f_lower]
            primary_keywords.extend(expanded[:2])
            secondary_keywords.extend(expanded[2:])
            for kw in expanded:
                keywords.add(kw)

    sorted_keywords = sorted(keywords, key=lambda x: (len(x), x))

    # Build iOS keyword field (100 chars max, comma-separated)
    ios_kw_list = []
    for kw in sorted_keywords:
        candidate = ",".join(ios_kw_list + [kw]) if ios_kw_list else kw
        if len(candidate) <= 100:
            ios_kw_list.append(kw)
        else:
            break
    ios_keyword_string = ",".join(ios_kw_list)

    return {
        "all_keywords": sorted_keywords,
        "primary_keywords": primary_keywords[:10],
        "secondary_keywords": secondary_keywords[:10],
        "ios_keyword_field": ios_keyword_string,
        "ios_keyword_field_length": len(ios_keyword_string),
        "ios_keyword_max": 100,
        "keyword_count": len(sorted_keywords),
        "tips": [
            "Avoid duplicating words already in your app title (Apple Search indexes title words automatically).",
            "Use singular forms - Apple indexes both singular and plural.",
            "Avoid trademarked terms, competitor names, and generic category names.",
            "Separate iOS keywords with commas, no spaces.",
            "Google Play extracts keywords from your description - embed them naturally.",
        ],
    }


# ---------------------------------------------------------------------------
# Category recommendations
# ---------------------------------------------------------------------------

def recommend_categories(category: str, features: list) -> dict:
    """Recommend primary and secondary store categories."""
    primary = APP_STORE_CATEGORIES.get(category)
    if not primary:
        primary = {"ios": "Utilities", "android": "Tools", "ios_id": 6002}

    feature_to_category = {
        "social": "social", "chat": "social", "payment": "finance",
        "workout": "health", "tracking": "health", "map": "navigation",
        "calendar": "productivity", "notes": "productivity", "camera": "photo",
        "video": "photo", "music": "music", "games": "games",
        "news": "news", "shopping": "shopping", "ai": "utilities",
    }

    secondary = None
    for feature in features:
        f_lower = feature.lower().strip()
        if f_lower in feature_to_category:
            sec_key = feature_to_category[f_lower]
            if sec_key != category:
                secondary = APP_STORE_CATEGORIES.get(sec_key)
                break

    result = {
        "primary_category": {
            "ios": primary["ios"],
            "android": primary["android"],
        },
        "guidelines": {
            "ios": "Select one primary and one secondary category. Choose the most relevant.",
            "android": "Select one primary category. Google may display your app in related categories.",
        },
    }

    if secondary:
        result["secondary_category"] = {
            "ios": secondary["ios"],
            "android": secondary["android"],
        }

    return result


# ---------------------------------------------------------------------------
# Privacy labels / Data Safety
# ---------------------------------------------------------------------------

def generate_privacy_labels(features: list) -> dict:
    """Generate privacy label and Data Safety section guidance."""
    collected_data = []
    seen_types = set()

    for feature in features:
        f_lower = feature.lower().strip()
        if f_lower in PRIVACY_DATA_TYPES:
            entry = PRIVACY_DATA_TYPES[f_lower]
            for dt in entry["data_types"]:
                if dt not in seen_types:
                    seen_types.add(dt)
                    collected_data.append({
                        "data_type": dt,
                        "purpose": entry["purpose"],
                        "linked_to_identity": entry["linked_to_identity"],
                        "triggered_by_feature": f_lower,
                    })

    # Baseline data types (every app collects these)
    baseline = [
        {"data_type": "Crash Data", "purpose": "App Functionality", "linked_to_identity": False, "triggered_by_feature": "baseline"},
        {"data_type": "Performance Data", "purpose": "Analytics", "linked_to_identity": False, "triggered_by_feature": "baseline"},
        {"data_type": "Device ID", "purpose": "Analytics", "linked_to_identity": False, "triggered_by_feature": "baseline"},
    ]
    for bt in baseline:
        if bt["data_type"] not in seen_types:
            seen_types.add(bt["data_type"])
            collected_data.append(bt)

    return {
        "ios_privacy_labels": {
            "description": "Apple App Privacy labels required on App Store Connect.",
            "data_collected": collected_data,
            "data_linked_to_identity": [d for d in collected_data if d["linked_to_identity"]],
            "data_not_linked": [d for d in collected_data if not d["linked_to_identity"]],
            "tracking_declaration": (
                "If you use any third-party SDKs for advertising attribution "
                "(Facebook SDK, Adjust, AppsFlyer), you must declare tracking "
                "and request ATT permission."
            ),
        },
        "android_data_safety": {
            "description": "Google Play Data Safety section required for all apps.",
            "data_collected": collected_data,
            "data_shared_with_third_parties": [],
            "security_practices": {
                "data_encrypted_in_transit": True,
                "data_deletion_available": "Provide a mechanism for users to request data deletion.",
            },
        },
        "recommendations": [
            "Review all third-party SDKs for data collection (analytics, crash reporting, ad networks).",
            "Document data retention periods for each data type.",
            "Provide a publicly accessible privacy policy URL.",
            "For iOS: implement App Tracking Transparency (ATT) if any tracking occurs.",
            "For Android: complete the Data Safety form in Google Play Console.",
            "Keep privacy labels updated when adding new features or SDKs.",
        ],
    }


# ---------------------------------------------------------------------------
# Age rating guidance
# ---------------------------------------------------------------------------

def _higher_rating(order, current, new_val):
    """Return the higher of two ratings based on an ordered list."""
    # Strip everything after the first space for comparison
    curr_key = current.split(" ")[0]
    new_key = new_val.split(" ")[0]
    try:
        curr_idx = next(i for i, r in enumerate(order) if r.startswith(curr_key))
    except StopIteration:
        return current
    try:
        new_idx = next(i for i, r in enumerate(order) if r.startswith(new_key))
    except StopIteration:
        return current
    return order[new_idx] if new_idx > curr_idx else order[curr_idx]


def generate_age_rating(category: str, features: list) -> dict:
    """Generate age rating guidance based on content and features."""
    flags = []
    max_ios = "4+"
    max_android = "Everyone"

    # Check category-level flags
    if category in AGE_RATING_FLAGS:
        entry = AGE_RATING_FLAGS[category]
        flags.append(entry)
        max_ios = _higher_rating(IOS_RATING_ORDER, max_ios, entry["ios_rating"])
        max_android = _higher_rating(ANDROID_RATING_ORDER, max_android, entry["android_rating"])

    # Check feature-level flags
    for feature in features:
        f_lower = feature.lower().strip()
        if f_lower in AGE_RATING_FLAGS:
            entry = AGE_RATING_FLAGS[f_lower]
            if entry not in flags:
                flags.append(entry)
            max_ios = _higher_rating(IOS_RATING_ORDER, max_ios, entry["ios_rating"])
            max_android = _higher_rating(ANDROID_RATING_ORDER, max_android, entry["android_rating"])

    return {
        "recommended_rating": {
            "ios": max_ios,
            "android": max_android,
        },
        "content_flags": flags,
        "questionnaire_guidance": {
            "ios": "Complete the Age Rating questionnaire in App Store Connect. Answer honestly - Apple reviews catch discrepancies.",
            "android": "Complete the IARC rating questionnaire in Google Play Console. Ratings are calculated automatically.",
        },
        "common_mistakes": [
            "Under-rating apps with user-generated content (UGC requires 12+ on iOS).",
            "Forgetting to disclose in-app purchases in the rating questionnaire.",
            "Not updating ratings when adding new features (e.g., adding chat to a 4+ app).",
            "Apps with web views showing unrestricted content need higher ratings.",
        ],
    }


# ---------------------------------------------------------------------------
# Description generation
# ---------------------------------------------------------------------------

def generate_description(app_name: str, category: str, description: str, features: list) -> dict:
    """Generate short and full descriptions for store listings."""
    cat_info = APP_STORE_CATEGORIES.get(category, {})
    cat_label = cat_info.get("ios", category.replace("-", " ").title())

    feature_bullets = "\n".join(f"- {f.strip().title()}" for f in features[:6]) if features else (
        "- Intuitive and beautiful interface\n"
        "- Fast and reliable performance\n"
        "- Privacy-first approach"
    )

    user_desc = description if description else f"a powerful {cat_label.lower()} tool"

    short_desc = _truncate(
        f"{app_name} - {user_desc.capitalize()}. Simple, powerful, designed for you.", 80
    )

    full_desc = textwrap.dedent(f"""\
        {app_name} - The {cat_label} App You Have Been Waiting For

        {app_name} is {user_desc}. Whether you are a beginner or a power user, {app_name} adapts to your workflow.

        KEY FEATURES:
        {feature_bullets}

        WHY {app_name.upper()}?
        We built {app_name} because we believe {cat_label.lower()} tools should be both powerful and delightful to use. Every detail is carefully crafted to help you achieve more with less effort.

        PRIVACY & SECURITY
        Your data is yours. {app_name} uses industry-standard encryption and never sells your personal information.

        GET STARTED
        Download {app_name} today and experience the difference. We improve based on user feedback - your input shapes the future of {app_name}.

        Questions or feedback? Contact us at support@example.com
    """)

    return {
        "short_description": short_desc,
        "full_description": full_desc[:4000],
        "promotional_text": _truncate(
            f"Discover {app_name} - the smarter way to handle {cat_label.lower()}!", 170
        ),
        "whats_new_template": (
            f"What's New in {app_name}:\n"
            "- Performance improvements and bug fixes\n"
            "- New features based on your feedback\n"
            "- Improved accessibility support"
        ),
    }


# ---------------------------------------------------------------------------
# Full metadata assembly
# ---------------------------------------------------------------------------

def generate_metadata(app_name: str, category: str, description: str, features: list) -> dict:
    """Generate complete store metadata."""
    return {
        "app_name": app_name,
        "input_category": category,
        "input_description": description,
        "input_features": features,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "titles": generate_titles(app_name, category, features),
        "keywords": generate_keywords(app_name, category, features),
        "categories": recommend_categories(category, features),
        "descriptions": generate_description(app_name, category, description, features),
        "privacy_labels": generate_privacy_labels(features),
        "age_rating": generate_age_rating(category, features),
        "screenshot_specs": {
            "ios": IOS_SCREENSHOT_SPECS,
            "android": ANDROID_SCREENSHOT_SPECS,
            "design_guidelines": {
                "recommended_count": 6,
                "order": [
                    "Hero / value proposition",
                    "Core feature #1",
                    "Core feature #2",
                    "Social proof or stats",
                    "Secondary feature",
                    "Call to action",
                ],
                "use_device_frames": True,
                "include_captions": True,
            },
        },
        "submission_checklist": {
            "ios": [
                "App icon: 1024x1024 PNG (no alpha, no rounded corners)",
                "Screenshots: 6.7\" (1290x2796) and 6.5\" (1284x2778) required",
                "iPad screenshots if universal: 12.9\" (2048x2732)",
                "App preview video (optional): 15-30 seconds, .mov or .mp4",
                "Description: up to 4000 characters",
                "Promotional text: up to 170 characters (can update without new build)",
                "Keywords: up to 100 characters, comma-separated",
                "Support URL: required",
                "Privacy Policy URL: required",
                "App Review notes: login credentials for review team if applicable",
                "Copyright info",
                "Build uploaded via Xcode or Transporter",
            ],
            "android": [
                "App icon: 512x512 PNG (32-bit with alpha)",
                "Feature graphic: 1024x500 PNG or JPG",
                "Screenshots: minimum 2 phone, recommended 8, JPEG or PNG",
                "Short description: up to 80 characters",
                "Full description: up to 4000 characters",
                "Privacy Policy URL: required",
                "Data Safety section: required",
                "IARC content rating questionnaire: required",
                "Target audience and content declaration: required",
                "AAB (Android App Bundle) uploaded via Play Console",
            ],
        },
    }


# ---------------------------------------------------------------------------
# Human-readable output
# ---------------------------------------------------------------------------

def print_human_report(metadata: dict):
    """Print metadata in human-readable format."""
    print("=" * 70)
    print("  APP STORE METADATA GENERATOR")
    print("=" * 70)
    print(f"  App Name:     {metadata['app_name']}")
    print(f"  Category:     {metadata['input_category']}")
    print(f"  Features:     {', '.join(metadata['input_features'])}")
    if metadata["input_description"]:
        print(f"  Description:  {metadata['input_description']}")
    print(f"  Generated:    {metadata['generated_at']}")
    print()

    # Titles
    titles = metadata["titles"]
    print("-" * 70)
    print("  TITLE VARIANTS")
    print("-" * 70)
    print(f"  Primary:          {titles['primary_title']}")
    print(f"  With Tagline:     {titles['title_with_tagline']}")
    print(f"  With Features:    {titles['title_with_features']}")
    print(f"  iOS Subtitle:     {titles['ios_subtitle']}")
    print(f"  Play Short Desc:  {titles['play_store_short_description']}")
    print()

    # Keywords
    kw = metadata["keywords"]
    print("-" * 70)
    print("  KEYWORDS")
    print("-" * 70)
    print(f"  Total Keywords:   {kw['keyword_count']}")
    print(f"  iOS Field ({kw['ios_keyword_field_length']}/100 chars):")
    print(f"    {kw['ios_keyword_field']}")
    print()
    if kw["primary_keywords"]:
        print(f"  Primary:   {', '.join(kw['primary_keywords'][:5])}")
    if kw["secondary_keywords"]:
        print(f"  Secondary: {', '.join(kw['secondary_keywords'][:5])}")
    print()
    print("  Tips:")
    for tip in kw["tips"]:
        print(f"    - {tip}")
    print()

    # Categories
    cats = metadata["categories"]
    print("-" * 70)
    print("  STORE CATEGORIES")
    print("-" * 70)
    print(f"  Primary (iOS):     {cats['primary_category']['ios']}")
    print(f"  Primary (Android): {cats['primary_category']['android']}")
    if "secondary_category" in cats:
        print(f"  Secondary (iOS):     {cats['secondary_category']['ios']}")
        print(f"  Secondary (Android): {cats['secondary_category']['android']}")
    print()

    # Privacy
    privacy = metadata["privacy_labels"]
    ios_priv = privacy["ios_privacy_labels"]
    print("-" * 70)
    print("  PRIVACY LABELS / DATA SAFETY")
    print("-" * 70)
    print(f"  Data types collected ({len(ios_priv['data_collected'])}):")
    for dt in ios_priv["data_collected"]:
        linked = " (linked to identity)" if dt["linked_to_identity"] else ""
        print(f"    - {dt['data_type']}: {dt['purpose']}{linked}")
    print()
    print("  Recommendations:")
    for rec in privacy["recommendations"]:
        print(f"    - {rec}")
    print()

    # Age Rating
    ar = metadata["age_rating"]
    print("-" * 70)
    print("  AGE RATING GUIDANCE")
    print("-" * 70)
    print(f"  Recommended iOS Rating:     {ar['recommended_rating']['ios']}")
    print(f"  Recommended Android Rating: {ar['recommended_rating']['android']}")
    if ar["content_flags"]:
        print()
        print("  Content Flags:")
        for flag in ar["content_flags"]:
            print(f"    - {flag['flag']}")
            print(f"      {flag['notes']}")
    print()

    # Submission Checklist
    print("-" * 70)
    print("  SUBMISSION CHECKLIST")
    print("-" * 70)
    for store, items in metadata["submission_checklist"].items():
        label = "App Store (iOS)" if store == "ios" else "Google Play (Android)"
        print(f"\n  {label}:")
        for item in items:
            print(f"    [ ] {item}")
    print()
    print("=" * 70)
    print("  Use --json for machine-readable output")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="store_metadata_generator",
        description="Generate App Store / Play Store metadata for a mobile app.",
        epilog=(
            'Example: python store_metadata_generator.py '
            '--app-name "My App" --category productivity '
            '--features "offline,sync,biometric" --json'
        ),
    )
    parser.add_argument(
        "--app-name",
        required=True,
        help="The app name",
    )
    parser.add_argument(
        "--category",
        required=True,
        choices=sorted(APP_STORE_CATEGORIES.keys()),
        help="Primary app category",
    )
    parser.add_argument(
        "--description",
        default="",
        help='Short app description (optional, e.g., "Track your daily workouts")',
    )
    parser.add_argument(
        "--features",
        required=True,
        help='Comma-separated list of features (e.g., "offline,sync,biometric")',
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output results as JSON",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    app_name = args.app_name.strip()
    category = args.category.strip().lower()
    description = args.description.strip()
    features = [f.strip() for f in args.features.split(",") if f.strip()]

    if not app_name:
        sys.stderr.write("Error: --app-name cannot be empty.\n")
        sys.exit(1)

    if not features:
        sys.stderr.write("Error: --features must contain at least one feature.\n")
        sys.exit(1)

    metadata = generate_metadata(app_name, category, description, features)

    if args.json:
        print(json.dumps(metadata, indent=2))
    else:
        print_human_report(metadata)


if __name__ == "__main__":
    main()
