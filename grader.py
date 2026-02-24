import subprocess


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def check_ingress():
    """
    Validate bleater ingress configuration.
    """

    cmd = """
    kubectl get ingress bleater -n bleater \
    -o jsonpath='{.spec.rules[0].host} {.spec.rules[0].http.paths[0].backend.service.name} {.spec.rules[0].http.paths[0].backend.service.port.number} {.spec.tls[0].secretName}'
    """

    code, out = run(cmd)

    if code != 0:
        return False, "Ingress not found"

    parts = out.replace("'", "").split()

    if len(parts) != 4:
        return False, f"Unexpected output: {out}"

    host, service, port, secret = parts

    if host != "bleater.devops.local":
        return False, f"Wrong host: {host}"

    if service != "bleater-minio":
        return False, f"Wrong backend: {service}"

    if port != "9001":
        return False, f"Wrong port: {port}"

    if secret != "bleater-ui-tls":
        return False, f"Wrong TLS secret: {secret}"

    return True, "Ingress correctly configured"


def grade():
    ok, msg = check_ingress()
    return (1.0, msg) if ok else (0.0, msg)