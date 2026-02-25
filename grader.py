#!/usr/bin/env python3

"""
Grader for minio-ui-ingress-drift

Validates that the existing Kubernetes ingress resource
has been corrected according to the task description.

Checks:
- backend service name
- backend service port
- TLS secret
- host value
"""

import subprocess
from apex_arena._types import GradingResult


EXPECTED_HOST = "minio.devops.local"
EXPECTED_SERVICE = "bleater-minio"
EXPECTED_PORT = "9001"
EXPECTED_TLS = "bleater-minio-tls"


def run(cmd: str):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_ingress_values():
    cmd = """
    kubectl get ingress bleater-ui -n bleater \
      -o jsonpath='{.spec.rules[0].host}{"|"}{.spec.rules[0].http.paths[0].backend.service.name}{"|"}{.spec.rules[0].http.paths[0].backend.service.port.number}{"|"}{.spec.tls[0].secretName}'
    """

    code, out, err = run(cmd)

    if code != 0 or not out:
        return None, f"Ingress not found or kubectl error: {err}"

    parts = out.split("|")

    if len(parts) != 4:
        return None, "Unexpected ingress structure"

    return parts, None


def grade(transcript: str) -> GradingResult:

    values, error = get_ingress_values()

    if error:
        return GradingResult(
            score=0.0,
            subscores={"ingress_validation": 0.0},
            weights={"ingress_validation": 1.0},
            feedback=error,
        )

    host, service, port, tls = values

    failures = []

    if host != EXPECTED_HOST:
        failures.append(f"host expected {EXPECTED_HOST}, got {host}")

    if service != EXPECTED_SERVICE:
        failures.append(f"service expected {EXPECTED_SERVICE}, got {service}")

    if port != EXPECTED_PORT:
        failures.append(f"port expected {EXPECTED_PORT}, got {port}")

    if tls != EXPECTED_TLS:
        failures.append(f"tls expected {EXPECTED_TLS}, got {tls}")

    if failures:
        return GradingResult(
            score=0.0,
            subscores={"ingress_validation": 0.0},
            weights={"ingress_validation": 1.0},
            feedback=" | ".join(failures),
        )

    return GradingResult(
        score=1.0,
        subscores={"ingress_validation": 1.0},
        weights={"ingress_validation": 1.0},
        feedback="Ingress configuration correct",
    )