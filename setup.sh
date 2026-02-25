#!/bin/bash
set -e

echo "Creating drifted MinIO ingress..."

# Create intentionally broken ingress (drifted state)
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
    secretName: wrong-secret
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
EOF

echo "Drifted ingress created successfully."