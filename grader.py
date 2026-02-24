#!/usr/bin/env python3
import subprocess
from apex_arena._types import GradingResult

def run_kubectl(cmd):
    full_cmd = f"kubectl {cmd} --kubeconfig=/etc/rancher/k3s/k3s.yaml"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def grade(transcript: str) -> GradingResult:
    feedback = []
    score = 0.0
    
    # 1. Check if Ingress exists
    code, out, err = run_kubectl("get ingress minio-ui-ingress -n minio -o name")
    ingress_exists = (code == 0 and "minio-ui-ingress" in out)
    
    # 2. Check Hostname
    code, host, err = run_kubectl("get ingress minio-ui-ingress -n minio -o jsonpath='{.spec.rules[0].host}'")
    host_ok = (host == "minio-ui.devops.local")

    # 3. Check Service Name and Port
    code, svc, err = run_kubectl("get ingress minio-ui-ingress -n minio -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}'")
    code, port, err = run_kubectl("get ingress minio-ui-ingress -n minio -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.port.number}'")
    backend_ok = (svc == "minio-console" and port == "9001")

    if ingress_exists:
        feedback.append("✓ Ingress resource created")
        if host_ok and backend_ok:
            feedback.append("✓ Ingress configured with correct host and backend port")
            score = 1.0
        else:
            feedback.append("✗ Ingress found but configuration (host/port) is incorrect")
    else:
        feedback.append("✗ Ingress 'minio-ui-ingress' not found in namespace 'minio'")

    return GradingResult(
        score=score,
        subscores={"ingress_drift_fixed": score},
        weights={"ingress_drift_fixed": 1.0},
        feedback=" | ".join(feedback)
    )