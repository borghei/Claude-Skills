#!/usr/bin/env python3
"""
Thumbnail Analyzer

Analyzes thumbnail text, composition patterns, and their correlation with
video performance (CTR, views). Identifies which thumbnail characteristics
drive higher click-through rates.

Expected CSV columns: video_id, title, views, ctr_pct, has_face, has_text,
  text_words, colors_dominant, emotion

Usage:
    python thumbnail_analyzer.py thumbnails.csv
    python thumbnail_analyzer.py thumbnails.csv --format json
    python thumbnail_analyzer.py thumbnails.csv --min-views 1000
    python thumbnail_analyzer.py thumbnails.csv --top 10
"""

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


def load_thumbnail_data(filepath: str) -> List[Dict[str, Any]]:
    """Load thumbnail data from CSV."""
    data = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                entry = {
                    "video_id": row.get("video_id", "").strip(),
                    "title": row.get("title", "").strip(),
                    "views": int(row.get("views", 0)),
                    "ctr_pct": float(row.get("ctr_pct", 0)),
                    "has_face": row.get("has_face", "").strip().lower() in ("yes", "true", "1"),
                    "has_text": row.get("has_text", "").strip().lower() in ("yes", "true", "1"),
                    "text_words": int(row.get("text_words", 0)),
                    "colors_dominant": row.get("colors_dominant", "").strip().lower(),
                    "emotion": row.get("emotion", "neutral").strip().lower(),
                }
                data.append(entry)
            except (ValueError, KeyError):
                continue
    return data


