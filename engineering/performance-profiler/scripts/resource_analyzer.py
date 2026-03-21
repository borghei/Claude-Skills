#!/usr/bin/env python3
"""Resource Analyzer — Analyze CPU, memory, and disk usage data for anomalies and trends.

Reads time-series resource usage data in JSON format and detects:
- Sustained high utilization (CPU, memory, disk above thresholds)
- Memory leaks (monotonically increasing memory over time)
- CPU spikes (sudden jumps in CPU usage)
- Disk pressure (approaching capacity limits)
- Trend analysis with linear regression for capacity planning

Input format: JSON array of timestamped resource snapshots.
Each entry should have: timestamp, and cpu/memory/disk metrics.
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime


def parse_input(source):
    """Read JSON resource data from file or stdin."""
    if source == "-":
        raw = sys.stdin.read()
    else:
        with open(source, "r") as f:
            raw = f.read()

    raw = raw.strip()
    if not raw:
        print("Error: empty input", file=sys.stderr)
        sys.exit(1)

    if raw.startswith("["):
        return json.loads(raw)
    else:
        entries = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return entries


def parse_timestamp(ts):
    """Try to parse various timestamp formats into epoch seconds."""
    if isinstance(ts, (int, float)):
        # Already epoch seconds or milliseconds
        if ts > 1e12:
            return ts / 1000.0
        return float(ts)
    if isinstance(ts, str):
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
            try:
                dt = datetime.strptime(ts.replace("+00:00", "Z").rstrip("Z") if "Z" not in fmt else ts, fmt)
                return dt.timestamp()
            except (ValueError, AttributeError):
                continue
    return 0.0


def extract_metric(entry, keys, default=None):
    """Extract a metric value trying multiple key names."""
    for key in keys:
        if key in entry:
            val = entry[key]
            if isinstance(val, dict):
                return val
            return val
    return default


def linear_regression(x_values, y_values):
    """Simple linear regression returning slope, intercept, and R-squared."""
    n = len(x_values)
    if n < 2:
        return 0, 0, 0

    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    sum_y2 = sum(y * y for y in y_values)

    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return 0, sum_y / n if n else 0, 0

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    # R-squared
    ss_tot = sum_y2 - (sum_y ** 2) / n
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return slope, intercept, r_squared


def analyze_cpu(entries, cpu_threshold):
    """Analyze CPU usage patterns."""
    cpu_values = []
    timestamps = []

    for entry in entries:
        cpu = extract_metric(entry, ["cpu_percent", "cpu_usage", "cpu", "cpu_pct"])
        if cpu is None:
            continue
        if isinstance(cpu, dict):
            cpu = cpu.get("percent") or cpu.get("usage") or cpu.get("total", 0)
        cpu_values.append(float(cpu))
        ts = extract_metric(entry, ["timestamp", "ts", "time", "date"], 0)
        timestamps.append(parse_timestamp(ts))

    if not cpu_values:
        return None

    avg = sum(cpu_values) / len(cpu_values)
    peak = max(cpu_values)
    minimum = min(cpu_values)

    # Detect spikes: values > 2 standard deviations above mean
    if len(cpu_values) >= 3:
        mean = avg
        sd = math.sqrt(sum((x - mean) ** 2 for x in cpu_values) / len(cpu_values))
        spike_threshold = mean + 2 * sd if sd > 0 else cpu_threshold
        spikes = sum(1 for v in cpu_values if v > spike_threshold)
    else:
        spikes = 0

    # Sustained high usage: percentage of samples above threshold
    high_samples = sum(1 for v in cpu_values if v > cpu_threshold)
    sustained_pct = (high_samples / len(cpu_values)) * 100

    # Trend
    if timestamps and timestamps[0] > 0 and len(timestamps) >= 3:
        t_norm = [(t - timestamps[0]) / 3600.0 for t in timestamps]  # hours
        slope, _, r2 = linear_regression(t_norm, cpu_values)
    else:
        slope, r2 = 0, 0

    findings = []
    if sustained_pct > 50:
        findings.append({
            "type": "sustained_high_cpu",
            "severity": "critical" if sustained_pct > 80 else "warning",
            "detail": f"CPU above {cpu_threshold}% for {sustained_pct:.1f}% of samples",
        })
    if spikes > 0:
        findings.append({
            "type": "cpu_spikes",
            "severity": "warning",
            "detail": f"{spikes} spike(s) detected (>2 std devs above mean)",
        })
    if slope > 1.0 and r2 > 0.5:
        findings.append({
            "type": "cpu_trend_increasing",
            "severity": "warning",
            "detail": f"CPU trending up at {slope:.2f}%/hour (R²={r2:.2f})",
        })

    return {
        "samples": len(cpu_values),
        "avg_percent": round(avg, 2),
        "min_percent": round(minimum, 2),
        "max_percent": round(peak, 2),
        "sustained_high_pct": round(sustained_pct, 1),
        "spike_count": spikes,
        "trend_slope_per_hour": round(slope, 3),
        "trend_r_squared": round(r2, 3),
        "findings": findings,
    }


def analyze_memory(entries, mem_threshold):
    """Analyze memory usage patterns, detect leaks."""
    mem_values = []
    timestamps = []

    for entry in entries:
        mem = extract_metric(entry, ["memory_percent", "memory_usage", "memory", "mem_pct", "mem_percent"])
        if mem is None:
            mem_mb = extract_metric(entry, ["memory_mb", "mem_mb", "rss_mb"])
            mem_total = extract_metric(entry, ["memory_total_mb", "total_memory_mb"])
            if mem_mb is not None and mem_total and mem_total > 0:
                mem = (float(mem_mb) / float(mem_total)) * 100
            elif mem_mb is not None:
                mem = float(mem_mb)  # Use raw MB if no total available
            else:
                continue
        if isinstance(mem, dict):
            mem = mem.get("percent") or mem.get("usage") or mem.get("used_pct", 0)
        mem_values.append(float(mem))
        ts = extract_metric(entry, ["timestamp", "ts", "time", "date"], 0)
        timestamps.append(parse_timestamp(ts))

    if not mem_values:
        return None

    avg = sum(mem_values) / len(mem_values)
    peak = max(mem_values)
    minimum = min(mem_values)

    high_samples = sum(1 for v in mem_values if v > mem_threshold)
    sustained_pct = (high_samples / len(mem_values)) * 100

    # Memory leak detection via linear regression
    if timestamps and timestamps[0] > 0 and len(timestamps) >= 3:
        t_norm = [(t - timestamps[0]) / 3600.0 for t in timestamps]
        slope, _, r2 = linear_regression(t_norm, mem_values)
    else:
        # Use index as proxy
        indices = list(range(len(mem_values)))
        slope, _, r2 = linear_regression(indices, mem_values)

    # Monotonic increase check (leak indicator)
    if len(mem_values) >= 5:
        window = max(1, len(mem_values) // 5)
        windows = [mem_values[i:i + window] for i in range(0, len(mem_values), window)]
        window_avgs = [sum(w) / len(w) for w in windows if w]
        monotonic = all(window_avgs[i] <= window_avgs[i + 1] for i in range(len(window_avgs) - 1))
    else:
        monotonic = False

    findings = []
    if sustained_pct > 50:
        findings.append({
            "type": "sustained_high_memory",
            "severity": "critical" if sustained_pct > 80 else "warning",
            "detail": f"Memory above {mem_threshold}% for {sustained_pct:.1f}% of samples",
        })
    if slope > 0.5 and r2 > 0.7 and monotonic:
        findings.append({
            "type": "probable_memory_leak",
            "severity": "critical",
            "detail": f"Memory monotonically increasing at {slope:.2f} units/hour (R²={r2:.2f})",
        })
    elif slope > 0.5 and r2 > 0.5:
        findings.append({
            "type": "memory_trend_increasing",
            "severity": "warning",
            "detail": f"Memory trending up at {slope:.2f} units/hour (R²={r2:.2f})",
        })

    return {
        "samples": len(mem_values),
        "avg_percent": round(avg, 2),
        "min_percent": round(minimum, 2),
        "max_percent": round(peak, 2),
        "sustained_high_pct": round(sustained_pct, 1),
        "trend_slope_per_hour": round(slope, 3),
        "trend_r_squared": round(r2, 3),
        "monotonic_increase": monotonic,
        "findings": findings,
    }


def analyze_disk(entries, disk_threshold):
    """Analyze disk usage and detect capacity pressure."""
    disk_values = []
    timestamps = []

    for entry in entries:
        disk = extract_metric(entry, ["disk_percent", "disk_usage", "disk", "disk_pct"])
        if disk is None:
            disk_used = extract_metric(entry, ["disk_used_gb", "disk_used_mb"])
            disk_total = extract_metric(entry, ["disk_total_gb", "disk_total_mb"])
            if disk_used is not None and disk_total and float(disk_total) > 0:
                disk = (float(disk_used) / float(disk_total)) * 100
            else:
                continue
        if isinstance(disk, dict):
            disk = disk.get("percent") or disk.get("usage") or disk.get("used_pct", 0)
        disk_values.append(float(disk))
        ts = extract_metric(entry, ["timestamp", "ts", "time", "date"], 0)
        timestamps.append(parse_timestamp(ts))

    if not disk_values:
        return None

    avg = sum(disk_values) / len(disk_values)
    current = disk_values[-1]
    peak = max(disk_values)

    # Trend for capacity planning
    if timestamps and timestamps[0] > 0 and len(timestamps) >= 3:
        t_norm = [(t - timestamps[0]) / 3600.0 for t in timestamps]
        slope, intercept, r2 = linear_regression(t_norm, disk_values)
        # Estimate hours until threshold
        if slope > 0 and r2 > 0.5:
            hours_to_threshold = (disk_threshold - current) / slope if current < disk_threshold else 0
            hours_to_full = (100 - current) / slope
        else:
            hours_to_threshold = None
            hours_to_full = None
    else:
        slope, r2 = 0, 0
        hours_to_threshold = None
        hours_to_full = None

    findings = []
    if current > disk_threshold:
        findings.append({
            "type": "disk_pressure",
            "severity": "critical" if current > 95 else "warning",
            "detail": f"Disk usage at {current:.1f}%, above {disk_threshold}% threshold",
        })
    if hours_to_full is not None and hours_to_full < 168:  # less than 7 days
        days = hours_to_full / 24
        findings.append({
            "type": "disk_capacity_warning",
            "severity": "critical" if days < 2 else "warning",
            "detail": f"At current growth rate, disk reaches 100% in {days:.1f} days",
        })

    result = {
        "samples": len(disk_values),
        "avg_percent": round(avg, 2),
        "current_percent": round(current, 2),
        "peak_percent": round(peak, 2),
        "trend_slope_per_hour": round(slope, 3),
        "trend_r_squared": round(r2, 3),
        "findings": findings,
    }
    if hours_to_full is not None:
        result["estimated_days_to_full"] = round(hours_to_full / 24, 1)

    return result


def format_human(report):
    """Format the report as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("RESOURCE USAGE ANALYSIS REPORT")
    lines.append("=" * 70)
    s = report["summary"]
    lines.append(f"Total samples: {s['total_samples']}  |  Findings: {s['total_findings']}")
    lines.append(f"Critical: {s['critical_count']}  |  Warning: {s['warning_count']}")
    lines.append("")

    for section_key, title in [("cpu", "CPU ANALYSIS"), ("memory", "MEMORY ANALYSIS"), ("disk", "DISK ANALYSIS")]:
        data = report.get(section_key)
        if data is None:
            continue

        lines.append("-" * 70)
        lines.append(title)
        lines.append("-" * 70)

        if section_key == "cpu":
            lines.append(f"  Samples: {data['samples']}  |  Avg: {data['avg_percent']}%  |  Min: {data['min_percent']}%  |  Max: {data['max_percent']}%")
            lines.append(f"  Sustained high: {data['sustained_high_pct']}% of samples  |  Spikes: {data['spike_count']}")
            lines.append(f"  Trend: {data['trend_slope_per_hour']:+.3f}%/hr (R²={data['trend_r_squared']:.3f})")
        elif section_key == "memory":
            lines.append(f"  Samples: {data['samples']}  |  Avg: {data['avg_percent']}%  |  Min: {data['min_percent']}%  |  Max: {data['max_percent']}%")
            lines.append(f"  Sustained high: {data['sustained_high_pct']}% of samples  |  Monotonic increase: {'Yes' if data['monotonic_increase'] else 'No'}")
            lines.append(f"  Trend: {data['trend_slope_per_hour']:+.3f} units/hr (R²={data['trend_r_squared']:.3f})")
        elif section_key == "disk":
            lines.append(f"  Samples: {data['samples']}  |  Avg: {data['avg_percent']}%  |  Current: {data['current_percent']}%  |  Peak: {data['peak_percent']}%")
            lines.append(f"  Trend: {data['trend_slope_per_hour']:+.3f}%/hr (R²={data['trend_r_squared']:.3f})")
            if "estimated_days_to_full" in data:
                lines.append(f"  Estimated days to 100%: {data['estimated_days_to_full']}")

        for f in data.get("findings", []):
            sev = "CRITICAL" if f["severity"] == "critical" else "WARNING "
            lines.append(f"  [{sev}] {f['detail']}")
        lines.append("")

    if s["total_findings"] == 0:
        lines.append("All resource metrics within normal thresholds.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze resource usage data (CPU, memory, disk) and flag anomalies and trends.",
        epilog="Input: JSON array of timestamped resource snapshots.",
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input file path or '-' for stdin (default: stdin)")
    parser.add_argument("--cpu-threshold", type=float, default=80,
                        help="CPU usage percent threshold for high-usage alerts (default: 80)")
    parser.add_argument("--memory-threshold", type=float, default=85,
                        help="Memory usage percent threshold for high-usage alerts (default: 85)")
    parser.add_argument("--disk-threshold", type=float, default=90,
                        help="Disk usage percent threshold for capacity alerts (default: 90)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    try:
        entries = parse_input(args.input)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("Error: no resource data entries found", file=sys.stderr)
        sys.exit(1)

    cpu_result = analyze_cpu(entries, args.cpu_threshold)
    mem_result = analyze_memory(entries, args.memory_threshold)
    disk_result = analyze_disk(entries, args.disk_threshold)

    all_findings = []
    total_samples = 0
    for result in [cpu_result, mem_result, disk_result]:
        if result:
            all_findings.extend(result.get("findings", []))
            total_samples = max(total_samples, result.get("samples", 0))

    report = {
        "summary": {
            "total_samples": total_samples,
            "total_findings": len(all_findings),
            "critical_count": sum(1 for f in all_findings if f["severity"] == "critical"),
            "warning_count": sum(1 for f in all_findings if f["severity"] == "warning"),
        },
        "cpu": cpu_result,
        "memory": mem_result,
        "disk": disk_result,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_human(report))


if __name__ == "__main__":
    main()
