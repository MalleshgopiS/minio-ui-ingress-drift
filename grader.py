import subprocess
import json


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


# -------------------------
# DNS CHECK
# -------------------------
def check_dns():
    code, out = run("getent hosts bleater.devops.local")
    return code == 0


# -------------------------
# INGRESS CHECK
# -------------------------
def check_ingress():
    cmd = """
kubectl get ingress bleater -n bleater -o json
"""
    code, out = run(cmd)
    if code != 0:
        return False

    data = json.loads(out)

    paths = data["spec"]["rules"][0]["http"]["paths"]

    root = next(p for p in paths if p["path"] == "/")

    svc = root["backend"]["service"]["name"]
    port = root["backend"]["service"]["port"]["number"]

    tls = data["spec"]["tls"][0]["secretName"]

    return (
        svc == "bleater-minio"
        and port == 9001
        and tls == "bleater-ui-tls"
    )


# -------------------------
# MINIO POLICY CHECK
# -------------------------
def check_bucket():
    code, out = run("mc anonymous get local/ui")
    return "download" in out.lower()


# -------------------------
# END TO END CHECK
# -------------------------
def check_http():
    code, _ = run(
        "curl -k --fail https://bleater.devops.local/index.html"
    )
    return code == 0


def grade():
    checks = [
        check_dns(),
        check_ingress(),
        check_bucket(),
        check_http(),
    ]

    if all(checks):
        return 1.0, "UI fully restored"

    return 0.0, "System still broken"