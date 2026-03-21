#!/usr/bin/env python3
"""Bottleneck Detector — Analyze application logs/traces to identify performance bottlenecks.

Parses JSON-formatted request logs or trace data and detects:
- Slow endpoints exceeding latency thresholds
- N+1 query patterns (repeated similar queries per request)
- High-latency external calls (DB, HTTP, cache)
- Endpoints with high variance (unstable performance)

Input format: JSON array of request log entries or newline-delimited JSON.
Each entry should have: endpoint, duration_ms, and optionally queries/spans.
"""

import argparse
import json
import math
import sys
from collections import defaultdict


def parse_input(source):
    """Read JSON log entries from file or stdin."""
    if source == "-":
        raw = sys.stdin.read()
    else:
        with open(source, "r") as f:
            raw = f.read()

    raw = raw.strip()
    if not raw:
        print("Error: empty input", file=sys.stderr)
        sys.exit(1)

    # Support both JSON array and newline-delimited JSON
    if raw.startswith("["):
        return json.loads(raw)
    else:
        entries = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return entries


def percentile(values, pct):
    """Calculate the given percentile from a sorted list of values."""
    if not values:
        return 0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def stddev(values):
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def detect_slow_endpoints(entries, threshold_ms):
    """Find endpoints where P95 latency exceeds the threshold."""
    by_endpoint = defaultdict(list)
    for entry in entries:
        ep = entry.get("endpoint") or entry.get("path") or entry.get("url", "unknown")
        dur = entry.get("duration_ms") or entry.get("latency_ms") or entry.get("response_time_ms", 0)
        by_endpoint[ep].append(dur)

    findings = []
    for ep, durations in sorted(by_endpoint.items()):
        p50 = percentile(durations, 50)
        p95 = percentile(durations, 95)
        p99 = percentile(durations, 99)
        avg = sum(durations) / len(durations)
        if p95 > threshold_ms:
            findings.append({
                "endpoint": ep,
                "request_count": len(durations),
                "avg_ms": round(avg, 2),
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "max_ms": round(max(durations), 2),
                "severity": "critical" if p95 > threshold_ms * 3 else "warning",
            })
    findings.sort(key=lambda x: x["p95_ms"], reverse=True)
    return findings


def detect_n_plus_one(entries, query_threshold):
    """Detect N+1 query patterns: requests with excessive query counts."""
    findings = []
    by_endpoint = defaultdict(list)

    for entry in entries:
        queries = entry.get("queries") or entry.get("db_queries") or []
        query_count = entry.get("query_count", len(queries))
        ep = entry.get("endpoint") or entry.get("path") or entry.get("url", "unknown")
        by_endpoint[ep].append({
            "query_count": query_count,
            "queries": queries,
            "duration_ms": entry.get("duration_ms", 0),
        })

    for ep, reqs in sorted(by_endpoint.items()):
        counts = [r["query_count"] for r in reqs]
        avg_count = sum(counts) / len(counts) if counts else 0
        max_count = max(counts) if counts else 0

        if avg_count > query_threshold:
            # Look for repeated query templates as N+1 evidence
            all_queries = []
            for r in reqs:
                all_queries.extend(r.get("queries", []))

            template_counts = defaultdict(int)
            for q in all_queries:
                tpl = q.get("template") or q.get("sql") or str(q)
                template_counts[tpl] += 1

            repeated = {t: c for t, c in template_counts.items() if c > len(reqs) * 2}

            findings.append({
                "endpoint": ep,
                "request_count": len(reqs),
                "avg_queries_per_request": round(avg_count, 1),
                "max_queries_per_request": max_count,
                "suspected_n_plus_one": bool(repeated),
                "repeated_query_templates": len(repeated),
                "severity": "critical" if avg_count > query_threshold * 3 else "warning",
            })

    findings.sort(key=lambda x: x["avg_queries_per_request"], reverse=True)
    return findings


def detect_high_latency_spans(entries, span_threshold_ms):
    """Identify high-latency spans (DB calls, HTTP calls, cache lookups)."""
    span_stats = defaultdict(list)

    for entry in entries:
        spans = entry.get("spans") or entry.get("traces") or []
        for span in spans:
            name = span.get("name") or span.get("operation") or "unknown"
            stype = span.get("type") or span.get("service") or "unknown"
            dur = span.get("duration_ms") or span.get("latency_ms", 0)
            key = f"{stype}:{name}"
            span_stats[key].append(dur)

    findings = []
    for key, durations in sorted(span_stats.items()):
        p95 = percentile(durations, 95)
        avg = sum(durations) / len(durations)
        if p95 > span_threshold_ms:
            stype, name = key.split(":", 1)
            findings.append({
                "span": name,
                "type": stype,
                "call_count": len(durations),
                "avg_ms": round(avg, 2),
                "p95_ms": round(p95, 2),
                "max_ms": round(max(durations), 2),
                "severity": "critical" if p95 > span_threshold_ms * 3 else "warning",
            })

    findings.sort(key=lambda x: x["p95_ms"], reverse=True)
    return findings


