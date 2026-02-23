import subprocess


def run(cmd):
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip()


def check_ingress():
    """
    Validate that the bleater-ui ingress has been corrected.

    Checks:
    - backend service name
    - backend port
    - TLS secret name
    """

    cmd = """kubectl get ingress bleater-ui -n bleater -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name} {.spec.rules[0].http.paths[0].backend.service.port.number} {.spec.tls[0].secretName}'"""
    code, out = run(cmd)

    if code != 0:
        return False, "Ingress not found"

    service, port, secret = out.replace("'", "").split()

    if service != "bleater-minio":
        return False, f"Wrong service: {service}"

    if port != "9001":
        return False, f"Wrong port: {port}"

    if secret != "bleater-minio-tls":
        return False, f"Wrong TLS secret: {secret}"

    return True, "Ingress correctly configured"


def grade():
    ok, msg = check_ingress()
    if ok:
        return 1.0, msg
    return 0.0, msg