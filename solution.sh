#!/usr/bin/env bash
set -e

echo "Fixing MinIO ingress drift..."

if ! kubectl get ingress bleater-ui -n bleater >/dev/null 2>&1; then
  echo "Ingress not found"
  exit 1
fi

kubectl patch ingress bleater-ui -n bleater --type='merge' -p '
spec:
  rules:
  - host: minio.devops.local
    http:
      paths:
      - backend:
          service:
            name: bleater-minio
            port:
              number: 9001
  tls:
  - secretName: bleater-minio-tls
'

echo "Ingress drift fixed."