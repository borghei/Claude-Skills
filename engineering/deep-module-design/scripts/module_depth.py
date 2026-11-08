#!/usr/bin/env python3
"""Measure module depth and rank deepening opportunities in a Python/JS/TS codebase.

For each module (file) it counts the public interface (entry points plus their
parameters), the implementation size (code lines), pass-through functions that
only forward their arguments to another call, overlong parameter lists, and
imports of another module's private names. It classifies modules as deep,
shallow, pass-through layers or leaky, then ranks the opportunities, optionally
weighted by change frequency.

Usage:
  python3 module_depth.py --path src/
  python3 module_depth.py --input codebase.json --format json

Exit codes: 0 no shallow/pass-through/leaky module, 1 findings, 2 input error.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

EXTS = {".py", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", "coverage"}
TEST_RE = re.compile(r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*\.py$|_test\.py$|\.(test|spec)\.[jt]sx?$")
JS_FUNC = re.compile(r"export\s+(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w*)\s*\(([^)]*)\)")
JS_ARROW = re.compile(r"export\s+const\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s+)?\(([^)]*)\)\s*(?::[^=]+)?=>")
JS_CLASS = re.compile(r"export\s+(?:default\s+)?(?:abstract\s+)?class\s+(\w+)")
JS_METHOD = re.compile(r"^\s+(?:public\s+|static\s+|async\s+)*(?!constructor\b|if\b|for\b|while\b|switch\b|return\b)"
                       r"([A-Za-z]\w*)\s*\(([^)]*)\)\s*(?::[^{]+)?\{", re.MULTILINE)
JS_NAMED = re.compile(r"export\s*\{([^}]*)\}")
JS_PASS = re.compile(r"^\s*(?:return\s+)?(?:await\s+)?[\w.$]+\(([^()]*)\)\s*;?\s*$")
JS_PRIVATE_IMPORT = re.compile(r"import\s*\{([^}]*)\}\s*from")


def split_params(raw: str) -> List[str]:
    """Return parameter names from a JS/TS parameter list, ignoring types and defaults."""
    names = []
    for part in raw.split(","):
        name = re.split(r"[:=?]", part.strip().lstrip("."))[0].strip()
        if name:
            names.append(name)
    return names


def code_lines(src: str, lang: str) -> int:
    """Count non-blank, non-comment lines."""
    marks = ("#",) if lang == "py" else ("//", "/*", "*", "*/")
    return sum(1 for ln in src.splitlines() if ln.strip() and not ln.strip().startswith(marks))


def py_is_pass_through(fn: ast.AST) -> bool:
    """True when a function body is one call that forwards the function's own parameters."""
    body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    if len(body) != 1 or not isinstance(body[0], (ast.Return, ast.Expr)):
        return False
    call = body[0].value
    call = call.value if isinstance(call, ast.Await) else call
    if not isinstance(call, ast.Call):
        return False
    params = {a.arg for a in fn.args.args + fn.args.kwonlyargs} - {"self", "cls"}
    passed = {a.id for a in call.args if isinstance(a, ast.Name)}
    passed |= {k.value.id for k in call.keywords if isinstance(k.value, ast.Name)}
    simple = all(isinstance(a, (ast.Name, ast.Starred)) for a in call.args)
    return simple and passed == params


def analyse_py(src: str) -> Dict[str, Any]:
    """Extract interface, pass-through and leak data from Python source."""
    tree = ast.parse(src)
    exported = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                exported = {e.value for e in node.value.elts if isinstance(e, ast.Constant)}
    entries: List[Tuple[str, int]] = []
    funcs, passes = 0, []
    fn_types = (ast.FunctionDef, ast.AsyncFunctionDef)

    def public(name: str) -> bool:
        return (name in exported) if exported is not None else not name.startswith("_")

    for node in tree.body:
        if isinstance(node, fn_types):
            funcs += 1
            if public(node.name):
                entries.append((node.name, len(node.args.args) + len(node.args.kwonlyargs)))
            if py_is_pass_through(node):
                passes.append(node.name)
        elif isinstance(node, ast.ClassDef) and public(node.name):
            entries.append((node.name, 0))
            for item in node.body:
                if isinstance(item, fn_types):
                    funcs += 1
                    n = len([a for a in item.args.args if a.arg not in ("self", "cls")]) + len(item.args.kwonlyargs)
                    if not item.name.startswith("_") or item.name == "__init__":
                        entries.append((f"{node.name}.{item.name}", n))
                    if py_is_pass_through(item) and item.name != "__init__":
                        passes.append(f"{node.name}.{item.name}")
    private_imports = [f"{n.module}.{a.name}" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                       for a in n.names if a.name.startswith("_") and not a.name.startswith("__")]
    return {"entries": entries, "functions": funcs, "pass_through": passes, "private_imports": private_imports}


