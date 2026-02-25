#!/usr/bin/env python3

import subprocess
import time
from apex_arena._types import GradingResult


# ==================================================
# Helper command runner
# ==================================================

def run(cmd: str):
    """Execute shell command safely."""
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


# ==================================================
# Wait for cluster stability
# ==================================================

def wait_for_cluster(timeout=120):
    """
    Wait until ingress resource becomes readable.
    Prevents race conditions during cluster startup.
    """
    start = time.time()

    while time.time() - start < timeout:
        code, _, _ = run(
            "kubectl get ingress bleater-ui -n bleater"
        )
        if code == 0:
            return True

        time.sleep(5)

    return False


# ==================================================
# UID helpers (ANTI-CHEAT)
# ==================================================

def get_current_uid():
    """Fetch current ingress UID."""
    code, out, _ = run(
        "kubectl get ingress bleater-ui -n bleater "
        "-o jsonpath='{.metadata.uid}'"
    )

    if code != 0:
        return None

    return out.replace("'", "").strip()


def get_original_uid():
    """
    Read UID captured during setup.sh.
    This represents the ingress BEFORE agent actions.
    """
    try:
        with open("/tmp/bleater-ui-original-uid", "r") as f:
            return f.read().strip()
    except Exception:
        return None


# ==================================================
# Main grading logic
# ==================================================

def grade(transcript: str) -> GradingResult:

    wait_for_cluster()

    # --------------------------------------------------
    # Read ingress configuration
    # --------------------------------------------------

    code, out, err = run(
        "kubectl get ingress bleater-ui -n bleater "
        "-o jsonpath='{.spec.rules[0].host}|"
        "{.spec.rules[0].http.paths[0].backend.service.name}|"
        "{.spec.rules[0].http.paths[0].backend.service.port.number}|"
        "{.spec.tls[0].secretName}'"
    )

    if code != 0 or not out:
        return GradingResult(
            score=0.0,
            feedback="Failed to read ingress configuration",
        )

    try:
        host, service, port, tls = out.replace("'", "").split("|")
    except ValueError:
        return GradingResult(
            score=0.0,
            feedback="Unexpected ingress output format",
        )

    # --------------------------------------------------
    # Validation checks
    # --------------------------------------------------

    checks = {
        "host_correct": host == "minio.devops.local",
        "service_correct": service == "bleater-minio",
        "port_correct": str(port) == "9001",
        "tls_correct": tls == "bleater-minio-tls",
    }

    # --------------------------------------------------
    # Anti-cheat: ensure ingress NOT recreated
    # --------------------------------------------------

    original_uid = get_original_uid()
    current_uid = get_current_uid()

    uid_preserved = (
        original_uid is not None
        and current_uid is not None
        and original_uid == current_uid
    )

    checks["resource_not_recreated"] = uid_preserved

    # --------------------------------------------------
    # Scoring
    # --------------------------------------------------

    total_checks = len(checks)
    passed = sum(checks.values())
    score = passed / total_checks

    feedback = ", ".join(
        f"{k}:{'✓' if v else '✗'}" for k, v in checks.items()
    )

    return GradingResult(
        score=score,
        subscores=checks,
        weights={k: 1 / total_checks for k in checks},
        feedback=feedback,
    )