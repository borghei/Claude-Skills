#!/usr/bin/env python3
"""Generate deployment artifacts for a model service from a JSON spec.

Writes a Dockerfile (slim base, non-root user, HEALTHCHECK), Kubernetes
manifests (Deployment + Service + HorizontalPodAutoscaler with probes and
resource requests/limits), a stdlib serve.py health/readiness stub and a
requirements.txt stub into --output, then reports checks on the spec.

Usage:
    python model_deployment_pipeline.py --input spec.json --output deploy/
    python model_deployment_pipeline.py --example > spec.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

EXAMPLE_SPEC: Dict[str, Any] = {
    "name": "churn-classifier",
    "framework": "sklearn",
    "model_file": "model.joblib",
    "image": "registry.example.com/ml/churn-classifier:1.4.0",
    "port": 8080,
    "replicas": {"min": 2, "max": 6},
    "resources": {"cpu_request": "500m", "cpu_limit": "1",
                  "memory_request": "1Gi", "memory_limit": "2Gi"},
    "health": {"liveness_path": "/health", "readiness_path": "/ready"},
    "env": {"LOG_LEVEL": "info", "FEATURE_STORE_TOKEN": ""},
    "gpu": False,
    "target_cpu_utilization": 70,
}
PACKAGES = {"sklearn": ["scikit-learn", "joblib"], "pytorch": ["torch"],
            "tensorflow": ["tensorflow"], "onnx": ["onnxruntime"],
            "xgboost": ["xgboost"], "lightgbm": ["lightgbm"], "custom": []}
CPU_BASE = "python:3.11-slim"
GPU_BASE = "nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04"
SECRET_WORDS = {"PASSWORD", "PASSWD", "PWD", "SECRET", "TOKEN", "APIKEY", "CREDENTIAL", "CREDENTIALS"}
SECRET_PAIRS = {"API_KEY", "ACCESS_KEY", "PRIVATE_KEY", "SECRET_KEY", "SIGNING_KEY", "ENCRYPTION_KEY"}
NAME_RE = re.compile(r"[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?")
FILE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}(/[A-Za-z0-9][A-Za-z0-9._-]{0,127}){0,7}")
PATH_RE = re.compile(r"/([A-Za-z0-9._~-]+(/[A-Za-z0-9._~-]+)*)?")
IMAGE_RE = re.compile(r"[a-z0-9]+([._-][a-z0-9]+)*(:[0-9]{1,5})?(/[a-z0-9]+([._-][a-z0-9]+)*)*"
                      r"(:[A-Za-z0-9_][A-Za-z0-9_.-]{0,127})?(@sha256:[a-f0-9]{64})?")
QTY_RE = re.compile(r"[0-9]+(\.[0-9]+)?(m|k|M|G|T|Ki|Mi|Gi|Ti)?")
ENV_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
UID = 10001
PLAIN = re.compile(r"[A-Za-z_/][A-Za-z0-9_./-]*")

SERVE_STUB = '''"""Health/readiness stub for {name}. Replace load_model() and predict()."""
import json, os, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_PATH = os.environ.get("MODEL_PATH", "/app/model/{model_file}")
STATE = {{"model": None, "error": None}}

def load_model():
    """Load the model once at startup. Swap in the framework loader ({framework})."""
    try:
        with open(MODEL_PATH, "rb") as fh:
            STATE["model"] = fh.read()  # TODO: real deserialization
    except OSError as exc:
        STATE["error"] = str(exc)

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "{liveness}":
            self._send(200, {{"status": "alive"}})
        elif self.path == "{readiness}":
            ready = STATE["model"] is not None
            self._send(200 if ready else 503, {{"ready": ready, "error": STATE["error"]}})
        else:
            self._send(404, {{"error": "not found"}})

    def do_POST(self):
        if self.path != "/predict":
            return self._send(404, {{"error": "not found"}})
        self._send(501, {{"error": "predict() not implemented"}})

if __name__ == "__main__":
    threading.Thread(target=load_model, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "{port}"))), Handler).serve_forever()
'''


def scalar(v: Any) -> str:
    """Render a YAML scalar; strings are plain when safe, else JSON-quoted (valid YAML)."""
    if isinstance(v, str):
        safe = PLAIN.fullmatch(v) and v.lower() not in ("true", "false", "yes", "no", "on", "off", "null", "y", "n")
        return v if safe else json.dumps(v)
    return json.dumps(v) if isinstance(v, bool) or v is None else str(v)


def to_yaml(obj: Any, ind: int = 0) -> List[str]:
    """Emit block-style YAML for nested dicts and lists."""
    pad = "  " * ind
    lines: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:")
                lines.extend(to_yaml(v, ind + 1))
            else:
                empty = "{}" if isinstance(v, dict) else "[]"
                lines.append(f"{pad}{k}: {empty if isinstance(v, (dict, list)) else scalar(v)}")
    else:
        for item in obj:
            if isinstance(item, (dict, list)):
                sub = to_yaml(item, ind + 1)
                lines.append(f"{pad}- {sub[0].lstrip()}")
                lines.extend(sub[1:])
            else:
                lines.append(f"{pad}- {scalar(item)}")
    return lines


def is_secret(key: str) -> bool:
    """True when an env name has a secret-like segment (DB_PASSWORD, API_KEY), not a substring (TOKENIZER)."""
    parts = [x for x in re.split(r"[_-]", key.upper()) if x]
    pairs = {f"{a}_{b}" for a, b in zip(parts, parts[1:])}
    return bool(set(parts) & SECRET_WORDS or pairs & SECRET_PAIRS)


def need(ok: Any, msg: str) -> None:
    """Raise ValueError(msg) unless ok."""
    if not ok:
        raise ValueError(msg)


def as_int(v: Any, field: str, lo: int, hi: int) -> int:
    """Validate an integer field within [lo, hi]."""
    need(isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi,
         f"{field} must be an integer between {lo} and {hi}, got {v!r}")
    return v


def normalize(spec: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """Validate the spec, fill defaults and collect checks (severity, message)."""
    checks: List[Dict[str, str]] = []
    add = lambda sev, msg: checks.append({"severity": sev, "message": msg})
    for key in ("name", "model_file"):
        need(spec.get(key), f"spec is missing required field '{key}'")
    name = spec["name"]
    need(isinstance(name, str) and NAME_RE.fullmatch(name),
         f"name {name!r} is not a valid Kubernetes name (lowercase letters, digits, '-', max 63)")
    model_file = spec["model_file"]
    need(isinstance(model_file, str) and FILE_RE.fullmatch(model_file),
         f"model_file {model_file!r} must be a relative path of letters, digits, '.', '_', '-' and '/'")
    fw = spec.get("framework", "custom")
    need(isinstance(fw, str), "framework must be a string")
    fw = fw.lower()
    if fw not in PACKAGES:
        add("warn", f"unknown framework '{fw}', treated as custom (known: {', '.join(PACKAGES)})")
        fw = "custom"
    gpu = spec.get("gpu", False)
    need(isinstance(gpu, bool), "gpu must be true or false")
    image = spec.get("image") or f"{name}:latest"
    need(isinstance(image, str) and IMAGE_RE.fullmatch(image), f"image {image!r} is not a valid image reference")
    tag = image.rsplit("/", 1)[-1].partition(":")[2] if "@" not in image else "digest"
    if tag in ("", "latest"):
        add("warn", f"image '{image}' uses an implicit or 'latest' tag; pin a version or digest")
    base = spec.get("base_image") or (GPU_BASE if gpu else CPU_BASE)
    need(isinstance(base, str) and IMAGE_RE.fullmatch(base), f"base_image {base!r} is not a valid image reference")
    if "@" not in base and (base.endswith(":latest") or ":" not in base.rsplit("/", 1)[-1]):
        add("warn", f"base image '{base}' is not pinned to a tag")
    if spec.get("run_as_root"):
        add("warn", "run_as_root is set; generated files still use a non-root user (uid 10001)")
    port = as_int(spec.get("port", 8080), "port", 1, 65535)
    if port < 1024:
        add("warn", f"port {port} is privileged; a non-root container cannot bind it, use >= 1024")
    rep = spec.get("replicas", {"min": 2, "max": 4})
    need(isinstance(rep, (int, dict)) and not isinstance(rep, bool), "replicas must be an integer or {\"min\", \"max\"}")
    rmin = as_int(rep if isinstance(rep, int) else rep.get("min", 2), "replicas.min", 1, 1000)
    rmax = as_int(rep if isinstance(rep, int) else rep.get("max", 4), "replicas.max", rmin, 1000)
    if rmin < 2:
        add("warn", "min replicas < 2: a single pod gives no availability during rollouts or node loss")
    res = spec.get("resources") or {}
    need(isinstance(res, dict), "resources must be an object of cpu/memory requests and limits")
    for k in ("cpu_request", "memory_request", "cpu_limit", "memory_limit"):
        if not res.get(k):
            add("warn", f"resources.{k} missing; pods without it risk eviction or noisy-neighbour starvation")
        else:
            need(QTY_RE.fullmatch(str(res[k])) and not isinstance(res[k], bool),
                 f"resources.{k} {res[k]!r} is not a Kubernetes quantity such as 500m, 2 or 1Gi")
    if not res.get("cpu_request"):
        add("warn", "HPA scales on CPU utilization, which needs resources.cpu_request")
    health = spec.get("health") or {}
    need(isinstance(health, dict), "health must be an object with liveness_path and readiness_path")
    live, ready = health.get("liveness_path", "/health"), health.get("readiness_path", "/ready")
    for field, val in (("liveness_path", live), ("readiness_path", ready)):
        need(isinstance(val, str) and PATH_RE.fullmatch(val),
             f"health.{field} {val!r} must be a URL path like /health (letters, digits, '.', '_', '-', '~', '/')")
    if live == ready:
        add("info", "liveness and readiness share a path; a slow model load will restart pods")
    env = spec.get("env") or {}
    need(isinstance(env, dict), "env must be an object of NAME: value")
    secrets = []
    for k, v in env.items():
        need(ENV_RE.fullmatch(k), f"env name {k!r} must match [A-Za-z_][A-Za-z0-9_]*")
        need(isinstance(v, (str, int, float, bool)), f"env {k} must have a string or number value")
        if is_secret(k):
            secrets.append(k)
            if v not in ("", None):
                add("warn", f"env {k} had a literal value in the spec; it was dropped, put it in {name}-secrets")
    if secrets:
        add("info", f"treated as secrets (secretKeyRef {name}-secrets): {', '.join(secrets)}")
    if gpu and fw in ("sklearn", "lightgbm"):
        add("info", f"gpu requested for {fw}, which normally serves on CPU")
    norm = {"name": name, "framework": fw, "model_file": model_file, "image": image,
            "base_image": base, "gpu": gpu, "gpu_count": as_int(spec.get("gpu_count", 1), "gpu_count", 1, 16) if gpu else 0,
            "port": port, "min": rmin, "max": rmax, "resources": res, "liveness": live, "readiness": ready,
            "env": env, "secret_env": secrets,
            "target_cpu": as_int(spec.get("target_cpu_utilization", 70), "target_cpu_utilization", 1, 100)}
    return norm, checks


def render_dockerfile(s: Dict[str, Any]) -> str:
    """Return a Dockerfile with a pinned base, non-root user and HEALTHCHECK."""
    py = "python3" if s["gpu"] and s["base_image"] == GPU_BASE else "python"
    install = ("RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip \\\n"
               "    && rm -rf /var/lib/apt/lists/*\n") if py == "python3" else ""
    probe = (f"import urllib.request; urllib.request.urlopen('http://127.0.0.1:{s['port']}"
             f"{s['liveness']}', timeout=2)")
    return (f"# Model service: {s['name']} ({s['framework']})\nFROM {s['base_image']}\n{install}"
            "ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1\nWORKDIR /app\n"
            f"RUN groupadd --system --gid {UID} app && useradd --system --uid {UID} --gid app --no-create-home app\n"
            f"COPY requirements.txt .\nRUN {py} -m pip install --no-cache-dir -r requirements.txt\n"
            f"COPY --chown={UID}:{UID} model/ /app/model/\nCOPY --chown={UID}:{UID} serve.py /app/serve.py\n"
            f"ENV MODEL_PATH=/app/model/{s['model_file']} PORT={s['port']}\nUSER {UID}\nEXPOSE {s['port']}\n"
            f"HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \\\n"
            f"  CMD {py} -c \"{probe}\" || exit 1\nCMD [\"{py}\", \"serve.py\"]\n")


def render_k8s(s: Dict[str, Any]) -> str:
    """Return Deployment, Service and HPA as one multi-document YAML."""
    labels = {"app": s["name"]}
    res = s["resources"]
    requests = {k: res[f"{k}_request"] for k in ("cpu", "memory") if res.get(f"{k}_request")}
    limits = {k: res[f"{k}_limit"] for k in ("cpu", "memory") if res.get(f"{k}_limit")}
    if s["gpu"]:
        limits["nvidia.com/gpu"] = s["gpu_count"]
    env = [{"name": "PORT", "value": str(s["port"])}]
    for k, v in s["env"].items():
        env.append({"name": k, "valueFrom": {"secretKeyRef": {"name": f"{s['name']}-secrets", "key": k}}}
                   if k in s["secret_env"] else {"name": k, "value": json.dumps(v) if isinstance(v, bool) else str(v)})
    probe = lambda path, period, fail: {"httpGet": {"path": path, "port": "http"},
                                        "periodSeconds": period, "timeoutSeconds": 3, "failureThreshold": fail}
    container = {"name": "model", "image": s["image"], "imagePullPolicy": "IfNotPresent",
                 "ports": [{"name": "http", "containerPort": s["port"]}], "env": env,
                 "resources": {"requests": requests, "limits": limits},
                 "startupProbe": probe(s["liveness"], 10, 30),
                 "livenessProbe": probe(s["liveness"], 10, 3),
                 "readinessProbe": probe(s["readiness"], 5, 3),
                 "securityContext": {"allowPrivilegeEscalation": False, "capabilities": {"drop": ["ALL"]}}}
    deployment = {"apiVersion": "apps/v1", "kind": "Deployment",
                  "metadata": {"name": s["name"], "labels": labels},
                  "spec": {"replicas": s["min"], "selector": {"matchLabels": labels},
                           "strategy": {"type": "RollingUpdate",
                                        "rollingUpdate": {"maxSurge": 1, "maxUnavailable": 0}},
                           "template": {"metadata": {"labels": labels}, "spec": {
                               "securityContext": {"runAsNonRoot": True, "runAsUser": UID, "runAsGroup": UID},
                               "containers": [container]}}}}
    service = {"apiVersion": "v1", "kind": "Service", "metadata": {"name": s["name"], "labels": labels},
               "spec": {"type": "ClusterIP", "selector": labels,
                        "ports": [{"name": "http", "port": 80, "targetPort": "http"}]}}
    hpa = {"apiVersion": "autoscaling/v2", "kind": "HorizontalPodAutoscaler",
           "metadata": {"name": s["name"], "labels": labels},
           "spec": {"scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": s["name"]},
                    "minReplicas": s["min"], "maxReplicas": s["max"],
                    "metrics": [{"type": "Resource", "resource": {"name": "cpu", "target": {
                        "type": "Utilization", "averageUtilization": s["target_cpu"]}}}]}}
    return "\n---\n".join("\n".join(to_yaml(d)) for d in (deployment, service, hpa)) + "\n"


def render_requirements(s: Dict[str, Any]) -> str:
    """Return a requirements stub listing the framework packages to pin."""
    pkgs = PACKAGES[s["framework"]]
    if s["framework"] == "onnx" and s["gpu"]:
        pkgs = ["onnxruntime-gpu"]
    body = "".join(f"# {p}==<version you trained with>\n" for p in pkgs) or "# add serving dependencies\n"
    return "# Pin every package to the exact version used in training, then uncomment.\n" + body


def build(spec: Dict[str, Any], out: Path, force: bool) -> Dict[str, Any]:
    """Render all artifacts and write them under out; refuse to overwrite unless force."""
    s, checks = normalize(spec)
    files = {"Dockerfile": render_dockerfile(s), "k8s.yaml": render_k8s(s),
             "serve.py": SERVE_STUB.format(name=s["name"], model_file=s["model_file"], framework=s["framework"],
                                           liveness=s["liveness"], readiness=s["readiness"], port=s["port"]),
             "requirements.txt": render_requirements(s)}
    existing = [n for n in files if (out / n).exists()]
    if existing and not force:
        raise FileExistsError(f"{out} already has {', '.join(existing)}; pass --force to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    for fname, text in files.items():
        (out / fname).write_text(text, encoding="utf-8")
    return {"service": s["name"], "output": str(out), "files": sorted(files),
            "image": s["image"], "base_image": s["base_image"], "port": s["port"],
            "replicas": {"min": s["min"], "max": s["max"]}, "gpu": s["gpu"], "secret_env": s["secret_env"],
            "checks": checks,
            "warnings": sum(c["severity"] == "warn" for c in checks)}


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the result as JSON or as a readable summary."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return
    print(f"Deployment artifacts for {result['service']} -> {result['output']}")
    for f in result["files"]:
        print(f"  wrote {f}")
    r = result["replicas"]
    print(f"Image {result['image']} on {result['base_image']}, port {result['port']}, "
          f"replicas {r['min']}-{r['max']}, gpu {'yes' if result['gpu'] else 'no'}")
    print(f"Checks ({result['warnings']} warnings):" if result["checks"] else "Checks: none raised")
    for c in result["checks"]:
        print(f"  [{c['severity'].upper()}] {c['message']}")


def main() -> None:
    """Parse arguments, build artifacts and report."""
    ap = argparse.ArgumentParser(description="Generate a Dockerfile, Kubernetes Deployment/Service/HPA, "
                                 "a health/readiness stub and a requirements stub from a model-service spec.")
    ap.add_argument("--input", "-i", help="model-service spec JSON (see --example)")
    ap.add_argument("--output", "-o", help="directory to write artifacts into")
    ap.add_argument("--force", action="store_true", help="overwrite existing files in --output")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="report format (default text)")
    ap.add_argument("--example", action="store_true", help="print a sample spec and exit")
    args = ap.parse_args()
    if args.example:
        print(json.dumps(EXAMPLE_SPEC, indent=2))
        return
    if not args.input or not args.output:
        ap.error("--input and --output are required (or use --example)")
    try:
        spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise ValueError("spec must be a JSON object")
        output(build(spec, Path(args.output), args.force), args.format)
    except FileNotFoundError:
        sys.exit(f"error: input file not found: {args.input}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {args.input} is not valid JSON ({exc.msg} at line {exc.lineno})")
    except (ValueError, TypeError, AttributeError, KeyError, FileExistsError, OSError) as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
