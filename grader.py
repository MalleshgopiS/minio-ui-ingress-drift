#!/usr/bin/env python3

import subprocess
import time
from apex_arena._types import GradingResult


# -----------------------------
# Helper runner
# -----------------------------
def run(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


# -----------------------------
# Wait for cluster stability
# -----------------------------
def wait_for_cluster(timeout=180):
    start = time.time()

    while time.time() - start < timeout:
        code, out, _ = run(
            "kubectl get pods -n bleater "
            "--no-headers "
            "-o custom-columns=':status.phase'"
        )

        if code == 0 and out:
            pods = [p.strip() for p in out.split("\n") if p.strip()]
            if pods and all(p == "Running" for p in pods):
                return True

        time.sleep(5)

    return False


# -----------------------------
# Validation Logic
# -----------------------------
def validate_ingress():

    wait_for_cluster()

    cmd = """
kubectl get ingress bleater-ui -n bleater \
-o jsonpath='{.spec.rules[0].host}{"|"}\
{.spec.rules[0].http.paths[0].backend.service.name}{"|"}\
{.spec.rules[0].http.paths[0].backend.service.port.number}{"|"}\
{.spec.tls[0].secretName}'
"""

    code, out, err = run(cmd)

    if code != 0 or not out:
        return 0.0, f"Failed to read ingress: {err}"

    try:
        host, service, port, tls = out.split("|")
    except ValueError:
        return 0.0, "Ingress output malformed"

    # ---- Safe port parsing (fix reviewer issue) ----
    try:
        port_ok = int(port) == 9001
    except Exception:
        port_ok = False

    checks = {
        "host_correct": host == "minio.devops.local",
        "service_name_correct": service == "bleater-minio",
        "service_port_correct": port_ok,
        "tls_secret_correct": tls == "bleater-minio-tls",
    }

    score = sum(0.25 for v in checks.values() if v)

    feedback = ", ".join(
        [f"{k}={'OK' if v else 'FAIL'}" for k, v in checks.items()]
    )

    return score, feedback


# -----------------------------
# Main grading entrypoint
# -----------------------------
def grade(transcript: str) -> GradingResult:

    score, feedback = validate_ingress()

    return GradingResult(
        score=score,
        subscores={"ingress_validation": score},
        weights={"ingress_validation": 1.0},
        feedback=feedback,
    )