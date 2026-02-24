#!/usr/bin/env python3

import subprocess
import json
import os
import time
from apex_arena._types import GradingResult


# ---------------------------
# Command Runner
# ---------------------------

def run(cmd, timeout=60):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)


# ---------------------------
# Cluster Stabilization
# ---------------------------

def wait_for_pods_ready(timeout=180):
    """
    Wait until all pods in bleater namespace are Ready.
    Prevents non-deterministic test failures.
    """
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


# ---------------------------
# Nebula Test Suite Runner
# ---------------------------

def run_test_suite():
    """
    Nebula validation entrypoint.

    Test suite validates:
      - DNS routing
      - Ingress correctness
      - MinIO access
      - UI loads
      - API health
    """

    test_script = "/root/tests/test_suite.sh"
    results_file = "/root/tests/test_results.json"

    if not os.path.exists(test_script):
        return False, "Test suite missing"

    # Wait for infra convergence
    wait_for_pods_ready()

    try:
        subprocess.run(
            ["bash", test_script],
            cwd="/root/tests",
            timeout=300,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return False, "Test suite timeout"

    if not os.path.exists(results_file):
        return False, "Test results not generated"

    try:
        with open(results_file) as f:
            results = json.load(f)
    except Exception:
        return False, "Invalid test_results.json"

    if not isinstance(results, dict):
        return False, "Malformed test_results.json"

    total = len(results)
    passed = sum(1 for v in results.values() if v == 1)

    if total == 0:
        return False, "No tests executed"

    if passed == total:
        return True, f"All {total} tests passed"

    failed = [k for k, v in results.items() if v == 0]

    return False, f"{passed}/{total} tests passed. Failed: {', '.join(failed)}"


# ---------------------------
# Main Grade Entrypoint
# ---------------------------

def grade(transcript: str) -> GradingResult:
    """
    Apex Arena grading entrypoint.
    """

    feedback_parts = []

    suite_ok, message = run_test_suite()

    if suite_ok:
        score = 1.0
        feedback_parts.append(f"✓ {message}")
    else:
        score = 0.0
        feedback_parts.append(f"✗ {message}")

    feedback = " | ".join(feedback_parts)

    return GradingResult(
        score=score,
        subscores={"nebula_validation": score},
        weights={"nebula_validation": 1.0},
        feedback=feedback,
    )