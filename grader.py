import subprocess


NAMESPACE = "bleater"
INGRESS = "bleater-ui"


def run(cmd: str):
    """Run shell command safely."""
    return subprocess.check_output(
        cmd,
        shell=True,
        text=True
    ).strip()


def check_ingress():
    """
    Validate MinIO ingress drift fix.
    """

    try:
        output = run(
            f"kubectl get ingress {INGRESS} -n {NAMESPACE} "
            "-o jsonpath=\"{.spec.rules[0].http.paths[0].backend.service.name} "
            "{.spec.rules[0].http.paths[0].backend.service.port.number} "
            "{.spec.tls[0].secretName}\""
        )

        service, port, secret = output.split()

        if service != "bleater-minio":
            return {
                "score": 0.0,
                "feedback": f"Wrong service name: {service}"
            }

        if port != "9001":
            return {
                "score": 0.0,
                "feedback": f"Wrong service port: {port}"
            }

        if secret != "bleater-minio-tls":
            return {
                "score": 0.0,
                "feedback": f"Wrong TLS secret: {secret}"
            }

        return {
            "score": 1.0,
            "feedback": "Ingress correctly fixed ✅"
        }

    except subprocess.CalledProcessError:
        return {
            "score": 0.0,
            "feedback": "Ingress not found"
        }


def grade(task_output=None):
    """
    Apex entrypoint.
    Must accept one argument (even if unused).
    """
    return check_ingress()