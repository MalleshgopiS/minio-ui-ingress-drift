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


# ------------------------------------------------
# DNS MUST MATCH INGRESS IP
# ------------------------------------------------
def check_dns():

    code, ingress_ip = run("""
kubectl get svc -n ingress-nginx ingress-nginx-controller \
-o jsonpath='{.spec.clusterIP}'
""")

    if code != 0:
        return False

    code, resolved = run("getent hosts bleater.devops.local")

    if code != 0:
        return False

    return ingress_ip in resolved


# ------------------------------------------------
# INGRESS VALIDATION
# ------------------------------------------------
def check_ingress():

    code, out = run(
        "kubectl get ingress bleater -n bleater -o json"
    )

    if code != 0:
        return False

    data = json.loads(out)

    try:
        paths = data["spec"]["rules"][0]["http"]["paths"]
    except Exception:
        return False

    root_backend = None

    for p in paths:
        if p.get("path") == "/":
            root_backend = p["backend"]["service"]

    if not root_backend:
        return False

    tls_secret = data["spec"]["tls"][0]["secretName"]

    return (
        root_backend["name"] == "bleater-minio"
        and root_backend["port"]["number"] == 9001
        and tls_secret == "bleater-ui-tls"
    )


# ------------------------------------------------
# MINIO POLICY
# ------------------------------------------------
def check_bucket():
    code, out = run("mc anonymous get local/ui 2>/dev/null")
    return code == 0 and "download" in out.lower()


# ------------------------------------------------
# END-TO-END TEST
# ------------------------------------------------
def check_http():
    code, _ = run(
        "curl -k --fail --max-time 5 https://bleater.devops.local/index.html"
    )
    return code == 0


# ------------------------------------------------
# MAIN
# ------------------------------------------------
def grade():

    checks = [
        retry(check_dns),
        retry(check_ingress),
        retry(check_bucket),
        retry(check_http),
    ]

    if all(checks):
        return 1.0, "UI restored successfully"

    return 0.0, "Infrastructure still misconfigured"