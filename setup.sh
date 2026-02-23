#!/usr/bin/env bash
set -e

# Create namespace first to avoid resource creation errors
kubectl create namespace bleater --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bleater-ui
  namespace: bleater
spec:
  rules:
  - host: minio.devops.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wrong-service
            port:
              number: 80
  tls:
  - hosts:
    - minio.devops.local
    secretName: wrong-secret
EOF