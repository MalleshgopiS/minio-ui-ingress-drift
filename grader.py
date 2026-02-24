#!/usr/bin/env python3
import json
import subprocess
import time

NAMESPACE = "bleater"
INGRESS = "bleater-ui"


# ---------------------------------------------------
# Helper
# ---------------------------------------------------

def run(cmd):
    return subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------
# Visible Validation Tests
# ---------------------------------------------------

def validate_ingress_configuration():
    """Validate ingress backend + TLS + host configuration"""

    svc = run(
        f"kubectl get ingress {INGRESS} -n {NAMESPACE} "
        "-o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}'"
    ).stdout.strip().strip("'")

    port = run(
        f"kubectl get ingress {INGRESS} -n {NAMESPACE} "
        "-o jsonpath='{.spec.rules[0].http.paths[0].backend.service.port.number}'"
    ).stdout.strip().strip("'")

    tls = run(
        f"kubectl get ingress {INGRESS} -n {NAMESPACE} "
        "-o jsonpath='{.spec.tls[0].secretName}'"
    ).stdout.strip().strip("'")

    host = run(
        f"kubectl get ingress {INGRESS} -n {NAMESPACE} "
        "-o jsonpath='{.spec.rules[0].host}'"
    ).stdout.strip().strip("'")

    errors = []

    if svc != "bleater-minio":
        errors.append("Backend service incorrect")

    if port != "9001":
        errors.append("Backend port incorrect")

    if tls != "bleater-minio-tls":
        errors.append("TLS secret incorrect")

    if host != "minio.devops.local":
        errors.append("Host incorrect")

    return errors


def wait_for_pods_ready(timeout=120):
    start = time.time()

    while time.time() - start < timeout:
        result = run(
            "kubectl get pods -A --no-headers | "
            "grep -v Running | grep -v Completed || true"
        )

        if result.stdout.strip() == "":
            return True

        time.sleep(5)

    return False


# ---------------------------------------------------
# External Nebula Tests
# ---------------------------------------------------

def run_nebula_tests():
    result = run("/root/tests/test_suite.sh")

    if result.returncode != 0:
        return False, "External test suite failed"

    try:
        with open("/root/tests/test_results.json") as f:
            data = json.load(f)

        failures = [t for t in data if not t.get("passed")]

        if failures:
            return False, f"{len(failures)} tests failed"

    except Exception as e:
        return False, f"Could not read results: {e}"

    return True, "All Nebula tests passed"


# ---------------------------------------------------
# ⭐ REQUIRED BY APEX
# ---------------------------------------------------

def grade():
    """Entry point required by Apex MCP grader"""

    if not wait_for_pods_ready():
        return {
            "score": 0.0,
            "feedback": "Cluster not ready"
        }

    visible_errors = validate_ingress_configuration()

    if visible_errors:
        return {
            "score": 0.0,
            "feedback": " | ".join(visible_errors)
        }

    nebula_ok, msg = run_nebula_tests()

    if not nebula_ok:
        return {
            "score": 0.0,
            "feedback": msg
        }

    return {
        "score": 1.0,
        "feedback": "✓ All visible + Nebula tests passed"
    }


# Optional local execution
if __name__ == "__main__":
    print(json.dumps(grade()))