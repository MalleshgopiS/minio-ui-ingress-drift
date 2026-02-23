import subprocess


NAMESPACE = "bleater"
INGRESS_NAME = "bleater-ui"


def run(cmd: str) -> str:
    """Execute shell command and return output."""
    return subprocess.check_output(
        cmd,
        shell=True,
        text=True
    ).strip()


def grade(task_output=None):
    """
    Apex Arena grader entrypoint.
    Must accept one parameter (same as scale_deployment task).
    Must return dict with score + feedback.
    """

    try:
        # Read ingress configuration
        output = run(
            f"kubectl get ingress {INGRESS_NAME} -n {NAMESPACE} "
            "-o jsonpath=\"{.spec.rules[0].http.paths[0].backend.service.name} "
            "{.spec.rules[0].http.paths[0].backend.service.port.number} "
            "{.spec.rules[0].http.paths[0].pathType} "
            "{.spec.tls[0].secretName}\""
        )

        service, port, path_type, tls_secret = output.split()

        # ---- VALIDATIONS (same grading style as sample task) ----

        if service != "bleater-minio":
            return {
                "score": 0.0,
                "feedback": f"❌ Wrong backend service: {service}"
            }

        if port != "9001":
            return {
                "score": 0.0,
                "feedback": f"❌ Wrong service port: {port}"
            }

        if path_type != "Prefix":
            return {
                "score": 0.0,
                "feedback": f"❌ pathType not fixed: {path_type}"
            }

        if tls_secret != "bleater-minio-tls":
            return {
                "score": 0.0,
                "feedback": f"❌ Wrong TLS secret: {tls_secret}"
            }

        # SUCCESS
        return {
            "score": 1.0,
            "feedback": "✅ MinIO ingress drift fixed successfully"
        }

    except subprocess.CalledProcessError as e:
        return {
            "score": 0.0,
            "feedback": f"Ingress validation failed: {str(e)}"
        }

    except Exception as e:
        return {
            "score": 0.0,
            "feedback": f"Unexpected grader error: {str(e)}"
        }