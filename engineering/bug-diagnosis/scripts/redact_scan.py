#!/usr/bin/env python3
"""Find and redact secrets in logs, traces and captured artifacts before sharing.

Scans text files for credentials (private keys, cloud access keys, code-host
and chat tokens, JWTs, auth and cookie headers, credentials embedded in URLs,
secret-looking assignments, high-entropy blobs) and optionally personal data.
Findings are printed with a masked preview, never the full value. With
--write-redacted the tool writes a redacted copy next to each input file.

Usage:
  python3 redact_scan.py --paths debug.log
  python3 redact_scan.py --paths logs/ --pii --write-redacted --format json

Exit codes: 0 nothing found, 1 secrets or personal data found, 2 read error.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

# (kind, severity, compiled pattern, group holding the secret value)
RULES: List[Tuple[str, str, "re.Pattern[str]", int]] = [
    ("private-key-block", "high", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), 0),
    ("cloud-access-key-id", "high", re.compile(r"\b((?:AKIA|ASIA)[0-9A-Z]{16})\b"), 1),
    ("code-host-token", "high", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b"), 1),
    ("chat-token", "high", re.compile(r"\b(xox[abprs]-[A-Za-z0-9-]{10,})"), 1),
    ("payment-key", "high", re.compile(r"\b([rs]k_(?:live|test)_[A-Za-z0-9]{10,})\b"), 1),
    ("jwt", "high", re.compile(r"\b(eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{6,})"), 1),
    ("auth-header", "high",
     re.compile(r"(?i)\b(?:proxy-)?authorization\s*:\s*(?:bearer|basic|token|digest)\s+([^\s,;]+)"), 1),
    ("cookie-header", "medium", re.compile(r"(?i)\b(?:set-)?cookie\s*:\s*([^\r\n]+)"), 1),
    ("url-credentials", "high", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s:/@]+:([^\s@/]+)@"), 1),
    ("secret-assignment", "medium",
     re.compile(r"(?i)\b(?:pass(?:word|wd)?|pwd|secret|client[_-]?secret|api[_-]?key|access[_-]?key|"
                r"private[_-]?key|token|session[_-]?id)\b[\"']?\s*[:=]\s*[\"']?([^\s\"',;&}]{6,})"), 1),
]
PII_RULES: List[Tuple[str, str, "re.Pattern[str]", int]] = [
    ("email", "low", re.compile(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"), 1),
    ("ipv4", "low", re.compile(r"\b((?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})\b"), 1),
]
BLOB_RE = re.compile(r"(?<![A-Za-z0-9+/_-])([A-Za-z0-9+/_-]{32,}={0,2})")
SAFE_VALUES = {"<redacted>", "null", "none", "true", "false", "undefined", "******"}


def entropy(text: str) -> float:
    """Return the Shannon entropy of a string in bits per character."""
    if not text:
        return 0.0
    counts: Dict[str, int] = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    return -sum(c / len(text) * math.log2(c / len(text)) for c in counts.values())


def mask(value: str) -> str:
    """Return a preview that never reveals more than four characters."""
    return (value[:4] + "***") if len(value) > 8 else "***"


def scan_line(line: str, rules: Iterable[Tuple[str, str, "re.Pattern[str]", int]],
              min_entropy: float) -> List[Tuple[str, str, int, int]]:
    """Return (kind, severity, start, end) spans for secrets on one line."""
    spans: List[Tuple[str, str, int, int]] = []
    for kind, sev, pattern, group in rules:
        for m in pattern.finditer(line):
            value = m.group(group)
            if value.strip("\"'").lower() in SAFE_VALUES or value.startswith("<REDACTED"):
                continue
            spans.append((kind, sev, m.start(group), m.end(group)))
    for m in BLOB_RE.finditer(line):
        value = m.group(1)
        covered = any(s <= m.start(1) < e for _, _, s, e in spans)
        if not covered and entropy(value) >= min_entropy and not value.isalpha():
            spans.append(("high-entropy-blob", "medium", m.start(1), m.end(1)))
    rank = {"high": 0, "medium": 1, "low": 2}
    kept: List[Tuple[str, str, int, int]] = []
    for span in sorted(spans, key=lambda s: (rank[s[1]], s[2], -s[3])):
        if all(span[3] <= k[2] or span[2] >= k[3] for k in kept):
            kept.append(span)
    return sorted(kept, key=lambda s: s[2])


def redact_line(line: str, spans: List[Tuple[str, str, int, int]]) -> str:
    """Replace each secret span with a typed placeholder."""
    for kind, _, start, end in sorted(spans, key=lambda s: -s[2]):
        line = line[:start] + f"<REDACTED:{kind}>" + line[end:]
    return line


def collect(paths: List[str]) -> List[Path]:
    """Expand files and directories into a sorted list of text files."""
    files: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.is_file() and ".redacted" not in f.name)
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(raw)
    return files


def scan(files: List[Path], pii: bool, min_entropy: float, write: bool) -> Dict[str, object]:
    """Scan files, optionally write redacted copies, and build the report."""
    rules = RULES + (PII_RULES if pii else [])
    findings: List[Dict[str, object]] = []
    written: List[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise OSError(f"{path}: {exc}") from exc
        out_lines = []
        in_key_block = False
        for no, line in enumerate(text.splitlines(), 1):
            if in_key_block:
                out_lines.append("<REDACTED:private-key-body>")
                in_key_block = "PRIVATE KEY-----" not in line or "BEGIN" in line
                continue
            spans = scan_line(line, rules, min_entropy)
            for kind, sev, s, e in spans:
                findings.append({"file": str(path), "line": no, "kind": kind,
                                 "severity": sev, "preview": mask(line[s:e])})
                if kind == "private-key-block":
                    in_key_block = True
            out_lines.append(redact_line(line, spans) if spans else line)
        if write:
            target = path.with_name(path.stem + ".redacted" + path.suffix)
            target.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
            written.append(str(target))
    by_sev = {s: sum(f["severity"] == s for f in findings) for s in ("high", "medium", "low")}
    return {"files_scanned": len(files), "findings": findings, "by_severity": by_sev,
            "redacted_copies": written, "verdict": "UNSAFE TO SHARE" if findings else "CLEAN"}


def output(report: Dict[str, object], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    sev = report["by_severity"]
    print(f"Scanned {report['files_scanned']} file(s): {report['verdict']}")
    print(f"  high {sev['high']}  medium {sev['medium']}  low {sev['low']}")
    for f in report["findings"]:
        print(f"  [{f['severity'].upper():6}] {f['file']}:{f['line']}  {f['kind']:<20} {f['preview']}")
    for path in report["redacted_copies"]:
        print(f"Redacted copy written: {path}")
    if report["findings"] and not report["redacted_copies"]:
        print("Re-run with --write-redacted, review the copy by eye, and share only that.")


def main() -> None:
    """Parse arguments, scan inputs, and exit with the gate result."""
    p = argparse.ArgumentParser(description="Find and redact secrets in logs before sharing them.")
    p.add_argument("--paths", nargs="+", required=True, help="files or directories to scan")
    p.add_argument("--pii", action="store_true", help="also flag email addresses and IPv4 addresses")
    p.add_argument("--min-entropy", type=float, default=4.3,
                   help="bits/char above which a 32+ char blob is flagged (default 4.3)")
    p.add_argument("--write-redacted", action="store_true", help="write <name>.redacted<ext> beside each file")
    p.add_argument("--format", choices=("text", "json"), default="text", help="output format (default text)")
    args = p.parse_args()
    try:
        report = scan(collect(args.paths), args.pii, args.min_entropy, args.write_redacted)
    except (OSError, FileNotFoundError) as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(1 if report["findings"] else 0)


if __name__ == "__main__":
    main()
