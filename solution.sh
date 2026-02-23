#!/usr/bin/env bash
set -e

INGRESS="bleater-ui"
NS="bleater"

# Check existence to avoid silent errors
if ! kubectl get ingress "$INGRESS" -n "$NS" >/dev/null 2>&1; then
  exit 1
fi

# Atomic patch for all three requirements
kubectl patch ingress "$INGRESS" -n "$NS" --type='json' -p='[
  {"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/name", "value": "bleater-minio"},
  {"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/port/number", "value": 9001},
  {"op": "replace", "path": "/spec/tls/0/secretName", "value": "bleater-minio-tls"}
]'