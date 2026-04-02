#!/usr/bin/env python3
"""
Snowflake Query Helper - Analyze and optimize Snowflake SQL with warehouse sizing.

Performs static analysis of Snowflake SQL to identify anti-patterns, optimization
opportunities, and provides warehouse sizing recommendations based on workload.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple


@dataclass
class QueryIssue:
    """An issue found in a SQL query."""
    severity: str  # critical, high, medium, low, info
    category: str  # performance, cost, correctness, style
    title: str
    description: str
    line_number: Optional[int] = None
    suggestion: str = ""
    estimated_impact: str = ""  # high, medium, low


@dataclass
class QueryAnalysis:
    """Analysis of a single SQL query."""
    query_text: str
    query_index: int
    issues: List[QueryIssue] = field(default_factory=list)
    complexity_score: int = 0  # 0-100
    estimated_warehouse_size: str = ""


@dataclass
class AnalysisReport:
    """Full analysis report."""
    total_queries: int
    total_issues: int
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    queries: List[QueryAnalysis] = field(default_factory=list)
    warehouse_recommendation: Optional[Dict] = None


# SQL anti-pattern detection rules
# (pattern, severity, category, title, description, suggestion, impact)
SQL_PATTERNS = [
    (r'\bSELECT\s+\*\b', "high", "performance",
     "SELECT * detected",
     "SELECT * reads all columns, increasing I/O and network transfer. In columnar storage like Snowflake, specifying columns dramatically reduces scan time.",
     "Specify only the columns needed: SELECT col1, col2, ...",
     "high"),

    (r'\bORDER\s+BY\b(?![\s\S]*\bLIMIT\b)', "medium", "performance",
     "ORDER BY without LIMIT",
     "Sorting large result sets is expensive. Without LIMIT, the entire dataset must be sorted.",
     "Add LIMIT clause or remove ORDER BY if not needed for final output.",
     "medium"),

    (r'\bUNION\b(?!\s+ALL)', "medium", "performance",
     "UNION without ALL (implicit DISTINCT)",
     "UNION performs deduplication which requires sorting. Use UNION ALL if duplicates are acceptable.",
     "Use UNION ALL unless deduplication is explicitly required.",
     "medium"),

    (r'\bNOT\s+IN\s*\(', "medium", "correctness",
     "NOT IN with potential NULL values",
     "NOT IN behaves unexpectedly with NULLs - if any value in the subquery is NULL, no rows are returned.",
     "Use NOT EXISTS instead of NOT IN for NULL-safe behavior.",
     "medium"),

    (r'(?:WHERE|AND|OR)\s+\w+\s*(?:LIKE|ILIKE)\s+[\'"]%', "medium", "performance",
     "Leading wildcard in LIKE/ILIKE",
     "Leading wildcard (LIKE '%pattern') prevents use of search optimization and causes full scans.",
     "Consider using SEARCH OPTIMIZATION or restructuring the query to avoid leading wildcards.",
     "high"),

    (r'(?:WHERE|AND|OR)\s+(?:UPPER|LOWER|TRIM|SUBSTR)\s*\(', "medium", "performance",
     "Function on column in WHERE clause",
     "Applying functions to columns in WHERE prevents pruning and search optimization.",
     "Pre-compute values in a derived column or use expression-based search optimization.",
     "medium"),

    (r'\bCROSS\s+JOIN\b', "high", "performance",
     "CROSS JOIN detected",
     "CROSS JOINs produce cartesian products which can generate massive intermediate result sets.",
     "Verify CROSS JOIN is intentional. Consider replacing with INNER/LEFT JOIN with conditions.",
     "high"),

    (r'\bINSERT\s+INTO\b[\s\S]*?\bSELECT\b[\s\S]*?\bORDER\s+BY\b', "low", "performance",
     "ORDER BY in INSERT...SELECT",
     "ORDER BY in INSERT...SELECT is unnecessary - row order is not preserved in tables.",
     "Remove the ORDER BY clause from the INSERT...SELECT statement.",
     "low"),

    (r'\bDISTINCT\b', "low", "performance",
     "DISTINCT keyword used",
     "DISTINCT requires deduplication processing. Ensure it's necessary - often indicates a JOIN issue.",
     "Verify DISTINCT is needed. If used to fix duplicate rows from JOINs, fix the JOIN instead.",
     "low"),

    (r'\bCOUNT\s*\(\s*DISTINCT\b', "low", "performance",
     "COUNT(DISTINCT ...) detected",
     "COUNT(DISTINCT) is expensive on large datasets. Consider APPROX_COUNT_DISTINCT for estimates.",
     "Use APPROX_COUNT_DISTINCT() if exact count is not required (99% accuracy, much faster).",
     "medium"),

    (r'(?:LATERAL\s+)?FLATTEN\s*\(', "info", "style",
     "FLATTEN operation detected",
     "FLATTEN on semi-structured data is valid but can be expensive on large VARIANT columns.",
     "Ensure FLATTEN is applied to pre-filtered data to minimize processing.",
     "low"),

    (r'\bCREATE\s+(?:OR\s+REPLACE\s+)?TABLE\b(?![\s\S]*\bTRANSIENT\b)[\s\S]*?\bAS\s+SELECT\b', "info", "cost",
     "CTAS creating permanent table",
     "Creating permanent tables incurs Time Travel and Fail-Safe storage costs.",
     "Use TRANSIENT tables for staging/temporary data to avoid extra storage costs.",
     "low"),

    (r'\bALTER\s+WAREHOUSE\b[\s\S]*?\bRESUME\b', "info", "cost",
     "Manual warehouse resume",
     "Manual warehouse management may indicate missing auto-resume settings.",
     "Enable auto-resume on warehouses to reduce management overhead.",
     "low"),

    (r'\bCOPY\s+INTO\b[\s\S]*?\bFROM\b[\s\S]*?@', "info", "style",
     "COPY INTO from stage detected",
     "Data loading from stage. Ensure proper file format and error handling are configured.",
     "Use ON_ERROR = 'CONTINUE' for fault-tolerant loads. Consider Snowpipe for streaming.",
     "low"),

    (r'\bMERGE\s+INTO\b', "info", "style",
     "MERGE statement detected",
     "MERGE is ideal for upsert patterns. Ensure the join condition is selective.",
     "Verify the ON clause is selective. Unselective MERGE can be very slow.",
     "medium"),
]

# Warehouse sizing recommendations
WAREHOUSE_SIZES = {
    "X-Small": {"credits_hr": 1, "max_data_gb": 50, "max_concurrent": 5},
    "Small": {"credits_hr": 2, "max_data_gb": 200, "max_concurrent": 10},
    "Medium": {"credits_hr": 4, "max_data_gb": 500, "max_concurrent": 20},
    "Large": {"credits_hr": 8, "max_data_gb": 2000, "max_concurrent": 50},
    "X-Large": {"credits_hr": 16, "max_data_gb": 5000, "max_concurrent": 100},
    "2X-Large": {"credits_hr": 32, "max_data_gb": 20000, "max_concurrent": 200},
}

WORKLOAD_PROFILES = {
    "etl": {
        "description": "Extract-Transform-Load batch processing",
        "typical_size": "Medium to Large",
        "auto_suspend": 0,
        "auto_resume": True,
        "multi_cluster": False,
        "scaling_policy": "N/A",
        "tips": [
            "Size warehouse to complete ETL within SLA window",
            "Larger warehouse = faster completion, same total credits",
            "Suspend immediately after pipeline completion",
            "Schedule during off-peak hours if using reserved capacity",
        ],
    },
    "bi": {
        "description": "Business Intelligence dashboards and reporting",
        "typical_size": "Small to Medium",
        "auto_suspend": 300,
        "auto_resume": True,
        "multi_cluster": True,
        "scaling_policy": "Standard",
        "tips": [
            "Enable multi-cluster for concurrent dashboard users",
            "5-minute auto-suspend balances cost and responsiveness",
            "Consider materialized views for common dashboard queries",
            "Monitor queue time - if high, scale up",
        ],
    },
    "ad-hoc": {
        "description": "Interactive analyst queries",
        "typical_size": "X-Small to Small",
        "auto_suspend": 60,
        "auto_resume": True,
        "multi_cluster": False,
        "scaling_policy": "N/A",
        "tips": [
            "Aggressive auto-suspend (60s) minimizes idle costs",
            "Start small - analysts can size up for complex queries",
            "Set resource monitors to prevent runaway costs",
            "Consider separate warehouse per team for cost attribution",
        ],
    },
    "data-science": {
        "description": "Data science and ML workloads",
        "typical_size": "Medium to X-Large",
        "auto_suspend": 300,
        "auto_resume": True,
        "multi_cluster": False,
        "scaling_policy": "N/A",
        "tips": [
            "Size based on data volume being processed",
            "Consider Snowpark-optimized warehouses for ML workloads",
            "Use temporary tables for intermediate results",
            "Monitor credit consumption per notebook/session",
        ],
    },
    "ingest": {
        "description": "Real-time or near-real-time data ingestion",
        "typical_size": "X-Small to Small",
        "auto_suspend": 60,
        "auto_resume": True,
        "multi_cluster": False,
        "scaling_policy": "N/A",
        "tips": [
            "Consider Snowpipe for automatic ingestion",
            "Use COPY INTO for batch loading",
            "X-Small is sufficient for most file-based ingestion",
            "Monitor file queue depth",
        ],
    },
}


def split_queries(sql_text: str) -> List[str]:
    """Split SQL text into individual queries."""
    # Remove comments
    sql_text = re.sub(r'--[^\n]*', '', sql_text)
    sql_text = re.sub(r'/\*.*?\*/', '', sql_text, flags=re.DOTALL)

    queries = [q.strip() for q in sql_text.split(";") if q.strip()]
    return queries


def analyze_query(query: str, index: int) -> QueryAnalysis:
    """Analyze a single SQL query."""
    analysis = QueryAnalysis(query_text=query, query_index=index)
    query_upper = query.upper()

    # Run pattern matching
    lines = query.split("\n")
    for pattern_str, severity, category, title, desc, suggestion, impact in SQL_PATTERNS:
        try:
            matches = list(re.finditer(pattern_str, query, re.IGNORECASE | re.DOTALL))
        except re.error:
            continue

        for match in matches:
            # Find line number
            pos = match.start()
            line_num = query[:pos].count("\n") + 1

            analysis.issues.append(QueryIssue(
                severity=severity,
                category=category,
                title=title,
                description=desc,
                line_number=line_num,
                suggestion=suggestion,
                estimated_impact=impact,
            ))

    # Calculate complexity score
    complexity = 0
    if re.search(r'\bJOIN\b', query_upper):
        join_count = len(re.findall(r'\bJOIN\b', query_upper))
        complexity += join_count * 10
    if re.search(r'\bSUBQUERY\b|\(\s*SELECT\b', query_upper):
        complexity += 20
    if re.search(r'\bWINDOW\b|OVER\s*\(', query_upper):
        complexity += 15
    if re.search(r'\bGROUP\s+BY\b', query_upper):
        complexity += 10
    if re.search(r'\bHAVING\b', query_upper):
        complexity += 10
    if re.search(r'\bUNION\b', query_upper):
        complexity += 15
    if re.search(r'\bCASE\b', query_upper):
        complexity += 5
    cte_count = len(re.findall(r'\bWITH\b', query_upper))
    complexity += cte_count * 10
    analysis.complexity_score = min(100, complexity)

    # Estimate warehouse size
    if analysis.complexity_score <= 20:
        analysis.estimated_warehouse_size = "X-Small"
    elif analysis.complexity_score <= 40:
        analysis.estimated_warehouse_size = "Small"
    elif analysis.complexity_score <= 60:
        analysis.estimated_warehouse_size = "Medium"
    elif analysis.complexity_score <= 80:
        analysis.estimated_warehouse_size = "Large"
    else:
        analysis.estimated_warehouse_size = "X-Large"

    return analysis


def recommend_warehouse(workload: str, data_volume_str: str) -> Dict:
    """Generate warehouse sizing recommendation."""
    profile = WORKLOAD_PROFILES.get(workload, WORKLOAD_PROFILES["ad-hoc"])

    # Parse data volume
    volume_gb = 0
    match = re.match(r'(\d+(?:\.\d+)?)\s*(GB|TB|PB)', data_volume_str, re.IGNORECASE)
    if match:
        num = float(match.group(1))
        unit = match.group(2).upper()
        if unit == "TB":
            volume_gb = num * 1024
        elif unit == "PB":
            volume_gb = num * 1024 * 1024
        else:
            volume_gb = num

    # Find appropriate size
    recommended_size = "X-Small"
    for size_name, specs in WAREHOUSE_SIZES.items():
        if volume_gb <= specs["max_data_gb"]:
            recommended_size = size_name
            break
    else:
        recommended_size = "2X-Large"

    specs = WAREHOUSE_SIZES.get(recommended_size, WAREHOUSE_SIZES["Medium"])

    return {
        "workload_type": workload,
        "workload_description": profile["description"],
        "data_volume": data_volume_str,
        "recommended_size": recommended_size,
        "credits_per_hour": specs["credits_hr"],
        "estimated_daily_cost_8hr": round(specs["credits_hr"] * 8 * 2.0, 2),  # $2/credit estimate
        "configuration": {
            "auto_suspend_seconds": profile["auto_suspend"],
            "auto_resume": profile["auto_resume"],
            "multi_cluster": profile["multi_cluster"],
            "scaling_policy": profile["scaling_policy"],
        },
        "tips": profile["tips"],
        "sql_create": (
            f"CREATE WAREHOUSE IF NOT EXISTS wh_{workload}\n"
            f"  WAREHOUSE_SIZE = '{recommended_size}'\n"
            f"  AUTO_SUSPEND = {profile['auto_suspend']}\n"
            f"  AUTO_RESUME = {profile['auto_resume']}\n"
            f"  {'ENABLE_QUERY_ACCELERATION = TRUE' if workload == 'ad-hoc' else ''}\n"
            f"  COMMENT = '{profile['description']}';"
        ),
    }


def analyze_file(sql_text: str) -> AnalysisReport:
    """Analyze SQL file."""
    queries = split_queries(sql_text)
    report = AnalysisReport(total_queries=len(queries), total_issues=0)

    for i, query in enumerate(queries):
        analysis = analyze_query(query, i + 1)
        report.queries.append(analysis)
        report.total_issues += len(analysis.issues)

    severity_counts: Dict[str, int] = {}
    for q in report.queries:
        for issue in q.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
    report.issues_by_severity = severity_counts

    return report


def format_human_analysis(report: AnalysisReport) -> str:
    """Format analysis for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("SNOWFLAKE SQL ANALYSIS")
    lines.append("=" * 65)
    lines.append(f"Queries analyzed: {report.total_queries}")
    lines.append(f"Total issues: {report.total_issues}")
    if report.issues_by_severity:
        lines.append(f"By severity: {report.issues_by_severity}")
    lines.append("")

    for q in report.queries:
        lines.append(f"--- Query #{q.query_index} (complexity: {q.complexity_score}/100, suggested WH: {q.estimated_warehouse_size}) ---")
        preview = q.query_text.strip()[:100].replace("\n", " ")
        lines.append(f"  {preview}...")
        lines.append("")

        if not q.issues:
            lines.append("  No issues found.")
        else:
            for i, issue in enumerate(q.issues, 1):
                ln = f" (line {issue.line_number})" if issue.line_number else ""
                lines.append(f"  [{issue.severity.upper()}]{ln} {issue.title}")
                lines.append(f"    {issue.description}")
                lines.append(f"    Fix: {issue.suggestion}")
                lines.append(f"    Impact: {issue.estimated_impact}")
                lines.append("")

    if report.warehouse_recommendation:
        rec = report.warehouse_recommendation
        lines.append("WAREHOUSE RECOMMENDATION:")
        lines.append(f"  Size: {rec['recommended_size']}")
        lines.append(f"  Credits/hr: {rec['credits_per_hour']}")
        lines.append(f"  Est. daily cost (8hr): ${rec['estimated_daily_cost_8hr']}")

    lines.append("=" * 65)
    return "\n".join(lines)