def detect_high_variance(entries, cv_threshold):
    """Find endpoints with high coefficient of variation (unstable performance)."""
    by_endpoint = defaultdict(list)
    for entry in entries:
        ep = entry.get("endpoint") or entry.get("path") or entry.get("url", "unknown")
        dur = entry.get("duration_ms") or entry.get("latency_ms") or entry.get("response_time_ms", 0)
        by_endpoint[ep].append(dur)

    findings = []
    for ep, durations in sorted(by_endpoint.items()):
        if len(durations) < 5:
            continue
        avg = sum(durations) / len(durations)
        if avg == 0:
            continue
        sd = stddev(durations)
        cv = sd / avg

        if cv > cv_threshold:
            findings.append({
                "endpoint": ep,
                "request_count": len(durations),
                "avg_ms": round(avg, 2),
                "stddev_ms": round(sd, 2),
                "coefficient_of_variation": round(cv, 3),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
                "severity": "warning",
            })

    findings.sort(key=lambda x: x["coefficient_of_variation"], reverse=True)
    return findings


def format_human(report):
    """Format the report as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("PERFORMANCE BOTTLENECK ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append(f"Total requests analyzed: {report['summary']['total_requests']}")
    lines.append(f"Unique endpoints: {report['summary']['unique_endpoints']}")
    lines.append(f"Total findings: {report['summary']['total_findings']}")
    lines.append(f"Critical: {report['summary']['critical_count']}  |  Warning: {report['summary']['warning_count']}")
    lines.append("")

    if report["slow_endpoints"]:
        lines.append("-" * 70)
        lines.append("SLOW ENDPOINTS (P95 exceeds threshold)")
        lines.append("-" * 70)
        for f in report["slow_endpoints"]:
            sev = "CRITICAL" if f["severity"] == "critical" else "WARNING "
            lines.append(f"  [{sev}] {f['endpoint']}")
            lines.append(f"           Requests: {f['request_count']}  |  Avg: {f['avg_ms']}ms  |  P95: {f['p95_ms']}ms  |  P99: {f['p99_ms']}ms  |  Max: {f['max_ms']}ms")
        lines.append("")

    if report["n_plus_one"]:
        lines.append("-" * 70)
        lines.append("N+1 QUERY PATTERNS")
        lines.append("-" * 70)
        for f in report["n_plus_one"]:
            sev = "CRITICAL" if f["severity"] == "critical" else "WARNING "
            n1 = " [N+1 CONFIRMED]" if f["suspected_n_plus_one"] else ""
            lines.append(f"  [{sev}] {f['endpoint']}{n1}")
            lines.append(f"           Avg queries/req: {f['avg_queries_per_request']}  |  Max: {f['max_queries_per_request']}  |  Repeated templates: {f['repeated_query_templates']}")
        lines.append("")

    if report["high_latency_spans"]:
        lines.append("-" * 70)
        lines.append("HIGH-LATENCY SPANS")
        lines.append("-" * 70)
        for f in report["high_latency_spans"]:
            sev = "CRITICAL" if f["severity"] == "critical" else "WARNING "
            lines.append(f"  [{sev}] {f['type']}:{f['span']}")
            lines.append(f"           Calls: {f['call_count']}  |  Avg: {f['avg_ms']}ms  |  P95: {f['p95_ms']}ms  |  Max: {f['max_ms']}ms")
        lines.append("")

    if report["high_variance"]:
        lines.append("-" * 70)
        lines.append("HIGH VARIANCE ENDPOINTS (unstable performance)")
        lines.append("-" * 70)
        for f in report["high_variance"]:
            lines.append(f"  [WARNING ] {f['endpoint']}")
            lines.append(f"           CV: {f['coefficient_of_variation']}  |  Avg: {f['avg_ms']}ms  |  StdDev: {f['stddev_ms']}ms  |  Range: {f['min_ms']}-{f['max_ms']}ms")
        lines.append("")

    if report["summary"]["total_findings"] == 0:
        lines.append("No bottlenecks detected. All endpoints within thresholds.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze application logs/traces to identify performance bottlenecks.",
        epilog="Input: JSON array or newline-delimited JSON with request log entries.",
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input file path or '-' for stdin (default: stdin)")
    parser.add_argument("--latency-threshold", type=float, default=200,
                        help="P95 latency threshold in ms for slow endpoint detection (default: 200)")
    parser.add_argument("--query-threshold", type=int, default=10,
                        help="Avg queries per request threshold for N+1 detection (default: 10)")
    parser.add_argument("--span-threshold", type=float, default=100,
                        help="P95 span latency threshold in ms (default: 100)")
    parser.add_argument("--cv-threshold", type=float, default=1.5,
                        help="Coefficient of variation threshold for high variance detection (default: 1.5)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    try:
        entries = parse_input(args.input)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("Error: no log entries found in input", file=sys.stderr)
        sys.exit(1)

    slow = detect_slow_endpoints(entries, args.latency_threshold)
    n1 = detect_n_plus_one(entries, args.query_threshold)
    spans = detect_high_latency_spans(entries, args.span_threshold)
    variance = detect_high_variance(entries, args.cv_threshold)

    all_findings = slow + n1 + spans + variance
    endpoints = set()
    for e in entries:
        ep = e.get("endpoint") or e.get("path") or e.get("url", "unknown")
        endpoints.add(ep)

    report = {
        "summary": {
            "total_requests": len(entries),
            "unique_endpoints": len(endpoints),
            "total_findings": len(all_findings),
            "critical_count": sum(1 for f in all_findings if f.get("severity") == "critical"),
            "warning_count": sum(1 for f in all_findings if f.get("severity") == "warning"),
        },
        "slow_endpoints": slow,
        "n_plus_one": n1,
        "high_latency_spans": spans,
        "high_variance": variance,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_human(report))


if __name__ == "__main__":
    main()
