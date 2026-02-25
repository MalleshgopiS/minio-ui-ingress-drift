# Validation Specification

This task validates correction of configuration drift
in the Kubernetes ingress resource `bleater-ui`
within the `bleater` namespace.

---

## Environment Initialization

Before grading begins, the environment is initialized
by executing `setup.sh`.

The setup script prepares the Kubernetes cluster and
creates a deliberately drifted ingress configuration
that the agent must repair.

The following incorrect values are introduced:

- Backend service name → `wrong-service`
- Backend service port → `80`
- TLS secret → `wrong-secret`

The host remains:

- `minio.devops.local`

The agent must modify the existing ingress resource
to restore the correct configuration.

---

## Validations Performed

The grader checks the following fields:

1. Host  
   Expected: `minio.devops.local`

2. Backend Service Name  
   Expected: `bleater-minio`

3. Backend Service Port  
   Expected: `9001`

4. TLS Secret  
   Expected: `bleater-minio-tls`

---

## Validation Method

The grader executes:

kubectl get ingress bleater-ui -n bleater -o jsonpath=...

and compares returned values against expected configuration.

---

## Pass Criteria

Each field is validated independently.
All values must match expected configuration for full score.

---

## Security

Validation is performed directly against Kubernetes cluster state.
No external scripts or hidden tests are used.