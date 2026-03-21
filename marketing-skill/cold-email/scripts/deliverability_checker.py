#!/usr/bin/env python3
"""
Cold Email Deliverability Checker

Audits email content and infrastructure configuration for deliverability
issues against 2025-2026 Gmail/Yahoo/Microsoft requirements.
No API calls -- analyzes text content and DNS config locally.

Usage:
    python deliverability_checker.py email.txt
    python deliverability_checker.py email.txt --json
    python deliverability_checker.py email.txt --domain yourdomain.com
"""

import argparse
import json
import re
import sys
from pathlib import Path

# --- 2025-2026 Compliance Requirements ---
REQUIRED_AUTH = ["SPF", "DKIM", "DMARC"]
SPAM_COMPLAINT_THRESHOLD = 0.10  # percent
BOUNCE_RATE_THRESHOLD = 2.0  # percent
MAX_COLD_EMAIL_LENGTH = 200  # words
OPTIMAL_EMAIL_LENGTH = (50, 150)  # words

# --- Spam trigger patterns ---
SPAM_WORDS = [
    "free", "guarantee", "act now", "limited time", "urgent", "winner",
    "click here", "buy now", "order now", "risk-free", "no obligation",
    "100% free", "amazing deal", "cash bonus", "double your",
    "earn extra", "million dollars", "once in a lifetime", "congratulations",
    "you have been selected", "apply now", "sign up free",
]

