"""Benign test fixture: align the columns of a markdown table read from a file."""
import argparse
import sys
from pathlib import Path


def align(lines):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines if line.strip()]
    widths = [max(len(r[i]) for r in rows if i < len(r)) for i in range(max(map(len, rows)))]
    return ["| " + " | ".join(c.ljust(w) for c, w in zip(r, widths)) + " |" for r in rows]


def main():
    parser = argparse.ArgumentParser(description="Align a markdown table")
    parser.add_argument("table")
    args = parser.parse_args()
    path = Path(args.table)
    if not path.is_file():
        print(f"error: not found: {path}", file=sys.stderr)
        sys.exit(2)
    print("\n".join(align(path.read_text(encoding="utf-8").splitlines())))


if __name__ == "__main__":
    main()
