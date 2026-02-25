# Validation Specification

This task validates correction of configuration drift in the
Kubernetes ingress resource `bleater-ui` located in the
`bleater` namespace.

The grader performs direct validation against Kubernetes
cluster state using `kubectl`.

## Environment Setup

The evaluation container executes `setup.sh` before grading.

The setup script creates a reproducible drifted environment:

- Namespace: `bleater`
- Ingress: `bleater-ui`
- Incorrect backend service configuration
- Incorrect TLS configuration

The agent must repair the existing ingress resource.

## Validations Performed

The grader validates the following fields:

1. Host  
Expected value: `minio.devops.local`

2. Backend Service Name  
Expected value: `bleater-minio`

3. Backend Service Port  
Expected value: `9001`

4. TLS Secret  
Expected value: `bleater-minio-tls`

## Validation Method

The grader executes:

kubectl get ingress bleater-ui -n bleater -o jsonpath=...

and compares returned values with expected configuration.

## Pass Criteria

Each correct field contributes 0.25 to the final score.

Full score (1.0) requires all four values to match.

## Security & Anti-Cheating

The grader verifies that the original ingress resource
was modified rather than deleted and recreated by
checking the Kubernetes resource UID.