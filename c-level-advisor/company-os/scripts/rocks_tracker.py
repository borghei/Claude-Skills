#!/usr/bin/env python3
"""
90-Day Rocks Tracker - Track quarterly rocks with binary status and accountability.

Manages company and individual rocks with on/off track status,
accountability assignments, and quarterly review preparation.
"""

import argparse
import json
import sys
from datetime import datetime


def track_rocks(data: dict) -> dict:
    """Track 90-day rocks status."""
    company_rocks = data.get("company_rocks", [])
    individual_rocks = data.get("individual_rocks", [])
    quarter = data.get("quarter", "Q1")

    results = {
        "timestamp": datetime.now().isoformat(),
        "quarter": quarter,
        "company_rocks": {"total": 0, "on_track": 0, "off_track": 0, "complete": 0, "rocks": []},
        "individual_summary": {},
        "individual_rocks": [],
        "issues": [],
        "recommendations": [],
    }

    for rock in company_rocks:
        status = rock.get("status", "on_track")
        result = {
            "description": rock.get("description", ""),
            "owner": rock.get("owner", ""),
            "status": status,
            "due_date": rock.get("due_date", ""),
            "progress_note": rock.get("progress_note", ""),
            "blocker": rock.get("blocker", ""),
        }
        results["company_rocks"]["rocks"].append(result)
        results["company_rocks"]["total"] += 1
        if status == "complete":
            results["company_rocks"]["complete"] += 1
        elif status == "on_track":
            results["company_rocks"]["on_track"] += 1
        else:
            results["company_rocks"]["off_track"] += 1
            if result["blocker"]:
                results["issues"].append({
                    "rock": result["description"][:50],
                    "owner": result["owner"],
                    "blocker": result["blocker"],
                    "type": "company_rock",
                })

    for rock in individual_rocks:
        owner = rock.get("owner", "")
        status = rock.get("status", "on_track")
        result = {
            "description": rock.get("description", ""),
            "owner": owner,
            "status": status,
            "due_date": rock.get("due_date", ""),
        }
        results["individual_rocks"].append(result)

        if owner not in results["individual_summary"]:
            results["individual_summary"][owner] = {"total": 0, "on_track": 0, "off_track": 0, "complete": 0}
        results["individual_summary"][owner]["total"] += 1
        if status == "complete":
            results["individual_summary"][owner]["complete"] += 1
        elif status == "on_track":
            results["individual_summary"][owner]["on_track"] += 1
        else:
            results["individual_summary"][owner]["off_track"] += 1

    # Recommendations
    cr = results["company_rocks"]
    if cr["total"] > 7:
        results["recommendations"].append(f"Too many company rocks ({cr['total']}). Max 7. Prioritize ruthlessly.")
    if cr["off_track"] > 0:
        results["recommendations"].append(f"{cr['off_track']} company rock(s) off track. Address in L10.")

    for owner, summary in results["individual_summary"].items():
        if summary["total"] > 7:
            results["recommendations"].append(f"{owner} has {summary['total']} rocks (max 7). Reduce or delegate.")
        if summary["off_track"] >= 2:
            results["recommendations"].append(f"{owner} has {summary['off_track']} rocks off track. Capacity issue.")

    return results


def format_text(results: dict) -> str:
    """Format as L10-ready rocks review."""
    cr = results["company_rocks"]
    lines = [
        "=" * 65,
        f"90-DAY ROCKS TRACKER - {results['quarter']}",
        "=" * 65,
        f"Company: {cr['complete']} done / {cr['on_track']} on track / {cr['off_track']} off track (of {cr['total']})",
        "",
        "COMPANY ROCKS:",
    ]

    for r in cr["rocks"]:
        icon = "[x]" if r["status"] == "complete" else "[~]" if r["status"] == "on_track" else "[!]"
        lines.append(f"  {icon} {r['description']} ({r['owner']}, due: {r['due_date']})")
        if r["blocker"]:
            lines.append(f"      Blocker: {r['blocker']}")

    lines.extend(["", "INDIVIDUAL ROCKS BY OWNER:"])
    for owner, summary in results["individual_summary"].items():
        lines.append(f"  {owner}: {summary['complete']}x / {summary['on_track']}~ / {summary['off_track']}! (of {summary['total']})")

    if results["issues"]:
        lines.extend(["", "ISSUES FOR IDS:"])
        for issue in results["issues"]:
            lines.append(f"  >> {issue['rock']}... ({issue['owner']}): {issue['blocker']}")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "=" * 65])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track 90-day rocks")
    parser.add_argument("--input", "-i", help="JSON file with rocks data")
    parser.add_argument("--quarter", default="Q1", help="Quarter label")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "quarter": args.quarter,
            "company_rocks": [
                {"description": "Hit $3M ARR", "owner": "CRO", "status": "on_track", "due_date": "2026-03-31"},
                {"description": "Launch enterprise tier", "owner": "CPO", "status": "off_track", "due_date": "2026-03-31", "blocker": "API redesign delayed by 3 weeks"},
                {"description": "Achieve SOC 2 Type I", "owner": "CISO", "status": "on_track", "due_date": "2026-03-31"},
                {"description": "Hire 5 key roles", "owner": "CHRO", "status": "off_track", "due_date": "2026-03-31", "blocker": "2 offers declined, comp bands may need refresh"},
            ],
            "individual_rocks": [
                {"description": "Close 3 enterprise deals", "owner": "CRO", "status": "on_track", "due_date": "2026-03-31"},
                {"description": "Reduce MTTR to < 4 hours", "owner": "CTO", "status": "complete", "due_date": "2026-03-31"},
                {"description": "Launch content hub", "owner": "CMO", "status": "on_track", "due_date": "2026-03-31"},
                {"description": "Implement weekly L10", "owner": "COO", "status": "complete", "due_date": "2026-02-28"},
                {"description": "Build hiring scorecard v2", "owner": "CHRO", "status": "off_track", "due_date": "2026-03-31"},
            ],
        }

    results = track_rocks(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
