import subprocess


def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def check_ingress():
    """
    Validate bleater-ui ingress configuration.

    Checks:
    - backend service name
    - backend port
    - TLS secret name
    - host value
    """

    try:
        output = run(
            "kubectl get ingress bleater-ui -n bleater "
            "-o jsonpath='{.spec.rules[0].host} "
            "{.spec.rules[0].http.paths[0].backend.service.name} "
            "{.spec.rules[0].http.paths[0].backend.service.port.number} "
            "{.spec.tls[0].secretName}'"
        ).replace("'", "")
    except Exception as e:
        return False, f"Ingress not found or kubectl failed: {e}"

    parts = output.split()

    if len(parts) != 4:
        return False, f"Unexpected output format: {output}"

    host, service, port, tls = parts

    if host != "minio.devops.local":
        return False, f"Host incorrect: {host}"

    if service != "bleater-minio":
        return False, f"Service incorrect: {service}"

    if port != "9001":
        return False, f"Port incorrect: {port}"

    if tls != "bleater-minio-tls":
        return False, f"TLS secret incorrect: {tls}"

    return True, "All ingress values correct"


# ⭐⭐⭐ CRITICAL FIX HERE ⭐⭐⭐
def grade(context=None):
    ok, message = check_ingress()

    if ok:
        return {
            "score": 1.0,
            "feedback": message
        }

    return {
        "score": 0.0,
        "feedback": message
    }