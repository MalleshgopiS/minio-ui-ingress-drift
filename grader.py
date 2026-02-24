"""
Grader for MinIO UI DNS + Ingress Drift task.

Validates:
1. DNS resolves to ingress controller IP
2. /api route remains functional
3. Root path routes to MinIO console
4. TLS secret updated
5. Bucket allows anonymous read
6. UI loads end-to-end
"""

import subprocess
import json
import time


def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def retry(fn, attempts=20, delay=3):
    for _ in range(attempts):
        if fn():
            return True
        time.sleep(delay)
    return False


def get_ingress_ip():
    """Discover ingress controller IP dynamically."""
    candidates = ["ingress-nginx-controller", "ingress-nginx"]

    for svc in candidates:
        code, ip = run(
            f"kubectl get svc -n ingress-nginx {svc} "
            "-o jsonpath='{.spec.clusterIP}'"
        )
        if code == 0 and ip:
            return ip.strip("'")
    return None


def check_dns():
    """DNS must resolve to ingress controller."""
    ip = get_ingress_ip()
    if not ip:
        return False

    code, out = run("getent hosts bleater.devops.local")
    return code == 0 and ip in out


def check_api_route():
    """API path must still function."""
    code, _ = run(
        "curl -k --fail --max-time 5 https://bleater.devops.local/api"
    )
    return code == 0


def check_ingress():
    """Root path must point to MinIO console."""
    code, out = run(
        "kubectl get ingress bleater -n bleater -o json"
    )
    if code != 0:
        return False

    data = json.loads(out)

    paths = data["spec"]["rules"][0]["http"]["paths"]

    root = next((p for p in paths if p["path"] == "/"), None)
    if not root:
        return False

    svc = root["backend"]["service"]
    tls = data["spec"]["tls"][0]["secretName"]

    return (
        svc["name"] == "bleater-minio"
        and svc["port"]["number"] == 9001
        and tls == "bleater-ui-tls"
    )


def check_bucket():
    """Bucket must allow anonymous download."""
    code, out = run("mc anonymous get local/ui 2>/dev/null")
    return code == 0 and "download" in out.lower()


def check_ui():
    """UI must load successfully."""
    code, _ = run(
        "curl -k --fail --max-time 5 https://bleater.devops.local/index.html"
    )
    return code == 0


def grade():
    checks = [
        retry(check_dns),
        retry(check_api_route),
        retry(check_ingress),
        retry(check_bucket),
        retry(check_ui),
    ]

    if all(checks):
        return 1.0, "UI fully restored"

    return 0.0, "System still broken"