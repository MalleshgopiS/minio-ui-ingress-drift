#!/usr/bin/env python3
import subprocess
from apex_arena._types import GradingResult


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def check_ingress():
    cmd = """kubectl get ingress bleater-ui -n bleater -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name} {.spec.rules[0].http.paths[0].backend.service.port.number} {.spec.tls[0].secretName}'"""
    code, out = run(cmd)

    if code != 0:
        return False, "Ingress not found"

    service, port, secret = out.replace("'", "").split()

    if service != "bleater-minio":
        return False, f"Wrong service: {service}"

    if port != "9001":
        return False, f"Wrong port: {port}"

    if secret != "bleater-minio-tls":
        return False, f"Wrong TLS secret: {secret}"

    return True, "Ingress correctly configured"


def grade(transcript: str):
    ok, msg = check_ingress()

    return GradingResult(
        score=1.0 if ok else 0.0,
        subscores={"ingress_fixed": 1.0 if ok else 0.0},
        weights={"ingress_fixed": 1.0},
        feedback=msg
    )