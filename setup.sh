#!/usr/bin/env bash
set -e

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