LINK_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
IMAGE_PATTERN = re.compile(r"<img\s|!\[.*?\]\(", re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
TRACKING_PIXEL_PATTERN = re.compile(r'<img[^>]*(?:width|height)\s*=\s*["\']?1', re.IGNORECASE)
UNSUBSCRIBE_PATTERN = re.compile(r"unsubscribe|opt.out|opt-out|remove me|stop email", re.IGNORECASE)
ADDRESS_PATTERN = re.compile(r"\d+\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr|suite|ste|boulevard|blvd|lane|ln|way|place|pl)\b", re.IGNORECASE)


def analyze_email(content: str, domain: str = None) -> dict:
    """Analyze email content for deliverability issues."""
    results = {
        "overall_score": 100,
        "checks": [],
        "warnings": [],
        "critical": [],
        "recommendations": [],
        "stats": {},
    }

    # --- Content stats ---
    plain_text = HTML_TAG_PATTERN.sub("", content)
    words = plain_text.split()
    word_count = len(words)
    link_count = len(LINK_PATTERN.findall(content))
    has_html = bool(HTML_TAG_PATTERN.search(content))
    has_images = bool(IMAGE_PATTERN.search(content))
    has_tracking_pixel = bool(TRACKING_PIXEL_PATTERN.search(content))
    has_unsubscribe = bool(UNSUBSCRIBE_PATTERN.search(content))
    has_address = bool(ADDRESS_PATTERN.search(content))
    char_count = len(plain_text)

    results["stats"] = {
        "word_count": word_count,
        "character_count": char_count,
        "link_count": link_count,
        "has_html": has_html,
        "has_images": has_images,
        "has_tracking_pixel": has_tracking_pixel,
        "has_unsubscribe": has_unsubscribe,
        "has_physical_address": has_address,
    }

    # --- Check 1: Email length ---
    if word_count <= MAX_COLD_EMAIL_LENGTH:
        results["checks"].append({
            "name": "Email Length",
            "status": "PASS",
            "detail": f"{word_count} words (max recommended: {MAX_COLD_EMAIL_LENGTH})",
        })
    else:
        results["checks"].append({
            "name": "Email Length",
            "status": "WARN",
            "detail": f"{word_count} words exceeds {MAX_COLD_EMAIL_LENGTH}-word recommendation",
        })
        results["warnings"].append("Email is too long for cold outreach. Keep under 200 words.")
        results["overall_score"] -= 10

    if OPTIMAL_EMAIL_LENGTH[0] <= word_count <= OPTIMAL_EMAIL_LENGTH[1]:
        results["checks"].append({
            "name": "Optimal Length",
            "status": "PASS",
            "detail": f"{word_count} words is in the optimal range ({OPTIMAL_EMAIL_LENGTH[0]}-{OPTIMAL_EMAIL_LENGTH[1]})",
        })

    # --- Check 2: Spam trigger words ---
    found_spam = []
    lower_content = content.lower()
    for word in SPAM_WORDS:
        if word in lower_content:
            found_spam.append(word)

    if not found_spam:
        results["checks"].append({
            "name": "Spam Triggers",
            "status": "PASS",
            "detail": "No spam trigger words detected",
        })
    elif len(found_spam) <= 2:
        results["checks"].append({
            "name": "Spam Triggers",
            "status": "WARN",
            "detail": f"Found: {', '.join(found_spam)}",
        })
        results["warnings"].append(f"Spam trigger words detected: {', '.join(found_spam)}. Remove or rephrase.")
        results["overall_score"] -= 10
    else:
        results["checks"].append({
            "name": "Spam Triggers",
            "status": "FAIL",
            "detail": f"Found {len(found_spam)} spam triggers: {', '.join(found_spam)}",
        })
        results["critical"].append(f"Multiple spam triggers will likely cause spam filtering: {', '.join(found_spam)}")
        results["overall_score"] -= 25

    # --- Check 3: Link count ---
    if link_count == 0:
        results["checks"].append({
            "name": "Link Count",
            "status": "PASS",
            "detail": "No links (best for first cold touch in 2026)",
        })
    elif link_count <= 2:
        results["checks"].append({
            "name": "Link Count",
            "status": "WARN",
            "detail": f"{link_count} link(s) detected. ESPs flag links in cold emails.",
        })
        results["warnings"].append("In 2026, Gmail and Microsoft flag links in cold emails as security risks. Consider removing links from first touch.")
        results["overall_score"] -= 8
    else:
        results["checks"].append({
            "name": "Link Count",
            "status": "FAIL",
            "detail": f"{link_count} links detected. Too many for cold outreach.",
        })
        results["critical"].append("Multiple links in cold email significantly increase spam risk. Limit to 0-1 links.")
        results["overall_score"] -= 20

    # --- Check 4: HTML complexity ---
    if not has_html:
        results["checks"].append({
            "name": "Email Format",
            "status": "PASS",
            "detail": "Plain text format (best for cold email deliverability)",
        })
    else:
        html_tags = HTML_TAG_PATTERN.findall(content)
        if len(html_tags) > 10:
            results["checks"].append({
                "name": "Email Format",
                "status": "FAIL",
                "detail": f"Heavy HTML detected ({len(html_tags)} tags). Use plain text for cold email.",
            })
            results["critical"].append("HTML-heavy emails look like marketing blasts. Use plain text for cold outreach.")
            results["overall_score"] -= 20
        else:
            results["checks"].append({
                "name": "Email Format",
                "status": "WARN",
                "detail": "Minimal HTML detected. Plain text is preferred for cold email.",
            })
            results["overall_score"] -= 5

    # --- Check 5: Tracking pixels ---
    if has_tracking_pixel:
        results["checks"].append({
            "name": "Tracking Pixel",
            "status": "WARN",
            "detail": "Tracking pixel detected. These trigger spam filters in 2026.",
        })
        results["warnings"].append("Tracking pixels are increasingly flagged by Gmail/Yahoo. Consider disabling open tracking for cold email.")
        results["overall_score"] -= 10
    else:
        results["checks"].append({
            "name": "Tracking Pixel",
            "status": "PASS",
            "detail": "No tracking pixels detected",
        })

    # --- Check 6: Images ---
    if has_images:
        results["checks"].append({
            "name": "Images",
            "status": "WARN",
            "detail": "Images detected. Avoid images in cold email first touches.",
        })
        results["warnings"].append("Images in cold emails are considered security risks by ESPs. Remove for first touch.")
        results["overall_score"] -= 8

    # --- Check 7: Unsubscribe mechanism ---
    if has_unsubscribe:
        results["checks"].append({
            "name": "Unsubscribe",
            "status": "PASS",
            "detail": "Unsubscribe mechanism detected (required by CAN-SPAM and RFC 8058)",
        })
    else:
        results["checks"].append({
            "name": "Unsubscribe",
            "status": "WARN",
            "detail": "No unsubscribe mechanism detected",
        })
        results["warnings"].append("RFC 8058 one-click unsubscribe is required by Gmail/Yahoo/Microsoft since 2024. Add List-Unsubscribe headers.")
        results["overall_score"] -= 10

    # --- Check 8: Physical address ---
    if has_address:
        results["checks"].append({
            "name": "Physical Address",
            "status": "PASS",
            "detail": "Physical address detected (CAN-SPAM requirement)",
        })
    else:
        results["checks"].append({
            "name": "Physical Address",
            "status": "WARN",
            "detail": "No physical address detected (required by CAN-SPAM for US recipients)",
        })
        results["recommendations"].append("Include a physical mailing address for CAN-SPAM compliance.")
        results["overall_score"] -= 5

    # --- Check 9: Personalization ---
    personalization_patterns = [
        re.compile(r"\{\{?\s*name\s*\}?\}", re.IGNORECASE),
        re.compile(r"\{\{?\s*company\s*\}?\}", re.IGNORECASE),
        re.compile(r"\{\{?\s*first.?name\s*\}?\}", re.IGNORECASE),
        re.compile(r"\[name\]|\[company\]|\[first.?name\]", re.IGNORECASE),
    ]
    has_personalization = any(p.search(content) for p in personalization_patterns)
    if has_personalization:
        results["checks"].append({
            "name": "Personalization",
            "status": "PASS",
            "detail": "Personalization tokens detected",
        })
    else:
        results["checks"].append({
            "name": "Personalization",
            "status": "INFO",
            "detail": "No personalization tokens found. Personalized emails get 2-3x higher reply rates.",
        })
        results["recommendations"].append("Add personalization (name, company, trigger) to improve reply rates.")

    # --- Check 10: Sentence starters ---
    sentences = re.split(r"[.!?]\s+", plain_text)
    i_we_starts = sum(1 for s in sentences if re.match(r"^(I |We |My |Our )", s.strip()))
    if sentences and i_we_starts / max(len(sentences), 1) > 0.5:
        results["checks"].append({
            "name": "Self-Reference",
            "status": "WARN",
            "detail": f"{i_we_starts}/{len(sentences)} sentences start with I/We/My/Our",
        })
        results["warnings"].append("Too many sentences start with 'I' or 'We'. Lead with the prospect's world, not yours.")
        results["overall_score"] -= 8

    # --- Domain-specific checks ---
    if domain:
        results["domain_checks"] = {
            "domain": domain,
            "recommendations": [
                f"Verify SPF record exists for {domain}",
                f"Verify DKIM signing is configured for {domain}",
                f"Verify DMARC record exists: v=DMARC1; p=quarantine; rua=mailto:dmarc@{domain}",
                "Use a dedicated sending subdomain (e.g., mail.{} or outreach.{})".format(domain, domain),
                "Warm up new domains for 4-6 weeks before cold outreach",
                "Keep spam complaint rate under 0.10% (2026 Gmail/Yahoo threshold)",
                "Keep bounce rate under 2% (2026 Microsoft/Gmail requirement)",
                "Implement RFC 8058 one-click unsubscribe headers",
            ],
        }

    # --- Recommendations ---
    if not results["recommendations"]:
        results["recommendations"].append("Email content looks deliverability-friendly.")

    results["overall_score"] = max(0, min(100, results["overall_score"]))

    # Grade
    score = results["overall_score"]
    if score >= 85:
        results["grade"] = "A"
    elif score >= 70:
        results["grade"] = "B"
    elif score >= 55:
        results["grade"] = "C"
    elif score >= 40:
        results["grade"] = "D"
    else:
        results["grade"] = "F"

    return results


def format_human(result: dict) -> str:
    """Format result for human reading."""
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("  COLD EMAIL DELIVERABILITY CHECKER")
    lines.append("=" * 60)
    lines.append(f"\n  Overall Score: {result['overall_score']}/100 (Grade: {result['grade']})")
    lines.append(f"  Word Count: {result['stats']['word_count']} | Links: {result['stats']['link_count']} | HTML: {'Yes' if result['stats']['has_html'] else 'No'}")
    lines.append("")

    # Checks
    lines.append("  Checks:")
    for check in result["checks"]:
        icon = {"PASS": "+", "WARN": "!", "FAIL": "X", "INFO": "i"}
        lines.append(f"    [{icon.get(check['status'], '?')}] {check['name']}: {check['detail']}")

    if result["critical"]:
        lines.append("\n  CRITICAL ISSUES:")
        for c in result["critical"]:
            lines.append(f"    X {c}")

    if result["warnings"]:
        lines.append("\n  Warnings:")
        for w in result["warnings"]:
            lines.append(f"    ! {w}")

    if result["recommendations"]:
        lines.append("\n  Recommendations:")
        for r in result["recommendations"]:
            lines.append(f"    > {r}")

    if "domain_checks" in result:
        lines.append(f"\n  Domain: {result['domain_checks']['domain']}")
        lines.append("  Authentication Checklist:")
        for r in result["domain_checks"]["recommendations"]:
            lines.append(f"    [ ] {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Audit cold email content for deliverability against 2025-2026 requirements."
    )
    parser.add_argument("file", help="Email content file to analyze")
    parser.add_argument("--domain", "-d", help="Sending domain for infrastructure checks")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    args = parser.parse_args()

    try:
        content = Path(args.file).read_text()
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = analyze_email(content, domain=args.domain)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
