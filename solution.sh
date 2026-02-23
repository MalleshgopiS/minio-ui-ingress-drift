#!/usr/bin/env bash
set -e

echo "Fixing MinIO ingress drift..."

INGRESS="bleater-ui"
NS="bleater"

if ! kubectl get ingress $INGRESS -n $NS >/dev/null 2>&1; then
  echo "Ingress not found"
  exit 1
fi

# Fix backend service name
kubectl patch ingress $INGRESS -n $NS --type='json' -p='[
  {
    "op": "replace",
    "path": "/spec/rules/0/http/paths/0/backend/service/name",
    "value": "bleater-minio"
  }
]'

# Fix backend port
kubectl patch ingress $INGRESS -n $NS --type='json' -p='[
  {
    "op": "replace",
    "path": "/spec/rules/0/http/paths/0/backend/service/port/number",
    "value": 9001
  }
]'

# Fix TLS secret
kubectl patch ingress $INGRESS -n $NS --type='json' -p='[
  {
    "op": "replace",
    "path": "/spec/tls/0/secretName",
    "value": "bleater-minio-tls"
  }
]'

echo "Ingress drift fixed successfully."