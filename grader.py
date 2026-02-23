import subprocess
from apex_arena.grader import GradeResult


NAMESPACE = "bleater"
INGRESS = "bleater-ui"


def run(cmd: str) -> str:
    """Run shell command and return output."""
    return subprocess.check_output(
        cmd, shell=True, text=True
    ).strip()


def check_ingress():
    """
    Validate ingress configuration drift is fixed.

    Checks:
    - backend service name
    - backend service port
    - TLS secret name
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
            return GradeResult(
                score=0.0,
                feedback=f"Wrong service name: {service}"
            )

        if port != "9001":
            return GradeResult(
                score=0.0,
                feedback=f"Wrong service port: {port}"
            )

        if secret != "bleater-minio-tls":
            return GradeResult(
                score=0.0,
                feedback=f"Wrong TLS secret: {secret}"
            )

        return GradeResult(
            score=1.0,
            feedback="Ingress correctly fixed ✅"
        )

    except subprocess.CalledProcessError:
        return GradeResult(
            score=0.0,
            feedback="Ingress not found"
        )


def grade():
    """Apex entrypoint."""
    return check_ingress()