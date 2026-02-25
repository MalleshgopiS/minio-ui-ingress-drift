#!/usr/bin/env python3

import subprocess
import time
from apex_arena._types import GradingResult


# ---------------------------------------------------
# Helper runner
# ---------------------------------------------------

def run(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


# ---------------------------------------------------
# Wait for cluster stability
# ---------------------------------------------------

def wait_for_cluster(timeout=180):
    start = time.time()

    while time.time() - start < timeout:
        code, out, _ = run(
            "kubectl get pods -n bleater --no-headers 2>/dev/null"
        )

        if code == 0:
            return True

        time.sleep(5)

    return False


# ---------------------------------------------------
# Anti-cheat: capture ingress UID
# ---------------------------------------------------

def get_ingress_uid():
    code, out, _ = run(
        "kubectl get ingress bleater-ui -n bleater "
        "-o jsonpath='{.metadata.uid}' 2>/dev/null"
    )
    return out.strip().replace("'", "") if code == 0 else None


# ---------------------------------------------------
# Validation Logic
# ---------------------------------------------------

def validate_ingress():

    cmd = (
        "kubectl get ingress bleater-ui -n bleater "
        "-o jsonpath='{.spec.rules[0].host}|"
        "{.spec.rules[0].http.paths[0].backend.service.name}|"
        "{.spec.rules[0].http.paths[0].backend.service.port.number}|"
        "{.spec.tls[0].secretName}'"
    )

    code, out, err = run(cmd)

    if code != 0 or not out:
        return 0.0, ["✗ Unable to read ingress resource"]

    parts = out.replace("'", "").split("|")

    if len(parts) != 4:
        return 0.0, ["✗ Unexpected ingress output format"]

    host, service, port, tls = parts

    checks = {
        "host_correct": host == "minio.devops.local",
        "service_name_correct": service == "bleater-minio",
        "service_port_correct": False,
        "tls_secret_correct": tls == "bleater-minio-tls",
    }

    # Safe port parsing
    try:
        checks["service_port_correct"] = int(port) == 9001
    except Exception:
        checks["service_port_correct"] = False

    score = sum(checks.values()) * 0.25

    feedback = []
    for k, v in checks.items():
        feedback.append(f"{'✓' if v else '✗'} {k}")

    return score, feedback


# ---------------------------------------------------
# Main grading entrypoint
# ---------------------------------------------------

def grade(transcript: str) -> GradingResult:

    wait_for_cluster()

    # Capture UID BEFORE agent actions
    original_uid = get_ingress_uid()

    score, feedback = validate_ingress()

    # Anti-cheat validation
    new_uid = get_ingress_uid()

    if original_uid and new_uid and original_uid != new_uid:
        feedback.append("✗ Ingress was recreated (new resource detected)")
        score = 0.0

    return GradingResult(
        score=score,
        subscores={"ingress_validation": score},
        weights={"ingress_validation": 1.0},
        feedback=" | ".join(feedback),
    )