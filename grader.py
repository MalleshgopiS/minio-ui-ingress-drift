#!/usr/bin/env python3

import subprocess
import json
import os
import time
from apex_arena._types import GradingResult


# --------------------------------------------------
# helpers
# --------------------------------------------------

def run(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


# --------------------------------------------------
# wait for cluster convergence
# --------------------------------------------------

def wait_for_pods_ready(timeout=120):
    start = time.time()

    while time.time() - start < timeout:
        code, out, _ = run(
            "kubectl get pods -n bleater "
            "--no-headers "
            "-o custom-columns=':status.conditions[?(@.type==\"Ready\")].status'"
        )

        if code == 0 and out:
            statuses = out.split("\n")
            if all(s.strip() == "True" for s in statuses if s.strip()):
                return True

        time.sleep(5)

    return False


# --------------------------------------------------
# run nebula test suite
# --------------------------------------------------

def run_test_suite():
    """
    Nebula validation entrypoint.
    Test suite validates:
      - DNS routing
      - ingress correctness
      - MinIO access
      - UI loads
      - API health
    """

    test_script = "/root/tests/test_suite.sh"
    results_file = "/root/tests/test_results.json"

    if not os.path.exists(test_script):
        return False, "Test suite missing"

    # wait for infra stabilization
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

    total = len(results)
    passed = sum(results.values())

    if total == 0:
        return False, "No tests executed"

    if passed == total:
        return True, f"All {total} tests passed"

    failed = [k for k, v in results.items() if v == 0]

    return False, f"{passed}/{total} tests passed. Failed: {', '.join(failed)}"


# --------------------------------------------------
# main grade entrypoint
# --------------------------------------------------

def grade(transcript: str) -> GradingResult:

    feedback_parts = []

    suite_ok, msg = run_test_suite()

    if suite_ok:
        feedback_parts.append(f"✓ {msg}")
        score = 1.0
    else:
        feedback_parts.append(f"✗ {msg}")
        score = 0.0

    feedback = " | ".join(feedback_parts)

    return GradingResult(
        score=score,
        subscores={"nebula_validation": score},
        weights={"nebula_validation": 1.0},
        feedback=feedback,
    )