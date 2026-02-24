import subprocess
import json
import time


# --------------------------------------------------
# helpers
# --------------------------------------------------

def run(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def retry(cmd, attempts=20, delay=5):
    """
    Wait for system convergence (Nebula requirement).
    """
    for _ in range(attempts):
        code, out, _ = run(cmd)
        if code == 0 and out:
            return True, out
        time.sleep(delay)

    return False, ""


# --------------------------------------------------
# ingress checks
# --------------------------------------------------

def check_ingress():
    cmd = """
    kubectl get ingress bleater-ui -n bleater -o json
    """

    code, out, err = run(cmd)
    if code != 0:
        return False, "Ingress bleater-ui not found"

    data = json.loads(out)

    host = data["spec"]["rules"][0]["host"]
    svc = data["spec"]["rules"][0]["http"]["paths"][0]["backend"]["service"]["name"]
    port = str(
        data["spec"]["rules"][0]["http"]["paths"][0]["backend"]["service"]["port"]["number"]
    )
    tls = data["spec"]["tls"][0]["secretName"]

    if host != "bleater.devops.local":
        return False, f"Wrong host: {host}"

    if svc != "bleater-minio":
        return False, f"Wrong backend service: {svc}"

    if port not in ["9000", "9001"]:
        return False, f"Unexpected MinIO port: {port}"

    if tls != "bleater-minio-tls":
        return False, f"Wrong TLS secret: {tls}"

    return True, "Ingress OK"


# --------------------------------------------------
# dnsmasq validation
# --------------------------------------------------

def check_dnsmasq():
    """
    Ensure wildcard DNS points to ingress IP.
    """

    ok, ingress_ip = retry(
        "kubectl -n ingress-nginx get svc ingress-nginx-controller "
        "-o jsonpath='{.spec.clusterIP}'"
    )

    if not ok:
        return False, "Cannot determine ingress IP"

    code, out, _ = run("cat /etc/dnsmasq.d/devops.conf 2>/dev/null")

    if code != 0:
        return False, "dnsmasq config missing"

    if ingress_ip not in out:
        return False, "dnsmasq not pointing to ingress IP"

    return True, "dnsmasq OK"


# --------------------------------------------------
# runtime validation
# --------------------------------------------------

def curl_host(path="/"):
    ok, ingress_ip = retry(
        "kubectl -n ingress-nginx get svc ingress-nginx-controller "
        "-o jsonpath='{.spec.clusterIP}'"
    )

    if not ok:
        return 1, ""

    cmd = f"""
    curl -sk -H "Host: bleater.devops.local" https://{ingress_ip}{path}
    """

    return run(cmd)


def check_ui_loads():
    code, out, _ = curl_host("/")

    if code != 0:
        return False, "UI request failed"

    if "<html" not in out.lower():
        return False, "UI HTML not served"

    return True, "UI loads"


def check_api():
    code, out, _ = curl_host("/api/health")

    if code != 0:
        return False, "API unreachable"

    if "ok" not in out.lower():
        return False, "API unhealthy"

    return True, "API healthy"


# --------------------------------------------------
# MinIO public bucket check
# --------------------------------------------------

def check_minio_public():
    """
    Anonymous access should work.
    403 means bucket still private.
    """

    code, out, err = curl_host("/index.html")

    if "AccessDenied" in out or "403" in err:
        return False, "MinIO bucket not public"

    return True, "MinIO public access OK"


# --------------------------------------------------
# main grading
# --------------------------------------------------

def grade():

    checks = [
        check_ingress,
        check_dnsmasq,
        check_ui_loads,
        check_api,
        check_minio_public,
    ]

    for check in checks:
        ok, msg = check()
        if not ok:
            return 0.0, msg

    return 1.0, "All validations passed — UI + API stable"