def js_body(src: str, start: int) -> str:
    """Return the text between the brace at or after start and its matching close."""
    i = src.find("{", start)
    if i < 0:
        return ""
    depth = 0
    for j in range(i, len(src)):
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        if depth == 0:
            return src[i + 1:j]
    return src[i + 1:]


def js_pass(body: str, params: List[str]) -> bool:
    """True when a JS/TS body is one call forwarding exactly the given parameters."""
    lines = [ln for ln in body.strip().splitlines() if ln.strip() and not ln.strip().startswith("//")]
    if len(lines) != 1:
        return False
    m = JS_PASS.match(lines[0])
    return bool(m) and set(split_params(m.group(1))) == set(params)


def analyse_js(src: str) -> Dict[str, Any]:
    """Extract interface, pass-through and leak data from JS/TS source by pattern matching."""
    entries: List[Tuple[str, int]] = []
    passes: List[str] = []
    funcs = len(re.findall(r"\bfunction\b|=>", src))
    for m in JS_FUNC.finditer(src):
        params = split_params(m.group(2))
        entries.append((m.group(1) or "default", len(params)))
        if js_pass(js_body(src, m.end()), params):
            passes.append(m.group(1) or "default")
    for m in JS_ARROW.finditer(src):
        params = split_params(m.group(2))
        entries.append((m.group(1), len(params)))
        rest = src[m.end():].lstrip()
        body = js_body(src, m.end()) if rest.startswith("{") else rest.split("\n", 1)[0]
        if js_pass(body, params):
            passes.append(m.group(1))
    for m in JS_CLASS.finditer(src):
        entries.append((m.group(1), 0))
        body = js_body(src, m.end())
        for mm in JS_METHOD.finditer(body):
            if re.search(r"\b(private|protected)\b", body[max(0, mm.start() - 30):mm.start() + 12]):
                continue
            params = split_params(mm.group(2))
            entries.append((f"{m.group(1)}.{mm.group(1)}", len(params)))
            if js_pass(js_body(body, mm.end() - 1), params):
                passes.append(f"{m.group(1)}.{mm.group(1)}")
    for m in JS_NAMED.finditer(src):
        entries += [(n.split(" as ")[-1].strip(), 0) for n in m.group(1).split(",") if n.strip()]
    private_imports = [n.strip() for m in JS_PRIVATE_IMPORT.finditer(src) for n in m.group(1).split(",")
                       if n.strip().startswith("_")]
    return {"entries": entries, "functions": max(funcs, len(passes)), "pass_through": passes,
            "private_imports": private_imports}


def assess(name: str, src: str, args: argparse.Namespace, churn: Dict[str, int]) -> Dict[str, Any]:
    """Score one module and classify it."""
    lang = "py" if name.endswith(".py") else "js"
    data = analyse_py(src) if lang == "py" else analyse_js(src)
    cost = sum(1 + p for _, p in data["entries"])
    impl = code_lines(src, lang)
    depth = round(impl / cost, 1) if cost else float(impl)
    pt_ratio = round(len(data["pass_through"]) / data["functions"], 2) if data["functions"] else 0.0
    long_params = [f"{e} ({p})" for e, p in data["entries"] if p > args.max_params]
    labels = []
    if pt_ratio >= args.pass_ratio and len(data["pass_through"]) >= 2:
        labels.append("pass-through layer")
    if len(data["entries"]) >= args.min_entries and depth < args.shallow_below:
        labels.append("shallow")
    if long_params or data["private_imports"]:
        labels.append("leaky")
    if not labels:
        labels.append("deep" if depth >= args.deep_above else "ok")
    score = 0.0
    if labels[0] not in ("deep", "ok"):
        score = max(0.0, (args.shallow_below - depth) / args.shallow_below) * 40 + pt_ratio * 40
        score += 8 * (len(long_params) + len(data["private_imports"])) + 2 * min(len(data["entries"]), 10)
        score *= 1 + math.log2(1 + churn.get(name, 0)) / 4
    return {"module": name, "entries": len(data["entries"]), "interface_cost": cost, "impl_lines": impl,
            "depth": depth, "pass_through": data["pass_through"], "pass_through_ratio": pt_ratio,
            "long_param_lists": long_params, "private_imports": data["private_imports"],
            "changes": churn.get(name, 0), "labels": labels, "opportunity": round(score, 1)}


