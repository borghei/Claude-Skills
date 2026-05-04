#!/usr/bin/env python3
"""
PDF Auditor — audit a PDF file for metadata, page count, encryption, JavaScript,
embedded files, and version. Standard library only.

Usage:
    python pdf_auditor.py document.pdf
    python pdf_auditor.py document.pdf --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


VERSION_RE = re.compile(rb"%PDF-(\d\.\d)")
PAGE_OBJ_RE = re.compile(rb"/Type\s*/Page(?![s])")
ENCRYPT_RE = re.compile(rb"/Encrypt[\s\d]")
JS_RE = re.compile(rb"/(JS|JavaScript)\b")
ACTION_RE = re.compile(rb"/AA\b")
EMBEDDED_FILES_RE = re.compile(rb"/EmbeddedFiles\b")
NAMES_DICT_RE = re.compile(rb"/Names\b")
INFO_RE = re.compile(rb"/Info\s+(\d+)\s+(\d+)\s+R")
XMP_RE = re.compile(rb"<x:xmpmeta[^>]*>(.+?)</x:xmpmeta>", re.DOTALL)


def decode_pdf_string(raw):
    """Decode a PDF string literal to text. Handles parens, hex, and PDFDocEncoding."""
    if not raw:
        return ""
    raw = raw.strip()
    if raw.startswith(b"<") and raw.endswith(b">"):
        # Hex string — sometimes UTF-16BE with BOM
        hex_str = raw[1:-1].replace(b" ", b"").replace(b"\n", b"")
        try:
            decoded = bytes.fromhex(hex_str.decode("ascii"))
            if decoded.startswith(b"\xfe\xff"):
                return decoded[2:].decode("utf-16-be", errors="replace")
            return decoded.decode("latin-1", errors="replace")
        except Exception:
            return ""
    if raw.startswith(b"(") and raw.endswith(b")"):
        inner = raw[1:-1]
        # Handle UTF-16 BOM in literal strings
        if inner.startswith(b"\xfe\xff"):
            try:
                return inner[2:].decode("utf-16-be", errors="replace")
            except Exception:
                pass
        # Basic escape unescape
        try:
            return inner.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\").decode("latin-1", errors="replace")
        except Exception:
            return ""
    return raw.decode("latin-1", errors="replace")


def extract_info_dict(data):
    """Find /Info object and return its key/value pairs (Title, Author, etc.)."""
    info_match = INFO_RE.search(data)
    if not info_match:
        return {}
    obj_id = info_match.group(1).decode()
    obj_re = re.compile(rf"\b{obj_id}\s+\d+\s+obj\b(.+?)\bendobj\b".encode(), re.DOTALL)
    obj_match = obj_re.search(data)
    if not obj_match:
        return {}
    body = obj_match.group(1)
    fields = {}
    for key in [b"Title", b"Author", b"Subject", b"Keywords", b"Creator", b"Producer", b"CreationDate", b"ModDate"]:
        # Match /Key (...) or /Key <...>
        pat = re.compile(rb"/" + key + rb"\s*(\([^)]*\)|<[^>]+>)")
        m = pat.search(body)
        if m:
            fields[key.decode()] = decode_pdf_string(m.group(1))
    return fields


def extract_xmp(data):
    m = XMP_RE.search(data)
    if not m:
        return {}
    xmp = m.group(1).decode("utf-8", errors="replace")
    # Pull common Dublin Core / XMP fields by tag
    fields = {}
    for tag in ["dc:title", "dc:creator", "dc:description", "xmp:CreatorTool",
                "xmp:CreateDate", "xmp:ModifyDate", "pdf:Producer"]:
        pat = re.compile(rf"<{re.escape(tag)}[^>]*>(.+?)</{re.escape(tag)}>", re.DOTALL)
        m = pat.search(xmp)
        if m:
            inner = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            fields[tag] = inner
    return fields


def audit(path):
    data = Path(path).read_bytes()
    file_size = len(data)
    if not data.startswith(b"%PDF-"):
        raise ValueError("Not a PDF (header missing)")

    version_match = VERSION_RE.search(data[:64])
    version = version_match.group(1).decode() if version_match else "unknown"

    page_count = len(PAGE_OBJ_RE.findall(data))
    encrypted = bool(ENCRYPT_RE.search(data))
    has_js = bool(JS_RE.search(data))
    has_actions = bool(ACTION_RE.search(data))
    has_embedded = bool(EMBEDDED_FILES_RE.search(data)) or bool(
        NAMES_DICT_RE.search(data) and EMBEDDED_FILES_RE.search(data)
    )

    info = extract_info_dict(data)
    xmp = extract_xmp(data)

    return {
        "file": str(path),
        "size_bytes": file_size,
        "size_kb": round(file_size / 1024, 1),
        "pdf_version": version,
        "page_count": page_count,
        "encrypted": encrypted,
        "javascript_present": has_js,
        "additional_actions_present": has_actions,
        "embedded_files_present": has_embedded,
        "info_dictionary": info,
        "xmp_metadata": xmp,
    }


def render_human(result):
    lines = [f"Audit: {result['file']}"]
    lines.append("")
    lines.append(f"  PDF version:   {result['pdf_version']}")
    lines.append(f"  Pages:         {result['page_count']}")
    lines.append(f"  Size:          {result['size_kb']} KB ({result['size_bytes']} bytes)")
    lines.append(f"  Encrypted:     {'YES' if result['encrypted'] else 'no'}")
    lines.append(f"  JavaScript:    {'YES' if result['javascript_present'] else 'no'}")
    lines.append(f"  AA (actions):  {'YES' if result['additional_actions_present'] else 'no'}")
    lines.append(f"  Embedded files:{'YES' if result['embedded_files_present'] else 'no'}")
    lines.append("")
    if result["info_dictionary"]:
        lines.append("Info dictionary:")
        for k, v in result["info_dictionary"].items():
            lines.append(f"  {k:<14} {v}")
    else:
        lines.append("Info dictionary: (none)")
    lines.append("")
    if result["xmp_metadata"]:
        lines.append("XMP metadata:")
        for k, v in result["xmp_metadata"].items():
            lines.append(f"  {k:<22} {v}")
    else:
        lines.append("XMP metadata: (none)")
    lines.append("")
    issues = []
    if result["javascript_present"]:
        issues.append("JavaScript present — review in sandbox")
    if result["additional_actions_present"]:
        issues.append("Additional Actions present — review for auto-execution")
    if result["embedded_files_present"]:
        issues.append("Embedded files — verify expected")
    info = result["info_dictionary"]
    if info.get("Author") and "intern" in info["Author"].lower():
        issues.append("Author metadata appears unscrubbed")
    if info.get("Title") and any(p in info["Title"].lower() for p in ["draft", "wip", "internal", "tbd"]):
        issues.append("Title metadata looks like a working title")
    if issues:
        lines.append("Pre-handoff / security issues:")
        for issue in issues:
            lines.append(f"  • {issue}")
    else:
        lines.append("Pre-handoff / security issues: none detected by automated scan.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit a .pdf file (stdlib only).")
    parser.add_argument("pdf", help="Path to .pdf file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.pdf)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        result = audit(path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