def calculate_stats(values: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a list of values."""
    if not values:
        return {"count": 0, "mean": 0, "median": 0, "stdev": 0, "min": 0, "max": 0}
    return {
        "count": len(values),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "stdev": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        "min": round(min(values), 2),
        "max": round(max(values), 2),
    }


def analyze_by_attribute(data: List[Dict], attribute: str, value_key: str = "ctr_pct") -> Dict[str, Any]:
    """Analyze performance grouped by a boolean or categorical attribute."""
    groups = defaultdict(list)
    for entry in data:
        val = entry.get(attribute)
        if isinstance(val, bool):
            key = "yes" if val else "no"
        else:
            key = str(val) if val else "unknown"
        groups[key].append(entry[value_key])

    result = {}
    for key, values in sorted(groups.items()):
        result[key] = calculate_stats(values)
    return result


def analyze_text_word_count(data: List[Dict]) -> Dict[str, Any]:
    """Analyze CTR by number of text words on thumbnail."""
    buckets = {"0 words": [], "1-3 words": [], "4-5 words": [], "6+ words": []}

    for entry in data:
        wc = entry["text_words"]
        ctr = entry["ctr_pct"]
        if wc == 0:
            buckets["0 words"].append(ctr)
        elif wc <= 3:
            buckets["1-3 words"].append(ctr)
        elif wc <= 5:
            buckets["4-5 words"].append(ctr)
        else:
            buckets["6+ words"].append(ctr)

    return {k: calculate_stats(v) for k, v in buckets.items()}


def analyze_color_performance(data: List[Dict]) -> Dict[str, Any]:
    """Analyze CTR by dominant thumbnail colors."""
    color_ctrs = defaultdict(list)
    for entry in data:
        colors = entry["colors_dominant"]
        if not colors:
            continue
        # Handle multi-color entries like "red-yellow"
        for color in colors.replace(",", "-").split("-"):
            color = color.strip()
            if color:
                color_ctrs[color].append(entry["ctr_pct"])

    return {color: calculate_stats(ctrs) for color, ctrs in sorted(color_ctrs.items())}


def find_top_performers(data: List[Dict], n: int = 10) -> List[Dict]:
    """Find top N performing thumbnails by CTR."""
    sorted_data = sorted(data, key=lambda x: x["ctr_pct"], reverse=True)
    return sorted_data[:n]


def find_bottom_performers(data: List[Dict], n: int = 10) -> List[Dict]:
    """Find bottom N performing thumbnails by CTR."""
    sorted_data = sorted(data, key=lambda x: x["ctr_pct"])
    return sorted_data[:n]


def generate_recommendations(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate actionable recommendations from analysis."""
    recs = []

    # Face analysis
    face_data = analysis.get("face_analysis", {})
    if "yes" in face_data and "no" in face_data:
        face_ctr = face_data["yes"]["mean"]
        no_face_ctr = face_data["no"]["mean"]
        if face_ctr > no_face_ctr * 1.1:
            lift = ((face_ctr - no_face_ctr) / no_face_ctr * 100)
            recs.append({
                "category": "Faces",
                "recommendation": f"Include faces in thumbnails - {lift:.0f}% higher CTR with faces "
                                  f"({face_ctr:.1f}% vs {no_face_ctr:.1f}%)",
                "priority": "high",
            })
        elif no_face_ctr > face_ctr * 1.1:
            recs.append({
                "category": "Faces",
                "recommendation": "Thumbnails without faces perform better for your content - "
                                  "consider graphic/text-focused designs",
                "priority": "medium",
            })

    # Text analysis
    text_data = analysis.get("text_analysis", {})
    if "yes" in text_data and "no" in text_data:
        text_ctr = text_data["yes"]["mean"]
        no_text_ctr = text_data["no"]["mean"]
        if text_ctr > no_text_ctr * 1.05:
            recs.append({
                "category": "Text",
                "recommendation": f"Text overlays improve CTR ({text_ctr:.1f}% vs {no_text_ctr:.1f}%)",
                "priority": "high",
            })

    # Word count analysis
    wc_data = analysis.get("word_count_analysis", {})
    if wc_data:
        best_bucket = max(
            [(k, v["mean"]) for k, v in wc_data.items() if v["count"] >= 3],
            key=lambda x: x[1],
            default=(None, 0),
        )
        if best_bucket[0]:
            recs.append({
                "category": "Text Length",
                "recommendation": f"Optimal text length: {best_bucket[0]} (avg CTR: {best_bucket[1]:.1f}%)",
                "priority": "medium",
            })

    # Emotion analysis
    emotion_data = analysis.get("emotion_analysis", {})
    if emotion_data:
        valid_emotions = [(k, v["mean"]) for k, v in emotion_data.items() if v["count"] >= 3]
        if valid_emotions:
            best_emotion = max(valid_emotions, key=lambda x: x[1])
            if best_emotion[1] > 0:
                recs.append({
                    "category": "Emotion",
                    "recommendation": f"Best performing emotion: '{best_emotion[0]}' "
                                      f"(avg CTR: {best_emotion[1]:.1f}%)",
                    "priority": "medium",
                })

    # Color analysis
    color_data = analysis.get("color_analysis", {})
    if color_data:
        valid_colors = [(k, v["mean"]) for k, v in color_data.items() if v["count"] >= 3]
        if valid_colors:
            top_colors = sorted(valid_colors, key=lambda x: x[1], reverse=True)[:3]
            color_list = ", ".join(f"{c[0]} ({c[1]:.1f}%)" for c in top_colors)
            recs.append({
                "category": "Colors",
                "recommendation": f"Top performing colors: {color_list}",
                "priority": "low",
            })

    return recs


def print_human(analysis: Dict[str, Any], top: List[Dict], bottom: List[Dict],
                recs: List[Dict]) -> None:
    """Print analysis in human-readable format."""
    print("=" * 70)
    print("  Thumbnail Performance Analysis")
    print("=" * 70)

    overall = analysis["overall_stats"]
    print(f"\n  Total Thumbnails Analyzed: {overall['count']}")
    print(f"  Average CTR: {overall['mean']:.2f}%")
    print(f"  Median CTR:  {overall['median']:.2f}%")
    print(f"  CTR Range:   {overall['min']:.2f}% - {overall['max']:.2f}%")

    # Face analysis
    print(f"\n  --- Face Presence ---")
    for key, stats in analysis.get("face_analysis", {}).items():
        print(f"  {key:<6}: avg CTR {stats['mean']:.2f}% (n={stats['count']})")

    # Text analysis
    print(f"\n  --- Text Overlay ---")
    for key, stats in analysis.get("text_analysis", {}).items():
        print(f"  {key:<6}: avg CTR {stats['mean']:.2f}% (n={stats['count']})")

    # Word count
    print(f"\n  --- Text Word Count ---")
    for bucket, stats in analysis.get("word_count_analysis", {}).items():
        if stats["count"] > 0:
            bar = "#" * max(1, int(stats["mean"] * 2))
            print(f"  {bucket:<12}: avg CTR {stats['mean']:.2f}% (n={stats['count']})  {bar}")

    # Emotion
    print(f"\n  --- Emotion ---")
    for emotion, stats in sorted(analysis.get("emotion_analysis", {}).items(),
                                  key=lambda x: x[1]["mean"], reverse=True):
        if stats["count"] > 0:
            bar = "#" * max(1, int(stats["mean"] * 2))
            print(f"  {emotion:<12}: avg CTR {stats['mean']:.2f}% (n={stats['count']})  {bar}")

    # Colors
    print(f"\n  --- Dominant Colors ---")
    for color, stats in sorted(analysis.get("color_analysis", {}).items(),
                                key=lambda x: x[1]["mean"], reverse=True):
        if stats["count"] > 0:
            bar = "#" * max(1, int(stats["mean"] * 2))
            print(f"  {color:<12}: avg CTR {stats['mean']:.2f}% (n={stats['count']})  {bar}")

    # Top performers
    print(f"\n  --- Top Performers ---")
    for i, t in enumerate(top[:5], 1):
        face = "Face" if t["has_face"] else "No face"
        text_info = f"{t['text_words']} words" if t["has_text"] else "No text"
        print(f"  {i}. {t['title'][:35]:<35} CTR: {t['ctr_pct']:.1f}%  ({face}, {text_info})")

    # Bottom performers
    print(f"\n  --- Bottom Performers ---")
    for i, t in enumerate(bottom[:5], 1):
        face = "Face" if t["has_face"] else "No face"
        text_info = f"{t['text_words']} words" if t["has_text"] else "No text"
        print(f"  {i}. {t['title'][:35]:<35} CTR: {t['ctr_pct']:.1f}%  ({face}, {text_info})")

    # Recommendations
    if recs:
        print(f"\n  --- Recommendations ---")
        priority_order = {"high": 0, "medium": 1, "low": 2}
        for rec in sorted(recs, key=lambda r: priority_order.get(r["priority"], 9)):
            marker = {"high": "[!!!]", "medium": "[ ! ]", "low": "[   ]"}.get(rec["priority"], "[   ]")
            print(f"  {marker} {rec['category']}: {rec['recommendation']}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze thumbnail text and composition patterns for optimization"
    )
    parser.add_argument("file", help="CSV file with thumbnail data")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--min-views", type=int, default=0, help="Minimum views filter")
    parser.add_argument("--top", type=int, default=10, help="Number of top/bottom performers to show")
    args = parser.parse_args()

    data = load_thumbnail_data(args.file)
    if not data:
        print("Error: No valid thumbnail data found", file=sys.stderr)
        sys.exit(1)

    if args.min_views > 0:
        data = [d for d in data if d["views"] >= args.min_views]
        if not data:
            print(f"Error: No thumbnails with >= {args.min_views} views", file=sys.stderr)
            sys.exit(1)

    ctrs = [d["ctr_pct"] for d in data]

    analysis = {
        "overall_stats": calculate_stats(ctrs),
        "face_analysis": analyze_by_attribute(data, "has_face"),
        "text_analysis": analyze_by_attribute(data, "has_text"),
        "word_count_analysis": analyze_text_word_count(data),
        "emotion_analysis": analyze_by_attribute(data, "emotion"),
        "color_analysis": analyze_color_performance(data),
    }

    top = find_top_performers(data, args.top)
    bottom = find_bottom_performers(data, args.top)
    recs = generate_recommendations(analysis)

    if args.format == "json":
        output = {
            "analysis": analysis,
            "top_performers": top,
            "bottom_performers": bottom,
            "recommendations": recs,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_human(analysis, top, bottom, recs)


if __name__ == "__main__":
    main()