def load_sources(args: argparse.Namespace) -> Tuple[Dict[str, str], Dict[str, int]]:
    """Load sources from a JSON bundle or a filesystem path."""
    churn: Dict[str, int] = {}
    if args.input:
        bundle = json.loads(Path(args.input).read_text(encoding="utf-8"))
        files, churn = bundle.get("files", {}), bundle.get("churn", {})
    else:
        root = Path(args.path)
        paths = [root] if root.is_file() else [p for p in sorted(root.rglob("*")) if p.is_file()
                                               and p.suffix in EXTS and not SKIP_DIRS & set(p.parts)]
        base = root.parent if root.is_file() else root
        files = {str(p.relative_to(base)): p.read_text(encoding="utf-8", errors="replace") for p in paths}
    if args.churn:
        churn = json.loads(Path(args.churn).read_text(encoding="utf-8"))
    if not args.include_tests:
        files = {k: v for k, v in files.items() if not TEST_RE.search(k)}
    return files, churn


def output(rows: List[Dict[str, Any]], fmt: str) -> None:
    """Print ranked findings as text or JSON."""
    flagged = [r for r in rows if r["opportunity"] > 0]
    if fmt == "json":
        print(json.dumps({"modules": rows, "flagged": len(flagged)}, indent=2))
        return
    print(f"{'module':<34}{'entries':>8}{'cost':>6}{'impl':>6}{'depth':>7}{'pass%':>7}  labels")
    for r in rows:
        print(f"{r['module'][:33]:<34}{r['entries']:>8}{r['interface_cost']:>6}{r['impl_lines']:>6}"
              f"{r['depth']:>7}{int(r['pass_through_ratio'] * 100):>6}%  {', '.join(r['labels'])}")
    print(f"\nDeepening opportunities ({len(flagged)}), highest first:")
    for i, r in enumerate(flagged, 1):
        why = [f"forwards: {', '.join(r['pass_through'])}" if r["pass_through"] else "",
               f"long params: {', '.join(r['long_param_lists'])}" if r["long_param_lists"] else "",
               f"private imports: {', '.join(r['private_imports'])}" if r["private_imports"] else "",
               f"changed {r['changes']}x" if r["changes"] else ""]
        print(f"  {i}. {r['module']}  score {r['opportunity']}  [{', '.join(r['labels'])}]")
        print(f"     {'; '.join(w for w in why if w) or 'interface nearly as large as the body'}")


def main() -> None:
    """Parse arguments, analyse modules, and exit with the gate result."""
    p = argparse.ArgumentParser(description="Rank shallow, pass-through and leaky modules.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--path", help="file or directory to scan (.py .js .ts .tsx .jsx .mjs .cjs)")
    src.add_argument("--input", help='JSON bundle: {"files": {name: source}, "churn": {name: changes}}')
    p.add_argument("--churn", help="JSON map of module -> commit count, weights the ranking")
    p.add_argument("--shallow-below", type=float, default=4.0, help="depth under which a module is shallow")
    p.add_argument("--deep-above", type=float, default=8.0, help="depth at or over which a module is deep")
    p.add_argument("--min-entries", type=int, default=3, help="entry points before shallowness counts")
    p.add_argument("--pass-ratio", type=float, default=0.5, help="pass-through share that marks a layer")
    p.add_argument("--max-params", type=int, default=5, help="parameter count that marks a leaky entry point")
    p.add_argument("--include-tests", action="store_true", help="include test files")
    p.add_argument("--format", choices=("text", "json"), default="text", help="output format (default text)")
    args = p.parse_args()
    try:
        files, churn = load_sources(args)
    except (OSError, ValueError) as exc:
        print(f"error: cannot analyse input: {exc}", file=sys.stderr)
        sys.exit(2)
    rows = []
    for name, text in sorted(files.items()):
        try:
            rows.append(assess(name, text, args, churn))
        except SyntaxError as exc:
            print(f"warning: skipped {name}: syntax error at line {exc.lineno}", file=sys.stderr)
    rows.sort(key=lambda r: (-r["opportunity"], r["module"]))
    output(rows, args.format)
    sys.exit(1 if any(r["opportunity"] > 0 for r in rows) else 0)


if __name__ == "__main__":
    main()