def format_human_warehouse(rec: Dict) -> str:
    """Format warehouse recommendation for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("SNOWFLAKE WAREHOUSE SIZING RECOMMENDATION")
    lines.append("=" * 65)
    lines.append(f"Workload: {rec['workload_type']} ({rec['workload_description']})")
    lines.append(f"Data Volume: {rec['data_volume']}")
    lines.append(f"Recommended Size: {rec['recommended_size']}")
    lines.append(f"Credits/hour: {rec['credits_per_hour']}")
    lines.append(f"Est. daily cost (8hr @ $2/credit): ${rec['estimated_daily_cost_8hr']}")
    lines.append("")
    lines.append("Configuration:")
    for k, v in rec["configuration"].items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("Tips:")
    for tip in rec["tips"]:
        lines.append(f"  - {tip}")
    lines.append("")
    lines.append("SQL:")
    lines.append(rec["sql_create"])
    lines.append("=" * 65)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Snowflake Query Helper - Analyze and optimize Snowflake SQL"
    )
    parser.add_argument("--file", help="Path to SQL file to analyze")
    parser.add_argument("--sql", help="SQL text to analyze")
    parser.add_argument("--action", required=True,
                        choices=["analyze", "optimize", "warehouse-sizing"],
                        help="Action to perform")
    parser.add_argument("--workload",
                        choices=list(WORKLOAD_PROFILES.keys()),
                        help="Workload type (for warehouse-sizing)")
    parser.add_argument("--data-volume", default="100GB",
                        help="Data volume (e.g., 500GB, 2TB) for warehouse-sizing")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format")

    args = parser.parse_args()

    if args.action == "warehouse-sizing":
        workload = args.workload or "ad-hoc"
        rec = recommend_warehouse(workload, args.data_volume)
        if args.format == "json":
            print(json.dumps(rec, indent=2))
        else:
            print(format_human_warehouse(rec))
        return

    # analyze or optimize
    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        sql_text = path.read_text(encoding="utf-8", errors="ignore")
    elif args.sql:
        sql_text = args.sql
    else:
        print("Error: --file or --sql required for analyze/optimize", file=sys.stderr)
        sys.exit(1)

    report = analyze_file(sql_text)

    if args.format == "json":
        data = {
            "total_queries": report.total_queries,
            "total_issues": report.total_issues,
            "issues_by_severity": report.issues_by_severity,
            "queries": [
                {
                    "index": q.query_index,
                    "complexity_score": q.complexity_score,
                    "estimated_warehouse_size": q.estimated_warehouse_size,
                    "issues": [asdict(i) for i in q.issues],
                }
                for q in report.queries
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(format_human_analysis(report))

    sys.exit(1 if report.issues_by_severity.get("critical", 0) > 0 else 0)


if __name__ == "__main__":
    main()
