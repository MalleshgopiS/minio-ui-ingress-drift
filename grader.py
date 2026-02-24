import subprocess
import json
import time


def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def retry(fn, attempts=20, delay=3):
    for _ in range(attempts):
        if fn():
            return True
        time.sleep(delay)
    return False


def get_ingress_ip():
    return run(
        "kubectl get ingress bleater -n bleater "
        "-o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
    )


# ---------------- CHECKS ---------------- #

def check_dns():
    """DNS must resolve to ingress IP"""
    ip = get_ingress_ip()
    out = run("getent hosts bleater.devops.local")
    return ip in out


def check_api_route():
    """API path must still function"""
    subprocess.check_call(
        "curl -skf https://bleater.devops.local/api/health",
        shell=True
    )
    return True


def check_ingress():
    """Root path must point to MinIO console"""
    data = json.loads(run(
        "kubectl get ingress bleater -n bleater -o json"
    ))

    path = next(p for p in data["spec"]["rules"][0]["http"]["paths"]
                if p["path"] == "/")

    return (
        path["backend"]["service"]["name"] == "bleater-minio"
        and path["backend"]["service"]["port"]["number"] == 9001
        and data["spec"]["tls"][0]["secretName"] == "bleater-ui-tls"
    )


def check_bucket():
    """Bucket must allow anonymous download"""
    out = run("mc anonymous get local/ui")
    return "download" in out.lower()


def check_ui():
    """UI must load"""
    subprocess.check_call(
        "curl -skf https://bleater.devops.local/index.html",
        shell=True
    )
    return True


# ---------------- GRADER ---------------- #

def grade():
    checks = [
        check_dns,
        check_api_route,
        check_ingress,
        check_bucket,
        check_ui,
    ]

    for c in checks:
        if not retry(c):
            return 0.0

    return 1.0


if __name__ == "__main__":
    print(grade())