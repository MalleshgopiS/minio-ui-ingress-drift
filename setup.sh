#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="bleater"
INGRESS="bleater-ui"

echo "Waiting for Kubernetes API..."

# --------------------------------------------------
# wait for namespace
# --------------------------------------------------
for i in {1..60}; do
  if kubectl get ns $NAMESPACE >/dev/null 2>&1; then
    echo "Namespace ready"
    break
  fi
  sleep 5
done

kubectl get ns $NAMESPACE >/dev/null

# --------------------------------------------------
# VERY IMPORTANT:
# wait until ingress EXISTS (from snapshot restore)
# --------------------------------------------------

echo "Waiting for existing ingress (snapshot restore)..."

for i in {1..90}; do
  if kubectl get ingress $INGRESS -n $NAMESPACE >/dev/null 2>&1; then
    echo "Ingress detected"
    break
  fi
  sleep 5
done

# HARD FAIL if not found
if ! kubectl get ingress $INGRESS -n $NAMESPACE >/dev/null 2>&1; then
  echo "ERROR: ingress never appeared — refusing to create new one"
  exit 1
fi

# --------------------------------------------------
# PATCH ONLY (NEVER APPLY)
# --------------------------------------------------

echo "Injecting ingress drift safely..."

kubectl patch ingress $INGRESS -n $NAMESPACE \
  --type=json \
  -p='[
    {
      "op":"replace",
      "path":"/spec/rules/0/http/paths/0/backend/service/name",
      "value":"wrong-service"
    },
    {
      "op":"replace",
      "path":"/spec/rules/0/http/paths/0/backend/service/port/number",
      "value":80
    },
    {
      "op":"replace",
      "path":"/spec/tls/0/secretName",
      "value":"wrong-secret"
    }
  ]'

echo "✅ Drift injected (patched existing ingress)"