#!/bin/bash
set -e

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

echo "Fixing MinIO ingress drift..."

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bleater-ui
  namespace: bleater
spec:
  tls:
  - hosts:
    - minio.devops.local
    secretName: bleater-minio-tls
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
EOF

echo "Ingress fixed successfully."