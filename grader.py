#!/usr/bin/env python3

import subprocess
import json
import time
from apex_arena._types import GradingResult


# -----------------------------
# helper runner
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
# wait for cluster stability
# -----------------------------
def wait_for_pods_ready(timeout=180):
    start = time.time()

    while time.time() - start < timeout:
        code, out, _ = run(
            "kubectl get pods -n bleater "
            "--no-headers "
            "-o custom-columns=':status.conditions[?(@.type==\"Ready\")].status'"
        )

        if code == 0 and out:
            statuses = [s.strip() for s in out.split("\n") if s.strip()]
            if statuses and all(s == "True" for s in statuses):
                return True

        time.sleep(5)

    return False


# -----------------------------
# ingress validation
# -----------------------------
def validate_ingress():

    wait_for_pods_ready()

    cmd = """
kubectl get ingress bleater-ui -n bleater -o jsonpath='
{.spec.rules[0].host}|\
{.spec.rules[0].http.paths[0].backend.service.name}|\
{.spec.rules[0].http.paths[0].backend.service.port.number}|\
{.spec.tls[0].secretName}'
"""
    code, out, err = run(cmd)

    if code != 0 or not out:
        return None, f"Failed to read ingress: {err}"

    host, service, port, tls = out.split("|")

    # --- FIXED CHECKS (partial scoring) ---
    checks = {
        "host_correct": host == "minio.devops.local",
        "service_name_correct": service == "bleater-minio",
        "service_port_correct": int(port) == 9001,  # FIX: integer comparison
        "tls_secret_correct": tls == "bleater-minio-tls",
    }

    return checks, None


# -----------------------------
# grading entrypoint
# -----------------------------
def grade(transcript: str) -> GradingResult:

    checks, error = validate_ingress()

    if error:
        return GradingResult(
            score=0.0,
            subscores={"ingress_validation": 0.0},
            weights={"ingress_validation": 1.0},
            feedback=error,
        )

    passed = sum(checks.values())
    total = len(checks)

    score = passed / total

    feedback = f"{passed}/{total} ingress fields correct"

    return GradingResult(
        score=score,
        subscores=checks,
        weights={
            "host_correct": 0.25,
            "service_name_correct": 0.25,
            "service_port_correct": 0.25,
            "tls_secret_correct": 0.25,
        },
        feedback=feedback,
    )