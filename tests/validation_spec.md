# Validation Specification

This task validates correction of configuration drift in the Kubernetes
Ingress resource `bleater-ui` located in the `bleater` namespace.

The environment is initialized automatically using `setup.sh`
before the agent begins execution.

---

## Initial Environment State (Setup)

During setup:

- The `bleater` namespace is created if it does not exist.
- A placeholder backend Service named `wrong-service` is created.
- A placeholder TLS secret named `wrong-secret` is created.
- An Ingress resource `bleater-ui` is created with intentional configuration drift.

The ingress initially contains incorrect values:

| Field | Drifted Value |
|------|---------------|
| Backend Service | `wrong-service` |
| Backend Port | `80` |
| TLS Secret | `wrong-secret` |
| Host | `minio.devops.local` (correct and must remain unchanged) |

The setup process also records the original Kubernetes resource UID:

`/tmp/bleater-ui-original-uid`

This UID is later used by the grader to ensure the resource was modified
instead of deleted and recreated.

---

## Validations Performed

The grader validates the live Kubernetes cluster state using `kubectl`.

### 1. Host

Expected value:

`minio.devops.local`

### 2. Backend Service Name

Expected value:

`bleater-minio`

### 3. Backend Service Port

Expected value:

`9001`

### 4. TLS Secret

Expected value:

`bleater-minio-tls`

### 5. Resource Preservation (Anti-Cheat)

The grader verifies that:

- The ingress UID matches the original UID captured during setup.
- The agent modified the existing resource.
- The resource was NOT deleted and recreated.

---

## Validation Method

The grader executes commands similar to:

kubectl get ingress bleater-ui -n bleater -o jsonpath=...

Values are extracted directly from cluster state and compared against
expected configuration.

---

## Scoring

Each validation contributes equally to the final score:

- Host correct
- Service name correct
- Port correct
- TLS secret correct
- Resource not recreated

Final score = passed_checks / total_checks.

---

## Pass Criteria

All configuration values must match expected values and the ingress UID
must remain unchanged.

---

## Security Model

Validation is performed directly against Kubernetes cluster state.

- No hidden tests
- No external services
- No agent-modifiable grading files

The only way to pass is to correctly repair the ingress configuration.