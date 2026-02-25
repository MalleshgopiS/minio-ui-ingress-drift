# Validation Specification

This task validates correction of configuration drift
in the Kubernetes ingress resource `bleater-ui`
within the `bleater` namespace.

The grader performs direct cluster validation using kubectl.

## Validations Performed

The grader checks the following fields:

1. Host
   - Expected: `minio.devops.local`

2. Backend Service Name
   - Expected: `bleater-minio`

3. Backend Service Port
   - Expected: `9001`

4. TLS Secret
   - Expected: `bleater-minio-tls`

## Validation Method

The grader executes:

kubectl get ingress bleater-ui -n bleater -o jsonpath=...

and compares returned values against expected configuration.

## Pass Criteria

All values must exactly match expected configuration.

If any field differs, grading fails.

## Security

Validation is performed directly against Kubernetes cluster state.
No external scripts or hidden tests are used.