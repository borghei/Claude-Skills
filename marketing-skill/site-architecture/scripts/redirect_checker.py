#!/usr/bin/env python3
"""
URL Redirect Chain Checker for Site Architecture

Checks URLs for redirect chains, HTTP/HTTPS consistency, trailing slash
consistency, and common URL pattern issues. Designed for architecture
migration audits and restructuring projects.

Usage:
    python redirect_checker.py --file urls.txt
    python redirect_checker.py --file urls.txt --json
    python redirect_checker.py --url https://example.com/old-page
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def normalize_url(url):
    """Ensure URL has a scheme."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def check_url_patterns(url):
    """Analyze URL for architectural issues."""
    issues = []
    parsed = urlparse(normalize_url(url))

    # HTTP check
    if parsed.scheme == 'http':
        issues.append({
            "type": "no_https",
            "severity": "High",
            "detail": "URL uses HTTP — should be HTTPS",
        })

    # Path depth
    segments = [s for s in parsed.path.split('/') if s]
    depth = len(segments)
    if depth > 3:
        issues.append({
            "type": "deep_url",
            "severity": "Medium",
            "detail": f"URL depth is {depth} — ideally 3 or fewer levels",
        })

    # Uppercase
    if parsed.path != parsed.path.lower():
        issues.append({
            "type": "uppercase",
            "severity": "Medium",
            "detail": "URL contains uppercase characters — may cause duplicates",
        })

    # Underscores
    if '_' in parsed.path:
        issues.append({
            "type": "underscores",
            "severity": "Low",
            "detail": "URL uses underscores — hyphens preferred by Google",
        })

    # Parameters
    if parsed.query:
        issues.append({
            "type": "parameters",
            "severity": "Medium",
            "detail": f"URL contains parameters: {parsed.query}",
        })

    # File extensions (non-standard)
    if re.search(r'\.(php|asp|aspx|jsp|cgi)$', parsed.path, re.IGNORECASE):
        issues.append({
            "type": "legacy_extension",
            "severity": "Low",
            "detail": "URL has legacy file extension — clean URLs preferred",
        })

    # Double slashes in path
    if '//' in parsed.path:
        issues.append({
            "type": "double_slash",
            "severity": "Medium",
            "detail": "URL contains double slash in path",
        })

    # IDs or numbers in URL
    if re.search(r'/\d{4,}', parsed.path):
        issues.append({
            "type": "numeric_id",
            "severity": "Low",
            "detail": "URL contains numeric IDs — descriptive slugs preferred",
        })

    return {
        "url": url,
        "normalized": normalize_url(url),
        "depth": depth,
        "segments": segments,
        "has_trailing_slash": parsed.path.endswith('/') and parsed.path != '/',
        "issues": issues,
        "passed": len([i for i in issues if i["severity"] in ("High", "Critical")]) == 0,
    }


def check_redirect(url, max_hops=10):
    """Check URL for redirect chains via HTTP."""
    url = normalize_url(url)
    chain = []
    current = url
    visited = set()
    issues = []

    try:
        import http.client
        import ssl

        for hop in range(max_hops):
            if current in visited:
                issues.append({
                    "type": "redirect_loop",
                    "severity": "Critical",
                    "detail": f"Loop detected at {current}",
                })
                break
            visited.add(current)

            parsed = urlparse(current)
            try:
                if parsed.scheme == 'https':
                    ctx = ssl.create_default_context()
                    conn = http.client.HTTPSConnection(parsed.netloc, timeout=10, context=ctx)
                else:
                    conn = http.client.HTTPConnection(parsed.netloc, timeout=10)

                path = parsed.path or '/'
                if parsed.query:
                    path += '?' + parsed.query

                conn.request('HEAD', path, headers={'User-Agent': 'Architecture-Audit/1.0'})
                resp = conn.getresponse()
                status = resp.status

                chain.append({"hop": hop + 1, "url": current, "status": status})

                if status in (301, 302, 303, 307, 308):
                    location = resp.getheader('Location', '')
                    if location:
                        from urllib.parse import urljoin
                        next_url = urljoin(current, location)

                        if status == 302:
                            issues.append({
                                "type": "temporary_redirect",
                                "severity": "High",
                                "detail": f"302 at hop {hop + 1} — should be 301 for permanent moves",
                            })

                        current = next_url
                    else:
                        break
                else:
                    break

                conn.close()
            except Exception as e:
                chain.append({"hop": hop + 1, "url": current, "status": "error", "error": str(e)})
                break

    except ImportError:
        chain.append({"hop": 1, "url": current, "status": "skipped", "note": "HTTP check unavailable"})

    hops = max(len(chain) - 1, 0)
    if hops > 2:
        issues.append({
            "type": "long_chain",
            "severity": "High",
            "detail": f"Redirect chain has {hops} hops — max 2 recommended",
        })

    return {
        "original_url": url,
        "final_url": chain[-1]["url"] if chain else url,
        "total_hops": hops,
        "chain": chain,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check URLs for redirect chains and architecture issues"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Single URL to check")
    group.add_argument("--file", help="File with URLs (one per line)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--patterns-only", action="store_true", help="Only check URL patterns, no HTTP requests")
    args = parser.parse_args()

    urls = []
    if args.url:
        urls = [args.url]
    else:
        fp = Path(args.file)
        if not fp.exists():
            print(f"Error: {fp} not found", file=sys.stderr)
            sys.exit(1)
        urls = [l.strip() for l in fp.read_text().splitlines() if l.strip() and not l.startswith('#')]

    results = []
    trailing_slash_counts = {"with": 0, "without": 0}

    for url in urls:
        pattern_result = check_url_patterns(url)
        if pattern_result["has_trailing_slash"]:
            trailing_slash_counts["with"] += 1
        elif pattern_result["depth"] > 0:
            trailing_slash_counts["without"] += 1

        if not args.patterns_only:
            redirect_result = check_redirect(url)
            pattern_result["redirect"] = redirect_result
            pattern_result["issues"].extend(redirect_result["issues"])

        results.append(pattern_result)

    # Check trailing slash consistency across all URLs
    consistency_issue = None
    if trailing_slash_counts["with"] > 0 and trailing_slash_counts["without"] > 0:
        consistency_issue = {
            "type": "inconsistent_trailing_slash",
            "severity": "Medium",
            "detail": f"{trailing_slash_counts['with']} URLs with trailing slash, {trailing_slash_counts['without']} without",
        }

    passed = sum(1 for r in results if r["passed"])

    output = {
        "total_urls": len(results),
        "passed": passed,
        "trailing_slash_consistency": consistency_issue,
        "results": results,
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  URL ARCHITECTURE CHECK — {len(results)} URLs")
        print(f"{'='*60}")
        print(f"  Passed: {passed}/{len(results)}")

        if consistency_issue:
            print(f"  [{consistency_issue['severity']}] {consistency_issue['detail']}")

        for r in results:
            all_issues = r["issues"]
            status = "OK" if r["passed"] else "ISSUES"
            print(f"\n  [{status}] {r['url']} (depth: {r['depth']})")
            if all_issues:
                for issue in all_issues:
                    print(f"    [{issue['severity']}] {issue['detail']}")
            if "redirect" in r and r["redirect"]["total_hops"] > 0:
                print(f"    Redirects: {r['redirect']['total_hops']} hops -> {r['redirect']['final_url']}")

        print()


if __name__ == "__main__":
    main()
