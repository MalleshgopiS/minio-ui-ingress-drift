#!/bin/bash
set -e

###############################################################################
# SETUP SCRIPT
#
# Purpose:
#   Initializes the task environment by creating a DRIFTED ingress resource.
#
# Initial (Incorrect) State Created:
#   - ingress name: bleater-ui
#   - namespace: bleater
#   - WRONG backend service: wrong-service
#   - WRONG backend port: 80
#   - WRONG TLS secret: wrong-secret
#
# Expected Agent Fix:
#   - service  -> bleater-minio
#   - port     -> 9001
#   - tls      -> bleater-minio-tls
#   - host remains: minio.devops.local
#
# This ensures the task starts in a broken configuration
# which the agent must repair.
###############################################################################

echo "Creating drifted MinIO ingress..."

kubectl create namespace bleater --dry-run=client -o yaml | kubectl apply -f -

cat <<EOF | kubectl apply -f -
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

echo "Drifted ingress created."