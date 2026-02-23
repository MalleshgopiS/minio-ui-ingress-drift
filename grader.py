import subprocess
import json


def run(cmd: str):
    """Run shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_ingress():
    """
    Validate that the bleater-ui ingress has been corrected.

    Checks:
    - backend service name = bleater-minio
    - backend port = 9001
    - TLS secret = bleater-minio-tls
    """

    cmd = """
    kubectl get ingress bleater-ui -n bleater \
      -o jsonpath="{.spec.rules[0].http.paths[0].backend.service.name} \
{.spec.rules[0].http.paths[0].backend.service.port.number} \
{.spec.tls[0].secretName}"
    """

    rc, out, err = run(cmd)

    if rc != 0:
        return False, f"Failed to get ingress: {err}"

    parts = out.replace("'", "").split()

    if len(parts) != 3:
        return False, f"Unexpected ingress output: {out}"

    service, port, secret = parts

    if service != "bleater-minio":
        return False, f"Wrong service: {service}"

    if port != "9001":
        return False, f"Wrong port: {port}"

    if secret != "bleater-minio-tls":
        return False, f"Wrong TLS secret: {secret}"

    return True, "Ingress correctly configured"


# ⭐ OLD STYLE APEX GRADER (IMPORTANT)
def grade():
    success, message = check_ingress()

    if success:
        return {
            "score": 1.0,
            "message": message,
        }

    return {
        "score": 0.0,
        "message": message,
    }


# local debug
if __name__ == "__main__":
    print(json.dumps(grade(), indent=2))