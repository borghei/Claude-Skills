#!/usr/bin/env python3
"""
pairwise_ranking.py — rank variants from pairwise win/loss records.

Reads a JSON file of head-to-head match outcomes between variants (e.g. model
A vs model B, judged by an LLM-as-judge or a human), then computes:
  * a win-rate matrix (how often each variant beats each other)
  * Elo ratings (sequential update, order-sensitive)
  * Bradley-Terry strengths (iterative MM fit, order-independent MLE)
  * a final ranking table

This tool does NOT call any model. It only aggregates outcomes you provide.
Ties count as half a win to each side.

Input JSON shape:
{
  "variants": ["model-a", "model-b", "model-c"],   # optional; inferred if absent
  "matches": [
    {"a": "model-a", "b": "model-b", "winner": "model-a"},
    {"a": "model-a", "b": "model-b", "winner": "tie"},
    {"a": "model-b", "b": "model-c", "winner": "model-c"}
  ]
}

"winner" must be one of the two variant names, or "tie"/"draw".
"""
import argparse
import json
import math
import sys
from itertools import combinations


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _collect(data):
    matches = data["matches"]
    variants = data.get("variants")
    if not variants:
        seen = []
        for m in matches:
            for k in (m["a"], m["b"]):
                if k not in seen:
                    seen.append(k)
        variants = seen
    return variants, matches


def win_matrix(variants, matches):
    """wins[i][j] = number of (half-)wins of i over j."""
    idx = {v: k for k, v in enumerate(variants)}
    n = len(variants)
    wins = [[0.0] * n for _ in range(n)]
    games = [[0.0] * n for _ in range(n)]
    for m in matches:
        a, b = m["a"], m["b"]
        if a not in idx or b not in idx:
            continue
        i, j = idx[a], idx[b]
        w = str(m.get("winner", "")).lower()
        games[i][j] += 1
        games[j][i] += 1
        if w in ("tie", "draw", "both", ""):
            wins[i][j] += 0.5
            wins[j][i] += 0.5
        elif m["winner"] == a:
            wins[i][j] += 1.0
        elif m["winner"] == b:
            wins[j][i] += 1.0
    return wins, games


def elo(variants, matches, k=32.0, base=1500.0):
    rating = {v: base for v in variants}
    for m in matches:
        a, b = m["a"], m["b"]
        if a not in rating or b not in rating:
            continue
        ea = 1.0 / (1.0 + 10 ** ((rating[b] - rating[a]) / 400.0))
        eb = 1.0 - ea
        w = str(m.get("winner", "")).lower()
        if w in ("tie", "draw", "both", ""):
            sa, sb = 0.5, 0.5
        elif m["winner"] == a:
            sa, sb = 1.0, 0.0
        elif m["winner"] == b:
            sa, sb = 0.0, 1.0
        else:
            sa, sb = 0.5, 0.5
        rating[a] += k * (sa - ea)
        rating[b] += k * (sb - eb)
    return {v: round(r, 1) for v, r in rating.items()}


def bradley_terry(variants, wins, games, iters=200, tol=1e-9):
    """Iterative MM fit for Bradley-Terry strengths, geometric-mean normalized."""
    n = len(variants)
    p = [1.0] * n
    total_wins = [sum(wins[i]) for i in range(n)]
    for _ in range(iters):
        new = [0.0] * n
        for i in range(n):
            denom = 0.0
            for j in range(n):
                if i == j:
                    continue
                nij = games[i][j]
                if nij <= 0:
                    continue
                denom += nij / (p[i] + p[j])
            new[i] = (total_wins[i] / denom) if denom > 0 else p[i]
        # geometric-mean normalize to keep scale stable
        prod = 1.0
        positive = [x for x in new if x > 0]
        if positive:
            log_gm = sum(math.log(x) for x in positive) / len(positive)
            gm = math.exp(log_gm)
            new = [x / gm if gm > 0 else x for x in new]
        if max(abs(new[i] - p[i]) for i in range(n)) < tol:
            p = new
            break
        p = new
    return {variants[i]: round(p[i], 4) for i in range(n)}


def build(data, k, base):
    variants, matches = _collect(data)
    wins, games = win_matrix(variants, matches)
    n = len(variants)

    matrix = {}
    win_rate = {}
    for i, vi in enumerate(variants):
        row = {}
        played = 0.0
        won = 0.0
        for j, vj in enumerate(variants):
            if i == j:
                continue
            g = games[i][j]
            row[vj] = {
                "wins": wins[i][j],
                "games": g,
                "rate": round(wins[i][j] / g, 4) if g > 0 else None,
            }
            played += g
            won += wins[i][j]
        matrix[vi] = row
        win_rate[vi] = round(won / played, 4) if played > 0 else None

    elo_r = elo(variants, matches, k=k, base=base)
    bt = bradley_terry(variants, wins, games)

    ranking = sorted(
        variants,
        key=lambda v: (elo_r[v], bt[v]),
        reverse=True,
    )
    table = [
        {
            "rank": r + 1,
            "variant": v,
            "elo": elo_r[v],
            "bradley_terry": bt[v],
            "overall_win_rate": win_rate[v],
        }
        for r, v in enumerate(ranking)
    ]
    return {
        "variants": variants,
        "n_matches": len(matches),
        "ranking": table,
        "win_rate_matrix": matrix,
    }


def _print_human(result):
    print("== Pairwise Ranking ==")
    print(f"variants : {len(result['variants'])}   matches: {result['n_matches']}")
    print("\nranking (by Elo, then Bradley-Terry):")
    print(f"    {'#':<3}{'variant':<18}{'elo':>8}{'bt':>10}{'win%':>9}")
    for row in result["ranking"]:
        wr = "n/a" if row["overall_win_rate"] is None else f"{row['overall_win_rate']*100:.1f}"
        print(f"    {row['rank']:<3}{row['variant']:<18}{row['elo']:>8}{row['bradley_terry']:>10}{wr:>9}")
    print("\nwin-rate matrix (row beats column):")
    variants = result["variants"]
    header = "".join(f"{v[:10]:>12}" for v in variants)
    print(f"    {'':<14}{header}")
    for vi in variants:
        cells = ""
        for vj in variants:
            if vi == vj:
                cells += f"{'-':>12}"
            else:
                rate = result["win_rate_matrix"][vi][vj]["rate"]
                cells += f"{('n/a' if rate is None else f'{rate:.2f}'):>12}"
        print(f"    {vi[:14]:<14}{cells}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Rank variants from pairwise win/loss records.")
    p.add_argument("--data", required=True, help="path to pairwise matches JSON")
    p.add_argument("--k", type=float, default=32.0, help="Elo K-factor (default 32)")
    p.add_argument("--base", type=float, default=1500.0, help="Elo base rating (default 1500)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of human-readable")
    args = p.parse_args(argv)

    try:
        data = _load(args.data)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: could not read --data: {exc}", file=sys.stderr)
        return 2

    if "matches" not in data:
        print("error: input JSON must contain 'matches'", file=sys.stderr)
        return 2

    result = build(data, k=args.k, base=args.base)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
