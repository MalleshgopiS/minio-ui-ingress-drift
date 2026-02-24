#!/usr/bin/env python3
import subprocess
from apex_arena._types import GradingResult

def run_kubectl(cmd):
    full_cmd = f"KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl {cmd}"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def grade(transcript: str) -> GradingResult:
    feedback_parts = []
    
    # 1. Check if Ingress exists
    code, out, _ = run_kubectl("get ingress minio-ui-ingress -n minio -o name")
    if code == 0 and "minio-ui-ingress" in out:
        feedback_parts.append("✓ Minio UI Ingress exists")
        ingress_exists = True
    else:
        feedback_parts.append("✗ Minio UI Ingress not found")
        ingress_exists = False

    # 2. Check Configuration
    host_code, host, _ = run_kubectl("get ingress minio-ui-ingress -n minio -o jsonpath='{.spec.rules[0].host}'")
    port_code, port, _ = run_kubectl("get ingress minio-ui-ingress -n minio -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.port.number}'")
    
    if host == "minio-ui.devops.local" and port == "9001":
        feedback_parts.append("✓ Host and Backend port correctly configured")
        config_ok = True
    else:
        feedback_parts.append("✗ Ingress configuration mismatch")
        config_ok = False

    final_score = 1.0 if (ingress_exists and config_ok) else 0.0

    return GradingResult(
        score=final_score,
        subscores={"ingress_drift_fixed": final_score},
        weights={"ingress_drift_fixed": 1.0},
        feedback=" | ".join(feedback_parts)
    )