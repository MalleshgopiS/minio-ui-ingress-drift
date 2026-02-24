#!/usr/bin/env python3
import json
import subprocess
import sys
import time

NAMESPACE = "bleater"
INGRESS = "bleater-ui"


def run(cmd):
    return subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------
# Visible Validation Tests (Required for Quality PASS)
# ---------------------------------------------------

def validate_ingress_configuration():
    """Validate ingress backend + TLS configuration"""

    print("Running visible ingress validation checks...")

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

    errors = []

    if svc != "bleater-minio":
        errors.append("Backend service incorrect")

    if port != "9001":
        errors.append("Backend port incorrect")

    if tls != "bleater-minio-tls":
        errors.append("TLS secret incorrect")

    return errors


def wait_for_pods_ready(timeout=120):
    print("Waiting for pods to stabilize...")
    start = time.time()

    while time.time() - start < timeout:
        result = run(
            "kubectl get pods -A --no-headers | grep -v Running || true"
        )

        if result.stdout.strip() == "":
            return True

        time.sleep(5)

    return False


# ---------------------------------------------------
# External Nebula Test Suite
# ---------------------------------------------------

def run_nebula_tests():
    print("Running Nebula external test suite...")

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
# MAIN GRADER
# ---------------------------------------------------

def main():

    if not wait_for_pods_ready():
        print(json.dumps({
            "score": 0.0,
            "feedback": "Cluster not ready"
        }))
        sys.exit(0)

    visible_errors = validate_ingress_configuration()

    if visible_errors:
        print(json.dumps({
            "score": 0.0,
            "feedback": " | ".join(visible_errors)
        }))
        sys.exit(0)

    nebula_ok, msg = run_nebula_tests()

    if not nebula_ok:
        print(json.dumps({
            "score": 0.0,
            "feedback": msg
        }))
        sys.exit(0)

    print(json.dumps({
        "score": 1.0,
        "feedback": "✓ All visible + Nebula tests passed"
    }))


if __name__ == "__main__":
    main()