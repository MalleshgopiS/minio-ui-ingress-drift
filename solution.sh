#!/usr/bin/env bash
set -e

echo "Searching for MinIO ingress..."

if ! kubectl get ingress bleater-ui -n bleater >/dev/null 2>&1; then
  echo "MinIO ingress not found"
  exit 1
fi

echo "Fixing ingress configuration..."

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bleater-ui
  namespace: bleater
spec:
  ingressClassName: nginx
  rules:
  - host: minio.devops.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bleater-minio
            port:
              number: 9001
  tls:
  - hosts:
    - minio.devops.local
    secretName: bleater-minio-tls
EOF

echo "Ingress fixed successfully."