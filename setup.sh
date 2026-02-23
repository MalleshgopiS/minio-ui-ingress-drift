#!/usr/bin/env bash
set -e

echo "Creating drifted MinIO ingress..."

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
            name: WRONG-SERVICE
            port:
              number: 80
  tls:
  - hosts:
    - minio.devops.local
    secretName: WRONG-TLS
EOF

echo "Drifted ingress created."