# Validation Specification

This task validates correction of configuration drift in the Kubernetes ingress resource **bleater-ui** located in the **bleater** namespace.

The grader validates the final Kubernetes cluster state directly using `kubectl`.

---

## Environment Setup (setup.sh)

Before evaluation begins, the container automatically runs the `setup.sh` script.

The setup script prepares the Kubernetes environment and creates the initial **drifted ingress configuration** required for the task.

The setup process performs the following actions:

- Creates the namespace `bleater`
- Ensures required backend services exist
- Creates the ingress resource `bleater-ui`
- Applies intentionally incorrect configuration values to simulate configuration drift

### Initial Drifted Configuration

| Field | Drifted Value |
|------|---------------|
| Host | minio.devops.local |
| Backend Service Name | wrong-service |
| Backend Service Port | 80 |
| TLS Secret | wrong-secret |

This guarantees every evaluation starts from a reproducible misconfigured state that the agent must repair.

The agent must **modify the existing ingress resource only** and must **not create new Kubernetes resources**.

---

## Validations Performed

The grader validates the following ingress fields.

### Host
Expected value: minio.devops.local

### Backend Service Name
Expected value: bleater-minio

### Backend Service Port
Expected value: 9001

### TLS Secret
Expected value: bleater-minio-tls

---

## Validation Method

The grader retrieves ingress values directly from the Kubernetes cluster using:

kubectl get ingress bleater-ui -n bleater -o jsonpath=...

Values are extracted using Kubernetes JSONPath queries and compared against expected configuration values.

No regex parsing or hidden validation scripts are used.

---

## Scoring Logic

Each validation contributes **0.25** to the final score:

| Check | Score |
|------|------|
| Host correct | 0.25 |
| Service name correct | 0.25 |
| Service port correct | 0.25 |
| TLS secret correct | 0.25 |

Maximum score: **1.0**

Partial credit is awarded when only some fields are corrected.

---

## Pass Criteria

A full score (1.0) is awarded when all four fields match the expected configuration exactly.

If any field differs, partial credit is assigned based on the number of successful validations.

---

## Security and Anti-Cheating

Validation is performed directly against the live Kubernetes cluster state.

- The grader reads real resource configuration.
- Agents cannot modify grader logic.
- No hidden scripts or external internet access are available.
- Passing requires actual modification of the ingress resource.

The grader validates the final system state rather than the commands used.

---

## Reproducibility

The environment is deterministic because:

- A pinned base image (`nebula-devops:1.0.0`) is used.
- `setup.sh` recreates the same drifted ingress each run.
- Validation uses direct Kubernetes state inspection.

This ensures consistent evaluation results across executions.